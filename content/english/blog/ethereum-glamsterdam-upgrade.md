---
title: "Ethereum Glamsterdam Upgrade: ePBS, BALs, Every EIP and Operational Changes"
meta_title: ""
description: "How Glamsterdam changes block construction, parallel validation, gas and networking. The ePBS and BAL mechanisms, all 25 EIPs, activation status and implications for users, developers and validators."
date: 2026-10-17T12:00:00+09:00
lastmod: 2026-10-17T12:00:00+09:00
image: "/images/posts/ethereum-glamsterdam-upgrade/glamsterdam-cover.webp"
categories: ["Blockchain"]
tags: ["ethereum", "glamsterdam", "epbs", "block-access-lists", "evm", "validators"]
author: "whackur"
slug: "ethereum-glamsterdam-upgrade"
translationKey: "ethereum-glamsterdam-upgrade"
draft: false
---

Glamsterdam aims to expand Ethereum L1 capacity by **changing both how blocks are built and how receiving nodes validate them**. Enshrined proposer-builder separation (ePBS) brings commitments, payload reveals and proposer payments into the protocol. Block-level access lists (BALs) carry actual state accesses and post-transaction changes so receiving nodes can parallelize reads and validation. Gas repricing and networking changes support that effort. These changes do not guarantee lower fees for every transaction or a particular TPS figure. [EIP-7773](https://eips.ethereum.org/EIPS/eip-7773) defines the scope; [EIP-7732](https://eips.ethereum.org/EIPS/eip-7732) and [EIP-7928](https://eips.ethereum.org/EIPS/eip-7928) define the two central mechanisms.

## Amsterdam execution and Gloas consensus

Ethereum's Execution Layer (EL) executes transactions and updates state such as balances and storage. Its Consensus Layer (CL) handles validator proposals, votes and chain selection. Glamsterdam combines the **Amsterdam** EL upgrade with the **Gloas** CL upgrade. The two clients work together, so updating only one is insufficient for a node operator. The [official testnet announcement](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement) explains the distinction and the need to update both.

The changes address related constraints:

| Area | Constraint or problem | Glamsterdam's approach |
| --- | --- | --- |
| Block construction and delivery | Proposer-builder exchange relies on trusted mediation, while execution must fit into a tight consensus deadline. | ePBS puts exchange and payment into the protocol and separates consensus and execution validation in time. |
| State reads and execution | Required accounts, storage slots and intermediate changes are difficult to know before execution. | BALs supply actual accessed locations and post-transaction values. |
| Resource pricing and state growth | Underpriced access, writes and state creation increase node load as blocks grow. | Execution, state and data costs are adjusted alongside block accounting. |
| Propagation and synchronization | Large receipt lists, duplicated blob downloads and state healing consume bandwidth. | P2P messages, the blobpool and BAL-based synchronization are improved. |

This groups the design goals of the EIPs below. Real throughput still depends on client implementation, hardware, block workload and network conditions.

## Status as of October 17, 2026

**Specification status, upgrade inclusion and network activation are separate facts.** This snapshot uses ethereum/EIPs [commit `deb8f0d`](https://github.com/ethereum/EIPs/tree/deb8f0d3ea9167bd30775fb3d45d052fce651d56/EIPS), checked directly on October 17, 2026 KST.

| Dimension | Published record |
| --- | --- |
| Upgrade scope | EIP-7773 has 18 Core EIPs Scheduled for Inclusion (SFI). Its separate Other EIPs lists contain five Networking and two Informational documents. |
| Document status | Meta EIP-7773 and Core EIP-7688 are `Review`. Raw metadata for the other 24 documents says `Last Call`. That means neither `Final` standardization nor activation on every network. |
| Sepolia schedule | Epoch 353,024, UNIX timestamp 1,791,294,816, October 6, 2026 at 13:53:36 UTC. |
| Hoodi and mainnet schedule | Their activation fields in EIP-7773 are blank. The testnet announcement explicitly does not schedule either network. |
| Mainnet expectation | The [ethereum.org roadmap](https://ethereum.org/en/roadmap/glamsterdam/) displays Q4 2026 with the date unconfirmed. Its displayed last-update date is September 14, 2026. This is an expectation, separate from a confirmed activation announcement. |

Sepolia's announced time has passed. The passage of that timestamp alone does not independently establish successful activation or the implementation version behind a particular RPC endpoint. The explanations below describe the pinned specifications, not measured before-and-after execution on a live chain. Operational decisions require the target network's announcement, client release notes and actual node state. [Pinned EIP-7773](https://github.com/ethereum/EIPs/blob/deb8f0d3ea9167bd30775fb3d45d052fce651d56/EIPS/eip-7773.md), [testnet announcement](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement)

## ePBS brings block exchange and payment into the protocol

A proposer is the validator selected to propose a block in a particular slot. A builder selects and orders transactions to construct an execution payload. That payload contains the transactions to execute and information used to verify their result. This division of labor is proposer-builder separation (PBS). With enshrined PBS, [EIP-7732](https://eips.ethereum.org/EIPS/eip-7732) moves the exchange from trusted external mediation into the consensus protocol.

1. **The builder signs a bid.** It commits to an execution block hash that will be revealed later and a value payable to the proposer.
2. **The proposer includes the commitment in a beacon block.** The block carries the signed commitment instead of the full execution payload. The protocol deducts payment from the builder's beacon-chain balance and arranges a withdrawal to the proposer's chosen execution-layer address.
3. **The builder reveals the execution payload.** Validators assigned to the Payload Timeliness Committee (PTC) attest to whether the committed payload was revealed on time and whether the corresponding blob data was available.
4. **Execution correctness is checked separately.** A PTC timeliness attestation does not require full EVM execution validation. Deferring execution validation until the next beacon-block validation removes that work from the tight path immediately before the consensus vote.

Validation remains mandatory, but its timing changes. Choosing a commitment, revealing a payload and validating execution become distinct stages. Wallets and explorers should distinguish seeing a payload, subsequent validation of its execution and consensus finality. [EIP-7732's delayed-validation section](https://eips.ethereum.org/EIPS/eip-7732#delayed-validation) explains this distinction.

ePBS does not eliminate maximal extractable value (MEV), the value available from transaction selection, ordering and inclusion. Builders still construct transactions into blocks. Protocol-managed exchange and payment reduce trust requirements, but optional middleware for bid delivery, builder discovery or operational policy can remain. The specification also accommodates trusted payment promises fulfilled elsewhere. It does not automatically resolve builder concentration or remove every intermediary service. [EIP-7732](https://eips.ethereum.org/EIPS/eip-7732)

The builder lifecycle needs to be read alongside this mechanism. [EIP-8282](https://eips.ethereum.org/EIPS/eip-8282) adds dedicated EL contracts and request types for registration, top-ups and exits. It retains the special onboarding of the initial builder set at the fork transition, while ordinary post-fork onboarding uses the dedicated builder deposit path. Operators should not use the validator deposit contract for builder deposits based only on EIP-7732's original description. Exit authorization is checked against the builder's `execution_address`, rather than the BLS key that continuously signs bids.

## BALs carry actual accesses and post-transaction values

A Block-Level Access List, defined by [EIP-7928](https://eips.ethereum.org/EIPS/eip-7928), records execution information across a block. It serves a different purpose from an optional EIP-2930 transaction access list supplied by a user. **The producer records the accounts and storage locations actually accessed during execution, together with post-transaction changes; the receiver verifies that record.** It does not simply copy addresses declared by transaction senders.

### The producer records accesses during execution

As the producing EL executes transactions, it collects:

- Accessed accounts and storage keys, including reads that leave values unchanged.
- Storage changes and changes to balances, nonces and code, associated with post-transaction values and ordering indices.
- System processing around the transactions: index 0 for pre-execution, 1 through n for transactions, and n+1 for post-execution processing and withdrawals.

A BAL is not an opcode-by-opcode execution trace. Read-only storage keys are listed separately, while changes to a slot are summarized as post-transaction values. Actual reads in reverted calls must also be distinguished from writes that do not survive. Unused access-list declarations are not automatically included, and rolled-back writes must not be presented as committed changes. The specification's access conditions, ordering and uniqueness rules determine the record. [EIP-7928 scope and state-change tracking](https://eips.ethereum.org/EIPS/eip-7928#scope-and-inclusion)

### The receiver prefetches state and validates in parallel

The receiver learns which data it needs before executing the block, so it can load accounts and storage slots from disk in parallel. Post-transaction changes supply the preceding state needed by individual transactions. Clients can use that information to parallelize transaction execution validation and state-root computation. A state root is the cryptographic hash representing the overall state. [EIP-7928](https://eips.ethereum.org/EIPS/eip-7928)

Suppose transaction A sets storage slot `x` to 5, then transaction B reads it and sets it to 6. B depends on A. With A's post-transaction `x=5` in the BAL, the receiver can supply the value B should read and prepare B's execution validation. It must also check that A really produced 5. If A's claimed output is false, B appearing consistent with that output does not make the block valid. Supplying preceding values means the benefit is not limited to transactions touching disjoint slots. It does not remove state dependencies or make every workload equally parallel.

### Both commitment and execution correctness are checked

The header's `block_access_list_hash` is the Keccak-256 hash of the RLP-encoded BAL. The EL stores the full BAL separately from the block and passes it as a field in the execution payload over the Engine API. The hash checks that the received data matches the committed data. It does not prove that the data describes correct execution. [EIP-7928 block structure](https://eips.ethereum.org/EIPS/eip-7928#block-structure-modification)

The receiving EL must compute actual accesses and changes and check them against the supplied BAL. Missing or spurious entries invalidate the block. An implementation may build a virtual BAL during execution and compare its hash. The producer's results are not accepted on trust. [EIP-7928 state-transition validation](https://eips.ethereum.org/EIPS/eip-7928#state-transition-function)

Applying BAL changes without re-executing transactions also supports synchronization. This executionless state-update path still needs a validated chain context and header commitments. [EIP-8189](https://eips.ethereum.org/EIPS/eip-8189) requires BAL-based healing to apply changes in block order, verify each hash and check the final state root. This synchronization technique does not abolish execution-validity checks for new blocks.

![Separate flows for ePBS commitments and payload reveal, and BAL execution records and parallel validation](/images/posts/ethereum-glamsterdam-upgrade/block-construction-and-validation.svg)

ePBS governs block construction and reveal timing; BALs supply execution data that must be validated. Both retain execution validation. The diagram is not an exact within-slot timetable.

## Complete EIP inventory

These 25 entries cover all three lists in [EIP-7773](https://github.com/ethereum/EIPs/blob/deb8f0d3ea9167bd30775fb3d45d052fce651d56/EIPS/eip-7773.md), grouped by role. The first 18 are SFI Core EIPs; the remaining seven are Other EIPs. **They are not 25 consensus rules all activated by the same fork switch.**

### Six SFI Core changes to construction, validation and consensus

| No. | EIP and specification title | Role and qualification |
| --- | --- | --- |
| 1 | [EIP-7732: Enshrined Proposer-Builder Separation](https://eips.ethereum.org/EIPS/eip-7732) | Protocol-managed builder commitments, reveals and proposer payments, with consensus and execution validation separated in time. The PTC attests to timeliness and data availability, not full execution validity. |
| 2 | [EIP-7928: Block-Level Access Lists](https://eips.ethereum.org/EIPS/eip-7928) | Carries actual state accesses and post-transaction changes for parallel reads, execution validation and state-root computation. The BAL's own correctness must be verified. |
| 3 | [EIP-7688: Forward compatible consensus data structures](https://eips.ethereum.org/EIPS/eip-7688) | Uses progressive SSZ structures to make Merkle proofs more compatible with future changes. Serialization bytes of affected types stay unchanged, but Merkleization changes, so proof tooling must handle the transition. |
| 4 | [EIP-8045: Exclude slashed validators from proposing](https://eips.ethereum.org/EIPS/eip-8045) | Filters slashed validators from proposer selection, reducing missed slots caused by proposals that would already be invalid. |
| 5 | [EIP-8061: Increase exit and consolidation churn](https://eips.ethereum.org/EIPS/eip-8061) | Roughly quadruples exit churn and restores its proportionality to total stake, while roughly doubling consolidation churn. The activation cap remains. The shorter weak-subjectivity period also affects synchronization operations. |
| 6 | [EIP-8282: Builder Execution Requests](https://eips.ethereum.org/EIPS/eip-8282) | Adds dedicated builder deposit, top-up and exit contracts and requests. Fork-transition onboarding is a special case, distinct from ordinary post-fork flows. |

### Six SFI Core changes to gas, data and state costs

| No. | EIP and specification title | Role and qualification |
| --- | --- | --- |
| 7 | [EIP-2780: Resource-based intrinsic transaction gas](https://eips.ethereum.org/EIPS/eip-2780) | Decomposes the flat base cost into resource components and intrinsic versus runtime charges. A plain positive-value ETH transfer to another existing ordinary account remains 21,000 execution gas. It does not make every transfer cost 12,000. |
| 8 | [EIP-7778: Block Gas Accounting without Refunds](https://eips.ethereum.org/EIPS/eip-7778) | Stops refunds from reducing block-limit accounting. Eligible user refunds remain; the user's bill and the work counted against block capacity are separate. |
| 9 | [EIP-7976: Increase Calldata Floor Cost](https://eips.ethereum.org/EIPS/eip-7976) | Raises the calldata floor to 64 gas per zero or nonzero byte. This is a minimum-cost rule for data-heavy transactions, not unconditional replacement of every byte's charge in every transaction. |
| 10 | [EIP-7981: Increase Access List Cost](https://eips.ethereum.org/EIPS/eip-7981) | Adds a flat 64-gas-per-byte surcharge for user-supplied access-list data to prevent bypassing the calldata floor. These lists are distinct from the BAL received by nodes. |
| 11 | [EIP-8037: State Creation Gas Cost Increase](https://eips.ethereum.org/EIPS/eip-8037) | Introduces per-byte state-creation pricing and separate state-gas metering with a reservoir. Pricing targets average state growth of 120 GiB/year at a 150M reference block gas limit; it is not an enforced cap on actual growth. |
| 12 | [EIP-8038: State-access gas cost update](https://eips.ethereum.org/EIPS/eip-8038) | Raises cold-account access costs and separates account and storage write charges. Accounts for the second database read in `EXTCODESIZE` and `EXTCODECOPY`; EIP-8037 handles new-state creation costs. |

These changes align resource costs with the work needed for scaling. EIP-8037's state gas is not a free allowance independent of the transaction's `gasLimit`. Execution gas and a separate state reservoir are managed within one transaction budget, and `gasleft()` does not report that reservoir. The separate article [Glamsterdam's New Gas Model](/en/blog/glamsterdam-gas-model/) covers storage writes, deletion and fixed-gas internal calls with Solidity examples.

### Six SFI Core changes to the EVM and developer tools

| No. | EIP and specification title | Role and qualification |
| --- | --- | --- |
| 13 | [EIP-7708: ETH transfers emit a log](https://eips.ethereum.org/EIPS/eip-7708) | Emits protocol logs for specified positive-value ETH transfers: transactions, `CALL` and `SELFDESTRUCT` to different accounts, plus `CREATE` and `CREATE2` endowments. It does not log every balance change, including fees, base-fee burns and withdrawals. |
| 14 | [EIP-7843: SLOTNUM opcode](https://eips.ethereum.org/EIPS/eip-7843) | Adds an opcode for the current slot number. Slots differ from block numbers; exposing the slot reduces reliance on contracts hardcoding slot duration. |
| 15 | [EIP-7954: Increase Maximum Contract Size](https://eips.ethereum.org/EIPS/eip-7954) | Raises the runtime code limit from 24 KiB to 64 KiB and the initcode limit from 48 KiB to 128 KiB. A permitted size does not guarantee a sufficient deployment gas budget. |
| 16 | [EIP-7997: Deterministic Factory Contract](https://eips.ethereum.org/EIPS/eip-7997) | Formally requires the presence of a specified `CREATE2` factory. It supplies infrastructure for matching deployment addresses; it does not automatically make every EVM chain adopt the rule or arbitrary deployments produce identical addresses. |
| 17 | [EIP-8024: Backward compatible SWAPN, DUPN, EXCHANGE](https://eips.ethereum.org/EIPS/eip-8024) | Adds deeper stack-access instructions to help compiler stack scheduling. It does not automatically reoptimize already-deployed bytecode. |
| 18 | [EIP-8246: Remove SELFDESTRUCT Burn](https://eips.ethereum.org/EIPS/eip-8246) | Removes remaining ETH-burning paths involving contracts created and selfdestructed in the same transaction. Preserves balances of affected accounts at cleanup; it does not restore broad code and storage deletion from before EIP-6780. |

### Five Networking documents under Other EIPs

| No. | EIP and specification title | Role and qualification |
| --- | --- | --- |
| 19 | [EIP-7975: eth/70 - partial block receipt lists](https://eips.ethereum.org/EIPS/eip-7975) | Allows requests for partial receipt lists, reducing synchronization failures when large-block receipts exceed message-size limits. |
| 20 | [EIP-8070: eth/72 - Sparse Blobpool](https://eips.ethereum.org/EIPS/eip-8070) | Downloads some blobs in full and samples cells aligned with CL custody for the remainder. Reduces the bandwidth burden of full replication while retaining data-availability checks. |
| 21 | [EIP-8136: Cell-Level Deltas for Data Column Broadcast](https://eips.ethereum.org/EIPS/eip-8136) | A PeerDAS optimization that exchanges missing cells rather than resending cells already held. Backward compatible and progressively deployable without a hard fork; full-column exchange remains for unsupported peers. |
| 22 | [EIP-8159: eth/71 - Block Access List Exchange](https://eips.ethereum.org/EIPS/eip-8159) | Adds peer-to-peer BAL request and response messages for historical blocks and synchronization, alongside live Engine API delivery. |
| 23 | [EIP-8189: snap/2 - BAL-Based State Healing](https://eips.ethereum.org/EIPS/eip-8189) | Uses BALs to heal state during snap sync. Verifies header commitments, block order and the final state root; negotiates a protocol version distinct from `snap/1`. |

### Two Informational documents under Other EIPs

| No. | EIP and specification title | Role and qualification |
| --- | --- | --- |
| 24 | [EIP-7904: Compute Gas Cost Analysis](https://eips.ethereum.org/EIPS/eip-7904) | Analyzes compute and precompile performance in clients incorporating BAL-related optimizations. Concludes examined operations meet a 100 Mgas/s (100 million gas per second) target and recommends no compute repricing. This is neither a network TPS measurement nor a new opcode price schedule. |
| 25 | [EIP-8261: Gas Limit Schedule](https://eips.ethereum.org/EIPS/eip-8261) | Recommends optional post-Gloas CL configuration for epoch-based default gas preferences and recommended maxima. Operator overrides remain allowed, and exceeding the recommendation alone does not invalidate a block. It is neither a consensus cap nor an instant gas-limit increase. |

## Implications for users, developers and operators

### Users and wallets

Mainnet ETH holders do not need to move assets or exchange tokens because of a Sepolia announcement. The [official FAQ](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement#faq) says mainnet will receive a separate announcement. Changes become relevant to users when wallets and RPC providers support the new gas estimates and the target network applies the rules.

Costs depend on the workload. Data-heavy transactions and new-state creation can become more expensive. Lower base costs for some lightweight transactions do not mean all ordinary ETH transfers become cheaper. Gas consumed is also separate from the market price per gas unit. L1 improvements cannot be translated into a universal reduction in every L2 fee. [EIP-2780](https://eips.ethereum.org/EIPS/eip-2780), [EIP-7976](https://eips.ethereum.org/EIPS/eip-7976), [EIP-8037](https://eips.ethereum.org/EIPS/eip-8037)

### Applications, indexers and compilers

Developers should retest gas estimates and failure paths in an environment supporting the target fork. Fixed gas forwarded to internal calls, `gasleft()`-based branches, deployment code size and deployment budgets deserve attention. New opcodes and larger code limits require support from both tooling and the activated target chain. EIP-7954's size allowance does not cancel EIP-8037's state costs. [EIP-8037](https://eips.ethereum.org/EIPS/eip-8037), [EIP-8024](https://eips.ethereum.org/EIPS/eip-8024)

Indexers need to distinguish EIP-7708 system-emitted ETH logs from ERC-20 logs and avoid double counting with their existing traces. Fees and withdrawals still need separate accounting. SSZ proof producers and verifiers need to handle EIP-7688's Merkleization transition. Deterministic-deployment tooling must check the factory, initcode, salt and support on each chain. [EIP-7708](https://eips.ethereum.org/EIPS/eip-7708), [EIP-7688](https://eips.ethereum.org/EIPS/eip-7688), [EIP-7997](https://eips.ethereum.org/EIPS/eip-7997)

EVM-derived chains must make their own adoption decisions. EIP-8246 specifically calls for a separate migration plan for OP Stack-derived withdrawal accounting that uses `SELFDESTRUCT` burns. Ethereum mainnet changes cannot be assumed to apply unchanged to every L2. [EIP-8246 backward compatibility](https://eips.ethereum.org/EIPS/eip-8246#backwards-compatibility)

### Nodes, validators and builders

Operators need compatible EL and CL releases for their particular network, including both the beacon node and Validator Client. They should also check PTC duties, builder connections, payload reveal and execution-validation states, and Engine API compatibility. Receiving BALs does not make every client equally fast at parallel execution. Disk I/O, CPU, memory, bandwidth and actual validation time need to be observed together. [Official operator guidance](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement), [EIP-7928](https://eips.ethereum.org/EIPS/eip-7928)

A large number in a document does not automatically change the gas limit. EIP-8261 offers optional management of defaults and recommendations for supporting clients; the realized limit still follows the existing roughly ±1/1024-per-block adjustment rule. EIP-8061 increases exit and consolidation capacity without guaranteeing immediate withdrawals. Its calculations shorten the weak-subjectivity period to about seven days. Nodes returning after a long offline period need a recent trusted checkpoint; a shorter weak-subjectivity period tightens that operational window. Offline recovery, checkpoints and BAL retention policies need to be checked against the applicable specifications and client guidance. [EIP-8261](https://eips.ethereum.org/EIPS/eip-8261), [EIP-8061](https://eips.ethereum.org/EIPS/eip-8061), [EIP-7928](https://eips.ethereum.org/EIPS/eip-7928)

Builders need to check EIP-8282's dedicated deposit and exit paths and signature handling. An invalid first-deposit proof of possession can lock the principal; exits depend on `execution_address` authorization and pending-balance conditions. This is an infrastructure concern rather than an ordinary user's task. [EIP-8282 security considerations](https://eips.ethereum.org/EIPS/eip-8282#security-considerations)

Glamsterdam should be evaluated through block execution-validation time, state growth, propagation delay and operational stability alongside any target gas limit. ePBS allocates validation time differently, and BALs supply needed state data earlier. Those changes provide a basis for larger blocks. How much capacity they deliver must be established through implementation and network operation.

## Further reading

- [Glamsterdam's New Gas Model](/en/blog/glamsterdam-gas-model/): Solidity examples for storage changes, deletion and fixed-gas internal calls.
- [Glamsterdam roadmap](https://ethereum.org/en/roadmap/glamsterdam/): Upgrade goals and publicly reported progress.
- [EIP-7928 specification](https://eips.ethereum.org/EIPS/eip-7928): BAL structures, access conditions and validation rules.

## References

Sources were checked on October 17, 2026 KST. Each EIP link in the inventory is the primary source for its entry. Specification status and inclusion use the pinned texts below and may change later.

- [Pinned EIP-7773](https://github.com/ethereum/EIPs/blob/deb8f0d3ea9167bd30775fb3d45d052fce651d56/EIPS/eip-7773.md): SFI and Other EIPs categories and activation schedule.
- [Pinned ethereum/EIPs snapshot](https://github.com/ethereum/EIPs/tree/deb8f0d3ea9167bd30775fb3d45d052fce651d56/EIPS): Version used to check all 25 specifications, titles and metadata.
- [Glamsterdam Testnet Announcement](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement): Ethereum Foundation Sepolia announcement and operator guidance.
- [Glamsterdam](https://ethereum.org/en/roadmap/glamsterdam/): ethereum.org overview and unconfirmed mainnet expectation.
