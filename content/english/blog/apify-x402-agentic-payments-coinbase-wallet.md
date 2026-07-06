---
title: "Apify x402 and Coinbase Wallets, in Depth: How Agents Buy Web Automation Tools Directly"
meta_title: ""
description: "Apify opened more than 20,000 Actors to x402. This deep dive explains the HTTP 402 flow, EIP-3009 and Permit2, facilitators, Coinbase Agentic Wallet, Bazaar discovery, security practices, the agentic-payment ecosystem, and country-level constraints."
date: 2026-07-05T01:10:00+09:00
lastmod: 2026-07-06T11:32:39+09:00
image: ""
categories: ["Blockchain"]
tags: ["x402", "agentic-payments", "apify", "coinbase", "ai-agent", "usdc", "base", "eip-3009", "stablecoin"]
author: "whackur"
translationKey: "apify-x402-agentic-payments-coinbase-wallet"
draft: false
---

Apify, the web scraping platform, [announced x402 support](https://blog.apify.com/introducing-x402-agentic-payments/): AI agents can now run more than 20,000 Apify Actors by paying with USDC on Base, with no Apify account and no API key. Apify frames the prior x402 ecosystem as roughly 2,000 endpoints, so by its own count this integration expanded the paid-tool surface by about 10x.

The structural change matters more than the number. A web automation marketplace that used to require a human to sign up and attach a card or credits has become a tool supply layer that agents can discover, pay for, and call at runtime. This expanded version looks at both sides: the technical core of x402, including HTTP 402, EIP-3009, Permit2, facilitators, Coinbase Agentic Wallet, and Bazaar discovery, and the business context around competing protocols, adoption metrics, Korea, and operational security.

## TL;DR

- On June 30, 2026, Apify opened more than 20,000 Actors to x402 payments. Agents can pay for Actor runs with USDC on Base without an Apify account or API key.
- x402 revives HTTP 402 Payment Required as a real payment handshake. v2 standardized the `PAYMENT-REQUIRED`, `PAYMENT-SIGNATURE`, and `PAYMENT-RESPONSE` headers and added a path toward discovery through Bazaar.
- The protocol has no country lock, but the surrounding layers do. Wallet and onramp availability, Apify seller KYC and payout methods, stablecoin regulation, tax, and scraping law still need jurisdiction-by-jurisdiction review.

## What changed when Apify joined x402

Apify runs web scraping and browser automation in the cloud. The execution unit is an Actor, a serverless program, and developers can publish Actors to [Apify Store](https://docs.apify.com/platform/actors/publishing/monetize) as paid products. Search result collectors, social media crawlers, price monitors, and map data extractors are already sold there.

Until now the customer was usually a human: create an account, add billing, generate an API token, then call the API. The x402 integration changes that assumption. An agent calls an Actor API endpoint, receives an HTTP 402 payment requirement, signs a payment payload from its wallet, and retries the same request. Apify also added x402 support to [`mcpc`](https://github.com/apify/mcpc), its universal CLI client for the Model Context Protocol, so tool discovery and payment can sit in the same agent workflow.

The important shift is that an agent's usable tool list is no longer frozen at deploy time. It can decide at runtime that it needs an Instagram profile scraper, buy a dollar's worth of access, run it, and continue the task. Apify's integration is not just a crypto checkout. It is a runtime-purchasable tool supply layer for agents.

## The x402 payment flow

HTTP 402 Payment Required was reserved in the HTTP spec for future payment use, but it mostly sat unused. x402 turns it into a working protocol. According to the [Coinbase Developer Platform docs](https://docs.cdp.coinbase.com/x402/welcome), x402 lets clients and servers exchange stablecoin payments over HTTP without accounts, sessions, or bespoke API keys.

The flow has four steps.

1. The client sends a normal HTTP request to a paid resource.
2. The server replies with HTTP 402 and a `PAYMENT-REQUIRED` header. The header contains base64-encoded JSON with the accepted scheme, network, token, amount, recipient, and expiry details.
3. The client wallet signs a payment payload and retries the same request with a `PAYMENT-SIGNATURE` header.
4. The server verifies and settles the payment through a facilitator, then returns the resource with a `PAYMENT-RESPONSE` header.

x402 v2 standardized those three headers. `PAYMENT-REQUIRED` carries the server's offer, `PAYMENT-SIGNATURE` carries the buyer's proof of authorization, and `PAYMENT-RESPONSE` carries the settlement result. In Apify's examples, Base mainnet is identified with the CAIP-2 network string `eip155:8453`, and `1000000` means one dollar because USDC uses 6 decimals.

## EIP-3009, Permit2, and facilitators

The gasless user experience comes from the buyer not having to submit the on-chain transaction directly. On EVM chains, the smoothest path is [EIP-3009](https://eips.ethereum.org/EIPS/eip-3009) `transferWithAuthorization`. The buyer signs an EIP-712 typed message containing fields such as `from`, `to`, `value`, `validAfter`, `validBefore`, and `nonce`. A facilitator submits that authorization on-chain and pays gas. USDC and EURC support EIP-3009, which is why USDC is the most common x402 example.

Not every ERC-20 supports EIP-3009. For generic ERC-20s, x402 uses Permit2. Permit2 is Uniswap's universal approval and transfer layer, and x402 can combine it with gas sponsorship extensions. Without a sponsorship extension, the buyer may still need a one-time Permit2 approval before the first payment. So the cleanest path is still an EIP-3009 token such as USDC.

A facilitator is the service that keeps sellers from having to run blockchain infrastructure. The resource server passes the payment payload to the facilitator for verification and settlement. The [CDP network support docs](https://docs.cdp.coinbase.com/x402/network-support) list support for Base, Polygon, Arbitrum, World, and Solana on the Coinbase Developer Platform facilitator. The pricing model is 1,000 transactions per month for free, then $0.001 per transaction, with gas charged separately. The x402 protocol itself has no native token and no protocol fee.

x402 is also not a one-chain protocol. The [x402 network and token docs](https://docs.x402.org/core-concepts/network-and-token-support) cover EVM, Solana, TON, Algorand, Stellar, Aptos, Hedera, Keeta, and Concordium network families. That is the broader protocol and facilitator ecosystem. Apify's current integration is narrower: USDC on Base.

## Payment schemes: exact, upto, and batch settlement

A scheme defines how much the buyer authorizes and how the seller settles it.

`exact` is a fixed amount payment. It fits cases like reading one article or calling one fixed-price API endpoint. It is awkward for an Actor whose cost is only known after the run finishes, so Apify layers a deposit pattern on top. In the direct Actor-run flow described in the Apify announcement, the server asks for a $1 prepaid deposit and refunds unused server-side balance after 60 minutes with no active runs or new paid calls.

`upto` is better for variable-cost work. The buyer authorizes a maximum, and the service charges actual usage up to that ceiling when the run completes. Apify describes this as the preferred shape for Actors whose runtime cost is unknown at the start.

`batch-settlement` addresses high-frequency micropayment workloads. Instead of settling every request on-chain, the buyer deposits into escrow, signs off-chain vouchers, and sellers redeem them in batches. Cloudflare has also proposed a deferred pattern for crawler and publisher workflows where the cryptographic handshake can happen immediately while financial settlement is delayed or aggregated.

One detail is easy to mix up. The manual prepaid-token path in the [Apify x402 docs](https://docs.apify.com/platform/integrations/x402) has a $1 minimum, a token balance that acts as a hard cap, a 14-day expiry, and no refund for unused balance. The direct Actor-run `exact` flow in the Apify announcement describes a different $1 deposit and a refund after 60 minutes of inactivity. Both are Apify-documented flows, but they apply in different contexts.

## Agentic Wallet is not an exchange account

The Coinbase name is the easiest source of confusion. The `awal` tool that Apify recommends is Coinbase Agentic Wallet CLI, not a Coinbase exchange account. It lets an agent authenticate by email OTP, hold USDC, read a 402 challenge, and sign the payment payload.

Where the funds live is the important part. The [Apify docs](https://docs.apify.com/platform/integrations/x402) state that funds live in the wallet itself, not in a Coinbase exchange account, and can come from any source that sends USDC on Base. You can withdraw from an exchange, send from another wallet, or use an onramp. The protocol requirement is a funded wallet that can speak the supported asset and network, not a Coinbase exchange signup.

That does not remove wallet risk. Agentic Wallet replaces a human approval button with a programmable signing surface, spend controls, policies, and auditability. An agent wallet should be treated like a low-balance hot wallet or prepaid debit card. Operators still need to define balances, token allowances, task budgets, and the list of Actors the agent is allowed to buy.

## Apify pricing and Actor eligibility

There are now two buyer paths.

The first is the existing Apify account path. A human creates an account, adds billing, and calls Actors with an Apify token. Even after x402, a client can send an Apify token instead of a payment signature and pay from the account balance.

The second is the wallet path. The buyer authenticates `awal`, funds the wallet with Base USDC plus a tiny amount of Base ETH for the first wallet deployment, then pays the agentic endpoint. In the documented manual prepaid-token flow, the returned token behaves like a bearer token. Actor runs draw down the balance, and the token balance is the absolute spending cap. The token expires after 14 days and unused balance is not refunded, so buyers should fund only what they expect to use.

Not every Actor qualifies. For now, an x402-eligible Actor must use Pay Per Event pricing, run with limited permissions, and not use Standby mode. Eligible Actors are marked with `allowsAgenticUsers=true` and surface in agentic discovery.

Sellers still go through Apify's normal monetization path. Revenue share is 80% for Pay Per Event, and payouts run monthly. Invoices are generated on the 11th, sellers get a 3-day review window, and auto-approval happens on the 14th. Minimum payout thresholds are $20 for PayPal and Wise and $100 for other methods. Getting paid requires billing information, a payout method, identity verification, and AML/KYC checks.

## Bazaar and the discovery layer

x402 makes an endpoint payable, but it does not automatically make that endpoint findable. CDP Bazaar addresses discovery. The [CDP Bazaar docs](https://docs.cdp.coinbase.com/x402/bazaar) describe it as a catalog and search layer for x402-enabled services, with endpoint metadata and trust signals derived from payment activity.

Sellers declare input and output schemas plus discovery metadata in route configuration. When the CDP facilitator successfully settles a payment for that endpoint, it can index the metadata. Verification alone is not enough. Settlement has to succeed, and there is no separate registration step.

Buyers can browse `GET /v2/x402/discovery/resources`, search `GET /v2/x402/discovery/search`, or use the Bazaar MCP server for agent workflows. Resources with no activity in the last 30 days are excluded from results, and quality metrics are recomputed every 6 hours.

This matters because discovery is the other half of agent commerce. If a wallet is the payment instrument and x402 is the payment language, Bazaar is how the agent finds what it can buy. Apify's marketplace integration makes that layer more important because it adds a large set of real tools to the searchable surface.

## The complementary protocol map

Agent payments will not be a single-protocol market. Several layers are forming around different parts of the transaction.

- **MCP** is the tool discovery and invocation interface. It is not primarily a payment rail.
- **x402** is the machine-to-machine API payment rail: HTTP resource, wallet signature, facilitator, settlement.
- **Google AP2** focuses on payment authorization through verifiable mandates such as intent, cart, and payment mandate. It can support cards, bank transfers, and crypto, with x402 as a stablecoin rail.
- **Skyfire** productizes agent payments with spend caps and identity.
- **Stripe, Visa, and Mastercard** are bringing agent authorization into existing checkout and card-network flows.
- **Cloudflare** approaches the market from the resource gateway side with pay-per-crawl and Monetization Gateway.
- **Circle** connects USDC-native micropayments and nanopayments to the same design space.

In production these are more likely to stack than to replace one another. MCP can discover tools, x402 can pay for machine-to-machine API calls, AP2 or card-network frameworks can handle retail checkout authorization, and settlement can use stablecoins or legacy rails depending on the merchant and jurisdiction.

## Reading adoption metrics and forecasts

Agentic commerce forecasts are large. Bain, Morgan Stanley, and McKinsey have published scenarios in which agent-driven commerce reaches hundreds of billions or even trillions of dollars by 2030. Those are forecasts, not realized revenue. The range depends heavily on methodology and on how much purchasing authority actually moves from humans to agents.

x402 adoption numbers also need caution. Cumulative transaction counts and volume can include tests, gamified activity, self-dealing, or wash-like behavior. Early incentive-driven traffic can make “agent payments” look more mature than they are. A better read looks at wash-adjusted volume, unique paying clients, repeat purchases, and settlement data from real service endpoints.

That is why Apify is interesting even before Apify-specific x402 volume is public. It connects x402 to a real web automation marketplace. The metric to watch is not just transaction count. It is whether agents repeatedly buy Actors to finish useful tasks.

## Country-level constraints for Korean developers

The protocol itself has no country lock. x402 runs through HTTP and wallet signatures, and Apify's x402 buyer path does not require an Apify account. The surrounding layers are different.

First is wallet and onramp access. Coinbase exchange, onramp, and hosted wallet products vary by country. If production depends on `awal`, check whether the product and email OTP automation work in your jurisdiction. This still does not mean a Coinbase exchange account is mandatory. If you can fund the wallet with Base USDC from another route, the protocol requirement is met.

Second is seller KYC and payout. The official Apify documents reviewed here do not say that only U.S. residents can sell. A Korean developer should expect the normal Apify requirements: account, billing information, tax documentation, payout method, identity verification, and AML/KYC. Payout-method availability, sanctions screening, and tax treatment remain country-specific.

Third is stablecoin and data law. Korea's dedicated stablecoin framework is still being shaped, and tax treatment, stablecoin acquisition, and reporting can change. Also, paying for a tool and legally collecting the target data are separate questions. Target-site terms, privacy law, copyright, database rights, and sector-specific rules need to be assessed Actor by Actor.

KakaoPay being mentioned as an x402 Foundation participant is a useful signal that Korean payment companies are watching agentic payment standards. It does not mean domestic onramps or won-stablecoin settlement paths are ready. For Korean production use, compliance and payout paths will likely be the bottleneck before the protocol itself.

## Operational security checklist

The technology is only half of the rollout. The operator still has to define policy.

- Keep balances small. A first pilot in the $10 to $50 range across 3 to 5 Actors is a reasonable shape.
- Do not fund the agent wallet from a main wallet. Treat it as a low-balance hot wallet.
- Treat prepaid tokens and `PAYMENT-SIGNATURE` payloads like API keys. Keep them out of logs, terminal output, issues, and dashboards.
- Use an Actor allowlist. Do not let an agent buy any tool it discovers.
- Put per-run ceilings in `upto` or prepaid caps, and add a task-level budget as a separate policy.
- For side-effecting work, prefer settle-then-work over verify-then-work. It adds latency but reduces grant-before-settlement and replay windows.
- Check nonce, short expiry, and request path/method binding. Make sure proxies do not strip, duplicate, or reuse payment headers incorrectly.
- Review scraping legality per Actor. Paying for the tool and legally using the collected data are separate issues.
- Treat email OTP automation as another security surface. If an agent can read an inbox, that inbox access should be narrow and auditable.

## Wrap-up

Apify's x402 integration moves agentic payments from demos toward product scale. More than 20,000 Actors reachable through Base USDC and HTTP 402 means agents can discover, buy, and run web automation tools from a real marketplace at runtime.

It does not remove the operational work. x402 is the payment language, facilitators reduce blockchain infrastructure, and Agentic Wallet gives agents a signing surface. Actual production safety comes from budget caps, allowlists, token secrecy, KYC, payouts, local law, and scraping compliance.

The sensible path is to start small: low wallet balance, narrow Actor allowlist, `upto` or prepaid caps, settle-then-work for side effects, and strict log masking. Then watch whether Apify-specific settlement data and wash-adjusted x402 usage show sustained real demand.

## Further reading

- [x402 quickstart for sellers](https://docs.x402.org/getting-started/quickstart-for-sellers): SDKs and schemes for exposing a paid API
- [Coinbase Developer Platform x402 docs](https://docs.cdp.coinbase.com/x402/welcome): protocol structure, facilitator, and supported networks
- [CDP x402 Bazaar](https://docs.cdp.coinbase.com/x402/bazaar): endpoint discovery and schema metadata for x402 services
- [Agentic payments, June 2026](/en/blog/agentic-payments-june-2026-x402-ucp-mpp/): recent changes across the wider payment stack including x402

## References

- [Introducing x402 support: 10x more tools for autonomous agents](https://blog.apify.com/introducing-x402-agentic-payments/), Apify Blog, accessed 2026-07-06
- [Apify x402 integration docs](https://docs.apify.com/platform/integrations/x402), Apify Docs, accessed 2026-07-06
- [Monetize your Actor](https://docs.apify.com/platform/actors/publishing/monetize), Apify Docs, accessed 2026-07-06
- [Monthly payouts](https://docs.apify.com/platform/actors/publishing/monetize/monthly-payouts), Apify Docs, accessed 2026-07-06
- [Apify Store Publishing Terms and Conditions](https://docs.apify.com/legal/store-publishing-terms-and-conditions), Apify Legal, accessed 2026-07-06
- [x402 overview](https://docs.cdp.coinbase.com/x402/welcome), Coinbase Developer Platform, accessed 2026-07-06
- [Network Support](https://docs.cdp.coinbase.com/x402/network-support), Coinbase Developer Platform, accessed 2026-07-06
- [x402 Bazaar](https://docs.cdp.coinbase.com/x402/bazaar), Coinbase Developer Platform, accessed 2026-07-06
- [HTTP 402](https://docs.x402.org/core-concepts/http-402), x402 Docs, accessed 2026-07-06
- [Networks & Token Support](https://docs.x402.org/core-concepts/network-and-token-support), x402 Docs, accessed 2026-07-06
- [Introducing x402 V2](https://www.x402.org/writing/x402-v2-launch), x402 Blog, 2025-12-11
- [Introducing Agentic Wallets](https://www.coinbase.com/developer-platform/discover/launches/agentic-wallets), Coinbase Developer Platform, 2026-02-11
- [Launching the x402 Foundation with Coinbase](https://blog.cloudflare.com/x402/), Cloudflare Blog, 2025-09-23
- [Announcing Agent Payments Protocol](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol), Google Cloud
- [Five Attacks on x402 Agentic Payment Protocol](https://arxiv.org/abs/2605.11781), arXiv
- [x402 Explained: Security Risks & Controls](https://www.halborn.com/blog/post/x402-explained-security-risks-and-controls-for-http-402-micropayments), Halborn
- [Agentic Commerce Impact Could Reach $385 Billion by 2030](https://www.morganstanley.com/insights/articles/agentic-commerce-market-impact-outlook), Morgan Stanley
- [2030 Forecast: How Agentic AI Will Reshape US Retail](https://www.bain.com/insights/2030-forecast-how-agentic-ai-will-reshape-us-retail-snap-chart/), Bain & Company
- [Coinbase highlights Korea's potential as Kakao Pay enters its agentic payment alliance](https://www.koreatimes.co.kr/economy/cryptocurrency/20260416/coinbase-highlights-koreas-potential-as-kakao-pay-enters-its-agentic-payment-alliance), The Korea Times
