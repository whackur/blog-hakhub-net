---
title: "GPT-5.6 Sol·Terra·Luna 코딩 에이전트 모델 선택 가이드"
meta_title: ""
description: "GPT-5.6의 Sol·Terra·Luna 티어와 max/high/xhigh/ultra 설정을 구분하고, OpenAI 런치 스냅샷과 DeepSWE·Artificial Analysis 최신 수치로 Hermes Agent·Codex 같은 코딩 에이전트에 어떤 모델을 언제 써야 하는지 정리합니다."
date: 2026-07-13T09:30:00+09:00
lastmod: 2026-07-13T09:30:00+09:00
image: ""
categories: ["AI"]
tags: ["gpt-5-6", "coding-agent", "model-routing", "benchmark", "llm"]
author: "whackur"
translationKey: "gpt-5-6-coding-agent-model-routing"
draft: false
---

GPT-5.6 이야기를 하다 보면 "Luna Max가 Terra High보다 낫다더라" 식의 서열이 자주 돌아다닙니다. 이 문장은 애초에 성립하지 않는 비교입니다. Sol·Terra·Luna는 서로 다른 모델(능력 티어)이고, max·high·xhigh·ultra는 같은 모델 안에서 얼마나 오래 생각하고 얼마나 많은 에이전트를 병렬로 굴릴지 정하는 설정입니다. 티어와 설정을 한 줄로 섞어 서열화하면 애초에 비교 축이 다른 값을 나란히 놓는 셈입니다.

이 글은 [OpenAI 발표](https://openai.com/index/gpt-5-6/), [DeepSWE 공식 리더보드](https://deepswe.datacurve.ai/), [Artificial Analysis](https://artificialanalysis.ai/) 모델 페이지(2026년 7월 13일 조회)를 근거로 세 모델의 차이를 정리하고, Hermes Agent나 Codex 같은 코딩 에이전트에서 어떤 작업에 어떤 티어를 쓰는 게 합리적인지 라우팅 기준을 제시합니다.

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

[DeepSWE 공식 사이트](https://deepswe.datacurve.ai/)는 2026년 7월 9일 갱신 기준(2026-07-13 조회) 113개 태스크, 91개 저장소, 5개 언어를 다루고, 모델 간 조건을 맞추기 위해 고정된 `mini-swe-agent` 스캐폴드로 리더보드를 돌립니다. 원본 장기 과제, 프로그램/행동 기반 검증기, 홀드아웃 테스트, 별도 검증 환경을 씁니다. 즉 이건 모델이 아니라 벤치마크/리더보드입니다.

| 모델 (설정) | Pass@1 | 태스크당 평균 비용 | 태스크당 출력 토큰 | 스텝 수 |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol [max] | 73% ± 3% | $8.39 | 60k | 61 |
| GPT-5.6 Terra [max] | 70% ± 3% | $4.95 | 72k | 76 |
| GPT-5.6 Luna [max] | 67% ± 4% | $3.03 | 73k | 102 |

출처: [DeepSWE 공식 리더보드](https://deepswe.datacurve.ai/), 조회일 2026-07-13.

Sol이 절대 성공률에서 가장 높습니다. Terra는 Sol보다 3%p 낮은데 태스크당 비용은 약 41% 적습니다. Luna는 6%p 낮은데 비용은 약 64% 적습니다. 이 41%·64%는 표에 나온 값을 제가 직접 계산한 파생 수치이지, DeepSWE가 공식적으로 발표한 "토큰 효율" 지표가 아닙니다. 태스크당 가격이 낮다고 해서 같은 성공 확률을 보장하지는 않습니다.

DeepSWE의 고정 하네스는 세 모델의 행동을 하나의 스캐폴드 위에서 비교한 것입니다. Hermes Agent나 Codex, Claude Code처럼 각자 다른 오케스트레이션·툴·프롬프트·재시도·샌드박스를 쓰는 완제품의 순위를 직접 매긴 게 아닙니다.

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
2. **범위가 명확한 코딩**: 단일 기능 구현, 정형화된 버그 수정, 테스트 보강. Terra high/max를 기본값으로 둡니다. DeepSWE 점수 차이가 Sol 대비 3%p 수준으로 크지 않은데 태스크당 비용은 상당히 낮기 때문입니다. 다만 이건 DeepSWE 태스크 기준이므로, 실제로는 팀 자신의 저장소·워크플로에서 검증해야 합니다.
3. **고위험 / 멀티파일 / 장시간 자율 작업**: 마이그레이션, 보안에 민감한 변경, 여러 파일에 걸친 실패, 사람 개입 없이 오래 도는 자율 실행. Sol max를 기본으로 쓰고, 병렬 오케스트레이션과 추가 비용이 정당화될 때만 `ultra`를 검토합니다.

**에스컬레이션 트리거**: 테스트 실패가 반복되거나, 모델이 스스로 불확실성을 표시하거나, 같은 문제에서 재시도 횟수가 임계치를 넘으면 한 단계 위 티어로 올립니다. 반대로 저위험 작업에서 Terra/Sol을 계속 쓰고 있다면 Luna로 내려서 비용을 줄일 여지가 있는지 확인합니다.

## 측정 체크리스트

모델 선택을 검증할 때는 다음을 함께 봅니다. 어느 하나만으로는 판단이 왜곡됩니다.

- 성공률 (태스크 완료 여부)
- 해결된 태스크당 비용
- wall-clock 시간 (실제로 걸린 총 시간)
- 첫 유효 응답까지 걸린 시간 (reasoning 포함)
- 재시도·스텝 수
- 회귀율 (고친 곳에서 새 버그가 나는 빈도)
- 사람 리뷰에 드는 시간

`성공률 / 토큰 수`처럼 서로 다른 벤치마크·다른 태스크에 걸쳐 하나의 숫자로 뭉뚱그린 "효율" 지표는 쓰지 않는 게 낫습니다. 토큰 수는 태스크 난이도, 하네스, reasoning effort 설정에 따라 달라지므로 벤치마크가 다르면 같은 잣대가 아닙니다. DeepSWE 표에서 계산한 비용 차이(41%, 64%)도 DeepSWE라는 하나의 벤치마크·하나의 하네스 안에서만 유효한 파생값입니다.

## 정리

Sol·Terra·Luna는 모델 자체가 다르고, max·high·xhigh·ultra는 그 모델을 얼마나 오래 생각시키고 어떻게 병렬화할지 정하는 설정입니다. 이 둘을 뒤섞어 만든 서열은 처음부터 성립하지 않습니다. 어려운 장기 과제에서 절대 성공률이 우선이면 Sol max에서 시작하고, 병렬 오케스트레이션이 필요할 때만 ultra를 씁니다. 일상적인 코딩 에이전트 실행의 기본값으로는 Terra high/max가 DeepSWE 격차 대비 비용 이점 때문에 첫 후보가 됩니다. 대량의 저위험·검증 쉬운 작업에는 낮은 effort의 Luna가 합리적이지만, Luna max도 첫 응답 지연 자체는 인터랙티브용으로 빠르지 않다는 점은 기억해 둘 만합니다. 무엇을 고르든 벤치마크 점수 하나가 아니라 성공률·비용·시간·회귀율을 함께 재고, 자신의 하네스에서 다시 검증하는 과정이 필요합니다.

## 함께 보면 좋을 자료

- [OpenAI, "Previewing GPT-5.6 Sol: a next-generation model"](https://openai.com/index/previewing-gpt-5-6-sol/): Sol 단독 프리뷰 발표.
- [Artificial Analysis, Terminal-Bench v2.1 평가 페이지](https://artificialanalysis.ai/evaluations/terminalbench-v2-1): Terminal-Bench 독립 평가 방법론과 다른 모델과의 비교.
- [DeepSWE 공식 GitHub](https://github.com/datacurve-ai/deep-swe): 태스크 구성과 검증 방식 원문.

## 참고 자료

- [OpenAI, "GPT-5.6: Frontier intelligence that scales with your ambition"](https://openai.com/index/gpt-5-6/), 2026-07-09, 조회일 2026-07-13.
- [OpenAI, "Previewing GPT-5.6 Sol: a next-generation model"](https://openai.com/index/previewing-gpt-5-6-sol/), 조회일 2026-07-13.
- [OpenAI 도움말 센터, "GPT-5.6 in ChatGPT"](https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna), 조회일 2026-07-13.
- [Artificial Analysis, GPT-5.6 Sol](https://artificialanalysis.ai/models/gpt-5-6-sol), 조회일 2026-07-13.
- [Artificial Analysis, GPT-5.6 Terra](https://artificialanalysis.ai/models/gpt-5-6-terra), 조회일 2026-07-13.
- [Artificial Analysis, GPT-5.6 Luna](https://artificialanalysis.ai/models/gpt-5-6-luna), 조회일 2026-07-13.
- [Artificial Analysis, 성능 벤치마킹 방법론](https://artificialanalysis.ai/methodology/performance-benchmarking), 조회일 2026-07-13.
- [Artificial Analysis, Terminal-Bench v2.1](https://artificialanalysis.ai/evaluations/terminalbench-v2-1), 조회일 2026-07-13.
- [DeepSWE 공식 리더보드](https://deepswe.datacurve.ai/), 갱신일 2026-07-09, 조회일 2026-07-13.
- [DeepSWE 공식 GitHub](https://github.com/datacurve-ai/deep-swe), 조회일 2026-07-13.
- [Terminal-Bench 공식 사이트](https://www.tbench.ai/), 조회일 2026-07-13.
- [Terminal-Bench 저장소](https://github.com/laude-institute/terminal-bench), 조회일 2026-07-13.
