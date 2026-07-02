---
title: "Mixture of Agents(MoA): 여러 LLM을 쌓아 GPT-4 Omni를 넘은 방법"
meta_title: ""
description: "여러 LLM을 계층으로 배치해 집합적 강점을 끌어내는 MoA 아키텍처. 벤치마크, 변형 구조, Hermes Agent 통합까지 정리했습니다."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
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

## Hermes Agent MoA 2.0

Nous Research의 Hermes Agent가 2026년 6월 26일 MoA 2.0을 문서화했습니다([공식 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/)). `moa` 가상 모델 제공자로 노출되며, 각 preset이 선택 가능한 모델로 표시됩니다. 기본 preset 구성은 다음과 같습니다.

| 역할 | 모델 |
|---|---|
| Reference 1 | GPT-5.5 (openai-codex) |
| Reference 2 | DeepSeek-V4-Pro (openrouter) |
| Aggregator | Claude Opus 4.8 (openrouter) |

동작 순서는 이렇습니다. reference 모델들이 먼저 tool schema 없이 분석을 실행합니다. 비용을 줄이기 위해 시스템 프롬프트와 tool transcript를 제거한 상태로 돌립니다. 그 출력이 aggregator의 private 컨텍스트로 들어가고, aggregator가 정상 Hermes tool schema와 함께 최종 응답을 작성합니다. 이후의 tool 실행과 다음 반복도 같은 방식으로 이어집니다.

Hermes Agent 자체 벤치마크인 HermesBench 기준으로(타사 독립 벤치마크가 아닙니다) MoA 구성이 0.8202를 기록해, Claude Opus 4.8 단독(0.7607)과 GPT-5.5 단독(0.7412)을 앞섰습니다. SWE-bench Pro에서도 Hermes MoA preset이 Claude Opus 4.8(69.2%)과 GPT-5.5(58.6%)를 앞섰다고 밝혔지만, MoA 구성의 구체적인 점수는 공개하지 않았습니다. 두 결과 모두 Nous Research 내부 측정값입니다.

설계 선택 몇 가지가 눈에 띕니다. reference 출력을 user turn 끝에 추가해 stable prefix 캐시 무효화를 피합니다. reference 모델 인증이 실패해도 실행을 중단하지 않고 실패 메시지를 컨텍스트에 포함한 채 계속 진행합니다. aggregator가 다른 MoA preset을 참조하는 재귀 MoA는 허용하지 않습니다.

```yaml
# config.yaml 예시
moa:
  default_preset: default
  presets:
    default:
      reference_models:
        - provider: openai-codex
          model: gpt-5.5
        - provider: openrouter
          model: deepseek/deepseek-v4-pro
      aggregator:
        provider: openrouter
        model: anthropic/claude-opus-4.8
      reference_temperature: 0.6
      aggregator_temperature: 0.4
      max_tokens: 4096
      enabled: true
```

사용법은 `/moa` 명령으로 기본 preset으로 전환하고, `hermes moa configure [name]`으로 직접 만들 수 있습니다. `hermes moa list`로 목록을 확인합니다.

고려할 점도 있습니다. 반복당 N개의 reference call과 1개의 aggregator call이 추가되므로 토큰 비용이 reference 모델 수에 비례해 늘어납니다. 2026년 6월에 문서화된 신규 기능이라 실제 사용 패턴에 따라 동작이 계속 바뀔 수 있습니다.

## 함께 보면 좋을 자료

- [arXiv:2406.04692](https://arxiv.org/abs/2406.04692): MoA 원 논문 (Together AI et al.)
- [togethercomputer/moa](https://github.com/togethercomputer/moa): 참조 구현 (Apache 2.0)
- [Hermes Agent MoA 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/): Hermes Agent 통합 상세
- [Emergent Mind: MoA](https://www.emergentmind.com/topics/mixture-of-agents): 관련 논문 및 커뮤니티 동향

## 참고 자료

- [arXiv:2406.04692: Mixture-of-Agents Enhances Large Language Model Capabilities](https://arxiv.org/abs/2406.04692): Together AI et al., 2024
- [togethercomputer/moa](https://github.com/togethercomputer/moa): GitHub, Apache 2.0, 조회일 2026-06-30
- [Hermes Agent MoA 공식 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/): Nous Research, 조회일 2026-06-30
- [Tony Reviews Things: MoA 2.0 리뷰](https://www.tonyreviewsthings.com/hermes-agent-mixture-of-agents-20/): 커뮤니티 사용 후기, 조회일 2026-06-30
- [Crypto Briefing: Hermes MoA 벤치마크](https://cryptobriefing.com/hermes-agent-moa-beats-claude-opus-gpt-benchmarks/): 조회일 2026-06-30
