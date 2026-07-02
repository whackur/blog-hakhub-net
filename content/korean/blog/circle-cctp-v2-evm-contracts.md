---
title: "Circle CCTP V2 EVM 컨트랙트 파헤치기"
meta_title: ""
description: "Circle CCTP V2의 TokenMessengerV2·MessageTransmitterV2·TokenMinterV2 세 컨트랙트가 역할을 어떻게 나누는지 소스코드 기준으로 정리했습니다. burn-and-mint 라이프사이클과 메시지 레이아웃, fast transfer 수수료 모델, hookData·destinationCaller의 실무 영향까지 다룹니다."
date: 2026-06-30T17:30:00+09:00
lastmod: 2026-07-02T00:00:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["cctp", "circle", "usdc", "cross-chain", "solidity"]
author: "whackur"
translationKey: "circle-cctp-v2-evm-contracts"
draft: false
---

USDC를 한 체인에서 다른 체인으로 옮기는 브리지 설계는 크게 두 갈래로 나뉩니다. 하나는 lock-and-mint입니다. 원본 토큰을 소스 체인(source chain)의 컨트랙트에 잠가 두고, 목적지 체인(destination chain)에서 래핑 토큰을 찍어냅니다. 다른 하나는 burn-and-mint입니다. 소스 체인에서 토큰을 아예 소각하고, 목적지 체인에서 같은 양을 새로 발행합니다. Circle이 만든 [CCTP(Cross-Chain Transfer Protocol)](https://developers.circle.com/stablecoins/cctp-getting-started)는 후자입니다.

burn-and-mint가 아무 토큰에나 가능한 방식은 아닙니다. 목적지 체인에서 진짜 토큰을 새로 발행하려면 모든 체인에서 발행 권한을 가진 주체가 있어야 합니다. USDC는 발행사인 Circle이 체인마다 민트 권한을 쥐고 있어 이 조건을 만족합니다. 발행 권한이 없는 범용 브리지가 래핑 토큰을 만들 수밖에 없는 이유이기도 합니다.

이 글은 CCTP V2의 EVM 컨트랙트를 소스코드 수준에서 살펴봅니다. 코드는 [circlefin/evm-cctp-contracts](https://github.com/circlefin/evm-cctp-contracts) 레포에 공개되어 있습니다. V1과의 차이, 세 컨트랙트의 역할 분리, 메시지 포맷, 소각과 민트의 라이프사이클, V2에서 추가된 fast transfer 수수료 모델과 hookData, 그리고 연동하는 쪽이 미리 알아야 할 신뢰 전제와 실패 지점을 다룹니다.

## 래핑 USDC의 유동성 분절

lock-and-mint 브리지의 문제는 두 방향에서 나타납니다.

첫째는 보안입니다. 잠금 컨트랙트 하나에 브리지 전체의 담보가 쌓입니다. TVL이 커질수록 이 컨트랙트는 그 자체로 대형 익스플로잇의 표적이 됩니다. 잠금 컨트랙트가 뚫리면 담보가 사라지고, 그 담보를 근거로 발행된 래핑 토큰은 한순간에 무담보 자산이 됩니다.

둘째는 유동성 분절입니다. 래핑 토큰은 발행한 브리지마다 서로 다른 컨트랙트입니다. 같은 "USDC"라도 A 브리지를 거친 버전과 B 브리지를 거친 버전은 호환되지 않는 별개 토큰이고, DEX 풀과 대출 시장도 각각 따로 만들어집니다. Avalanche나 Arbitrum에서 오래 쓰인 USDC.e가 대표적입니다. Circle이 해당 체인에 네이티브 USDC를 직접 발행하기 전까지, 사용자들은 브리지판 USDC.e와 네이티브 USDC가 공존하며 유동성이 갈라지는 상황을 감수해야 했습니다.

CCTP는 이 두 문제를 같은 방법으로 해소합니다. 잠금이 없으니 허니팟도 없습니다. 소스 체인의 USDC는 실제로 소각되고, Circle이 그 소각을 확인한 뒤 목적지 체인에서 네이티브 USDC를 새로 발행합니다. 어떤 경로로 옮기든 도착하는 토큰은 언제나 Circle이 발행한 단일한 네이티브 USDC입니다.

물론 공짜는 아닙니다. 소각을 확인하고 발행을 승인하는 권한을 Circle이 독점합니다. Circle의 인프라가 멈추면 전송도 멈춥니다. 거대한 TVL 잠금 대신 중앙화된 발행사 신뢰를 받아들이는 구조라는 점을 알고 써야 합니다. 이 신뢰 경계가 코드에 어떻게 드러나는지는 뒤의 attestation 섹션에서 자세히 봅니다.

## 세 컨트랙트의 역할 분리

CCTP V2의 EVM 구현은 세 컨트랙트로 구성됩니다.

| 컨트랙트 | 역할 | 호출 주체 |
|----------|------|-----------|
| `TokenMessengerV2` | 사용자 진입점. 소각 요청 접수, 민트 실행 | 사용자 EOA 또는 컨트랙트 |
| `MessageTransmitterV2` | 체인 간 메시지 라우팅, attestation 검증 | TokenMessengerV2, 릴레이어 |
| `TokenMinterV2` | 토큰 소각·민트 실행, 한도 관리 | TokenMessengerV2만 |

한 줄로 요약하면 이렇습니다. TokenMessengerV2는 사용자가 만나는 진입점, MessageTransmitterV2는 메시지와 attestation을 다루는 통신 계층, TokenMinterV2는 소각과 발행 권한을 쥔 금고지기입니다.

이 분리의 효과는 관심사마다 신뢰 범위를 좁힐 수 있다는 데 있습니다. MessageTransmitterV2는 토큰이라는 개념을 전혀 모르는 범용 메시지 전달 컨트랙트입니다. 반대로 USDC의 민트 권한은 TokenMinterV2 한 곳에만 있고, 그 TokenMinterV2는 TokenMessengerV2만 호출할 수 있습니다. 민트로 가는 경로가 코드 상에서 하나로 좁혀져 있어, 검토해야 할 공격 표면도 그만큼 줄어듭니다.

## TokenMessengerV2: 사용자 진입점

TokenMessengerV2는 사용자가 직접 호출하는 유일한 컨트랙트입니다. V1의 `depositForBurn`이 파라미터 4개를 받았다면 V2에서는 `destinationCaller`·`maxFee`·`minFinalityThreshold` 3개가 추가됐습니다. 추가된 파라미터 하나하나가 V2의 새 기능과 연결됩니다.

**depositForBurn**: 기본 소각 요청입니다.

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

`mintRecipient`는 `address`가 아니라 `bytes32` 타입입니다. EVM 주소는 32바이트 필드에 우측 정렬(좌측 제로 패딩)로 인코딩합니다. Solidity로는 `bytes32(uint256(uint160(addr)))`입니다. Solana처럼 32바이트 주소를 네이티브로 쓰는 체인과 포맷을 통일하기 위한 선택입니다.

`destinationCaller`가 `bytes32(0)`이면 목적지에서 누구나 `receiveMessage()`를 호출해 민트를 완료할 수 있습니다. 특정 릴레이어나 컨트랙트로 제한하려면 해당 주소를 넣습니다.

`maxFee`는 발신자가 수락하는 수수료 상한입니다(소각 토큰 단위). Circle이 실제 부과하는 수수료는 이 상한 안에서만 유효하므로, fast transfer를 쓰려면 maxFee를 현행 fast 수수료 이상으로 잡아야 합니다.

`minFinalityThreshold`는 발신자가 요구하는 최소 finality(블록이 재편성으로 되돌려질 가능성이 사실상 사라진 확정 상태) 수준입니다. Circle 문서는 `minFinalityThreshold <= 1000`을 Fast Transfer, `>= 2000`을 Standard Transfer(수수료 없음)로 분류합니다. 수신 쪽 컨트랙트는 메시지에 기록된 `finalityThresholdExecuted`가 `FINALITY_THRESHOLD_FINALIZED`(2000) 미만이면 unfinalized 경로로, 이상이면 finalized 경로로 라우팅합니다. TokenMessengerV2가 허용하는 unfinalized 임계값의 최솟값은 500입니다. 반환값은 없습니다.

**depositForBurnWithHook**: hookData를 함께 전달하는 V2 전용 함수입니다. `hookData`는 빈 값을 허용하지 않습니다.

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

민트 이후 목적지에서 추가 동작을 이어 붙이는 채널입니다. hookData 섹션에서 자세히 다룹니다.

소각 요청이 들어오면 TokenMessengerV2 내부에서 두 가지 일이 순서대로 일어납니다. 먼저 `TokenMinterV2.burn()`으로 USDC를 소각하고, 이어서 `MessageTransmitterV2.sendMessage()`로 소각 사실을 담은 메시지를 emit합니다. `DepositForBurn` 이벤트와 `MessageSent` 이벤트가 같은 트랜잭션 영수증에 함께 남습니다.

## MessageTransmitterV2: 메시지 라우팅과 attestation 검증

MessageTransmitterV2는 CCTP의 통신 계층입니다. 토큰이 무엇인지 모릅니다. 원시 바이트 메시지를 보내고, 받고, 서명을 검증할 뿐입니다.

**sendMessage**: TokenMessengerV2가 소각 완료 후 호출합니다. 목적지 도메인, 수신자 컨트랙트 주소, destinationCaller, minFinalityThreshold, 메시지 바디를 받아 `MessageSent` 이벤트를 emit합니다. 이벤트에 담긴 `message` 바이트가 릴레이어가 수집해야 하는 데이터입니다.

**receiveMessage**: 목적지 체인에서 릴레이어가 호출합니다.

```solidity
function receiveMessage(
    bytes calldata message,
    bytes calldata attestation
) external returns (bool success);
```

이 함수는 라우팅 전에 세 가지를 검증합니다. 첫째, 메시지 헤더의 목적지 도메인이 로컬 체인과 일치하는지 확인합니다. 둘째, attestation에 담긴 서명을 Circle의 attester 주소 집합으로 검증합니다. 셋째, nonce가 이미 쓰였는지 `usedNonces` 매핑에서 확인하고 사용 처리합니다. 같은 메시지를 다시 제출하면 여기서 revert됩니다. 세 검증을 통과하면 `finalityThresholdExecuted` 값에 따라 분기합니다. 2000(`FINALITY_THRESHOLD_FINALIZED`) 이상이면 `handleReceiveFinalizedMessage()`, 미만이면 `handleReceiveUnfinalizedMessage()`가 호출됩니다.

attester는 `enabledAttesters`에 등록된 Circle 관리 주소 집합입니다. `signatureThreshold`개 이상의 유효한 서명이 있어야 통과합니다. 컨트랙트 차원에서는 설정 가능한 M-of-N 다중 서명을 지원하지만, 실제 배포에 적용된 임계값과 attester 구성은 배포된 컨트랙트나 Circle 공식 배포 문서에서 직접 확인해야 합니다.

## TokenMinterV2: 소각과 민트 실행

TokenMinterV2는 실제 소각과 민트를 담당합니다. 호출자는 TokenMessengerV2 하나뿐이고, 외부에서 직접 접근하는 경로는 없습니다.

`burn(address burnToken, uint256 amount)`은 소스 체인에서 USDC를 소각합니다. 소각 전에 `burnLimitsPerMessage[burnToken]`을 확인해, 한도를 넘는 금액이면 revert합니다. 이 한도는 체인별·토큰별로 설정하는 리스크 관리 장치입니다. 오라클 없이 동작하는 소극적 방어라 공격 자체를 막지는 못하지만, 단일 트랜잭션의 피해 규모에 상한을 겁니다.

`mint()`는 목적지 체인에서 USDC를 발행합니다. V2 인터페이스는 한 번의 호출로 두 수신자에게 민트할 수 있습니다. mintRecipient(사용자)와 feeRecipient(수수료 수취인)입니다. fast transfer의 수수료 공제가 이 이중 수신자 구조 위에서 동작합니다. 소스 체인 토큰 주소를 로컬 USDC 주소로 바꾸는 데는 `remoteTokensToLocalTokens[sourceDomain][burnToken]` 매핑을 씁니다. 이 매핑은 Circle이 관리하며, 지원 토큰 쌍은 공식 문서에서 확인합니다.

## 메시지 레이아웃

CCTP 메시지는 고정 길이 헤더와 가변 길이 바디로 이루어진 바이너리 포맷입니다. ABI 인코딩이 아니라 바이트 오프셋으로 직접 파싱하는 packed 포맷입니다.

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

V2에서 nonce는 V1의 uint64 순차 카운터에서 `bytes32` 값으로 바뀌었습니다. 발신 시점에는 빈 값(`bytes32(0)`)으로 보내고, Circle attester가 서명 전에 실제 값을 채웁니다. `minFinalityThreshold`와 `finalityThresholdExecuted`가 추가되면서 헤더 전체 크기는 116바이트에서 148바이트로 늘었습니다.

도메인 ID는 Circle이 중앙에서 할당합니다. 현재 주요 EVM 체인 도메인:

| 체인 | 도메인 |
|------|--------|
| Ethereum | 0 |
| Avalanche C-Chain | 1 |
| OP Mainnet | 2 |
| Arbitrum One | 3 |
| Base | 6 |
| Polygon PoS | 7 |

**BurnMessage 바디:**

헤더(148바이트) 이후에 오는 바디는 BurnMessageV2 포맷입니다.

| 필드 | 타입 | 설명 |
|------|------|------|
| version | uint32 | BurnMessage 버전 |
| burnToken | bytes32 | 소스 체인 소각 토큰 주소 |
| mintRecipient | bytes32 | 목적지 수신자 주소 |
| amount | uint256 | 전송량 |
| messageSender | bytes32 | `depositForBurn` 호출자 |
| maxFee | uint256 | 발신자가 설정한 최대 수수료 상한 |
| feeExecuted | uint256 | Circle이 실제 부과하는 수수료 (attester가 채워 넣음) |
| expirationBlock | uint256 | 메시지 만료 블록 번호 (0이면 만료 없음) |
| hookData | bytes | V2 신규: 임의 길이 훅 데이터 |

발신 시 `feeExecuted`와 `expirationBlock`도 `0`으로 전송됩니다. Circle attester가 서명 전에 실제 값을 채웁니다. `hookData`가 없으면 바디 크기는 228바이트로 고정입니다.

이 레이아웃에 CCTP의 신뢰 구조가 그대로 드러납니다. nonce, finalityThresholdExecuted, feeExecuted, expirationBlock 네 필드는 온체인에서 만들어지지 않습니다. Circle의 오프체인 서비스가 값을 채우고 서명하며, 그 서명된 결과가 목적지 체인에서 그대로 사실로 통합니다. attester는 소각을 목격하는 증인이면서 동시에 메시지를 완성하는 주체입니다.

## 소각 라이프사이클

소스 체인에서 시작해 목적지 체인에서 USDC를 받기까지의 흐름입니다.

1. **승인**: 사용자가 TokenMessengerV2에 USDC 지출 승인(`approve`)을 줍니다.

2. **depositForBurn 호출**: TokenMessengerV2를 호출합니다. 함수 내부에서:
   - `TokenMinterV2.burn()` 호출 → USDC 소각
   - `MessageTransmitterV2.sendMessage()` 호출 → 소각 메시지 emit
   - `DepositForBurn` 이벤트와 `MessageSent` 이벤트가 같은 트랜잭션에 emit됩니다.

3. **이벤트 수집**: 릴레이어(또는 사용자 본인)가 `MessageSent` 이벤트에서 `message` 바이트를 추출합니다.

4. **attestation 요청**: Circle Iris API에 메시지 해시(keccak256)를 넘기고 attestation을 기다립니다.
   ```
   GET https://iris-api.circle.com/attestations/{messageHash}
   ```
   표준 경로는 소스 체인의 finality를 기다립니다. Ethereum에서는 약 15~20분 걸립니다.

5. **receiveMessage 호출**: attestation status가 `complete`가 되면 목적지 체인의 MessageTransmitterV2에 `receiveMessage(message, attestation)`을 호출합니다.

## 민트 라이프사이클

목적지 체인에서 `receiveMessage`가 호출된 이후의 흐름입니다.

1. **헤더 파싱**: 목적지 도메인 일치를 확인합니다.
2. **attestation 검증**: 서명 수가 signatureThreshold 이상인지 확인합니다.
3. **destinationCaller 확인**: 헤더의 destinationCaller가 0이 아니면 `msg.sender == destinationCaller`를 검증합니다.
4. **nonce 체크**: `usedNonces[nonce]`가 사용된 적 없는지 확인하고 사용 처리합니다.
5. **finality 라우팅**: `finalityThresholdExecuted >= 2000`이면 `handleReceiveFinalizedMessage()`(수수료 없음, 전액 민트), 미만이면 `handleReceiveUnfinalizedMessage()`를 호출합니다.
6. **USDC 민트**: finalized 경로는 `amount` 전액을 mintRecipient에게 민트합니다. unfinalized 경로는 `amount - feeExecuted`를 mintRecipient에게, `feeExecuted`를 feeRecipient에게 각각 민트합니다.
7. **hookData**: BurnMessageV2에 담긴 hookData는 릴레이어 래퍼(예: Circle의 CCTPHookWrapper)가 `receiveMessage()` 완료 후 별도로 처리합니다. TokenMessenger·MessageTransmitter 자체는 hookData 기반 훅 호출을 수행하지 않습니다.

nonce는 bytes32 단일 키로 관리됩니다. 같은 메시지를 두 번 제출하면 두 번째는 4번 단계에서 revert됩니다.

## Fast transfer와 수수료 모델

V2에서 실무 영향이 가장 큰 변화는 fast transfer입니다.

**Standard 경로**: 소스 체인이 finality에 도달할 때까지 기다립니다. Ethereum에서는 15~20분, Arbitrum 같은 L2에서는 체인에 따라 수분에서 수십 분이 걸립니다. 수수료는 없습니다.

**Fast 경로**: Circle이 소스 체인의 finality를 기다리지 않고 attestation을 먼저 발행합니다. USDC가 수초에서 수분 안에 목적지에 도착합니다. 대신 수수료가 붙습니다.

수수료는 소각 금액에서 공제됩니다. `amount = 100 USDC`, `fee = 1 USDC`면 mintRecipient는 `99 USDC`를 받습니다. 수수료 구조와 정확한 금액은 [Circle 개발자 문서](https://developers.circle.com/stablecoins/cctp-getting-started)에서 현행 값을 확인해야 합니다.

이 수수료의 정체는 reorg 위험의 가격입니다. finality 전에 민트를 승인했는데 소스 체인이 재편성되어 소각 트랜잭션이 사라지면, 목적지에는 이미 민트된 USDC가 남습니다. 이 손실은 Circle이 떠안습니다. 수수료는 Circle이 감수하는 그 위험에 매긴 보험료인 셈입니다.

연동하는 입장에서 챙길 부분은 두 가지입니다. 정산 로직이 "보낸 금액 = 받는 금액"을 전제하면 안 됩니다. fast 경로에서 mintRecipient가 받는 금액은 `amount - feeExecuted`입니다. 그리고 maxFee가 실제 수수료보다 낮으면 fast 처리가 성립하지 않으므로, fast 경로를 의도한다면 현행 수수료를 확인하고 maxFee를 여유 있게 설정해야 합니다.

## destinationCaller와 hookData

**destinationCaller**는 메시지 헤더의 bytes32 필드로, 목적지에서 `receiveMessage()`를 호출할 수 있는 주소를 제한합니다.

- `0x000...000`: 제한 없음. 누구나 attestation과 메시지를 들고 민트를 완료할 수 있습니다.
- 특정 주소로 설정: 그 주소만 `receiveMessage()`를 호출할 수 있습니다. 릴레이어 컨트랙트를 지정해 MEV를 차단하거나 실행 순서를 통제할 때 씁니다.

강력한 만큼 운영 부담도 따라옵니다. destinationCaller를 지정한 순간, 그 주소가 호출하지 않으면 민트를 완료할 방법이 없습니다. 지정한 릴레이어가 다운되거나 키를 잃으면 소각은 끝났는데 민트는 못 하는 상태로 자금이 묶입니다. 자체 릴레이어를 지정할 때는 그 릴레이어의 가용성과 키 관리가 곧 사용자 자금의 가용성이라는 점까지 계산에 넣어야 합니다.

**hookData**는 V2에서 추가된 가변 길이 바이트 필드입니다. `depositForBurnWithHook()` 사용 시 BurnMessage 바디 끝에 붙습니다. 민트가 끝난 뒤 목적지에서 추가 동작을 이어 붙이는 채널입니다. 활용 패턴:

- 브리지 후 즉시 DEX 스왑
- 브리지 후 대출 프로토콜 예치
- 크로스체인 페이롤·결제 흐름의 후속 처리

주의할 점은 코어 컨트랙트가 hookData를 실행하지 않는다는 사실입니다. TokenMessengerV2는 hookData를 BurnMessageV2에 저장하고 파싱할 뿐, 훅 호출을 직접 수행하지 않습니다. 실행은 릴레이어 래퍼의 몫입니다. Circle의 참조 구현인 CCTPHookWrapper는 `receiveMessage()`를 먼저 완료한 다음 훅을 별도로 실행합니다. 훅이 실패해도 USDC 민트는 이미 끝난 뒤입니다.

이 비원자성은 의도된 설계입니다. 민트와 훅이 한 트랜잭션에 원자적으로 묶여 있다면, 공격자가 가스를 빠듯하게 넣어 호출해서 nonce만 소모시키고 훅을 실패시키는 방식으로 메시지를 영구히 죽일 수 있습니다. 훅을 민트 뒤로 분리하면 이 공격이 성립하지 않습니다. 대신 훅을 쓰는 쪽은 "민트는 성공했는데 훅은 실행되지 않은 상태"가 정상적으로 발생할 수 있다는 전제로 설계해야 합니다. USDC는 이미 mintRecipient에 도착해 있으므로, 훅이 실패했을 때 재시도할지 수동으로 복구할지를 애플리케이션 차원에서 정해 둬야 합니다.

## Attestation이라는 신뢰 경계

CCTP를 쓴다는 것은 결국 Circle의 attestation(Circle attester들이 소각 사실을 확인하고 발행하는 서명)을 신뢰한다는 뜻입니다. 이 신뢰의 경계를 정확히 그어 두는 편이 좋습니다.

온체인 컨트랙트가 검증하는 것은 서명뿐입니다. MessageTransmitterV2는 등록된 attester들이 이 메시지에 서명했는지를 확인할 뿐, 소각이 실제로 있었는지를 스스로 확인할 방법이 없습니다. attester 키로 서명된 메시지는 소각 여부와 무관하게 목적지에서 유효합니다. CCTP의 실질 보안이 스마트 컨트랙트 감사보다 Circle의 키 관리와 오프체인 인프라 운영에 더 크게 좌우되는 이유입니다.

**다중 서명 구성**: MessageTransmitterV2는 설정 가능한 M-of-N attester 서명을 지원합니다. 실제 배포에 적용된 서명 임계값과 attester 구성은 배포된 컨트랙트나 Circle 공식 배포 문서에서 직접 확인해야 합니다. 임계값이 몇이든 attester를 등록하고 해제하는 권한이 Circle에 있다는 사실은 변하지 않습니다.

**리플레이 방지**: `usedNonces[nonce]` 매핑이 각 목적지 체인에서 메시지 재사용을 막습니다. V2의 nonce는 순차 카운터가 아니라 Circle attester가 서명 시 채워 넣는 bytes32 값입니다.

**소각 한도**: `burnLimitsPerMessage[token]`이 단일 트랜잭션에서 소각할 수 있는 최대량을 제한합니다. 사고를 막는 장치가 아니라 사고의 규모를 줄이는 장치입니다.

**컨트랙트 업그레이드 가능성**: TokenMessengerV2와 MessageTransmitterV2는 업그레이드 가능한 프록시 뒤에 배포되어 있습니다. Circle이 로직을 교체할 수 있다는 뜻입니다. 업그레이드 전 타임락이 있는지 [배포 주소](https://developers.circle.com/stablecoins/evm-smart-contract-addresses) 페이지에서 출발해 프록시 어드민을 확인해 보는 것이 좋습니다.

**오프체인 의존성**: attestation을 발급하는 Iris API(`iris-api.circle.com`)가 멈추면 진행 중인 전송도 멈춥니다. 소각은 이미 끝났고 attestation 없이는 민트할 수 없으니, 그 사이 자금은 어느 체인에도 존재하지 않는 상태가 됩니다. Circle 인프라가 복구되면 attestation을 다시 받을 수 있지만, 다운 중에 온체인에서 꺼낼 방법은 없습니다. 연동 서비스라면 이 구간을 지연으로 안내할지 장애로 처리할지, 모니터링과 사용자 안내 정책을 미리 정해 둘 필요가 있습니다.

## 통합 체크리스트

직접 CCTP V2를 연동할 때 순서대로 확인할 항목입니다.

1. **컨트랙트 주소 확인**: 체인별·버전별 주소는 [Circle 개발자 문서의 스마트 컨트랙트 주소 페이지](https://developers.circle.com/stablecoins/evm-smart-contract-addresses)에서 가져옵니다. V1과 V2는 별도 컨트랙트로 배포되어 있으므로 버전을 혼동하면 안 됩니다. 코드에 하드코딩하지 말고 설정 파일로 관리합니다.

2. **approve**: `depositForBurn` 호출 전, USDC 컨트랙트에서 TokenMessengerV2를 spender로 `approve(tokenMessengerV2, amount)`를 실행합니다.

3. **mintRecipient 인코딩**: `address`를 `bytes32`로 변환할 때 우측 정렬(좌측 제로 패딩)로 처리합니다. Solidity에서는 `bytes32(uint256(uint160(addr)))`. 잘못 인코딩하면 자금이 의도하지 않은 주소로 발행될 수 있고, 되돌릴 방법이 없습니다. EVM이 아닌 체인은 해당 체인의 주소 인코딩 규칙을 따릅니다.

4. **이벤트 파싱**: `MessageSent(bytes message)` 이벤트에서 `message` 필드 전체를 바이트 그대로 저장합니다. attestation 조회 키가 이 바이트의 keccak256 해시라서, 한 바이트라도 달라지면 조회 자체가 안 됩니다.

5. **attestation 폴링**: `message`를 keccak256으로 해시해 Iris API에 질의합니다. status가 `pending`이면 재시도하고, `complete`가 되면 다음 단계로 넘어갑니다. pending 상태의 attestation을 목적지에 제출하면 안 됩니다.

6. **receiveMessage 호출**: 가스 부족으로 실패하지 않도록 목적지 체인의 가스 가격과 한도를 고려합니다. 훅이 있다면 훅 컨트랙트 실행 비용도 포함해야 합니다.

7. **destinationCaller 처리**: 기본값 0이면 누구나 완료할 수 있습니다. 특정 주소로 제한한 경우 그 주소를 가진 릴레이어 또는 사용자가 호출해야 하며, 해당 주소의 가용성을 연동 서비스가 책임져야 합니다.

8. **소각 한도 사전 확인**: 단일 트랜잭션 금액이 `burnLimitsPerMessage`를 넘으면 revert됩니다. 대량 전송은 여러 트랜잭션으로 분할합니다.

## 정리

CCTP V2를 컨트랙트 관점에서 한 문단으로 요약하면 이렇습니다. TokenMessengerV2가 소각 요청을 받아 TokenMinterV2로 USDC를 소각하고, MessageTransmitterV2가 메시지를 내보냅니다. Circle의 attester가 nonce와 수수료 필드를 채워 서명하면, 목적지 체인의 MessageTransmitterV2가 그 서명을 검증하고, TokenMessengerV2를 거쳐 TokenMinterV2가 네이티브 USDC를 발행합니다.

기억할 트레이드오프는 셋입니다. 래핑 토큰과 잠금 허니팟이 없는 대신 Circle이라는 단일 주체를 신뢰합니다. fast transfer는 속도를 얻는 대신 reorg 위험의 가격을 수수료로 지불합니다. hookData는 조합 가능성을 열어 주는 대신 민트와 훅 실행의 원자성을 포기합니다. 세 가지 모두 코드에 그대로 드러나 있으니, 연동 전에 이 글에서 짚은 지점들을 소스코드와 공식 문서로 직접 확인해 보시기 바랍니다.

## 함께 보면 좋을 자료

- [circlefin/evm-cctp-contracts](https://github.com/circlefin/evm-cctp-contracts) — CCTP V2 EVM 컨트랙트 소스코드 (MIT)
- [Circle CCTP 개발자 문서](https://developers.circle.com/stablecoins/cctp-getting-started) — 공식 통합 가이드
- [CCTP V2 개요](https://developers.circle.com/stablecoins/cctp-v2-overview) — V1과 V2의 차이 정리
- [CCTP 스마트 컨트랙트 주소](https://developers.circle.com/stablecoins/evm-smart-contract-addresses) — 체인별 배포 주소

## 참고 자료

- [circlefin/evm-cctp-contracts](https://github.com/circlefin/evm-cctp-contracts) — Circle, 조회일 2026-06-30
- [CCTP 개발자 문서: 시작하기](https://developers.circle.com/stablecoins/cctp-getting-started) — Circle Developer Docs, 조회일 2026-06-30
- [CCTP EVM 스마트 컨트랙트 주소](https://developers.circle.com/stablecoins/evm-smart-contract-addresses) — Circle Developer Docs, 조회일 2026-06-30
- [CCTP V2 개요](https://developers.circle.com/stablecoins/cctp-v2-overview) — Circle Developer Docs, 조회일 2026-06-30
