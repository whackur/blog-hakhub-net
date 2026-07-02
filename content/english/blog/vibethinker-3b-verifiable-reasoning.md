---
title: "VibeThinker-3B: Packing Verifiable Reasoning into 3 Billion Parameters"
meta_title: ""
description: "WeiboAI's VibeThinker-3B applies multi-stage RL and self-distillation to a 3B base model, claiming frontier-level results on math and coding benchmarks. A look at what it achieves and where it falls short."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
image: ""
categories: ["AI"]
tags: ["small-language-model", "reasoning", "reinforcement-learning", "math", "coding"]
author: "whackur"
translationKey: "vibethinker-3b-verifiable-reasoning"
draft: false
---

"Small model beats big model" papers appear regularly. Usually the claim holds on a specific benchmark under specific conditions, not across the board. WeiboAI's [VibeThinker-3B](https://arxiv.org/abs/2606.16140), published June 15, 2026, follows a similar structure but draws a clearer boundary: the claim is not that a 3B model replaces a frontier generalist. The claim is that **verifiable reasoning can be compressed into a small model**, while open-domain knowledge and general dialogue still benefit from more parameters.

## Model basics

- arXiv: [2606.16140](https://arxiv.org/abs/2606.16140)
- Base model: [Qwen/Qwen2.5-Coder-3B](https://huggingface.co/Qwen/Qwen2.5-Coder-3B)
- Parameters: approx. 3,085,938,688 (BF16 safetensors)
- Authors: Sen Xu et al., Sina Weibo Inc.
- License: MIT
- Resources: [WeiboAI/VibeThinker (GitHub)](https://github.com/WeiboAI/VibeThinker), [WeiboAI/VibeThinker-3B (HuggingFace)](https://huggingface.co/WeiboAI/VibeThinker-3B)

## The central hypothesis

The authors distinguish two kinds of capability by how they scale with parameters:

- **Compressible:** verifiable reasoning, multi-step reasoning, constraint satisfaction, self-correction, math/coding/STEM problem-solving.
- **Needs broad coverage:** open-domain knowledge, general-purpose dialogue, long-tail scenario understanding, factual recall across many topics.

If this distinction holds, domains with reliable verification signals (math, code) are good candidates for a focused training push on a small model. VibeThinker-3B tests that idea.

## Training pipeline

Five stages:

### 1. Curriculum-based two-stage SFT

Stage 1 covers math, code, STEM reasoning, general dialogue, and instruction following broadly. Stage 2 shifts to hard, long-horizon reasoning samples. Seed queries are selected for having clear answers, full solutions, unit tests, or executable evaluation rules.

Rather than learning one correct solution path, the distillation preserves multiple valid reasoning traces from a teacher model. The authors call this **Diversity-Exploring Distillation**, aimed at building a spectrum of valid approaches rather than memorizing one.

### 2. Multi-domain reasoning RL

Reuses **MGPO (MaxEnt-Guided Policy Optimization)** from VibeThinker-1.5B. Samples where rollouts include both correct and incorrect answers get higher training weight than samples at the extremes (always right or always wrong). The intuition is that problems the model always solves or always fails carry almost no learning signal; the boundary problems carry the most. Training runs Math RL, then Code RL, then STEM RL. A single 64K context window preserves long reasoning trajectories without truncation.

### 3. Long2Short Math RL

After accuracy-focused RL has expanded the model's reasoning ability, a second RL pass shifts reward toward shorter correct trajectories. The goal is to maintain accuracy while reducing redundant reasoning tokens.

### 4. Offline self-distillation

Selects verified-correct trajectories from the Math/Code/STEM RL checkpoints and applies SFT back to a unified student model. A length-normalized negative log-likelihood score (learning-potential score) prioritizes traces the student currently handles poorly, so distillation adds the most value where the model is weakest.

### 5. Instruct RL

A final stage for user-facing behavior: format-sensitive prompts, long-context instructions, and general alignment examples. Explicit constraints use rule-based validators; open-ended prompts use a rubric-based reward model.

## Benchmark results

From the paper and the [model card](https://huggingface.co/WeiboAI/VibeThinker-3B). CLR-augmented scores are explained in the next section.

| Benchmark | Score | With CLR |
|-----------|-------|----------|
| AIME25 | 91.4 | 96.7 |
| AIME26 | 94.3 | 97.1 |
| HMMT25 | 89.3 | 95.4 |
| BruMO25 | 93.8 | 99.2 |
| IMO-AnswerBench | 76.4 | 80.6 |
| LiveCodeBench v6 | 80.2 Pass@1 | N/A |
| OJBench | 38.6 | N/A |
| GPQA-Diamond | N/A | 72.9 |
| IFEval | 93.4 | N/A |
| IFBench | 74.5 | N/A |

LeetCode OOD (new problems from April 25 to May 31, 2026; Python one-shot): 123 of 128, 96.1%.

Evaluation conditions vary by benchmark: math uses 64 independent generation samples averaged for Pass@1, IMO-AnswerBench uses 16, coding uses 8. Comparison model scores come from each model's own release reports or public leaderboards, not re-evaluated under an identical harness.

## CLR: Claim-Level Reliability Assessment

CLR is a test-time scaling technique that does not modify model weights.

Standard self-verification checks a whole reasoning trace at once. CLR splits the trace into individual claims or logical anchors and assesses each one's reliability separately. The paper reports this pushes Pass@1 higher on answer-verifiable math benchmarks: AIME26 goes from 94.3 to 97.1, HMMT25 from 89.3 to 95.4, BruMO25 from 93.8 to 99.2, IMO-AnswerBench from 76.4 to 80.6.

## Intended use and stated limitations

The [model card](https://huggingface.co/WeiboAI/VibeThinker-3B) is direct about scope.

**Well-suited for:**
- LeetCode and competitive programming problems
- Math olympiad, STEM reasoning, problems with verifiable answers
- Local or low-cost inference where a strong reasoning core matters
- Solving verifiable subproblems decomposed by a larger orchestrator

**Not suitable for:**
- Tool calling / function calling
- API orchestration
- Autonomous coding agents
- Broad research agents
- General chat, open-domain factual QA

The model card explicitly states the model was not trained on tool-calling or agent-based programming data, and recommends against those use cases.

## Caveats

Math evaluation mixes automated verifiers with LLM-as-judge, which means the choice of judge can affect reported numbers. Comparison scores are not from a unified re-evaluation harness. The math scores are also averages over 64 independent generations, which can differ from what a single call feels like in practice. The strong results apply to verifiable reasoning domains; treating them as evidence that a 3B model is a general frontier replacement would be overreading the paper.

## Further reading

- [arXiv:2606.16140](https://arxiv.org/abs/2606.16140): VibeThinker-3B paper
- [Qwen2.5-Coder blog](https://qwenlm.github.io/blog/qwen2.5-coder/): background on the base model
- [DeepSeek-R1 technical report](https://arxiv.org/abs/2501.12948): an earlier example of GRPO-based reasoning RL at scale
- [LiveCodeBench](https://livecodebench.github.io): the coding benchmark used in the paper

## References

- [arXiv:2606.16140 "VibeThinker-3B: Exploring the Frontier of Verifiable Reasoning in Small Language Models"](https://arxiv.org/abs/2606.16140): Xu et al., Sina Weibo Inc., submitted 2026-06-15
- [WeiboAI/VibeThinker (GitHub)](https://github.com/WeiboAI/VibeThinker): code and training pipeline, accessed 2026-06-30
- [WeiboAI/VibeThinker-3B (HuggingFace)](https://huggingface.co/WeiboAI/VibeThinker-3B): model card with usage limits and benchmark results, accessed 2026-06-30
- [Hugging Face Papers: 2606.16140](https://huggingface.co/papers/2606.16140): paper summary, accessed 2026-06-30
