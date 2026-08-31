---
title: "SwarmWorld: LLM Agents That Cooperate Without Talking, and Technology That Outlives Them"
meta_title: ""
description: "MIT LAMM published SwarmWorld on August 26, 2026. Fifty to two hundred identical gpt-5.6-luna agents were dropped into a 72x54 grid, and the paper cuts their communication channels one by one to see what still spreads. This post covers stigmergy, the four conditions, the held-out resilience assay that removes every agent, the division of labor that appears on its own, and the boundary the authors draw around the swarm's advantage."
date: 2026-08-30T20:00:00+09:00
lastmod: 2026-08-31T10:05:00+09:00
image: "/images/posts/swarmworld-stigmergic-technological-evolution/final-checkpoint-comparison-1200.png"
categories: ["AI"]
tags: ["llm-agents", "multi-agent", "emergent-behavior", "stigmergy", "ai-research"]
author: "whackur"
translationKey: "swarmworld-stigmergic-technological-evolution"
draft: false
---

When we build multi-agent systems, one choice happens almost automatically. Agents exchange messages, share a scratchpad, and an orchestrator decides who does what. Coordination is conversation, which means you can open the logs and read what happened.

[SwarmWorld](https://arxiv.org/abs/2608.26081), posted to arXiv on August 26, 2026 by Subhadeep Pal, Fiona Y. Wang and Markus J. Buehler of MIT LAMM (Laboratory for Atomistic and Molecular Mechanics), inverts that assumption. It makes the world itself the coordination channel instead of the chat, and the results are specific. Hundreds of agents that started out identical split into explorers, builders, caretakers and coordinators, the things they build keep running after every one of them is deleted, and the collective advantage has a boundary the authors draw themselves.

## Stigmergy: coordination through traces

The concept the paper builds on is stigmergy: individuals coordinate not by instructing each other but by leaving traces in the environment that trigger the next action.

Termite mounds are the standard example. A termite deposits a pellet of soil somewhere, and that pellet becomes the signal for the next termite. Add here. Build the wall this way. No foreman holds a blueprint. Ant pheromone trails work the same way. A trace left by a successful forager attracts more foragers, and the more it gets used the stronger it becomes. Information flows between individual and environment rather than between individuals.

![Illustration of stigmergic coordination. Instead of messaging each other, agents leave artifacts with controllers in a shared world, and the next agent reads that world state and reuses it. Arrows flow only between agents and the world, never agent to agent.](/images/posts/swarmworld-stigmergic-technological-evolution/stigmergic-coordination-loop.png)

In both conditions, roughly 95% of first reuse happened through this kind of direct physical observation.

That makes stigmergy interesting for LLM agent research for a clear reason. It only works if the environment holds state and the next actor can read it. The memory lives in the world, not in a chat log. This blog covered [state-externalizing harnesses](/en/blog/harness-1-state-externalizing-search-agents/), which push a single agent's context outside its window. SwarmWorld turns that external state into a shared physical world that many agents write to.

## What SwarmWorld is

The world is a 2D lattice of 72 x 54 cells. The base environment is called BioFoundry, and it carries terrain layers, resource distributions, and environmental fields such as moisture and contamination. Agents move across it, gather and transform matter, test materials, construct persistent artifacts, and install executable controllers on them.

The central design choice is the separation of cognition from consequence. Agents propose structures and controllers inside fixed action and material schemas, and a deterministic simulator decides what actually functions. Every action passes through a transactional resolver, so there is no room for an LLM to invent an outcome. An agent claiming its filtration device cleared the contamination proves nothing. Only the physics engine's numbers count.

Controllers are what make persistence possible. Each is a deterministic straight-line program of 1 to 64 instructions over 16 floating-point registers. Named sensors expose local moisture, nutrients, temperature, solar exposure, contamination, artifact health and maturity, storage and reserve levels, opening fraction, and measured material properties. That is why artifacts keep working once agents are gone. The intelligence is compiled into the structure.

A turn works like this. Macroturns are staggered, and an agent whose turn comes up receives a local observation plus its own private memory. The LLM returns a strictly validated research-state update and a plan of up to 12 atomic actions. Execution goes through a queue, one action per agent per tick. The configuration is in the paper: 4,096 output tokens, at most 12 planned actions, a 60,000-character retrieved-context budget, and 64 private memory records.

Every agent runs the same model: gpt-5.6-luna, temperature 0.7, low reasoning effort, the same system prompt, the same action schema, the same initial capabilities, inventory limit and memory budgets. At tick zero there is nothing to tell them apart. Everything that follows starts from there.

## The experiment: identical agents, four conditions

The paper compares four conditions, removing one coordination channel at a time.

1. **Full culture**: shared world plus the full set of explicit channels. Messages, public records, teaching, trading, task claims, publication-dependent composition, and cross-agent inheritance of executable programs.
2. **No communication**: direct communication and publication are removed. The shared world and program inheritance remain.
3. **No explicit culture**: cross-agent program forking and measured skill inheritance are removed as well. Only physical stigmergy is left.
4. **Independent search**: the control. N isolated single-agent worlds, combined into an endpoint-wise best-of-N envelope. Because the winner can change from endpoint to endpoint, this is a deliberately strong control.

Two studies sit on top of that. The population-scaling study runs 4 conditions x N in {50, 100, 200} x 4 matched world seeds (3201 to 3204) for 800 discovery ticks each, 48 episodes in total. With a macroturn interval of 50, each agent gets 16 scheduled decisions. The long-horizon study runs N=100 for 3,200 ticks across full culture, no explicit culture, and a best-of-100 isolated envelope, with frozen evaluation at ticks 400, 800, 1,600, 2,400 and 3,200. That is a 12-episode matrix.

Disturbances are injected on schedules: contamination, drought and storm. These are not narrative events. They change environmental field values on the map.

The evaluation is the part worth studying. The **held-out resilience assay** freezes the complete world state at a checkpoint into 8 exact clones and then **removes every agent**. Each clone runs 288 physics ticks under a paired unseen disturbance schedule, with centers, timings and orderings that never appeared during discovery. World physics and installed artifact programs keep running, and balanced service coverage Q_s(t) is integrated and averaged to produce the held-out resilience score. The held-out disturbance seeds are 9201 to 9208.

So the question "did these agents build anything useful" is scored by how well an abandoned world holds up, not by what the agents said about their work. Beyond BioFoundry the same setup was run on AshenRealm, a volcanic materials world with metallurgical operations, and Protein Realms, a sequence-defined protein biomaterials world. Both are also 72 x 54.

## Technology that outlives its creators

The first number to look at is collaboration. Under full culture, the share of artifacts with multiple contributors was 67% at N=50, 76% at N=100, and 56% at N=200, well above the ablated conditions.

Diffusion is more striking. 99.3% of full-culture artifacts and 96.9% of no-explicit-culture artifacts were reused by an agent that did not create them. Median time to first reuse was 5 ticks versus 8, and mean adoption breadth was 13.53 versus 7.49 noncreator agents. Cut the conversation entirely and leave only physical traces, and technology still spreads almost as widely. It just spreads a little slower and a little narrower.

The mechanism behind that is the interesting part. In both conditions, roughly 95% of first reuse happened through direct physical observation. An adopter did not learn from meeting the creator. It saw the structure standing there and copied it. The authors also checked whether direct creator-to-adopter contact was enriched relative to a timestamp-shuffled null, and it exceeded the null only weakly at the shortest 25-tick window (mean ratio 1.175), falling below parity for windows from 50 to 400 ticks. Direct transmission is not consistently enriched.

Inherited programs form genealogies. Mean lineage depth for executable controllers reached 9.75 by tick 3,200, roughly half of eligible forks crossed author boundaries, and the deepest representative genealogy contains 12 fork edges. One agent's program was picked up and modified by another, then picked up and modified again, more than ten times over.

The agent-artifact network grows superlinearly. Plotting cumulative unique ties against total agents plus artifacts on log-log axes gives descriptive exponents of 3.47 for full culture and 3.48 for no explicit culture. At tick 3,200 the mean unique tie count is 4,031.3 versus 2,027.3, and the relationship reuse interval-to-next is 0.650 versus 0.588.

## Division of labor without assignment

The role analysis used label-blind clustering: 22,400 agent-windows from 20 episodes, 13 robust-scaled features, fit on a balanced sample of 16,000 windows.

Two broad modes separate first, artifact-centered behavior and mobile exploration, with a silhouette of 0.467. Inside those, four recurring states show up: constructor/operator, artifact-local caretaker, cultural coordinator, and mobile surveyor. The clusters are stable, with an adjusted Rand index of 0.999 on the broad split and 0.921 and 0.980 on the conditional splits.

The trajectory over time carries the result. In N=200, 800-tick full culture, the constructor/operator fraction goes from 0 in the first window to 0.240 in the last, while the cultural-coordinator fraction drops from 0.814 to 0.560. In N=100 over 3,200 ticks the shift is much larger: constructors go from 0.008 to 0.535 and coordinators from 0.695 to 0.292. Early on most agents roam and coordinate. Late on, more than half are building and operating. Under no explicit culture, constructors stop at 0.252 and mobile surveyors stay the majority at 0.633.

These roles are states, not identities. Window-to-window switching runs at 0.270 under full culture versus 0.102 under no explicit culture at 800 ticks, and 0.244 versus 0.138 at 3,200 ticks. The same agent builds for a while, then goes back to surveying. Keeping explicit cultural channels open makes roles more fluid, not less.

All of this came out of identical gpt-5.6-luna instances with no role assignment in the prompt.

## The bounded swarm advantage

This is the section that makes the paper credible. The authors do not stop at "the collective won."

Condition ranking in the population-scaling study is not monotonic. At N=50, full culture and no communication trailed the isolated envelope on discovery AUC. At N=100, all three shared-world conditions beat it. At N=200, no explicit culture produced the largest paired discovery gain at +0.069. More agents did not automatically mean more benefit from cooperation, and more cultural channels did not automatically mean better results.

The long-horizon study crosses several times. Full culture caught up with no explicit culture on best-artifact performance around tick 800, and passed it on portfolio resilience (the resilience of the whole technology portfolio) and cumulative artifact count near tick 1,600. It never once passed it on validated invention count. Held-out resilience changed sign across checkpoints and was effectively tied at 3,200.

![Bar chart of the SwarmWorld final checkpoint. Left panel, portfolio resilience: full culture 0.2474, no explicit culture 0.2365, isolated search 0.1794. Right panel, validated invention count: full culture 5.75, no explicit culture 7.00, isolated search 2.75. A callout below reads that the strongest single artifact at tick 3,200 was 0.3488 under isolated search versus 0.2380 under full culture.](/images/posts/swarmworld-stigmergic-technological-evolution/final-checkpoint-comparison.svg)

The final checkpoint numbers (N=100, tick 3,200) read as follows. Portfolio resilience: 0.2474 for full culture, 0.2365 for no explicit culture, 0.1794 for the isolated envelope. Validated inventions: 5.75 and 7.00 against 2.75. On held-out resilience, no explicit culture reached 0.0446 against 0.0356 for isolated search. Cumulative artifacts finished at 277.5 versus 238.5.

And the strongest single artifact at the end belonged to isolated search: 0.3488 against 0.2380 for full culture. If you want one high-performing device, the agent that worked alone for a long time produced the better one.

The authors call this the **bounded swarm advantage**. Interaction mainly supports the accumulation of a diverse, persistent technological ecology, not universally superior individual inventions. The collective covers ground. The individual digs deep.

## What this means for multi-agent design and monitoring

The paper does not make these arguments directly. The reading below is mine.

First, when the coordination channel is the environment rather than the chat, observability changes shape. Monitoring an agent society usually means reading message logs. In SwarmWorld roughly 95% of first reuse happened through physical observation, so watching messages alone would miss most of the diffusion. The same applies to real agent systems running on a shared filesystem or a shared database. What matters is what was left behind, not what was said. Wipe the logs and the traces are still there. Read clean logs and coordination may already have happened.

Second, the knockout results translate straight into architecture advice. Removing half the agents at random left 98.3% of artifacts (full culture) and 95.2% (no explicit culture) connected to at least one surviving agent. Random dropout is handled well. Targeting high-degree hubs instead cut access to 59.6% and 73.9%, and targeting brokers cut it to 62.9% and 68.4%. Distributed redundancy holds up against random failure, and hubs are the weak point under targeted removal. Anyone who has watched a hand-designed orchestrator become a single point of failure will recognize the shape.

## Limitations and next steps

Here are the caveats the authors state.

The technology portraits in Figure 7 are mechanism visualizations, not experimentally manufactured geometries. The knockout assay measures graph topology, not physical recovery in a world where the agents have actually disappeared. The held-out evaluation is also a finite window of 288 physics ticks per clone. Nothing here shows that the technology runs indefinitely.

Three next steps are named: coupling recipes, geometries and controllers to atomistic and continuum solvers; grounding sensing and disturbance in measured environmental records and embedded hardware; and embodiment through robotic platforms and autonomous laboratories. Open axes include heterogeneous model populations, agent mortality and reproduction, resource economies, and human participants sharing the same persistent world.

On reproducibility, the source repository holds the engine, configurations, replay and analysis tools, frozen figure inputs, and deterministic journal-figure generators, with offline figure generation that verifies SHA-256 hashes and writes output manifests. The paper HTML we checked does not state a public repository URL, so this is not something you can clone and run today.

## Community reaction

As of August 30, 2026, the reaction is quiet.

Corresponding author Markus Buehler summarized the result in [a post on X on August 29, 2026](https://x.com/ProfBuehlerMIT/status/2093630309585531033).

> A swarm of hundreds of initially identical agents spontaneously differentiates into explorers, builders, caretakers, and coordinators - without direct communication.
> — Markus J. Buehler, [X](https://x.com/ProfBuehlerMIT/status/2093630309585531033)

The [Hacker News submission](https://news.ycombinator.com/item?id=49490461) from the same day sits at 3 points with one comment, and that comment quotes Buehler's thread and says it looks fascinating. There is no on-topic Reddit discussion yet.

A few analysis posts exist. [explainx.ai's write-up](https://explainx.ai/blog/swarmworld-stigmergic-ai-agents-buehler-mit-august-2026) walks through the numbers against the paper, and [an evoailabs piece on Medium](https://evoailabs.medium.com/beyond-the-hive-mind-how-decentralized-ai-agents-build-persistent-technological-ecologies-45739b7a6803) frames the result as the era of orchestrating LLMs as stigmergic workers on a shared, rigorously checked substrate. That second one is opinion rather than reporting. There is no independent replication and no substantive rebuttal yet, which is about what you would expect four days after posting.

## Further reading

- [SwarmWorld full text in HTML](https://arxiv.org/html/2608.26081v1): the paper with figures and tables, for checking condition definitions and measurement details directly.
- [Generative Agents (arXiv:2304.03442)](https://arxiv.org/abs/2304.03442): the predecessor on emergent social behavior in LLM agent societies. SwarmWorld moves the focus from social behavior to functional technologies with external evaluation.
- [TerraLingua (arXiv:2603.16910)](https://arxiv.org/abs/2603.16910): the closest comparison on persistent cultural accumulation, with textual artifacts instead of externally assayed functional technologies.
- [Project Sid (arXiv:2411.00114)](https://arxiv.org/abs/2411.00114): many-agent simulation aimed at AI civilization.
- [Harness-1: Teaching Search Agents to Offload State](/en/blog/harness-1-state-externalizing-search-agents/): the single-agent view of pushing state out of the context window.
- [TradingAgents: Reading the Paper and Code Behind an LLM Trading Desk](/en/blog/tradingagents-multi-agent-llm-trading/): the opposite setup, where humans assign roles and agents coordinate by talking.

## Wrapping up

SwarmWorld drops 50 to 200 identical gpt-5.6-luna agents into a 72 x 54 grid and removes coordination channels one at a time to see what survives. A deterministic simulator, not the agents' own reports, decides what worked, and evaluation freezes the world, deletes every agent, and makes the remains survive 288 physics ticks of disturbance they never saw.

Three findings carry the paper. Technology spreads even with conversation fully cut, with roughly 95% of first reuse happening through physical observation and 96.9% of artifacts reused by a noncreator. Initially identical agents split into builders, caretakers, coordinators and surveyors with no assignment, and those roles shift with the situation rather than sticking (constructors go from 0.008 to 0.535 over 3,200 ticks under full culture). And the collective advantage has a boundary: at tick 3,200 the swarm leads on portfolio resilience (0.2474 against 0.1794) while the strongest single artifact belongs to the agent that worked alone (0.3488 against 0.2380).

If there is a practical takeaway, it is that before adding another chat channel between agents, design how they leave state behind. For broad coverage of a solution space, use a population. For one best-performing result, run a single agent for a long time. All of this is still inside a simulator, and the authors list physics solvers and robotic grounding as the work that comes next.

## References

- [SwarmWorld: Stigmergic technological evolution in societies of language-model agents](https://arxiv.org/abs/2608.26081) — Subhadeep Pal, Fiona Y. Wang, Markus J. Buehler (MIT LAMM), arXiv:2608.26081v1 [cs.AI], submitted 2026-08-26, accessed 2026-08-30
- [SwarmWorld HTML full text](https://arxiv.org/html/2608.26081v1) — arXiv, accessed 2026-08-30
- [DOI: 10.48550/arXiv.2608.26081](https://doi.org/10.48550/arXiv.2608.26081) — arXiv, accessed 2026-08-30
- [Markus Buehler's X thread](https://x.com/ProfBuehlerMIT/status/2093630309585531033) — 2026-08-29, accessed 2026-08-30
- [Hacker News thread](https://news.ycombinator.com/item?id=49490461) — submitted 2026-08-29 (3 points, 1 comment), accessed 2026-08-30
- [SwarmWorld explainer](https://explainx.ai/blog/swarmworld-stigmergic-ai-agents-buehler-mit-august-2026) — explainx.ai, accessed 2026-08-30
- [Beyond the Hive Mind](https://evoailabs.medium.com/beyond-the-hive-mind-how-decentralized-ai-agents-build-persistent-technological-ecologies-45739b7a6803) — evoailabs, Medium (opinion and analysis), accessed 2026-08-30
- [alphaXiv paper page](https://www.alphaxiv.org/abs/2608.26081) — alphaXiv, accessed 2026-08-30
- [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442) — Park et al., arXiv:2304.03442, accessed 2026-08-30
- [TerraLingua](https://arxiv.org/abs/2603.16910) — arXiv:2603.16910, accessed 2026-08-30
- [Project Sid](https://arxiv.org/abs/2411.00114) — arXiv:2411.00114, accessed 2026-08-30
