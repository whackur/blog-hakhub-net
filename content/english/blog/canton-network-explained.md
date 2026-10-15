---
title: "Understanding Canton Network: Financial Privacy, Atomic Settlement, and Institutional Adoption"
meta_title: "Canton Network Architecture and Adoption (October 2026)"
description: "How Daml contracts, selective disclosure, the Global Synchronizer, and Canton Coin fit together, with a stage-by-stage assessment of DTCC, Tradeweb, MUFG, and other institutional announcements."
date: 2026-10-15T09:00:00+09:00
lastmod: 2026-10-15T09:00:00+09:00
image: "/images/posts/canton-network-explained/cover.png"
categories: ["Blockchain"]
tags: ["canton", "daml", "tokenization", "institutional-finance", "privacy", "settlement"]
author: "whackur"
translationKey: "canton-network-explained"
draft: false
---

Buying a security changes records in several places. A trading venue records the execution, a custodian records the securities position, and a bank maintains the cash ledger. Each institution has its own account of the transaction. Reconciliation checks that amounts, rights, and processing states agree. A single public database might appear to simplify the problem, but institutions cannot publish their customers' balances and trading strategies to everyone operating the infrastructure.

Canton is a distributed ledger protocol built around that tension. **The parties involved share the state they need, while changes across applications can be combined into one transaction.** Contract permissions determine who receives information. Canton Network is the ecosystem of applications and infrastructure connected using that protocol. The [protocol specification](https://docs.canton.network/overview/reference/canton-protocol-specification) is the starting point for understanding the distinction.

This article explains the contract and consensus model before examining adoption. The status check is dated **October 15, 2026, KST**. It covers the official documentation and institutional announcements linked below, rather than an inspection of every institution's private ledger or live deployment. Completed trades, product support, proofs of concept, and launch plans represent different kinds of progress.

## The financial state institutions need to share

A buyer can pay without receiving a security, or a seller can deliver without receiving payment. Delivery versus Payment (DvP) links the two movements to reduce that settlement exposure. On Canton, appropriately modeled cash and securities contracts can be consumed and replacement ownership contracts created within the same Daml transaction. The [cross-Synchronizer DvP example](https://docs.canton.network/overview/reference/cross-sync-dvp-example) illustrates the mechanics and their prerequisites.

The parties need different information. A securities registrar needs to know that ownership changed, but generally does not need the buyer's entire cash balance. A payment bank does not need every holding in a counterparty's securities portfolio. Canton distributes the relevant parts of a transaction to the participants that need them. This restriction operates at the ledger and protocol level, rather than merely hiding columns in an application screen. The [privacy model](https://docs.canton.network/overview/learn/privacy-model) therefore belongs alongside the business model in an architectural review.

Reconciliation still has a role. Shared contract state can agree while external banking processes, custody books, corporate actions, or price sources require integration. A token's legal rights also depend on arrangements outside the protocol. Evaluating a deployment starts with identifying the records managed jointly and those left in external systems. Introducing a ledger does not automatically remove those boundaries.

## Daml, the protocol, and the public infrastructure

Canton materials often discuss a language, a network, an infrastructure service, and a token together. They occupy different layers. The [Splice architecture documentation](https://docs.canton.network/sdks-tools/api-reference/splice-architecture) explains the operational applications that sit on the shared infrastructure.

| Name | Role |
| --- | --- |
| Daml | A smart contract language for data, actions, and authorization. Daml-LF is its compiled execution representation. |
| Canton Protocol | Distributed contract validation, selective disclosure, message ordering and outcome coordination, and contract reassignment. |
| Canton Network | The connected ecosystem of Canton applications, institutions, and synchronization infrastructure. |
| Synchronizer | A service that coordinates message ordering and transaction outcomes among connected participants. |
| Global Synchronizer (GS) | Shared public synchronization infrastructure. Applications can also use dedicated Synchronizers. |
| Splice | Applications implementing GS governance, Canton Coin, validator operations, and related services. |
| Canton Coin (CC) | A utility token associated with purchasing GS traffic and rewarding qualifying contributions. |

Running a Canton deployment and connecting an application to the public GS are separate decisions. An institution's use of Daml does not establish that all its activity consumes GS traffic. Nor does the notional value of the institution's assets translate directly into token expenditure. A connected ecosystem can contain different operators, access policies, and synchronization services.

There are also three useful historical dates. The [protocol whitepaper dated February 4, 2020](https://www.canton.io/publications/canton-whitepaper.pdf) already describes Daml-based ledger interoperability. Digital Asset and participating institutions [announced Canton Network on May 9, 2023](https://blog.digitalasset.com/press-release/new-global-blockchain-network-of-networks-for-financial-market-participants-and-institutional-assets). The [GS and Canton Coin go-live announcement](https://www.prnewswire.com/news-releases/the-canton-networks-global-synchronizer-and-canton-coin-go-live-302186479.html) followed on July 1, 2024. The protocol's history, the institutional network announcement, and the public service's launch are distinct events.

## Business state as contracts that are created and consumed

A Daml contract instance is immutable after creation. A change of ownership usually consumes an existing contract and creates another describing the new holding. This resembles a UTXO-style model, but it should not be confused with Bitcoin's fixed payment and scripting model. Contracts can represent trade proposals, custody delegations, collateral requests, or other multi-party workflows as well as assets. The [detailed ledger model](https://docs.canton.network/overview/reference/ledger-model-detailed) defines the state and authorization semantics.

A `template` defines contract data and rules. An instance has its own contract identifier. A `choice` expresses an action available on that contract. A successful consuming choice makes the original contract unavailable for another consumption, and applications must track the identifiers of any replacements. A `nonconsuming` choice preserves its target contract but can still create or consume other contracts. It is not necessarily a read-only operation. These distinctions are covered in the [Daml language reference](https://docs.canton.network/appdev/reference/daml-language-reference).

Three roles matter when reading a model:

| Role | Meaning |
| --- | --- |
| `signatory` | Supplies the authority required to create a contract. |
| `controller` | Has authority to exercise a particular choice. |
| `observer` | Receives contract information without automatically acquiring authority to exercise choices. |

Consider a proposal from A that B must accept. A can create a proposal with B as an observer. B exercises an acceptance choice, and the resulting authorization context can support a contract involving both parties. Consuming the proposal prevents it from being accepted twice. This is an illustration of authorization, rather than a complete securities issuance or bank payment implementation.

Application login is another layer. A logged-in user, an API user's `actAs` or `readAs` permissions, a contract controller, and a signing key are not interchangeable identities. Knowing a contract identifier does not grant authority over it. Reviewing an application requires tracing the relationship between the person shown in its interface and the party whose authority the ledger actually recognizes. The [security guidance](https://docs.canton.network/appdev/modules/m7-security) covers this boundary between application access and ledger operations.

## Parties, participants, and Super Validators

A party is an identifier used for contract roles and authorization. It can represent a person, organization, or process, but does not automatically equal an Ethereum address or bank customer number. A participant hosts parties, stores their contract data, executes commands, and validates relevant transactions. One participant can host multiple parties; hosting and confirmation arrangements can also involve multiple participants for a party. [Smart Contract Consensus](https://docs.canton.network/overview/reference/smart-contract-consensus) explains these relationships.

A validator deployment can include a participant, the Splice validator application, user administration, and traffic management. A Super Validator (SV) has a different role in operating public GS sequencing, mediation, and governance. Treating a user's participant and an SV as identical global execution validators obscures the privacy design. SVs coordinate operational changes through the jointly hosted Decentralized Synchronizer Operator (DSO) party, as described in the [governance reference](https://docs.canton.network/overview/reference/sv-governance-reference). An institution's appointment as an SV also does not mean all its financial products have moved to Canton.

![Parties use hosting participants that retain authorized contract views and check execution; a common Synchronizer orders encrypted messages and coordinates the outcome through sequencers and mediators](/images/posts/canton-network-explained/architecture.svg)

Original conceptual diagram based on the [protocol specification](https://docs.canton.network/overview/reference/canton-protocol-specification) and [ordering documentation](https://docs.canton.network/overview/reference/ordering-consensus). Arrows represent logical message exchanges. Protocol messages between participants and mediators also pass through sequencers. Issuers, custodians, and detailed hosting topology are omitted. [View full-size SVG](/images/posts/canton-network-explained/architecture.svg)

## Execution confirmation and ordering consensus

Canton separates checking a transaction's execution from agreeing on message order. Relevant participants receive authorized transaction views and check the required conditions, including contract activity, authorization, and execution results. A Synchronizer's sequencers order and deliver messages. Mediators collect the required confirmations and determine approval, rejection, or timeout. These services do not need to decrypt the financial payload to perform their coordination role. [Execution consensus](https://docs.canton.network/overview/reference/smart-contract-consensus) and [ordering consensus](https://docs.canton.network/overview/reference/ordering-consensus) describe the two layers.

The stakeholder in Proof of Stakeholder is a stakeholder in a contract. **It is not ordinary coin-weighted Proof of Stake.** Holding more CC does not provide authority to validate arbitrary financial contracts. Required confirmations and thresholds depend on protocol policies and hosting topology. Nor does the name mean every observer manually signs each transaction in a wallet. An external user signature and a participant's protocol confirmation are different steps.

In a conceptual transaction flow, the submitting participant interprets a command and checks the relevant contracts, parties, packages, and synchronization route. It sends encrypted views to the required recipients. Receiving participants validate their views and return confirmations; the coordinated result is then delivered and applied within each participant's authorized scope. Ordering is scoped to a Synchronizer. There is no requirement that every application expose one universal financial state under a single public block sequence.

The separation assigns different operational responsibilities. Participant operators manage hosted data and execution, while Synchronizer operators provide ordering, delivery, and coordination availability. A dedicated service relying on one operator has a different trust profile from shared public infrastructure. Claims about decentralization alone do not establish a particular deployment's fault tolerance. Its actual configuration and policies matter.

## Selective disclosure and its limits

Canton privacy combines contract authorization, selective replication, and encrypted message transport. Unrelated participants need not receive every input and output. However, the participant hosting a party processes that party's data. Moving signing keys to a hardware wallet does not automatically conceal contract information from the hosting operator. The [external-party documentation](https://docs.canton.network/overview/reference/external-party) helps distinguish signing authority from hosting and data processing.

An observer is not a field-level masking mechanism. Making someone an observer and hiding the amount in the UI does not reduce ledger-level access to that contract. A workflow that shares only a summary needs appropriate separation of sensitive data and reporting contracts. Fetches, explicit disclosure, and composition with other contracts can also affect what becomes visible. The [ledger model](https://docs.canton.network/overview/reference/ledger-model-detailed) should be checked against actual API results.

Encrypted financial payloads do not eliminate metadata. Message timing, size, and recipients remain a separate concern. Information already received by an authorized counterparty cannot simply be recalled. Logs, backups, operator access, and regulatory reporting need their own controls. Selective disclosure therefore does not mean complete anonymity or automatic compliance with privacy law. Supervisory access must also be modeled with the required permissions. The [privacy documentation](https://docs.canton.network/overview/learn/privacy-model) explains the technical mechanism, while each deployment still defines its business disclosure policy.

## Prerequisites for one atomic DvP

Suppose Alice's cash contract is on a Payments Synchronizer and Bob's security contract is on a Securities Synchronizer. Exchanging them requires a common place where the necessary contracts can be used. **All input contracts for one Daml transaction must be assigned to the same Synchronizer.** Canton does not leave arbitrary inputs on separate services and execute one transaction across both unchanged. The [multi-Synchronizer architecture](https://docs.canton.network/overview/learn/multi-synchronizer) and [DvP example](https://docs.canton.network/overview/reference/cross-sync-dvp-example) explain the reassignment mechanism.

1. Select a common settlement Synchronizer. Required parties, including payment and securities providers, need suitable hosting, participant connectivity, package vetting, and asset policies.
2. Reassign contracts that are elsewhere. They are unassigned from the source and assigned to the destination. A contract must not be consumable on both services at once.
3. Prepare cash and security inputs or allocations that match the trade. Check instruments, quantities, counterparties, executor authority, and deadlines.
4. Execute one Daml transaction on the common Synchronizer. It consumes the relevant inputs and creates the replacement cash and securities contracts. Failure of the required conditions causes the transaction's legs to fail together.
5. Observe the actual committed result. Output contracts can subsequently be reassigned if the business workflow requires it.

Reassignment is part of preparation. Between unassignment and assignment, a contract may temporarily be unavailable for business transactions. An issuer might prohibit the proposed common service, or a required package might not be vetted. Assets are not instantly composable merely because both are described as Canton assets. Atomicity of the final business transaction differs from immediate completion of the entire preparation and routing process.

Atomicity also has a defined perimeter. An all-or-nothing change to ledger contracts does not establish the legal finality of bank payment, ownership on a custodian's books, or an issuer's ability to redeem an asset. If a token represents an external record, that relationship needs examination. Transfers to other blockchains have additional protocols and trust assumptions. The internal DvP guarantee cannot be extended without qualification to arbitrary external chains.

## Differences from a typical public EVM

This comparison covers the usual execution models, rather than every EVM privacy extension or specialized deployment. The [Canton guide for Ethereum developers](https://docs.canton.network/appdev/modules/m2-canton-for-ethereum-devs) provides the technical context.

| Area | Typical public EVM | Canton's Daml execution model |
| --- | --- | --- |
| State changes | Updates to accounts and contract storage. | Creation and consumption of contract instances. |
| Authorization | Function logic and access-control patterns. | Signatories, controllers, and observers within the model. |
| Data distribution | Broad replication of public state and events. | Authorized views delivered to relevant participants. |
| Validation | The chain's execution and block-consensus system. | Execution confirmation separated from synchronization ordering. |
| Application interfaces | Solidity, ABI, and Ethereum JSON-RPC. | Daml, Ledger API, token standards, and wallet interfaces. |

The native Daml environment is not an EVM-compatible execution environment. Existing Solidity contracts and Ethereum RPC calls cannot simply be assumed to work with the same meaning. Separate EVM integration environments or middleware proposals should be assessed within their own scope. They do not make the native execution model identical to Ethereum. Tooling reuse requires checking the supported environment, assets, permissions, and deployment status.

Access has several layers too. Reading the code and building locally, applying to operate a production validator, and buying a particular security are different activities. The [official FAQ](https://www.canton.network/faq) says validator requests currently require sponsorship and distinguishes application-level permissioning. KYC, investor eligibility, and transfer restrictions belong to the asset and service operator. A public network does not imply unrestricted access to every financial product.

## Standards connecting assets, wallets, and applications

If every Daml asset exposes different templates and choices, each wallet or trading application needs custom integration. The Canton Token Standard supplies common interfaces for holdings, transfers, and assets allocated to settlement while allowing registries to retain their internal implementation. It connects asset registries, wallets and custody providers, and transaction or settlement applications. It does not standardize all legal rights or issuer policies. [CIP-0056](https://github.com/canton-foundation/cips/blob/main/cip-0056/cip-0056.md) defines the V1 baseline.

A Free of Payment (FOP) transfer does not combine a consideration leg with the transfer; the name does not mean zero fees. DvP uses allocations for specified settlement conditions before combining the legs. A wallet needs to show the instrument, amount, executor, and deadline that the user authorizes. Supporting the standard does not make every asset's recipient-acceptance or redemption rules identical.

V2, [CIP-0112](https://github.com/canton-foundation/cips/blob/main/cip-0112/cip-0112.md), extends the model for custody accounts, configurable visibility in batch settlement, and allocation or reuse of funds. These features address workflows such as a custodian tracking client entitlements or a venue settling multiple trades. In the raw proposal headers checked on October 15, V1 is `Final` and V2 is `Approved`. V2's approval date is June 12, 2026. Approval is not evidence that every production asset and wallet implements the features.

Mixed-version integrations need capability checks. A wallet that cannot interpret authority for repeated settlement must not present it as a one-off transfer. Unsupported economic conditions should be rejected safely, and the interface must match what is actually signed. The [V2 proposal](https://github.com/canton-foundation/cips/blob/main/cip-0112/cip-0112.md) describes the intended evolution; a particular product's implementation still needs verification.

The wallet-to-dApp interface is another layer. [CIP-0103](https://github.com/canton-foundation/cips/blob/main/cip-0103/cip-0103.md) standardizes primitives for account and network information and transaction preparation, signing, and execution. Its raw status is `Active`, with approval dated January 29, 2026. The interface helps decouple applications from a particular connectivity or key-management provider. It does not certify wallet security or customer admission. External signing still requires checking the prepared transaction and hash and observing ledger completion, as explained in the [signing guide](https://docs.canton.network/sdks-tools/sdks/wallet-sdk/guides/preparing-and-signing-a-transaction).

Operational software versions are separate from standard generations. The dashboard updated October 14 lists Canton 3.5.19 and Splice 0.8.4 for MainNet, whereas the [latest Canton release](https://github.com/digital-asset/canton/releases/tag/v3.6.1) is 3.6.1, published October 5. This compares official documentation with release metadata; it is not an independent survey of every production node. Use the [official compatibility dashboard](https://docs.canton.network/shared/version-compatibility-dashboard) for environment-specific combinations, and distinguish the latest binary release from production adoption. A higher package number does not prove every V2 feature is enabled. A feature available on DevNet should not automatically be assumed available on MainNet.

## Canton Coin and the cash leg of a trade

CC connects GS traffic purchases with rewards for qualifying contributions. Purchasing traffic burns CC, while rewards mint CC under the applicable rules. These are distinct flows. A large securities notional does not establish a proportionate quantity of token burning. The [GS tokenomics documentation](https://docs.canton.network/overview/reference/tokenomics-of-gs) explains traffic, pricing, and rewards.

Infrastructure usage costs also differ from asset-transfer costs. [CIP-0078](https://github.com/canton-foundation/cips/blob/main/cip-0078/cip-0078.md) removes specified CC fees; it does not declare GS traffic, custody services, or every other token registry free. An application or operator can pay traffic costs even when the end user sees no direct fee. Rewards depend on eligibility and policy, so creating more contracts alone is not a sufficient revenue model.

The cash asset exchanged for a security can be something else. Circle [announced USDCx availability on December 4, 2025](https://www.circle.com/blog/usdcx-on-canton-now-available-via-circle-xreserve). Depositing USDC into xReserve on Ethereum initiates a mint of USDCx by a decentralized protocol on Canton. USDCx is a USDC-backed protocol token. It should not be described as the identical token to Circle-issued USDC, and issuance and redemption paths deserve separate attention.

Paying for a security in USDCx and purchasing GS traffic with CC are different transactions. Growth in institutional collateral activity, GS usage, net token burning, and market price are separate claims. Supply, reward, usage, and liquidity data are needed to connect them. The adoption evidence below concerns technology and deployment stages, rather than an automatic token-price thesis.

## Institutional adoption by stage

The table records what the announcing organizations say they completed or support. Provider statements are not independent verification of private transaction records, custody positions, or customer deployments. Each event is classified separately because the names appearing in an ecosystem do not share one adoption stage.

| Announcement date | Organization and event | Verified announcement stage and scope |
| --- | --- | --- |
| 2026-10-05 | [Ripple Custody 1.43](https://docs.ripple.com/products/custody/support/change-history/v143) | Product support for holding and transferring CC and CIP-56 tokens using an external validator. Available on-premises and through the hybrid model for SaaS; requires ledger accounting refactor phase 2. Canton management is through the API in this release. It does not establish customer deployment volume. |
| 2026-09-28 | [LSEG appointed Super Validator](https://www.lseg.com/en/media-centre/press-releases/2026/lseg-appointed-as-a-super-validator-on-canton-network) | Infrastructure and governance participation. The release describes repo settlement using DiSH cash as PoCs. |
| 2026-08-27 | [Virtu, M1X, and Tradeweb repo](https://www.tradeweb.com/newsroom/media-center/in-the-news/first-fully-onchain-repo-transaction-completed-using-sovereign-digital-bond) | Completed transaction announcement covering an execution and repurchase cycle using sovereign digital bond USDM1 as collateral. |
| 2026-08-19 | [Ledger Canton support](https://www.ledger.com/blog-canton-coin-on-ledger-wallet) | Product support for CC. The product article describes wider privacy-enabled asset support as coming next. |
| 2026-08-13 | [MUFG and partners' JGB repo](https://www.mufg.jp/dam/pressrelease/2026/pdf/news-20260813-002_en.pdf) | Launch of a PoC linking book-entry Japanese government bonds and blockchain workflows, rather than a market-wide commercial service. |
| 2026-07-15 | [DTCC transactions with DTC-tokenized assets](https://www.dtcc.com/press-releases/2026/dtcc-turns-tokenization-into-reality) | Completed production trades on Canton and DTCC's private Besu network. The broader service launch is described separately as planned for October. |
| 2026-07-01 | [Tradeweb U.S. Treasury transaction](https://www.tradeweb.com/newsroom/media-center/news-releases/tradeweb-facilitates-landmark-on-chain-u.s.-treasuries-transaction-on-the-canton-network) | Completed trade announcement: Franklin Templeton sold, Virtu bought, and USDCx supplied the payment leg. |
| 2026-02-25 | [Chainlink data services](https://www.prnewswire.com/news-releases/chainlink-now-live-on-canton-accelerating-institutional-grade-tokenization-at-scale-302696344.html) | Data Streams, SmartData, and Proof of Reserve announced live. Canton CCIP deployment was a future plan in that release. |
| 2025-12-04 | [Circle xReserve and USDCx](https://www.circle.com/blog/usdcx-on-canton-now-available-via-circle-xreserve) | Availability and live-transaction announcement connecting USDC deposits to protocol-issued USDCx. |
| 2025-06-26 | [Nasdaq Calypso, QCP, and partners](https://ir.nasdaq.com/news-releases/news-release-details/nasdaq-and-qcp-set-new-standard-capital-efficiency-connecting) | Demonstrated integration of margin and collateral workflows. It does not announce migration of the entire Nasdaq stock market. |

DTCC's July announcement explicitly describes real production trades, which distinguishes it from a demonstration. It does not establish that the broader October service has already launched. On the October 15 check, [Canton's DTCC readiness page](https://www.canton.network/dtcc-tokenization-service-on-canton) continued to describe technical preparation for the October launch. The official DTCC material checked and that readiness page did not confirm completion of the full commercial launch. This is an observation within that source scope, not an exhaustive real-time check of every official channel.

Tradeweb's two events also involve different instruments. The July trade concerned a U.S. Treasury and USDCx. The August repo used USDM1, a Marshall Islands sovereign digital bond backed by U.S. Treasuries. USDM1 should not be relabeled a directly issued U.S. government bond or a stablecoin. Completing a transaction demonstrates a particular technical and business connection; repeat volumes, customer growth, and available liquidity require further evidence.

The MUFG PoC preserves the legal nature of book-entry JGBs while examining on-chain repo processes. A related [Secured Finance announcement](https://blog.digitalasset.com/press-release/secured-finance-to-provide-lending-protocol-for-mitsubishi-ufj-trust-and-bankings-proof-of-concept-for-on-chain-japanese-government-bond-jgb-repo-transactions) describes its protocol-provider role. The example illustrates why moving workflow state onto a blockchain can differ from replacing the legal ownership register.

Custody and infrastructure announcements have a different significance from trade announcements. Ripple adds a product route for managing Canton assets alongside institutional authorization policies. Ledger expands access to CC with hardware signing. LSEG's SV appointment adds an infrastructure and governance role. Product support and appointments alone cannot establish how much real customer value is being used on the network.

Chainlink data and cross-chain connectivity also need separate checks. The [official Data Streams changelog](https://docs.chain.link/changelog/data-streams-expands-to-canton) confirms its Canton expansion. The later [September 28, 2026 CCIP 2.0 announcement](https://chain.link/blog/introducing-ccip-2-0) does not itself specify a Canton launch. It is not used here as evidence that Canton CCIP deployment is complete. Data availability, application usage, and cross-chain transfer support are separate capabilities.

## Public discussion and financial metrics

Public discussion combines interest in institutional use with questions about access and control. A [Reddit discussion of atomicity and privacy](https://www.reddit.com/r/defi/comments/1s69u2y/chains_with_atomicity_privacy_features/) includes criticism of Canton's permissioning. A short discussion cannot represent all users or verify performance. It does expose a useful reader question: public infrastructure, validator admission, and access to a financial product need separate explanations.

The [developer forum](https://forum.canton.network/top) includes questions about participant-scoped queries, custody accounts, reassignment, and package compatibility. Interoperable interfaces and privacy provide a starting point; a working integration still needs explicit decisions about authority, visibility, and recovery. The existence of a question is not proof of a defect in the current release. Equally, a vendor's explanation is not an independent user review.

Large financial numbers need their original units and scope. DTCC's **$114 trillion in 2025** describes its depository subsidiary's custody and asset-servicing base. It is not Canton TVL or the amount already tokenized by this service. Daily or monthly repo notional is a flow that can include repeated use of the same collateral. It cannot be compared directly with a stock of assets locked at one time. Adding an institution's total customer assets or a venue's total trading volume to Canton assets would overstate the result. The [DTCC announcement](https://www.dtcc.com/press-releases/2026/dtcc-turns-tokenization-into-reality) provides the context for its figure.

Useful adoption questions remain concrete: which asset and cash moved together, which parties saw the necessary information, and which Synchronizer carried the transaction? Repeated operation, redemption rights, and legal ownership need their own evidence. The official material shows progress in connecting collateral and settlement workflows, expanding custody interfaces, and participating in shared infrastructure. Understanding those developments begins with contracts and operational boundaries before token prices.

## Further reading

- [Canton Protocol Specification](https://docs.canton.network/overview/reference/canton-protocol-specification): Transaction views and confirmation mechanics.
- [Cross-Synchronizer DvP Example](https://docs.canton.network/overview/reference/cross-sync-dvp-example): Reassignment and prerequisites for a common settlement service.
- [Canton Token Standard](https://docs.sync.global/app_dev/token_standard/index.html): Integration between registries, wallets, and settlement applications.

## References

All web sources were checked on October 15, 2026. Dated announcements describe the scope stated by their authors; the completed-trade, PoC, support, and planned-launch classifications above apply.

- [2020 Canton whitepaper](https://www.canton.io/publications/canton-whitepaper.pdf), [2023 Network announcement](https://blog.digitalasset.com/press-release/new-global-blockchain-network-of-networks-for-financial-market-participants-and-institutional-assets), [2024 GS and CC go-live](https://www.prnewswire.com/news-releases/the-canton-networks-global-synchronizer-and-canton-coin-go-live-302186479.html).
- [Splice architecture](https://docs.canton.network/sdks-tools/api-reference/splice-architecture), [ledger model](https://docs.canton.network/overview/reference/ledger-model-detailed), [Daml language](https://docs.canton.network/appdev/reference/daml-language-reference), [security guidance](https://docs.canton.network/appdev/modules/m7-security).
- [Smart Contract Consensus](https://docs.canton.network/overview/reference/smart-contract-consensus), [Ordering Consensus](https://docs.canton.network/overview/reference/ordering-consensus), [privacy](https://docs.canton.network/overview/learn/privacy-model), [multi-Synchronizer architecture](https://docs.canton.network/overview/learn/multi-synchronizer).
- [Ethereum developer guide](https://docs.canton.network/appdev/modules/m2-canton-for-ethereum-devs), [external parties](https://docs.canton.network/overview/reference/external-party), [signing guide](https://docs.canton.network/sdks-tools/sdks/wallet-sdk/guides/preparing-and-signing-a-transaction), [FAQ](https://www.canton.network/faq), [version dashboard](https://docs.canton.network/shared/version-compatibility-dashboard).
- [CIP-0056](https://github.com/canton-foundation/cips/blob/main/cip-0056/cip-0056.md), [CIP-0112](https://github.com/canton-foundation/cips/blob/main/cip-0112/cip-0112.md), [CIP-0103](https://github.com/canton-foundation/cips/blob/main/cip-0103/cip-0103.md), [CIP-0078](https://github.com/canton-foundation/cips/blob/main/cip-0078/cip-0078.md), [GS tokenomics](https://docs.canton.network/overview/reference/tokenomics-of-gs), [SV governance](https://docs.canton.network/overview/reference/sv-governance-reference), [Canton 3.6.1 release](https://github.com/digital-asset/canton/releases/tag/v3.6.1).
- [DTCC production trades](https://www.dtcc.com/press-releases/2026/dtcc-turns-tokenization-into-reality), [DTCC readiness](https://www.canton.network/dtcc-tokenization-service-on-canton), [Tradeweb Treasury trade](https://www.tradeweb.com/newsroom/media-center/news-releases/tradeweb-facilitates-landmark-on-chain-u.s.-treasuries-transaction-on-the-canton-network), [Tradeweb repo](https://www.tradeweb.com/newsroom/media-center/in-the-news/first-fully-onchain-repo-transaction-completed-using-sovereign-digital-bond).
- [MUFG PoC](https://www.mufg.jp/dam/pressrelease/2026/pdf/news-20260813-002_en.pdf), [Secured Finance role](https://blog.digitalasset.com/press-release/secured-finance-to-provide-lending-protocol-for-mitsubishi-ufj-trust-and-bankings-proof-of-concept-for-on-chain-japanese-government-bond-jgb-repo-transactions), [Circle USDCx](https://www.circle.com/blog/usdcx-on-canton-now-available-via-circle-xreserve).
- [Ripple Custody 1.43](https://docs.ripple.com/products/custody/support/change-history/v143), [Ledger support](https://www.ledger.com/blog-canton-coin-on-ledger-wallet), [LSEG SV appointment](https://www.lseg.com/en/media-centre/press-releases/2026/lseg-appointed-as-a-super-validator-on-canton-network), [Nasdaq Calypso](https://ir.nasdaq.com/news-releases/news-release-details/nasdaq-and-qcp-set-new-standard-capital-efficiency-connecting).
- [Chainlink joint announcement](https://www.prnewswire.com/news-releases/chainlink-now-live-on-canton-accelerating-institutional-grade-tokenization-at-scale-302696344.html), [Data Streams changelog](https://docs.chain.link/changelog/data-streams-expands-to-canton), [CCIP 2.0](https://chain.link/blog/introducing-ccip-2-0).
- [Canton developer forum](https://forum.canton.network/top), [Reddit privacy and atomicity discussion](https://www.reddit.com/r/defi/comments/1s69u2y/chains_with_atomicity_privacy_features/): Sources of questions and opinions, not protocol verification.
