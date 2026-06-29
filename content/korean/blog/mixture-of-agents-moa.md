---
title: "Mixture of Agents(MoA): 여러 LLM을 쌓아 GPT-4 Omni를 넘은 방법"
meta_title: ""
description: "여러 LLM을 계층으로 배치해 집합적 강점을 끌어내는 MoA 아키텍처. 벤치마크, 변형 구조, Hermes Agent 통합까지 정리했습니다."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-06-30T02:00:00+09:00
image: ""
categories: ["AI"]
tags: ["moa", "llm", "multi-agent", "ensemble", "ai-architecture"]
author: "hakhub"
translationKey: "mixture-of-agents-moa"
draft: false
---

모델 한 개를 더 크게 만드는 대신, 여러 모델을 계층으로 쌓아 서로 출력을 다듬게 하는 방법이 있다. Together AI 연구진이 2024년 6월 발표한 논문 [arXiv:2406.04692](https://arxiv.org/abs/2406.04692)이 그 접근을 공개했다. 오픈소스 모델만 조합한 MoA(Mixture of Agents)가 AlpacaEval 2.0에서 GPT-4 Omni를 7.6%p 앞섰다.

## 계층적 구조

MoA는 각 층마다 복수의 LLM이 병렬로 실행된다. 각 에이전트는 이전 층의 출력 전체를 컨텍스트로 받아 자신의 답변을 생성하고, aggregator가 그 결과를 합쳐 다음 층의 입력으로 넘긴다. 같은 패턴을 여러 층에서 반복한다.

| 구성 요소 | 역할 |
|---|---|
| Agent models | Llama 3, Mixtral, WizardLM 2, Qwen 1.5, DBRX 등 병렬 실행 |
| Aggregator | 각 층 출력을 하나로 합쳐 다음 층으로 전달 |
| Judge agent | 역할 분화 시 상위 k개 응답 선택 |
| Moderator | 합의 기반 early stopping 담당 |

Together Computer의 참조 구현은 [togethercomputer/moa](https://github.com/togethercomputer/moa)(Apache 2.0)에 공개되어 있다. 기본 `moa.py`는 50줄, 3층 이상 구성은 `advanced-moa.py`, 대화형 CLI는 `bot.py`다.

## 벤치마크

논문이 제시한 주요 결과는 두 벤치마크다.

**AlpacaEval 2.0**

| 모델 | 점수 |
|---|---|
| MoA (오픈소스 조합) | 65.1% |
| GPT-4 Omni | 57.5% |

**FLASK 다차원 평가**

FLASK는 정확성, 사실성, 통찰, 완결성, 메타인지 등을 차원별로 평가한다. MoA는 Qwen1.5-110B-Chat 대비 전 차원에서 앞섰고, GPT-4 Omni 대비로는 정확성, 사실성, 통찰, 완결성, 메타인지에서 우위를 보였다. 논문 기준 벤치마크이며 모든 실제 환경을 대표하지 않는다.

## 변형 구조

원 논문 이후 여러 연구에서 MoA를 수정한 구조가 나왔다.

| 변형 | 핵심 아이디어 |
|---|---|
| SMoA (Sparse MoA) | 동적 프루닝으로 각 층에서 에이전트 부분집합만 활성화 (Li et al., 2024) |
| RMoA (Residual MoA) | residual connection과 임베딩 기반 다양성 선택 (Xie et al., 2025) |
| DMoE (Dynamic MoE) | 동적 컨볼루션 커널 + gating + diversity triplet loss (Kong et al., 2025) |
| Distributed MoA | gossip 프로토콜 기반 엣지 기기 협업 추론 (Mitra et al., 2024) |

## 품질 대 다양성 트레이드오프

MoA 연구에서 반직관적인 결론이 나온다. 단일 고품질 모델의 출력만 여러 번 합친 Self-MoA가, 이질적 모델을 섞은 MoA보다 성능이 좋은 경우가 많다. 연구팀은 성능을 `t = αq + βd + γ`(q=품질, d=다양성)로 모델링했는데, 실제 설정에서 α >> β로 나타났다. 품질이 다양성보다 훨씬 영향이 크다는 의미다.

개별 에이전트의 특성이 작업 이질성과 맞아떨어질 때만 이질적 MoA가 Self-MoA를 앞선다. 모델을 무작정 섞기보다 작업에 맞는 조합이 중요하다.

## Hermes Agent MoA 2.0

Nous Research의 Hermes Agent가 2026년 6월 26일 MoA 2.0을 문서화했다([공식 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/)). `moa` 가상 모델 제공자로 노출되며, 각 preset이 선택 가능한 모델로 표시된다. 기본 preset 구성:

| 역할 | 모델 |
|---|---|
| Reference 1 | GPT-5.5 (openai-codex) |
| Reference 2 | DeepSeek-V4-Pro (openrouter) |
| Aggregator | Claude Opus 4.8 (openrouter) |

동작 순서는 다음과 같다. reference 모델들이 먼저 tool schema 없이 분석을 실행한다. 비용을 줄이려고 시스템 프롬프트와 tool transcript를 제거한 상태로 돌린다. 그 출력이 aggregator의 private 컨텍스트로 들어가고, aggregator가 정상 Hermes tool schema와 함께 최종 응답을 작성한다. 이후 tool 실행과 다음 반복이 같은 방식으로 이어진다.

Hermes Agent 자체 벤치마크인 HermesBench 기준으로(타사 독립 벤치마크 아님), MoA 구성이 Claude Opus 4.8 단독(0.7607)과 GPT-5.5 단독(0.7412)보다 높은 0.8202를 기록했다. SWE-bench Pro에서도 Hermes MoA preset이 Claude Opus 4.8(69.2%)과 GPT-5.5(58.6%)를 앞섰다고 밝혔다. 두 수치 모두 Nous Research 내부 측정값이다.

설계 선택 몇 가지가 있다. reference 출력을 user turn 끝에 추가해 stable prefix 캐시 무효화를 피한다. reference 모델 인증 실패 시 중단 없이 계속 진행하고 실패 메시지를 컨텍스트에 포함한다. aggregator가 다른 MoA preset을 참조하는 재귀 MoA는 허용하지 않는다.

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

사용 방법은 `/moa` 명령으로 기본 preset으로 전환하고, `hermes moa configure [name]`으로 직접 만들 수 있다. `hermes moa list`로 목록을 확인한다.

고려할 점도 있다. 반복당 N개 reference call과 1개 aggregator call이 추가되므로 토큰 비용이 상당히 늘어난다. 2026년 6월 문서화된 신규 기능이라 실제 사용 패턴에 따라 계속 바뀔 수 있다.

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
