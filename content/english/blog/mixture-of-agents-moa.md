---
title: "Mixture of Agents: How Layering Open-Source LLMs Beat GPT-4 Omni"
meta_title: ""
description: "MoA stacks multiple LLMs in layers, each refining the previous layer's outputs. Here's the architecture, benchmark results, variants, and how Hermes Agent integrates it."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-06-30T02:00:00+09:00
image: ""
categories: ["AI"]
tags: ["moa", "llm", "multi-agent", "ensemble", "ai-architecture"]
author: "hakhub"
translationKey: "mixture-of-agents-moa"
draft: false
---

Instead of scaling a single model up, what happens when you stack multiple models in layers and have each one refine the previous layer's output? Together AI's research team answered that in June 2024 with [arXiv:2406.04692](https://arxiv.org/abs/2406.04692). Using only open-source models, their Mixture of Agents (MoA) configuration scored 65.1% on AlpacaEval 2.0, versus 57.5% for GPT-4 Omni.

## Architecture

Each MoA layer runs multiple LLMs in parallel. Every agent receives the full output of the previous layer as context, generates its own response, and an aggregator merges those responses into the next layer's input. The pattern repeats across layers.

| Component | Role |
|---|---|
| Agent models | Models like Llama 3, Mixtral, WizardLM 2, Qwen 1.5, DBRX run in parallel |
| Aggregator | Merges each layer's outputs into the next input |
| Judge agent | Selects top-k responses when roles are split |
| Moderator | Handles consensus-based early stopping |

Together Computer's reference implementation is on GitHub ([togethercomputer/moa](https://github.com/togethercomputer/moa), Apache 2.0). The core `moa.py` is 50 lines; `advanced-moa.py` handles three or more layers; `bot.py` is an interactive CLI.

## Benchmark results

The paper's two main evaluations:

**AlpacaEval 2.0**

| Model | Score |
|---|---|
| MoA (open-source only) | 65.1% |
| GPT-4 Omni | 57.5% |

**FLASK multi-dimensional evaluation**

FLASK scores correctness, factuality, insightfulness, completeness, metacognition, and other dimensions separately. MoA led on all dimensions against Qwen1.5-110B-Chat, and beat GPT-4 Omni on correctness, factuality, insightfulness, completeness, and metacognition. These are paper-reported numbers on specific benchmarks and may not generalize uniformly across all tasks and use cases.

## Variants

Several papers since the original have proposed changes to the architecture.

| Variant | Key idea |
|---|---|
| SMoA (Sparse MoA) | Dynamic pruning activates only a subset of agents per layer (Li et al., 2024) |
| RMoA (Residual MoA) | Residual connections and embedding-based diversity selection (Xie et al., 2025) |
| DMoE (Dynamic MoE) | Dynamic convolution kernels, gating, and diversity triplet loss (Kong et al., 2025) |
| Distributed MoA | Gossip protocol for collaborative inference across edge devices (Mitra et al., 2024) |

## Quality versus diversity

One finding from MoA research goes against the obvious expectation. Self-MoA, where you combine outputs from a single high-quality model multiple times, often outperforms a mix of diverse heterogeneous models. The paper models performance as `t = αq + βd + γ` (q = quality, d = diversity), and in practice α >> β: quality dominates diversity by a wide margin.

Diversity helps when individual agents' characteristics align with the task's heterogeneity. Mixing models without considering that fit often doesn't pay off.

## Hermes Agent MoA 2.0

Nous Research documented MoA 2.0 in Hermes Agent on June 26, 2026 ([official docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/)). It's exposed as a `moa` virtual model provider, with presets appearing as selectable model options. Default preset:

| Role | Model |
|---|---|
| Reference 1 | GPT-5.5 (openai-codex) |
| Reference 2 | DeepSeek-V4-Pro (openrouter) |
| Aggregator | Claude Opus 4.8 (openrouter) |

The flow: reference models run first without tool schemas (system prompts and tool transcripts stripped to reduce cost). Their outputs go into the aggregator's private context, then the aggregator runs with the full Hermes tool schema and writes the final response. Tool execution and subsequent iterations follow the same pattern.

On Nous Research's internal HermesBench (not a third-party benchmark), the MoA configuration scored 0.8202, against 0.7607 for Claude Opus 4.8 alone and 0.7412 for GPT-5.5 alone. On SWE-bench Pro, Hermes MoA presets reportedly outperformed Claude Opus 4.8 (69.2%) and GPT-5.5 (58.6%); a specific MoA score wasn't published. Both figures are Nous Research's own measurements.

A few design decisions stand out. Reference outputs are appended at the end of the user turn, so the stable-prefix cache isn't invalidated. Credential failures in reference models don't crash the run; the failure message goes into context instead. Recursive MoA (aggregator pointing to another MoA preset) is blocked.

```yaml
# config.yaml example
moa:
  default_preset: default
  presets:
    default:
      reference_models:
        - provider: openai-codex
          model: gpt-5.5
        - provider: openrouter
          model: deepseek/deepseek-v4-pro
      aggregator:
        provider: openrouter
        model: anthropic/claude-opus-4.8
      reference_temperature: 0.6
      aggregator_temperature: 0.4
      max_tokens: 4096
      enabled: true
```

The `/moa` slash command switches to the default preset; `hermes moa configure [name]` builds a custom one; `hermes moa list` shows what's available.

The cost tradeoff is concrete: every iteration runs N reference calls plus one aggregator call, so token costs scale linearly with the number of reference models. This is also a new feature, documented in June 2026, so behavior may shift as usage patterns emerge.

## Further reading

- [arXiv:2406.04692](https://arxiv.org/abs/2406.04692): the original MoA paper
- [togethercomputer/moa](https://github.com/togethercomputer/moa): reference implementation (Apache 2.0)
- [Hermes Agent MoA docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/): Hermes integration details
- [Emergent Mind: Mixture of Agents](https://www.emergentmind.com/topics/mixture-of-agents): related papers and community coverage

## References

- [arXiv:2406.04692: Mixture-of-Agents Enhances Large Language Model Capabilities](https://arxiv.org/abs/2406.04692): Together AI et al., 2024
- [togethercomputer/moa](https://github.com/togethercomputer/moa): GitHub, Apache 2.0, accessed 2026-06-30
- [Hermes Agent MoA documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/): Nous Research, accessed 2026-06-30
- [Tony Reviews Things: MoA 2.0 review](https://www.tonyreviewsthings.com/hermes-agent-mixture-of-agents-20/): community review, accessed 2026-06-30
- [Crypto Briefing: Hermes MoA benchmarks](https://cryptobriefing.com/hermes-agent-moa-beats-claude-opus-gpt-benchmarks/): accessed 2026-06-30
