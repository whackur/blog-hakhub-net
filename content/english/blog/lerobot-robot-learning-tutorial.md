---
title: "Robot Learning: A Tutorial (From Classical Robotics to Generalist Policies)"
meta_title: "Robot Learning: A Tutorial (arXiv:2510.12403)"
description: "Connect demonstration collection, ACT training, and physical evaluation with LeRobot, including control, imitation and reinforcement learning, VLAs, action chunks, data distributions, and safety conditions."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-10-16T01:03:42+09:00
image: "/images/posts/lerobot-robot-learning-tutorial/robot-learning-editorial-20261016.webp"
categories: ["AI"]
tags: ["lerobot", "robot-learning", "imitation-learning", "diffusion-policy", "act", "vla", "smolvla", "physical-ai"]
author: "whackur"
translationKey: "lerobot-robot-learning-tutorial"
draft: false
---

A practical way to start robot learning is to teleoperate one task, train an imitation policy such as ACT, and evaluate it on the same hardware under controlled conditions. Classical control handles joints and motion; the learned policy selects actions from observations. A VLA adds language instructions and pretraining, but calibration, data collection, and physical evaluation remain necessary. LeRobot’s official documentation also recommends [ACT as a first policy](https://huggingface.co/docs/lerobot/en/act).

[Robot Learning: A Tutorial](https://arxiv.org/abs/2510.12403v1), by Francesco Capuano, Caroline Pascal, Adil Zouitine, Thomas Wolf, and Michel Aractingi, connects these roles across classical robotics, reinforcement learning, imitation learning, and generalist policies. The verified paper version is v1, submitted on October 14, 2025. The practical workflow uses **official LeRobot documentation and source checked on October 16, 2026 (KST)**. The paper’s examples and today’s CLI should not be assumed to use the same version.

## The roles of control, imitation, and reinforcement learning

In classical robotics, forward kinematics (FK) computes the end-effector pose from joint values; inverse kinematics (IK) finds joint values for a desired pose. A planner chooses a path, and a feedback controller reduces the difference between measured and target values. When friction and contact change throughout a task, engineering the environment model and perception pipeline becomes expensive. Learning provides a way to fit relationships between observations and actions from data. Robot kinematics, motor control, and workspace constraints still apply. This combination is a central point of the tutorial’s [classical robotics section](https://arxiv.org/html/2510.12403v1#S2).

| Approach | What is learned or designed | Suitable starting conditions | Main burden |
|---|---|---|---|
| Classical control and planning | Models, targets, paths, and error-correction rules | Geometry and operating conditions can be specified well | Modeling contact, perception, and environmental changes |
| Imitation learning (IL) | Relationships between demonstrated observations and actions | A person can repeatedly demonstrate the intended behavior | Unseen states and missing recovery behavior |
| Reinforcement learning (RL) | A policy that increases cumulative reward through interaction | Rewards, resets, and exploration boundaries can be managed | Physical trial and error, reward errors, and supervision |
| VLA | A policy producing actions from images, language, and robot state | A pretrained model can be adapted to the hardware and task | Data compatibility, action representation, and inference latency |

VLA stands for Vision-Language-Action and describes model inputs and structure. IL and RL describe learning methods. Fine-tuning a VLA on demonstrations is also imitation learning. Treating these as four mutually exclusive algorithms obscures the choice.

Behavioral Cloning (BC) uses supervised learning to predict demonstrated actions from demonstrated observations. ACT and Diffusion Policy are policy families that serve this objective; they need not be understood as separate algorithms attached after BC. RL instead optimizes expected cumulative reward in a decision process involving states, actions, transitions, rewards, and a discount factor. The tutorial discusses TRPO, PPO, SAC, and TD-MPC, but coverage in the paper does not mean that every method has an equivalent LeRobot real-robot CLI. The paper’s [definitions of imitation and reinforcement learning](https://arxiv.org/html/2510.12403v1) should be distinguished from the features of an installed version.

## Action chunks and feedback frequency

The first difficulty in imitation learning is the data distribution. A gripper that slightly misses its target can enter a state absent from the demonstrations, where its next prediction may also be wrong. This distribution shift and compounding error may not be apparent from training loss. Demonstrations can also contain several valid behaviors. If people move around an object on either side, a regressor predicting one average action can head toward the obstacle. The tutorial’s [BC discussion](https://arxiv.org/html/2510.12403v1#S4) separates these two problems.

**ACT (Action Chunking with Transformers)** predicts several future actions from current images and joint state. During training, a conditional variational autoencoder (CVAE) represents demonstration variability with a latent variable; at inference, that variable is set to zero. The original ACT temporal-ensembling procedure predicts a new chunk at every timestep and takes a weighted average of predictions for the same execution time. Chunking therefore does not inherently mean fewer model calls. The [ACT project](https://tonyzhaozh.github.io/aloha/) and [LeRobot ACT documentation](https://huggingface.co/docs/lerobot/en/act) describe this design.

**Diffusion Policy** generates action sequences through iterative denoising conditioned on observations. It can represent multiple valid behaviors and uses receding-horizon control: execute part of a predicted sequence, then plan again from fresh observations. Generation time and observation-update frequency must be considered together. These properties follow the method described on the [official project site](https://diffusion-policy.cs.columbia.edu/).

If the entire chunk executes before another observation reaches the policy, that interval is open loop from the policy’s perspective. For example, 30 actions executed at 30 Hz span one second. This is an illustration of the connection between chunk length and responsiveness, not a recommended setting for a particular model. Low-level joint feedback can continue throughout that interval; incorporating a new image showing that an object has moved is a separate matter.

Asynchronous inference computes the next chunk while the current one executes. LeRobot’s [Real-Time Chunking (RTC)](https://huggingface.co/docs/lerobot/en/rtc) uses the overlapping actions from the previous chunk to condition the next chunk in supported flow-matching policies. Overlapping computation with execution and aligning actions in time are the essential mechanisms. Observation age when inference finishes and the remaining action queue also matter. Asynchrony alone guarantees neither safety nor task success.

## Connecting LeRobotDataset to hardware configuration

LeRobot is Hugging Face’s open-source library connecting robot hardware, data collection, training, and inference. The current [LeRobotDataset v3 documentation](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3) describes Parquet for states, actions, and timestamps; MP4 for camera video; and metadata for schemas, normalization statistics, and episode boundaries. Multiple episodes can share a file, so one file must not be treated as one episode.

A learner receives more than video. Keys such as `observation.state`, `action`, and `observation.images.front`, together with their dimensions and ordering, form a data contract. `delta_timestamps` specifies windows of past observations or future actions relative to a reference time. Large datasets can be streamed, but the storage format does not establish whether another robot’s actions are meaningful for yours.

The examples use an SO-101 follower and leader with one fixed OpenCV camera. The follower performs the task, while the person moves the leader to provide demonstration commands. Other hardware needs the appropriate types, drivers, and calibration from its [robot-specific guide](https://huggingface.co/docs/lerobot/en/so101). The commands below were checked against documentation and source; they were not executed on physical hardware for this post.

### Installation and device discovery

Prepare a separate Python 3.12 environment and a platform-appropriate PyTorch installation. The CUDA example assumes an NVIDIA GPU with a compatible driver. Check the [installation guide](https://huggingface.co/docs/lerobot/en/installation) for platform-specific FFmpeg/TorchCodec video-decoding requirements. This source installation pins the inspected commit and includes hardware, training, and Feetech dependencies.

```bash
git clone https://github.com/huggingface/lerobot.git
cd lerobot
git checkout 297774fca4e3ad0aa34e7425fbf937111637e77b
python -m pip install -e '.[core_scripts,training,feetech]'
lerobot-find-port
lerobot-find-cameras opencv
```

Port discovery identifies a device by asking you to disconnect its USB connection. Check camera indices directly as well. The `FOLLOWER_PORT`, `LEADER_PORT`, and `CAMERA_INDEX` values below must be replaced with your devices; do not guess ports before sending robot commands. Linux also requires access permissions for the serial devices. New-motor ID and baud-rate setup, along with assembly, must be completed using the SO-101 guide before calibration.

### Calibration and teleoperation

Calibration makes equivalent leader and follower poses map to consistent joint values. It requires moving the hardware to measure its range, so clear the surrounding space and follow the official procedure. Keep the same device IDs through collection and evaluation: LeRobot uses them to identify calibration files.

```bash
FOLLOWER_PORT=/dev/ttyACM0
LEADER_PORT=/dev/ttyACM1
CAMERA_INDEX=0
CAMERAS="{front: {type: opencv, index_or_path: ${CAMERA_INDEX}, width: 640, height: 480, fps: 30}}"

lerobot-calibrate --robot.type=so101_follower \
  --robot.port="$FOLLOWER_PORT" --robot.id=tutorial_follower
lerobot-calibrate --teleop.type=so101_leader \
  --teleop.port="$LEADER_PORT" --teleop.id=tutorial_leader

lerobot-teleoperate \
  --robot.type=so101_follower --robot.port="$FOLLOWER_PORT" \
  --robot.id=tutorial_follower --robot.cameras="$CAMERAS" \
  --teleop.type=so101_leader --teleop.port="$LEADER_PORT" \
  --teleop.id=tutorial_leader --display_data=true
```

First check that the arm moves in the expected direction and that the gripper and object are visible. The [official collection guide](https://huggingface.co/docs/lerobot/en/il_robots) recommends a setup in which a person can perform the task from the camera images alone. Moving a camera during demonstrations also changes the observation conditions.

### A small recording and data inspection

This five-episode trial checks storage paths and feature keys. It does not establish that there is enough training data. Hub uploading is disabled, allowing local collection without logging in. `example-user` is a placeholder identifier; replace it with a repository you control if you later upload.

```bash
DATASET_ID=example-user/cube-pickplace
DATA_ROOT="$PWD/data/cube-pickplace"

lerobot-record \
  --robot.type=so101_follower --robot.port="$FOLLOWER_PORT" \
  --robot.id=tutorial_follower --robot.cameras="$CAMERAS" \
  --teleop.type=so101_leader --teleop.port="$LEADER_PORT" \
  --teleop.id=tutorial_leader --display_data=true \
  --dataset.repo_id="$DATASET_ID" --dataset.root="$DATA_ROOT" \
  --dataset.single_task="Put the cube in the bin" \
  --dataset.num_episodes=5 --dataset.fps=30 \
  --dataset.push_to_hub=false
```

Inspect whether video, joint state, and actions align; whether the object is occluded; and whether success and failure segments were recorded as intended. The official guide suggests 50 episodes with 10 per position as a starting point for a first grasping task. That is advice for a particular collection setup, not a universal minimum or a guarantee of success. Repeat each starting position sufficiently, then introduce changes such as object location and lighting one at a time once the baseline works. This makes failures easier to diagnose.

The following code checks state and action dimensions and image tensors in the same local dataset. Matching dimensions alone do not establish correct joint order or action units, so inspect the metadata too.

```python
import os
from lerobot.datasets import LeRobotDataset

dataset = LeRobotDataset(
    "example-user/cube-pickplace",
    root=os.path.join(os.getcwd(), "data/cube-pickplace"),
)
sample = dataset[0]
for key in ("observation.state", "action", "observation.images.front"):
    print(key, sample[key].shape)
```

### ACT training and bounded physical evaluation

After inspecting data quantity and quality, train ACT using the same dataset path. The 10,000 steps and batch size of 8 below illustrate a run configuration, not a convergence criterion. Adjust them for GPU memory, evaluation results, and the task. Data and training outputs remain local.

```bash
lerobot-train \
  --dataset.repo_id="$DATASET_ID" --dataset.root="$DATA_ROOT" \
  --policy.type=act --policy.device=cuda \
  --output_dir=outputs/train/act_cube --job_name=act_cube \
  --batch_size=8 --steps=10000 \
  --policy.push_to_hub=false --wandb.enable=false
```

Check that the checkpoint exists, then run a short evaluation with the same calibration ID and camera configuration. The `base` strategy executes actions without automatically recording evaluation video. Keep a separate trial log, or configure the documented `episodic` strategy when recording is needed. The [inspected deployment CLI source](https://github.com/huggingface/lerobot/blob/297774fca4e3ad0aa34e7425fbf937111637e77b/src/lerobot/scripts/lerobot_rollout.py) defines `lerobot-rollout` as the entry point for real-robot policy execution.

```bash
lerobot-rollout \
  --strategy.type=base \
  --policy.path=outputs/train/act_cube/checkpoints/last/pretrained_model \
  --robot.type=so101_follower --robot.port="$FOLLOWER_PORT" \
  --robot.id=tutorial_follower --robot.cameras="$CAMERAS" \
  --task="Put the cube in the bin" --fps=30 --duration=10
```

`--duration=10` puts a 10-second limit on the policy execution loop. The [configuration defaults](https://github.com/huggingface/lerobot/blob/297774fca4e3ad0aa34e7425fbf937111637e77b/src/lerobot/rollout/configs.py#L340) to `return_to_initial_position=True`, and [`base` teardown](https://github.com/huggingface/lerobot/blob/297774fca4e3ad0aa34e7425fbf937111637e77b/src/lerobot/rollout/strategies/base.py#L90) receives this setting, so shutdown may include additional motion back to the starting pose. This time limit is neither a physical emergency stop nor a guarantee that all motion ends exactly after 10 seconds.

Start with soft objects and a workspace in which a person can stop execution immediately. Repeat the training starting conditions, then separately test predefined positions absent from the demonstrations. Record successes/attempts, human interventions, collisions or drops, starting positions, and the checkpoint. If failures repeat under the same conditions, checking occlusion, action representation, observation delay, and missing recovery demonstrations is more useful than simply increasing training steps.

## VLA transfer and its limits

VLAs combine pretrained visual and language understanding with robot action generation. [π₀](https://www.physicalintelligence.company/blog/pi0) combines a PaliGemma-based VLM and an action expert, using flow matching to generate continuous actions. Flow matching learns a vector field describing movement between noise and target actions; at inference, following that field generates action samples. [SmolVLA](https://huggingface.co/docs/lerobot/en/smolvla) also uses a VLM and an action expert. The official `lerobot/smolvla_base` model is a starting point for fine-tuning on your own data.

This design reuses visual and language pretraining for robotics, but changing an instruction does not make the same task work on every arm. Joint count and ordering, absolute positions versus relative displacements, units, camera keys, and normalization statistics must match. Recognizing an object’s location is also different from controlling contact and force during a grasp. The tutorial’s [generalist-policy section](https://arxiv.org/html/2510.12403v1#S5) discusses embodied-data heterogeneity and negative transfer from indiscriminate mixing.

[Open X-Embodiment](https://robotics-transformer-x.github.io/) pools data across robots to study transfer; [DROID](https://droid-dataset.github.io/) provides manipulation data collected in varied real environments. Their value depends on action representations and environmental coverage as well as collection size. For data from another embodiment, format conversion alone should not be assumed sufficient for deployment.

## Conditions for physical reinforcement learning

RL can be considered when exploring improvements beyond demonstrations or optimizing a policy against a success criterion. However, simulated friction, contact, and sensors differ from physical conditions, while real exploration incurs wear and object-reset costs. A misspecified reward may produce behavior that increases a score without accomplishing the intended task. Simulation success therefore cannot establish physical safety.

LeRobot’s [HIL-SERL guide](https://huggingface.co/docs/lerobot/en/hilserl) combines prior demonstrations, a visual success classifier, an online actor with human intervention, and a SAC learner. Human corrections and real interactions enter training, while workspace bounds, resets, and success detection require separate configuration. Human intervention is neither the only approach to RL nor an automatic safety certification. It is one design for physical learning with supervision and a means to interrupt execution.

Physical precautions also apply to imitation-policy evaluation. Secure the arm, organize cables, clear the workspace, and keep hands and people away from gripper and joint pinch points. Within the capabilities supported by the manufacturer and hardware, limit speed, action changes, and joint and end-effector ranges; establish how to cut power safely. A recording program’s quit key is not a physical emergency stop. These operating recommendations apply independently of the learning algorithm.

Consistency between observations and actions matters more to a first experiment than the model name. Connecting demonstration collection, data inspection, ACT training, and repeated evaluation on one task also makes it possible to tell what improves when VLA fine-tuning or online RL is introduced.

## Further reading

- [ACT and ALOHA](https://tonyzhaozh.github.io/aloha/): the original work on action chunks and precise bimanual manipulation.
- [Diffusion Policy](https://diffusion-policy.cs.columbia.edu/): action distributions and receding-horizon control.
- [Open X-Embodiment](https://robotics-transformer-x.github.io/) and [DROID](https://droid-dataset.github.io/): compare the robots and environments represented in the data.

## References

Sources below were checked on October 16, 2026 (KST). The command examples use LeRobot commit `297774fca4e3ad0aa34e7425fbf937111637e77b` as their source baseline.

- Capuano, Pascal, Zouitine, Wolf, Aractingi, [Robot Learning: A Tutorial, arXiv:2510.12403v1](https://arxiv.org/abs/2510.12403v1), submitted October 14, 2025.
- Hugging Face, [Installation](https://huggingface.co/docs/lerobot/en/installation), [SO-101 setup and calibration](https://huggingface.co/docs/lerobot/en/so101), [Cameras](https://huggingface.co/docs/lerobot/en/cameras), [Real-world imitation learning](https://huggingface.co/docs/lerobot/en/il_robots).
- Hugging Face, [LeRobotDataset v3](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3), [ACT](https://huggingface.co/docs/lerobot/en/act), [SmolVLA](https://huggingface.co/docs/lerobot/en/smolvla), [RTC](https://huggingface.co/docs/lerobot/en/rtc), [HIL-SERL](https://huggingface.co/docs/lerobot/en/hilserl).
- Hugging Face, [Inspected LeRobot source](https://github.com/huggingface/lerobot/tree/297774fca4e3ad0aa34e7425fbf937111637e77b).
- Physical Intelligence, [Introducing π₀](https://www.physicalintelligence.company/blog/pi0).
