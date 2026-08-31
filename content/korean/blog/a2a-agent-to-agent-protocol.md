---
title: "A2A(Agent-to-Agent) 프로토콜: 에이전트 간 협업 표준과 결제 레이어의 접점"
meta_title: ""
description: "Google이 2025년 4월 공개하고 Linux Foundation에 기증한 A2A 프로토콜의 핵심 개념(Agent Card, Task, Message, Artifact)과 동작 방식, MCP와의 역할 분담, x402·AP2·UCP 결제 확장과 만나는 지점, 2026년 8월 기준 채택 현황과 커뮤니티 비판을 정리합니다."
date: 2026-08-27T10:00:00+09:00
lastmod: 2026-08-28T10:00:00+09:00
image: "/images/posts/a2a-agent-to-agent-protocol/a2a-layer-stack-1200.png"
categories: ["Blockchain"]
tags: ["a2a", "ai-agent", "agentic-payments", "x402", "mcp"]
author: "whackur"
translationKey: "a2a-agent-to-agent-protocol"
draft: false
---

이 블로그에서 [x402·UCP·MPP 결제 동향](/blog/agentic-payments-june-2026-x402-ucp-mpp/)이나 [KYA(Know Your Agent)](/blog/know-your-agent-kya-ai-agent-identity-onchain/) 같은 글을 쓸 때마다 "A2A"라는 단어가 전제처럼 등장했습니다. 에이전트가 다른 에이전트에게 일을 맡기고, 그 대가를 결제하고, 상대가 누구인지 확인한다는 이야기는 전부 "에이전트끼리 어떻게 말을 주고받는가"라는 바닥 층 위에 서 있습니다. 그 바닥 층을 표준화하려는 시도가 A2A(Agent2Agent) 프로토콜입니다.

먼저 결론 하나를 못 박아 두겠습니다. A2A 자체는 블록체인과 아무 관계가 없습니다. HTTP 위에서 JSON을 주고받는 웹 프로토콜이고, 지갑도 토큰도 체인도 스펙에 없습니다. 블록체인은 A2A의 확장(extension) 자리에 결제 레이어로 끼어들어 옵니다. 이 글은 A2A가 무엇인지부터 시작해서, MCP와 어디가 다른지, 결제 확장이 어떤 방식으로 얹히는지, 2026년 8월 시점에 실제로 얼마나 쓰이는지, 그리고 "MCP가 있는데 왜 A2A가 필요한가"라는 회의론까지 순서대로 따라갑니다.

## A2A의 정의와 배경

A2A는 서로 다른 회사가 서로 다른 프레임워크로 만들어 서로 다른 서버에서 돌리는 AI 에이전트들이 **도구가 아니라 에이전트로서** 협업하게 해 주는 개방형 프로토콜입니다. Google Cloud가 [2025년 4월 9일 개발자 블로그](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)에서 Atlassian, Salesforce, SAP, ServiceNow 등 50개 이상의 파트너와 함께 공개했습니다. 발표 글은 다섯 가지 설계 원칙을 내세웁니다. 에이전트의 자율성을 그대로 살리는 것(공유 메모리나 도구 없이도 협업), HTTP·SSE·JSON-RPC 같은 기존 표준 위에 얹는 것, 기본값이 보안인 것, 몇 시간에서 며칠 걸리는 장기 작업을 지원하는 것, 텍스트뿐 아니라 오디오·비디오 같은 여러 모달리티를 다루는 것입니다.

왜 이런 게 필요했는지는 발표 시점의 상황을 보면 이해가 됩니다. 2024년 11월 Anthropic이 공개한 MCP(Model Context Protocol)가 "에이전트가 도구와 데이터에 접근하는 방법"을 빠르게 표준화하고 있었습니다. 그런데 기업 안에는 HR 에이전트, 구매 에이전트, IT 지원 에이전트처럼 각기 다른 벤더가 만든 에이전트가 늘어나고 있었고, 이들이 서로 일을 넘기려면 매번 벤더 쌍마다 맞춤 연동을 해야 했습니다. Google은 발표 글에서 A2A가 MCP를 대체하는 것이 아니라 보완한다고 명시했습니다.

거버넌스는 빠르게 Google 손을 떠났습니다. [2025년 6월 23일](https://developers.googleblog.com/en/google-cloud-donates-a2a-to-linux-foundation/) Google은 스펙·SDK·개발 도구를 Linux Foundation에 기증했고, AWS·Cisco·Google·Microsoft·Salesforce·SAP·ServiceNow가 창립 멤버로 참여했습니다. 이 시점에 지원 조직은 100개를 넘었습니다. 두 달 뒤인 [2025년 8월](https://lfaidata.foundation/communityblog/2025/08/29/acp-joins-forces-with-a2a-under-the-linux-foundations-lf-ai-data/)에는 IBM Research가 BeeAI용으로 만들던 경쟁 프로토콜 ACP(Agent Communication Protocol)가 독립 개발을 멈추고 A2A에 합류했습니다. 2026년 3월 12일에는 [v1.0.0](https://github.com/a2aproject/A2A/releases/tag/v1.0.0)이 태그됐고, 2026년 8월 17일에는 Linux Foundation 산하에서 MCP·AGENTS.md·goose·agentgateway를 관리하는 [AAIF(Agentic AI Foundation)](https://aaif.io/blog/a2a-joins-aaif)로 옮겨 갔습니다. 에이전트↔도구 표준(MCP)과 에이전트↔에이전트 표준(A2A)이 같은 재단 아래 놓인 셈입니다.

### 네 가지 핵심 개념

A2A 스펙은 개념이 많지 않습니다. 네 가지만 잡으면 나머지는 따라옵니다. 아래 설명은 [v1.0 스펙](https://a2a-protocol.org/latest/specification/)을 기준으로 합니다.

**Agent Card**는 에이전트의 명함입니다. 이름, 제공자, 할 수 있는 일(skills), 지원하는 전송 방식과 엔드포인트, 요구하는 인증 방식, 스트리밍·푸시 알림 지원 여부를 JSON 문서 하나에 담습니다. 기본 위치는 `https://{도메인}/.well-known/agent-card.json`이고, 클라이언트는 이 문서를 읽어서 "이 에이전트에게 무엇을 어떻게 맡길 수 있는지"를 알아냅니다. v1.0부터는 카드에 `signatures` 필드가 들어가서 JWS 서명으로 카드 위조를 막습니다(서명 전 RFC 8785 방식으로 정규화).

**Task**는 작업 단위입니다. 서버가 `id`를 발급하고, 상태(`status`), 결과물(`artifacts`), 주고받은 메시지 이력(`history`)을 묶어서 관리합니다. 상태는 여덟 가지입니다. 진행 중 상태가 `SUBMITTED`·`WORKING`, 멈춰서 상대를 기다리는 상태가 `INPUT_REQUIRED`·`AUTH_REQUIRED`, 종료 상태가 `COMPLETED`·`FAILED`·`CANCELED`·`REJECTED`입니다. 뒤에 나오는 결제 확장이 이 가운데 `INPUT_REQUIRED`를 "결제가 필요하다"는 신호로 재활용합니다.

**Message**와 **Part**는 대화의 한 턴과 그 내용물입니다. Message에는 보낸 쪽 역할(`ROLE_USER` 또는 `ROLE_AGENT`)과 Part 배열이 들어가고, Part 하나는 텍스트, 바이너리(`raw`), 원격 파일 참조(`url`) 가운데 하나를 담습니다. 여러 메시지를 하나의 대화로 묶을 때는 `contextId`를 씁니다.

**Artifact**는 Task의 결과물입니다. 보고서 파일, 구조화된 JSON, 생성된 이미지 등 에이전트가 만들어 낸 산출물이 Part로 구성되어 여기에 담깁니다. 중간 메시지와 최종 산출물이 구분되어 있어서 클라이언트가 "대화 로그"와 "받아야 할 것"을 헷갈리지 않습니다.

## 동작 방식

A2A 상호작용은 대체로 다음 순서로 진행됩니다.

1. **발견(discovery)**: 클라이언트 에이전트가 상대 서버의 `/.well-known/agent-card.json`을 GET으로 읽습니다. [공식 문서](https://a2a-protocol.org/latest/topics/agent-discovery/)는 이 well-known URI 외에 큐레이션된 레지스트리(사내 에이전트 카탈로그)와 설정 파일에 직접 박아 두는 방식을 대안으로 제시합니다. 인증한 클라이언트에게만 더 자세한 카드를 주는 `GetExtendedAgentCard`도 있습니다.
2. **위임(delegation)**: 클라이언트가 `SendMessage`로 첫 Message를 보냅니다. 서버는 바로 답을 줄 수도 있고, Task를 만들어 `id`를 돌려주고 비동기로 처리할 수도 있습니다.
3. **메시지 교환**: 서버가 추가 정보가 필요하면 Task를 `INPUT_REQUIRED`로 바꾸고, 클라이언트가 같은 `taskId`로 후속 Message를 보냅니다. 사람 승인이 필요한 human-in-the-loop 흐름도 같은 방식입니다.
4. **진행 상황 수신**: 클라이언트는 `GetTask`로 폴링하거나, `SendStreamingMessage`·`SubscribeToTask`로 SSE(Server-Sent Events) 스트림을 열어 상태 변경과 Artifact 조각을 실시간으로 받거나, 웹훅 주소를 등록해 푸시 알림을 받습니다. 몇 시간 걸리는 작업에서는 연결을 끊고 푸시로 받는 편이 자연스럽습니다.
5. **Artifact 반환**: Task가 `COMPLETED`가 되면 최종 산출물이 `artifacts`에 담겨 옵니다. 실패하면 `FAILED`, 서버가 거절하면 `REJECTED`, 클라이언트가 `CancelTask`로 중단하면 `CANCELED`입니다.

전송 계층은 v1.0에서 세 가지 바인딩이 동등하게 정의됐습니다. JSON-RPC 2.0, gRPC, 그리고 REST 스타일의 HTTP+JSON입니다. 같은 논리 에이전트를 세 방식 가운데 어느 쪽으로든 노출할 수 있고, Agent Card의 `supportedInterfaces`에 각각을 선언합니다. 인증은 OAuth 2.0(v1.0에서 Device Code 흐름 추가, Implicit·Password 흐름 제거, PKCE 옵션), API 키, mTLS 같은 표준 방식을 그대로 씁니다. [v1.0 변경 사항 문서](https://a2a-protocol.org/latest/whats-new-v1/)를 보면 메서드 이름이 `message/send` 같은 경로형에서 `SendMessage` 같은 PascalCase로 바뀌었고, 하나의 엔드포인트가 여러 에이전트를 서비스하는 멀티테넌시를 위해 요청에 `tenant` 필드가 추가되었습니다.

### MCP와 역할 분담

MCP는 AI 모델이나 에이전트가 도구·API·데이터 소스에 접근하는 방법을 표준화한 프로토콜입니다. 서버가 "이런 도구가 있다"고 선언하면 클라이언트(주로 LLM 애플리케이션)가 구조화된 입력을 넣고 구조화된 출력을 받습니다. 대체로 한 번 호출하면 끝나는 함수 호출 모델입니다.

A2A 공식 문서의 [A2A와 MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/) 페이지는 이 차이를 자동차 수리점 예시로 설명합니다. 고객 에이전트가 수리점 매니저 에이전트와 대화하는 것은 A2A입니다("차에서 이상한 소리가 나요"라는 모호한 요청을 여러 턴에 걸쳐 좁혀 갑니다). 정비사 에이전트가 진단 스캐너, 수리 매뉴얼 데이터베이스, 리프트를 조작하는 것은 MCP입니다(정해진 입력과 출력이 있는 도구 호출). 정비사 에이전트가 부품 공급사 에이전트에게 재고를 묻고 주문하는 것은 다시 A2A입니다. 문서의 표현을 빌리면 A2A는 에이전트들이 작업에서 **협력(partnering)** 하는 것이고, MCP는 에이전트가 기능을 **사용(using)** 하는 것입니다.

| 관점 | MCP | A2A |
|------|-----|-----|
| 연결 대상 | 에이전트 ↔ 도구·데이터 | 에이전트 ↔ 에이전트 |
| 상호작용 형태 | 구조화된 입력/출력, 대체로 단발 호출 | 다중 턴, 장기 실행, 상태 있는 Task |
| 상대의 내부 | 도구 스키마가 공개됨 | 상대 에이전트는 불투명(내부 로직·메모리·도구 비공개) |
| 발견 방법 | 서버가 도구 목록 제공 | Agent Card |
| 주 사용처 | 한 에이전트에 기능 붙이기 | 조직·프레임워크 경계를 넘는 위임 |

경계가 완전히 깨끗한 것은 아닙니다. 발표 직후 Hacker News에서 한 개발자(vessenes)가 스펙과 클라이언트 코드를 읽고 "A2A를 구현하면 MCP를 따로 구현할 필요가 없어 보인다"고 평했듯이, 에이전트를 도구처럼 감싸서 MCP로 노출하는 것도 가능하고 실제로 많이 그렇게 합니다. 이 겹침이 뒤에 나오는 회의론의 출발점입니다.

![A2A 스택 계층 다이어그램. 맨 위에 UCP·AP2·A2A x402 확장 같은 선택적 상거래·결제 확장, 그 아래 클라이언트 에이전트와 원격 에이전트가 Agent Card·Task·Message·Artifact를 교환하는 A2A 계층, 그 아래 각 에이전트가 자기 도구에 접근하는 MCP 계층, 맨 아래 HTTP·JSON-RPC·gRPC·SSE·OAuth 전송 계층. A2A 코어에는 블록체인 의존성이 없고 체인은 x402 확장의 정산 단계에만 등장한다는 주석이 있다.](/images/posts/a2a-agent-to-agent-protocol/a2a-layer-stack.svg)

*A2A(가로, 에이전트 간)와 MCP(세로, 에이전트와 도구)의 위치, 그리고 그 위에 선택적으로 얹히는 결제 확장. 체인에 정산하는 상자는 x402 확장 하나뿐입니다. 출처는 각 프로토콜 스펙, 2026-08-28 확인.*

## 블록체인 접점

여기서부터가 이 블로그의 관심사입니다. 다시 강조하면 A2A 코어 스펙에는 블록체인이 등장하지 않습니다. 인증은 OAuth·API 키·mTLS이고, 신원은 도메인과 서명된 Agent Card에 묶이고, 결제라는 개념 자체가 없습니다. 블록체인은 세 경로로 A2A와 만납니다. Google이 만든 a2a-x402 확장, 그 위의 상거래 프로토콜 AP2·UCP, 그리고 학계의 탈중앙 발견 제안입니다.

### x402와 a2a-x402 확장

x402는 HTTP 상태 코드 402 "Payment Required"를 실제로 쓰는 결제 프로토콜입니다. 1990년대 HTTP 스펙에 예약만 되어 있던 이 코드를 Coinbase가 2025년 5월 되살렸습니다. 서버가 결제가 필요한 요청에 402와 함께 "얼마를, 어느 체인의 어느 토큰으로, 어디로" 보내라는 요구 사항을 돌려주면, 클라이언트가 지갑으로 결제 승인에 서명해서 재요청하고, facilitator(서명 검증과 온체인 정산을 대행하는 서비스)가 확인한 뒤 서버가 응답을 내줍니다. 사람이 회원가입하고 카드를 등록하는 대신 에이전트가 요청 한 번에 스테이블코인 몇 센트를 내는 흐름을 목표로 합니다. [x402.org](https://www.x402.org/)는 EVM 계열 체인과 Solana를 지원한다고 밝히고 있고, 2026년 8월 27일 조회 시점에 최근 30일 트랜잭션 7,541만 건, 거래 대금 2,424만 달러, 판매자 2만 2천 곳을 표시했습니다. 거버넌스는 Linux Foundation 산하 x402 Foundation으로 이관되었습니다. 구체적인 구현 사례는 [Apify x402 글](/blog/apify-x402-agentic-payments-coinbase-wallet/)에서 다뤘습니다.

[google-agentic-commerce/a2a-x402](https://github.com/google-agentic-commerce/a2a-x402)는 이 x402 흐름을 A2A Task 안에 넣은 확장입니다. Google이 만들어 google-agentic-commerce 조직에서 관리하며, 2026년 8월 28일 기준 GitHub 스타 554개, 포크 144개, 마지막 push 2026년 8월 4일, 라이선스 Apache-2.0입니다. 스펙 디렉터리에는 v0.1과 v0.2가 함께 들어 있고, 2025년 11월 4일 추가된 [v0.2](https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md)가 최신입니다. 다만 README는 여전히 v0.1을 공식 스펙으로 안내하고 릴리스 태그도 v0.1.0 하나뿐입니다(v0.2.0 태그 없음). v0.2는 태그가 붙은 릴리스가 아니라 main 브랜치에 올라온 최신 스펙으로 읽어야 합니다. 아래 설명은 v0.2 기준입니다.

- 판매자 에이전트는 Agent Card의 `extensions` 배열에 확장 URI `https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2`를 선언합니다. v0.1의 URI는 `https://github.com/google-a2a/a2a-x402/v0.1`이었는데, 조직 이름이 google-a2a에서 google-agentic-commerce로 바뀐 흔적입니다. `required: true`로 두면 이 확장을 모르는 클라이언트는 유료 skill을 호출할 수 없습니다.
- 클라이언트는 요청 시 `X-A2A-Extensions` HTTP 헤더에 같은 URI를 넣어 확장을 활성화하고, 서버는 응답 헤더에 URI를 돌려줘 확인합니다.
- 클라이언트가 유료 작업을 요청하면 판매자는 Task를 만들어 상태를 `input-required`(v0.x 표기, v1.0의 `INPUT_REQUIRED`)로 두고, 메시지 `metadata`에 `x402.payment.status: "payment-required"`를 담아 돌려줍니다. 결제 요구 사항(`x402PaymentRequiredResponse`: 금액, 자산, 네트워크, 수취 주소 등)이 어디에 실리는지는 아래 두 흐름에 따라 다릅니다.
- 클라이언트는 조건을 보고 결제할지 결정합니다. 거절하면 `payment-rejected`, 진행하면 지갑으로 서명한 `PaymentPayload`를 `x402.payment.status: "payment-submitted"`와 함께 같은 `taskId`로 보냅니다.
- 판매자는 facilitator로 서명을 검증하고 온체인에 정산한 뒤 `payment-verified`를 거쳐 `payment-completed`로 바꾸고, 실제 작업을 수행해 Artifact를 돌려줍니다. 정산 결과(`x402SettleResponse`)는 `x402.payment.receipts` 배열에 담기며, 이 키는 최종 Task 메시지에 반드시 들어가야 합니다. 실패하면 `payment-failed`가 되고 `x402.payment.error`에 짧은 오류 코드가 붙습니다. 스펙이 정의한 오류 코드는 `INSUFFICIENT_FUNDS`, `INVALID_SIGNATURE`, `EXPIRED_PAYMENT`, `DUPLICATE_NONCE`, `NETWORK_MISMATCH`, `INVALID_AMOUNT`, `SETTLEMENT_FAILED` 일곱 가지입니다.

즉 A2A의 Task 상태 기계는 그대로 두고, 그 위에 `metadata` 필드로 결제 상태 기계를 한 층 더 얹은 구조입니다. 결제 데이터 구조(`x402PaymentRequiredResponse`, `PaymentRequirements`, `PaymentPayload`, `x402SettleResponse`)는 새로 정의하지 않고 Coinbase의 코어 x402 스펙을 그대로 참조합니다.

v0.2의 핵심 변화는 이 x402 객체들을 A2A 메시지의 어디에 실을지 두 가지 흐름으로 나눠 조합할 수 있게 한 composable 설계입니다.

- **Standalone Flow**(단독 흐름): x402 객체를 A2A 메시지 metadata에 직접 담습니다. `x402PaymentRequiredResponse`는 `task.status.message.metadata`의 `x402.payment.required` 키에, `PaymentPayload`는 `message.metadata`의 `x402.payment.payload` 키에 들어갑니다. 스펙의 JSON 예시에서 네트워크는 `base`입니다. v0.1이 정의했던 metadata 방식이 이 흐름에 해당합니다.
- **Embedded Flow**(내장 흐름): x402가 AP2 같은 상위 프로토콜의 결제 수단(form of payment) 가운데 하나로 동작합니다. `x402PaymentRequiredResponse`는 AP2의 CartMandate(장바구니 위임장) 같은 상위 객체 안에 담겨 `task.artifacts`로 전달되고, `PaymentPayload`는 AP2의 PaymentMandate(결제 위임장) 안에 담겨 `message.parts`로 전달됩니다. 다음 절에서 다루는 AP2가 x402와 실제로 맞물리는 지점이 여기입니다.

클라이언트가 두 흐름을 구분하는 규칙은 단순합니다. `x402.payment.status: "payment-required"`를 받았을 때 metadata에 `x402.payment.required` 키가 있으면 Standalone이고, 없으면 Embedded로 판단해 artifacts에서 상위 객체를 찾습니다.

v0.2는 사람이 자리에 있는지에 따라 세 가지 서명 패턴도 정리했습니다. **Atomic Signing**(human-present)은 지갑이 결제 서명과 주문 서명 두 개를 사용자 승인 한 번으로 처리하는 방식입니다. **Delegated Signing**(human-not-present)은 사용자가 미리 승인한 위임 범위 안에서 에이전트가 자기 키로 서명합니다. **Smart Contract Escrow**(decoupled)는 사용자가 컨트랙트에 자금을 먼저 넣어 두고, 체크아웃 시점에 오프체인 서명을 한 번 하면 판매자가 컨트랙트에서 자금을 인출(release)하는 구조입니다.

거버넌스 위치는 따로 짚어 둘 필요가 있습니다. A2A의 [확장 거버넌스 문서](https://a2a-protocol.org/latest/topics/extension-and-binding-governance/)에 따르면 공식 확장은 a2aproject 조직에 `ext-{name}` 접두어 저장소로 두고 URI도 `https://a2a-protocol.org/extensions/`로 시작해야 하며, 실험 단계는 `experimental-ext-{name}` 접두어를 씁니다. a2a-x402는 google-agentic-commerce 조직에 있고 URI도 github.com 도메인이어서 이 공식 확장 네임스페이스 밖에 있습니다. 공식 문서가 예시로 드는 확장 목록(Secure Passport, Timestamp, Traceability, AGP)에도 x402는 없습니다. Google이 만든 확장은 맞지만 a2aproject의 공식 확장은 아닙니다.

저장소 자체는 아카이브되지 않았고 폐기 공지도 없습니다. 다만 마지막 push가 2026년 8월 4일, main 브랜치의 마지막 실질 커밋이 2026년 5월 24일(Dependabot 설정)로 활동이 적습니다. 파이썬 예제(adk-demo)는 기본값으로 모의 facilitator와 하드코딩된 키를 쓰는 모의 지갑을 사용하며, 실제 온체인 거래를 위해서는 facilitator 설정과 MetaMask·MPC·하드웨어 서명 같은 지갑 구현을 직접 연결해야 합니다. v0.2 스펙 본문에 experimental 표기는 없지만 파트너 초안이 들어 있는 `schemes/` 디렉터리는 여전히 experimental입니다. A2A 위에서 x402 결제를 구현할 때 참조할 스펙은 여전히 이 저장소이고 최신은 v0.2입니다. 반면 A2A 코어의 현재 상태는 a2aproject 조직과 a2a-protocol.org에서 확인해야 합니다.

### AP2와 UCP

에이전트가 결제를 보낼 수 있게 되면 곧바로 다음 질문이 따라옵니다. 사용자가 정말 이 구매를 시켰다는 것을 어떻게 증명하고, 사고가 나면 누가 책임지는가. 이 질문에 답하는 층이 AP2(Agent Payments Protocol)입니다. Google이 [2025년 9월 17일](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol) Adyen, American Express, Coinbase, Mastercard, PayPal, Revolut 등 60개 이상 파트너와 함께 발표했고, [ap2-protocol.org](https://ap2-protocol.org/)는 AP2를 A2A의 개방형 확장으로 정의하고, UCP와는 별도 통합 가이드로 연결합니다. 핵심 장치는 Mandate라는 암호학적으로 서명된 위임장입니다. 사용자의 최초 요청을 담는 Intent Mandate와 사용자가 승인한 정확한 품목·가격을 담는 Cart Mandate가 있고(현재 v0.2 문서는 이를 Checkout Mandate와 Payment Mandate로 정리합니다), 각각 검증 가능한 디지털 자격증명(VDC) 형태로 판매자·결제사에 전달되어 사후에 부인할 수 없는 증거가 됩니다. 발표 글은 AP2가 풀려는 문제를 권한(authorization), 진위(authenticity), 책임(accountability) 세 가지로 요약합니다.

AP2의 기본 결제 레일은 카드입니다. v0.2는 신용·직불카드를 지원하고 실시간 계좌 이체(UPI, PIX)와 디지털 통화는 로드맵에 있습니다. 블록체인은 여기서도 확장으로 들어옵니다. Google은 AP2 발표와 함께 Coinbase, Ethereum Foundation, MetaMask 등과 만든 x402용 AP2 확장을 공개했고, AP2 저장소의 샘플 디렉터리에는 사람이 자리에 있는 경우와 없는 경우(human-present/human-not-present)의 x402 시나리오가 각각 들어 있습니다. 표준화는 FIDO Alliance의 Agentic Authentication and Payments 워킹그룹이 맡고 있습니다.

UCP(Universal Commerce Protocol)는 그 위에서 쇼핑 대화 자체를 다루는 층입니다. Google이 [2026년 1월 11일](https://developers.googleblog.com/under-the-hood-universal-commerce-protocol-ucp/) Shopify, Etsy, Walmart, Target, Stripe, Visa, Mastercard 등 20개 이상 파트너와 공개했고, 결제(checkout), 할인 적용, 주문 관리, 배송, 계정 연결 같은 상거래 기능을 표준 어휘로 정의합니다. 전송 방식은 REST, A2A, MCP 세 가지를 모두 지원하고 결제는 AP2와 호환됩니다. UCP의 최근 진행 상황은 [2026년 6월 결제 동향 글](/blog/agentic-payments-june-2026-x402-ucp-mpp/)에 정리했습니다.

정리하면 층이 이렇게 쌓입니다. A2A가 "에이전트끼리 Task를 주고받는 방법"을 정하고, UCP가 그 위에서 "쇼핑 대화의 어휘"를, AP2가 "사용자 위임과 책임의 증명"을, x402가 "온체인 정산"을 맡습니다. 넷 가운데 블록체인을 직접 만지는 것은 x402 하나입니다. Google 오픈소스 블로그의 [A2A 1주년 글](https://opensource.googleblog.com/2026/04/a-year-of-open-collaboration-celebrating-the-anniversary-of-a2a.html)은 AP2·UCP와 사용자 인터페이스용 A2UI를 묶어 A2A의 확장 모델로 만들어진 "A2Family"라고 부릅니다.

### 논문: 온체인 Agent Card와 x402 통합 제안

학계에서는 A2A의 빈칸을 블록체인으로 채우려는 제안이 나왔습니다. TU Berlin과 T-Labs의 Awid Vaziry, Sandro Rodriguez Garzon, Axel Küpper가 2025년 7월 24일 공개한 [arXiv 2507.19550](https://arxiv.org/abs/2507.19550) "Towards Multi-Agent Economies: Enhancing the A2A Protocol with Ledger-Anchored Identities and x402 Micropayments for AI Agents"입니다. IJCCI 2025 학회에서 발표되어 Springer CCIS 2827권에 실렸습니다.

논문은 A2A의 두 한계를 짚습니다. 첫째, 발견이 중앙화되어 있다는 점입니다. well-known URI는 도메인을 이미 알아야 하고, 레지스트리는 운영자를 신뢰해야 합니다. 둘째, 에이전트 간 마이크로페이먼트가 없다는 점입니다. 저자들은 Agent Card를 스마트 컨트랙트로 온체인에 게시해서 변조 불가능하고 검증 가능한 에이전트 신원 겸 발견 수단으로 쓰고, x402를 A2A에 통합해 체인 중립적인 HTTP 기반 마이크로페이먼트를 붙이는 아키텍처를 제안하고 구현·평가했습니다.

한 가지는 구분해서 읽어야 합니다. 이 제안은 논문이고 공식 스펙이 아닙니다. A2A 공식 문서가 인정하는 발견 방식은 여전히 well-known URI, 레지스트리, 직접 설정 세 가지이며, v1.0의 Signed Agent Card는 도메인 소유자의 서명으로 위조를 막지만 카드를 체인에 올리지는 않습니다. 다만 "에이전트 신원을 온체인 레지스트리에 고정한다"는 발상 자체는 이더리움 쪽 [ERC-8004](/blog/erc8004-agent-reputation-registry-lookup/)가 별도로 구현해 2026년 1월 메인넷에 배포했고, 그 등록 파일에는 A2A 엔드포인트와 `x402Support` 필드가 들어갑니다. 서로 다른 커뮤니티가 같은 빈칸을 각자의 방식으로 메우고 있는 셈이고, 이 구도는 [KYA 글](/blog/know-your-agent-kya-ai-agent-identity-onchain/)에서 자세히 다뤘습니다.

## 2026년 동향

Linux Foundation은 [2026년 4월 9일 보도자료](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)로 A2A 1주년을 정리했습니다. 확인된 수치와 상태는 다음과 같습니다.

- **지원 조직 150개 이상.** 2025년 4월 발표 때 50개에서 늘었습니다. 기술 운영 위원회(TSC)에는 AWS, Cisco, Google, IBM Research, Microsoft, Salesforce, SAP, ServiceNow 8개사가 참여합니다.
- **v1.0 스펙.** 2026년 3월에 나온 첫 안정 버전으로, 세 전송 바인딩(JSON-RPC·gRPC·HTTP+JSON)의 동등성 보장, Signed Agent Card, 단일 엔드포인트 멀티테넌시, OAuth 2.0 흐름 현대화가 들어갔습니다. Agent Card는 하위 호환을 유지해서 한 에이전트가 v0.3과 v1.0을 동시에 광고할 수 있습니다. 2026년 5월 28일에 v1.0.1이 나왔습니다.
- **클라우드 플랫폼 통합.** Microsoft는 Azure AI Foundry와 Copilot Studio에, AWS는 Amazon Bedrock AgentCore Runtime에 A2A를 넣었고, Google Cloud는 2025년 8월 v0.3 업그레이드와 함께 Vertex AI Agent Engine과 Agentspace 지원을 [발표](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade)했습니다. 3대 클라우드가 모두 관리형 런타임에서 A2A 에이전트를 호스팅합니다.
- **SDK.** 보도자료는 Python, JavaScript, Java, Go, .NET 5개 언어를 프로덕션 준비 상태로 꼽았습니다. 2026년 8월 27일 기준 [저장소 README](https://github.com/a2aproject/A2A)와 로드맵은 Rust를 더해 6개를 나열합니다.
- **GitHub 스타.** 보도자료 시점 2만 2천 개 이상, 2026년 8월 28일 조회 시점 25,522개(포크 2,590개, 마지막 push 2026년 8월 25일).
- **프로덕션 사용.** 공급망, 금융 서비스, 보험, IT 운영 분야에서 실제 배포가 있다고 밝혔습니다. 이름이 공개된 사례로는 Google Cloud가 2025년 8월에 언급한 Tyson Foods(영업·공급망 최적화)와 Gordon Food Service(제품 데이터·리드 공유 채널)가 있습니다.

[로드맵 문서](https://a2a-protocol.org/latest/roadmap/)(2026년 3월 10일 갱신)는 확장 SDK 지원 확대, 구현 검증용 A2A Inspector와 호환성 테스트 키트(TCK), 커뮤니티 모범 사례 문서화를 다음 과제로 적었습니다. 2026년 8월 AAIF 합류는 이 흐름의 연장입니다.

## 커뮤니티 반응과 비판

발표 당일 [Hacker News 스레드](https://news.ycombinator.com/item?id=43631381)는 450포인트, 댓글 277개를 모았고 분위기는 회의론이 우세했습니다. 가장 많은 답글이 붙은 댓글(zellyn)은 "이 프로토콜들이 실제로 어떻게 생겼는지 보기가 답답할 정도로 어렵다. LLM 출력과 실제로 오가는 JSON이 들어간 간단한 예시 대화 하나가 전부인데"라며 발표 글 끝의 파트너 나열이 오히려 인상을 나쁘게 했다고 썼습니다. simonw는 "LLM이 도구와 API를 호출하는 가치는 완전히 이해하지만 LLM이 다른 LLM을 호출하는 데서 큰 가치를 아직 못 봤다"며 에이전트 간 통신 자체의 필요성을 물었고, hliyan은 "SOA와 WSDL을 LLM 버전으로 다시 발명하는 것 아닌가"라고 적었습니다. phillipcarter는 "MCP는 사람들이 오늘 실제로 겪는 문제를 풀고, A2A는 Google이 파트너들과 쫓는 마케팅 문제를 푼다"고 잘라 말했습니다. 긍정 쪽 의견도 있었습니다. 스펙과 SDK를 읽은 vessenes는 대역 내·외 데이터 전달 방식과 토큰 기반 보안이 MCP의 여러 아픈 지점을 비교적 가볍게 개선했다고 평했습니다.

이 회의론은 이후 실제 사건으로 이어졌습니다. 2025년 7월 25일 OpenAI Agents SDK 저장소에 한 기여자가 A2A 지원을 추가하는 [1,291줄 PR](https://github.com/openai/openai-agents-python/pull/1245)을 올렸는데, 관리자는 "이 SDK에 A2A 지원을 추가할 당면 계획이 없다"고 답했고 PR은 8월 13일 stale 처리로 닫혔습니다. 후속 논의에서 관리자는 어댑터를 코어 SDK에 넣지 않고 별도 패키지로 공개해 달라고 요청했습니다. 이 일은 10월 말 HN에서 다시 회자되었습니다. 요점은 OpenAI가 A2A를 거부했다기보다, 2025년 내내 주요 프레임워크 가운데 A2A를 코어에 넣는 쪽이 소수였다는 사실입니다.

[Fatih Kadir Akın은 2025년 9월 글](https://blog.fka.dev/blog/2025-09-11-what-happened-to-googles-a2a/)에서 이를 "채택이 아키텍처를 이긴다(adoption beats architecture)"로 정리했습니다. A2A는 기술적으로 더 우수한 프로토콜이었을지 모르지만 MCP는 개발자가 실제로 쓰고 싶은 것을 만들었다는 진단입니다. 그는 간단한 도구 연동을 원하는 개인 개발자가 에이전트 발견, 역량 협상, 보안 카드 같은 개념을 먼저 소화해야 했던 점, 소비자용 AI 앱에 바로 붙은 MCP와 달리 A2A가 기업 오케스트레이션부터 접근한 점을 원인으로 꼽았습니다.

2026년 시점의 평가는 조금 더 균형이 잡혔습니다. Rost Glukhov의 [2026년 채택 분석](https://www.glukhov.org/ai-systems/comparisons/a2a-protocol-2026-adoption/)은 "A2A는 죽지 않았다. 다만 보편적이지 않다"고 요약합니다. 이 글은 채택을 네 단계로 나눕니다. 로고만 올리는 단계, SDK로 실제로 만들 수 있는 단계, 클라우드·프레임워크가 기본 지원하는 단계, 그리고 프로덕션에서 계속 쓰이는 단계입니다. 150개 조직이라는 수치는 첫 단계와 두 번째 단계를 말해 주지만 마지막 단계와는 별개이고, "지원은 사용이 아니다(support is not usage)"라는 것이 핵심 지적입니다. 저자의 결론은 실무 권고 형태입니다. **MCP로 시작해서 에이전트 경계를 처음부터 깨끗하게 설계하고, 그 경계가 배포·소유권·상호운용성의 실제 제약이 되는 순간에만 A2A를 얹으라**는 것입니다. 구체적으로는 에이전트가 독립적으로 배포되고, 다른 팀이 소유하며, 다른 프레임워크로 만들어졌고, 자기 도구와 권한을 따로 갖고, 장기 실행 작업을 책임질 때 A2A가 정당화됩니다. 같은 팀 안에서 함수 몇 개를 에이전트라고 부르는 수준이면 MCP 도구로 감싸는 것이 낫습니다. 이 권고는 A2A 공식 문서의 MCP 병용 설명과도 사실상 같은 방향입니다.

비판은 크게 세 갈래로 나뉩니다. "MCP로 충분한데 왜 하나 더 배워야 하나"(겹침), "파트너 로고는 많은데 코드 기여와 프로덕션 사례는 어디 있나"(지원 대 사용), "에이전트끼리 대화하는 것이 정말 필요한가"(전제 자체에 대한 의심). 첫째는 v1.0과 클라우드 통합으로 학습 비용이 낮아지며 일부 완화됐고, 둘째는 Tyson Foods 같은 이름 있는 사례와 IBM ACP 통합으로 조금씩 채워지고 있으며, 셋째는 여전히 열린 질문입니다.

## 함께 보면 좋을 자료

- [A2A Protocol Specification](https://a2a-protocol.org/latest/specification/): v1.0 스펙 원문. 데이터 객체와 RPC 메서드 정의를 직접 확인할 때.
- [A2A와 MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/): 공식 문서의 역할 분담 설명과 자동차 수리점 예시.
- [a2a-samples](https://github.com/a2aproject/a2a-samples): ADK, LangGraph, CrewAI 등 여러 프레임워크로 만든 A2A 에이전트 예제 모음.
- [A2A x402 Extension 스펙 v0.2](https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md): 결제 상태 흐름, Standalone·Embedded 두 흐름, 서명 패턴 정의.
- [에이전트 결제 2026년 6월 동향](/blog/agentic-payments-june-2026-x402-ucp-mpp/): x402·UCP·MPP 구현 진전, 이 글의 결제 층을 더 깊이 볼 때.
- [KYA(Know Your Agent)](/blog/know-your-agent-kya-ai-agent-identity-onchain/): 에이전트 신원을 어디에 고정할지에 대한 표준 경쟁.

## 정리

A2A는 서로 다른 조직과 프레임워크의 에이전트가 Agent Card로 서로를 알아보고, Task 단위로 일을 맡기고, 스트리밍이나 푸시로 진행 상황을 받고, Artifact로 결과를 돌려받는 HTTP 프로토콜입니다. MCP가 에이전트에 도구를 붙이는 세로 방향 표준이라면 A2A는 에이전트를 옆의 에이전트에 연결하는 가로 방향 표준이고, 2026년 8월 현재 둘은 같은 재단(AAIF) 아래에 있습니다.

블록체인은 이 코어에 없습니다. 체인은 a2a-x402 확장의 정산 단계에서, 그리고 AP2의 x402 확장에서만 등장하고, 그마저도 태그된 릴리스가 v0.1.0 하나뿐인 초안 스펙(최신 v0.2)과 모의 facilitator 예제 단계입니다. 온체인 Agent Card 같은 제안은 논문과 ERC-8004 커뮤니티에서 각자 진행 중이지 A2A 스펙의 일부가 아닙니다. 이 구분을 놓치면 "A2A = 블록체인 에이전트 프로토콜"이라는 잘못된 인상을 갖기 쉽습니다.

채택은 확실히 진행됐지만 보편적이지는 않습니다. 150개 조직, v1.0, 3대 클라우드 통합은 사실이고, 그 수치가 곧 깊은 프로덕션 사용을 뜻하지 않는다는 지적도 사실입니다. 개인적인 판단으로는 지금 무언가를 만든다면 커뮤니티 권고대로 MCP로 시작하는 것이 맞고, 에이전트가 조직 경계를 넘어 다른 팀의 에이전트와 장기 작업을 주고받는 독립 시스템이 되는 시점에 A2A를 얹는 것이 순서입니다. 결제 층(x402, AP2)은 그 다음 단계이고, 지금은 스펙과 샘플을 읽어 두는 정도가 적절합니다.

## 참고 자료

- [A2A Protocol Specification](https://a2a-protocol.org/latest/specification/) — a2a-protocol.org, 조회일 2026-08-27
- [What's New in A2A v1.0](https://a2a-protocol.org/latest/whats-new-v1/) — a2a-protocol.org, 조회일 2026-08-27
- [Announcing Version 1.0](https://a2a-protocol.org/latest/announcing-1.0/) — a2a-protocol.org, 조회일 2026-08-27
- [A2A and MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/) — a2a-protocol.org, 조회일 2026-08-27
- [Agent Discovery in A2A](https://a2a-protocol.org/latest/topics/agent-discovery/) — a2a-protocol.org, 조회일 2026-08-27
- [A2A Roadmap](https://a2a-protocol.org/latest/roadmap/) — a2a-protocol.org (2026-03-10 갱신), 조회일 2026-08-27
- [a2aproject/A2A](https://github.com/a2aproject/A2A) — GitHub (스타 25,522, v1.0.0 2026-03-12, v1.0.1 2026-05-28), 조회일 2026-08-28
- [Announcing the Agent2Agent Protocol (A2A)](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) — Google for Developers, 2025-04-09, 조회일 2026-08-27
- [Google Cloud donates A2A to Linux Foundation](https://developers.googleblog.com/en/google-cloud-donates-a2a-to-linux-foundation/) — Google for Developers, 2025-06-23, 조회일 2026-08-27
- [Agent2Agent protocol (A2A) is getting an upgrade](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade) — Google Cloud Blog, 2025-08-01, 조회일 2026-08-27
- [ACP Joins Forces with A2A Under the Linux Foundation's LF AI & Data](https://lfaidata.foundation/communityblog/2025/08/29/acp-joins-forces-with-a2a-under-the-linux-foundations-lf-ai-data/) — LF AI & Data, 2025-08-29, 조회일 2026-08-27
- [A2A Protocol Surpasses 150 Organizations...](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year) — Linux Foundation, 2026-04-09, 조회일 2026-08-27
- [A year of open collaboration: Celebrating the anniversary of A2A](https://opensource.googleblog.com/2026/04/a-year-of-open-collaboration-celebrating-the-anniversary-of-a2a.html) — Google Open Source Blog, 2026-04-16, 조회일 2026-08-27
- [A2A joins AAIF's open agentic stack](https://aaif.io/blog/a2a-joins-aaif) — Agentic AI Foundation, 2026-08-17, 조회일 2026-08-27
- [google-agentic-commerce/a2a-x402](https://github.com/google-agentic-commerce/a2a-x402) — GitHub (스타 554, 마지막 push 2026-08-04, v0.2 스펙 2025-11-04 추가, 태그는 v0.1.0만 있고 v0.2.0 태그 없음), 조회일 2026-08-28
- [A2A Protocol: x402 Payments Extension v0.2](https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md) — GitHub, 조회일 2026-08-28
- [Extension and Binding Governance](https://a2a-protocol.org/latest/topics/extension-and-binding-governance/) — a2a-protocol.org, 조회일 2026-08-28
- [x402.org](https://www.x402.org/) — x402 Foundation, 조회일 2026-08-27
- [Towards Multi-Agent Economies: Enhancing the A2A Protocol with Ledger-Anchored Identities and x402 Micropayments for AI Agents](https://arxiv.org/abs/2507.19550) — Vaziry, Rodriguez Garzon, Küpper (TU Berlin / T-Labs), arXiv 2025-07-24, IJCCI 2025 / Springer CCIS vol. 2827, 조회일 2026-08-27
- [Agent Payments Protocol (AP2)](https://ap2-protocol.org/) — ap2-protocol.org (v0.2), 조회일 2026-08-27
- [Powering AI commerce with the new Agent Payments Protocol (AP2)](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol) — Google Cloud Blog, 2025-09-17, 조회일 2026-08-27
- [google-agentic-commerce/AP2](https://github.com/google-agentic-commerce/AP2) — GitHub (x402 샘플 시나리오), 조회일 2026-08-27
- [Under the hood: Universal Commerce Protocol (UCP)](https://developers.googleblog.com/under-the-hood-universal-commerce-protocol-ucp/) — Google for Developers, 2026-01-11, 조회일 2026-08-27
- [The Agent2Agent Protocol (A2A) | Hacker News](https://news.ycombinator.com/item?id=43631381) — 2025-04-09, 450포인트 / 댓글 277개, 조회일 2026-08-27
- [Feature: Add Agent-to-Agent (A2A) Protocol Support with AgentCardBuilder #1245](https://github.com/openai/openai-agents-python/pull/1245) — openai/openai-agents-python, 2025-07-25 생성 / 2025-08-13 닫힘, 조회일 2026-08-27
- [What Happened to Google's A2A?](https://blog.fka.dev/blog/2025-09-11-what-happened-to-googles-a2a/) — Fatih Kadir Akın, 2025-09-11, 조회일 2026-08-27
- [Google A2A Protocol in 2026: Adoption, Hype, and Reality](https://www.glukhov.org/ai-systems/comparisons/a2a-protocol-2026-adoption/) — Rost Glukhov, 조회일 2026-08-27
