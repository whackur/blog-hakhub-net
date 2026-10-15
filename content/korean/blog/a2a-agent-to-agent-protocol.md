---
title: "A2A(Agent-to-Agent) 프로토콜: 에이전트 간 협업 표준과 결제 레이어의 접점"
meta_title: ""
description: "A2A의 Agent Card 발견, 작업 위임과 상태 관리, 스트리밍·인증을 1.0 명세로 설명합니다. MCP의 도구 연결, AP2의 구매 승인, UCP의 상거래, x402의 결제 정산을 구분하고 실제 적용 조건을 짚습니다."
date: 2026-08-27T10:00:00+09:00
lastmod: 2026-10-15T15:41:34Z
image: "/images/posts/a2a-agent-to-agent-protocol/a2a-editorial-20261016.webp"
categories: ["Blockchain"]
tags: ["a2a", "ai-agent", "agentic-payments", "x402", "mcp"]
author: "whackur"
translationKey: "a2a-agent-to-agent-protocol"
draft: false
---

**A2A(Agent2Agent)는 따로 운영되는 에이전트에 일을 맡기고, 진행 상태와 결과를 받는 방법을 표준화합니다.** 요청자는 Agent Card로 상대의 기능·접속 주소·인증 조건을 확인하고, 오래 걸리는 일은 Task로 추적합니다. MCP는 각 에이전트가 도구와 데이터를 사용하는 연결을 담당하며, 구매 승인이나 결제 정산은 AP2·x402 같은 별도 규약이 맡습니다. A2A로 협업하는 데 블록체인이나 지갑은 필요하지 않습니다. [A2A 명세](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md), [MCP와의 역할 분담](https://a2a-protocol.org/latest/topics/a2a-and-mcp/)

## 구매 요청 하나로 보는 협업 단위

구매 담당 에이전트가 외부 공급업체 에이전트에 “이 부품 100개의 납기와 견적을 알려 달라”고 요청한다고 가정하겠습니다. 공급업체는 재고를 조회하고 운송 조건을 계산해야 합니다. 품번이 모호하면 추가 질문을 보내고, 견적이 완성되면 문서나 구조화된 데이터를 반환합니다. 이때 요청자는 공급업체의 내부 프롬프트·모델·도구를 공유받을 필요가 없습니다.

A2A는 이 교환을 다음 객체로 표현합니다. 수량과 상황은 설명을 위한 예시이며 실제 거래 사례가 아닙니다. 객체의 정의는 [명세의 핵심 개념과 데이터 모델](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#22-core-concepts)에 따릅니다.

| 객체 | 구매 예시에서의 역할 | 구분할 점 |
| --- | --- | --- |
| Agent Card | 공급업체가 공개한 견적 기능, 주소, 지원 형식, 인증 조건 | 기능 설명이며 품질 인증서가 아닙니다. |
| Message | 견적 요청, 품번 확인 질문, 추가 답변 | 대화의 한 차례를 나타냅니다. |
| Task | 견적 산출이라는 작업과 현재 상태 | 서버가 발급한 ID로 추적합니다. |
| Artifact | 완성한 견적서나 가격·납기 데이터 | 작업 결과이며 진행 안내 메시지와 구별합니다. |
| Part | 메시지나 결과 안의 텍스트, 파일, 구조화된 값 | 하나의 메시지에 여러 형식이 들어갈 수 있습니다. |

클라이언트는 요청을 시작하는 애플리케이션 또는 에이전트이고, 서버는 A2A 엔드포인트를 제공하는 상대 에이전트입니다. 같은 서비스도 다른 에이전트를 호출할 때는 클라이언트가 됩니다. A2A가 정하는 것은 이 경계에서의 교환이며, 내부 추론 방식이나 에이전트를 몇 개로 나눌지는 구현자가 정합니다.

### 명세 버전과 SDK 버전

2026년 10월 15일 UTC에 확인한 최신 공식 명세 릴리스는 [v1.0.1](https://github.com/a2aproject/A2A/releases/tag/v1.0.1), 공식 Python SDK 릴리스는 [v1.2.2](https://github.com/a2aproject/a2a-python/releases/tag/v1.2.2)입니다. 두 버전 번호는 다른 대상을 가리킵니다. Python SDK v1.2.2는 [README의 호환성 표](https://github.com/a2aproject/a2a-python/blob/v1.2.2/README.md)에 A2A 1.0 구현과 0.3 호환 모드를 명시하며, JSON-RPC·HTTP+JSON/REST·gRPC를 지원합니다.

프로토콜 협상에서는 패치 번호를 제외한 `1.0`을 씁니다. Agent Card 자체의 `version`은 에이전트 소프트웨어 버전이고, 각 인터페이스의 `protocolVersion`이 A2A 버전입니다. 이 둘을 혼동하면 SDK를 갱신하고도 잘못된 요청을 보낼 수 있습니다. [버전 규칙](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#36-versioning)

## Agent Card를 찾고 접속 조건을 고릅니다

클라이언트가 상대 도메인을 알고 있다면 `https://{domain}/.well-known/agent-card.json`에서 카드를 찾습니다. 조직이 관리하는 카탈로그나 미리 설정한 카드 주소를 사용해도 됩니다. A2A가 전 세계 에이전트를 자동 검색하는 단일 디렉터리를 정해 주지는 않습니다. 어떤 카탈로그와 제공자를 신뢰할지는 운영 환경의 선택입니다. [발견 방식](https://a2a-protocol.org/latest/topics/agent-discovery/)

카드에서 기능을 뜻하는 `skills`, 입출력 미디어 형식, `capabilities`, 보안 요구사항을 읽습니다. `supportedInterfaces`는 접속 URL·`protocolBinding`·`protocolVersion`을 우선순위대로 나열합니다. 클라이언트는 자신이 지원하는 인터페이스를 골라 그 URL을 사용합니다. 인터페이스에 `tenant`가 있으면 요청에도 같은 값을 넣어야 합니다. 여러 에이전트를 같은 엔드포인트에서 제공할 때 필요한 라우팅 정보입니다. [Agent Card와 인터페이스 정의](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

접속 가능한 것과 요청을 수행할 권한이 있는 것은 별개입니다. 공개 카드에 견적 기능이 적혀 있어도 특정 고객에게만 가격을 공개할 수 있습니다. 인증 뒤 더 자세한 카드를 제공하는 기능도 선택 사항이며 `capabilities.extendedAgentCard`로 확인합니다. 공개 카드가 보여 주는 기능 목록을 모든 사용자의 접근 권한으로 해석하면 안 됩니다. [확장 카드와 접근 제어](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#3111-get-extended-agent-card)

## 메시지에서 작업 완료까지

1.0 JSON-RPC 바인딩의 요청은 다음처럼 구성할 수 있습니다. 접속 경로는 카드가 알려 준 URL을 사용하고, 인증 헤더는 해당 서비스의 요구사항에 맞춰 별도로 설정합니다. 이 예시는 메시지 구조를 보여 주며 실행한 거래 기록은 아닙니다. 메서드는 `SendMessage`, 송신 역할은 `ROLE_USER`입니다. [메서드 매핑](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#53-method-mapping-reference), [메시지 스키마](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

```http
POST /rpc HTTP/1.1
Host: supplier.example.com
Content-Type: application/json
A2A-Version: 1.0

{
  "jsonrpc": "2.0",
  "id": "rpc-1",
  "method": "SendMessage",
  "params": {
    "message": {
      "messageId": "msg-1",
      "role": "ROLE_USER",
      "parts": [{"text": "Quote 100 units of part AX-10 with delivery dates."}]
    },
    "configuration": {"returnImmediately": true}
  }
}
```

`returnImmediately: true`는 작업이 끝나기 전에 응답하도록 요청합니다. 기본값인 `false`는 완료·실패 등의 종료 상태나 추가 입력·권한을 기다리는 중단 상태까지 기다립니다. 서버는 추적할 작업이 필요하면 Task를 만들지만, 단순한 응답은 Task 없이 Message로 돌려줘도 됩니다. 모든 대화가 장기 작업이 되는 것은 아닙니다. [전송 설정](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#322-sendmessageconfiguration)

서버가 견적 Task를 만들었다면 클라이언트는 작업 ID를 보관합니다. `rpc-1`은 JSON-RPC 요청과 응답을 짝짓는 값이고, `messageId`는 메시지 식별자입니다. 서버가 발급하는 Task ID와 역할이 다릅니다. `contextId`는 관련 작업과 메시지를 묶지만 서로 다른 에이전트의 내부 메모리를 공유하지는 않습니다.

작업은 다음 상태를 사용합니다. 정확한 열거형 이름은 [v1.0.1 프로토콜 정의](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)에 있습니다.

| 상태 | 의미와 클라이언트의 다음 행동 |
| --- | --- |
| `TASK_STATE_SUBMITTED`, `TASK_STATE_WORKING` | 요청을 접수했거나 처리 중입니다. 상태·결과 업데이트를 기다립니다. |
| `TASK_STATE_INPUT_REQUIRED` | 품번 같은 추가 정보가 필요합니다. 같은 `taskId`를 지정한 메시지로 답합니다. |
| `TASK_STATE_AUTH_REQUIRED` | API 접근이나 사람의 승인 등 추가 권한이 필요합니다. 합의한 절차로 권한을 제공합니다. |
| `TASK_STATE_COMPLETED` | 성공적으로 끝났습니다. Artifact에서 결과를 읽습니다. |
| `TASK_STATE_FAILED`, `TASK_STATE_CANCELED`, `TASK_STATE_REJECTED` | 오류·취소·수행 거절로 끝났습니다. 성공한 결과로 취급하지 않습니다. |

추가 입력과 권한 요청은 작업을 계속할 수 있는 중단 상태입니다. 완료·실패·취소·거절은 종료 상태이므로 그 Task에 메시지를 더 보내 재개하지 않습니다. 완료된 견적을 바탕으로 새 주문을 요청한다면 새 작업으로 처리하고 필요한 문맥을 연결해야 합니다. [작업 식별자와 다중 대화](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#34-multi-turn-interactions)

`CancelTask`는 취소 요청이며 성공을 보장하지 않습니다. 이미 끝났거나 취소할 수 없는 단계일 수 있습니다. 재시도도 주의가 필요합니다. 명세는 `SendMessage`의 중복 제거를 의무화하지 않고 `messageId`를 활용할 수 있다고 규정합니다. 따라서 네트워크 시간 초과 뒤 같은 요청을 보냈다는 이유만으로 주문·결제 같은 부수 효과가 한 번만 실행된다고 가정해서는 안 됩니다. 실제 서비스에서 중복 방지와 재시도 정책을 따로 정해야 합니다. [취소](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#315-cancel-task), [멱등성](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#331-idempotency)

## 진행 상황을 받는 세 가지 방식

상태를 추적하는 방식은 처리 시간과 네트워크 조건에 따라 고릅니다. 스트리밍과 push는 카드가 해당 기능을 선언했을 때 사용합니다. [업데이트 전달 규칙](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#35-task-update-delivery-mechanisms)

- **Polling**: `GetTask`로 현재 상태와 결과를 조회합니다. 지속 연결 없이 구현하지만 조회 간격만큼 늦고 불필요한 요청이 생깁니다.
- **Streaming**: `SendStreamingMessage` 또는 기존 작업의 `SubscribeToTask`로 이벤트를 받습니다. `capabilities.streaming`이 필요합니다. JSON-RPC·HTTP+JSON은 SSE, gRPC는 자체 스트림을 사용합니다.
- **Push**: 서버가 등록한 webhook에 HTTP POST를 보냅니다. `capabilities.pushNotifications`와 외부에서 도달 가능한 수신 주소가 필요합니다.

작업 스트림은 처음에 Task를 보내고 이후 `TaskStatusUpdateEvent`와 `TaskArtifactUpdateEvent`로 상태와 결과 조각을 보냅니다. 화면에 토큰이 늘어나는 기능만을 뜻하지 않습니다. 스트림 연결과 작업의 생명주기는 별개이므로 연결이 끊겼다는 사실만으로 작업이 취소됐다고 판단하지 않습니다. 클라이언트는 저장한 ID로 상태를 조회하거나 진행 중인 작업을 다시 구독할 수 있습니다.

Push도 정확히 한 번 전달되는 영구 메시지 큐를 보장하지 않습니다. 서버는 전달을 적어도 한 번 시도해야 하지만 재시도와 중단 정책에는 구현 선택이 남습니다. 수신자는 예상한 Task ID와 발신자를 검증하고, 중복 알림을 처리할 수 있어야 합니다. 서버가 임의의 내부 주소로 요청하지 않도록 webhook URL 검증도 필요합니다. [Push 페이로드·전달 조건](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#433-push-notification-payload), [보안 조건](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#132-push-notification-security)

## 인증은 접속과 작업 권한을 나눠 처리합니다

프로덕션에서는 HTTP 바인딩에 HTTPS, gRPC에 TLS를 사용해야 합니다. 클라이언트는 카드의 `securitySchemes`와 보안 요구사항을 확인하고 OAuth 등의 외부 절차로 자격 증명을 얻어 요청 헤더나 해당 바인딩의 메타데이터에 넣습니다. 서버는 요청을 인증한 뒤 자신의 정책으로 기능·데이터·작업 접근을 허가합니다. Task ID를 알고 있다는 이유만으로 다른 고객의 작업을 읽을 수 있어서는 안 됩니다. [인증·인가](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#7-authentication-and-authorization), [데이터 접근 범위](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#131-data-access-and-authorization-scoping)

이미 로그인했어도 작업 중 새로운 권한이 필요할 수 있습니다. 예를 들어 견적을 조회할 권한이 주문을 확정할 권한까지 포함하지는 않습니다. 이때 서버는 `TASK_STATE_AUTH_REQUIRED`로 멈추고 필요한 승인을 설명합니다. 기본적으로 자격 증명은 별도 보안 경로로 전달하며, 대화 메시지 안에서 전달하려면 확장이나 사전 합의가 필요합니다. 여러 에이전트를 거치는 대화에 토큰을 그대로 실으면 경유 에이전트에도 노출될 수 있습니다. [작업 중 권한 요청](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#76-in-task-authorization)

Agent Card의 서명은 또 다른 검증입니다. 선택적으로 JCS로 정규화한 카드에 JWS 서명을 붙여 변경 여부와 서명자를 확인합니다. 검증자는 공개키의 신뢰 관계도 판단해야 합니다. 유효한 서명이 에이전트의 답변 품질·가격 적정성·사용자의 구매 동의를 증명하지는 않습니다. 이 서명에 블록체인 등록은 필요하지 않습니다. [카드 서명](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#84-agent-card-signing)

## MCP·상거래·결제는 각자 다른 계약입니다

공급업체 에이전트가 재고 데이터베이스를 조회할 때는 MCP(Model Context Protocol)를 사용할 수 있습니다. 구매 담당 에이전트와 견적 작업을 주고받는 연결에는 A2A를 쓸 수 있습니다. 공식 문서도 두 프로토콜을 함께 쓰는 구조를 설명합니다. 단순한 기능을 도구로 노출하는 선택도 가능하므로 “에이전트가 있으면 무조건 A2A”라는 구분은 맞지 않습니다. [A2A와 MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/)

거래가 이어지면 작업 교환 이외의 계약이 필요해집니다.

| 규약 | 주로 정하는 내용 | A2A와의 관계 |
| --- | --- | --- |
| UCP(Universal Commerce Protocol) | 상품·장바구니·체크아웃·주문 관리 같은 상거래 교환 | A2A·MCP 등과 연동할 수 있는 상거래 규약입니다. |
| AP2(Agent Payments Protocol) | 사용자가 허용한 구매 내용과 결제 권한의 서명된 증거 | A2A와 UCP에 적용하는 별도 승인 규약입니다. |
| a2a-x402 확장 | 결제 요구·서명된 결제 정보·온체인 정산 결과 교환 | 유료 A2A 서비스를 위한 별도 확장 문서입니다. |

이 조합이 반드시 모두 필요한 것은 아닙니다. 무료 견적에는 결제가 없고, 카드 결제를 사용하는 AP2 거래가 온체인 정산을 요구하지도 않습니다. [UCP 공식 설명](https://ucp.dev/), [AP2 공식 설명](https://ap2-protocol.org/), [a2a-x402 v0.2 문서](https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md)

### x402는 작업에 결제 요구와 영수증을 연결합니다

별도 저장소의 **a2a-x402 v0.2 문서**는 판매자 에이전트가 작업을 멈추고 결제 조건을 보내는 흐름을 정의합니다. 클라이언트는 조건을 선택하고 지갑이나 서명 서비스로 `PaymentPayload`를 서명해 같은 작업에 돌려줍니다. 판매자는 결제 서명을 검증하고 온체인 정산을 수행한 뒤 영수증과 작업 결과를 전달합니다. 서명을 제출한 단계와 정산이 끝난 단계는 다릅니다. [결제 흐름](https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md)

Standalone 방식에서는 요구 조건을 `task.status.message.metadata`의 `x402.payment.required`에, 제출 정보를 `message.metadata`의 `x402.payment.payload`에 넣습니다. Embedded 방식에서는 상위 상거래 규약의 객체 안에 결제 정보를 넣습니다. `x402.payment.status`의 `payment-required`·`payment-submitted`·`payment-completed`는 확장이 정의한 값이며 A2A 핵심 Task 상태가 아닙니다.

이 문서의 예시는 `input-required`와 `X-A2A-Extensions`를 사용합니다. A2A 1.0의 열거형 `TASK_STATE_INPUT_REQUIRED`, 서비스 매개변수 `A2A-Extensions`와 표기가 다릅니다. 따라서 예시를 1.0 서버에 그대로 붙여 호환된다고 가정하지 말고, 선택한 확장 구현과 SDK의 상태·헤더·페이로드 변환을 검증해야 합니다. 확장 문서의 존재는 특정 서비스가 실제 자금으로 이를 운영한다는 증거도 아닙니다. [확장 문서](https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md), [1.0 서비스 매개변수](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#326-service-parameters)

### 구매 승인은 결제 전송과 별개입니다

AP2의 현재 v0.2 설명은 `Checkout Mandate`와 `Payment Mandate`를 구분합니다. 전자는 구매할 항목과 조건을, 후자는 특정 결제 수단의 지급 권한을 담습니다. Open 단계는 자율 구매의 제약을 정하고, Closed 단계는 확정한 체크아웃이나 특정 금액의 거래를 승인합니다. 에이전트가 견적 메시지를 받았다는 사실만으로 결제 권한을 얻는 구조가 아닙니다. [AP2의 Mandate 정의](https://ap2-protocol.org/)

UCP는 그 거래의 상품·체크아웃·주문 정보를 다룹니다. 결제 승인을 증명하는 AP2, 자금을 정산하는 x402와 각각 역할이 다릅니다. 이 경계를 유지해야 주문 확정, 사용자 승인, 실제 정산을 같은 성공 상태로 뭉뚱그리지 않을 수 있습니다. [UCP의 상거래 범위](https://ucp.dev/)

## 지원 조직 수와 실제 운영을 구분합니다

Linux Foundation은 [2026년 4월 9일 발표](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)에서 150개 넘는 지원 조직, Google·Microsoft·AWS 플랫폼 통합, 여러 산업의 프로덕션 사용을 보고했습니다. 이는 재단이 발표한 지원·도입 현황입니다. 150개 조직이 모두 유료 서비스나 대규모 운영을 한다는 수치는 아닙니다.

[2026년 8월 17일 AAIF 합류 발표](https://aaif.io/blog/a2a-joins-aaif)는 더 구체적인 연결을 설명합니다. Huawei의 Celia와 앱 에이전트 간 장기 작업 위임, Tencent WeChat과 OS 어시스턴트 연동, 주요 클라우드의 A2A 서버 호스팅이 사례로 등장합니다. 이런 사례는 실제 연결 대상과 플랫폼 지원을 보여 주지만, 발표만으로 처리량·장애율·재사용률을 비교할 수는 없습니다.

도입 판단에서는 같은 팀의 함수 몇 개를 묶는 상황과, 서로 다른 팀이 배포·운영하는 서비스에 일을 넘기는 상황을 나눌 필요가 있습니다. 호출 결과만 받으면 되는 기능은 기존 API나 MCP 도구로 충분할 수 있습니다. 상대가 작업 상태를 보관하고 추가 질문·권한 요청·지연된 결과를 돌려줘야 한다면 A2A의 계약을 채택할 이유가 더 분명해집니다. 운영자는 그 위에 업무 용어, 접근 정책, 재시도, 결제 승인을 정해야 합니다. 프로토콜이 그 결정을 대신하지는 않습니다.

## 함께 보면 좋을 자료

- [A2A 1.0.1 명세](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md): 요청·상태·바인딩·보안 계약을 확인할 기준입니다.
- [Python SDK v1.2.2 README](https://github.com/a2aproject/a2a-python/blob/v1.2.2/README.md): 호환성 표와 실행 예제 연결을 제공합니다.
- [A2A와 MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/): 도구 사용과 독립 에이전트 협업을 함께 설계할 때 참고할 설명입니다.

## 참고 자료

- [A2A v1.0.1 릴리스](https://github.com/a2aproject/A2A/releases/tag/v1.0.1): a2aproject, 조회 2026-10-15 UTC.
- [A2A 1.0.1 명세](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md), [프로토콜 스키마](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto): a2aproject, 조회 2026-10-15 UTC.
- [Python SDK v1.2.2 릴리스](https://github.com/a2aproject/a2a-python/releases/tag/v1.2.2), [README](https://github.com/a2aproject/a2a-python/blob/v1.2.2/README.md): a2aproject, 조회 2026-10-15 UTC.
- [Agent Discovery](https://a2a-protocol.org/latest/topics/agent-discovery/), [A2A and MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/): A2A 문서, 조회 2026-10-15 UTC.
- [A2A x402 Payments Extension v0.2](https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md): google-agentic-commerce, 조회 2026-10-15 UTC.
- [AP2](https://ap2-protocol.org/), [UCP](https://ucp.dev/): 공식 문서, 조회 2026-10-15 UTC.
- [A2A Protocol Surpasses 150 Organizations](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year): Linux Foundation, 2026-04-09, 조회 2026-10-15 UTC.
- [A2A joins AAIF's open agentic stack](https://aaif.io/blog/a2a-joins-aaif): AAIF, 2026-08-17, 조회 2026-10-15 UTC.
