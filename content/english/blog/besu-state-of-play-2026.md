---
title: "Understanding Besu: From Ethereum Execution to Bank Token Payments"
meta_title: "Besu Explained: EVM, Execution Clients, Permissioned Networks and Project Hangang"
description: "Learn how the Java Ethereum execution client Besu processes transactions and state, how mainnet differs from permissioned networks, and what Korea’s Project Hangang and recent development show."
date: 2026-10-15T11:37:00+09:00
lastmod: 2026-10-15T13:33:05+09:00
image: "/images/posts/besu-state-of-play-2026/cover.png"
categories: ["Blockchain"]
tags: ["besu", "ethereum", "execution-client", "qbft", "enterprise-blockchain"]
author: "whackur"
translationKey: "besu-state-of-play-2026"
draft: false
---

Besu is an open-source Ethereum execution client written in Java. It can validate transactions on Ethereum mainnet or run a separate blockchain whose participating institutions are selected in advance. Using the same software does not make those networks share their money, participants or consensus mechanism. That distinction matters when reading about a financial institution adopting Besu. [Besu documentation](https://docs.besu-eth.org/)

Suppose several banks build a token payment network with Besu. They can draw on Solidity contracts and familiar Ethereum development tools. Their deposit tokens do not thereby become mainnet ETH, and mainnet validators do not guarantee the banks’ payments. The execution facilities supplied by the client and the trust relationships established by the institutions need separate explanations.

This guide starts with the relationship between the EVM, a client and a network, then follows a token transfer. It moves on to permissioned consensus and an illustrative interbank payment design before examining Korea’s Project Hangang and recent Besu development. Release and support information that can change is identified as **checked on October 15, 2026**.

## EVM, client and network

The Ethereum Virtual Machine (EVM) defines the rules and environment for executing smart-contract bytecode. Its instructions cover operations such as arithmetic, branching and reading or writing storage, with gas accounting for execution. Solidity is a language for writing contracts; the EVM executes the bytecode produced by its compiler. Nodes do not pass Solidity source files around and execute the source directly. [Solidity compiler documentation](https://docs.soliditylang.org/en/latest/using-the-compiler.html)

Besu is the **complete node software** that includes this execution environment. It accepts transactions, communicates with peers, stores blocks and state, executes contracts and exposes JSON-RPC to applications. JSON-RPC is an interface for requesting remote procedure calls (RPC) using JSON messages. The EVM handles execution within that larger system. Treating “Besu” and “EVM” as interchangeable leaves transaction propagation, disk storage and the consensus interface unexplained. [Besu introduction](https://docs.besu-eth.org/)

Geth and Nethermind are also Ethereum execution clients. They are implementations that compete with Besu or participate alongside it, rather than different kinds of virtual machines placed next to Besu. To participate in the same network, clients must produce the same execution result for the same ordered transactions under the active protocol rules. Their internal data structures and optimizations can differ. [Ethereum nodes and clients](https://ethereum.org/en/developers/docs/nodes-and-clients/)

A network is the shared ledger in which those software instances participate. Its genesis, chain ID, protocol activation schedule and rules for finalizing blocks establish its boundaries. Installing Besu on two machines does not automatically connect them to the same chain. A mainnet node and a bank node configured with a separate genesis record different state. [Besu network options](https://docs.besu-eth.org/public-networks/reference/options)

| Layer | Responsibility | Relationship to Besu |
| --- | --- | --- |
| Solidity | Express contract behavior in source code | Compile the code, then deploy and execute the result |
| EVM | Execute bytecode and account for gas | An execution component inside Besu |
| Execution client | Handle transactions, state, blocks and RPC | Implementations include Besu, Geth and Nethermind |
| Network | Define the shared ledger, protocol and consensus rules | Separate networks can use the same client |

This separation also helps assess portability. An EVM-based environment can make code easier to reuse, but it does not mean two networks share assets. Compatible execution rules and continuity of the ledger are different properties.

## Accounts and state

Ethereum state includes account balances, nonces, code and storage information. A conventional private-key-controlled account authorizes transactions with signatures, while a contract account executes deployed code. Native currency balances and ERC-20 balances need to be distinguished: an ERC-20 balance is typically a value in the token contract’s storage. The node does not store every token in the account’s native currency balance field. [Ethereum accounts](https://ethereum.org/en/developers/docs/accounts/), [ERC-20](https://eips.ethereum.org/EIPS/eip-20)

Suppose `balanceOf(Alice)` on a token contract returns 100. That value belongs to that contract on that network. Alice does not acquire the same 100 tokens on another chain simply by using the same address there. Identical address strings can refer to different code, state and economic claims. Switching the network displayed in a wallet is not an asset transfer.

A transaction requests a change to this state. Nodes execute transactions in block order and check that the resulting state agrees with the block’s commitment. The state root is a cryptographic summary of the entire state. Rather than independently editing spreadsheets and comparing totals afterward, nodes reproduce state transitions using the same execution rules. Whether that code correctly represents a real claim or property right remains an application and institutional responsibility. [Transaction structure](https://ethereum.org/en/developers/docs/transactions/)

## Following an ERC-20 transfer

Consider Alice sending ten tokens to Bob. Assume a conventional ERC-20 contract is already deployed, without special transfer fees or restrictions. The amount here is expressed for readability; the actual call takes an integer adjusted for the contract’s decimal convention. This is an explanatory example, not a reconstruction of any financial system’s internal implementation.

1. **The wallet prepares call data.** The transaction destination is the token contract, rather than Bob. The `data` field encodes the selector and arguments for `transfer(Bob, amount)`. For a simple token transfer, the native currency `value` is normally zero. Confusing token quantity with the native currency amount creates a different transaction.
2. **A signer authorizes the transaction.** The signature covers the sender’s nonce, chain ID, gas limit and fee fields appropriate to the network. The nonce manages transaction ordering for that account. Applications should not assume Besu holds their users’ private keys: its documentation treats external signing and key management separately.
3. **An RPC node receives the signed transaction.** A wallet or backend submits it with `eth_sendRawTransaction`. The node checks validity, including signature, nonce and funding or fee conditions, as well as applicable permissioning rules. The returned hash identifies the submitted transaction; it does not guarantee block inclusion or a successful transfer.
4. **The transaction enters a block candidate.** A selection of pending transactions is drawn from the pool. Who is entitled to propose the block differs between mainnet proof of stake and permissioned QBFT. The node accepting the RPC request need not be the node producing the block.
5. **The EVM executes the contract.** The contract checks the sender’s balance and its conditions, then updates Alice’s and Bob’s balances in storage. A successful transfer also emits the ERC-20 `Transfer` event. Events let applications track changes; the current balances themselves are read from storage.
6. **Other nodes validate the result.** They check the state transition by executing the prescribed block order. Following the consensus process, the application checks the receipt’s execution status and logs and waits for its required level of finality. A reverted transaction can still be included in a block, and gas used in execution is accounted for separately.

The call interface and event come from [ERC-20](https://eips.ethereum.org/EIPS/eip-20). Transaction fields, lifecycle and the relationship between reverts and gas follow the [Ethereum transaction documentation](https://ethereum.org/en/developers/docs/transactions/). Key management and RPC responsibilities follow the [Besu introduction](https://docs.besu-eth.org/).

In this sequence, RPC is the entry point, the EVM supplies execution rules, storage holds execution results and consensus determines which blocks become the shared record. These layers do not substitute for one another. A successful RPC response can precede a contract revert. A local simulation can succeed while execution at the actual inclusion point encounters a different balance or price. Using `eth_call` to read or simulate execution also differs from finalizing a signed transaction.

An application can retain the transaction hash as a reference, while tying business-level payment completion to the execution result and the network’s finality rules. Retrying by blindly creating a new transaction risks duplicate payments. Assigning a unique identifier to a payment intent and reconciling contract state with backend records remain application design tasks after Besu has been selected. This is design advice derived from the transaction flow, rather than a guarantee supplied by a particular product feature.

## Solidity compatibility and portability

Running Solidity contracts on Besu has prerequisites. The compiler’s `evmVersion` must match the fork rules activated on the destination network. Bytecode using a new opcode may fail on a chain that has not enabled that instruction. Required precompiles and gas rules also need checking. The label “EVM compatible” cannot guarantee that every generation of bytecode works on every configuration. [Solidity EVM target settings](https://docs.soliditylang.org/en/latest/using-the-compiler.html#setting-the-evm-version-to-target)

The same reasoning applies to tools. Wallets, libraries and test tools built around JSON-RPC and contract application binary interfaces (ABIs) are useful starting points, but supported namespaces, response details, tracing and fee estimation still require verification. For example, [26.9.0](https://github.com/besu-eth/besu/releases/tag/26.9.0) tightened argument validation for `eth_feeHistory`. Following a standard does not promise that every existing application call continues unchanged.

External dependencies can present a larger obstacle. An application referencing a mainnet price oracle, token address, liquidity pool, bridge or another contract is incomplete if only its own code is moved. The destination needs those contracts and data providers, with the intended price meanings and redemption terms. A test that replaces those dependencies with mock responses does not establish real market liquidity.

Redeploying the same source on another network creates a separate instance. Existing user balances, storage, administrative permissions and deposited assets do not copy themselves over. A bridge or state migration needs additional rules: who locks or burns the original asset, which evidence the destination trusts and how supplies on both sides are reconciled. Installing Besu does not establish this economic connection.

### London, Prague, Osaka and active rules

Besu’s software version and its EVM revision names describe different things. `26.9.0` identifies a Besu distribution; London, Prague and Osaka name Ethereum execution-layer hardforks. These revisions can change gas accounting and transaction validation as well as EVM instructions. Besu implements rules from multiple periods rather than remaining fixed at London or Prague. The tagged 26.9.0 Java implementation, [`MainnetEVMs`](https://github.com/besu-eth/besu/blob/26.9.0/evm/src/main/java/org/hyperledger/besu/evm/MainnetEVMs.java), has separate EVM construction methods for London, Prague and Osaka.

The chain’s activation schedule determines which implemented rules apply. The same tag’s [mainnet configuration](https://github.com/besu-eth/besu/blob/26.9.0/config/src/main/resources/mainnet.json) contains the values below. London uses a block number, while Prague and Osaka use block timestamps. This selection is different from comparing package versions.

| Execution-layer revision | 26.9.0 mainnet configuration | Activation boundary |
| --- | --- | --- |
| London | `londonBlock: 12965000` | From block 12,965,000 |
| Prague | `pragueTime: 1746612311` | From that Unix timestamp |
| Osaka | `osakaTime: 1764798551` | From that Unix timestamp |

Evidence of Osaka support extends beyond a configuration field. The [25.11.0 release](https://github.com/besu-eth/besu/releases/tag/25.11.0) identifies itself as the Fusaka mainnet-ready release and explicitly adds Osaka, BPO1 and BPO2 activation times. Osaka is also present in the later 26.9.0 code and mainnet configuration. Conversely, an Amsterdam schedule in the 26.9.0 [release](https://github.com/besu-eth/besu/releases/tag/26.9.0) and [Sepolia configuration](https://github.com/besu-eth/besu/blob/26.9.0/config/src/main/resources/sepolia.json) does not establish mainnet activation. The same tag’s mainnet configuration has no Amsterdam activation time.

The distinction also applies when validating historical blocks. A current binary does not simply re-execute every old transaction under its newest rules. It selects the applicable rules using the block number or timestamp and the chain’s schedule. The tagged [`DefaultProtocolSchedule.getByBlockHeader`](https://github.com/besu-eth/besu/blob/26.9.0/ethereum/core/src/main/java/org/hyperledger/besu/ethereum/mainnet/DefaultProtocolSchedule.java) implements that selection. Knowing the rules needed to reproduce historical execution is separate from retaining the necessary historical state, so the archive requirements discussed below still matter.

For a separate permissioned chain, operators must check their agreed genesis and fork schedule alongside the implementation in their Besu version. Upgrading the binary alone does not guarantee activation of a desired revision. The milestone fields in the [genesis configuration reference](https://docs.besu-eth.org/public-networks/reference/genesis-items) are a starting point, but fork-specific consensus prerequisites and required system contracts also need verification. The mainnet evidence above does not guarantee that every fork works unchanged on QBFT. The evidence here consists of tagged source, configuration and releases; it is not a live RPC measurement of a chain’s current execution rules.

## Consensus on mainnet and a permissioned network

On Ethereum mainnet, Besu handles the Execution Layer (EL). It connects to a Consensus Layer (CL) client such as Teku through the Engine API to build and validate execution payloads. The two processes authenticate with JWT. Staking additionally requires validator duties on the consensus side; operating a regular node and operating a validator are different activities. Starting Besu alone does not complete a mainnet staking setup. [Besu and Teku setup](https://docs.besu-eth.org/public-networks/tutorials/besu-teku-mainnet)

A separate permissioned chain can instead have approved Besu validators agree on blocks. The official documentation recommends Quorum Byzantine Fault Tolerance (QBFT) for new enterprise configurations and also documents Istanbul Byzantine Fault Tolerance (IBFT) 2.0. This consensus path does not require a mainnet beacon consensus client. [QBFT](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft), [IBFT 2.0](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/ibft)

![On mainnet, a consensus client connects to Besu through the Engine API. On a permissioned network, approved Besu validators agree using QBFT or IBFT 2.0. Both configurations use the EVM, transaction pool and storage, while signing, RPC access control and privacy require separate design.](/images/posts/besu-state-of-play-2026/besu-deployment-roles.svg)

*Original conceptual diagram based on the official mainnet and QBFT documentation. It is not a deployment diagram for a particular financial institution.* [Enlarge SVG](/images/posts/besu-state-of-play-2026/besu-deployment-roles.svg)

In QBFT, validators take turns proposing blocks, with signatures from at least two thirds required for approval. The documentation warns that block production stops if more than one third of validators cannot participate. With four validators, a configuration that accommodates one unavailable validator can still run into trouble when two become unavailable together. Meeting the participation conditions for finalizing a block and successfully executing a contract are separate checks. [QBFT consensus conditions](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft)

The number of servers also differs from the number of independent operators. Four machines operated by one company under one cloud account can share failure modes and administrative authority. Participants must decide who adds or removes validators, whose consent is needed to change rules and which records govern a dispute. A small approved set does not inherit public Ethereum’s participation structure and economic security. These questions concern institutional relationships and governance as much as software performance.

## Zero gas price still leaves resource limits

A permissioned chain can be configured so users do not need to buy native currency to pay transaction fees. Besu’s [free gas guide](https://docs.besu-eth.org/private-networks/how-to/configure/free-gas) covers minimum gas prices and base fee settings after London, among other details. Transaction-accepting nodes and wallet fee settings must agree, so the configuration involves more than a single switch.

**Gas measures computation; gas price prices that unit.** A zero price leaves transaction and block gas limits in place. It does not remove the need to bound looping code or excessive storage writes. Operators still pay for CPU, disk and networking. A policy of not charging users directly does not make resources unlimited.

The ERC-20 example still requires execution to change balances. An insufficient gas limit can cause failure regardless of the token’s price. Even if a bank app shows customers only a fiat amount, its backend needs gas estimation, submission controls and an overload policy. The face value of the financial asset and the price of network resources belong to different parts of the design.

## Permissioning and transaction privacy

Permissioning controls which nodes may connect or which accounts may submit transactions. Besu’s local node and account allowlists are enforced by individual nodes, so operators need to coordinate policy across the network. They do not automatically create one shared permission list. [Local permissioning](https://docs.besu-eth.org/private-networks/how-to/use-local-permissioning)

Restricting connectivity does not automatically conceal data from participants that execute transactions and replicate state. Keeping a network off the public internet and keeping individual transactions private between participating banks are different requirements. Replacing a customer name with an address can still expose relationships or amounts. A privacy assessment should begin by identifying which participants can read raw transactions, state and logs.

Older tutorials describing Tessera private transactions no longer describe a current built-in feature. [25.6.0](https://github.com/besu-eth/besu/releases/tag/25.6.0) recorded removal of Tessera privacy and smart-contract-based onchain node and account permissioning. [25.7.0](https://github.com/besu-eth/besu/releases/tag/25.7.0) removed the `EEA` and `PRIV` RPC groups. Contract-based validator selection in QBFT is a different facility from the removed permissioning mechanism.

A financial system can evaluate separate encryption, selective-disclosure or data-separation mechanisms, but it must identify what each participant can verify and which parties it trusts. A plugin should not be presumed to replace the old privacy API completely. The distinction between audit information that must be available and customer information that must remain confidential deserves requirements work before selecting Besu.

## An illustrative interbank token payment

Consider a customer of Bank A paying KRW 10,000 to a customer of Bank B. The following hypothetical design explains what an EVM ledger can support. It does not reproduce Project Hangang’s contract addresses, APIs or deployment sequence, and does not assert that Hangang adopts ERC-20.

Simply transferring a token issued by one bank gives the recipient a claim on that issuing bank. Delivering a deposit at the recipient’s own bank requires a different structure. In addition to reducing A’s deposit tokens and increasing B’s, a settlement asset must move between the banks. One payment on a customer’s screen can involve coordinated changes to several kinds of ledger state.

Assume the same ledger holds both banks’ deposit tokens and an institutional settlement asset, with a contract authorized to perform the required operations. That contract could burn the sender’s A tokens, transfer the settlement asset from A to B and issue B tokens to the recipient. If all steps execute within one transaction and errors propagate as a full revert, the design can prevent partial payment. An external bank API call changes the boundary: EVM atomicity alone cannot roll back an outside system.

Authority and funding conditions matter. Arbitrary users must not be able to issue deposit tokens, and the design must define what happens when A lacks settlement liquidity. Customer identification, sanctions checks, refunds and dispute handling remain necessary. Contract issuance authority should be distinguished from a validator’s authority to propose blocks. Producing a block should not confer permission to create a bank’s liabilities at will.

Conditions based on external facts introduce oracles. The EVM cannot directly observe that goods have been delivered. Someone must provide that information under an agreed authority. Having multiple institutions execute the same contract does not make an incorrect delivery report true. The design’s benefit is the ability to coordinate assets on shared state; factual adjudication and legal responsibility remain institutional tasks.

## Korea’s Project Hangang

The Bank of Korea’s Project Hangang provides a documented Korean example. [*A unified ledger in practice: lessons from Project Hangang*](https://www.ecb.europa.eu/pub/pdf/sintra/ecb.forumcentbankpub2026_Shin_paper.sk.pdf), by Bank of Korea authors Jaemin Ryu, Hyun Song Shin, Joonyi Sung and Sung Guan Yun, is a slightly revised version of a paper presented at the ECB Forum on July 1, 2026. The authors state that their views do not necessarily reflect those of the Bank of Korea or its Monetary Policy Board (page 1).

The paper explicitly identifies Hyperledger Besu as the underlying technology for both Hangang’s Digital Currency System (DCS) and Project Agorá (section 4.2, page 24). Phase I live transactions ran from **April 1 to June 30, 2025**, involving approximately 80,000 users and 12,000 merchants. The seven banks were KB Kookmin, Shinhan, Woori, Hana, IBK, NongHyup and Busan (section 3.2, page 16). Their participation does not mean seven independently deployed Besu production networks.

Retail users held tokenized deposits, while banks settled in wholesale central bank money. Burning deposits at the sending bank, settling between banks and issuing deposits at the receiving bank formed a burn-and-issue arrangement intended to preserve the two-tier banking system (section 2.3, pages 8 and 9). The paper describes a proof-of-authority (PoA) arrangement with the central bank as authoritative validator (section 2.1, pages 4 to 6). It does not establish a specific QBFT configuration, and the payments should not be described as Ethereum mainnet settlement.

Reported results and subsequent plans require different treatment. Section 3.3 (pages 18 and 19) describes plans to broaden bank participation, improve usability and apply the platform to Treasury funds. Those schedules alone cannot confirm completion of every plan by October. The paper also records Phase I’s lack of a direct real-time gross settlement (RTGS) link and the burden of prefunding and offline reconciliation (page 17). Operating hours, legal characterization and liquidity remain commercialization issues, while an Agorá connection is being explored (pages 7 and 24 to 26). Possible interoperability is not evidence of a deployed international link.

Hangang’s DCS is the Korean Besu use directly verified and presented here. Hyperledger membership or a Fabric deployment is insufficient evidence to add another institution to that list. Hangang illustrates the use of Ethereum execution technology in an institutional payment design, while its currency and participation structure remain distinct from public Ethereum.

## Comparing Fabric and public Ethereum

Projects once grouped under the Hyperledger name can have different application architectures. In Fabric’s standard transaction flow, endorsing peers simulate a proposed chaincode execution. The ordering service orders transactions containing endorsements and read/write sets. Peers then validate endorsement policies and state conflicts before applying valid writes. This is a different development and transaction path from Ethereum’s EVM execution model. [Fabric transaction flow](https://hyperledger-fabric.readthedocs.io/en/latest/txflow.html)

Besu offers a route to a separate network while retaining Ethereum’s account model, Solidity bytecode and much of its tooling experience. Fabric is a relevant comparison when organization-specific endorsement policies shape the design. Existing contracts and development skills, transaction participation policy and data visibility are better starting points than declaring one framework universally suitable for enterprises. A framework’s name does not guarantee regulatory compliance or privacy.

Public Ethereum provides opportunities to interact with assets and applications already on a common ledger. It also entails public verification, network fees and the protocol’s rules. A permissioned network gives institutions more direct control over participation and change procedures, while leaving them to establish liquidity and access. Public Ethereum’s decentralization and ecosystem are not packaged inside the client binary for copying to another network. [Ethereum node architecture](https://ethereum.org/en/developers/docs/nodes-and-clients/)

My assessment is that a useful first question is which institutions need shared state and who can change its rules, before setting a TPS target. If one organization controls everything and external verification is unnecessary, a conventional database deserves comparison. The case for a shared execution ledger becomes more specific when several institutions need to verify contract results together and coordinate multiple assets within one transaction.

## State storage and historical queries

A node caught up to the latest block cannot necessarily answer every historical question. Current balances, contract execution at an old block, old transaction receipts and state proofs are distinct data requirements. The payment application described earlier needs different node services to display a current balance and to audit years of payments.

Besu’s default world-state storage format is Bonsai, designed around efficient current-state access and storage use. Forest of Tries remains documented. Ordinary Bonsai has a default historical block limit of 512. That is not simply a disk savings setting, and increasing the number does not by itself establish every archive capability. [Storage formats and data access](https://docs.besu-eth.org/public-networks/concepts/data-storage-formats)

The documentation’s estimates of roughly 1.14 TB for a Bonsai SNAP full node and 12 TB for a Forest FULL archive node describe different service scopes. The former comes from a particular AWS environment in May 2026. These are not compression ratios for equivalent databases or permanent minimum disk specifications. Evaluating the cost of historical state retention starts with fixing the query range the application requires.

Bonsai Archive is a separate experimental development path. [26.4.0](https://github.com/besu-eth/besu/releases/tag/26.4.0) and [26.5.0](https://github.com/besu-eth/besu/releases/tag/26.5.0) warned that storage changes required a full resync. Expiring old block bodies and receipts is also distinct from retaining historical world state. The official guide says headers and genesis remain, but indexers that require those receipts are affected. [History expiry](https://docs.besu-eth.org/public-networks/how-to/pre-merge-history-expiry)

A community operations report illustrates the same distinction. An [Eth Docker operator’s post](https://www.reddit.com/r/ethstaker/comments/1vtatpn/eth_docker_2681_with_5_months_rolling_expiry/) describes experimental Besu rolling-expiry support alongside constraints in downstream services that depend on receipts. It pairs the benefit of disk savings with a service compatibility burden. This is one tool operator’s observation, rather than a retention policy for every deployment or a community-wide assessment.

## What performance improvements change

Besu optimization extends beyond EVM instruction execution. State reads, writes and state-root calculation also affect block processing time. The official [parallel execution explanation](https://docs.besu-eth.org/public-networks/concepts/parallel-transaction-execution) describes optimistic execution in the background, followed by reuse of conflict-free results during canonical sequential processing. Conflicts require re-execution, while unavailable results fall back to the ordinary path. The optimization does not arbitrarily reorder block transactions.

Workloads that repeatedly modify the same account or storage differ from those operating on independent accounts. A many-user simple-transfer test therefore does not directly predict the performance of contracts updating a shared liquidity pool. Defaults and experimental conditions matter too: the current [option reference](https://docs.besu-eth.org/public-networks/reference/options#bonsai-parallel-tx-processing-enabled) lists Bonsai parallel transaction processing as enabled by default.

Parallel state-root calculation became a default in [26.1.0](https://github.com/besu-eth/besu/releases/tag/26.1.0). Maintainers Karim Taam and Ameziane Hamlat’s [April 20, 2026 explanation](https://www.lfdecentralizedtrust.org/blog/optimizing-besu-performance-parallelizing-state-root-computation) describes independent trie branch processing and batched persistence. Their eight-core, eight-thread non-NVMe test reduced block processing time by up to 40%, with smaller gains expected on NVMe. That result is not a TPS guarantee for an arbitrary banking network.

Block Access List execution in [26.7.0](https://github.com/besu-eth/besu/releases/tag/26.7.0) is another implementation development. Shipped code, testnet settings and mainnet activation require separate evidence. Benchmark comparisons also need hardware, state snapshots, block workloads and replay conditions. Another client team, Nethermind, sets out such conditions in its [benchmark methodology](https://www.nethermind.io/blog/getting-ethereum-ready-for-gigagas). It is a competing project’s experiment, rather than a universal ranking for today.

## The current project and support boundaries

Besu is an Apache 2.0 project under LF Decentralized Trust (LFDT). The foundation’s [September 16, 2024 launch announcement](https://www.lfdecentralizedtrust.org/announcements/linux-foundation-decentralized-trust-launches-with-17-projects-100-founding-members) explained that Hyperledger Besu would use the name Besu. Its current repository is [`besu-eth/besu`](https://github.com/besu-eth/besu), with the migration noted in [26.4.0](https://github.com/besu-eth/besu/releases/tag/26.4.0). Documents found under the old name do not necessarily describe current features.

The latest stable release returned by the official GitHub API on October 15, 2026 was **26.9.0**, published September 25 at 22:22 UTC. Its [release notes](https://github.com/besu-eth/besu/releases/tag/26.9.0) record native tracers, RPC validation changes and exiting on out-of-memory errors by default. [26.6.0](https://github.com/besu-eth/besu/releases/tag/26.6.0) introduced the JDK 25 requirement. These details inform runtime planning; they do not mean Besu’s basic concepts change each year.

Support statements need precise reading. [26.2.0](https://github.com/besu-eth/besu/releases/tag/26.2.0) removed Fast Sync, and [26.4.0](https://github.com/besu-eth/besu/releases/tag/26.4.0) removed starting or mining pure Clique chains. Synchronizing the history of chains that transitioned from Clique to PoS remains a separate supported case. Plugin modules are being separated, with future API and lifecycle breaks announced, but [26.9.0](https://github.com/besu-eth/besu/releases/tag/26.9.0) explicitly preserves a compatibility path through re-exported modules. Future plans should not be read as completed removals.

Foundation hosting and maintainer diversity are different properties. LFDT’s [2026 annual report](https://lf-decentralized-trust.github.io/governance/project-updates/2026/2026-annual-Besu/), reviewing 2025, lists approximately 19 of 21 active maintainers as Consensys-affiliated. This is evidence of organizational concentration at that time, rather than an October headcount or a measurement of individual replaceability. Active development and dependence on one source of engineering staff can coexist.

Adoption evidence is best read project by project. LFDT’s [institutional adoption report](https://www.lfdecentralizedtrust.org/ledger-insights-report-2026), commissioned from Ledger Insights, lists Citi Token Services, Fnality and Clearstream D7 among Besu examples. It includes production and preparation for production; the total number of LFDT cases is not a Besu customer count. Stake share, reachable node count, operating institutions and transaction value also have different denominators. This guide does not estimate current market share.

## Reading security fix history

Checking a version number does not complete a security assessment. The [signature recovery advisory](https://github.com/besu-eth/besu/security/advisories/GHSA-4h4f-925g-8h9p) and [typed transaction decoding advisory](https://github.com/besu-eth/besu/security/advisories/GHSA-cgvq-9xfq-c54j), published October 14, 2026, identify 26.8.0 as patched. Disclosure and patch release dates can differ, and publishing an advisory is not evidence that an attack was observed.

The individual tracing step-limit fixes [`ebaf89e162`](https://github.com/besu-eth/besu/compare/ebaf89e162...26.9.0) and [`facf43ddb9`](https://github.com/besu-eth/besu/compare/facf43ddb9...26.9.0) are included in 26.9.0. The subsequently merged [PR #11378](https://github.com/besu-eth/besu/pull/11378) reconciled already released commits into `main`. A later merge date does not establish that the patch was missing from the release.

A separate follow-up, [`7f904a379c`](https://github.com/besu-eth/besu/commit/7f904a379cf5b59e7016118d64f6d68abadf69a2), hardened step-ceiling enforcement for the batch `debug_traceBlock` family and is not included in 26.9.0. The shipped fixes and additional path hardening should be distinguished. Restricting public RPC access to `DEBUG` and `TRACE` and responding to the separate [QBFT P2P availability advisory](https://github.com/besu-eth/besu/security/advisories/GHSA-g5j7-4r2x-rx9j) protect different boundaries. This discussion does not certify a particular version as safe across every path.

## Turning the explanation into requirements

A practical evaluation can start with a short list. These are design recommendations from this guide, rather than guarantees listed in the documentation.

- Decide between a mainnet execution node and a separate permissioned ledger, then record consensus participants and authority to change the rules.
- Verify contract fork, opcode and precompile requirements, along with external contract, oracle and liquidity dependencies, on the destination chain.
- Separate application signing keys, validator keys and RPC permissions, and establish who can read each transaction’s data.
- Define requirements for current state, historical state, receipts and proofs before choosing storage and recovery tests.
- Check the target release, security fixes, Java and plugin compatibility together, and test consensus availability under failure conditions.

Understanding Besu makes the phrase “uses Ethereum technology” more precise. A system may share execution rules and tools while separately defining the legal meaning of money and rules for ledger participation. Keeping that distinction when reading about projects such as Hangang makes it possible to assess both their technical results and the institutional work that remains.

## Further reading

- [Ethereum nodes and clients](https://ethereum.org/en/developers/docs/nodes-and-clients/): execution and consensus clients and their roles on the public network.
- [ERC-20](https://eips.ethereum.org/EIPS/eip-20): the original token interface and event specification.
- [Fabric transaction flow](https://hyperledger-fabric.readthedocs.io/en/latest/txflow.html): endorsement, ordering and validation for comparison.

## References

Sources below were checked on October 15, 2026. Release dates use UTC. Living documentation is distinguished from reports describing a particular period.

- [Besu documentation](https://docs.besu-eth.org/), [source repository](https://github.com/besu-eth/besu), [options](https://docs.besu-eth.org/public-networks/reference/options).
- [Ethereum accounts](https://ethereum.org/en/developers/docs/accounts/), [transactions](https://ethereum.org/en/developers/docs/transactions/), [Solidity compiler](https://docs.soliditylang.org/en/latest/using-the-compiler.html).
- [Besu and Teku mainnet](https://docs.besu-eth.org/public-networks/tutorials/besu-teku-mainnet), [QBFT](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft), [IBFT](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/ibft), [free gas](https://docs.besu-eth.org/private-networks/how-to/configure/free-gas), [local permissioning](https://docs.besu-eth.org/private-networks/how-to/use-local-permissioning).
- [Hangang paper](https://www.ecb.europa.eu/pub/pdf/sintra/ecb.forumcentbankpub2026_Shin_paper.sk.pdf): Ryu, Shin, Sung and Yun, ECB Forum 2026, revised after the July 1 presentation. Sections and printed page numbers appear inline.
- [Storage formats](https://docs.besu-eth.org/public-networks/concepts/data-storage-formats), [history expiry](https://docs.besu-eth.org/public-networks/how-to/pre-merge-history-expiry), [parallel execution](https://docs.besu-eth.org/public-networks/concepts/parallel-transaction-execution), [parallel state-root calculation](https://www.lfdecentralizedtrust.org/blog/optimizing-besu-performance-parallelizing-state-root-computation), [Nethermind benchmark methodology](https://www.nethermind.io/blog/getting-ethereum-ready-for-gigagas).
- [Official releases](https://github.com/besu-eth/besu/releases): support and changes in the individually linked 25.6.0, 25.7.0, 26.1.0, 26.2.0, 26.4.0, 26.5.0, 26.6.0, 26.7.0 and 26.9.0 releases.
- [Security advisories](https://github.com/besu-eth/besu/security/advisories), [release reconciliation](https://github.com/besu-eth/besu/pull/11378), [tracing follow-up](https://github.com/besu-eth/besu/commit/7f904a379cf5b59e7016118d64f6d68abadf69a2). Individual tag ancestry comparisons are linked inline.
- [LFDT launch](https://www.lfdecentralizedtrust.org/announcements/linux-foundation-decentralized-trust-launches-with-17-projects-100-founding-members), [Besu annual report](https://lf-decentralized-trust.github.io/governance/project-updates/2026/2026-annual-Besu/), [institutional adoption report](https://www.lfdecentralizedtrust.org/ledger-insights-report-2026).
- [Eth Docker operator observation](https://www.reddit.com/r/ethstaker/comments/1vtatpn/eth_docker_2681_with_5_months_rolling_expiry/): experimental rolling expiry and downstream receipt dependencies. No exact publication date is asserted.
- [Tagged mainnet configuration](https://github.com/besu-eth/besu/blob/26.9.0/config/src/main/resources/mainnet.json), [Sepolia configuration](https://github.com/besu-eth/besu/blob/26.9.0/config/src/main/resources/sepolia.json), [EVM implementation](https://github.com/besu-eth/besu/blob/26.9.0/evm/src/main/java/org/hyperledger/besu/evm/MainnetEVMs.java), [protocol selection](https://github.com/besu-eth/besu/blob/26.9.0/ethereum/core/src/main/java/org/hyperledger/besu/ethereum/mainnet/DefaultProtocolSchedule.java), [25.11.0](https://github.com/besu-eth/besu/releases/tag/25.11.0), [genesis milestones](https://docs.besu-eth.org/public-networks/reference/genesis-items): implementation and chain activation evidence.
