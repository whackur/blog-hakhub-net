---
title: "Data Enclosure and Platform Concentration in the AI Era"
meta_title: ""
description: "Naver, Reddit, X and Cloudflare show how API termination, purpose restrictions, selective agreements and usage pricing can shape AI competition."
date: 2026-10-15T16:00:00+09:00
lastmod: 2026-10-15T20:23:51+09:00
image: "/images/posts/ai-data-enclosure-platform-monopolization/platform-archives-selective-access-editorial.webp"
categories: ["AI"]
tags: ["data-enclosure", "platforms", "competition", "data-licensing", "ai-search", "commerce"]
author: "whackur"
translationKey: "ai-data-enclosure-platform-monopolization"
draft: false
---

**Data enclosure in the AI era is about platforms deciding who may reuse data, and for what purpose.** Some end APIs; others supply selected AI companies under contract or charge for usage. These cases show access conditions being reorganized. They do not, by themselves, establish monopoly or unlawful conduct by any company.

| Case | Documented action | Key distinction |
| --- | --- | --- |
| [Naver](https://developers.naver.com/notice/article/32564) | Ended Shopping, Book and Professional Document Search APIs on July 31, 2026 | This did not end every shopping-related API |
| [Reddit](https://redditinc.com/news/reddit-and-google-expand-partnership) | Contract-based data provision to Google and other partners | A partnership does not give every developer the same rights |
| [X](https://docs.x.com/x-api/getting-started/pricing) | Operates usage-based API pricing | Access costs and permitted uses are separate |
| [Cloudflare](https://blog.cloudflare.com/pay-per-use/) | Tests payment for downstream use alongside crawl access charges | Pay Per Use is in beta, with buyer-reported usage |

For competition, the central issue is **whether a new entrant can obtain the current data and usage rights it needs on affordable terms**. Permission to display data, train a model, and use it to generate an answer can differ even for the same collection.

## Naver ended Shopping Search while migrating other APIs

Naver's [termination notice](https://developers.naver.com/notice/article/32564) sets July 31, 2026 as the end date for Shopping, Book and Professional Document Search APIs. Its [migration notice](https://developers.naver.com/notice/article/32530) says these three receive no grace period, existing keys cannot call them, and no replacement API is offered, including through NAVER API HUB.

APIs with “shopping” in their names serve different purposes.

| Product | Function | Termination or migration scope |
| --- | --- | --- |
| [Shopping Search](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md) | Product search results for a query | Terminated |
| [Shopping Insight](https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md) | Search click trends by category and keyword | Migrating to API HUB |
| [Commerce API](https://apicenter.commerce.naver.com/docs/commerce-api/current) | Commerce operations including products, orders and settlement | Documented as a separate API |

For the remaining migrating Search APIs, Search Trend and Shopping Insight, new applications through the developer center stopped on July 31, 2026. Existing applications are supported until June 30, 2027. Shopping Insight migration therefore does not replace product search. The notice also cannot establish the status of separate partnership or supply agreements. [Migration notice](https://developers.naver.com/notice/article/32530)

Permitted purposes changed separately. A [Search API terms amendment effective September 7](https://developers.naver.com/notice/article/33400) prohibits using search data as AI input or for training, improvement, evaluation and display. A service that only generates answers, without training a model, still needs to consider the AI-input restriction. There is no basis for automatically extending this clause to API HUB, Commerce API or separate agreements.

The verified domestic case is the loss of a particular product-search route. The termination notice does not identify AI competition as its cause, so it does not establish that Naver closed the API to protect its own AI.

## Reddit defines external provision through approval and partnerships

Reddit's [current Data API Terms](https://redditinc.com/policies/data-api-terms) require a separate agreement for commercial use and certain other uses. They also state that users own their content, and that ordinary API permission does not include model training without express permission from the relevant rightsholders.

There are separate routes for AI companies. The [Google partnership announced February 22, 2024](https://redditinc.com/news/reddit-and-google-expand-partnership) describes structured data access, content display and support for model training. The [OpenAI partnership announced May 16 that year](https://redditinc.com/news/reddit-and-oai-partner) provides real-time Data API content for ChatGPT and other products.

This is provision to defined recipients for defined purposes. The public announcements do not say these deals are exclusive or available to anyone on the same terms. Growth in partnerships and wider access for new entrants need to be assessed separately.

## X attaches a price to access volume

The [X pricing page](https://docs.x.com/x-api/getting-started/pricing), checked October 15, 2026, describes usage-based billing with prepaid credits. Ordinary Post reads cost $0.005 per returned resource; qualifying Owned Reads of the developer's own data cost $0.001. Costs differ according to what is retrieved.

That structure can affect a small reading tool and a large data-collection service differently. Charging is not inherently unfair, but acquisition costs change which products are viable. The [Developer Policy](https://docs.x.com/developer-terms/policy) also requires compliance with approved uses and content-handling rules. Payment alone does not grant every reuse right.

## Cloudflare separates access charges from payment for use

Cloudflare [announced Pay Per Crawl in private beta on July 1, 2025](https://blog.cloudflare.com/introducing-pay-per-crawl/). Site operators can allow or block crawlers, or set a price per request. HTTP 402 can request payment, and the [current documentation](https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/) still labels it beta.

[Pay Per Use, announced September 30, 2026](https://blog.cloudflare.com/pay-per-use/), is a beta that charges for downstream use. An AI company proposes a paid-use definition and price; publishers choose whether to participate. The buyer reports uses, and Cloudflare handles billing and payment. Program terms may include training restrictions.

This could reduce transaction work for publishers unable to negotiate individual deals. Usage, however, is self-reported by the buyer. A beta announcement does not demonstrate adequate compensation or commercial adoption. Charging for access and paying for actual content use still leave different outcomes to verify.

## Four forms of access change

These cases place different conditions on outside services, even when grouped under “data enclosure.”

- **Termination:** an existing retrieval route disappears. APIs serving other purposes do not necessarily replace its function.
- **Purpose restrictions:** retrieval may be allowed while downstream uses such as AI input or training are restricted.
- **Selective agreements:** data is supplied to particular counterparties for specified purposes. Contract scope and entry conditions matter.
- **Usage-based pricing:** costs depend on what is counted, such as returned data, crawl requests or downstream uses.

These forms can overlap. A paid API may still exclude the AI use a product needs; a discontinued API might leave only a separately negotiated route. API availability alone is therefore an incomplete measure of openness.

## Restriction and selective access create different economic incentives

If an AI answer replaces a source visit, a platform or publisher may lose advertising, subscription or sales opportunities. Under those conditions, charging for data or keeping users within its own service becomes attractive. If source links bring visits or licensing revenue offsets losses, external provision may instead be worthwhile.

Serving high request volumes, protecting personal information and reflecting deletions also cost money. Approval and pricing can help fund those tasks. But withholding necessary data from outside firms with comparable costs and risks, while supplying an internal service, could make entry harder.

The risk can grow when hard-to-replace data is combined with a service that attracts users. Data could improve recommendations, and more users' choices could produce further data. This is a hypothesis about how combining data and service distribution could affect competition. Adequate substitutes and people using several services can weaken the effect.

## Effects and outlook depend on the terms of participation

Independent developers and researchers may face contract negotiations and supplier-switching work alongside retrieval costs. Users may gain convenient integrated AI services while facing fewer comparison or recommendation alternatives. Publishers could gain revenue, but a platform's contract income does not automatically compensate individual contributors.

Regulators have also introduced measures to support choice. On [June 3, 2026, the UK's Competition and Markets Authority (CMA) imposed a publisher conduct requirement on Google search](https://www.gov.uk/government/news/cma-secures-fairer-deal-for-publishers-and-improves-google-search-services-in-uk/). It requires controls to opt out of content use in search AI features and clear attribution links, among other measures, with nine months to implement all changes. This does not mean worldwide implementation is complete. The CMA also says strategic market status designation does not itself imply anticompetitive conduct.

The issue ahead is participation terms rather than deal counts. Paid provision can sustain an external ecosystem if small firms can obtain necessary data at predictable prices. If only internal products and selected partners get essential data, concentration risks increase. The connection between data enclosure and platform concentration depends on the size of that access gap and how difficult it is to find substitutes.

## Further reading

- [Reddit Data API Terms](https://redditinc.com/policies/data-api-terms): distinguishes data access from rights in user content.
- [UK CMA measures for Google search](https://www.gov.uk/government/news/cma-secures-fairer-deal-for-publishers-and-improves-google-search-services-in-uk/): publisher choice over AI use and source attribution.

## References

Accessed October 15, 2026. Partnership descriptions refer to the scope publicly disclosed at announcement.

- Naver: [Shopping, Book and Professional Document Search termination](https://developers.naver.com/notice/article/32564), [API HUB migration](https://developers.naver.com/notice/article/32530), [Search API terms amendment](https://developers.naver.com/notice/article/33400).
- Naver API documentation: [legacy Shopping Search reference](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md), [Shopping Insight](https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md), [Commerce API](https://apicenter.commerce.naver.com/docs/commerce-api/current).
- Reddit: [Google partnership, 2024-02-22](https://redditinc.com/news/reddit-and-google-expand-partnership), [OpenAI partnership, 2024-05-16](https://redditinc.com/news/reddit-and-oai-partner), [Data API Terms](https://redditinc.com/policies/data-api-terms).
- X: [API pricing](https://docs.x.com/x-api/getting-started/pricing), [Developer Policy](https://docs.x.com/developer-terms/policy).
- Cloudflare: [Pay Per Crawl, 2025-07-01](https://blog.cloudflare.com/introducing-pay-per-crawl/), [beta documentation](https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/), [Pay Per Use, 2026-09-30](https://blog.cloudflare.com/pay-per-use/).
- UK CMA: [Google search measures, 2026-06-03](https://www.gov.uk/government/news/cma-secures-fairer-deal-for-publishers-and-improves-google-search-services-in-uk/).
