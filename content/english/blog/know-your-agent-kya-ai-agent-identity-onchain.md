---
title: "Know Your Agent (KYA): AI Agent Identity, the Standards Race, and What Is Actually On-Chain"
meta_title: ""
description: "KYA applies the KYC due-diligence frame to AI agents. This post covers the concept, the standards race between ERC-8004, Visa TAP, Trulioo and Sumsub, regulatory signals from NIST, the EU and Singapore, and on-chain reality including vouch spam in the reputation registry."
date: 2026-08-27T10:00:00+09:00
lastmod: 2026-08-27T10:00:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["ai-agent", "kya", "identity", "erc-8004", "reputation", "compliance"]
author: "whackur"
translationKey: "know-your-agent-kya-ai-agent-identity-onchain"
draft: true
---

When you open a bank account you show an ID. When you sign up for an exchange you take a selfie. That procedure is KYC (Know Your Customer), and since the FATF was founded in 1989 it has been the standard way to keep illicit money out at the entry point of the financial system. Now the entity signing contracts, sending payments and swapping tokens on a DEX is increasingly not a person but an AI agent, and the same question comes back in a new form. The agent that just sent a payment request to my API: who is it, who built it, and what was it actually authorized to do? The trust layer that answers that question is being called KYA (Know Your Agent).

This blog has already covered the [ERC-8004, 8126 and 8196 trust stack](/en/blog/ai-agent-wallet-trust-stack-erc-8004-8126-8196/) and the [practical side of querying the ERC-8004 reputation registry](/en/blog/erc8004-agent-reputation-registry-lookup/). This post does not re-explain those specs. It starts from the KYC/AML due-diligence frame, places on-chain registries as one implementation of that due diligence, and pulls together the standards race, the regulatory signals, and what the on-chain data actually shows.

## What KYA is

KYA is KYC for AI agents: a trust layer that verifies "who this agent is" before the agent autonomously executes a contract, a payment or a trade. The term started getting attention in 2025. The [Agentica wiki](https://agentica.wiki/articles/know-your-agent) (updated 2026-03-18) breaks it into six dimensions.

| Dimension | What it checks |
|-----------|----------------|
| Identity | Is this agent uniquely identifiable |
| Ownership binding | Which person or organization is accountable for it |
| Authorization scope | What was it delegated to do |
| Provenance | What model and code produced it, and has it been tampered with |
| Runtime compliance | Does it stay within policy while running |
| Auditability | Can its actions be traced and attributed afterwards |

Put next to KYC, the difference shows. KYC checks attributes that rarely change (an ID document, an address) once. Three of the six KYA dimensions (authorization scope, runtime compliance, auditability) are things you have to keep checking during execution, not at registration. An agent's behavior can change with a single model update, so a check it passed once tells you little about next week. Most of the criticism later in this post grows from that root.

KYA is not needed everywhere. [Tiger Research's 2026 report](https://reports.tiger-research.com/p/2026-know-your-agent-eng) argues that inside centralized platforms (Google, OpenAI, Coinbase) the KYC already attached to the platform account is enough. KYA matters outside the platform: when an independently deployed autonomous agent touches a DEX, an agent-to-agent (A2A) payment, or a commerce site, the counterparty has no platform vouching for it. The same report predicts that, much as KYC became a precondition for entering financial markets, having KYA infrastructure will decide who gets into the next round. That is a forecast. As the regulation section below shows, no jurisdiction requires it yet.

## The standards race

The name is one, but "where trust is anchored" differs by camp. Four approaches stand out.

![Comparison of four KYA approaches, ERC-8004 on-chain registries, Visa TAP signed HTTP requests, Trulioo certificate-authority model and Sumsub verified-human binding, showing trust anchor, status and key numbers](/images/posts/know-your-agent-kya-ai-agent-identity-onchain/kya-four-approaches.svg)

*Where each approach anchors trust: on-chain registries, signed HTTP requests, a certificate authority, or a verified human. Numbers are from the sources cited in the text.*

### On-chain registries: ERC-8004 and the layers above it

[ERC-8004 "Trustless Agents"](https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-8004.md) registers agent identity as an ERC-721 token and accumulates reputation signals and independent validation results in two further registries. The registration file (the JSON that `agentURI` points to) carries service endpoints such as A2A, MCP, ENS and DID, plus `x402Support` and `supportedTrust` fields. The `agentWallet` (the wallet address the agent actually moves assets with) can only be bound through an EIP-712 or ERC-1271 signature and is automatically unbound when the NFT is transferred. Trust models are pluggable: reputation, crypto-economic re-execution with staking, zkML, or TEE attestation (an integrity proof issued by a trusted execution environment).

The precise status is this. ERC-8004 is at Draft stage in the standards process, but it has been live on Ethereum mainnet since 2026-01-29, is deployed as a singleton on more than 30 chains, and held roughly 90,000 registrations as of June 2026. "The spec can still change" and "the deployment is live and used" are separate facts, and both are true.

Mapped onto the six KYA dimensions, ERC-8004 covers identity and, partially, ownership binding. Above it, [ERC-8126 "AI Agent Verification"](https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-8126.md) (Final, created 2026-01-15) handles provenance with five verification types and a 0 to 100 risk score, and [ERC-8196 "AI Agent Authenticated Wallet"](https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-8196.md) (Final, created 2026-03-14) fills runtime compliance and auditability with policy-bound execution and an immutable audit trail. The interfaces and verification types are written up in the [earlier post](/en/blog/ai-agent-wallet-trust-stack-erc-8004-8126-8196/).

One thing worth pointing out: this stack has no human identity binding. There is an NFT owner address, but the spec does not ask who is behind it. [Concordium](https://www.concordium.com/article/erc-8004-explained-what-it-solves-and-the-gap-it-leaves) calls this the accountability gap and proposes CIS-8004 as a counterpart standard to fill it. The agent communication protocols A2A and MCP are not KYA themselves; they complement ERC-8004. Communication goes over A2A/MCP, discovery and trust go through ERC-8004.

### Payment networks: Visa TAP and Mastercard Agent Pay

[Visa Trusted Agent Protocol (TAP)](https://developer.visa.com/use-cases/trusted-agent-protocol) was [announced](https://investor.visa.com/news/news-details/2025/Visa-Introduces-Trusted-Agent-Protocol-An-Ecosystem-Led-Framework-for-AI-Commerce/default.aspx) by Visa and Cloudflare on 2025-10-14. It uses no blockchain at all. Agent identity is signed into request headers using HTTP message signatures based on Web Bot Auth, and the merchant side verifies them. There are three signatures: the agent's own legitimacy, the delegator (the person who set the agent to work), and the payment method. Twelve launch partners were named, including Adyen, Ant International and Checkout.com. The backdrop is a 4,700% surge in AI traffic to US retail sites. Merchants can neither block all bots nor accept all of them, so they need a signature that separates the good ones.

Mastercard announced Agent Pay in April 2025. It expresses verifiable intent using SD-JWT, with three layers and eight constraint types, and expanded into Agent Suite in January 2026. Deployments have been reported at Santander (EU) and DBS/UOB (Singapore).

Both payment-network approaches lay KYA's ownership binding and authorization scope on top of the merchant and issuer relationships the card networks already have. The root of trust is the network operator, not a chain.

### Identity vendors: Trulioo's certificate-authority model and Sumsub

Trulioo borrowed the SSL certificate authority (CA) model outright. A DPA (Digital Personhood Authority) issues a DAP (Digital Agent Passport), and the counterparty checks that passport the way a browser checks a TLS certificate. In a survey Trulioo ran with PYMNTS Intelligence across 350 risk and compliance leaders, about 90% of firms named bot management a top challenge, and the estimated annual loss from outdated identity controls came to roughly $100B. Read that with the usual caution for vendor co-sponsored research.

Sumsub launched AI Agent Verification in January 2026. Its approach is the closest to KYC as practiced: bind the agent to a verified human identity and require a liveness check (confirming a real person is present right now) on that human. It fits any setting where someone must be able to name, immediately, the person legally accountable for an agent's actions. Prove has also shipped a Verified Agent product built on a shared trust registry.

### Metadata standards and indexers

[AgentFacts](https://agentfacts.org/kya/) (Jared Grogan, [arXiv 2506.13794](https://arxiv.org/abs/2506.13794)) is a ten-category metadata standard tied to no chain or vendor. Under four pillars (Identity, Capability, Compliance, Provenance) it includes DID, EU AI Act classification and NIST AI RMF alignment fields, aiming to be the common description layer that can sit on top of whichever camp wins.

[knowyouragent.network](https://knowyouragent.network/) works from the other direction, reading what is already on-chain. It indexes more than 150,000 agents across 12 chains and combines wallet tenure (how long an address has been active), ownership history and ERC-8004 fraud detection into an RNWY score. If a registry is a bulletin board, indexers like this are where the actual due diligence happens.

## On-chain reality

Set aside the spec documents and vendor announcements and look at what has actually accumulated in the registries, and KYA's current position comes into focus. [Blokz's on-chain audit](https://www.blokz.dev/articles/erc-8004-agent-registries-onchain) (as of 2026-06-12) is a good starting point.

Registration volume is about 55,210 on Base and about 34,437 on Ethereum mainnet, roughly 89,600 combined, 19 weeks after the mainnet launch. Holders number 16,652 on Base and 8,573 on Ethereum, so each holder owns 3.3 to 4 agents on average. That is not individuals registering one agent each; it is platforms mass-minting. Cost is no barrier. Registering on Base through an ERC-4337 bundle costs 273,820 gas, a total fee of 0.0000017 ETH, about $0.0028 at ETH $1,667. As a concrete example, agentId 55,210 "Bob — Crypto Trading Agent" (0xWork platform) lists a $9 USDC service price in its registration-v1 file.

The problem is the reputation registry. Blokz caught a single agent (id 25,975) receiving 10 feedback events in 48 seconds, all with value=1, tagged miner-vouch/botcoin, and all with `feedbackHash` set to 0x0. A zero feedbackHash means no evidence backing the feedback was committed anywhere. Individual "client" addresses were also found leaving vouches (endorsement feedback) thousands of times. This vouch spam is possible because the spec delegates Sybil resistance (defense against one actor creating many identities to inflate a signal) to off-chain aggregation rather than enforcing it on-chain. The contract records anyone's feedback.

Blokz's conclusion is to consume the reputation registry like an event bus. Keep an allowlist of client addresses you trust, take only feedback with a non-zero feedbackHash, check the evidence at feedbackURI, and only then aggregate. In the audit's own words, having the word reputation in the contract name does not mean the trust problem is solved. How to turn that prescription into actual query code is covered in the [reputation registry post](/en/blog/erc8004-agent-reputation-registry-lookup/).

Academia is looking at the same data. [arXiv 2606.26028](https://arxiv.org/abs/2606.26028) is an empirical study that crawled Identity and Reputation events, off-chain registration files and x402 payments across Ethereum, BNB/BSC and Base up to 2026-05-13. Being able to argue about on-chain KYA from measurement data rather than vendor whitepapers is this year's change.

## Regulatory and policy signals

No jurisdiction requires KYA by law. Three signals point at the direction, though.

NIST NCCoE in the US published the concept paper ["Accelerating the Adoption of Software and AI Agent Identity and Authorization"](https://csrc.nist.gov/pubs/other/2026/02/05/accelerating-the-adoption-of-software-and-ai-agent/ipd) (Initial Public Draft) on 2026-02-05, with comments open until 2026-04-02. It is part of the AI Agent Standards Initiative, whose preceding RFI drew more than 930 submissions. The paper explicitly addresses agent identity, delegation-chain authorization (the chain of a person delegating to an agent and that agent delegating to another), and audit requirements. Those topics overlap heavily with KYA's six dimensions.

The EU AI Act requires operator identity to be recorded in the activity logs of high-risk AI systems. It does not call this agent identity verification, but to put the operator in the log you need something that binds the agent to the operator. Singapore has published the first national-level agentic AI governance framework.

According to [Agentica](https://agentica.wiki/articles/know-your-agent), as of March 2026 no jurisdiction explicitly requires KYA, and organizations are adopting it ahead of regulation. Reading the vendor activity above as regulatory response overstates it. Right now what pulls KYA forward is bot traffic on commerce sites and fraud cost on payment networks, not regulators.

## Criticisms and open problems

Most criticism of KYA comes down to asking where the KYC analogy breaks.

**Sybil resistance.** The biggest weakness of the on-chain camp. With registration at about $0.003 and reputation feedback open to anyone, the vouch spam above is not a bug; it is the natural result of the design. The spec leaves filtering to the application, and who does that filtering by what criteria becomes an off-chain trust problem again. Visa TAP and Sumsub do not have this problem, but in exchange the network operator or vendor becomes the single gatekeeper.

**Privacy.** The stronger the ownership binding, the more every transaction an agent makes traces back to a specific person. Sumsub's approach accepts that head-on. ERC-8126 compromises with PDV (Private Data Verification), hiding verification details behind a ZKP and letting only the agent wallet holder read results. Neither has cleanly found the point where accountability is possible but everyday transactions are not tracked.

**Fragmentation.** Four camps use four different trust anchors, and so far there is no sign of convergence on one. An agent paying by card may need a TAP signature, an agent using a DEX may need an ERC-8004 registration, and an agent touching regulated finance may need Sumsub-style human binding. Metadata layers like AgentFacts offer to be the glue, but adoption is a separate question.

**Dynamic agent behavior.** KYC rests on the assumption that a person is the same person tomorrow. Agents change behavior through model swaps, prompt edits and added tools. Verification at registration says nothing about safety at execution, which is why a separate runtime policy layer like ERC-8196 became necessary.

**No mandate.** With no jurisdiction requiring KYA, adoption is voluntary and therefore uneven. If only careful operators register and malicious ones do not, the registry becomes a list of good agents rather than a filter against bad ones. KYC worked not because it was voluntary but because it was required.

## Community reaction

I could not find an active community debate about KYA as such. On Hacker News, Esther Dyson's Substack piece ["Know Your .agent?"](https://estherdyson.substack.com/p/know-your-agent) was posted on 2026-05-06 and drew zero comments. An x402 API Show HN on 2026-02-23 shows a server registered on Base as ERC-8004 Agent #18763, which is a signal that someone is actually using it, not a KYA debate. That is why this post uses the Blokz audit and the arXiv empirical study, rather than community reviews, as the basis for its criticism.

## Further reading

- [AI Agent Trust Stack: ERC-8004, ERC-8126, ERC-8196](/en/blog/ai-agent-wallet-trust-stack-erc-8004-8126-8196/): the interfaces and verification types this post deliberately did not re-explain (this blog)
- [ERC-8004 Agent Reputation: On-Chain Registration and Lookup](/en/blog/erc8004-agent-reputation-registry-lookup/): filtering the reputation registry with allowlists and evidence checks in practice (this blog)
- [Tiger Research: 2026 Know Your Agent](https://reports.tiger-research.com/p/2026-know-your-agent-eng): a market forecast that reads KYA against the history of KYC
- [AgentFacts KYA page](https://agentfacts.org/kya/): chain- and vendor-neutral metadata standard
- [NIST NCCoE concept paper](https://csrc.nist.gov/pubs/other/2026/02/05/accelerating-the-adoption-of-software-and-ai-agent/ipd): the US standards body's draft on agent identity, delegation and audit

## Summary

KYA is not a new technology. It is an attempt to move an old regulatory practice onto a new kind of actor, and in the process the KYC analogy holds only halfway. Identity and ownership binding transfer over. Authorization scope, runtime compliance and auditability are continuous-check problems that a single registration does not settle.

The on-chain camp leads on deployment speed. ERC-8004 gathered roughly 90,000 registrations across more than 30 chains. But a large share of that number is platform mass-minting, and the reputation registry is filling with evidence-free vouches, so "it is in the registry" and "it can be trusted" are still different statements. Payment networks and identity vendors route around the Sybil problem by anchoring on relationships they already hold (merchants, KYC'd customers), at the price of depending on a single gatekeeper.

My own read: if you run agents or receive agent traffic today, the job is not to pick a camp. It is to treat any registry as an event bus and filter it by your own criteria, and to start keeping records that bind each agent to an accountable party now. If regulation arrives, you will need those records. If it does not, you will need them the day something goes wrong.

## References

- [ERC-8004: Trustless Agents](https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-8004.md): ethereum/ERCs, Draft (standards process), mainnet live 2026-01-29, accessed 2026-08-27
- [ERC-8126: AI Agent Verification](https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-8126.md): ethereum/ERCs, Final, accessed 2026-08-27
- [ERC-8196: AI Agent Authenticated Wallet](https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-8196.md): ethereum/ERCs, Final, accessed 2026-08-27
- [2026 Know Your Agent](https://reports.tiger-research.com/p/2026-know-your-agent-eng): Tiger Research, accessed 2026-08-27
- [ERC-8004 Agent Registries On-chain](https://www.blokz.dev/articles/erc-8004-agent-registries-onchain): Blokz, audit as of 2026-06-12, accessed 2026-08-27
- [Know Your Agent](https://agentica.wiki/articles/know-your-agent): Agentica wiki, updated 2026-03-18, accessed 2026-08-27
- [AgentFacts KYA](https://agentfacts.org/kya/) and [arXiv 2506.13794](https://arxiv.org/abs/2506.13794): Jared Grogan, accessed 2026-08-27
- [Visa Trusted Agent Protocol](https://developer.visa.com/use-cases/trusted-agent-protocol) and [press release](https://investor.visa.com/news/news-details/2025/Visa-Introduces-Trusted-Agent-Protocol-An-Ecosystem-Led-Framework-for-AI-Commerce/default.aspx): Visa, 2025-10-14, accessed 2026-08-27
- [Accelerating the Adoption of Software and AI Agent Identity and Authorization](https://csrc.nist.gov/pubs/other/2026/02/05/accelerating-the-adoption-of-software-and-ai-agent/ipd): NIST NCCoE, Initial Public Draft 2026-02-05, accessed 2026-08-27
- [knowyouragent.network](https://knowyouragent.network/): RNWY score indexer, accessed 2026-08-27
- [ERC-8004 Explained: What It Solves and the Gap It Leaves](https://www.concordium.com/article/erc-8004-explained-what-it-solves-and-the-gap-it-leaves): Concordium (CIS-8004), accessed 2026-08-27
- [arXiv 2606.26028](https://arxiv.org/abs/2606.26028): three-chain empirical study of ERC-8004, accessed 2026-08-27
- [Know Your .agent?](https://estherdyson.substack.com/p/know-your-agent): Esther Dyson, 2026-05-06, accessed 2026-08-27
