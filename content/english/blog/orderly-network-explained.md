---
title: "What Is Orderly? Shared Perpetual Futures Infrastructure for DEXs"
meta_title: ""
description: "How Orderly's shared orderbook, execution and settlement work, how builders and ORDER holders earn, and where it fits in the onchain perpetuals market."
date: 2026-11-17T02:34:00Z
lastmod: 2026-11-17T02:34:00Z
image: "/images/posts/orderly-network-explained/cover.webp"
categories: ["Blockchain"]
tags: ["orderly", "perpetuals", "defi", "orderbook", "trading-infrastructure"]
author: "whackur"
translationKey: "orderly-network-explained"
draft: false
---

Orderly provides **perpetual futures trading infrastructure** for teams building their own trading applications. Builders own the interface and customer relationship; Orderly supplies the backend for execution and settlement. In its standard markets, orders arriving through different applications and supported chains access shared liquidity. A DEX can have its own name while Orderly processes its trades behind the scenes. This is the business model described in the [official introduction](https://orderly.network/docs/introduction/getting-started/what-is-orderly).

The arrangement addresses a problem every new venue faces: building a trading screen is different from building a market with enough buyers and sellers. Teams using Orderly can avoid running their own matching engine and bootstrapping liquidity for standard markets, then focus on the trading experience for their customers. Applications also share operational and security dependencies on the common backend.

## Perpetual futures and the application's role

Perpetual futures are derivatives without an expiry date. Traders take exposure to price changes rather than directly owning the underlying asset, and maintain positions with margin. Funding payments between longs and shorts help keep the contract price near its underlying reference price. Funding is separate from exchange trading fees. Leverage allows a large position against a smaller amount of collateral, but losses can trigger liquidation. [Orderly's funding documentation](https://orderly.network/docs/introduction/trade-on-orderly/perpetual-futures/funding-rate) explains how the difference between trading and reference prices enters the funding calculation.

Offering this product requires order management, matching, margin calculations, liquidations, and deposits and withdrawals. Orderly exposes these common functions through APIs and SDKs. Teams can use REST and WebSocket APIs or the React SDK for custom development, or choose Orderly One for a faster launch. Builders choose their branding, interface, and user fee policy. The [official homepage](https://orderly.network/) lists Raydium, WOOFi Pro, and BTSE DEX among ecosystem examples. Inclusion on that page does not independently establish an application's current activity or quality.

## Shared orderbooks and onchain settlement are separate stages

Orderly uses a central limit order book (CLOB). Buy and sell orders sit at specified prices until compatible orders match. For the same standard market, orders from different builders and supported chains enter a common book. Customers of different applications can trade against one another, reducing the need for every application to source liquidity independently. The [orderbook design documentation](https://orderly.network/docs/introduction/trade-on-orderly/trading-basics/orderbook-design) describes this as liquidity unification across chains.

The order flow has four main steps:

1. A user submits an order through an application, which forwards a signed request to Orderly.
2. The infrastructure verifies the signature, and an offchain engine matches orders using price-time priority.
3. The user receives order and execution updates.
4. Matched trade data is batched and recorded in the settlement layer on Orderly L2.

An execution update on screen and completed blockchain settlement therefore occur at different points. Unfilled and canceled orders are not all included in settlement batches. According to the [order lifecycle documentation](https://orderly.network/docs/build-on-omnichain/user-flows/order-management), these batches contain matched trade data.

Asset location is another distinction. Asset Vaults on supported chains hold deposited funds, while a separate settlement layer maintains the trading ledger. LayerZero carries cross-chain messages for deposits, withdrawals, and balance updates. Users access applications from supported chains while connecting to the common trading and settlement system underneath. The official list includes EVM chains such as Ethereum, Arbitrum, and Base, as well as Solana. Each application's supported chains and collateral still need to be checked separately. [Architecture](https://orderly.network/docs/build-on-omnichain/building-on-omnichain), [supported chains](https://orderly.network/docs/introduction/trade-on-orderly/supported-chains)

## Benefits for builders and traders

Builders can reduce the work required to develop and operate a trading product. A wallet or community application adding perpetuals does not need to build a matching engine first. Access to standard markets leaves room to differentiate through the interface, trading tools, customer support, and distribution. Acquiring customers and running the product remain the builder's responsibilities even when Orderly supplies its backend. [Official introduction](https://orderly.network/docs/introduction/getting-started/what-is-orderly)

For traders, the benefit is access to orders from other applications while using a familiar interface and supported chain. Pooling orders can reduce liquidity fragmentation. Actual spreads and slippage still depend on the market, order size, and market makers' available quotes. A shared orderbook alone does not guarantee a good execution price for every order.

**Shared liquidity has an important boundary.** Perp Anything lets builders operate separate perpetual markets. Even for the same underlying asset, standard and builder-operated markets have separate symbols, books, liquidity, and risk parameters. Community Listed markets use isolated margin only, and their liquidity depends on the builder's market-making arrangements. Insurance is separated by builder-assigned fund accounts; markets assigned to the same account share its available coverage. Listing on Orderly therefore does not imply the same depth or protection as a standard market. The [Perp Anything documentation](https://orderly.network/docs/build-on-omnichain/perp-anything/introduction) explicitly says Orderly does not operate or backstop these markets.

The product range also extends beyond perpetuals. Official documentation describes Orderly Predict, with round-based UP and DOWN trading. Its structure differs from an open-ended futures position and should be understood as a separate product. [Orderly Predict overview](https://orderly.network/docs/introduction/trade-on-orderly/orderly-predict/overview)

## Trading fees and the ORDER token

Orderly's business revenue, a builder's revenue, and a token holder's rewards are separate flows. On an ordinary taker trade, Orderly retains a base fee, while the builder keeps the positive difference between that base and the fee charged to the user. A positive maker fee can become builder revenue. A negative maker fee is a rebate passed to the trader and should not be counted as builder income. [Custom fee documentation](https://orderly.network/docs/build-on-omnichain/user-flows/custom-fees)

ORDER connects staking, ecosystem rewards, and governance participation. Its documented maximum supply is one billion tokens. The network having a native token does not mean every deposit or withdrawal pays gas in ORDER. Trading and funding infrastructure should be considered separately from the token's reward design. [Token overview](https://orderly.network/docs/introduction/tokenomics/overview-of-order), [distribution and emission schedule](https://orderly.network/docs/introduction/tokenomics/distribution-and-emission-schedule)

The current rewards system should also be distinguished from the older USDC distribution model. Official staking documentation says the system introduced on November 4, 2025 allocates 30% of net fees to the new treasury pool, settled through an ORDER buyback at epoch end. Staking ORDER or esORDER accrues VALOR, a nontransferable measure of the amount and duration staked, which can be redeemed for esORDER rewards. The legacy USDC pool receives no new revenue. [Staking documentation](https://orderly.network/docs/introduction/tokenomics/order-staking/staking)

The separate [buyback announcement](https://orderly.network/blog/buybacks) describes purchases every two weeks using **up to 60%** of net fees. Half of the purchased tokens go to stakers as esORDER, and half go to a community-governed wallet. Tokens sent to that wallet are not all automatically burned. Converting esORDER into liquid ORDER requires vesting; the documentation specifies 90 days for full conversion. [esORDER documentation](https://orderly.network/docs/introduction/tokenomics/esorder)

A funded buyback mechanism does not guarantee a rising token price. Outcomes also depend on how much trading activity becomes net fees, how rewards are distributed, and how circulating supply changes. Higher turnover cannot be treated as a guaranteed return to token holders.

## Position in the onchain perpetuals market

Orderly focuses on helping builders serve trading customers across multiple chains. Its competition includes other perpetual venues and the tools those venues offer external applications to access liquidity.

| Service     | Structure and focus                                                             | Relevant comparison with Orderly                                                         |
| ----------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Orderly     | Trading backend and shared standard-market orderbooks for multiple applications | Builder control over branding and fees; deposits and withdrawals across supported chains |
| Hyperliquid | HyperCore orderbooks and HyperEVM on its own L1                                 | Liquidity within its trading ecosystem and builder codes for external applications       |
| Lighter     | Emphasizes proofs of exchange operations and Ethereum settlement and exits      | Verification of matching and liquidation; operator dependencies                          |
| dYdX Chain  | Cosmos SDK chain with validators maintaining orderbooks                         | Validator-based order propagation and execution                                          |

These descriptions follow [Hyperliquid's introduction](https://hyperliquid.gitbook.io/hyperliquid-docs), [builder codes](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/builder-codes), [Lighter's architecture](https://docs.lighter.xyz/about-lighter/technical-architecture-lighter-core), and [dYdX's architecture](https://docs.dydx.xyz/concepts/architecture/overview). Hyperliquid also allows external applications to send orders and receive fees, so supporting builders is not exclusive to Orderly.

Drift, a familiar comparison in Solana perpetuals, requires attention to source dates. On November 17, 2026, the [existing Drift documentation address](https://docs.drift.trade/) describes a perpetuals and lending protocol branded Velocity. It combines collateral and lending within one Solana program, a different product configuration from Orderly's multichain trading backend. Historical Drift architecture and metrics should not be assumed to describe its current state.

### Scale through a common fee window

The following figures sum daily observations from DeFiLlama's public API. The window is **November 10 to 16, 2026 UTC**, seven complete days, in USD. Data was retrieved at approximately **02:32 UTC on November 17, 2026**.

| DeFiLlama series  | Seven-day fees |
| ----------------- | -------------: |
| Orderly Perps     |        $35,634 |
| Hyperliquid Perps |    $24,642,335 |
| Lighter Perps     |     $1,474,048 |
| dYdX V4           |        $61,098 |

Sources: [Orderly Perps API](https://api.llama.fi/summary/fees/orderly-perps?dataType=dailyFees), [Hyperliquid Perps API](https://api.llama.fi/summary/fees/hyperliquid-perps?dataType=dailyFees), [Lighter Perps API](https://api.llama.fi/summary/fees/lighter-perps?dataType=dailyFees), and [dYdX V4 API](https://api.llama.fi/summary/fees/dydx-v4?dataType=dailyFees). The Hyperliquid series includes stablecoin reserve-yield allocations alongside crypto and HIP-3 perpetual trading fees and builder fees. The populations therefore differ despite the common window. These figures provide context on revenue-generating activity; they are neither a pure trading-fee comparison nor market shares.

Orderly's observed fees are smaller than Hyperliquid's and Lighter's in this window. That alone does not establish that shared infrastructure has failed or tell us the quality of any application. Free trading policies, rebates, and product mix change the relationship between fees and volume. Orderly's approach brings applications' trading activity to a common backend; actual liquidity and customer retention are needed to judge how well that approach works.

Trading volume measures contract notional traded during a period. Open interest (OI) measures outstanding positions, while total value locked (TVL) measures deposited or locked assets. None is interchangeable with fees. Adding the volume of Orderly-powered frontends to Orderly's aggregate volume can count the same trades twice. The table excludes downstream applications and chain gas-fee series.

## Noncustodial design still has operator and bridge risks

Offchain matching supports fast responses, but Orderly's operating infrastructure can see and process full orders. The documentation's MEV protection is specifically about pre-match front-running through a public blockchain mempool. It does not mean orders are hidden from the operator or that every form of MEV disappears. [Orderbook design documentation](https://orderly.network/docs/introduction/trade-on-orderly/trading-basics/orderbook-design)

Holding funds in onchain Vaults does not establish an always-available withdrawal path independent of operators. The standard withdrawal flow includes wallet authorization, API processing, and cross-chain messaging. The [withdrawal documentation](https://orderly.network/docs/build-on-omnichain/user-flows/withdrawal-deposit) and [security documentation](https://orderly.network/docs/introduction/security) make the funding path and multisig upgrade authority relevant to assessing risk. Audit history is useful evidence, rather than a guarantee against outages or losses.

The settlement layer also needs a separate assessment. [L2BEAT's Orderly evaluation](https://l2beat.com/scaling/projects/orderly) flags permissioned state updates, immediate upgrades, and frozen withdrawals if the proposer fails. It classifies data availability as external, using Celestia. The official orderbook documentation linked above instead describes publishing batch data to Ethereum. This discrepancy does not establish the actual deployed configuration, so Ethereum's security should not be assumed to apply unchanged to every trade and withdrawal.

Shared infrastructure reduces the cost of implementing the same functions for each builder. A failure in a common engine or messaging path can also affect multiple applications. Understanding an Orderly-powered product requires looking beyond its interface brand to its orderbook, settlement system, and asset custody path.

## Further reading

- [Orderly builder onboarding](https://orderly.network/docs/introduction/getting-started/builder-onboarding): Operator registration and integration options.
- [Perp Anything](https://orderly.network/docs/build-on-omnichain/perp-anything/introduction): Responsibility and risk boundaries between standard and builder-operated markets.
- [Lighter architecture](https://docs.lighter.xyz/about-lighter/technical-architecture-lighter-core): An alternative design centered on proofs and emergency exits.

## References

Sources checked on November 17, 2026. Documented capabilities can differ from what an individual application exposes.

- [Orderly homepage](https://orderly.network/), [introduction](https://orderly.network/docs/introduction/getting-started/what-is-orderly), [architecture](https://orderly.network/docs/build-on-omnichain/building-on-omnichain), [supported chains](https://orderly.network/docs/introduction/trade-on-orderly/supported-chains).
- [Orderbook design](https://orderly.network/docs/introduction/trade-on-orderly/trading-basics/orderbook-design), [order lifecycle](https://orderly.network/docs/build-on-omnichain/user-flows/order-management), [deposits and withdrawals](https://orderly.network/docs/build-on-omnichain/user-flows/withdrawal-deposit), [security](https://orderly.network/docs/introduction/security), [funding](https://orderly.network/docs/introduction/trade-on-orderly/perpetual-futures/funding-rate).
- [Custom fees](https://orderly.network/docs/build-on-omnichain/user-flows/custom-fees), [ORDER overview](https://orderly.network/docs/introduction/tokenomics/overview-of-order), [distribution and emissions](https://orderly.network/docs/introduction/tokenomics/distribution-and-emission-schedule), [staking](https://orderly.network/docs/introduction/tokenomics/order-staking/staking), [esORDER](https://orderly.network/docs/introduction/tokenomics/esorder), [buyback announcement](https://orderly.network/blog/buybacks).
- [Perp Anything](https://orderly.network/docs/build-on-omnichain/perp-anything/introduction), [Orderly Predict](https://orderly.network/docs/introduction/trade-on-orderly/orderly-predict/overview), [L2BEAT](https://l2beat.com/scaling/projects/orderly).
- [Hyperliquid](https://hyperliquid.gitbook.io/hyperliquid-docs), [builder codes](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/builder-codes), [Lighter](https://docs.lighter.xyz/about-lighter/technical-architecture-lighter-core), [dYdX](https://docs.dydx.xyz/concepts/architecture/overview), [current content at the Drift documentation address](https://docs.drift.trade/).
- DeFiLlama public fee APIs: [Orderly](https://api.llama.fi/summary/fees/orderly-perps?dataType=dailyFees), [Hyperliquid](https://api.llama.fi/summary/fees/hyperliquid-perps?dataType=dailyFees), [Lighter](https://api.llama.fi/summary/fees/lighter-perps?dataType=dailyFees), [dYdX](https://api.llama.fi/summary/fees/dydx-v4?dataType=dailyFees).
