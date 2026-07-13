---
title: "On-Policy Distillation: Closing the Gap Between RL and SFT"
meta_title: ""
description: "A review of Thinking Machines Lab's on-policy distillation: sampling trajectories from the student and scoring every token against a teacher model, with the Qwen3 technical report numbers and what it takes to reproduce the method in 2026."
date: 2026-07-10T14:08:50+09:00
lastmod: 2026-07-10T14:08:50+09:00
image: ""
categories: ["AI"]
tags: ["llm", "post-training", "distillation", "reinforcement-learning", "reverse-kl"]
author: "whackur"
translationKey: "on-policy-distillation"
draft: false
---

The two standard post-training methods each leave a gap. Supervised fine-tuning (SFT) has the student imitate sequences a teacher already produced, but training happens on states the student may never actually visit, so errors compound over long generations. Reinforcement learning (RL) samples from the student's own rollouts, which fixes that mismatch, but the reward is usually a single bit or two per episode. [A post Thinking Machines Lab published in October 2025](https://thinkingmachines.ai/blog/on-policy-distillation/) proposes combining the two: sample trajectories from the student, then have a strong teacher score every token in that trajectory.

This piece works through the mechanism, what the Qwen3 technical report and Thinking Machines' own experiments actually show, and what reproducing this in 2026 requires now that the original models used in the experiments have been retired.

## What SFT and RL each leave out

Post-training methods split by where the learning signal comes from.

- **Off-policy training.** SFT is the standard case: the student copies fixed sequences a teacher (or a human) already wrote. Every token carries a target, so the signal is dense, but the student's training states diverge from the states it actually encounters at inference. Once one token goes wrong, the next is generated from a state the student never trained on, and the error compounds with sequence length. [Gudibande et al.](https://arxiv.org/abs/2305.15717) observed something adjacent: imitation captures style more readily than factual accuracy.
- **On-policy training.** RL is the standard case: rewards attach to rollouts the student generated itself, so training only touches states the student actually reaches. The trade-off is that the reward is usually sparse, a single correct/incorrect signal at the end of an episode, with no more information per extra token.

The Thinking Machines post frames this with a chess analogy: pure on-policy RL is like playing games with no coach and learning only from the final win or loss. Off-policy distillation is like watching a grandmaster's games; you see strong moves, but you're never actually in the positions where you'd need to find them yourself.

## The mechanism

On-policy distillation combines the two:

| Method | Sampling | Reward signal |
| --- | --- | --- |
| SFT | off-policy | dense |
| Reinforcement learning | on-policy | sparse |
| On-policy distillation | on-policy | dense |

**The student samples its own trajectory, and a fixed teacher scores every token in it.** Because scoring happens on states the student actually visited, the off-policy mismatch problem disappears. Because scoring is per-token, RL's sparse-reward problem disappears too.

The idea itself isn't new. [DAGGER](https://arxiv.org/abs/1011.0686) (2010) already ran teacher evaluation over the student's own trajectories iteratively, and [process reward modeling](https://arxiv.org/abs/2305.20050) scores each step of a chain of thought. Applied to language models directly, [Agarwal et al.'s GKD](https://arxiv.org/abs/2306.13649) (2023, ICLR 2024) and [MiniLLM](https://arxiv.org/abs/2306.08543) (Gu et al., ICLR 2024) cover similar ground. The Thinking Machines post extends this lineage, connects it to the [Qwen3 team's experiments](https://arxiv.org/abs/2505.09388), and publishes a simplified implementation on top of its Tinker training stack.

### The loss: reverse KL

The core loss is the per-token reverse KL divergence, evaluated on trajectories sampled from the student itself:

```text
KL(π_θ ‖ π_teacher)
= E_{x_{t+1} ~ π_θ}[log π_θ(x_{t+1}|x_{1..t})
                     - log π_teacher(x_{t+1}|x_{1..t})]
```

At every student-generated prefix `x_{1..t}`, the next token `x_{t+1}` is sampled from student policy `π_θ`, and the estimator uses the difference between the log-probabilities assigned to that token by the student and teacher policy `π_teacher`. The discount factor on future steps is set to zero in practice; Thinking Machines reports that a positive discount factor didn't improve results in its experiments.

Reverse KL is used instead of forward KL (the direction SFT effectively optimizes) for three stated reasons:

1. **Hard to hack.** Low KL always means the behavior is desirable from the teacher's point of view, unlike RL where the student can find gaps in a reward function to exploit. This is only relative to matching a fixed teacher distribution, though. It says nothing about whether the teacher's distribution is factually correct, safe, or unbiased. If the teacher is wrong or biased, the student learns to be wrong and biased in exactly the same way.
2. **Mode-seeking.** Forward KL spreads probability mass across everything the teacher might do, while reverse KL concentrates on the specific behaviors the student can actually reproduce. This helps when the student has less capacity than the teacher, at the cost of diversity. Agarwal et al. note that which divergence works best is task-dependent.
3. **Reduced exposure bias.** Errors that compound once a model lands in a state it never trained on ([Bengio et al.](https://arxiv.org/abs/1506.03099)) matter less here, because scoring happens directly on states the student generated.

One precondition matters throughout. Reverse-KL optimization can't manufacture teacher behavior that falls outside the student's support, the range of tokens the student can assign nonzero probability to. Every experiment in the post starts from a student that's already been through mid-training or SFT for this reason. SFT (the forward-KL direction) is what widens that support in the first place; on-policy distillation then reshapes the probability mass inside it to match the teacher.

### Implementation: swap the reward term in an RL loop

For a team that already has RL infrastructure, the change is small.

```text
1. Set up a sampling client for the teacher model (needs log-probability access)
2. Sample rollouts from the student policy (same procedure as RL, log-probs come for free)
3. Query the teacher for log-probabilities on the same sequences (one compute_logprobs forward pass)
4. Set per-token advantage = -reverse_KL(student, teacher)
   and train with RL's importance-sampling loss
```

No separate reward model or labeling pipeline is needed. The post's claim is that if an RL implementation already has a KL-regularization term, swapping its target to the teacher model is most of the change required. Rewards can also be computed on partial rollouts, since there's no need to wait for a sequence to finish.

## What the Qwen3 technical report shows

Table 21 of the [Qwen3 technical report](https://arxiv.org/abs/2505.09388) compares adding RL versus adding on-policy distillation, both starting from the same off-policy-distilled checkpoint.

| Method | AIME'24 | AIME'25 | MATH500 | LiveCodeBench v5 | MMLU-Redux | GPQA-Diamond | GPU hours |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Off-policy distillation checkpoint | 55.0 | 42.8 | 92.4 | 42.0 | 86.4 | 55.6 | not reported |
| + RL | 67.6 | 55.5 | 94.8 | 52.9 | 86.9 | 61.3 | 17,920 |
| + on-policy distillation | 74.4 | 65.5 | 97.0 | 60.3 | 88.3 | 63.3 | 1,800 |

From the same starting point, on-policy distillation scores higher across every benchmark using roughly a tenth of the GPU hours RL used. This is a same-report, same-checkpoint comparison from Qwen's specific setup, not a general law that distillation is always ten times cheaper than RL.

### Thinking Machines' own experiment, and where extrapolation enters

Thinking Machines Lab ran a separate experiment with Qwen3-8B-Base as the student and a Qwen3-family teacher. Full fine-tuning on 400K prompts from [OpenThoughts-3](https://arxiv.org/abs/2506.04178) (generated by QwQ-32B), an off-policy distillation step during mid-training, reached about 60% on AIME'24. Extending that log-linear scaling trend suggests roughly 70% at 2M prompts, but that number is **extrapolated, not measured**, and the post itself flags that the extrapolation assumes the scaling trend doesn't bend, which it calls non-trivial.

Starting from that 400K checkpoint, about 150 steps of on-policy distillation (roughly 77K prompts, 4 samples each) reached 70% on AIME'24. One footnote is worth flagging: the prose describes the teacher as Qwen3-32B, but an experiment footnote says the actual teacher used was Qwen3-8B, which performed slightly better, and that 32B FLOPs were used only for the compute comparison below. The model actually used and the model size used for cost accounting differ, which matters when quoting the efficiency numbers.

| Method | AIME'24 | Teacher FLOPs | Student FLOPs | Compute efficiency vs. SFT-2M |
| --- | ---: | ---: | ---: | ---: |
| SFT-400K (init) | 60% | 8.5×10^20 | 3.8×10^20 | – |
| SFT-2M (extrapolated) | ~70% (estimated) | 3.4×10^21 | 1.5×10^21 | 1x |
| Reinforcement learning | 68% | – | – | ≈1x |
| On-policy distillation | 70% | 8.4×10^19 | 8.2×10^19 | 9-30x |

The 9x to 30x range depends entirely on accounting choices. Treating the teacher-generated SFT dataset as a sunk cost, already amortized across prior runs, drops teacher FLOPs from the comparison and gives roughly 9x (about 18x by GPU hours, since log-probability computation parallelizes more easily). Including the full cost of generating a new off-policy dataset from the teacher pushes the ratio to about 30x. Thinking Machines Lab itself calls this comparison non-trivial: it's a parameter-count-based theoretical FLOPs figure that ignores real GPU parallelization, it assumes the SFT initialization already sits inside the teacher's support, it assumes access to per-token teacher log-probabilities, and it depends on the specific Tinker stack used. These numbers reflect one lab's experimental conditions, not a guarantee that carries over to other models, datasets, or infrastructure.

### A more direct efficiency comparison from the Discussion section

The same post's discussion section runs a cleaner test of dense supervision's efficiency. Starting from Qwen3-8B-Base with no additional SFT, the team trained it with RL (rank-128 LoRA, following the "LoRA Without Regret" procedure) on the DeepMath dataset, then used that RL-trained model as a teacher to distill the original base model on-policy. Distillation matched the RL model's performance in roughly 7 to 10 times fewer gradient steps; after accounting for shorter rollouts and smaller batch sizes, the post estimates an overall 50-100x compute-efficiency gain. Reverse KL dropped to near zero in under 10 steps, versus 70 for RL.

A separate experiment tested data reuse: training on a single randomly chosen prompt for 20 steps (256 rollouts per step) approached the teacher's AIME'24 performance without overfitting. RL trained repeatedly on one prompt tends to collapse into memorizing an answer; the post's interpretation is that minimizing reverse KL against the teacher's full distribution memorizes less because it's approximating a distribution rather than a single correct answer.

## Restoring capability rather than teaching new knowledge

Separately from the math benchmarks, Thinking Machines Lab ran a personalization experiment with an internal-assistant scenario. Qwen3-8B, already RL post-trained, lost a large amount of instruction-following ability ([IF-eval](https://arxiv.org/abs/2311.07911)) after further training on internal document QA data. [Prior work](https://arxiv.org/abs/2505.11711) suggests RL only tunes a small subnetwork of the base model, and a large volume of new data can simply overwrite that narrow subnetwork.

| Model | Internal QA (knowledge) | IF-eval (chat) |
| --- | ---: | ---: |
| Qwen3-8B (baseline) | 18% | 85% |
| + midtrain (100% documents) | 43% | 45% |
| + midtrain (70% documents) | 36% | 79% |
| + midtrain (70%) + on-policy distillation | 41% | 83% |

No mix of document and chat data during midtraining held IF-eval at its original level. Using the pre-midtrain Qwen3-8B as a teacher and running on-policy distillation on [Tulu 3](https://arxiv.org/abs/2411.15124) prompts, unrelated to the internal documents, recovered IF-eval to 83% with almost no loss of the newly learned knowledge.

What's notable is that an earlier version of the same model works as the teacher. Recalling behavior a model lost during fine-tuning by distilling against its own prior checkpoint is presented as a continual-learning tool, but it's worth being precise about what it restores: this is behavior recovery, not new knowledge acquisition. The document knowledge still had to come from midtraining or SFT. On-policy distillation doesn't substitute for pretraining, doesn't shortcut acquiring new knowledge, and doesn't replace the exploration RL does to find a good strategy in the first place. It's closer to a cheap way to replicate a strategy once something has already found it.

The post pushes this further with an experiment showing that even self-distillation can drift: resampling Qwen3-32B's own outputs on Tulu 3 prompts (in expectation, KL=0 against the teacher) and running SFT on that data still degrades IF-eval at any positive learning rate. Its interpretation is that any finite batch carries slightly biased gradients even when the expected KL is zero, so training on your own samples eventually becomes off-policy too. On-policy distillation avoids this because the teacher stays fixed, so the student never drifts from a genuinely on-policy target. That's the authors' interpretation, and whether it holds to the same degree across other model and data combinations isn't established by this one experiment.

## What reproduction requires in 2026

Reproducing this exactly requires access to the teacher's **per-token log-probabilities**. An ordinary text-only black-box API isn't enough; you need either open weights or a service that exposes something like `compute_logprobs`.

The documented reference configuration, Qwen3-8B-Base as student and Qwen3-32B as the teacher endpoint, was [retired from the Tinker lineup on 2026-06-12](https://tinker-docs.thinkingmachines.ai/tinker/model-deprecations/). As noted above, a footnote says the lab's actual math run used Qwen3-8B as teacher, so the retired reference configuration and the model used in that run should not be conflated. The [Tinker cookbook's distillation recipe](https://github.com/thinking-machines-lab/tinker-cookbook/tree/main/tinker_cookbook/recipes/distillation) now uses Qwen3.5-9B-Base as student and Qwen3.5-9B as teacher, and its README reports roughly 65% AIME'24 after rank-128 LoRA SFT, rising to roughly 76.7% after 200 steps of on-policy distillation. Those are the recipe's own reported figures; this piece did not reproduce or independently measure them.

## Where this leaves things

On-policy distillation pairs RL's on-policy sampling with distillation's dense per-token signal. The Qwen3 technical report and Thinking Machines Lab's own experiments both support treating it as an efficient way to align an already-capable student with a specific teacher's behavior at lower compute cost. Most of that evidence sits in math reasoning benchmarks, though, the compute-efficiency numbers swing widely with accounting choices, and reproducing the method requires teacher log-probabilities that ordinary APIs don't expose. Teaching genuinely new knowledge, and finding a good strategy in the first place, remain outside what it does.

## Further reading

- [LoRA Without Regret](https://thinkingmachines.ai/blog/lora/): Thinking Machines Lab's earlier post on the information-theoretic cost of RL
- [Defeating Nondeterminism in LLM Inference](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/): Thinking Machines Lab's earlier post on what genuinely on-policy data requires
- [RL's Razor: Why Online Reinforcement Learning Forgets Less](https://arxiv.org/abs/2509.04259): Shenfeld et al. on the relationship between on-policy training and forgetting
- [A Survey of On-Policy Distillation for Large Language Models](https://arxiv.org/abs/2604.00626): a follow-up survey of the method

## References

- [On-Policy Distillation](https://thinkingmachines.ai/blog/on-policy-distillation/): Kevin Lu, Thinking Machines Lab, 2025-10-27, accessed 2026-07-10
- [Qwen3 Technical Report](https://arxiv.org/abs/2505.09388): Qwen Team, arXiv:2505.09388, accessed 2026-07-10
- [On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes](https://arxiv.org/abs/2306.13649): Agarwal et al., arXiv:2306.13649 (ICLR 2024), accessed 2026-07-10
- [MiniLLM: Knowledge Distillation of Large Language Models](https://arxiv.org/abs/2306.08543): Gu et al., arXiv:2306.08543 (ICLR 2024), accessed 2026-07-10
- [tinker-cookbook distillation recipes](https://github.com/thinking-machines-lab/tinker-cookbook/tree/main/tinker_cookbook/recipes/distillation): Thinking Machines Lab, GitHub, accessed 2026-07-10
- [Tinker model deprecations](https://tinker-docs.thinkingmachines.ai/tinker/model-deprecations/): Thinking Machines Lab, accessed 2026-07-10
