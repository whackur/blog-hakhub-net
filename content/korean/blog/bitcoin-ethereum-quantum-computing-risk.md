---
title: "비트코인과 이더리움, 양자 컴퓨터는 정말 위협일까"
meta_title: ""
description: "양자 공격의 대상은 서명과 공개키입니다. 2026년 10월 확인한 자원 추정, 노출 기간, 비트코인 제안과 이더리움 전환 계획을 구분해 설명합니다."
date: 2026-07-05T23:37:01+09:00
lastmod: 2026-10-16T01:03:28+09:00
image: "/images/posts/bitcoin-ethereum-quantum-computing-risk/quantum-ledgers-cover-20261016.webp"
categories: ["Blockchain"]
tags: ["bitcoin", "ethereum", "quantum-computing", "post-quantum-cryptography", "cryptography"]
author: "whackur"
translationKey: "bitcoin-ethereum-quantum-computing-risk"
draft: false
---

양자 컴퓨터는 비트코인과 이더리움의 **서명을 위조할 수 있는 장기적 위협**입니다. 다만 2026년 10월 16일(KST) 확인한 공개 연구는 실제 secp256k1 개인키 복구 시연이 아니라, 미래의 오류 수정 양자 컴퓨터에 필요한 자원을 계산한 결과입니다. 위험을 가르는 조건은 공개키가 얼마나 오래 노출되는지, 공격 계산이 얼마나 걸리는지, 그 전에 서명과 권한을 전환할 수 있는지입니다. 비트코인의 방어안은 아직 제안 단계이고 이더리움도 계정·합의·데이터 계층을 함께 바꾸는 작업을 진행 중입니다. [자원 추정 논문](https://arxiv.org/html/2609.05625v1), [BIP-360](https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki), [이더리움 재단의 전환 계획](https://blog.ethereum.org/2026/09/07/protocol-priorities)

## 서명 위조와 해시 공격은 다른 문제입니다

전자서명은 코인을 암호화하지 않습니다. 거래를 승인할 권한이 있다는 것을 증명합니다. 타원곡선 공개키를 `Q = d·G`라고 쓰면 `d`가 개인키이고 `G`는 정해진 기준점입니다. `d`를 아는 사람은 `Q`를 계산할 수 있지만, `Q`만으로 `d`를 구하는 타원곡선 이산로그 문제는 고전 컴퓨터로 풀기 어렵습니다. 충분한 오류 수정 능력을 갖춘 양자 컴퓨터는 Shor 알고리즘으로 이 문제를 다항 시간에 풀 수 있습니다. 개인키를 얻은 공격자는 소유자처럼 새 거래에 서명합니다. [Schrottenloher의 회로 연구](https://arxiv.org/html/2606.02235v1)

| 암호 기술 | 비트코인·이더리움에서 맡는 일 | 양자 공격의 차이 |
| --- | --- | --- |
| secp256k1 ECDSA | 비트코인의 기존 서명, 이더리움 외부 소유 계정(EOA)의 인증 | Shor로 공개키에서 개인키를 복구하면 서명 위조 가능 |
| secp256k1 Schnorr | 비트코인 Taproot 서명 | 서명 형식이 달라도 같은 곡선의 이산로그에 의존 |
| BLS | 이더리움 검증자의 합의 서명과 집계 | 역시 양자 공격 대상이지만 secp256k1과 곡선·파라미터가 다름 |
| SHA-256·Keccak 등 해시 | 채굴, 주소·데이터에 대한 커밋 등 | 일반적인 원상 탐색에는 Grover의 제곱근 가속이 적용됨 |

[BIP-340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki)은 Schnorr 서명이 secp256k1을 사용한다고 명시합니다. [이더리움의 암호 전환 문서](https://ethereum.org/roadmap/security/quantum-resistance/)는 ECDSA와 BLS, KZG 커밋을 별도 대상으로 구분합니다. 따라서 “secp256k1 공격에 1,450 논리 큐비트”라는 수치를 BLS 공격 비용에 그대로 적용할 수 없습니다.

Grover 알고리즘은 후보가 `N`개인 비구조적 탐색을 대략 `√N`번의 질의로 줄입니다. 이상적인 일반 원상 공격을 가정하면 256비트 해시는 약 `2^128`, 160비트 해시는 약 `2^80`번의 양자 질의가 필요합니다. 이는 실제 실행 시간이 아니며 각 질의의 회로 비용과 오류 수정을 더해야 합니다. HASH160은 `RIPEMD160(SHA256(public_key))`이며, 공개키를 숨기는 역할도 결국 해시의 안전성에 달려 있습니다. [NIST의 Grover 설명](https://xlinux.nist.gov/dads/HTML/groversAlgo.html), [BIP-141의 공개키 해시 규칙](https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki)

채굴은 특정한 256비트 해시값의 원상을 찾는 작업과도 다릅니다. 난이도 목표보다 작은 해시를 찾는 경쟁이므로 게이트 속도, 병렬화, ASIC과의 비용 비교가 필요합니다. SHA-256 원상 탐색의 `2^128`만으로 채굴 지배를 주장할 수 없고, 난이도 조정만으로 공격자의 블록 생산 비중이 제한되는 것도 아닙니다. 2026년 Google·이더리움 재단·스탠퍼드 등의 [공동 논문 III.4절](https://arxiv.org/html/2603.28846v2#S3.SS4)은 해당 하드웨어 가정에서 채굴 공격보다 서명 공격이 훨씬 현실적인 표적이라고 분석합니다.

## 공개키 노출 기간이 공격 시간을 결정합니다

비트코인에서 주소와 공개키는 같은 것이 아닙니다. 미사용 출력(UTXO)은 아직 지출하지 않은 코인을 잠그는 조건입니다. 어떤 출력은 공개키 자체를 담고, 어떤 출력은 공개키나 스크립트의 해시만 담습니다. [SegWit 규칙](https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki)과 [Taproot 규칙](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki)에 따른 차이는 다음과 같습니다.

| 대상 | 공격자가 공개키를 얻는 시점 | 남은 자금에 미치는 영향 |
| --- | --- | --- |
| P2PK·bare multisig | 출력을 만들 때 | 키가 이미 공개돼 장시간 계산 가능 |
| P2PKH·P2WPKH | 보통 지출할 때 공개키를 제출 | 같은 키로 잠긴 다른 UTXO가 남거나 다시 입금되면 장기 노출 |
| P2SH·P2WSH | 지출 시 스크립트를 공개하며 내부 키가 드러날 수 있음 | 스크립트와 키 재사용 여부에 따라 달라짐 |
| P2TR(Taproot) | 출력에 32바이트 출력 공개키를 직접 기록 | script-path로 지출할 생각이어도 key-path 검증에 쓰는 키가 공개됨 |
| 이더리움 EOA | 보낸 거래의 서명으로 공개키 복구 가능 | 계정에 남은 자금과 이후 입금, 해당 계정의 권한이 계속 대상이 됨 |

Taproot의 key-path는 출력 공개키에 대한 서명으로 지출하는 경로입니다. 숨긴 스크립트 안에 다른 보호 장치를 넣더라도, 출력 공개키의 개인키를 계산할 수 있는 공격자는 이 경로를 사용할 수 있습니다. [BIP-341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki)

두 사례를 비교하면 시간 제약이 분명해집니다. 공개키가 드러난 P2PK 출력에 코인이 그대로 있다면 공격자는 다음 블록 전까지 계산을 끝낼 필요가 없습니다. 며칠 걸리는 기계도 문제가 됩니다. 반면 공개키를 다른 곳에 노출하지 않은 새 P2WPKH 출력은 첫 지출 거래를 멤풀에 전파할 때 공개키가 드러납니다. 공격자는 원래 거래가 확정되기 전에 키를 복구하고, 같은 코인을 쓰는 경쟁 거래가 먼저 포함되도록 해야 합니다. 평균 10분이라는 비트코인 블록 간격은 보장된 방어 시간이 아닙니다. 거래 전파와 수수료, 블록 도착 시점도 결과에 영향을 줍니다. [공동 논문 III.2절](https://arxiv.org/html/2603.28846v2#S3.SS2)

해시형 주소라도 오프체인에서 공개키를 공유했다면 이 보호 조건이 사라집니다. 지갑의 확장 공개키(xpub)나 descriptor를 받은 상대도 고려해야 합니다. 이미 지출한 출력은 다시 훔칠 수 없지만 같은 키가 보호하는 남은 출력은 별개입니다. [BIP-360의 노출 조건](https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki)

이더리움에서는 한 번 사용한 계정을 계속 쓰는 경우가 많습니다. 서명에서 키가 복구되면 빠른 블록 주기만으로 장기 공격을 막을 수 없습니다. 잔액이 작은 관리자 계정도 브리지나 업그레이드 권한을 가졌다면 영향이 큽니다. 이 위험은 과거 거래를 복호화하는 문제와 다르며, 키를 복구한 뒤 새로운 권한 행사를 위조하는 문제입니다. [이더리움 계정 문서](https://ethereum.org/developers/docs/accounts/), [포스트양자 팀 FAQ](https://pq.ethereum.org/)

## 큐비트 수와 실행 시간을 함께 읽어야 합니다

물리 큐비트는 실제 장치의 구성 요소입니다. 논리 큐비트는 여러 물리 큐비트와 오류 검출·정정 절차로 보호한 계산 단위입니다. 둘 사이에 고정된 환산 비율은 없습니다. 오류율, 연결 구조, 코드, 계산 길이와 허용 실패 확률에 따라 필요한 장치 규모가 달라집니다. Willow의 [임계값 이하 오류 수정 연구](https://www.nature.com/articles/s41586-024-08449-y)는 코드를 키울수록 논리 오류가 줄어드는 양자 메모리를 시연했습니다. 이것만으로 긴 암호 공격 회로 전체를 실행한 것은 아닙니다.

Toffoli 게이트는 두 제어 비트의 조건에 따라 다른 비트를 뒤집는 가역 연산이며, 이 게이트의 수는 공격 회로의 주요 비용 지표입니다. 실행 시간에는 병렬 실행 가능한 정도와 측정·제어 지연도 작용합니다. 2026년 연구들을 비교할 때는 전체 키 복구 회로인지, 내부 연산 하나의 최적화인지부터 나눠야 합니다.

| 연구 | 논리 회로의 자원 | 물리 장치·시간의 의미 |
| --- | --- | --- |
| [Babbush 외, 3월 공개](https://arxiv.org/html/2603.28846v2) | 1,200 이하 논리 큐비트·9,000만 이하 Toffoli, 또는 1,450 이하·7,000만 이하 | 초전도·평면 degree-4 연결·물리 오류율 `10^-3`에서 물리 큐비트 50만 미만 추정 |
| [Schrottenloher, 6월](https://arxiv.org/html/2606.02235v1) | 전체 회로 약 1,208·`2^26.11` Toffoli, 또는 1,462·`2^25.78` | 공개한 논리 회로 설계. 물리 장치나 실행 시간의 실측치가 아님 |
| [이온트랩 연구, 9월](https://arxiv.org/html/2609.05625v1) | 본문 기준 1,457 논리 큐비트·약 3,900만 Toffoli | 특정 오류 수정 아키텍처에서 물리 큐비트 19,397개·시도당 약 25.7일 추정 |

3월 논문의 시간 추정은 제어 반응 10μs와 게이트당 50% 추가 비용을 가정해 18~23분입니다. 공개키와 무관한 전반부를 미리 계산한 상태에서 기다리면, 공개키를 얻은 뒤 약 9~12분으로 줄어든다는 계산입니다. 오류 수정 주기는 1μs를 가정합니다. 모두 단일 키 공격의 자원 추정이며 실제 장치의 측정 결과가 아닙니다. 회로 세부는 공개하지 않고 영지식 증명으로 자원·검사 결과를 제시했습니다. [논문 II.1~II.2절과 부록](https://arxiv.org/html/2603.28846v2)

9월 이온트랩 논문은 공간을 줄이는 대신 긴 실행 시간을 허용하는 다른 설계입니다. 물리 오류율 `10^-4`, 물리 연산 주기 200μs, 논리 측정층당 약 0.02950초 등을 가정합니다. 메모리의 낮은 논리 오류율은 더 높은 오류율에서 얻은 시뮬레이션을 외삽했습니다. 전체 성공 확률도 확정값이 아닙니다. 논문은 계산 성공률의 엄밀한 하한을 출발점으로 한 추정 약 40.7%와, 휴리스틱을 출발점으로 한 추정 약 63.3%를 구분합니다. **19,397개짜리 현재 장치로 공격에 성공했다는 뜻이 아닙니다.** 수일 이상 공개된 키에는 관련이 있지만 일반적인 멤풀 지출 경쟁을 설명하는 수치는 아닙니다. [논문 II.3절·V부·부록 E](https://arxiv.org/html/2609.05625v1)

또 다른 9월 논문 [ECDSA.Fail](https://arxiv.org/html/2609.09582v2)은 7월 26일 데이터 기준 점 덧셈 회로에서 1,151 논리 큐비트와 평균 1,299,453회의 실행 Toffoli를 보고합니다. 이는 Shor 알고리즘 내부 연산의 벤치마크입니다. 논문도 전체 알고리즘 통합과 검증이 남았으며, 입력 인터페이스와 집계 규칙이 달라 수치만으로 기존 전체 회로보다 우월하다고 단정할 수 없다고 밝힙니다. “1,151 큐비트로 비트코인을 깼다”는 해석은 성립하지 않습니다.

## 표준 서명을 고르는 것만으로 전환이 끝나지 않습니다

NIST가 2024년 8월 확정한 표준에서 [ML-KEM(FIPS 203)](https://csrc.nist.gov/pubs/fips/203/final)은 통신용 공유 비밀을 만드는 키 캡슐화 방식입니다. 코인 지출 서명을 대체하는 알고리즘이 아닙니다. 서명 표준은 격자 기반 [ML-DSA(FIPS 204)](https://csrc.nist.gov/pubs/fips/204/final)와 상태를 별도로 추적하지 않는 해시 기반 [SLH-DSA(FIPS 205)](https://csrc.nist.gov/pubs/fips/205/final)입니다.

크기 차이도 큽니다. BIP-340 Schnorr 서명은 64바이트인 반면 ML-DSA-44는 공개키 1,312바이트·서명 2,420바이트, SLH-DSA-SHA2-128s는 공개키 32바이트·서명 7,856바이트입니다. 이는 각 파라미터의 예시이며 같은 안전성 수준의 직접 비교표는 아닙니다. [BIP-340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki), [FIPS 204 표 2](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf), [FIPS 205 표 2](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf)

이 알고리즘을 채택하려면 서명·공개키 크기와 검증 비용을 블록 공간, 가스, 노드의 대역폭에 맞춰야 합니다. 이더리움이 검증용 precompile과 증명 기반 서명 집계를 연구하는 이유입니다. 현재 후보를 도입했다는 사실과 모든 계정·관리자 키·합의 규칙이 전환됐다는 사실은 다릅니다. [이더리움 포스트양자 연구](https://pq.ethereum.org/)

상태가 있는 해시 서명도 정확히 구분해야 합니다. XMSS는 하나의 상위 키 아래 여러 일회용 서명 키를 트리로 묶어 여러 메시지에 서명합니다. 위험한 것은 상위 키를 두 번 쓰는 행위 자체가 아니라, 백업 복원이나 여러 장치의 동시 서명으로 같은 일회용 키 인덱스를 재사용하는 상황입니다. 지갑은 인덱스 관리와 복구 절차까지 검증해야 합니다. [NIST SP 800-208](https://csrc.nist.gov/pubs/sp/800/208/final)

## 비트코인은 출력 형식과 기존 코인 처리를 따로 논의합니다

2026년 10월 16일(KST) 확인한 **BIP-360은 Draft인 P2MR(Pay-to-Merkle-Root) 제안**입니다. Taproot와 비슷한 스크립트 트리를 쓰되 key-path 지출을 없애고 머클 루트에 커밋합니다. 공개키가 출력에 바로 드러나는 경로를 제거해 장기 노출 공격을 줄이는 것이 목적입니다. 기존 ECDSA·Schnorr로 지출하면서 멤풀에 키가 드러나는 공격까지 해결하지는 않습니다. 포스트양자 서명 도입은 별도 작업입니다. 제안 저장소에 문서가 있다는 사실은 네트워크 활성화를 뜻하지 않습니다. [BIP-360 원문](https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki)

**BIP-361도 Draft이며 Informational 문서**입니다. 아직 정해지지 않은 포스트양자 서명 제안을 전제로 합니다. 현재 문서는 활성화 약 3년 뒤(160,000블록) 취약한 주소로의 송금을 제한하는 Phase A, 그로부터 2년 뒤 기존 ECDSA·Schnorr 지출에 양자 안전 구제 절차를 요구하는 Phase B를 제시합니다. 이는 채택된 일정이 아닙니다. [BIP-361 원문](https://github.com/bitcoin/bips/blob/master/bip-0361.mediawiki)

구제 절차의 핵심은 양자 공격자가 알아낸 개별 개인키와 진짜 보유자만 가진 정보의 차이입니다. 예를 들어 hardened 파생을 거친 HD 지갑의 상위 비밀키를 안다는 증명을 검토합니다. 원문은 어떤 구제 방식이 얼마나 많은 기존 코인을 포괄할지 아직 알 수 없다고 명시합니다. 오래 움직이지 않은 코인이라고 모두 분실됐다고 단정할 수도 없습니다. 소유자가 이동하지 않는 코인을 계속 지출 가능하게 둘지, 추가 조건을 부과할지는 기술과 재산권이 함께 걸린 합의 문제입니다. [BIP-361의 구제 논의](https://github.com/bitcoin/bips/blob/master/bip-0361.mediawiki)

## 이더리움은 계정·합의·데이터를 함께 바꿉니다

이더리움 재단 Protocol 클러스터는 2026년 9월 7일 **L1의 실행·합의·데이터 계층을 2029년 12월까지 양자 내성으로 전환한다는 목표**를 발표했습니다. 2030년 공격 가능성을 공격적인 계획 가정으로 사용하지만 Q-day 예측이라고 하지는 않습니다. 팀이 정한 준비 목표와 실제 업그레이드 합의·배포는 구분해야 합니다. 연구팀 FAQ는 전체 실행 계층의 사용자 이동에는 그 이후에도 시간이 더 걸릴 수 있다고 설명합니다. [연구팀 FAQ](https://pq.ethereum.org/) [EF Protocol 발표](https://blog.ethereum.org/2026/09/07/protocol-priorities)

| 계층 | 전환하려는 대상 | 진행 중인 접근 |
| --- | --- | --- |
| 실행 | EOA·스마트 계정과 애플리케이션의 인증 | 계정 추상화, 포스트양자 서명 검증, 기존 키 권한의 폐기 |
| 합의 | 검증자의 BLS 서명 | leanXMSS 같은 해시 서명과 leanVM 기반 증명 집계 연구 |
| 데이터 | blob의 KZG 커밋 등 | 양자 안전 커밋과 검증 구조 연구 |

[공식 연구 허브](https://pq.ethereum.org/)가 설명하는 다층 전환입니다. BLS의 짧은 집계 서명을 더 큰 해시 서명으로 바꾸려면 네트워크 전파와 검증 비용도 다시 맞춰야 합니다. KZG처럼 타원곡선 기반 설정 파라미터를 쓰는 구조와 일부 페어링 기반 증명 시스템도 함께 살펴야 합니다. 표준 계정 서명만 교체해도 이 작업이 자동으로 끝나지는 않습니다. [이더리움 암호 전환 문서](https://ethereum.org/roadmap/security/quantum-resistance/)

KZG 커밋은 blob 데이터를 다항식으로 표현하고, 짧은 커밋과 증명으로 특정 위치의 값이 그 데이터와 맞는지 검사하게 합니다. [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844)의 검증 구조입니다. 공개 설정값에서 이산로그를 풀어 설정의 비밀값을 복구하면, 이후에는 고전 컴퓨터로도 거짓 증명을 만들 수 있다는 것이 공동 논문의 on-setup 공격입니다. 설정 참여자가 비밀을 지웠더라도 공개 파라미터의 이산로그 문제가 양자 안전해지는 것은 아닙니다. [공동 논문 IV절·V.5절](https://arxiv.org/html/2603.28846v2#S5.SS5)

특히 **EIP-7702 위임만으로 기존 ECDSA 키가 폐기되지는 않습니다.** 원래 키로 위임을 변경할 수 있으므로 위임된 코드가 포스트양자 서명을 검사하더라도 원래 키를 복구한 공격자가 이를 우회할 여지가 남습니다. [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702)

9월 EF 계획은 Frame Transaction인 EIP-8141과 계정을 실제 컨트랙트 계정으로 바꾸는 제안들을 전환 경로로 다룹니다. 별도의 Draft인 [EIP-8151](https://eips.ethereum.org/EIPS/eip-8151)은 코드가 비어 있지도, 정확한 EIP-7702 위임 표시도 아닌 계정에 대해 `ecRecover`가 0을 반환하도록 제안합니다. 전환 후에도 기존 키가 토큰 `permit` 같은 컨트랙트 인증에 쓰일 수 있는 문제를 다루는 것입니다. 컨트랙트가 자체 ECDSA 검증을 구현한 경로까지 모두 해결하지는 않습니다. [EF의 계정 전환 설명](https://blog.ethereum.org/2026/09/07/protocol-priorities)

## 준비 여부는 권한 전환까지 확인해야 합니다

개발팀이 점검할 대상은 양자 컴퓨터의 출시 연도보다 구체적입니다.

- **키와 권한을 연결합니다.** 사용자 잔액 외에 관리자·복구자·브리지·업그레이드 키를 찾고 공개키가 온체인 또는 오프체인에서 드러나는 경로를 확인합니다.
- **키 재사용을 줄이고 노출을 기록합니다.** 비트코인의 새 해시형 출력도 첫 지출 때 키를 공개하므로 이를 영구적인 양자 안전성으로 취급하지 않습니다.
- **새 서명과 기존 우회 경로를 함께 시험합니다.** 포스트양자 검증, 복구·백업·키 교체, 기존 ECDSA 권한의 폐기까지 한 시나리오에서 검증해야 합니다. 다중서명도 모든 키가 같은 취약한 수학에 의존하면 그 자체로 양자 내성을 주지 않습니다.
- **추정·시연·활성화를 따로 추적합니다.** 자원 추정에는 오류율·연결 구조·실행 시간·실패 확률이, 업그레이드에는 클라이언트 구현·테스트·활성화·실제 사용자 이동이 필요합니다.

이는 [BIP-360의 노출 분석](https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki), [EIP-8151의 권한 문제](https://eips.ethereum.org/EIPS/eip-8151), [EF의 전환 계획](https://blog.ethereum.org/2026/09/07/protocol-priorities)을 실제 시스템에 적용할 때의 점검 기준입니다. 오류 수정 연구나 회로 최적화가 진전됐다는 사실을 특정 연도에 모든 코인이 위험해진다는 예측으로 바꿀 근거는 없습니다. 방어가 끝났다는 판단도 새 알고리즘의 이름보다, 남아 있는 키와 권한 경로를 기준으로 내려야 합니다.

## 함께 보면 좋을 자료

- [BIP-341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki): 출력 공개키와 두 지출 경로의 규칙.
- [NIST SP 800-208](https://csrc.nist.gov/pubs/sp/800/208/final): 상태형 해시 서명의 키 관리 조건.
- [Post-Quantum Ethereum](https://pq.ethereum.org/): 계층별 연구와 공개 구현으로 이어지는 공식 허브.

## 참고 자료

- [Securing Elliptic Curve Cryptocurrencies against Quantum Vulnerabilities](https://arxiv.org/html/2603.28846v2): Babbush 외, II~III절·부록, 조회일 2026-10-16(KST).
- [Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms](https://arxiv.org/html/2606.02235v1): André Schrottenloher, 표 1~2, 조회일 2026-10-16(KST).
- [Computing 256-bit elliptic curve discrete logarithms in 26 days](https://arxiv.org/html/2609.05625v1): II.3절·V부·부록 E, 조회일 2026-10-16(KST).
- [ECDSA.Fail](https://arxiv.org/html/2609.09582v2): 실험 결과·한계, 조회일 2026-10-16(KST).
- [BIP-141](https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki): SegWit 규칙, 조회일 2026-10-16(KST).
- [BIP-340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki): secp256k1 Schnorr, 조회일 2026-10-16(KST).
- [BIP-341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki): Taproot 규칙, 조회일 2026-10-16(KST).
- [BIP-360](https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki): P2MR 제안, 조회일 2026-10-16(KST).
- [BIP-361](https://github.com/bitcoin/bips/blob/master/bip-0361.mediawiki): 전환·구제 제안, 조회일 2026-10-16(KST).
- [Grover’s algorithm](https://xlinux.nist.gov/dads/HTML/groversAlgo.html): NIST, 조회일 2026-10-16(KST).
- [Quantum error correction below the surface code threshold](https://www.nature.com/articles/s41586-024-08449-y): Google Quantum AI and Collaborators, Nature, 조회일 2026-10-16(KST).
- [FIPS 203](https://csrc.nist.gov/pubs/fips/203/final): NIST, ML-KEM, 조회일 2026-10-16(KST).
- [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final): NIST, ML-DSA, 조회일 2026-10-16(KST).
- [FIPS 205](https://csrc.nist.gov/pubs/fips/205/final): NIST, SLH-DSA, 조회일 2026-10-16(KST).
- [SP 800-208](https://csrc.nist.gov/pubs/sp/800/208/final): NIST, 상태형 해시 서명, 조회일 2026-10-16(KST).
- [Post-Quantum Ethereum](https://pq.ethereum.org/): 이더리움 재단 연구팀, 조회일 2026-10-16(KST).
- [EF Protocol: Current and Emerging Priorities](https://blog.ethereum.org/2026/09/07/protocol-priorities): EF Protocol 클러스터, 2026-09-07, 조회일 2026-10-16(KST).
- [Post-quantum cryptography on Ethereum](https://ethereum.org/roadmap/security/quantum-resistance/): ethereum.org, 조회일 2026-10-16(KST).
- [Ethereum accounts](https://ethereum.org/developers/docs/accounts/): ethereum.org, 조회일 2026-10-16(KST).
- [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844): blob과 KZG 검증 규칙, 조회일 2026-10-16(KST).
- [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702): 코드 위임 규칙, 조회일 2026-10-16(KST).
- [EIP-8151](https://eips.ethereum.org/EIPS/eip-8151): 컨트랙트 인증의 기존 키 제한 제안, 조회일 2026-10-16(KST).
