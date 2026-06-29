---
title: "Qwen3.6-35B-A3B: Community Reviews, Uncensored Variants, and MTP Benchmarks"
meta_title: ""
description: "From the 1.2M-download uncensored variant to real MTP acceleration numbers on 12 GB and 16 GB VRAM. What the community has found running Qwen3.6-35B-A3B locally."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-06-30T02:00:00+09:00
image: ""
categories: ["Local LLM"]
tags: ["qwen", "local-llm", "moe", "mtp", "uncensored", "llama-cpp"]
author: "hakhub"
translationKey: "qwen3-6-35b-a3b-community-reviews"
draft: false
---

Alibaba released Qwen3.6-35B-A3B in April 2026: a 35B-parameter MoE model with around 3B active per token, a 262K native context, and an official SWE-bench score of 73.4%. Two months in, it's the most widely tested 35B-class model in the local LLM community.

This post compiles what people have found on Reddit, HackerNews, and personal blogs. These are individual experiences; results depend heavily on hardware, driver version, and settings. Independent replication is needed before drawing firm conclusions.

## Specs

| Field | Value |
|---|---|
| Architecture | MoE (256 experts, 8 routed + 1 shared per token) |
| Parameters | 35B total / ~3B active |
| Context | 262K (extendable to 1M via YaRN) |
| Modalities | Text, image, video |
| License | Apache 2.0 |

Official benchmarks (Alibaba-reported): SWE-bench 73.4%, GPQA 86.0, LiveCodeBench v6 80.7, MMLU-Pro 85.2, AIME 2026 92.7.

## Uncensored variants

The base model has significant refusal behavior on certain topics. Several community variants strip or reduce that.

### HauhauCS Aggressive

According to the [r/hermesagent definitive variant guide](https://www.reddit.com/r/hermesagent/comments/1tmp2qy/qwen3635ba3b_community_variants_the_definitive/), by June 2026 the HauhauCS Aggressive variant had over 1.22 million downloads and 761 likes, making it the most tested uncensored option. The creator reports 0 refusals across 465 tests with no capability loss. VRAM requirements are roughly 22 GB for Q4_K_P and 20 GB for IQ4_XS. The creator acknowledges sporadic topic drift in long agentic loops.

The community consensus from that guide is that the model answers exactly what it is asked and produces unusual outputs only when given unusual inputs — in short, behavior tracks the user's prompts rather than the model's own tendencies (see [r/hermesagent guide](https://www.reddit.com/r/hermesagent/comments/1tmp2qy/qwen3635ba3b_community_variants_the_definitive/)).

### Other variants

| Variant | Technique | Downloads | Notes |
|---|---|---|---|
| Wasserstein (LuffyTheFox) | Embedding-space Wasserstein distance | 455K | Different uncensoring path; edge-case behavior may differ |
| heretic (llmfan46) | Abliteration + decensor hybrid | 53K | KL divergence 0.0015, 88% fewer refusals |
| huihui-ai Abliterated | Pure abliteration | 19K | Creator describes it as "crude, proof-of-concept" |

## Hermes Agent compatibility

### What works well

From the [r/hermesagent guide](https://www.reddit.com/r/hermesagent/comments/1tmp2qy/qwen3635ba3b_community_variants_the_definitive/) and the [r/LocalLLM tool-calling test thread](https://www.reddit.com/r/LocalLLM/comments/1sqpsut/qwen_3635ba3b_reddit_asked_so_i_tested_if_the_35/):

- **Tool calling**: Improved stability over Qwen3.5. One independently measured MCPMark score of 37.0.
- **Coding**: Codebase-wide analysis and modification gets consistently positive marks.
- **Reasoning**: Deep reasoning traces praised for complex problems.
- **Value**: Several users describe frontier-level performance locally at around 21 GB VRAM.

Simon Willison wrote on his blog that ["on my laptop, Qwen3.6 drew a better pelican than Claude Opus 4.7"](https://simonwillison.net/2026/Apr/16/qwen-beats-opus/). A comment on [HN](https://news.ycombinator.com/item?id=47798382) reported solving 11 out of 98 Power Ranking tasks. Both are individual data points.

### Known issues

Reported consistently across threads (see [HackerNoon's overview](https://hackernoon.com/qwen36-35b-a3b-uncensored-a-35b-moe-model-with-262k-context) and the r/hermesagent guide):

- **Tool-call loops**: The most-cited problem. The model repeatedly calls the same tool.
- **Topic drift**: Shows up in long agentic runs; the creator of HauhauCS Aggressive acknowledges this.
- **Temperature sensitivity**: temp=1.0 is widely recommended to reduce repetition and looping. Default 0.6-0.8 produces more loop behavior.
- **Code recall**: Distilled variants show lower CodeNeedle scores, with potential for mistakes when reproducing code.

### Recommended settings

```
temp=1.0, top_k=20, presence_penalty=1.5, top_p=0.95
--jinja --reasoning-budget 4096 --spec-type draft-mtp  # if MTP enabled
enable_thinking: false  # if it interferes with tool call parsing
```

## MTP acceleration benchmarks

Multi-Token Prediction (MTP) predicts multiple tokens at once to increase generation speed. Enable it in llama.cpp with `--spec-type draft-mtp`. Results differ substantially based on available VRAM.

### 12 GB VRAM (RTX 4070 Super)

From the [r/LocalLLaMA K_P quants thread](https://www.reddit.com/r/LocalLLaMA/comments/1snlo1x/qwen3635ba3b_uncensored_aggressive_is_out_with_k/): settings `-fitt 1536`, `--spec-draft-n-max 2`, `-ctk/-ctv q8_0`.

- Result: 70-82 tok/s at 128K context
- Acceptance rate: 0.69 to 0.95 depending on the task
- This combination makes a 35B-class model with 128K context viable at 12 GB VRAM.

### 16 GB VRAM (RTX 5080)

| Setup | Speed |
|---|---|
| Q4_K_XL + MTP | 74 tok/s (acceptance ~79.5%) |
| Q4_K_XL, no MTP, short context | 97 tok/s |
| Q4_K_XL, no MTP, 128K context | 56 tok/s |

At 128K context, prompt processing runs around 1,584 tok/s (about 81 seconds). MTP only helps when the full model fits in VRAM. If the MTP compute buffer forces MoE expert layers onto CPU, that bottleneck can make MTP slower than running without it, even with a high acceptance rate.

These numbers are from individual community members. Hardware, drivers, and settings all affect results.

## Variant summary

| Variant | Type | Downloads | VRAM | MTP | Notes |
|---|---|---|---|---|---|
| Qwopus v1 | Reasoning Distilled | 299K | ~22 GB | Not released | temp=1.0 recommended |
| lordx64 Opus 4.7 | Reasoning Distilled | 158K | ~22 GB | Via APEX | Cleanest reasoning traces |
| hesamation Opus 4.6 | Reasoning Distilled | 206K | ~22 GB | Via APEX | MMLU-Pro 75.71% (70 questions) |
| HauhauCS Aggressive | Uncensored | 1.22M | ~22 GB | Not released | Most downloads, most tested |
| heretic | Abliterated | 54K | ~22 GB | Built-in | KL divergence 0.0015 |
| unsloth MTP | Vanilla+MTP | 548K | ~23 GB | Built-in | Reference MTP implementation |
| mudler APEX MTP | APEX+MTP | 33K | ~18 GB | Built-in | Best quality-per-byte for MoE |

## Limitations and open questions

Community data means independent replication is needed before drawing strong conclusions. MTP and Vision (`--mmproj`) cannot run in parallel in llama.cpp. Qwopus + MTP and HauhauCS Balanced/Moderate variants are frequently requested but not yet released. MTP performance data for 24 GB+ GPUs is limited.

## Further reading

- [r/hermesagent definitive variant guide](https://www.reddit.com/r/hermesagent/comments/1tmp2qy/qwen3635ba3b_community_variants_the_definitive/): community variant comparison in detail
- [Simon Willison's Weblog](https://simonwillison.net/2026/Apr/16/qwen-beats-opus/): laptop inference experience
- [LushBinary: Hermes Agent + Qwen 3.6 setup guide](https://lushbinary.com/blog/hermes-agent-qwen-3-6-setup-guide/): integration walkthrough
- [HackerNoon: Qwen3.6-35B-A3B Uncensored](https://hackernoon.com/qwen36-35b-a3b-uncensored-a-35b-moe-model-with-262k-context): model overview and 262K context

## References

- [r/hermesagent: Qwen3.6-35B-A3B community variants guide](https://www.reddit.com/r/hermesagent/comments/1tmp2qy/qwen3635ba3b_community_variants_the_definitive/): accessed 2026-06-30
- [r/LocalLLaMA: K_P quants and MTP benchmarks](https://www.reddit.com/r/LocalLLaMA/comments/1snlo1x/qwen3635ba3b_uncensored_aggressive_is_out_with_k/): accessed 2026-06-30
- [HackerNoon: Qwen3.6-35B-A3B Uncensored](https://hackernoon.com/qwen36-35b-a3b-uncensored-a-35b-moe-model-with-262k-context): accessed 2026-06-30
- [Simon Willison: Qwen3.6 vs Claude Opus 4.7](https://simonwillison.net/2026/Apr/16/qwen-beats-opus/): accessed 2026-06-30
- [HN: Qwen 3.6 35B A3B coding benchmarks](https://news.ycombinator.com/item?id=47798382): accessed 2026-06-30
- [r/LocalLLM: tool calling test](https://www.reddit.com/r/LocalLLM/comments/1sqpsut/qwen_3635ba3b_reddit_asked_so_i_tested_if_the_35/): accessed 2026-06-30
- [LushBinary: Hermes Agent Qwen 3.6 setup](https://lushbinary.com/blog/hermes-agent-qwen-3-6-setup-guide/): accessed 2026-06-30
