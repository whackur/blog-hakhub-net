---
title: "The A2A (Agent-to-Agent) Protocol: How Agents Delegate to Each Other, and Where Payments Plug In"
meta_title: ""
description: "How A2A 1.0 handles Agent Card discovery, delegation, task state, streaming and authentication. Separating MCP tool access, AP2 purchase authorization, UCP commerce and x402 settlement, with the conditions each integration needs."
date: 2026-08-27T10:00:00+09:00
lastmod: 2026-10-15T15:41:34Z
image: "/images/posts/a2a-agent-to-agent-protocol/a2a-editorial-20261016.webp"
categories: ["Blockchain"]
tags: ["a2a", "ai-agent", "agentic-payments", "x402", "mcp"]
author: "whackur"
translationKey: "a2a-agent-to-agent-protocol"
draft: false
---

**A2A (Agent2Agent) standardizes how to delegate work to an independently operated agent and receive progress and results.** A client reads an Agent Card for capabilities, endpoints and authentication requirements, then tracks longer work as a Task. MCP connects each agent to tools and data; separate protocols such as AP2 and x402 handle purchase authorization and payment settlement. Collaborating over A2A requires neither a blockchain nor a wallet. [A2A specification](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md), [division of responsibilities with MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/)

## The units of a procurement request

Suppose a procurement agent asks an external supplier agent for a quote and delivery date for 100 units of a part. The supplier needs to check inventory and calculate shipping conditions. It may ask for clarification of the part number before returning a quotation document or structured data. The client does not need access to the supplier's internal prompts, model or tools.

A2A represents this exchange with the following objects. The quantity and scenario are illustrative, not a reported transaction. The definitions come from the specification's [core concepts and data model](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#22-core-concepts).

| Object | Role in the procurement example | Distinction |
| --- | --- | --- |
| Agent Card | Advertises quotation skills, endpoints, formats and authentication requirements | A capability description, not a quality certificate. |
| Message | A quotation request, clarification or reply | One turn of communication. |
| Task | The quotation job and its current state | Tracked with a server-generated ID. |
| Artifact | The finished quotation or price and delivery data | A work product, distinct from a progress message. |
| Part | Text, a file or a structured value within a message or result | A message can contain several content formats. |

The client is the application or agent initiating a request. The server is the remote agent exposing an A2A endpoint. A service becomes a client when it calls another agent. A2A defines the exchange across that boundary; implementers choose the internal reasoning process and how many agents to use.

### Specification and SDK versions

As checked on October 15, 2026 UTC, the latest official specification release is [v1.0.1](https://github.com/a2aproject/A2A/releases/tag/v1.0.1), while the official Python SDK release is [v1.2.2](https://github.com/a2aproject/a2a-python/releases/tag/v1.2.2). These version numbers identify different things. The Python SDK v1.2.2 [compatibility table](https://github.com/a2aproject/a2a-python/blob/v1.2.2/README.md) lists an A2A 1.0 implementation and a 0.3 compatibility mode, covering JSON-RPC, HTTP+JSON/REST and gRPC.

Protocol negotiation uses `1.0`, without the patch number. The Agent Card's own `version` identifies the agent software; each interface's `protocolVersion` identifies A2A. Confusing these can produce an invalid request even after upgrading the SDK. [Version rules](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#36-versioning)

## Discover the card and select an interface

If the client knows the supplier's domain, it can fetch `https://{domain}/.well-known/agent-card.json`. An organization can instead maintain a catalog or configure card URLs directly. A2A does not prescribe one global directory that automatically finds every agent. Choosing trusted catalogs and providers remains an operational decision. [Discovery mechanisms](https://a2a-protocol.org/latest/topics/agent-discovery/)

The client reads the card's `skills`, input and output media types, `capabilities` and security requirements. The ordered `supportedInterfaces` list advertises each URL, `protocolBinding` and `protocolVersion`. The client selects a supported interface and uses its URL. If the interface declares a `tenant`, requests must carry the same value. That routes requests when several agents share an endpoint. [Agent Card and interface definitions](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

Reaching an endpoint and having permission to use it are separate conditions. A public card can advertise quotation skills while prices remain restricted to particular customers. A server may provide a more detailed card after authentication, advertised by `capabilities.extendedAgentCard`. Its public skills list does not grant every caller access to those skills. [Extended cards and access control](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#3111-get-extended-agent-card)

## From a message to completed work

A 1.0 JSON-RPC request can take this form. Use the endpoint from the card and configure authentication headers separately according to that service's requirements. This example illustrates the message structure; it is not a record of an executed transaction. The method is `SendMessage` and the sending role is `ROLE_USER`. [Method mapping](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#53-method-mapping-reference), [message schema](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

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

`returnImmediately: true` requests a response before processing finishes. The default, `false`, waits for a terminal state such as completion or failure, or an interrupted state requiring input or authorization. The server creates a Task when work needs tracking, but it can return a direct Message for a simple interaction. Not every conversation becomes a long-running job. [Send configuration](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#322-sendmessageconfiguration)

If the server creates a quotation Task, the client stores its ID. `rpc-1` correlates the JSON-RPC request and response, while `messageId` identifies a message. Neither is the server-generated Task ID. A `contextId` groups related tasks and messages without sharing the agents' internal memory.

Tasks use the following states. The exact enum names appear in the [v1.0.1 protocol definition](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto).

| State | Meaning and the client's next action |
| --- | --- |
| `TASK_STATE_SUBMITTED`, `TASK_STATE_WORKING` | Acknowledged or being processed. Wait for status and result updates. |
| `TASK_STATE_INPUT_REQUIRED` | More information, such as a part number, is needed. Reply with the same `taskId`. |
| `TASK_STATE_AUTH_REQUIRED` | Additional authority, such as API access or human approval, is needed. Fulfill it through the agreed process. |
| `TASK_STATE_COMPLETED` | Finished successfully. Read the resulting Artifacts. |
| `TASK_STATE_FAILED`, `TASK_STATE_CANCELED`, `TASK_STATE_REJECTED` | Finished with an error, cancellation or refusal. Do not treat it as a successful result. |

Input and authorization requests are interrupted states from which work can continue. Completion, failure, cancellation and rejection are terminal: a client cannot resume that Task by sending another message to it. An order based on a finished quotation should become new work with the relevant context linked. [Task identifiers and multi-turn interactions](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#34-multi-turn-interactions)

`CancelTask` requests cancellation without guaranteeing success. Work may already have finished or reached a stage that cannot be canceled. Retries need care too. The specification does not require `SendMessage` deduplication; agents may use `messageId` for it. Resending a request after a network timeout therefore does not guarantee that an order or payment side effect executes only once. The service needs an explicit deduplication and retry policy. [Cancellation](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#315-cancel-task), [idempotency](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#331-idempotency)

## Three ways to receive progress

Choose a delivery mechanism according to processing time and network conditions. Streaming and push require the corresponding capabilities in the card. [Update delivery rules](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#35-task-update-delivery-mechanisms)

- **Polling**: Fetch current state and results with `GetTask`. No persistent connection is needed; polling intervals add delay and potentially unnecessary requests.
- **Streaming**: Receive events through `SendStreamingMessage` or `SubscribeToTask` for existing work. Requires `capabilities.streaming`. JSON-RPC and HTTP+JSON use SSE; gRPC uses its native stream.
- **Push**: The server sends HTTP POST requests to a registered webhook. Requires `capabilities.pushNotifications` and a reachable receiver.

A task stream starts with a Task, followed by `TaskStatusUpdateEvent` and `TaskArtifactUpdateEvent` updates carrying state changes and result chunks. Streaming means more than displaying generated tokens. The task lifecycle is independent of the connection, so losing a stream does not establish that the work was canceled. A client can query with its saved ID or subscribe again to ongoing work.

Push does not guarantee an exactly-once, durable message queue either. Servers must attempt delivery at least once, while retry and abandonment policies leave implementation choices. Receivers must validate expected Task IDs, verify the sender and tolerate duplicate notifications. Servers also need webhook URL validation to prevent requests to arbitrary internal addresses. [Push payload and delivery conditions](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#433-push-notification-payload), [security requirements](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#132-push-notification-security)

## Authenticate the connection and authorize the work

Production deployments require HTTPS for HTTP bindings and TLS for gRPC. A client reads `securitySchemes` and security requirements from the card, obtains credentials through an external process such as OAuth, and supplies them in request headers or binding-specific metadata. The server authenticates requests, then authorizes skills, data and task access under its own policy. Knowing a Task ID must not grant access to another customer's work. [Authentication and authorization](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#7-authentication-and-authorization), [data access scoping](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#131-data-access-and-authorization-scoping)

An authenticated caller may still need further authority during a task. Permission to read a quote, for example, need not include permission to place an order. The server can pause with `TASK_STATE_AUTH_REQUIRED` and explain the approval needed. Credentials travel out of band by default; sending them inside the conversation requires an extension or prior agreement. Putting a token in a conversation that passes through several agents can expose it to each intermediary. [In-task authorization](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#76-in-task-authorization)

Agent Card signatures perform a different check. A card can optionally be canonicalized with JCS and signed with JWS to establish integrity and verify the signer. The verifier must also assess trust in the public key. A valid signature does not establish answer quality, fair pricing or the user's consent to a purchase. Card signing does not require blockchain registration. [Card signing](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#84-agent-card-signing)

## Tools, commerce and payments have separate contracts

The supplier agent can use MCP (Model Context Protocol) to query its inventory database and A2A to exchange quotation work with the procurement agent. The official documentation describes using both together. A simple capability can also be exposed as a tool, so the presence of an agent alone does not make A2A necessary. [A2A and MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/)

As the transaction proceeds, it needs contracts beyond exchanging work.

| Protocol | Main responsibility | Relationship to A2A |
| --- | --- | --- |
| UCP (Universal Commerce Protocol) | Commerce exchanges involving products, carts, checkout and orders | A commerce protocol compatible with A2A, MCP and other integrations. |
| AP2 (Agent Payments Protocol) | Signed evidence of permitted purchases and payment authority | A separate authorization protocol available for A2A and UCP. |
| a2a-x402 extension | Payment requirements, signed payment information and on-chain settlement results | A separate extension document for paid A2A services. |

These components are not all mandatory. A free quotation needs no payment, and an AP2 transaction using a card does not require on-chain settlement. [UCP overview](https://ucp.dev/), [AP2 overview](https://ap2-protocol.org/), [a2a-x402 v0.2 document](https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md)

### x402 attaches payment requirements and receipts to work

The separate **a2a-x402 v0.2 document** defines a flow in which the merchant agent pauses work and sends payment requirements. The client chooses an option, signs a `PaymentPayload` through a wallet or signing service, and returns it to the same task. The merchant verifies the payment signature, settles on-chain and provides a receipt and the work product. Submitting a signature and completing settlement are different stages. [Payment flow](https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md)

The Standalone flow places requirements under `x402.payment.required` in `task.status.message.metadata` and submission data under `x402.payment.payload` in `message.metadata`. The Embedded flow nests payment structures in a higher-level commerce protocol's objects. Values such as `payment-required`, `payment-submitted` and `payment-completed` in `x402.payment.status` belong to the extension, not A2A's core Task states.

The document's examples use `input-required` and `X-A2A-Extensions`. Those spellings differ from A2A 1.0's `TASK_STATE_INPUT_REQUIRED` enum and `A2A-Extensions` service parameter. Do not assume the examples work unchanged with a 1.0 server: validate state, header and payload mapping in the selected extension implementation and SDK. The existence of an extension document also does not establish that a particular service operates it with real funds. [Extension document](https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md), [1.0 service parameters](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md#326-service-parameters)

### Purchase authorization is separate from payment transmission

AP2's current v0.2 overview distinguishes `Checkout Mandate` from `Payment Mandate`. The former captures purchase items and terms; the latter authorizes payment against a particular instrument. An Open stage sets constraints for autonomous purchases, while a Closed stage authorizes a finalized checkout or a transaction for a specific amount. Receiving a quotation message does not grant an agent authority to pay. [AP2 mandate definitions](https://ap2-protocol.org/)

UCP handles the transaction's product, checkout and order information. That differs from AP2's evidence of authorization and x402's settlement of funds. Keeping these responsibilities distinct prevents order confirmation, user approval and actual settlement from being collapsed into one success state. [UCP commerce scope](https://ucp.dev/)

## Supporting organizations and operational use

In its [April 9, 2026 announcement](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year), the Linux Foundation reported more than 150 supporting organizations, integration across Google, Microsoft and AWS platforms, and production use across industries. These are foundation-reported support and adoption claims. The figure does not count 150 organizations all running paid services or large deployments.

The [August 17, 2026 announcement that A2A was joining AAIF](https://aaif.io/blog/a2a-joins-aaif) describes more concrete connections: long-running task delegation between Huawei's Celia and app agents, Tencent WeChat integration with OS assistants, and A2A server hosting on major clouds. These cases show integration targets and platform availability. The announcement alone cannot establish comparative throughput, failure rates or retention.

An adoption decision should distinguish a few functions owned by one team from work delegated to services deployed and operated by separate teams. An existing API or MCP tool may suffice when a caller only needs a function result. A2A has a clearer purpose when the remote service must retain task state, ask follow-up questions, request additional authority and return delayed results. Operators still need to define business vocabulary, access policies, retries and purchase authorization. The protocol does not make those decisions for them.

## Further reading

- [A2A 1.0.1 specification](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md): the reference for requests, states, bindings and security contracts.
- [Python SDK v1.2.2 README](https://github.com/a2aproject/a2a-python/blob/v1.2.2/README.md): the compatibility matrix and links to runnable examples.
- [A2A and MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/): guidance for designing tool access alongside independent agent collaboration.

## References

- [A2A v1.0.1 release](https://github.com/a2aproject/A2A/releases/tag/v1.0.1): a2aproject, accessed 2026-10-15 UTC.
- [A2A 1.0.1 specification](https://github.com/a2aproject/A2A/blob/v1.0.1/docs/specification.md), [protocol schema](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto): a2aproject, accessed 2026-10-15 UTC.
- [Python SDK v1.2.2 release](https://github.com/a2aproject/a2a-python/releases/tag/v1.2.2), [README](https://github.com/a2aproject/a2a-python/blob/v1.2.2/README.md): a2aproject, accessed 2026-10-15 UTC.
- [Agent Discovery](https://a2a-protocol.org/latest/topics/agent-discovery/), [A2A and MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/): A2A documentation, accessed 2026-10-15 UTC.
- [A2A x402 Payments Extension v0.2](https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md): google-agentic-commerce, accessed 2026-10-15 UTC.
- [AP2](https://ap2-protocol.org/), [UCP](https://ucp.dev/): official documentation, accessed 2026-10-15 UTC.
- [A2A Protocol Surpasses 150 Organizations](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year): Linux Foundation, 2026-04-09, accessed 2026-10-15 UTC.
- [A2A joins AAIF's open agentic stack](https://aaif.io/blog/a2a-joins-aaif): AAIF, 2026-08-17, accessed 2026-10-15 UTC.
