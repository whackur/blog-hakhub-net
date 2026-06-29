---
title: "Figure: From HELOC Lender to Blockchain-Native Capital Markets"
meta_title: ""
description: "Figure Technology Solutions started as a consumer HELOC lender and has since built a blockchain-native capital markets platform on Provenance Blockchain, integrating loan origination, the DART ownership registry, tokenized lending markets, and the YLDS yield-bearing security."
date: 2026-06-30T07:00:00+09:00
lastmod: 2026-06-30T07:00:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["rwa", "provenance", "capital-markets", "tokenization", "heloc", "ylds"]
author: "hakhub"
translationKey: "figure-blockchain-capital-markets"
draft: true
---

Two companies go by the name Figure. One is Figure AI, the humanoid robotics company. The other is [Figure Technology Solutions](https://www.figure.com/), which is what this post is about. They are unrelated.

Figure Technology Solutions started as a consumer home equity lender and has built out a system that connects loan origination, on-chain ownership recording, a tokenized loan marketplace, and a yield-bearing settlement asset into one platform, all running on Provenance Blockchain. The company trades on Nasdaq as FIGR.

## The Closed-Loop Thesis

"Putting RWA on a blockchain" undersells what Figure is building. The actual thesis, as stated in its [Investor Relations materials](https://investors.figure.com/investor-relations), is a "blockchain-native capital marketplace for the origination, funding, sale and trading of on-chain loan products and tokenized assets."

The important detail: Figure is not tokenizing assets that were created somewhere else. It originates loans directly onto Provenance Blockchain, then connects those loans to an ownership registry, a trading marketplace, and a yield-bearing cash instrument. The pipeline is closed-loop from the start.

## The System Components

### HELOC and Loan Origination

Figure's consumer product is a HELOC (Home Equity Line of Credit). The official site advertises five-minute approvals, funding in as little as five days, and loans up to $750,000. These loans are the source assets for the tokenized pipeline that follows: DART registration, marketplace trading, and securitization.

The Loan Origination System (LOS) automates application processing, underwriting, valuation, lien verification, income checks, and remote closing. Figure says AI partnerships have cut document processing costs and improved partner onboarding, though these are company-reported figures without independent verification.

### DART: On-Chain Ownership Registry

DART (Digital Asset Registry Technology) records loan ownership and liens on Provenance Blockchain. [Provenance's official site](https://provenance.io/) describes it as "the first blockchain-based system for real-time loan ownership updates" and notes ESIGN/UETA compliance.

DART handles ownership transfers, lien and collateral management, eNote and servicer connections, and the link between tokenized loans and their legal ownership records.

One caveat: ESIGN/UETA compliance means the electronic records meet federal electronic-signature law standards. It does not automatically mean the same legal effect as traditional MERS-based recording in every state. Jurisdiction-by-jurisdiction analysis of lien perfection still matters.

### Provenance Blockchain

Provenance is a proof-of-stake blockchain designed for financial products. [Figure's major systems](https://provenance.io/) use Provenance as the record, settlement, and tokenization layer. Sensitive personal information like borrower PII is not posted on-chain directly.

### Figure Connect: Consumer Loan Marketplace

Figure Connect connects loan originators with capital buyers for HELOC, DSCR, and personal loan assets. Per [Figure's Q1 2026 results](https://investors.figure.com/investor-relations), Figure Connect volume was $1.6B in the quarter, representing 56% of the total Consumer Loan Marketplace volume of $2.9B.

### YLDS: A Registered Fixed-Income Security

YLDS transfers and settles like a stablecoin, but [its official site](https://www.ylds.com/) is explicit: it is "a registered fixed-income security, not a stablecoin."

Key details: issued by Figure Certificate Company, registered with the SEC as a fixed-income security under the Investment Company Act, with 1 YLDS = 1 Certificate = $0.01 NAV. It accrues a variable yield based on SOFR minus 35bps, credited daily. It supports peer-to-peer on-chain transfer and 24/7 settlement across Provenance, Solana, and Stellar. A Big Four audit is mentioned. As of May 2026, $557M in YLDS was in circulation.

In practice, YLDS functions as a regulated yield-bearing cash instrument inside the Figure ecosystem: idle capital, lender supply, settlement asset, or treasury holding. The security classification, not stablecoin classification, is the key legal point.

### Democratized Prime: On-Chain Lending Market

Democratized Prime is Figure Markets' on-chain lending marketplace. Lenders can supply cash or crypto; borrowers access funds through RWA-backed pools, crypto-collateralized loans, and HELOC-backed structures. May 2026 figures from Figure IR: Matched Offers Balance $385M, Borrower Demand $412M, Available Lender Supply $500M.

## Public Metrics Summary

From [Figure's IR page](https://investors.figure.com/investor-relations), reported figures as of Q1/May 2026:

- May 2026 Consumer Loan Marketplace Volume: $1,402M
- Q1 2026 Consumer Loan Marketplace Volume: $2.9B
- Q1 2026 Figure Connect Volume: $1.6B
- Q1 2026 Net Revenue: $167M; Net Income: $45M; Adjusted EBITDA: $83M

Some commonly cited claims require independent verification: "#1 non-bank HELOC lender," "75% RWA tokenization market share," "$130B+ revenue opportunity," and details around AAA-rated blockchain-native securitization methodology.

## Risks Worth Tracking

**Regulatory.** YLDS is structured as a registered security, not a stablecoin. US digital asset legislation could affect its positioning. **Legal.** DART registry lien perfection in each state requires separate legal analysis. **Credit.** HELOC, DSCR, and crypto-backed loans all carry exposure to real estate prices, interest rates, and collateral volatility. **Vertical integration.** Origination, registry, marketplace, lending pools, and settlement assets all sit inside one ecosystem, which raises conflict-of-interest and governance questions. **On-chain verification scope.** Figure uses blockchain throughout its operations, but the boundary between what is publicly verifiable on-chain and what relies on off-chain legal process trust is not always obvious from public materials.

## Further Reading

- [Provenance Blockchain](https://provenance.io/) — Figure's record, settlement, and tokenization rail
- [DART](https://dartinc.io/) — on-chain loan ownership and lien registry
- [YLDS](https://www.ylds.com/) — SEC-registered yield-bearing security
- [Figure Markets](https://www.figuremarkets.com/) — exchange, Democratized Prime, HASH

## References

- [Figure Official Site](https://www.figure.com/) — figure.com, accessed 2026-06-30
- [Figure Investor Relations](https://investors.figure.com/investor-relations) — accessed 2026-06-30
- [SEC Prospectus](https://www.sec.gov/Archives/edgar/data/2064124/000206412425000013/figuretechnologysolutionsi.htm) — 2025 IPO filing, accessed 2026-06-30
- [Figure Markets](https://www.figuremarkets.com/) — accessed 2026-06-30
- [Provenance Blockchain](https://provenance.io/) — accessed 2026-06-30
- [DART](https://dartinc.io/) — accessed 2026-06-30
- [YLDS](https://www.ylds.com/) — accessed 2026-06-30
