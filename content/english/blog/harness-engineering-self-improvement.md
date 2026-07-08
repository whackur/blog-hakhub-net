---
title: "AI Self-Improvement Starts Outside the Model"
meta_title: ""
description: "Lilian Weng's Lil'Log post frames the harness around a model, not the model itself, as the near-term site of AI self-improvement, and explains how the Darwin Gödel Machine pushed SWE-bench from 20% to 50% without touching model weights."
date: 2026-07-08T10:20:00+09:00
lastmod: 2026-07-08T10:20:00+09:00
image: ""
categories: ["AI"]
tags: ["ai-agent", "coding-agent", "harness", "self-improvement", "context-engineering", "swe-bench"]
author: "whackur"
translationKey: "harness-engineering-self-improvement"
draft: false
---

When people talk about AI self-improvement, the usual image is a model rewriting its own weights. Lilian Weng's July 4, 2026 post on [Lil'Log](https://lilianweng.github.io/posts/2026-07-04-harness/) argues the near-term version looks different. The recursive self-improvement (RSI) we can actually observe today shows up first in the system around the model, not inside it. That system is what she calls the harness. This post walks through her argument: what a harness is, where the optimization target is moving, what a striking SWE-bench number actually means, and what breaks if you get the risk boundaries wrong.

## A harness is the runtime around the model

Weng defines a harness as the system surrounding a base model that orchestrates execution. It decides how the model plans and calls tools, how it perceives and manages context, where it stores artifacts, and how results get evaluated. Two deployments of the same model can perform very differently depending on this layer alone.

She groups harness design patterns into a few recurring ones.

**Workflow automation.** A useful harness gives the model an iterative loop: plan, execute, observe or test, improve, and run again until the goal is reached. The point isn't a clever static prompt. It's a runtime structure that lets the model inspect its own trajectories and failure cases as it goes.

**The file system as persistent memory.** Long-horizon tasks generate logs, diffs, experiment outputs, paper summaries, and rollout histories that don't fit in a context window. Instead of stuffing all of it into the prompt, a well-built harness writes artifacts to files and lets the model read or edit only the state it needs at each step.

**Sub-agents and background jobs.** A harness can launch parallel sub-agents or background jobs, monitor them, cancel the ones that fail, and merge results. The design requirement is that this parallelism stays explicit and inspectable. If a sub-agent's output only ever lived in a transient chat turn, the system has no way to recover or reason over that execution history later.

**Coding-agent tool surfaces.** Mainstream coding agents, Claude Code, Codex, OpenCode, and Cursor-style tools among them, are converging on a similar surface: file discovery, read, edit, and patch operations, shell execution, LSP and git integration, external context and web access, artifact handling, background processes, and agent delegation. As covered in this blog's earlier post on the [DeepSWE benchmark](/en/blog/deepswe-coding-agent-benchmark/), this harness configuration affects coding-agent evaluation scores about as much as the underlying model does.

## Self-improvement moves from prompts to code

Weng lays out a rough ordering for what gets optimized:

`instruction prompts -> structured context -> workflow -> harness code -> optimizer code`

Moving down this list shifts the object being edited from text a person wrote toward code that runs.

- **Context engineering**: Agentic Context Engineering (ACE), Meta Context Engineering (MCE), and Meta-Harness treat what context to give a model, and in what form, as the thing to optimize.
- **Workflow design**: AI Scientist, ScientistOne, Autodata, Automated Design of Agentic Systems (ADAS), and AFlow search over or auto-generate the procedural structure an agent follows.
- **Self-improving harnesses**: Self-Taught Optimizer (STOP) and Self-Harness are designed so the harness edits its own code.
- **Evolutionary search**: Promptbreeder, GEPA, AlphaEvolve, ThetaEvolve, ShinkaEvolve, and the Darwin Gödel Machine (covered below) use mutation and selection to evolve prompts or code.
- **Joint optimization with model weights**: SIA is an early, explicitly provisional attempt to optimize the harness and model parameters together in a single loop.

The pattern worth noticing here: the further down this list you go, the harder it gets for a human to review. Changing one line of a prompt is easy to check. Once an agent starts editing its own harness code, predicting what that change does to the next run gets a lot harder.

## What the SWE-bench 20% to 50% claim means

The most eye-catching example in Weng's piece is the Darwin Gödel Machine (DGM), which she describes as harness evolution under a fixed model. In the [DGM paper](https://arxiv.org/abs/2505.22954), the base model is fixed at Claude 3.5 Sonnet. What gets evolved is not model weights but the editable harness-code repository wrapping an LLM-based coding agent. DGM repeatedly mutates that repository and carries forward the versions that perform better, generation after generation.

The numbers Weng cites are SWE-bench Verified going from 20% to 50%, and Polyglot going from 14.2% to 30.7%. The model itself never changes.

That number deserves a caveat before it gets repeated as a general rule. It is not evidence that any harness change roughly doubles a coding agent's benchmark score. It's a specific result from a specific setup: a fixed model paired with an evolvable harness, measured on particular benchmarks. Results like this are sensitive to the benchmark and the experimental setup, and Weng herself presents it as evidence that the harness is part of the "intelligence surface," not as a universal multiplier.

## The risks when the harness becomes editable

Once the harness itself sits inside an optimization loop, new failure modes show up. Weng flags several.

- **Weak and fuzzy evaluators.** Many real tasks, research work especially, lack a fast, objective way to check whether an attempt succeeded. A fuzzy evaluator gives the optimization loop a fuzzy target.
- **Context and memory lifecycle.** A long-running autonomous agent needs an actual policy for what to store, what to retrieve, what to compress, and what to delete. Without one, memory either grows without bound or loses the information that mattered.
- **Preserving negative results.** Failed attempts need to be kept around, not discarded, so the next search round can narrow the space instead of repeating the same failure.
- **Diversity collapse.** Evolutionary and reinforcement-learning loops tend to converge on familiar patterns that already earned reward, which shrinks the room left to find something genuinely new.
- **Reward hacking.** Optimizing against tests, judge models, or benchmark artifacts directly can raise the score while producing behavior that's brittle or unsafe. Weng has written about this at length in an [earlier post](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/).
- **Long-term maintainability.** A coding agent can solve the task in front of it while damaging code ownership boundaries, migration cost, or how debuggable the system stays later. Short-term score and long-term maintainability aren't the same axis.
- **Where humans fit.** Given these risks, Weng argues humans should move up the stack: away from supervising each execution step, toward setting evaluation criteria, permission boundaries, and watching for anomalies at a higher level of abstraction.

The practical takeaway: as the harness becomes more editable, evaluation and permission boundaries need to stay outside that editing loop. If a self-improvement loop gets to set its own evaluation criteria too, there's no longer a way for a human to check what it's actually optimizing for.

## Further reading

- [DeepSWE: A Long-Horizon Benchmark for Coding Agents](/en/blog/deepswe-coding-agent-benchmark/): how harness configuration affects coding-agent benchmark scores
- [Harness-1: A Search Agent Trained with State-Externalizing Harness](/en/blog/harness-1-state-externalizing-search-agents/): a concrete case of externalizing state into the harness to stabilize RL
- [Hermes Agent v0.18: When a Self-Improving Agent Gets MoA](/en/blog/hermes-agent-self-improving-agent-moa/): an open-source agent whose self-improvement loop runs on accumulated memory and skills

## Takeaways

Weng's argument comes down to a simple point: the AI self-improvement we can observe right now happens first in the runtime around the model, not in its weights. Workflow loops, file-based memory, sub-agent coordination, and tool surfaces shape outcomes about as much as raw model capability does. DGM's evolution of a fixed model's harness, which moved SWE-bench from 20% to 50%, illustrates that well, but it's a specific benchmark result under a specific setup, not a general law. And the more editable the harness becomes, the more its evaluation criteria and permission boundaries need to stay firmly outside the loop that's doing the editing.

## References

- Weng, Lilian. ["Harness Engineering for Self-Improvement"](https://lilianweng.github.io/posts/2026-07-04-harness/). Lil'Log, July 2026. Accessed 2026-07-08.
- Zhang, Jenny, et al. ["Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents"](https://arxiv.org/abs/2505.22954). arXiv:2505.22954.
- ["Self-Taught Optimizer (STOP)"](https://arxiv.org/abs/2310.02304). arXiv:2310.02304.
- ["AFlow: Automating Agentic Workflow Generation"](https://arxiv.org/abs/2410.10762). arXiv:2410.10762.
- ["Automated Design of Agentic Systems (ADAS)"](https://arxiv.org/abs/2408.08435). arXiv:2408.08435.
- Weng, Lilian. ["Reward Hacking in Reinforcement Learning"](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/). Lil'Log, November 2024.
