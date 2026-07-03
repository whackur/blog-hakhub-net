---
title: "Mixture of Agents(MoA): 여러 LLM을 쌓아 GPT-4 Omni를 넘은 방법"
meta_title: ""
description: "여러 LLM을 계층으로 배치해 집합적 강점을 끌어내는 MoA 아키텍처. 벤치마크, 변형 구조, 품질 대 다양성 트레이드오프를 정리했습니다."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-07-03T17:45:00+09:00
image: ""
categories: ["AI"]
tags: ["moa", "llm", "multi-agent", "ensemble", "ai-architecture"]
author: "whackur"
translationKey: "mixture-of-agents-moa"
draft: false
---

모델 한 개를 더 크게 만드는 대신, 여러 모델을 계층으로 쌓아 서로의 출력을 다듬게 하는 방법이 있습니다. Together AI 연구진이 2024년 6월 발표한 논문 [arXiv:2406.04692](https://arxiv.org/abs/2406.04692)가 이 접근을 MoA(Mixture of Agents)라는 이름으로 정리했습니다. 오픈소스 모델만 조합한 MoA가 AlpacaEval 2.0에서 GPT-4 Omni를 7.6%p 앞섰습니다.

출발점이 된 관찰이 있습니다. 논문이 collaborativeness라고 부르는 현상인데, LLM은 다른 모델의 답변을 참고 자료로 받으면 더 나은 답을 내놓는 경향이 있습니다. 참고로 주어진 답변의 품질이 자기 혼자 낸 답보다 낮아도 그렇습니다. MoA는 이 성질을 아키텍처로 만든 것입니다.

## 계층적 구조

MoA는 각 층마다 복수의 LLM이 병렬로 실행됩니다. 각 에이전트는 이전 층의 출력 전체를 컨텍스트로 받아 자신의 답변을 생성하고, aggregator가 그 결과를 합쳐 다음 층의 입력으로 넘깁니다. 같은 패턴이 층을 따라 반복되고, 마지막 층의 aggregator가 최종 답변을 작성합니다.

| 구성 요소 | 역할 |
|---|---|
| Agent models | Llama 3, Mixtral, WizardLM 2, Qwen 1.5, DBRX 등 병렬 실행 |
| Aggregator | 각 층 출력을 하나로 합쳐 다음 층으로 전달 |
| Judge agent | 역할 분화 시 상위 k개 응답 선택 |
| Moderator | 합의 기반 early stopping 담당 |

구조상 비용과 지연이 함께 늘어납니다. 층 하나를 통과할 때마다 에이전트 수만큼 추론 호출이 추가되고, 각 층은 이전 층의 모든 출력이 나와야 시작할 수 있어 지연도 층수만큼 쌓입니다. 논문이 층수를 줄인 경량 구성인 MoA-Lite를 함께 제시한 이유이기도 합니다.

Together Computer의 참조 구현은 [togethercomputer/moa](https://github.com/togethercomputer/moa)(Apache 2.0)에 공개되어 있습니다. 기본 `moa.py`는 50줄이고, 3층 이상 구성은 `advanced-moa.py`, 대화형 CLI는 `bot.py`입니다.

## 벤치마크

논문이 제시한 주요 결과는 두 벤치마크입니다.

**AlpacaEval 2.0**

| 모델 | 점수 |
|---|---|
| MoA (오픈소스 조합) | 65.1% |
| GPT-4 Omni | 57.5% |

**FLASK 다차원 평가**

FLASK는 정확성, 사실성, 통찰, 완결성, 메타인지 등을 차원별로 평가합니다. MoA는 Qwen1.5-110B-Chat 대비 전 차원에서 앞섰고, GPT-4 Omni 대비로는 정확성, 사실성, 통찰, 완결성, 메타인지에서 우위를 보였습니다. 다만 논문 기준 벤치마크이며 모든 실제 환경을 대표하지는 않습니다.

## 변형 구조

원 논문 이후 여러 연구에서 MoA를 수정한 구조가 나왔습니다.

| 변형 | 핵심 아이디어 |
|---|---|
| SMoA (Sparse MoA) | 동적 프루닝으로 각 층에서 에이전트 부분집합만 활성화 (Li et al., 2024) |
| RMoA (Residual MoA) | residual connection과 임베딩 기반 다양성 선택 (Xie et al., 2025) |
| DMoE (Dynamic MoE) | 동적 컨볼루션 커널 + gating + diversity triplet loss (Kong et al., 2025) |
| Distributed MoA | gossip 프로토콜 기반 엣지 기기 협업 추론 (Mitra et al., 2024) |

## 품질 대 다양성 트레이드오프

후속 연구에서 반직관적인 결론이 나왔습니다. 단일 고품질 모델의 출력만 여러 번 샘플링해 합치는 Self-MoA가, 이질적인 모델을 섞은 MoA보다 성능이 좋은 경우가 많다는 것입니다. Self-MoA를 제안한 연구팀은 성능을 `t = αq + βd + γ`(q는 응답 품질, d는 다양성)로 모델링했는데, 실제 설정에서 α가 β를 크게 앞섰습니다. 다양한 모델을 섞어서 얻는 이득보다, 참여하는 응답의 품질이 성능을 훨씬 크게 좌우한다는 뜻입니다.

이질적 MoA가 Self-MoA를 앞서는 것은 개별 에이전트의 강점이 작업의 이질성과 맞아떨어질 때입니다. 모델을 무작정 섞기보다 작업에 맞는 조합을 고르는 것이 중요합니다.

## Hermes Agent가 제품화한 MoA

MoA는 연구 패턴에 머물지 않고 실제 제품에도 들어갔습니다. Nous Research의 오픈소스 에이전트 Hermes Agent는 MoA를 별도 파이프라인이 아니라 `moa`라는 가상 모델 제공자로 만들어, 기존 에이전트 루프의 tool 호출과 메모리, prompt cache를 그대로 유지한 채 여러 모델의 관점을 끼워 넣습니다.

Hermes Agent 자체는 메모리·스킬·세션 회상을 갖춘 자기개선형 에이전트이기도 합니다. reference/aggregator 구성, `/moa` 명령, 설정 방법, HermesBench 수치, 커뮤니티 반응까지 제품 관점의 자세한 내용은 [Hermes Agent v0.18: 스스로 배우는 에이전트와 MoA가 만났을 때](/blog/hermes-agent-self-improving-agent-moa/)에서 다룹니다.

## 함께 보면 좋을 자료

- [arXiv:2406.04692](https://arxiv.org/abs/2406.04692): MoA 원 논문 (Together AI et al.)
- [togethercomputer/moa](https://github.com/togethercomputer/moa): 참조 구현 (Apache 2.0)
- [Hermes Agent v0.18: 스스로 배우는 에이전트와 MoA가 만났을 때](/blog/hermes-agent-self-improving-agent-moa/): Hermes Agent의 MoA 제품 통합 상세
- [Emergent Mind: MoA](https://www.emergentmind.com/topics/mixture-of-agents): 관련 논문 및 커뮤니티 동향

## 참고 자료

- [arXiv:2406.04692: Mixture-of-Agents Enhances Large Language Model Capabilities](https://arxiv.org/abs/2406.04692): Together AI et al., 2024
- [togethercomputer/moa](https://github.com/togethercomputer/moa): GitHub, Apache 2.0, 조회일 2026-06-30
- [Hermes Agent MoA 공식 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/): Nous Research, 조회일 2026-06-30
