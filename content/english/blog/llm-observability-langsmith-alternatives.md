---
title: "LLM Observability Without LangSmith: Five Open-Source Tools Compared"
meta_title: ""
description: "A practical comparison of Langfuse, Opik, Laminar/LMNR, Arize Phoenix, and Helicone as self-hostable LangSmith alternatives for LLM and agent debugging."
date: 2026-06-30T07:00:00+09:00
lastmod: 2026-06-30T07:00:00+09:00
image: ""
categories: ["AI"]
tags: ["llm-observability", "evals", "tracing", "langfuse", "opik"]
author: "hakhub"
translationKey: "llm-observability-langsmith-alternatives"
draft: true
---

At some point in building LLM applications or agents, you need to know why a call failed, what the tool invocation looked like, or why the agent got stuck in a loop. LangSmith has been the default answer, but it has pricing and hosting constraints that send a lot of teams looking for alternatives.

Five tools are worth knowing. They cover different parts of the space, and picking the right one depends on what you're actually trying to observe.

## Langfuse

- **GitHub**: [langfuse/langfuse](https://github.com/langfuse/langfuse) (~28.7k stars)
- **License**: MIT-based core; Enterprise features are separate

The most direct LangSmith replacement. Langfuse covers traces, observations/spans, sessions, user tracking, and token/cost/latency. It also handles agent graph views, prompt management with versioning, datasets, evals, and annotation. OpenTelemetry-based, with wide integration support for LangChain, OpenAI SDK, LiteLLM, and LlamaIndex.

The [self-hosted Open Source plan](https://langfuse.com/pricing-self-host) gives you core platform features and APIs without limits, according to the docs. Project-level RBAC, data retention management, SCIM, and compliance audit logs are Enterprise. For debugging LLM apps rather than satisfying security compliance teams, that distinction doesn't bite often.

If you're replacing LangSmith and want something with community momentum and a wide integration surface, start here.

## Opik (by Comet)

- **GitHub**: [comet-ml/opik](https://github.com/comet-ml/opik) (~19.5k stars)
- **License**: Apache-2.0

Opik focuses on the full loop from tracing to evaluation. You trace every LLM call, tool invocation, and agent step, then turn failures into test cases, build datasets from them, and run experiments to confirm improvements. The [self-host overview](https://www.comet.com/docs/opik/self-host/overview) states that tracing and evaluation are fully available in the open-source version. The main things missing are user management, billing, and managed support.

If "pure open-source license + minimal capability gating + agent/RAG eval workflow" is the priority list, Opik and Langfuse are essentially tied, with Opik slightly cleaner on the first two criteria.

## Laminar / LMNR

- **GitHub**: [lmnr-ai/lmnr](https://github.com/lmnr-ai/lmnr) (~3.0k stars)
- **License**: Apache-2.0

Newer and smaller, but purpose-built for agent observability in a way Langfuse and Opik aren't. Laminar gives you OpenTelemetry-native tracing, real-time trace views, full-text trace search, SQL access to traces, and dashboards. The timeline view for LLM reasoning, tool calls, and sub-agent steps is a strength.

The Signals feature is interesting: it detects natural-language failure patterns like "agent is stuck in a loop" and routes them to Slack alerts, cluster analysis, or eval datasets. It also integrates with MCP/CLI for coding agents that need to read and act on their own traces.

The tradeoff is community maturity. Laminar has less production usage at scale than Langfuse or Opik. But if agent loop debugging is your core problem, it deserves a proof of concept before you commit to a baseline.

## Arize Phoenix

- **GitHub**: [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix) (~10.1k stars)
- **License**: Elastic License 2.0 (ELv2)

The [self-hosting page](https://arize.com/docs/phoenix/self-hosting) says free to self-host, no license fees, no usage limits, no feature gates. Traces, evals, datasets, experiments, and prompt management all work. Built on OpenTelemetry and OpenInference, which makes it strong for RAG analysis and research-oriented eval workflows.

The catch: ELv2 is source-available, not open-source by OSI definition. It restricts using the software to offer a competing managed service. Fine for internal self-hosting, but worth verifying against your own licensing requirements before building a product on it. Check the [license file](https://github.com/Arize-ai/phoenix/blob/main/LICENSE) directly.

## Helicone

- **GitHub**: [Helicone/helicone](https://github.com/Helicone/helicone) (~5.8k stars)
- **License**: Apache-2.0

Helicone is an OpenAI-compatible LLM gateway with request logging, cost tracking, and latency analytics. Routing, fallback, caching, and per-user usage dashboards are its strong suit. If you want one place to watch all your LLM API traffic and costs, it works.

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
