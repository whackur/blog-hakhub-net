---
title: "FHE·SP1·Groth16로 보는 비밀 투표 아키텍처"
meta_title: ""
description: "온체인 비밀 투표를 FHE 집계, SP1 실행 증명, Groth16 온체인 검증으로 설계하는 방법을 구체적인 아키텍처와 신뢰 가정 체크리스트와 함께 설명합니다."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
image: ""
categories: ["Blockchain"]
tags: ["fhe", "zk-proof", "groth16", "sp1", "voting", "privacy", "zero-knowledge", "maci", "semaphore"]
author: "whackur"
translationKey: "fhe-sp1-groth16-secret-voting"
draft: false
---

비밀 투표를 온체인에서 구현하면 즉시 세 가지 긴장이 생깁니다. 표 내용을 숨겨야 하는데 집계는 해야 하고, 오프체인 연산을 신뢰할 수 없는데 결과는 온체인에 확정해야 하며, EVM이 무거운 암호 연산을 직접 실행하기 어려운데 검증은 해야 합니다. FHE(완전 동형 암호), SP1 zkVM, Groth16 SNARK는 각각 이 세 가지 긴장을 담당합니다.

"FHE로 표를 숨긴 채 더하고, SP1으로 집계·검증 로직이 맞음을 증명하고, Groth16으로 EVM이 싸게 확인한다"는 설명은 큰 그림으로 맞습니다. 다만 실제 배포에는 코프로세서(coprocessor), 게이트웨이, KMS 임계 복호화, nullifier 기반 중복 방지, trusted setup 가정이 따라옵니다. 이 글은 각 요소의 역할을 정리하고, 비슷하지만 다른 프라이버시 투표 패턴과 비교하며, 설계 선택 기준을 제시합니다.

## 세 요소의 역할

### FHE: 암호문 위에서 집계

FHE(Fully Homomorphic Encryption)의 임무는 표를 복호화하지 않은 채로 집계하는 것입니다. 유권자는 `찬성=1`, `반대=0`을 FHE 공개키로 암호화해 제출하고, 코프로세서가 `FHE.add`로 암호문들을 더합니다. 중간 집계값이 평문으로 공개되지 않습니다.

[Zama Protocol](https://docs.zama.ai/protocol/protocol/overview)을 기준으로 지원되는 연산은 `add`, `sub`, `mul`, `min`, `max`, 비교, bitwise, `FHE.select` 등이며, 나눗셈·나머지는 평문 divisor만 지원하는 등 제약이 있습니다. EVM이 FHE 연산을 직접 실행하는 것이 아니라는 점이 중요합니다. 호스트 컨트랙트가 symbolic 이벤트를 내면 오프체인 [코프로세서](https://docs.zama.ai/protocol/protocol/overview/coprocessor)가 TFHE-rs 등으로 실제 계산을 수행합니다.

### SP1: 실행 무결성 증명

[SP1](https://docs.succinct.xyz/docs/sp1/introduction)은 RISC-V로 컴파일 가능한 Rust 프로그램의 실행이 올바랐음을 증명하는 zkVM입니다. 비밀 투표 맥락에서는 "유권자 자격 검증, nullifier 중복 방지, 제출된 암호문 handle 목록, 집계 규칙, 공개값 digest가 서로 일관된다"를 Rust 프로그램으로 확인하고 증명을 만듭니다.

주의할 점이 있습니다. FHE 동형 연산 자체를 SP1 안에서 전부 재실행해 증명하는 구조는 비용이 커집니다. 실무에서는 FHE 계산 경계와 ZK 검증 경계를 분리합니다. SP1은 FHE 연산이 올바르게 위탁됐다는 transcript와 공개 입력의 일관성을 증명하는 역할에 가깝습니다.

### Groth16: 온체인 검증 압축

[SP1 proof type](https://docs.succinct.xyz/docs/sp1/generating-proofs/proof-types)은 네 가지입니다.

| 유형 | 크기 | 온체인 gas | 용도 |
|------|------|------------|------|
| Core | 실행 크기 비례 | 높음 | 오프체인 검증 |
| Compressed | 상수 크기 STARK | 높음 | 재귀 집계, 온체인 비권장 |
| Groth16 | 약 260 bytes | 약 270k gas | 온체인 배포 권장 경로 |
| PLONK | 약 868 bytes | 약 300k gas | trusted setup 기피 시 대안 |

Groth16은 큰 실행 증명을 EVM이 검증하기 좋은 상수 크기 SNARK로 압축합니다. "약 260바이트짜리 영수증"이라는 비유는 방향이 맞지만, 실제 검증에는 proof bytes, public values, program verification key, verifier routing이 함께 들어갑니다. trusted setup 부담을 피하고 싶다면 PLONK가 대안입니다.

## 전체 흐름

1. **유권자 등록**: group membership 또는 allowlist에 등록합니다. 익명 1인 1표에는 Semaphore식 identity commitment와 nullifier 패턴이 적합합니다.

2. **투표 제출**: 브라우저가 표를 FHE 공개키로 암호화하고, "등록 유권자이고, 이 투표에서 nullifier를 쓴 적 없으며, 암호문이 올바르게 만든 값"임을 ZK proof로 증명합니다. 온체인 컨트랙트는 proof와 nullifier를 검증한 뒤 암호문 handle을 기록합니다.

3. **암호문 집계**: 호스트 컨트랙트가 FHE 연산을 symbolic 이벤트로 내면, 오프체인 코프로세서가 실제 `add`, `select` 연산을 수행하고 결과 암호문 commitment를 게시합니다.

4. **실행 무결성 증명**: SP1 프로그램이 공개 입력 목록, nullifier 집합, 암호문 handle, 집계 규칙, commitment/digest, 최종 공개값의 일관성을 확인합니다. 증명은 Groth16 또는 PLONK로 wrap되어 Ethereum 또는 Base verifier에서 검증됩니다.

5. **개표**: 투표 종료 후 [KMS](https://docs.zama.ai/protocol/protocol/overview/kms)가 임계 복호화를 수행합니다. Zama KMS 문서 기준 예시는 13개 MPC 노드 중 9개가 참여하는 구조이며, 개인키는 단일 주체가 직접 접근하지 못하도록 secret sharing됩니다.

6. **온체인 확정**: Ethereum 또는 Base 컨트랙트가 Groth16/PLONK proof와 복호화 결과를 검증한 뒤 최종 집계를 기록합니다. Base 같은 L2에서는 동일한 gas량이라도 실제 비용이 낮아집니다.

## 비슷하지만 다른 패턴들

비밀 투표 요구사항은 어느 속성에 무게를 두느냐에 따라 달라집니다. "익명 1인 1표", "매수 저항", "마감 전 결과 은폐", "코디네이터도 평문을 못 봄"에 따라 선택이 나뉩니다.

### Semaphore

[Semaphore](https://docs.semaphore.pse.dev/)는 익명 그룹 멤버가 한 번만 signal을 보냈음을 증명합니다. identity commitment를 Merkle tree에 넣고, proof는 "나는 멤버이고 같은 external nullifier에서 아직 signal하지 않았다"를 검증합니다. 단순 익명 1인 1표, DAO signaling에 적합합니다. 매수 저항은 자동으로 제공하지 않습니다.

### MACI

[MACI(Minimal Anti-Collusion Infrastructure)](https://maci.pse.dev/docs/introduction)는 privacy와 collusion/bribery resistance를 같이 노립니다. 사용자가 암호화된 vote message를 제출하고, coordinator가 오프체인에서 처리한 뒤 tally가 맞음을 zk-SNARK로 증명합니다. key-change message로 이전 투표를 무효화할 수 있어 매수자가 유권자의 실제 투표를 신뢰하기 어렵습니다. 결과 조작은 zk-SNARK가 막지만, coordinator가 개별 투표를 볼 수 있다는 신뢰 가정은 남습니다.

### Shutter / 임계 암호화

[Shutter Network](https://docs.shutter.network/)는 마감 전 표 내용을 숨겨 front-running, bandwagon effect, 막판 매수 유인을 줄입니다. keyper 위원회가 임계 키를 관리하고, 종료 후 복호화 키 share를 공개합니다. keyper t-of-n 정직성·가용성 가정이 필요합니다.

### FHE+ZK 하이브리드

코디네이터가 평문 표를 보지 않고도 암호문 상태에서 집계할 수 있습니다. FHE로 집계하고, ZK/SP1으로 유효성·집계 규칙·공개값 일관성을 증명합니다. 대신 코프로세서, 게이트웨이, KMS, 임계 복호화, trusted setup, 증명 생성 비용을 모두 보안 모델에 포함해야 합니다.

## 설계 선택 기준

요구사항에 따라 접근이 달라집니다.

- **단순 익명 1인 1표**: Semaphore/nullifier 패턴이 가장 단순합니다.
- **매수·담합 저항이 핵심**: MACI를 우선 검토합니다.
- **마감 전 중간 결과 은폐**: Shutter식 임계 암호화 또는 timelock encryption이 적합합니다.
- **코디네이터도 평문을 볼 수 없어야 한다면**: FHE 집계 + 임계 복호화 + ZK/SP1 무결성 증명을 결합합니다.
- **Ethereum/Base 온체인 검증 비용을 낮춰야 한다면**: SP1 Groth16 verifier를 사용하되 trusted setup 가정과 증명 생성 비용을 문서화합니다. trusted setup 부담이 크면 PLONK도 검토합니다.

## 보안 가정 체크리스트

구현 전 다음 질문에 답을 준비해야 합니다.

- 유권자 자격 소스는 무엇인가? (allowlist, token snapshot, identity credential, Semaphore group)
- nullifier domain은 투표별로 분리되는가?
- 투표 암호문이 허용 범위(0/1, 후보 인덱스) 안임을 증명하는 range proof가 있는가?
- 중복 투표, revote, key-change 정책은 무엇인가?
- FHE 코프로세서 결과를 어떻게 commitment/signature로 검증하는가?
- KMS 임계값은 몇-of-몇이며, 조기복호화·복호화 거부·담합 시나리오를 어떻게 다루는가?
- SP1 public inputs에는 어떤 digest와 상태 root가 들어가는가?
- Groth16 trusted setup 가정 또는 PLONK 선택 사유가 문서화되어 있는가?
- 최종 tally만 공개되는가, 아니면 turnout metadata가 privacy leak이 될 수 있는가?

## 함께 보면 좋을 자료

- [Zama Protocol 문서](https://docs.zama.ai/protocol/protocol/overview): FHE 온체인 구조, 코프로세서, KMS 설계
- [Succinct SP1 문서](https://docs.succinct.xyz/docs/sp1/introduction): zkVM 개요와 proof type 비교
- [SP1 Contracts](https://github.com/succinctlabs/sp1-contracts): Ethereum/Base 배포용 verifier 컨트랙트
- [MACI 문서](https://maci.pse.dev/docs/introduction): anti-collusion 투표 시스템
- [Semaphore 문서](https://docs.semaphore.pse.dev/): 익명 그룹 멤버십 증명
- [Shutter Network 문서](https://docs.shutter.network/): 임계 암호화 기반 front-running 방지

## 참고 자료

- [Zama Protocol Overview](https://docs.zama.ai/protocol/protocol/overview): docs.zama.ai, 조회일 2026-06-30
- [Zama Protocol: Operations on encrypted types](https://docs.zama.ai/protocol/solidity-guides/smart-contract/operations): docs.zama.ai, 조회일 2026-06-30
- [Zama Protocol: KMS](https://docs.zama.ai/protocol/protocol/overview/kms): docs.zama.ai, 조회일 2026-06-30
- [Succinct SP1 Introduction](https://docs.succinct.xyz/docs/sp1/introduction): docs.succinct.xyz, 조회일 2026-06-30
- [SP1 Proof Types](https://docs.succinct.xyz/docs/sp1/generating-proofs/proof-types): docs.succinct.xyz, 조회일 2026-06-30
- [SP1 Contracts](https://github.com/succinctlabs/sp1-contracts): GitHub, succinctlabs, 조회일 2026-06-30
- [MACI Introduction](https://maci.pse.dev/docs/introduction): maci.pse.dev, 조회일 2026-06-30
- [Semaphore Documentation](https://docs.semaphore.pse.dev/): docs.semaphore.pse.dev, 조회일 2026-06-30
- [Shutter Network Documentation](https://docs.shutter.network/): docs.shutter.network, 조회일 2026-06-30
