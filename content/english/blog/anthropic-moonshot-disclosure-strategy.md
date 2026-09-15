---
title: "Why Anthropic Went Public: Moonshot's Silent Claude Rerouting and the Strategic Value of a Dead Channel"
meta_title: ""
description: "Anthropic's September 2026 threat report says Moonshot silently rerouted Kimi customer requests to Claude, sensitive data included. We look at why a company would disclose and kill that channel instead of quietly watching it."
date: 2026-09-15T13:30:00+09:00
lastmod: 2026-09-15T13:30:00+09:00
image: "/images/posts/anthropic-moonshot-disclosure-strategy/cover.png"
categories: ["AI"]
tags: ["llm", "distillation", "ai-security", "anthropic", "kimi"]
author: "whackur"
translationKey: "anthropic-moonshot-disclosure-strategy"
draft: false
---

Anthropic's threat intelligence report [Detecting and countering misuse of AI: September 2026](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf), published on September 10, 2026, contains one claim that stops you cold. Moonshot AI, the company behind the Kimi models, allegedly forwarded its own customers' requests to Claude without telling them, then displayed Claude's responses as if Kimi had produced them. Some of those rerouted requests carried sensitive material: CCTV archive analysis of a single tracked individual in Chengdu, submitted by a user Anthropic assesses as likely PLA-affiliated, and internal code plus live credentials from an engineer at a major PRC state-owned enterprise.

That raises an obvious question. A channel through which Chinese sensitive data flows into a US company's servers is, from an intelligence agency's point of view, a dream collection window. Anthropic chose to publish instead, killing the channel in the open. Why? This post first lays out what the report actually claims, then works through the strategic calculus of disclosure.

## What the report actually claims

Let's be precise about the epistemic status first. Everything below is Anthropic's own claim, based on Anthropic's own investigation. None of it has been independently verified by a third party.

The report covers operations disrupted between December 2025 and August 2026, and the unauthorized distillation section is the one at issue here. The core claim in the Moonshot case (GTG-16002): Moonshot silently forwarded customer requests to Claude instead of processing them with Kimi, and users who thought they were talking to a Kimi model received Claude's responses. In one instance, Moonshot relayed almost 300,000 customer requests to Anthropic over a ten-day period, the vast majority routed to Claude Opus. The relay ran through a proxy network of 5,380 fraudulent accounts, most of them appearing to be in Singapore and Japan.

Here are the disclosed distillation campaigns at a glance. The exchange counts are what Anthropic says it observed between May and July 2026; the report does not attach an observation window to the other figures.

| Organization | Scale claimed in the report |
|------|------|
| Moonshot (Kimi) | Over 23 million exchanges. Nearly 300,000 requests relayed in ten days, 5,380 fraudulent accounts |
| Alibaba (Qwen/Tongyi Lab) | Over 151 million exchanges, the largest distillation attack Anthropic has ever measured |
| Xiaomi (MiMo) | Over 400k requests across more than 1,500 accounts |
| DeepSeek | Same cross-session replay tactics, similar silent relaying |

The technically interesting part is the chain-of-thought extraction. Claude does not expose its raw internal reasoning; instead it seals the reasoning behind a signed value called a thinking signature. Raw reasoning traces are the single most valuable training data for distillation, which is exactly why they are protected: downstream callers get the signature, not the text. According to the report, Moonshot and DeepSeek built a pipeline that saved the thinking signature and replayed it in a fresh session to recover the sealed reasoning. That is a direct circumvention of the control.

The report does not say when that pipeline stopped working. It does list countermeasures. Claude now summarizes its internal reasoning before responding, which makes a harvested transcript less useful as training data. Fable 5.1 introduced preserved thinking, which blocks new API accounts from altering the system prompt, the tool definitions, or the messages that precede the reasoning. Anthropic also says it strengthened its classifiers alongside the Fable 5 launch and added identity verification for accounts registered in unsupported countries, naming China, Russia, and Iran.

The sensitive data cases, as the report states them: a user assessed as likely PLA-affiliated used what they believed was Kimi to load CCTV archive data about one targeted individual, drawn from hundreds of cameras across Chengdu, including cameras outside PLA facilities and institutes, and asked whether the person was behaving abnormally. Separately, an engineer at a major PRC state-owned enterprise used Kimi to build an internal system, exposing internal code and live credentials from multiple major PRC companies, including high-profile technology firms.

Now the caveats, stated plainly. The PLA link is Anthropic's assessment ("likely"), not verified attribution. The sensitive data claims rest entirely on Anthropic's own investigation. "Data reached Anthropic's servers" is a very different statement from "the US government obtained state secrets." And the report itself says Anthropic does not know whether Moonshot ever told its customers their requests were being rerouted to a third party.

## The strategic calculus of disclosure

From here on, this is interpretation grounded in the report's facts. We cannot know Anthropic's internal motives, so the useful move is to ask how the calculus looks from a company's seat.

### The channel was already dead at publication

The report's observation window runs May through July 2026, and the activity is described as disrupted, meaning blocked, well before the September 10 publication. There was no live channel that silence would have preserved. Proxy networks are disposable and get rebuilt fast; the moment a batch of accounts is banned, that particular collection window is worthless. Read that way, disclosure did not kill a living channel. It monetized a dead one.

### For a company, that data is a liability, not an asset

Imagine a company that knows PLA-linked surveillance data and live SOE credentials keep arriving on its servers and quietly keeps receiving them. That company starts to look like an unregistered intelligence collector. Receiving data unknowingly before detection and knowingly retaining it after detection are different things, legally and reputationally. The only legitimate exit for a company is to share with authorities and industry partners, which the report says happened "where appropriate," and to disclose. If anyone benefits from keeping such a stream flowing, it is a state agency, not a private firm carrying regulatory risk and public scrutiny.

### Disclosure itself is the weapon

Publishing is how you cash out a dead channel, and the payoff runs in at least five directions.

First, customer trust collapses for the labs that did the rerouting. For a Chinese enterprise customer, "the data I gave a domestic model was processed by a US company" translates directly into churn and harder procurement reviews. Second, China's own data-sovereignty regime can be turned against Chinese labs. The Data Security Law (DSL) and the Personal Information Protection Law (PIPL) restrict unauthorized cross-border data transfers, and this report is ready-made evidence. Note that the possibility of a Cyberspace Administration of China (CAC) investigation or sanction, raised in an [AI Times article](https://www.aitimes.com/news/articleView.html?idxno=215229), is speculation, not an established fact. Third, deterrence advertising: demonstrating that Anthropic can attribute proxy networks to specific organizations raises the cost of distillation for every lab watching. Fourth, a proof point for safeguards. The report says Zhipu, preparing the GLM 5.3 launch, initially targeted Fable, Anthropic's top generally accessible model with strengthened cyber safeguards, gave up after the safeguards degraded its attacks, and switched to Opus 4.6 and another US lab's top model expressly because it assessed those safeguards as weaker. That is a documented case of safeguards changing an attacker's choices. Fifth, the report supplies primary-source evidence for US frontier-model protection arguments, a debate that was already heating up, as [CNBC's reporting](https://www.cnbc.com/2026/09/03/anthropic-distillation-battle-turns-to-dark-web-china-concerns-swell.html) on dark-web distillation and China concerns shows.

### The channel was never free eavesdropping

This is the point people miss. Keeping the channel alive meant Anthropic had to keep supplying Claude responses, which Moonshot then sold to its customers as a service and distilled into training data. Maintaining the window meant continuously funding a competitor's product quality and model improvement in exchange for intelligence of uncertain value. For a company, that is a plainly bad trade. An intelligence agency would run the numbers differently: a competitor's growth is not its loss, and the collection window is worth far more to it. The original question, "why not keep listening," is what you get when you apply an intelligence agency's ledger to a company. Separating those two ledgers is, I think, the key to the whole case.

### The two motives coexist

The report states its reason for publishing directly: "we believe we have a responsibility to disclose malicious misuse of our services." There is no reason to treat that stated safety duty as insincere. The strategic benefits above are also real. The two are not mutually exclusive. Corporate decisions get easy when principle and interest point the same way, and this disclosure looks like exactly that situation.

## Community reaction

The [main Hacker News thread on the report](https://news.ycombinator.com/item?id=49647300) (243 comments) and a [separate thread on the Moonshot rerouting](https://news.ycombinator.com/item?id=49656698) split along several lines.

The sharpest pushback aimed at Anthropic itself. One commenter (CrzyLngPwd) summarized the report as a way to "tell us you are spying on your customers without saying you are spying on your customers." Reconstructing rerouted sessions in this level of detail proves the company can inspect request contents, which is not a comfortable fact for enterprise customers either.

The distillation ethics debate ran hot. Some commenters (esafak, jchw, and others) argued distillation is comparable to learning from the open web. Others (villish, qgin, and others) countered that the real violations are the fraudulent accounts, the stolen credentials, and the man-in-the-middle deception toward customers. wongarsu drew the line cleanly: if Moonshot had sold a disclosed "mystery model" tier, there would be nothing to object to; pretending to serve Kimi while proxying Claude is the bad part.

There was a technical plausibility debate too. KronisLV reported having seen Kimi's thinking output reference Anthropic guidelines, which fits either relaying or distillation. realusername pushed back that Kimi exposes full thinking traces while Claude hides them, and asked how relaying squares with that. echelon noted that synchronous relaying lets the operator also collect user behavior after the response, useful for RLHF. Benchmark skepticism showed up (enraged_camel connected the rerouting to how these labs "scored so high in benchmarks"), and so did attribution skepticism (punk_ihaq: machines connecting from Yemen, Russia, or China could be VPN exits for actors elsewhere; attribution is not trivial). echelon also read the report as regulatory positioning, essentially a message that the US should regulate AI.

One comment came from a Chinese user's perspective: woctordho wrote that people in China are accustomed to surveillance, so Anthropic seeing the data is "not a big problem," and workarounds exist. bbor argued the opposite, that the thread was under-reacting: the insane part, in that reading, is the existence of shared proxy infrastructure routing millions of Chinese users' requests to a US company, which dwarfs the distillation ethics question. For a compact news summary of the whole affair, [TechCrunch's coverage](https://techcrunch.com/2026/09/10/anthropic-details-distillation-campaigns-from-alibaba-moonshot-ai-and-deepseek/) is a good starting point.

## Further reading

- [Detecting and countering misuse of AI: September 2026 (PDF)](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf): Anthropic's original report
- [HN: Detecting and countering misuse of AI](https://news.ycombinator.com/item?id=49647300): main discussion thread
- [HN: Moonshot serves Claude instead of Kimi](https://news.ycombinator.com/item?id=49656698): thread focused on the Moonshot case
- [TechCrunch: Anthropic details distillation campaigns](https://techcrunch.com/2026/09/10/anthropic-details-distillation-campaigns-from-alibaba-moonshot-ai-and-deepseek/): news summary
- [CNBC: Anthropic's distillation battle turns to the dark web](https://www.cnbc.com/2026/09/03/anthropic-distillation-battle-turns-to-dark-web-china-concerns-swell.html): background on the wider distillation fight
- [AI Times: Kimi's unauthorized Claude rerouting controversy (Korean)](https://www.aitimes.com/news/articleView.html?idxno=215229): Korean coverage, includes the speculative CAC angle

## Takeaways

Back to the opening question: why publish and kill a channel that carried Chinese sensitive data? The answer lives in the question's hidden premise. The party that profits from keeping such a channel open is an intelligence agency, not a company. From Anthropic's seat, the channel was already blocked by publication day, the incoming data was a legal and reputational liability rather than an asset, and keeping the window open would have meant continuously improving a competitor's product and model. Disclosure converted a dead channel into five kinds of value: trust damage to the rerouting labs, borrowed leverage from China's own data-export rules, deterrence, a safeguards proof point, and policy evidence. The stated duty to disclose and the strategic gains do not conflict; they point to the same decision. Hold on to the caveats throughout, though: every factual claim here rests on Anthropic's own investigation, the PLA link is an assessment, and CAC sanctions remain speculation.

## References

1. [Detecting and countering misuse of AI: September 2026](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf): Anthropic, accessed 2026-09-15
2. [HN thread: Detecting and countering misuse of AI](https://news.ycombinator.com/item?id=49647300): Hacker News, accessed 2026-09-15
3. [HN thread: Moonshot serves Claude instead of Kimi](https://news.ycombinator.com/item?id=49656698): Hacker News, accessed 2026-09-15
4. [Anthropic details distillation campaigns from Alibaba, Moonshot AI, and DeepSeek](https://techcrunch.com/2026/09/10/anthropic-details-distillation-campaigns-from-alibaba-moonshot-ai-and-deepseek/): TechCrunch, accessed 2026-09-15
5. [Anthropic's distillation battle turns to the dark web as China concerns swell](https://www.cnbc.com/2026/09/03/anthropic-distillation-battle-turns-to-dark-web-china-concerns-swell.html): CNBC, accessed 2026-09-15
6. [중국 '키미', 클로드 무단 우회 연결 파문…안보·기업 기밀 유출 논란](https://www.aitimes.com/news/articleView.html?idxno=215229): AI Times (Daejun Lim), accessed 2026-09-15
