---
title: "Don't Ship Agent Skills Without Evals: Philipp Schmid's Testing Method and SkillsBench"
meta_title: "Agent Skills Eval Methodology and SkillsBench"
description: "A digest of Philipp Schmid's skill eval methodology from Google DeepMind, the SkillsBench paper numbers, and open-source harnesses like skill-eval-harness you can use today."
date: 2026-07-18T01:00:00+09:00
lastmod: 2026-07-18T01:00:00+09:00
image: ""
categories: ["AI"]
tags: ["agent-skills", "evals", "coding-agent", "llm-agents"]
author: "whackur"
translationKey: "agent-skills-evals-skillsbench"
draft: false
---

If you use a coding agent like Claude Code, Gemini CLI, or Codex, you eventually end up writing skills: Markdown files that hand the agent your team's coding conventions, a specific SDK's usage patterns, or a deployment procedure. The problem is that almost nobody tests them. We would never ship code without tests, yet skills, which directly change how an agent behaves, get shipped after a few manual runs and a gut-level "looks fine."

Philipp Schmid of Google DeepMind tackled this head-on in his AI Engineer talk [Don't Ship Skills Without Evals](https://www.youtube.com/watch?v=0vphxNt4wyk) and the companion post [Practical Guide to Evaluating and Testing Agent Skills](https://www.philschmid.de/testing-skills). This article digests the methodology from the talk and the guide, walks through the SkillsBench paper it draws on, and lists open-source eval tooling you can actually use.

## What an Agent Skill is

An Agent Skill is a "folder of instructions, scripts, and resources" that extends an agent's abilities without retraining or fine-tuning the model. [Anthropic's Agent Skills format](https://agentskills.io/) has become the de facto standard, and harnesses such as Claude Code and Gemini CLI read the same structure.

The minimum unit is a single `SKILL.md` file with three parts.

- **Frontmatter**: a YAML `name` and `description`. This is the trigger the agent uses to decide when to load the skill, which makes it the most important part.
- **Body**: the actual instructions such as API usage, patterns, and pitfalls.
- **Resources (optional)**: `scripts/`, `examples/`, and `references/` folders the agent reads only when needed.

This layout is the progressive disclosure pattern. The agent normally sees only the description, reads the body when a relevant task arrives, and descends into reference files when it needs detail. It is how you pack deep knowledge into a skill while keeping context tokens cheap.

## Why skills need evals

Agents are nondeterministic. The same prompt produces a different solution path on every run. When an agent with a skill attached fails a task, telling apart a model limitation, a design flaw in the skill, and a skill that never triggered requires repeated runs and measurement.

Reality points the other way. A community survey found more than 47,000 skills across roughly 6,300 repositories, almost none of them with evals, and a large share of them AI-generated. In Schmid's framing: you would not ship code without tests, so why ship skills without evals?

Schmid also points out that about half of all failures happen at the **invocation stage**, not inside the skill content. If the description is vague, the agent either never reads the skill or triggers it on unrelated tasks. No amount of polishing the body fixes this, and only running tests makes it visible.

## Capability skills and preference skills

Schmid splits skills into two kinds, and the split matters because the maintenance strategy differs.

**Capability skills** compensate for things the current model cannot do consistently: new SDK syntax, a fresh API, tools released after the model's knowledge cutoff. These are inherently temporary. Once a model update absorbs that knowledge, the skill becomes token waste and a potential source of confusion.

**Preference skills** encode an organization's own style, workflows, and conventions. No matter how smart models get, they will not know your team's commit message rules or deployment procedure, so these skills are durable assets worth protecting.

The retirement rule is clean: **if the eval passes with the skill unloaded, the model has absorbed the skill's value and you can retire it.** Without an eval, that judgment is impossible. The real reason to maintain evals is not to defend your skills but to retire or rework them aggressively as models evolve.

## Principles for writing good skills

The writing guidance from the talk and the guide boils down to the following.

1. **Invest most in the description.** Half of invocation failures start here. Write it around user intent rather than API jargon, and state why, when, and how the skill should be used.
2. **Write directives, not recommendations.** "Always use X" works measurably better than "X is recommended."
3. **Keep it short.** Keep `SKILL.md` under 500 lines. Excess information wastes tokens and confuses the model.
4. **Layer the information.** Essentials at the top, details split into reference files the agent reads on demand.
5. **State goals and constraints instead of step lists.** If the workflow needs many exact steps, a script beats a skill.
6. **Say what not to do.** Defining negative cases is what prevents misfires.
7. **Remove no-ops.** Instructions the model already follows, like "write readable code," degrade performance and add cost.
8. **Test with evals from day one.** Five happy-path prompts and five negative cases are enough to start.

## An eval harness can be this simple

Schmid's central message is that skill evals do not require heavy infrastructure. The harness in his guide is roughly one Python script.

![Flow diagram showing test cases run through an agent CLI, verified by regex checks and an LLM judge, and aggregated into an ablation report](/images/posts/agent-skills-evals-skillsbench/eval-harness-flow.svg)

*The basic structure of a skill eval harness, redrawn from the philschmid.de guide.*

**1) Define test cases.** Write prompts and expected checks in JSON or YAML. Always include negative cases where the skill must not trigger (`should_trigger: false`).

```json
{
  "id": "py_basic_generation",
  "prompt": "Write a Python script that sends text to Gemini and prints the response",
  "should_trigger": true,
  "expected_checks": ["correct_sdk", "no_old_sdk", "current_model"]
}
```

**2) Run the agent.** Invoke the agent CLI via subprocess and parse its JSON output. Run each case 3 to 5 times in a clean environment so you see a distribution, not a single result.

**3) Deterministic checks.** Run regexes over the output code. Checks like "does it import the correct SDK," "is a deprecated model ID such as `gemini-1.5-pro` absent," and "does it follow the prescribed API call pattern" are fast and free with regex alone.

**4) LLM-as-judge only where needed.** Qualitative criteria that regex cannot capture, such as design quality, go to an LLM grader with a Pydantic schema attached via structured output. It adds cost and latency, so use it selectively.

**5) Ablation.** Run the same suite with the skill on and off and measure the pass-rate gap. That gap is the skill's contribution, and when it disappears, it is retirement time.

One principle matters throughout: evaluate outcomes, not paths. Agents solve problems creatively, so checking whether tools were used in a specific order marks perfectly good solutions as failures.

The guide's case study shows the method pays off. Testing a Gemini Interactions API skill with 17 cases (12 Python, 5 TypeScript) gave an initial pass rate of 66.7%. Two fixes, rewriting the description from API jargon to user intent and turning recommendations into directives, brought it to 100%. Most failures were trigger problems, not content problems.

## SkillsBench: measuring skill impact systematically

Separate from the survey cited in the talk, the academic measurement of skill impact comes from the [SkillsBench paper](https://arxiv.org/abs/2602.12670) and the [benchflow-ai/skillsbench](https://github.com/benchflow-ai/skillsbench) repository (Apache 2.0).

The structure is gym-style. Each task ships `task.md`, a Docker environment with a skills folder, an oracle solve script, and a deterministic verifier. The rule "the oracle must pass before the agent runs" guarantees every task is actually verifiable.

The headline numbers:

- Across 87 tasks in 8 domains, curated skills raised the average pass rate from 33.9% to 50.5% (+16.6 percentage points).
- Gains vary widely, from +4.1 to +25.7pp across configurations, and by domain from +4.5pp for Software Engineering to +51.9pp for Healthcare. The natural reading is that skills help most in domains where the model's pretraining is weakest.
- On some tasks, skills made results worse (negative deltas). Skills are not a free win.

The most striking result: skills the agent generated for itself (self-generated skills) were nearly useless or actively harmful. The gap between skills refined by humans observing failures and skills a model produced from its own knowledge was large. That is quantitative backing for exactly Schmid's practical advice: run the eval, then fix the description.

## Community reaction

SkillsBench sparked a large [Hacker News thread with 364 points and 171 comments](https://news.ycombinator.com/item?id=47040430). The recurring points:

- The most-voiced criticism targeted the self-generation setup: having the model write skills from its own knowledge with no external information differs from how practitioners actually author skills.
- Practitioners repeatedly argued that a skill's real value lies in the loop of observing failures and improving through feedback. Several framed skills as context-specific notepads rather than devices that create new information.
- The gap between Healthcare (+51.9pp) and Software Engineering (+4.5pp) fueled the interpretation that skills work best where models are weakest.
- A paper author joined the thread and confirmed the distinction between feedback-driven and self-generated skills.

Schmid's guide itself was discussed in a [separate HN thread](https://news.ycombinator.com/item?id=46822519), and OpenAI published a [similar skill-eval guide](https://developers.openai.com/blog/eval-skills) around the same time. Skill testing is settling in as an ecosystem-wide concern rather than a single vendor's topic.

## Open source you can use today

If you want to follow the talk's approach in practice, these projects are worth a look.

- [philschmid.de/testing-skills](https://www.philschmid.de/testing-skills): there is no dedicated repo, but the Python harness code in the post is the de facto reference implementation. The case-study subjects [google-gemini/gemini-skills](https://github.com/google-gemini/gemini-skills) and the skill examples in [anthropics/claude-code](https://github.com/anthropics/claude-code) pair well with it.
- [benchflow-ai/skillsbench](https://github.com/benchflow-ai/skillsbench): the benchmark covered above. Its Docker-based task definitions and verifier layout are a good template for designing your own evals.
- [adewale/skill-eval-harness](https://github.com/adewale/skill-eval-harness): a dedicated harness supporting paired skill on/off comparison, trace artifacts, and runner adapters.
- [mgechev/skillgrade](https://github.com/mgechev/skillgrade): a lightweight tool billing itself as "unit tests" for skills.
- [darkrishabh/agent-skills-eval](https://github.com/darkrishabh/agent-skills-eval): a test runner for agentskills.io-style skills.
- [aws-samples/sample-agent-skill-eval](https://github.com/aws-samples/sample-agent-skill-eval): AWS's skill eval sample.
- [benchflow-ai/awesome-evals](https://github.com/benchflow-ai/awesome-evals): a curated list of papers, posts, and tools on agent evaluation.

## Further reading

- [AI Self-Improvement Starts Outside the Model](/en/blog/harness-engineering-self-improvement/): the view that harness components, including skills and memory, drive agent performance
- [DeepSWE: A Benchmark for Long-Horizon Coding Agents](/en/blog/deepswe-coding-agent-benchmark/): another benchmark that evaluates coding agents on verifiable tasks
- [LLM Observability Without LangSmith: Five Open-Source Tools Compared](/en/blog/llm-observability-langsmith-alternatives/): observability tools to look at once evals move into production

## Takeaways

Skills are becoming the deployment unit of the agent era, but the testing culture around them is where code was a decade ago. Three things stick from Schmid's method. First, half of skill failures are description (trigger) problems rather than content problems, so fix those first. Second, an eval can start with 10 to 20 JSON cases and regex checks; there is no reason to wait for a perfect framework. Third, keep measuring each skill's contribution with ablations and retire it without regret once the model catches up.

The SkillsBench numbers add quantitative weight: well-curated skills buy 16+ percentage points of average pass rate, while carelessly made ones do nothing or cause harm. A good starting point is to pick your single most-used skill and write five test cases for it.

## References

- [Don't Ship Skills Without Evals](https://www.youtube.com/watch?v=0vphxNt4wyk): Philipp Schmid, AI Engineer talk (YouTube). Accessed 2026-07-18
- [Practical Guide to Evaluating and Testing Agent Skills](https://www.philschmid.de/testing-skills): philschmid.de. Accessed 2026-07-18
- [SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks](https://arxiv.org/abs/2602.12670): arXiv:2602.12670
- [benchflow-ai/skillsbench](https://github.com/benchflow-ai/skillsbench): GitHub, Apache 2.0
- [SkillsBench Hacker News discussion](https://news.ycombinator.com/item?id=47040430): 364 points, 171 comments. Accessed 2026-07-18
- [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills): OpenAI Developers
- [Agent Skills format](https://agentskills.io/): agentskills.io
