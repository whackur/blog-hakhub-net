---
title: "LLM Observability 오픈소스 스택: LangSmith 대안 5종 비교"
meta_title: ""
description: "LangSmith를 대체할 수 있는 오픈소스 LLM observability 도구 Langfuse, Opik, Laminar/LMNR, Arize Phoenix, Helicone를 목적별로 비교합니다."
date: 2026-06-30T07:00:00+09:00
lastmod: 2026-06-30T07:00:00+09:00
image: ""
categories: ["AI"]
tags: ["llm-observability", "evals", "tracing", "langfuse", "opik"]
author: "hakhub"
translationKey: "llm-observability-langsmith-alternatives"
draft: false
---

LLM 앱이나 AI 에이전트를 운영하다 보면 "어떤 프롬프트가 실패했고, 어떤 도구 호출이 막혔고, 왜 에이전트가 루프에 빠졌는가"를 추적해야 하는 시점이 온다. LangSmith가 이 공간을 선점했지만, 자체 호스팅과 오픈소스 선호도에 따라 여러 대안이 등장했다.

여기서 비교하는 기준은 세 가지다. LLM call·tool call·RAG·agent step을 추적·디버깅할 수 있는가, self-host/오픈소스 환경에서 핵심 기능이 잘 열려 있는가, 라이선스가 명확한가.

## Langfuse

- **GitHub**: [langfuse/langfuse](https://github.com/langfuse/langfuse) (약 28.7k stars)
- **라이선스**: core는 MIT 기반 오픈소스, Enterprise 기능은 별도

Langfuse는 LangSmith 대안 포지션이 가장 명확한 도구다. traces/observations/spans, sessions, user tracking, token·cost·latency 추적을 제공하고, agent graph 표현, prompt management/versioning, datasets, evals, annotation까지 갖췄다. OpenTelemetry 기반이라 LangChain, OpenAI SDK, LiteLLM, LlamaIndex 등 통합 범위가 넓다.

self-hosted Open Source 플랜에서는 core platform features와 API가 문서 기준 무료·무제한으로 제공된다. 다만 project-level RBAC, data retention 관리, SCIM, admin API, compliance audit log는 Enterprise 플랜에 있다. 순수 디버깅·개발 목적이라면 이 제약이 문제될 일이 많지 않다.

범용 LangSmith 대체와 LLM observability baseline으로는 1순위다.

## Opik (by Comet)

- **GitHub**: [comet-ml/opik](https://github.com/comet-ml/opik) (약 19.5k stars)
- **라이선스**: Apache-2.0

[Opik](https://www.comet.com/docs/opik/)은 LLM app, RAG, agent workflow 디버깅·평가·모니터링에 초점을 맞춘다. self-host 문서에 tracing, evaluation 등 핵심 기능 전체를 사용할 수 있다고 명시되어 있다. trace에서 실패 사례를 test case/dataset으로 만들고, eval/experiment로 개선을 확인하는 흐름이 자연스럽다.

Cloud와 오픈소스 버전의 차이는 주로 user management, billing, managed support다. [self-host 개요](https://www.comet.com/docs/opik/self-host/overview)를 보면 tracing/evaluation에 제약이 없다고 확인된다.

"순수 오픈소스 + 기능 제약 적음 + agent/RAG eval" 조건을 중요하게 보면 Langfuse와 거의 동급이며, 일부 조건에서는 먼저 시도해볼 만하다.

## Laminar / LMNR

- **GitHub**: [lmnr-ai/lmnr](https://github.com/lmnr-ai/lmnr) (약 3.0k stars)
- **라이선스**: Apache-2.0

[Laminar](https://docs.lmnr.ai/)는 AI agent observability에 특화된 신흥 도구다. OpenTelemetry-native tracing SDK, realtime trace view, full-text trace search, SQL access, dashboards를 제공한다. LLM reasoning, tool calls, sub-agent 흐름을 transcript/timeline 형태로 보여주는 방향성이 강하다.

Signals 기능이 특이하다. "agent is stuck in a loop" 같은 자연어 실패 패턴을 감지하고, Slack alert·cluster·eval dataset으로 이어가는 컨셉이다. Browser Use, Stagehand, LangChain, OpenAI, Anthropic, Gemini 등 agent-heavy stack을 강조한다.

Langfuse/Opik보다 커뮤니티 규모는 작지만, 복잡한 agent workflow 디버깅이 핵심이라면 반드시 PoC해볼 가치가 있다.

## Arize Phoenix

- **GitHub**: [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix) (약 10.1k stars)
- **라이선스**: Elastic License 2.0 (ELv2)

[Phoenix self-hosting](https://arize.com/docs/phoenix/self-hosting) 문서는 free to self-host, no license fees, no usage limits, no feature gates라고 명시한다. traces, evals, datasets, experiments, prompt management를 모두 지원하고, OpenTelemetry/OpenInference 기반이라 RAG 분석·eval 연구에 강하다.

다만 ELv2는 OSI 기준 strict open-source가 아니라 source-available 성격이다. hosted/managed service 제공에 제한이 있어, 제품화나 상용 SaaS로 확장할 계획이면 라이선스를 먼저 확인해야 한다. 내부 self-host 디버깅/평가 전용이라면 충분히 강력하다.

## Helicone

- **GitHub**: [Helicone/helicone](https://github.com/Helicone/helicone) (약 5.8k stars)
- **라이선스**: Apache-2.0

[Helicone](https://docs.helicone.ai/getting-started/self-host/overview)은 LLM Gateway / request logging / cost & latency tracking에 강하다. OpenAI-compatible gateway로 모델 라우팅, fallback, caching, 요청·응답 로그를 쉽게 남길 수 있다. API 호출 감사, 비용·지연시간·사용자별 사용량 추적이 목적이면 실용적이다.

복잡한 agent trace, eval, dataset, prompt experiment, failure replay 관점에서는 Langfuse/Opik/Laminar보다 약하다. "모든 LLM API 호출을 게이트웨이에서 로깅하고 싶다"면 좋지만, "에이전트가 왜 실패했는가"를 깊게 보려면 다른 도구가 필요하다.

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

- [Langfuse LangSmith 대안 비교](https://langfuse.com/faq/all/langsmith-alternative) — Langfuse 공식 비교
- [Opik self-host 개요](https://www.comet.com/docs/opik/self-host/overview) — Opik 자체 호스팅 문서
- [Laminar 문서](https://docs.lmnr.ai/) — agent observability 특화 기능

## 참고 자료

- [Langfuse self-hosted pricing](https://langfuse.com/pricing-self-host) — Langfuse, 조회일 2026-06-30
- [Opik documentation](https://www.comet.com/docs/opik/) — Comet ML, 조회일 2026-06-30
- [Laminar/LMNR GitHub](https://github.com/lmnr-ai/lmnr) — lmnr-ai, 조회일 2026-06-30
- [Arize Phoenix self-hosting](https://arize.com/docs/phoenix/self-hosting) — Arize, 조회일 2026-06-30
- [Helicone self-hosting](https://docs.helicone.ai/getting-started/self-host/overview) — Helicone, 조회일 2026-06-30
- [Phoenix license](https://github.com/Arize-ai/phoenix/blob/main/LICENSE) — GitHub, 조회일 2026-06-30
