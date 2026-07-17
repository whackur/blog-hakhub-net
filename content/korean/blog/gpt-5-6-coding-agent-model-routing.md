---
title: "GPT-5.6 Sol·Terra·Luna 코딩 에이전트 모델 선택 가이드"
meta_title: ""
description: "GPT-5.6의 Sol·Terra·Luna 티어와 max/high/xhigh/ultra 설정을 구분하고, OpenAI 런치 스냅샷과 DeepSWE·Artificial Analysis 최신 수치로 Hermes Agent·Codex 같은 코딩 에이전트에 어떤 모델을 언제 써야 하는지 정리합니다."
date: 2026-07-13T09:30:00+09:00
lastmod: 2026-07-17T15:27:11+09:00
image: ""
categories: ["AI"]
tags: ["gpt-5-6", "coding-agent", "model-routing", "benchmark", "llm"]
author: "whackur"
translationKey: "gpt-5-6-coding-agent-model-routing"
draft: false
---

GPT-5.6 이야기를 하다 보면 "Luna Max가 Terra High보다 낫다더라" 식의 서열이 자주 돌아다닙니다. 이 문장은 애초에 성립하지 않는 비교입니다. Sol·Terra·Luna는 서로 다른 모델(능력 티어)이고, max·high·xhigh·ultra는 같은 모델 안에서 얼마나 오래 생각하고 얼마나 많은 에이전트를 병렬로 굴릴지 정하는 설정입니다. 티어와 설정을 한 줄로 섞어 서열화하면 애초에 비교 축이 다른 값을 나란히 놓는 셈입니다.

이 글은 [OpenAI 발표](https://openai.com/index/gpt-5-6/), [DeepSWE 공식 리더보드](https://deepswe.datacurve.ai/)(2026년 7월 16일 갱신, 7월 17일 조회), [Artificial Analysis](https://artificialanalysis.ai/) 모델 페이지(2026년 7월 13일 조회)를 근거로 세 모델의 차이를 정리하고, Hermes Agent나 Codex 같은 코딩 에이전트에서 어떤 작업에 어떤 티어를 쓰는 게 합리적인지 라우팅 기준을 제시합니다.

## 티어와 reasoning effort 설정을 구분해야 하는 이유

[OpenAI 발표](https://openai.com/index/gpt-5-6/)에 따르면 Sol은 플래그십, Terra는 일상 작업용 균형형(저비용), Luna는 가장 빠르고 저렴한 모델입니다. 셋 다 독립된 모델이며 각자 max/high/xhigh 같은 reasoning effort 설정을 가질 수 있습니다. `ultra`는 별도로, 기본값으로 네 개 에이전트를 병렬 조율하는 오케스트레이션 모드입니다. API에는 Programmatic Tool Calling과 Responses API의 멀티 에이전트 베타가 노출되어 있습니다. OpenAI는 `max`가 `xhigh`보다 더 긴 추론 시간을 쓴다고 설명합니다.

[OpenAI 도움말 센터](https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna)는 표준 ChatGPT 대화창에서는 Terra와 Luna를 직접 선택할 수 없고, 플랜에 따라 Work·Codex·API 쪽에서 쓸 수 있다고 안내합니다. API 개발자는 Sol·Terra·Luna 세 모델 모두에 접근할 수 있습니다. 1M 토큰당 API 가격은 Sol 입력 $5/출력 $30, Terra 입력 $2.50/출력 $15, Luna 입력 $1/출력 $6입니다. GPT-5.6은 명시적 캐시 브레이크포인트와 최소 30분 캐시 수명을 지원하며, 캐시 쓰기는 비캐시 입력의 1.25배로 과금되고 캐시 읽기는 90% 할인이 유지됩니다. 가격과 제공 범위는 시점에 따라 바뀔 수 있으니 실제 적용 전 공식 페이지를 다시 확인하는 게 안전합니다.

## OpenAI 런치 페이지 코딩 스냅샷

OpenAI 발표 페이지는 Artificial Analysis Coding Agent Index v1.1, SWE-Bench Pro, DeepSWE v1.1, Terminal-Bench 2.1 네 지표로 세 모델(모두 max 설정)을 나란히 보여줍니다.

| 모델 (설정) | Coding Agent Index | SWE-Bench Pro | DeepSWE v1.1 | Terminal-Bench 2.1 |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol (max) | 80 | 64.6% | 72.7% | 88.8% |
| GPT-5.6 Terra (max) | 77.4 | 63.4% | 69.6% | 87.4% |
| GPT-5.6 Luna (max) | 74.6 | 62.7% | 67.2% | 84.7% |

출처: [OpenAI, "GPT-5.6: Frontier intelligence that scales with your ambition"](https://openai.com/index/gpt-5-6/), 2026-07-09.

이 표는 런치 시점의 스냅샷이지 고정된 리더보드가 아닙니다. OpenAI는 본문에서 Sol이 80점으로 새로운 최고 기록을 세웠고, Terra는 Fable 5 바로 위, Luna는 이 비교에서 Opus 4.8을 앞섰다고 설명합니다.

## DeepSWE 현재 리더보드 스냅샷

[DeepSWE 공식 사이트](https://deepswe.datacurve.ai/)는 2026년 7월 16일 갱신 기준(2026-07-17 조회) 113개 태스크, 91개 저장소, 5개 언어, 15개 모델을 다룹니다. 모델 간 조건을 맞추기 위해 15개 모델 모두 고정된 `mini-swe-agent` 스캐폴드로 리더보드를 돌립니다. 원본 장기 과제, 프로그램/행동 기반 검증기, 홀드아웃 테스트, 별도 검증 환경을 씁니다. 즉 이건 모델이 아니라 벤치마크/리더보드입니다.

리더보드에 내장된 공식 설명에 따르면 `pass@1`은 채점된 롤아웃 시도 전체에 대한 시도 통과율이고, `pass@4`는 시도한 태스크 중 한 번이라도 통과한 태스크의 비율입니다. 컨텍스트 윈도우 초과와 에이전트 타임아웃은 실패로 채점되고, 프로바이더·검증기·네트워크 오류는 집계에서 제외됩니다. 표의 출력 토큰과 스텝 수는 채점된 시도 전체에 대한 **평균값**입니다. 중앙값도 아니고 누적 합계도 아닙니다. 비용도 시도당 평균 비용입니다.

| 모델 (설정) | Pass@1 | 평균 비용 | 평균 출력 토큰 | 평균 스텝 수 |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol [max] | 73% ± 3% | $8.39 | 60k | 61 |
| Claude Fable 5 [max] | 70% ± 4% | $21.63 | 119k | 88 |
| GPT-5.6 Terra [max] | 70% ± 3% | $4.95 | 72k | 76 |
| GPT-5.6 Luna [max] | 67% ± 4% | $3.03 | 73k | 102 |
| GPT-5.5 [xhigh] | 67% ± 6% | $7.23 | 46k | 82 |
| Claude Opus 4.8 [max] | 59% ± 2% | $13.22 | 135k | 120 |
| Claude Sonnet 5 [max] | 54% ± 4% | $26.40 | 214k | 268 |
| Grok 4.5 [high] | 54% ± 2% | $2.42 | 36k | 61 |
| Muse Spark 1.1 [xhigh] | 53% ± 3% | $2.36 | 74k | 96 |
| GPT-5.4 [xhigh] | 52% ± 2% | $5.65 | 71k | 70 |
| GLM-5.2 [max] | 44% ± 2% | $3.92 | 78k | 129 |
| Gemini 3.5 Flash [medium] | 37% ± 2% | $7.34 | 276k | 86 |
| Kimi K2.7 Code [unspecified] | 31% ± 1% | $2.82 | 59k | 149 |
| Claude Sonnet 4.6 [high] | 30% ± 4% | $5.52 | 76k | 134 |
| Gemini 3.1 Pro [high] | 12% ± 2% | $9.48 | 196k | 81 |

출처: [DeepSWE 공식 리더보드](https://deepswe.datacurve.ai/), 갱신일 2026-07-16, 조회일 2026-07-17. Best view 기준 전체 15개 모델입니다. 태스크·검증 설계는 [공식 GitHub](https://github.com/datacurve-ai/deep-swe)와 [v1.1 방법론 글](https://deepswe.datacurve.ai/blog/deepswe-v1-1)에 있습니다.

Sol이 15개 모델 중 절대 성공률 1위이면서, 같은 GPT-5.6 max 안에서 Terra나 Luna보다 평균 출력 토큰과 평균 스텝 수는 오히려 적습니다. 점수가 토큰을 많이 써서 나온 결과라는 설명은 이 표에서 성립하지 않는다는 뜻입니다. 더 직접적인 동작 방식과 부합하는 정황이지, 그 이유 자체를 이 표가 증명하지는 않습니다.

Terra는 Sol보다 3%p 낮은 대신 평균 비용은 약 41.0% 적습니다. 다만 그 대가로 평균 출력 토큰은 약 20.0% 많고 평균 스텝 수는 약 24.6% 많습니다. Terra가 모든 축에서 가장 효율적인 건 아니고, 점수 대비 비용이라는 축에서 좋은 절충안일 뿐입니다.

Luna는 Terra보다 3%p 낮고 평균 비용은 약 38.8% 적습니다. 그런데 평균 출력 토큰은 Terra와 거의 같습니다(73k 대 72k, 차이는 1.4%). 반면 평균 스텝 수는 34.2% 더 많습니다. Luna가 싼 이유는 토큰을 덜 쓰거나 루프를 덜 돌기 때문이 아니라, 모델 자체의 단가가 낮기 때문으로 읽는 편이 정확합니다.

같은 패턴은 GPT-5.6 계열 밖에서도 반복됩니다. Claude Fable 5는 Terra와 똑같이 반올림 70% pass@1을 기록하지만 비용은 4.37배(337.0% 더 많음), 출력 토큰은 65.3% 더 많고, 스텝 수는 15.8% 더 많습니다. 다만 두 모델의 신뢰구간은 겹치고, [DeepSWE v1.1 공식 글](https://deepswe.datacurve.ai/blog/deepswe-v1-1)은 Fable 5의 시도 2,260건 중 73건이 미국 정부 지시로 접근이 중단돼 완주하지 못했다고 밝히고 있어 이 비교를 과도하게 확대 해석하면 안 됩니다. GPT-5.5와 Luna도 반올림 67% pass@1로 같지만, GPT-5.5는 출력 토큰이 37.0% 적고 스텝도 19.6% 적은데 비용은 138.6% 더 비쌉니다. 토큰 수와 달러 비용이 어긋나는 건 모델별 가격 정책이 다르기 때문입니다. Grok 4.5와 Claude Sonnet 5는 나란히 54% pass@1을 기록하지만 Grok은 비용이 90.8% 적고, 출력 토큰은 83.2% 적고, 스텝은 77.2% 적습니다. 이 역시 effort 설정이 다르고 신뢰구간이 겹치므로 하나의 보편적 순위로 쓸 수는 없습니다. 다만 공통적으로 보여주는 건, 토큰이나 스텝을 더 쓴다고 성공률이 따라 올라가지는 않는다는 점입니다.

평균 출력 토큰과 평균 스텝 수는 서로 다른 것을 잽니다. 토큰은 생성한 분량을 어림하고, 스텝은 도구 호출·상호작용 루프가 몇 번 돌았는지를 어림합니다. Luna와 Terra처럼 토큰은 비슷한데 스텝이 크게 다르면 더 짧고 조각난 사이클을 여러 번 돈다고 해석할 수는 있지만, 이 자체가 품질이나 지연시간, 원인을 증명하지는 않습니다. [DeepSWE v1.1 공식 글](https://deepswe.datacurve.ai/blog/deepswe-v1-1)은 호스트 성능과 프로바이더 부하가 일정하지 않아 더 이상 wall-clock 시간을 보고하지 않는다고 밝힙니다. 스텝 수가 적다고 그 모델이 실제로 더 빨리 끝난다는 뜻은 아닙니다.

DeepSWE의 고정 하네스는 15개 모델의 행동을 하나의 스캐폴드 위에서 비교한 것입니다. Hermes Agent나 Codex, Claude Code처럼 각자 다른 오케스트레이션·툴·프롬프트·재시도·샌드박스를 쓰는 완제품의 순위를 직접 매긴 게 아닙니다.

## 응답 속도와 첫 응답까지 걸리는 시간

[Artificial Analysis](https://artificialanalysis.ai/) 모델 페이지(2026-07-13 조회, max 설정 기준)는 다음 값을 보고합니다.

| 모델 (설정) | Intelligence Index | 출력 속도 | 페이지 표기 TTFT/첫 응답 지연 | 전체 평가에 쓰인 출력 토큰 |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol [max] | 59 | 69.2 tok/s | 193.39초 | 70M |
| GPT-5.6 Terra [max] | 55 | 140.8 tok/s | 167.86초 | 96M |
| GPT-5.6 Luna [max] | 51 | 205.7 tok/s | 99.34초 | 130M |

출처: [artificialanalysis.ai/models/gpt-5-6-sol](https://artificialanalysis.ai/models/gpt-5-6-sol), [-terra](https://artificialanalysis.ai/models/gpt-5-6-terra), [-luna](https://artificialanalysis.ai/models/gpt-5-6-luna), 조회일 2026-07-13.

여기서 헷갈리기 쉬운 지점이 TTFT입니다. Artificial Analysis는 raw TTFT를 "요청부터 첫 응답 토큰까지"로 정의하는데, reasoning 모델에서는 그 첫 토큰이 reasoning 토큰일 수 있다고 명시합니다. 별도로 model thinking까지 포함한 time to first answer token 개념도 정의합니다. 페이지 FAQ는 위 긴 지연 수치에 "TTFT"라는 이름을 쓰면서 reasoning 시간을 반영한다고 설명합니다. 즉 표의 193초·168초·99초는 순수 네트워크 응답 시간이 아니라 모델이 답을 생성하기 시작할 때까지 reasoning에 쓴 시간까지 포함한 값입니다.

[Artificial Analysis 방법론 문서](https://artificialanalysis.ai/methodology/performance-benchmarking)는 이 측정치가 최근 구간의 P50이고, 주 측정 서버가 Google Cloud us-central1-a이며, 프롬프트 길이와 네트워크 위치가 TTFT에 영향을 준다고 밝힙니다. 다시 말해 TTFT는 순수한 모델 지능 속성이 아니라 서비스·네트워크 조건이 섞인 값입니다.

실용적으로 읽으면 이렇습니다. max 설정에서 Luna는 대기 시간이 가장 짧고 디코딩 속도도 가장 빠르지만, 첫 응답까지 약 99초는 인터랙티브한 채팅용으로는 여전히 느립니다. Sol은 셋 중 가장 오래 기다리고 디코딩도 가장 느린데, 같은 스냅샷에서 지능·DeepSWE 점수는 가장 높습니다. "시작한 뒤에는 빠르다"와 "첫 유효 답까지 빠르다"는 서로 다른 축입니다. 높은 디코딩 속도가 좋은 인터랙티브 지연을 뜻하지 않습니다.

## 벤치마크가 실제로 재는 것

- **DeepSWE**: 활발히 운영 중인 오픈소스 저장소에서 뽑은 113개의 원본 장기 소프트웨어 엔지니어링 태스크. 행동 기반/홀드아웃 검증, 고정된 `mini-swe-agent` 리더보드 스캐폴드를 씁니다. 자세한 정의는 [공식 GitHub](https://github.com/datacurve-ai/deep-swe)에 있습니다.
- **Terminal-Bench v2.1**: 소프트웨어 엔지니어링, 시스템 관리, 데이터 처리, 모델 학습, 보안 다섯 분야에 걸친 89개 큐레이션 태스크를 실제 터미널 환경에서 프로그램적으로 검증합니다. Artificial Analysis는 자체 평가에서 e2b의 Terminus 2를 사용해 3회 반복 pass@1을 측정한다고 밝힙니다. 공식 사이트는 [tbench.ai](https://www.tbench.ai/), 저장소는 [laude-institute/terminal-bench](https://github.com/laude-institute/terminal-bench)입니다.
- **Artificial Analysis Coding Agent Index**: 코딩 에이전트 성능을 종합한 독립 지표(현재 v1.1). 단일 저장소 태스크가 아니고 DeepSWE와 동일한 잣대도 아닙니다.
- **Artificial Analysis Intelligence Index v4.1**: 에이전틱 작업, 코딩, 과학, 추론, 지식, 롱컨텍스트 등 9개 평가를 합친 종합 지표. 위 표의 출력 토큰 수치는 이 종합 평가 전체에 쓰인 토큰이라 DeepSWE의 태스크당 토큰 수와 직접 비교할 수 없습니다.

이 벤치마크들의 공통점은 하나의 고정 하네스로 여러 모델을 나란히 돌린다는 점입니다. 고정 하네스 비교는 유용하지만, Hermes Agent·Codex처럼 각자 다른 프롬프트 엔지니어링, 도구 세트, 재시도 전략, 샌드박스 격리, 컨텍스트 관리로 만들어진 완제품 간의 실제 체감 성능과는 다른 질문입니다. 벤치마크 점수는 "이 모델이 이 하네스 위에서 얼마나 잘 하는가"를 답하고, 제품 선택은 "내 하네스 위에서 이 모델이 얼마나 잘 하는가"를 답해야 합니다. 두 질문은 상관관계는 있어도 같은 질문이 아닙니다.

## 코딩 에이전트 라우팅 프레임워크

Hermes Agent나 Codex를 운영할 때는 모델 티어 하나를 고정하기보다 작업의 위험도와 되돌리기 쉬운 정도에 따라 라우팅하는 편이 낫습니다.

1. **저위험 / 읽기 전용 / 트리아지**: 로그 조회, 코드 설명, 이슈 분류, 간단한 포맷팅. Luna를 낮은 reasoning effort로 우선 시도합니다. 실패 비용이 낮고 검증이 쉬운 영역입니다.
2. **범위가 명확한 코딩**: 단일 기능 구현, 정형화된 버그 수정, 테스트 보강. Terra high/max를 기본값으로 둡니다. DeepSWE 점수 차이가 Sol 대비 3%p 수준으로 크지 않은데 태스크당 비용은 약 41% 낮기 때문입니다. 다만 그 대가로 평균 출력 토큰과 스텝 수는 Sol보다 오히려 많으므로, Terra를 모든 축에서 가장 효율적인 선택으로 오해하면 안 됩니다. 이건 DeepSWE 태스크 기준이므로, 실제로는 팀 자신의 저장소·워크플로에서 검증해야 합니다.
3. **고위험 / 멀티파일 / 장시간 자율 작업**: 마이그레이션, 보안에 민감한 변경, 여러 파일에 걸친 실패, 사람 개입 없이 오래 도는 자율 실행. Sol max를 기본으로 쓰고, 병렬 오케스트레이션과 추가 비용이 정당화될 때만 `ultra`를 검토합니다.

**에스컬레이션 트리거**: 테스트 실패가 반복되거나, 모델이 스스로 불확실성을 표시하거나, 같은 문제에서 재시도 횟수가 임계치를 넘으면 한 단계 위 티어로 올립니다. 반대로 저위험 작업에서 Terra/Sol을 계속 쓰고 있다면 Luna로 내려서 비용을 줄일 여지가 있는지 확인합니다.

## 커뮤니티에서 관찰되는 사용 경험

위 벤치마크와 별개로, 실제 사용자들이 올린 후기도 참고할 만합니다. 다만 이런 글은 표본이 편향돼 있고 재현 가능성도 없는 개인 경험담이라는 점을 먼저 짚어 둡니다.

[한 사용자](https://www.reddit.com/r/codex/comments/1us7fwv/i_gave_gpt54_gpt55_gpt56_sol_terra_and_luna_the/)는 35단어짜리 코카콜라 제로 랜딩페이지 프롬프트를 GPT-5.4, GPT-5.5, GPT-5.6 Luna Max, Terra Ultra, Sol Ultra에 똑같이 넣고 결과물을 나란히 올렸습니다. 본인이 밝힌 토큰 사용량은 Luna 94,393, Terra 154,574, Sol 200,352이고, 이 수치는 작성자가 직접 보고한 값일 뿐 검증된 것은 아닙니다. 작성자는 개인적으로 Luna 결과물을 더 선호했다고 적었습니다. 혼자 돌려본 프런트엔드 쇼케이스이지 통제된 코딩 에이전트 벤치마크가 아니므로, 여기서 모델 순위나 일반적인 토큰 효율을 끌어내면 안 됩니다.

반대로 [다른 사용자](https://www.reddit.com/r/codex/comments/1ut3u5l/very_bad_first_experience_with_gpt_56_terra/)는 결제·환불 경로의 idempotency를 강화하려고 Terra를 high 설정으로 돌렸는데, 관련 없는 로컬 개발 데이터베이스의 users, sessions, wallet, invoices, transactions 테이블이 삭제됐다고 보고했습니다. 이 사용자는 Terra에 대한 신뢰가 떨어져 GPT-5.5로 돌아가는 것을 고민 중이라고 썼습니다. 재현이나 원인 규명이 없는 단 한 건의 미검증 사용자 보고이므로 Terra 자체가 일반적으로 위험하다는 결론으로 확장해서는 안 됩니다. 다만 자율 실행 에이전트에 샌드박스, 승인 절차, 백업, 테스트 게이트 같은 운영 안전장치가 왜 필요한지 보여주는 사례로는 참고할 만합니다.

[Hermes Agent 서브레딧의 한 스레드](https://www.reddit.com/r/hermesagent/comments/1us3uc0/gpt56_is_moving_to_permanent_tiers_sol_terra_and/)에서는 Terra를 기본값으로 쓰고, 어려운 작업엔 Sol을, 대량·백그라운드 작업엔 Luna를 쓰자는 라우팅 어림짐작이 오갑니다. 이건 커뮤니티 의견이며 댓글 반응은 엇갈립니다. 한 댓글은 Terra를 기본값으로 두는 데 반대하며 하위 티어가 저평가됐다고 주장했고, 다른 댓글은 Terra medium이 GPT-5.5 medium보다 못하게 느껴졌지만 high는 오히려 효율적으로 느껴졌다고 보고했습니다. 스레드에는 모델 계보에 관한 추측성 주장도 섞여 있는데, 근거가 없어 여기서는 다루지 않습니다.

이 세 건 모두 선택 편향이 있고 재현되지 않은 개인 후기입니다. OpenAI 발표, DeepSWE 리더보드, Artificial Analysis 측정치를 대체하지 않으며, 위 라우팅 프레임워크를 뒤집을 근거로도 쓸 수 없습니다.

## 측정 체크리스트

모델 선택을 검증할 때는 다음을 함께 봅니다. 어느 하나만으로는 판단이 왜곡됩니다.

- 성공률 (태스크 완료 여부)
- 해결된 태스크당 비용
- wall-clock 시간 (실제로 걸린 총 시간)
- 첫 유효 응답까지 걸린 시간 (reasoning 포함)
- 재시도·스텝 수
- 회귀율 (고친 곳에서 새 버그가 나는 빈도)
- 사람 리뷰에 드는 시간

`성공률 / 토큰 수`처럼 서로 다른 벤치마크·다른 태스크에 걸쳐 하나의 숫자로 뭉뚱그린 "효율" 지표는 쓰지 않는 게 낫습니다. 토큰 수는 태스크 난이도, 하네스, reasoning effort 설정에 따라 달라지므로 벤치마크가 다르면 같은 잣대가 아닙니다. DeepSWE 표에서 계산한 비용·토큰·스텝 차이(Terra는 Sol 대비 비용 41.0% 낮지만 토큰 20.0%·스텝 24.6% 많음, Luna는 Terra 대비 비용 38.8% 낮지만 토큰은 1.4%만 많고 스텝은 34.2% 많음)도 DeepSWE라는 하나의 벤치마크·하나의 하네스 안에서만 유효한 파생값입니다.

## 정리

Sol·Terra·Luna는 모델 자체가 다르고, max·high·xhigh·ultra는 그 모델을 얼마나 오래 생각시키고 어떻게 병렬화할지 정하는 설정입니다. 이 둘을 뒤섞어 만든 서열은 처음부터 성립하지 않습니다. 어려운 장기 과제에서 절대 성공률이 우선이면 Sol max에서 시작하고, 병렬 오케스트레이션이 필요할 때만 ultra를 씁니다. Sol의 1위는 토큰이나 스텝을 더 써서 얻은 게 아니라 DeepSWE 표에서 오히려 그 반대로 나타난다는 점이 이번 갱신에서 다시 확인됐습니다. 일상적인 코딩 에이전트 실행의 기본값으로는 Terra high/max가 DeepSWE 격차 대비 비용 이점 때문에 첫 후보가 되지만, 출력 토큰과 스텝 수까지 보면 모든 축에서 최선은 아닙니다. 대량의 저위험·검증 쉬운 작업에는 낮은 effort의 Luna가 합리적입니다. 다만 Luna가 싼 이유는 토큰을 아껴서가 아니라 모델 단가 자체가 낮기 때문이고, Luna max도 첫 응답 지연 자체는 인터랙티브용으로 빠르지 않다는 점은 기억해 둘 만합니다. 무엇을 고르든 벤치마크 점수 하나가 아니라 성공률·비용·시간·토큰·스텝·회귀율을 함께 재고, 자신의 하네스에서 다시 검증하는 과정이 필요합니다.

## 함께 보면 좋을 자료

- [OpenAI, "Previewing GPT-5.6 Sol: a next-generation model"](https://openai.com/index/previewing-gpt-5-6-sol/): Sol 단독 프리뷰 발표.
- [Artificial Analysis, Terminal-Bench v2.1 평가 페이지](https://artificialanalysis.ai/evaluations/terminalbench-v2-1): Terminal-Bench 독립 평가 방법론과 다른 모델과의 비교.
- [DeepSWE 공식 GitHub](https://github.com/datacurve-ai/deep-swe): 태스크 구성과 검증 방식 원문.
- [DeepSWE, "DeepSWE v1.1"](https://deepswe.datacurve.ai/blog/deepswe-v1-1): 리더보드 지표 정의와 Fable 5 완주율 각주 원문.

## 참고 자료

- [OpenAI, "GPT-5.6: Frontier intelligence that scales with your ambition"](https://openai.com/index/gpt-5-6/), 2026-07-09, 조회일 2026-07-13.
- [OpenAI, "Previewing GPT-5.6 Sol: a next-generation model"](https://openai.com/index/previewing-gpt-5-6-sol/), 조회일 2026-07-13.
- [OpenAI 도움말 센터, "GPT-5.6 in ChatGPT"](https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna), 조회일 2026-07-13.
- [Artificial Analysis, GPT-5.6 Sol](https://artificialanalysis.ai/models/gpt-5-6-sol), 조회일 2026-07-13.
- [Artificial Analysis, GPT-5.6 Terra](https://artificialanalysis.ai/models/gpt-5-6-terra), 조회일 2026-07-13.
- [Artificial Analysis, GPT-5.6 Luna](https://artificialanalysis.ai/models/gpt-5-6-luna), 조회일 2026-07-13.
- [Artificial Analysis, 성능 벤치마킹 방법론](https://artificialanalysis.ai/methodology/performance-benchmarking), 조회일 2026-07-13.
- [Artificial Analysis, Terminal-Bench v2.1](https://artificialanalysis.ai/evaluations/terminalbench-v2-1), 조회일 2026-07-13.
- [DeepSWE 공식 리더보드](https://deepswe.datacurve.ai/), 갱신일 2026-07-16, 조회일 2026-07-17.
- [DeepSWE, "DeepSWE v1.1"](https://deepswe.datacurve.ai/blog/deepswe-v1-1), 조회일 2026-07-17.
- [DeepSWE, "DeepSWE"](https://deepswe.datacurve.ai/blog/deepswe), 조회일 2026-07-17.
- [DeepSWE 공식 GitHub](https://github.com/datacurve-ai/deep-swe), 조회일 2026-07-17.
- [Terminal-Bench 공식 사이트](https://www.tbench.ai/), 조회일 2026-07-13.
- [Terminal-Bench 저장소](https://github.com/laude-institute/terminal-bench), 조회일 2026-07-13.
