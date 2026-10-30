---
title: "Binance Ethereum Wallet Incident and EIP-7702 Nonce-Range Spray"
meta_title: ""
description: "A detailed account of 50 valid Binance 14 delegation signatures, seven key transactions, later swaps, and the unresolved boundary of signing-authority compromise."
date: 2026-10-30T14:00:00+09:00
lastmod: 2026-10-30T14:53:07+09:00
image: "/images/posts/binance-eip-7702-nonce-spray-incident/cover.webp"
categories: ["Blockchain", "Security"]
tags: ["ethereum", "eip-7702", "binance", "custody", "incident-analysis"]
author: "whackur"
translationKey: "binance-eip-7702-nonce-spray-incident"
draft: false
---

<style id="binance-7702-mobile">
.content:has(#binance-7702-mobile) { overflow-wrap: anywhere; }
.content:has(#binance-7702-mobile) :not(pre) > code { white-space: normal; }
.content:has(#binance-7702-mobile) pre { max-width: 100%; overflow-x: auto; overflow-wrap: normal; }
.content:has(#binance-7702-mobile) pre code { white-space: pre; overflow-wrap: normal; }
.content:has(#binance-7702-mobile) table { display: block; max-width: 100%; overflow-x: auto; }
</style>

Early on October 30, 2026 in Korea, the Ethereum account labeled **Binance 14** by Etherscan acquired an EIP-7702 delegation. Three minutes and 24 seconds later, an external executor called the account, and ETH plus multiple ERC-20 tokens moved to the attacker recipient. The raw delegation transaction contains 50 valid signatures that recover to the victim account. The observed path is consistent with **account authority takeover using valid delegation signatures**. The available evidence does not establish a signature-verification bypass or a break of ECDSA. [Delegation transaction](https://etherscan.io/tx/0xad99264d5532ae0dd04b2004eebda05f25657e70dacb764f7ac8d4ccd051298b), [main sweep](https://etherscan.io/tx/0x53bd38b816c23e74134786c29a8c18d792777998a3b9326047b583100e88e2f3)

The central unresolved question is how those valid signatures were obtained. Theft of the private key itself, abuse of signing infrastructure, an approval-policy failure, and stolen pre-signed authorizations cannot be distinguished from the on-chain result alone. The signatures covering multiple nonces provide a clue, but do not settle that question.

This report covers the Ethereum Binance 14 delegation, seven representative transactions, a subsequent swap, and a dated balance observation. All event times use Korea Standard Time (KST, UTC+9); the initial incident falls on October 29 in UTC. [Unchained's report](https://unchainedcrypto.com/binance-says-user-funds-are-completely-safe-after-3-5-billion-drains-from-its-hot-wallets/) also discusses other chains and an overall loss figure. Neither that total nor the aggregate frozen amount has been independently reconciled here. The Ethereum evidence does not explain the reported BTC, Tron, Arbitrum, or Avalanche compromises as EIP-7702 attacks.

## Accounts and delegated authority

An EOA (externally owned account) is an account associated with a private key. A traditional EOA has no execution code of its own and is treated as an account that sends signed transactions. EIP-7702 allows it to delegate execution to code at another address, running in the EOA's own context. A subsequent call to the EOA can then execute that code with access to the EOA's assets and authority. [EIP-7702 specification](https://eips.ethereum.org/EIPS/eip-7702#specification)

The addresses in this report are listed below. Binance and Exploiter names are Etherscan labels; a label is not cryptographic proof of legal ownership or an attacker's identity.

| Role | Address |
| --- | --- |
| Victim account, Binance 14 | [0x28C6c06298d514Db089934071355E5743bf21d60](https://etherscan.io/address/0x28C6c06298d514Db089934071355E5743bf21d60) |
| External executor, Binance Hot Wallet Exploiter | [0x7C8601d4645b93cea45F71e118A729332e6B5CA0](https://etherscan.io/address/0x7C8601d4645b93cea45F71e118A729332e6B5CA0) |
| Main recipient, Binance Hot Wallet Exploiter 2 | [0x5227f603C1eE34CE3C06eFe6477003BDfCCB2f8c](https://etherscan.io/address/0x5227f603C1eE34CE3C06eFe6477003BDfCCB2f8c) |
| Delegate implementation | [0x63e842b054bd624a465454d533c33f573e9c6fae](https://etherscan.io/address/0x63e842b054bd624a465454d533c33f573e9c6fae) |
| Separate sending account, Binance 16 | [0xDFd5293D8e347dFe59E90eFd55b2956a1343963d](https://etherscan.io/address/0xDFd5293D8e347dFe59E90eFd55b2956a1343963d) |

The external executor submitted the delegation transaction and made the calls. Binance 14 is the signer authorizing delegation. Separating those roles explains how funds could move without an ordinary outgoing transaction originating from Binance 14.

## Seven transactions from delegation to repeat sweep

All seven transactions below display an overall Success status on the explorer. Token amounts retain the transaction-detail values. Asset quantities are more durable than dollar conversions that change with market prices.

### 1. 05:20:59 KST, delegation installed

[0xad99264d5532ae0dd04b2004eebda05f25657e70dacb764f7ac8d4ccd051298b](https://etherscan.io/tx/0xad99264d5532ae0dd04b2004eebda05f25657e70dacb764f7ac8d4ccd051298b), block `26300753`.

The external executor is From and Binance 14 is To. Etherscan displays Binance 14 delegating to the implementation above. [Blockaid's public analysis](https://x.com/blockaid_/status/2115924317888495661) describes a single type-4 transaction carrying 50 authorizations with different nonces, one of which matched. Raw transaction verification confirms the count, signer, delegate, and actual descending order.

### 2. 05:24:23 KST, main Binance 14 sweep

[0x53bd38b816c23e74134786c29a8c18d792777998a3b9326047b583100e88e2f3](https://etherscan.io/tx/0x53bd38b816c23e74134786c29a8c18d792777998a3b9326047b583100e88e2f3), block `26300770`.

The executor calls Binance 14. Internal transfers show `167,464.247856558836135296 ETH` moving from Binance 14 to the main recipient. The ERC-20 transfer list contains 63 entries, including:

- `1,615,409,498.97324 USDT`
- `62,597,239.679797044969015518 RLUSD`
- `29,934.013163146020067927 wBETH`

Some internal calls carry execution reverted warnings. The overall transaction nevertheless succeeded and displays successful transfers. Treating a failed internal call as a failed sweep would miss the actual asset movements. Nor do 63 transfer entries necessarily mean 63 distinct tokens.

### 3. 05:24:47 KST, separate ETH transfer from Binance 16

[0x51f263fa50966df6bbd7f8c6e6e99e3791c94444f7c4343b2fef1ee2d62fd39f](https://etherscan.io/tx/0x51f263fa50966df6bbd7f8c6e6e99e3791c94444f7c4343b2fef1ee2d62fd39f), block `26300772`.

Binance 16 sends `28,005.6 ETH` to the same recipient. This is separate from the preceding call to Binance 14. A shared recipient does not establish that Binance 16's initial compromise also used EIP-7702.

### 4. 05:41:23 KST, USDC moves from Hot Wallet 34

[0xdc102dd89dded5a83f1008906883ffb7c81ff3b7d7965d8c7277d170b5e17481](https://etherscan.io/tx/0xdc102dd89dded5a83f1008906883ffb7c81ff3b7d7965d8c7277d170b5e17481), block `26300855`.

The top-level From is the external executor and To is Binance 14. The token transfer, however, originates from the account labeled Binance: Hot Wallet 34, with `780,000,000 USDC` going to the main recipient.

Unchained describes this as the exercise of authority over a separate smart wallet owned by Binance 14. The observed top-level call and token movement are consistent with that account. The wallet's owner storage, full call trace, and verified source have not been independently cross-checked here, so the detailed authority path remains attributed to the reporting. [Unchained report](https://unchainedcrypto.com/binance-says-user-funds-are-completely-safe-after-3-5-billion-drains-from-its-hot-wallets/)

### 5. 06:01:35 KST, USDT blocked

[0x7baba482077843514d9c72bac0110ba0916b0814288a72917e2c3bb27a9d8659](https://etherscan.io/tx/0x7baba482077843514d9c72bac0110ba0916b0814288a72917e2c3bb27a9d8659), block `26300954`.

Etherscan identifies this as Tether blocking the main recipient's use of USDT. This is an issuer control over that token, not a corresponding freeze of native ETH.

### 6. 06:04:59 KST, USDC blacklist

[0xc954c86f118e8e410e6a3eb9e3b38ff4a95fbdae9d2d58e13166afb7a1f4fc5f](https://etherscan.io/tx/0xc954c86f118e8e410e6a3eb9e3b38ff4a95fbdae9d2d58e13166afb7a1f4fc5f), block `26300971`.

The transaction displays a Blacklist call to USDC Token. This call and the preceding USDT block are observable, but do not independently verify a reported aggregate frozen amount. Later removal of restrictions and the spendability of every asset require separate checks.

### 7. 06:44:11 KST, repeat sweep of Binance 14

[0x55ba4dabc41b468e580751373ad31acdee6f5ba398682df2c93e5a8340870556](https://etherscan.io/tx/0x55ba4dabc41b468e580751373ad31acdee6f5ba398682df2c93e5a8340870556), block `26301167`.

The executor calls Binance 14 again. Transfers to the main recipient include `369.831856995580626695 ETH` and `200,397,771.824195 USDT`. The origin of every preceding deposit has not been traced. The transaction does demonstrate additional asset movement after delegation, relevant to the risk to remaining funds or later inflows.

## Fifty signatures covering an account nonce range

An account nonce is public execution state and a replay-protection counter. ECDSA also uses a secret signing value called a nonce, conventionally `k`. These are different values. Learning the public account nonce does not provide a private key or the ability to sign.

An EIP-7702 authorization has the following format and signing digest. Here, `address` identifies the delegate implementation, not a payment recipient. [Official specification](https://eips.ethereum.org/EIPS/eip-7702#set-code-transaction)

```text
authorization = [chain_id, address, nonce, y_parity, r, s]
digest = keccak256(0x05 || rlp([chain_id, address, nonce]))
```

RLP decoding and re-encoding of the [delegation transaction's Raw Tx Hex](https://etherscan.io/getRawTx?tx=0xad99264d5532ae0dd04b2004eebda05f25657e70dacb764f7ac8d4ccd051298b) reproduces the original bytes. Keccak-256 of the full bytes matches the transaction hash. This establishes the submitted list order independently of the explorer table's display order.

| Raw-data check | Result |
| --- | --- |
| Transaction type and authorization count | Type `0x04`, 50 entries |
| Chain ID | All `1`, not universal `0` |
| Recovered authority | Binance 14 for all 50 |
| Delegate | `0x63e842b054bd624a465454d533c33f573e9c6fae` for all 50 |
| Actual list order | `18914824, 18914823, …, 18914775` |
| Distinct ECDSA `r` values | 50 |
| Separate cryptography/OpenSSL ECDSA verification | All 50 pass |
| Sender recovered from the outer transaction signature | `0x7c8601d4645b93cea45f71e118a729332e6b5ca0` |

The OpenSSL verification received the already computed 32-byte Keccak digest through a Prehashed API. Its hash-algorithm parameter did not cause a second SHA-256 hashing pass. A separate ECDSA verification implementation accepted the same digest and signatures as the public-key recovery calculation. The outer transaction sender and the authorization authority also recover to different accounts.

These checks establish signature mathematics and the corresponding account. They do not establish approval by a legitimate operator, or prove that the attacker possessed the private key itself. The raw transaction does not identify the device that signed, the signing time, the requester, or the approval process.

Each account nonce changes the digest. Changing the nonce number in one valid signature cannot produce this set of 50. The bundle is a **nonce-range spray using valid delegation signatures**. It is not brute force against a private key using random signatures. It is compatible with accommodating a busy hot wallet's changing nonce before inclusion, but the pattern does not prove whether the attacker lacked an exact nonce or when the signatures were generated. [Raw transaction](https://etherscan.io/getRawTx?tx=0xad99264d5532ae0dd04b2004eebda05f25657e70dacb764f7ac8d4ccd051298b), [Blockaid analysis](https://x.com/blockaid_/status/2115924317888495661)

## One application under the displayed prestate

Etherscan's Authorizations table marks only nonce `18914809` as Validity=True; the other 49 display False. All 50 raw signatures pass cryptographic verification. False in this table must therefore not be read as an invalid signature. Cryptographic validity and eligibility under the account's nonce and code conditions are separate checks. [Transaction authorizations](https://etherscan.io/tx/0xad99264d5532ae0dd04b2004eebda05f25657e70dacb764f7ac8d4ccd051298b#authorizationlist)

The specification processes entries in list order. Among its checks, the recovered authority must have empty or already delegated code, and its account nonce must equal the signed nonce. An applied entry writes the delegation indicator `0xef0100 || address` and increments the authority nonce by one. An entry failing its conditions is skipped. [EIP-7702 processing rules](https://eips.ethereum.org/EIPS/eip-7702#behavior)

**Conditioned on the explorer's displayed prestate nonce of `18914809`**, the first 15 raw entries are skipped because their nonces are too high. The 16th entry, `18914809`, applies and advances the account nonce to `18914810`. All remaining 34 entries are `18914808` or lower and are skipped. The earlier `18914810` entry is not revisited. The explorer renders its table in the opposite direction to the raw list, so its visual ordering cannot be used as execution order.

![Conditional processing of 50 descending authorizations: one matches the displayed account nonce, increments it, and the remaining smaller entries are skipped](/images/posts/binance-eip-7702-nonce-spray-incident/nonce-range.svg)

This is a sequential calculation conditioned on the explorer's displayed prestate nonce. It is not an archive-node replay of the actual prestate. One applied authorization in the figure does not mean 50 code executions.

An ascending list could yield a different calculation with consecutive applications. The raw bytes in this incident establish a descending list, so that assumption would be wrong here. No repeated ECDSA `r` appears in these 50 signatures either. This finds no simple identical-`k` reuse pattern within the sample; it does not rule out biased `k`, partial leakage, or an MPC implementation fault.

## Valid authority abuse and the unresolved initial compromise

A signature-verification flaw lets an attacker pass a check without the required authority. The evidence here consists of 50 signatures over the correct digests that recover to the same victim account and pass separate ECDSA verification. It does not support classifying the event as a bypass of EIP-7702 consensus rules or ECDSA verification. This is not a proof that a validly verifying forgery is theoretically impossible. It places the immediate investigative focus on **authority to create or obtain signatures**.

| Possible acquisition path | Evidence needed to distinguish it |
| --- | --- |
| Theft of the private key itself | Key-access and extraction evidence, key-management forensics |
| Abuse of an HSM/MPC signer or signing service | Signing requests, authentication, quorum, and policy-evaluation logs |
| Raw-digest signing or approval-process abuse | Requested digests, requester identity, policy decisions, approval records and screens |
| Stolen pre-signed authorizations, signing inducement, or phishing | Signing times and distribution path, actual user interactions |

Some of these hypotheses could overlap. The on-chain evidence does not select one. Likewise, `chain_id=1` distinguishes this bundle from universal authorizations that could be reused on other chains; it does not explain compromises elsewhere.

A separate class of incident involves replay or bypass of an execution signature in an otherwise legitimate wallet implementation. Here, authorizations point directly to the implementation used in the attack. A bug in a legitimate delegate's `execute` checks is not needed to explain the initial observed path. Blockaid describes the implementation as a sweeper with a hardcoded operator. The sweeper description here rests on that analysis and the observed repeated asset movements, not an independent bytecode or access-control audit. [Blockaid's original analysis](https://x.com/blockaid_/status/2115924317888495661)

## Claude-reconstructed source published on Etherscan

At 14:49 KST on October 30, 2026, the [delegate implementation's Etherscan code page](https://etherscan.io/address/0x63e842b054bd624a465454d533c33f573e9c6fae#code) displayed `Source Code Verified / Exact Match`. It listed compiler `v0.8.28+commit.7893614a`, optimizer 200 runs, and EVM target `cancun`. This is an explorer verification of compiled-source matching, not a security audit or safety endorsement. The same page displayed `No Contract Security Audit Submitted`.

The published `Target.sol` comment explicitly identifies it as AI-reconstructed source rather than the original source code. According to that comment, Claude reconstructed it from deployed runtime bytecode at 00:30 UTC (09:30 KST) on October 30, 2026. It claims that compilation with `solc 0.8.28`, `via-ir`, optimizer 200 runs, and `cancun` produces identical runtime bytecode apart from the trailing metadata hash. Contract and parameter names are described as guesses. The Claude attribution and reconstruction time are source-comment claims, not independently authenticated authorship or an upload timestamp. The explorer's `Exact Match` label and the comment's metadata caveat must be read separately; no independent recompilation or bytecode comparison has been performed here. [Published source](https://etherscan.io/address/0x63e842b054bd624a465454d533c33f573e9c6fae#code)

In this reconstructed source, `onlyAuthorized` restricts the caller to the hardcoded `authorizedCaller`, `0x7C8601d4645b93cea45F71e118A729332e6B5CA0`. That is the same address recovered from the outer type-4 transaction signature above. The restriction appears on `sweep`, `withdrawETH`, `withdrawToken`, and `callExecute`, making the asset-transfer and external-execution structure easier to read. These are observations of the published reconstructed source, not independent verification of individual transaction execution traces. [Implementation code](https://etherscan.io/address/0x63e842b054bd624a465454d533c33f573e9c6fae#code)

This material helps explain the deployed sweeper's behavior. It does not change the finding of 50 valid delegation signatures or establish who obtained them and how. Publication of reconstructed source is not evidence that the attacker's original source was recovered or that Claude authored the attack code.

## Delegation scope and authority over external wallets

An ordinary ERC-20 `approve` grants an allowance for a particular token. EIP-7702 authorization selects code to execute as the account. Its signed fields bind `chain_id`, delegate `address`, and account `nonce`. They do not inherently bind the outer sender, an individual recipient, amount, calldata, or expiration time. A safe delegate and higher-level approval policy must provide granular execution constraints. [Specification and security considerations](https://eips.ethereum.org/EIPS/eip-7702#security-considerations)

The resulting exposure can include ETH and multiple tokens as well as owner or administrator powers the EOA holds in external contracts. The `780,000,000 USDC` movement from Hot Wallet 34 is relevant to that risk, while its precise ownership and call path retain the reporting attribution described above. Counting only Binance 14's own address balances could miss the effects of external authority.

Delegation does not automatically disappear after one call. Even a revert in the execution portion does not roll back delegation already processed. The 06:44:11 repeat sweep shows additional movement under continuing authority. Clearing delegation alone is not a complete recovery if the key or signer remains compromised. [EIP-7702 behavior](https://eips.ethereum.org/EIPS/eip-7702#behavior), [repeat sweep](https://etherscan.io/tx/0x55ba4dabc41b468e580751373ad31acdee6f5ba398682df2c93e5a8340870556)

These are risks independent of signature forgery. The specification warns about interfaces that expose signing of arbitrary application-proposed authorizations and calls for wallet-side code auditing. Failure to establish a protocol-verification flaw does not show that existing withdrawal controls adequately covered delegation's broader authority and persistence. [Wallet and application interaction guidance](https://eips.ethereum.org/EIPS/eip-7702#interaction-with-applications-and-wallets)

## The 13:19 to 13:30 KST balance observation and the RAD swap

The following values were observed on the [main recipient's address and token-holdings pages](https://etherscan.io/address/0x5227f603C1eE34CE3C06eFe6477003BDfCCB2f8c) at **13:19 to 13:30 KST on October 30, 2026**. The pages were not pinned to one common block. These are not the latest balances at publication.

| Asset | Explorer-displayed balance |
| --- | --- |
| ETH | `17,263.271817626578868333` |
| USDT | `1,175,464,712.87536` |
| USDC | `823,000,000` |
| XAUt | `12,574.046797` |
| USD1 | `27,824,039.9368965` |
| PAXG | `1,906.66772869` |

Restricted tokens can remain visible as balances. The explorer's roughly $2.1 billion token valuation is not a measure of spendable or recoverable funds: prices, liquidity, and restrictions matter. Although the earlier blacklist transactions were identified, this observation did not revalidate later unblocking or every asset's spendability.

A successful swap at **13:06:47 KST** that day, block `26303071`, provides a concrete subsequent action.

[0xbe98f5bdfce307e92c1e0bacde80995dfd817b77fc4303224f0283f3aacd1101](https://etherscan.io/tx/0xbe98f5bdfce307e92c1e0bacde80995dfd817b77fc4303224f0283f3aacd1101)

1. The recipient sends `700,567.745144517222388354 RAD` to the Uniswap V2 RAD/USDC pool.
2. That pool sends `122,529.838325 USDC` to the USDC/WETH pool.
3. Via WETH and Router 2, `39.178398816052027387 ETH` returns to the same recipient.

This converts RAD to ETH through pools. The intermediate USDC moves between pools, so it does not establish that existing USDC held by the blacklisted attacker address was spent or that a blacklist was bypassed. The latest 25 internal-transfer entries visible at observation also included several ETH receipts from Uniswap V2/V3 routers. They are consistent with token liquidation and ETH collection, but do not prove completed laundering or cash-out.

A different transaction at **13:10:47 KST** is a small inbound transfer: an external account sends 69 wei and text.

[0x98e03bf51e20c6b1a02f6759b3790fdbbc6e55c5af15f72f86ae78fb7dead479](https://etherscan.io/tx/0x98e03bf51e20c6b1a02f6759b3790fdbbc6e55c5af15f72f86ae78fb7dead479)

Anyone can send such messages or dust. Mentions of Hyperliquid and Monero in that text are not evidence of flows to either service.

Large ETH outflows to subsequent addresses, bridges, or exchanges have not been reconstructed across the full history. The latest 25 entries cannot substitute for it. Subtracting the observed balance from an initial theft quantity would not establish external outflows either. Additional deposits, swaps, gas, wrapping, and movements across other addresses and chains require reconciliation. Final arrival at a mixer or a named service is outside the verified scope.

## Signing boundaries for custody operators

The operational task is to control both withdrawal approval and signatures that change an account's execution code. Another account can submit the outer transaction, so **filtering outbound type-4 transactions at the sending service is insufficient**. The following defenses follow from the observed path and the authorization's scope.

- **Identify authorizations at the signer.** If EIP-7702 is unused, reject delegation signing in the `0x05` domain. Control request formats and permissions so raw-digest signing cannot bypass transaction-policy checks.
- **Approve delegation as a high-authority change.** Where needed, enforce chain and implementation allowlists, inspect the actual address and bytecode, and simulate behavior. For proxies, inspect upgrade authority too. Recipient, amount, calldata, and execution replay protection belong in safe delegate policies.
- **Trace the creation of the 50 signatures.** Correlate each nonce-specific digest request with its origin, generation time, authentication, and approvals. An HSM or MPC system that prevents key extraction still requires investigation for signing-authority abuse.
- **Monitor code changes and external powers together.** Detect delegation changes and halt automatic deposits or refills into compromised accounts. Identify external wallets where the EOA is an owner or administrator and separate or replace that authority.
- **Extend recovery beyond clearing delegation.** Investigate continuing key or signer compromise and plan migration of assets and external authority to safe accounts. An attacker who can still obtain valid signatures can install delegation again.

The established path is account authority takeover through EIP-7702 authorization and repeated sweeping. The initial signature-acquisition path, archive prestate nonce and code, runtime verification of the access controls read in the reconstructed source, exact external-wallet authority path, and full outflow reconciliation remain open. Keeping those questions distinct helps identify whether further evidence is needed at protocol verification or the custody signing-policy boundary.

## Further reading

- [EIP-7702 security considerations](https://eips.ethereum.org/EIPS/eip-7702#security-considerations): Execution signatures and replay protection that delegates must implement.
- [EIP-7702 backwards compatibility](https://eips.ethereum.org/EIPS/eip-7702#backwards-compatibility): The changed assumption that an external call can reduce an EOA's balance.

## References

- [EIP-7702: Set Code for EOAs](https://eips.ethereum.org/EIPS/eip-7702): Official Ethereum specification, accessed October 30, 2026.
- [Raw delegation transaction](https://etherscan.io/getRawTx?tx=0xad99264d5532ae0dd04b2004eebda05f25657e70dacb764f7ac8d4ccd051298b): Primary bytes for the hash, list order, and signature checks, accessed October 30, 2026. The seven representative and subsequent transactions are linked by full hash in their respective sections.
- [Reconstructed delegate source](https://etherscan.io/address/0x63e842b054bd624a465454d533c33f573e9c6fae#code): Etherscan verification display and published `Target.sol`, observed at 14:49 KST on October 30, 2026. Claude attribution, reconstruction time, and the metadata-hash exception are source-comment claims.
- [Blockaid incident analysis](https://x.com/blockaid_/status/2115924317888495661): Public source for the nonce-range spray and sweeper implementation analysis, accessed October 30, 2026.
- [Binance Says User Funds Are Completely Safe After $3.5 Billion Drains From Its Hot Wallets](https://unchainedcrypto.com/binance-says-user-funds-are-completely-safe-after-3-5-billion-drains-from-its-hot-wallets/): Unchained's reporting context and account of the external-wallet authority path, accessed October 30, 2026.
- [Main recipient account](https://etherscan.io/address/0x5227f603C1eE34CE3C06eFe6477003BDfCCB2f8c): Explorer observations at 13:19 to 13:30 KST on October 30, 2026, not a block-pinned balance snapshot.
