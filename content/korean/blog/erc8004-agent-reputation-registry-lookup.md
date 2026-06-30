---
title: "ERC-8004 에이전트 평판: 온체인 등록과 조회"
meta_title: ""
description: "ERC-8004는 단일 컨트랙트가 아닌 레지스트리 세트다. giveFeedback()으로 Reputation Registry에 피드백을 등록하고, getSummary()로 신뢰 집합 기준 집계 조회하는 방법. 배포된 컨트랙트 주소와 생태계 서비스 현황."
date: 2026-06-30T15:00:00+09:00
lastmod: 2026-06-30T15:45:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["ai-agent", "erc-8004", "reputation", "smart-contract", "onchain"]
author: "whackur"
translationKey: "erc8004-agent-reputation-registry-lookup"
draft: false
---

[지난 글](../ai-agent-wallet-trust-stack-erc-8004-8126-8196)에서 ERC-8004/8126/8196 신뢰 스택 개요를 살펴봤다. ERC-8004는 AI 에이전트 신원 등록(Identity Registry), 평판 기록(Reputation Registry), 작업 검증(Validation Registry) 세 레지스트리를 정의하는 Ethereum Draft 표준이다. 개념 설명은 그 글에 정리돼 있으니, 여기서는 중복하지 않는다.

이 글의 초점은 두 가지다. Reputation Registry에 피드백을 어떻게 온체인에 등록하고 조회하는지, 그리고 현재 이 레지스트리 데이터를 인덱싱하는 서비스들이 무엇인지.

## 레지스트리 세트 구조

ERC-8004는 단일 라우터 컨트랙트가 아니다. Identity Registry, Reputation Registry, Validation Registry 세 컨트랙트로 이뤄진 레지스트리 세트다. 각 컨트랙트는 독립적인 주소를 갖고, 호출도 각 컨트랙트에 직접 보낸다.

Reputation Registry는 초기화 시 Identity Registry 주소를 `initialize(address identityRegistry_)`로 받아 내부 `_identityRegistry`에 저장한다. `getIdentityRegistry()`로 연결된 Identity Registry 주소를 확인할 수 있다. 이 연결로 `giveFeedback()` 호출 시 Identity Registry에서 에이전트 존재 여부를 확인하고, 에이전트 소유자·운영자의 자작 피드백을 거부한다.

`giveFeedback()`에는 레지스트리 주소 파라미터가 없다. 트랜잭션 자체를 원하는 Reputation Registry 컨트랙트 주소(`tx.to`)로 보내면 된다. 어느 Reputation Registry 주소를 신뢰하고 쓸지는 애플리케이션이 결정한다. 피드백은 Identity Registry를 거치지 않고 Reputation Registry 스토리지에 직접 저장된다.

## Reputation Registry 구조

Reputation Registry는 퍼미션리스 온체인 게시판이다. 에이전트 소유자·운영자를 제외한 어떤 주소든 어느 에이전트에나 피드백을 올릴 수 있고, 레지스트리는 피드백의 진위를 판단하지 않는다.

레지스트리는 스팸이나 자작 리뷰를 막지 않는다. **피드백 신뢰성 판단은 조회 측의 책임이다.** 피드백을 읽을 때 신뢰하는 클라이언트 주소 집합을 직접 넘겨야만 집계된 요약을 얻을 수 있다. 레지스트리가 점수 하나를 내려주는 구조가 아니라, 필터링 기준을 호출자가 정하는 구조다.

## 저장 구조

온체인에 남는 Feedback struct는 다섯 필드다.

```solidity
struct Feedback {
    int128 value;
    uint8 valueDecimals;
    bool isRevoked;
    string tag1;
    string tag2;
}
```

- `value` (int128): 피드백 점수 정수부. 음수도 허용된다(`[-1e38, 1e38]` 범위).
- `valueDecimals` (uint8): 소수점 위치. 0 이상 18 이하. `value=9950, valueDecimals=2`는 소비자가 99.50으로 해석한다.
- `isRevoked` (bool): 피드백 취소 여부.
- `tag1`, `tag2` (string): 피드백 분류 태그.

`giveFeedback()` 호출 시 `value`/`valueDecimals`를 0~100 정수로 정규화하지 않는다. 입력한 값 그대로 저장된다.

`feedbackURI`(오프체인 URL)와 `feedbackHash`(URI 내용의 keccak256)는 struct에 넣지 않고 이벤트로 emit한다. 온체인 저장 비용을 줄이면서, 오프체인 인덱서로 복원 가능하게 설계한 것이다.

인덱싱은 3차원: `agentId → clientAddress → feedbackIndex`. 인덱스는 1부터 시작한다. `_lastIndex[agentId][client] == 0`이면 해당 클라이언트가 남긴 피드백이 없다는 뜻이다.

## 피드백 등록: giveFeedback()

```solidity
function giveFeedback(
    uint256 agentId,
    int128 value,
    uint8 valueDecimals,
    string calldata tag1,
    string calldata tag2,
    string calldata endpoint,
    string calldata feedbackURI,
    bytes32 feedbackHash
) external;
```

파라미터별 의미:

- **agentId**: Identity Registry에 등록된 에이전트의 ERC-721 토큰 ID.
- **value, valueDecimals**: 고정소수점 점수. `valueDecimals <= 18`. 품질 점수 85를 주려면 `value=85, valueDecimals=0`. 업타임 99.5%라면 `value=9950, valueDecimals=2` (소비자가 99.50으로 해석).
- **tag1, tag2**: 피드백 분류 문자열. 자유 문자열이며, 빈 문자열도 유효하다.
- **endpoint**: 피드백 대상 에이전트 엔드포인트. 에이전트 전체 대상이면 빈 문자열.
- **feedbackURI**: 상세 피드백을 담은 오프체인 URI. IPFS가 권장 방식이고, HTTPS도 가능하다.
- **feedbackHash**: feedbackURI 내용의 keccak256 해시. 오프체인 데이터 위변조 감지용.

트랜잭션을 보내는 지갑 주소(msg.sender)가 `clientAddress`로 이벤트에 기록된다. 피드백 1건 = 트랜잭션 1건이다. 호출자가 `agentId`의 소유자 또는 운영자이면 컨트랙트가 거부한다.

**예시:** 에이전트 ID 42에 품질 점수 85를 등록한다면.

```
agentId        = 42
value          = 85
valueDecimals  = 0
tag1           = "quality"
tag2           = ""
endpoint       = ""
feedbackURI    = "ipfs://Qm..."
feedbackHash   = 0xabc123...
```

온체인 Feedback struct에는 `value=85`, `valueDecimals=0`으로 저장된다. 소비자가 85.0으로 해석한다.

## 평판 조회와 Sybil 방어

```solidity
function getSummary(
    uint256 agentId,
    address[] calldata clientAddresses,
    string calldata tag1,
    string calldata tag2
) external view returns (uint64 count, int128 summaryValue, uint8 summaryValueDecimals);
```

반환 튜플:

- `count`: 집계에 포함된 피드백 건수.
- `summaryValue`: 집계 평균 점수 (정수부).
- `summaryValueDecimals`: 집계 결과의 소수점 위치.

집계 방식: 포함된 피드백 각각을 내부에서 18자리 소수점으로 정규화해 평균을 낸 다음, 포함된 피드백 중 가장 빈도가 높은 `valueDecimals` 값으로 스케일을 맞춰 반환한다.

`clientAddresses`는 빈 배열을 넘길 수 없다. 빈 배열이면 `clientAddresses required` 오류로 revert된다. 이것이 Sybil 방어를 강제하는 핵심이다. 누구나 피드백을 올릴 수 있는 구조에서 전체 피드백을 단순 평균 내면 자작 리뷰에 오염된다. 조회자가 신뢰하는 클라이언트 주소 집합을 직접 제공해야만 집계 결과를 얻는다.

## 신뢰 결정: 두 단계

ERC-8004 Reputation Registry를 활용할 때 실제로는 두 가지 신뢰 결정이 있다.

1. **어느 Reputation Registry 컨트랙트 주소를 신뢰할 것인가.** 네트워크마다 어느 Reputation Registry에 쓰고 읽을지 정해야 한다. 현재 mainnet에서 널리 쓰이는 주소는 `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63`이다.
2. **getSummary()에 어느 클라이언트 주소를 포함할 것인가.** 레지스트리 주소를 정했다 해도, 그 레지스트리 안에서 어떤 피드백 제출자를 신뢰할지는 별개로 결정해야 한다. 이 선택이 집계 결과 품질을 결정한다. 서비스 내에서 활동한 클라이언트 주소, 제3자 기관이 검증한 주소 등이 선택지다.

## 추가 조회 함수

단일 피드백 조회나 전체 피드백 일괄 조회에는 아래 함수를 사용한다.

```solidity
function getLastIndex(uint256 agentId, address clientAddress) external view returns (uint64)
function readFeedback(uint256 agentId, address clientAddress, uint64 feedbackIndex)
    external view returns (int128 value, uint8 valueDecimals, string memory tag1, string memory tag2, bool isRevoked)
function readAllFeedback(uint256 agentId, address[] calldata clientAddresses, string calldata tag1, string calldata tag2, bool includeRevoked) external view returns (...)
```

특정 클라이언트의 피드백을 순서대로 읽으려면, 먼저 `getLastIndex(agentId, clientAddress)`로 마지막 인덱스를 확인하고, `readFeedback(agentId, clientAddress, i)`를 `i=1..lastIndex` 범위로 반복 호출한다.

## 배포된 컨트랙트 주소

ERC-8004 레지스트리는 CREATE2를 써서 결정적(deterministic) 주소로 배포된다. 같은 주소가 Ethereum, Base, BNB Chain, Arbitrum, OP Mainnet, Polygon, Avalanche, Mantle, Scroll, Gnosis 10개 이상 mainnet에서 byte-identical로 동작한다.

| 레지스트리 | mainnet 주소 |
|-----------|------|
| Identity Registry | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| Reputation Registry | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` |
| Validation Registry | mainnet 미출시 (testnet 한정) |

주소가 `0x8004...`로 시작하는 것은 vanity 프리픽스다. Etherscan, Basescan, BSCScan 등 일반 블록 익스플로러에서 바로 조회 가능하다. **테스트넷 주소는 mainnet과 다르다.** 사용 전 [QuickNode ERC-8004 Explorer](https://erc-8004.quicknode.com)의 컨트랙트 문서에서 체인별 주소를 확인한다.

주소 정보 출처: QuickNode ERC-8004 Explorer 컨트랙트 문서(2026-05-05 갱신 기준).

## 생태계 서비스

ERC-8004 레지스트리 데이터를 인덱싱하거나 탐색하는 서비스들이 운영 중이다.

| 서비스 | URL | 역할 |
|--------|-----|------|
| Agentscan | [agentscan.info](https://agentscan.info) | Alias(AliasAI) 운영. 21개+ 체인 ERC-8004 에이전트 검색·탐색. OASF taxonomy 분류, 평판 점수, 온체인 활동 표시. 공개 에이전트와 StarCards 기반 private 에이전트를 함께 인덱싱한다. |
| QuickNode ERC-8004 Explorer | [erc-8004.quicknode.com](https://erc-8004.quicknode.com) | 에이전트 탐색(explorer)과 개발자 문서를 함께 제공한다. 피드백 제출 튜토리얼(viem 기준), 컨트랙트 주소·ABI 문서, 체인별 인덱서 설정이 포함된다. quality/safety/cost/speed/accuracy 태그를 관습으로 집계한다. |
| 8004agents.ai | [8004agents.ai](https://8004agents.ai) | 멀티체인 ERC-8004 에이전트 트래커. 평판 점수, validation 상태 표시. (일부 정보 미검증) |
| 8004.org | [8004.org](https://www.8004.org) | ERC-8004 공식 사이트. 2026-01-29 mainnet 출범과 함께 오픈. |
| DeepWiki erc-8004-contracts | [deepwiki.com/erc-8004/erc-8004-contracts](https://deepwiki.com/erc-8004/erc-8004-contracts) | 레퍼런스 컨트랙트 API·저장 구조 문서. 개발자용. |
| Allium 블로그 | [allium.so](https://www.allium.so) | ERC-8004 온체인 데이터 분석. MetaMask, Ethereum Foundation, Google, Coinbase 기여자 포함. |

## 태그 관습 차이

스펙의 예시 태그는 `starred`, `reachable`, `uptime`, `responseTime`이다. QuickNode ERC-8004 Explorer가 집계하는 관습 태그는 `quality`, `safety`, `cost`, `speed`, `accuracy`다.

태그는 자유 문자열이므로 어떤 값도 쓸 수 있지만, 정확히 같은 문자열끼리만 함께 집계된다. `"quality"`와 `"Quality"`는 서로 다른 태그다. 각 explorer와 애플리케이션이 자체 관습 태그 집합을 정의하고 그 기준으로 집계한다. 이것이 "게시판 구조만 정의하고, 점수 해석은 애플리케이션 책임으로 남긴다"는 표준의 설계 철학을 잘 보여주는 지점이다.

커스텀 태그를 정의할 때는 생태계 내에서 합의된 레이블을 쓰지 않으면 다른 서비스의 집계에 포함되지 않는다는 점을 고려해야 한다.

## 주의사항

**Draft 상태.** ERC-8004는 현재 Draft다([ethereum/ERCs](https://github.com/ethereum/ERCs/blob/master/ERCS/erc-8004.md)). 인터페이스는 언제든 변경될 수 있다. 상용 연동 전 스펙 변경 이력을 추적한다.

**플레이스홀더 에이전트 다수.** 2026년 5월 기준, 레지스트리에 등록된 에이전트 상당수가 실질 활동이 없는 placeholder다. 평판 데이터의 실질 신뢰성은 낮다.

**Sybil 공격 노출.** `getSummary()` 호출 시 `clientAddresses`를 잘못 설정하면 자작 리뷰에 오염된 점수를 받는다. 신뢰 집합 구성이 서비스 품질을 결정한다.

**오프체인 URI 무결성.** `feedbackHash`로 위변조를 감지할 수 있지만, HTTPS 서버처럼 오프체인 스토리지가 사라지면 상세 피드백 내용을 복원할 수 없다. IPFS 같은 콘텐츠 주소 체계를 권장한다.

**Validation Registry 미출시.** TEE attestation flow 확정 중으로 현재 testnet 한정 운영이다. 작업 검증 기능은 mainnet 출시를 기다려야 한다.

## 정리

ERC-8004 Reputation Registry는 퍼미션리스 게시판으로 설계됐다. Identity Registry, Reputation Registry, Validation Registry 세 컨트랙트로 이뤄진 레지스트리 세트이며, 각 컨트랙트에 직접 트랜잭션을 보낸다. 피드백은 `value`/`valueDecimals` 고정소수점 값 그대로 저장되고, `getSummary()`가 신뢰 집합 기준으로 집계한다. 어느 레지스트리 주소를 신뢰할지, 어느 클라이언트를 신뢰 집합에 넣을지는 별개의 두 결정이다.

CREATE2 결정적 주소 덕분에 10개 이상 mainnet에서 같은 주소로 동작한다. Agentscan, QuickNode ERC-8004 Explorer 등이 이미 데이터를 인덱싱하고 있다. 다만 Draft 스펙이라 인터페이스 변경 가능성이 있고, 실제 평판 데이터의 신뢰성은 아직 낮다.

## 함께 보면 좋을 자료

- [AI 에이전트 신원·검증·정책: ERC-8004/8126/8196 신뢰 스택](../ai-agent-wallet-trust-stack-erc-8004-8126-8196) — ERC-8004 개념 스택 개요 (이 블로그)
- [QuickNode ERC-8004 Explorer](https://erc-8004.quicknode.com) — 에이전트 탐색 + 피드백 제출 개발자 튜토리얼
- [Agentscan](https://agentscan.info) — 멀티체인 에이전트 검색 서비스
- [erc-8004-contracts 레퍼런스 구현](https://github.com/erc-8004/erc-8004-contracts) — ABI, 저장 구조 소스

## 참고 자료

- [EIP-8004 (Draft)](https://eips.ethereum.org/EIPS/eip-8004) — Ethereum Improvement Proposals, 조회일 2026-06-30
- [ethereum/ERCs: ERC-8004](https://github.com/ethereum/ERCs/blob/master/ERCS/erc-8004.md) — EIP 원문, 조회일 2026-06-30
- [erc-8004/erc-8004-contracts](https://github.com/erc-8004/erc-8004-contracts) — 레퍼런스 컨트랙트 구현, 조회일 2026-06-30
- [QuickNode ERC-8004 Explorer](https://erc-8004.quicknode.com) — 컨트랙트 주소·ABI 문서·피드백 제출 튜토리얼, 조회일 2026-06-30
- [Agentscan](https://agentscan.info) — AI 에이전트 explorer, 조회일 2026-06-30
- [8004.org](https://www.8004.org) — ERC-8004 공식 사이트, 조회일 2026-06-30
- [DeepWiki: erc-8004-contracts](https://deepwiki.com/erc-8004/erc-8004-contracts) — 레퍼런스 컨트랙트 API 문서, 조회일 2026-06-30
- [Allium](https://www.allium.so) — ERC-8004 온체인 데이터 분석, 조회일 2026-06-30
- [arXiv 2606.26028: Can Trustless Agents Be Trusted?](https://arxiv.org/abs/2606.26028) — Ethereum/BSC/Base 배포 실증 연구, 조회일 2026-06-30
