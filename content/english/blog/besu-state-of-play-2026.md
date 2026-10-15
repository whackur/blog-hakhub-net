---
title: "Understanding Besu: From Ethereum Execution to Bank Token Payments"
meta_title: "Besu Explained: EVM, Execution Clients, Permissioned Networks and Project Hangang"
description: "Learn how the Java Ethereum execution client Besu processes transactions and state, how mainnet differs from permissioned networks, and what Korea’s Project Hangang and recent development show."
date: 2026-10-15T11:37:00+09:00
lastmod: 2026-10-15T12:03:15+00:00
image: "/images/posts/besu-state-of-play-2026/execution-settlement-cover-20261015.webp"
categories: ["Blockchain"]
tags: ["besu", "ethereum", "execution-client", "qbft", "enterprise-blockchain"]
author: "whackur"
translationKey: "besu-state-of-play-2026"
draft: false
---

**Besu is a Java Ethereum client that executes smart contracts and verifies and stores their results.** Banks can use it to build a ledger that handles deposit tokens alongside interbank settlement assets. It also serves as an execution client on Ethereum mainnet. These deployments share execution technology, while the issuers of money and the parties that finalize the ledger depend on the network. [Besu documentation](https://docs.besu-eth.org/)

The useful starting point for a bank's adoption of Besu is **which balances change, and who authorizes those changes**. The Bank of Korea's Phase 1 report on Project Hangang explicitly documents Besu, QBFT and ERC-20 compliant contracts. Retail users held bank deposit tokens, while banks settled with each other in central bank money. This is a concrete connection between Ethereum technology and institutional payments. [BOK Phase 1 report, appendix pp.42-44](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216)

## Banks process customer deposits and interbank settlement together

Suppose a customer of Bank A pays ₩10,000 to a customer of Bank B. A deposit token represents a deposit claim against its issuing bank. Simply transferring A's token would leave the recipient holding a claim on A. A design that gives the recipient a deposit at their own bank, B, also needs settlement between the banks. Hangang's burn-and-issue model retires the sending bank's tokens, issues the receiving bank's tokens and settles between them in central bank money. [Phase 1 report, appendix p.43](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216)

The following simplifies that principle into a ₩10,000 payment. Assume sufficient balances and issuance permissions, with no fees. The table illustrates balance changes rather than reproducing Hangang's contract calls or accounting entries.

| Record that changes | Change caused by payment | Meaning |
| --- | --- | --- |
| A customer's deposit tokens issued by A | Decrease by ₩10,000 | A's deposit liability to that customer falls |
| A's institutional settlement asset | Decrease by ₩10,000 | A pays the interbank settlement amount |
| B's institutional settlement asset | Increase by ₩10,000 | B receives settlement money |
| B customer's deposit tokens issued by B | Increase by ₩10,000 | B's deposit liability to its customer rises |

When these assets occupy the same ledger, a smart contract can combine the changes into one transaction. If failure in an intermediate step causes the whole transaction to revert, the sender's tokens cannot disappear while the recipient receives nothing. This is atomic settlement. Hangang's report describes a design that completes the interbank payment only if all three stages succeed. Payments between customers of the same bank used a direct token transfer, without interbank settlement or burning and reissuance. [Phase 1 report, appendix pp.43-44](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216)

This property holds within the state controlled by the contract. The EVM cannot reverse a request that an application has sent to an external banking system, or recall goods already delivered. Connecting external assets requires a separate procedure for deciding which system's record establishes completion.

## Besu reproduces the state change behind a signed request

Processing a payment requires code that defines its meaning. A contract written in Solidity is compiled into bytecode and deployed. The **Ethereum Virtual Machine (EVM)** supplies the rules and environment for executing that bytecode. It checks conditions, reads and writes storage, and accounts for computational work in gas. [Ethereum's EVM explanation](https://ethereum.org/en/developers/docs/evm/), [Solidity compiler](https://docs.soliditylang.org/en/latest/using-the-compiler.html)

Besu is the node software around that EVM. It receives transactions, communicates with peers, verifies and stores execution results, and handles applications' JSON-RPC requests. Geth and Nethermind are execution clients at the same layer. A network is the ledger those nodes share under common rules. Besu can join mainnet or start a separate bank network from a different genesis, so the software's name alone does not identify the money or ledger being used. [Besu introduction](https://docs.besu-eth.org/), [Ethereum nodes and clients](https://ethereum.org/en/developers/docs/nodes-and-clients/)

### What changes when someone sends ten tokens

Consider a narrower execution example: Alice sends ten tokens to Bob using an ordinary ERC-20 contract. Assume no transfer fees or additional restrictions; ten is a human-readable quantity after accounting for token decimals. The interbank payment above requires additional burning, issuance and permission checks.

1. **The wallet constructs a transaction calling the token contract.** Its `to` field contains the contract's address, while the call data encodes `transfer(Bob, amount)`. The native-currency `value` field is separate from the token amount. ERC-20 balances are managed in the token contract's storage, distinct from an account's native-currency balance. [ERC-20](https://eips.ethereum.org/EIPS/eip-20), [Ethereum accounts](https://ethereum.org/en/developers/docs/accounts/)
2. **A signer authorizes the request and submits it to a node.** The transaction includes a nonce tracking the account's transaction sequence, a gas limit and other fields. A signed transaction can be submitted to Besu using `eth_sendRawTransaction`. The returned hash identifies the transaction; it is not yet evidence of a completed payment. [Transaction structure](https://ethereum.org/en/developers/docs/transactions/), [JSON-RPC](https://ethereum.org/en/developers/docs/apis/json-rpc/#eth_sendrawtransaction)
3. **The included transaction executes.** In the assumed contract, if Alice started with 100 tokens and Bob with zero, success leaves them with 90 and ten. The contract also emits a `Transfer` event. If execution reverts because a condition fails, such as insufficient tokens, that call's state changes are undone. An included failed transaction can still incur execution gas charges. [ERC-20](https://eips.ethereum.org/EIPS/eip-20), [Ethereum transactions](https://ethereum.org/en/developers/docs/transactions/)
4. **The application checks execution and finality.** It reads the receipt's status and logs and checks that the intended contract state was reached. ERC-20 permits implementations that return `false`, so receipt success alone cannot establish a successful transfer for every token. The application also checks whether the containing block has finalized under the network's rules. [Receipt API](https://ethereum.org/en/developers/docs/apis/json-rpc/#eth_gettransactionreceipt), [ERC-20 return-value requirements](https://eips.ethereum.org/EIPS/eip-20)

Other nodes verify the results under the block's transaction order and execution rules. The state root cryptographically commits to the resulting account and storage state. It lets nodes check that they have reproduced the contract's balance calculations. It does not establish whether a bank issuing those tokens can honor redemption. [EVM state transitions](https://ethereum.org/en/developers/docs/evm/)

### Parallel execution reuses conflict-free results

This execution model gives context to Besu's performance development. Its optimistic parallel execution computes transactions in the background, then reuses results that do not conflict with earlier transactions during ordered processing. Conflicts cause replay; unfinished background work falls back to sequential execution. The optimization preserves the required order and balances. Workloads touching the same accounts or shared liquidity state can require more replay, so a simple-transfer result cannot be treated as a TPS guarantee for a banking network. [Besu parallel execution](https://docs.besu-eth.org/public-networks/concepts/parallel-transaction-execution)

How long results remain queryable is a separate choice. Bonsai, the default storage format, is designed for current and recent state access. A service reading today's balance has different retention needs from one reconstructing contract state years ago. A node validating the latest blocks should not automatically be assumed to answer every historical-state query needed for an audit. [Storage formats](https://docs.besu-eth.org/public-networks/concepts/data-storage-formats)

## Validators determine the accepted blocks and trust structure

Checking the calculation and agreeing on the shared sequence of blocks are connected tasks with different responsibilities. On Ethereum mainnet, Besu handles execution. It connects to a consensus client such as Teku over an authenticated Engine API, while the consensus layer follows the chain under proof-of-stake (PoS) rules. Validator software adds block proposal and voting duties to ordinary node operation. Running Besu alone does not complete a staking setup. [Besu and Teku on mainnet](https://docs.besu-eth.org/public-networks/tutorials/besu-teku-mainnet)

Banks building a separate network can arrange consensus among approved validators. **Quorum Byzantine Fault Tolerance (QBFT)**, recommended in Besu's documentation, is a proof-of-authority (PoA) protocol for this setting. Designated validators take turns proposing blocks and collect the required supermajority of signatures to finalize them. This path does not require a mainnet beacon consensus client. [QBFT documentation](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft)

| Decision | Besu on Ethereum mainnet | A separate QBFT network |
| --- | --- | --- |
| Transactions executed | Transactions against mainnet state and contracts | Transactions against contracts deployed on that network |
| Consensus participation | Separate consensus client and PoS validator system | Approved QBFT validator set |
| Operational trust | Ethereum's public protocol and validator system | Institutions governing validator admission and changes |
| Assets and fees | Mainnet assets, execution fees paid in ETH | Network-specific issuance and redemption, separately chosen gas pricing |

QBFT still requires enough participating validators. The official guide warns that losing more than one third stops block production. Three cooperating validators in a four-validator setup differ from a situation where two are offline. Four servers controlled by one company through the same administration account also create a different trust structure from four institutions operating independently. [QBFT failure conditions](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft)

A private network can set its gas price to zero. Customers may then avoid acquiring a fee token, but transaction and block gas limits and server costs remain. The won value represented by a token and the computational work needed to execute its contract are different units. [Free gas configuration](https://docs.besu-eth.org/private-networks/how-to/configure/free-gas)

### A client release and network activation have different scopes

**The latest stable release checked on October 15, 2026 was 26.9.0, published September 25 UTC.** It includes security fixes and schedules the Amsterdam execution-layer upgrade on Sepolia. The Ethereum Foundation's Glamsterdam announcement separates Sepolia from mainnet; the mainnet schedule remains undecided in the checked announcement. Shipping a Besu implementation of a rule does not establish that every network has activated it. [Official release](https://github.com/besu-eth/besu/releases/tag/26.9.0), [Ethereum Foundation announcement](https://blog.ethereum.org/en/2026/09/17/glamsterdam-testnet-announcement)

Contract portability has the same boundary. Solidity's `evmVersion` must match the execution rules activated on the destination chain. Deploying identical code on a separate network does not move the original contract's balances, collateral, or dependencies on oracles and liquidity. Besu's code and tooling compatibility is separate from the work of connecting assets across ledgers. [Solidity EVM target settings](https://docs.soliditylang.org/en/latest/using-the-compiler.html#setting-the-evm-version-to-target)

## Hangang connected bank tokens through central bank settlement

The Bank of Korea's **December 2025 Phase 1 report** describes the Digital Currency System (DCS) as a permissioned ledger built with Besu. Appendix page 42 identifies QBFT consensus, ERC-20 compliant digital-money contracts and role-based access controls separating central bank and commercial bank authority. These are documented implementation details of that pilot. ERC-20 use does not establish anonymous participation or settlement on Ethereum mainnet. [Phase 1 report](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216)

The live pilot ran from **April 1 to June 30, 2025**. BOK researchers' ECB Forum 2026 paper records seven participating banks, approximately 80,000 users and approximately 12,000 merchants. Users converted deposits into tokens for payments, with institutional central bank money used for interbank settlement. This does not mean that seven banks each operated a separate commercial Besu chain. [Hangang paper, §3.2, p.16](https://www.ecb.europa.eu/pub/pdf/sintra/ecb.forumcentbankpub2026_Shin_paper.sk.pdf)

The paper describes the central bank as the authoritative validator. The generic QBFT model above does not establish that banks have authority equal to the central bank. Both the consensus algorithm and the participating institutions' mandates matter. [Hangang paper, §2.1, pp.4-6](https://www.ecb.europa.eu/pub/pdf/sintra/ecb.forumcentbankpub2026_Shin_paper.sk.pdf)

Integration outside the ledger remained a constraint. In the arrangement documented by the paper, DCS and the existing BOK-Wire+ system lacked a direct real-time connection; institutional settlement liquidity was prefunded and balances reconciled offline. Atomic settlement inside the ledger did not complete an automated, continuously available connection to the existing central bank account system. [Hangang paper, §§3.1-3.2, pp.14-17](https://www.ecb.europa.eu/pub/pdf/sintra/ecb.forumcentbankpub2026_Shin_paper.sk.pdf)

Work in 2026 broadened the use cases. The BOK's **October 8 explanation** says the subsidy project for medium-speed electric-vehicle charging facilities was underway, while follow-up live transactions with the general public were being prepared for later that year. The completed Phase 1 pilot, the ongoing subsidy project and the future public relaunch have different statuses. This update does not establish the complete 2026 node configuration or Besu version. [BOK October 8 update](https://www.bok.or.kr/portal/bbs/B0000347/view.do?nttId=11065408&menuNo=201106)

## Banks separately design issuance authority and data access

Authority to validate a block is separate from authority to issue deposit tokens. Validators check execution validity; contracts and business rules must still specify which accounts may request issuance and within what limits. Institutions retain responsibility for customer identification, redemption, settlement liquidity and disputes. Hangang's separate role-based contract permissions make sense in this context. [Phase 1 report, appendix pp.42-44](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216)

Permissioning controls which nodes may connect or which accounts may submit transactions. Besu applies local allowlists at each node. That control alone does not hide amounts or contract state from institutions participating in execution. **Membership and confidentiality are different requirements.** Current feature support matters here: Tessera privacy and the old onchain node/account permissioning were removed in 25.6.0. An old tutorial's privacy feature is therefore insufficient evidence for a current design. [Local permissioning](https://docs.besu-eth.org/private-networks/how-to/use-local-permissioning), [25.6.0 release](https://github.com/besu-eth/besu/releases/tag/25.6.0)

Hangang's Phase 1 report distinguishes ledger records needed for payment, including wallet addresses, amounts and timestamps, from supplementary identity and anti-money-laundering information exchanged through an off-chain message channel. Bank key management and connections to existing systems were additional components. This is a documented example of designing identity, signing and business integration around Besu, rather than a guarantee that all transaction information is cryptographically concealed. Besu itself does not manage users' signing keys inside the client. [Phase 1 report, appendix pp.44-46](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216), [Besu key-management scope](https://docs.besu-eth.org/)

The case for Besu rests on a need to place multiple institutions' assets and payment conditions in one execution environment and verify the results together. Without that need, existing databases and integration systems remain relevant alternatives. Hangang supplies a concrete basis for evaluation: distinguish the ledger executing EVM-compatible contracts, the institutions finalizing it, and the institutions issuing and redeeming its money. Those roles explain both the results of token settlement and the work that remains.

## Further reading

- [Ethereum nodes and clients](https://ethereum.org/en/developers/docs/nodes-and-clients/): the distinct roles of execution nodes, consensus clients and validators.
- [ERC-20](https://eips.ethereum.org/EIPS/eip-20): token interfaces, return values and event requirements.
- [BOK Project Hangang Phase 1 report](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216): its appendix describes consensus, contracts and banking-system integration.

## References

Sources checked on October 15, 2026. Release notes describe specific versions; Hangang's Phase 1 implementation is distinguished from subsequent work in 2026.

- [Besu documentation](https://docs.besu-eth.org/), [mainnet setup](https://docs.besu-eth.org/public-networks/tutorials/besu-teku-mainnet), [QBFT](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft).
- [EVM](https://ethereum.org/en/developers/docs/evm/), [accounts](https://ethereum.org/en/developers/docs/accounts/), [transactions](https://ethereum.org/en/developers/docs/transactions/), [JSON-RPC](https://ethereum.org/en/developers/docs/apis/json-rpc/), [ERC-20](https://eips.ethereum.org/EIPS/eip-20), [Solidity compiler](https://docs.soliditylang.org/en/latest/using-the-compiler.html).
- [Parallel execution](https://docs.besu-eth.org/public-networks/concepts/parallel-transaction-execution), [storage formats](https://docs.besu-eth.org/public-networks/concepts/data-storage-formats), [free gas](https://docs.besu-eth.org/private-networks/how-to/configure/free-gas), [local permissioning](https://docs.besu-eth.org/private-networks/how-to/use-local-permissioning).
- [Besu 26.9.0](https://github.com/besu-eth/besu/releases/tag/26.9.0), [25.6.0](https://github.com/besu-eth/besu/releases/tag/25.6.0), [Glamsterdam testnet announcement](https://blog.ethereum.org/en/2026/09/17/glamsterdam-testnet-announcement).
- [Project Hangang: Live Pilot of a Unified Ledger Integrating Wholesale CBDCs and Tokenized Deposits](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216): Bank of Korea, December 2025.
- [A unified ledger in practice: lessons from Project Hangang](https://www.ecb.europa.eu/pub/pdf/sintra/ecb.forumcentbankpub2026_Shin_paper.sk.pdf): Ryu, Shin, Sung and Yun, ECB Forum 2026, revised after the July 1 presentation. A research paper expressing the authors' views.
- [How Project Hangang's wholesale digital currency differs from retail CBDC](https://www.bok.or.kr/portal/bbs/B0000347/view.do?nttId=11065408&menuNo=201106): Bank of Korea, October 8, 2026 (Korean).
