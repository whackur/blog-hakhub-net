---
title: "Robot Learning: A Tutorial (고전 로보틱스에서 VLA까지)"
meta_title: "Robot Learning: A Tutorial 리뷰 (arXiv:2510.12403)"
description: "Francesco Capuano 외 저자들이 Hugging Face LeRobot과 함께 공개한 로봇 학습 튜토리얼 논문. 고전 로보틱스부터 ACT, Diffusion Policy, pi0, SmolVLA까지 전체 흐름을 정리합니다."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
image: ""
categories: ["AI"]
tags: ["lerobot", "robot-learning", "imitation-learning", "diffusion-policy", "act", "vla", "smolvla", "physical-ai"]
author: "whackur"
translationKey: "lerobot-robot-learning-tutorial"
draft: false
---

"Robot Learning: A Tutorial"([arXiv:2510.12403](https://arxiv.org/abs/2510.12403))은 Francesco Capuano, Caroline Pascal, Adil Zouitine, Thomas Wolf, Michel Aractingi가 쓴 논문 형식의 튜토리얼입니다. University of Oxford와 Hugging Face 소속 저자들이 LeRobot 라이브러리를 바탕으로 고전 로보틱스부터 강화학습, 모방 학습, Vision-Language-Action(VLA) 모델까지 로봇 학습의 전체 흐름을 한 편에 담았습니다.

로봇 학습은 진입 장벽이 높은 분야입니다. 제어 이론, 강화학습, 생성 모델, 대규모 사전학습이 한 문제 안에 얽혀 있고, 논문마다 전제하는 배경지식이 다릅니다. 이 튜토리얼의 가치는 그 조각들을 하나의 서사로 잇고, 단계마다 LeRobot으로 바로 실행할 수 있는 코드를 붙여 놓았다는 데 있습니다. Hugging Face Space([lerobot/robot-learning-tutorial](https://huggingface.co/spaces/lerobot/robot-learning-tutorial))에서 인터랙티브 웹 버전으로도 볼 수 있습니다.

## 튜토리얼 구성

튜토리얼은 7개 챕터로 구성됩니다.

1. **Foreword**: 현대 ML이 자율 로봇 개발에 중요해졌지만, 고전 로보틱스 지식도 여전히 필요하다는 관점 제시
2. **Introduction / LeRobotDataset**: LeRobot 라이브러리와 표준화된 로봇 학습 데이터 포맷 소개
3. **Classical Robotics**: FK/IK, 모션 계획, 피드백 루프, 동역학 기반 접근의 한계
4. **Robot Reinforcement Learning**: MDP 기반 로봇 RL, HIL-SERL, 실제 환경 RL의 난점
5. **Robot Imitation Learning**: Behavioral Cloning, VAE, Diffusion Models, Flow Matching, ACT, Diffusion Policy, 비동기 추론
6. **Generalist Robot Policies**: VLA, VLM 백본, pi0, SmolVLA, Open X-Embodiment, DROID
7. **Conclusions**: 모델 기반에서 데이터 기반으로의 전환, 오픈 데이터셋과 표준화의 중요성

## LeRobotDataset

LeRobot은 Hugging Face가 개발한 오픈소스 end-to-end 로봇 학습 라이브러리입니다. 실제 로봇 하드웨어의 저수준 제어, 데이터 로딩과 추론 최적화, PyTorch 기반 SOTA 알고리즘 구현까지 수직으로 통합합니다.

`LeRobotDataset`은 이 라이브러리의 표준 데이터셋 포맷입니다. 로봇 데이터는 카메라 프레임, 관절 상태, 행동이 서로 다른 주기로 뒤섞인 시계열이라, 연구실마다 제각각인 저장 방식이 재현과 비교를 막는 고질적인 문제였습니다. LeRobotDataset은 이를 세 층으로 나눠 정리합니다.

| 구성 | 역할 |
|---|---|
| Tabular data | joint state, action 등 저차원 고주파 데이터 (Parquet 기반) |
| Visual data | 카메라 프레임을 MP4로 묶어 저장, episode/camera/chunk 기준 조직 |
| Metadata | JSON 스키마, fps, normalization stats, episode 경계, task 레이블 |

`delta_timestamps`로 과거 관측 히스토리와 미래 action window를 선언적으로 지정할 수 있고, Hugging Face 허브에 호스팅된 대규모 데이터셋에는 전체를 내려받지 않고 스트리밍으로 접근할 수 있습니다. SO-100, ALOHA-2 같은 저가 플랫폼부터 휴머노이드, 시뮬레이션, 자율주행 데이터셋까지 지원합니다.

## 고전 로보틱스와 그 한계

튜토리얼은 로봇 모션을 manipulation(조작), locomotion(이동), mobile manipulation(둘의 결합)으로 구분합니다. 고전 방법론은 FK/IK, 모션 계획, 제어 이론, 피드백 루프로 문제를 풉니다. 로봇과 환경의 동역학을 수식으로 명시하고, 그 모델 위에서 궤적을 계산하는 방식입니다.

이 접근은 모델이 정확한 동안에는 정밀하고 예측 가능하게 동작합니다. 문제는 접촉이 많은 조작 task입니다. 물체를 쥐고 밀고 끼우는 순간마다 접촉 동역학이 달라지고, 장애물과 실시간 환경 변화까지 더해지면 명시적으로 모델링해야 할 항이 감당하기 어렵게 늘어납니다. 튜토리얼은 이 지점을 engineering overhead의 폭발로 설명합니다. 학습 기반 접근의 강점은 task와 embodiment를 넘나드는 일반화, 도메인 전문 지식 의존도 감소, 이미 쌓인 시연 데이터의 재활용입니다. 다만 서문에서 못 박듯이 고전 로보틱스가 쓸모없어졌다는 이야기는 아닙니다. 학습된 정책도 결국 고전적인 저수준 제어 위에서 실행됩니다.

## 로봇 강화학습

RL은 로봇 문제를 MDP(Markov Decision Process)로 모델링합니다. 상태, 행동, 동역학, 보상, 할인율, 초기 상태 분포를 정의하고 기대 보상을 최대화하는 정책을 학습합니다. 연속 제어 알고리즘으로는 TRPO, PPO, SAC, TD-MPC가 LeRobot 맥락에서 언급됩니다.

시뮬레이터에서 잘 되던 RL이 실제 로봇 앞에서 자주 막히는 이유를 튜토리얼은 이렇게 정리합니다.

- **샘플 비효율**: 시행착오가 수십만 스텝 단위로 필요한데, 실물 로봇은 그만큼 돌리면 마모되고 고장 납니다.
- **위험한 탐색**: 학습 초기의 무작위에 가까운 행동이 로봇 자신이나 주변 환경을 부술 수 있습니다.
- **리셋 비용**: 에피소드가 끝날 때마다 사람이 물체와 환경을 원위치로 되돌려야 합니다.
- **보상 설계**: "물체를 잘 집었다"를 센서 신호만으로 정의하기 어렵습니다.
- **sim-to-real gap**: 시뮬레이터 물리와 실제 물리의 차이가 학습된 정책을 무너뜨립니다.

**HIL-SERL**(Human-in-the-Loop Sample-Efficient Real-World RL)은 이 난점을 정면으로 다루는 접근으로 소개됩니다. 사전 시연 데이터로 출발점을 만들고, 온라인 학습 중에 사람이 개입해 위험한 탐색을 교정하며, 샘플 효율이 높은 RL로 실물 학습 시간을 실용적인 범위까지 끌어내립니다.

## 로봇 모방 학습

모방 학습은 보상 설계 없이 전문가 시연(observation-action pair)에서 정책을 배웁니다. RL의 탐색 위험을 피할 수 있지만, 두 가지 약점이 따라옵니다.

첫째는 covariate shift입니다. 정책의 작은 오차가 로봇을 시연 데이터에 없던 상태로 밀어 넣고, 그 낯선 상태에서는 더 큰 오차가 나오는 악순환이 생깁니다. 둘째는 multimodal demonstration입니다. 같은 상황에서 어떤 시연자는 장애물을 왼쪽으로, 어떤 시연자는 오른쪽으로 피해 갑니다. 이를 point-wise 정책으로 평균 내면 장애물 한가운데로 향하는, 물리적으로 성립하지 않는 행동이 나옵니다. 튜토리얼이 생성 모델 기반 정책을 강조하는 이유가 여기 있습니다. 행동의 평균이 아니라 행동의 분포를 배워야 하기 때문입니다.

### Behavioral Cloning

전문가 시연의 observation-action 매핑을 지도 학습으로 배웁니다. 구현이 단순해서 출발점으로 좋지만, 위의 두 약점을 그대로 안고 갑니다. 시연 품질이 곧 성능의 상한이기도 합니다.

### ACT (Action Chunking with Transformers)

단일 행동 대신 짧은 행동 시퀀스(chunk)를 예측합니다. VAE가 행동 궤적의 변동성을 잠재 변수로 흡수하고, 트랜스포머 디코더가 시각 관측에서 다음 chunk를 생성합니다. chunk 단위로 예측하면 제어 스텝마다 모델을 호출하지 않아도 되고, 호출 횟수가 줄어드는 만큼 오차가 누적될 기회도 줄어듭니다. compounding error를 완화하는 구조적 장치입니다.

### Diffusion Policy

행동 분포를 denoising 과정으로 모델링합니다. 같은 상황에 여러 타당한 행동이 존재하는 multimodal 케이스를 point-wise 정책보다 자연스럽게 처리합니다. 대가는 지연 시간입니다. multi-step denoising을 거쳐야 행동이 나오기 때문에, 실시간 제어 루프에 넣으려면 추론 지연을 따로 해결해야 합니다.

### Flow Matching

연속 행동 생성에 쓰이는 생성 모델링 기법으로, VLA 계열 모델에서 비중이 커지고 있습니다. pi0 같은 최신 VLA가 채택한 방식입니다.

### 비동기 추론 (Async Inference)

action planning과 action execution을 분리합니다. 로봇이 현재 chunk를 실행하는 동안 정책이 다음 chunk를 계산하는 구조라서, 추론이 무거운 생성 모델 기반 정책을 저지연 제어 루프에 배포할 때 현실적인 해법이 됩니다.

## Generalist Robot Policies

로봇 학습도 CV/NLP처럼 사전학습 후 미세조정(pre-train-and-adapt) 패러다임으로 이동하고 있다는 것이 튜토리얼의 진단입니다. 걸림돌은 데이터의 이질성입니다. 텍스트와 달리 로봇 데이터는 embodiment, task, 환경에 강하게 종속됩니다. 관절 구성이 다른 로봇의 데이터를 그대로 섞으면 오히려 성능이 떨어지는 negative transfer가 일어날 수 있습니다.

대규모 공개 데이터 프로젝트들이 이 문제를 공동으로 풀어가고 있습니다.

| 데이터셋 | 규모 |
|---|---|
| Open X-Embodiment | 22개 embodiment, 21개 기관, 60개 데이터셋, 1.4M trajectories |
| DROID | 75,000건 이상의 in-the-wild human demonstrations |
| RT-1 | 130k human-recorded trajectories, 13 robots, 17 months |

**pi0**는 Gemma/PaliGemma 계열 VLM 백본에 action expert와 Flow Matching을 결합한 모델입니다. 10M 이상의 trajectory로 학습했다고 소개되며, language-conditioned, cross-task, cross-embodiment 정책의 대표 사례로 다뤄집니다.

**SmolVLA**는 작고 효율적인 VLA로, LeRobot 예제에서 비동기 추론을 지원합니다. 관련 Hugging Face 모델로는 `fracapuano/smolvla_async`와 `lerobot/smolvla_base`가 있습니다.

튜토리얼은 BC-Zero에서 RT-1, RT-2, OpenVLA를 거쳐 pi0, SmolVLA에 이르는 흐름을 타임라인으로 정리하며, 더 큰 데이터셋과 더 표현력 있는 아키텍처라는 방향성을 짚습니다.

## 정리

로봇 학습을 시작하는 입장에서 튜토리얼의 결론은 실용적인 선택 지침으로 읽힙니다. 단일 task 모방 학습이라면 BC에 ACT나 Diffusion Policy를 결합하는 구성이 현실적인 기준점입니다. 실물 환경에서 RL을 돌려야 한다면 HIL-SERL처럼 사람 개입과 사전 데이터를 끼워 넣는 설계가 사실상 전제 조건입니다. 여러 task와 로봇을 아우르는 일반화가 목표라면 pi0, SmolVLA 같은 generalist VLA를 미세조정하는 경로가 현재 프론티어입니다. 그리고 어느 경로를 택하든, LeRobotDataset 같은 표준 포맷과 오픈 데이터셋이 진입 비용을 낮추는 기반이라는 것이 저자들의 일관된 메시지입니다.

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
