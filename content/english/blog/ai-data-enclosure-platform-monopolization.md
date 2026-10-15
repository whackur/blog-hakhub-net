---
title: "Data Enclosure and Platform Concentration in the AI Era"
meta_title: ""
description: "From Naver Shopping Search API termination to Reddit licensing, Cloudflare payment experiments and UK CMA requirements: how AI data access shapes platform competition."
date: 2026-10-15T16:00:00+09:00
lastmod: 2026-10-15T16:00:00+09:00
image: "/images/posts/ai-data-enclosure-platform-monopolization/cover.png"
categories: ["AI"]
tags: ["data-enclosure", "platforms", "competition", "data-licensing", "ai-search", "commerce"]
author: "whackur"
translationKey: "ai-data-enclosure-platform-monopolization"
draft: false
---

Naver's Shopping Search API termination is supported by official notices as of October 15, 2026. That does not mean every Naver API involving shopping data has ended. **Ending product search, migrating shopping click-trend data, and restricting the use of search data in AI are separate changes.** Keeping them separate makes it possible to explain what outside developers lost and what remains available. The respective evidence is the [termination notice](https://developers.naver.com/notice/article/32564), [migration notice](https://developers.naver.com/notice/article/32530), and [terms amendment](https://developers.naver.com/notice/article/33400).

Internationally, platforms have also restricted some forms of access while providing data to selected AI companies under contract. Reddit's Google partnership, Stack Overflow's OverflowAPI, and publisher licensing agreements are examples. These arrangements do not mean all data has disappeared or that every agreement is exclusive. This article examines seven cases since 2023, asking who can reuse publicly visible information and on what terms. It is a dated review of public evidence, rather than an exhaustive account of private contracts or changes after the access date.

The central argument is that counting public webpages is an inadequate measure of data enclosure. A page can remain readable while the rights to collect, combine, answer with, or transact on its information change. Competition risks increase when those differences involve data that is difficult to replace and a strong distribution channel. The cases below do not, by themselves, establish unlawful monopolization by any particular company.

## Separate the rights before assessing openness

Here, data enclosure means narrowing the access or reuse conditions for widely used data, with the operator selecting which users or uses it permits. This is an analytical definition, not a settled legal category. Termination, paid provision, application review, and restrictions on particular purposes have different consequences.

| Stage | Permission to check | Common mistake |
| --- | --- | --- |
| Collection and lookup | Web crawling, API calls, quotas and returned fields | Assuming browser visibility permits bulk collection |
| Training | Pretraining, fine-tuning and evaluation | Assuming a paid lookup includes model training |
| Retrieval and RAG | Indexing, search and context input for retrieval-augmented generation | Assuming every AI restriction disappears if model weights stay unchanged |
| Display and redistribution | Originals, excerpts, summaries, attribution, storage and export | Assuming a link permits every form of redistribution |
| Transactions and actions | Cart changes, orders, payment, cancellation and user authorization | Assuming product lookup also authorizes purchasing on someone's behalf |

Training changes a model's parameters. Retrieval-augmented generation (RAG) typically supplies external information as context when answering a request. Both use data, but a contract can treat them differently. A product that calls a search API and passes the results to a model needs to check both lookup permission and AI input permission. Naver's 2026 amendment illustrates why searching only for the word “training” can miss broader restrictions on input and evaluation.

Crawler signals are another layer. [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html) explains that robots.txt rules are not access authorization. Authentication and firewalls can enforce restrictions on requests; robots.txt asks cooperating crawlers to follow rules. Permission to crawl does not automatically establish copyright permission or a right to train. Technical receipt, contractual permission, and legally permitted use require separate analysis.

## What Naver terminated and what it migrated

Naver's [June 30, 2026 notice](https://developers.naver.com/notice/article/32564) names Shopping, Book, and Professional Document Search as termination targets, with July 31, 2026 as the effective date. The current text of the [migration notice registered on June 29](https://developers.naver.com/notice/article/32530) is more specific: those search APIs are excluded from NAVER API HUB migration, receive no grace period, and cannot be called with previously issued keys after the stated cutoff. It also says no separate replacement API, including on API HUB, is provided. The migration notice was modified on August 10. That modification date matters: it would be inaccurate to assume every sentence in its current version appeared at initial publication.

The remaining migration targets within Search API, together with Search Trend and Shopping Insight, follow a different schedule. New applications through the developer center stopped from July 31, 2026; new users apply through API HUB. Previously registered applications receive developer-center support through June 30, 2027 under the announced grace period. The Shopping Search termination date must not be presented as the termination date of all Shopping Insight service.

| Product or channel | Data or function | Verified scope |
| --- | --- | --- |
| Shopping Search within Search | Product names, links, prices and other search results | Termination target on July 31, 2026; existing keys excluded from grace; no API HUB replacement |
| DataLab Shopping Insight | Shopping search click trends by category and keyword | Migration target; existing applications supported through June 30, 2027 under the notice |
| Commerce API | Authenticated commerce integration for products, orders and settlement | Separate documented product; its existence does not confer general shopping search access |
| Affiliate or price-comparison feeds | Supplying merchant data to a platform or exchanging data under a contract | The cited termination notices do not establish the status of every private agreement or feed |

The distinction concerns function, not branding. The [Shopping Insight reference](https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md) describes click trends and relative values normalized so that the maximum is 100. That is different from returning products currently available for purchase or a live minimum price. The [current Commerce API reference](https://apicenter.commerce.naver.com/docs/commerce-api/current) and [authentication guide](https://apicenter.commerce.naver.com/docs/auth) cover operational functions and server-to-server authentication. Switching to a different API name does not bring the desired dataset with it.

A surviving document makes the situation more confusing. On the access date, the [old Shopping Search reference](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md) still describes endpoints, response fields, and a daily limit of 25,000 calls. Its public availability was checked; authenticated endpoint operation was not tested. The conclusion about termination rests on the specific official notices, not a failed request or a missing menu item. The old quota should not be advertised as a currently available free allowance.

API availability and permission to use the response in AI also differ. In a [notice published August 7, 2026](https://developers.naver.com/notice/article/33400), effective September 7, Naver added language prohibiting search data from being input into AI or used for training, improvement, evaluation and display, among other AI uses. It requires unprocessed search-result display and source links, while setting purpose-specific caching exceptions and periods. This amendment applies to the developer-center Search API terms. It should not automatically be extended to NAVER API HUB, Commerce API or separately negotiated contracts.

At the same time, Naver announced its [shopping AI agent beta on February 26](https://www.navercorp.com/media/pressReleasesDetail?seq=34353) and [recommendations incorporating real-time delivery information and order deadlines on September 17](https://www.navercorp.com/media/pressReleasesDetail?seq=10034666). Its own product direction combines product information, reviews, and delivery context. The coexistence of a shrinking external product-search route and a more capable internal AI service is a valid starting point for competition analysis. The termination notices do not establish that blocking AI competitors was the motive. Timing alone does not prove causation.

This evidence also sets the boundary of the domestic claim. A specific Naver notice cannot establish that Kakao, Daum, or Korean platforms collectively ended their APIs. It is more useful to distinguish seller workflow automation from the data routes used by outside comparison services than to say that Korean platforms have all closed their data.

## Reddit combines restricted access with licensed supply

Reddit's [2023 explanation of API changes](https://redditinc.com/news/apifacts) separates high-volume usage from free access, with exceptions for areas including moderation tools and accessibility apps. Describing it as a complete shutdown of all APIs would erase those distinctions. The document supports an account of policy at that time; it does not guarantee every applicant's rights today.

The [Google agreement announced February 22, 2024](https://redditinc.com/news/reddit-and-google-expand-partnership) subsequently described structured Data API access and support for model training. The [OpenAI partnership announced May 16](https://redditinc.com/news/reddit-and-oai-partner) described bringing real-time content into ChatGPT and other products, alongside collaboration on AI features for Reddit. Outside supply continued through approved channels. Neither announcement, by itself, establishes an exclusive grant to one buyer.

For competition, entry conditions matter more than the mere existence of a contract. Can a smaller developer obtain comparable freshness, coverage, and deletion handling? Are prices and application criteria published? The answers determine whether licensing broadens supply or concentrates it. The [current Data API Terms](https://redditinc.com/policies/data-api-terms) must be checked separately; a statement about free access in a 2024 partnership announcement is insufficient for designing a commercial service today. This article does not infer undisclosed prices or exclusivity clauses.

## X shows how an available API can still change product economics

[X's current pricing documentation](https://docs.x.com/x-api/getting-started/pricing) describes prepaid credits and pay-per-usage access rather than subscriptions. It lists ordinary Post reads at $0.005 per returned resource and qualifying Owned Reads at $0.001. At the ordinary rate, reading 100,000 distinct posts once would give a simple calculated cost of $500. This multiplies a documented rate; it is not a measured research bill. Endpoint eligibility and deduplication rules also affect billing.

Low initial spending can benefit a small account-management application. Large observational studies and products comparing many users face costs that grow with reading volume. The size of those costs is separate from their justification. Charging for operation does not establish discrimination, but it changes which services are economically feasible. The [developer policy](https://developer.x.com/en/developer-terms/agreement-and-policy) also imposes use-case disclosure and data-handling conditions. Paid reading must not be treated as unlimited permission to redistribute or train models.

## Stack Overflow separates content rights from delivery services

Stack Overflow's [May 6, 2024 OpenAI announcement](https://stackoverflow.co/company/press/archive/openai-partnership) described supplying technical knowledge through OverflowAPI, attribution within ChatGPT, and cooperation on improving models. A commercial delivery arrangement does not, by itself, remove existing licenses on public answers.

The [contribution licensing guide](https://stackoverflow.com/help/licensing) specifies CC BY-SA versions according to when content was posted. Hosting a contributor's writing is not the same as owning all copyright in it. Similarly, the freshness, preparation, and reliability offered by a delivery contract differ from rights a user may already have under a content license. The partnership announcement does not decide whether a particular training implementation satisfies applicable license obligations.

That distinction matters for compensation. Platform contract revenue, contributor recognition, and payments to contributors are separate design choices. Where attribution is promised, the practical question is how easily a reader can reach the original work and identify its author. Announcing a deal is insufficient evidence of community-wide consent or completed compensation.

## Publisher agreements selectively open particular collections

[News Corp's May 22, 2024 announcement](https://investors.newscorp.com/news-releases/news-release-details/news-corp-and-openai-sign-landmark-multi-year-global-partnership) describes a multi-year agreement giving OpenAI access to current and archived material from major publications, and permission to display content in response to user questions. It excludes content from other News Corp businesses. The first task is to identify the collection and products being connected. This is neither a transfer of all company copyrights nor an opening to every AI service.

Such agreements can have opposing effects. Revenue that pays for reporting can help sustain original production. If only large publishers and large AI companies can negotiate a workable arrangement, smaller publishers and search services may struggle to participate. The balance requires evidence about contract scope, accessible buyer programs, referrals and payments. Undisclosed prices, exclusivity, and post-deal traffic effects should not be presented as verified facts.

## Cloudflare tests what comes after blocking

Cloudflare announced [Pay Per Crawl in private beta on July 1, 2025](https://blog.cloudflare.com/introducing-pay-per-crawl/). Content owners could price crawler access and use HTTP 402 to request payment. This attempts to attach a payment condition to request handling, rather than relying solely on a robots.txt request for cooperation. The [current documentation](https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/) still labels the product beta.

The newer development is [Pay Per Use, announced in beta on September 30, 2026](https://blog.cloudflare.com/pay-per-use/). Buyers propose a defined paid use and price, publishers choose whether to participate, and settlement follows buyer reports. Unlike Pay Per Crawl’s per-fetch access charge, Pay Per Use bills for the defined downstream use rather than every fetch. Program terms can include training restrictions. Paying for access is consequently different from purchasing every downstream right.

A shared arrangement could lower the negotiation burden for small publishers. It also raises questions about validating buyer reports: the announcement explicitly describes usage as self-reported. A beta launch does not establish that creator compensation has been solved or that a market standard has emerged. Dependence on the intermediary that defines and administers the transaction is another issue to track.

## Separating Google search discovery from AI use

Google's [crawler documentation](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers) describes Google-Extended as a token controlling training and certain grounding uses for Gemini-related products. It states that the token does not affect inclusion or ranking in Google Search. Grounding here means supplying external evidence when a model answers. The documented scope must not be expanded into a universal opt-out for every Google AI product.

On [June 3, 2026, the UK CMA imposed a publisher conduct requirement on Google](https://www.gov.uk/find-digital-markets-measures/google-search-publisher-conduct-requirement). It covers controls over search content in generative AI, explanations, engagement metrics, and attribution. The [official announcement](https://www.gov.uk/government/news/cma-secures-fairer-deal-for-publishers-and-improves-google-search-services-in-uk) gives Google nine months to implement all changes. As of October, it would be wrong to describe every control as fully implemented worldwide. The decision and actual compliance require separate checks.

The policy issue is whether publishers can choose AI-use conditions while retaining search discoverability. A choice becomes less meaningful if rejecting AI use requires surrendering search referrals. The CMA also explicitly states that designation with strategic market status (SMS) does not itself imply anticompetitive conduct. A particular UK regulatory intervention should not be described as a worldwide judgment of unlawful monopoly.

## Competition risks arise when data meets distribution

Across these cases, operators set different conditions for different uses. The following is economic interpretation built on those observations. An answer that substitutes for reading a source can save the user time while reducing the publisher's opportunities for advertising, subscriptions, or sales. A source link might also bring a new reader, and licensing revenue might offset lost visits. Testing the balance requires looking beyond pageviews to paid-use revenue and the value of referred readers.

Provision also carries real costs and responsibilities: serving requests, handling large volumes, preventing spam, protecting personal information, and reflecting deletions. Unlimited free collection is not the only defensible arrangement. The competition question is whether comparable users with comparable costs and risks receive different terms, or whether only an operator's own products and selected partners receive the necessary quality. Cost and safety objectives can coexist with exclusionary effects. Neither explanation alone settles the issue.

![Conceptual diagram showing content passing through purpose-specific access conditions to internal services and approved external users, with service interactions producing new data](/images/posts/ai-data-enclosure-platform-monopolization/selective-access.svg)

*Original illustration by HakHub, synthesized from the Naver notices, Reddit and Stack Overflow partnerships, Cloudflare payment models, and CMA documents. Arrows represent possible relationships, not measured market shares or effect sizes. Internal use also remains subject to rights and privacy conditions.*

Consider a hypothetical shopping platform with product information, purchase context, and a recommendation service it can distribute directly. Better recommendations may attract users; their choices produce new signals. An outside service lacking comparable current product or delivery data may be disadvantaged in comparison or recommendation quality. The possible loop is data → AI quality and distribution → user interactions → new data. The diagram explains this mechanism; it does not measure its realization at a particular company.

The loop can weaken. Data may be stale or repetitive, alternative suppliers may be adequate, or users may use several services. Learning from behavior caused by poor recommendations can also reinforce errors. More data does not automatically mean better quality, and an initial advantage does not establish permanent monopoly.

Switching costs extend beyond replacing API calls. A developer may need to reconcile product identifiers, handle missing responses, dispose of stored data, and revise contracts and attribution. Researchers may face a break in a time series when collection conditions change. Separating a social change from a change in sampling access then becomes harder. These are plausible mechanisms, not measured estimates of losses across all developers and research projects.

Exclusivity needs contract-specific analysis. A nonexclusive agreement can leave room for multiple AI companies to use the same collection. An exclusive agreement may limit rivals within a defined collection, term, territory, or purpose. Even nonexclusive supply can remain inaccessible to small firms if minimum commitments are large or approval is opaque. Conversely, workable pricing by scale and research exceptions can make paid external supply more sustainable.

“Internal use” should also be separated from “domestic use.” Restricting data to a platform's own services concerns the boundary of a company. Data localization and sovereign AI concern dependence on national infrastructure, control, or jurisdiction. A domestic company can supply foreign buyers nonexclusively; a foreign company can process data on domestic servers while restricting outside reuse. Server location alone does not establish whether developers have meaningful access.

## Community concerns include compensation and intermediary power

In the [July 1, 2025 Hacker News discussion](https://news.ycombinator.com/item?id=44432385), [suyash](https://news.ycombinator.com/item?id=44432533) welcomed an attempt to address bot traffic while preferring an open protocol for permissions and payment. [Toritori12](https://news.ycombinator.com/item?id=44432530) agreed with the idea but questioned bypass economics and the cost ultimately passed to users. Support and criticism appear within individual comments. These are user opinions and reported experience, not a representative survey or an experiment proving bypass feasibility.

The independent [developerWithACat post of July 30, 2025](https://developerwithacat.com/blog/202507/cloudflare-pay-per-crawl/) likewise questioned blocking effectiveness and price agreement. Its criticism should not be applied retroactively as evidence that the 2026 usage-based beta failed. It helps identify what the different models need to demonstrate. Crawl counts, actual answer use, source referrals, and compensation are different measures.

## Open routes and evidence that could weaken the thesis

There are counterexamples to a universal closure story. [Wikimedia's public dumps](https://meta.wikimedia.org/wiki/Data_dumps) offer downloading and reuse for research, preservation, and offline applications. License conditions and limitations in completeness and freshness still apply, but access does not depend on negotiating a large bilateral purchase. Stack Overflow's public contribution licenses likewise need consideration separately from its commercial delivery service.

Practical alternatives include documents with rights secured directly, supply agreements with merchants, suitable open datasets, and multiple suppliers. These are design options rather than claims that any substitute is equivalent. An open dump cannot necessarily supply today's delivery availability or a newly deleted post. Choosing an open-weight model also does not create rights in its inputs. Model selection and data procurement need separate decisions.

The competition-risk hypothesis should be tested against indicators that could disprove it, rather than collecting only worsening examples:

- Compare actual grants and prices for new outside developers at matched purpose, freshness, and volume. Broader standard application routes and prices would weaken the concentration hypothesis.
- Compare internal products and outside APIs on fields, update delay, and missing records. Account for justified privacy and security differences before treating a gap as preferential access.
- Observe referrals, subscriptions, sales, and licensing revenue together. If net revenue holds after accounting for seasonality and suitable controls, a simple revenue-displacement claim needs revision.
- Record migration time and the extent of portable data. Easier supplier substitution and multi-service use reduce lock-in risk.
- Track approval rates and contracting time for small buyers and independent researchers. More announced deals do not necessarily mean more firms can enter.
- Check whether rejecting AI use changes ordinary search discoverability, and inspect actual attribution links. Measure the gap between announced controls and implemented choice.

## An access audit before building a product

Write down each source and purpose before listing APIs. A flow such as “retrieve products → rerank → send context to a model → display recommendations → place an order” reveals permissions that a successful request cannot establish. The checklist below connects documents to product behavior; it does not replace interpretation of a particular agreement. A screen where a person reads search results and one where a model reorganizes them into recommendations require different checks, even when both call the same API.

A concrete product example exposes the differences. Suppose a supplier permits displaying product names and prices, while withholding permission for model input and long-term storage. A developer may have a route to a search-results screen, yet still need separate permission to embed the same response in a persistent recommendation index. Transforming text into embeddings does not, by itself, remove contractual restrictions. Permission to summarize also provides no basis for assuming permission to resell data or execute an order. This is a hypothetical rights review, not a description of any particular provider's contract.

Evaluation data needs the same attention. A team comparing recommendation quality each month may retain responses and reference answers long after the information disappears from its interface. Applying deletion requests or cache expiry only to the user-facing screen can miss those copies. Record where data is copied and which purpose each copy serves. A purpose inventory should connect operational data, logs, search indexes, and evaluation samples to their retention locations and responsible operators. Including this work in migration estimates avoids treating a supplier change as merely an endpoint substitution.

| Check | Evidence to retain |
| --- | --- |
| Service status | Publication, modification and effective dates; new applications versus existing keys |
| Dataset | Fields, freshness, missing records, and the direction of lookup versus supply feeds |
| Purpose | Separate conditions for training, evaluation, RAG, display and export |
| Storage and rights | Cache periods, deletion handling, source and contributor attribution, redistribution |
| Transaction authority | User authorization, seller permissions, and responsibility for ordering, payment and cancellation |
| Costs and alternatives | Cost by returned volume, caps, change notices and a migration plan |

During operation, compare errors with authentication expiry, quota usage, status codes, and official notices before declaring a policy shutdown. An accessible document does not guarantee an operating service either. Naver demonstrates how a termination notice and an old endpoint reference can coexist. When provider documents appear inconsistent, retain the notice that identifies the specific target and dates, and leave unverified scope explicitly unresolved.

The evidence supports a more specific conclusion than “internet data is disappearing.” Some general-purpose routes end, others migrate, and new agreements authorize particular buyers and uses. For competition, the question is whether rivals can obtain the rights they need on predictable terms. Recording both those conditions and actual outcomes makes it possible to distinguish restricted access from effective compensation.

## Further reading

- [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html): the role of robots.txt and its distinction from security controls.
- [Wikimedia Data dumps](https://meta.wikimedia.org/wiki/Data_dumps): a public reuse route to compare with contract-based provision.
- [Google publisher conduct requirement](https://www.gov.uk/find-digital-markets-measures/google-search-publisher-conduct-requirement): controls and transparency requirements for generative AI use.

## References

All links were accessed October 15, 2026. Company claims about product effects and intentions remain company statements; undisclosed contract conditions have not been verified.

- [Naver: Shopping, Book and Professional Document Search termination](https://developers.naver.com/notice/article/32564): 2026-06-30; modified 2026-07-16; accessed 2026-10-15.
- [Naver: API termination and NAVER API HUB migration](https://developers.naver.com/notice/article/32530): 2026-06-29; modified 2026-08-10; accessed 2026-10-15.
- [Naver: Search API terms amendment](https://developers.naver.com/notice/article/33400): 2026-08-07; effective 2026-09-07; accessed 2026-10-15.
- [Naver: legacy Shopping Search reference](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md): Undated live reference; accessed 2026-10-15.
- [Naver: Shopping Insight reference](https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md): Undated live reference; accessed 2026-10-15.
- [Naver: Commerce API reference](https://apicenter.commerce.naver.com/docs/commerce-api/current): 2.90.1 listed 2026-10-07; accessed 2026-10-15.
- [Naver: Commerce API authentication](https://apicenter.commerce.naver.com/docs/auth): Live reference; accessed 2026-10-15.
- [Naver: shopping AI agent beta](https://www.navercorp.com/media/pressReleasesDetail?seq=34353): 2026-02-26; accessed 2026-10-15.
- [Naver: real-time delivery recommendations](https://www.navercorp.com/media/pressReleasesDetail?seq=10034666): 2026-09-17; accessed 2026-10-15.
- [Reddit: facts about 2023 API updates](https://redditinc.com/news/apifacts): 2023-06-15; updated 2023-06-30; accessed 2026-10-15.
- [Reddit: expanded Google partnership](https://redditinc.com/news/reddit-and-google-expand-partnership): 2024-02-22; accessed 2026-10-15.
- [Reddit: OpenAI partnership](https://redditinc.com/news/reddit-and-oai-partner): 2024-05-16; accessed 2026-10-15.
- [Reddit: current Data API Terms](https://redditinc.com/policies/data-api-terms): Live terms; accessed 2026-10-15.
- [X: pay-per-usage pricing](https://docs.x.com/x-api/getting-started/pricing): Live pricing; accessed 2026-10-15.
- [X: developer policy](https://developer.x.com/en/developer-terms/agreement-and-policy): Live policy; accessed 2026-10-15.
- [Stack Overflow: OpenAI partnership](https://stackoverflow.co/company/press/archive/openai-partnership): 2024-05-06; accessed 2026-10-15.
- [Stack Overflow: public contribution licenses](https://stackoverflow.com/help/licensing): Live help; accessed 2026-10-15.
- [News Corp: OpenAI agreement](https://investors.newscorp.com/news-releases/news-release-details/news-corp-and-openai-sign-landmark-multi-year-global-partnership): 2024-05-22; accessed 2026-10-15.
- [Cloudflare: introducing Pay Per Crawl](https://blog.cloudflare.com/introducing-pay-per-crawl/): 2025-07-01; accessed 2026-10-15.
- [Cloudflare: Pay Per Crawl documentation](https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/): Index last updated 2026-04-23; accessed 2026-10-15.
- [Cloudflare: Pay Per Use beta](https://blog.cloudflare.com/pay-per-use/): 2026-09-30; accessed 2026-10-15.
- [Google: common crawlers and Google-Extended](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers): Last updated 2026-07-14; accessed 2026-10-15.
- [CMA: Google publisher conduct requirement](https://www.gov.uk/find-digital-markets-measures/google-search-publisher-conduct-requirement): 2026-06-03; page updated 2026-08-04; accessed 2026-10-15.
- [CMA: publisher requirements announcement](https://www.gov.uk/government/news/cma-secures-fairer-deal-for-publishers-and-improves-google-search-services-in-uk): 2026-06-03; accessed 2026-10-15.
- [IETF: RFC 9309 Robots Exclusion Protocol](https://www.rfc-editor.org/rfc/rfc9309.html): 2022-09, background standard; accessed 2026-10-15.
- [Wikimedia: Data dumps](https://meta.wikimedia.org/wiki/Data_dumps): Live project documentation; modified 2026-07-23; accessed 2026-10-15.
- [Hacker News: Cloudflare Pay Per Crawl discussion](https://news.ycombinator.com/item?id=44432385): 2025-07-01; accessed 2026-10-15.
- [Hacker News: suyash on permissions and payment](https://news.ycombinator.com/item?id=44432533): 2025-07-01T10:46:06Z; accessed 2026-10-15.
- [Hacker News: Toritori12 on costs](https://news.ycombinator.com/item?id=44432530): 2025-07-01T10:45:45Z; accessed 2026-10-15.
- [developerWithACat: critique of Pay Per Crawl](https://developerwithacat.com/blog/202507/cloudflare-pay-per-crawl/): 2025-07-30; accessed 2026-10-15.
