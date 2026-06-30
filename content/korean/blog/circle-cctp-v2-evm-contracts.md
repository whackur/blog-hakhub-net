---
title: "Circle CCTP V2 EVM 컨트랙트 파헤치기"
meta_title: ""
description: "Circle CCTP V2의 TokenMessengerV2·MessageTransmitterV2·TokenMinterV2 세 컨트랙트가 역할을 어떻게 나누는지, 번-앤-민트 라이프사이클과 메시지 레이아웃·수수료 모델·hookData·destinationCaller 작동 방식을 소스코드 기준으로 정리했습니다."
date: 2026-06-30T17:30:00+09:00
lastmod: 2026-06-30T17:30:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["cctp", "circle", "usdc", "cross-chain", "solidity"]
author: "whackur"
translationKey: "circle-cctp-v2-evm-contracts"
draft: false
---

퍼블릭 블록체인에서 USDC를 다른 체인으로 옮기는 방법은 크게 두 가지다. 원본 토큰을 한 쪽에 잠그고 래핑된 버전을 다른 쪽에 찍어내는 락-앤-민트, 그리고 소스 체인에서 태워버리고 목적지 체인에서 동일한 양을 다시 찍어내는 번-앤-민트. Circle이 개발한 [CCTP(Cross-Chain Transfer Protocol)](https://developers.circle.com/stablecoins/cctp-getting-started)는 후자다.

래핑 USDC 없이 네이티브 USDC만 쓴다는 것이 차별점이다. 브리지를 타면서 서로 다른 "USDC" 버전이 생기는 문제를 근본적으로 없앤다. 이 글은 CCTP V2의 EVM 컨트랙트를 소스코드 수준에서 살펴본다. V1과의 차이, 세 컨트랙트의 역할 분리, 메시지 포맷, 번과 민트 라이프사이클, V2에서 추가된 수수료 모델·hookData·fast finality까지 다룬다.

## 왜 번-앤-민트인가

락-앤-민트 방식의 가장 큰 문제는 소스 체인의 잠금 컨트랙트다. 단일 스마트 컨트랙트에 집중된 TVL은 그 자체로 대규모 익스플로잇의 주요 표적이 된다.

번-앤-민트에서는 잠금이 없다. 소스 체인의 USDC는 진짜로 소각된다. Circle이 그 소각을 확인하고 목적지 체인에 같은 양을 민트할 권한을 가진다. 중앙화된 신뢰는 있지만, 거대한 TVL 잠금이 없다.

Circle이 이 권한을 독점한다는 점은 트레이드오프다. Circle이 오프라인이 되거나 서비스를 중단하면 전송이 멈춘다. 탈중앙화와 보안 면에서의 장단점을 알고 쓰는 것이 중요하다.

## 세 컨트랙트의 역할 분리

CCTP V2 EVM 구현은 세 컨트랙트가 서로 다른 관심사를 맡는다. 소스코드는 [circlefin/evm-cctp-contracts](https://github.com/circlefin/evm-cctp-contracts) GitHub 레포에 공개되어 있다.

| 컨트랙트 | 역할 | 호출 주체 |
|----------|------|-----------|
| `TokenMessengerV2` | 사용자 진입점. 번 요청 접수, 민트 실행 | 사용자 EOA 또는 컨트랙트 |
| `MessageTransmitterV2` | 체인 간 메시지 라우팅, 어테스테이션 검증 | TokenMessengerV2, 릴레이어 |
| `TokenMinterV2` | 토큰 소각·민트 실행, 한도 관리 | TokenMessengerV2만 |

이 분리는 UNIX의 단일 책임 원칙과 비슷하다. TokenMessengerV2는 도메인 규칙을 모른다. MessageTransmitterV2는 토큰을 모른다. TokenMinterV2는 메시지 라우팅에 무관심하다.

## TokenMessengerV2: 사용자 진입점

TokenMessengerV2는 사용자가 직접 호출하는 유일한 컨트랙트다. V2에서는 V1의 `depositForBurn` 4개 파라미터에 `destinationCaller`·`maxFee`·`minFinalityThreshold`가 추가됐다.

**depositForBurn**: 기본 번 요청.

```solidity
function depositForBurn(
    uint256 amount,
    uint32 destinationDomain,
    bytes32 mintRecipient,
    address burnToken,
    bytes32 destinationCaller,
    uint256 maxFee,
    uint32 minFinalityThreshold
) external notDenylistedCallers;
```

`mintRecipient`는 `bytes32` 타입으로, EVM 주소를 우측 정렬(좌측 제로 패딩) 형태로 인코딩한다. Solidity에서는 `bytes32(uint256(uint160(addr)))`. 솔라나처럼 32바이트 주소를 네이티브로 쓰는 체인과 포맷을 맞추기 위해서다.

`destinationCaller`가 `bytes32(0)`이면 누구나 목적지에서 `receiveMessage()`를 호출해 민트를 완료할 수 있다. 특정 릴레이어나 컨트랙트로 제한하려면 해당 주소를 넣는다. `maxFee`는 발신자가 수락 가능한 최대 수수료 상한이다(번 토큰 단위). Circle 문서는 `minFinalityThreshold <= 1000`을 Fast Transfer, `>= 2000`을 Standard Transfer(수수료 없음)로 분류한다. 컨트랙트는 수신 메시지의 `finalityThresholdExecuted`가 `FINALITY_THRESHOLD_FINALIZED`(2000) 미만이면 unfinalized 경로로, 이상이면 finalized 경로로 라우팅한다. TokenMessengerV2가 허용하는 unfinalized 임계값의 최솟값은 500이다. 반환값은 없다.

**depositForBurnWithHook**: hookData를 함께 전달하는 V2 전용 함수. `hookData`는 빈 값을 허용하지 않는다.

```solidity
function depositForBurnWithHook(
    uint256 amount,
    uint32 destinationDomain,
    bytes32 mintRecipient,
    address burnToken,
    bytes32 destinationCaller,
    uint256 maxFee,
    uint32 minFinalityThreshold,
    bytes calldata hookData
) external notDenylistedCallers;
```

민트 이후 목적지 컨트랙트에 추가 동작을 위임하는 채널이다. hookData 섹션에서 자세히 다룬다.

번 요청이 들어오면 TokenMessengerV2는 두 가지 일을 순서대로 처리한다. 먼저 `TokenMinterV2.burn()`을 불러 USDC를 소각하고, 이어서 `MessageTransmitterV2.sendMessage()`를 불러 소각 사실을 담은 메시지를 emit한다.

## MessageTransmitterV2: 메시지 라우팅과 어테스테이션

MessageTransmitterV2는 CCTP의 통신 레이어다. 토큰에 대해서는 모른다. 원시 바이트 메시지를 체인 간에 보내고 받을 뿐이다.

**sendMessage**: TokenMessengerV2가 번 완료 후 호출한다. 목적지 도메인, 수신자 컨트랙트 주소, destinationCaller, minFinalityThreshold, 메시지 바디를 받아 `MessageSent` 이벤트를 emit한다. 이벤트에 포함된 `message` 바이트가 릴레이어가 수집해야 하는 데이터다.

**receiveMessage**: 목적지 체인에서 릴레이어가 호출하는 함수다.

```solidity
function receiveMessage(
    bytes calldata message,
    bytes calldata attestation
) external returns (bool success);
```

이 함수가 하는 일은 크게 세 가지다. 첫째, 메시지 헤더에서 목적지 도메인이 로컬과 일치하는지 확인한다. 둘째, attestation의 서명을 검증한다(Circle의 어테스터 주소 집합으로). 셋째, 논스가 이미 쓰였는지 확인한 뒤 `usedNonces` 매핑에 기록한다(리플레이 방지). 이 세 가지를 통과하면 `finalityThresholdExecuted` 값에 따라 분기한다. 2000(`FINALITY_THRESHOLD_FINALIZED`) 이상이면 `handleReceiveFinalizedMessage()`를, 미만이면 `handleReceiveUnfinalizedMessage()`를 호출한다.

어테스터는 `enabledAttesters`에 등록된 Circle이 관리하는 주소 집합이다. `signatureThreshold`개 이상의 서명이 있어야 통과다. MessageTransmitterV2는 설정 가능한 M-of-N 어테스터 서명을 지원한다. 실제 배포된 임계값과 어테스터 구성은 배포된 컨트랙트나 Circle 공식 배포 문서에서 확인한다.

## TokenMinterV2: 토큰 관리

TokenMinterV2는 실제 소각과 민트를 담당한다. TokenMessengerV2만 이 컨트랙트를 호출할 수 있다. 외부에서 직접 접근하는 경로는 없다.

**주요 역할:**

`burn(address burnToken, uint256 amount)`: 소스 체인에서 USDC를 소각한다. 먼저 `burnLimitsPerMessage[burnToken]`을 넘는지 확인한다. 한도를 넘으면 reverts. 이 한도는 Chain당, 토큰당 설정된 오라클 없는 리스크 관리 메커니즘이다.

`mint()`: 목적지 체인에서 USDC를 민트한다. V2에서는 mintRecipient(사용자)와 feeRecipient(수수료 수취인)에게 각각 민트하는 이중 수신자 인터페이스를 지원한다. `remoteTokensToLocalTokens[sourceDomain][burnToken]`으로 소스 토큰 주소를 로컬 USDC 주소로 매핑한다.

**토큰 페어 등록**: `remoteTokensToLocalTokens` 매핑이 크로스체인 토큰 매핑을 담는다. 이 매핑은 Circle이 관리하며, 지원하는 토큰 쌍은 Circle 공식 문서에서 확인한다.

## 메시지 레이아웃

CCTP 메시지는 고정 길이 헤더와 가변 길이 바디로 이루어진 ABI 비호환 바이너리 포맷이다.

**메시지 헤더 (148 바이트):**

| 필드 | 타입 | 바이트 | 비고 |
|------|------|--------|------|
| version | uint32 | 4 | |
| sourceDomain | uint32 | 4 | |
| destinationDomain | uint32 | 4 | |
| nonce | bytes32 | 32 | V1의 uint64(8바이트)에서 변경 |
| sender | bytes32 | 32 | |
| recipient | bytes32 | 32 | |
| destinationCaller | bytes32 | 32 | |
| minFinalityThreshold | uint32 | 4 | V2 신규 |
| finalityThresholdExecuted | uint32 | 4 | V2 신규 (Circle이 채워 넣음) |
| **합계** | | **148** | |

V2에서 nonce는 `bytes32`(32바이트)로 바뀌었다. 발신 시점에는 빈 값(`bytes32(0)`)으로 전송되고, Circle 어테스터가 서명 전 실제 값을 채워 넣는다. `minFinalityThreshold`와 `finalityThresholdExecuted`가 새로 추가되어 헤더 전체 크기가 116바이트에서 148바이트로 늘었다.

도메인 ID는 Circle이 중앙에서 할당한다. 현재 주요 EVM 체인 도메인:

| 체인 | 도메인 |
|------|--------|
| Ethereum | 0 |
| Avalanche C-Chain | 1 |
| OP Mainnet | 2 |
| Arbitrum One | 3 |
| Base | 6 |
| Polygon PoS | 7 |

**BurnMessage 바디:**

헤더(148바이트) 이후에 오는 바디는 BurnMessageV2 포맷이다.

| 필드 | 타입 | 설명 |
|------|------|------|
| version | uint32 | BurnMessage 버전 |
| burnToken | bytes32 | 소스 체인 번 토큰 주소 |
| mintRecipient | bytes32 | 목적지 수신자 주소 |
| amount | uint256 | 전송량 |
| messageSender | bytes32 | `depositForBurn` 호출자 |
| maxFee | uint256 | 발신자가 설정한 최대 수수료 상한 |
| feeExecuted | uint256 | Circle이 실제 부과하는 수수료 (어테스터가 채워 넣음) |
| expirationBlock | uint256 | 메시지 만료 블록 번호 (0이면 만료 없음) |
| hookData | bytes | V2 신규: 임의 길이 훅 데이터 |

발신 시 `feeExecuted`와 `expirationBlock`은 `0`으로 전송된다. Circle 어테스터가 서명 전 실제 값을 채워 넣는다. `hookData`가 없으면 바디 크기는 228바이트로 고정이다.

## 번 라이프사이클

소스 체인에서 시작해 목적지 체인에서 USDC를 받기까지의 흐름:

1. **승인**: 사용자가 TokenMessengerV2에 USDC 지출 승인(`approve`)을 준다.

2. **depositForBurn 호출**: TokenMessengerV2를 호출한다. 함수 내부에서:
   - `TokenMinterV2.burn()` 호출 → USDC 소각
   - `MessageTransmitterV2.sendMessage()` 호출 → 소각 메시지 emit
   - `DepositForBurn` 이벤트와 `MessageSent` 이벤트가 같은 트랜잭션에 emit된다.

3. **이벤트 수집**: 릴레이어(또는 사용자 본인)가 `MessageSent` 이벤트에서 `message` 바이트를 추출한다.

4. **어테스테이션 요청**: Circle Iris API에 메시지 해시(keccak256)를 넘기고 어테스테이션을 기다린다.
   ```
   GET https://iris-api.circle.com/attestations/{messageHash}
   ```
   표준 경로는 소스 체인 완결성(finality)을 기다린다. Ethereum에서는 약 15~20분 소요된다.

5. **receiveMessage 호출**: 어테스테이션 status가 `complete`가 되면 목적지 체인의 MessageTransmitterV2에 `receiveMessage(message, attestation)`을 호출한다.

## 민트(수신) 라이프사이클

목적지 체인에서 `receiveMessage`가 호출된 이후:

1. **헤더 파싱**: 목적지 도메인 일치 확인.
2. **어테스테이션 검증**: 서명 수 ≥ signatureThreshold 확인.
3. **destinationCaller 확인**: 헤더의 destinationCaller가 0이 아니면 `msg.sender == destinationCaller` 검증.
4. **논스 체크**: `usedNonces[nonce]`가 사용된 적 없는지 확인하고 사용 처리.
5. **파이널리티 라우팅**: `finalityThresholdExecuted >= 2000`이면 `handleReceiveFinalizedMessage()` 호출(수수료 없음, 전액 민트), 미만이면 `handleReceiveUnfinalizedMessage()` 호출.
6. **USDC 민트**: finalized 경로는 `amount` 전액을 mintRecipient에게 민트. unfinalized 경로는 `amount - feeExecuted`를 mintRecipient에게, `feeExecuted`를 feeRecipient에게 각각 민트.
7. **hookData**: BurnMessageV2에 포함된 hookData는 릴레이어 래퍼(예: Circle의 CCTPHookWrapper)가 `receiveMessage()` 완료 후 별도로 처리한다. TokenMessenger·MessageTransmitter 자체는 hookData 기반 훅 호출을 수행하지 않는다.

논스는 bytes32 단일 키로 관리된다. 같은 메시지를 두 번 제출하면 두 번째는 revert된다.

## Fast Finality와 수수료 모델

V2의 가장 눈에 띄는 실용적 변화는 **fast transfers**다.

**Standard 경로**: 소스 체인이 최종 완결성에 도달할 때까지 기다린다. Ethereum에서는 15~20분, Arbitrum 같은 L2에서는 수분에서 수십 분. 수수료 없음.

**Fast 경로**: Circle이 소스 체인의 완결성을 기다리지 않고 빠른 어테스테이션을 발행한다. 수초에서 수분 내 USDC가 목적지에 도착한다. 대신 수수료가 발생한다.

수수료는 번 금액에서 공제된다. `amount = 100 USDC`, `fee = 1 USDC`면 mintRecipient는 `99 USDC`를 받는다. 수수료 구조와 정확한 금액은 [Circle 개발자 문서](https://developers.circle.com/stablecoins/cctp-getting-started)에서 현행 값을 확인한다.

Fast transfer는 Circle이 위험을 부담하는 구조다. 소스 체인 재편성(reorg)이 발생해 번 트랜잭션이 취소되더라도 목적지에 이미 민트가 완료된 경우, Circle이 그 손실을 감수한다. 이 위험이 수수료로 가격이 매겨진다.

## destinationCaller와 hookData

**destinationCaller**는 메시지 헤더의 bytes32 필드다. 목적지에서 `receiveMessage()`를 호출할 수 있는 주소를 제한한다.

- `0x000...000`: 제한 없음. 누구나 민트를 트리거할 수 있다.
- 특정 주소로 설정: 그 주소만 `receiveMessage()`를 호출할 수 있다. 릴레이어 컨트랙트를 쓸 때 MEV 방지 또는 원자적 실행 보장에 활용한다.

**hookData**는 V2에서 추가된 가변 길이 바이트 필드다. `depositForBurnWithHook()` 사용 시 BurnMessage 바디 끝에 붙는다.

TokenMessengerV2는 hookData를 BurnMessageV2에 저장하고 파싱하지만, hookData 기반 훅 호출은 TokenMessengerV2가 직접 수행하지 않는다. 릴레이어 래퍼(Circle의 CCTPHookWrapper 등)가 민트 완료 후 별도로 처리한다. 활용 패턴:

- 브리지 후 즉시 DEX 스왑
- 브리지 후 대출 프로토콜 예치
- 크로스체인 페이롤/결제 흐름

Circle의 참조 구현인 CCTPHookWrapper에서는 훅이 `receiveMessage()` 완료 후 별도로 실행된다. 훅이 실패해도 USDC 민팅은 이미 완료된 상태다. 이 설계는 의도적이다. 악의적인 호출자가 부족한 가스로 호출해 논스를 소모하면서 훅만 실패시키는 공격 벡터를 차단한다. 커스텀 훅을 구현할 때는 이 비원자적 실행 방식을 전제로 오류 처리와 재진입 방지를 설계해야 한다.

## 보안 모델과 신뢰 전제

CCTP의 보안 모델을 쓰기 전에 이해해야 하는 사항들:

**Circle 중앙 신뢰**: 어테스테이션을 발행하는 어테스터는 Circle이 등록하고 관리한다. MessageTransmitterV2는 설정 가능한 M-of-N 다중서명 어테스테이션을 지원하며, 실제 배포된 서명 임계값과 어테스터 구성은 배포된 컨트랙트나 Circle 공식 배포 문서에서 직접 확인해야 한다.

**리플레이 방지**: `usedNonces[nonce]` 매핑이 각 목적지 체인에서 메시지 재사용을 막는다. V2의 nonce는 bytes32 타입으로, Circle 어테스터가 서명 시 채워 넣는다.

**번 한도**: `burnLimitsPerMessage[token]`이 단일 트랜잭션에서 소각할 수 있는 최대량을 제한한다. 대규모 공격의 피해 규모를 줄이는 소극적 방어다.

**컨트랙트 업그레이드 가능성**: TokenMessengerV2와 MessageTransmitterV2는 업그레이드 가능한 프록시로 배포되어 있다. 이론적으로 Circle이 로직을 변경할 수 있다. 업그레이드 전 타임락이 있는지 [배포 주소](https://developers.circle.com/stablecoins/evm-smart-contract-addresses)의 프록시 어드민을 확인하는 것이 좋다.

**오프체인 의존성**: 어테스테이션 API(`iris-api.circle.com`)가 다운되면 전송이 대기 상태로 멈춘다. 이미 소각된 USDC는 어테스테이션 없이 민트되지 않는다. Circle 인프라가 복구되면 어테스테이션 재발급이 가능하지만, 다운 중에는 수동으로 해결할 방법이 없다.

## 통합 체크리스트

직접 CCTP V2를 연동할 때 순서대로 확인할 항목:

1. **컨트랙트 주소 확인**: 체인별·버전별 주소는 [Circle 개발자 문서의 스마트 컨트랙트 주소 페이지](https://developers.circle.com/stablecoins/evm-smart-contract-addresses)에서 가져온다. 코드에 하드코딩하지 말고 설정 파일로 관리한다.

2. **approve**: `depositForBurn` 호출 전, USDC 컨트랙트에서 TokenMessengerV2를 spender로 `approve(tokenMessengerV2, amount)`.

3. **mintRecipient 인코딩**: `address`를 `bytes32`로 변환할 때 우측 정렬(좌측 제로 패딩)로 처리한다. Solidity에서는 `bytes32(uint256(uint160(addr)))`. EVM이 아닌 체인은 해당 체인의 주소 인코딩 규칙을 따른다.

4. **이벤트 파싱**: `MessageSent(bytes message)` 이벤트에서 `message` 필드 전체를 바이트 그대로 저장한다. 이 값이 `receiveMessage` 호출에 필요하다.

5. **어테스테이션 폴링**: `message`를 keccak256 해시해 Iris API에 질의한다. status가 `pending`이면 재시도. `complete`가 되면 다음 단계로.

6. **receiveMessage 호출**: 가스 부족으로 실패하지 않도록 목적지 체인의 가스 가격과 한도를 고려한다. 훅이 있다면 훅 컨트랙트 실행 비용도 포함해야 한다.

7. **destinationCaller 처리**: 기본값 0이면 누구나 완료 가능. 특정 주소로 제한한 경우, 해당 주소를 가진 릴레이어 또는 사용자가 호출해야 한다.

8. **번 한도 사전 확인**: 단일 트랜잭션 금액이 `burnLimitsPerMessage`를 넘으면 revert된다. 대량 전송은 여러 트랜잭션으로 분할한다.

## 함께 보면 좋을 자료

- [circlefin/evm-cctp-contracts](https://github.com/circlefin/evm-cctp-contracts) — CCTP V2 EVM 컨트랙트 소스코드 (MIT)
- [Circle CCTP 개발자 문서](https://developers.circle.com/stablecoins/cctp-getting-started) — 공식 통합 가이드
- [CCTP 스마트 컨트랙트 주소](https://developers.circle.com/stablecoins/evm-smart-contract-addresses) — 체인별 배포 주소

## 참고 자료

- [circlefin/evm-cctp-contracts](https://github.com/circlefin/evm-cctp-contracts) — Circle, 조회일 2026-06-30
- [CCTP 개발자 문서: 시작하기](https://developers.circle.com/stablecoins/cctp-getting-started) — Circle Developer Docs, 조회일 2026-06-30
- [CCTP EVM 스마트 컨트랙트 주소](https://developers.circle.com/stablecoins/evm-smart-contract-addresses) — Circle Developer Docs, 조회일 2026-06-30
- [CCTP V2 개요](https://developers.circle.com/stablecoins/cctp-v2-overview) — Circle Developer Docs, 조회일 2026-06-30
