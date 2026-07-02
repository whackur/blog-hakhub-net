---
title: "DeepSWE: A Benchmark for Long-Horizon Coding Agents"
meta_title: ""
description: "DeepSWE from DataCurve AI evaluates coding agents on 113 original long-horizon tasks using behavior-based verification, not patch matching. Here is what it measures and how the leaderboard should be read."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
image: ""
categories: ["AI"]
tags: ["benchmark", "coding-agent", "swe-bench", "llm", "evaluation"]
author: "whackur"
translationKey: "deepswe-coding-agent-benchmark"
draft: false
---

SWE-bench has been the default coding-agent leaderboard for a while, but it has well-known weaknesses. Most tasks come from existing public issues and PR patches, so a high score might partly reflect memorization. Most tasks are also single-file bug fixes, which is not representative of the multi-file, long-horizon work that a coding agent does in practice.

[DeepSWE](https://deepswe.datacurve.ai/) from DataCurve AI tries a different approach. Tasks and reference solutions are written from scratch, scoring is behavior-based rather than patch-matching, and all leaderboard runs use a fixed agent harness so model comparisons stay consistent. Despite the name, DeepSWE is not a model or training recipe: per the [official README](https://github.com/datacurve-ai/deep-swe) and site, it is a benchmark and leaderboard.

## Task composition

DeepSWE has 113 tasks across five languages: TypeScript (35), Go (34), Python (34), JavaScript (5), Rust (5). The official site lists 91 source repositories. Most tasks (106 of 113) are classified as feature requests; the rest are 4 bug fixes and 3 enhancements. That is a meaningful difference from SWE-bench Verified, which skews toward bug fixes.

## Harbor task format

Each task follows the [Harbor framework](https://www.harborframework.com/docs/tasks) layout:

```text
task.toml         Metadata: repo URL, base commit, language, image, limits
instruction.md    The prompt the agent receives
pre_artifacts.sh  Extracts the agent's commits as a patch
environment/      Dockerfile for the prebuilt environment
tests/            Verifier entry point, held-out tests, grading config
solution/         Reference solution, hidden from the agent
```

Every task has a 5,400-second (90-minute) agent timeout. Internet access is blocked (`allow_internet = false`).

One example task gives a sense of the difficulty level. `happy-dom-abort-pending-body-reads` targets the TypeScript repo `capricorn86/happy-dom`. The instruction asks for correct abort/cleanup semantics when a shutdown interrupts Request/Response body consumption, formData parsing, and timers. This is not a function to implement in isolation; it requires understanding how multiple components interact and changing behavior across several files.

## How scoring works

### Behavior-based verification

This is the sharpest departure from SWE-bench. DeepSWE's verifier does not compare the submitted patch against a reference solution. It runs tests in a separate container to check whether the agent's changes produce the behavior described in the instruction. A solution with a different internal structure still passes if the observable behavior is correct.

The grading tests are held out from the agent. It sees only the instruction and has to infer what behavior will be verified, which closes off the shortcut of shaping an implementation around visible test code.

The `solution/` reference answer is never shown to the agent and is not used during grading. It exists for offline correctness spot-checks by reviewers.

### Separate verifier environment

Since v1.1, scoring uses Harbor's separate verifier environment:

1. The agent modifies code in an isolated container and commits.
2. `pre_artifacts.sh` extracts those commits as a patch.
3. The patch is applied to a fresh container.
4. The verifier runs tests and grades from that clean state.
5. Results go into `reward.json`, `ctrf.json`, `run.log`, and related files.

This separation prevents the agent from polluting the verification environment and makes every run reproducible from the patch alone.

### Pier and the network allowlist

DataCurve's Pier is a Harbor-compatible runner that forks Harbor and adds per-agent network allowlists. The practical problem it solves: with `allow_internet = false`, a fully offline container also blocks LLM API calls and dependency installs that the agent scaffold needs. Pier isolates the task environment while allowing only the network traffic the agent requires.

### mini-swe-agent as the fixed harness

Every leaderboard run uses [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) as the agent scaffold, with only the model swapped. The leaderboard compares models under the same scaffold. It is not a head-to-head comparison of Claude Code versus Codex as finished products. That distinction matters when reading the numbers.

## Leaderboard snapshot (June 2026)

From the official site; all runs on mini-swe-agent:

| Model | Score |
|-------|-------|
| gpt-5.5 [xhigh] | 70% ± 3% |
| claude-opus-4.8 [max] | 58% ± 2% |
| gpt-5.4 [xhigh] | 56% ± 2% |
| claude-opus-4.7 [max] | 54% ± 5% |
| claude-sonnet-4.6 [high] | 32% ± 2% |
| gemini-3.5-flash [medium] | 28% ± 4% |
| deepseek-v4-pro | 8% ± 3% |

The reasoning budget tier in brackets (xhigh, max, high, medium) affects scores. The same model at a lower budget would score lower.

## Comparison with SWE-bench

From the [official blog](https://deepswe.datacurve.ai/blog):

| Metric | SWE-Bench Verified | SWE-Bench Pro | DeepSWE |
|--------|-------------------|---------------|---------|
| Avg. prompt length | 1,700 chars | 4,614 chars | 2,158 chars |
| Avg. lines added (reference solution) | 10 | 120 | 668 |
| Avg. files edited | 1 | 5 | 7 |

The prompts are shorter than SWE-Bench Pro, but the expected change size is far larger. DeepSWE is designed to test whether an agent can navigate a codebase and produce a substantial change from a short behavioral description, rather than implement a long specification directly.

## Contamination claims and their limits

The official blog says tasks were written from scratch, not derived from existing public issue/PR/commit data. Since the reference solution is not used for grading, even if a model had seen it during pretraining, passing the verifier still requires producing the correct behavior.

That said, "contamination-free" is a design claim from DataCurve, not independently verified by a third party. Once tasks are public, they become potential training data for future models. These claims are best understood relative to a publication date.

## Running it yourself

From the [Run page](https://deepswe.datacurve.ai/run) and [README](https://github.com/datacurve-ai/deep-swe):

Before running, configure your provider's API key as an environment variable according to the provider's official documentation (e.g., Anthropic, OpenAI).

```bash
git clone https://github.com/datacurve-ai/deep-swe
uv tool install datacurve-pier

# Full run with Claude Opus 4.8
pier run -p deep-swe/tasks --agent mini-swe-agent --model anthropic/claude-opus-4-8

# Subset run (10 tasks, fixed seed)
pier run -p deep-swe/tasks --agent mini-swe-agent --n-tasks 10 --sample-seed 0

# Single task
pier run -p deep-swe/tasks/<task-id> --agent mini-swe-agent

# Parallel run via Modal
pier run -p deep-swe/tasks --agent mini-swe-agent --model <provider/model> --env modal
```

## Takeaways

Three things to keep in mind when reading DeepSWE scores. First, every score comes from the same mini-swe-agent scaffold, so the leaderboard is a model comparison, not a prediction of how finished products like Claude Code or Codex perform end to end. Second, because grading is behavior-based, having memorized the reference solution barely helps; the agent still has to implement the behavior the held-out tests demand. Third, 106 of the 113 tasks are feature requests, so DeepSWE measures a different capability than the bug-fix-heavy SWE-bench Verified. The two scores do not belong on the same axis.

## Further reading

- [SWE-bench](https://www.swebench.com): the established coding-agent benchmark DeepSWE compares against
- [SWE-agent/mini-swe-agent (GitHub)](https://github.com/SWE-agent/mini-swe-agent): the model-agnostic harness used for all DeepSWE leaderboard runs
- [Harbor Framework](https://www.harborframework.com/docs/tasks): the task format DeepSWE is built on
- [LiveCodeBench](https://livecodebench.github.io): a coding benchmark that continuously collects new problems to limit contamination

## References

- [DeepSWE official site](https://deepswe.datacurve.ai/): DataCurve AI, accessed 2026-06-30
- [datacurve-ai/deep-swe (GitHub)](https://github.com/datacurve-ai/deep-swe): README and task structure specification
- [DeepSWE blog](https://deepswe.datacurve.ai/blog): official blog, SWE-bench comparison figures
- [DeepSWE Run page](https://deepswe.datacurve.ai/run): Pier installation, network allowlist details
- [Harbor Framework Docs](https://www.harborframework.com/docs/tasks): task format specification, accessed 2026-06-30
- [SWE-agent/mini-swe-agent (GitHub)](https://github.com/SWE-agent/mini-swe-agent): agent harness, accessed 2026-06-30
