---
title: "Chainlink CCIP EVM 컨트랙트 구조 분석"
meta_title: ""
description: "Chainlink CCIP의 Router, OnRamp, OffRamp, TokenPool, FeeQuoter, RMN이 어떻게 맞물려 체인 간 메시지와 토큰을 이동시키는지 소스 코드 기준으로 정리합니다."
date: 2026-06-30T17:30:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
image: ""
categories: ["Blockchain"]
tags: ["chainlink", "ccip", "cross-chain", "solidity", "smart-contract"]
author: "whackur"
translationKey: "chainlink-ccip-evm-contracts"
draft: false
---

Ethereum Mainnet에서 Arbitrum으로 USDC를 보내거나, Polygon 컨트랙트가 Base 컨트랙트를 트리거하는 작업은 EVM 자체로는 불가능합니다. 체인은 기본적으로 서로 격리되어 있습니다. 크로스체인 브릿지가 이 공백을 메워 왔지만, 브릿지는 구조적으로 공격 표면이 넓어 업계 전반에서 보안 사고가 반복됐습니다.

Chainlink CCIP(Cross-Chain Interoperability Protocol)는 이 문제에 Chainlink의 DON(탈중앙화 오라클 네트워크)과 별도 위험 관리 네트워크(RMN)를 적용한 프로토콜입니다. 단순 토큰 전송뿐 아니라 임의 데이터를 함께 보낼 수 있고, 하나의 트랜잭션에서 토큰 이동과 컨트랙트 호출을 묶는 것도 가능합니다. 이 글은 CCIP EVM 컨트랙트의 각 구성 요소가 어떤 역할을 하는지, 그리고 그것들이 어떻게 맞물려 동작하는지를 소스 코드 기준으로 설명합니다.

## 전체 구조 개요

CCIP 컨트랙트는 크게 두 레이어로 나뉩니다. 사용자(또는 dApp)가 직접 접하는 **인터페이스 레이어**와 DON이 조율하는 **파이프라인 레이어**입니다.

사용자는 소스 체인의 Router 컨트랙트에만 접근합니다. Router가 OnRamp로 전달하면, DON과 오프체인 실행자가 `CCIPMessageSent` 이벤트를 관찰하고 대상 체인 OffRamp의 `execute(encodedMessage, ccvs, verifierResults, gasLimitOverride)`를 호출해 실행 데이터를 제출합니다. OffRamp가 수신 컨트랙트의 `ccipReceive`를 호출하면서 사이클이 끝납니다.

| 컨트랙트 | 배포 위치 | 역할 |
|----------|-----------|------|
| Router 1.2.0 | 소스·대상 | 사용자 진입점, 체인 셀렉터별 OnRamp·OffRamp 라우팅 |
| OnRamp 2.0.0 | 소스 | 아웃바운드 메시지 검증, 토큰 잠금/소각, 이벤트 발행 |
| OffRamp 2.0.0 | 대상 | CCV 검증, 인바운드 메시지 실행, 상태 관리 |
| TokenPool | 소스·대상 | 토큰 잠금·소각(소스)·해제·발행(대상) |
| FeeQuoter 2.0.0 | 소스 | 크로스체인 수수료 산정 |
| RMN 2.0.0 | 소스·대상 | 이상 감지 시 실행 차단(curse) |
| TokenAdminRegistry 1.5.0 | 소스·대상 | 토큰 주소 → TokenPool 주소 매핑 |

## Client 메시지 구조체

CCIP의 메시지 형식은 `Client.sol` 라이브러리에 정의됩니다. 전송할 때와 수신할 때 쓰는 구조체가 다릅니다.

### 전송 구조체 (EVM2AnyMessage)

```solidity
struct EVM2AnyMessage {
    bytes receiver;             // abi.encode(address) — 비EVM 체인 지원을 위해 bytes
    bytes data;                 // 임의 페이로드
    EVMTokenAmount[] tokenAmounts;
    address feeToken;           // address(0) = 네이티브 가스 토큰(ETH 등)
    bytes extraArgs;            // EVMExtraArgsV1 또는 V2 인코딩
}
```

`receiver`가 `address`가 아닌 `bytes`인 이유는 Solana 같은 비EVM 체인도 대상으로 지원하기 위해서입니다. EVM끼리 전송할 때는 `abi.encode(receiverAddress)`로 인코딩합니다.

`extraArgs`에는 대상 체인에서 `ccipReceive`를 실행할 가스 한도와 순서 보장 여부를 담습니다. `Client.sol`에는 `EVMExtraArgsV1`(가스 한도만)과 범용 `GenericExtraArgsV2`가 정의되어 있고, v2 파이프라인 내부는 CCV·Executor 필드를 포함한 `GenericExtraArgsV3`를 사용합니다.

```solidity
// GenericExtraArgsV2 (태그: 0x181dcf10): 일반 EVM 전송 권장
struct GenericExtraArgsV2 {
    uint256 gasLimit;                  // 수신 컨트랙트 ccipReceive 실행 가스
    bool allowOutOfOrderExecution;     // true이면 순서 없이 실행 허용
}
```

`gasLimit`을 너무 작게 설정하면 대상 체인에서 실행이 revert됩니다. 반면 지나치게 크게 설정하면 수수료가 올라갑니다. `EVMExtraArgsV1` 대신 `GenericExtraArgsV2`를 명시적으로 인코딩하는 것이 좋습니다. 버전이 올라갈 때 기본값이 달라질 수 있기 때문입니다.

### 수신 구조체 (Any2EVMMessage)

```solidity
struct Any2EVMMessage {
    bytes32 messageId;
    uint64 sourceChainSelector;
    bytes sender;              // abi.encode(address) — EVM이면 decode로 주소 추출
    bytes data;
    EVMTokenAmount[] destTokenAmounts;
}
```

소스 체인의 발신자 주소는 `abi.decode(message.sender, (address))`로 꺼냅니다.

## Router: 전송 진입점

Router는 사용자 코드가 직접 호출하는 유일한 CCIP 컨트랙트입니다. 인터페이스는 `IRouterClient`에 정의됩니다.

```solidity
interface IRouterClient {
    function getFee(
        uint64 destinationChainSelector,
        Client.EVM2AnyMessage memory message
    ) external view returns (uint256 fee);

    function getSupportedTokens(uint64 chainSelector)
        external view returns (address[] memory tokens);

    function isChainSupported(uint64 chainSelector)
        external view returns (bool supported);

    function ccipSend(
        uint64 destinationChainSelector,
        Client.EVM2AnyMessage calldata message
    ) external payable returns (bytes32 messageId);
}
```

`ccipSend`를 호출하기 전에 준비할 것들이 있습니다.

- `feeToken`이 LINK라면 Router에 LINK를 미리 `approve`해야 합니다.
- `tokenAmounts`에 전송할 토큰이 있다면 해당 토큰도 Router에 승인해야 합니다.
- `feeToken = address(0)`이면 `msg.value`로 수수료를 납부합니다.

`getFee`는 view 함수라 트랜잭션 없이 예상 수수료를 조회할 수 있습니다. 다만 `getFee` 호출과 `ccipSend` 사이에 블록이 지나면 가격이 변할 수 있으므로, 통상 10% 정도 여유분을 더해 승인 금액이나 `msg.value`를 설정합니다.

내부적으로 Router는 `destinationChainSelector`에 해당하는 OnRamp를 찾아 `forwardFromRouter`를 호출합니다.

## OnRamp: 아웃바운드 파이프라인

OnRamp는 소스 체인에서 메시지의 유효성을 검사하고, 토큰을 잠그거나 소각한 뒤, DON이 수신하는 이벤트를 발행합니다.

`forwardFromRouter` 호출 시 OnRamp가 실행하는 단계입니다.

1. **RMN 커스 확인**: 대상 체인 커스 여부를 확인합니다. 커스 상태이면 즉시 revert합니다.
2. **메시지 검증**: `tokenAmounts` 수, 데이터 크기, `extraArgs` 형식, `gasLimit` 범위를 확인합니다.
3. **CCV 목록 병합**: 사용자 지정·레인 필수·풀 요구 CCV를 합산하고 수수료를 계산합니다.
4. **수수료 처리**: CCV·풀·Executor·프로토콜 네트워크 수수료로 나눠 각 수령자에게 분배합니다.
5. **토큰 처리**: `TokenAdminRegistry`에서 각 토큰의 풀 주소를 조회해 `lockOrBurn`을 호출합니다(메시지당 최대 1개).
6. **메시지 번호 할당**: `DestChainConfig.messageNumber`를 증가시킵니다(대상 체인별 단조 증가).
7. **이벤트 발행**: `CCIPMessageSent` 이벤트를 내보냅니다.

`CCIPMessageSent` 이벤트에는 messageId, messageNumber, 인코딩된 메시지, Receipt 배열이 담깁니다. DON은 이 이벤트를 관찰해 실행 파이프라인을 시작합니다.

## OffRamp: 인바운드 파이프라인

OffRamp는 대상 체인에서 DON이 제출한 메시지를 검증하고 실행합니다. CCIP v2에서 OffRamp는 단일 인스턴스로 여러 소스 체인을 처리할 수 있습니다.

```solidity
function execute(
    bytes calldata encodedMessage,
    address[] calldata ccvs,
    bytes[] calldata verifierResults,
    uint32 gasLimitOverride
) external;
```

`execute`는 퍼미션리스 함수입니다. 누구나 호출할 수 있으며, DON의 Execute Plugin이 정상 흐름을 담당합니다.

OffRamp 실행 흐름입니다.

1. **RMN 커스 확인**: `rmnRemote.isCursed(sourceChainSelector)`가 true이면 즉시 revert합니다.
2. **소스 체인 설정 검증**: 소스 체인 활성화 여부, onRamp 주소 해시, offRamp 주소, 대상 체인 셀렉터를 모두 확인합니다.
3. **실행 상태 확인**: `UNTOUCHED` 또는 `FAILURE` 상태인 메시지만 진행합니다. `SUCCESS`는 재실행할 수 없습니다.
4. **CCV 쿼럼 확인**: `_ensureCCVQuorumIsReached`로 required CCV가 모두 제공됐는지 확인합니다.
5. **CCV 검증**: 각 CCV의 `verifyMessage`를 호출해 서명을 검증합니다.
6. **토큰 해제/발행**: 토큰이 있으면 TokenPool의 `releaseOrMint`를 호출합니다.
7. **수신 컨트랙트 호출**: 토큰 전용 전송이 아니면 `router.routeMessage`를 통해 `receiver.ccipReceive(message)`를 `gasLimit` 범위에서 호출합니다.
8. **실행 상태 저장**: `SUCCESS` 또는 `FAILURE`를 기록합니다.

실행 상태는 `MessageExecutionState` 열거형으로 관리됩니다: `UNTOUCHED(0)`, `IN_PROGRESS(1)`, `SUCCESS(2)`, `FAILURE(3)`. `FAILURE` 상태인 메시지는 `manuallyExecute`로 재시도할 수 있습니다.

## TokenPool: 네 가지 토큰 처리 모드

TokenPool은 체인 간 토큰 이동을 담당합니다. 추상 기반 클래스 `TokenPool.sol`에서 공통 인터페이스를 정의하고, 토큰의 성격에 따라 네 가지 구현체로 나뉩니다.

풀 공통 인터페이스입니다.

```solidity
function lockOrBurn(Pool.LockOrBurnInV1 calldata lockOrBurnIn)
    external returns (Pool.LockOrBurnOutV1 memory);

function releaseOrMint(Pool.ReleaseOrMintInV1 calldata releaseOrMintIn)
    external returns (Pool.ReleaseOrMintOutV1 memory);
```

**LockReleaseTokenPool**: 소스 체인에서 잠그고(lock), 대상 체인에서 해제(release)합니다. 토큰 총 공급량이 일정하게 유지됩니다. 다른 체인에 원래 배포되지 않은 토큰(WBTC 등)을 전송할 때 씁니다.

**BurnMintTokenPool**: 소스 체인에서 소각(burn)하고, 대상 체인에서 발행(mint)합니다. 토큰이 여러 체인에 네이티브로 존재할 때 적합합니다. 발행 권한이 풀 컨트랙트에 있어야 합니다.

**BurnWithFromMintTokenPool**: 소각 방식이 다릅니다. 풀이 `transferFrom` + 소각 순서로 처리합니다. 토큰 컨트랙트에서 `approve` → `burnFrom` 패턴을 지원하지 않는 경우에 씁니다.

**BurnFromMintTokenPool**: 풀이 `burnFrom`을 직접 호출합니다. 토큰 컨트랙트가 `burnFrom`을 지원하고 풀이 `allowance`를 확보한 상태여야 합니다.

어떤 모드를 쓸지는 토큰 컨트랙트 설계와 발행 권한 구조에 달립니다. 외부 브릿지 토큰이라면 LockRelease, CCIP 네이티브 멀티체인 토큰이라면 BurnMint가 일반적입니다.

**속도 제한(Rate Limiting)**

TokenPool은 체인별로 아웃바운드·인바운드 속도 제한을 각각 설정할 수 있습니다. 토큰 버킷 알고리즘으로 단위 시간당 최대 이동 금액을 제한합니다. 한도를 초과하면 트랜잭션이 revert됩니다. 한도 값은 풀 관리자가 온체인에서 조정할 수 있습니다.

## FeeQuoter: 수수료 산정 구조

FeeQuoter는 v1.4까지 `PriceRegistry`라고 불리던 컨트랙트의 역할을 확장한 것입니다. 크로스체인 수수료를 산정하고, 체인 간 가격 데이터를 관리합니다.

전송 수수료는 세 부분으로 구성됩니다.

- **네트워크 수수료**: 프로토콜 운영 고정 비용
- **대상 체인 실행 가스 비용**: `extraArgs.gasLimit × 대상 체인 가스 가격`을 소스 체인 feeToken 단위로 환산
- **토큰 전송 수수료**: 전송하는 토큰 종류와 금액에 따른 추가 비용

가격 데이터는 Chainlink DON이 주기적으로 업데이트합니다. FeeQuoter 2.0.0에서는 가격 만료(stale price) 검사가 제거됐습니다. 가격 최신성 유지는 DON의 책임입니다.

## RMN: 위험 관리 네트워크

RMN(Risk Management Network)은 CCIP 보안 레이어의 독립된 구성 요소입니다. DON과 분리된 별도 노드 집합이 소스 체인과 대상 체인을 각각 모니터링합니다.

이상 신호(재조직 의심, 비정상적 대규모 이동 등)가 감지되면 RMN은 특정 레인 또는 전체 체인에 curse를 겁니다.

```solidity
interface IRMNRemote {
    function isCursed() external view returns (bool);
    function isCursed(bytes16 subject) external view returns (bool);
    function verify(
        address offRampAddress,
        Internal.MerkleRoot[] memory merkleRoots,
        Internal.SignedMerkleRoot[] memory signatures,
        uint256 rawVs
    ) external view;
}
```

`isCursed(bytes16 subject)`에서 `subject`는 소스 체인 셀렉터와 레인 식별자의 조합입니다. OffRamp는 실행 진입 시 저주 여부를 확인해, true이면 즉시 실행을 거부합니다.

`verify`는 OffRamp가 메시지 검증(`verifyMessage`) 과정에서 CCV를 통해 내부적으로 호출합니다. Router, OnRamp, OffRamp, TokenPool은 모두 `isCursed` 호출로 RMN 커스 상태를 직접 확인하며, 커스 상태이면 즉시 실행을 거부합니다. DON이 손상되더라도 RMN이 독립적으로 실행을 차단할 수 있다는 뜻입니다.

CCIP v2에서는 각 체인에 `RMNRemote`를 배포해 로컬에서 서명을 검증하고, 원격 `RMNHome`이 RMN 노드 집합 설정을 관리합니다.

## CCIPReceiver: 수신 컨트랙트 구현 패턴

메시지를 받는 컨트랙트는 `IAny2EVMMessageReceiver` 인터페이스를 구현해야 합니다. Chainlink가 제공하는 `CCIPReceiver` 추상 컨트랙트를 상속하면 보일러플레이트를 줄일 수 있습니다.

```solidity
abstract contract CCIPReceiver is IAny2EVMMessageReceiver {
    address internal immutable i_ccipRouter;

    modifier onlyRouter() {
        if (msg.sender != i_ccipRouter) revert InvalidRouter(msg.sender);
        _;
    }

    function ccipReceive(Client.Any2EVMMessage calldata message)
        external virtual override onlyRouter
    {
        _ccipReceive(message);
    }

    function _ccipReceive(Client.Any2EVMMessage memory message) internal virtual;
}
```

`onlyRouter` 모디파이어가 핵심입니다. `ccipReceive`는 Router만 호출할 수 있어야 합니다. 이 검사를 생략하면 누구든 임의의 메시지로 컨트랙트를 호출할 수 있게 됩니다.

구현할 때 추가로 고려할 점들입니다.

**발신자 검증**: `sourceChainSelector`와 `abi.decode(message.sender, (address))`를 화이트리스트로 검증합니다. 신뢰하지 않는 체인·주소에서 온 메시지는 revert하거나 무시합니다.

**중복 실행 방지**: `message.messageId`를 기준으로 이미 처리된 메시지를 추적합니다. 단, 중복 체크로 인해 early return하면 OffRamp는 해당 메시지를 `SUCCESS`로 기록하므로 `manuallyExecute` 재시도가 불가능해집니다.

**멱등성**: `_ccipReceive`가 동일한 메시지에 대해 두 번 호출되더라도 상태가 이중으로 변경되지 않아야 합니다. 수동 재시도 시나리오를 감안하면 멱등성 설계가 중요합니다.

**revert 처리**: `_ccipReceive` 안에서 revert가 발생하면 OffRamp는 메시지를 `FAILURE`로 기록합니다. 이후 `manuallyExecute`로 재시도할 수 있지만, 같은 `gasLimit` 조건에서 같은 로직이 다시 실패할 수 있습니다.

## 메시지 순서 보장

메시지 순서는 OnRamp의 `DestChainConfig.messageNumber`(대상 체인별 단조 증가)와 OffRamp의 `s_executionStates`(messageId 기반 상태 추적)로 관리합니다. v2에서는 별도의 NonceManager 컨트랙트가 없습니다.

`allowOutOfOrderExecution`과 순서 정책은 `extraArgs`와 레인 설정에 인코딩됩니다. 레인별 실제 동작은 Chainlink 공식 문서와 CCIP 디렉터리에서 확인하세요. `allowOutOfOrderExecution = false`로 설정된 경우, 동일 발신자가 동일 대상 체인에 보낸 메시지는 순서대로 실행됩니다. 앞 메시지가 `FAILURE`이면 뒤 메시지는 앞 메시지가 해결될 때까지 `UNTOUCHED` 상태로 대기합니다.

`allowOutOfOrderExecution = true`로 설정하면 순서 검사를 건너뜁니다. 단순 토큰 전송이나 메시지 순서가 중요하지 않은 경우에 씁니다.

순서가 중요한 워크플로우(상태 머신 전이, 순차 결제 등)는 기본값을 유지하고, 앞 메시지가 `FAILURE`일 때의 복구 경로를 명확히 설계해야 합니다.

## 통합 체크리스트

프로덕션 연동 전 점검할 항목들입니다.

**전송 전 승인**
- [ ] feeToken이 LINK라면 Router에 LINK `approve` 완료
- [ ] `tokenAmounts`에 토큰이 있다면 Router에 해당 토큰 `approve` 완료
- [ ] `isChainSupported(destChainSelector)` 확인
- [ ] `getSupportedTokens(destChainSelector)`로 전송 토큰 지원 여부 확인

**수수료 처리**
- [ ] `getFee` 호출 결과에 여유분(10% 수준)을 더해 승인 금액 설정

**수신 컨트랙트**
- [ ] `msg.sender == router` 검증(onlyRouter) 적용
- [ ] `sourceChainSelector`와 sender 주소 화이트리스트 검증
- [ ] `messageId` 기반 중복 실행 방지
- [ ] `_ccipReceive` 로직 멱등성 확보
- [ ] `extraArgs.gasLimit`이 실제 실행 가스보다 충분히 큰지 확인

**오류 복구**
- [ ] `FAILURE` 메시지에 대한 `manuallyExecute` 권한 보유자(EOA 또는 다중서명) 지정
- [ ] `lockOrBurn` 이후 `releaseOrMint` 전에 실행이 실패해 토큰이 묶이는 케이스 대응 방안

**테스트**
- [ ] Chainlink 제공 `CCIP-BnM` 테스트 토큰으로 테스트넷 E2E 완료
- [ ] 컨트랙트 업그레이드 시 Router 주소 변경 가능성 고려

## 함께 보면 좋을 자료

- [Chainlink CCIP 공식 문서](https://docs.chain.link/ccip) — 아키텍처 개요, API 레퍼런스, 지원 네트워크
- [CCIP GitHub 소스 코드](https://github.com/smartcontractkit/chainlink/tree/develop/contracts/src/v0.8/ccip) — Router, OnRamp, OffRamp, TokenPool 구현체
- [CCIP Hardhat Starter Kit](https://github.com/smartcontractkit/ccip-starter-kit-hardhat) — 전송·수신 예제 코드
- [CCIP Explorer](https://ccip.chain.link) — 크로스체인 메시지 추적 대시보드
- [CCIP Best Practices](https://docs.chain.link/ccip/best-practices) — 공식 권장 패턴과 보안 주의사항

## 참고 자료

- [Chainlink CCIP Architecture](https://docs.chain.link/ccip/architecture) — docs.chain.link, 조회일 2026-06-30
- [Chainlink CCIP API Reference](https://docs.chain.link/ccip/api-reference) — docs.chain.link, 조회일 2026-06-30
- [Chainlink CCIP Best Practices](https://docs.chain.link/ccip/best-practices) — docs.chain.link, 조회일 2026-06-30
- [CCIP Supported Networks](https://docs.chain.link/ccip/supported-networks) — docs.chain.link, 조회일 2026-06-30
- [CCIP Source Code (smartcontractkit/chainlink)](https://github.com/smartcontractkit/chainlink/tree/develop/contracts/src/v0.8/ccip) — github.com/smartcontractkit, 조회일 2026-06-30
- [CCIP Starter Kit (Hardhat)](https://github.com/smartcontractkit/ccip-starter-kit-hardhat) — github.com/smartcontractkit, 조회일 2026-06-30
