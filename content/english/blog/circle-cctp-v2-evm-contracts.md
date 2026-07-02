---
title: "Circle CCTP V2 EVM Contracts: A Source-Code Walkthrough"
meta_title: ""
description: "How TokenMessengerV2, MessageTransmitterV2, and TokenMinterV2 divide responsibility in Circle's CCTP V2. Covers the burn-and-mint lifecycle, message layout, fast transfer fee model, hookData, destinationCaller, and the trust assumptions every integrator should know."
date: 2026-06-30T17:30:00+09:00
lastmod: 2026-07-02T00:00:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["cctp", "circle", "usdc", "cross-chain", "solidity"]
author: "whackur"
translationKey: "circle-cctp-v2-evm-contracts"
draft: false
---

Bridge designs for moving USDC between chains come down to two families. Lock-and-mint parks the original token in a contract on the source chain and issues a wrapped version on the destination. Burn-and-mint destroys the token on the source chain outright and issues the same amount fresh on the destination. Circle's [CCTP (Cross-Chain Transfer Protocol)](https://developers.circle.com/stablecoins/cctp-getting-started) is the second kind.

Burn-and-mint is not an option for arbitrary tokens. Minting a genuine token on the destination requires an entity that holds mint authority on every chain involved. USDC qualifies because Circle, the issuer, controls minting everywhere USDC exists natively. That is also why generic bridges, which hold no such authority, have no choice but to issue wrapped tokens.

This post walks through the CCTP V2 EVM contracts at the source-code level. The code is public at [circlefin/evm-cctp-contracts](https://github.com/circlefin/evm-cctp-contracts). It covers the differences from V1, the three-contract split, the message format, the burn and mint lifecycles, the V2 additions (fast transfers, the fee model, hookData), and the trust assumptions and failure modes an integrator should understand before shipping.

## Wrapped USDC fragmentation

Lock-and-mint bridges cause problems in two directions.

The first is security. A single locking contract accumulates the collateral for the entire bridge. The larger the TVL, the more attractive that one contract becomes as an exploit target. If the lockbox is drained, the collateral is gone, and every wrapped token issued against it becomes an unbacked asset in an instant.

The second is liquidity fragmentation. Each bridge issues its own wrapped token from its own contract. Two "USDC" tokens that crossed through different bridges are incompatible assets, each needing its own DEX pools and lending markets. USDC.e, long used on Avalanche and Arbitrum, is the canonical example. Until Circle launched native USDC on those chains, users lived with bridged USDC.e and native USDC coexisting and splitting liquidity between them.

CCTP removes both problems with the same move. No lockbox, so no honeypot. USDC on the source chain is actually destroyed; Circle confirms the burn and issues native USDC on the destination. Whatever route the transfer takes, the token that arrives is always the single native USDC issued by Circle.

This is not free. Circle holds a monopoly on confirming burns and authorizing mints. If Circle's infrastructure stops, transfers stop. The design trades a giant TVL lockbox for trust in a centralized issuer, and that trade should be made knowingly. How this trust boundary shows up in the code is covered in the attestation section below.

## Three contracts, three responsibilities

The V2 EVM implementation splits work across three contracts.

| Contract | Responsibility | Who calls it |
|----------|----------------|--------------|
| `TokenMessengerV2` | User-facing entry point. Accepts burn requests, handles receive | User EOA or contract |
| `MessageTransmitterV2` | Cross-chain message routing, attestation verification | TokenMessengerV2, relayers |
| `TokenMinterV2` | Execute token burns and mints, enforce per-token limits | TokenMessengerV2 only |

In one line each: TokenMessengerV2 is the entry point users touch, MessageTransmitterV2 is the communication layer that handles messages and attestations, and TokenMinterV2 is the vault keeper holding the actual burn and mint authority.

The value of the split is that each concern gets a narrow trust perimeter. MessageTransmitterV2 is a generic message-passing contract that knows nothing about tokens. USDC mint authority, on the other hand, lives in exactly one place, TokenMinterV2, and only TokenMessengerV2 can call it. The path to a mint is a single corridor in the code, so there is correspondingly less attack surface to audit.

## TokenMessengerV2: the user-facing entry point

TokenMessengerV2 is the only contract users call directly. Where V1's `depositForBurn` took 4 parameters, V2 adds three more: `destinationCaller`, `maxFee`, and `minFinalityThreshold`. Each new parameter maps to a V2 feature.

**depositForBurn**: the basic burn request.

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

`mintRecipient` is `bytes32`, not `address`. EVM addresses are right-aligned in the 32-byte field (left-padded with zeros). In Solidity: `bytes32(uint256(uint160(addr)))`. This keeps the format uniform with chains that natively use 32-byte addresses, such as Solana.

`destinationCaller` set to `bytes32(0)` allows anyone to call `receiveMessage()` on the destination and complete the mint. Set it to a specific relayer or contract address to restrict who can finish the transfer.

`maxFee` is the fee ceiling the sender accepts, denominated in the burn token. The fee Circle actually charges is only valid within this ceiling, so using a fast transfer requires setting maxFee at or above Circle's current fast fee.

`minFinalityThreshold` is the minimum finality level the sender demands, where finality means the state where a block can no longer realistically be reverted by a reorg. Circle's documentation classifies `minFinalityThreshold <= 1000` as Fast Transfer and `>= 2000` as Standard Transfer (no fee). On the receiving side, the contract routes on the message's recorded `finalityThresholdExecuted`: below `FINALITY_THRESHOLD_FINALIZED` (2000) takes the unfinalized path, at or above takes the finalized path. The minimum unfinalized threshold TokenMessengerV2 accepts is 500. There is no return value.

**depositForBurnWithHook**: V2-only, passes `hookData` along with the burn. Empty `hookData` is rejected.

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

This is the channel for chaining extra actions on the destination after the mint. More in the hookData section below.

When a burn request comes in, TokenMessengerV2 does two things in order. It calls `TokenMinterV2.burn()` to destroy the USDC, then calls `MessageTransmitterV2.sendMessage()` to emit the message carrying the burn. Both the `DepositForBurn` and `MessageSent` events land in the same transaction receipt.

## MessageTransmitterV2: routing and attestation verification

MessageTransmitterV2 is CCTP's communication layer. It has no idea what a token is. It sends raw byte messages, receives them, and verifies signatures. Nothing more.

**sendMessage** is called by TokenMessengerV2 after a burn. It takes the destination domain, recipient contract address, destinationCaller, minFinalityThreshold, and message body, then emits a `MessageSent` event. The `message` bytes in that event are what a relayer needs to collect.

**receiveMessage** is called by a relayer on the destination chain:

```solidity
function receiveMessage(
    bytes calldata message,
    bytes calldata attestation
) external returns (bool success);
```

Before routing, this function verifies three things. First, that the destination domain in the message header matches the local chain. Second, that the attestation's signatures check out against Circle's attester address set. Third, that the nonce has not been used, checked against and then recorded in the `usedNonces` mapping. Submitting the same message twice reverts here. Once all three pass, it branches on `finalityThresholdExecuted`: at 2000 (`FINALITY_THRESHOLD_FINALIZED`) or above it calls `handleReceiveFinalizedMessage()`; below that, `handleReceiveUnfinalizedMessage()`.

The attesters are Circle-managed addresses registered in `enabledAttesters`. Passing requires at least `signatureThreshold` valid signatures. At the contract level this is configurable M-of-N multisig, but the threshold and attester set actually deployed should be verified against the deployed contract or Circle's official deployment documentation.

## TokenMinterV2: burn and mint execution

TokenMinterV2 performs the actual burns and mints. Its only caller is TokenMessengerV2. There is no external entry point.

`burn(address burnToken, uint256 amount)` destroys USDC on the source chain. Before burning, it checks `burnLimitsPerMessage[burnToken]` and reverts if the amount exceeds the limit. This per-chain, per-token cap is a risk control that needs no oracle. As a passive defense it stops no attack outright, but it puts a ceiling on the damage a single transaction can do.

`mint()` issues USDC on the destination. The V2 interface can mint to two recipients in one call: `mintRecipient` (the user) and `feeRecipient` (the fee collector). The fast transfer fee deduction runs on top of this dual-recipient design. Mapping the source chain token address to the local USDC address uses `remoteTokensToLocalTokens[sourceDomain][burnToken]`. Circle manages this mapping; supported token pairs are listed in the official docs.

## Message layout

CCTP messages are a binary format with a fixed-length header and a variable-length body. It is packed, parsed by byte offset, not ABI-encoded.

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

The V2 nonce changed from V1's uint64 sequential counter to a `bytes32` value. It is sent empty (`bytes32(0)`) from the source chain, and Circle's attesters fill in the real value before signing. Adding `minFinalityThreshold` and `finalityThresholdExecuted` grew the header from 116 to 148 bytes.

Domain IDs are assigned centrally by Circle. Current major EVM chains:

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
| burnToken | bytes32 | Source chain burn token address |
| mintRecipient | bytes32 | Destination recipient |
| amount | uint256 | Transfer amount |
| messageSender | bytes32 | Original `depositForBurn` caller |
| maxFee | uint256 | Sender's maximum accepted fee |
| feeExecuted | uint256 | Actual fee charged; the attester fills this in |
| expirationBlock | uint256 | Message expiry block (0 = no expiry) |
| hookData | bytes | V2 addition; variable length |

`feeExecuted` and `expirationBlock` are also sent as `0` from the source chain; Circle's attesters fill in the real values before signing. Without hookData the body is 228 bytes fixed.

The trust structure of CCTP is visible right here in the layout. Four fields, nonce, finalityThresholdExecuted, feeExecuted, and expirationBlock, are never produced on-chain. Circle's off-chain service fills them in and signs the result, and that signed result is accepted as fact on the destination chain. The attesters witness the burn and, at the same time, complete the message.

## Burn lifecycle

The sequence from the source chain to receiving USDC on the destination:

1. **Approve**: the user grants TokenMessengerV2 a USDC spending approval (`approve`).

2. **Call depositForBurn**: inside the function:
   - `TokenMinterV2.burn()` destroys the USDC
   - `MessageTransmitterV2.sendMessage()` emits the burn message
   - Both `DepositForBurn` and `MessageSent` events are emitted in the same transaction.

3. **Collect the event**: a relayer (or the user) extracts the `message` bytes from the `MessageSent` event.

4. **Request attestation**: hash the message with keccak256 and poll Circle's Iris API:
   ```
   GET https://iris-api.circle.com/attestations/{messageHash}
   ```
   The standard path waits for source chain finality. On Ethereum that takes roughly 15–20 minutes.

5. **Call receiveMessage**: once the attestation status is `complete`, call `receiveMessage(message, attestation)` on the destination chain's MessageTransmitterV2.

## Mint lifecycle

After `receiveMessage` is called on the destination:

1. **Parse the header**: confirm the destination domain matches.
2. **Verify the attestation**: signature count must meet `signatureThreshold`.
3. **Check destinationCaller**: if the header's destinationCaller is nonzero, verify `msg.sender == destinationCaller`.
4. **Check the nonce**: confirm `usedNonces[nonce]` is unused, then mark it used.
5. **Route on finality**: `finalityThresholdExecuted >= 2000` calls `handleReceiveFinalizedMessage()` (no fee, full amount minted); below that, `handleReceiveUnfinalizedMessage()`.
6. **Mint USDC**: the finalized path mints the full `amount` to mintRecipient. The unfinalized path mints `amount - feeExecuted` to mintRecipient and `feeExecuted` to feeRecipient.
7. **hookData**: hookData carried in BurnMessageV2 is processed separately by a relay wrapper (e.g. Circle's CCTPHookWrapper) after `receiveMessage()` completes. TokenMessenger and MessageTransmitter themselves perform no hook calls based on hookData.

The nonce is managed as a single bytes32 key. Submitting the same message twice fails at step 4.

## Fast transfers and the fee model

The V2 change with the biggest practical impact is fast transfers.

**Standard path**: waits until the source chain reaches finality. That is 15–20 minutes on Ethereum, and anywhere from minutes to tens of minutes on L2s like Arbitrum depending on the chain. No fee.

**Fast path**: Circle issues the attestation before source chain finality. USDC arrives on the destination in seconds to minutes. A fee applies.

The fee is deducted from the burned amount. With `amount = 100 USDC` and `fee = 1 USDC`, the mintRecipient receives `99 USDC`. Check the current fee structure and values in [Circle's developer documentation](https://developers.circle.com/stablecoins/cctp-getting-started).

What the fee actually prices is reorg risk. If Circle authorizes a mint before finality and the source chain then reorganizes away the burn transaction, minted USDC is left standing on the destination. Circle absorbs that loss. The fee is effectively the insurance premium on the risk Circle takes.

Two things follow for integrators. Settlement logic must not assume "amount sent = amount received"; on the fast path the mintRecipient gets `amount - feeExecuted`. And a maxFee below the actual fee makes fast processing impossible, so if you intend the fast path, check the current fee and set maxFee with headroom.

## destinationCaller and hookData

**destinationCaller** is a bytes32 header field that restricts who can call `receiveMessage()` on the destination.

- `0x000...000`: no restriction. Anyone holding the message and attestation can complete the mint.
- A specific address: only that address can call `receiveMessage()`. Used to pin the transfer to a relayer contract for MEV protection or controlled execution ordering.

The power comes with an operational burden. The moment you set a destinationCaller, there is no way to complete the mint unless that address makes the call. If the designated relayer goes down or loses its keys, the burn is done but the mint cannot happen, and the funds sit stuck. When pointing this at your own relayer, count its availability and key management as part of your users' fund availability.

**hookData** is the variable-length bytes field added in V2. Using `depositForBurnWithHook()` appends it to the end of the BurnMessage body. It is the channel for chaining follow-up actions on the destination after the mint. Typical patterns:

- Swap on a DEX immediately on arrival
- Deposit into a lending protocol after bridging
- Downstream steps in cross-chain payroll or payment flows

The catch: the core contracts do not execute hookData. TokenMessengerV2 stores and parses hookData in BurnMessageV2 but never performs a hook call itself. Execution belongs to a relayer wrapper. Circle's reference implementation, CCTPHookWrapper, completes `receiveMessage()` first and then runs the hook separately. If the hook fails, the USDC mint has already happened.

This non-atomicity is deliberate. If the mint and the hook were bound atomically in one transaction, an attacker could call with just barely enough gas to consume the nonce while forcing the hook to fail, killing the message permanently. Separating the hook from the mint removes that attack. In exchange, anyone building on hooks must design for "mint succeeded, hook never ran" as a state that can legitimately occur. The USDC is already at the mintRecipient, so the application layer has to decide whether a failed hook gets retried or recovered manually.

## Attestation as the trust boundary

Using CCTP ultimately means trusting Circle's attestation, the signature Circle's attesters issue after confirming a burn. It is worth drawing the boundary of that trust precisely.

The on-chain contracts verify signatures and nothing else. MessageTransmitterV2 checks that registered attesters signed this message; it has no way to confirm on its own that a burn ever happened. A message signed with attester keys is valid on the destination whether or not the burn is real. This is why CCTP's effective security depends more on Circle's key management and off-chain operations than on smart contract audits.

**Multisig configuration**: MessageTransmitterV2 supports configurable M-of-N attester signatures. The threshold and attester set actually deployed should be verified against the deployed contract or Circle's official deployment docs. Whatever the threshold, the authority to register and remove attesters stays with Circle.

**Replay protection**: the `usedNonces[nonce]` mapping on each destination chain prevents message reuse. The V2 nonce is not a sequential counter; it is a bytes32 value Circle's attesters fill in at signing time.

**Burn limits**: `burnLimitsPerMessage[token]` caps how much a single transaction can burn. It is not a device that prevents an incident, only one that shrinks it.

**Upgradeable proxies**: TokenMessengerV2 and MessageTransmitterV2 are deployed behind upgradeable proxies, meaning Circle can swap the logic. It is worth checking whether a timelock guards the proxy admin, starting from the [deployed addresses](https://developers.circle.com/stablecoins/evm-smart-contract-addresses) page.

**Off-chain dependency**: if the Iris API (`iris-api.circle.com`) that issues attestations goes down, in-flight transfers stall with it. The burn is already done and no mint can happen without an attestation, so in the meantime the funds exist on no chain at all. Circle can re-issue attestations once its infrastructure recovers, but during the outage there is no on-chain way out. A service integrating CCTP should decide in advance whether to present this window as a delay or an outage, and set up monitoring and user messaging accordingly.

## Integration checklist

Items to work through, in order, when integrating CCTP V2 directly:

1. **Get contract addresses from the official docs**: per-chain, per-version addresses live on [Circle's smart contract address page](https://developers.circle.com/stablecoins/evm-smart-contract-addresses). V1 and V2 are separate deployments, so do not mix the versions up. Manage addresses in config, not hardcoded.

2. **Approve before burning**: before calling `depositForBurn`, run `approve(tokenMessengerV2, amount)` on the USDC contract with TokenMessengerV2 as the spender.

3. **Encode mintRecipient correctly**: converting `address` to `bytes32` must be right-aligned (left-padded with zeros). In Solidity: `bytes32(uint256(uint160(addr)))`. A wrong encoding can mint the funds to an unintended address, with no way back. Non-EVM chains follow their own address encoding rules.

4. **Store the full message bytes**: save the entire `message` field from the `MessageSent(bytes message)` event verbatim. The attestation lookup key is the keccak256 hash of these bytes, so even one changed byte makes the lookup fail.

5. **Poll the attestation**: hash `message` with keccak256 and query the Iris API. Retry while status is `pending`; move on once it is `complete`. Never submit a pending attestation to the destination.

6. **Call receiveMessage with enough gas**: budget for the destination chain's gas price and limits so the call does not fail partway. If there is a hook, include the hook contract's execution cost.

7. **Handle the destinationCaller restriction**: with the default of 0, anyone can complete the transfer. If restricted to a specific address, that relayer or user must make the call, and your integration owns that address's availability.

8. **Check burn limits before large transfers**: a single transaction above `burnLimitsPerMessage` reverts. Split large transfers across multiple transactions.

## Takeaways

CCTP V2 from the contracts' point of view, in one paragraph: TokenMessengerV2 accepts the burn request and destroys USDC through TokenMinterV2, then MessageTransmitterV2 emits the message. Circle's attesters fill in the nonce and fee fields and sign. The destination chain's MessageTransmitterV2 verifies that signature, and through TokenMessengerV2, TokenMinterV2 issues native USDC.

Three tradeoffs are worth keeping in mind. There is no wrapped token and no lockbox honeypot, but you trust a single party, Circle. Fast transfers buy speed by paying the price of reorg risk as a fee. hookData opens up composability but gives up atomicity between the mint and the hook. All three are plainly visible in the code, so before integrating, verify the points in this post against the source and the official docs yourself.

## Further reading

- [circlefin/evm-cctp-contracts](https://github.com/circlefin/evm-cctp-contracts) — source code for all CCTP V2 EVM contracts (MIT license)
- [Circle CCTP developer docs](https://developers.circle.com/stablecoins/cctp-getting-started) — official integration guide
- [CCTP V2 overview](https://developers.circle.com/stablecoins/cctp-v2-overview) — what changed from V1 to V2
- [CCTP smart contract addresses](https://developers.circle.com/stablecoins/evm-smart-contract-addresses) — chain-by-chain deployed addresses

## References

- [circlefin/evm-cctp-contracts](https://github.com/circlefin/evm-cctp-contracts) — Circle, accessed 2026-06-30
- [CCTP developer docs: getting started](https://developers.circle.com/stablecoins/cctp-getting-started) — Circle Developer Docs, accessed 2026-06-30
- [CCTP EVM smart contract addresses](https://developers.circle.com/stablecoins/evm-smart-contract-addresses) — Circle Developer Docs, accessed 2026-06-30
- [CCTP V2 overview](https://developers.circle.com/stablecoins/cctp-v2-overview) — Circle Developer Docs, accessed 2026-06-30
