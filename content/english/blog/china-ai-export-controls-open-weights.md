---
title: "China’s AI technology export controls: temporary registration and the draft catalogue"
meta_title: ""
description: "The legal status and classification criteria of China’s October 16, 2026 AI technology export measures, and their implications for public weights, first releases, APIs and overseas deployment."
date: 2026-10-21T11:30:00+09:00
lastmod: 2026-10-21T12:48:17+09:00
image: "/images/posts/china-ai-export-controls-open-weights/cover.webp"
categories: ["AI"]
tags: ["open-weights", "export-controls", "deepseek", "qwen", "hugging-face", "local-llm"]
author: "whackur"
translationKey: "china-ai-export-controls-open-weights"
draft: false
---

On October 16, 2026, China’s Ministry of Commerce (MOFCOM) and Ministry of Science and Technology issued Announcement No. 48, proposing changes to the prohibited and restricted technology export catalogue and introducing temporary pre-export registration for AI and other technologies. **As of October 21, registration is in effect; the revised catalogue remains open for consultation.** ([Official announcement](https://www.mofcom.gov.cn/zwgk/zcfb/art/2026/art_0a31a3c9ac404f7a9b0e917ce3412997.html))

For international AI development and deployment, the change matters because weight releases, overseas technology transfers and API services follow different procedures. The draft excludes already-public technology and proposes automatic licensing and other facilitation for open-source exports of restricted AI technology. It also distinguishes overseas server deployment from overseas access to models deployed in China. ([Official Q&A](https://www.mofcom.gov.cn/xwfb/xwfyrth/art/2026/art_d7661dbf62794345a221404f82a25959.html))

## Registration applies now; the expanded licensing regime is proposed

The Ministry of Commerce (MOFCOM) and Ministry of Science and Technology issued Announcement No. 48 on October 16. Consultation runs through November 15 on 23 AI technologies, five biopharmaceutical technologies and 12 photovoltaic technologies. **The consultation deadline is not the effective date of the revised catalogue.** ([Announcement, sections I and II](https://www.mofcom.gov.cn/zwgk/zcfb/art/2026/art_0a31a3c9ac404f7a9b0e917ce3412997.html))

A temporary registration requirement applies from the announcement date until the revised catalogue takes effect. Exporters must register before exporting the relevant technology, including exports that have started but remain incomplete. Covered transactions include transferring ownership overseas, licensing technology held in China for overseas use, and changes that place domestic technology under foreign ownership or actual control. Registration asks for information about the exporter and recipient, destination, technology and intended use, and estimated export value. ([Announcement, section III](https://www.mofcom.gov.cn/zwgk/zcfb/art/2026/art_0a31a3c9ac404f7a9b0e917ce3412997.html))

Registration submits information about an export; authorization permits it. The current registration obligation and the prohibitions and licensing requirements in the proposed catalogue have different legal status. Baker McKenzie’s [October 18 legal explanation](https://sanctionsnews.bakermckenzie.com/china-proposes-expanded-export-controls-on-ai-biopharma-and-solar-energy-technologies/) likewise distinguishes registration from approval or permission to export.

[Articles 30 and 31 of the Technology Import and Export Administration Regulations](https://www.baoji.gov.cn/bmpd/bjsswj/gzdt/tzgg/202606/t20260609_1276358.html) establish that prohibited technology cannot be exported and restricted technology requires a license. Automatic licensing is proposed facilitation for specified exports in the restricted category. The authorities describe a process approaching immediate export upon filing, but that is no guarantee that every future model will qualify. Final rules and implementation guidance still matter. ([Official Q&A](https://www.mofcom.gov.cn/xwfb/xwfyrth/art/2026/art_d7661dbf62794345a221404f82a25959.html), [Baker McKenzie](https://sanctionsnews.bakermckenzie.com/china-proposes-expanded-export-controls-on-ai-biopharma-and-solar-energy-technologies/))

## Model size alone does not determine classification

Annex 1 separates training-data classifications from technical characteristics. Large models trained using China’s legally defined **core data** and then used to provide services are proposed for the prohibited category, under 266501J. Large models trained using **important data** and then used to provide services appear in the restricted category, under 266504X, item 1. These are legal data categories, not informal descriptions of valuable training material. The annex refers to China’s Data Security Law and related laws and regulations. ([Annex 1, AI section](https://www.mofcom.gov.cn/zwgk/zcfb/art/2026/art_0a31a3c9ac404f7a9b0e917ce3412997.html))

A separate item 2 proposes restrictions on the core technologies of large models meeting any one of these conditions:

- Compute of at least **10²⁶ floating-point operations**. This is an operation count, not a processing rate in FLOP/s.
- At least **2 trillion parameters**. The original Chinese specifies 20,000 hundred-million parameters.
- Capabilities at a globally leading level.

The covered core technologies include weights, key checkpoints, underlying source code, architecture design, training optimization and inference acceleration. The annex defines globally leading capability by reference to a global top-10 position in public assessments at the time of export, conducted by mainstream domestic or international evaluation organizations, large industrial platforms and similar bodies. Its listed dimensions include overall performance, specialized capabilities, worldwide usage, safety performance and training efficiency. Selecting an arbitrary leaderboard result is insufficient to settle a model’s legal classification. ([266504X, item 2 and note ③](https://www.mofcom.gov.cn/zwgk/zcfb/art/2026/art_0a31a3c9ac404f7a9b0e917ce3412997.html))

There is also an exception for the important-data branch. It covers use of only a trace amount, no more than 0.1%, where the data cannot materially improve core technology R&D capability in that domain, security measures such as desensitization and cleaning are applied, and the important data will not reappear in outputs. The note also excludes cases where the relevant important data can lawfully be obtained publicly. This exception attaches to item 1. It does not erase the separate compute, parameter or capability tests in item 2. ([266504X, notes ① and ②](https://www.mofcom.gov.cn/zwgk/zcfb/art/2026/art_0a31a3c9ac404f7a9b0e917ce3412997.html))

The AI section separately proposes prohibitions for high-performance agents intended specifically or primarily for sensitive infrastructure, defense and core government applications, and for specified offensive technologies. A general chatbot or coding-model label does not establish that a model belongs to those categories. Data classification, technical characteristics and use conditions matter alongside size.

## Publication status and delivery method change the result

Publication status and delivery method determine how the classifications apply. Current registration obligations remain distinct from the treatment proposed for the period after formal implementation.

| Case | Treatment described in the announcement or proposal |
| --- | --- |
| AI technology already in the public domain through open-source release or academic publication | Excluded from scope. The extent of what has actually been disclosed matters. |
| First open-source release of previously unpublished restricted technology | Temporary pre-export registration must currently be assessed; the draft proposes automatic licensing and other facilitation for the future regime. |
| New export of technology proposed for the prohibited category | Prohibited if that classification is adopted. The facilitation for restricted open-source technology cannot simply be applied to it. |
| Local deployment of a restricted model on overseas servers | Described as a technology export after formal implementation. Deployment in an exporter’s own overseas cloud may qualify for automatic licensing. |
| Overseas API, app, web or SaaS access to a restricted model deployed in China | The Q&A places these outside large-model technology export management, distinguishing service access from transferring weights or core technology overseas. |

Sources: [Annex 1, AI footnotes 1 and 2](https://www.mofcom.gov.cn/zwgk/zcfb/art/2026/art_0a31a3c9ac404f7a9b0e917ce3412997.html), [Q&A on open source and overseas deployment](https://www.mofcom.gov.cn/xwfb/xwfyrth/art/2026/art_d7661dbf62794345a221404f82a25959.html).

## Existing public technology differs from a first release

The exclusion concerns technology that has **already entered the public domain** through open-source release, academic publication or similar means. An architecture disclosed in a paper and unpublished weights are different bodies of information. Publishing an earlier version does not make a later private checkpoint public. ([Annex 1, footnote 1](https://www.mofcom.gov.cn/zwgk/zcfb/art/2026/art_0a31a3c9ac404f7a9b0e917ce3412997.html))

For unpublished restricted technology, the act of releasing it may itself raise an export-procedure question. The draft addresses that case by offering automatic licensing and other facilitation for open-source exports of restricted AI technology. The same footnote covers Chinese companies building and operating their own overseas computing centers, overseas chip fabrication, joint R&D using overseas resources, and participation in international standards development. This supports continued publication, but does not mean that becoming public afterward eliminates procedures that apply before release. ([Annex 1, footnote 2](https://www.mofcom.gov.cn/zwgk/zcfb/art/2026/art_0a31a3c9ac404f7a9b0e917ce3412997.html))

The distinction applies to DeepSeek and Qwen. Existing public examples include the official model cards for [DeepSeek-V3.2](https://huggingface.co/deepseek-ai/DeepSeek-V3.2) and [Qwen3-235B-A22B](https://huggingface.co/Qwen/Qwen3-235B-A22B). The public-domain exclusion can be assessed for what has already been disclosed, while a first release of future private weights requires a separate assessment of classification and export procedures. These are examples of existing public technology, not evidence of whether a successor will be released.

Hugging Face is a [platform for hosting model repositories and files](https://huggingface.co/docs/hub/models-the-hub). The announcement provides no exemption for using that platform. The relevant questions concern the technology, the rights granted and the way it is supplied abroad.

Here, **open weights** means that trained weights are accessible for running the model yourself. That differs from fully open-source AI. For example, the [OSI Open Source AI Definition 1.0](https://opensource.org/ai/open-source-ai-definition) requires freedoms to use, study, modify and share, together with code, parameters and sufficient information about training data. It does not require distributing every raw training record. Neither that definition nor a model’s software license substitutes for China’s export-law tests concerning public-domain technology and licensing.

## API services and overseas weight deployment

The official Q&A explicitly discusses the period after the revised catalogue takes effect. It describes overseas local deployment of restricted technology as a technology export. Deployment in an exporter’s own overseas cloud, where risks are relatively controllable, may qualify for automatic licensing and other facilitation. ([Q&A on overseas deployment](https://www.mofcom.gov.cn/xwfb/xwfyrth/art/2026/art_d7661dbf62794345a221404f82a25959.html))

The same answer places overseas API, app, web and SaaS services using restricted large models deployed in China outside large-model technology export management. It also lists lightweight on-device deployment as a separate type. Transferring full weights to an overseas server is distinct from accessing an API service. The reference to lightweight on-device deployment cannot be extended into an exemption for every offline weight deployment. These are distinctions within this technology export framework, not exemptions from all other data, security or service obligations.

For development and operations, API access and access to weights are separate conditions. Running inference on an isolated network or modifying a model requires checking actual weight availability and the license. A paper, model card or API model name alone does not establish that downloadable weights have been released.

## Established obligations and pending decisions

As of October 21, the established obligation is temporary pre-export registration for the relevant technology. The proposed catalogue separates prohibited and restricted categories by training data, technical characteristics and intended use. It combines an exclusion for existing public technology with simplified procedures for certain exports of restricted technology. First weight releases, overseas local deployment and service access to models deployed in China receive different treatment within that structure.

Pending decisions include the final catalogue’s contents and effective date, how classifications apply at the time of export, and eligibility and filing procedures for automatic licensing. International joint research and model deployment plans need to account for those implementing rules alongside developers’ actual release decisions. The availability of an existing public model does not settle the conditions for future updates.

## Further reading

- [Hugging Face Model Hub](https://huggingface.co/docs/hub/models-the-hub): how model repositories and file distribution work.
- [Open Source AI Definition 1.0](https://opensource.org/ai/open-source-ai-definition): the difference between access to weights and open-source AI requirements.

## References

All sources accessed October 21, 2026.

- [MOFCOM and MOST Announcement No. 48 of 2026, with Annexes 1 and 2](https://www.mofcom.gov.cn/zwgk/zcfb/art/2026/art_0a31a3c9ac404f7a9b0e917ce3412997.html): October 16, 2026. AI entries 266501J and 266504X, footnotes 1 and 2, and temporary registration requirements.
- [Official MOFCOM Q&A](https://www.mofcom.gov.cn/xwfb/xwfyrth/art/2026/art_d7661dbf62794345a221404f82a25959.html): October 16, 2026. Open source, automatic licensing, overseas deployment and API services.
- [Technology Import and Export Administration Regulations](https://www.baoji.gov.cn/bmpd/bjsswj/gzdt/tzgg/202606/t20260609_1276358.html): Baoji municipal government republication, June 9, 2026. Framework for prohibited and restricted technology exports.
- [China Proposes Expanded Export Controls on AI, Biopharma and Solar Energy Technologies](https://sanctionsnews.bakermckenzie.com/china-proposes-expanded-export-controls-on-ai-biopharma-and-solar-energy-technologies/): Baker McKenzie, October 18, 2026. Explanation of registration, licensing and the proposed framework.
- [DeepSeek-V3.2](https://huggingface.co/deepseek-ai/DeepSeek-V3.2), [Qwen3-235B-A22B](https://huggingface.co/Qwen/Qwen3-235B-A22B): official developer model cards, as examples of existing public releases.
- [The Model Hub](https://huggingface.co/docs/hub/models-the-hub): official Hugging Face documentation.
- [The Open Source AI Definition 1.0](https://opensource.org/ai/open-source-ai-definition): Open Source Initiative.
