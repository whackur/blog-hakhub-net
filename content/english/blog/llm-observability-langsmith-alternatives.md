---
title: "LLM Observability Without LangSmith: Five Open-Source Tools Compared"
meta_title: ""
description: "A practical comparison of Langfuse, Opik, Laminar/LMNR, Arize Phoenix, and Helicone as self-hostable LangSmith alternatives for LLM and agent debugging."
date: 2026-06-30T07:00:00+09:00
lastmod: 2026-06-30T07:00:00+09:00
image: ""
categories: ["AI"]
tags: ["llm-observability", "evals", "tracing", "langfuse", "opik"]
author: "whackur"
translationKey: "llm-observability-langsmith-alternatives"
draft: false
---

At some point in building LLM applications or agents, you need to know why a call failed, what the tool invocation looked like, or why the agent got stuck in a loop. LangSmith, LangChain's commercial observability platform, has been the default answer for this: it covers trace visualization, prompt versioning, and evaluation in one place. Its usage-based pricing and cloud-hosted architecture are where teams start looking for alternatives.

Five tools are worth knowing. They cover different parts of the space, and picking the right one depends on what you're actually trying to observe.

## LLM observability, defined

LLM observability is not the same as application logging, and the difference matters when choosing a tool. A standard HTTP request log captures request and response as flat key-value records. A single LLM application request can fan out into multiple model calls, tool invocations (search, code execution, external APIs), memory lookups, and sub-agent delegations. Reconstructing "why did this response go wrong" means navigating a nested tree, not reading a flat log line.

A few concepts are worth understanding before comparing tools:

**Trace**: the full span of processing for one user request, from first call to final response. All nested operations hang off this root node.

**Span / observation**: a single step inside a trace. One LLM call, one tool invocation, one retrieval query. Each span records start and end time, inputs and outputs, token counts, and latency.

**Session**: a set of traces sharing context, typically a conversation thread. Multiple user turns in a chat session produce multiple traces under one session.

**Prompt version**: tracking which version of a prompt ran in production. When you change a prompt, you need to know whether the change helped or hurt, and on which inputs.

**Dataset and eval**: a collection of input-output pairs collected from real traces, used to run experiments. You pick a set of test cases, run a new prompt or model against them, and compare results against previous runs or human labels.

**Annotation**: human-applied quality labels on traces or spans. Used to validate automated evals, catch edge cases automated scoring misses, and build RLHF data.

**Cost and latency**: token cost per call, model response time. In agent loops, costs compound quickly across many calls, and knowing which steps consume the most tokens is usually the first step before any optimization.

The tools below differ in which of these they support well and how much of that support is available in the self-hosted or open-source tier. That's the actual decision surface.

## Langfuse

- **GitHub**: [langfuse/langfuse](https://github.com/langfuse/langfuse) (~28.7k stars)
- **License**: MIT-based core; Enterprise features are separate

Langfuse launched in 2023 as an open-source alternative to LangSmith. It's independent of the LangChain framework; you can use it with any LLM stack. The project is built on OpenTelemetry, which means instrumentation fits naturally into observability infrastructure already in use.

It covers traces, observations/spans, sessions, user tracking, and token/cost/latency. It also handles agent graph views, prompt management with versioning, datasets, evals, and annotation. Wide integration support for LangChain, OpenAI SDK, LiteLLM, and LlamaIndex.

The [self-hosted Open Source plan](https://langfuse.com/pricing-self-host) gives you core platform features and APIs without limits, according to the docs. Project-level RBAC, data retention management, SCIM, and compliance audit logs are Enterprise. For debugging LLM apps rather than satisfying security compliance requirements, that distinction doesn't bite often.

If you're replacing LangSmith and want something with community momentum and a wide integration surface, start here.

## Opik (by Comet)

- **GitHub**: [comet-ml/opik](https://github.com/comet-ml/opik) (~19.5k stars)
- **License**: Apache-2.0

Opik is built by Comet ML, which has been in the ML experiment tracking space for years. Comet's commercial platform focuses on training experiment management and reproducibility; Opik extends that competency into LLM application and agent workflows. Apache-2.0 licensing makes it one of the cleaner choices for teams that need to audit licensing before deployment.

Opik focuses on the full loop from tracing to evaluation. You trace every LLM call, tool invocation, and agent step, then turn failures into test cases, build datasets from them, and run experiments to confirm improvements. The [self-host overview](https://www.comet.com/docs/opik/self-host/overview) states that tracing and evaluation are fully available in the open-source version. The main things missing are user management, billing, and managed support.

If "pure open-source license + minimal capability gating + agent/RAG eval workflow" is the priority list, Opik and Langfuse are essentially tied, with Opik slightly cleaner on the first two criteria.

## Laminar / LMNR

- **GitHub**: [lmnr-ai/lmnr](https://github.com/lmnr-ai/lmnr) (~3.0k stars)
- **License**: Apache-2.0

Laminar is a newer tool from the lmnr-ai team, built specifically for agent observability rather than general LLM app monitoring. Where Langfuse and Opik cover a wide surface and handle agent tracing as one feature among many, Laminar treats agent loop debugging as the primary use case. It focuses on making the sequence of tool calls and sub-agent steps legible as a timeline rather than a flat log.

The tracing SDK is OpenTelemetry-native, with real-time trace views, full-text trace search, SQL access to traces, and dashboards. The timeline view for LLM reasoning, tool calls, and sub-agent steps is a strength.

The Signals feature is interesting: it detects natural-language failure patterns like "agent is stuck in a loop" and routes them to Slack alerts, cluster analysis, or eval datasets. It integrates with MCP and CLI tools for coding agents that need to read and act on their own traces.

The tradeoff is community maturity. Laminar has less production usage at scale than Langfuse or Opik. But if agent loop debugging is your core problem, it deserves a proof of concept before you commit to a baseline.

## Arize Phoenix

- **GitHub**: [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix) (~10.1k stars)
- **License**: Elastic License 2.0 (ELv2)

Phoenix is the open-source project from Arize AI, a company focused on ML model observability and production monitoring. Arize's commercial platform handles model drift and performance degradation for deployed ML systems; Phoenix applies that observability experience to LLM applications and RAG pipelines. Arize also leads the OpenInference standard, an OpenTelemetry-compatible tracing specification designed specifically for LLM apps.

The [self-hosting page](https://arize.com/docs/phoenix/self-hosting) says free to self-host, no license fees, no usage limits, no feature gates. Traces, evals, datasets, experiments, and prompt management all work. Built on OpenTelemetry and OpenInference, which makes it strong for RAG analysis and research-oriented eval workflows.

The catch: ELv2 is source-available, not open-source by OSI definition. It restricts using the software to offer a competing managed service. Fine for internal self-hosting, but worth verifying against your own licensing requirements before building a product on it. Check the [license file](https://github.com/Arize-ai/phoenix/blob/main/LICENSE) directly.

## Helicone

- **GitHub**: [Helicone/helicone](https://github.com/Helicone/helicone) (~5.8k stars)
- **License**: Apache-2.0

Helicone started as an OpenAI-compatible LLM gateway and has grown into a request logging and cost analytics platform. The approach differs from the other tools here: instead of instrumenting application code, you route all LLM API calls through Helicone's gateway, and logging happens automatically. This makes setup fast, but it also means visibility is at the API call level rather than the application level.

Routing, fallback, caching, and per-user usage dashboards are its strong suit. If you want one place to watch all your LLM API traffic and costs, it works.

It's not a full LangSmith replacement. Complex agent traces, failure replay, eval datasets, and prompt experiment comparison are not where Helicone shines. Think of it as a complement to one of the above tools rather than a substitute.

## Picking one

| Goal | Pick |
|------|------|
| General LangSmith replacement | Langfuse |
| Open-source license + full feature set | Opik or Laminar/LMNR |
| Agent loop debugging | Laminar/LMNR, then Opik |
| RAG eval and OpenTelemetry standard | Phoenix, Langfuse |
| LLM API gateway logging | Helicone |

The practical path: stand up Langfuse as a baseline, run a side-by-side with Opik on trace-to-eval workflows, and if agent failure debugging is the dominant use case, add Laminar as a separate test. They're not mutually exclusive.

## Community observations

Langfuse sees the most consistent Reddit and Hacker News mentions as a LangSmith alternative. There are frequent self-hosting walkthroughs and some frustration about Enterprise gating. Opik is growing quickly; the trace-to-eval flow gets positive feedback. Laminar has a smaller but focused following among people building agent-heavy stacks who find Langfuse trace views too coarse.

## Further reading

- [Langfuse LangSmith comparison](https://langfuse.com/faq/all/langsmith-alternative) — official Langfuse comparison page
- [Opik self-host overview](https://www.comet.com/docs/opik/self-host/overview) — what's available in OSS
- [Laminar docs](https://docs.lmnr.ai/) — agent observability features

## References

- [Langfuse self-hosted pricing](https://langfuse.com/pricing-self-host) — Langfuse, accessed 2026-06-30
- [Opik documentation](https://www.comet.com/docs/opik/) — Comet ML, accessed 2026-06-30
- [Laminar/LMNR GitHub](https://github.com/lmnr-ai/lmnr) — lmnr-ai, accessed 2026-06-30
- [Arize Phoenix self-hosting](https://arize.com/docs/phoenix/self-hosting) — Arize, accessed 2026-06-30
- [Helicone self-hosting](https://docs.helicone.ai/getting-started/self-host/overview) — Helicone, accessed 2026-06-30
- [Phoenix license](https://github.com/Arize-ai/phoenix/blob/main/LICENSE) — GitHub, accessed 2026-06-30
