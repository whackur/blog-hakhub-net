---
title: "Chainlink CCIP EVM Contracts: Architecture from Source Code"
meta_title: ""
description: "A source-code walkthrough of Chainlink CCIP: how Router, OnRamp, OffRamp, TokenPool, FeeQuoter, and RMN fit together to move messages and tokens across EVM chains."
date: 2026-06-30T17:30:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
image: ""
categories: ["Blockchain"]
tags: ["chainlink", "ccip", "cross-chain", "solidity", "smart-contract"]
author: "whackur"
translationKey: "chainlink-ccip-evm-contracts"
draft: false
---

EVM chains are isolated by design. A contract on Arbitrum has no native way to call a contract on Base, and sending USDC from Ethereum Mainnet to Polygon is not a built-in operation. Cross-chain bridges filled that gap for years, but the category has seen repeated security incidents that highlight how wide the attack surface is.

Chainlink CCIP (Cross-Chain Interoperability Protocol) applies Chainlink's DON infrastructure and an independent Risk Management Network to the problem. It supports arbitrary data payloads alongside token transfers and lets you combine both in a single transaction. This post walks through the EVM contracts: what each one does, how they connect, and what matters when you are building on top of them.

## Overall architecture

CCIP contracts split into two layers. The **interface layer** is what users and dApps touch directly. The **pipeline layer** is what the DON operates behind the scenes.

Users only ever call the Router. Router hands off to OnRamp on the source chain. The DON and offchain executors observe the `CCIPMessageSent` event and submit execution data to `OffRamp.execute(encodedMessage, ccvs, verifierResults, gasLimitOverride)` on the destination chain. OffRamp calls `ccipReceive` on the receiver contract, and the cycle is done.

| Contract | Chain | Role |
|----------|-------|------|
| Router 1.2.0 | source + destination | User entry point, routes by chain selector |
| OnRamp 2.0.0 | source | Validates outbound messages, locks/burns tokens, emits events |
| OffRamp 2.0.0 | destination | Verifies via CCVs, executes inbound messages, tracks state |
| TokenPool | source + destination | Lock/burn (source), release/mint (destination) |
| FeeQuoter 2.0.0 | source | Computes cross-chain fees |
| RMN 2.0.0 | source + destination | Blocks execution when anomalies are detected |
| TokenAdminRegistry 1.5.0 | source + destination | Token address to TokenPool address mapping |

## Client message structs

The `Client.sol` library defines the message format. Send and receive use different structs.

### Sending: EVM2AnyMessage

```solidity
struct EVM2AnyMessage {
    bytes receiver;             // abi.encode(address) — bytes to support non-EVM chains
    bytes data;                 // arbitrary payload
    EVMTokenAmount[] tokenAmounts;
    address feeToken;           // address(0) = native gas token (ETH, etc.)
    bytes extraArgs;            // encoded EVMExtraArgsV1 or V2
}
```

`receiver` is `bytes` rather than `address` because CCIP targets non-EVM chains (Solana, etc.) as well. For EVM-to-EVM transfers, encode it as `abi.encode(receiverAddress)`.

`extraArgs` carries the gas limit for executing `ccipReceive` on the destination and an ordering flag. `Client.sol` defines `EVMExtraArgsV1` (gas limit only) and the multi-chain `GenericExtraArgsV2`; the v2 pipeline internally uses `GenericExtraArgsV3`, which adds CCV and executor fields.

```solidity
// GenericExtraArgsV2 (tag: 0x181dcf10): recommended for standard EVM sends
struct GenericExtraArgsV2 {
    uint256 gasLimit;                  // gas for receiver's ccipReceive call
    bool allowOutOfOrderExecution;     // if true, out-of-order execution allowed
}
```

Set `gasLimit` too low and the execution reverts on the destination chain. Set it far higher than needed and you overpay, since the fee scales with the gas limit. Use `GenericExtraArgsV2` explicitly rather than relying on defaults; the default can change across versions.

### Receiving: Any2EVMMessage

```solidity
struct Any2EVMMessage {
    bytes32 messageId;
    uint64 sourceChainSelector;
    bytes sender;              // abi.encode(address) — decode to get the address
    bytes data;
    EVMTokenAmount[] destTokenAmounts;
}
```

Recover the sender address with `abi.decode(message.sender, (address))`.

## Router: the send surface

Router is the only CCIP contract your code calls directly. The interface is `IRouterClient`.

```solidity
interface IRouterClient {
    function getFee(
        uint64 destinationChainSelector,
        Client.EVM2AnyMessage memory message
    ) external view returns (uint256 fee);

    function getSupportedTokens(uint64 chainSelector)
        external view returns (address[] memory tokens);

    function isChainSupported(uint64 chainSelector)
        external view returns (bool supported);

    function ccipSend(
        uint64 destinationChainSelector,
        Client.EVM2AnyMessage calldata message
    ) external payable returns (bytes32 messageId);
}
```

Before calling `ccipSend`:

- If `feeToken` is LINK, `approve` the Router to spend LINK.
- If `tokenAmounts` contains tokens, `approve` the Router for each.
- If `feeToken == address(0)`, pass the fee as `msg.value`.

`getFee` is a view function, so you can read it off-chain without a transaction. Because the price can shift between the `getFee` call and `ccipSend`, add a ~10% buffer to your approval or `msg.value`.

Internally, Router looks up the OnRamp registered for `destinationChainSelector` and calls `forwardFromRouter`.

## OnRamp: outbound pipeline

OnRamp validates outbound messages, processes token locks or burns, and emits the event the DON monitors.

When `forwardFromRouter` is called, OnRamp runs these steps in order:

1. **RMN curse check**: checks whether the destination chain is cursed. Reverts immediately if it is.
2. **Message validation**: checks `tokenAmounts` count, data size, `extraArgs` version, and `gasLimit` bounds.
3. **CCV list merge**: combines user-specified, lane-mandated, and pool-required CCVs, then computes fees.
4. **Fee handling**: distributes fees to each CCV, pool, executor, and the protocol network fee.
5. **Token processing**: queries `TokenAdminRegistry` for each token's pool, then calls `lockOrBurn` (one token per message).
6. **Message number**: increments `DestChainConfig.messageNumber` for the destination chain.
7. **Event emission**: emits `CCIPMessageSent` with the messageId, messageNumber, encoded message, and receipt array.

The DON picks up the `CCIPMessageSent` event and starts the execution pipeline on the destination.

## OffRamp: inbound pipeline

OffRamp lives on the destination chain. In CCIP v2, a single OffRamp instance handles messages from multiple source chains.

```solidity
function execute(
    bytes calldata encodedMessage,
    address[] calldata ccvs,
    bytes[] calldata verifierResults,
    uint32 gasLimitOverride
) external;
```

`execute` is permissionless: anyone can call it. The DON's Execute Plugin handles the normal flow.

Execution steps:

1. **RMN curse check**: if `rmnRemote.isCursed(sourceChainSelector)` is true, revert immediately.
2. **Source chain validation**: checks that the source chain is enabled, the onRamp address hash is recognized, the offRamp address matches, and the destination chain selector is correct.
3. **Execution state check**: only `UNTOUCHED` or `FAILURE` messages can proceed. `SUCCESS` is final.
4. **CCV quorum**: `_ensureCCVQuorumIsReached` verifies that all required CCVs are present.
5. **CCV verification**: calls each CCV's `verifyMessage` to check signatures.
6. **Token release/mint**: if tokens are attached, calls `releaseOrMint` on the TokenPool.
7. **Receiver call**: for non-token-only transfers, calls `receiver.ccipReceive(message)` within the `gasLimit` via `router.routeMessage`.
8. **State update**: records `SUCCESS` or `FAILURE`.

Execution state uses `MessageExecutionState`: `UNTOUCHED(0)`, `IN_PROGRESS(1)`, `SUCCESS(2)`, `FAILURE(3)`. Failed messages can be retried via `manuallyExecute`.

## TokenPool: four modes of token handling

TokenPool handles token movement across chains. The abstract base class `TokenPool.sol` defines the shared interface; four concrete implementations handle different token designs.

The pool interface:

```solidity
function lockOrBurn(Pool.LockOrBurnInV1 calldata lockOrBurnIn)
    external returns (Pool.LockOrBurnOutV1 memory);

function releaseOrMint(Pool.ReleaseOrMintInV1 calldata releaseOrMintIn)
    external returns (Pool.ReleaseOrMintOutV1 memory);
```

**LockReleaseTokenPool**: locks tokens on the source chain and releases them on the destination. Total supply stays constant across both chains. For tokens that were originally deployed on one chain only (WBTC, for example).

**BurnMintTokenPool**: burns on source, mints on destination. The token must exist natively on multiple chains, and the pool contract must have mint authority on the destination.

**BurnWithFromMintTokenPool**: burns using a `transferFrom` + burn sequence. For token contracts that do not support `burnFrom` directly but do allow a pool to move and burn with explicit allowance.

**BurnFromMintTokenPool**: burns by calling `burnFrom` directly. Requires the token contract to support `burnFrom` and the pool to hold an allowance.

Which mode to pick depends on the token contract's design and where mint authority lives. External bridged tokens typically use LockRelease; tokens purpose-built for multi-chain use BurnMint.

**Rate limiting**

Every TokenPool can configure inbound and outbound rate limits per chain. The token bucket algorithm caps how much value can move per unit time. Exceeding the limit causes a revert. The limits are configurable on-chain by the pool administrator.

## FeeQuoter: fee computation

FeeQuoter took over from `PriceRegistry` in v1.5. It computes cross-chain fees and holds the price data the rest of the system uses.

A cross-chain fee has three parts:

- **Network fee**: a fixed protocol cost.
- **Destination gas cost**: `extraArgs.gasLimit × destination gas price`, converted into the source chain's fee token.
- **Token transfer fee**: per-token fee based on amount and token configuration.

The DON updates price data periodically. FeeQuoter 2.0.0 removed the stale price revert check. Price freshness is now the DON's responsibility rather than a hard on-chain guard.

## RMN: Risk Management Network

RMN is CCIP's independent security layer. A separate set of nodes (distinct from the DON) monitors both the source and destination chains.

If nodes detect anomalies such as chain reorganizations or abnormally large outflows, they vote to curse a lane or an entire chain.

```solidity
interface IRMNRemote {
    function isCursed() external view returns (bool);
    function isCursed(bytes16 subject) external view returns (bool);
    function verify(
        address offRampAddress,
        Internal.MerkleRoot[] memory merkleRoots,
        Internal.SignedMerkleRoot[] memory signatures,
        uint256 rawVs
    ) external view;
}
```

The `subject` parameter in `isCursed(bytes16 subject)` is a combination of the source chain selector and lane identifier. OffRamp checks this at the start of every execution call and reverts if cursed.

`verify` is called internally by OffRamp as part of message verification through CCVs (`verifyMessage`). Router, OnRamp, OffRamp, and TokenPool all check RMN curse state directly via `isCursed` and revert immediately if a curse is active. This means even if the DON were compromised, RMN can still block execution independently.

In v2, each chain has a deployed `RMNRemote` that verifies signatures locally, while a remote `RMNHome` manages the RMN node set configuration.

## CCIPReceiver: the receiver contract pattern

Any contract that receives CCIP messages must implement `IAny2EVMMessageReceiver`. Extending Chainlink's `CCIPReceiver` abstract contract takes care of the plumbing:

```solidity
abstract contract CCIPReceiver is IAny2EVMMessageReceiver {
    address internal immutable i_ccipRouter;

    modifier onlyRouter() {
        if (msg.sender != i_ccipRouter) revert InvalidRouter(msg.sender);
        _;
    }

    function ccipReceive(Client.Any2EVMMessage calldata message)
        external virtual override onlyRouter
    {
        _ccipReceive(message);
    }

    function _ccipReceive(Client.Any2EVMMessage memory message) internal virtual;
}
```

The `onlyRouter` modifier is what actually matters here. `ccipReceive` must only accept calls from the Router. Skip this check and anyone can call your contract with an arbitrary message.

Beyond that, a few patterns are worth enforcing:

**Sender validation**: decode `message.sender` and check it against a whitelist of trusted source chains and sender addresses. Reject anything unexpected.

**Idempotency**: if `_ccipReceive` can be called twice for the same messageId (via `manuallyExecute`), make sure the second call does not double-apply state changes.

**Duplicate execution guard**: track processed messageIds. Be aware that returning early without reverting marks the message as `SUCCESS`, which prevents future retries.

**Revert behavior**: if `_ccipReceive` reverts, OffRamp records the message as `FAILURE`. A `manuallyExecute` retry will run the same logic under the same gas limit, so investigate the root cause before retrying.

## Message ordering

Message ordering in v2 is managed through `DestChainConfig.messageNumber` in OnRamp and `s_executionStates` in OffRamp. There is no separate NonceManager contract.

The `allowOutOfOrderExecution` flag and finality/ordering policy are encoded in `extraArgs` and lane configuration. Check the Chainlink documentation and CCIP Directory for the actual behavior on specific lanes. When `allowOutOfOrderExecution` is false, messages from the same sender to the same destination chain execute in order. If message N fails, message N+1 stays in `UNTOUCHED` state until N is resolved.

Setting `allowOutOfOrderExecution` to true skips the ordering check. This is fine for standalone token transfers or any case where order genuinely does not matter.

For workflows where order is load-bearing (sequential payments, state machine transitions), keep the default and design an explicit recovery path for the case where an earlier message stays `FAILURE`.

## Integration checklist

Items to verify before going to production.

**Approvals**
- [ ] Router approved to spend LINK (if using LINK as fee token)
- [ ] Router approved to spend each transfer token
- [ ] `isChainSupported(destChainSelector)` returns true
- [ ] Transfer tokens confirmed in `getSupportedTokens(destChainSelector)`

**Fees**
- [ ] `getFee` result plus buffer (~10%) used for approval amount or `msg.value`

**Receiver contract**
- [ ] `onlyRouter` modifier on `ccipReceive`
- [ ] `sourceChainSelector` and sender address whitelist checked
- [ ] messageId-based duplicate execution guard
- [ ] `_ccipReceive` logic is idempotent
- [ ] `extraArgs.gasLimit` is large enough for the receiver's actual gas usage

**Error recovery**
- [ ] An EOA or multisig has authority to call `manuallyExecute` for failed messages
- [ ] Plan for token state if execution fails after `lockOrBurn` but before `releaseOrMint`

**Testing**
- [ ] End-to-end test on testnet using Chainlink's `CCIP-BnM` burn-and-mint test token
- [ ] Router address upgrade path accounted for in contract design

## Further reading

- [Chainlink CCIP Documentation](https://docs.chain.link/ccip) — architecture, API reference, supported networks
- [CCIP Source Code (smartcontractkit/chainlink)](https://github.com/smartcontractkit/chainlink/tree/develop/contracts/src/v0.8/ccip) — Router, OnRamp, OffRamp, TokenPool implementations
- [CCIP Hardhat Starter Kit](https://github.com/smartcontractkit/ccip-starter-kit-hardhat) — send and receive example contracts
- [CCIP Explorer](https://ccip.chain.link) — cross-chain message tracker
- [CCIP Best Practices](https://docs.chain.link/ccip/best-practices) — official guidance on security and integration patterns

## References

- [Chainlink CCIP Architecture](https://docs.chain.link/ccip/architecture) — docs.chain.link, accessed 2026-06-30
- [Chainlink CCIP API Reference](https://docs.chain.link/ccip/api-reference) — docs.chain.link, accessed 2026-06-30
- [Chainlink CCIP Best Practices](https://docs.chain.link/ccip/best-practices) — docs.chain.link, accessed 2026-06-30
- [CCIP Supported Networks](https://docs.chain.link/ccip/supported-networks) — docs.chain.link, accessed 2026-06-30
- [CCIP Source Code (smartcontractkit/chainlink)](https://github.com/smartcontractkit/chainlink/tree/develop/contracts/src/v0.8/ccip) — github.com/smartcontractkit, accessed 2026-06-30
- [CCIP Starter Kit (Hardhat)](https://github.com/smartcontractkit/ccip-starter-kit-hardhat) — github.com/smartcontractkit, accessed 2026-06-30
