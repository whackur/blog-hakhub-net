---
title: "Why did Anthropic publish its report on alleged Kimi-to-Claude routing?"
meta_title: ""
description: "Anthropic's September 2026 report alleges that Moonshot routed some Kimi requests to Claude and replayed thinking signatures to extract reasoning traces. A closer look at the claims, the API mechanics, and the possible effects of disclosure."
date: 2026-09-15T13:30:00+09:00
lastmod: 2026-10-15T08:25:58+00:00
image: "/images/posts/anthropic-moonshot-disclosure-strategy/cover.png"
categories: ["AI"]
tags: ["llm", "distillation", "ai-security", "anthropic", "kimi"]
author: "whackur"
translationKey: "anthropic-moonshot-disclosure-strategy"
draft: false
---

Footage collected from hundreds of CCTV cameras in Chengdu followed one person. According to Anthropic's September 2026 report, the user believed they were using Moonshot's Kimi and asked whether the person was behaving unusually. Anthropic says the request went to Claude.

In [Detecting and countering misuse of AI: September 2026](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf), Anthropic alleges that Moonshot AI forwarded some customer requests to Claude instead of processing them with Kimi, then showed Claude's responses as Kimi's. Anthropic published the report on September 10, 2026. It also describes internal code and credentials that were live at the time of observation, submitted by an engineer at a major Chinese state-owned enterprise.

Anthropic says it detected and disrupted several campaigns. The report does not give the exact date when Moonshot's rerouting stopped, or say whether new accounts or routes appeared afterward. Its publication alone does not establish that every route was closed.

## What the report claims

The report covers activity detected and disrupted between December 2025 and August 2026. It groups cases into seven areas: cyber operations, influence operations, surveillance, scams and fraud, biological misuse, conventional weapons, and illicit distillation. The Moonshot case appears in the final category. These details come from Anthropic's investigation; the report does not include an independent investigation of its claims.

The central allegation in the Moonshot case (GTG-16002) is that Moonshot sent customer requests to Claude instead of Kimi and returned Claude's responses to users. In one instance, Anthropic says Moonshot relayed nearly 300,000 customer requests over ten days, most of them to Claude Opus. It says the relay used a proxy network with 5,380 fraudulent accounts, most of which appeared to be in Singapore and Japan.

| Organization | Scale reported by Anthropic |
|------|------|
| Moonshot (Kimi) | More than 23 million exchanges. Nearly 300,000 requests relayed in ten days through 5,380 fraudulent accounts |
| Alibaba (Qwen/Tongyi Lab) | More than 151 million exchanges, Anthropic's largest measured distillation campaign |
| Xiaomi (MiMo) | More than 400,000 requests across more than 1,500 accounts |
| DeepSeek | Similar rerouting and cross-session replay tactics, according to the report |

The Moonshot and Alibaba exchange counts cover May through July 2026. Xiaomi's figure of more than 400,000 covers 20 days in March and April. The report does not give exact dates for Moonshot's ten-day relay example.

In the DeepSeek case (GTG-16001), Anthropic says the company selected requests from users running coding tools such as Claude Code, the Agent SDK, and OpenCode, then routed them to Claude Opus. Xiaomi replayed conversations from MiMo users through OpenClaw and OpenCode, the report says. It also says activity increased as the free MiMo-V2-Pro trial period ended. The report describes targeted collections of particular kinds of work and conversation, not a claim that every request was forwarded.

## How the requests were routed

In an ordinary setup, a user sends a request to the Kimi app or API, Moonshot processes it with a Kimi model, and the service returns the result. Anthropic's account adds a relay step that calls the Claude API. The exact routing implementation is not disclosed.

![Editorial illustration of a hand placing an envelope in a blue collection box while a robot arm behind a curtain passes an envelope to another machine, representing request routing.](/images/posts/anthropic-moonshot-disclosure-strategy/routing-illustration.webp)

A proxy is a server that forwards a request on someone else's behalf. Residential proxies use IP addresses from ordinary home internet connections. Anthropic does not say whether Moonshot's account network used residential proxies. Its description of residential proxies, disposable email addresses, and virtual-card payments concerns Alibaba's accounts. Anthropic says the first Alibaba pool had nearly 5,000 accounts and shifted traffic to a second pool after the first was banned. Anthropic says some of those accounts were also funneling requests for DeepSeek and Xiaomi. There is no basis in the report for assuming Moonshot used the same setup.

The report names China, Russia, and Iran as examples of unsupported countries and says signals of abuse, including accounts operating from such countries, can trigger identity checks. That makes the distinction between an apparent proxy location and the requester's actual location relevant. This general account does not establish where Moonshot's accounts were operated.

Anthropic says the requests did not arrive through one Moonshot account. They came through accounts that appeared unrelated. The report gives the Moonshot account count and apparent locations, but that does not establish where each request actually began or exactly how the accounts were divided.

Nearly 300,000 requests over ten days averages 30,000 a day. Divided evenly across 5,380 accounts, that would be around five or six requests per account per day. This is only arithmetic to help convey scale, not a measured distribution. Account creation, payment, and proxy operations suggest substantial coordination, but the report does not describe Moonshot's precise operating process.

The report describes other organizations too. MiniMax allegedly created a separate company to run a proxy service that offered Anthropic and OpenAI models, but no Chinese models. SenseTime's distillation pipeline allegedly included conversation records purchased from third-party data vendors. Those cases support Anthropic's point that account bans alone do not describe every route through which exchanges can circulate.

The report's account is consistent with some users receiving Claude-quality responses through Kimi. It does not claim that this rerouting produced Kimi's benchmark scores. That connection appeared as speculation in Hacker News discussions, not as a finding in the report.

## Thinking blocks and cross-session replay

A key technical allegation is that the collection included reasoning traces, not only final answers. Distillation uses a stronger model's outputs as training material for another model. Anthropic's report focuses on how the material was collected and whether users knew their conversations were being routed.

Claude API responses can include thinking blocks and a signature field. The thinking text may be summarized or omitted, and the signature itself is not readable reasoning text. Anthropic's report describes the signature as a reference the API uses on later calls to look up the associated raw thinking. The current API documentation describes the field as carrying encrypted full thinking and tells callers not to interpret or parse it. The alleged extraction involves prompting Claude to reproduce a trace, rather than directly decrypting the value. The API documentation says to return prior blocks unchanged in tool-using conversations. That ordinary continuation is different from the report's allegation about reusing a saved signature in a new session.

Anthropic alleges that Moonshot saved a signature from stored exchanges, reused it in a new session, and prompted Claude to reproduce the associated reasoning trace. The report calls this cross-session replay. It also says Moonshot extracted reasoning transcripts collected through other means. This differs from ordinary API continuation, which returns the prior block unchanged in the same conversation. The report does not publish the original requests, prompts, code, or exact sequence of steps. The disclosed details are also insufficient to reproduce the conditions under which signature reuse was possible.

![Editorial illustration of a robot arm moving a sheet with an intact wax seal between two open notebooks, representing reasoning-trace reuse.](/images/posts/anthropic-moonshot-disclosure-strategy/reasoning-reuse-illustration.webp)

A final answer alone does not show which approaches the model tried or revised. Reasoning traces can include those intermediate steps, giving a collector a different kind of training material. Anthropic says summarizing reasoning makes the transcripts less useful for training another model. That does not establish that a summary always removes every failed approach, or that possessing a trace is enough to reproduce the original model's capabilities.

Anthropic describes several layers of mitigation. Claude now summarizes its reasoning before responding. The company says Fable 5.1's preserved thinking prevents new API accounts from changing the system prompt, tool definitions, or messages that precede a reasoning block. That is intended to distinguish an unchanged continuation from a replay with altered prior context. Anthropic also mentions stronger classifiers, blocking suspicious requests and accounts, and identity checks for accounts operating from unsupported countries.

## Sensitive data in the report

Anthropic says a user it assessed as likely affiliated with the People's Liberation Army (PLA) uploaded CCTV archive data about one person while believing they were using Kimi. The report says the archive included footage from hundreds of cameras in Chengdu, including cameras outside PLA facilities, institutes affiliated with China Electronics Technology Group Corporation (CETC), and state-owned enterprises. The user asked whether the person being tracked was behaving abnormally. The PLA link is Anthropic's assessment, described as likely, not an independently verified attribution.

In another case, a developer at a major Chinese state-owned enterprise allegedly submitted internal code and live credentials belonging to several Chinese companies while building an internal system with Kimi. The report described those credentials as live at the time of its investigation. It does not establish that they remain valid today.

The DeepSeek cases included specifications, organizational structure, and strategic objectives for a major Chinese technology company's AI program. The report also mentions live credentials for a Russian government database used by a Russian defense agency. In the Xiaomi case, Anthropic says data included names, contact information, and company records belonging to hundreds of users, in at least a dozen languages.

Anthropic says it does not know whether Moonshot told its customers that requests were being rerouted. The report does not establish that every Moonshot customer was unaware. It separately assesses that DeepSeek customers were likely not informed about the rerouting.

## What disclosure may accomplish

### Disruption and publication were separate actions

Anthropic says it had been detecting and disrupting unauthorized distillation campaigns since February 2026. The Moonshot exchange count covers activity observed from May through July. The report appeared on September 10, but that date does not show when Moonshot's route ended. Nor does the report say whether new accounts or alternative routes appeared. We cannot treat publication as proof that all rerouting stopped.

Anthropic reports taking enforcement action before publishing its account of the investigation. Publication may make similar operations harder, but the report does not measure that effect.

### Customer questions about data handling

If a request entered through Kimi and went to Claude, users and enterprise customers have reason to ask which services processed their data. Anthropic says it does not know whether Moonshot notified customers, leaving customers to seek an explanation from the service they used. Public disclosure may pressure Moonshot to explain its data flows and notification practices. That is a possible consequence, not a motive Anthropic confirms.

For enterprise buyers, response quality and data-processing commitments are separate concerns. A customer who chose a domestic service to keep processing within the country would need to check whether a foreign provider received the input. Coding-tool requests may include repository structure, code fragments, and configuration rather than an isolated question. Checking the affected requests and subprocessors could delay procurement or renewal, though the report does not measure customer departures or lost revenue.

### Service protection and commercial interests

Anthropic says it blocks requests and accounts when it identifies unauthorized use. Preventing its responses from being used to train another model is part of protecting its service. The allegation that Moonshot also sent customer prompts to Claude adds questions about data handling and the provider's commitments to its users.

Publication also makes Anthropic's detection methods and cases visible. It can support the company's argument that frontier-model safeguards and controls against unauthorized distillation matter. That may serve Anthropic's commercial interests as well. The report does not say how much these possible effects influenced the decision to publish.

Allowing a detected relay to continue would mean continuing to answer a competitor's users with Claude while accepting the possibility that the responses would become training data. The 23 million observed exchanges cannot all be counted as distinct training examples, but the reported scale makes service protection a practical concern as well as a stated principle. Additional investigative information would have to be weighed against serving costs and the usefulness of the material to competing models. A state agency evaluating intelligence and a model provider operating its own service have different interests. The report does not say whether Anthropic weighed those options.

Receiving sensitive material also creates operational decisions about who can read credential-bearing logs, when to delete them, and what to preserve for incident response. Neither automatic deletion nor indefinite retention resolves those decisions by itself. The report's introduction says Anthropic shared information with authorities and industry partners where appropriate. That does not establish a particular government relationship or the transfer of any specific material. Blocking, notification, limited information sharing, and a public report are separate actions. The document does not show that publication was the only legally available response.

### Privacy and regulatory questions

Anthropic says the labs' use of user conversations was likely inconsistent with privacy laws and their own terms of service. This is the company's legal assessment. The report does not include findings about individual consent, contract terms, which laws apply to each request, or a court's conclusion.

The public report could give regulators in the labs' home country a lead for examining the activity. China's Personal Information Protection Law sets requirements for providing personal information abroad, including notice and separate consent, while the Data Security Law separately regulates transfers of important data ([PIPL](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm), [Data Security Law](https://www.cac.gov.cn/2021-06/11/c_1624994566919140.htm)). The report alone is not enough to conclude that a specific provision was violated. A possible investigation by China's Cyberspace Administration or cancellation of a service license, mentioned by [AI Times](https://www.aitimes.com/news/articleView.html?idxno=215229), remains speculation. The sources cited here do not establish that such an investigation began.

### Detection and safeguards

Anthropic says it combines metadata with irregular-activity signals to associate proxy accounts with an organization. It says this lets it act against an organization rather than ban accounts one by one. Publishing that approach may warn other operators that distributed accounts do not guarantee anonymity. Outside observers do not have enough evidence to assess the accuracy of Anthropic's attribution.

Repeated enforcement may require operators to replace accounts and payment methods and adjust request distribution. Anthropic must also analyze new evasions and update detection, so the public evidence does not let us compare how quickly each side's costs grow. Publicly associating activity with a named lab can add customer-trust and regulatory costs beyond an account ban. It also increases the consequences of a mistaken attribution, which makes the limited evidence available for external scrutiny consequential.

The Zhipu case also appears in the report as an example of safeguards affecting an operation. Anthropic says Zhipu used Claude to improve post-training pipelines, evaluate outputs, and organize reasoning transcripts. As Zhipu prepared GLM 5.3, the report says, it began testing the cyber capabilities of US frontier models through CTF challenges, starting with Fable, which Anthropic described as a widely available model with stronger cyber safeguards. Anthropic claims Fable's safeguards interfered with those attempts, after which Zhipu moved to Opus 4.6 and another lab's model because it assessed their safeguards as weaker. This account comes from Anthropic's investigation, not an independent test.

The case can support Anthropic's argument to enterprise customers that safeguards affected an operator's choices. It does not mean the attempts ended. In the report's account, Zhipu selected other models. Making an attempt harder on one model and reducing misuse across the industry are different outcomes; the report does not provide a full account of the subsequent activity.

### Evidence for a policy debate

Before Anthropic's report appeared, [CNBC reported on September 3](https://www.cnbc.com/2026/09/03/anthropic-distillation-battle-turns-to-dark-web-china-concerns-swell.html) on the distillation dispute, account trading, and concerns about Chinese models. Anthropic's September 10 report adds examples and numbers that can enter US policy discussions about protecting frontier models.

Some Hacker News commenters read the report as lobbying for regulation that would benefit Anthropic. The report may be useful in policy discussions, and Anthropic has commercial interests in those discussions. The public document does not establish that lobbying was the company's reason for publishing.

## Anthropic's stated reason and what readers can infer

Anthropic says it believes it has a responsibility to disclose malicious misuse of its services. That is the reason the company gives. The report also publicizes its detection and enforcement work and argues that unauthorized distillation can carry risks beyond the target tasks. Disclosure may align with Anthropic's business interests, but the report does not tell readers which consideration mattered most.

Organizations choosing model services should check which subprocessors receive prompts, how cross-border transfers are handled, how long logs are kept, how model routing works, and when customers are notified. Those questions apply whenever one service routes a prompt to another model provider.

## Community reaction

The [main Hacker News thread about the report](https://news.ycombinator.com/item?id=49647300) and a [separate thread about Moonshot's rerouting](https://news.ycombinator.com/item?id=49656698) raised questions about privacy, distillation, technical plausibility, and Anthropic's incentives. The comments reflect users' views; they are not independent verification of the report.

Concerns about Anthropic's data practices were prominent. CrzyLngPwd summarized the report as a way to “tell us you are spying on your customers without saying you are spying on your customers.” qlte found the case studies unsettling because they were so specific and some of the people sounded more like researchers doing routine work than terrorists. One commenter compared it with Google being able to read email, while not publishing detailed accounts of a flagged person's inbox every month.

AlanYx asked how customers could trust that Anthropic was not retaining a whole class of flagged accounts without notice, given that reconstructing these sessions required retaining exchanges. Shank pointed to the training-use language in consumer terms. wongarsu replied that commercial terms and zero data retention agreements are stricter, and guessed that thousands of accounts routed through a proxy service were likely consumer accounts under weaker terms. In another comment, wongarsu drew a line between a disclosed tier where the provider can choose the model and selling Kimi while routing requests to Claude without notice. The report's description of detection also raised questions about Anthropic's own data retention and use.

The ethics debate concerned whether distillation should be treated differently from other model training. nacs argued that US labs had scraped books and websites without permission and now objected when others distilled their models. esafak said the same transformative-use argument used to defend US labs should apply to Chinese labs too. jchw argued that paid tokens are not copyrighted, training on them does not create a derivative work, and there was no authentication bypass or model leak, so at worst the conduct was a terms-of-use violation.

Others focused on how the data was collected. nojito and villish cited the report's allegations about false identities, stolen cards, and stolen API keys, arguing that the method was the problem. villish also argued that European labs could not legally use those methods and were disadvantaged as a result. qgin said silently routing a user's request through another model added deception that was different from reading publicly available material. pwinnski asked whether users who paid Kimi prices and received Claude had actually lost anything. DonsDiscountGas said this was the first case they had seen of a provider substituting another company's model without notice.

Some commenters questioned whether the relay was technically plausible. realusername and wren6991 argued that differences in how Kimi and Claude expose reasoning would make a Claude relay noticeable. zahlman said model writing styles differ enough to make long-term concealment difficult. KronisLV offered a counterexample, saying Kimi's thinking output had referred to Anthropic guidelines. xscott noted similar cross-contamination in local models from Meta and Poolside, which made that observation suggestive rather than proof.

Economics also came up. throwa356262 saw little reason for DeepSeek to send requests to a more expensive model. alex_duf replied that resale markets for accounts and tokens could change the unit cost. gjm11 read Anthropic's claim as an effort to obtain real user conversations for training rather than to save money. echelon added that synchronous routing could reveal how users respond to an answer, which may be useful for training.

Other commenters questioned attribution and motive. punk_ihaq noted that a device connecting from Yemen, Russia, or China could be a relay node for someone elsewhere, making attribution difficult. echelon read the report as a message to the government about bad actors Anthropic had stopped. Terretta argued that the real audience was Washington and that several labs publishing similar reports around the same time resembled regulatory-capture lobbying. enraged_camel and nsoonhui wondered whether distillation explained Chinese models' high benchmark scores. vopi pushed back, saying the full report calls distillation a legitimate training method and gives a fairer account than excerpts suggested.

The widest disagreement concerned how much weight to give the rerouting itself. woctordho wrote that Chinese users may already expect their activity to be monitored, so Anthropic seeing it might not concern them, and that account bans can be bypassed. bbor argued that the thread was underreacting to shared proxy infrastructure capable of carrying Chinese users' requests to a US company. [TechCrunch's coverage](https://techcrunch.com/2026/09/10/anthropic-details-distillation-campaigns-from-alibaba-moonshot-ai-and-deepseek/) gives a concise overview of the case.

## Further reading

- [Detecting and countering misuse of AI: September 2026 (PDF)](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf): Anthropic's original report
- [Claude API thinking documentation](https://platform.claude.com/docs/en/about-claude/models/extended-thinking-models): thinking blocks and signatures
- [HN: Detecting and countering misuse of AI](https://news.ycombinator.com/item?id=49647300): discussion of the report
- [HN: Moonshot serves Claude instead of Kimi](https://news.ycombinator.com/item?id=49656698): discussion of the rerouting allegation
- [TechCrunch: Anthropic details distillation campaigns](https://techcrunch.com/2026/09/10/anthropic-details-distillation-campaigns-from-alibaba-moonshot-ai-and-deepseek/): coverage of the cases
- [CNBC: Anthropic's distillation battle turns to the dark web](https://www.cnbc.com/2026/09/03/anthropic-distillation-battle-turns-to-dark-web-china-concerns-swell.html): background on the dispute
- [China's Personal Information Protection Law](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm): Cyberspace Administration of China, cross-border personal information rules
- [China's Data Security Law](https://www.cac.gov.cn/2021-06/11/c_1624994566919140.htm): Cyberspace Administration of China, important-data rules
- [AI Times: Kimi's unauthorized Claude rerouting controversy](https://www.aitimes.com/news/articleView.html?idxno=215229): Korean coverage, including speculation about CAC action

## Takeaways

Anthropic alleges that Moonshot and DeepSeek collected Claude responses and reasoning traces, and says it disrupted campaigns to protect its service. The report does not say exactly when Moonshot's rerouting stopped or whether replacement accounts or routes remained. Publication made Anthropic's investigation and interpretation public. It may affect customer scrutiny, service protection, and policy debates, but the document does not reveal which effect the company intended most.

The PLA link is Anthropic's assessment, not a confirmed attribution. A request reaching Anthropic's servers is not the same claim as the US government receiving state secrets. Anthropic says it does not know whether Moonshot notified customers. The report presents important allegations, but readers should keep its disclosed evidence separate from what remains unverified.

## References

1. [Detecting and countering misuse of AI: September 2026](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf): Anthropic, accessed 2026-10-15
2. [Claude API thinking documentation](https://platform.claude.com/docs/en/about-claude/models/extended-thinking-models): Anthropic, accessed 2026-10-15
3. [HN thread: Detecting and countering misuse of AI](https://news.ycombinator.com/item?id=49647300): Hacker News, accessed 2026-10-15
4. [HN thread: Moonshot serves Claude instead of Kimi](https://news.ycombinator.com/item?id=49656698): Hacker News, accessed 2026-10-15
5. [Anthropic details distillation campaigns from Alibaba, Moonshot AI, and DeepSeek](https://techcrunch.com/2026/09/10/anthropic-details-distillation-campaigns-from-alibaba-moonshot-ai-and-deepseek/): TechCrunch, accessed 2026-10-15
6. [Anthropic's distillation battle turns to the dark web as China concerns swell](https://www.cnbc.com/2026/09/03/anthropic-distillation-battle-turns-to-dark-web-china-concerns-swell.html): CNBC, accessed 2026-10-15
7. [China's Personal Information Protection Law](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm): Cyberspace Administration of China, accessed 2026-10-15
8. [China's Data Security Law](https://www.cac.gov.cn/2021-06/11/c_1624994566919140.htm): Cyberspace Administration of China, accessed 2026-10-15
9. [중국 '키미', 클로드 무단 우회 연결 파문…안보·기업 기밀 유출 논란](https://www.aitimes.com/news/articleView.html?idxno=215229): AI Times, accessed 2026-10-15
