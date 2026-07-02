---
title: "Harness-1: Teaching Search Agents to Offload State"
meta_title: ""
description: "How the 20B Harness-1 search subagent externalizes working memory to a stateful harness, stabilizes RL training, and achieves 0.730 average curated recall across eight benchmarks."
date: 2026-06-30T07:00:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
image: ""
categories: ["AI"]
tags: ["search-agent", "retrieval", "rl", "rag", "agent-harness"]
author: "whackur"
translationKey: "harness-1-state-externalizing-search-agents"
draft: false
---

## Search agents and the state problem

A search agent is an AI system that answers a question by iterating through multiple searches. Unlike a one-shot retrieval lookup, it reads intermediate results, adjusts its search strategy, compares candidate documents, and checks whether specific claims are actually supported by what it found. Tasks like analyzing financial filings, tracing multi-hop facts across sources, or interpreting complex regulations need this kind of iterative work. A single query won't get you there.

The problem is state. To do any of this, the agent needs to track what it's already seen, which candidates it's keeping, which claims it's verified, and how much context budget remains. If all of that lives in the transcript, the model's context gets noisy fast. When RL training fails to improve the policy, it's not clear what went wrong: bad search decisions, forgetting state that got pushed off the edge of the context, or a skipped verification step. Transcript accumulation tangles the signal.

## The harness approach

A harness, in software engineering, wraps a unit under test to provide it with a controlled environment (inputs, mocks, fixtures). In the agent context, a search harness wraps the model to provide it with a managed state environment. Instead of the model maintaining its own working memory inside the transcript, the harness holds that state externally and hands the model a compressed rendering of it at each turn.

This is a form of cognitive offloading. People doing complex multi-step work use notebooks, whiteboards, and spreadsheets to extend working memory beyond what they can hold in their head. A search harness does the same for a model: it holds the intermediate state so the model can focus on decisions rather than bookkeeping. From RL's perspective, this means the training signal is cleaner. The policy is learning to make search decisions, not to maintain a consistent internal log.

[Harness-1](https://arxiv.org/abs/2606.02373v1) (arXiv, June 2026) is a 20B search subagent built on this idea. The code and checkpoint are public on [GitHub](https://github.com/pat-jj/harness-1) and [Hugging Face](https://huggingface.co/pat-jj/harness-1) under Apache 2.0.

## The core split

The model handles:
- what to search for
- which candidates to keep or discard
- which claims to verify
- when to stop

The harness handles:
- `P_t`: the candidate document pool after compression/dedup
- `C_t, I_t`: the curated evidence set with importance tags (very_high/high/fair/low). This is not the raw list of retrieved documents; it's the subset the model has explicitly chosen as relevant to the answer, with importance labels attached. Only documents the model curated end up here.
- `D_t`: full-text store of every document seen during the episode. Documents stay retrievable without a new search call.
- `G_t`: an evidence graph connecting entities (company names, dates, figures) and documents. This lets the model reference relationships across multiple sources without re-fetching them, which helps on multi-hop questions where the answer requires connecting information from several documents.
- `V_t`: per-claim verification records. Each entry is the result of asking "does this document actually support this claim?" Once a claim is verified, it doesn't need to be re-checked. RL can use the verification sequence as part of its reward computation.
- `H_t`: search history and result summaries
- `B_t`: context budget marker

Search results don't just get appended to a prompt. They update harness state `(s_t, a_t) → (s_{t+1}, o_{t+1})`, and the model sees a compressed rendering of that state at each turn.

## Tools

The policy issues one structured action per turn. The notable entries:

- `fan_out_search(queries)`: parallel hybrid search across up to 5 queries (RRF + rerank)
- `search_corpus(query)`: single hybrid search
- `read_document(doc_id)`: fetch full text of a specific document
- `review_docs(doc_ids)`: re-render documents already in working memory, no new search call
- `curate(add, remove, importance)`: edit the curated set
- `verify(doc_ids, claim)`: LLM entailment check per document for a specific claim
- `end_search(reasoning)`: close the episode and return the curated set

`review_docs` and `verify` matter because they're state manipulation actions, not retrieval. Without them, RL can't learn to distinguish "search more" from "process what you already have."

## Training

Supervised fine-tuning (SFT) used GPT-5.4 as a teacher agent on 899 filtered trajectories, with `openai/gpt-oss-20b` MoE as the base model. LoRA rank 32, max sequence 32,768, 3 epochs. The goal wasn't knowledge injection: it was teaching the model how to use the stateful interface.

RL used on-policy CISPO (an on-policy reinforcement learning algorithm) on SEC training queries: 128 queries per step, 8 rollouts per query, ~82K total rollouts. Reward combined curated set quality, trajectory recall, final-answer evidence recall, and a tool diversity bonus. KL anchor disabled.

Three design choices the paper argues are necessary for RL to work:

1. **Warm-started curation**: after the first successful search, automatically seed the top-8 reranked results at fair importance. This reduces catastrophic failure rewards on hard queries where the curated set would otherwise start empty.

2. **Compact derived-state rendering**: compress evidence graph, importance tags, history, budget marker, and BM25 sentence-level summaries into the model-facing state. Full document texts live in the outer tier, fetched only when needed.

3. **Diversity-preserving incentives**: without a tool diversity bonus, the policy collapses toward repeated fan_out_search calls. The paper reports that diversity drops from ~6 to ~3.5 without this reward, and curated recall stalls.

## Results

Across eight retrieval benchmarks, Harness-1 averaged a curated recall of **0.730**. The closest open search subagent, Tongyi DeepResearch 30B, is **+11.4pt** behind.

Transfer matters here. Compared to Context-1, Harness-1 gains +7.9pt on source-family benchmarks but +17.0pt on held-out transfer benchmarks. The paper reads this 2.2x gap as evidence of learning general state manipulation rather than domain-specific pattern matching.

Ablations on BrowseComp+: disabling all harness mechanisms drops Recall from 0.584 to 0.513 (FA Recall -12.2% relative). Importance tags removal alone costs FA Recall -7.9%.

One caveat worth noting: Opus-4.6 still leads on average curated recall, and there's a remaining gap on BrowseComp+ final-answer recall.

## Limitations

The paper is transparent about what Harness-1 doesn't do:

- Experiments focus on evidence-seeking retrieval. Open-ended report generation, abstention when evidence is missing, and adversarial web environments are out of scope.
- The evidence graph uses regex-based entity/date extraction, so quality varies across domains.
- `verify` is an LLM entailment proxy. It can be wrong on technical or ambiguous claims.
- Sentence-level BM25 compression can drop important information when discourse context matters.
- Full benchmark reproduction requires separate retrieval indices and credentials; it's not one-command reproducible.

## What this means for agent design

The stronger reading of Harness-1 isn't "this is a good retrieval model" but "the interface the model operates over matters as much as the model itself." Externalizing candidate pools, verification records, and importance tags into structured state gives RL a cleaner signal and gives the model a less cluttered context.

For anyone building long-horizon research agents or modular RAG pipelines, the implication is that transcript-based memory is architecturally weak for retrieval tasks. Explicit state for candidates, curated evidence, and claim verification status seems worth the engineering complexity. Harness-1 is also a retrieval subagent decoupled from the final answering model, so the curated evidence set stays reusable and auditable even if you swap the downstream answerer.

## Further reading

- [arXiv:2606.02373v1](https://arxiv.org/abs/2606.02373v1): the paper
- [pat-jj/harness-1 (GitHub)](https://github.com/pat-jj/harness-1): harness code and training pipeline
- [pat-jj/harness-1 (Hugging Face)](https://huggingface.co/pat-jj/harness-1): public checkpoint

## References

- [Harness-1: Reinforcement Learning for Search Agents with State-Externalizing Harnesses](https://arxiv.org/abs/2606.02373v1): arXiv, June 9, 2026; accessed 2026-06-30
- [GitHub: pat-jj/harness-1](https://github.com/pat-jj/harness-1): accessed 2026-06-30
- [Hugging Face: pat-jj/harness-1](https://huggingface.co/pat-jj/harness-1): accessed 2026-06-30
- [AI Times (Korean coverage)](https://www.aitimes.com/news/articleView.html?idxno=211522): AI Times, Park Chan, June 9, 2026; accessed 2026-06-30
