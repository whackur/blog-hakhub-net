---
title: "DeepSWE: 코딩 에이전트를 장기 과제로 평가하는 벤치마크"
meta_title: ""
description: "DataCurve AI가 공개한 long-horizon 소프트웨어 엔지니어링 벤치마크 DeepSWE. 113개 태스크, 행동 기반 verifier, mini-swe-agent 고정 harness로 모델별 성능을 측정합니다."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-06-30T02:00:00+09:00
image: ""
categories: ["AI"]
tags: ["benchmark", "coding-agent", "swe-bench", "llm", "evaluation"]
author: "whackur"
translationKey: "deepswe-coding-agent-benchmark"
draft: false
---

코딩 에이전트를 평가할 때 SWE-bench가 오랫동안 기준이었습니다. 그런데 SWE-bench의 태스크 대부분은 단일 파일 버그 수정이고, 정답이 이미 공개 커밋에 있습니다. 에이전트가 모델 학습 데이터에서 본 답을 그대로 재현하는 건지, 진짜로 코드를 이해하고 고치는 건지 구분하기 어렵습니다.

DataCurve AI가 공개한 [DeepSWE](https://deepswe.datacurve.ai/)는 이 문제를 다른 각도에서 접근합니다. 참조 패치 기반이 아니라 행동 기반 verifier로 채점하고, 태스크와 정답을 새로 작성해 오염 위험을 낮췄다고 주장합니다. 이름 때문에 DeepSeek 계열 모델이나 RL 학습법으로 오해하기 쉬운데, [공식 README](https://github.com/datacurve-ai/deep-swe)와 사이트 기준으로 DeepSWE 자체는 모델이 아니라 **벤치마크와 리더보드**입니다.

## 벤치마크 구성

[공식 사이트](https://deepswe.datacurve.ai/) 기준 DeepSWE는 113개 태스크로 구성됩니다. 언어 분포는 TypeScript 35개, Go 34개, Python 34개, JavaScript 5개, Rust 5개이고, 저장소 수는 공식 사이트가 91개로 소개합니다.

태스크 유형은 기능 추가(feature_request) 중심으로 113개 중 106개가 여기에 해당합니다. 버그 수정은 4개, 개선(enhancement)이 3개입니다. 단일 파일 수정 위주인 SWE-bench Verified와는 성격이 다릅니다.

## Harbor 태스크 형식

각 태스크는 [Harbor 형식](https://www.harborframework.com/docs/tasks)을 따릅니다.

```text
task.toml         메타데이터: 저장소, 기준 커밋, 언어, 이미지, 실행 제한
instruction.md    에이전트가 받는 지시문
pre_artifacts.sh  에이전트 커밋을 패치로 추출
environment/      재현 가능한 Dockerfile
tests/            verifier 진입점, held-out 테스트, 채점 설정
solution/         참조 정답 (에이전트에게 숨김)
```

모든 태스크의 에이전트 타임아웃은 5,400초(90분)입니다. 인터넷 접근은 차단(`allow_internet = false`)되어 있습니다.

태스크 예시를 보면 성격이 잡힙니다. `happy-dom-abort-pending-body-reads`는 TypeScript 저장소 `capricorn86/happy-dom`을 대상으로 합니다. 지시문은 "shutdown으로 Request/Response body 소비, formData 파싱, 타이머가 중단될 때 AbortError와 cleanup semantics를 맞추라"는 실제 코드베이스 동작 변경 요구입니다. 함수 하나를 짜는 문제가 아니라 여러 파일에 걸친 동작 변경입니다.

## 평가 원리

### 참조 패치 매칭이 아닌 행동 기반 채점

DeepSWE가 SWE-bench와 가장 뚜렷하게 다른 점입니다. verifier는 에이전트가 제출한 패치의 내부 구현이 참조 정답과 같은지 보지 않습니다. 대신 "지시문이 설명한 동작을 실제로 수행하는가"를 별도 컨테이너에서 실행해 확인합니다. 내부 심볼 이름이나 구현 구조가 달라도, 관측 가능한 동작이 맞으면 통과합니다.

`solution/`의 참조 정답은 에이전트에게 공개되지 않습니다. 채점 시에도 쓰이지 않고, 리뷰어가 오프라인에서 correctness를 spot-check하는 자료로만 씁니다.

### 별도 verifier 환경

v1.1부터 Harbor의 separate verifier environment를 사용합니다. 흐름은 이렇습니다.

1. 에이전트가 격리된 컨테이너에서 코드를 수정하고 커밋합니다.
2. `pre_artifacts.sh`가 커밋들을 패치로 추출합니다.
3. 패치를 새로운 컨테이너에 적용합니다.
4. verifier가 해당 컨테이너에서 테스트를 실행하고 채점합니다.
5. 결과는 `reward.json`, `ctrf.json`, `run.log` 등으로 남습니다.

에이전트가 작업 환경을 오염시키거나 verifier에 직접 영향을 주는 경로를 차단하고, 패치 적용 가능성과 재현성을 강제하는 구조입니다.

### Pier와 mini-swe-agent

DataCurve가 만든 Pier는 Harbor 호환 runner입니다. Harbor를 포크해서 시작했고, `allow_internet = false` 태스크에서 필요한 LLM API 호출과 도구 설치를 허용하는 **per-agent network allowlist**를 추가했습니다. 작업 환경은 격리하되 에이전트 동작에 필요한 네트워크만 허용하는 절충입니다.

리더보드의 모든 모델 점수는 [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)를 harness로 고정해 실행했습니다. DeepSWE 리더보드는 "동일한 SWE agent scaffold 위에서 모델별 성능 차이"를 보는 표입니다. Claude Code, Codex, OpenCode 같은 제품형 에이전트를 end-to-end로 비교한 표가 아닙니다.

## 리더보드 스냅샷 (2026년 6월 기준)

공식 사이트 기준 주요 결과입니다. 점수 옆 ±는 공식 불확실성 구간이고, 괄호 안은 추론 예산 설정입니다.

| 모델 | 점수 |
|------|------|
| gpt-5.5 [xhigh] | 70% ± 3% |
| claude-opus-4.8 [max] | 58% ± 2% |
| gpt-5.4 [xhigh] | 56% ± 2% |
| claude-opus-4.7 [max] | 54% ± 5% |
| claude-sonnet-4.6 [high] | 32% ± 2% |
| gemini-3.5-flash [medium] | 28% ± 4% |
| deepseek-v4-pro | 8% ± 3% |

추론 예산 설정(xhigh, max, high, medium)이 점수에 영향을 줍니다. 동일 모델이라도 예산 등급이 낮으면 점수가 내려갑니다.

## SWE-bench류와 비교

[공식 블로그](https://deepswe.datacurve.ai/blog)가 제시한 수치 비교입니다.

| 항목 | SWE-Bench Verified | SWE-Bench Pro | DeepSWE |
|------|-------------------|---------------|---------|
| 평균 prompt 길이 | 1,700자 | 4,614자 | 2,158자 |
| 평균 정답 추가 라인 | 10 | 120 | 668 |
| 평균 수정 파일 수 | 1 | 5 | 7 |

프롬프트 자체는 SWE-Bench Pro보다 짧지만, 참조 정답의 변경 규모는 훨씬 큽니다. "긴 스펙을 그대로 구현하는 능력"보다 "짧은 행동 요구에서 코드베이스를 탐색하고 큰 변경을 완성하는 능력"을 측정하려는 설계입니다.

## 오염 방지 주장과 한계

공식 블로그는 DeepSWE가 기존 공개 커밋/PR에서 정답을 가져오지 않고, 태스크와 참조 정답을 새로 작성했다고 주장합니다. 참조 정답이 채점에 쓰이지 않으므로, 모델이 참조 패치를 사전 학습에서 봤더라도 verifier를 통과해야 점수를 얻습니다.

다만 이는 DataCurve 측의 설계 주장이고, 공개 자료만으로 외부에서 독립 검증하기는 어렵습니다. 태스크가 공개 저장소에 올라간 이후에는 미래 모델 학습 데이터에 포함될 가능성도 생깁니다. "contamination-free" 주장은 공개 시점과 함께 읽어야 합니다.

## 직접 실행하기

[공식 README](https://github.com/datacurve-ai/deep-swe)와 [Run 페이지](https://deepswe.datacurve.ai/run) 기준 Quickstart입니다.

사용할 모델 제공사(Anthropic, OpenAI 등)의 API 키를 환경 변수로 설정해야 합니다. 설정 방법은 각 제공사의 공식 문서를 참고하세요.

```bash
git clone https://github.com/datacurve-ai/deep-swe
uv tool install datacurve-pier

# Claude Opus 4.8으로 전체 실행
pier run -p deep-swe/tasks --agent mini-swe-agent --model anthropic/claude-opus-4-8

# 서브셋 실행 (10개, 시드 고정)
pier run -p deep-swe/tasks --agent mini-swe-agent --n-tasks 10 --sample-seed 0

# 단일 태스크 실행
pier run -p deep-swe/tasks/<task-id> --agent mini-swe-agent

# Modal로 병렬 실행
pier run -p deep-swe/tasks --agent mini-swe-agent --model <provider/model> --env modal
```

## 함께 보면 좋을 자료

- [SWE-bench](https://www.swebench.com): 코딩 에이전트 평가의 기준점, public issue/PR 기반 태스크
- [SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent): DeepSWE가 harness로 사용하는 model-agnostic SWE agent
- [Harbor Framework](https://www.harborframework.com/docs/tasks): DeepSWE 태스크 형식의 기반 프레임워크
- [LiveCodeBench](https://livecodebench.github.io): 오염 방지를 위해 새 문제를 지속 수집하는 코딩 벤치마크

## 참고 자료

- [DeepSWE 공식 사이트](https://deepswe.datacurve.ai/): DataCurve AI, 조회일 2026-06-30
- [datacurve-ai/deep-swe GitHub](https://github.com/datacurve-ai/deep-swe): README 및 태스크 구조 명세
- [DeepSWE 블로그](https://deepswe.datacurve.ai/blog): 공식 블로그, SWE-bench 비교 수치 포함
- [DeepSWE Run 페이지](https://deepswe.datacurve.ai/run): Pier 설치·실행법, network allowlist 설명
- [Harbor Framework Docs](https://www.harborframework.com/docs/tasks): 태스크 형식 명세, 조회일 2026-06-30
- [SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent): harness 배경, 조회일 2026-06-30
