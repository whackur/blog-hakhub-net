---
title: "GPT-5.6 Sol, Terra, and Luna: A Model Routing Guide for Coding Agents"
meta_title: ""
description: "A source-grounded breakdown of GPT-5.6's Sol, Terra, and Luna tiers versus its max/high/xhigh/ultra reasoning settings, using OpenAI's launch snapshot plus the 18-model DeepSWE leaderboard and Artificial Analysis data to decide which model fits which coding agent task."
date: 2026-07-13T09:30:00+09:00
lastmod: 2026-08-05T10:00:00+09:00
image: ""
categories: ["AI"]
tags: ["gpt-5-6", "coding-agent", "model-routing", "benchmark", "llm"]
author: "whackur"
translationKey: "gpt-5-6-coding-agent-model-routing"
draft: false
---

A claim like "Luna Max beats Terra High" circulates around GPT-5.6 discussions, and it does not hold up. Sol, Terra, and Luna are separate models, each a different capability tier. Max, high, xhigh, and ultra are settings within a given model that control how much reasoning time it uses and how many agents run in parallel. Collapsing a tier name and a settings name into one ranking compares two different axes as if they were one.

This post uses [OpenAI's announcement](https://openai.com/index/gpt-5-6/), the [official DeepSWE leaderboard](https://deepswe.datacurve.ai/) (v1.1, updated July 25, 2026, checked August 5), and [Artificial Analysis](https://artificialanalysis.ai/) model pages (checked August 5, 2026) to lay out what actually differs between the three models, then gives a routing framework for coding agents like Hermes Agent or Codex.

## Tiers are not reasoning settings

Per [OpenAI's announcement](https://openai.com/index/gpt-5-6/), Sol is the flagship, Terra is a balanced, lower-cost model for everyday work, and Luna is the fastest and cheapest of the three. Each is an independent model, and each can run at reasoning-effort settings like max, high, or xhigh. Ultra is separate: an orchestration mode that coordinates four agents in parallel by default. The API exposes Programmatic Tool Calling and a multi-agent beta in the Responses API. OpenAI states that max uses more reasoning time than xhigh.

The [OpenAI Help Center](https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna) notes that Terra and Luna aren't selectable in standard ChatGPT conversations, but are available through Work, Codex, or the API depending on plan. API developers can reach all three models.

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
| --- | ---: | ---: |
| GPT-5.6 Sol | $5.00 | $30.00 |
| GPT-5.6 Terra | $2.00 | $12.00 |
| GPT-5.6 Luna | $0.20 | $1.20 |

Source: [OpenAI API pricing](https://openai.com/api/pricing/), checked August 5, 2026.

The gaps between the three tiers are wide. Sol's output price is 2.5x Terra's and 25x Luna's, and Terra sits 10x above Luna. That multiplier is far larger than the performance gap, and the DeepSWE table below is where that shows up.

GPT-5.6 supports explicit cache breakpoints with a 30-minute minimum cache life. The cache write and cache read multipliers weren't confirmed as numbers at the time of this check, so if caching factors into your cost model, read the current values off the [official pricing page](https://openai.com/api/pricing/) rather than assuming them. Pricing and availability change, so verify before acting on any of these numbers.

## OpenAI's launch-page coding snapshot

OpenAI's launch page shows all three models at max reasoning effort across four metrics: Artificial Analysis Coding Agent Index v1.1, SWE-Bench Pro, DeepSWE v1.1, and Terminal-Bench 2.1.

| Model (config) | Coding Agent Index | SWE-Bench Pro | DeepSWE v1.1 | Terminal-Bench 2.1 |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol (max) | 80 | 64.6% | 72.7% | 88.8% |
| GPT-5.6 Terra (max) | 77.4 | 63.4% | 69.6% | 87.4% |
| GPT-5.6 Luna (max) | 74.6 | 62.7% | 67.2% | 84.7% |

Source: [OpenAI, "GPT-5.6: Frontier intelligence that scales with your ambition"](https://openai.com/index/gpt-5-6/), July 9, 2026.

This is a snapshot taken at the July 9, 2026 launch. OpenAI's own text says Sol set a new state of the art at 80, Terra landed just above Fable 5, and Luna outperformed Opus 4.8 in that same comparison.

The DeepSWE figures here (72.7%, 69.6%, 67.2%) are the values OpenAI's launch page cited. They differ in precision and in snapshot date from the current DeepSWE leaderboard values in the next section (73%, 70%, 67%). Keep the two sets apart rather than treating them as one series.

## DeepSWE's current leaderboard snapshot

The [official DeepSWE site](https://deepswe.datacurve.ai/) at v1.1, updated July 25, 2026 and checked August 5, covers 113 tasks across 91 repositories in five languages and 18 models. All 18 run through a fixed `mini-swe-agent` scaffold to keep conditions consistent. It uses original long-horizon tasks, behavior-based and held-out verification, and a separate verifier environment. It's a benchmark and leaderboard, not a model.

The leaderboard's own embedded description says `pass@1` is the attempt pass rate over scored rollout attempts, and `pass@4` is the share of attempted tasks with at least one passing rollout. Context-window failures and agent timeouts are scored as failures; provider, verifier, and network errors are excluded. The output-token and step figures in the table below are **means over every scored attempt**, not medians and not totals. Cost is also a mean per scored attempt.

| Model (config) | Pass@1 | Average cost | Mean output tokens | Mean steps |
| --- | ---: | ---: | ---: | ---: |
| Claude Opus 5 [max] | 74% ± 4% | $11.84 | 118k | 99 |
| GPT-5.6 Sol [max] | 73% ± 3% | $8.39 | 60k | 61 |
| Claude Fable 5 [max] | 70% ± 4% | $21.63 | 119k | 88 |
| GPT-5.6 Terra [max] | 70% ± 3% | $3.96 | 72k | 76 |
| Kimi K3 [max] | 69% ± 5% | $4.65 | 81k | 98 |
| GPT-5.6 Luna [max] | 67% ± 4% | $0.61 | 73k | 102 |
| GPT-5.5 [xhigh] | 67% ± 6% | $7.23 | 46k | 82 |
| Claude Opus 4.8 [max] | 59% ± 2% | $13.22 | 135k | 120 |
| Claude Sonnet 5 [max] | 54% ± 4% | $26.40 | 214k | 268 |
| Grok 4.5 [high] | 54% ± 2% | $2.42 | 36k | 61 |
| Muse Spark 1.1 [xhigh] | 53% ± 3% | $2.36 | 74k | 96 |
| GPT-5.4 [xhigh] | 52% ± 2% | $5.65 | 71k | 70 |
| Gemini 3.6 Flash [high] | 49% ± 5% | $3.53 | 97k | 108 |
| GLM-5.2 [max] | 44% ± 2% | $3.92 | 78k | 129 |
| Gemini 3.5 Flash [medium] | 37% ± 2% | $7.34 | 276k | 86 |
| Kimi K2.7 Code [unspecified] | 31% ± 1% | $2.82 | 59k | 149 |
| Claude Sonnet 4.6 [high] | 30% ± 4% | $5.52 | 76k | 134 |
| Gemini 3.1 Pro [high] | 12% ± 2% | $9.48 | 196k | 81 |

Source: [DeepSWE official leaderboard](https://deepswe.datacurve.ai/), v1.1, updated July 25, 2026, accessed August 5, 2026. Best view, all 18 models. Task and verification design is documented on the [official GitHub repo](https://github.com/datacurve-ai/deep-swe) and the [v1.1 methodology post](https://deepswe.datacurve.ai/blog/deepswe-v1-1).

Claude Opus 5 holds the top spot at 74% for $11.84 per task. This post is about GPT-5.6 routing, so Opus 5 appears here as comparison context only. Within GPT-5.6, Sol leads at 73%, one point behind the top score with overlapping confidence intervals (±4% and ±3%), and at $8.39 it costs 29.1% less than Opus 5.

Sol has the highest pass rate of the three GPT-5.6 tiers while using the fewest mean output tokens and the fewest mean steps. That score isn't bought by spending more tokens. You can read it as Sol reaching an answer in fewer steps, but the table alone doesn't say why.

Terra sits 3 points behind Sol while its average cost is 52.8% lower. That comes at a cost, though: mean output tokens run 20.0% higher and mean steps 24.6% higher. Terra isn't the best on every axis; it's a strong tradeoff on score versus cost specifically.

Luna is the row worth staring at. It sits 3 points behind Terra at 67%, but its $0.61 per task is 15.4% of Terra's cost and 7.3% of Sol's. Its mean output tokens are nearly identical to Terra's (73k versus 72k, a 1.4% difference) and its mean steps run 34.2% higher. Luna's low cost reflects low model pricing, not fewer generated tokens or fewer tool-call loops.

The same pattern shows up outside the GPT-5.6 family. Claude Fable 5 matches Terra's rounded 70% pass@1 but costs 5.46x as much, uses 65.3% more output tokens, and takes 15.8% more steps. Their confidence intervals overlap, and the [official DeepSWE v1.1 post](https://deepswe.datacurve.ai/blog/deepswe-v1-1) notes that 73 of Fable 5's 2,260 trials didn't complete because access was suspended by a US government directive partway through the sweep, so this comparison shouldn't be stretched too far.

GPT-5.5 also matches Luna's rounded 67% pass@1, using 37.0% fewer output tokens and 19.6% fewer steps, yet costing 11.9x as much. Kimi K3 lands one point below Terra at 69% while costing more ($4.65) and taking more steps (98). Grok 4.5 and Claude Sonnet 5 tie at 54% pass@1, but Grok costs 90.8% less, uses 83.2% fewer output tokens, and takes 77.2% fewer steps. Effort settings differ and confidence intervals overlap, so none of this is a universal ranking. What it does show consistently: spending more tokens or steps doesn't reliably buy a higher success rate, and dollar cost tracks each vendor's pricing far more closely than it tracks token volume.

Mean output tokens and mean steps measure different things. Tokens estimate how much a model generates; steps estimate how many tool-call or interaction cycles it runs. Luna and Terra's near-identical tokens paired with a large step gap suggest shorter, more fragmented cycles for Luna, but that alone doesn't establish quality, latency, or root cause. v1.1 no longer reports wall-clock time, because host performance and provider load make it inconsistent across runs. Fewer steps doesn't mean a model actually finishes faster, and there's no way to read run time off the leaderboard at all.

### Reading the effort configs

The leaderboard table is a Best view: one row per model, showing its highest-scoring config. That's why all three GPT-5.6 rows above are `[max]`. Turning on the **All effort levels** button above the chart plots every scored config for every model as its own scatter point. GPT-5.6 Sol, Terra, and Luna each have all five configs scored (low, medium, high, xhigh, max, so 5/5 apiece), which makes it possible to see in one view how cost and pass@1 move as you dial effort down within a single model. Across the board, 48 configs are active over the 18 models. Coverage varies by model, and some entries such as Grok 4.5 and Gemini 3.6 Flash have only a single config.

One limit worth stating: the per-effort numbers aren't published in the table. They're readable from the scatter points, so this post does not put pass@1 or cost figures on low, medium, high, or xhigh individually. If you need the actual savings from dropping effort, read the points off the leaderboard directly or measure it on your own harness.

DeepSWE's fixed harness compares 18 models' behavior on one scaffold. It doesn't directly rank complete products like Hermes Agent, Codex, or Claude Code, each of which runs its own orchestration, tools, prompts, retry logic, and sandboxing.

![Scatter plot of DeepSWE Pass@1 versus average cost for 18 models, next to a bar comparison of GPT-5.6 Sol, Terra, and Luna's mean output tokens and mean agent steps](/images/posts/gpt-5-6-coding-agent-model-routing/deepswe-routing-tradeoffs.svg)
*Top: Pass@1 versus average cost for all 18 models on the [DeepSWE official leaderboard](https://deepswe.datacurve.ai/)'s best view; the 15 models outside the GPT-5.6 family are shown as unlabeled context dots. Bottom: mean output tokens and mean agent steps for the three GPT-5.6 tiers. This reflects the current DeepSWE v1.1 leaderboard, updated July 25, 2026.*

## Response speed versus time to a useful answer

[Artificial Analysis](https://artificialanalysis.ai/) model pages (checked August 5, 2026, max configuration) report the following.

| Model (config) | Intelligence Index | Output speed | Time to First Answer Token | Output tokens used for the full evaluation |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol [max] | 59 | 70.6 tok/s | 131.39s | 70M |
| GPT-5.6 Terra [max] | 55 | 145.8 tok/s | 162.17s | 96M |
| GPT-5.6 Luna [max] | 51 | 180.5 tok/s | 132.75s | 130M |

Source: [artificialanalysis.ai/models/gpt-5-6-sol](https://artificialanalysis.ai/models/gpt-5-6-sol), [-terra](https://artificialanalysis.ai/models/gpt-5-6-terra), [-luna](https://artificialanalysis.ai/models/gpt-5-6-luna), accessed August 5, 2026.

The part worth slowing down on is what this latency column actually measures. Artificial Analysis defines raw TTFT as the time from request to first response token, and for reasoning models that first token can itself be a reasoning token. It defines a separate concept, time to first answer token, which includes the model's thinking time, and that's the column above. So the 131, 162, and 133 second figures aren't pure network round trips; they include however long each model spent reasoning before it started producing an answer.

The [Artificial Analysis methodology page](https://artificialanalysis.ai/methodology/performance-benchmarking) adds that these are P50 measurements over a recent window, taken from a primary server in Google Cloud us-central1-a, and that prompt length and network location both affect the number. Latency here is a mix of model behavior and serving conditions, not a property of model intelligence. This snapshot makes that concrete: the three tiers don't order by capability at all. Sol is fastest to a first answer at 131s, Luna is essentially tied at 133s, and Terra is slowest at 162s. Measure on a different day and the order can shift again, so pick a tier on latency only after measuring from your own region with your own prompt lengths.

Decode speed does follow the tier order. Luna runs at 180.5 tok/s, Terra at 145.8, and Sol at 70.6, making Luna 2.6x Sol. But all three take over two minutes to a first answer, so none of them fits an interactive chat latency budget. "Fast once it starts producing tokens" and "fast to a useful first answer" are separate properties, and a high tokens-per-second number doesn't make the wait any shorter.

## What the benchmarks actually measure

- **DeepSWE**: 113 original long-horizon software engineering tasks pulled from active open-source repositories, with behavior-based and held-out verification run through a fixed `mini-swe-agent` leaderboard scaffold. v1.1 adds an isolated verification environment and CTRF structured test reports, and drops wall-clock time from the reported metrics. See the [official GitHub repo](https://github.com/datacurve-ai/deep-swe) for the task design.
- **Terminal-Bench v2.1**: 89 curated tasks spanning software engineering, system administration, data processing, model training, and security, verified programmatically inside real terminal environments. Artificial Analysis runs its own evaluation using Terminus 2 in e2b, averaging pass@1 over three repeats. Official site: [tbench.ai](https://www.tbench.ai/); repo: [laude-institute/terminal-bench](https://github.com/laude-institute/terminal-bench).
- **Artificial Analysis Coding Agent Index**: an independent composite index for coding-agent performance, currently v1.1. It is not a single repository task and not equivalent to DeepSWE.
- **Artificial Analysis Intelligence Index v4.1**: a composite of nine evaluations, namely GDPval-AA v2, 𝜏³-Banking, Terminal-Bench v2.1, SciCode, Humanity's Last Exam, GPQA Diamond, CritPt, AA-Omniscience, and AA-LCR. The output-token figures in the table above cover the entire index evaluation, so they aren't directly comparable to DeepSWE's per-task token counts.

All of these run one fixed harness across several models. That comparison is useful, but it answers a different question than the one that matters when picking a model for a product like Hermes Agent or Codex, each built with its own prompt engineering, tool set, retry strategy, sandboxing, and context management. A benchmark score answers "how well does this model do on this harness." Choosing a model for your own product needs an answer to "how well does this model do on my harness." The two are correlated, not identical.

## A routing framework for coding agents

Running Hermes Agent or Codex works better with routing by task risk and reversibility than with a single fixed model tier.

1. **Low-risk, read-only, triage, or bulk work**: log inspection, code explanation, issue triage, simple formatting, large batch runs. Use Luna at a low reasoning-effort setting. Its $0.61 per DeepSWE task is 7.3% of Sol's and 15.4% of Terra's, at 67% pass@1, three points behind Terra. When failure is cheap and verification is easy, that price gap alone justifies Luna as the default. You can afford two or three retries and still spend less than one Terra run.
2. **Scoped implementation work**: a single well-defined feature, a routine bug fix, filling in test coverage. Terra at high or max is a reasonable default. The DeepSWE gap to Sol is only 3 points while average cost is 52.8% lower. That comes with more mean output tokens and steps than Sol, though, so don't read Terra as the most efficient choice on every axis. The gap is also measured on DeepSWE tasks specifically, so validate it against your own repositories and workflows before trusting it as a general rule.
3. **High-risk, multi-file, or long-horizon autonomous work**: migrations, security-sensitive changes, failures spanning multiple files, long unattended runs. Sol at max is the sensible starting point; reach for ultra only when parallel orchestration and the added cost are justified. If you're willing to route outside GPT-5.6, Claude Opus 5 leads DeepSWE at 74% but costs $11.84 per task, 41.1% more than Sol. Whether one point is worth that depends entirely on what a single failure costs you.

**Escalation triggers**: move up a tier when tests keep failing, the model flags its own uncertainty, or retry counts on the same problem cross a threshold. In the other direction, if low-risk work is still routed to Terra or Sol, check whether dropping to Luna would cut cost without hurting outcomes.

## What community reports look like

Alongside the benchmarks above, it's worth looking at what actual users are posting. All three reports below are from July 2026, and all three are selection-biased, non-reproducible personal accounts.

In [one post](https://www.reddit.com/r/codex/comments/1us7fwv/i_gave_gpt54_gpt55_gpt56_sol_terra_and_luna_the/), a user ran the same 35-word Coca-Cola Zero landing-page prompt across GPT-5.4, GPT-5.5, GPT-5.6 Luna Max, Terra Ultra, and Sol Ultra and posted the outputs side by side. The author self-reported token usage of 94,393 for Luna, 154,574 for Terra, and 200,352 for Sol; those numbers are author-reported, not independently verified. The author said they personally preferred the Luna output. This is one person's self-run frontend showcase, not a controlled coding-agent benchmark, and it shouldn't be read as evidence for model ranking or general token efficiency.

By contrast, [another user reported](https://www.reddit.com/r/codex/comments/1ut3u5l/very_bad_first_experience_with_gpt_56_terra/) that while trying to harden idempotency in a payment and refund path, Terra on high deleted unrelated local development database tables, users, sessions, wallet, invoices, and transactions. The author said their confidence in Terra dropped and they were considering going back to GPT-5.5. This is a single unverified report with no reproduction or root-cause confirmation, and it shouldn't be generalized into a claim that Terra is broadly unsafe. It's worth reading only as a reminder of why sandboxing, approval gates, backups, and test gates matter when an agent runs autonomously.

A [thread on the Hermes Agent subreddit](https://www.reddit.com/r/hermesagent/comments/1us3uc0/gpt56_is_moving_to_permanent_tiers_sol_terra_and/) discusses a routing heuristic: Terra by default, Sol for hard tasks, Luna for bulk or background work. This is community opinion, and replies are mixed. One commenter pushed back on Terra as the default and argued the lower tiers are underrated, while another said Terra medium felt worse than GPT-5.5 medium even though Terra high felt more efficient. The thread also includes speculative claims about model lineage that aren't addressed here since they aren't substantiated.

These threads predate the current price table, so they can't be used as a basis for cost judgments. They don't replace the OpenAI, DeepSWE, or Artificial Analysis measurements covered above, and they don't override the routing framework in this post.

## A measurement checklist

Validating a model choice means looking at several numbers together, not one in isolation.

- Success rate (did the task actually complete)
- Cost per solved task
- Wall-clock time (DeepSWE doesn't report it, so measure it yourself)
- Time to first useful answer, reasoning included
- Retry and step count
- Regression rate (new bugs introduced by the fix)
- Human review time

Avoid collapsing success rate and token count into one "efficiency" number across different benchmarks and tasks. Token counts shift with task difficulty, harness design, and reasoning-effort setting, so they aren't comparable across benchmarks that weren't built the same way. Even the cost, token, and step differences computed above from the DeepSWE table (Terra costs 52.8% less than Sol but uses 20.0% more tokens and 24.6% more steps; Luna costs 84.6% less than Terra while using 1.4% more tokens and 34.2% more steps) are derived values valid only within that one benchmark and that one harness.

## Takeaways

Sol, Terra, and Luna are different models; max, high, xhigh, and ultra are settings that control how long a given model reasons and how it's orchestrated. A ranking that mixes the two doesn't hold up.

Routing decisions start from one fact: the price gaps between the three tiers are much wider than the performance gaps. On DeepSWE, Luna and Sol are 6 points apart on pass@1 while their per-task cost differs by 13.8x. For high-volume, low-risk, easy-to-verify work, Luna at a lower effort setting is a defensible default rather than just a cheap fallback. For routine coding-agent execution, Terra at high or max is the first candidate: 3 points behind Sol at less than half the cost. For difficult, long-horizon work where absolute success rate matters most, start with Sol at max and reach for ultra only when parallel orchestration is worth the added spend.

A few things only show up if you read the table closely. Sol's lead within GPT-5.6 isn't bought with more tokens or steps; it uses fewer of both than Terra or Luna. Terra is a good tradeoff on cost but isn't the best on every efficiency axis once output tokens and steps are counted. Luna's low cost reflects model pricing rather than fewer generated tokens, and all three tiers take over two minutes to a first answer, so none of them is an interactive-latency choice. Whichever model you pick, validate it against success rate, cost, time, tokens, steps, and regression rate together on your own harness rather than trusting a single benchmark score.

## Further reading

- [OpenAI, "Previewing GPT-5.6 Sol: a next-generation model"](https://openai.com/index/previewing-gpt-5-6-sol/): the standalone Sol preview announcement.
- [Artificial Analysis, Terminal-Bench v2.1 evaluation page](https://artificialanalysis.ai/evaluations/terminalbench-v2-1): independent methodology and cross-model comparison.
- [DeepSWE official GitHub](https://github.com/datacurve-ai/deep-swe): task construction and verification details.
- [DeepSWE, "DeepSWE v1.1"](https://deepswe.datacurve.ai/blog/deepswe-v1-1): what changed in v1.1, leaderboard metric definitions, and the Fable 5 completion-rate footnote.
- [Artificial Analysis, Intelligence Index methodology](https://artificialanalysis.ai/methodology/intelligence-index): the nine evaluations behind v4.1 and how they're weighted.

## References

- [OpenAI, "GPT-5.6: Frontier intelligence that scales with your ambition"](https://openai.com/index/gpt-5-6/), July 9, 2026, accessed August 5, 2026.
- [OpenAI, "Previewing GPT-5.6 Sol: a next-generation model"](https://openai.com/index/previewing-gpt-5-6-sol/), accessed August 5, 2026.
- [OpenAI API pricing](https://openai.com/api/pricing/), accessed August 5, 2026.
- [OpenAI Help Center, "GPT-5.6 in ChatGPT"](https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna), accessed August 5, 2026.
- [Artificial Analysis, GPT-5.6 Sol](https://artificialanalysis.ai/models/gpt-5-6-sol), accessed August 5, 2026.
- [Artificial Analysis, GPT-5.6 Terra](https://artificialanalysis.ai/models/gpt-5-6-terra), accessed August 5, 2026.
- [Artificial Analysis, GPT-5.6 Luna](https://artificialanalysis.ai/models/gpt-5-6-luna), accessed August 5, 2026.
- [Artificial Analysis, performance benchmarking methodology](https://artificialanalysis.ai/methodology/performance-benchmarking), accessed August 5, 2026.
- [Artificial Analysis, Intelligence Index methodology](https://artificialanalysis.ai/methodology/intelligence-index), accessed August 5, 2026.
- [Artificial Analysis, Terminal-Bench v2.1](https://artificialanalysis.ai/evaluations/terminalbench-v2-1), accessed August 5, 2026.
- [DeepSWE official leaderboard](https://deepswe.datacurve.ai/), v1.1, updated July 25, 2026, accessed August 5, 2026.
- [DeepSWE, "DeepSWE v1.1"](https://deepswe.datacurve.ai/blog/deepswe-v1-1), accessed August 5, 2026.
- [DeepSWE, "DeepSWE"](https://deepswe.datacurve.ai/blog/deepswe), accessed August 5, 2026.
- [DeepSWE official GitHub](https://github.com/datacurve-ai/deep-swe), accessed August 5, 2026.
- [Terminal-Bench official site](https://www.tbench.ai/), accessed August 5, 2026.
- [Terminal-Bench repository](https://github.com/laude-institute/terminal-bench), accessed August 5, 2026.
