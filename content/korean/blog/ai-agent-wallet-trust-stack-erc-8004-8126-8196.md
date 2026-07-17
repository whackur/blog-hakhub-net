---
title: "AI 에이전트 신뢰 스택: ERC-8004, ERC-8126, ERC-8196"
meta_title: ""
description: "AI 에이전트가 사용자를 대신해 온체인 자산을 다룰 때 필요한 신원·검증·정책 실행 3계층 표준 ERC-8004, ERC-8126, ERC-8196을 정리합니다."
date: 2026-06-30T07:00:00+09:00
lastmod: 2026-07-17T17:50:08+09:00
image: ""
categories: ["Blockchain"]
tags: ["ai-agent", "wallet", "erc-8004", "erc-8126", "erc-8196"]
author: "whackur"
translationKey: "ai-agent-wallet-trust-stack-erc-8004-8126-8196"
draft: false
---

AI 에이전트가 사용자를 대신해 자산을 쓰고, 컨트랙트를 호출하고, 유료 API에 접근하는 시대가 가까워지면서 "이 에이전트를 믿고 돈을 맡겨도 되는가"라는 질문이 실질적인 설계 문제가 됐다. 블록체인 커뮤니티는 이 문제를 세 계층으로 나눠 접근하고 있다. 신원 등록(ERC-8004), 보안 검증(ERC-8126), 정책 기반 실행(ERC-8196)이다.

## 자율 에이전트와 신뢰 문제

사람이 MetaMask로 직접 트랜잭션에 서명할 때는 서명 주체가 명확하다. AI 에이전트가 자동으로 거래를 실행할 때는 세 가지 문제가 생긴다.

첫째, **식별 문제**다. 서로 다른 조직이 만든 에이전트들이 상호작용하려면 공통 등록 체계가 필요하다. 에이전트가 "나는 결제 에이전트다"라고 주장해도 상대방이 그 주장을 독립적으로 확인할 방법이 없으면 의미가 없다. 각 플랫폼이 독자적인 에이전트 목록을 유지하면 규모가 커질수록 파편화된다.

둘째, **검증 문제**다. 에이전트가 등록되어 있다고 해서 안전하다는 보장은 없다. 스마트 컨트랙트 코드에 취약점이 있거나 지갑이 이미 알려진 악성 주소와 연결되어 있을 수 있다. 등록 자체는 발견 가능성을 줄 뿐, 안전성 평가는 별도 계층의 역할이다.

셋째, **위임 범위 문제**다. 에이전트에게 private key를 그대로 맡기면 에이전트가 정책과 무관하게 임의 거래를 낼 수 있다. 소유자가 허용 행동, 허용 컨트랙트, 금액 한도, 유효 기간을 미리 지정하고 지갑이 그 범위 안에서만 실행해야 한다.

Ethereum 커뮤니티는 이 세 문제를 별개의 ERC 표준으로 접근한다. 각 계층은 독립적으로 쓸 수 있지만, 고위험 자동 거래에서는 세 계층을 함께 쓰는 것이 권장된다.

## ERC-8004: Trustless Agents

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004)는 사전 신뢰 없는 조직과 플랫폼 경계를 넘어 AI 에이전트를 발견하고 상호작용하기 위한 표준이다. 2026년 1월 29일 이더리움 메인넷에 배포됐으며, 이후 BSC와 Base로 확장됐다. ethereum/ercs 저장소 기준 표준 프로세스 상태는 Draft다. 저자는 Marco De Rossi, Davide Crapis, Jordan Ellis, Erik Reppel이다.

ERC-721, EIP-712, EIP-155, ERC-1271을 기반으로 세 레지스트리를 정의한다.

**Identity Registry**

에이전트는 ERC-721 NFT처럼 등록·소유·이전된다. `tokenId`가 `agentId`, `tokenURI`가 `agentURI`로 쓰인다. 전역 식별자는 다음 형태다.

```
agentRegistry = {namespace}:{chainId}:{identityRegistry}
agentId       = ERC-721 tokenId
```

`agentURI`가 가리키는 에이전트 등록 JSON 파일에는 이름, 설명, 서비스 endpoint, 지원하는 신뢰 모델(reputation, crypto-economic, tee-attestation 등)이 담긴다. 등록 파일은 발견 가능성과 식별성을 제공하는 것이지 에이전트 안전성을 보증하지는 않는다. 그 역할은 나머지 두 레지스트리가 담당한다.

**Reputation Registry**

클라이언트가 에이전트에 피드백을 게시하고 조회하는 인터페이스다. `starred`, `reachable`, `uptime`, `responseTime` 같은 tag로 분류하고 고정소수점 value를 기록한다. 중요한 점은 Sybil 공격을 막기 위해 신뢰할 수 있는 `clientAddresses` 집합으로 필터링해야 한다는 것이다. Registry 자체는 범용 게시판이고, 신뢰할 클라이언트 선정은 애플리케이션 계층의 책임이다. 2026년 5월 기준 배포된 에이전트 다수가 플레이스홀더로 등록된 것으로 확인되어 평판 데이터의 실질적 신뢰성은 아직 낮다.

**Validation Registry**

에이전트 작업 검증 요청과 검증자 응답을 온체인에 기록한다. `response`는 0~100 값이며 이진 검증에는 0(실패)/100(통과)으로 쓸 수 있다. `tag`로 `tee-attestation`, `zkml`, `reexecution` 같은 검증 유형을 분류한다.

ERC-8004는 단일 신뢰 모델을 강제하지 않는다. 피자 주문 같은 저가 작업과 의료 진단 같은 고위험 작업에 같은 검증 비용을 요구하지 않는 것이 설계 원칙이다.

## ERC-8126: AI Agent Verification

ERC-8004는 에이전트의 존재와 소유권을 기록하지만, 그 에이전트가 실제로 안전한지는 알려주지 않는다. ERC-8126은 이 검증 계층을 담당한다. 외부 보안 검증 제공자가 등록된 에이전트의 지갑 이력, 컨트랙트 코드, web endpoint, 미디어를 평가하고 0~100 위험 점수를 제공하는 인터페이스를 정의한다. 점수가 낮을수록 안전하다.

[ERC-8126](https://eips.ethereum.org/EIPS/eip-8126)은 2026년 6월 2일 `Final` 상태로 이동했다. 저자는 Leigh Cronian(@cybercentry), Chris Johnson(Virtuals)이다.

핵심 설계는 개별 파라미터를 직접 제출받지 않는다는 것이다. `walletAddress`, `url`, `contractAddress`를 따로 넘기는 게 아니라, ERC-8004의 `agentId`로 등록 메타데이터를 해석한다. 검증 결과가 특정 등록 에이전트 신원에 귀속되도록 만드는 장치다.

**검증 타입 5종**

- **ETV (Ethereum Token Verification)**: 컨트랙트 주소의 배포 여부와 기본 보안성 검사. OWASP SCSVS 준수 권장.
- **MCV (Media Content Verification)**: 에이전트 이미지·미디어의 AI 생성 여부, 출처, 무결성 검증. C2PA 프레임워크 사용 권장.
- **SCV (Solidity Code Verification)**: Solidity 코드의 재진입·flash loan·접근 제어 등 취약 패턴 검사.
- **WAV (Web Application Verification)**: HTTPS endpoint 응답, TLS 유효성, 피싱·endpoint hijacking 위험 평가.
- **WV (Wallet Verification)**: 지갑 소유 확인, 온체인 거래 이력, threat intelligence database 대조.

추가로 PDV (Private Data Verification)는 ZKP(영지식 증명, zero-knowledge proof) proof로 상세 결과를 숨기고, QCV (Quantum Cryptography Verification)는 양자 리스크 완화를 위한 선택 옵션이다.

**위험 점수**

검증 결과는 0~100 위험 점수로 요약된다. 0에 가까울수록 안전하고, 80 이상이면 Critical tier다. 이 점수는 "신뢰 점수"가 아니라 "위험 점수"라는 점을 명확히 해야 한다.

| Tier | 범위 |
|------|------|
| Low Risk | 0~20 |
| Moderate | 21~40 |
| Elevated | 41~60 |
| High Risk | 61~80 |
| Critical | 81~100 |

Final 상태로 이동했다는 것은 스펙이 구현 기준으로 참조 가능한 단계라는 의미다. 특정 검증 제공자의 품질을 보증하지는 않는다.

## ERC-8196: AI Agent Authenticated Wallet

에이전트의 신원을 확인하고(ERC-8004) 위험도를 평가했다면(ERC-8126), 실제 거래 실행을 어떻게 제한할지가 남는다. private key를 에이전트에게 그대로 맡기면 에이전트가 정책과 무관하게 임의 거래를 낼 수 있다. ERC-8196은 이 문제를 정책 등록 방식으로 푼다. 소유자가 허용 행동, 허용 컨트랙트, 금액 한도, 유효 기간을 정책으로 지정하고, 지갑은 그 정책 안에서만 에이전트 요청을 실행한다. 에이전트에게 private key를 주는 것이 아니라 제한된 실행 권한만 위임하는 구조다.

[ERC-8196](https://eips.ethereum.org/EIPS/eip-8196)의 표준 프로세스 상태는 Last Call이고 last-call-deadline은 2026-07-14다. Last Call은 여전히 동료 검토 단계이지 Final이 아니므로, 검토 과정에서 interface와 보안 모델이 바뀔 수 있다. 저자는 Leigh Cronian(@cybercentry), Chris Johnson이다.

**Agent Policy 구성**

```
policyId        → 정책 고유 식별자
agentAddress    → 권한을 받은 AI 에이전트 주소
agentId         → ERC-8004 Identity Registry의 에이전트 tokenId
ownerAddress    → 자산 소유자 / 위임자
allowedActions  → 허용된 행동 목록 (예: transfer, swap)
allowedContracts → 호출 가능한 컨트랙트 allowlist
blockedContracts → 호출 금지 컨트랙트 blocklist
maxValuePerTx   → 거래 1건당 최대 금액
maxValuePerDay  → 하루 최대 지출한도 (선택)
validAfter      → 정책 시작 시각
validUntil      → 정책 만료 시각
minVerificationScore → 허용 가능한 ERC-8126 위험 점수 상한
```

`agentId`는 필수 필드다. `registerPolicy` 호출 시 에이전트 주소와 함께 등록하며, 실행 시점의 ERC-8126 검증에 그대로 쓰인다. 구현체는 `executeAction`을 처리하기 전에 정책의 `agentId`로 `getLatestRiskScore`를 호출해 ERC-8126 위험 점수를 확인해야 한다(MUST).

`minVerificationScore`라는 이름이 직관과 어긋난다. ERC-8126 risk score는 낮을수록 안전하므로, 실제로는 "허용 가능한 최대 위험 점수"처럼 다뤄야 한다. 조회한 위험 점수가 이 값을 넘으면 실행이 거부된다. 예를 들어 값이 20이면 Low Risk tier(0~20)만 자동 실행을 허용한다.

**인터페이스**

핵심 함수는 네 가지다. `registerPolicy`는 에이전트 주소와 `agentId`, 행동·컨트랙트 allowlist, 한도, 유효 기간, `minVerificationScore`를 등록한다. `executeAction`은 `policyHash`, 대상 주소, 금액, calldata, nonce, entropy commitment, 서명을 받아 `(bool success, bytes32 auditEntryId)`를 반환한다. `revokePolicy`와 `getPolicy`가 나머지 두 함수다. 이벤트는 `PolicyRegistered`, `ActionExecuted`, `PolicyRevoked`, `AuditEntryLogged`이고, 에러는 `PolicyExpired`, `ValueExceedsLimit`, `InvalidSignature`, `EntropyVerificationFailed`, `PolicyViolation`이다.

**감사 로그**

각 audit entry는 `previousHash`를 포함해 hash chain을 형성한다. 중간 항목을 삭제하거나 변경하면 이후 hash 연결이 깨진다. 전체 로그를 온체인에 저장하지 않고 IPFS 같은 오프체인 저장소에 두고 Merkle root만 ERC-8004 Validation Registry에 게시할 수 있다.

**EIP-712 서명**

action과 delegation은 EIP-712 typed data로 서명한다. 사용자가 blind hash가 아니라 자신이 승인하는 내용을 읽고 서명할 수 있다.

**EIP-4337 호환**

EIP-4337 account abstraction wallet 또는 policy enforcement module로 구현할 수 있어 기존 AA wallet 생태계와 결합이 가능하다.

## 세 표준의 관계

![ERC-8004 신원·평판·검증 레지스트리에서 ERC-8126 위험 점수를 거쳐 ERC-8196 정책 검사를 통과한 뒤 지갑 트랜잭션이 실행되는 AI 에이전트 지갑 신뢰 스택 다이어그램](/images/posts/ai-agent-wallet-trust-stack-erc-8004-8126-8196/trust-stack-layers.svg)

*이 다이어그램은 ERC-8004·ERC-8126·ERC-8196을 하나의 흐름으로 합성한 개념도다. 세 표준을 반드시 함께 묶어 구현해야 한다는 뜻은 아니며, 각 계층은 독립적으로도 쓸 수 있다.*

ERC-8004가 "이 에이전트가 누구인가"를 답하고, ERC-8126이 "이 에이전트가 안전한가"를 평가하며, ERC-8196이 "지금 이 행동이 소유자 정책 안에서 허용되는가"를 실행 단계에서 검증한다.

## 보안 한계

세 표준 모두 한계를 명확히 인식해야 한다.

- 등록 파일은 발견 가능성을 줄 뿐 에이전트 안전성을 직접 보증하지 않는다
- 평판은 Sybil 공격에 취약하며, 신뢰할 피드백 제공자 필터링이 애플리케이션 책임이다
- ERC-8126 risk score가 낮아도 에이전트의 선의를 보장하지 않는다. 특정 시점 기술 검증 결과일 뿐이다
- ERC-8004는 메인넷에 배포되어 있으나 표준 프로세스 상태가 Draft여서 인터페이스 명세가 바뀔 수 있다
- ERC-8196의 표준 프로세스 상태는 Last Call이다(last-call-deadline: 2026-07-14). Last Call은 Final이 아닌 동료 검토 단계이므로 interface와 보안 모델이 여전히 바뀔 수 있다
- host manipulation은 ERC-8196으로도 완전히 제거되지 않으며, 고가치 에이전트에는 여러 independent host 사용이 권장된다
- 검증 제공자 품질은 제각각이다. ERC-8126이 Final이라는 사실이 그 스펙을 구현한 개별 제공자의 품질을 보증하지 않는다

## 함께 보면 좋을 자료

- [ERC-8004 에이전트 평판: 온체인 등록과 조회](../erc8004-agent-reputation-registry-lookup) — Reputation Registry 실전 사용법 (이 블로그)
- [ERC-8004 원문](https://eips.ethereum.org/EIPS/eip-8004) — Ethereum EIPs, Draft (표준 프로세스); 2026-01-29 메인넷 배포
- [ERC-8126 원문](https://eips.ethereum.org/EIPS/eip-8126) — Ethereum EIPs, Final
- [ERC-8196 원문](https://eips.ethereum.org/EIPS/eip-8196) — Ethereum EIPs, Last Call (마감 2026-07-14)
- [ERC-8126 Ethereum Magicians 토론](https://ethereum-magicians.org/t/erc-8126-ai-agent-verification/27445)
- [ERC-8004.org 공식 출범 발표](https://www.8004.org/blog/welcome-to-8004) — 2026-01-29

## 참고 자료

- [ERC-8004: Trustless Agents](https://eips.ethereum.org/EIPS/eip-8004) — ethereum.org, Draft (표준 프로세스), 2026-01-29 메인넷 배포, 조회일 2026-07-04
- [ERC-8126: AI Agent Verification](https://eips.ethereum.org/EIPS/eip-8126) — ethereum.org, Final (2026-06-02), 조회일 2026-07-04
- [ERC-8196: AI Agent Authenticated Wallet](https://eips.ethereum.org/EIPS/eip-8196) — ethereum.org, Last Call (last-call-deadline 2026-07-14), 조회일 2026-07-15
- [ethereum/ercs GitHub](https://github.com/ethereum/ercs) — 원문 소스, 조회일 2026-07-04
- [8004.org 공식 출범 발표](https://www.8004.org/blog/welcome-to-8004) — ERC-8004 공식 사이트, 2026-01-29, 조회일 2026-06-30
- [arXiv 2606.26028v1](https://arxiv.org/abs/2606.26028) — Ethereum, BSC, Base 배포 분석 연구, 조회일 2026-06-30
