---
title: "VibeThinker-3B: 검증 가능한 추론을 3B 모델에 압축한 실험"
meta_title: ""
description: "Sina Weibo의 WeiboAI가 발표한 VibeThinker-3B. Qwen2.5-Coder-3B 기반 3B 모델에 다단계 RL과 자기증류를 집중 적용해 수학·코딩 벤치마크에서 frontier급 결과를 주장하는 기술 보고서입니다."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
image: ""
categories: ["AI"]
tags: ["small-language-model", "reasoning", "reinforcement-learning", "math", "coding"]
author: "whackur"
translationKey: "vibethinker-3b-verifiable-reasoning"
draft: false
---

"작은 모델이 큰 모델을 이겼다"는 주장은 논문마다 나옵니다. 보통은 특정 벤치마크 하나에서의 결과를 두고 하는 말입니다. Sina Weibo의 WeiboAI팀이 2026년 6월 15일 공개한 [VibeThinker-3B](https://arxiv.org/abs/2606.16140) 역시 비슷한 구조의 주장을 합니다. 다만 논문이 조심스럽게 선을 긋는 부분이 있습니다. "작은 모델이 모든 걸 대체한다"가 아니라, **검증 가능한 추론(verifiable reasoning) 영역만큼은 작은 모델로 압축될 수 있다**는 겁니다.

## 모델 기본 정보

- arXiv ID: [2606.16140](https://arxiv.org/abs/2606.16140)
- 베이스 모델: [Qwen/Qwen2.5-Coder-3B](https://huggingface.co/Qwen/Qwen2.5-Coder-3B)
- 파라미터: 약 3,085,938,688 (BF16 safetensors 기준)
- 저자: Sen Xu 외, Sina Weibo Inc.
- 라이선스: MIT
- GitHub/HuggingFace: [WeiboAI/VibeThinker](https://github.com/WeiboAI/VibeThinker), [WeiboAI/VibeThinker-3B](https://huggingface.co/WeiboAI/VibeThinker-3B)

## 핵심 가설: 압축과 커버리지

저자들은 모델 능력이 파라미터에 의존하는 방식이 능력 유형별로 다르다고 봅니다.

- **압축 가능한 능력**: 검증 가능한 추론, 다단계 추론, 제약 충족, 자기 수정, 수학/코딩/STEM 문제 풀이.
- **넓은 커버리지가 필요한 능력**: 열린 도메인 지식, 범용 대화, 장기 시나리오 이해, 광범위한 사실 회상.

이 가설이 맞다면, 수학이나 코딩처럼 정답 검증이 명확한 영역에서는 훈련을 집중해 작은 모델을 고밀도 전문가로 만들 수 있습니다. VibeThinker-3B는 그 시도입니다.

## 학습 파이프라인

5단계로 구성됩니다.

### 1. 커리큘럼 기반 2단계 SFT

1단계에서는 수학, 코드, STEM 추론, 일반 대화, 명령 따르기를 폭넓게 커버합니다. 2단계에서는 어렵고 긴 추론 샘플로 전환합니다. seed query는 명확한 정답, 풀이, unit test, 실행 가능한 평가 규칙이 있는 데이터 위주로 선택합니다.

여러 candidate reasoning trace를 보존하는 **Diversity-Exploring Distillation**을 씁니다. 단일 정답 풀이를 암기하는 게 아니라, 다양한 유효 풀이 경로의 스펙트럼을 만드는 것이 목표입니다.

### 2. 다중 도메인 추론 RL

VibeThinker-1.5B에서 쓰인 **MGPO(MaxEnt-Guided Policy Optimization)**를 재사용합니다. 프롬프트별 그룹 정확도가 0이나 1에 가까운 샘플보다, 정답/오답 rollout이 공존하는 경계 샘플에 더 큰 학습 가중치를 줍니다. 항상 맞히거나 항상 틀리는 문제에는 학습 신호가 거의 없고, 맞기도 틀리기도 하는 경계 문제에 신호가 가장 많이 담겨 있다는 발상입니다. Math RL → Code RL → STEM RL 순서로 진행하며, 64K long-context window를 단일 컨텍스트로 사용해 긴 추론 trajectory를 보존합니다.

### 3. Long2Short Math RL

accuracy 중심 RL로 충분히 추론을 펼친 뒤, 올바른 trajectory 중 더 짧은 응답에 보상을 이동시킵니다. 정확도를 유지하면서 중복 추론 토큰을 줄이는 게 목표입니다.

### 4. 오프라인 자기증류

Math/Code/STEM RL 체크포인트에서 verifier로 맞는 trajectory를 골라 통합 student 모델에 다시 SFT합니다. 아직 잘 모델링하지 못하는 correct trace를 우선 선택하기 위해, length-normalized negative log-likelihood 기반 learning-potential score를 씁니다.

### 5. Instruct RL

최종 사용자 응답 품질을 위해 format-sensitive prompt, long-context instruction, general alignment 예제를 사용합니다. 명시적 제약은 rule-based validator, 열린 prompt는 rubric-based reward model로 평가합니다.

## 주요 벤치마크 결과

논문과 [모델카드](https://huggingface.co/WeiboAI/VibeThinker-3B)에서 보고한 수치입니다. CLR이 붙은 숫자는 아래에서 설명할 test-time 기법을 적용한 결과입니다.

| 벤치마크 | 점수 | CLR 적용 |
|---------|------|---------|
| AIME25 | 91.4 | 96.7 |
| AIME26 | 94.3 | 97.1 |
| HMMT25 | 89.3 | 95.4 |
| BruMO25 | 93.8 | 99.2 |
| IMO-AnswerBench | 76.4 | 80.6 |
| LiveCodeBench v6 | 80.2 Pass@1 | 해당 없음 |
| OJBench | 38.6 | 해당 없음 |
| GPQA-Diamond | 해당 없음 | 72.9 |
| IFEval | 93.4 | 해당 없음 |
| IFBench | 74.5 | 해당 없음 |

LeetCode OOD(2026년 4월 25일~5월 31일 신규 문제, Python one-shot)는 128문제 중 123개를 맞춰 96.1%를 기록했다고 보고합니다.

평가 조건도 함께 읽어야 합니다. 수학 평가는 64회 독립 generation 평균 Pass@1, IMO-AnswerBench는 16회, 코딩은 8회 평균입니다. 비교 모델 점수는 각 모델의 release report나 공개 리더보드에서 가져온 것으로, 완전히 동일한 harness로 재평가한 결과가 아닐 수 있습니다.

## CLR: 클레임 단위 신뢰도 평가

**CLR(Claim-Level Reliability Assessment)**은 모델 가중치를 업데이트하지 않는 test-time scaling 전략입니다.

기존 self-verification은 긴 추론 trace 전체를 한 번에 검증합니다. CLR은 trace를 중요한 claim이나 논리적 앵커 단위로 쪼개 각각의 신뢰도를 평가합니다. 정확도를 올리는 방향으로 작동하며, answer-verifiable 수학 벤치마크에서 Pass@1을 끌어올렸다고 보고합니다.

개선폭은 벤치마크별로 이렇습니다. AIME26은 94.3에서 97.1로, HMMT25는 89.3에서 95.4로, BruMO25는 93.8에서 99.2로, IMO-AnswerBench는 76.4에서 80.6으로 올라갑니다.

## 적합한 용도와 제한 사항

[모델카드](https://huggingface.co/WeiboAI/VibeThinker-3B)가 명확하게 선을 긋습니다.

**적합한 용도:**
- LeetCode / 경쟁 프로그래밍 스타일 문제
- 수학 경시, STEM 추론, 정답 검증 가능한 문제
- 로컬/저비용 추론 환경에서 강한 reasoning core가 필요한 경우
- 큰 orchestrator가 분해한 검증 가능한 subproblem 풀이

**피해야 하는 용도:**
- tool calling / function calling
- API orchestration
- 자율 코딩 에이전트
- 범용 리서치 에이전트
- 일반 대화, 잡지식 QA

모델카드는 이 모델이 tool-calling이나 agent-based programming 데이터로 학습되지 않았다고 명시합니다.

## 한계와 주의점

수학 평가에 LLM-as-judge를 함께 쓰므로, 어떤 judge를 쓰느냐에 따라 결과가 달라질 수 있습니다. 비교 모델 점수가 동일 harness 재평가가 아닌 공개 리포트에서 수집한 것이라는 점도 기억해야 합니다. 수학 점수가 64회 독립 생성의 평균이라는 점 역시 단일 호출에서 체감하는 성능과는 차이를 만들 수 있습니다. "3B가 frontier generalist를 대체한다"는 식으로 읽으면 과장입니다. 성능은 verifiable reasoning 도메인에 한정됩니다.

## 함께 보면 좋을 자료

- [arXiv:2606.16140](https://arxiv.org/abs/2606.16140): VibeThinker-3B 원논문
- [Qwen2.5-Coder 시리즈](https://qwenlm.github.io/blog/qwen2.5-coder/): VibeThinker-3B 베이스 모델 배경
- [DeepSeek-R1 기술 보고서](https://arxiv.org/abs/2501.12948): GRPO 기반 reasoning RL의 앞선 사례
- [LiveCodeBench](https://livecodebench.github.io): 논문에서 사용한 코딩 벤치마크

## 참고 자료

- [arXiv:2606.16140 "VibeThinker-3B: Exploring the Frontier of Verifiable Reasoning in Small Language Models"](https://arxiv.org/abs/2606.16140): Xu et al., Sina Weibo Inc., 2026-06-15
- [WeiboAI/VibeThinker GitHub](https://github.com/WeiboAI/VibeThinker): 코드·학습 파이프라인, 조회일 2026-06-30
- [WeiboAI/VibeThinker-3B 모델카드](https://huggingface.co/WeiboAI/VibeThinker-3B): 사용 제한, 벤치마크 결과, 조회일 2026-06-30
- [Hugging Face Papers: 2606.16140](https://huggingface.co/papers/2606.16140): 논문 요약, 조회일 2026-06-30
