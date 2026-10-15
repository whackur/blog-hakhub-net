---
title: "Besu in 2026 and the Changes Operators Need to Check"
meta_title: "Besu in 2026: Execution Clients, QBFT, Storage, and Upgrades"
description: "A source-grounded look at Besu as of October 15, 2026: releases, governance, execution performance, storage, and upgrade checks for mainnet and permissioned networks."
date: 2026-10-15T11:37:00+09:00
lastmod: 2026-10-15T11:37:00+09:00
image: "/images/posts/besu-state-of-play-2026/cover.png"
categories: ["Blockchain"]
tags: ["besu", "ethereum", "execution-client", "qbft", "enterprise-blockchain"]
author: "whackur"
translationKey: "besu-state-of-play-2026"
draft: false
---

If your introduction to Besu came from an older Hyperledger tutorial, its supported features deserve another look. The name and repository have changed. Work on Ethereum mainnet execution performance has continued while some enterprise features have left the core client. Permissioned networks remain supported, but copying an old configuration no longer reliably reproduces the system described in that tutorial.

This article uses **October 15, 2026 KST** as its cutoff. The latest stable release retrieved from the official GitHub repository is **26.9.0**, published at 22:22 UTC on September 25, or September 26 in Korea. Release dates below consistently use UTC. The public security evidence extends further, to advisories published on October 14. Retrieval dates and the dates of the underlying evidence serve different purposes. [Official releases](https://github.com/besu-eth/besu/releases), [security advisories](https://github.com/besu-eth/besu/security/advisories).

Three changes matter throughout this review. Besu uses different consensus arrangements on mainnet and permissioned chains. Performance work reaches beyond Ethereum Virtual Machine (EVM) execution into state access and state-root computation. An upgrade now involves checking Java, remote procedure call (RPC) behavior, storage, and plugins alongside the client binary.

## The current name and project home

The official name is Besu, an LF Decentralized Trust project. The Linux Foundation's [September 16, 2024 launch announcement](https://www.lfdecentralizedtrust.org/announcements/linux-foundation-decentralized-trust-launches-with-17-projects-100-founding-members) explained that technologies developed under Hyperledger Foundation would become projects of the new organization, and that Hyperledger Besu would be named Besu. This was a naming and organizational change, rather than the creation of a new client in 2026.

The canonical source repository is [`besu-eth/besu`](https://github.com/besu-eth/besu). The [26.4.0 release](https://github.com/besu-eth/besu/releases/tag/26.4.0) records its migration from `hyperledger/besu` and says existing GitHub links redirect automatically. Current documentation lives at [docs.besu-eth.org](https://docs.besu-eth.org/). An article using the old name can still be useful, but its installation commands and feature inventory need their own freshness check.

The name, foundation affiliation, and organizations maintaining the code are separate questions. Foundation hosting does not establish that several companies contribute equal maintenance capacity. The maintainer distribution discussed below is more directly relevant to operational continuity.

## Mainnet and permissioned deployment roles

Besu is a Java Ethereum client released under Apache 2.0. It executes transactions in the EVM, updates state, and exposes a command-line interface (CLI) and JSON-RPC interfaces for node operation. This lets Solidity applications use familiar Ethereum development tools and APIs. EVM compatibility alone does not guarantee identical RPC details or deployment arrangements. [Official introduction](https://docs.besu-eth.org/).

On Ethereum mainnet, Besu is an execution-layer client (EL). It connects to a consensus-layer client (CL), such as Teku, through the Engine API to build and validate execution payloads. The clients share JSON Web Token (JWT) authentication material. Staking additionally requires validator duties on the consensus side of the stack. Starting a Besu process alone does not create a complete Ethereum validator. [Besu and Teku mainnet tutorial](https://docs.besu-eth.org/public-networks/tutorials/besu-teku-mainnet).

A permissioned network has a different arrangement. Besu validators participate in block consensus through Quorum Byzantine Fault Tolerance (QBFT) or Istanbul Byzantine Fault Tolerance (IBFT) 2.0. This path does not need an Ethereum beacon consensus client. The documentation recommends QBFT for private networks and still provides [IBFT 2.0 documentation](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/ibft). [QBFT documentation](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft).

![Besu deployment roles: a mainnet consensus client connects to Besu execution through the Engine API, while permissioned Besu validators use QBFT or IBFT 2.0 with their peers. Signing, RPC access control, and data privacy require separate design.](/images/posts/besu-state-of-play-2026/besu-deployment-roles.svg)

*Original conceptual diagram based on the official mainnet and QBFT documentation. It distinguishes shared execution functions from consensus boundaries without making a particular external product or plugin mandatory.* [Enlarge the original SVG](/images/posts/besu-state-of-play-2026/besu-deployment-roles.svg)

QBFT assumes an approved validator set. The documentation requires signatures from at least two-thirds of validators and warns that block production stalls if more than one-third stop participating. Even replacing one node at a time in a four-node deployment can fail if another remaining node is already slow or disconnected. A rolling-upgrade procedure needs to inspect actual participation. [QBFT operating constraints](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft).

Key responsibilities also need to be separated. Application transaction signing, peer-to-peer (P2P) node identity, QBFT validator keys, and mainnet staking keys are different concepts. The official introduction directs application key management outside the client, for example to Web3Signer. That does not eliminate the other keys a node or validator requires. An operational runbook should name the owner and recovery responsibility for each key class. [Key management guidance](https://docs.besu-eth.org/).

## Changes demonstrated by 2026 releases

The official GitHub release API lists eleven non-prerelease 2026 releases from 26.1.0 through 26.9.0. That count excludes release candidates (RCs). The apparent month in a tag is not its publication date: 26.2.0, for example, was published on March 5. This is evidence of continuing development, rather than an automatic guarantee of production reliability. [Release history](https://github.com/besu-eth/besu/releases).

The table selects releases with major changes.

| Published date (UTC) | Release | Operator relevance |
| --- | --- | --- |
| 2026-02-03 | [26.1.0](https://github.com/besu-eth/besu/releases/tag/26.1.0) | Parallel Bonsai state-root computation |
| 2026-03-05 | [26.2.0](https://github.com/besu-eth/besu/releases/tag/26.2.0) | Removal of Fast Sync and Ethereum Classic support |
| 2026-04-22 | [26.4.0](https://github.com/besu-eth/besu/releases/tag/26.4.0) | Repository migration and removal of pure Clique network support |
| 2026-05-12 | [26.5.0](https://github.com/besu-eth/besu/releases/tag/26.5.0) | Experimental Bonsai Archive storage changes requiring a full resync |
| 2026-06-04 | [26.6.0](https://github.com/besu-eth/besu/releases/tag/26.6.0) | Java Development Kit (JDK) 25 requirement, stricter RPC arguments, BFT mixed-version compatibility option |
| 2026-07-13 | [26.7.0](https://github.com/besu-eth/besu/releases/tag/26.7.0) | Block Access List parallel-execution implementation |
| 2026-08-19 | [26.8.0](https://github.com/besu-eth/besu/releases/tag/26.8.0) | Discovery configuration changes and Plugin API module extraction |
| 2026-09-01 | [26.8.1](https://github.com/besu-eth/besu/releases/tag/26.8.1) | Log-filter address limit and removal of the dev-network option |
| 2026-09-25 | [26.9.0](https://github.com/besu-eth/besu/releases/tag/26.9.0) | Security-update notice, native tracers, and default exit on out-of-memory (OOM) errors |

## Parallel execution and the limits of performance claims

Transaction execution and state-root computation are useful separate lenses on Besu performance. Execution handles EVM operations and state reads and writes. State-root computation calculates the hashes of the state tree after those changes. Accelerating either stage can leave the other as a bottleneck.

The [Bonsai parallel transaction execution documentation](https://docs.besu-eth.org/public-networks/concepts/parallel-transaction-execution) describes an optimistic approach. Besu executes transactions in the background while also proceeding through sequential processing. When a transaction's turn arrives, a completed background result can be applied if it does not conflict with earlier state changes. Conflicting work is replayed. If the background result is not ready, execution proceeds sequentially. This does not arbitrarily reorder Ethereum transactions.

The benefit therefore depends on the workload. Repeated updates to the same storage slot can require more replay than transactions touching independent state. The current [option reference](https://docs.besu-eth.org/public-networks/reference/options#bonsai-parallel-tx-processing-enabled) gives the Bonsai parallel-processing option a default of `true`. Checking the setting is only a starting point; processing time and conflict or replay behavior are more useful operational measurements.

State-root computation has gained parallelism too. A maintainer [article published April 20, 2026](https://www.lfdecentralizedtrust.org/blog/optimizing-besu-performance-parallelizing-state-root-computation) describes collecting and sorting updates, then partitioning work across independent trie subpaths. Child results are combined into parent hashes, with persistence performed in batches. Publication of the explanation and shipment of the feature happened on different dates: it became the Bonsai default in 26.1.0, released February 3.

The authors reported up to a 40% reduction in mainnet block-processing time on an eight-core, eight-thread system with non-NVMe storage. They expected smaller relative gains on NVMe and described sensitivity to physical core count and storage characteristics. This is not a promise that every server gains 40% in transactions per second (TPS). Reduced block-processing time and higher network-wide throughput are different measurements.

For an external comparison, Nethermind published its original [GigaGas benchmark](https://www.nethermind.io/blog/getting-ethereum-ready-for-gigagas) on December 16, 2025. It replays identical blocks on the same hardware and snapshot, separating real blocks from synthetic workloads formed by merging blocks. As a competing client team's experiment, it is useful for examining methodology and the conditions tested. It does not establish a ranking of October 2026 binaries.

## Storage choices and historical-data services

The current documentation identifies Bonsai as the default storage format. It is designed to reduce storage needs and support direct access to recent state. Forest remains documented. The removal of particular Forest commands should not be read as removal of the entire storage format. [Storage formats](https://docs.besu-eth.org/public-networks/concepts/data-storage-formats), [26.2.0](https://github.com/besu-eth/besu/releases/tag/26.2.0).

Capacity numbers need to be read alongside the service a node provides. The documentation estimates approximately 1.14 TB for a Bonsai SNAP full node and 12 TB for a Forest FULL archive node. The former is explicitly based on May 2026 burn-in results for the 26.5.0 release cycle on AWS `m8g.2xlarge` instances. These nodes offer different historical-state coverage. This is neither a compression comparison between equivalent services nor a permanent minimum disk specification.

Ordinary Bonsai historical access also differs from Bonsai Archive. The documented default historical block limit for ordinary Bonsai is 512. It controls how far back state may be reconstructed for queries; changing it does not directly shrink the database. A service requiring older `eth_call` results or `eth_getProof` responses needs more verification than checking that the node has reached the chain head. [Historical access](https://docs.besu-eth.org/public-networks/concepts/data-storage-formats#accessing-data).

Bonsai Archive has progressed, but treating it like the established ordinary Bonsai mode would hide migration costs. Both [26.4.0](https://github.com/besu-eth/besu/releases/tag/26.4.0) and [26.5.0](https://github.com/besu-eth/besu/releases/tag/26.5.0) warn that experimental Archive column-family changes require a full resync. An evaluation should test historical balances, execution, state proofs, and recovery independently. Archive proofs appearing on a roadmap do not guarantee production support for proofs at every historical block.

History expiry is another dimension. Removing old block bodies and receipts is different from retaining historical world state. The official [pre-merge pruning documentation](https://docs.besu-eth.org/public-networks/how-to/pre-merge-history-expiry) says pruning retains headers and genesis while removing bodies and receipts. The old online option, `--history-expiry-prune`, has been deprecated since 26.1.0. If an indexer requires older receipts, agree on retention and restoration before pruning. Optimizing disk use alone can break an application's data contract.

## Removed enterprise features and remaining extensions

Tessera-based privacy belongs in migration history, rather than a current feature list. [25.6.0](https://github.com/besu-eth/besu/releases/tag/25.6.0) records removal of Tessera privacy and smart-contract-based onchain permissioning. [25.7.0](https://github.com/besu-eth/besu/releases/tag/25.7.0) records removal of the `EEA` and `PRIV` RPC groups. These are shipped removals, beyond an announcement of future deprecation.

Local node and account permissioning and permissioning plugins remain separate options. Contract-based validator selection in the QBFT documentation is also distinct from the removed onchain node and account permissioning system. Grouping every contract-related feature under the same removal would lead to incorrect deployment decisions. [Local permissioning](https://docs.besu-eth.org/private-networks/how-to/use-local-permissioning), [QBFT validator selection](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft).

Restricting membership does not automatically make replicated EVM state confidential between participants. A financial network needing private transaction state or selective disclosure must examine the trust assumptions and data distribution of a separate privacy layer. It should not assume that a new plugin is a drop-in replacement for the old private-transaction APIs.

Synchronization and consensus support have changed as well. Fast Sync was removed in 26.2.0. In 26.4.0, Besu lost the ability to start or mine on pure Clique networks, while retaining support for syncing chains that began with Clique and subsequently transitioned to PoS. Current consensus operation and historical-chain compatibility therefore need separate checks. [26.2.0](https://github.com/besu-eth/besu/releases/tag/26.2.0), [26.4.0](https://github.com/besu-eth/besu/releases/tag/26.4.0).

## Shipped implementation and remaining plans

The maintainers' February 4 [retrospective and goals](https://www.lfdecentralizedtrust.org/blog/a-deep-dive-into-besu-milestones-2025-highlights-and-2026-goals) describe peer discovery, Bonsai Archive, and plugin expansion as 2026 work. Treating that article as a current status table would miss later releases. By 26.8.0, the release notes document `--discovery-mode` choices of V4, V5, and BOTH, with V4 as the default. The former `v5Bootnodes` field was moved into a unified `bootnodes` array. [26.8.0](https://github.com/besu-eth/besu/releases/tag/26.8.0).

Block Access List (BAL) parallel execution appears in 26.7.0. Implementation, a testnet schedule, and mainnet activation require different evidence. Release 26.9.0 schedules Amsterdam on Sepolia for October 6, 2026 at 13:53:36 UTC. Its tagged [Sepolia configuration](https://github.com/besu-eth/besu/blob/26.9.0/config/src/main/resources/sepolia.json) contains that timestamp; its [mainnet configuration](https://github.com/besu-eth/besu/blob/26.9.0/config/src/main/resources/mainnet.json) contains no Amsterdam activation time. Those artifacts alone do not establish that the new rules are live on mainnet. [26.7.0](https://github.com/besu-eth/besu/releases/tag/26.7.0), [26.9.0](https://github.com/besu-eth/besu/releases/tag/26.9.0).

The Plugin API needs the same distinction. Feature-specific module extraction has shipped, with existing modules re-exported through `besu-plugin-api`. Release 26.9.0 also warns that future package, signature, and lifecycle changes will not all be source compatible. This does not mean every plugin is already broken. It does mean plugin operators need an API migration workstream alongside core-client upgrades. [Plugin change notice](https://github.com/besu-eth/besu/releases/tag/26.9.0).

## October security advisories and patch verification

Read advisories published after the September release. The [signature recovery advisory](https://github.com/besu-eth/besu/security/advisories/GHSA-4h4f-925g-8h9p) and [typed-transaction decoding advisory](https://github.com/besu-eth/besu/security/advisories/GHSA-cgvq-9xfq-c54j), both published October 14, describe possible consensus disagreements and list 26.8.0 as patched. Publication dates do not identify when a defect was introduced or establish observed exploitation.

The individual fixes [`ebaf89e162`](https://github.com/besu-eth/besu/compare/ebaf89e162...26.9.0) and [`facf43ddb9`](https://github.com/besu-eth/besu/compare/facf43ddb9...26.9.0) associated with the [tracing-limit advisory](https://github.com/besu-eth/besu/security/advisories/GHSA-qfmh-cxw4-9h66) are included in the 26.9.0 tag. The tagged [`DebugTraceTransaction.java`](https://github.com/besu-eth/besu/blob/26.9.0/ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/methods/DebugTraceTransaction.java) also applies a server-side step limit. [PR #11378](https://github.com/besu-eth/besu/pull/11378), merged September 30, was a post-release reconciliation of released commits into `main`.

Released limits and later hardening need to be distinguished. The additional September 30 commit [`7f904a379c`](https://github.com/besu-eth/besu/commit/7f904a379cf5b59e7016118d64f6d68abadf69a2) extends the step ceiling to the batch JSON-RPC path for the `debug_traceBlock` family. That follow-up commit is not included in the 26.9.0 tag. Shipment of the earlier limits therefore does not establish the safety of every tracing path.

Operators can check their artifact's patches and enabled RPC paths, restrict `DEBUG` and `TRACE` access to trusted callers, or disable unused namespaces. The QBFT P2P path has a [separate availability advisory](https://github.com/besu-eth/besu/security/advisories/GHSA-g5j7-4r2x-rx9j). RPC and consensus communication each need protection.

## Maintenance and adoption evidence

The LFDT [2026 annual report](https://lf-decentralized-trust.github.io/governance/project-updates/2026/2026-annual-Besu/) reviews 2025 and lists 21 active maintainers, approximately 19 from Consensys. This supports examining organizational concentration. It is not an October 15 personnel census or a measurement of individual workload and substitutability. My assessment is that release activity and organizational diversity should be evaluated separately. Active development can coexist with concentrated staffing risk.

I would not reuse that report's EL stake-share estimate as current market share. Reachable node share, stake share, and the number of operating institutions have different denominators. Combining them without a methodology and reference time can misrepresent client diversity.

There are named institutional examples. The [2026 adoption material](https://www.lfdecentralizedtrust.org/ledger-insights-report-2026), commissioned by LFDT from Ledger Insights, lists Citi Token Services, Fnality, and Clearstream D7 as Besu projects. It covers both production systems and projects on a path toward production. The inventory across all LFDT technologies is not a Besu customer count, and an institution's total assets under custody are not Besu onchain transaction value. The examples establish use cases; they do not let us calculate the total installed base or production-conversion rate.

## Community operating observations

An [Eth Docker operator post](https://www.reddit.com/r/ethstaker/comments/1vtatpn/eth_docker_2681_with_5_months_rolling_expiry/) pairs experimental rolling-expiry support with receipt dependencies in downstream services. It illustrates both interest in disk savings and the compatibility work that comes with them. This account concerns particular tooling and services; it does not establish a pruning policy for every Besu deployment or a community-wide assessment.

## An operator upgrade checklist

The following sequence is proposed operational guidance derived from the documented changes. Adapt it to the network's availability objectives and retention policy.

1. **Record the node's role and dependencies.** Distinguish a mainnet EL, permissioned validator, RPC service, and archive serving an indexer. Record CL, plugin, and external signer versions alongside Besu. Identical client versions can require different acceptance checks.
2. **Compare original release notes with security advisories.** Read the intervening breaking changes between the installed version and the target tag. Verify relevant fixes in the target tag using individual commits and release source.
3. **Test Java and process recovery first.** JDK 25 is required from 26.6.0. Release 26.9.0 makes exit on OOM the default. Check the production Java Virtual Machine (JVM), service-manager restart policy, and repeated-exit alerts together. [26.6.0](https://github.com/besu-eth/besu/releases/tag/26.6.0), [26.9.0](https://github.com/besu-eth/besu/releases/tag/26.9.0).
4. **Exercise real RPC requests and responses.** Account for strict hexadecimal arguments in 26.6.0, the default 1,000-address log-filter limit in 26.8.1, and `eth_feeHistory` validation changes in 26.9.0. Verify application handling of error codes as well as successful results. [26.8.1](https://github.com/besu-eth/besu/releases/tag/26.8.1), [26.9.0](https://github.com/besu-eth/besu/releases/tag/26.9.0).
5. **Rehearse mixed-version BFT operation.** Release 26.6.0 documents `--Xbft-legacy-protocol-encoding` for rolling upgrades involving 25.x nodes. Define the replacement sequence and when to remove compatibility settings, rather than copying them permanently. Check real block progress and consensus participation after every step. [26.6.0 BFT fix](https://github.com/besu-eth/besu/releases/tag/26.6.0).
6. **Test restoration and historical queries separately.** A backup's existence matters less than whether a restored node returns the required blocks, receipts, and state proofs. Include resync time when evaluating pruning or experimental archive changes.
7. **Compare metrics under comparable workloads.** Track block-processing time, RPC latency, heap and garbage collection (GC), free disk, peer connectivity, and QBFT round changes before and after replacement. Sync completion and process survival alone do not establish service health.

Besu's Java execution environment and QBFT support remain concrete reasons to evaluate it. A deployment also needs to account for removed privacy features, the migration cost of experimental archive storage, and planned Plugin API changes. Selecting a recent tag starts the upgrade; validating the service contract completes it.

## Further reading

- [Besu and Teku on mainnet](https://docs.besu-eth.org/public-networks/tutorials/besu-teku-mainnet): a starting point for EL/CL connectivity and signing responsibilities.
- [QBFT configuration](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft): validator management and fault-tolerance constraints.
- [Nethermind's GigaGas experiment](https://www.nethermind.io/blog/getting-ethereum-ready-for-gigagas): workload design and reproducibility in client comparisons.

## References

The following sources and the release and advisory links in the body were retrieved on October 15, 2026 KST. Undated documentation describes the retrieved version; measurements retain the separate evidence dates stated above.

- [Besu repository and releases](https://github.com/besu-eth/besu/releases): Besu maintainers; see each tag's actual publication date.
- [LFDT launch announcement](https://www.lfdecentralizedtrust.org/announcements/linux-foundation-decentralized-trust-launches-with-17-projects-100-founding-members): LF Decentralized Trust, September 16, 2024.
- [Official documentation](https://docs.besu-eth.org/), [storage formats](https://docs.besu-eth.org/public-networks/concepts/data-storage-formats), [parallel execution](https://docs.besu-eth.org/public-networks/concepts/parallel-transaction-execution), [options](https://docs.besu-eth.org/public-networks/reference/options), [history expiry](https://docs.besu-eth.org/public-networks/how-to/pre-merge-history-expiry), [local permissioning](https://docs.besu-eth.org/private-networks/how-to/use-local-permissioning): Besu documentation.
- [2025 performance accomplishments and 2026 roadmap](https://www.lfdecentralizedtrust.org/blog/boosting-besu-performance-2025-accomplishments-and-2026-roadmap): Besu maintainers, November 19, 2025.
- [2025 highlights and 2026 goals](https://www.lfdecentralizedtrust.org/blog/a-deep-dive-into-besu-milestones-2025-highlights-and-2026-goals): Besu maintainers, February 4, 2026.
- [Parallel state-root computation](https://www.lfdecentralizedtrust.org/blog/optimizing-besu-performance-parallelizing-state-root-computation): Karim Taam and Ameziane Hamlat, April 20, 2026.
- [2026 annual project report](https://lf-decentralized-trust.github.io/governance/project-updates/2026/2026-annual-Besu/): retrospective of 2025 submitted to LFDT TAC; an exact publication day is not separately stated.
- [2026 institutional adoption material](https://www.lfdecentralizedtrust.org/ledger-insights-report-2026): LFDT and Ledger Insights, 2026 report.
- [Besu security advisory index](https://github.com/besu-eth/besu/security/advisories): individual publication dates and patch evidence linked in the body.
- [Eth Docker and rolling expiry](https://www.reddit.com/r/ethstaker/comments/1vtatpn/eth_docker_2681_with_5_months_rolling_expiry/): yorickdowne, r/ethstaker; tooling and downstream compatibility discussion.
