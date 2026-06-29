---
title: "Robot Learning: A Tutorial (고전 로보틱스에서 VLA까지)"
meta_title: "Robot Learning: A Tutorial 리뷰 (arXiv:2510.12403)"
description: "Francesco Capuano 외 저자들이 Hugging Face LeRobot과 함께 공개한 로봇 학습 튜토리얼 논문. 고전 로보틱스부터 ACT, Diffusion Policy, pi0, SmolVLA까지 전체 흐름을 정리합니다."
date: 2026-06-30T10:00:00+09:00
lastmod: 2026-06-30T10:00:00+09:00
image: ""
categories: ["Physical AI"]
tags: ["lerobot", "robot-learning", "imitation-learning", "diffusion-policy", "act", "vla", "smolvla"]
author: "hakhub"
translationKey: "lerobot-robot-learning-tutorial"
draft: true
---

"Robot Learning: A Tutorial"([arXiv:2510.12403](https://arxiv.org/abs/2510.12403))은 Francesco Capuano, Caroline Pascal, Adil Zouitine, Thomas Wolf, Michel Aractingi가 작성한 논문 형식의 튜토리얼이다. University of Oxford와 Hugging Face 소속 저자들이 LeRobot 라이브러리를 기반으로 고전 로보틱스부터 강화학습, 모방 학습, Vision-Language-Action 모델까지 로봇 학습 전반을 한 편에 담았다.

논문은 Hugging Face Space([lerobot/robot-learning-tutorial](https://huggingface.co/spaces/lerobot/robot-learning-tutorial))에서 인터랙티브 웹 버전으로도 볼 수 있으며, 챕터마다 실행 가능한 코드 예제가 포함된다.

## 튜토리얼 구성

튜토리얼은 7개 챕터로 구성된다.

1. **Foreword**: 현대 ML이 자율 로봇 개발에 중요해졌지만, 고전 로보틱스 지식도 여전히 필요하다는 관점 제시
2. **Introduction / LeRobotDataset**: LeRobot 라이브러리와 표준화된 로봇 학습 데이터 포맷 소개
3. **Classical Robotics**: FK/IK, 모션 계획, 피드백 루프, 동역학 기반 접근의 한계
4. **Robot Reinforcement Learning**: MDP 기반 로봇 RL, HIL-SERL, 실제 환경 RL의 난점
5. **Robot Imitation Learning**: Behavioral Cloning, VAE, Diffusion Models, Flow Matching, ACT, Diffusion Policy, 비동기 추론
6. **Generalist Robot Policies**: VLA, VLM 백본, pi0, SmolVLA, Open X-Embodiment, DROID
7. **Conclusions**: 모델 기반에서 데이터 기반으로의 전환, 오픈 데이터셋과 표준화의 중요성

## LeRobotDataset

LeRobot은 Hugging Face가 개발한 오픈소스 end-to-end 로봇 학습 라이브러리다. 실제 로봇 하드웨어의 저수준 제어, 데이터와 추론 최적화, PyTorch 기반 SOTA 알고리즘 구현을 수직 통합한다.

`LeRobotDataset`은 로봇 학습 연구를 위한 표준화된 데이터셋 포맷이다.

| 구성 | 역할 |
|---|---|
| Tabular data | joint state, action 등 저차원 고주파 데이터 (Parquet 기반) |
| Visual data | 카메라 프레임을 MP4로 묶어 저장, episode/camera/chunk 기준 조직 |
| Metadata | JSON 스키마, fps, normalization stats, episode 경계, task 레이블 |

`delta_timestamps` 기반 히스토리와 미래 action window 개념을 지원하며, 대규모 HF 호스팅 데이터셋에 스트리밍 접근도 가능하다. SO-100, ALOHA-2, 휴머노이드, 시뮬레이션, 자율주행 데이터셋 등 다양한 플랫폼을 지원한다.

## 고전 로보틱스와 그 한계

튜토리얼은 로봇 모션을 manipulation(조작), locomotion(이동), mobile manipulation(이동과 조작의 결합)으로 구분한다. 고전 방법론은 FK/IK, 모션 계획, 제어 이론, 피드백 루프에 기반한다.

이 접근의 한계는 명확하다. 환경 제약, 접촉 동역학, 장애물, 실시간 변화가 복잡해질수록 engineering overhead가 급격히 커진다. 튜토리얼은 학습 기반 접근이 task와 embodiment 간 일반화, 전문 지식 의존도 감소, 과거 데이터 활용 측면에서 강점이 있다고 설명한다.

## 로봇 강화학습

RL은 로봇 문제를 MDP(Markov Decision Process)로 모델링한다. 상태, 행동, 동역학, 보상, 할인율, 초기 상태 분포를 통해 정책을 학습한다. 연속 제어 알고리즘으로는 TRPO, PPO, SAC, TD-MPC가 LeRobot 맥락에서 언급된다.

실제 로봇 RL에는 여러 난점이 있다.

- sample inefficiency (샘플 비효율)
- 안전하지 않은 탐색 (exploration risk)
- 하드웨어 리셋 비용
- 보상 설계의 어려움
- 시뮬레이터와 실제 환경 사이의 gap

**HIL-SERL**(Human-in-the-Loop Sample-Efficient Real-World RL)은 사람의 개입, 사전 데이터, 샘플 효율적 RL을 결합해 이 문제의 일부를 완화하는 접근으로 소개된다.

## 로봇 모방 학습

모방 학습의 핵심은 보상 설계 없이 전문가 시연(observation-action pair)으로부터 정책을 학습하는 것이다. 단순 point-wise 정책은 covariate shift와 multimodal demonstration에 취약하다. 튜토리얼은 이를 극복하기 위해 생성 모델 기반 접근의 필요성을 설명한다.

### Behavioral Cloning

전문가 시연의 observation-action 매핑을 지도 학습으로 배운다. 구현이 단순하고 시작점으로 쓸 수 있지만, 학습 분포 밖 상태에서 오류가 누적된다.

### ACT (Action Chunking with Transformers)

단일 행동 대신 짧은 행동 시퀀스(chunk)를 예측한다. VAE로 행동 궤적의 불확실성을 잠재 변수로 표현하고, 트랜스포머 디코더가 시각 관측에서 다음 chunk를 생성한다. chunk 단위 예측은 매 제어 스텝마다 모델을 호출하지 않아도 되므로 compounding error를 완화한다.

### Diffusion Policy

행동 분포를 denoising 방식으로 모델링한다. 같은 상황에서 여러 합리적인 행동이 존재하는 multimodal 케이스를 point-wise 정책보다 자연스럽게 처리한다. 대신 multi-step denoising으로 인해 실시간 제어 루프에 적용하려면 지연 문제를 고려해야 한다.

### Flow Matching

연속 행동 생성과 VLA 계열 모델에서 중요해지는 생성 모델링 방식이다. pi0 같은 최신 VLA에서 활용된다.

### 비동기 추론 (Async Inference)

action planning과 action execution을 분리해 런타임 지연을 줄이는 구조다. 생성 모델 기반 정책을 저지연 제어 루프에서 현실적으로 배포하기 위한 방법으로 소개된다.

## Generalist Robot Policies

튜토리얼은 로봇 학습이 CV/NLP처럼 사전학습 후 미세조정(pre-train-and-adapt) 패러다임으로 이동하고 있다고 설명한다. 로봇 데이터는 embodiment, task, 환경에 강하게 종속되고 이질적(heterogeneous)이어서 단순 혼합이 오히려 성능을 낮출 수 있다.

대규모 공개 데이터 프로젝트들이 이 문제를 공동으로 풀어가고 있다.

| 데이터셋 | 규모 |
|---|---|
| Open X-Embodiment | 22개 embodiment, 21개 기관, 60개 데이터셋, 1.4M trajectories |
| DROID | 75,000건 이상의 in-the-wild human demonstrations |
| RT-1 | 130k human-recorded trajectories, 13 robots, 17 months |

**pi0**는 Gemma/PaliGemma 계열 VLM 백본에 action expert와 Flow Matching을 결합한 모델로, 10M 이상의 trajectories로 학습한 것으로 소개된다. language-conditioned, cross-task, cross-embodiment 정책의 대표 사례로 다뤄진다.

**SmolVLA**는 작고 효율적인 VLA로, LeRobot 예제에서 비동기 추론을 지원한다. 관련 Hugging Face 모델로는 `fracapuano/smolvla_async`, `lerobot/smolvla_base`가 있다.

튜토리얼은 BC-Zero, RT-1, RT-2, OpenVLA를 거쳐 pi0, SmolVLA에 이르는 흐름을 타임라인으로 정리하며, 더 큰 데이터셋과 더 표현력 있는 아키텍처를 향한 방향성을 설명한다.

## 결론

튜토리얼의 핵심 메시지는 명확하다. 로봇 학습은 dynamics 기반 모델에서 데이터 기반 정책 학습으로 이동하고 있다. RL은 강력하지만 실제 환경에서 샘플 비효율과 보상 설계 문제 때문에 어렵다. BC에 ACT 또는 Diffusion Policy를 결합하는 방식이 단일 태스크 모방 학습의 현실적인 기준점이다. pi0, SmolVLA 같은 generalist VLA 정책이 현재 프론티어이며, 오픈 데이터셋과 표준화된 라이브러리가 접근성 확대의 핵심이다.

## 함께 보면 좋을 자료

- [arXiv:2510.12403](https://arxiv.org/abs/2510.12403): Robot Learning: A Tutorial 원논문 (Capuano et al.)
- [LeRobot 인터랙티브 튜토리얼](https://huggingface.co/spaces/lerobot/robot-learning-tutorial): Hugging Face Space, 챕터별 실행 가능 코드
- [huggingface/lerobot](https://github.com/huggingface/lerobot): Hugging Face LeRobot 라이브러리 GitHub
- [Open X-Embodiment](https://robotics-transformer-x.github.io/): 크로스 embodiment 로봇 대규모 공개 데이터셋

## 참고 자료

- Francesco Capuano, Caroline Pascal, Adil Zouitine, Thomas Wolf, Michel Aractingi, "Robot Learning: A Tutorial," [arXiv:2510.12403](https://arxiv.org/abs/2510.12403), DOI: [10.48550/arXiv.2510.12403](https://doi.org/10.48550/arXiv.2510.12403)
- Hugging Face Space: [lerobot/robot-learning-tutorial](https://huggingface.co/spaces/lerobot/robot-learning-tutorial) (인터랙티브 버전)
- [huggingface/lerobot](https://github.com/huggingface/lerobot): GitHub 저장소
- [Open X-Embodiment](https://robotics-transformer-x.github.io/): 크로스 embodiment 로봇 데이터셋
