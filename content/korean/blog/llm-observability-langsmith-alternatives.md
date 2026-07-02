---
title: "LLM Observability 오픈소스 스택: LangSmith 대안 5종 비교"
meta_title: ""
description: "LangSmith를 대체할 수 있는 오픈소스 LLM observability 도구 Langfuse, Opik, Laminar/LMNR, Arize Phoenix, Helicone를 목적별로 비교합니다."
date: 2026-06-30T07:00:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
image: ""
categories: ["AI"]
tags: ["llm-observability", "evals", "tracing", "langfuse", "opik"]
author: "whackur"
translationKey: "llm-observability-langsmith-alternatives"
draft: false
---

LLM 앱이나 AI 에이전트를 운영하다 보면 "어떤 프롬프트가 실패했고, 어떤 도구 호출이 막혔고, 왜 에이전트가 루프에 빠졌는가"를 추적해야 하는 시점이 온다. LangSmith는 LangChain이 만든 상용 LLM 관측 플랫폼으로, trace 시각화, 프롬프트 버저닝, eval을 한 곳에서 제공한다. 사실상 기본 선택지로 자리 잡았지만, 사용량 기반 과금과 클라우드 중심 호스팅이 제약으로 작용해 자체 호스팅과 오픈소스를 선호하는 팀들이 대안을 찾기 시작했다. trace에는 사용자 입력과 내부 프롬프트가 그대로 담기기 때문에, 이 데이터가 외부 SaaS로 나가는 것 자체가 부담인 조직도 많다.

## LLM 관측성이란

LLM 관측성(LLM observability)은 AI 애플리케이션의 내부 동작을 추적하고 분석하는 실천이다. 일반 앱 로그와 근본적으로 다른 이유가 있다. HTTP 요청 로그는 요청-응답 쌍을 기록하는 단순한 키-값 레코드다. LLM 앱에서 사용자 요청 하나는 여러 LLM 호출, 도구 호출(검색·코드 실행·API), 메모리 조회, 서브에이전트 위임을 거치며 트리 구조로 펼쳐진다. "왜 이 답변이 나왔는가"를 재구성하려면 이 트리 전체를 볼 수 있어야 한다.

이 복잡성을 다루는 핵심 개념들:

- **Trace**: 사용자 요청 하나가 처리되는 전체 흐름. 여러 LLM 호출과 도구 호출이 하나의 trace 아래 묶인다.
- **Span / Observation**: trace 안의 단일 단계. LLM 호출 하나, 도구 호출 하나, RAG 검색 하나가 각각 span이다. 시작·종료 시각, 입력·출력, 토큰 수, 지연시간이 기록된다.
- **Session**: 대화 맥락을 공유하는 여러 turn의 묶음. 챗봇 대화라면 한 세션이 여러 trace를 포함한다.
- **Prompt version**: 어느 프롬프트 버전이 실제 운영에 사용됐는지 추적. 프롬프트가 바뀌면 성능도 달라지므로 버전별 결과를 비교할 수 있어야 한다.
- **Dataset / Eval**: 과거 trace에서 수집한 입력-기대출력 쌍. 새 프롬프트나 모델 버전이 기존 케이스를 올바르게 처리하는지 실험하는 기반이다.
- **Annotation**: 사람이 개별 trace나 span에 달아두는 품질 레이블. 자동 평가 기준을 검증하거나 RLHF 데이터를 수집할 때 쓴다.
- **Cost / Latency**: 호출당 토큰 비용, 모델별 응답 시간. 에이전트 루프가 길어질수록 비용이 급격히 늘기 때문에 어떤 단계에서 토큰이 집중되는지 파악해야 한다.

각 도구가 이 가운데 어느 부분을 얼마나 잘 지원하느냐에 따라 적합성이 갈린다.

여기서 비교하는 기준은 세 가지다. LLM call·tool call·RAG·agent step을 추적·디버깅할 수 있는가, self-host/오픈소스 환경에서 핵심 기능이 잘 열려 있는가, 라이선스가 명확한가.

## Langfuse

- **GitHub**: [langfuse/langfuse](https://github.com/langfuse/langfuse) (약 28.7k stars)
- **라이선스**: core는 MIT 기반 오픈소스, Enterprise 기능은 별도

Langfuse는 2023년 공개된 오픈소스 LLM 관측성 플랫폼으로, LangSmith가 제공하는 기능을 자체 호스팅 환경에서 대체하는 것을 목표로 만들어졌다. LangChain 생태계 밖에서도 독립적으로 쓸 수 있고, OpenTelemetry 기반이라 기존 계측 인프라와 통합이 자연스럽다.

LangSmith 대안 포지션이 가장 명확한 도구다. traces/observations/spans, sessions, user tracking, token·cost·latency 추적을 제공하고, agent graph 표현, prompt management/versioning, datasets, evals, annotation까지 갖췄다. LangChain, OpenAI SDK, LiteLLM, LlamaIndex 등 통합 범위가 넓다.

self-hosted Open Source 플랜에서는 core platform features와 API가 문서 기준 무료·무제한으로 제공된다. 다만 project-level RBAC, data retention 관리, SCIM, admin API, compliance audit log는 Enterprise 플랜에 있다. 순수 디버깅·개발 목적이라면 이 제약이 문제될 일이 많지 않다.

범용 LangSmith 대체와 LLM observability baseline으로는 1순위다.

## Opik (by Comet)

- **GitHub**: [comet-ml/opik](https://github.com/comet-ml/opik) (약 19.5k stars)
- **라이선스**: Apache-2.0

Opik은 ML 실험 추적 도구 Comet ML이 만든 LLM 특화 관측성 플랫폼이다. Comet은 ML 훈련 실험 관리 분야에서 오랜 경험이 있으며, Opik은 그 경험을 LLM 앱과 에이전트 영역으로 확장한 제품이다. Apache-2.0 라이선스라 상업적 활용에도 제약이 적다.

LLM app, RAG, agent workflow 디버깅·평가·모니터링에 초점을 맞춘다. self-host 문서에 tracing, evaluation 등 핵심 기능 전체를 사용할 수 있다고 명시되어 있다. trace에서 실패 사례를 test case/dataset으로 만들고, eval/experiment로 개선을 확인하는 흐름이 자연스럽다.

Cloud와 오픈소스 버전의 차이는 주로 user management, billing, managed support다. [self-host 개요](https://www.comet.com/docs/opik/self-host/overview)를 보면 tracing/evaluation에 제약이 없다고 확인된다.

"순수 오픈소스 + 기능 제약 적음 + agent/RAG eval" 조건을 중요하게 보면 Langfuse와 거의 동급이며, 일부 조건에서는 먼저 시도해볼 만하다.

## Laminar / LMNR

- **GitHub**: [lmnr-ai/lmnr](https://github.com/lmnr-ai/lmnr) (약 3.0k stars)
- **라이선스**: Apache-2.0

Laminar는 lmnr-ai 팀이 만든 에이전트 관측성 특화 도구다. 범용 LLM 관측성 플랫폼을 지향하는 Langfuse나 Opik과 달리, 복잡한 에이전트 워크플로 디버깅에 집중하는 방향성을 처음부터 선택했다. 에이전트가 어떤 순서로 도구를 호출했고 어디서 막혔는지를 timeline 형태로 추적하는 데 강점이 있다.

AI agent observability에 특화된 신흥 도구다. OpenTelemetry-native tracing SDK, realtime trace view, full-text trace search, SQL access, dashboards를 제공한다. LLM reasoning, tool calls, sub-agent 흐름을 transcript/timeline 형태로 보여주는 방향성이 강하다.

Signals 기능이 특이하다. "agent is stuck in a loop" 같은 자연어 실패 패턴을 감지하고, Slack alert·cluster·eval dataset으로 이어가는 컨셉이다. Browser Use, Stagehand, LangChain, OpenAI, Anthropic, Gemini 등 agent-heavy stack을 강조한다.

Langfuse/Opik보다 커뮤니티 규모는 작지만, 복잡한 agent workflow 디버깅이 핵심이라면 반드시 PoC해볼 가치가 있다.

## Arize Phoenix

- **GitHub**: [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix) (약 10.1k stars)
- **라이선스**: Elastic License 2.0 (ELv2)

Phoenix는 ML 모델 관측성 전문 회사 Arize AI의 오픈소스 프로젝트다. Arize는 프로덕션 ML 모델의 성능 저하와 드리프트를 감지하는 엔터프라이즈 플랫폼으로 알려져 있으며, Phoenix는 그 경험을 LLM 앱과 RAG 시스템 평가로 확장한 도구다. LLM 앱 계측 표준인 OpenInference도 Arize가 주도한다.

[Phoenix self-hosting](https://arize.com/docs/phoenix/self-hosting) 문서는 free to self-host, no license fees, no usage limits, no feature gates라고 명시한다. traces, evals, datasets, experiments, prompt management를 모두 지원하고, OpenTelemetry/OpenInference 기반이라 RAG 분석·eval 연구에 강하다.

다만 ELv2는 OSI 기준 strict open-source가 아니라 source-available 성격이다. hosted/managed service 제공에 제한이 있어, 제품화나 상용 SaaS로 확장할 계획이면 라이선스를 먼저 확인해야 한다. 내부 self-host 디버깅/평가 전용이라면 충분히 강력하다.

## Helicone

- **GitHub**: [Helicone/helicone](https://github.com/Helicone/helicone) (약 5.8k stars)
- **라이선스**: Apache-2.0

Helicone은 OpenAI API 호환 게이트웨이로 시작한 LLM 요청 관리 도구다. 에이전트 워크플로 디버깅보다 LLM API 트래픽 전체를 게이트웨이 수준에서 통제하는 것을 핵심으로 한다. 모든 LLM 호출이 Helicone을 통과하기 때문에 모델 라우팅, 캐싱, 속도 제한을 한 곳에서 관리할 수 있다.

LLM Gateway / request logging / cost & latency tracking에 강하다. OpenAI-compatible gateway로 모델 라우팅, fallback, caching, 요청·응답 로그를 쉽게 남길 수 있다. API 호출 감사, 비용·지연시간·사용자별 사용량 추적이 목적이면 실용적이다.

복잡한 agent trace, eval, dataset, prompt experiment, failure replay 관점에서는 Langfuse/Opik/Laminar보다 약하다. "모든 LLM API 호출을 게이트웨이에서 로깅하고 싶다"면 좋지만, "에이전트가 왜 실패했는가"를 깊게 보려면 다른 도구가 필요하다. 위 도구들의 대체재라기보다 함께 쓰는 보완재로 보는 편이 맞다.

## 목적별 추천

| 목적 | 추천 도구 |
|------|-----------|
| 범용 LangSmith 대체 | Langfuse |
| 순수 오픈소스 + 기능 제약 최소화 | Opik, Laminar/LMNR |
| Agent workflow 디버깅 특화 | Laminar/LMNR, Opik |
| RAG/eval 연구·OpenTelemetry 표준성 | Phoenix, Langfuse |
| LLM API Gateway 비용/latency 추적 | Helicone |

순서보다 중요한 건 목적이다. 단순 LLM 앱 디버깅이면 Langfuse로 시작하고, agent loop 실패 분석이 핵심이면 Laminar/LMNR을 병행 검토하는 방식이 현실적이다.

## 커뮤니티 반응

Langfuse는 커뮤니티에서 가장 많이 언급되는 LangSmith 대안이다. [공식 비교 페이지](https://langfuse.com/faq/all/langsmith-alternative)도 있고, Reddit과 HN에서 자체 호스팅 후기가 꾸준히 올라온다. 다만 Enterprise 기능이 별도라는 점에 대한 불만도 있다.

Opik은 빠르게 성장하는 중이다. trace → dataset → eval 흐름이 매끄럽다는 평이 많다. Laminar는 규모는 작지만 agent debugging에 집중하는 방향성 때문에 agent 스택 사용자들의 관심을 받고 있다.

## 함께 보면 좋을 자료

- [Langfuse LangSmith 대안 비교](https://langfuse.com/faq/all/langsmith-alternative): Langfuse 공식 비교
- [Opik self-host 개요](https://www.comet.com/docs/opik/self-host/overview): Opik 자체 호스팅 문서
- [Laminar 문서](https://docs.lmnr.ai/): agent observability 특화 기능

## 참고 자료

- [Langfuse self-hosted pricing](https://langfuse.com/pricing-self-host): Langfuse, 조회일 2026-06-30
- [Opik documentation](https://www.comet.com/docs/opik/): Comet ML, 조회일 2026-06-30
- [Laminar/LMNR GitHub](https://github.com/lmnr-ai/lmnr): lmnr-ai, 조회일 2026-06-30
- [Arize Phoenix self-hosting](https://arize.com/docs/phoenix/self-hosting): Arize, 조회일 2026-06-30
- [Helicone self-hosting](https://docs.helicone.ai/getting-started/self-host/overview): Helicone, 조회일 2026-06-30
- [Phoenix license](https://github.com/Arize-ai/phoenix/blob/main/LICENSE): GitHub, 조회일 2026-06-30
