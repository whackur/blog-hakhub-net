---
title: "Why Anthropic Went Public: Moonshot's Silent Claude Rerouting and the Strategic Value of a Dead Channel"
meta_title: ""
description: "Anthropic's September 2026 threat report says Moonshot silently rerouted Kimi customer requests to Claude, sensitive data included. How the relay worked, and why a company would publish and close that channel instead of quietly listening."
date: 2026-09-15T13:30:00+09:00
lastmod: 2026-09-15T15:30:00+09:00
image: "/images/posts/anthropic-moonshot-disclosure-strategy/cover.png"
categories: ["AI"]
tags: ["llm", "distillation", "ai-security", "anthropic", "kimi"]
author: "whackur"
translationKey: "anthropic-moonshot-disclosure-strategy"
draft: false
---

Footage pulled from hundreds of CCTV cameras across Chengdu, following one person. The user who uploaded it asked for an analysis of whether that person was behaving abnormally. They believed they were asking Kimi, a Chinese model. The system that actually received the request and wrote the answer was Claude, built by a US company.

That case sits in [Detecting and countering misuse of AI: September 2026](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf), the threat intelligence report Anthropic published on September 10, 2026. The report claims Moonshot AI, the company behind the Kimi models, quietly forwarded its own customers' requests to Claude and returned Claude's responses as if Kimi had written them. Along with the CCTV case, the rerouted traffic carried internal code and live credentials uploaded by an engineer at a major Chinese state-owned enterprise.

Which raises an obvious question. A channel that walks Chinese sensitive data into a US company's servers is, from an intelligence agency's seat, a dream collection window. Anthropic published instead, closing it in the open. Why?

This post runs in two halves. First, what the report actually claims and how the relay worked at a technical level. Then the calculus behind disclosure. The second half is interpretation, and I will say so wherever it is.

## What the report actually claims

Start with the epistemic status. Everything below is Anthropic's claim, resting on Anthropic's own investigation. None of it has been independently verified.

The report covers operations disrupted between December 2025 and August 2026, sorted into seven areas: cyber, influence operations, surveillance, scams and fraud, biological misuse, conventional weapons, and illicit distillation. This controversy comes out of the last one.

The core claim in the Moonshot case (GTG-16002) is short. Moonshot silently forwarded customer requests to Claude instead of processing them with Kimi, and users who thought they were talking to a Kimi model received Claude's responses. In one instance, Moonshot relayed almost 300,000 customer requests to Anthropic over a ten-day period, the vast majority routed to Claude Opus. The relay ran through a proxy network of 5,380 fraudulent accounts, most of which appeared to be located in Singapore and Japan.

Here are the disclosed distillation campaigns at a glance. The exchange counts are what Anthropic says it observed between May and July 2026; the report does not attach an observation window to the other figures.

| Organization | Scale claimed in the report |
|------|------|
| Moonshot (Kimi) | Over 23 million exchanges. Nearly 300,000 requests relayed in ten days, 5,380 fraudulent accounts |
| Alibaba (Qwen/Tongyi Lab) | Over 151 million exchanges, the largest distillation attack Anthropic has ever measured |
| Xiaomi (MiMo) | Over 400k requests across more than 1,500 accounts |
| DeepSeek | Same cross-session replay tactics, similar silent relaying |

The DeepSeek case (GTG-16001) adds a detail worth noting. According to the report, DeepSeek identified users running agent harnesses such as Claude Code, the Agent SDK, and OpenCode, and relayed those users' requests to Claude Opus. Xiaomi replayed MiMo user conversations to Claude through the OpenClaw and OpenCode harnesses, and the bulk of the distillation landed as the free MiMo-V2-Pro trial was ending. The claim is not that they shoveled everything across, but that they picked the expensive traffic.

### How the relay worked

For readers who do not live in this stack, here is the structure one layer at a time.

The normal picture is simple. A user sends a request to the Kimi app or API, a Moonshot server takes it, hands it to a Kimi model, and returns the result. The picture the report describes has one extra layer in the middle: a routing tier that sends some share of incoming requests to an outside API instead of the in-house model. That tier calls the Anthropic API, then dresses Claude's answer up as Kimi's and puts it on the user's screen. Nothing looks different from the user's side.

What Anthropic sees is a different picture again. Not one customer named Moonshot sending 300,000 requests, but 5,380 apparently unrelated accounts in Singapore and Japan each sending a modest trickle. Proxies are what connect the two pictures.

A proxy is a relay server that sends your request on your behalf. Residential proxies rent out IP addresses belonging to ordinary home internet connections. Datacenter IPs carry the fingerprints of bulk automation and are comparatively easy to filter; a request arriving from a home broadband address looks like a regular person. Anthropic treats China, Russia, and Iran as unsupported countries, so connecting directly from China gets blocked. Hence the requirement to look like an ordinary individual in a supported country. The Singapore and Japan locations mean very little on their own. Proxy exits explain why the accounts appear to sit there; they don't tell us why those particular exit points were picked or where the traffic actually originated.

The fraudulent account pool is the second layer on top: a reserve of accounts large enough that traffic can be spread thin instead of concentrated on one identity. Describing the Alibaba case specifically, the report says the first pool consisted of nearly 5,000 accounts and combined residential proxies, disposable emails, and virtual-card payments. The report does not lay out the same detail for Moonshot; what it establishes there is a pool of 5,380 fraudulent accounts, not that Moonshot used the identical recipe.

Divide the numbers and the reason for all that machinery becomes clear. 300,000 requests over ten days is 30,000 a day; spread evenly over 5,380 accounts, that is five or six requests per account per day. Real traffic is never that even, but the structure clearly does not require any single account to burn hot enough to stand out. Running this means automated account creation, a supply of payment instruments, proxy rental contracts, request distribution logic, and an operations loop that swaps in new accounts as old ones get banned. That is not a hobby project. It is infrastructure with a budget and staff behind it. MiniMax went further, per the report, and ran its own proxy network service through a shell company, a service that offers only Anthropic and OpenAI models and no Chinese ones at all.

The supply chain extends one step further. The report says SenseTime's distillation pipeline included transcripts purchased from third-party data vendors that harvest exchanges through intermediaries. There is a market where you can buy the harvest without running any accounts yourself, which is also why banning one account pool does not cut off the whole flow.

Which leaves customers with one question: what was the "Kimi performance" they were paying for? For the rerouted requests at least, the quality they experienced was Opus quality. One step further would be a step too far, though. The report does not claim Kimi's benchmark scores were produced this way. That connection is something the community added, and I will come back to it.

### Thinking signatures and cross-session replay

The most interesting technical piece is how the reasoning traces were extracted.

Distillation means training a smaller model on a larger model's outputs, using them as the answer key. What's in dispute here is not distillation as a technique, it's how the material was obtained.

And the material comes in grades. A model's final answer is worth far less as training data than the chain-of-thought it produced on the way there. Think of a problem set with answers only, versus one with full worked solutions. You need the record of which hypothesis got dropped and where the model corrected itself if you want to copy how it thinks rather than only what it said.

So Claude does not hand back its raw internal reasoning. It returns a signed value called a thinking signature. The caller can pass that signature back on the next turn, which lets the model continue from its earlier reasoning, but nobody can read what is inside it. Continuity without the text.

The report claims Moonshot and DeepSeek built a pipeline to break that seal: save the signature, open a fresh session, and submit it again. That is the cross-session replay. The signature was designed to mean something only inside the conversation that produced it, and replaying it in a different context converted it back into readable reasoning.

The countermeasures show how Anthropic understood the attack. Claude now summarizes its internal reasoning before responding. A summary keeps the skeleton of the conclusion and loses the dead ends, the abandoned hypotheses, and the self-corrections, which are exactly what a distiller wants, so summarizing cuts the unit price of anything harvested. Fable 5.1's preserved thinking attacks it from a different angle: new API accounts cannot alter the system prompt, the tool definitions, or the messages that precede the reasoning. A replay only works if you can attach a saved signature to a context other than its original one, and this blocks that manipulation directly. Anthropic also says it strengthened its classifiers alongside the Fable 5 launch and added identity verification for accounts registered in unsupported countries.

The report does not say when the pipeline stopped working. That gap matters later.

### The sensitive data that came through

As the report describes them:

The user assessed as likely PLA-affiliated loaded CCTV archive data about a single targeted individual into what they believed was Kimi, drawn from hundreds of cameras across Chengdu, including cameras outside PLA facilities and institutes, and asked whether the tracked person was behaving abnormally.

The engineer at a major PRC state-owned enterprise was building an internal system and exposed internal code and live credentials belonging to multiple major PRC companies, high-profile technology firms among them. The word doing the work there is "live." Not expired test keys. Access that works right now.

The DeepSeek cases run the same way. Full specifications, organizational structure, and strategic objectives for a PRC technology company's flagship AI program went across, as did live credentials for a Russian government database used by a Russian defense agency. Xiaomi's case brought a different category of data: names, contact information, and corporate data belonging to hundreds of Xiaomi users, in at least a dozen languages.

### What to hold onto while reading

The caveats, stated plainly.

The PLA link is Anthropic's assessment ("likely"), not verified attribution. Every sensitive data claim rests on Anthropic's own investigation. "Data reached Anthropic's servers" is a very different proposition from "the US government obtained state secrets." And the report itself says Anthropic does not know whether Moonshot told its customers about the rerouting. It does not assert they were kept in the dark. It says nobody at Anthropic knows.

## The calculus behind disclosure

From here on, this is interpretation. Anthropic's internal reasoning is not available to us, so the useful move is to work out how the numbers look from a company's seat.

### The channel was already closed by publication day

The observation window runs May through July 2026, the activity is described as disrupted, and publication came on September 10. There was no live channel that silence could have preserved.

Proxy networks are consumables. The moment an account pool gets banned, that collection window is worth zero. The attacking side knows this and rebuilds; the defending side knows it too, which is why nobody holds a particular batch of accounts open for sentimental reasons. So disclosure did not kill a living channel. It cashed out a spent one.

There is a hole in that reasoning, and it should be named. The report does not say when the pipeline was shut down, or whether a fresh account pool stood up afterward. "Already closed" is itself an inference resting on Anthropic's description.

### Keeping the channel open had a price tag

This is the part that gets skipped most often. "Why not just listen quietly" assumes listening is free. It was not.

To keep the channel open, Anthropic had to keep supplying Claude responses. Those responses were the product Moonshot was selling to its own customers under the Kimi name, so maintaining the window meant maintaining a competitor's product quality by hand. The fraudulent account pool would have to keep running too, which means detecting it and choosing not to ban it, a legally distinct position from being breached without knowing. The distillation would have to be tolerated: 23 million exchanges observed between May and July alone, high-grade training data feeding a competing model at that volume. And Anthropic would have to keep receiving surveillance data it assessed as PLA-linked, plus credentials for another country's government databases, with full knowledge that it was happening.

For an intelligence agency, most of that bill is somebody else's money. A competitor's growth never lands on its balance sheet, and the value of the collection window swamps every other line. For a company it inverts. Each relayed response is a transfer of capability, and the cost posts to its own books. Uncertain intelligence value on one side, certain subsidy on the other.

If the opening question felt strange, that is not because the question was badly posed. It quietly borrows an intelligence agency's ledger and hands it to a company. Change the principal and the answer changes by itself. Separating those two ledgers is, I think, the key to the whole case.

To be clear, none of this implies any particular relationship between Anthropic and the US government. The report says only that it shared with authorities and industry partners where appropriate. The document does not support going further.

### The incoming data was a liability

The legal shape points the same direction.

Receiving data unknowingly before detection and knowingly holding onto it afterward are different things. The first is an accident, the second is a decision. A company that knows another state's military-linked surveillance data is landing on its servers and keeps the channel open starts to look like an unregistered intelligence collector. From that point on, the question it has to answer is not how it handled the data but why it kept taking delivery.

Credentials are hotter still. Live credentials are keys that open doors today. Holding them is an incident waiting to happen, an insider risk, and immediate damage if they leak. Add the Russian government database credentials from the DeepSeek case and more than one jurisdiction is in play.

A company holding that material has essentially one clean exit: close the channel, share with authorities and industry partners where appropriate, and disclose. The report says it did share, using exactly that phrase. If anyone stands to gain from keeping such a stream flowing, it is a state agency, not a private firm carrying the regulatory and reputational risk alone.

## What disclosure buys

If publishing is how you cash out a channel whose usefulness is over, what form does the cash arrive in? At least five.

### Trust damage inside the rerouting labs' customer base

The most direct hit lands on Moonshot's and DeepSeek's customer lists.

Put yourself in a Chinese enterprise buyer's chair. Often the whole reason for picking a domestic model was to keep data inside the country. If your prompts may have been processed through a US company's servers instead, a list of questions appears before the next renewal. Which of my requests went out? Do logs of that exist? Was Anthropic on the subprocessor list in my contract? What did the cross-border transfer clause say? Weak answers stretch out procurement reviews, and stretched reviews become churn.

The severity also varies by customer segment. In the DeepSeek case the report says the targeted users were developers running harnesses like Claude Code and OpenCode. What those users hand a model is not a short question but a working context: repository structure, code fragments, sometimes configuration. One leaked chat and a cross-section of an internal codebase are incidents of different weight.

What is odd here is that the gap in the report works against the labs rather than for them. Anthropic wrote that it does not know whether Moonshot notified customers. A confirmed lie would have a bounded scope. "We do not know" leaves every customer to check for themselves.

wongarsu drew the line well on Hacker News: if Moonshot had sold a "mystery model" tier, openly labeled as possibly routing anywhere, there would be nothing to object to. Pretending to serve Kimi while proxying Claude is where the wrong sits.

### China's own data rules, pointed the other way

The second payoff has an ironic shape.

China has the Data Security Law (DSL) and the Personal Information Protection Law (PIPL). The DSL sorts data into tiers by sensitivity and tightly restricts moving the higher tiers out of the country. PIPL requires separate consent and a government security assessment before personal information crosses the border, with penalties that reach fines and suspension of operations. Both were built mainly with foreign companies exporting Chinese data in mind.

If the report's account is accurate, those provisions now point at Chinese companies. Chinese users' requests left the country for a US company's servers without consent. Where user names and contact details were mixed in, as the Xiaomi case suggests, the personal information side bites more directly. A document published by a US company can end up in a Chinese regulator's evidence file. Anthropic has no way to regulate these labs, so the report reaches for the labs' own home regulator instead.

Draw the line clearly here. The possibility of a Cyberspace Administration of China (CAC) investigation or a revoked service license, raised in an [AI Times article](https://www.aitimes.com/news/articleView.html?idxno=215229), is speculation. There is no confirmed reporting that any such investigation opened. A rule existing and a rule firing are separate facts.

### Deterrence advertising

The third payoff is not addressed to readers. It is addressed to every other lab currently sizing up a similar pipeline.

In its disruption section the report says Anthropic combined metadata with irregular-activity signals to attribute proxy networks to specific organizations. That one sentence carries a clear market message: scatter your accounts however you like, hide behind residential IPs, and a company name can still get attached to the traffic.

Look at the cost structure and the effect makes sense. The attacking side keeps spending cash on account creation, payment instruments, proxy rental, and replacing banned accounts. The defending side already holds metadata for every request, and each takedown adds another labeled example for the next round of detection. Standing up a new account pool scales roughly linearly in cost, while detection gets better as data accumulates. Organization-level attribution adds one more line to the attacker's bill, converting an anonymous technical risk into reputational and regulatory exposure.

How accurate that attribution is, of course, cannot be checked from outside. The community said so immediately.

### A record of safeguards actually working

The fourth is the Zhipu story, the best-selling paragraph in the whole report.

Per the report, Zhipu used Claude to refine post-training pipelines, to judge outputs, and to clean and normalize reasoning transcripts. Ahead of the GLM 5.3 launch it changed direction and began targeting the cyber capabilities of leading US frontier models through CTF challenges. The first target was Fable, Anthropic's top generally accessible model, which carries strengthened cyber safeguards.

Zhipu gave up. Once the safeguards kept degrading its attacks, it dropped Fable and moved to Opus 4.6 and another US lab's top model. The report states the reason outright: Zhipu assessed those safeguards as weaker.

Safety features usually get treated as a cost line. More refusals, more friction, more complaints. Here there is a documented case of an attacker changing targets because of them. That sentence goes straight into an enterprise procurement review.

The same paragraph carries an uncomfortable implication. The attacker did not disappear. It moved next door. A win for Fable is a relocation for the industry, and the report does not name which house it moved into.

### Evidence for the policy fight

The fifth payoff is in Washington.

The US debate over protecting frontier models was already warming up. [CNBC's reporting](https://www.cnbc.com/2026/09/03/anthropic-distillation-battle-turns-to-dark-web-china-concerns-swell.html) in early September covered the distillation fight spilling into dark-web account trading as China concerns grew. What that debate is short on is concrete primary material: numbers with scale attached, organization names, step-by-step accounts of method, and cases showing what actually came through. The report supplies all of it at once.

There is always a competing reading, and I do not dismiss it. A significant share of the community treats the report as lobbying material aimed at regulatory capture. Evidence being useful and its publisher having an interest in publishing it are both true at once. Read the document with both in the calculation.

## The two motives coexist

The report states its reason for publishing directly: "we believe we have a responsibility to disclose malicious misuse of our services."

There is no reason to treat that as insincere. The strategic gains above are also real. The two do not exclude each other. Corporate decisions get easy when principle and interest point the same way; the hard cases are the ones where they diverge, and this was not one of them. Whether Anthropic would have made the same call with no strategic upside is not something this report can answer, and I do not think it needs to.

For anyone choosing a model vendor the lesson is drier. The guarantee that whoever writes the response is also whoever sends the invoice holds only when a contract says so. Subprocessor lists, cross-border transfer clauses, and log retention policies are the items that get waved through on a procurement checklist, and this case is a demonstration that they were never a formality. None of it is specific to Chinese models either. Any customer who cannot verify by contract who actually produces the answers is standing in the same place.

## Community reaction

The [main Hacker News thread on the report](https://news.ycombinator.com/item?id=49647300) and a [separate thread on the Moonshot rerouting](https://news.ycombinator.com/item?id=49656698) split along far more lines than I expected. What stands out is how few commenters took Anthropic's side.

The sharpest pushback aimed at Anthropic itself. CrzyLngPwd summarized the report as a way to "tell us you are spying on your customers without saying you are spying on your customers." qlte explained the discomfort more concretely: the case studies are unsettling precisely because they are so specific, and some of the people described sound less like terrorists than like researchers doing their day jobs. The comparison offered was Google, which can read your email, but does not publish monthly blog posts detailing what it found in one flagged person's inbox.

That thread produced the most practically sharp question in either discussion. AlanYx pointed out that reconstructing these sessions requires retaining the exchanges, and asked how an average customer is supposed to trust that a whole class of flagged accounts is not being retained without notice. Shank noted the training-use language in the consumer terms; wongarsu added that those are the consumer terms, that the commercial terms and zero-data-retention agreements are considerably stricter, and that thousands of accounts run through a proxy service are most likely consumer accounts governed by the weaker set. The report advertises Anthropic's detection capability and puts its own data handling on the table in the same motion.

The distillation ethics argument ran hot, as expected. nacs argued that US labs scraped the internet and books without permission and now cry foul when someone distills them. esafak made the symmetry explicit: if learning and distillation are transformative and legal for American labs, the same logic covers Chinese ones. jchw laid it out step by step, arguing that tokens you paid for are not copyrighted, training on them creates no derivative work, there is no authentication bypass and no model leak, and at worst it is a terms-of-use violation.

The counterargument focused elsewhere. nojito and villish said the problem is the method, not the distillation, citing the report's description of proxy services using false identities, stolen credit cards, and stolen API keys, and adding that European labs cannot legally do any of this and lose ground because of it. qgin drew the distinction that this case adds man-in-the-middle deception on top, which is not the same as reading what anyone could read. From the other direction, pwinnski asked whether users got Claude at Kimi prices, deceptive but hardly a loss, and DonsDiscountGas said this is the first case they had seen of a provider substituting another company's model with no disclosure at all.

Technical skepticism was a strong current too. realusername and wren6991 landed on the same point: Kimi serves full reasoning traces while Claude hides them, so a Claude relay should have been obvious to users immediately. zahlman added that model-to-model differences in writing style make this hard to sustain. Evidence pointing the other way showed up as well. KronisLV reported seeing Kimi's thinking output reference Anthropic's guidelines on many occasions, though xscott balanced that by reporting similar cross-contamination in local models from Meta and Poolside, which makes it suggestive rather than probative. Economics came up: throwa356262 saw no reason for DeepSeek to relay requests to a far more expensive model, and alex_duf answered that a parallel market in resold accounts and tokens changes the unit price. gjm11 clarified that Anthropic's claim is about acquiring real user conversations for training, not about saving money, and echelon noted that you can collect questions asynchronously, but relaying synchronously also lets you run RLHF on what users do after the response.

Doubts about motive were loud. punk_ihaq observed that machines connecting from Yemen, Russia, or China may be relay nodes for actors from entirely different states, so attribution is not trivial. echelon read the report as a message to government along the lines of "look at the bad guys we stopped." Terretta went further, arguing the real audience is Washington and that several labs publishing similar reports in the same window is the standard choreography of regulatory-capture lobbying. enraged_camel and nsoonhui raised the benchmark suspicion, wondering whether this explains how the Chinese models scored so well. vopi pushed back that people were reacting to excerpts: read in full, the report explicitly calls distillation a legitimate training method and frames things more fairly than the thread assumed.

The widest gap in temperature came at the end. woctordho wrote from a Chinese user's perspective that people there are used to everything they say being observed, so Anthropic seeing it too is not a big problem, and that there are plenty of ways around account blocking. From the opposite pole, bbor accused the thread of under-reacting: the distillation ethics argument is beside the point, and the genuinely alarming item is that shared proxy infrastructure exists to carry millions of Chinese users' requests to a US company. For a compact summary of the whole affair, [TechCrunch's coverage](https://techcrunch.com/2026/09/10/anthropic-details-distillation-campaigns-from-alibaba-moonshot-ai-and-deepseek/) is a good starting point.

## Further reading

- [Detecting and countering misuse of AI: September 2026 (PDF)](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf): Anthropic's original report
- [HN: Detecting and countering misuse of AI](https://news.ycombinator.com/item?id=49647300): main discussion thread
- [HN: Moonshot serves Claude instead of Kimi](https://news.ycombinator.com/item?id=49656698): thread focused on the Moonshot case
- [TechCrunch: Anthropic details distillation campaigns](https://techcrunch.com/2026/09/10/anthropic-details-distillation-campaigns-from-alibaba-moonshot-ai-and-deepseek/): news summary
- [CNBC: Anthropic's distillation battle turns to the dark web](https://www.cnbc.com/2026/09/03/anthropic-distillation-battle-turns-to-dark-web-china-concerns-swell.html): background on the wider distillation fight
- [AI Times: Kimi's unauthorized Claude rerouting controversy (Korean)](https://www.aitimes.com/news/articleView.html?idxno=215229): Korean coverage, includes the speculative CAC angle

## Takeaways

Back to the opening question: why publish and close a channel carrying Chinese sensitive data?

The answer sits in the question's premise. The party that profits from keeping such a channel open is an intelligence agency, not a company. From Anthropic's seat the channel was already blocked by publication day, the incoming data was a legal and reputational liability rather than an asset, and the cost of keeping it open arrived every month in the form of a competitor's product and model getting better. Disclosure converted a spent collection window into five assets: trust damage to the rerouting labs, pressure borrowed from China's own data rules, deterrence advertising, a record of safeguards changing an attacker's behavior, and evidence for the policy fight. The stated duty to disclose and those gains do not conflict. They point to the same decision.

A few things stay attached to all of it. Every factual claim here rests on Anthropic's own investigation. The PLA link is an assessment, not a finding. Data reaching a US company's servers is not the same as a government obtaining secrets. CAC sanctions are speculation. The useful posture with a document like this is neither to swallow it whole nor to dismiss it whole, but to keep sorting what can be checked from what cannot.

## References

1. [Detecting and countering misuse of AI: September 2026](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf): Anthropic, accessed 2026-09-15
2. [HN thread: Detecting and countering misuse of AI](https://news.ycombinator.com/item?id=49647300): Hacker News, accessed 2026-09-15
3. [HN thread: Moonshot serves Claude instead of Kimi](https://news.ycombinator.com/item?id=49656698): Hacker News, accessed 2026-09-15
4. [Anthropic details distillation campaigns from Alibaba, Moonshot AI, and DeepSeek](https://techcrunch.com/2026/09/10/anthropic-details-distillation-campaigns-from-alibaba-moonshot-ai-and-deepseek/): TechCrunch, accessed 2026-09-15
5. [Anthropic's distillation battle turns to the dark web as China concerns swell](https://www.cnbc.com/2026/09/03/anthropic-distillation-battle-turns-to-dark-web-china-concerns-swell.html): CNBC, accessed 2026-09-15
6. [중국 '키미', 클로드 무단 우회 연결 파문…안보·기업 기밀 유출 논란](https://www.aitimes.com/news/articleView.html?idxno=215229): AI Times (Daejun Lim), accessed 2026-09-15
