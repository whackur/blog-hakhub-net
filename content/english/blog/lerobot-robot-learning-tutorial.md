---
title: "Robot Learning: A Tutorial (From Classical Robotics to Generalist Policies)"
meta_title: "Robot Learning: A Tutorial (arXiv:2510.12403)"
description: "A summary of the LeRobot tutorial paper by Capuano et al., covering the full arc from classical robotics through reinforcement learning, ACT, Diffusion Policy, and generalist VLA models including pi0 and SmolVLA."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-06-30T02:00:00+09:00
image: ""
categories: ["AI"]
tags: ["lerobot", "robot-learning", "imitation-learning", "diffusion-policy", "act", "vla", "smolvla", "physical-ai"]
author: "whackur"
translationKey: "lerobot-robot-learning-tutorial"
draft: false
---

"Robot Learning: A Tutorial" ([arXiv:2510.12403](https://arxiv.org/abs/2510.12403)) is a paper-length tutorial by Francesco Capuano, Caroline Pascal, Adil Zouitine, Thomas Wolf, and Michel Aractingi, from the University of Oxford and Hugging Face. It covers the full arc of robot learning methods, from classical dynamics-based control through reinforcement learning, imitation learning, and generalist vision-language-action models, using the Hugging Face LeRobot library throughout.

An interactive version is hosted on Hugging Face Space at [lerobot/robot-learning-tutorial](https://huggingface.co/spaces/lerobot/robot-learning-tutorial), with runnable code examples embedded in each chapter.

## Tutorial structure

The tutorial is organized into seven chapters.

1. **Foreword**: modern ML is important for autonomous robots, but classical robotics knowledge is not obsolete
2. **Introduction / LeRobotDataset**: the LeRobot library and its standardized dataset format for robot learning research
3. **Classical Robotics**: FK/IK, motion planning, feedback loops, and the limits of dynamics-based methods
4. **Robot Reinforcement Learning**: MDP formulation, HIL-SERL, simulator issues, and reward design challenges
5. **Robot Imitation Learning**: Behavioral Cloning, VAE, Diffusion Models, Flow Matching, ACT, Diffusion Policy, async inference
6. **Generalist Robot Policies**: VLA models, VLM backbones, pi0, SmolVLA, Open X-Embodiment, DROID
7. **Conclusions**: the shift from model-based to data-driven robotics, and the role of open datasets

## LeRobotDataset

LeRobot is an open-source, end-to-end robotics library from Hugging Face. It vertically integrates low-level real robot control, data and inference optimizations, and state-of-the-art robot learning methods in PyTorch.

`LeRobotDataset` is the standardized dataset format the tutorial builds on. It has three main components.

| Component | Role |
|---|---|
| Tabular data | joint states and actions as low-dimensional, high-frequency data via Parquet |
| Visual data | camera frames stored as concatenated MP4, organized by episode, camera, and chunk |
| Metadata | JSON schema, fps, normalization stats, episode boundaries, task labels |

The format supports `delta_timestamps`-based history and future action windows, and streaming access for large HF-hosted datasets. Supported platforms include SO-100, ALOHA-2, humanoid arms, simulation datasets, and self-driving car datasets.

## Classical robotics and its limits

The tutorial distinguishes three robot motion categories: manipulation, locomotion, and mobile manipulation. Classical methods rely on FK/IK, motion planning, control theory, and feedback loops.

The stated limitations are that dynamics-based methods become brittle and engineering-heavy as environment constraints, contact dynamics, obstacles, and real-time changes grow complex. Learning-based approaches offer advantages in generalization across tasks and embodiments, reduced dependence on domain expertise, and the ability to learn from historical trajectory data.

## Robot reinforcement learning

RL frames robotics as a Markov Decision Process with states, actions, dynamics, rewards, discount, and initial state distribution. The tutorial covers continuous-control approaches including TRPO, PPO, SAC, and TD-MPC, all of which appear in the LeRobot context.

Real-world robot RL challenges are addressed directly.

- Sample inefficiency
- Unsafe exploration
- Hardware reset costs
- Reward design difficulty
- Simulator-to-real gap

**HIL-SERL** (Human-in-the-Loop Sample-Efficient Real-World RL) is presented as an approach that partially addresses these by combining human guidance, prior demonstration data, and sample-efficient RL.

## Robot imitation learning

Behavioral Cloning learns from expert demonstration trajectories, mapping observations to actions without reward design or online exploration. It avoids the risks of RL but suffers from distribution shift and cannot exceed demonstration quality. The tutorial explains why point-wise policies fail on multimodal demonstrations and motivates generative model-based approaches.

### ACT (Action Chunking with Transformers)

ACT predicts short sequences of actions (chunks) rather than single-step actions. A VAE encodes action trajectory uncertainty into a latent variable; a transformer decoder predicts the next chunk from visual observations. Chunk-level prediction reduces per-step inference calls and mitigates compounding errors.

### Diffusion Policy

Diffusion Policy models the action distribution via denoising. It handles multimodal action distributions naturally, where a single-mode BC prediction would produce a physically incoherent average. The tradeoff is that multi-step denoising adds latency to the control loop.

### Flow Matching

Flow Matching is a generative modeling approach used for continuous action generation. It is relevant to the VLA-family models discussed later, notably pi0.

### Async inference

Async inference decouples action planning from action execution. It is presented as a practical method for deploying generative-model-based policies in latency-sensitive control loops.

## Generalist robot policies

The tutorial frames the current direction of robot learning as a move toward the pre-train-and-adapt paradigm that transformed NLP and computer vision. The challenge specific to robotics: data is strongly tied to embodiment, task, and environment, and naive mixing across sources can cause negative transfer.

Key large-scale data efforts discussed in the tutorial:

| Dataset | Scale |
|---|---|
| Open X-Embodiment | 60 datasets, 22 embodiments, 21 institutions, 1.4M trajectories |
| DROID | 75,000+ in-the-wild human demonstrations |
| RT-1 | 130k human-recorded trajectories, 13 robots, 17 months |

**pi0** uses a Gemma/PaliGemma-class VLM backbone combined with an action expert and Flow Matching. The tutorial describes it as trained on over 10M trajectories and positions it as a leading candidate for language-conditioned, cross-task, cross-embodiment robot policies.

**SmolVLA** is a smaller, more efficient VLA with async inference support in LeRobot examples. Related Hugging Face models include `fracapuano/smolvla_async` and `lerobot/smolvla_base`.

The tutorial traces the development timeline from BC-Zero through RT-1, RT-2, OpenVLA, to pi0 and SmolVLA, situating each model in the broader trend toward larger datasets and more expressive architectures.

## Conclusions

The tutorial's framing is direct: robot learning is shifting from dynamics-based engineering toward data-driven policy learning. RL is powerful but difficult in real-world settings because of sample inefficiency and reward design. BC combined with ACT or Diffusion Policy is the practical baseline for single-task imitation learning. Generalist VLA policies like pi0 and SmolVLA represent the current frontier. Openness, large public datasets, and standardized libraries like LeRobot are what make that frontier accessible.

## Further reading

- [arXiv:2510.12403](https://arxiv.org/abs/2510.12403): "Robot Learning: A Tutorial", Capuano et al., full paper
- [LeRobot interactive tutorial](https://huggingface.co/spaces/lerobot/robot-learning-tutorial): Hugging Face Space with runnable chapter examples
- [huggingface/lerobot](https://github.com/huggingface/lerobot): LeRobot library, GitHub
- [Open X-Embodiment](https://robotics-transformer-x.github.io/): large-scale cross-embodiment robot dataset collection

## References

- Francesco Capuano, Caroline Pascal, Adil Zouitine, Thomas Wolf, Michel Aractingi, "Robot Learning: A Tutorial," [arXiv:2510.12403](https://arxiv.org/abs/2510.12403), DOI: [10.48550/arXiv.2510.12403](https://doi.org/10.48550/arXiv.2510.12403)
- Hugging Face Space: [lerobot/robot-learning-tutorial](https://huggingface.co/spaces/lerobot/robot-learning-tutorial) (interactive version)
- [huggingface/lerobot](https://github.com/huggingface/lerobot): GitHub repository
- [Open X-Embodiment](https://robotics-transformer-x.github.io/): cross-embodiment robotics dataset
