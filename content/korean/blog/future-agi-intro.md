---
title: "Future AGI: AI 에이전트 평가·관찰·개선을 한곳에서"
meta_title: ""
description: "프로덕션에서 무너지는 AI 에이전트를 하나의 피드백 루프로 다잡는 오픈소스 플랫폼 Future AGI. 코드와 경쟁 도구 비교까지 짚었습니다."
date: 2026-06-29T10:00:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
image: ""
categories: ["AI"]
author: "whackur"
tags: ["ai-agent", "llm", "observability", "evals", "open-source"]
draft: false
translationKey: "future-agi-intro"
---

AI 에이전트를 만들어 본 사람은 이 장면이 익숙합니다. 데모는 잘 돕니다. 그런데 프로덕션에 올리면 환각이 터지고, 뭐가 왜 틀렸는지 추적이 안 됩니다. 그래서 평가 도구 하나, 관측 도구 하나, 가드레일 하나를 따로 붙이죠. 진짜 문제는 이것들이 서로 말을 안 한다는 겁니다. 고치는 루프가 닫히지 않습니다.

[Future AGI](https://github.com/future-agi/future-agi)는 그 루프를 닫으려는 오픈소스 플랫폼입니다. 시뮬레이션, 평가, 보호, 모니터링, 최적화를 한 판에 올리고 데이터가 그 사이를 돌게 만듭니다. Apache 2.0이고 직접 호스팅합니다. GitHub 스타는 1.2k를 넘었고요.

## 해결하는 문제

요즘 LLM 운영 스택은 대개 이렇게 흩어져 있습니다.

- 평가는 Braintrust
- 관측은 Langfuse나 Helicone
- 가드레일은 Guardrails AI
- 시뮬레이션은 직접 짠 스크립트

조각마다 도구가 다르니 데이터가 안 흐릅니다. 프로덕션 트레이스가 다음 버전 개선으로 돌아오질 않죠. 에이전트는 관측만 되고 나아지지는 않습니다. Future AGI는 이 흐름을 하나로 합칩니다. 트레이스 하나가 다음 개선의 입력이 되도록요.

루프가 닫힌다는 건 구체적으로 이런 흐름입니다. 프로덕션에서 실패한 트레이스를 잡아 eval 데이터셋에 넣고, 그 데이터셋으로 프롬프트 최적화를 돌리고, 개선된 프롬프트를 배포한 뒤 새 트레이스로 결과를 확인합니다. 도구가 나뉘어 있으면 이 사이클의 단계마다 수동 export/import가 끼어들고, 대개 거기서 루프가 끊깁니다.

## 6가지 기능

여섯 개의 기둥으로 이뤄집니다. 각각이 보통 따로 쓰던 도구 하나를 대신합니다.

| 기능 | 하는 일 |
|------|---------|
| Simulate | 페르소나·적대적 입력·엣지 케이스로 멀티턴 대화를 미리 돌려봅니다 (텍스트 + 음성: LiveKit, VAPI) |
| Evaluate | `evaluate()` 한 번에 50여 개 지표(근거성, 환각, 도구 사용 정확도, PII, 톤). LLM 판정 + 휴리스틱 + ML |
| Protect | 내장 스캐너 18종(PII·탈옥·인젝션) + 벤더 어댑터 15종(Lakera, Presidio, Llama Guard) |
| Monitor | OpenTelemetry 기반 트레이싱. 50여 개 프레임워크(LangChain, LlamaIndex, CrewAI)를 설정 없이 연동 |
| Agent Command Center | OpenAI 호환 게이트웨이. 100여 개 프로바이더, 시맨틱 캐싱. ~29k req/s, 가드레일 켜고 P99 21ms 이하 |
| Optimize | 프롬프트 최적화 알고리즘 6종(GEPA, PromptWizard, ProTeGi). 프로덕션 트레이스가 학습 데이터로 돌아옵니다 |

게이트웨이는 Go로 짰습니다. 성능 숫자를 벤치마크 하네스로 같이 공개하고요. "빠르다"는 말 대신 직접 돌려볼 코드를 둔 셈입니다.

## 60초로 시작

설치 없이 무료 티어로 시작:

```bash
pip install ai-evaluation
# app.futureagi.com 가입
```

전체 스택을 직접 띄우려면 (Docker):

```bash
git clone https://github.com/future-agi/future-agi.git
cd future-agi
./bin/install            # Windows는 .\bin\install.ps1
# http://localhost:3000
```

기존 에이전트에 트레이싱을 붙이는 것도 몇 줄이면 끝납니다.

```python
from fi_instrumentation import register
from traceai_openai import OpenAIInstrumentor

register(project_name="my-agent")
OpenAIInstrumentor().instrument()
# 기존 OpenAI 코드가 그대로 트레이싱됩니다.
```

## 경쟁 도구와 차이

이 바닥엔 이미 강자가 많습니다. LangSmith는 LangChain 생태계 트레이싱에 강하고, Arize는 ML 관측 출신이라 통계가 탄탄합니다. Braintrust는 프롬프트 실험 중심이고, Langfuse는 오픈소스 자체 호스팅의 대표 주자죠. Future AGI의 노림수는 좀 다릅니다. 단계마다 다른 벤더를 엮지 말고 한 판에서 끝내자는 쪽입니다. 가격도 좌석당이 아니라 정액(무료 플랜 + Pro 월 $50 고정)이고, 데이터가 네트워크 밖으로 안 나간다는 점을 내세웁니다.

성숙도 차이는 감안해야 합니다. GitHub 스타 기준 Langfuse가 약 28.7k, Opik이 약 19.5k인 데 비해 Future AGI는 1.2k 수준입니다. 커뮤니티 규모, 축적된 문서, 프로덕션 검증 사례에서 아직 격차가 있다는 뜻입니다.

솔직히 말하면, 통합이 강점인 만큼 한 영역만 깊게 필요한 팀은 전용 도구가 더 맞을 수도 있습니다. "전 단계를 한곳에서"가 끌리는 팀에 어울리는 선택입니다.

## 함께 보면 좋을 자료

- [Langfuse](https://langfuse.com): 오픈소스 관측의 대표 주자, 자체 호스팅
- [Arize Phoenix](https://phoenix.arize.com): ML 관측 기반의 평가·드리프트 분석
- [Braintrust](https://www.braintrust.dev): 프롬프트 실험·평가 워크플로
- [LangSmith](https://www.langchain.com/langsmith): LangChain 스택용 트레이싱

## 정리

LLM 앱을 프로토타입 너머로 끌고 가는 단계에서 도구 난립에 지쳤다면, 한 번 들여다볼 값어치가 있습니다. 단계별 1등은 아닐지 몰라도, 흩어진 걸 한 줄로 꿴다는 방향은 분명합니다.

## 참고 자료
- [future-agi/future-agi](https://github.com/future-agi/future-agi): GitHub 저장소 (Apache 2.0), 조회일 2026-06-29
- [Future AGI 공식 사이트·문서](https://futureagi.com): 가격·자체 호스팅 정책
- [traceAI](https://github.com/future-agi/traceAI) · [ai-evaluation](https://github.com/future-agi/ai-evaluation): 핵심 SDK
- [LLM 관측 도구 비교 (2026)](https://www.digitalapplied.com/blog/agent-observability-platforms-langsmith-langfuse-arize-2026): 경쟁 도구 포지셔닝 참고
