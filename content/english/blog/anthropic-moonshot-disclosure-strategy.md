---
title: "Why did Anthropic publish its report on alleged Kimi-to-Claude routing?"
meta_title: ""
description: "Why disclosing alleged Kimi-to-Claude routing can serve Anthropic despite incoming sensitive data, and how reasoning replay and privacy scrutiny change the tradeoff."
date: 2026-09-15T13:30:00+09:00
lastmod: 2026-10-15T11:40:30+00:00
image: "/images/posts/anthropic-moonshot-disclosure-strategy/disclosure-cover-20261015.webp"
categories: ["AI"]
tags: ["llm", "distillation", "ai-security", "anthropic", "kimi"]
author: "whackur"
translationKey: "anthropic-moonshot-disclosure-strategy"
draft: false
---

If sensitive information was reaching Claude, why would Anthropic reveal the route? **A model provider may gain more from limiting unauthorized use and alerting customers to a data-handling problem than from continuing to observe the inputs.** Answering a competitor’s users consumes compute and may produce training material for that competitor. Publication also reaches users and enterprise buyers whom account bans alone cannot inform. These incentives explain why disclosure can make sense; they do not establish how Anthropic made its internal decision.

In its [September 2026 report](https://www.anthropic.com/threat-intelligence-report-september-2026), Anthropic gives a stated reason: responsibility to disclose malicious misuse of its services. It also says the findings should help other developers detect abuse and help society respond. The allegation that Moonshot sent Kimi requests to Claude is one case in that report. Treating the arrival of sensitive inputs as an intelligence success overlooks both the provider’s interest in protecting its service and the rights of the people whose data arrived.

## Serving customer requests while collecting training material

The Moonshot case, GTG-16002, connects two alleged activities. Moonshot sent some customer requests to Claude instead of Kimi and returned Claude’s responses to users. It also saved some exchanges and extracted reasoning transcripts for model training. **Routing determines how a live request is served; distillation uses collected outputs to train another model.** Evidence of routing alone would not establish training. Anthropic alleges both here. ([Original PDF, pp. 148-149](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf))

The reported flow takes a user request through Moonshot and a network of proxy accounts to Claude, then returns Claude’s answer to the user. Anthropic says one instance involved almost 300,000 requests over ten days, mostly to Opus. It describes 5,380 fraudulent accounts, most apparently located in Singapore and Japan. The exact routing implementation and account-level operating records are not public.

This differs from sending a large, prepared set of questions to a model and collecting its answers. Real users supply the tasks, and a response becomes both the service’s answer and potential training material. In Anthropic’s account, corporate documents or code accompanying a request travel with it. The report does not establish that all Kimi requests were forwarded or that Kimi’s overall performance came from Claude.

The sensitive-data examples make the stakes concrete. Anthropic describes a user submitting an archive from hundreds of CCTV cameras in Chengdu to assess whether a particular person was behaving abnormally. Its assessment that the user was likely affiliated with the People’s Liberation Army (PLA) is Anthropic’s attribution. Another example concerns an engineer at a major Chinese state-owned enterprise whose requests allegedly included internal code and live credentials from several companies. “Live” describes their status during the investigation, not their validity today. ([PDF, p. 149](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf))

The report explicitly says Anthropic does not know whether Moonshot notified customers about the routing. That prevents a blanket claim that every customer was unaware. The alleged mismatch between the service a customer selected and the company receiving its input still warrants examining data-processing commitments. Attribution and case details come from Anthropic’s own investigation; the cited material contains no independent audit of them.

## An API that can reuse encrypted reasoning

Training material can include intermediate reasoning, or chain of thought (CoT), as well as final answers. Anthropic alleges that Moonshot exploited Claude’s thinking functionality to obtain those transcripts. Understanding the claim requires separating visible reasoning from the data returned to the API on a later call.

The [current Claude API documentation](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-encryption) distinguishes these fields:

| API element | Documented role |
| --- | --- |
| `thinking` inside a `thinking` block | Readable reasoning or a summary, depending on model and settings; it may also be empty. |
| `signature` in the same block | Contains encrypted full reasoning. The API uses it for verification; callers return it unchanged rather than interpreting or parsing it. |
| `data` inside a `redacted_thinking` block | Encrypted reasoning withheld for safety. This is a separate block type. |

Calling the signature readable reasoning would be wrong. Describing it solely as a verification tag unrelated to reasoning data would also be inaccurate. Despite the field’s name, current documentation explicitly says it contains encrypted full thinking.

Sending earlier thinking back to the API is normal functionality. When Claude calls a tool and waits for its result, the caller returns the previous thinking blocks unchanged so Claude can continue the same response. ([Preserving thinking blocks during tool use](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks))

What the report calls cross-session replay allegedly involved saving a signature, reusing it in a new session, and eliciting the associated reasoning transcript from Claude. This is different from independently decrypting ciphertext. The security problem concerns both the model’s ability to reuse encrypted reasoning and the controls that prevent it from exposing that reasoning. Anthropic does not publish Moonshot’s full requests or reproduction code, so the precise conditions for success cannot be verified from the report. ([PDF, pp. 148-149](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf))

Anthropic describes reasoning summaries and preserved thinking as defenses. Current documentation says preserved thinking, starting with Fable 5.1, checks whether the preceding system prompt, tools, or messages have changed. This prefix check applies by default to accounts created on or after August 31, 2026, at 00:00 UTC. For older accounts it applies to requests that send the specified setting. Those conditional protections are not a guarantee that every form of replay is impossible on every account. ([Current API enforcement conditions](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-thinking))

## The value of observation versus protecting the service

Sensitive requests may have investigative value. But while those requests continue, Claude must generate responses that may help train a competitor. Anthropic’s interests include compute costs, access restrictions, and limiting unauthorized collection of model capabilities, alongside observing incoming traffic. Receiving sensitive material also creates decisions about access to records, retention, and evidence needed for incident response. Sensitivity alone does not establish that continuing to receive it is the more valuable option.

Anthropic also makes a safety argument. It says distillation can improve general reasoning and thereby improve biological or cyber capabilities even when those were not the tasks targeted during collection, while Claude’s safeguards do not transfer with the capabilities. This is the provider’s risk argument, not an independent measurement of that outcome in a particular Moonshot model. ([PDF, p. 146](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf))

Blocking and publishing have overlapping purposes but different effects. An account ban stops that account’s access. Disclosure prompts customers and other providers to ask about data flows and offers clues for recognizing similar activity. Anthropic reports detecting and disrupting campaigns, but does not establish that every Moonshot access route was closed before publication. The explanation that it published only after observation had become impossible is therefore unverified too.

## Disclosure exposes Anthropic to scrutiny as well

For customers, the immediate issue is which company processed an input, beyond which model answered it best. An enterprise buyer learning about rerouting can check the actual processors and retention conditions against contractual commitments. More such questions would create an explanation and response burden for Moonshot. Publication also showcases Anthropic’s detection work and its case for protecting model capabilities. That may help it in customer and policy discussions, but neither actual revenue effects nor the relative weight of these motives in the publication decision is established.

Those effects do not all favor Anthropic. Detailed case studies also invite questions about how much request content it retains and who can read it. In the [Hacker News Moonshot discussion](https://news.ycombinator.com/item?id=49656698), wongarsu distinguished a service that discloses possible routing to another model from one that offers Kimi while forwarding to Claude. In the same discussion, AlanYx worried that retention for abuse investigations could be broader than customers expect. One concern is routing transparency; the other is the investigator’s authority to process data. Neither comment independently verifies the incident.

The [author of a Reddit discussion](https://www.reddit.com/r/ClaudeAI/comments/1wdz975/anthropics_new_report_has_no_winners_and_the_part/) similarly questioned users’ limited visibility into which provider ultimately receives a prompt. That concern can be examined without extending it into a claim that Anthropic conducts unlimited surveillance of all users.

Anthropic’s [current commercial-product retention guidance](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data) says API inputs and outputs are generally deleted within 30 days, with exceptions including contracts, policy enforcement, and law. For chats flagged by automated systems as policy violations, it describes retaining inputs and outputs for up to two years and classification scores for up to seven. This does not identify the contracts or actual retention periods applied to the proxy accounts in this case. It does explain why abuse detection and privacy warrant examination together.

The legality of cross-border processing also depends on the particular circumstances. The report’s privacy allegations alone do not establish a specific legal violation or penalty. Customer notification, blocking access, limited intelligence sharing, and public reporting are separate actions; the cited material does not show that publication was the only lawful response. The report’s introductory statement about sharing intelligence with authorities where appropriate likewise does not prove that a particular government acquired Moonshot customers’ material.

Public disclosure creates benefits different from continued private observation. It turns alleged unauthorized collection into a data-processing issue that customers can investigate and brings Anthropic’s service-protection argument to an outside audience. Supporting that argument also requires Anthropic to explain its evidence and retention practices. The report’s persuasiveness depends on how well both companies’ data handling can be examined, beyond how forcefully it names a competitor.

## Further reading

- [Claude API Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking): reasoning display, encryption, normal reuse, and current enforcement conditions.
- [Commercial-product retention guidance](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data): abuse investigations and retention exceptions.

## References

- [Detecting and countering misuse of AI: September 2026, PDF](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf): Anthropic, especially pp. 146, 148-149, and 153. Accessed October 15, 2026.
- [Report web edition](https://www.anthropic.com/threat-intelligence-report-september-2026): Anthropic’s stated publication rationale and case descriptions. Accessed October 15, 2026.
- [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking): Claude Platform Docs. Accessed October 15, 2026.
- [How long do you store my organization’s data?](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data): Anthropic Privacy Center. Accessed October 15, 2026.
- [Moonshot serves Claude instead of Kimi and collects exchanges for model training](https://news.ycombinator.com/item?id=49656698): Hacker News discussion. Accessed October 15, 2026.
- [Anthropic’s new report has no winners](https://www.reddit.com/r/ClaudeAI/comments/1wdz975/anthropics_new_report_has_no_winners_and_the_part/): privacy commentary on Reddit’s r/ClaudeAI. Accessed October 15, 2026.
