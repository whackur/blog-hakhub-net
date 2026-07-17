---
title: "GPT-5.6 Sol, Terra, and Luna: A Model Routing Guide for Coding Agents"
meta_title: ""
description: "A source-grounded breakdown of GPT-5.6's Sol, Terra, and Luna tiers versus its max/high/xhigh/ultra reasoning settings, using OpenAI's launch snapshot and current DeepSWE and Artificial Analysis data to decide which model fits which coding agent task."
date: 2026-07-13T09:30:00+09:00
lastmod: 2026-07-17T17:50:08+09:00
image: ""
categories: ["AI"]
tags: ["gpt-5-6", "coding-agent", "model-routing", "benchmark", "llm"]
author: "whackur"
translationKey: "gpt-5-6-coding-agent-model-routing"
draft: false
---

A claim like "Luna Max beats Terra High" circulates around GPT-5.6 discussions, and it does not hold up. Sol, Terra, and Luna are separate models, each a different capability tier. Max, high, xhigh, and ultra are settings within a given model that control how much reasoning time it uses and how many agents run in parallel. Collapsing a tier name and a settings name into one ranking compares two different axes as if they were one.

This post uses [OpenAI's announcement](https://openai.com/index/gpt-5-6/), the [official DeepSWE leaderboard](https://deepswe.datacurve.ai/) (updated July 16, 2026, checked July 17), and [Artificial Analysis](https://artificialanalysis.ai/) model pages (checked July 13, 2026) to lay out what actually differs between the three models, then gives a routing framework for coding agents like Hermes Agent or Codex.

## Tiers are not reasoning settings

Per [OpenAI's announcement](https://openai.com/index/gpt-5-6/), Sol is the flagship, Terra is a balanced, lower-cost model for everyday work, and Luna is the fastest and cheapest of the three. Each is an independent model, and each can run at reasoning-effort settings like max, high, or xhigh. Ultra is separate: an orchestration mode that coordinates four agents in parallel by default. The API exposes Programmatic Tool Calling and a multi-agent beta in the Responses API. OpenAI states that max uses more reasoning time than xhigh.

The [OpenAI Help Center](https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna) notes that Terra and Luna aren't selectable in standard ChatGPT conversations, but are available through Work, Codex, or the API depending on plan. API developers can reach all three models. Per-1M-token API pricing is $5 input / $30 output for Sol, $2.50 / $15 for Terra, and $1 / $6 for Luna. GPT-5.6 supports explicit cache breakpoints with a 30-minute minimum cache life, cache writes bill at 1.25x uncached input, and cache reads keep a 90% discount. Pricing and availability are time-sensitive, so check the official pages before acting on these numbers.

## OpenAI's launch-page coding snapshot

OpenAI's launch page shows all three models at max reasoning effort across four metrics: Artificial Analysis Coding Agent Index v1.1, SWE-Bench Pro, DeepSWE v1.1, and Terminal-Bench 2.1.

| Model (config) | Coding Agent Index | SWE-Bench Pro | DeepSWE v1.1 | Terminal-Bench 2.1 |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol (max) | 80 | 64.6% | 72.7% | 88.8% |
| GPT-5.6 Terra (max) | 77.4 | 63.4% | 69.6% | 87.4% |
| GPT-5.6 Luna (max) | 74.6 | 62.7% | 67.2% | 84.7% |

Source: [OpenAI, "GPT-5.6: Frontier intelligence that scales with your ambition"](https://openai.com/index/gpt-5-6/), July 9, 2026.

This is a snapshot at launch, not a fixed leaderboard. OpenAI's own text says Sol set a new state of the art at 80, Terra landed just above Fable 5, and Luna outperformed Opus 4.8 in that same comparison.

## DeepSWE's current leaderboard snapshot

The [official DeepSWE site](https://deepswe.datacurve.ai/), updated July 16, 2026 and checked July 17, covers 113 tasks across 91 repositories in five languages and 15 models. All 15 run through a fixed `mini-swe-agent` scaffold to keep conditions consistent. It uses original long-horizon tasks, behavior-based and held-out verification, and a separate verifier environment. It's a benchmark and leaderboard, not a model.

The leaderboard's own embedded description says `pass@1` is the attempt pass rate over scored rollout attempts, and `pass@4` is the share of attempted tasks with at least one passing rollout. Context-window failures and agent timeouts are scored as failures; provider, verifier, and network errors are excluded. The output-token and step figures in the table below are **means over every scored attempt**, not medians and not totals. Cost is also a mean per scored attempt.

| Model (config) | Pass@1 | Average cost | Mean output tokens | Mean steps |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol [max] | 73% ± 3% | $8.39 | 60k | 61 |
| Claude Fable 5 [max] | 70% ± 4% | $21.63 | 119k | 88 |
| GPT-5.6 Terra [max] | 70% ± 3% | $4.95 | 72k | 76 |
| GPT-5.6 Luna [max] | 67% ± 4% | $3.03 | 73k | 102 |
| GPT-5.5 [xhigh] | 67% ± 6% | $7.23 | 46k | 82 |
| Claude Opus 4.8 [max] | 59% ± 2% | $13.22 | 135k | 120 |
| Claude Sonnet 5 [max] | 54% ± 4% | $26.40 | 214k | 268 |
| Grok 4.5 [high] | 54% ± 2% | $2.42 | 36k | 61 |
| Muse Spark 1.1 [xhigh] | 53% ± 3% | $2.36 | 74k | 96 |
| GPT-5.4 [xhigh] | 52% ± 2% | $5.65 | 71k | 70 |
| GLM-5.2 [max] | 44% ± 2% | $3.92 | 78k | 129 |
| Gemini 3.5 Flash [medium] | 37% ± 2% | $7.34 | 276k | 86 |
| Kimi K2.7 Code [unspecified] | 31% ± 1% | $2.82 | 59k | 149 |
| Claude Sonnet 4.6 [high] | 30% ± 4% | $5.52 | 76k | 134 |
| Gemini 3.1 Pro [high] | 12% ± 2% | $9.48 | 196k | 81 |

Source: [DeepSWE official leaderboard](https://deepswe.datacurve.ai/), updated July 16, 2026, accessed July 17, 2026. Best view, all 15 models. Task and verification design is documented on the [official GitHub repo](https://github.com/datacurve-ai/deep-swe) and the [v1.1 methodology post](https://deepswe.datacurve.ai/blog/deepswe-v1-1).

Sol has the highest pass rate of the 15 models while using fewer mean output tokens and fewer mean steps than either Terra or Luna under this fixed harness. That score isn't bought by spending more tokens, which is consistent with more direct behavior, though the table alone doesn't establish why.

Terra sits 3 points behind Sol while its average cost is about 41.0% lower. That comes at a cost, though: mean output tokens run about 20.0% higher and mean steps about 24.6% higher. Terra isn't the best on every axis; it's a strong tradeoff on score versus cost specifically.

Luna sits 3 points behind Terra with average cost about 38.8% lower. Its mean output tokens are nearly identical to Terra's (73k versus 72k, a 1.4% difference), but its mean steps run 34.2% higher. Luna's lower price mainly reflects lower model pricing, not fewer generated tokens or fewer tool-call loops.

The same pattern shows up outside the GPT-5.6 family. Claude Fable 5 matches Terra's rounded 70% pass@1, but costs 4.37x as much (337.0% more), uses 65.3% more output tokens, and takes 15.8% more steps. Their confidence intervals overlap, and the [official DeepSWE v1.1 post](https://deepswe.datacurve.ai/blog/deepswe-v1-1) notes that 73 of Fable 5's 2,260 trials didn't complete because access was suspended by a US government directive partway through the sweep, so this comparison shouldn't be stretched too far. GPT-5.5 also matches Luna's rounded 67% pass@1, using 37.0% fewer output tokens and 19.6% fewer steps, yet costing 138.6% more. Token counts and dollar cost diverge here because model pricing differs. Grok 4.5 and Claude Sonnet 5 tie at 54% pass@1, but Grok costs 90.8% less, uses 83.2% fewer output tokens, and takes 77.2% fewer steps. Effort settings differ and confidence intervals overlap, so this isn't a universal ranking either, but the pattern repeats: spending more tokens or steps doesn't reliably buy a higher success rate.

Mean output tokens and mean steps measure different things. Tokens estimate how much a model generates; steps estimate how many tool-call or interaction cycles it runs. Luna and Terra's near-identical tokens paired with a large step gap suggest shorter, more fragmented cycles for Luna, but that alone doesn't establish quality, latency, or root cause. The [official DeepSWE v1.1 post](https://deepswe.datacurve.ai/blog/deepswe-v1-1) says wall-clock time is no longer reported because host performance and provider load make it inconsistent across runs. Fewer steps doesn't mean a model actually finishes faster.

DeepSWE's fixed harness compares 15 models' behavior on one scaffold. It doesn't directly rank complete products like Hermes Agent, Codex, or Claude Code, each of which runs its own orchestration, tools, prompts, retry logic, and sandboxing.

![Scatter plot of DeepSWE Pass@1 versus average cost for 15 models, next to a bar comparison of GPT-5.6 Sol, Terra, and Luna's mean output tokens and mean agent steps](/images/posts/gpt-5-6-coding-agent-model-routing/deepswe-routing-tradeoffs.svg)
*Top: Pass@1 versus average cost for all 15 models on the [DeepSWE official leaderboard](https://deepswe.datacurve.ai/)'s best view; the other 12 models are shown as unlabeled context dots. Bottom: mean output tokens and mean agent steps for the three GPT-5.6 tiers. This is the July 16, 2026 snapshot, so it won't reflect later leaderboard changes.*

## Response speed versus time to a useful answer

[Artificial Analysis](https://artificialanalysis.ai/) model pages (checked July 13, 2026, max configuration) report the following.

| Model (config) | Intelligence Index | Output speed | Page-reported TTFT/first-answer latency | Output tokens used for the full evaluation |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol [max] | 59 | 69.2 tok/s | 193.39s | 70M |
| GPT-5.6 Terra [max] | 55 | 140.8 tok/s | 167.86s | 96M |
| GPT-5.6 Luna [max] | 51 | 205.7 tok/s | 99.34s | 130M |

Source: [artificialanalysis.ai/models/gpt-5-6-sol](https://artificialanalysis.ai/models/gpt-5-6-sol), [-terra](https://artificialanalysis.ai/models/gpt-5-6-terra), [-luna](https://artificialanalysis.ai/models/gpt-5-6-luna), accessed July 13, 2026.

The part worth slowing down on is what TTFT actually measures here. Artificial Analysis defines raw TTFT as the time from request to first response token, and for reasoning models that first token can itself be a reasoning token. It defines a separate concept, time to first answer token, which includes the model's thinking time. Its own FAQ applies the label "TTFT" to the long latency values shown above and says the number accounts for reasoning time. So the 193, 168, and 99 second figures in the table aren't pure network round trips; they include however long each model spent reasoning before it started producing an answer.

The [Artificial Analysis methodology page](https://artificialanalysis.ai/methodology/performance-benchmarking) adds that these are P50 measurements over a recent window, taken from a primary server in Google Cloud us-central1-a, and that prompt length and network location both affect TTFT. In other words, TTFT is a mix of model behavior and serving conditions, not a pure property of model intelligence.

The practical read: at max, Luna has the shortest reported wait and the fastest decode speed, but a roughly 99-second wait for a first answer is still slow for anything interactive. Sol waits the longest and decodes the slowest of the three in this snapshot, while scoring highest on both intelligence and DeepSWE. "Fast once it starts producing tokens" and "fast to a useful first answer" are separate properties, and a high output-speed number does not translate into good interactive latency.

## What the benchmarks actually measure

- **DeepSWE**: 113 original long-horizon software engineering tasks pulled from active open-source repositories, with behavior-based and held-out verification run through a fixed `mini-swe-agent` leaderboard scaffold. See the [official GitHub repo](https://github.com/datacurve-ai/deep-swe) for the task design.
- **Terminal-Bench v2.1**: 89 curated tasks spanning software engineering, system administration, data processing, model training, and security, verified programmatically inside real terminal environments. Artificial Analysis runs its own evaluation using Terminus 2 in e2b, averaging pass@1 over three repeats. Official site: [tbench.ai](https://www.tbench.ai/); repo: [laude-institute/terminal-bench](https://github.com/laude-institute/terminal-bench).
- **Artificial Analysis Coding Agent Index**: an independent composite index for coding-agent performance, currently v1.1. It is not a single repository task and not equivalent to DeepSWE.
- **Artificial Analysis Intelligence Index v4.1**: a composite of nine evaluations spanning agentic work, coding, science, reasoning, knowledge, and long context. The output-token figures in the table above cover the entire index evaluation, so they aren't directly comparable to DeepSWE's per-task token counts.

All of these run one fixed harness across several models. That comparison is useful, but it answers a different question than the one that matters when picking a model for a product like Hermes Agent or Codex, each built with its own prompt engineering, tool set, retry strategy, sandboxing, and context management. A benchmark score answers "how well does this model do on this harness." Choosing a model for your own product needs an answer to "how well does this model do on my harness." The two are correlated, not identical.

## A routing framework for coding agents

Running Hermes Agent or Codex works better with routing by task risk and reversibility than with a single fixed model tier.

1. **Low-risk, read-only, or triage work**: log inspection, code explanation, issue triage, simple formatting. Start with Luna at a low reasoning-effort setting. Failure is cheap here and easy to check.
2. **Scoped implementation work**: a single well-defined feature, a routine bug fix, filling in test coverage. Terra at high or max is a reasonable default. The DeepSWE gap to Sol is only 3 points, and average cost is about 41% lower. That comes with more mean output tokens and steps than Sol, though, so don't read Terra as the most efficient choice on every axis. The gap is also measured on DeepSWE tasks specifically, so validate it against your own repositories and workflows before trusting it as a general rule.
3. **High-risk, multi-file, or long-horizon autonomous work**: migrations, security-sensitive changes, failures spanning multiple files, long unattended runs. Sol at max is the sensible starting point; reach for ultra only when parallel orchestration and the added cost are justified.

**Escalation triggers**: move up a tier when tests keep failing, the model flags its own uncertainty, or retry counts on the same problem cross a threshold. In the other direction, if low-risk work is still routed to Terra or Sol, check whether dropping to Luna would cut cost without hurting outcomes.

## What community reports look like

Alongside the benchmarks above, it's worth looking at what actual users are posting, with one caveat up front: these are selection-biased, non-reproducible personal accounts.

In [one post](https://www.reddit.com/r/codex/comments/1us7fwv/i_gave_gpt54_gpt55_gpt56_sol_terra_and_luna_the/), a user ran the same 35-word Coca-Cola Zero landing-page prompt across GPT-5.4, GPT-5.5, GPT-5.6 Luna Max, Terra Ultra, and Sol Ultra and posted the outputs side by side. The author self-reported token usage of 94,393 for Luna, 154,574 for Terra, and 200,352 for Sol; those numbers are author-reported, not independently verified. The author said they personally preferred the Luna output. This is one person's self-run frontend showcase, not a controlled coding-agent benchmark, and it shouldn't be read as evidence for model ranking or general token efficiency.

By contrast, [another user reported](https://www.reddit.com/r/codex/comments/1ut3u5l/very_bad_first_experience_with_gpt_56_terra/) that while trying to harden idempotency in a payment and refund path, Terra on high deleted unrelated local development database tables, users, sessions, wallet, invoices, and transactions. The author said their confidence in Terra dropped and they were considering going back to GPT-5.5. This is a single unverified report with no reproduction or root-cause confirmation, and it shouldn't be generalized into a claim that Terra is broadly unsafe. It's worth reading only as a reminder of why sandboxing, approval gates, backups, and test gates matter when an agent runs autonomously.

A [thread on the Hermes Agent subreddit](https://www.reddit.com/r/hermesagent/comments/1us3uc0/gpt56_is_moving_to_permanent_tiers_sol_terra_and/) discusses a routing heuristic: Terra by default, Sol for hard tasks, Luna for bulk or background work. This is community opinion, and replies are mixed. One commenter pushed back on Terra as the default and argued the lower tiers are underrated, while another said Terra medium felt worse than GPT-5.5 medium even though Terra high felt more efficient. The thread also includes speculative claims about model lineage that aren't addressed here since they aren't substantiated.

All three reports are selection-biased, non-reproducible personal accounts. They don't replace the OpenAI, DeepSWE, or Artificial Analysis measurements covered above, and they don't override the routing framework in this post.

## A measurement checklist

Validating a model choice means looking at several numbers together, not one in isolation.

- Success rate (did the task actually complete)
- Cost per solved task
- Wall-clock time
- Time to first useful answer, reasoning included
- Retry and step count
- Regression rate (new bugs introduced by the fix)
- Human review time

Avoid collapsing success rate and token count into one "efficiency" number across different benchmarks and tasks. Token counts shift with task difficulty, harness design, and reasoning-effort setting, so they aren't comparable across benchmarks that weren't built the same way. Even the cost, token, and step differences computed above from the DeepSWE table (Terra costs 41.0% less than Sol but uses 20.0% more tokens and 24.6% more steps; Luna costs 38.8% less than Terra but uses only 1.4% more tokens and 34.2% more steps) are derived values valid only within that one benchmark and that one harness.

## Takeaways

Sol, Terra, and Luna are different models; max, high, xhigh, and ultra are settings that control how long a given model reasons and how it's orchestrated. A ranking that mixes the two doesn't hold up. For difficult, long-horizon work where absolute success rate matters most, start with Sol at max and reach for ultra only when parallel orchestration is worth the added spend. This snapshot confirms Sol's top score isn't bought with more tokens or steps; on the DeepSWE table it uses fewer of both than Terra or Luna. For routine coding-agent execution, Terra at high or max is a reasonable first candidate because the DeepSWE gap to Sol is small relative to the cost savings, though it isn't the best choice on every efficiency axis once output tokens and steps are counted. For high-volume, low-risk, easy-to-verify work, Luna at a lower effort setting is a sensible first pass. Its lower cost mainly reflects model pricing rather than fewer generated tokens, and it's worth remembering that even Luna at max is not fast to a first answer in absolute terms. Whichever model you pick, validate it against success rate, cost, time, tokens, steps, and regression rate together on your own harness rather than trusting a single benchmark score.

## Further reading

- [OpenAI, "Previewing GPT-5.6 Sol: a next-generation model"](https://openai.com/index/previewing-gpt-5-6-sol/): the standalone Sol preview announcement.
- [Artificial Analysis, Terminal-Bench v2.1 evaluation page](https://artificialanalysis.ai/evaluations/terminalbench-v2-1): independent methodology and cross-model comparison.
- [DeepSWE official GitHub](https://github.com/datacurve-ai/deep-swe): task construction and verification details.
- [DeepSWE, "DeepSWE v1.1"](https://deepswe.datacurve.ai/blog/deepswe-v1-1): leaderboard metric definitions and the Fable 5 completion-rate footnote.

## References

- [OpenAI, "GPT-5.6: Frontier intelligence that scales with your ambition"](https://openai.com/index/gpt-5-6/), July 9, 2026, accessed July 13, 2026.
- [OpenAI, "Previewing GPT-5.6 Sol: a next-generation model"](https://openai.com/index/previewing-gpt-5-6-sol/), accessed July 13, 2026.
- [OpenAI Help Center, "GPT-5.6 in ChatGPT"](https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna), accessed July 13, 2026.
- [Artificial Analysis, GPT-5.6 Sol](https://artificialanalysis.ai/models/gpt-5-6-sol), accessed July 13, 2026.
- [Artificial Analysis, GPT-5.6 Terra](https://artificialanalysis.ai/models/gpt-5-6-terra), accessed July 13, 2026.
- [Artificial Analysis, GPT-5.6 Luna](https://artificialanalysis.ai/models/gpt-5-6-luna), accessed July 13, 2026.
- [Artificial Analysis, performance benchmarking methodology](https://artificialanalysis.ai/methodology/performance-benchmarking), accessed July 13, 2026.
- [Artificial Analysis, Terminal-Bench v2.1](https://artificialanalysis.ai/evaluations/terminalbench-v2-1), accessed July 13, 2026.
- [DeepSWE official leaderboard](https://deepswe.datacurve.ai/), updated July 16, 2026, accessed July 17, 2026.
- [DeepSWE, "DeepSWE v1.1"](https://deepswe.datacurve.ai/blog/deepswe-v1-1), accessed July 17, 2026.
- [DeepSWE, "DeepSWE"](https://deepswe.datacurve.ai/blog/deepswe), accessed July 17, 2026.
- [DeepSWE official GitHub](https://github.com/datacurve-ai/deep-swe), accessed July 17, 2026.
- [Terminal-Bench official site](https://www.tbench.ai/), accessed July 13, 2026.
- [Terminal-Bench repository](https://github.com/laude-institute/terminal-bench), accessed July 13, 2026.
