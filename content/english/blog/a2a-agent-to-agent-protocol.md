---
title: "The A2A (Agent-to-Agent) Protocol: How Agents Delegate to Each Other, and Where Payments Plug In"
meta_title: ""
description: "A2A, announced by Google in April 2025 and donated to the Linux Foundation, standardizes agent-to-agent collaboration. This post covers its core objects (Agent Card, Task, Message, Artifact), how it differs from MCP, where x402, AP2 and UCP attach as payment extensions, adoption as of August 2026, and the criticism it has drawn."
date: 2026-08-27T10:00:00+09:00
lastmod: 2026-08-28T10:00:00+09:00
image: "/images/posts/a2a-agent-to-agent-protocol/a2a-layer-stack-1200.png"
categories: ["Blockchain"]
tags: ["a2a", "ai-agent", "agentic-payments", "x402", "mcp"]
author: "whackur"
translationKey: "a2a-agent-to-agent-protocol"
draft: false
---

Every time this blog has covered [x402, UCP and MPP](/en/blog/agentic-payments-june-2026-x402-ucp-mpp/) or [Know Your Agent](/en/blog/know-your-agent-kya-ai-agent-identity-onchain/), the term "A2A" showed up as an assumption. An agent hands work to another agent, pays for it, checks who the counterparty is. All of that sits on a lower layer: how do two agents talk in the first place? The attempt to standardize that layer is the Agent2Agent (A2A) protocol.

One thing up front. A2A itself has nothing to do with blockchains. It is a web protocol that moves JSON over HTTP. There are no wallets, tokens or chains in the spec. Blockchains enter through A2A's extension mechanism, as a payment layer bolted on top. This post starts with what A2A is, then covers how it differs from MCP, how payment extensions attach, how much it is actually used as of August 2026, and the recurring objection "we already have MCP, why do we need A2A?"

## What A2A is and where it came from

A2A is an open protocol that lets AI agents built by different companies, on different frameworks, running on different servers, work together **as agents rather than as tools**. Google Cloud published it on [April 9, 2025](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) with more than 50 partners including Atlassian, Salesforce, SAP and ServiceNow. The announcement lists five design principles: preserve agent autonomy (collaborate without sharing memory or tools), build on existing standards (HTTP, SSE, JSON-RPC), be secure by default, support tasks that run for hours or days, and stay modality agnostic (text, audio, video).

The context explains the motivation. Anthropic's MCP (Model Context Protocol), released in November 2024, was quickly becoming the standard way for an agent to reach tools and data. Meanwhile enterprises were accumulating agents from different vendors (HR, procurement, IT support) that had no common way to hand work to each other without a bespoke integration per vendor pair. Google's announcement stated that A2A complements MCP rather than replacing it.

Governance left Google's hands fast. On [June 23, 2025](https://developers.googleblog.com/en/google-cloud-donates-a2a-to-linux-foundation/) Google donated the spec, SDKs and tooling to the Linux Foundation, with AWS, Cisco, Google, Microsoft, Salesforce, SAP and ServiceNow as founding members and more than 100 supporting organizations. In [August 2025](https://lfaidata.foundation/communityblog/2025/08/29/acp-joins-forces-with-a2a-under-the-linux-foundations-lf-ai-data/) IBM Research folded its competing ACP (Agent Communication Protocol, built for BeeAI) into A2A and stopped independent development. [v1.0.0](https://github.com/a2aproject/A2A/releases/tag/v1.0.0) was tagged on March 12, 2026. On August 17, 2026 the project moved under the [Agentic AI Foundation (AAIF)](https://aaif.io/blog/a2a-joins-aaif), the Linux Foundation body that also hosts MCP, AGENTS.md, goose and agentgateway. The agent-to-tool standard and the agent-to-agent standard now live under the same roof.

### Four core concepts

The spec is not concept-heavy. Four objects carry most of the weight. The description below follows the [v1.0 specification](https://a2a-protocol.org/latest/specification/).

The **Agent Card** is the agent's business card: a JSON document with its name, provider, skills, supported transports and endpoints, required authentication, and whether it supports streaming and push notifications. The default location is `https://{domain}/.well-known/agent-card.json`. A client reads it to learn what it can ask this agent to do and how. Since v1.0 the card carries a `signatures` field so a JWS signature (over an RFC 8785 canonicalized form) can prove the card was not forged.

A **Task** is the unit of work. The server assigns an `id` and tracks `status`, output `artifacts`, and the message `history`. There are eight states. Two are active (`SUBMITTED`, `WORKING`), two are interrupted and waiting on the other side (`INPUT_REQUIRED`, `AUTH_REQUIRED`), and four are terminal (`COMPLETED`, `FAILED`, `CANCELED`, `REJECTED`). The payment extension described later reuses `INPUT_REQUIRED` as its "payment needed" signal.

A **Message** is one turn of the conversation and a **Part** is a piece of its content. A Message has a sender role (`ROLE_USER` or `ROLE_AGENT`) and an array of Parts; each Part holds text, inline binary (`raw`), or a remote file reference (`url`). A `contextId` groups multiple messages into one conversation.

An **Artifact** is a Task's output: a report file, structured JSON, a generated image, whatever the agent produced, composed of Parts. Keeping intermediate messages and final deliverables separate means the client never has to guess which part of the log is the actual result.

## How it works

A typical A2A interaction runs in this order.

1. **Discovery.** The client agent GETs `/.well-known/agent-card.json` from the remote server. The [official discovery page](https://a2a-protocol.org/latest/topics/agent-discovery/) also lists curated registries (an internal agent catalog) and direct configuration as alternatives, plus `GetExtendedAgentCard` for handing a more detailed card only to authenticated clients.
2. **Delegation.** The client sends the first Message with `SendMessage`. The server can answer directly or create a Task, return its `id`, and work asynchronously.
3. **Message exchange.** When the server needs more information it sets the Task to `INPUT_REQUIRED` and the client replies with a follow-up Message carrying the same `taskId`. Human-in-the-loop approval steps use the same mechanism.
4. **Progress updates.** The client can poll with `GetTask`, open an SSE (Server-Sent Events) stream via `SendStreamingMessage` or `SubscribeToTask` to receive state changes and Artifact chunks as they happen, or register a webhook for push notifications. For a job that takes hours, disconnecting and waiting for a push is the natural choice.
5. **Artifact return.** When the Task reaches `COMPLETED` the deliverables are in `artifacts`. Otherwise it ends in `FAILED`, `REJECTED` (server declined), or `CANCELED` (client called `CancelTask`).

On the wire, v1.0 defines three bindings with equivalence guarantees: JSON-RPC 2.0, gRPC, and REST-style HTTP+JSON. The same logical agent can be exposed over any of them, declared per entry in the Agent Card's `supportedInterfaces`. Authentication reuses standard schemes: OAuth 2.0 (v1.0 adds the Device Code flow, drops the deprecated Implicit and Password flows, and adds a `pkce_required` option), API keys, mTLS. The [v1.0 changes page](https://a2a-protocol.org/latest/whats-new-v1/) notes that method names moved from path style (`message/send`) to PascalCase (`SendMessage`), and that a `tenant` field was added to requests so one endpoint can serve multiple agents.

### Division of labor with MCP

MCP standardizes how a model or agent reaches tools, APIs and data sources. A server declares its tools, and the client (usually an LLM application) sends structured input and gets structured output back. It is mostly a function-call model: one call, one result.

The official [A2A and MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/) page uses an auto repair shop to draw the line. A customer agent talking to the shop manager agent is A2A ("my car makes a weird noise" gets narrowed down over several turns). The mechanic agent operating a diagnostic scanner, a repair manual database and a vehicle lift is MCP (tools with defined inputs and outputs). The mechanic asking a parts supplier agent about stock and placing an order is A2A again. In the document's own phrasing, A2A is about agents **partnering** on tasks, while MCP is about agents **using** capabilities.

| Aspect | MCP | A2A |
|--------|-----|-----|
| Connects | agent to tools and data | agent to agent |
| Interaction shape | structured in/out, mostly single call | multi-turn, long-running, stateful Task |
| Counterparty internals | tool schema is exposed | remote agent is opaque (no shared logic, memory or tools) |
| Discovery | server lists tools | Agent Card |
| Typical use | attach capabilities to one agent | delegate across team, framework or company boundaries |

The boundary is not perfectly clean. On launch day a Hacker News commenter (vessenes) who had read the spec and the client code wrote that if you implemented A2A for a project you probably would not need MCP as well. Wrapping an agent as a tool and exposing it over MCP is possible and common. That overlap is where the skepticism covered below starts.

![Layer diagram of the A2A stack. Top: optional commerce and payment extensions (UCP, AP2, the A2A x402 extension). Second: the A2A layer where a client agent and a remote agent exchange Agent Card, Task, Message and Artifact objects. Third: the MCP layer where each agent reaches its own tools. Bottom: transport (HTTP, JSON-RPC, gRPC, SSE, OAuth). A note says A2A core has no blockchain dependency and chains appear only in the x402 extension's settlement step.](/images/posts/a2a-agent-to-agent-protocol/a2a-layer-stack.svg)

*Where A2A (horizontal, agent to agent) and MCP (vertical, agent to tools) sit, and the optional payment extensions above them. Only one box settles on a chain: the x402 extension. Sources are the respective specs, checked 2026-08-28.*

## Where blockchains come in

This is the part this blog cares about. To repeat: the A2A core spec never mentions a blockchain. Authentication is OAuth, API keys or mTLS; identity is bound to a domain and a signed Agent Card; there is no concept of payment at all. Chains meet A2A through three routes: Google's a2a-x402 extension, the commerce protocols AP2 and UCP layered above it, and an academic proposal for decentralized discovery.

### x402 and the a2a-x402 extension

x402 is a payment protocol that actually uses HTTP status code 402 "Payment Required", a code reserved in the HTTP spec since the 1990s and never standardized. Coinbase revived it in May 2025. When a request needs payment the server returns 402 along with requirements (how much, which token on which chain, to which address). The client signs a payment authorization with its wallet and retries, a facilitator (a service that verifies the signature and settles on-chain) confirms it, and the server releases the response. The goal is for an agent to pay a few cents in stablecoins per request instead of a human signing up and registering a card. [x402.org](https://www.x402.org/) states support for EVM chains and Solana; when checked on August 27, 2026 it showed 75.41M transactions, $24.24M in volume and 22K sellers over the trailing 30 days. Governance has moved to an x402 Foundation under the Linux Foundation. For a concrete deployment see the [Apify x402 post](/en/blog/apify-x402-agentic-payments-coinbase-wallet/).

[google-agentic-commerce/a2a-x402](https://github.com/google-agentic-commerce/a2a-x402) is the extension that puts this flow inside an A2A Task. Google built it and maintains it in the google-agentic-commerce organization. As of August 28, 2026 the repo has 554 GitHub stars, 144 forks, a last push on August 4, 2026, and an Apache-2.0 license. The spec directory holds both v0.1 and v0.2; [v0.2](https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md), added on November 4, 2025, is the latest. The README still points to v0.1 as the official spec, and the only release tag is v0.1.0 (there is no v0.2.0 tag), so v0.2 is best read as the current spec on the main branch rather than a tagged release. The description below follows v0.2.

- The merchant agent declares the extension URI `https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2` in the `extensions` array of its Agent Card. The v0.1 URI was `https://github.com/google-a2a/a2a-x402/v0.1`, a leftover from when the organization was named google-a2a rather than google-agentic-commerce. With `required: true`, clients that do not understand the extension cannot call the paid skills.
- The client activates the extension by sending the same URI in the `X-A2A-Extensions` HTTP header; the server echoes it back to confirm.
- When the client requests a paid job, the merchant creates a Task in the `input-required` state (the v0.x spelling of v1.0's `INPUT_REQUIRED`) and puts `x402.payment.status: "payment-required"` in the message `metadata`. Where the payment requirements themselves (`x402PaymentRequiredResponse`: amount, asset, network, payee address and so on) travel depends on which of the two flows below is in use.
- The client evaluates the terms. It can decline with `payment-rejected`, or sign a `PaymentPayload` with its wallet and send it back under the same `taskId` with `x402.payment.status: "payment-submitted"`.
- The merchant verifies the signature through a facilitator, settles on-chain, moves the status through `payment-verified` to `payment-completed`, then does the actual work and returns Artifacts. Settlement results (`x402SettleResponse`) go into the `x402.payment.receipts` array, which must be present in the final Task message. Failures set `payment-failed` and put a short error code in `x402.payment.error`. The spec defines seven: `INSUFFICIENT_FUNDS`, `INVALID_SIGNATURE`, `EXPIRED_PAYMENT`, `DUPLICATE_NONCE`, `NETWORK_MISMATCH`, `INVALID_AMOUNT` and `SETTLEMENT_FAILED`.

In other words, the A2A Task state machine stays untouched and a second, payment-specific state machine rides on top of it in `metadata`. The payment data structures (`x402PaymentRequiredResponse`, `PaymentRequirements`, `PaymentPayload`, `x402SettleResponse`) are not redefined; the extension references Coinbase's core x402 spec for them.

The main change in v0.2 is a composable design that splits where those x402 objects travel inside A2A messages into two flows that can be combined with other protocols.

- **Standalone Flow.** The x402 objects go directly into A2A message metadata. `x402PaymentRequiredResponse` sits under the `x402.payment.required` key of `task.status.message.metadata`, and `PaymentPayload` under the `x402.payment.payload` key of `message.metadata`. The spec's JSON examples use `base` as the network. The metadata approach v0.1 defined corresponds to this flow.
- **Embedded Flow.** x402 acts as one form of payment inside a higher-level protocol such as AP2. `x402PaymentRequiredResponse` is embedded in a higher-level object such as an AP2 CartMandate and delivered through `task.artifacts`, and `PaymentPayload` is embedded in an AP2 PaymentMandate and delivered through `message.parts`. This is where AP2, covered in the next section, actually connects to x402.

The rule for telling the two apart is simple. When a client receives `x402.payment.status: "payment-required"`, it checks the metadata for an `x402.payment.required` key. If the key is there, this is the Standalone Flow; if not, it is the Embedded Flow and the client looks for the higher-level object in the artifacts.

v0.2 also lays out three signing patterns depending on whether a human is present. **Atomic Signing** (human-present): the wallet handles two signatures, one for the payment and one for the order, with a single user approval. **Delegated Signing** (human-not-present): the agent signs with its own key within a delegation the user pre-authorized. **Smart Contract Escrow** (decoupled): the user pre-funds a contract, signs once off-chain at checkout, and the merchant releases the funds from the contract.

Governance deserves a separate note. According to A2A's [extension governance page](https://a2a-protocol.org/latest/topics/extension-and-binding-governance/), official extensions live in the a2aproject organization in repositories prefixed `ext-{name}`, with URIs starting `https://a2a-protocol.org/extensions/`; experimental ones use the `experimental-ext-{name}` prefix. a2a-x402 sits in the google-agentic-commerce organization with a github.com URI, which puts it outside that official namespace. The example extensions listed in the official documentation (Secure Passport, Timestamp, Traceability, AGP) do not include x402 either. It is Google's extension, but not an official a2aproject extension.

The repository is not archived and carries no deprecation notice, but activity is low: the last push was August 4, 2026 and the last substantive commit on main was May 24, 2026 (a Dependabot configuration). The Python example (adk-demo) defaults to a mock facilitator and a mock wallet with a hardcoded key; real on-chain settlement requires a facilitator configuration and a wallet implementation of your own (the README suggests MetaMask, an MPC service, or a hardware signer). The v0.2 spec body itself is not labelled experimental, but the `schemes/` directory holding partner drafts still is. This repository remains the reference spec for x402 payments over A2A, and v0.2 is its latest version. For the current state of A2A core, look to the a2aproject organization and a2a-protocol.org instead.

### AP2 and UCP

Once agents can send payments the next question arrives immediately: how do you prove the user actually asked for this purchase, and who is liable when something goes wrong? That layer is AP2 (Agent Payments Protocol). Google announced it on [September 17, 2025](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol) with more than 60 partners including Adyen, American Express, Coinbase, Mastercard, PayPal and Revolut, and [ap2-protocol.org](https://ap2-protocol.org/) defines it as an open extension of A2A, with a separate integration guide for UCP. Its central device is the Mandate, a cryptographically signed authorization. The announcement describes an Intent Mandate (the user's original request) and a Cart Mandate (the exact items and price the user approved); the current v0.2 documentation organizes these as a Checkout Mandate and a Payment Mandate. Each is a verifiable digital credential (VDC) handed to merchants and payment processors as non-repudiable evidence. The announcement frames the three problems AP2 addresses as authorization, authenticity and accountability.

AP2's default rail is cards. v0.2 supports credit and debit cards; real-time bank transfers (UPI, PIX) and digital currencies are on the roadmap. Blockchains enter here, too, as an extension: alongside the announcement Google published an x402 extension for AP2 built with Coinbase, the Ethereum Foundation, MetaMask and others, and the AP2 repository's samples include x402 scenarios for both human-present and human-not-present flows. Standardization is being carried by the FIDO Alliance's Agentic Authentication and Payments working groups.

UCP (Universal Commerce Protocol) sits above that and handles the shopping conversation itself. Google published it on [January 11, 2026](https://developers.googleblog.com/under-the-hood-universal-commerce-protocol-ucp/) with more than 20 partners including Shopify, Etsy, Walmart, Target, Stripe, Visa and Mastercard. It defines a standard vocabulary for checkout, discounts, order management, fulfillment and identity linking, supports REST, A2A and MCP as transports, and is compatible with AP2 for payments. Recent UCP progress is covered in the [June 2026 agentic payments post](/en/blog/agentic-payments-june-2026-x402-ucp-mpp/).

So the stack is: A2A decides how agents exchange Tasks; UCP supplies the shopping vocabulary; AP2 supplies proof of user authorization and accountability; x402 supplies on-chain settlement. Of the four, only x402 touches a chain. Google's Open Source Blog [anniversary post](https://opensource.googleblog.com/2026/04/a-year-of-open-collaboration-celebrating-the-anniversary-of-a2a.html) groups AP2, UCP and the UI-oriented A2UI as the "A2Family", all built through A2A's extension model.

### The paper: on-chain Agent Cards plus x402

Academia has proposed filling A2A's gaps with a ledger. Awid Vaziry, Sandro Rodriguez Garzon and Axel Küpper of TU Berlin and T-Labs posted [arXiv 2507.19550](https://arxiv.org/abs/2507.19550), "Towards Multi-Agent Economies: Enhancing the A2A Protocol with Ledger-Anchored Identities and x402 Micropayments for AI Agents", on July 24, 2025. It was presented at IJCCI 2025 and appears in Springer's CCIS volume 2827.

The paper names two limitations. First, discovery is centralized: the well-known URI requires knowing the domain in advance, and a registry requires trusting its operator. Second, A2A has no agent-to-agent micropayments. The authors propose publishing Agent Cards on-chain as smart contracts, giving each agent a tamper-proof and verifiable identity that doubles as a discovery mechanism, and integrating x402 into A2A for chain-agnostic HTTP micropayments. They implement and evaluate the architecture.

One distinction matters when reading it. This is a paper, not the spec. The discovery methods the official documentation recognizes are still the well-known URI, registries and direct configuration, and v1.0's Signed Agent Cards prevent forgery through a domain owner's signature without putting the card on any chain. The underlying idea, anchoring agent identity in an on-chain registry, has been implemented separately on Ethereum as [ERC-8004](/en/blog/erc8004-agent-reputation-registry-lookup/), deployed to mainnet in January 2026, whose registration file includes A2A endpoints and an `x402Support` field. Different communities are filling the same gap in their own ways; the [KYA post](/en/blog/know-your-agent-kya-ai-agent-identity-onchain/) walks through those approaches.

## Where things stand in 2026

The Linux Foundation's [press release of April 9, 2026](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year) marked A2A's first year. The verified figures and status:

- **More than 150 supporting organizations**, up from 50 at launch. The Technical Steering Committee has eight companies: AWS, Cisco, Google, IBM Research, Microsoft, Salesforce, SAP and ServiceNow.
- **The v1.0 spec**, released in March 2026 as the first stable version, with equivalence guarantees across the three bindings (JSON-RPC, gRPC, HTTP+JSON), Signed Agent Cards, single-endpoint multi-tenancy, and modernized OAuth 2.0 flows. The Agent Card stayed backward compatible so one agent can advertise v0.3 and v1.0 at the same time. v1.0.1 followed on May 28, 2026.
- **Cloud platform integration.** Microsoft added A2A to Azure AI Foundry and Copilot Studio, AWS to Amazon Bedrock AgentCore Runtime, and Google Cloud [announced](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade) Vertex AI Agent Engine and Agentspace support with the v0.3 upgrade in August 2025. All three major clouds now host A2A agents in a managed runtime.
- **SDKs.** The press release counts five production-ready languages: Python, JavaScript, Java, Go and .NET. As of August 27, 2026 the [repository README](https://github.com/a2aproject/A2A) and roadmap list six, adding Rust.
- **GitHub stars.** More than 22,000 at the time of the press release; 25,522 when checked on August 28, 2026 (2,590 forks, last push August 25, 2026).
- **Production use** in supply chain, financial services, insurance and IT operations. Named examples come from Google Cloud's August 2025 post: Tyson Foods (sales and supply chain optimization) and Gordon Food Service (a real-time channel for product data and lead sharing).

The [roadmap](https://a2a-protocol.org/latest/roadmap/) (updated March 10, 2026) lists expanded SDK support for extensions, an A2A Inspector and a Technology Compatibility Kit (TCK) for validating implementations, and documentation of community best practices. The August 2026 move into AAIF continues that trajectory.

## Community reaction and criticism

The launch-day [Hacker News thread](https://news.ycombinator.com/item?id=43631381) collected 450 points and 277 comments, and skepticism dominated. The most-replied comment (zellyn) said it was "frustratingly difficult to see what these (A2A and MCP) protocols actually look like", asked for a single example conversation showing the LLM output and the JSON on the wire, and added that the wall of partner endorsements at the end made it seem worse. simonw wrote that he fully understood the value of LLMs calling tools and APIs but still did not see much value in LLMs calling other LLMs, questioning the premise of agent-to-agent communication. hliyan asked whether this was "rediscovering SOA and WSDL, but this time for LLM interop". phillipcarter put it bluntly: MCP solves specific problems people have in practice today, while A2A "solves a marketing problem that Google is chasing with technology partners". There was praise too. vessenes, after reading the spec and SDKs, said A2A addressed several of MCP's pain points with relatively lightweight answers, specifying in-band and out-of-band data flow and taking a sane token-based approach to security.

That skepticism showed up in a concrete event. On July 25, 2025 a contributor opened a [1,291-line PR](https://github.com/openai/openai-agents-python/pull/1245) adding A2A support to the OpenAI Agents SDK. A maintainer replied that they had no immediate plans to add A2A support to the SDK and could not say if or when they would review it; the PR was closed as stale on August 13. In the follow-up discussion the maintainer asked that any adapter be published as a separate package rather than in the core SDK. The episode resurfaced on HN in late October. The point is less that OpenAI rejected A2A and more that, through 2025, frameworks that put A2A in their core were the minority.

[Fatih Kadir Akın summed this up in September 2025](https://blog.fka.dev/blog/2025-09-11-what-happened-to-googles-a2a/) as "adoption beats architecture": Google may have built the technically superior protocol, but MCP built what developers actually wanted to use. He points to an indie developer wanting a simple tool integration having to wade through agent discovery, capability negotiation and security cards first, and to A2A approaching from enterprise orchestration while MCP shipped straight into consumer AI apps.

Assessments in 2026 are more balanced. Rost Glukhov's [2026 adoption analysis](https://www.glukhov.org/ai-systems/comparisons/a2a-protocol-2026-adoption/) boils down to "A2A is not dead. It is just not universal." The piece separates four tiers of adoption: logo adoption (a company lists support), SDK adoption (developers can actually build with it), platform adoption (clouds and frameworks support it natively), and production retention (teams keep relying on it for live workflows). The 150-organization figure speaks to the first two tiers, not the last one, and "support is not usage" is the central point. The conclusion is a practical recommendation: **start with MCP, design clean agent boundaries from the beginning, and add A2A only when those boundaries become real deployment, ownership or interoperability constraints.** Concretely, A2A earns its place when agents are independently deployed, owned by different teams, built on different frameworks, running with their own tools and permissions, and responsible for long-running tasks. If "agents" are a handful of functions inside one team, wrapping them as MCP tools is the better call. That advice lines up with what the official A2A documentation says about using both protocols together.

The criticism, then, comes in three strands. "MCP is enough, why learn another one" (overlap). "Lots of partner logos, where are the code contributions and production cases" (support versus usage). "Is agent-to-agent conversation actually needed" (doubt about the premise). The first has eased somewhat as v1.0 and cloud integrations lowered the learning cost. The second is filling in slowly with named cases like Tyson Foods and the IBM ACP merger. The third remains open.

## Further reading

- [A2A Protocol Specification](https://a2a-protocol.org/latest/specification/): the v1.0 spec itself, for exact object and method definitions.
- [A2A and MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/): the official division-of-labor explanation and the repair shop example.
- [a2a-samples](https://github.com/a2aproject/a2a-samples): example A2A agents built with ADK, LangGraph, CrewAI and others.
- [A2A x402 Extension spec v0.2](https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md): the payment state flow, the Standalone and Embedded flows, and the signing patterns.
- [Agentic Payments in June 2026](/en/blog/agentic-payments-june-2026-x402-ucp-mpp/): x402, UCP and MPP implementation progress, for a deeper look at the payment layer.
- [Know Your Agent (KYA)](/en/blog/know-your-agent-kya-ai-agent-identity-onchain/): the standards race over where agent identity gets anchored.

## Wrapping up

A2A is an HTTP protocol that lets agents from different organizations and frameworks recognize each other through Agent Cards, delegate work as Tasks, receive progress through streaming or push, and get results back as Artifacts. If MCP is the vertical standard that attaches tools to an agent, A2A is the horizontal standard that connects an agent to the agent next to it, and as of August 2026 both live under the same foundation (AAIF).

There is no blockchain in that core. Chains appear only in the settlement step of the a2a-x402 extension and in AP2's x402 extension, and even there we are at a draft spec (v0.2 is the latest, and the only tagged release is v0.1.0) with mock-facilitator examples. On-chain Agent Card proposals exist in a paper and, separately, in the ERC-8004 community, but they are not part of the A2A spec. Miss that distinction and it is easy to come away with the wrong impression that A2A is "the blockchain agent protocol".

Adoption is real but not universal. The 150 organizations, the v1.0 release and the three-cloud integrations are facts; so is the observation that those numbers do not equal deep production use. My own read is that if you are building something today, the community advice is right: start with MCP, and add A2A at the point where your agents become independent systems that hand long-running work across team or company boundaries. The payment layer (x402, AP2) is the step after that. For now, reading the specs and samples is the appropriate level of investment.

## References

- [A2A Protocol Specification](https://a2a-protocol.org/latest/specification/) — a2a-protocol.org, accessed 2026-08-27
- [What's New in A2A v1.0](https://a2a-protocol.org/latest/whats-new-v1/) — a2a-protocol.org, accessed 2026-08-27
- [Announcing Version 1.0](https://a2a-protocol.org/latest/announcing-1.0/) — a2a-protocol.org, accessed 2026-08-27
- [A2A and MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/) — a2a-protocol.org, accessed 2026-08-27
- [Agent Discovery in A2A](https://a2a-protocol.org/latest/topics/agent-discovery/) — a2a-protocol.org, accessed 2026-08-27
- [A2A Roadmap](https://a2a-protocol.org/latest/roadmap/) — a2a-protocol.org (updated 2026-03-10), accessed 2026-08-27
- [a2aproject/A2A](https://github.com/a2aproject/A2A) — GitHub (25,522 stars; v1.0.0 2026-03-12; v1.0.1 2026-05-28), accessed 2026-08-28
- [Announcing the Agent2Agent Protocol (A2A)](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) — Google for Developers, 2025-04-09, accessed 2026-08-27
- [Google Cloud donates A2A to Linux Foundation](https://developers.googleblog.com/en/google-cloud-donates-a2a-to-linux-foundation/) — Google for Developers, 2025-06-23, accessed 2026-08-27
- [Agent2Agent protocol (A2A) is getting an upgrade](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade) — Google Cloud Blog, 2025-08-01, accessed 2026-08-27
- [ACP Joins Forces with A2A Under the Linux Foundation's LF AI & Data](https://lfaidata.foundation/communityblog/2025/08/29/acp-joins-forces-with-a2a-under-the-linux-foundations-lf-ai-data/) — LF AI & Data, 2025-08-29, accessed 2026-08-27
- [A2A Protocol Surpasses 150 Organizations...](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year) — Linux Foundation, 2026-04-09, accessed 2026-08-27
- [A year of open collaboration: Celebrating the anniversary of A2A](https://opensource.googleblog.com/2026/04/a-year-of-open-collaboration-celebrating-the-anniversary-of-a2a.html) — Google Open Source Blog, 2026-04-16, accessed 2026-08-27
- [A2A joins AAIF's open agentic stack](https://aaif.io/blog/a2a-joins-aaif) — Agentic AI Foundation, 2026-08-17, accessed 2026-08-27
- [google-agentic-commerce/a2a-x402](https://github.com/google-agentic-commerce/a2a-x402) — GitHub (554 stars; last push 2026-08-04; v0.2 spec added 2025-11-04; only tag is v0.1.0, no v0.2.0 tag), accessed 2026-08-28
- [A2A Protocol: x402 Payments Extension v0.2](https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md) — GitHub, accessed 2026-08-28
- [Extension and Binding Governance](https://a2a-protocol.org/latest/topics/extension-and-binding-governance/) — a2a-protocol.org, accessed 2026-08-28
- [x402.org](https://www.x402.org/) — x402 Foundation, accessed 2026-08-27
- [Towards Multi-Agent Economies: Enhancing the A2A Protocol with Ledger-Anchored Identities and x402 Micropayments for AI Agents](https://arxiv.org/abs/2507.19550) — Vaziry, Rodriguez Garzon, Küpper (TU Berlin / T-Labs), arXiv 2025-07-24; IJCCI 2025, Springer CCIS vol. 2827, accessed 2026-08-27
- [Agent Payments Protocol (AP2)](https://ap2-protocol.org/) — ap2-protocol.org (v0.2), accessed 2026-08-27
- [Powering AI commerce with the new Agent Payments Protocol (AP2)](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol) — Google Cloud Blog, 2025-09-17, accessed 2026-08-27
- [google-agentic-commerce/AP2](https://github.com/google-agentic-commerce/AP2) — GitHub (x402 sample scenarios), accessed 2026-08-27
- [Under the hood: Universal Commerce Protocol (UCP)](https://developers.googleblog.com/under-the-hood-universal-commerce-protocol-ucp/) — Google for Developers, 2026-01-11, accessed 2026-08-27
- [The Agent2Agent Protocol (A2A) | Hacker News](https://news.ycombinator.com/item?id=43631381) — 2025-04-09, 450 points / 277 comments, accessed 2026-08-27
- [Feature: Add Agent-to-Agent (A2A) Protocol Support with AgentCardBuilder #1245](https://github.com/openai/openai-agents-python/pull/1245) — openai/openai-agents-python, opened 2025-07-25 / closed 2025-08-13, accessed 2026-08-27
- [What Happened to Google's A2A?](https://blog.fka.dev/blog/2025-09-11-what-happened-to-googles-a2a/) — Fatih Kadir Akın, 2025-09-11, accessed 2026-08-27
- [Google A2A Protocol in 2026: Adoption, Hype, and Reality](https://www.glukhov.org/ai-systems/comparisons/a2a-protocol-2026-adoption/) — Rost Glukhov, accessed 2026-08-27
