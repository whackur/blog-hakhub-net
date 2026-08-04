---
title: "The Failure a Pass Rate Hides: How the YouTube Ads Team Runs Production Evals"
meta_title: "Running Production Agent Evals (YouTube Ads Team)"
description: "How Google's YouTube Ads team runs evals for a production agent: starting on intuition before going strict, managing human raters, calibrating an LLM judge, and the disclaimer removal only a trace revealed."
date: 2026-08-04T10:00:00+09:00
lastmod: 2026-08-04T10:00:00+09:00
image: ""
categories: ["AI"]
tags: ["evals", "llm-as-judge", "agent", "prompt-engineering"]
author: "whackur"
translationKey: "production-agent-evals-youtube-ads"
draft: false
---

The idea that a well-written prompt makes an agent behave holds up right until the demo ends. In production, the same prompt and the same input produce different results run to run. A case that passed yesterday fails today, and one that failed yesterday passes. Deciding whether that system is ready to ship takes measurement, not a feeling.

Preetika Bhateja and Daniel Bump of Google's YouTube Ads team walked through this in their talk [How Evals and Prompts Shape Agent Behavior](https://www.youtube.com/watch?v=xyL2Ltkh-SA). Both work on the image and video models behind YouTube ads. The agents they build generate and edit ad creative, and those agents get launched to real end users, which makes the cost of a bad output high and the launch bar something they need to state precisely.

An eval, in this sense, is a fixed set of inputs you run the agent against and score against criteria the team agreed on in advance, so the result comes out as a number. It resembles a unit test, except the correct answer is rarely single-valued and the scoring itself requires judgment. The talk is clear about why an eval is needed at all. Generative output is not deterministic, so the same case succeeds on one run and fails on the next. You cannot guarantee how the agent behaves once it is live, so the only option left is to define what good output looks like and then measure against that definition at scale. Half the work of building an eval is pinning that definition down in writing.

What makes this talk worth reading is not which tooling they picked. It is how they staffed and operated the scoring.

The original talk is embedded below. A Korean-English subtitled re-edit is also available on the [Tech Bridge channel](https://www.youtube.com/watch?v=hfaUTT8bLzU).

{{< youtube-lite id="xyL2Ltkh-SA" >}}

## Tools, then self-correction, then evals

The talk does not open on evals. Two steps come first.

The first is a narrow, solid set of LLM-friendly tools. If tool descriptions are vague or the argument design is messy, the agent keeps tripping in the same place. Bolt an eval onto that and you are measuring the tool defects over and over, with prompt edits that never move the score.

The second is an independent critique agent that reviews the output, plus a remediation loop that fixes what the critique flags. It covers gaps the base tool set cannot close on its own.

Evals come after that foundation. Bump frames their job two ways: proving that a change actually delivered value, and making ablations possible. An ablation removes or disables one component and reruns the same tests to measure the difference. If you do not know how far the score drops when the critique agent is off, you do not know whether the critique agent earns its cost.

Those two jobs are why Bump calls a strong eval essential for climbing the quality ladder, the phrase he uses throughout for pushing quality up a rung at a time. An eval is the instrument that tells you which rung to reach for next, and that is also why he keeps repeating that the foundation has to be in place first.

The line the talk lands on: agent reliability is a function of the agent's capabilities, the guardrails, and the evals. Hold onto one of those and the others slide.

![Flow diagram starting from tool optimization and a self-correction loop, moving through vibe evals to a strict eval, then human raters, an LLM judge and trace spot checks, pattern-level failure analysis, and a launch gate, with online evals feeding the eval set back](/images/posts/production-agent-evals-youtube-ads/eval-operations-loop.svg)

*The order the talk presents, plus its launch readiness section, reassembled as one flow.*

## Start by vibing, get strict later

An eval that survives scale has to be strict and measurable. The counterintuitive part of this talk is that chasing those properties on day one backfires, and that vibing helps early on. Vibing here means doing the thing that does not scale: reading outputs by hand, sorting good from bad on intuition, and fixing fast.

You could build the comprehensive eval on day one instead. But early on you rewrite the architecture and overhaul prompts often, and each time you have to recalibrate the eval and the rubric with it. When scores swing hard, you cannot tell whether the model improved or the scoring shifted. A precise eval turns into a brake on the changes you most need to make.

The talk ties that risk to when you bring rating headcount in. Pull in outside raters too early and you are changing the model hard while calibrating the eval at the same time, so scores lurch up and down and nobody can name the cause.

Problems are also easy to spot at that stage. A handful of outputs is enough to see what went wrong. Prompt tweaks still buy large gains, so a short iteration loop pays. Along the way you learn the failure patterns firsthand, and that knowledge is the raw material for the real eval later. In Bump's framing you come out of it with a real sense of depth about what you are building, which is what lets you hill-climb in a targeted way rather than a random one.

The transition is gradual too. A large golden set on day one is unnecessary. A golden set is the reference dataset whose correct answers or expected verdicts have been settled. Look through the agent, pick the few core tasks it absolutely has to get right, then fill in detail as you go.

Negative cases get their own emphasis. Checking that the agent did not do the thing you forbade matters as much as checking that it did the task. That point connects directly to the disclaimer case below.

There is a joke in the talk that writing the eval code is a small dot, and humans arguing over what the rubric should be is the large blob. Only a team that has actually run this says that.

## Working with scale raters

Early on the team is a couple of people, a PM and someone on UX. Once that group has its bearings, more teams come in and the golden set and dataset you want to test grow with them. Scoring at that size needs dedicated headcount, and the talk calls those people scale raters: staff who only rate, not the team that built the product. This is exactly the point where the verdict criteria the team was carrying in its head have to come out on paper. LLM raters show up at this stage for the same reason. Bhateja names two things that worked here.

**A clear rubric with concrete examples.** Early on, edge cases the team never anticipated keep arriving. A rater asks how to handle one, and the team itself splits on whether it is a pass or a fail. So human-human agreement inside the team, meaning how often several people reach the same verdict on the same sample, has to come first. Without it, no scoring result rests on anything. Settle the disagreement internally before handing verdicts to raters outside the team.

**Explanations, not only pass or fail.** Collecting verdicts alone tells you nothing about where to fix the agent. You need the reasoning behind each rating before improvement targets appear. The same holds for side-by-side evals, where two models' outputs are compared directly. Which one won matters less than why it won, because the why sets the next task.

Explanations matter more when the output splits across axes. Scoring ad creative, this team asked about accuracy, brand safety, and whether the ad was what they expected, all on the same item. An output that is excellent on brand safety and poor on accuracy does not compress into one pass/fail. The explanation is what shows which axis broke, and that text becomes input for improving the agent.

## Calibrating an LLM judge

Handing the scoring itself to another LLM is LLM-as-judge. It is cheaper and faster than people, and it inherits the same nondeterminism problem, now in the scorer. This team went that route and added two mechanisms to earn trust in it.

The first is a sampling pipeline that tracks agreement and disagreement continuously. The same samples get scored by a human expert and by the LLM rater, and the team watches how far the two diverge. The trend matters more than the absolute number: whether the disagreement rate stays in the range they expect, and whether it widens only on particular kinds of cases.

The second is spot-checking the reasoning behind a verdict rather than stopping at pass or fail. From the verdict alone you cannot tell a lucky score from a sound one. Pull a few cases, read the logic, and you see where the judgment came from.

All of this rests on golden set quality. Without a golden set that covers a wide range of use cases and shows high human-human agreement inside the team, an agreement rate means nothing. Counting how often two raters land on the same answer while the standard itself keeps moving is counting noise. In the Q&A someone asked whether all judgments were human, whether they used LLM-as-judge, and how they calibrated it. The answer was that it depends on the use case, and the details of the benchmarking system stayed private. What transfers is not a recipe but the habit: monitor disagreement rates, keep a sampling pipeline.

## The disclaimer removal only the trace showed

A trace is the record of intermediate reasoning and tool calls an agent leaves on its way to an answer. Bhateja's one-line framing for this section: if you want to know what the agent is doing, look at its thinking.

The team told the agent in the prompt that for legal reasons a disclaimer can never be removed. They said it more than once and trained the agent on it. Things ran fine for a while. Then in some edge cases the agent, having read the prompt and having spotted the disclaimer in the ad, removed it anyway. The trace showed both moves in order: noticing the disclaimer, then deciding to take it out.

The example was a public service ad about parks that Bhateja built herself and ran through the agent. It carries the line "America, we can do better," with a sponsor attribution in the bottom right reading "Paid by the community of parks of keep parks clean." That attribution is the exact thing they had told the agent never to touch, and the agent deleted it.

The point is that this failure is invisible in a pass rate. Inside an aggregate percentage, a case like this disappears into the "some percent failed" bucket. The number also will not tell you whether the agent missed the rule or saw it and broke it, and those two causes call for opposite fixes. If it missed the rule, that is a prompt placement or context problem. If it read the rule and deleted anyway, the agent ranked some other goal above the constraint. Here the trace settled it: the agent read the rule, found the disclaimer, then removed it. Skip the trace and that distinction stays hidden, and you end up rewriting the same instruction in stronger words for no return.

## Patterns over single runs, and managing regressions

Habits from traditional ML still apply. Agents generalize poorly outside the range of data you trained and evaluated them on, so keep datasets that probe edge cases and broader capabilities, and keep a separate test set. Use the test set sparingly and refresh it with production data.

Bump singles out one trap: fixating on individual runs. You run the agent once, see a case fail, and want to patch the prompt for that case. In a nondeterministic system that instinct backfires. The same case may pass on the next run, and meanwhile the prompt has picked up one more poorly grounded sentence. Put several examples of the same pattern in the golden set instead, and look at how often the pattern fails overall. The unit of repair is the pattern, not the run.

The talk also sketches the loop for when human eval comes in under the bar. Review the eval set first and check numbers like precision and recall. Then decide whether to fix the eval and the rating guide or the agent itself, and rerun. Once the eval is well defined, that loop becomes the main engine for climbing quality.

Launch readiness comes down to understanding regressions. The sequence the talk sketches: iterate on the model several times, then run an A/B diff or an ablation to identify where performance degraded and why, then sort the result into acceptable tradeoffs and critical failures. The practical piece here is to fix the gatekeeping rule in advance: whether the bar is a precision and recall target, some other metric, or something different again for a model eval. Skip that and you end up negotiating the criteria days before launch, when the judgment is already compromised.

The last piece of advice is to invest in online evals and confirm the data matches real-world distribution. An offline golden set that drifts from live inputs will look healthy right up to the point production breaks.

## Skill-level evals and agent-level evals

This blog already has [a post on skill-level evals](/en/blog/agent-skills-evals-skillsbench/). That one takes a single `SKILL.md`, attaches 10 to 20 test cases and regex checks, and measures contribution by comparing the skill on against the skill off. Its conclusion is that a single script is enough of a harness.

This talk sits one layer up. The subject is the whole agent, not one skill, and the problem is process rather than tooling. How raters get trained, how verdicts get agreed on, how often the golden set gets refreshed, what conditions permit a launch.

Both layers earn their keep. Skill evals verify a change; agent evals justify a release. With only the first, the parts run well and nobody knows when the product can ship. With only the second, scores move and you cannot narrow down why.

## What makes an eval system good

The talk hangs one caveat on its closing list: this is what worked for their application, and your mileage may vary. With that stated:

- **It represents what the product has to be great at.** An MVP eval and a production rollout eval look different. Either way it has to track the areas where the product must be strong.
- **It keeps evolving.** Online evals, a test set refreshed with production data, sampling pipelines, and a golden set that widens as the use cases widen.
- **It funds rater training.** Bhateja reckons this is closer to common practice now, while noting that six months earlier their own teams were still working out how to rate things and what they expected from raters.
- **Its rubrics and rater templates carry enough examples.** How often raters come back asking how to score something, and how many items land as unknown, is the report card on that investment.
- **The launch metrics get chosen up front.** Not deciding the bar after you see where the regression landed, but setting the bar and then judging the regression against it.

## Further reading

- [Don't Ship Agent Skills Without Evals](/en/blog/agent-skills-evals-skillsbench/): building an eval harness around a single skill, with the SkillsBench numbers
- [LLM Observability Without LangSmith: Five Open-Source Tools Compared](/en/blog/llm-observability-langsmith-alternatives/): the tooling you need if you actually want to store and read traces
- [AI Self-Improvement Starts Outside the Model](/en/blog/harness-engineering-self-improvement/): the view that harness design, not the model, drives agent performance

## Takeaways

Three things to carry out of this talk.

There is an order to building evals. Sharpen the tools, add a self-correction loop, then measure. Run on intuition early, and move to a strict eval once the failure patterns are in your hands.

Scoring is an agreement problem before it is a technical one. Attach outside raters or an LLM judge while the team still splits on verdicts and you have added noise. Rubrics with examples, collected explanations, and agreement monitoring are what hold the agreement in place.

Numbers hide failures. The disclaimer case is the proof. A rule stated in the prompt and trained on, which the agent recognized and then broke, did not show up anywhere in the pass rate table. Aggregate metrics tell you where to look. The trace tells you what happened.

## References

- [How Evals and Prompts Shape Agent Behavior](https://www.youtube.com/watch?v=xyL2Ltkh-SA): Preetika Bhateja, Daniel Bump (Google YouTube Ads), talk on YouTube. Accessed 2026-08-04
- [Korean and English subtitled cut](https://www.youtube.com/watch?v=hfaUTT8bLzU): Tech Bridge channel, the same talk with Korean and English subtitles. Accessed 2026-08-04
- [Daniel Bump (X)](https://x.com/DanielJBump): speaker account
- [Daniel Bump (LinkedIn)](https://www.linkedin.com/in/danielbump): speaker profile
