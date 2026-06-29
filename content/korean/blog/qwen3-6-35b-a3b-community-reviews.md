---
title: "Qwen3.6-35B-A3B 커뮤니티 리뷰: uncensored 변종, MTP 가속, Hermes 호환"
meta_title: ""
description: "1.2M 다운로드의 uncensored 변종부터 12GB/16GB VRAM 실측치까지. Qwen3.6-35B-A3B를 실제로 써본 커뮤니티 후기와 권장 설정을 정리했습니다."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-06-30T02:00:00+09:00
image: ""
categories: ["AI"]
tags: ["qwen", "local-llm", "moe", "mtp", "uncensored", "llama-cpp"]
author: "hakhub"
translationKey: "qwen3-6-35b-a3b-community-reviews"
draft: false
---

Alibaba가 2026년 4월 출시한 Qwen3.6-35B-A3B는 총 파라미터 35B에 토큰당 활성 파라미터 약 3B인 MoE 모델이다. 기본 컨텍스트 262K, 공식 SWE-bench 점수 73.4%. 출시 두 달 만에 로컬 LLM 커뮤니티에서 가장 많이 테스트된 35B급 모델이 됐다.

이 글은 Reddit, HackerNews, 개인 블로그에서 공유된 커뮤니티 경험을 모은 것이다. 개인 사례가 많으므로 독립 재현이 필요하고, 환경(하드웨어, 드라이버, 설정)에 따라 결과가 달라진다.

## 기본 스펙

| 항목 | 값 |
|---|---|
| 아키텍처 | MoE (256 experts, 토큰당 8 routed + 1 shared) |
| 파라미터 | 35B total / ~3B active |
| 컨텍스트 | 262K (YaRN으로 1M까지 확장) |
| 멀티모달 | 텍스트, 이미지, 비디오 |
| 라이선스 | Apache 2.0 |

공식 벤치마크(Alibaba 발표 기준): SWE-bench 73.4%, GPQA 86.0, LiveCodeBench v6 80.7, MMLU-Pro 85.2, AIME 2026 92.7.

## uncensored 변종 비교

베이스 모델은 특정 주제에 대해 거절 응답이 많다. 커뮤니티에서는 refusal을 제거하거나 줄인 변종을 여럿 만들었다.

### HauhauCS Aggressive

[r/hermesagent 커뮤니티 변종 종합 가이드](https://www.reddit.com/r/hermesagent/comments/1tmp2qy/qwen3635ba3b_community_variants_the_definitive/)에 따르면 2026년 6월 기준 다운로드 122만 건, 좋아요 761개로 uncensored 변종 중 가장 많이 검증됐다. 제작자는 465회 테스트에서 refusal 0회, 베이스 모델과 동일한 품질을 주장했다. VRAM은 Q4_K_P 기준 약 22GB, IQ4_XS 기준 약 20GB다. 긴 agentic loop에서 topic drift가 간헐적으로 발생한다고 제작자 본인도 인정했다.

커뮤니티 평가를 한 마디로 요약하면, 질문한 것만 답하고 사용자가 이상한 질문을 해야만 이상한 답이 나온다는 평이 많다([r/hermesagent 가이드](https://www.reddit.com/r/hermesagent/comments/1tmp2qy/qwen3635ba3b_community_variants_the_definitive/) 참고).

### 다른 uncensored 변종

| 변종 | 기법 | 다운로드 | 비고 |
|---|---|---|---|
| Wasserstein (LuffyTheFox) | 임베딩 공간 Wasserstein distance 기반 | 455K | 다른 uncensoring 경로라 edge case 행동이 다를 수 있음 |
| heretic (llmfan46) | abliteration + decensor hybrid | 53K | KL divergence 0.0015, 거절 88% 감소 |
| huihui-ai Abliterated | 순수 abliteration | 19K | 제작자가 "개념 증명 수준"이라 평가 |

## Hermes Agent 사용 후기

### 장점

[r/hermesagent 가이드](https://www.reddit.com/r/hermesagent/comments/1tmp2qy/qwen3635ba3b_community_variants_the_definitive/)와 [r/LocalLLM tool calling 테스트](https://www.reddit.com/r/LocalLLM/comments/1sqpsut/qwen_3635ba3b_reddit_asked_so_i_tested_if_the_35/)에서 나온 긍정적 평가:

- **Tool calling**: Qwen3.5 대비 안정성 개선. MCPMark 점수 37.0 (개인 측정).
- **코딩**: 코드베이스 전체 분석, 수정 능력이 좋다는 평이 많음.
- **추론**: 추론 깊이가 길고 복잡한 문제에 강하다.
- **가성비**: 약 21GB VRAM에서 frontier급 성능을 기대할 수 있다는 평가.

Simon Willison은 자신의 블로그에서 ["노트북에서 Qwen3.6이 Claude Opus 4.7보다 나은 펠리컨을 그렸다"](https://simonwillison.net/2026/Apr/16/qwen-beats-opus/)고 적었다. [HN 코멘트](https://news.ycombinator.com/item?id=47798382)에는 "Power Ranking 태스크 98개 중 11개 해결"이라는 사례도 올라왔다. 두 사례 모두 개별 데이터 포인트다.

### 문제점

[HackerNoon 분석](https://hackernoon.com/qwen36-35b-a3b-uncensored-a-35b-moe-model-with-262k-context) 및 커뮤니티 스레드에서 공통으로 지적된 문제:

- **Tool call loop**: 같은 tool을 반복 호출하는 버그가 가장 흔하다.
- **Topic drift**: 긴 agentic loop에서 주제 이탈이 발생한다.
- **Temperature 민감도**: temp=1.0이 repetition과 looping을 줄이는 데 효과적이다. 기본값 0.6~0.8에서는 루프가 더 잦다.
- **코드 재현**: distilled 변종에서 코드 재현 시 실수 가능성이 있다.

### 권장 설정

```
temp=1.0, top_k=20, presence_penalty=1.5, top_p=0.95
--jinja --reasoning-budget 4096 --spec-type draft-mtp  # MTP 활성화 시
enable_thinking: false  # tool call parsing 방해 시
```

## MTP 가속 실측치

MTP(Multi-Token Prediction)는 여러 토큰을 한 번에 예측해 생성 속도를 높이는 기법이다. llama.cpp에서 `--spec-type draft-mtp`로 활성화한다. VRAM 용량별 결과가 크게 다르다.

### 12GB VRAM (RTX 4070 Super)

[r/LocalLLaMA K_P quants 스레드](https://www.reddit.com/r/LocalLLaMA/comments/1snlo1x/qwen3635ba3b_uncensored_aggressive_is_out_with_k/)에서 공유된 실측치. 설정: `-fitt 1536`, `--spec-draft-n-max 2`, `-ctk/-ctv q8_0`.

- 결과: 70~82 tok/s, 128K 컨텍스트 기준
- acceptance rate: 0.69~0.95 (작업마다 편차가 크다)
- 12GB VRAM에서 35B급 모델을 128K 컨텍스트로 실행할 수 있다.

### 16GB VRAM (RTX 5080)

| 설정 | 속도 |
|---|---|
| Q4_K_XL + MTP | 74 tok/s (acceptance ~79.5%) |
| Q4_K_XL, MTP 없음, 짧은 컨텍스트 | 97 tok/s |
| Q4_K_XL, MTP 없음, 128K 컨텍스트 | 56 tok/s |

128K 컨텍스트에서 prompt processing은 약 1,584 tok/s (처리 시간 약 81초). MTP가 효과를 내려면 모델 전체가 VRAM에 올라가야 한다. MTP compute buffer 때문에 VRAM 여유가 줄어들면, MoE expert layer가 CPU로 밀리고 그 병목 때문에 MTP 없을 때보다 느려질 수 있다.

## 주요 변종 요약

| 변종 | 타입 | 다운로드 | VRAM | MTP | 비고 |
|---|---|---|---|---|---|
| Qwopus v1 | Reasoning Distilled | 299K | ~22GB | 미출시 | temp=1.0 권장 |
| lordx64 Opus 4.7 | Reasoning Distilled | 158K | ~22GB | APEX 경유 | 가장 깔끔한 reasoning trace |
| hesamation Opus 4.6 | Reasoning Distilled | 206K | ~22GB | APEX 경유 | MMLU-Pro 75.71% (70문항) |
| HauhauCS Aggressive | Uncensored | 1.22M | ~22GB | 미출시 | 다운로드 최다, 가장 많이 검증 |
| heretic | Abliterated | 54K | ~22GB | 내장 | KL divergence 0.0015 |
| unsloth MTP | Vanilla+MTP | 548K | ~23GB | 내장 | MTP 참조 구현 |
| mudler APEX MTP | APEX+MTP | 33K | ~18GB | 내장 | 품질/용량 비율 우수 |

## 한계와 미해결 항목

- 커뮤니티 데이터이므로 독립 재현이 필요하다.
- llama.cpp에서 MTP와 Vision(`--mmproj`)을 병렬 사용하지 못한다.
- Qwopus + MTP 조합, HauhauCS Balanced/Moderate 변종은 요청이 많지만 아직 미출시다.
- 24GB 이상 GPU에서 MTP 성능 데이터는 아직 부족하다.

## 함께 보면 좋을 자료

- [r/hermesagent 커뮤니티 변종 가이드](https://www.reddit.com/r/hermesagent/comments/1tmp2qy/qwen3635ba3b_community_variants_the_definitive/): 변종 비교 상세 정리
- [Simon Willison's Weblog](https://simonwillison.net/2026/Apr/16/qwen-beats-opus/): 노트북 실행 후기
- [LushBinary: Hermes Agent + Qwen 3.6 셋업 가이드](https://lushbinary.com/blog/hermes-agent-qwen-3-6-setup-guide/): 통합 실행 방법
- [HackerNoon: Qwen3.6-35B-A3B Uncensored 소개](https://hackernoon.com/qwen36-35b-a3b-uncensored-a-35b-moe-model-with-262k-context): 모델 개요 및 262K 컨텍스트

## 참고 자료

- [r/hermesagent: Qwen3.6-35B-A3B 커뮤니티 변종 종합 가이드](https://www.reddit.com/r/hermesagent/comments/1tmp2qy/qwen3635ba3b_community_variants_the_definitive/): 조회일 2026-06-30
- [r/LocalLLaMA: K_P quants 및 MTP 실측](https://www.reddit.com/r/LocalLLaMA/comments/1snlo1x/qwen3635ba3b_uncensored_aggressive_is_out_with_k/): 조회일 2026-06-30
- [HackerNoon: Qwen3.6-35B-A3B Uncensored](https://hackernoon.com/qwen36-35b-a3b-uncensored-a-35b-moe-model-with-262k-context): 조회일 2026-06-30
- [Simon Willison: Qwen3.6 vs Claude Opus 4.7](https://simonwillison.net/2026/Apr/16/qwen-beats-opus/): 조회일 2026-06-30
- [HN: Qwen 3.6 35B A3B coding benchmarks](https://news.ycombinator.com/item?id=47798382): 조회일 2026-06-30
- [r/LocalLLM: tool calling 테스트](https://www.reddit.com/r/LocalLLM/comments/1sqpsut/qwen_3635ba3b_reddit_asked_so_i_tested_if_the_35/): 조회일 2026-06-30
- [LushBinary: Hermes Agent Qwen 3.6 셋업](https://lushbinary.com/blog/hermes-agent-qwen-3-6-setup-guide/): 조회일 2026-06-30
