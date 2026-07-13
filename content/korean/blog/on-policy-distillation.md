---
title: "On-Policy Distillation: RL과 SFT 사이의 빈틈을 메우는 법"
meta_title: ""
description: "Thinking Machines Lab이 공개한 on-policy distillation을 리뷰합니다. 학생이 직접 생성한 궤적에 교사 모델이 토큰 단위로 점수를 매기는 방식으로, Qwen3 기술보고서 수치와 함께 reverse KL의 성격과 재현 조건을 짚습니다."
date: 2026-07-10T14:08:50+09:00
lastmod: 2026-07-10T14:08:50+09:00
image: ""
categories: ["AI"]
tags: ["llm", "post-training", "distillation", "reinforcement-learning", "reverse-kl"]
author: "whackur"
translationKey: "on-policy-distillation"
draft: false
---

포스트 트레이닝에서 흔히 쓰는 두 방법에는 각자 구멍이 있습니다. SFT(supervised fine-tuning)는 교사가 만든 정답 시퀀스를 그대로 모방시키는데, 학생이 실제로 방문할 상태가 아닌 곳에서 배우다 보니 추론 단계가 길어질수록 오차가 쌓입니다. RL(강화학습)은 학생이 직접 생성한 궤적으로 배우니 이 문제는 없지만, 보상이 에피소드 하나당 한두 비트로 끝나는 경우가 많아 학습 신호가 지나치게 희박합니다. Thinking Machines Lab이 2025년 10월 [공개한 글](https://thinkingmachines.ai/blog/on-policy-distillation/)은 이 둘의 장점만 남기는 조합을 제안합니다. 학생이 스스로 궤적을 만들고, 강한 교사 모델이 그 궤적의 토큰 하나하나에 점수를 매기는 방식입니다.

이 글은 그 아이디어의 메커니즘, Qwen3 기술보고서와 Thinking Machines의 실험이 실제로 보여주는 것, 그리고 2026년 현재 이걸 재현하려면 무엇이 필요한지를 정리합니다.

## SFT와 RL이 각자 남기는 빈틈

포스트 트레이닝 방법은 학습 신호를 어디서 얻느냐로 나뉩니다.

- **오프폴리시(off-policy) 학습**: SFT가 대표적입니다. 교사(또는 사람)가 만든 고정된 시퀀스를 학생이 그대로 따라 배웁니다. 매 토큰마다 정답이 주어지니 신호가 조밀(dense)합니다. 문제는 학생이 실제 추론 중에 마주칠 상태와 학습 데이터의 상태가 어긋난다는 점입니다. 한 토큰이 틀리면 다음 토큰도 학생이 훈련 때 보지 못한 상태에서 나오게 되고, 이 오차가 시퀀스 길이만큼 누적됩니다. 스타일은 잘 흡수해도 사실 정확도까지 흡수하지는 못한다는 [Gudibande 등의 관찰](https://arxiv.org/abs/2305.15717)도 이 문제와 맞닿아 있습니다.
- **온폴리시(on-policy) 학습**: RL이 대표적입니다. 학생이 직접 샘플링한 롤아웃에 보상을 매기니 학생이 실제로 방문하는 상태에서만 학습합니다. 대신 보상은 보통 에피소드 끝에서 한 번, 정답/오답 같은 희박한(sparse) 형태로만 주어집니다. 토큰 수가 늘어나도 정보량은 늘지 않습니다.

Thinking Machines Lab의 글은 이 대비를 체스 코칭으로 설명합니다. 온폴리시 RL만으로 배우는 건 코치 없이 대국만 반복하고 승패만 통보받는 것과 비슷합니다. 오프폴리시 distillation은 그랜드마스터의 대국을 관전하는 것과 비슷한데, 강한 수를 보긴 하지만 초보자는 그 국면에 놓일 일이 애초에 없습니다.

## On-policy distillation의 구조

on-policy distillation은 이 둘을 다음처럼 조합합니다.

| 방법 | 샘플링 | 보상 신호 |
| --- | --- | --- |
| SFT | 오프폴리시 | dense |
| RL | 온폴리시 | sparse |
| On-policy distillation | 온폴리시 | dense |

**학생이 직접 궤적을 샘플링**하고, **고정된 교사가 그 궤적의 각 토큰에 점수를 매깁니다.** 학생이 실제로 방문한 상태에서 채점이 이뤄지니 오프폴리시 학습의 상태 불일치 문제가 없고, 토큰 단위로 신호가 나오니 RL의 희박한 보상 문제도 없습니다.

이 아이디어 자체가 새로운 건 아닙니다. 학생 궤적에 반복적으로 교사 평가를 붙이는 [DAGGER](https://arxiv.org/abs/1011.0686)(2010)나 추론 과정의 각 단계를 채점하는 [process reward modeling](https://arxiv.org/abs/2305.20050) 계열이 먼저 있었고, 언어모델에 직접 적용한 연구로는 [Agarwal 등](https://arxiv.org/abs/2306.13649)의 GKD(2023, ICLR 2024)와 [MiniLLM](https://arxiv.org/abs/2306.08543)(Gu 등, ICLR 2024)이 있습니다. Thinking Machines의 글은 이 계보를 확장해 [Qwen3 팀의 실험](https://arxiv.org/abs/2505.09388)까지 연결하고, 구현을 단순화해 Tinker 학습 스택 위에 공개했습니다.

### reverse KL 손실 함수

핵심 손실은 학생 분포에서 샘플링한 시퀀스에 대한 토큰별 reverse KL입니다.

```text
KL(π_θ ‖ π_teacher)
= E_{x_{t+1} ~ π_θ}[log π_θ(x_{t+1}|x_{1..t})
                     - log π_teacher(x_{t+1}|x_{1..t})]
```

학생이 실제로 만든 prefix `x_{1..t}`마다 다음 토큰 `x_{t+1}`을 학생 정책 `π_θ`에서 샘플링하고, 그 토큰에 학생과 교사 정책 `π_teacher`가 부여한 로그 확률의 차이를 사용합니다. 미래 스텝에 대한 discount factor는 실무에서 0으로 둡니다. Thinking Machines의 실험에서는 0보다 큰 값을 써도 성능이 더 좋아지지 않았다고 합니다.

reverse KL을 forward KL(SFT가 쓰는 방향) 대신 쓰는 이유는 세 가지로 설명됩니다.

1. **"해킹하기 어렵다"**: KL이 낮다는 건 교사 관점에서 항상 바람직한 행동이라는 뜻입니다. RL에서 보상 함수의 틈을 찾아 우회하는 reward hacking과 대비됩니다. 다만 이건 **고정된 교사 분포를 얼마나 잘 따르는가**에 대한 이야기일 뿐입니다. 교사 분포 자체가 사실이거나 안전하거나 편향 없다는 보장은 아닙니다. 교사가 틀렸거나 편향돼 있으면 학생은 그 틀림과 편향까지 충실하게 따라갑니다.
2. **mode-seeking**: forward KL은 교사가 갖는 여러 가능성에 분산해서 맞추려 하는 반면, reverse KL은 학생이 감당할 수 있는 특정 행동 하나에 확률을 몰아줍니다. 학생 용량이 교사보다 작을 때 유리하게 작동합니다. 다만 다양성을 희생하는 트레이드오프이기도 해서, Agarwal 등은 어떤 divergence가 나은지는 과제마다 다르다고 언급합니다.
3. **exposure bias 완화**: 학습 중 본 적 없는 상태에 놓였을 때 오류가 누적되는 문제([Bengio 등](https://arxiv.org/abs/1506.03099))가 줄어듭니다. 학생이 만든 상태에서 바로 채점하기 때문입니다.

여기서 중요한 전제가 하나 있습니다. reverse KL 최적화는 학생의 **support**(0이 아닌 확률을 가질 수 있는 토큰의 범위) 밖에 있는 교사 행동을 만들어내지는 못합니다. 그래서 실험들은 전부 이미 어느 정도 도메인 지식을 갖춘, mid-training이나 SFT를 거친 학생에서 시작합니다. SFT(forward KL 방향)로 넓힌 support 안에서, on-policy distillation이 그 지지 범위 안의 확률 분포를 교사에 맞춰 재조정하는 역할을 한다고 보면 됩니다.

### RL 파이프라인의 보상 함수만 바꾸는 구현

구현은 이미 RL 인프라를 갖춘 곳이라면 크게 복잡하지 않습니다.

```text
1. 교사 모델의 sampling client를 준비한다 (로그 확률 계산 가능해야 함)
2. 학생 정책에서 롤아웃을 샘플링한다 (RL과 동일한 절차, 학생 로그 확률도 함께 얻는다)
3. 교사에게 같은 시퀀스에 대한 로그 확률을 요청한다 (compute_logprobs 1회 forward pass)
4. per-token advantage = -reverse_KL(학생, 교사) 로 설정하고
   RL의 importance-sampling loss로 그레디언트를 계산한다
```

별도의 보상 모델이나 레이블링 파이프라인이 필요 없습니다. 이미 KL 정규화 항을 쓰는 RL 구현이 있다면, 그 정규화 대상을 교사 모델로 바꾸는 정도의 변경으로 충분하다는 게 원문의 주장입니다. 또한 부분 시퀀스만으로도 보상을 계산할 수 있어서, 롤아웃이 끝날 때까지 기다릴 필요가 없다는 것도 계산 비용 측면의 장점입니다.

## Qwen3 기술보고서가 보여주는 것

[Qwen3 기술보고서](https://arxiv.org/abs/2505.09388)의 Table 21은 같은 오프폴리시 distillation 체크포인트에서 시작해 RL을 추가한 경우와 on-policy distillation을 추가한 경우를 비교합니다.

| 방법 | AIME'24 | AIME'25 | MATH500 | LiveCodeBench v5 | MMLU-Redux | GPQA-Diamond | GPU 시간 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 오프폴리시 distillation 체크포인트 | 55.0 | 42.8 | 92.4 | 42.0 | 86.4 | 55.6 | 미공개 |
| + RL | 67.6 | 55.5 | 94.8 | 52.9 | 86.9 | 61.3 | 17,920 |
| + on-policy distillation | 74.4 | 65.5 | 97.0 | 60.3 | 88.3 | 63.3 | 1,800 |

같은 출발점에서 on-policy distillation이 RL보다 전 항목에서 높은 점수를, 약 10분의 1의 GPU 시간으로 냈다는 결과입니다. 다만 이건 Qwen3 팀의 특정 학습 세팅 안에서의 같은 보고서 내 비교이지, "distillation이 RL보다 항상 10배 싸다"는 일반 법칙으로 읽을 수치는 아닙니다.

### Thinking Machines의 자체 실험과 외삽

Thinking Machines Lab은 별도로 Qwen3-8B-Base를 학생, Qwen3 계열을 교사로 자체 실험을 진행했습니다. QwQ-32B가 생성한 [OpenThoughts-3](https://arxiv.org/abs/2506.04178) 데이터셋으로 40만 개 프롬프트를 풀파인튜닝(오프폴리시 distillation, mid-training 단계)한 결과 AIME'24 약 60%에 도달했습니다. 이 로그-선형 스케일링 트렌드를 그대로 연장하면 200만 개 프롬프트에서 70%에 도달할 것으로 **추정**됩니다. 이건 실측이 아니라 외삽치이고, 원문도 "스케일링 법칙이 꺾이지 않는다는 가정이 필요해 단순하지 않다"고 스스로 밝히고 있습니다.

이 40만 개짜리 체크포인트에서 시작해 on-policy distillation을 약 150스텝(프롬프트 약 7만 7천 개, 프롬프트당 4샘플) 돌리자 AIME'24가 70%까지 올라갔습니다. 여기서 짚어둘 부분이 있는데, 본문은 교사를 "Qwen3-32B"라고 서술하지만 실험 각주에는 실제로는 Qwen3-8B를 교사로 썼고, 컴퓨트 비교를 위한 FLOPs 계산에만 32B 모델 크기를 사용했다고 밝혀져 있습니다. 실제 사용한 교사와 비용 계산에 쓴 모델 크기가 다르다는 뜻이라 수치를 인용할 때 유의할 지점입니다.

이 실험을 바탕으로 한 컴퓨트 효율 비교는 다음과 같습니다.

| 방법 | AIME'24 | 교사 FLOPs | 학생 FLOPs | SFT-2M 대비 컴퓨트 효율 |
| --- | ---: | ---: | ---: | ---: |
| SFT-400K (초기값) | 60% | 8.5×10²⁰ | 3.8×10²⁰ | – |
| SFT-2M (외삽) | ~70%(추정) | 3.4×10²¹ | 1.5×10²¹ | 1× |
| RL | 68% | – | – | ≈1× |
| On-policy distillation | 70% | 8.4×10¹⁹ | 8.2×10¹⁹ | 9~30× |

9배에서 30배라는 범위는 회계 방식에 따라 갈립니다. SFT용 교사 데이터셋을 "이미 존재하는 것으로 간주"(여러 학습 실행에 걸쳐 상각)하면 교사 FLOPs를 비교에서 빼도 되니 9배가 나오고(GPU 시간 기준으로는 로그 확률 계산이 병렬화하기 쉬워 약 18배로 추정), 새로 오프폴리시 데이터셋을 만드는 비용까지 전부 포함하면 약 30배가 나옵니다. Thinking Machines Lab 스스로도 이 FLOP 비교가 단순하지 않다고 인정합니다. 파라미터 수 기반의 이론적 FLOPs이라 실제 GPU 병렬화 특성을 반영하지 않고, SFT 초기화가 이미 교사 분포의 support 안에 어느 정도 들어 있다는 전제, 교사의 토큰별 로그 확률에 접근 가능해야 한다는 전제, Tinker라는 특정 학습 스택에 의존한다는 전제가 모두 깔려 있습니다. 이 숫자는 Thinking Machines Lab의 특정 실험 조건에서 나온 결과이며, 다른 모델·데이터·인프라 조합에 그대로 적용된다고 볼 근거는 없습니다.

### Discussion의 추가 실험

같은 글의 Discussion 섹션에는 dense supervision의 효율을 더 직접적으로 보여주는 실험이 있습니다. Qwen3-8B-Base(추가 SFT 없이)를 DeepMath 데이터셋에서 LoRA rank 128 RL로 학습시킨 뒤, 그 RL 모델을 교사로 삼아 원래 base 모델에 on-policy distillation을 적용했습니다. distillation이 RL이 도달한 성능에 약 7~10배 적은 그레디언트 스텝으로 도달했고, 더 짧은 롤아웃과 더 작은 배치 크기까지 고려하면 전체 컴퓨트 효율은 50~100배로 추정됐습니다. reverse KL은 10스텝 미만에서 거의 0으로 떨어졌는데, RL은 같은 성능에 70스텝이 필요했습니다.

데이터 재사용 실험도 있습니다. 데이터셋에서 무작위로 고른 프롬프트 단 하나로 20스텝(스텝당 256개 롤아웃)을 학습시켰는데, 오버피팅 없이 교사의 AIME'24 성능에 가까워졌습니다. RL로 같은 프롬프트를 반복 학습하면 흔히 정답을 암기하는 방향으로 흐르는 데 비해, reverse KL 최소화는 교사의 분포 전체를 근사하려 하기 때문에 암기가 덜하다는 해석입니다.

## continual learning에서의 능력 회복

수학 추론과는 별도로, Thinking Machines Lab은 내부 어시스턴트 시나리오로 두 번째 실험을 진행했습니다. 이미 RL로 post-trained된 Qwen3-8B에 내부 문서 QA 지식을 추가로 학습시키면 instruction-following 능력([IF-eval](https://arxiv.org/abs/2311.07911))이 크게 떨어집니다. RL이 원본 네트워크의 작은 서브네트워크만 조정한다는 [선행 연구](https://arxiv.org/abs/2505.11711)를 참고하면, 그 좁은 서브네트워크가 대량의 새 데이터로 덮여버리는 셈입니다.

| 모델 | Internal QA (지식) | IF-eval (채팅) |
| --- | ---: | ---: |
| Qwen3-8B (기준) | 18% | 85% |
| + midtrain (문서 100%) | 43% | 45% |
| + midtrain (문서 70%) | 36% | 79% |
| + midtrain (70%) + on-policy distillation | 41% | 83% |

문서와 채팅 데이터 비율을 아무리 조절해도 IF-eval을 원래 수준으로 유지하는 조합은 찾지 못했다고 합니다. 대신 문서를 섞기 **전의** Qwen3-8B를 교사로 삼아, [Tulu 3](https://arxiv.org/abs/2411.15124) 프롬프트에 대해 on-policy distillation을 돌리자 지식은 거의 잃지 않은 채로 IF-eval이 83%까지 회복됐습니다. 내부 문서와는 무관한 프롬프트로 채팅 능력만 복원한 결과입니다.

이 실험이 흥미로운 건, "이전 버전의 자기 자신"을 교사로 쓸 수 있다는 점입니다. 파인튜닝으로 잃은 능력을 이전 체크포인트에서 다시 불러오는 방식이라, continual learning에 쓸 수 있는 도구로 제시됩니다. 다만 이건 행동을 복원하는 것이고, 문서에 있던 새로운 지식 자체를 가르치는 건 여전히 mid-training이나 SFT의 몫입니다. on-policy distillation은 사전학습을 대체하지 않고, 새로운 지식 습득의 지름길도 아니며, RL이 하는 탐색(exploration)을 대신하지도 않습니다. 좋은 전략을 이미 찾은 뒤에 그 전략을 값싸게 복제하는 역할에 가깝습니다.

같은 글은 이 관찰을 조금 더 밀어붙여서, Qwen3-32B에서 재샘플링한 자기 자신의 출력으로 SFT를 돌려도(이론상 교사와 KL=0인 데이터인데도) IF-eval이 계속 악화된다는 실험을 보여줍니다. 유한한 배치가 언제나 미세하게 편향된 그레디언트를 만들어내기 때문이라는 해석입니다. 반면 on-policy distillation은 교사가 고정돼 있어서 이 표류가 생기지 않는다고 설명합니다. 이건 저자들의 해석이고, 다른 데이터·모델 조합에서도 같은 정도로 나타나는지는 이 실험만으로 확정할 수 없습니다.

## 2026년 기준 재현 조건

on-policy distillation을 그대로 재현하려면 교사 모델의 **토큰별 로그 확률**에 접근해야 합니다. 텍스트만 반환하는 일반적인 블랙박스 API로는 부족합니다. `compute_logprobs` 같은 기능을 제공하는 오픈 웨이트 모델이거나, 그런 엔드포인트를 노출하는 서비스가 필요합니다.

여기서 재현성 문제가 하나 생깁니다. 원문이 대표 구성으로 제시한 Qwen3-8B-Base 학생과 Qwen3-32B 교사 endpoint는 2026년 6월 12일 Tinker 모델 라인업에서 [은퇴](https://tinker-docs.thinkingmachines.ai/tinker/model-deprecations/)했습니다. 앞서 짚었듯 자체 수학 실험은 실제로 Qwen3-8B 교사를 썼다는 각주가 있으므로, 대표 구성의 은퇴 안내와 실제 run을 구분해서 읽어야 합니다. [Tinker cookbook의 증류 레시피](https://github.com/thinking-machines-lab/tinker-cookbook/tree/main/tinker_cookbook/recipes/distillation)는 현재 학생 Qwen3.5-9B-Base, 교사 Qwen3.5-9B 조합으로 갱신돼 있고, README에는 rank-128 LoRA SFT 후 약 65%, 이후 200스텝의 on-policy distillation 후 약 76.7%의 AIME'24 수치가 실려 있습니다. 이 수치는 레시피 저자들이 보고한 값이며, 이 글을 준비하면서 별도로 재현하거나 재측정하지는 않았습니다.

## 정리

on-policy distillation은 RL의 온폴리시 샘플링과 distillation의 조밀한 토큰별 신호를 합친 방법입니다. 이미 mid-training이나 SFT로 어느 정도 능력을 갖춘 학생을 더 적은 컴퓨트로 특정 교사 행동에 정렬시키는 데 유효하다는 근거를 Qwen3 기술보고서와 Thinking Machines Lab의 자체 실험이 함께 보여줍니다. 다만 그 근거의 대부분은 수학 추론 벤치마크에 한정돼 있고, 컴퓨트 효율 수치는 회계 방식에 따라 크게 달라지며, 재현하려면 교사의 로그 확률에 접근할 수 있어야 합니다. 새로운 지식을 가르치는 일, 좋은 전략을 처음 찾아내는 탐색 과정은 여전히 이 방법의 범위 밖에 있습니다.

## 함께 보면 좋을 자료

- [LoRA Without Regret](https://thinkingmachines.ai/blog/lora/): Thinking Machines Lab, RL의 정보이론적 비용을 다룬 앞선 글
- [Defeating Nondeterminism in LLM Inference](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/): Thinking Machines Lab, 진짜 on-policy 데이터의 조건을 다룬 앞선 글
- [RL's Razor: Why Online Reinforcement Learning Forgets Less](https://arxiv.org/abs/2509.04259): Shenfeld 등, on-policy 학습과 forgetting의 관계
- [A Survey of On-Policy Distillation for Large Language Models](https://arxiv.org/abs/2604.00626): 이 방법을 다룬 후속 서베이 논문

## 참고 자료

- [On-Policy Distillation](https://thinkingmachines.ai/blog/on-policy-distillation/): Kevin Lu, Thinking Machines Lab, 2025-10-27, 조회일 2026-07-10
- [Qwen3 Technical Report](https://arxiv.org/abs/2505.09388): Qwen Team, arXiv:2505.09388, 조회일 2026-07-10
- [On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes](https://arxiv.org/abs/2306.13649): Agarwal 등, arXiv:2306.13649 (ICLR 2024), 조회일 2026-07-10
- [MiniLLM: Knowledge Distillation of Large Language Models](https://arxiv.org/abs/2306.08543): Gu 등, arXiv:2306.08543 (ICLR 2024), 조회일 2026-07-10
- [tinker-cookbook distillation recipes](https://github.com/thinking-machines-lab/tinker-cookbook/tree/main/tinker_cookbook/recipes/distillation): Thinking Machines Lab, GitHub, 조회일 2026-07-10
- [Tinker model deprecations](https://tinker-docs.thinkingmachines.ai/tinker/model-deprecations/): Thinking Machines Lab, 조회일 2026-07-10
