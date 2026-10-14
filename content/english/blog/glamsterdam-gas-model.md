---
title: "Glamsterdam's New Gas Model: EIP-8037 State Gas, EIP-8038 Access Costs, EIP-2780 Intrinsic Gas"
meta_title: ""
description: "How Glamsterdam splits gas into execution gas and state gas, reprices state access, and breaks up the flat 21,000 intrinsic cost. Exact parameters, the reservoir model, refunds and reverts, developer impact, and what is still undecided, from the specs as of October 15, 2026."
date: 2026-10-15T01:19:45+09:00
lastmod: 2026-10-15T01:19:45+09:00
image: "/images/posts/glamsterdam-gas-model/glamsterdam-gas-cover.png"
categories: ["Blockchain"]
tags: ["ethereum", "glamsterdam", "gas", "evm", "eip-8037", "eip-8038", "eip-2780"]
author: "whackur"
translationKey: "glamsterdam-gas-model"
draft: false
---

Glamsterdam, the next Ethereum network upgrade, changes how a transaction's gas is counted, not just what individual operations cost. Three proposals do most of the work. [EIP-8037](https://eips.ethereum.org/EIPS/eip-8037) gives state creation its own gas dimension and prices it per byte. [EIP-8038](https://eips.ethereum.org/EIPS/eip-8038) raises the cost of reading and writing state that already exists. [EIP-2780](https://eips.ethereum.org/EIPS/eip-2780) replaces the flat 21,000 intrinsic transaction cost with a sum of named parts, and moves the state-dependent parts out of the validity check.

Any one of these would be a normal repricing. Together they change the shape of a transaction's gas budget: `tx.gas` is still one number, but the protocol now splits it into two pools, and the `GAS` opcode only sees one of them. Contracts that measure `gasleft()`, wallets that hardcode gas limits, bundlers, block builders and RPC simulators all have something to check.

This post walks through the three specifications as they stand on October 15, 2026. All numbers come from the EIP texts at ethereum/EIPs commit [`5ef3801`](https://github.com/ethereum/EIPs/commit/5ef380124bd68d09c02fa90d0de0f2455f37d5ee) and are cross-checked against the Amsterdam fork code in [ethereum/execution-specs](https://github.com/ethereum/execution-specs/tree/16898000911c1e3caa57be08509536c10ae92d3e/src/ethereum/forks/amsterdam). Where public sources disagree, I say so.

## Status as of October 15, 2026

Three different "statuses" get mixed up in coverage of this fork. They answer different questions, so here they are separately.

**EIP process status.** EIP-8037, EIP-8038 and EIP-2780 are all `Last Call`, with a `last-call-deadline` of 2026-11-01. The move to Last Call landed in a single commit dated 2026-10-06 ([ethereum/EIPs PR #12442](https://github.com/ethereum/EIPs/pull/12442)). Last Call means the text is close to final, not that it is frozen. EIP-8037 itself still says the EIP-8038 values it depends on "are not yet final", and EIP-2780 calls its own base numbers "provisional".

**Fork inclusion.** The Glamsterdam meta EIP, [EIP-7773](https://eips.ethereum.org/EIPS/eip-7773), lists all three under "EIPs Scheduled for Inclusion" (SFI). EIP-8037 was marked Considered for Inclusion in January 2026 and was already scheduled by June, according to its author in the discussion thread. EIP-2780 and EIP-8038 moved from considered to scheduled in a 2026-08-05 commit to EIP-7773. EIP-7773 itself is in `Review` status.

**Network activation.** EIP-7773's activation table has one filled row: Sepolia at epoch 353024, timestamp 1791294816 (2026-10-06 13:53:36 UTC). The Hoodi and Mainnet rows are blank, and the meta EIP notes that rows "will be filled as activation times are decided by client teams." The [Ethereum Foundation's testnet announcement](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement) says the same thing in plain words: "Hoodi and mainnet activation dates have not yet been decided," and the announcement "does not schedule a mainnet upgrade."

So "scheduled for inclusion" is a decision about scope. It is not a mainnet date, and no official source gives one yet. The copy of ethereum.org's [Glamsterdam page](https://ethereum.org/en/roadmap/glamsterdam/) I read on October 14 (marked as last updated September 14) said "Expected on mainnet Q4 2026 · Date not yet confirmed," which is an expectation, not a schedule. One community member, PyraVim, [reported on Ethereum Magicians](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/50) (post #50, October 8, 2026) that Glamsterdam went live on Sepolia at the scheduled time and posted measurements from the first hours. That is useful field data, but it comes from a single observer.

## Why the gas schedule is changing

The motivation sections of the three EIPs point at two separate problems.

The first is **state growth**. EIP-8037 reports that a Geth node's state database was about 390 GiB in January 2026. After the block gas limit went from 30M to 60M, the average new state created per day rose from about 105 MiB to about 326 MiB, roughly 116 GiB a year. The authors note this response was not linear (a 2× gas limit produced roughly 3× daily state growth) and that extrapolating it to a 200M gas limit gives about 387 GiB a year, which would cross the 650 GiB point where they say nodes start to degrade in under a year. State creation was also priced inconsistently: deploying code cost about 200 gas per new byte, while a new storage slot cost about 313 gas per byte.

The second is **state access**. EIP-8038 points out that access costs were last raised by [EIP-2929](https://eips.ethereum.org/EIPS/eip-2929) in the Berlin fork in March 2021, and the state has grown a lot since. Reading an account or slot from a bigger database is slower, but the gas cost stayed the same. `EXTCODESIZE` and `EXTCODECOPY` also cost the same as `BALANCE` even though they do a second database read.

A third, smaller issue sits in transaction pricing. EIP-2780 argues that a flat 21,000 base charges a zero-value call and an account-creating transfer the same, which overprices the first and underprices the second.

The common thread is that the gas limit cannot keep rising while these operations stay cheap relative to the work they cause. The EF's [repricing testing post](https://blog.ethereum.org/2026/08/24/glamsterdam-repricing-testing) calls the repricing "a prerequisite for raising the gas limit further."

## The three EIPs at a glance

| EIP | Official title | What it changes | Gas dimension |
| --- | --- | --- | --- |
| [EIP-8037](https://eips.ethereum.org/EIPS/eip-8037) | State Creation Gas Cost Increase | Prices new state per byte (`CPSB` = 1,530), adds a separate state-gas dimension and the reservoir model | State gas (plus some execution gas) |
| [EIP-8038](https://eips.ethereum.org/EIPS/eip-8038) | State-access gas cost update | Raises cold account access, adds explicit write surcharges, charges `EXTCODESIZE`/`EXTCODECOPY` for a second read | Execution gas |
| [EIP-2780](https://eips.ethereum.org/EIPS/eip-2780) | Resource-based intrinsic transaction gas | Splits 21,000 into named primitives; moves state-dependent charges to a runtime phase | Execution gas (intrinsic) and both (runtime) |

The dependencies run in a loop. EIP-8038 requires EIP-8037; EIP-8037 requires both EIP-2780 and EIP-8038; EIP-2780 requires both of the others. In practice they ship as one package. EIP-8037's title in screenshots and summaries is sometimes shortened to "State Gas", but the official title is the one above.

## EIP-8037: state creation gets its own gas dimension

### Cost per state byte

EIP-8037 introduces one unit price, `CPSB` (cost per state byte), set to **1,530 gas**. Every state-creating operation is priced as bytes × `CPSB`, using fixed byte sizes:

| Parameter | Value | What it represents |
| --- | --- | --- |
| `CPSB` | 1,530 | Gas per new state byte |
| `STATE_BYTES_PER_STORAGE_SET` | 64 | 32-byte slot hash key + 32-byte value |
| `STATE_BYTES_PER_NEW_ACCOUNT` | 120 | 32-byte key + nonce 8 + balance 16 + code hash 32 + storage root 32 |
| `STATE_BYTES_PER_AUTH_BASE` | 23 | EIP-7702 delegation indicator (`0xef0100` + 20-byte address) |
| `SYSTEM_MAX_SSTORES_PER_CALL` | 16 | Margin for system contract calls |
| `TX_MAX_TOTAL_GAS_LIMIT` | 4,294,967,295 (2^32 − 1) | New absolute cap on `tx.gas` |

The EIP says these byte counts cover only the leaf and its key, not intermediate trie nodes, so they are a lower bound on real growth.

The 1,530 figure comes from a short derivation in the Rationale. The authors target 120 GiB of state growth per year at a reference block gas limit of 150M, assume state gas uses 50% of the limit on average (the base fee converges to the target, which is half the limit), and use 12-second slots (2,628,000 blocks a year). That gives 75,000,000 × 2,628,000 ≈ 1.971 × 10^14 gas a year, and dividing by 120 × 2^30 bytes gives ≈1,530 gas per byte. The EIP describes the 150M reference as a midpoint between the 60M limit at the time of writing and an expected future 300M. It is an input to the derivation, not the current mainnet gas limit and not a forecast of one. The Rationale also has a short table of growth rates at other block limits, but it labels those as full-block worst cases while the derivation above assumes 50% utilization, so I have left its numbers out. In November 2025, participants in the [Magicians thread](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694) (posts #8 to #13) also discussed alternatives: a price that adapts with the gas limit, or one that adapts with actual state usage. The current text uses a fixed value and says a later EIP can re-derive it.

### What new state costs now

Multiplying out gives the state-gas portion for the three cases most people will hit:

- **New account**: 120 × 1,530 = 183,600, where the old `GAS_NEW_ACCOUNT` charged 25,000 (about 7×).
- **New storage slot**: 64 × 1,530 = 97,920, against the old `GAS_STORAGE_SET` of 20,000 (about 5×).
- **24 kB contract deployment**: 37,784,880 for the account plus code bytes, against 4,947,200 before (about 8×, the EIP's own figure).

These are state gas only. EIP-8038's execution-gas charges (`ACCOUNT_WRITE`, `STORAGE_WRITE`, the code hash cost) come on top. In the spec, each old constant is replaced by a state-gas part and, where needed, an EIP-8038 execution part: `GAS_CREATE`, `GAS_NEW_ACCOUNT` and 7702's `PER_EMPTY_ACCOUNT_COST` all become 120 × `CPSB`; `GAS_STORAGE_SET` becomes 64 × `CPSB`; 7702's `PER_AUTH_BASE_COST` becomes 23 × `CPSB` plus a 7,816 execution base; and the code deposit becomes `CPSB` per byte plus a hash cost of 6 gas per 32-byte word.

Code is now priced like any other state: 1,530 per byte instead of 200. The motivation also notes that duplicated bytecode pays the same as new bytecode even though clients store it once; the current spec does not add a discount for that.

### Two dimensions, one gas limit

The structural change is that gas now has two dimensions, **execution gas** and **state gas**. State-creating operations put their "new state" cost into state gas and their access/write cost into execution gas. Everything else is execution gas.

The user still pays for both. A transaction's total cost is the sum of the two dimensions, and the fee is computed the same way as today: the final gas used (after the refund cap and the calldata floor, shown in the receipt as `gasUsed`) times the transaction's effective gas price (`effectiveGasPrice`, the base fee plus the priority fee actually paid). So a 5× or 7× rise in gas units is not a fixed rise in ETH or dollar cost. The base fee moves with demand from block to block, and the ETH price moves on its own. EIP-8037 converts its examples to ETH at a 0.08 gwei base fee, the average it observed in December 2025 and January 2026; read that as an illustration, not a forecast. The same applies to every gas figure in this post.

What changes is which limits apply:

- [EIP-7825](https://eips.ethereum.org/EIPS/eip-7825)'s per-transaction cap (`TX_MAX_GAS_LIMIT`, 16,777,216) now applies to execution gas only.
- `tx.gas` as a whole is capped at `TX_MAX_TOTAL_GAS_LIMIT` (2^32 − 1).
- At the block level, the header's `gas_used` becomes `max(block_execution_gas_used, block_state_gas_used)`. Block validity and the base-fee update both use that value.

That last rule is where the scaling argument lives. The block gas limit now bounds whichever resource is the bottleneck, so a block full of state creation does not eat the execution budget, and the reverse. EIP-8037 explains the reason for keeping the 7825 cap on execution only: with `CPSB` = 1,530 and the old single cap, a deployment with a 5M constructor budget would top out around 7,564 bytes of code. With the split, the 2^32 − 1 total cap leaves room for roughly 2.8 MB of code deposit in one transaction, about 43 times the 65,536-byte limit that [EIP-7954](https://eips.ethereum.org/EIPS/eip-7954) (also scheduled for Glamsterdam) sets.

On the gas side, a transaction must pass these checks before inclusion: `tx.gas` must cover `max(intrinsic_gas, calldata_floor_gas_cost)`, as it already must today; `tx.gas <= TX_MAX_TOTAL_GAS_LIMIT`; `max(intrinsic_gas, calldata_floor_gas_cost) <= TX_MAX_GAS_LIMIT`; and, per dimension, the transaction must fit the remaining block budget (`min(TX_MAX_GAS_LIMIT, tx.gas)` against execution, `tx.gas` against state). The execution-specs `validate_transaction` raises an "insufficient intrinsic gas" error when the first check fails. This list covers only the gas rules. The usual nonce, balance, fee-cap and transaction-type checks still apply.

### The reservoir model

A transaction has only one gas field, so the protocol needs a rule for which part of `tx.gas` is execution budget and which is state budget. EIP-8037 calls its answer the **reservoir model**:

```python
evm_gas = tx.gas - intrinsic_gas
execution_gas_budget = TX_MAX_GAS_LIMIT - intrinsic_gas
gas_left = min(execution_gas_budget, evm_gas)
state_gas_reservoir = evm_gas - gas_left
```

Anything up to the 7825 cap becomes `gas_left`, the familiar execution pool. Anything above the cap goes into `state_gas_reservoir`. The [execution-specs](https://github.com/ethereum/execution-specs/blob/16898000911c1e3caa57be08509536c10ae92d3e/src/ethereum/forks/amsterdam/vm/gas.py) implementation (`allocate_evm_gas`) is the same four lines.

The rules for the two pools:

- Execution charges come out of `gas_left` only.
- State charges come out of the reservoir first. When it is empty, the remainder comes out of `gas_left`, and a frame-local counter `state_gas_from_gas_left` records how much was borrowed.
- The reservoir is passed to a child call **in full**. The 63/64 rule applies only to `gas_left`. The parent keeps none of the reservoir while the child runs and gets it back when the child exits.
- The `GAS` opcode returns `gas_left` only. In the execution-specs code, the `GAS` instruction pushes `evm.gas_meter.gas_left` and nothing else.
- The `SSTORE` stipend check (an `SSTORE` fails unless more than the 2,300 call stipend remains) also looks at `gas_left` only. A large reservoir does not help a frame pass it.

A consequence that is easy to miss: for any transaction with `tx.gas` at or below 16,777,216, the reservoir starts at zero. Every state charge in such a transaction is paid from `gas_left`, which is also what `gasleft()` reports. The reservoir only matters for transactions that ask for more than the 7825 cap.

![Glamsterdam transaction gas flow: tx.gas must cover the larger of the state-independent intrinsic gas (EIP-2780) and the calldata floor, and that amount must fit the 16,777,216 execution cap, alongside the usual non-gas validity checks. tx.gas is then split into gas_left capped at 16,777,216 minus intrinsic and a state_gas_reservoir for the excess (EIP-8037), then pays pre-execution runtime charges (running out of gas there still includes the transaction and reverts its pre-execution changes) and per-opcode charges. State charges draw from the reservoir first and spill into gas_left. A new storage slot pays state gas only when its original and current values are zero and the new value is not. Settlement tracks execution and state gas separately, the sender pays final gas used times the effective gas price, and the block header gas_used is the larger of the two block totals.](/images/posts/glamsterdam-gas-model/glamsterdam-gas-flow.svg "Glamsterdam transaction gas flow")

*Original diagram reconstructed from the EIP-2780, EIP-8037 and EIP-8038 texts at ethereum/EIPs commit `5ef3801` (Last Call, 2026-10-06), with values checked against the execution-specs Amsterdam fork. Parameters can still change before mainnet, and no mainnet activation is scheduled.*

### Refills, reverts and halts

When state creation is undone, the state gas comes back. EIP-8037 calls this a **refill** and keeps it separate from the refund counter. Examples are a storage slot that was zero at transaction start and goes 0 → x → 0 within the transaction, a value-bearing `CALL` that fails, or a `CREATE` whose frame reverts.

Refills run in last-in, first-out order. Since charges take from the reservoir first and from `gas_left` last, a refill credits `gas_left` first (up to `state_gas_from_gas_left`) and puts any remainder back into the reservoir. Refills also reduce `evm_state_gas_used`, the transaction's running total of state gas.

Reverts and exceptional halts use a different mechanism. Each frame records `state_gas_baseline`, the reservoir value at frame entry. On rollback the frame's state gas is restored to that baseline, and whatever it borrowed from `gas_left` is credited back to `gas_left`. The difference between the two failure types is the same as today: a revert returns the remaining `gas_left` to the parent, while an exceptional halt consumes it.

When a child frame succeeds, its borrowed amount merges into the parent's, and the frame then moves state gas from the reservoir back into `gas_left`, up to what it still owes. The EIP explains why this step exists. The `SSTORE` "original value" is the value at transaction start, so a frame can clear a slot that an earlier frame allocated, and the refill can land in a frame that never paid for it. The merge step keeps the two pools from drifting.

[EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) authorizations are the one exception. They are applied before the top-level frame starts and are not undone when that frame reverts, so the state gas paid for them must not be refilled. The top-level frame takes its baseline after the authorization charges, and the part those charges drew from `gas_left` is "committed" (marked as not refillable) in a separate `state_gas_committed` counter. If the transaction fails before the top-level frame starts at all, the whole pre-execution phase rolls back, authorizations included, and all of that state gas is refilled.

### CALL, CREATE and SELFDESTRUCT

The account-creation charge (120 × `CPSB` = 183,600) is conditional everywhere. An account counts as existing if it has a nonzero balance, a nonzero nonce, or non-empty code ([EIP-161](https://eips.ethereum.org/EIPS/eip-161)).

- **`CALL*` with value to a non-existent account**: charged right before the child frame. If the call fails before entry (insufficient balance, depth limit) or the child reverts or halts, the charge is refilled.
- **`CREATE`/`CREATE2`**: charged in the creating frame, after the balance, nonce-overflow and depth checks and after the single destination read that also performs the [EIP-684](https://eips.ethereum.org/EIPS/eip-684) collision check, and *before* 63/64 of the remaining gas is forwarded. If part of the charge comes from `gas_left`, the child gets less gas. If the destination already exists (for example, it holds a balance), there is no account charge, only the code deposit at `L × CPSB`. If the create frame fails, the charge is refilled. An address collision under EIP-684 needs a nonzero nonce or non-empty code at the destination (a balance or leftover storage alone is not a collision). Such a destination already exists, so no account charge was made, and the collision halts the create frame and consumes the gas forwarded to it.
- **`SELFDESTRUCT`** that sends balance to a non-existent account pays 183,600 at the point it runs. A `SELFDESTRUCT` of an account created in the same transaction does **not** refill any state gas.

The `CREATE` timing was a deliberate choice. An earlier revision charged unconditionally before the create frame and refunded afterwards. The authors switched to the conditional model because it removes several refill paths and lines `CREATE` up with `CALL`. The Rationale also explains why the charge is not placed after the child frame: up to 63/64 of the parent's execution gas goes to the child, and charging at exit could make an otherwise successful deployment fail at the last step.

The same-transaction `SELFDESTRUCT` rule is still argued about. A [Magicians post](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/46) (post #46, August 26, 2026) notes that a refill for this case was agreed in a repricing breakout, implemented, and then dropped for bal-devnet-7. The author argues that ephemeral contracts, such as executors behind deposit-address sweeps, now pay the full 183,600 for an account that never reaches the state. The topic was put on the [ACDE #244 agenda](https://github.com/ethereum/pm/issues/2197) (call of August 27, 2026) along with a spec PR. As of this snapshot, the EIP text has no such refill.

### Settlement, refunds and the calldata floor

At the end of the transaction:

```python
tx_gas_used_before_refund = tx.gas - tx_output.gas_left - tx_output.state_gas_reservoir
tx_gas_refund = min(tx_gas_used_before_refund // 5, tx_output.refund_counter)
tx_gas_used_after_refund = tx_gas_used_before_refund - tx_gas_refund
tx_gas_used = max(tx_gas_used_after_refund, calldata_floor_gas_cost)
```

The refund cap stays at 20%, and the [EIP-7623](https://eips.ethereum.org/EIPS/eip-7623) calldata floor applies after refunds. An unused reservoir goes back to the sender like unused `gas_left`. Two other Glamsterdam changes move the floor itself: [EIP-7976](https://eips.ethereum.org/EIPS/eip-7976), also scheduled, raises the floor cost, and EIP-2780 replaces the flat 21,000 inside the floor formula with the transaction's decomposed base (`TX_BASE_COST` plus the recipient and value charges that apply).

For the block counters, state gas is the net `evm_state_gas_used`, and execution gas is the rest, floored at the calldata cost. The floor is compared against the execution portion alone, so padding a transaction with state creation cannot absorb it. Glamsterdam also schedules [EIP-7778](https://eips.ethereum.org/EIPS/eip-7778), which stops subtracting refunds from block gas accounting. EIP-8037 specifies the combined version, where execution gas is computed before refunds, and the execution-specs Amsterdam code implements that version. The EIP argues that state-gas refills are not refunds in 7778's sense, because the state they paid for was never created, so they stay netted out of the state dimension.

One detail for anyone parsing receipts: `cumulative_gas_used` now tracks the running sum of what each transaction paid, not the block header's `gas_used`. With two dimensions those numbers differ.

System calls at the start of each block (the [EIP-2935](https://eips.ethereum.org/EIPS/eip-2935), [EIP-4788](https://eips.ethereum.org/EIPS/eip-4788), [EIP-7002](https://eips.ethereum.org/EIPS/eip-7002) and [EIP-7251](https://eips.ethereum.org/EIPS/eip-7251) contracts) get a larger limit: 30,000,000 + 64 × 1,530 × 16, which works out to 31,566,720. The extra 1,566,720 goes into the reservoir. System calls still do not count toward either block counter.

## EIP-8038: access and write costs

### Three cost components

EIP-8038 rewrites state-touching costs as the sum of up to three parts:

1. **Access**: loading an account or slot. `COLD_ACCOUNT_ACCESS`, `COLD_STORAGE_ACCESS`, `WARM_ACCESS` (renamed from the EIP-2929 constants). The EIP-2929 warm/cold rules do not change.
2. **Write**: changing a leaf's values. Two new parameters, `STORAGE_WRITE` and `ACCOUNT_WRITE`. Before, this cost was hidden inside composite constants like `SSTORE_RESET_GAS` and `G_callvalue`.
3. **State creation**: adding a new leaf. This is EIP-8037's state gas, not repriced by EIP-8038.

The two write charges follow different rules. `STORAGE_WRITE` is net-metered per transaction: a slot that ends the transaction changed pays it once, and a slot restored to its original value gets it back. `ACCOUNT_WRITE` is charged per operation with no tracking, so a contract that sends value to the same address three times pays it three times. (EIP-2780 has its own once-per-authority rule for 7702 processing.)

### New parameter values

| Parameter | Component | Before | After | Change |
| --- | --- | --- | --- | --- |
| `COLD_ACCOUNT_ACCESS` | Access | 2,600 | 3,000 | +15% |
| `COLD_STORAGE_ACCESS` | Access | 2,100 | 2,100 | 0 |
| `WARM_ACCESS` | Access | 100 | 100 | 0 |
| `ACCOUNT_WRITE` | Write | 6,700 (equivalent) | 9,000 | +34% |
| `STORAGE_WRITE` | Write | 2,800 (equivalent) | 10,000 | +257% |
| `CREATE_ACCESS` | Access + write | 7,000 (equivalent) | 12,000 | +71% |
| `STORAGE_CLEAR_REFUND` | Refund | 4,800 | 11,616 | +142% |
| `ACCESS_LIST_STORAGE_KEY_COST` | Prepaid access | 1,900 | 2,000 | +5% |
| `ACCESS_LIST_ADDRESS_COST` | Prepaid access | 2,400 | 2,900 | +21% |

The "before" values for the three new parameters are the EIP's own extraction from the old composites: 6,700 = 9,000 `G_callvalue` − 2,300 stipend; 2,800 = 5,000 `SSTORE_RESET_GAS` − 2,100 − 100; 7,000 = 32,000 `G_create` − 25,000 `G_newaccount`. The EIP notes the old schedule does not separate cleanly, so these are approximations.

Several values are derived from others, and the execution-specs code computes them the same way: `STORAGE_CLEAR_REFUND = (STORAGE_WRITE + COLD_STORAGE_ACCESS) × 4800/5000`, access-list costs are the cold cost minus `WARM_ACCESS` (so prepaying an entry is never more expensive than a cold touch), and `CREATE_ACCESS = ACCOUNT_WRITE + COLD_ACCOUNT_ACCESS`.

### SSTORE in practice

EIP-8038 defines the new `SSTORE` cost in terms of the slot's *original* value (at transaction start) and its *current* value (just before this `SSTORE`):

- access cost, cold or warm, as before;
- plus `STORAGE_WRITE` if the new value differs from the current value and the current value still equals the original (the first change away from the transaction-start value);
- plus `GAS_STORAGE_SET` (97,920, in state gas) only if the original value is zero, the current value is zero, and the new value is nonzero.

All three conditions matter for the state charge. A slot that was nonzero at transaction start, cleared, and then set again (`x → 0 → y`) does not create new state, so it pays no state gas. Apart from the access cost, that write only reverses the clearing refund, as described below. Some concrete cases, computed from the parameters above:

| Write | Before Glamsterdam | Execution gas | State gas | Total |
| --- | --- | --- | --- | --- |
| Update existing nonzero slot, warm | 2,900 | 100 + 10,000 = 10,100 | 0 | 10,100 |
| Update existing nonzero slot, cold | 5,000 | 2,100 + 10,000 = 12,100 | 0 | 12,100 |
| New slot (original 0, current 0, new x), cold | 22,100 | 12,100 | 97,920 | 110,020 |
| Set and clear within one tx (original 0: 0 → x → 0) | | warm 100, `STORAGE_WRITE` refunded | 97,920 refilled | access costs only, subject to the refund cap |

The first two rows are the ones people tend to miss. EIP-8038 makes ordinary storage updates, with no new state at all, about 2.4 to 3.5 times more expensive in execution gas. A [community measurement on Sepolia](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/50) found exactly these values (2,900 → 10,100 warm, 5,000 → 12,100 cold) and traced DEX swaps that ran out of gas at pool storage updates.

The refund rules were also tightened. Clearing a slot that was nonzero at transaction start adds `STORAGE_CLEAR_REFUND`. Setting it nonzero again later in the same transaction subtracts that refund. Restoring the original value refunds `STORAGE_WRITE`. The goal, per the EIP, is that a round trip like `x → 0 → x` is never net-profitable. That reversal was added after a [Magicians thread discussion](https://ethereum-magicians.org/t/eip-8038-state-access-gas-cost-update/25693/20) found the earlier text missed it; an EIP author opened the fix on June 22, 2026. All of these still go through the refund counter and its 20% cap.

### CALL, CREATE, SELFDESTRUCT and EXTCODE*

- **`CALL`/`CALLCODE`**: `CALL_VALUE` is now `ACCOUNT_WRITE + CALL_STIPEND` = 9,000 + 2,300 = 11,300 (before: 9,000). The 2,300 stipend forwarded to the callee is unchanged. A value transfer to a dead account also pays EIP-8037's account charge in state gas.
- **`CREATE`/`CREATE2`**: the flat 32,000 becomes `CREATE_ACCESS` (12,000, execution) plus the new-account state gas. The EIP points out that this does not match the legacy decomposition exactly and chooses not to reconcile it.
- **`SELFDESTRUCT`**: `COLD_ACCOUNT_ACCESS` if the beneficiary is cold (warm stays free, as under EIP-2929), plus `ACCOUNT_WRITE` if a positive balance goes to a dead account.
- **`EXTCODESIZE`/`EXTCODECOPY`**: one extra `WARM_ACCESS` (100) for the second database read.

### How the numbers were derived

EIP-8038 sets a performance target of 100 million gas per second, which it describes as a factor of 5 over "our current 20 Mgas/s." Each execution client ran synthetic benchmark blocks that isolate a single operation, on a state snapshot the size of mainnet in March 2026, with the 10 GB storage tests targeting a contract the size of the largest one on mainnet. A non-negative least squares regression estimated per-operation runtime, filtered to fits with R² > 0.5 and p < 0.05, and the result was converted at `gas = 100,000,000 × runtime_seconds`. The final value for each parameter is the worst case across clients. The EIP says this is the conservative choice: the slowest client on an operation sets the price for everyone.

One framing difference is worth knowing. The EF's August post describes the repricing as supporting "roughly a 3x increase in base throughput," while EIP-8038 states a 5× target (20 → 100 Mgas/s). I use the EIP's own figure where it matters.

## EIP-2780: intrinsic gas and runtime gas

### Decomposing 21,000

EIP-2780 replaces the flat base with named primitives:

| Primitive | Value | Charged when |
| --- | --- | --- |
| `TX_BASE_COST` | 12,000 | Always (signature recovery, sender access and write, block inclusion) |
| `COLD_ACCOUNT_ACCESS` | 3,000 | `tx.to` is another account (always at the cold rate) |
| `CREATE_ACCESS` | 12,000 | Contract-creation transaction, instead of the recipient touch |
| `TX_VALUE_COST` | 6,000 | Nonzero value to a different account; not charged for a self-transfer or a contract-creation transaction (covers the balance write and [EIP-7708](https://eips.ethereum.org/EIPS/eip-7708) transfer log) |
| `EXECUTION_PER_AUTH_BASE_COST` | 7,816 | Per EIP-7702 authorization |

The 7,816 is defined in EIP-8037: 101 bytes × 16 for the authorization tuple's calldata (1,616), plus `PRECOMPILE_ECRECOVER` (3,000), plus a cold account access (3,000), plus two warm accesses (200). Calldata and access-list metering are unchanged by EIP-2780.

The recipient and authority are always charged at the cold rate, even when an access list would make them warm. The reason is that intrinsic gas must be computable without reading state.

### Reference cases

From EIP-2780's own table (calldata, access lists and executed code excluded):

| Transaction | Intrinsic (execution) | Runtime | Total |
| --- | --- | --- | --- |
| ETH transfer to self | 12,000 | 0 | 12,000 |
| Zero-value call to an EOA or empty account | 15,000 | 0 | 15,000 |
| ETH transfer to an existing EOA | 21,000 | 0 | 21,000 |
| ETH transfer to a 7702-delegated account | 21,000 | 3,000 (delegation target, cold) | 24,000 + execution |
| ETH transfer creating a new account | 21,000 | 183,600 state | 21,000 execution + 183,600 state |
| Contract creation, target does not exist | 24,000 | 183,600 state | 24,000 + 183,600 state |
| Contract creation, target already holds a balance | 24,000 | 0 | 24,000 |

### Not a blanket fee cut

EIP-2780 is easy to misread as a fee cut, partly because of its history. When it was revived in September 2025, the [Magicians thread](https://ethereum-magicians.org/t/eip-2780-reduce-intrinsic-cost-of-transactions/4413), still titled "Reduce intrinsic cost of transactions", described the goal as cutting 21,000 to 6,000. The current normative text is different. Its abstract says "A plain ETH transfer to an existing account remains at `21,000` execution gas." Only zero-value calls (15,000) and self-transfers (12,000) drop below 21,000. A transfer that creates an account now costs 204,600 in total, nearly ten times the old price. EIP-2780's security section states the invariant directly: the decomposed charges "sum to at least the legacy 21,000 for any transaction that moves value to a distinct, cold account."

The EIP says the base numbers come from an execution-layer benchmark that fills blocks with ETH transfers to four receiver types, run on Besu, Erigon, Geth, Nethermind and Reth, and converted at the same 100 Mgas/s anchor. It calls them provisional.

### The runtime phase

The change in charge timing matters more than the numbers. EIP-2780 splits the old intrinsic cost into two kinds:

- **Intrinsic gas**: computable from transaction fields alone. It is the only input to the validity check. If it does not fit, the transaction is invalid and cannot be included.
- **Runtime gas**: anything that depends on state. Is the recipient new? Is it delegated? Does the authority exist? These are charged in a **pre-execution phase**, after the validity check and before the first EVM frame.

The pre-execution phase runs in a fixed order: split gas into `gas_left` and the reservoir (EIP-8037), process 7702 authorizations, add the recipient to the [EIP-7928](https://eips.ethereum.org/EIPS/eip-7928) block-level access list, then apply the remaining account-creation and access charges.

Running out of gas during this phase does **not** invalidate the transaction. It is included, the sender's nonce increments, the sender pays for the gas consumed, and all pre-execution changes, including 7702 delegations, are reverted. EIP-2780 compares this to an out-of-gas inside a `CALL`: block inclusion is the "caller", and a runtime failure cannot undo that decision. The payoff is that builders can decide validity without executing anything.

The practical effect shows up in the Sepolia report covered under community reaction below. A wallet that sends ETH with a hardcoded 21,000 limit to a fresh address no longer gets a rejected transaction. It gets an included, failed one, and the sender pays the fee.

### EIP-7702 authorizations

Authorization pricing was the other worst-case reservation in the old schedule: EIP-7702 charged `PER_EMPTY_ACCOUNT_COST` (25,000) per authorization up front and, when the account already existed, refunded part of it (25,000 − 12,500 = 12,500) through the capped refund counter. Under EIP-2780, only the 7,816 base is intrinsic. During pre-execution, each valid authorization adds, at most once per authority:

- 183,600 state gas if the authority account does not exist;
- `ACCOUNT_WRITE` (9,000) on the first write to that authority in the transaction, skipped when the write is already paid for (the authority is the sender, was written by an earlier authorization, or is the recipient of a value transfer);
- 35,190 state gas (23 × 1,530) if it sets a nonzero delegation and the authority had no indicator at transaction start. Clearing and re-setting an indicator that already existed at transaction start does not pay this again.

## Worked examples across all three

Putting the EIPs together for a few common transactions (calldata, access lists and constructor execution excluded):

**ETH to a fresh address.** 12,000 + 3,000 + 6,000 = 21,000 intrinsic, plus 183,600 state at runtime: **204,600**. With `tx.gas` = 21,000 the transaction is valid, included, and fails in the pre-execution phase.

**First write to a new storage slot inside a contract call.** Cold access 2,100 + `STORAGE_WRITE` 10,000 = 12,100 execution, plus 97,920 state: **110,020**, against 22,100 before.

**Deploying a 24,576-byte contract with a top-level creation transaction to a fresh address.** Intrinsic 12,000 + `CREATE_ACCESS` 12,000 = 24,000 execution. Runtime account state 183,600. Code deposit 24,576 × 1,530 = 37,601,280 state, plus a hash cost of 6 × 768 = 4,608 execution. State gas totals 37,784,880, the same figure as EIP-8037's impact table. Execution gas stays around 28,600 plus whatever the constructor runs, far below the 16,777,216 execution cap. The state gas does not count against that cap, but it is more than twice the number. If state and execution gas shared the single EIP-7825 cap, as all gas does without EIP-8037, this deployment could not fit in a single transaction at the new prices. That is why the state dimension sits outside the cap: with `tx.gas` above 16.7M, the excess becomes the reservoir and pays for the code.

**Value-bearing internal `CALL` to a non-existent account.** Cold access 3,000 + `CALL_VALUE` 11,300 execution, plus 183,600 state, charged before the child frame.

## What developers need to check

The spec sections and the EF's [repricing guidance](https://blog.ethereum.org/2026/08/24/glamsterdam-repricing-testing) converge on the same list.

**Hardcoded gas limits.** Presigned transactions, scripts and contracts that pass fixed gas values are the most common breakage. EIP-8037 gives one example worth knowing: classic deterministic deployment factories (Nick's method, with a 100,000 presigned gas limit, and others such as `SingletonFactory`, `Create2Deployer`, `ImmutableCreate2Factory` and `CreateX`) can no longer be deployed with their original transactions. This does not affect mainnet or L2s where they already exist. It affects new devnets and testnets that start with the EIP active, which have to pre-deploy them at genesis or regenerate the transactions.

**`gasleft()` arithmetic.** Because refills credit `gas_left` before the reservoir, `gas_left` can go *up* after an operation, but only when the state charge being undone was paid from `gas_left`. EIP-8037's own example is `SSTORE(k, 1); GAS; SSTORE(k, 0); GAS` on a slot that was zero at transaction start. If the reservoir was empty when the first store ran, which is always the case when `tx.gas` is at or below the 7825 cap, the 97,920 charge came out of `gas_left`, the clear refills it there, and the second read is higher than the first by the refill minus the cost of the clear. If the reservoir paid for the first store instead, the refill goes back to the reservoir and the second read is lower, as usual. Across a successful sub-call, the merge step can return state gas to the caller's `gas_left`. A contract computing "gas used" as the difference of two `GAS` reads can get a negative value, which reverts under checked arithmetic and wraps under unchecked arithmetic. The EIP states that "contracts already deployed with such metering cannot be fixed." For transactions at or under the 7825 cap, the reservoir is zero, so every state charge shows up in `gasleft()`.

**Logic that branches on remaining gas.** ChainSecurity [raised a concern](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/28) (post #28, June 5, 2026) about the `try`/`catch` pattern: an attacker sets the inner call's gas just below a `gasleft()` threshold to force the `catch` path, and with most of an `SSTORE`'s cost moved into state gas funded by an overprovisioned reservoir, the catch path's writes can now fit. The analysis used the parameter values in the draft at the time (June 2026), but the pattern holds as long as large `tx.gas` funds the reservoir. Other commenters in the same exchange called `gasleft()`-based gating an anti-pattern that previous repricings already broke, while a follow-up reply (post #30) pointed out that popular contracts using it cannot easily be migrated.

**Gas estimation.** EIP-8037 and EIP-8038 both say wallets and RPC nodes MUST update `eth_estimateGas`, and EIP-8037 adds that the returned `tx.gas` must cover both dimensions. One tooling bug showed up on day one: the Sepolia report found anvil estimating 21,000 for a transfer to a new account; Foundry merged a fix (PR #17432) on October 7, so older builds still carry the bug.

**`eth_call` and simulations.** A [Magicians post](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/47) (post #47, September 29, 2026) pointed out that `eth_call` on geth's master branch at the time applied the same reservoir split, so a read-only call given 50M gas got only about 16.76M of execution gas. Left that way, heavy view functions (on-chain SVG renderers, quoters, aggregators) that ran fine under the default RPC gas cap would have failed. The issue was on the [ACDT #99 agenda](https://github.com/ethereum/pm/issues/2242), and an EIP author replied on October 6 that a geth fix existed but was not yet merged and that the intended behaviour will go into the execution-apis spec. Geth merged that fix, [PR #35845](https://github.com/ethereum/go-ethereum/pull/35845), the same day and closed the original report (issue #35838). In the merged code, `eth_call`, `debug_traceCall` and non-strict `eth_simulateV1` skip the execution cap and the reservoir split, while `eth_estimateGas` and strict `eth_simulateV1` stay bound by it. Merged is not the same as deployed. I have not checked which geth releases or RPC providers carry the change, or how other clients behave. If you rely on heavy simulations, confirm the client version and provider you actually hit. A call that passes under `eth_call` can still hit the cap under `eth_estimateGas` or strict simulation.

**ERC-4337 bundles.** `EntryPoint` contracts meter user operations with `gasleft()` deltas, which cannot see the reservoir. Because all operations in a bundle share it, one operation's refill can subsidize another's charge invisibly. EIP-8037 says bundlers and `EntryPoint` implementations MUST account for state gas explicitly. On Sepolia, the community report found 4337 accounts failing because the first use of a fresh nonce key writes a new slot (97,920 state gas) inside the verification gas limit.

**Block builders.** With two dimensions, optimal packing becomes a two-resource problem. EIP-8037 acknowledges this could favour sophisticated builders, and argues that simple greedy filling until one dimension saturates stays effective.

**Storage-heavy designs.** The cost moves most for contracts that keep adding slots rather than updating them. That covers checkpoint-based voting tokens, per-authorization salts like EIP-3009's `transferWithAuthorization`, and ACL mappings with random keys.

## Community reaction

The [EIP-8037 discussion thread](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694) is the main public record, and it is mixed.

On the supportive side, OpenZeppelin's Amxx [wrote](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/38) (post #38, June 19, 2026) that the change is needed for L1 sustainability and security, and that EIP-8037 has no impact on a plain ERC-20 balance update unless it creates or funds a new account. That point is about state gas only: the same balance update still pays EIP-8038's higher `STORAGE_WRITE`, as the `SSTORE` table above shows. The same post lists who pays more: governance tokens with vote checkpoints, EIP-3009 authorization salts, and ACL contracts. It also notes that boolean mappings waste a full 32-byte slot per bit. The EIP authors' position, stated in the thread, is that the EIP is scheduled, already running on devnets, and a [blocker for raising the gas limit further](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/34).

The critical side is specific. Builders of confidential tokens on the draft ERC-7984 standard [estimated](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/33) (post #33, June 15, 2026) that one confidential transfer creates at least seven new persistent ACL slots, which would be at least 685,440 state gas, and asked for a delay to the following fork, Hegotá. An on-chain NFT developer [worried](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/15) in November 2025, against an early version of the EIP, that storage-heavy apps would be pushed off L1. Another commenter [questioned](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/20) (January 2026) targeting linear state growth when storage costs fall exponentially, and [doubted](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/23) (February 2026) that block composition will change much. On EIP-8038, a [cost analysis](https://ethereum-magicians.org/t/eip-8038-state-access-gas-cost-update/25693/18) (June 20, 2026) using preliminary parameters for both repricings found sample liquidation and arbitrage transactions about 44% to 63% more expensive in gas. EIP-8038's values were revised after that.

The first field data came after the Sepolia fork. The [community report](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/50) (PyraVim, October 8, 2026) recorded failures rising from 1.91% to 10.97% of Sepolia transactions in the first 10.5 hours, compared with the 10.5 hours before the fork. About a third of the extra failures came from bots repeating the same failing call. The causes it traced were fixed gas limits on transfers to new accounts, 4337 nonce keys, and storage writes. It also confirmed that a value transfer to an existing account stays at 21,000, a zero-value transfer at 15,000 and a self-transfer at 12,000. This comes from one person's node and should be treated as an early sample, but its numbers match the spec arithmetic exactly. The EF's position is that "the large majority of smart contracts are unaffected" in their mainnet replay, and it published an [affected-contracts search](https://ethereum.github.io/repricing-impact/) for maintainers.

## Still undecided

- **Mainnet and Hoodi activation**: not decided in any official source as of this snapshot. The [ACDT #100 agenda](https://github.com/ethereum/pm/issues/2264) asked client teams for Hoodi releases by October 16, which is preparation, not an activation time.
- **Final parameter values**: the EIPs are in Last Call until November 1, and both EIP-8037 and EIP-2780 describe some inputs as not final or provisional.
- **`eth_call` semantics** under the reservoir split across clients.
- **A refill for same-transaction `CREATE` + `SELFDESTRUCT`**: requested, discussed at ACDE, not in the current text.

## My take

Splitting gas into dimensions is the part I would watch most closely. On paper it does what it says: state growth gets its own budget and price, and the block limit stops forcing a trade-off between execution and storage. The cost is that "gas" no longer means one thing inside the EVM. `gasleft()` reports part of the budget, refills can make it go up, and the reservoir only exists for transactions above 16.7M gas. That is a lot of new behaviour for contract authors and tooling to absorb. The worst case is a transaction that fails silently and still costs a fee.

The early Sepolia numbers look like the usual repricing pattern, where hardcoded limits break first, and not like a design flaw. Whether the pricing actually changes how people use state, which several critics doubt, is something only mainnet data can show.

## Further reading

- [EIP-7928: Block-Level Access Lists](https://eips.ethereum.org/EIPS/eip-7928): the headliner that constrains when `CREATE` may read its destination, and the reason EIP-8038's benchmarks assume parallel reads
- [EIP-7778: Block Gas Accounting without Refunds](https://eips.ethereum.org/EIPS/eip-7778): the block-accounting change EIP-8037 is specified against
- [EIP-7825: Transaction Gas Limit Cap](https://eips.ethereum.org/EIPS/eip-7825): origin of the 16,777,216 execution cap
- [Glamsterdam repricing impact checker](https://ethereum.github.io/repricing-impact/): EF tool for looking up affected contracts
- [Forkcast: Glamsterdam](https://forkcast.org/upgrade/glamsterdam): ACD-based status tracker (the meta EIP remains the source of truth)

## References

- [EIP-8037: State Creation Gas Cost Increase](https://eips.ethereum.org/EIPS/eip-8037), raw text at [ethereum/EIPs `5ef3801`](https://github.com/ethereum/EIPs/blob/5ef380124bd68d09c02fa90d0de0f2455f37d5ee/EIPS/eip-8037.md), accessed 2026-10-15
- [EIP-8038: State-access gas cost update](https://eips.ethereum.org/EIPS/eip-8038), raw at [`5ef3801`](https://github.com/ethereum/EIPs/blob/5ef380124bd68d09c02fa90d0de0f2455f37d5ee/EIPS/eip-8038.md), accessed 2026-10-15
- [EIP-2780: Resource-based intrinsic transaction gas](https://eips.ethereum.org/EIPS/eip-2780), raw at [`5ef3801`](https://github.com/ethereum/EIPs/blob/5ef380124bd68d09c02fa90d0de0f2455f37d5ee/EIPS/eip-2780.md), accessed 2026-10-15
- [EIP-7773: Hardfork Meta - Glamsterdam](https://eips.ethereum.org/EIPS/eip-7773), raw at [`644b847`](https://github.com/ethereum/EIPs/blob/644b84799ba6873edcb13c0e21fdd319b4efbc08/EIPS/eip-7773.md), accessed 2026-10-15
- [ethereum/execution-specs, Amsterdam fork](https://github.com/ethereum/execution-specs/tree/16898000911c1e3caa57be08509536c10ae92d3e/src/ethereum/forks/amsterdam), branch `forks/amsterdam` at `1689800`, accessed 2026-10-15
- [Glamsterdam](https://ethereum.org/en/roadmap/glamsterdam/), ethereum.org, page last updated 2026-09-14, accessed 2026-10-15
- [Glamsterdam Testnet Announcement](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement), Ethereum Foundation Blog, 2026-09-17, accessed 2026-10-15
- [Glamsterdam repricing testing](https://blog.ethereum.org/2026/08/24/glamsterdam-repricing-testing), Ethereum Foundation Blog, 2026-08-24, accessed 2026-10-15
- [ACDE #244 agenda and comments](https://github.com/ethereum/pm/issues/2197), ethereum/pm, accessed 2026-10-15
- [ACDT #99 agenda and comments](https://github.com/ethereum/pm/issues/2242), ethereum/pm, accessed 2026-10-15
- [ACDT #100 agenda](https://github.com/ethereum/pm/issues/2264), ethereum/pm, accessed 2026-10-15
- [go-ethereum PR #35845: core, eth, internal: skip the execution gas cap on eth_call](https://github.com/ethereum/go-ethereum/pull/35845), merged 2026-10-06 (`df4c524`), closes issue #35838, accessed 2026-10-15
- [EIP-8037 discussion thread](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694), Ethereum Magicians, accessed 2026-10-15
- [EIP-8038 discussion thread](https://ethereum-magicians.org/t/eip-8038-state-access-gas-cost-update/25693), Ethereum Magicians, accessed 2026-10-15
- [EIP-2780 discussion thread](https://ethereum-magicians.org/t/eip-2780-reduce-intrinsic-cost-of-transactions/4413), Ethereum Magicians, accessed 2026-10-15
