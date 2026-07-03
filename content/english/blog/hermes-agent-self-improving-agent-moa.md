---
title: "Hermes Agent v0.18: When a Self-Improving Agent Gets MoA"
meta_title: ""
description: "Hermes Agent v0.18.0, from Nous Research, refines a self-improvement loop of memory, skills, /learn, and /journey, and turns Mixture of Agents into a virtual model provider inside that same loop."
date: 2026-07-03T17:45:00+09:00
lastmod: 2026-07-03T17:45:00+09:00
image: ""
categories: ["AI"]
tags: ["hermes-agent", "multi-agent", "moa", "ai-agent", "skills", "memory"]
author: "whackur"
translationKey: "hermes-agent-self-improving-agent-moa"
draft: false
---

Nous Research's open-source agent Hermes Agent shipped v0.18.0 on July 1, 2026. The [release notes](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.1) call it "The Judgment Release." Reading this as a routine feature update misses the point. The [official docs](https://hermes-agent.nousresearch.com/docs) describe Hermes Agent as "the self-improving AI agent," and the project is built around a loop that accumulates memory and skills the more it gets used. This post covers how that loop was refined in v0.18, and what role Mixture of Agents (MoA), now a first-class model choice in the same release, plays inside it.

## The problem Hermes Agent targets

Hermes Agent isn't a CLI tool that only runs on a laptop. It's built to live on a VPS, a GPU cluster, or serverless infrastructure, with the CLI, TUI, desktop app, and messaging gateway sharing the same core. It supports several execution backends (local, Docker, SSH, Daytona, Singularity, Modal) and connects through messaging channels including Telegram, Discord, Slack, WhatsApp, Signal, Matrix, and email.

Model and provider choice isn't locked to one vendor either. It plugs into Nous Portal, OpenRouter, OpenAI, or any custom endpoint. Cron handles scheduled runs, and subagents can take on delegated work in parallel. `execute_code` runs tool-calling scripts, MCP is supported, and skills follow the agentskills.io format. Research-oriented features include batch processing and trajectory export for reinforcement learning through Atropos.

## A self-improving agent by design

The core of Hermes Agent is a closed learning loop: memory, skill creation and self-improvement, cross-session recall, and Honcho-based user modeling.

Per the [memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory), persistent memory splits into two files. `MEMORY.md` holds the agent's own notes, capped at 2,200 characters by default. `USER.md` holds a user profile, capped at 1,375 characters. Both get injected into the system prompt as a frozen snapshot at session start, which keeps the prompt cache intact even as memory changes mid-session. The memory tool supports add, replace, and remove operations, and since v0.17 an atomic `operations` array lets several changes go through in one batch. Anything outside the injected snapshot is retrieved through session search. Teams can also swap in external memory provider plugins: Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory.

If memory stores facts and context, [skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) are closer to procedural memory: knowledge of how to do something. Skills are on-demand documents loaded only when needed, using progressive disclosure to keep token use down. The default skill directory is `~/.hermes/skills/`, holding bundled skills, skills installed from the Skills Hub, and skills the agent creates on its own. The `/learn` command turns a directory, a URL, a conversation's workflow, or pasted notes into a reusable skill. Skills follow the standard `SKILL.md` format, can bundle references, templates, scripts, and assets, and can declare their own environment variable requirements and settings.

## Judgment and verification in v0.18

According to the [release notes](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.1), roughly 1,720 commits and 998 merged pull requests landed since v0.17.0, with contributions from over 370 community members. The "Judgment" framing is about priority, not volume: the release notes report every P0 and P1 issue and pull request closed at release time, clearing around 700 top-priority items.

What actually changed is how the agent checks its own work. Coding tasks now leave verification evidence, `/goal` states completion conditions as an explicit contract, and `pre_verify` hooks can insert a check before a task is marked done. `/learn` is the skill-creation command described above; `/journey` shows a timeline of how memory and skills accumulated over time (the desktop app adds a memory graph on top). `delegate_task` runs multiple subagents in the background at once and returns consolidated results.

The desktop app now organizes work by project: a codebase sidebar, a coding rail, a review pane, and git worktree management, structured as project, then repo, then lane. The gateway for hosted and team deployments adds scale-to-zero when idle and drain coordination during rollouts. To keep self-improvement cheap, post-turn background review routes to an auxiliary model, digests context, and adjusts its own cadence. `/prompt` opens `$EDITOR` for composing long prompts, and a new Google Vertex AI provider brings Gemini in through a GCP service account with short-lived OAuth tokens.

Several security items were also addressed:

- Hardened how MCP configuration persists to disk
- Blocked a path where cron jobs could exfiltrate data through `base_url`
- Added a secret sentinel that filters file reads for embedded credentials
- Redacted Slack `xapp` tokens from logs
- Set a floor against browser tools reaching cloud metadata endpoints
- Pinned a minimum aiohttp version in response to a CVE

## How MoA works differently inside Hermes

Mixture of Agents started as a research pattern from Together AI: stack several LLMs in layers so they can reference each other's output (see the [background post](/en/blog/mixture-of-agents-moa/) for the details). Hermes Agent doesn't run that as a separate pipeline. It builds MoA into the model selection system the agent already uses.

Per the [MoA docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/), MoA is exposed as a virtual model provider called `moa`. Each named MoA preset shows up as a selectable model in the CLI, TUI, desktop app, and gateway. Selecting a preset makes that preset's aggregator the acting model: it writes the actual response and issues tool calls. Reference models run first, purely to hand the aggregator something to work from.

The sequence: Hermes resolves the selected preset, then runs the reference models without tool schemas. Neither the Hermes system prompt nor the tool-call transcript goes to them, which keeps the calls cheap and avoids providers rejecting an unfamiliar format. Reference output gets appended as private context for the aggregator, which then runs with the normal Hermes tool schema and produces the real response. If the aggregator calls a tool, Hermes executes it as usual, and the next model iteration repeats the same process over the updated conversation. Since v0.18, each reference model's full output renders as a labeled block, and the aggregator's final answer streams live.

There are two ways to reach a preset. `/moa <prompt>` is a one-shot command: it switches to the default preset for that single turn, then restores whatever model was active before. Typing `/moa` alone just prints usage, and it no longer fuzzy-matches preset names. Switching for the whole session means going through the model picker instead, either `/model default --provider moa`, `hermes model`, the dashboard, or the MoA presets section in the desktop model dropdown.

Configuration lives in the dashboard under Models, Model Settings, Mixture of Agents, in Desktop Settings under Model, Mixture of Agents, through the `hermes moa configure [name]` CLI command, or in `config.yaml`. The documented default preset:

| Role | Model |
|---|---|
| Reference 1 | GPT-5.5 (openai-codex) |
| Reference 2 | DeepSeek-V4-Pro (openrouter) |
| Aggregator | Claude Opus 4.8 (openrouter) |

`reference_temperature` and `aggregator_temperature` are optional. Leave them out and temperature isn't sent at all, so the provider's default applies. `reference_max_tokens` caps output length, but only for reference models; aggregator output isn't capped. CLI management runs through `hermes moa list`, `hermes moa configure`, `hermes moa configure review`, and `hermes moa delete review`.

A few behaviors are worth noting at the v0.18.0 documentation level. MoA doesn't appear under `hermes tools` and isn't a toggleable toolset. Setting `enabled: false` on a preset disables reference fanout only, so the aggregator answers alone. Recursive MoA (an aggregator pointing at another MoA preset) is blocked. If one reference model's credentials fail, the turn doesn't abort. The failure gets folded into context and the remaining reference models continue. After the v0.18.0 release, work continued on main to refine MoA's fanout cadence and how provider-default temperatures are handled, so some of these specifics may shift.

On Nous Research's own HermesBench, the MoA configuration (Claude Opus 4.8 as aggregator, GPT-5.5 as reference) scored 0.8202, against 0.7607 for Claude Opus 4.8 alone and 0.7412 for GPT-5.5 alone, about 6 points above the stronger single model. This is Nous's own internal benchmark, not a third-party result.

## A MoA design that preserves the prompt cache

A common worry with MoA-style setups is that routing through multiple models breaks the prompt cache every turn, adding cost and latency instead of saving them. The [MoA docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/) treat this as an explicit design goal. Selecting MoA doesn't rewrite past context, swap tool sets, or rebuild the system prompt mid-conversation.

Reference models receive a trimmed, deterministic view of the conversation, so their own caches build up normally. The aggregator gets reference output appended to the end of the latest user turn as private guidance, which keeps the stable prefix at the start of the conversation untouched. The real added cost of MoA isn't cache invalidation. It's the extra reference model calls on every iteration.

## Cost and limits

Turning on MoA adds one call per reference model on every iteration, plus the aggregator call. `reference_max_tokens` can trim wall time on the advisor side, but the aggregator output that actually becomes the response isn't capped. Recursive MoA is blocked, and a failed reference credential doesn't stop the turn, though whatever that model would have contributed is simply lost.

This is still a feature being refined. It was documented only recently, and behavior keeps shifting on main after the release. MoA also isn't a universal upgrade: it helps on hard tasks where multiple perspectives genuinely add something, and mostly adds cost and latency on ordinary requests.

## Community reaction

External coverage of MoA lands in a few different places. [Tony Reviews Things](https://www.tonyreviewsthings.com/hermes-agent-mixture-of-agents-20/) calls out the practical side: presets behave like ordinary models rather than a custom pipeline, and the behavior is consistent across CLI, TUI, gateway, and desktop. It repeats the HermesBench numbers but is explicit that they come from an internal benchmark, not third-party verification.

[Crypto Briefing](https://cryptobriefing.com/hermes-agent-moa-beats-claude-opus-gpt-benchmarks/) leads with the benchmark result, while also noting Hermes Agent's persistent memory, built-in learning loop, and external tool and API integration. It references SWE-bench Pro context without a published full leaderboard, so that part is worth reading cautiously rather than as a settled result.

[Noqta](https://noqta.tn/en/news/nous-hermes-mixture-of-agents-2-virtual-models-2026) frames MoA as "virtual model" packaging and translates the numbers into relative terms: about 8% above Opus, 11% above GPT-5.5. It also points out that HermesBench's methodology and any third-party reproduction weren't available at launch, and it spends real attention on the cost, latency, and failure-mode tradeoff of calling several providers at once. The [AgentOS guide](https://agentos.guide/moa-2-system-beats-model) leans more promotional and is best read as a signal of community interest in "a system beating a single model" rather than as an independent evaluation.

Taken together, outside coverage mostly treats MoA as a notable way to get multi-model behavior without building a custom pipeline, and the benchmark numbers everyone cites trace back to Nous. No independent reproduction has surfaced yet.

## Why this is a separate post from the MoA explainer

The MoA concept itself is covered in this blog's [earlier post](/en/blog/mixture-of-agents-moa/): the original Together AI paper, the layered architecture, AlpacaEval and FLASK results, variants like SMoA and RMoA, and the quality-versus-diversity tradeoff that Self-MoA surfaced. This post doesn't repeat that ground. It focuses on how Hermes Agent folded that pattern into a real agent that already has a self-improvement loop running. Read the earlier post for the research background, and this one for how MoA behaves in an actual product.

## Summary

Hermes Agent v0.18.0 is the release that made the self-improvement loop verifiable. `/goal` and `pre_verify` add checks on top of the memory-and-skills structure the agent already had, and `/learn` and `/journey` let users see that learning process directly. MoA, now a first-class model choice in the same release, shows one way to fold multiple models' perspectives into that loop without a separate pipeline. It costs more, the benchmark numbers are still Nous's own, and the details keep changing after release. All of that is worth keeping in mind.

## Further reading

- [Mixture of Agents: How Layering Open-Source LLMs Beat GPT-4 Omni](/en/blog/mixture-of-agents-moa/): the research background and variants
- [Hermes Agent documentation](https://hermes-agent.nousresearch.com/docs): full feature overview
- [Hermes Agent GitHub repository](https://github.com/NousResearch/hermes-agent): source and issue tracker

## References

- [Hermes Agent v0.18.0 release notes](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.1): Nous Research, accessed 2026-07-03
- [Hermes Agent v0.17.0 release notes](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.6.19): Nous Research, accessed 2026-07-03
- [Mixture of Agents documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/): Nous Research, accessed 2026-07-03
- [Skills documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills): Nous Research, accessed 2026-07-03
- [Memory documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory): Nous Research, accessed 2026-07-03
- [Tony Reviews Things: MoA 2.0 review](https://www.tonyreviewsthings.com/hermes-agent-mixture-of-agents-20/): community review, accessed 2026-07-03
- [Crypto Briefing: Hermes Agent MoA benchmarks](https://cryptobriefing.com/hermes-agent-moa-beats-claude-opus-gpt-benchmarks/): accessed 2026-07-03
- [Noqta: Nous Research Ships Mixture of Agents 2.0](https://noqta.tn/en/news/nous-hermes-mixture-of-agents-2-virtual-models-2026): accessed 2026-07-03
