---
title: "Know Your Agent (KYA): AI Agent Identity, the Standards Race, and What Is Actually On-Chain"
meta_title: ""
description: "Separate agent identity, authentication, authorization and reputation, then examine ERC-8004's standards status and mainnet activity alongside the scope and limits of Visa TAP, Trulioo and Sumsub."
date: 2026-08-27T10:00:00+09:00
lastmod: 2026-10-15T15:36:42Z
image: "/images/posts/know-your-agent-kya-ai-agent-identity-onchain/kya-identity-editorial-20261016.webp"
categories: ["Blockchain"]
tags: ["ai-agent", "kya", "identity", "erc-8004", "reputation", "compliance"]
author: "whackur"
translationKey: "know-your-agent-kya-ai-agent-identity-onchain"
draft: false
---

An identity credential or an on-chain registration number is insufficient grounds to let an AI agent spend money or access data. **Identifying the agent, authenticating the requester, checking its authority for this action, and deciding how much to trust past feedback** are separate checks. Know Your Agent (KYA) groups these concerns under one name. ERC-8004 supplies identifiers and public trust signals; Visa TAP and identity-verification vendors offer other ways to check requests, organizations or people. The service receiving the request still decides whether to grant access. The [ERC-8004 specification](https://eips.ethereum.org/EIPS/eip-8004) and [Trulioo's product description](https://www.trulioo.com/products/kya-verification) both limit what registration or verification establishes.

*Standards status and product descriptions checked on October 16, 2026 KST. Historical measurements carry their own observation periods.*

## Identity, authentication, authorization and reputation

Consider a shopping agent that moves from searching for products to calling a purchase API. Looking up its registration number and approving the purchase are different operations.

| Check | What it establishes | Evidence needed for a purchase request |
| --- | --- | --- |
| Identity | Which agent is being referenced | Registry address and agent ID, operating organization information |
| Authentication | Whether the requester controls the key or credential associated with that identity | Signature verification, a connection to a trusted issuer or key, request validity period |
| Authorization | Whether this principal may perform this action | The user's permitted merchant, products, amount and duration, plus conditions on further delegation |
| Reputation | How useful past assessments are for this decision | Reviewer, task being assessed, units, supporting evidence and revocation status |

Suppose a user permits purchases at one merchant for 30 minutes with a total limit of KRW 100,000. A valid agent signature does not authorize a KRW 120,000 order. These amounts and the duration are illustrative policy choices. Search permission and purchase permission should be separate, and the purchase API or wallet must enforce the conditions immediately before execution. A favorable reputation does not override the budget.

Checking the operator is another task. Knowing which address controls a key does not identify the person or company behind it. Recording the model and code's provenance also differs from authenticating a request. [NIST warns that sharing user credentials with agents or leaving broad permissions in place](https://www.nist.gov/blogs/cybersecurity-insights/back-future-why-agentic-ai-needs-strong-identity-foundation) weakens accountability and access control. These distinctions matter inside centralized platforms too.

## The information ERC-8004 connects

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) defines Identity, Reputation and Validation registries. Identity identifies an agent through an ERC-721 token. Reputation records feedback. Validation connects requests for verification with a validator's responses. Payments themselves are outside the specification's scope.

An identity lookup requires more than an `agentId`. The same number can exist on different chains and registries, so the identifier combines `agentRegistry`, which identifies the chain and registry, with `agentId`. The registration file referenced by the token's `agentURI` contains its name, description, service addresses such as an Agent2Agent (A2A) AgentCard or Model Context Protocol (MCP) endpoint, and supported trust mechanisms. These declarations help a counterparty find an agent. They do not establish that its advertised capabilities work or are safe.

The connection between the registration file and a service address also needs checking. The specification includes optional domain verification: publish `/.well-known/agent-registration.json` on the service domain and match its registration information. Listing an arbitrary domain differs from proving control of it. An owner or approved operator can also change `agentURI`, so consequential transactions should retain the file and ownership information used at the time of the decision.

The `agentWallet` is a **payment-receiving address**. Registration initially sets it to the owner's address. Changing it requires proof of control of the new wallet through an EIP-712 signature or ERC-1271 validation for a smart contract wallet. Transferring the token clears the binding. This procedure binds a receiving address; it does not grant permission to spend a user's assets or establish the operator's legal identity. The [reference implementation](https://github.com/erc-8004/erc-8004-contracts) describes the same initialization, update and transfer rules.

Validation provides an interface for committing a request hash associated with evidence such as task inputs and outputs, then receiving a response from the designated validator. It can connect to re-execution, zero-knowledge machine learning (zkML) proofs or trusted execution environment (TEE) verification. The registry does not automatically perform all those checks. A counterparty still needs to establish what was verified and which validator it trusts.

## Standards status and mainnet activity are different evidence

The official documents' process status and the implementation repository's deployment information answer different questions.

| Document | Official process status | Scope | What status alone cannot establish |
| --- | --- | --- | --- |
| [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) | Draft | Agent identity, reputation and validation registries | Whether a deployed version matches, usage or service quality |
| [ERC-8126](https://eips.ethereum.org/EIPS/eip-8126) | Final | AI Agent Verification | A verification provider's deployment or assessment quality |
| [ERC-8196](https://eips.ethereum.org/EIPS/eip-8196) | Final | Wallet execution and delegation with proof of policy compliance | Implementation, operation or adoption of a particular wallet |

Contracts can be deployed and used while a proposal is Draft. Final is a [document status in the EIP process](https://eips.ethereum.org/EIPS/eip-1), rather than network activation or a security certification. These documents also do not establish a mandatory single stack that every KYA service must implement together.

The ERC-8004 [reference implementation repository](https://github.com/erc-8004/erc-8004-contracts) publishes Identity and Reputation addresses for Ethereum and Base mainnet. At Ethereum's Identity address, `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`, a **successful registration transaction in block 26,198,758 at 15:17:23 UTC on October 15, 2026** emitted `Registered` with `agentId = 54155`. [That transaction](https://eth.blockscout.com/tx/0x97c640ad052770b66f9744c1318555ccd894e2e0cea215c41dbd86754aa34308) is concrete evidence of an actual registration call beyond a specification document. The [Reputation address's logs](https://eth.blockscout.com/address/0x8004BAa17C55a88189AE136b182e5fdA19dE9b63?tab=logs) also contain `NewFeedback` events.

These events cannot establish the number of paying customers or autonomously working agents. An ID is an identifier, and registration differs from service execution. The reference repository also warns that the Validation Registry portion remains under active update and discussion with the TEE community. A deployment list for Identity and Reputation does not establish equal operational maturity for all three registries.

An empirical study illustrates the difference between registration and service availability. Xiong and colleagues' [ERC-8004 study, version 2](https://arxiv.org/html/2606.26028v2), observes Ethereum, BNB Smart Chain (BSC) and Base from deployment through **May 13, 2026**. Under the study's operational classification of a retrievable registration file with the required `type` value and at least one declared service, the shares of registrations were approximately **3%, 4% and 15%**, respectively. These results apply to that period and classification. A service declaration does not establish task performance, and those percentages are not October uptime measurements.

## Read the reviewer and units behind a reputation score

The [Reputation specification's](https://eips.ethereum.org/EIPS/eip-8004#reputation-registry) `value` and `valueDecimals` encode a general-purpose number. For example, `9977` with `2` represents `99.77`, but tags and evidence are needed to establish whether that means uptime or a rating. Averaging response times, star ratings and cumulative revenues as though they were one score produces a meaningless result.

Agent owners and approved operators cannot submit feedback on their own agent. That restriction does not prevent one actor from creating multiple addresses. The specification explicitly recognizes Sybil attacks, and `getSummary` requires a nonempty `clientAddresses` list. The party aggregating feedback must choose which reviewers it trusts.

Evidence files need equally careful interpretation. Both `feedbackURI` and `feedbackHash` are optional. In particular, **`feedbackHash = 0` does not by itself establish an absence of evidence.** A content-addressed URI such as IPFS can omit the separate hash. Conversely, a hash does not make an assessment true. It provides a way to check file integrity.

A practical decision process selects trusted reviewers, checks tags, units and revocation status, then retrieves supporting files when necessary to compare their integrity and task content. Payment evidence establishes something different from result quality. The specification's optional `proofOfPayment` is not a quality guarantee either.

## What Visa, Trulioo and Sumsub verify

These approaches are not complete substitutes competing over identical functions. An agent can have an on-chain registration, sign its HTTP requests and obtain separate organization verification.

| Approach | Mechanism and trusted party | Conditions that remain |
| --- | --- | --- |
| ERC-8004 | On-chain ownership and public feedback or validation records | Request authentication, operator due diligence, reviewer selection and execution authority are separate |
| Visa Trusted Agent Protocol (TAP) | Public keys and HTTP message signatures verify agent requests and their action context | Key trust, request validity and the merchant's policy decision |
| Trulioo KYA | Developer organization checks and agent information connected in a signed DAP | Alpha product availability, credential status and access policy |
| Sumsub AI Agent Verification | Automation detection, risk assessment and binding to a verified human | Additional checks according to risk and human confirmation when needed |

[Visa's official repository](https://github.com/visa/trusted-agent-protocol) provides examples of RFC 9421 HTTP message signatures, a key registry and merchant verification. A merchant reconstructs the signature base from the request and verifies it with the public key. Time and session information, domain and action context also need checking. The mechanism verifies requests without requiring an ERC-8004 registration. The public sample implementation does not establish deployment across the entire merchant network.

[Trulioo's current product page](https://www.trulioo.com/products/kya-verification) calls its DAP a **Digital Agent Profile**. It combines developer organization know-your-business (KYB), anti-money-laundering (AML) and domain-control checks with agent information such as purpose and authority, and describes signed, time-bound credentials with a defined scope and status checks. The page labels KYA Alpha and says registration is available to organizations whose domains have been enabled. Trulioo explicitly states that a credential does not guarantee future safe behavior and that the relying organization makes access decisions.

[Sumsub's January 29, 2026 announcement](https://sumsub.com/newsroom/sumsubs-ai-agent-verification-introduces-agent-to-human-binding-to-establish-human-accountability-in-ai/) describes binding agent activity to a verified human. It first detects automation and assesses risk, then can require additional checks such as targeted liveness verification to confirm that a real person is present in higher-risk situations. This should not be generalized into a face check for every action. Binding to a person supplies information useful for accountability; the binding alone does not determine legal liability for a particular act.

## Controls that remain at execution time

A useful starting point for KYA is to define permitted actions before choosing a registration mechanism. Searching public documents, reading personal data and making a payment have different consequences when something goes wrong. In the purchase example, the API or wallet should enforce these conditions:

1. Check registration or organization credentials and the request signature. Reject expired or revoked keys or credentials.
2. Compare the delegating user, permitted merchant, total amount and validity period with the purchase request. Further delegation must not expand the original authority.
3. Handle duplicate requests and budget consumption at execution time. Reputation or an earlier approval must not make an already-spent budget available again.
4. Record the policy, credentials and task version used for the decision, plus the execution result. When the model, prompt or tools change, reassess what the earlier verification actually covers.

This sequence is an example of separating identity checks from action authorization, rather than a mandatory procedure in one standard. [NIST's current project hub](https://pages.nist.gov/nccoe-ai-identity/) likewise describes practical guidance for applying existing identity and authorization standards to agents, with an SP 1800 series practice guide as an intended outcome. It should not be read as a legally mandated KYA certification scheme. NIST also [warns](https://www.nist.gov/blogs/cybersecurity-insights/back-future-why-agentic-ai-needs-strong-identity-foundation) that excessive human approval requests can weaken controls through consent fatigue.

Publishing legal names or detailed task records in a public registry also requires care. Information that connects identifiers and public addresses can make long-term tracking easier. A suitable design separates necessary proof from public disclosure and restricts access to sensitive material.

On-chain records let different organizations consult the same identifiers and history. Selecting trustworthy reviewers, authenticating the current request and enforcing the delegated scope remain responsibilities of the service operator.

## Further reading

- [ERC-8004 reference implementation](https://github.com/erc-8004/erc-8004-contracts): Deployment addresses, registration and reputation queries, and the Validation update warning.
- [Visa TAP sample implementation](https://github.com/visa/trusted-agent-protocol): Components for request signatures and merchant verification.
- [NIST agent identity and authorization resource hub](https://pages.nist.gov/nccoe-ai-identity/): Enterprise identity, delegation and access-control work.

## References

The following sources were checked on October 16, 2026 KST.

- [ERC-8004: Trustless Agents](https://eips.ethereum.org/EIPS/eip-8004), [official raw source](https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-8004.md): Identity, reputation, validation and security limits.
- [ERC-8126: AI Agent Verification](https://eips.ethereum.org/EIPS/eip-8126), [ERC-8196: AI Agent Authenticated Wallet](https://eips.ethereum.org/EIPS/eip-8196), [EIP-1](https://eips.ethereum.org/EIPS/eip-1): Interfaces and standards-process status.
- [ERC-8004 contracts](https://github.com/erc-8004/erc-8004-contracts): Deployment list and reference implementation.
- [Ethereum registration transaction](https://eth.blockscout.com/tx/0x97c640ad052770b66f9744c1318555ccd894e2e0cea215c41dbd86754aa34308), [Reputation logs](https://eth.blockscout.com/address/0x8004BAa17C55a88189AE136b182e5fdA19dE9b63?tab=logs): Examples of actual registry activity.
- [Can Trustless Agents Be Trusted? v2](https://arxiv.org/html/2606.26028v2): Xiong et al., revised July 8, 2026. Three-chain observations through May 13, especially registration-file classification and study limitations.
- [Visa Trusted Agent Protocol](https://github.com/visa/trusted-agent-protocol): Official description and sample implementation.
- [Trulioo KYA](https://www.trulioo.com/products/kya-verification): Digital Agent Profile, Alpha availability and verification scope.
- [Sumsub AI Agent Verification](https://sumsub.com/newsroom/sumsubs-ai-agent-verification-introduces-agent-to-human-binding-to-establish-human-accountability-in-ai/): Risk-based human checks and agent binding.
- [NIST project hub](https://pages.nist.gov/nccoe-ai-identity/), [Back to the Future: Why Agentic AI Needs a Strong Identity Foundation](https://www.nist.gov/blogs/cybersecurity-insights/back-future-why-agentic-ai-needs-strong-identity-foundation): Project goals and identity/access-management failure patterns.
