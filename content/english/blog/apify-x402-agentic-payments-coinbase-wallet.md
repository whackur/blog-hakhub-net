---
title: "Apify x402 and Coinbase Wallets: How Agents Buy Web Automation Tools Directly"
meta_title: ""
description: "Apify opened more than 20,000 Actors to x402 payments. A walkthrough of the HTTP 402 flow, the Coinbase Agentic Wallet (awal) versus an exchange account, prepaid USDC tokens on Base, seller KYC and payouts, and where country-level constraints actually sit."
date: 2026-07-05T01:10:00+09:00
lastmod: 2026-07-05T01:10:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["x402", "agentic-payments", "apify", "coinbase", "ai-agent", "usdc", "base"]
author: "whackur"
translationKey: "apify-x402-agentic-payments-coinbase-wallet"
draft: false
---

Apify, the web scraping platform, [announced x402 support](https://blog.apify.com/introducing-x402-agentic-payments/): AI agents can now run more than 20,000 Apify Actors by paying with USDC on Base, with no Apify account and no API key. Apify frames the prior x402 ecosystem as roughly 2,000 endpoints, so by its own accounting this single integration grew the paid-tool surface about tenfold.

The structural change matters more than the number. A web automation marketplace that used to require a human to sign up and register a payment method has become a tool supply layer that agents can discover and purchase from at runtime. What decides whether teams actually adopt it, though, is mostly not the protocol. It is wallet funding, spending limits, seller KYC, payout rails, and which of those layers gets awkward in your country. This post walks through each of them, sticking to what the official docs say.

## Apify Actors as a tool supply chain for agents

Apify runs web scraping and browser automation in the cloud. The unit of execution is an Actor, a serverless program, and developers can publish Actors to [Apify Store](https://docs.apify.com/platform/actors/publishing/monetize) as paid products. Search result collectors, social media crawlers, and site monitors are already listed there for sale.

Until now the customer was a person: create an account, add a card or credits, get an API token, call the API. The x402 integration changes that assumption. Per the [Apify announcement](https://blog.apify.com/introducing-x402-agentic-payments/), an agent browsing Actor metadata over the Model Context Protocol (MCP) can detect a payment requirement in the response, authorize the payment from its wallet, and retry automatically. Discovery, payment, and execution happen without a human in the loop. Apify also added x402 support to `mcpc`, its universal CLI client for MCP.

From the agent's side, the list of usable tools is no longer frozen at deploy time. It can find the scraper it needs and buy a dollar's worth of it on the spot.

## x402 revives HTTP 402 as a payment flow

HTTP 402 Payment Required has been a reserved status code since HTTP/1.1, sitting unused. x402 puts it to work. According to the [Coinbase Developer Platform docs](https://docs.cdp.coinbase.com/x402/welcome), x402 was originally built by Coinbase and is now an open source protocol governed under the Linux Foundation. It handles stablecoin payments over plain HTTP, with no accounts, sessions, or bespoke authentication.

The flow is short. A client requests a paid resource and the server replies with 402 plus the payment terms: chain, token, amount, supported schemes. The wallet signs a USDC transfer off-chain, and the client retries with the payment payload in a `PAYMENT-SIGNATURE` header. The server verifies the signature and settles on-chain through an intermediary called a facilitator, then returns the resource. In [Apify's example challenge](https://blog.apify.com/introducing-x402-agentic-payments/), the network is the CAIP-2 identifier `eip155:8453` (Base mainnet), the token is USDC with 6 decimals, and an amount of `1000000` equals one dollar.

Two settlement schemes cover most cases. `exact` is fixed-price and can pair with a prepaid deposit-and-refund pattern. `upto` arrived in x402 v2: the client authorizes a maximum and the service charges only actual cost up to that ceiling, which fits Actors whose cost is unknown until the run finishes. The [seller quickstart](https://docs.x402.org/getting-started/quickstart-for-sellers) lists a third, `batch-settlement`.

The protocol is not tied to one chain. The [Apify docs](https://docs.apify.com/platform/integrations/x402) describe it as supporting EVM-compatible chains and Solana, and the CDP facilitator settles ERC-20 payments on Base, Polygon, Arbitrum, World, and Solana. Apify's actual combination is just one of those: USDC on Base. For scale context, [x402.org](https://www.x402.org/) displayed 75.41M cumulative transactions and $24.24M in volume when checked on July 5, 2026. Those figures move constantly, so treat them as a snapshot.

## Buyers choose between an Apify account and a wallet

There are now two ways to pay for an Actor.

The first is the existing path: an Apify account, a card or credits, and an API token. If a human manages the workflow, or the team already uses Apify, nothing needs to change. Even after the x402 integration, [a client can send an Apify token instead of a payment signature](https://blog.apify.com/introducing-x402-agentic-payments/) and pay from the account balance.

The second is the x402 wallet path. The [Apify x402 docs](https://docs.apify.com/platform/integrations/x402) list four prerequisites: the Coinbase Agentic Wallet (`awal`) CLI, at least $1 of USDC on Base mainnet, a tiny amount of Base ETH (around 0.000001 ETH) for the one-time gas cost of deploying the wallet, and an email address to authenticate it. Authentication uses an email OTP, so a fully autonomous agent needs the ability to read its inbox to fetch the verification code. No Apify account is involved.

What you actually end up holding on this path is a prepaid token. Buying balance from Apify's agentic endpoint with USDC returns a token tied to that balance, and it behaves like an API token for as long as the balance lasts. A few conditions apply: the minimum transaction is $1, the token balance is an absolute spending cap, the token expires 14 days after purchase, and unused balance is not refunded. Apify marks the whole feature as experimental.

Not every Actor is reachable this way either. Only Actors using Pay Per Event pricing, running with limited permissions, and not using Standby mode qualify for now.

## The Coinbase wallet is a convenience, not a requirement

The Coinbase name is the easiest place to get confused. `awal` is not a Coinbase exchange account. Per the [Agentic Wallet CLI docs](https://docs.cdp.coinbase.com/agentic-wallet/cli/welcome), it is a standalone wallet for AI agents. The agent authenticates by email OTP and can hold, send, and spend USDC, but it never touches private keys. Keys stay inside Coinbase infrastructure, and the wallet layer enforces spending limits plus KYT transaction screening and OFAC sanctions screening. Supported networks are Base, Base Sepolia, Polygon, Solana, and Solana Devnet.

Where the money lives is the point. The [Apify docs](https://docs.apify.com/platform/integrations/x402) state that funds sit in the wallet itself, not in a Coinbase exchange account, and can come from any source able to send USDC on Base. Withdraw from an exchange, transfer from another wallet, or use an onramp; the protocol does not care. What x402 requires at the protocol level is a funded wallet that speaks a supported asset and network, not a Coinbase exchange signup. `awal` is simply the easiest route Apify currently documents, and the standard itself is wider than that one tool.

The convenience is real, to be fair. It reads the 402 challenge and handles signing on its own, which is why Apify says it works best in coding-agent runtimes that can execute shell commands and keep local state.

## Country constraints live in the layers around the protocol

x402 itself has no country lock. [x402.org](https://www.x402.org/) presents it as an open standard that works without account setup or personal information. That does not mean it works everywhere without friction. The constraints sit in three layers around the protocol, and they fail independently.

First, the seller layer. Apify Technologies is registered in Prague, Czech Republic, and under the [Store publishing terms](https://docs.apify.com/legal/store-publishing-terms-and-conditions), receiving revenue requires being over 18 and passing identity verification and KYC. That can extend to government ID, proof of address, tax documentation, and beneficial ownership information. Sanctions or watchlist hits can suspend payouts or terminate the account. Nothing in the official documents reviewed for this post says only U.S. persons can publish or sell. A developer in Korea, or most other countries, should expect ID, billing, tax, and payout verification rather than any U.S. residency requirement, though payout-method availability and sanctions screening can still play out differently by country.

Second, the buyer funding layer. Coinbase's exchange, onramp, and hosted wallet products vary in availability by country. If a particular Coinbase product is unavailable where you are, that does not by itself make x402 impossible, because the protocol needs a wallet that can send USDC on Base and there is more than one way to fund one. Still, if production plans depend on `awal` specifically, check its availability in your jurisdiction and whether the email OTP step can be automated before committing.

Third, local law. How you acquire stablecoins, how you handle tax, and whether what the Actor does is legal (target-site terms of service, privacy and data law) all differ by country, and neither Apify nor Coinbase decides that for you. The CDP facilitator roadmap mentions optional seller attestations for KYC or geographic restrictions, but that is a roadmap item. Current x402 does not resolve legal constraints at the protocol level.

The summary: selling runs through Apify's KYC and payout rules, buyer funding runs through wallet and onramp availability in your country, and usage runs through local law. Check the three layers separately. One being blocked does not automatically block the others.

## Sellers go through Apify monetization and KYC

There is no separate "seller account." A regular Apify account with [monetization configured](https://docs.apify.com/platform/actors/publishing/monetize) is the whole setup: enter billing details in the Console and pick a pricing model under the Actor's Publication settings. Current pricing models are Pay Per Event, billed per defined event, and Pay Per Usage.

Revenue share is [80% of fees](https://docs.apify.com/legal/store-publishing-terms-and-conditions) for supported pricing models, potentially reduced by platform usage costs depending on configuration. Payouts run [monthly](https://docs.apify.com/platform/actors/publishing/monetize/monthly-payouts): invoices are generated on the 11th, sellers get 3 days to review, and no action means auto-approval on the 14th. Minimum thresholds are $20 for PayPal and Wise and $100 for other payout methods. If a Pay Per Event Actor's monthly profit goes negative, it is floored at $0 so one Actor's loss does not eat into the rest of the payout.

Getting paid requires passing AML/KYC. Individuals submit a legal full name matching their ID and a high-resolution photo of an ID card or driver's license; companies submit their official name and registration details. If verification is not complete when the month's payout is issued, earnings roll over. KYC is ongoing rather than one-time, and the terms allow forfeiture of accrued unpaid balance if verification stays unresolved for 12 continuous months.

Exposure to agentic buyers uses the conditions mentioned earlier: Pay Per Event pricing, limited permissions, no Standby mode. Qualifying Actors get flagged `allowsAgenticUsers=true` and surface in agentic discovery automatically, with no separate opt-in. The Store API supports searching on that flag too.

Put end to end: money a buyer pays through x402 still reaches the seller through Apify's normal payout flow. The payment being on-chain does not make the payout on-chain.

## Policies to set before production

Having the protocol and a wallet working is not the same as being ready to run this. A few decisions belong to the operator, not the tooling.

- Keep wallet balances small. The prepaid token's balance is a hard cap and `awal` has spending limits, but the actual ceiling is a policy you choose. Given the 14-day expiry and no refunds, fund only what you expect to spend.
- Treat the prepaid token exactly like an API key. While balance remains it is spendable by anyone holding it, so keep it out of logs and terminal output and control where it is stored.
- Decide which Actors the agent is allowed to call. `upto` and prepaid caps limit the damage of a single call, but an allowlist of tools and a spend ceiling per task are policy questions the protocol cannot answer.
- Assess scraping risk per Actor. Buying the tool legally does not make the data it collects legal; target-site terms and local data law still apply. Actor authors, for their part, should document limitations and avoid implying official affiliation with the services they scrape.
- If the agent runs unattended, design for the email OTP. The `awal` verification code arrives by email, so inbox access becomes part of the automation path, and that access is itself a new security surface.

## Wrap-up

Apify's x402 integration moves agentic payments from demos to product scale. More than 20,000 Actors reachable with nothing but a funded wallet means an agent's tool list is decided at runtime rather than deploy time, and that is now true of a real marketplace rather than a proof of concept.

It also shows exactly where the friction remains. The payment protocol has no borders; wallet products, onramps, seller KYC, tax, and scraping law all do. Two common assumptions fail against the docs: a Coinbase exchange account is not required for the x402 path, and nothing published says Apify selling is restricted to any single country. What replaces those assumptions is layer-by-layer homework: how to fund a wallet where you live, how to pass payout verification, and whether the data your Actors touch is legal to collect. Add Apify's own experimental label on the feature, and starting with small balances and a narrow allowlist looks like the sensible opening move.

## Further reading

- [x402 quickstart for sellers](https://docs.x402.org/getting-started/quickstart-for-sellers): SDKs and schemes for exposing your own paid API
- [Coinbase Developer Platform x402 docs](https://docs.cdp.coinbase.com/x402/welcome): protocol structure, facilitator, supported networks
- [Agentic payments, June 2026](/en/blog/agentic-payments-june-2026-x402-ucp-mpp/): recent changes across the wider payment stack including x402

## References

- [Introducing x402 support: 10x more tools for autonomous agents](https://blog.apify.com/introducing-x402-agentic-payments/), Apify Blog, accessed 2026-07-05
- [Apify x402 integration docs](https://docs.apify.com/platform/integrations/x402), Apify Docs, accessed 2026-07-05
- [x402 welcome](https://docs.cdp.coinbase.com/x402/welcome), Coinbase Developer Platform, accessed 2026-07-05
- [Agentic Wallet CLI](https://docs.cdp.coinbase.com/agentic-wallet/cli/welcome), Coinbase Developer Platform, accessed 2026-07-05
- [x402.org](https://www.x402.org/), x402 project home, accessed 2026-07-05
- [Quickstart for sellers](https://docs.x402.org/getting-started/quickstart-for-sellers), x402 Docs, accessed 2026-07-05
- [Monetize your Actor](https://docs.apify.com/platform/actors/publishing/monetize), Apify Docs, accessed 2026-07-05
- [Monthly payouts](https://docs.apify.com/platform/actors/publishing/monetize/monthly-payouts), Apify Docs, accessed 2026-07-05
- [Apify Store Publishing Terms and Conditions](https://docs.apify.com/legal/store-publishing-terms-and-conditions), Apify Legal, accessed 2026-07-05
