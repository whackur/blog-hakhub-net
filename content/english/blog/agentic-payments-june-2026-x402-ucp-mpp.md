---
title: "Agentic Payments in June 2026: x402, UCP, and MPP Implementation Progress"
meta_title: ""
description: "A month's worth of implementation changes across x402, UCP, MPP/pay.sh, and ACP: auth-capture, builder-code attribution, idempotency hardening, and ERC-8126 going Final."
date: 2026-06-30T07:00:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
image: ""
categories: ["Blockchain"]
tags: ["agentic-payments", "x402", "ucp", "mpp", "stablecoin"]
author: "whackur"
translationKey: "agentic-payments-june-2026-x402-ucp-mpp"
draft: false
---

Agentic payments in June 2026 moved from "can an agent pay" toward "who authorized the payment, how is it verified, and how is it traced." The major open protocols (x402, UCP, MPP/pay.sh, and ACP) each had meaningful implementation changes. All figures and commit details below come from GitHub API, PyPI, and npm registry checks.

## What agentic payments are

Agentic payments are transactions where an AI agent pays for services without real-time human approval. The basic flow: an agent calls an image-generation API. The API returns HTTP 402 with a payment challenge: a specification that says "send this amount in this token to this address and I'll serve you." The agent executes an on-chain stablecoin payment and re-sends the request with a payment receipt. The API verifies the receipt and returns the content.

Card payments don't fit here for two reasons. Card checkout requires a human to approve each transaction. An agent calling dozens of APIs per minute can't pause for human input each time. And usage-based services like LLM inference don't have a fixed charge until the request completes, which breaks the pre-authorization assumption that card payments depend on.

**Key actors in an agentic payment flow:**

- **Requester**: the AI agent or client application calling the paid API
- **Resource server**: the server offering paid content or services; returns HTTP 402 with a payment challenge when a request arrives without valid payment
- **Facilitator**: an intermediate service that executes the on-chain payment on behalf of the requester and delivers the payment receipt to the resource server
- **Merchant**: in UCP contexts, the business selling goods or services
- **Buyer agent**: an agent handling the purchase flow on the merchant's platform
- **Payment challenge**: the specification in the HTTP 402 response body describing payment terms
- **Settlement**: the on-chain transfer of payment tokens. Fulfillment is the subsequent delivery of the service or product

**What each protocol targets:**

Agentic payments aren't a single protocol. Different standards handle different layers.

- **x402**: standardizes the HTTP payment challenge and response. Covers immediate settlement and auth-capture (pre-authorize now, settle later) flows. Stablecoin-centric.
- **UCP (Universal Commerce Protocol)**: the commerce layer for cart and checkout. Handles buyer consent, delegated identity, and signed order evidence for agentic shopping scenarios.
- **MPP/pay.sh**: tooling for payment initiation from execution environments like CLI and MCP servers. Solana-based.
- **ACP (Agentic Commerce Protocol)**: the OpenAI/Stripe-affiliated protocol. Focused on product feed provenance and transaction traceability.

What follows covers the concrete implementation changes each protocol made in June 2026.

## x402: auth-capture, attribution, usage-based settlement

Development on x402 is concentrated in `x402-foundation/x402`. The `coinbase/x402` repository saw near-zero activity in June.

**Auth-capture flow.** The TypeScript `@x402/evm` client added support for detecting auth-capture payment requirements and signing a payer-agnostic `PaymentInfo` hash using ERC-3009 (a meta-transaction token transfer authorization standard) by default, or Permit2 (Uniswap's one-shot signature delegation standard) as fallback. Splitting authorization from capture is standard in e-commerce: authorize at order time, capture at shipment or after inventory confirmation. This change lets x402 express those flows instead of only immediate settlement. Server and facilitator support was left for follow-up PRs.

**Builder-code attribution.** x402's builder-code extension embeds ERC-8021 Schema 2 attribution codes in settlement transaction calldata as a CBOR suffix. Three codes: `a` for the application exposing the paid API, `s` for the client or intermediate service, `w` for the settlement facilitator wallet.

In mid-June, the `s` field was expanded from a single service code to an array. The motivation: when an MCP server calls a paid API and another agent runtime wraps that, there are multiple intermediate actors in one payment path. Revenue attribution, dispute investigation, and cost analysis all need to account for a chain of participants rather than a single client ID.

**Usage-based settlement via `upto`.** The `upto` EVM scheme documentation was clarified on settle-time verification. The signature validation checks `permit2Authorization.permitted.amount` (the maximum the user authorized), while the actual settlement must confirm that `paymentRequirements.amount` is at or below that ceiling. This matters for LLM or compute calls where the final charge isn't known until the request completes. It prevents overclaiming.

**MCP v1 support.** Python and Go clients added x402 v1 payment challenge handling. TypeScript was already covered; this extends the same payment flow to other runtimes calling paid MCP servers.

**Security hardening.** EOA rejection as an asset address (prevents accepting a plain wallet address as a payment token), partial money string rejection (blocks inputs like `$0.01abc`), explicit gas limits on batch `settle()` calls (reduces EVM execution failure risk), and v1 discovery path param preservation (prevents route mismatching on paid API endpoints).

Package releases: PyPI `x402 2.12.0` (May 29), npm `@x402/* 2.14.0` (May 29), PyPI `x402 2.13.0` (June 12), npm `@x402/extensions 2.15.0` (June 12).

## UCP: idempotency, buyer consent, signed order responses

The Universal Commerce Protocol saw a focused set of changes around payment correctness and evidence.

**Idempotency 409 contract.** A [fix commit](https://github.com/Universal-Commerce-Protocol/ucp) made the idempotency key contract explicit: same key plus mismatched payload returns HTTP 409 Conflict. This closes a gap where an agent retrying after a network failure could accidentally get a stale cached response for a different cart or checkout body. The `Content-Digest` header serves as the natural payload comparison primitive. This is a small spec change with real consequences for preventing duplicate orders and stale price confirmations.

**Buyer consent expansion.** Cart and checkout now support purpose-scoped consent structures with `granted`, `source`, and `description` fields. The `source` distinguishes between a business default and a platform-captured buyer preference. For agentic shopping, this matters because agents can encounter consent decisions during browsing and cart assembly, not only at checkout.

**Delegated identity providers.** Merchants can declare trusted external identity providers. If the platform already holds an upstream token from a trusted IdP, it can try an accelerated identity chaining flow rather than forcing a fresh OAuth redirect. Fallback to direct OAuth remains required when the chaining fails.

**Signed order responses.** `get_order` responses now include `Signature`, `Signature-Input`, and `Content-Digest` headers. An agent acting on an order state (requesting a refund, changing delivery, triggering a follow-up payment) can verify the response it received wasn't tampered with.

## MPP/pay.sh: subscriptions and onboarding

`solana-foundation/pay` added two features:

**Experimental subscriptions.** `feat: add support for subscriptions [experimental]` introduced client-side subscription intent, 402 challenge parsing, `Authorization: Payment` HTTP header support, local subscription persistence, and a `pay subscriptions list/status/new/cancel/refresh` CLI. The intent: group repeated API calls into a subscription or delegation rather than handling each as an individual payment. Server-side activation verification and on-chain `create_plan` broadcast remain as TODOs. Not production-ready yet, but the direction is clear.

**Redeem codes.** `pay setup --redeem CODE` lets a campaign activation code bypass the MoonPay/onramp flow and get funding from a gateway hot wallet. The practical problem it solves: getting a developer to their first paid API call requires wallet creation, stablecoin acquisition, gas, and payment authorization. A redeem code collapses that to a sponsor credit. The tradeoffs (abuse prevention, regional constraints, accounting) are left to the implementation.

npm `@solana/pay 1.0.18` shipped June 9.

## ACP: product feed provenance

Agentic Commerce Protocol added `feed_update_id` and `last_update_id` to the Feed API upsert response. Every product feed upsert gets a version identifier, and each product carries the ID of the last update that changed it. This creates a traceable link between the product state an agent saw and the checkout, refund, or dispute that followed.

## ERC-8126 Final, ERC-8273 Draft

On the Ethereum ERC side:

[ERC-8126](https://eips.ethereum.org/EIPS/eip-8126) (AI Agent Verification) moved to Final status on June 2. It defines the interface for security verification providers that assess ERC-8004 registered agents across wallet history, contract code, web endpoints, media, and Solidity code, outputting a 0-100 risk score. Final means the spec is stable enough to implement against.

[ERC-8273](https://github.com/ethereum/ercs/blob/master/ERCS/erc-8273.md) (Attestation-Gated Agentic Actions) was added as a Draft. It proposes `attestAndCall()`: an authorized attestor creates an attestation, the registry logs a persistent audit record, and EIP-1153 transient storage holds a one-shot authorization that's used and discarded within the same transaction. The motivation is that a long-lived identity (ERC-8004) doesn't answer "is this specific action authorized right now", which is what you need at the moment of a swap, payment, or escrow release. Draft status; interface and security model may change.

ERC-8004 itself had no ethereum/ercs process-status change in June. That is separate from deployment status: the ERC-8004 registries were already live on Ethereum mainnet as of 2026-01-29.

## The layer split

The June changes show agentic payments splitting across layers rather than converging on one protocol. x402 handles HTTP 402 payment challenges and facilitator settlement. UCP covers cart/checkout consent, identity, and order evidence. ERC-8004/8126/8273 handle agent identity and action-level authorization. pay.sh handles execution-surface tooling.

The practical implication is that building a complete agentic payment flow requires decisions across all four layers, and they don't yet talk to each other in a standardized way.

If you're evaluating an integration now, it helps to mark what is unfinished. x402 auth-capture landed client-side signing only; server and facilitator support is pending. MPP subscriptions still have server-side activation verification and the on-chain `create_plan` broadcast as TODOs. ERC-8273 is a Draft whose interface can change. As of this month, the changes you can put into production directly are the UCP idempotency contract and the x402 security patches. The rest are directional signals.

## Further reading

- [x402 Foundation GitHub](https://github.com/x402-foundation/x402) — protocol repository
- [UCP specification](https://ucp.dev/2026-01-11/specification/overview/) — Universal Commerce Protocol
- [ERC-8126](https://eips.ethereum.org/EIPS/eip-8126) — AI Agent Verification, Final
- [x402 builder-code extension](https://docs.x402.org/extensions/builder-code) — attribution spec

## References

- [x402 Foundation GitHub](https://github.com/x402-foundation/x402) — accessed 2026-06-30
- [PyPI — x402](https://pypi.org/project/x402/) — accessed 2026-06-30
- [npm — @x402/core](https://registry.npmjs.org/@x402/core) — accessed 2026-06-30
- [UCP GitHub](https://github.com/Universal-Commerce-Protocol/ucp) — accessed 2026-06-30
- [ACP GitHub](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol) — accessed 2026-06-30
- [Solana Foundation pay GitHub](https://github.com/solana-foundation/pay) — accessed 2026-06-30
- [ERC-8126: AI Agent Verification](https://eips.ethereum.org/EIPS/eip-8126) — ethereum.org, Final (2026-06-02); accessed 2026-06-30
- [ERC-8273 Draft](https://github.com/ethereum/ercs/blob/master/ERCS/erc-8273.md) — ethereum/ercs; accessed 2026-06-30
