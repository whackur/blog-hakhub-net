---
title: "Paladin의 Pente·Noto·Zeto: 비공개 데이터와 결제 검증의 경계"
description: "Besu와 Paladin의 역할부터 Pente 그룹 승인, Noto notary, Zeto 영지식 증명, 같은 원장의 DvP 결제까지 설명합니다."
meta_title: ""
date: 2026-11-10T07:13:48Z
lastmod: 2026-11-10T08:20:54Z
image: "/images/posts/paladin-pente-noto-zeto-privacy/cover.png"
categories: ["Blockchain"]
tags: ["besu", "paladin", "pente", "noto", "zeto", "privacy", "atomic-settlement"]
author: "whackur"
translationKey: "paladin-pente-noto-zeto-privacy"
slug: "paladin-pente-noto-zeto-privacy"
draft: false
---

Besu와 Paladin을 함께 쓸 때 Pente·Noto·Zeto의 차이는 **공유 EVM 원장에 어떤 검증 규칙을 기록하고, 비공개 데이터를 누가 보며, 누가 상태 전이를 검증하는가**에 있습니다. Pente는 그룹이 같은 EVM 계산을 재실행해 승인합니다. Noto는 거래 내용을 아는 notary가 토큰 전이를 검사합니다. Zeto는 선택한 회로의 규칙을 영지식 증명으로 검증합니다. 세 방식은 서로 다른 신뢰 조건을 유지하면서 같은 원장에서 결제할 수 있습니다. [Paladin 프로그래밍 모델](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/programming_model.md) · [Atomic Interop](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/atomic_interop.md)

## Besu는 공유 원장, Paladin은 비공개 실행 조정

Besu는 Ethereum Virtual Machine(EVM)을 실행하는 클라이언트입니다. 공유 체인에서 거래 순서와 계약 실행을 처리하며 네트워크의 합의 규칙을 따릅니다. Paladin은 그 위에서 별도로 실행되는 런타임입니다. 비공개 상태를 보관하고 필요한 참여자에게 전달하며 도메인별 실행·서명·증명 생성과 최종 원장 제출을 조정합니다. Besu에 붙여 모든 거래를 일괄 암호화하는 모듈로 이해하면 데이터 경계를 놓칩니다. [공식 계층 설명](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/ledger_layers.md) · [데이터 전달과 registry](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/data_and_registry.md)

Paladin의 도메인은 공개 계약과 오프체인 구현을 함께 묶습니다. 공개 계약이 승인이나 proof를 검사하는 동안 원문 데이터는 해당 데이터를 받은 Paladin 노드에 남습니다. 여기서 ‘공개 원장’은 참가자가 공유하는 기반 원장이라는 뜻이며 Ethereum 메인넷으로 한정하지 않습니다. 허가형 Besu 네트워크에서도 이 구분은 같습니다. 고객 인증·계정계·회계·법적 권리 장부는 별도 업무 시스템의 영역입니다. [공유 원장과 기관별 업무 계층](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/ledger_layers.md)

설명 기준은 Paladin 소스 `656bedd8a7192be7b3a7a06efabf6ff1769104c6`과 Zeto 소스 `dd495492f540c5f71988d15f8d3eb2b0d93c5099`입니다. 2026-11-10 조회한 코어 릴리스는 정식 `v1.0.0`(2026-06-25 UTC), 프리릴리스 `v1.0.1-rc.1`(2026-09-28 UTC)이며 operator 태그는 별도입니다. 아래 소스 스냅샷의 기능을 모두 v1.0.0 지원 기능으로 읽어서는 안 됩니다. [릴리스 메타데이터](https://api.github.com/repos/LFDT-Paladin/paladin/releases?per_page=10)

## 세 도메인의 데이터와 검증 경계

UTXO(Unspent Transaction Output)는 아직 소비하지 않은 상태 조각입니다. 거래는 기존 입력을 소비하고 새 출력을 만듭니다. 이 모델을 공유하더라도 상태의 내용과 유효성을 판단하는 방법은 도메인마다 다릅니다. [Paladin state store](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/state_store.md)

| 구분 | Pente | Noto | Zeto |
| --- | --- | --- | --- |
| 실행 대상 | 그룹 안의 EVM 계약 | notary 기반 토큰 | 회로 기반 토큰 |
| 비공개 상태 | 계정·code·storage·nonce | owner·amount·salt 코인 | 값·salt·소유 키 등 commitment 원문 |
| 검증 주체 | 그룹 재실행·endorsement, 원장은 서명·상태 검사 | notary가 소유·수량 검사, 원장은 권한·소비 검사 | verifier가 proof·공개 입력 검사, 계약이 중복 소비 차단 |
| 데이터를 보는 주체 | 해당 privacy group 멤버 | notary와 상태를 배포받은 당사자, hooks의 해당 그룹 | 소유자·수취자, 암호화·감사자 변형에 따른 지정 주체 |
| 적합한 용도·제약 | 비공개 업무 로직, 그룹 승인·데이터 가용성 필요 | 발행자 감독 자산, notary 신뢰·가용성 필요 | 값·소유 정보 은닉, 회로·키·변형 정합 필요 |

표는 [Pente](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/pente.md), [Noto](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/noto.md), [Zeto 기본 개념](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/concepts/basics.md)을 비교한 것입니다. 임의 Solidity 계약을 Zeto에 넣으면 자동으로 비공개 증명 회로가 되는 것은 아닙니다. 아래 개념도도 같은 문헌의 데이터 경계와 원장 검증 기준만 재구성했으며 노드 수나 실제 배포 연결을 나타내지 않습니다.

![Pente의 그룹 승인, Noto의 notary 검사, Zeto의 proof 검증이 공유 EVM 원장에 연결되는 개념도](/images/posts/paladin-pente-noto-zeto-privacy/verification-ko.svg)

## 요청부터 원장 확정까지

Paladin의 공통 흐름은 assemble, endorse 또는 proof 확보, prepare, 기반 원장 commit과 이벤트 색인으로 읽을 수 있습니다. 각 도메인이 같은 메시지를 같은 횟수로 주고받는다는 뜻은 아닙니다. [도메인 lifecycle 정의](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/toolkit/proto/protos/to_domain.proto)

1. **Assemble**: 사용할 입력 상태를 고르고 실행 결과나 증명 입력을 구성합니다. 필요한 상태가 아직 없는 `PARK`와 업무 실행 실패인 `REVERT`는 구분됩니다.
2. **Endorse·증명 확보**: 도메인이 요구하는 재실행·서명·proof를 확보합니다. 모든 도메인에서 모든 노드가 동일한 합의에 참여하는 구조는 아닙니다.
3. **Prepare**: 최종 호출할 계약 ABI(Application Binary Interface, 호출 인코딩 규격)와 인자를 만듭니다. 준비된 호출을 앱이 나중에 제출하는 경로도 있습니다.
4. **Commit·색인·배포 확인**: 공유 EVM 계약이 권한·proof·상태 소비 조건을 검사합니다. Paladin은 원장 이벤트를 색인하고 로컬 상태와 receipt를 갱신합니다. 비공개 상태 전달은 앞선 준비·검증에도 필요하므로 commit 뒤의 단일 단계로만 보지 않습니다.

Assemble이 성공해도 경쟁 거래가 입력을 먼저 소비하면 최종 제출은 실패할 수 있습니다. `prepared`는 결제 완료가 아닙니다. Receipt의 `indexed`는 해당 노드의 색인 시각이고 `sequence`는 로컬 전달 순서입니다. 전역 순서는 기반 체인의 거래 위치로 확인해야 하며 체인의 확정 정책과 법적·외부 지급 최종성도 따로 판단합니다. [TransactionReceipt 정의](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/reference/types/transactionreceipt.md) · [업무 계층의 범위](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/ledger_layers.md)

## Pente의 private EVM과 그룹 신뢰

### 계정 상태를 UTXO로 소비합니다

Pente는 privacy group마다 독립된 EVM world state, 즉 계정 상태 집합을 유지합니다. 그룹 안에서 계정의 nonce·balance·code·storage를 읽어 실행합니다. 바뀐 계정의 이전 상태를 입력으로 소비한 뒤 새 상태를 출력합니다. 같은 주소여도 그룹이 다르면 상태와 nonce가 별개입니다. Paladin은 Besu EVM 코드를 Java 모듈로 불러 필요한 때 실행하며 이를 위해 Paladin마다 완전한 Besu 노드와 Besu 상태 DB를 함께 둘 필요는 없습니다. [Pente 상태 모델과 ephemeral EVM](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/pente.md)

수정하지 않고 읽은 기존 계정은 `reads`로 기록합니다. 공유 계약은 입력이 미소비 상태인지 확인하고 소비합니다. read 상태는 여전히 유효한지 확인하되 소비하지 않습니다. 따라서 같은 계정의 서로 다른 storage slot을 바꾸는 두 요청도 계정 상태 입력이 같으면 충돌할 수 있습니다. 읽었던 상태가 먼저 바뀌어도 다시 조립해야 할 수 있습니다. `info`는 서명된 실행 입력 같은 전달용 상태를 연결하며 소비 대상 UTXO와 역할이 다릅니다. [공개 계약의 inputs·reads·outputs·info 처리](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/solidity/contracts/domains/pente/PentePrivacyGroup.sol)

### 재실행과 endorsement가 계산을 보증합니다

그룹의 endorser는 받은 입력·read 상태와 서명된 EVM 거래를 다시 실행하고 제안된 출력과 맞는지 검사합니다. Endorsement는 특정 상태 전이에 대한 승인 서명입니다. 입력·읽기·출력·info ID와 외부 호출 목록을 묶어 서명하므로 단순히 거래를 열람했다는 표시보다 강한 의미를 갖습니다. 공유 원장은 이 서명과 상태 ID 규칙을 검사하며 private Solidity 계산 전체를 다시 실행하지 않습니다. [Pente assemble·endorse 구현](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/domains/pente/src/main/java/io/kaleido/paladin/pente/domain/PenteDomain.java) · [전이 해시와 서명 검증](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/solidity/contracts/domains/pente/PentePrivacyGroup.sol)

이 보증은 필요한 endorser들이 올바른 상태를 받아 같은 계산을 검증한다는 신뢰에 의존합니다. 공개 계약에는 threshold, 즉 필요한 서명 수를 검사하는 코드가 있지만 고정 소스의 Java 그룹 생성 경로는 resolved endorser 전원의 승인인 **100%**로 설정합니다. 이를 임의 M-of-N 운영 지원으로 해석하면 안 됩니다. 전원 승인이 필요한 그룹에서는 한 멤버의 중단도 진행에 영향을 줍니다. [그룹 생성과 threshold 설정](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/domains/pente/src/main/java/io/kaleido/paladin/pente/domain/PenteDomain.java)

### 그룹 안의 가시성과 공개 외부 호출

그룹의 비공개 상태와 실행 입력은 해당 그룹 멤버에게 공유됩니다. 그룹 밖의 원장 관찰자도 상태 ID 배열·서명·호출 시점·그룹 계약과 공개 설정을 볼 수 있습니다. 검토한 API와 계약에는 일반적인 멤버 추가·삭제·교체 경로가 확인되지 않았습니다. 업그레이드 기능을 멤버 변경 API로 대신 설명할 수는 없습니다. 신규 멤버가 과거 실행을 재현하려면 어떤 private 데이터를 받아야 하는지도 별도 절차로 정해야 합니다. 공유 체인의 해시만으로 유실된 계정 원문을 복원할 수는 없습니다. [privacy group API](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/reference/apis/pgroup.md) · [그룹 설정과 상태 가용성](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/domains/pente/src/main/java/io/kaleido/paladin/pente/domain/PenteDomain.java) · [그룹 계약](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/solidity/contracts/domains/pente/PentePrivacyGroup.sol)

`externalCallsEnabled`를 켠 그룹은 private 계약의 `PenteExternalCall` 이벤트로 공개 계약 호출을 요청할 수 있습니다. 그 대상과 calldata는 endorsement에 결합됩니다. 기반 EVM에서 그룹 계약이 실제 호출합니다. 같은 트랜잭션에서 외부 호출이 revert하면 Pente 상태 전이도 되돌아갑니다. 다만 공개 호출의 주소와 인자에 넣은 데이터는 공개됩니다. 비밀 업무 입력을 그대로 넘겨서는 안 됩니다. [외부 호출 추출과 설정](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/domains/pente/src/main/java/io/kaleido/paladin/pente/domain/PenteDomain.java) · [외부 호출 실행](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/solidity/contracts/domains/pente/PentePrivacyGroup.sol)

## Noto의 notary와 토큰 정책

### 금액을 검사하는 주체는 notary입니다

Noto 코인은 `owner`, `amount`, 무작위 `salt`를 담습니다. 공개 원장에는 상태 ID가 남고 원문은 private 채널로 전달됩니다. 예를 들어 100인 입력에서 70을 이전하면 수취자용 70과 송신자 거스름 30을 새 출력으로 만듭니다. Notary는 요청자 서명·소유권·출력 수량을 확인하고 일반 이전의 값 보존을 검사합니다. **민감한 수량이 notary에게도 숨겨지는 모델은 아닙니다.** [Noto 상태와 notary 검증](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/noto.md)

표준 Noto 공개 계약은 notary 권한과 입력 상태의 미소비 여부를 강제합니다. 원장 노드가 숨겨진 금액을 복원해 입력 합계와 출력 합계를 재계산하는 구조는 아닙니다. `mint`는 발행 출력을 만듭니다. `transfer`는 기존 입력을 수취자·거스름 출력으로 바꾸며 `burn`은 소각량을 제외한 출력을 만듭니다. 발행·소각 허용 정책과 올바른 금액 검사는 notary 측 검증에 달려 있습니다. [작업별 private 요청](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/noto.md) · [표준 Noto 공개 계약](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/solidity/contracts/domains/noto/Noto.sol)

`basic` 모드에는 발행 제한·소각·잠금 설정이 있습니다. `hooks` 모드는 Pente private 계약에서 업무 규칙을 검사하도록 연결합니다. 예를 들어 이전 한도나 발행 권한을 그룹 안에서 관리할 수 있습니다. 이때도 notary는 검증 경로에 남습니다. hook 그룹 멤버는 전달받은 인자와 정책 상태를 봅니다. Basic의 기본 제한은 hooks에 자동 승계되지 않으므로 필요한 정책을 hook에 명시해야 합니다. [Notary logic과 hooks](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/noto.md)

### 잠금·위임·승인은 서로 다른 동작입니다

잠금은 자산을 결제용으로 묶는 단계이고 prepare는 허용할 소비 결과를 구성하는 단계입니다. 고정 소스의 표준 V2 경로는 잠금에 정상 소비 `spend`와 취소 `cancel` 결과의 commitment를 준비합니다. `delegateLock`으로 실행권을 지정 spender에게 넘깁니다. 준비와 위임이 끝난 잠금은 해당 spender가 약정된 인자로 소비하거나 취소할 수 있습니다. 취소도 사전 약정 출력에 구속되며 임의 회수권은 아닙니다. 인터페이스가 자동 만료나 owner의 강제 회수를 보장하지 않으므로 조정 계약의 취소 경로가 중요합니다. [Noto V2 잠금 실행](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/solidity/contracts/domains/noto/Noto.sol) · [ILockableCapability 권한 규칙](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/solidity/contracts/domains/interfaces/ILockableCapability.sol)

Noto private API에 ERC-20 allowance 같은 별도 `approve()`가 있는 것은 아닙니다. Pente의 `approveTransition`은 특정 전이를 특정 delegate가 실행하도록 승인하는 별도 기능입니다. 개발자는 private 요청 API와 공개 계약 ABI도 구분해야 합니다. 고정 문서의 구형 lock API와 소스 V2의 `ILockableCapability` 호출이 일치하지 않는 구간이 있으므로 token variant·factory·실제 ABI를 맞춰야 합니다. [문서의 private·public ABI](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/noto.md) · [V2 구현](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/solidity/contracts/domains/noto/Noto.sol) · [Pente 승인 함수](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/solidity/contracts/domains/pente/PentePrivacyGroup.sol)

데이터 경계에도 같은 구분이 필요합니다. 정상 Noto private 요청의 `data`·`unlockData` 원문은 private info state에 담깁니다. 공개 ABI의 동명 `data`에는 도메인이 info-state 참조 등을 인코딩하며 요청 원문을 그대로 넣는다는 뜻이 아닙니다. 반대로 공개 Solidity calldata나 이벤트에 직접 실은 bytes는 공개 정보입니다. [private info state 생성](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/domains/noto/internal/noto/states.go) · [공개 데이터 인코딩](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/domains/noto/internal/noto/noto.go)

## Zeto의 commitment와 증명

### 원문을 숨기고 전이 규칙을 증명합니다

Zeto는 영지식 증명(Zero-Knowledge Proof, ZKP) 기반 토큰 구현 모음입니다. Fungible 토큰의 commitment는 값·salt·소유자 BabyJubjub 공개 키를 해시로 묶은 표현입니다. 소유자는 이 해시를 만드는 원문인 opening과 비밀 키를 보관합니다. 토큰의 지출 권한은 BabyJubjub 키로 증명하며 체인에 거래를 제출하는 EVM 주소와 소유자가 같을 필요는 없습니다. [Commitment와 지출 권한](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/concepts/basics.md) · [키와 데이터 전달](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/concepts/how-zeto-works.md)

송신자는 입력 opening·비밀 키·출력 데이터를 witness, 즉 증명 계산에 필요한 비공개 입력과 중간 값으로 사용합니다. 회로는 소유권, 입력과 출력의 값 보존, 출력 범위 등 선택된 규칙을 계산합니다. 공개 계약의 verifier는 proof와 공개 입력이 그 규칙을 만족하는지 검사합니다. 따라서 일반적인 비공개 업무 계약의 모든 조건이 자동 검증되는 것이 아니라 선택한 회로가 표현하는 조건이 보증 범위입니다. [Anon 회로의 검증 명제](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/implementations/anon.md) · [증명 산출물과 verifier](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/zkp/circuits/README.md)

### Anon·AnonEnc·AnonNullifier의 차이

`Zeto_Anon`은 값과 소유 정보를 commitment로 가리지만 소비 입력과 새 출력의 연결은 공개됩니다. 수취자가 나중에 지출하려면 값·salt 같은 opening을 안전한 별도 채널로 받아야 합니다. `Zeto_AnonEnc`는 수취자용 암호문을 거래에 포함해 opening 전달을 돕습니다. 암호문이 추가돼도 입력·출력 연결은 남습니다. [Anon](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/implementations/anon.md) · [AnonEnc](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/implementations/anon_enc.md)

`Zeto_AnonNullifier`는 소비할 입력 commitment를 직접 드러내는 대신 nullifier를 공개합니다. Nullifier는 입력 값·salt·소유 비밀 키로부터 계산하는 일회 소비 표식입니다. 같은 입력의 재사용은 같은 nullifier를 내므로 계약이 막습니다. 다만 nullifier만으로 입력 자산의 존재를 증명할 수는 없습니다. 그래서 등록된 commitment들을 요약한 Merkle root와 그 안에 실제 입력이 있다는 membership 경로를 proof에 결합합니다. 관찰자는 proof의 유효성을 확인하면서도 어느 commitment를 소비했는지 직접 읽지 못합니다. [Nullifier와 Merkle membership](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/implementations/anon_nullifier.md)

이 변형은 수취자용 암호화를 자동으로 포함하지 않습니다. Nullifier, Merkle root, 출력 commitment, 제출 주소와 시점은 계속 공개됩니다. Nullifier가 없는 변형의 거래 그래프와 nullifier 변형의 통계적 연결 가능성을 구분해야 하며 공개 입출금의 금액·주소·타이밍이나 민팅 활동까지 모두 숨겨진다고 설명할 수는 없습니다. [공개 입력 구조](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/implementations/anon_nullifier.md) · [공개 토큰의 deposit·withdraw 경계](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/advanced/shield-unshield.md)

### KYC·감사자 기능과 Paladin 지원 범위

`Zeto_AnonNullifierKyc`는 고객확인(KYC) registry에 송신자와 수취자 키가 포함됐다는 조건을 transfer proof에 더합니다. Registry의 등록 권한과 키 관리가 신뢰 조건이며 등록 이벤트에는 공개 키와 `data`가 남습니다. Membership 증명만으로 법적 실명 검증이나 규제 적합성이 완성되지는 않습니다. 별도 `NonRepudiation` 변형은 지정 authority 키로 소유 정보 암호문을 열도록 설계합니다. 이 선택적 감사 권한도 키 보안과 접근 정책에 의존합니다. [KYC 변형](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/implementations/anon_nullifier_kyc.md) · [등록 이벤트](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/solidity/contracts/lib/registry.sol) · [NonRepudiation 변형](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/implementations/anon_enc_nullifier_non_repudiation.md)

Standalone Zeto의 변형 전체가 Paladin 내장 지원은 아닙니다. 고정 Paladin 소스에 이름이 정의된 fungible 변형은 `Zeto_Anon`, `Zeto_AnonEnc`, `Zeto_AnonNullifier`, `Zeto_AnonNullifierKyc`입니다. 암호화·nullifier·KYC를 결합한 모든 변형이나 authority 감사 변형까지 이 목록에 있다고 볼 수 없습니다. 실제 사용에서는 domain·계약·회로·verifier를 한 조합으로 고정해야 합니다. [Paladin 지원 이름](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/domains/zeto/pkg/constants/constants.go) · [Standalone 구현 목록](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/implementations/index.md)

## Noto 펀드와 Zeto 대금을 함께 결제하는 DvP

매도자가 Noto 펀드 토큰을, 매수자가 Zeto 대금 토큰을 보유한다고 가정합니다. 두 당사자의 Pente 그룹 계약은 주문 조건과 결제 진행 상태를 관리합니다. DvP(Delivery versus Payment)는 자산 인도와 지급을 함께 실행하는 거래입니다. 이 예시는 공식 Atomic Interop의 fund·cash·private logic 구성을 바탕으로 하며 Zeto 대금이 외부 은행 예금과 동일한 법적 지급수단이라는 가정은 하지 않습니다. [공식 DvP 구성](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/atomic_interop.md)

당사자는 private 업무 상태를 합의하고 각 자산의 입력과 출력을 준비합니다. Noto 측에서는 notary가 펀드 이전을 검증합니다. Zeto 측에서는 선택한 토큰 규칙에 맞는 proof를 준비합니다. Pente 그룹은 결제 상태 전이를 재실행해 endorsement를 모읍니다. 이어 고정된 호출 목록을 실행할 swap 계약 주소에 필요한 실행 권한을 부여합니다. 이 준비·승인은 여러 EVM 거래일 수 있고 어느 한쪽만 준비된 중간 상태도 존재합니다. 구체적인 잠금·승인 방식은 사용 버전과 token variant에 맞춰야 합니다. [Pre-approval·prepare 단계](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/atomic_interop.md)

최종 `execute()`는 하나의 EVM 트랜잭션에서 펀드 이전, 대금 이전, Pente 상태 전이를 호출합니다. 모든 leg, 즉 각 결제 부분이 성공하거나 해당 트랜잭션 전체가 revert됩니다. 다만 이 원자성은 앞서 완료된 준비 거래를 없애거나 수취자의 private payload 수신을 보장하지 않습니다. 준비된 잠금의 취소, 중단 뒤 재시도, 수취자의 opening 보존은 별도 책임입니다. [Execution·commit 단계](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/atomic_interop.md)

이 구조를 여러 Pente 그룹의 계정 상태를 한 전이가 직접 교차 소비하는 일반 기능으로 확대할 수는 없습니다. 고정 그룹 계약은 그 기능을 TODO로 남깁니다. 원자성 경계도 같은 기반 EVM 트랜잭션까지입니다. 다른 체인이나 은행송금, 외부 권리 장부를 포함한 end-to-end 원자성에는 별도 조정과 대사가 필요합니다. [교차 그룹 지원 경계](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/solidity/contracts/domains/pente/PentePrivacyGroup.sol) · [외부 업무 계층](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/ledger_layers.md)

## 운영 전 확인할 항목

다음 항목은 위 구조에서 도출되는 운영 점검입니다. 이 글은 공식 문서와 고정 소스를 읽은 설명이며 실제 노드 기동·회로 proof 생성·장애 주입·독립 보안 감사·성능 벤치마크는 수행하지 않았습니다.

- **버전과 증명 산출물**: 코어·도메인·factory·ABI를 맞추고 Zeto 회로·WASM·proving key·verification key·배포 verifier가 같은 생성물인지 확인합니다. 기본 생성 키와 체크인 verifier는 테스트용이라는 안내가 있으므로 운영용 Groth16 setup과 verifier 재생성이 필요합니다. KYC도 tree·witness·public input의 정합을 실제 선택 조합에서 확인해야 합니다. [Zeto artifact와 production setup 안내](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/zkp/circuits/README.md)
- **키·private state·DB 복구**: 원장 해시만으로 원문을 재생성할 수 없습니다. 백업한 상태와 키로 기존 자산을 실제 소비하고 그룹 재실행·수취자 opening 복구까지 되는지 확인합니다. HSM 연동만으로 ZK witness 계산의 모든 비밀이 HSM 내부에 남는다고 가정하지 않습니다. [상태 저장](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/state_store.md) · [키 저장과 in-memory proving](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/key_management.md)
- **경쟁·재조직·재시도·취소**: 동시 소비, stale Merkle 경로, 원장 재조직 뒤 색인 복구, execute와 cancel 경합을 시험합니다. 업무 intent와 원래 transaction을 연결해 멱등성(idempotency, 중복 처리 방지)을 관리해야 합니다. 문서상 같은 `idempotencyKey` 재제출은 409 Conflict이며 원래 응답이 자동 재생된다는 계약은 아닙니다. [TransactionInput의 멱등키 계약](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/reference/types/transactioninput.md)
- **Notary·멤버 장애**: Noto의 검증자나 Pente 필수 endorser가 멈췄을 때 신규 거래와 이미 준비된 잠금의 진행 가능성을 나눠 확인합니다. 위임된 lock의 spend·cancel 권한과 private 데이터 복구는 서로 다른 문제입니다. [잠금 권한](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/solidity/contracts/domains/interfaces/ILockableCapability.sol) · [전원 endorsement 경로](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/domains/pente/src/main/java/io/kaleido/paladin/pente/domain/PenteDomain.java)

도메인을 고를 때는 숨길 필드만 나열해서는 부족합니다. Pente에서는 어느 그룹이 계산을 함께 검증하는지, Noto에서는 누구에게 금액과 정책 판단을 맡기는지, Zeto에서는 어느 회로 명제와 공개 신호를 허용하는지가 설계를 결정합니다. 같은 원장에서 결제한다는 조건 위에 이 데이터 접근권과 검증 책임을 명시해야 합니다.

## 함께 보면 좋을 자료

- [Paladin Programming Model](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/programming_model.md): 공개 계약과 오프체인 도메인이 함께 동작하는 방식입니다.
- [Atomic Interop](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/atomic_interop.md): 준비·승인과 최종 단일 원장 실행을 구분하는 공식 예시입니다.
- [How Zeto tokens work](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/concepts/how-zeto-works.md): 소유 키와 수취자에게 전달할 비공개 데이터의 관계를 설명합니다.

## 참고 자료

조회일은 2026-11-10입니다. 본문의 GitHub 파일 링크는 위 고정 commit을 기준으로 합니다.

- [Paladin Ledger Layers](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/ledger_layers.md) · [Data and Registry](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/data_and_registry.md) · [State Store](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/state_store.md) · [Key Management](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/key_management.md)
- [Pente architecture](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/pente.md) · [PenteDomain.java](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/domains/pente/src/main/java/io/kaleido/paladin/pente/domain/PenteDomain.java) · [PentePrivacyGroup.sol](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/solidity/contracts/domains/pente/PentePrivacyGroup.sol) · [Privacy Group API](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/reference/apis/pgroup.md)
- [Noto architecture](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/architecture/noto.md) · [Noto.sol](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/solidity/contracts/domains/noto/Noto.sol) · [ILockableCapability.sol](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/solidity/contracts/domains/interfaces/ILockableCapability.sol) · [Noto state preparation](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/domains/noto/internal/noto/states.go) · [Noto transaction data encoding](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/domains/noto/internal/noto/noto.go)
- [Zeto Basics](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/concepts/basics.md) · [Anon](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/implementations/anon.md) · [AnonEnc](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/implementations/anon_enc.md) · [AnonNullifier](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/implementations/anon_nullifier.md) · [KYC](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/implementations/anon_nullifier_kyc.md) · [KYC registry](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/solidity/contracts/lib/registry.sol) · [NonRepudiation](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/implementations/anon_enc_nullifier_non_repudiation.md)
- [Zeto implementation index](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/implementations/index.md) · [Paladin Zeto constants](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/domains/zeto/pkg/constants/constants.go) · [Shield and unshield](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/doc-site/docs/advanced/shield-unshield.md) · [Circuit artifacts and setup](https://github.com/LFDT-Paladin/zeto/blob/dd495492f540c5f71988d15f8d3eb2b0d93c5099/zkp/circuits/README.md)
- [Domain lifecycle protocol](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/toolkit/proto/protos/to_domain.proto) · [TransactionReceipt](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/reference/types/transactionreceipt.md) · [TransactionInput](https://github.com/LFDT-Paladin/paladin/blob/656bedd8a7192be7b3a7a06efabf6ff1769104c6/doc-site/docs/reference/types/transactioninput.md) · [Paladin releases](https://api.github.com/repos/LFDT-Paladin/paladin/releases?per_page=10)
