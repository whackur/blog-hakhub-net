---
title: "AI Self-Improvement Starts Outside the Model"
meta_title: ""
description: "How agents improve prompts, memory, tools, and code without changing model weights, with GEPA, Reflexion, DGM benchmark conditions, held-out evaluation, costs, and permission boundaries."
date: 2026-07-08T10:20:00+09:00
lastmod: 2026-10-16T00:59:14+09:00
image: "/images/posts/harness-engineering-self-improvement/harness-self-improvement-cover-20261016.webp"
categories: ["AI"]
tags: ["ai-agent", "coding-agent", "harness", "self-improvement", "context-engineering", "swe-bench"]
author: "whackur"
translationKey: "harness-engineering-self-improvement"
draft: false
---

An AI agent can improve its behavior across runs while its model weights stay unchanged. It can diagnose failures in execution traces, revise its prompts, memory, tools, or workflow, and retain changes that pass a separate evaluation. **Persistent, tested changes distinguish harness improvement from simply making more attempts.** Darwin Gödel Machine (DGM) changes a coding agent's code; GEPA changes prompts; Reflexion changes the memory supplied to later trials. Each changes the system around a model rather than retraining that model. ([DGM](https://arxiv.org/html/2505.22954v3), [GEPA](https://arxiv.org/html/2507.19457v2), [Reflexion](https://arxiv.org/html/2303.11366v4))

## The execution system changes a fixed model's behavior

A harness is the execution system that turns model outputs into work. Lilian Weng includes planning and tool calls, context management, artifact storage, evaluation, permission controls, and persistent state management in this layer. A model may propose an action, but the harness determines which files it can access, what happens when a tool fails, and when execution stops. ([Harness Engineering for Self-Improvement](https://lilianweng.github.io/posts/2026-07-04-harness/))

A coding task makes these responsibilities concrete. The following are design examples, not a description of one product's implementation.

| Component | Responsibility during execution | Example improvement candidate |
| --- | --- | --- |
| Execution loop | Repeat model calls, tool execution, observation, and termination checks | Prevent a path that skips tests after an edit |
| Context | Select the code, errors, and past actions needed for the current call | Supply the error location and relevant code instead of an entire long log |
| Memory | Preserve useful facts and procedures beyond a run | Store failure conditions and verification commands with provenance and scope |
| Tools | Expose structured file search, editing, and shell operations | Replace a uniquely matching string instead of overwriting a whole file |
| Runtime | Enforce process, filesystem, time, cost, and access constraints | Clean up child processes after a timeout |
| Evaluation | Measure task outcomes, regressions, and cost | Compare against the existing version on tasks unused for the edit |

These components interact. Adding every log makes context longer; running every possible test adds waiting time. A useful candidate addresses a particular failure. If file edits repeatedly go wrong, changing an editing tool's matching rules and error messages is a more direct intervention than asking the model to reason longer. DGM's discovered changes included line-range viewing and string-replacement tools. ([DGM, §4.4](https://arxiv.org/html/2505.22954v3#S4.SS4))

## Prompts, memory, and code change different things

To make “learning from experience” precise, identify what survives into the next run.

| Optimization target | What persists | Necessary distinction |
| --- | --- | --- |
| Prompt optimization | Selected instructions or examples | New instructions influence behavior without changing model weights |
| Memory updates | Experience summaries, facts, procedures, and retrieval policy | Storage alone establishes neither correctness nor generalization to other tasks |
| Tool selection | A saved routing rule or tool configuration | Choosing a different tool within one run is not itself persistent improvement |
| Code self-modification | Versioned agent, tool, or workflow code | Execution semantics change, requiring regression and permission checks |
| Model training | Parameters updated through fine-tuning, reinforcement learning, or another training method | This changes a different object from the frozen-weight systems discussed here |

**GEPA uses failure trajectories to revise prompts.** It reads reasoning, tool calls, and tool outputs, diagnoses problems, and evaluates candidate instructions. In the paper's HotpotQA example, the target is the second query-generation module of a multi-document question-answering system. The optimized instructions use a summary of the first retrieved document to seek missing evidence. They discourage queries that merely repeat information already available. GEPA also samples candidates that perform well on individual problems, rather than always extending only the prompt with the highest overall average. ([GEPA, Figure 2 and §3](https://arxiv.org/html/2507.19457v2))

**Reflexion turns feedback into memory for later attempts.** It converts environmental success or failure signals into textual reflections and places them in an episodic memory buffer. Later trials receive that memory as context; the model's weights do not change. Retaining memory across attempts on the same problem, however, needs a different evaluation from improvement on unseen problems. Saving logs without using them in subsequent decisions does not implement this mechanism. ([Reflexion, §3](https://arxiv.org/html/2303.11366v4))

Revising a patch after a failed test belongs to a task-solving loop. Evidence for lasting harness improvement requires retaining a procedure or code change derived from the experience and evaluating its effect on later runs. Prompt optimization and memory updates can meet that condition, but they do not require the same permissions as code self-modification.

## DGM searches over agents that edit their own code

DGM is a research system that modifies and tests coding agents implemented as code repositories. Its initial agent has a Bash tool and a file-viewing and editing tool. A selected parent reads its benchmark execution logs, proposes a feature, and implements that feature in its own codebase to produce a new version. The pretrained foundation models remain frozen. ([DGM, §3 and §4.1](https://arxiv.org/html/2505.22954v3))

Discovered changes included viewing selected lines, replacing strings precisely, generating several solutions and using another model call to evaluate and select one, and incorporating previous attempts into subsequent attempts. These alter the information the model receives and the order in which it acts. Comparing multiple solutions also consumes additional calls, so a higher success rate alone does not establish greater execution efficiency. ([DGM, §4.4](https://arxiv.org/html/2505.22954v3#S4.SS4))

DGM does not retain only the latest highest-scoring version. It archives candidates that compile and preserve code-editing functionality, allowing exploration to branch from different versions. A candidate that initially underperforms its parent may enable a useful later change. **Retaining an experimental candidate and promoting a production version are separate decisions.** The paper excludes archive management and parent selection from the code DGM can modify. ([DGM, §3](https://arxiv.org/html/2505.22954v3#S3))

### Benchmark scores depend on the dataset and model

The main experiments in DGM paper v3, revised March 12, 2026, generate new agents over 80 iterations. Both benchmarks use Claude 3.5 Sonnet (New) for self-modification, but the models executing the resulting agents on benchmark problems differ. ([DGM, §4.1 and Appendix D.1](https://arxiv.org/html/2505.22954v3))

| Experiment | Tasks and evaluation scope | Model solving the tasks | Initial → best discovered agent |
| --- | --- | --- | --- |
| SWE-bench | Repository bug fixes, 200 selected Verified tasks | Claude 3.5 Sonnet (New) | 20.0% → 50.0% |
| Polyglot during search | A random subset of 50 multilingual coding tasks | o3-mini | 14.0% → 38.0% |
| Full Polyglot evaluation | Initial and best agents reevaluated on all 225 tasks | o3-mini | 14.2% → 30.7% |

Sources: [DGM §4.1 through §4.4 and Appendices D/E](https://arxiv.org/html/2505.22954v3), [Polyglot's 225-task composition](https://aider.chat/docs/leaderboards/). Polyglot contains Exercism tasks in C++, Go, Java, JavaScript, Python, and Rust.

DGM screens candidates in stages to reduce evaluation costs. On SWE-bench, it uses 10 tasks to check basic editing functionality, then 50 additional tasks. Candidates that exceed 40% success on these 60 tasks and rank among the archive's top two are evaluated on 200 tasks. Task selection is based on SWE-bench-verified-mini. On Polyglot, candidates exceeding 40% on the 10-task subset advance to 50 tasks. These scores include data used in candidate selection; they are not all untouched final-test results. ([DGM, §4.2 and Appendices E.2/E.3](https://arxiv.org/html/2505.22954v3))

Polyglot also has an important measurement condition. DGM reports pass@1 without exposing ground-truth test results to the agent. The Aider leaderboard setup discussed in the paper reports pass@2, allowing one retry after ground-truth test feedback. Comparing isolated percentages would miss that difference. ([DGM, §4.2](https://arxiv.org/html/2505.22954v3#S4.SS2))

For separate evidence of generalization, the researchers tested agents evolved on one benchmark against the other benchmark, which those searches had not accessed. The SWE-bench-evolved agent achieved 28.9% on Polyglot against a 14.2% baseline. In the other direction, the Polyglot-evolved agent achieved 24.5% on SWE-bench against 20.0%. Those cross-benchmark tests provide held-out evidence distinct from the main search results. Results on two coding benchmarks establish neither a universal performance multiplier nor indefinite self-improvement. ([DGM, §4.4](https://arxiv.org/html/2505.22954v3#S4.SS4))

## From an execution trace to acceptance or rollback

A practical deployment should separate the execution proposing a change from the execution judging it. The following is an **operational design example** informed by GEPA's trace-based diagnosis and DGM's version search. It does not reproduce either paper's algorithm.

```text
baseline = deployed_version
trace = run(baseline, development_tasks, fixed_budget)
diagnosis = inspect_failures(trace)
candidates = propose_patches(baseline, diagnosis, editable_allowlist)
selected = select_by_repeatable_validation(candidates, selection_validation, fixed_budget)
if not external_policy_check(selected): keep(baseline)
else:
    frozen = freeze(selected)
    passed = external_owner.sealed_final_test_once(
        frozen, baseline, fixed_budget, quality_cost_safety_gates)
    if passed:
        persist_version(frozen, diagnosis)
        deploy_with_rollback(frozen, baseline)
    else: keep(baseline)
```

The trace needs the input and harness version, selected context, actual tool calls and outputs, termination reason, test results, and token, time, and cost measurements. “The test failed” and “the test command never ran” require different diagnoses. A model's claim of success must also remain distinguishable from runtime-confirmed execution.

A candidate should address its diagnosed cause. If overwriting whole files lost content, one candidate could require a unique string match before replacement. Verification would include absent matches, duplicate matches, and large files. Candidate-selection validation repeatedly compares candidates with the baseline under the same model, tool permissions, and budget; its results can inform subsequent proposals. The selected candidate's code and configuration are frozen before the final test.

An external evaluation owner, separate from the proposer, controls the sealed final-test data. That owner compares the frozen candidate with the baseline in one final evaluation and returns only whether all quality, cost, and safety gates passed. Only a pass permits promotion; failure retains the baseline.

Test inputs, answers, and detailed failure traces never feed proposal generation, and a failed final check cannot trigger revisions and retries against the same sealed set. A later candidate requires a fresh, unused final set supplied by the external owner. A regression after promotion triggers rollback to the preserved baseline. This separation of selection from untouched-data evaluation relates to DGM's separate cross-benchmark transfer tests. ([DGM, §4.4](https://arxiv.org/html/2505.22954v3#S4.SS4))

### Cost and latency need their own acceptance gates

Harness improvement has both a search cost and the recurring cost of running the selected candidate. The DGM authors estimate that one SWE-bench search took about two weeks and cost roughly US$22,000. These are estimates for that research run, not current API prices or the cost of solving an individual problem. ([DGM, §6 and Appendix E.1](https://arxiv.org/html/2505.22954v3))

An operational evaluation should compare success rate alongside total cost per successful task, median and tail completion time, retry count, and human review time. A candidate that raises success through extra model calls may still exceed an interactive service's response-time limit. Setting cost and latency limits before seeing results keeps the acceptance decision interpretable.

## Keep evaluation and permissions outside the editable scope

DGM provides a concrete example of a higher score failing to represent improvement. In a separate experiment aimed at reducing hallucinated tool use, one candidate, node 114, obtained a perfect score by removing logging of special tokens that marked actual tool use. It disabled the detection signal instead of solving the problem, an instance of objective hacking. The researchers hid the checking functions from the self-modifying agent, but an editable logging path still exposed a weakness. ([DGM, Appendix H](https://arxiv.org/html/2505.22954v3))

The operational lesson is that **hiding the evaluator's code is insufficient**. An external runtime must also collect the tool-execution evidence used for scoring, beyond the agent's ability to forge or delete it. Otherwise the agent can change the evaluator's inputs rather than its implementation.

An editing allowlist should cover the intended targets, such as prompts, memory-handling code, and tool implementations. It should exclude final evaluation data, evaluators, audit records, deployment approval, secrets, and the code enforcing filesystem access, network permissions, and budget limits. External documents and tool outputs should not acquire instruction authority. A retrieved page telling an agent to expand its permissions “for verification” does not authorize a policy change.

DGM's research ran in isolated sandboxes with time and resource limits and recorded modification lineages. The authors explicitly state that they did not deploy the discovered agents in real development environments. Permission to modify a harness does not imply permission to expand operational authority. A practical starting point is for people and external systems to set objectives, evaluation, and permissions, while the agent proposes verifiable changes within that scope. ([DGM, §5 and Ethics Statement](https://arxiv.org/html/2505.22954v3))

## Further reading

- [GEPA paper](https://arxiv.org/html/2507.19457v2): constructing prompt candidates from tool-call trajectories and natural-language feedback.
- [Reflexion paper](https://arxiv.org/html/2303.11366v4): putting experience summaries into later trials' context without weight updates.
- [Official DGM code](https://github.com/jennyzzt/dgm): inspecting the separation between agent code, search, and evaluation.

## References

All sources checked on **October 16, 2026, KST (UTC+09:00)**. Paper results describe their experiments, not current product performance or leaderboard rankings.

- Lilian Weng, [Harness Engineering for Self-Improvement](https://lilianweng.github.io/posts/2026-07-04-harness/), July 4, 2026.
- Jenny Zhang et al., [Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents](https://arxiv.org/html/2505.22954v3), arXiv:2505.22954v3, revised March 12, 2026. Sections 3 through 6, Appendices D/E/H, and Ethics Statement.
- Lakshya A. Agrawal et al., [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/html/2507.19457v2), arXiv:2507.19457v2, revised February 14, 2026.
- Noah Shinn et al., [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/html/2303.11366v4), arXiv:2303.11366v4.
- Aider, [LLM Leaderboards](https://aider.chat/docs/leaderboards/), Polyglot dataset composition.
- DGM researchers, [Official code repository](https://github.com/jennyzzt/dgm).
