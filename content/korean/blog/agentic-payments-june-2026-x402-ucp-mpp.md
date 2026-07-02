---
title: "에이전트 결제 2026년 6월 동향: x402, UCP, MPP 구현 진전"
meta_title: ""
description: "2026년 6월 x402 auth-capture와 builder-code attribution, UCP idempotency 강화, MPP 구독형 결제 실험, ERC-8126 Final 이동 등 에이전트 결제 스택의 주요 변화를 정리합니다."
date: 2026-06-30T07:00:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
image: ""
categories: ["Blockchain"]
tags: ["agentic-payments", "x402", "ucp", "mpp", "stablecoin"]
author: "whackur"
translationKey: "agentic-payments-june-2026-x402-ucp-mpp"
draft: false
---

2026년 6월 에이전트 결제 관련 오픈소스 프로토콜들이 "에이전트가 결제할 수 있는가"에서 "누가 결제 권한을 갖고, 어떻게 검증하며, 어떻게 추적하는가"로 초점을 이동했다. x402, UCP, MPP/pay.sh, ACP 각각에서 크고 작은 구현 변화가 있었다. 이 글은 2026년 6월 한 달간 관찰된 주요 변화를 정리한다. 수치와 커밋 내용은 직접 확인한 GitHub API·PyPI·npm registry 기준이다.

## 에이전트 결제 개념과 배경

에이전트 결제(agentic payments)는 AI 에이전트가 사람의 실시간 개입 없이 유료 서비스에 자동으로 대금을 지불하는 흐름이다. 기본 시나리오를 보면 이해가 빠르다. 에이전트가 이미지 생성 API를 호출한다. 서버는 HTTP 402 응답으로 payment challenge를 보낸다. "이 주소에, 이 토큰으로, 이 금액을 보내면 콘텐츠를 주겠다"는 명세다. 에이전트는 스테이블코인 결제를 완료하고 결제 증거를 첨부해 재요청한다. 서버가 확인하면 콘텐츠를 돌려준다.

카드 결제를 그대로 쓰면 안 되는 이유가 있다. 카드 결제는 사람이 화면에서 직접 승인하는 구조다. 에이전트가 분당 수십 개의 API를 자동으로 호출할 때마다 사람이 개입할 수 없다. 또한 LLM 추론처럼 실행이 끝나야 금액이 확정되는 종량제 서비스는 거래 전 금액이 고정된다는 카드 결제의 전제와 맞지 않는다.

**결제 흐름의 주요 참여자**

- **요청자(requester)**: 유료 API를 호출하는 AI 에이전트 또는 클라이언트 애플리케이션
- **resource server**: 유료 콘텐츠·서비스를 제공하는 서버. 결제 미완료 요청에 HTTP 402와 payment challenge를 돌려보낸다
- **facilitator**: 요청자를 대신해 온체인 결제를 실행하고 resource server에 결제 증거를 전달하는 중간 서비스
- **merchant**: UCP 맥락에서 상품·서비스를 판매하는 사업자
- **buyer agent**: merchant 플랫폼에서 구매 절차를 처리하는 에이전트
- **payment challenge**: HTTP 402 응답에 담긴, 결제 조건을 서술한 명세
- **settlement(정산)**: 결제 토큰이 실제로 온체인에서 이전되는 행위. fulfillment는 정산 이후 서비스가 실제로 제공되는 단계

**각 프로토콜이 다루는 문제**

현재 에이전트 결제 스택은 단일 프로토콜이 아니라 계층별로 다른 표준이 담당한다.

- **x402**: HTTP 요청/응답 안에서 결제 과제와 응답 흐름을 표준화한다. 즉시 정산 외에 승인과 capture를 분리하는 상거래형 흐름도 지원하며 스테이블코인 결제 중심이다
- **UCP(Universal Commerce Protocol)**: 장바구니·결제 단계에서 구매 동의, 신원 위임, 주문 증거를 다루는 상거래 계층이다
- **MPP/pay.sh**: CLI·MCP 서버 같은 실행 환경에서 결제 시작을 처리하는 도구 계층이다. Solana 기반으로 개발 중이다
- **ACP(Agentic Commerce Protocol)**: OpenAI·Stripe 계열로, 상품 피드와 거래 데이터의 출처 추적에 초점을 맞춘다

아래 내용은 2026년 6월 한 달간 각 프로토콜에서 있었던 구체적인 구현 변화를 정리한다.

## x402: auth-capture, attribution, 사용량 기반 정산

`x402-foundation/x402` 저장소는 6월 한 달간 수십 개의 커밋이 누적됐다. `coinbase/x402`는 같은 기간 거의 활동이 없었고 실질 개발 표면은 Foundation 저장소에 집중되어 있다.

**auth-capture 흐름**

TypeScript `@x402/evm` 클라이언트에 auth-capture payment requirement를 감지하고 ERC-3009(메타트랜잭션 방식 토큰 전송 위임 표준)를 기본값으로, Permit2(Uniswap이 개발한 일회성 서명 위임 방식)를 대안으로 사용해 payer-agnostic `PaymentInfo` hash에 서명하는 흐름이 추가됐다. 승인 시점과 청구(capture) 시점이 분리되는 구조는 전자상거래에서 표준적인 방식이다. 재고 확인 후 청구, 배송 시점 청구 같은 흐름을 x402 위에서 표현할 수 있게 되는 확장이며, 기존의 즉시 정산 한 가지였던 결제 모델이 둘로 늘어난다. 서버와 facilitator 지원은 후속 단계다.

**builder-code attribution**

x402는 ERC-8021 Schema 2 builder codes를 settlement transaction calldata에 CBOR suffix로 붙이는 방식을 문서화했다. `a`는 유료 API를 노출한 애플리케이션 코드, `s`는 결제를 요청하거나 중간에서 처리한 서비스 코드, `w`는 정산 facilitator/wallet 코드다.

6월 중순에는 `s` 필드가 단일 서비스 코드에서 배열로 확장됐다. MCP 서버가 중간에서 유료 API를 호출하고 그 위에 다른 앱이나 agent runtime이 얹히는 구조를 표현하기 위해서다. 결제 경로에 중간 참여자가 둘 이상 있으면 수익 배분, 분쟁 조사, 비용 분석 모두 "단일 클라이언트 ID"가 아니라 참여자 체인을 다뤄야 한다.

**upto 부분 정산**

`upto` EVM scheme 문서가 settle-time verification을 명확화했다. 사용자가 서명한 최대 한도(`permit2Authorization.permitted.amount`)와 실제 정산액(`paymentRequirements.amount`)을 분리 검증해야 한다는 내용이다. LLM token이나 compute처럼 최종 금액이 요청 후 결정되는 API에서 과금액이 승인 한도를 넘지 않도록 보장하는 안전장치다.

**MCP v1 지원**

Python/Go 클라이언트에 x402 v1 결제 challenge 처리가 추가됐다. TypeScript 외 runtime에서도 paid MCP server를 같은 결제 흐름으로 호출할 수 있게 하는 변화다.

**보안/운영 강화**

EOA를 asset 주소로 거부하는 패치(잘못된 자산 주소로 결제 검증하는 사고 방지), 부분 money string 거부(`$0.01abc` 같은 입력 차단), batch settlement에 explicit gas limit 추가(정산 실패 리스크 완화), v1 discovery path params 보존(결제 가능 API route 잘못 매칭 방지)이 포함됐다.

패키지 배포는 5월 29일 PyPI `x402 2.12.0`과 npm `@x402/* 2.14.0`, 6월 12일 PyPI `x402 2.13.0`과 npm `@x402/extensions 2.15.0`이다.

## UCP: idempotency 강화, 동의, 주문 증거

Universal Commerce Protocol(UCP) 저장소에도 의미 있는 변화가 있었다.

**idempotency 409 명시**

같은 idempotency key로 다른 payload가 들어오면 HTTP 409 Conflict로 거절하도록 contract가 명시됐다. `cart-rest.md`, `checkout-rest.md`, `signatures.md`, `split-payments.md`가 수정됐다. 에이전트나 플랫폼이 네트워크 오류 후 retry할 때 같은 key로 다른 cart·checkout body가 섞이면 stale cached response가 잘못 반환되어 잘못된 가격으로 주문이 확정될 수 있다. payload 비교 기준으로는 `Content-Digest` header가 쓰인다. 스펙 한 줄짜리 변경이지만 중복 주문, payload 변조, 감사 기록 불일치를 막는 효과는 실질적이다.

**buyer consent 확장**

cart와 checkout 양쪽에 걸친 purpose별 buyer consent 구조가 추가됐다. 각 purpose에 `granted`, `source`, `description`을 두고, `source`는 현재 동의 상태가 business default인지 platform이 실제 buyer preference로 포착한 값인지 구분한다. 에이전트가 장바구니 탐색 단계부터 analytics·marketing·계정 연결 동의를 다룰 수 있게 되는 기반이다.

**delegated identity providers**

merchant가 신뢰하는 외부 identity provider를 선언하면 platform이 이미 보유한 upstream token으로 identity chaining을 시도하는 흐름이 추가됐다. 적합하지 않으면 business domain direct OAuth로 fallback한다.

**`get_order` 서명 응답**

`Signature`, `Signature-Input`, `Content-Digest` header가 `get_order` 응답에 추가됐다. 에이전트가 주문 상태를 근거로 후속 행동(환불, 배송 변경 등)을 할 때 응답 변조 여부를 확인할 수 있다.

## MPP/pay.sh: 구독형 결제와 onboarding

Solana Foundation의 `solana-foundation/pay` 저장소에 두 가지 실험적 변화가 있었다.

**experimental subscriptions**

`feat: add support for subscriptions [experimental]`가 들어갔다. client-side subscription intent, 402 challenge parsing, `Authorization: Payment` header, subscription persistence, `pay subscriptions list/status/new/cancel/refresh` CLI가 추가됐다. 반복 API·tool 사용을 subscription/delegation으로 묶으려는 방향이다. 다만 server-side activation credential verification과 `create_plan` on-chain broadcast는 아직 TODO로 표시된다. 상용화까지는 추가 구현이 필요하다.

**redeem codes**

`pay setup --redeem CODE` 흐름이 추가됐다. activation campaign code로 MoonPay/onramp TUI를 건너뛰고 gateway hot wallet에서 계정에 자금을 넣는 방식이다. 개발자가 paid API를 처음 테스트할 때 wallet 생성·stablecoin 구입·gas 확보 과정을 압축하는 onboarding 기능이다.

npm `@solana/pay 1.0.18`이 6월 9일 배포됐다.

## ACP: product feed provenance

OpenAI/Stripe 축의 Agentic Commerce Protocol(ACP) 저장소에는 `feed_update_id`와 `last_update_id` 두 필드가 추가됐다. 상품 feed upsert마다 version identifier가 붙고, 각 상품이 마지막으로 어떤 update에서 갱신됐는지 표시된다. 에이전트가 본 상품·가격 데이터가 어느 feed update에서 왔는지 추적할 수 있게 해 환불·분쟁·감사에서 증거 연결을 돕는 변화다.

## ERC-8126 Final, ERC-8273 Draft

Ethereum ERC 쪽에서는 두 신호가 있었다.

[ERC-8126](https://eips.ethereum.org/EIPS/eip-8126) (AI Agent Verification)이 2026년 6월 2일 `Final` 상태로 이동했다. ERC-8004에 등록된 에이전트의 지갑·코드·web endpoint·컨트랙트·미디어를 검증하고 0~100 위험 점수와 ZKP proof를 제공하는 표준이다. Final 이동은 Draft 실험에서 구현 가능한 기준으로 올라섰다는 신호다.

[ERC-8273](https://github.com/ethereum/ercs/blob/master/ERCS/erc-8273.md) (Attestation-Gated Agentic Actions) 초안이 추가됐다. 장기 신원 registry만으로는 "이번 특정 action이 허용됐는가"를 답하기 어렵다는 문제를 겨냥한다. `attestAndCall()` 패턴으로 authorization-and-action을 같은 transaction에서 atomic하게 실행하고, EIP-1153 transient storage(트랜잭션 종료 시 자동 삭제되는 임시 저장소)에 일회성 권한을 써서 transaction이 끝나면 자동 소멸시킨다. Draft이므로 interface와 보안 모델이 변경될 가능성이 높다.

ERC-8004 자체는 6월 한 달간 ethereum/ercs 표준 프로세스 상태 변경이 없었다. 다만 이는 배포 여부와는 다른 이야기다. ERC-8004 레지스트리는 2026년 1월 29일 이더리움 메인넷에 배포된 상태에서 6월을 맞았다.

## 레이어별 분업 구도

6월 한 달간 에이전트 결제 스택의 경쟁이 수렴하는 단일 프로토콜로 가는 게 아니라는 점이 분명해졌다. x402는 HTTP 402 payment challenge와 facilitator settlement를 담당한다. UCP는 cart/checkout의 동의·신원·주문 증거를 정리한다. ERC-8004/8126/8273 계열은 에이전트 신원과 action별 권한 증명을 다룬다. pay.sh/MPP는 실행 환경에서 결제 시작 표면을 다듬는다.

각 레이어가 분리되어 있다는 것은 구현자가 어떤 레이어를 먼저 채택할지 선택할 수 있다는 뜻이기도 하고, 상호운용성이 아직 완성되지 않았다는 뜻이기도 하다. 완전한 에이전트 결제 흐름을 지금 만들려면 네 레이어 각각에서 선택을 내려야 하고, 그 선택들이 표준화된 방식으로 서로 연결되지는 않는다.

지금 연동을 검토한다면 미완성 지점을 짚어둘 필요가 있다. x402 auth-capture는 클라이언트 서명까지만 들어갔고 서버·facilitator 지원이 남아 있다. MPP subscription은 server-side activation 검증과 `create_plan` 온체인 broadcast가 TODO다. ERC-8273은 Draft라 interface가 바뀔 수 있다. 이번 달 기준으로 프로덕션에 바로 얹을 수 있는 변화는 UCP idempotency contract와 x402 보안 패치 정도이고, 나머지는 방향 신호에 가깝다.

## 함께 보면 좋을 자료

- [x402 Foundation GitHub](https://github.com/x402-foundation/x402) — x402 프로토콜 저장소
- [UCP 공식 문서](https://ucp.dev/2026-01-11/specification/overview/) — Universal Commerce Protocol 스펙
- [ERC-8126 원문](https://eips.ethereum.org/EIPS/eip-8126) — AI Agent Verification, Final
- [x402 builder-code extension 문서](https://docs.x402.org/extensions/builder-code) — attribution 코드 명세

## 참고 자료

- [x402 Foundation GitHub](https://github.com/x402-foundation/x402) — 조회일 2026-06-30
- [PyPI — x402](https://pypi.org/project/x402/) — 조회일 2026-06-30
- [npm — @x402/core](https://registry.npmjs.org/@x402/core) — 조회일 2026-06-30
- [UCP GitHub](https://github.com/Universal-Commerce-Protocol/ucp) — 조회일 2026-06-30
- [ACP GitHub](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol) — 조회일 2026-06-30
- [Solana Foundation pay GitHub](https://github.com/solana-foundation/pay) — 조회일 2026-06-30
- [ERC-8126: AI Agent Verification](https://eips.ethereum.org/EIPS/eip-8126) — ethereum.org, Final (2026-06-02), 조회일 2026-06-30
- [ERC-8273 원문](https://github.com/ethereum/ercs/blob/master/ERCS/erc-8273.md) — ethereum/ercs, Draft, 조회일 2026-06-30
