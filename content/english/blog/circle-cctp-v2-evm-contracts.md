---
title: "Circle CCTP V2 EVM Contracts: A Source-Code Walkthrough"
meta_title: ""
description: "How TokenMessengerV2, MessageTransmitterV2, and TokenMinterV2 divide responsibility in Circle's CCTP V2. Covers the burn-and-mint lifecycle, message layout, fee model, hookData, destinationCaller, and the trust assumptions every integrator should know."
date: 2026-06-30T17:30:00+09:00
lastmod: 2026-06-30T17:30:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["cctp", "circle", "usdc", "cross-chain", "solidity"]
author: "whackur"
translationKey: "circle-cctp-v2-evm-contracts"
draft: false
---

Moving USDC across blockchains comes down to two designs. Lock-and-mint freezes the original token on the source chain and issues a wrapped version elsewhere, concentrating a large TVL target inside a single smart contract. Burn-and-mint does the opposite: the source chain burns the original, and a trusted authority mints an equal amount on the destination. No lockbox, no wrapped variant.

Circle's [CCTP (Cross-Chain Transfer Protocol)](https://developers.circle.com/stablecoins/cctp-getting-started) takes the second approach. Every USDC that crosses chains via CCTP is a native USDC on arrival, with no wrapped-USDC fragmentation.

This post walks through the V2 EVM contracts at the source-code level. The code is public at [circlefin/evm-cctp-contracts](https://github.com/circlefin/evm-cctp-contracts). The focus is on the three-contract architecture, message format, the burn and mint lifecycles, V2 additions (fast finality, fee model, hookData), and the trust assumptions every integrator should understand before shipping.

## Burn-and-mint vs. lock-and-mint

The practical concern with lock-and-mint is concentration risk: the full TVL sitting inside a single locking contract is a large, attractive target for exploits.

Burn-and-mint removes that concentrated target. Burned USDC on the source chain is gone. Circle's attestation service witnesses the burn and authorizes an equivalent mint on the destination. The risk model shifts from "does the lockbox have a bug?" to "can Circle's attestation be forged or censored?" That is a different (and more centralized) trust assumption, but without a nine-figure honeypot sitting on-chain.

## Three contracts, three responsibilities

V2's EVM implementation splits work across three contracts.

| Contract | Responsibility | Who calls it |
|----------|----------------|--------------|
| `TokenMessengerV2` | User-facing entry point. Accepts burn requests, handles receive | User EOA or contract |
| `MessageTransmitterV2` | Cross-chain message routing, attestation verification | TokenMessengerV2, relayers |
| `TokenMinterV2` | Execute token burns and mints, enforce per-token limits | TokenMessengerV2 only |

The separation follows a single-responsibility design: TokenMessengerV2 knows about USDC but not about domain routing. MessageTransmitterV2 knows about message formats but nothing about tokens. TokenMinterV2 knows about token mechanics but ignores message routing entirely.

## TokenMessengerV2: the user-facing entry point

TokenMessengerV2 is the only contract users call directly. V2 adds `destinationCaller`, `maxFee`, and `minFinalityThreshold` to the base `depositForBurn` call.

**depositForBurn**: the basic burn.

```solidity
function depositForBurn(
    uint256 amount,
    uint32 destinationDomain,
    bytes32 mintRecipient,
    address burnToken,
    bytes32 destinationCaller,
    uint256 maxFee,
    uint32 minFinalityThreshold
) external notDenylistedCallers;
```

`mintRecipient` is `bytes32`, not `address`. EVM addresses are right-aligned in the 32-byte field (left-padded with zeros). In Solidity: `bytes32(uint256(uint160(addr)))`. This keeps the format consistent across chains that natively use 32-byte addresses (Solana, Noble).

`destinationCaller` set to `bytes32(0)` allows anyone to call `receiveMessage()` on the destination. Set it to a specific relayer or contract address to restrict who can complete the transfer. `maxFee` is the maximum fee the sender accepts, denominated in the burn token. Circle's documentation classifies `minFinalityThreshold <= 1000` as Fast Transfer and `>= 2000` as Standard Transfer (no fee). The contract routes received messages based on whether `finalityThresholdExecuted` is below `FINALITY_THRESHOLD_FINALIZED` (2000); TokenMessengerV2 requires the unfinalized execution threshold to be at least 500. No return value.

**depositForBurnWithHook**: V2-only. Adds `hookData` to the destination. Empty `hookData` is rejected.

```solidity
function depositForBurnWithHook(
    uint256 amount,
    uint32 destinationDomain,
    bytes32 mintRecipient,
    address burnToken,
    bytes32 destinationCaller,
    uint256 maxFee,
    uint32 minFinalityThreshold,
    bytes calldata hookData
) external notDenylistedCallers;
```

More on hookData below.

Internally, every burn call does two things in order: `TokenMinterV2.burn()` to destroy the USDC, then `MessageTransmitterV2.sendMessage()` to emit the cross-chain message. Both `DepositForBurn` and `MessageSent` events land in the same transaction receipt.

## MessageTransmitterV2: routing and attestation

MessageTransmitterV2 is the communications layer. It has no knowledge of tokens, just raw byte messages.

**sendMessage** is called by TokenMessengerV2 after a burn. It accepts the destination domain, recipient contract, destinationCaller, minFinalityThreshold, and message body, then emits a `MessageSent` event. The `message` bytes in that event are what a relayer needs to collect.

**receiveMessage** is called by a relayer on the destination chain:

```solidity
function receiveMessage(
    bytes calldata message,
    bytes calldata attestation
) external returns (bool success);
```

It does three things before routing: checks that the destination domain matches the local chain, verifies the attestation signatures against the `enabledAttesters` set, and marks the nonce as used in `usedNonces` to prevent replay. If all three pass, it branches on `finalityThresholdExecuted`: at 2000 or above (`FINALITY_THRESHOLD_FINALIZED`) it calls `handleReceiveFinalizedMessage()`; below 2000 it calls `handleReceiveUnfinalizedMessage()`.

The attesters are a set of Circle-controlled addresses registered via `enabledAttesters`. Passing requires at least `signatureThreshold` valid signatures. MessageTransmitterV2 supports configurable M-of-N attester signatures. The actual deployed threshold and attester set should be verified against the deployed contract or Circle's official deployment documentation.

## TokenMinterV2: token mechanics

TokenMinterV2 handles the actual burn and mint operations. Only TokenMessengerV2 can call it. There is no external entry point.

`burn(address burnToken, uint256 amount)` destroys USDC on the source chain. Before burning, it checks that `amount` does not exceed `burnLimitsPerMessage[burnToken]`. Exceeding the limit reverts. This per-token cap is a risk management control with no oracle dependency.

`mint()` creates USDC on the destination. The V2 interface accepts two recipients in one call: `mintRecipient` (the user) and `feeRecipient` (the fee collector), with corresponding amounts. It uses `remoteTokensToLocalTokens[sourceDomain][burnToken]` to map the source chain token address to the local USDC address. Circle manages this mapping; supported token pairs are listed in the official developer docs.

## Message layout

CCTP messages use a packed binary format (not ABI-encoded). The header is fixed-length; the body varies.

**Message header (148 bytes):**

| Field | Type | Bytes | Notes |
|-------|------|-------|-------|
| version | uint32 | 4 | |
| sourceDomain | uint32 | 4 | |
| destinationDomain | uint32 | 4 | |
| nonce | bytes32 | 32 | Changed from uint64 (8 bytes) in V1 |
| sender | bytes32 | 32 | |
| recipient | bytes32 | 32 | |
| destinationCaller | bytes32 | 32 | |
| minFinalityThreshold | uint32 | 4 | V2 addition |
| finalityThresholdExecuted | uint32 | 4 | V2 addition; Circle fills this in |
| **Total** | | **148** | |

The V2 nonce is `bytes32`, sent as `bytes32(0)` on the source chain and filled in by Circle's attestation service before signing. `minFinalityThreshold` and `finalityThresholdExecuted` are new, pushing the header from 116 to 148 bytes.

Domain IDs are assigned by Circle centrally. Current major EVM chains:

| Chain | Domain |
|-------|--------|
| Ethereum | 0 |
| Avalanche C-Chain | 1 |
| OP Mainnet | 2 |
| Arbitrum One | 3 |
| Base | 6 |
| Polygon PoS | 7 |

**BurnMessage body (starts at byte 148):**

| Field | Type | Notes |
|-------|------|-------|
| version | uint32 | BurnMessage format version |
| burnToken | bytes32 | Source chain token address |
| mintRecipient | bytes32 | Destination recipient |
| amount | uint256 | Transfer amount |
| messageSender | bytes32 | Original `depositForBurn` caller |
| maxFee | uint256 | Sender's maximum accepted fee |
| feeExecuted | uint256 | Actual fee charged; Circle fills this in |
| expirationBlock | uint256 | Message expiry block (0 = no expiry) |
| hookData | bytes | V2 addition; variable length |

`feeExecuted` and `expirationBlock` are sent as `0` from the source chain; Circle's attestation service fills them in before signing. Without hookData the body is 228 bytes fixed.

## Burn lifecycle

The sequence from source chain to destination:

1. **Approve**: call `USDC.approve(tokenMessengerV2Address, amount)`.

2. **depositForBurn**: TokenMessengerV2 burns the USDC via TokenMinterV2, then calls `MessageTransmitterV2.sendMessage()` to emit `MessageSent`. Both `DepositForBurn` and `MessageSent` land in the same transaction receipt.

3. **Collect the message bytes**: parse the `MessageSent` event for the `message` field. Store it verbatim.

4. **Request attestation**: hash the message with keccak256 and poll Circle's Iris API:
   ```
   GET https://iris-api.circle.com/attestations/{messageHash}
   ```
   Status starts as `pending`. On the standard path, the API waits for source chain finality before returning `complete`. On Ethereum that is roughly 15–20 minutes.

5. **receiveMessage**: once the attestation is `complete`, submit the original `message` bytes and the `attestation` bytes to MessageTransmitterV2 on the destination chain.

## Mint lifecycle

After `receiveMessage` is called on the destination:

1. Parse the header; confirm `destinationDomain` matches.
2. Verify attestation signatures meet the threshold.
3. If `destinationCaller != 0`, confirm `msg.sender == destinationCaller`.
4. Check `usedNonces[nonce]` is unused; mark it used. (`nonce` is a `bytes32` single key in V2.)
5. Branch on `finalityThresholdExecuted`: at 2000 or above, call `handleReceiveFinalizedMessage()` (no fee, full `amount` to `mintRecipient`). Below 2000, call `handleReceiveUnfinalizedMessage()` (`amount - feeExecuted` to `mintRecipient`, `feeExecuted` to `feeRecipient`).
6. hookData in BurnMessageV2 is available for relay wrappers (e.g. CCTPHookWrapper) to process after `receiveMessage` completes; MessageTransmitter and TokenMessenger do not themselves call mintRecipient based on hookData.

A replay attempt with the same message fails at step 4: the nonce is already marked used.

## Fast finality and the fee model

Fast transfers are V2's headline addition.

**Standard path**: waits for source chain finality. About 15–20 minutes on Ethereum; a few minutes on faster chains. No fee.

**Fast path**: Circle issues an attestation before full finality. USDC arrives on the destination in seconds to minutes. A fee applies.

The fee comes out of the minted amount. If `amount = 100 USDC` and `fee = 1 USDC`, the `mintRecipient` receives `99 USDC`. Circle absorbs the risk of a source chain reorg invalidating a burn that has already been minted; that risk is what the fee prices. Specific fee values are in Circle's [developer documentation](https://developers.circle.com/stablecoins/cctp-getting-started).

## destinationCaller and hookData

**destinationCaller** is a `bytes32` header field that gates who can call `receiveMessage()` on the destination.

`0x000...000` means no restriction: anyone can trigger the mint. Setting it to a specific address (right-aligned in bytes32) means only that address can call `receiveMessage()`. This lets you tie the transfer to a specific relayer contract for MEV protection or sequenced execution.

**hookData** is a variable-length bytes field appended to the BurnMessage body when using `depositForBurnWithHook`. TokenMessengerV2 stores and parses hookData in BurnMessageV2 but does not itself call mintRecipient as a hook. Circle's CCTPHookWrapper reference wrapper calls `receiveMessage()` and then performs hook processing separately, outside the core contracts.

Use cases:
- Swap on arrival (bridge into a DEX swap in one relayer transaction)
- Deposit into a lending protocol on the destination
- Cross-chain payment flows with downstream logic

Circle's reference implementation (CCTPHookWrapper) runs hooks non-atomically: the hook executes after `receiveMessage` completes, so a hook failure does not roll back the mint. This is intentional. Without it, an attacker could submit with insufficient gas to burn the nonce while leaving the hook unexecuted. Custom hook contracts should account for this non-atomic execution model.

## Security model and trust assumptions

**Centralized attestation**: Circle controls the attesters. MessageTransmitterV2 supports M-of-N multisig; the actual deployed signature threshold and attester count should be checked on the deployed contract or Circle's official deployment docs. Regardless of threshold, Circle manages the attester set — the known trust tradeoff in exchange for no TVL lockbox.

**Replay protection**: `usedNonces[nonce]` on each destination chain prevents double-minting. In V2, the nonce is a `bytes32` value filled in by Circle's attestation service, not a sequential counter.

**Burn limits**: `burnLimitsPerMessage[token]` caps the amount in a single transaction. This limits the blast radius of an attack but does not prevent one.

**Upgradeable proxies**: TokenMessengerV2 and MessageTransmitterV2 are deployed behind upgradeable proxies. Circle can update the logic. Check whether a timelock is in place on the proxy admin. The [deployed contract addresses](https://developers.circle.com/stablecoins/evm-smart-contract-addresses) page is the starting point for that investigation.

**Off-chain dependency**: if `iris-api.circle.com` is unavailable, in-flight transfers stall after the burn. The USDC is already destroyed on the source chain and cannot be recovered without a valid attestation. Circle can re-issue attestations when the service recovers, but there is no on-chain escape path.

## Integration checklist

Running through this before shipping saves pain:

1. **Get addresses from the official docs**: [Circle's smart contract address page](https://developers.circle.com/stablecoins/evm-smart-contract-addresses). Don't hardcode; manage them in config.

2. **Approve before burning**: `USDC.approve(tokenMessengerV2, amount)` in the same transaction or just before.

3. **Encode mintRecipient correctly**: convert an EVM address with `bytes32(uint256(uint160(addr)))` in Solidity. Non-EVM chains have their own encoding rules.

4. **Store the full message bytes**: from the `MessageSent` event. This exact byte sequence is what `receiveMessage` takes.

5. **Poll until complete**: the Iris API returns `pending` while waiting for finality. Don't submit to the destination with a pending attestation.

6. **Account for hook gas**: if using hookData, the destination transaction includes the hook contract execution. Estimate gas accordingly.

7. **Handle the destinationCaller restriction**: if you set a non-zero destinationCaller, only that address can complete the transfer. Make sure your relaying infrastructure controls that address.

8. **Check burn limits before large transfers**: amounts above `burnLimitsPerMessage` revert. Split large transfers across multiple transactions.

## Further reading

- [circlefin/evm-cctp-contracts](https://github.com/circlefin/evm-cctp-contracts) — source code for all CCTP V2 EVM contracts (MIT license)
- [Circle CCTP developer docs](https://developers.circle.com/stablecoins/cctp-getting-started) — official integration guide
- [CCTP smart contract addresses](https://developers.circle.com/stablecoins/evm-smart-contract-addresses) — chain-by-chain deployed addresses

## References

- [circlefin/evm-cctp-contracts](https://github.com/circlefin/evm-cctp-contracts) — Circle, accessed 2026-06-30
- [CCTP developer docs: getting started](https://developers.circle.com/stablecoins/cctp-getting-started) — Circle Developer Docs, accessed 2026-06-30
- [CCTP EVM smart contract addresses](https://developers.circle.com/stablecoins/evm-smart-contract-addresses) — Circle Developer Docs, accessed 2026-06-30
- [CCTP V2 overview](https://developers.circle.com/stablecoins/cctp-v2-overview) — Circle Developer Docs, accessed 2026-06-30
