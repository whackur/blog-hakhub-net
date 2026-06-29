---
title: "Harness-1: 상태 외부화 하네스로 학습한 검색 에이전트"
meta_title: ""
description: "20B 검색 서브에이전트 Harness-1이 하네스에 상태를 외부화해 RL을 안정시키고 8개 벤치마크 평균 curated recall 0.730을 달성한 방법을 살펴봅니다."
date: 2026-06-30T07:00:00+09:00
lastmod: 2026-06-30T07:00:00+09:00
image: ""
categories: ["AI"]
tags: ["search-agent", "retrieval", "rl", "rag", "agent-harness"]
author: "hakhub"
translationKey: "harness-1-state-externalizing-search-agents"
draft: true
---

에이전트가 긴 검색 태스크를 처리할 때 흔히 생기는 문제가 있다. 의미적 판단과 기계적 상태 관리를 모델 정책이 동시에 떠맡는 구조다. 이미 본 문서 목록, 후보 풀, 검증 여부, 남은 컨텍스트 예산까지 transcript 안에 쌓이면 RL로 검색 행동을 개선하기 점점 어려워진다. 실패했을 때 "검색을 잘못한 건지, 봤지만 잊은 건지, 검증을 빠뜨린 건지" 구분이 안 된다.

[Harness-1](https://arxiv.org/abs/2606.02373v1)은 이 문제를 **상태 외부화(state-externalizing harness)**로 풀었다. 2026년 6월 arXiv에 공개된 이 논문은 20B 검색 서브에이전트가 하네스에 반복적 bookkeeping을 맡기면 RL이 더 안정적으로 검색 행동을 학습할 수 있음을 보여준다. GitHub과 Hugging Face에 코드와 checkpoint가 공개되어 있으며 Apache 2.0 라이선스다.

## 설계 원칙

핵심은 역할 분리다. **모델은 의미적 판단**을 맡고, **하네스는 작업대를 유지**한다.

모델/정책이 결정하는 것:
- 무엇을 검색할지
- 어떤 후보를 보존하거나 제거할지
- 어떤 claim을 검증할지
- 언제 검색을 마칠지

하네스/환경이 관리하는 것:
- `P_t`: compression/dedup 이후 후보 문서 풀
- `C_t, I_t`: curated evidence set과 중요도 태그 (very_high/high/fair/low)
- `D_t`: 검색 중 본 문서의 full-text store
- `G_t`: 엔티티/날짜/문서 간 evidence graph
- `V_t`: claim별 검증 기록
- `H_t`: 검색 히스토리와 결과 요약
- `B_t`: context budget marker

검색 결과가 단순히 다음 prompt에 append되지 않는다. 하네스 상태 `(s_t, a_t) → (s_{t+1}, o_{t+1})`를 갱신하고, 모델은 압축된 상태 렌더링을 보며 다음 행동을 결정한다.

## 도구 인터페이스

정책은 한 턴에 하나의 structured action을 낸다. 주요 도구는 다음과 같다.

- `fan_out_search(queries)`: 최대 5개 query 병렬 hybrid search (RRF + rerank)
- `search_corpus(query)`: 단일 hybrid search
- `read_document(doc_id)`: 특정 문서 full-text 읽기
- `review_docs(doc_ids)`: working memory 안 문서를 새 검색 없이 재방문
- `curate(add, remove, importance)`: curated set 편집
- `verify(doc_ids, claim)`: claim에 대한 문서별 LLM entailment check
- `end_search(reasoning)`: episode 종료 및 curated set 반환

`review_docs`와 `verify`가 중요하다. 둘 다 새 검색 호출이 아니라 이미 수집된 상태를 조작하는 행동이다. 이런 행동들이 명시적으로 존재해야 RL이 "더 검색하기"와 "이미 본 것을 정리하기" 사이의 절충을 학습할 수 있다.

## 훈련

SFT 단계에서는 GPT-5.4 live agent를 teacher로 `openai/gpt-oss-20b` MoE를 fine-tuning했다. 필터링 후 899개 trajectory, LoRA rank 32, max sequence 32,768, 3 epochs. 목표는 지식 주입이 아니라 **stateful interface 조작법** 습득이다.

RL 단계에서는 on-policy CISPO를 사용했다. SEC training queries 단일 도메인, 128 queries/step, 8 rollouts/query, 총 약 82K rollouts. 보상은 curated set 품질, trajectory recall, final-answer evidence recall, tool diversity bonus 등을 결합했다. KL anchor는 비활성화했다.

논문은 하네스가 있어도 다음 세 가지 설계가 없으면 RL이 제대로 동작하지 않는다고 강조한다.

1. **Warm-started curation**: 첫 successful search 이후 top-8 results를 fair 중요도로 자동 seed. 빈 curated set에서 시작하는 hard query의 실패 보상을 줄인다.
2. **Compact derived-state rendering**: evidence graph, 중요도 태그, summary, budget marker, BM25 sentence compression으로 prompt 상태를 압축한다.
3. **Diversity-preserving incentives**: diversity reward 없으면 policy가 fan_out_search 반복으로 붕괴되고 curated recall이 정체된다.

## 평가 결과

8개 retrieval benchmark에서 평균 curated recall **0.730**을 기록했다. 벤치마크는 source-family (BrowseComp+, Web, Patents, SEC)와 held-out transfer (LongSealQA, Seal0QA, FRAMES, HotpotQA)로 나뉜다. 다음으로 강한 공개 검색 서브에이전트인 Tongyi DeepResearch 30B보다 **+11.4pt** 높다.

source-family 평균 gain은 +7.9pt인 반면 held-out transfer 평균은 +17.0pt다. 이 2.2배 격차를 논문은 "도메인별 패턴 암기가 아니라 명시적 검색 상태 위의 일반적 조작 학습"의 근거로 해석한다.

Ablation에서는 harness mechanism을 모두 비활성화했을 때 BrowseComp+ Recall이 0.584에서 0.513으로, FA Recall이 상대적으로 -12.2% 떨어졌다. importance tags 제거가 FA Recall -7.9%로 개별 구성요소 중 가장 크게 영향을 미쳤다.

비교군 중 Opus-4.6은 평균 curated recall에서 여전히 앞서며, BrowseComp+ final-answer recall 격차도 남아 있다.

## 한계

논문 자체가 명시한 한계다.

- evidence graph가 regex 기반 entity/date extractor라서 도메인별 품질 편차가 있다
- verify가 LLM entailment proxy이므로 기술적·모호한 claim에서 틀릴 수 있다
- sentence-BM25 compression은 discourse-level context가 필요한 경우 중요 정보를 제거할 수 있다
- 실험은 evidence-seeking retrieval 중심이며, open-ended report generation과 adversarial web 환경은 주 범위 밖이다
- benchmark 재현에는 별도 retrieval index와 credentials가 필요해 one-command reproducibility가 아니다

## 에이전트 설계에 주는 의미

Harness-1의 결과는 "더 큰 모델"보다 **모델이 조작하는 상태 인터페이스 설계**가 검색 에이전트 성능을 크게 좌우한다는 쪽에 증거를 준다.

장기 리서치 에이전트나 RAG 시스템을 설계할 때, transcript 중심보다 candidate pool, curated sources, claims to verify, verified claims, budget state를 명시 상태로 분리하는 방향을 고려할 가치가 있다. Harness-1은 retrieval subagent로 최종 답변 모델과 분리되어 있어, downstream answerer를 바꿔도 curated evidence set을 재사용하거나 감사할 수 있다는 점도 실용적이다.

## 함께 보면 좋을 자료

- [arXiv:2606.02373v1](https://arxiv.org/abs/2606.02373v1) — Harness-1 원 논문
- [pat-jj/harness-1 (GitHub)](https://github.com/pat-jj/harness-1) — 코드와 훈련 파이프라인
- [pat-jj/harness-1 (Hugging Face)](https://huggingface.co/pat-jj/harness-1) — 공개 checkpoint

## 참고 자료

- [Harness-1: Reinforcement Learning for Search Agents with State-Externalizing Harnesses](https://arxiv.org/abs/2606.02373v1) — arXiv, 2026-06-09, 조회일 2026-06-30
- [GitHub — pat-jj/harness-1](https://github.com/pat-jj/harness-1) — 조회일 2026-06-30
- [Hugging Face — pat-jj/harness-1](https://huggingface.co/pat-jj/harness-1) — 조회일 2026-06-30
- ["20B로 GPT-5.4 검색 성능 능가"...오픈소스 에이전트 '하네스-1' 공개](https://www.aitimes.com/news/articleView.html?idxno=211522) — AI타임스, 박찬, 2026-06-09, 조회일 2026-06-30
