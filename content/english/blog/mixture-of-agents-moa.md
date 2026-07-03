---
title: "Mixture of Agents: How Layering Open-Source LLMs Beat GPT-4 Omni"
meta_title: ""
description: "MoA stacks multiple LLMs in layers, each refining the previous layer's outputs. Here's the architecture, benchmark results, variants, and the quality-versus-diversity tradeoff."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-07-03T17:45:00+09:00
image: ""
categories: ["AI"]
tags: ["moa", "llm", "multi-agent", "ensemble", "ai-architecture"]
author: "whackur"
translationKey: "mixture-of-agents-moa"
draft: false
---

Instead of scaling a single model up, you can stack multiple models in layers and have each one refine the previous layer's output. Together AI's research team formalized that approach in June 2024 as Mixture of Agents (MoA) in [arXiv:2406.04692](https://arxiv.org/abs/2406.04692). Using only open-source models, their MoA configuration scored 65.1% on AlpacaEval 2.0, versus 57.5% for GPT-4 Omni.

The starting observation is what the paper calls the collaborativeness of LLMs: a model tends to produce a better answer when it is given other models' answers as reference material, even when those reference answers are worse than what it would have produced on its own. MoA turns that property into an architecture.

## Architecture

Each MoA layer runs multiple LLMs in parallel. Every agent receives the full output of the previous layer as context, generates its own response, and an aggregator merges those responses into the next layer's input. The pattern repeats across layers.

| Component | Role |
|---|---|
| Agent models | Models like Llama 3, Mixtral, WizardLM 2, Qwen 1.5, DBRX run in parallel |
| Aggregator | Merges each layer's outputs into the next input |
| Judge agent | Selects top-k responses when roles are split |
| Moderator | Handles consensus-based early stopping |

Cost and latency grow with the structure. Every layer adds one inference call per agent, and a layer cannot start until all outputs from the previous layer are in, so delay stacks with depth. That is also why the paper includes MoA-Lite, a lighter configuration with fewer layers.

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

One finding from follow-up research goes against the obvious expectation. Self-MoA, where you combine multiple sampled outputs from a single high-quality model, often outperforms a mix of diverse heterogeneous models. The study that proposed Self-MoA models performance as `t = αq + βd + γ` (q = response quality, d = diversity), and in practice α >> β: quality dominates diversity by a wide margin.

Diversity helps when individual agents' characteristics align with the task's heterogeneity. Mixing models without considering that fit often doesn't pay off.

## MoA productized in Hermes Agent

MoA didn't stay a research pattern. Nous Research's open-source agent Hermes Agent turns it into a `moa` virtual model provider rather than a separate pipeline, folding multiple models' perspectives into the agent's existing loop while keeping its tool calls, memory, and prompt cache intact.

Hermes Agent itself is also a self-improving agent with memory, skills, and session recall. The reference-and-aggregator setup, the `/moa` command, configuration, HermesBench numbers, and community reaction are covered in depth in [Hermes Agent v0.18: When a Self-Improving Agent Gets MoA](/en/blog/hermes-agent-self-improving-agent-moa/).

## Further reading

- [arXiv:2406.04692](https://arxiv.org/abs/2406.04692): the original MoA paper
- [togethercomputer/moa](https://github.com/togethercomputer/moa): reference implementation (Apache 2.0)
- [Hermes Agent v0.18: When a Self-Improving Agent Gets MoA](/en/blog/hermes-agent-self-improving-agent-moa/): Hermes Agent's MoA product integration in depth
- [Emergent Mind: Mixture of Agents](https://www.emergentmind.com/topics/mixture-of-agents): related papers and community coverage

## References

- [arXiv:2406.04692: Mixture-of-Agents Enhances Large Language Model Capabilities](https://arxiv.org/abs/2406.04692): Together AI et al., 2024
- [togethercomputer/moa](https://github.com/togethercomputer/moa): GitHub, Apache 2.0, accessed 2026-06-30
- [Hermes Agent MoA documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/): Nous Research, accessed 2026-06-30
