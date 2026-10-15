---
title: "Glamsterdam's New Gas Model: EIP-8037 State Gas, EIP-8038 Access Costs, EIP-2780 Intrinsic Gas"
meta_title: ""
description: "How three Glamsterdam proposals change Solidity storage writes, deletion and fixed-gas calls. Execution and state budgets, final charges, specification status and network activation explained."
date: 2026-10-15T01:19:45+09:00
lastmod: 2026-10-15T16:10:31Z
image: "/images/posts/glamsterdam-gas-model/glamsterdam-resource-costs-20261015.webp"
categories: ["Blockchain"]
tags: ["ethereum", "glamsterdam", "gas", "evm", "eip-8037", "eip-8038", "eip-2780"]
author: "whackur"
translationKey: "glamsterdam-gas-model"
draft: false
---

Glamsterdam's three gas proposals make **new persistent state more expensive and raise the cost of updating existing state**, while lowering the base cost of some transactions that do less work. A fresh cold storage write has specified components of 12,100 execution gas plus 97,920 state gas; the first cold change away from an existing slot’s nonzero transaction-start value costs 12,100 execution gas and no state gas. Both still draw on the transaction's single `gasLimit`, but `gasleft()` does not report the separate state-gas reservoir. These are specification costs, not measured Solidity function totals or an announcement that the rules are active on mainnet. [EIP-8037](https://eips.ethereum.org/EIPS/eip-8037), [EIP-8038](https://eips.ethereum.org/EIPS/eip-8038) and [EIP-2780](https://eips.ethereum.org/EIPS/eip-2780) define the changes together.

## Specification status and network activation

As checked on October 15, 2026 UTC, the three proposal texts at ethereum/EIPs commit [`8b1cae5`](https://github.com/ethereum/EIPs/tree/8b1cae50601fb194452db0ed857f4c237ca62c1f/EIPS) have the following status:

| Question | Published record |
| --- | --- |
| How far along are the specifications? | All three are `Last Call`, with a November 1, 2026 deadline. EIP-8037 still calls its dependent parameters nonfinal; EIP-2780 calls its pricing inputs provisional. |
| Are they in Glamsterdam's planned scope? | All three are Scheduled for Inclusion in [EIP-7773](https://eips.ethereum.org/EIPS/eip-7773). The meta EIP itself is `Review`. |
| What activation time is published? | Sepolia: epoch 353,024, timestamp 1,791,294,816, October 6, 2026 at 13:53:36 UTC. The Hoodi and Mainnet rows are blank. |

The [Ethereum Foundation's testnet announcement](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement) explicitly covers Sepolia and does not schedule mainnet. Sepolia's published activation time has passed, making it the announced test network for these changes. A schedule alone does not establish which subsequent specification revisions a particular client or RPC provider implements. The examples below explain the checked specification; they do not claim a live-chain before/after benchmark. Inclusion in a fork, document finalization and activation on a named network are separate facts.

## From a transaction envelope to an execution budget

The proposals address different parts of the same transaction. EIP-2780 prices inclusion and moves state-dependent charges to runtime. EIP-8038 prices state access and writes. EIP-8037 prices new state and supplies the two-dimensional accounting.

For a plain transaction without calldata, access-list entries, authorizations or recipient code execution, EIP-2780 replaces the flat 21,000 with these components:

| Transaction shape | Execution gas | State gas | Combined gas |
| --- | ---: | ---: | ---: |
| Transfer to self, ordinary nondelegated sender | 12,000 | 0 | 12,000 |
| Zero-value call to a different ordinary EOA or empty address | 12,000 + 3,000 | 0 | 15,000 |
| Positive ETH transfer to a different existing ordinary EOA | 12,000 + 3,000 + 6,000 | 0 | 21,000 |
| Positive ETH transfer that creates an account | 21,000 | 183,600 | 204,600 |

An EOA is an externally owned account. The 12,000 base covers the sender and inclusion work; 3,000 covers the recipient touch; 6,000 covers the recipient balance write and the [EIP-7708](https://eips.ethereum.org/EIPS/eip-7708) transfer log. A call to contract code adds its execution. A delegated EIP-7702 recipient also adds a runtime delegation-target access, 3,000 when cold or 100 when already warm, followed by the delegated code's execution. These extra conditions are why “ETH transfers now cost 12,000” would be misleading. [EIP-2780's reference cases](https://eips.ethereum.org/EIPS/eip-2780#transaction-reference-cases) distinguish them explicitly.

Intrinsic gas is computable from transaction fields without reading state. The recipient touch is charged intrinsically at the cold rate even if the address appears in an access list. Whether an account must be created is determined later, during pre-execution, after the transaction has passed its inclusion checks but before the first EVM call frame.

A fresh-address transfer with a 21,000 limit can therefore pass the gas-related intrinsic check and then run out of gas on the 183,600 state charge. Provided it passes the other validity checks and is included, it fails, increments the sender nonce and consumes gas fees; the ETH transfer does not complete. A rejected invalid transaction and an included failed transaction have different consequences. Wallets need an estimator that accounts for both dimensions, rather than a constant for every ETH transfer. [EIP-2780](https://eips.ethereum.org/EIPS/eip-2780#runtime-gas-costs)

## The same Solidity assignment has different storage paths

This small contract supplies three operations without unrelated business logic:

```solidity
pragma solidity 0.8.30;

contract Slot {
    uint256 public value;

    function write(uint256 next) external {
        value = next;
    }

    function clear() external {
        delete value;
    }
}
```

The comparisons below refer to the `SSTORE` opcode that changes `value`, not to the whole function. Function dispatch, ABI decoding, stack operations and any memory work add execution gas. Transaction intrinsic gas and calldata also contribute to the final receipt. The examples compile with Solidity 0.8.30, optimizer enabled with 200 runs, `viaIR: false` and `evmVersion: "prague"`. Compilation checks the code and emitted instructions; no old/new fork runtime measurements are claimed.

For the cold rows, assume no access list and no earlier touch of this storage key in the transaction. “Original” means the value at transaction start; “current” means the value immediately before this `SSTORE`. Earlier transactions establish the initial values but do not preserve warmth into a new transaction. The comparison schedule before these proposals follows [EIP-2200](https://eips.ethereum.org/EIPS/eip-2200), [EIP-2929](https://eips.ethereum.org/EIPS/eip-2929) and [EIP-3529](https://eips.ethereum.org/EIPS/eip-3529).

| Operation and initial condition | Earlier schedule, execution gas | Proposed execution gas | Proposed state gas |
| --- | ---: | ---: | ---: |
| `write(7)`, original = current = 0, cold | 22,100 | 2,100 + 10,000 = 12,100 | 97,920 |
| `write(9)`, original = current = 7, cold | 5,000 | 12,100 | 0 |
| Same nonzero update, key warmed by a prior read in this transaction | 2,900 | 100 + 10,000 = 10,100 | 0 |
| `clear()`, original = current = 7, cold | 5,000, plus a 4,800 refund credit | 12,100, plus an 11,616 refund credit | 0 |

### New slots and existing values

On a fresh deployment, call `write(7)` while `value` is still zero. EIP-8037 assigns 64 accounting bytes to a new storage leaf and its key. At `CPSB` (cost per state byte) = 1,530, that is 64 × 1,530 = 97,920 state gas. EIP-8038 adds the cold access and first-write components, giving 110,020 across the two dimensions for this opcode. The function needs more than that amount in total.

For the existing-value case, first call `write(7)` in a separate transaction and let it complete. Then call `write(9)` in the transaction being evaluated. There is no new storage leaf to charge, but the first change from the original value still pays `STORAGE_WRITE` = 10,000. Avoiding state creation does not avoid the execution repricing. A prior read in the same transaction makes the later write warm; that read itself also costs gas. [EIP-8038's SSTORE rules](https://eips.ethereum.org/EIPS/eip-8038#sstore-pricing)

Further writes to an already modified slot do not all pay another 10,000. For example, original 7 → current 9 → new 11 pays only warm access on the second write. Restoring 7 credits `STORAGE_WRITE` to the refund counter. Returning to the original value and moving away again can trigger a new write charge. The rules follow original/current/new values throughout the transaction, rather than charging each source-level assignment independently.

### Deletion credits the deleting transaction

Initialize `value` to 7 in an earlier transaction, then call `clear()`. The proposed 11,616 is a credit to that transaction's refund counter, not an immediate addition to the call frame's remaining gas. The applied credit is capped at one fifth of pre-refund gas used, and a calldata floor can reduce its benefit further. For example, a hypothetical transaction using 30,000 before refunds with an 11,616 counter receives only 6,000, leaving 24,000 charged if the floor is nonbinding. This is settlement arithmetic, not a measurement of `clear()`. [EIP-8037 settlement](https://eips.ethereum.org/EIPS/eip-8037#transaction-gas-used)

Reading `value` later is not discounted because it now contains zero. A cold `SLOAD` remains 2,100 and a warm one 100; the getter's other instructions are additional. An on-chain getter call consumes gas. An off-chain `eth_call` executes a simulation without charging the caller an on-chain transaction fee, subject to the node's simulation limits.

### Setting and clearing within one transaction

If the slot starts at zero, is set to 7 and returns to zero within the same transaction, two mechanisms apply to the clearing write:

- EIP-8037 refills 97,920 state gas because the new leaf is no longer needed.
- EIP-8038 charges 100 warm execution gas and credits 10,000 to the capped refund counter because the original value is restored.

This path does not also receive the 11,616 credit for deleting a slot that was nonzero at transaction start. By contrast, clearing an original-nonzero slot and setting it again reverses its deletion credit and creates no new state-gas charge. A persistent clear and a same-transaction round trip are different cases. [EIP-8037](https://eips.ethereum.org/EIPS/eip-8037#gas-accounting-for-sstore-opcode-level), [EIP-8038](https://eips.ethereum.org/EIPS/eip-8038#sstore-pricing)

## A fixed internal allowance can fail independently of the outer limit

The caller's reaction to a failed child call matters as much as the limit. This wrapper calls the `Slot` contract above:

```solidity
pragma solidity 0.8.30;

contract FixedAllowance {
    uint256 public marker;
    uint256 public immutable childGasCap;

    constructor(uint256 cap) {
        childGasCap = cap;
    }

    function run(address target, uint256 next, bool mustSucceed)
        external returns (bool ok)
    {
        marker = next;
        (ok,) = target.call{gas: childGasCap}(
            abi.encodeWithSignature("write(uint256)", next)
        );
        if (mustSucceed) require(ok, "child failed");
    }
}
```

Use the actual `Slot` address as `target`, not an address without code. Initialize both `Slot.value` and `FixedAllowance.marker` to 7 in earlier transactions, then call `run(target, 9, ...)`. In each comparison start from that same state, with the child's slot cold, and give the outer transaction enough gas to forward the full immutable allowance after the caller's costs and the 63/64 rule. Both writes change existing nonzero values, so this example isolates execution repricing from new-state charges.

A cap large enough for the earlier compiled child path but below the repriced path's requirement can make that child succeed before repricing and fail with out-of-gas afterward. No numeric threshold or reproduced regression is claimed here. It depends on the full emitted child code, not just the table's `SSTORE`. Increasing the outer transaction limit does not increase `childGasCap`; the cap or call design needs to change.

With `mustSucceed = false`, a child OOG returns `false`; the wrapper can finish and retain `marker = 9` while the child's write is rolled back. With `mustSucceed = true`, `require(ok)` reverts the wrapper frame too, rolling back its marker. These outcomes assume sufficient caller gas to finish handling the result. A child's `REVERT` returns unused execution gas; an exceptional halt such as OOG consumes the forwarded execution allowance. Neither outcome makes a low-level call automatically revert its caller. [EIP-140](https://eips.ethereum.org/EIPS/eip-140), [EIP-8037 rollback rules](https://eips.ethereum.org/EIPS/eip-8037#gas-accounting-for-halts-and-reverts)

The unchanged 2,300 stipend is not a suitable regression example for this write. The `SSTORE` guard already rejects a frame with at most 2,300 execution gas; a reservoir does not bypass that guard. A write that already failed under the earlier rules is not a new Glamsterdam failure.

## The reservoir changes what gasleft can observe

[EIP-8037](https://eips.ethereum.org/EIPS/eip-8037#transaction-level-gas-accounting-reservoir-model) splits the supplied gas after intrinsic cost:

```text
C = 16,777,216
evm_gas = tx.gas - intrinsic_gas
gas_left = min(C - intrinsic_gas, evm_gas)
state_gas_reservoir = evm_gas - gas_left
```

For a valid transaction at or below `C`, the reservoir starts at zero. State charges therefore draw from `gas_left` alongside execution charges. Above `C`, the excess goes to the reservoir. With a hypothetical intrinsic cost of 15,000 and `tx.gas` of 20,000,000, the initial pools are 16,762,216 and 3,222,784, before runtime charges. The 15,000 assumption excludes calldata and other additions; it is not a full ABI call estimate.

Execution charges can use only `gas_left`. State charges use the reservoir first and draw any shortfall from `gas_left`. Supplying more than the cap therefore adds state capacity, not more execution capacity. Total `tx.gas` is capped at 4,294,967,295, while block inclusion must also fit the remaining budget in each dimension. The usual balance, nonce and fee checks still apply.

`gasleft()`, implemented by the `GAS` opcode, sees only `gas_left`. The entire reservoir passes to a child; only its execution allowance is subject to the 63/64 rule. A small fixed execution cap consequently does not cap all the state gas the child can consume from a funded shared reservoir.

A refill credits `gas_left` first, up to the state charges that this frame funded from it, then credits the reservoir. This can make `gasleft()` rise. In the specification's sequence `SSTORE(k, 1); GAS; SSTORE(k, 0); GAS`, where the slot originally was zero and the reservoir was empty, the second reading includes the 97,920 refill less intervening execution costs. Measuring around both writes instead includes both the charge and its reversal. Successful child-frame merges can also move restored state budget into the caller's `gas_left`. A subtraction such as `beforeGas - gasleft()` can then underflow under Solidity's checked arithmetic. [EIP-8037's metering warning](https://eips.ethereum.org/EIPS/eip-8037#gas_left-can-increase)

On rollback, the frame restores its reservoir baseline and reverses the state charges for rolled-back changes. A reverting child returns its resulting unused execution gas; an exceptionally halted child consumes it. Successful child merges need extra accounting because one frame can clear state created by an earlier frame. These rules prevent a failed clearing call from leaving behind a refill for state that its rollback restored.

## Unused budget, refunds and the final charge

Three amounts that can reduce a bill have different rules:

| Amount | When it applies | Main limitation |
| --- | --- | --- |
| Unused allowance | Settlement returns the unspent execution and reservoir budgets | It is unused budget, not a deletion credit subject to the 20% refund cap |
| Refund counter | Settlement applies credits such as clearing an original-nonzero slot | At most 20% of pre-refund usage; the calldata floor applies afterward |
| State refill | Execution reverses a state charge, such as a new slot cleared in the same transaction | Follows the source-pool and rollback rules; it is separate from the capped counter |

Using the final frame's remaining pools, EIP-8037 specifies:

```text
used_before_refund = tx.gas - gas_left - state_gas_reservoir
refund = min(used_before_refund // 5, refund_counter)
charged_gas = max(used_before_refund - refund, calldata_floor_gas_cost)
```

A refill is already reflected in those remaining pools and state accounting; it is not subtracted again as a refund-counter credit. The sender pays `charged_gas × effectiveGasPrice`. Higher gas units do not establish a fixed ETH or fiat cost increase, since the effective gas price also changes. The floor limits how far a data-heavy transaction's charge can fall. EIP-2780 replaces the floor's old 21,000 base with the transaction's applicable decomposed base; calldata pricing also has a separate scheduled change, [EIP-7976](https://eips.ethereum.org/EIPS/eip-7976).

Block capacity uses a different aggregation: the header's `gas_used` is the larger of accumulated execution gas and accumulated state gas. Each dimension must fit the block limit, and this maximum feeds the base-fee update. With the scheduled [EIP-7778](https://eips.ethereum.org/EIPS/eip-7778), capped refund-counter credits do not reduce the execution contribution to block usage; state refills still reduce net state usage. Receipt `cumulative_gas_used` instead adds the amounts charged to transactions after refunds and the floor. Its difference between consecutive receipts is the transaction's paid gas, not a contribution to the block's maximum. [EIP-8037's integration and receipt rules](https://eips.ethereum.org/EIPS/eip-8037#integration-with-eip-7778)

## Deployment, accounts and delegated code

The state-byte weights also affect operations beyond `SSTORE`:

| State being added | Specified state charge |
| --- | ---: |
| New account leaf and key, 120 accounting bytes | 183,600 |
| New storage leaf and key, 64 accounting bytes | 97,920 |
| New EIP-7702 delegation indicator, 23 bytes | 35,190 |
| Deposited runtime code | 1,530 per byte |

These weights are not a count of all physical database bytes: EIP-8037 excludes intermediate trie nodes. Its price derivation targets 120 GiB of annual state growth at a reference 150M block limit with assumed average utilization. That reference is a pricing input, not a statement of the current mainnet limit or a guaranteed growth ceiling. EIP-8038 separately uses client benchmarks to price the work of accessing and updating state. [EIP-8037 rationale](https://eips.ethereum.org/EIPS/eip-8037#rationale), [EIP-8038 rationale](https://eips.ethereum.org/EIPS/eip-8038#rationale)

For a top-level deployment to a nonexistent address with 24,576 bytes of deposited code, the account and code state charge is 183,600 + 24,576 × 1,530 = 37,784,880. Execution components include the 24,000 transaction base plus creation access, and a code hash cost of 6 × ceil(24,576 / 32) = 4,608. Initcode calldata, initcode word charges, constructor instructions and other work remain additional. This is a component calculation, not a deployment estimate. Separating the dimensions lets a sufficiently funded reservoir pay code-deposit state gas beyond the 16,777,216 execution cap; it does not remove contract-size limits.

An address with a nonzero balance already counts as existing, even with zero nonce and empty code. A valid deployment to such a prefunded address avoids the new-account charge but still pays code deposit and execution. Prefunding itself creates the account when necessary, so it does not eliminate that earlier state cost. For internal `CREATE`/`CREATE2`, the conditional account charge happens in the creating frame before gas forwarding, after the prerequisite checks and destination access. A failure to fund that charge can halt the creator; it should not be described merely as a child returning a failure flag. A same-transaction `SELFDESTRUCT` does not refill the created account's state charge under the checked text. [EIP-8037 account rules](https://eips.ethereum.org/EIPS/eip-8037#gas-accounting-for-new-accounts)

For ordinary internal calls, cold account access rises from 2,600 to 3,000; warm access remains 100. A value-bearing `CALL` also pays a `CALL_VALUE` execution component of 9,000 + 2,300 = 11,300, with state gas added if it creates an account. Account-write charges apply per operation, unlike the transaction-scoped storage-write accounting. `EXTCODESIZE` and `EXTCODECOPY` add 100 for their second database read, besides the account access and any other copy or memory costs. These are opcode components, not total transfer or copy fees. [EIP-8038 account pricing](https://eips.ethereum.org/EIPS/eip-8038#account-access-pricing)

EIP-7702 authorization processing has its own boundaries. Each authorization pays 7,816 intrinsic execution gas. For valid authorizations, account creation can add 183,600 state gas, a first account write can add 9,000 execution gas, and net-new delegation bytes can add 35,190 state gas, each at most once per authority under the specified conditions. The account-write charge is skipped if already covered by the sender base, an earlier authorization or the value-bearing recipient charge. An indicator present at transaction start can be cleared and reset without paying for new delegation bytes again; clearing does not earn a refill for that indicator.

Authorizations are processed before the first EVM frame. Failure during pre-execution rolls them back. A later top-level frame revert or OOG preserves the already applied authorizations, so their state charges remain consumed; rollback must not refill state that persists. Resolving delegated code at runtime is a separate access from setting its pointer. [EIP-2780 authorization rules](https://eips.ethereum.org/EIPS/eip-2780#eip-7702-authorization-processing)

## Tests that expose the changed assumptions

For a contract maintainer, the useful comparison is the same operation under both schedules with identical compiler settings, transaction input and initial state. Include new slots, earlier-transaction nonzero updates, clears, same-transaction round trips, and cold versus deliberately warmed paths. For fixed internal calls, record both the child success flag and the caller's resulting state, as well as the receipt. A fee estimate alone cannot establish correct failure handling.

Wallet and RPC maintainers need `eth_estimateGas` to cover both dimensions and the state-dependent pre-execution charges. A successful `eth_call` is not evidence that a transaction with a chosen limit will be included and succeed; simulation gas policies can differ by client and provider. Test the actual node version and fork configuration. For ERC-4337 bundlers, `gasleft()` differences cannot attribute state spending funded by the bundle's shared reservoir, and one operation's refill can affect another. EIP-8037 explicitly requires bundlers and `EntryPoint` implementations to account for state gas rather than relying on those differences alone. [Compatibility](https://eips.ethereum.org/EIPS/eip-8037#backwards-compatibility), [bundle accounting](https://eips.ethereum.org/EIPS/eip-8037#interaction-with-erc-4337-bundles)

Deployment tooling needs a separate check for presigned factory transactions with fixed limits. EIP-8037 warns that their original limits can be insufficient on new networks that start with the repricing active. Already deployed factories are not redeployed by a fork. The practical migration work is therefore to identify where a system creates state, where it hardcodes an allowance, and where it treats `gasleft()` as the whole budget.

## Further reading

- [EIP-7825: Transaction Gas Limit Cap](https://eips.ethereum.org/EIPS/eip-7825): the execution cap that the reservoir model retains.
- [EIP-7928: Block-Level Access Lists](https://eips.ethereum.org/EIPS/eip-7928): state-access recording and the timing constraints around creation.
- [EIP-7778: Block Gas Accounting without Refunds](https://eips.ethereum.org/EIPS/eip-7778): why paid transaction gas and block capacity accounting differ.

## References

- [EIP-8037](https://eips.ethereum.org/EIPS/eip-8037), [immutable text](https://github.com/ethereum/EIPs/blob/8b1cae50601fb194452db0ed857f4c237ca62c1f/EIPS/eip-8037.md): Ethereum EIPs, accessed October 15, 2026 UTC.
- [EIP-8038](https://eips.ethereum.org/EIPS/eip-8038), [immutable text](https://github.com/ethereum/EIPs/blob/8b1cae50601fb194452db0ed857f4c237ca62c1f/EIPS/eip-8038.md): Ethereum EIPs, accessed October 15, 2026 UTC.
- [EIP-2780](https://eips.ethereum.org/EIPS/eip-2780), [immutable text](https://github.com/ethereum/EIPs/blob/8b1cae50601fb194452db0ed857f4c237ca62c1f/EIPS/eip-2780.md): Ethereum EIPs, accessed October 15, 2026 UTC.
- [EIP-7773](https://eips.ethereum.org/EIPS/eip-7773), [immutable text](https://github.com/ethereum/EIPs/blob/8b1cae50601fb194452db0ed857f4c237ca62c1f/EIPS/eip-7773.md): fork scope and activation table, accessed October 15, 2026 UTC.
- [Glamsterdam Testnet Announcement](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement): Ethereum Foundation, accessed October 15, 2026 UTC.
- [EIP-2200](https://eips.ethereum.org/EIPS/eip-2200), [EIP-2929](https://eips.ethereum.org/EIPS/eip-2929), [EIP-3529](https://eips.ethereum.org/EIPS/eip-3529): baseline storage and refund rules, accessed October 15, 2026 UTC.
- [EIP-140](https://eips.ethereum.org/EIPS/eip-140): `REVERT`, accessed October 15, 2026 UTC.
- [EIP-7623](https://eips.ethereum.org/EIPS/eip-7623), [EIP-7976](https://eips.ethereum.org/EIPS/eip-7976), [EIP-7708](https://eips.ethereum.org/EIPS/eip-7708): calldata floor and transfer logs, accessed October 15, 2026 UTC.
