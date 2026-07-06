---
title: "Apify x402와 Coinbase 지갑 심층편: 에이전트가 웹 자동화 도구를 직접 사는 구조"
meta_title: ""
description: "Apify가 2만 개 넘는 Actor를 x402로 열었다. HTTP 402 결제 흐름, EIP-3009·Permit2, facilitator, Coinbase Agentic Wallet, Bazaar 발견 레이어, 보안 체크리스트, 에이전트 결제 생태계와 한국 제약을 함께 정리한다."
date: 2026-07-05T01:10:00+09:00
lastmod: 2026-07-06T11:32:39+09:00
image: ""
categories: ["Blockchain"]
tags: ["x402", "agentic-payments", "apify", "coinbase", "ai-agent", "usdc", "base", "eip-3009", "stablecoin"]
author: "whackur"
translationKey: "apify-x402-agentic-payments-coinbase-wallet"
draft: false
---

웹 스크래핑 플랫폼 Apify가 [x402 결제 지원](https://blog.apify.com/introducing-x402-agentic-payments/)을 발표했다. AI 에이전트가 Apify 계정도 API 키도 없이 Base 체인의 USDC로 결제하고, 2만 개가 넘는 Actor를 실행할 수 있다는 내용이다. Apify는 기존 x402 생태계를 약 2,000개 엔드포인트 규모로 보고, 이번 통합으로 결제 가능한 도구 표면이 약 10배 커졌다고 설명한다.

숫자보다 중요한 변화는 구조다. 사람이 가입하고 카드나 크레딧을 등록해야 쓸 수 있던 웹 자동화 마켓플레이스가, 에이전트가 실행 시점에 발견하고 결제하고 호출하는 도구 공급 레이어가 됐다. 이 글은 이전 글을 확장해 기술 구조와 사업적 의미를 함께 정리한다. x402의 HTTP 402 흐름, EIP-3009와 Permit2, facilitator, Coinbase Agentic Wallet, Bazaar 발견 레이어, 보안 체크리스트, 경쟁·보완 프로토콜, 한국 개발자에게 남는 제약을 한 번에 본다.

## 3줄 요약

- Apify는 2026년 6월 30일 2만 개 넘는 Actor를 x402 결제 경로에 올렸다. 에이전트는 Apify 계정이나 API 키 없이 Base USDC로 Actor 실행 비용을 낼 수 있다.
- x402는 잠자던 HTTP 402 Payment Required를 실제 결제 핸드셰이크로 쓰는 오픈 프로토콜이다. v2는 `PAYMENT-REQUIRED`, `PAYMENT-SIGNATURE`, `PAYMENT-RESPONSE` 헤더와 Bazaar 발견 확장을 표준화했다.
- 프로토콜은 국경이 없지만 주변 레이어에는 국경이 있다. 지갑과 온램프, Apify 판매자 KYC와 지급 수단, 스테이블코인 규제, 세금, 스크래핑 합법성은 국가별로 따로 점검해야 한다.

## Apify가 x402에 붙으면서 달라진 것

Apify는 웹 스크래핑과 브라우저 자동화를 클라우드에서 돌리는 플랫폼이다. 실행 단위는 Actor라고 부르는 서버리스 프로그램이고, 개발자는 Actor를 [Apify Store](https://docs.apify.com/platform/actors/publishing/monetize)에 올려 판매할 수 있다. 검색 결과 수집기, SNS 크롤러, 쇼핑몰 가격 모니터, 지도 데이터 수집기 같은 도구가 이미 상품으로 존재한다.

기존 고객은 사람이었다. 가입하고, 결제 수단을 등록하고, API token을 발급받아 호출하는 흐름이다. x402 통합은 이 전제를 바꾼다. 에이전트가 Actor API를 호출하면 서버가 결제 요구를 HTTP 402로 돌려주고, 에이전트 지갑이 결제 payload에 서명한 뒤 같은 요청을 재시도한다. Apify는 MCP용 범용 CLI인 [`mcpc`](https://github.com/apify/mcpc)에도 x402 지원을 넣어, MCP tool discovery와 결제를 자연스럽게 붙였다.

이제 에이전트의 도구 목록은 배포 시점에 고정되지 않는다. 필요한 순간에 “Instagram profile scraper를 1달러어치만 실행하라”처럼 요청하고, 지갑 잔액과 정책이 허용하면 그 자리에서 도구를 산다. 이것이 Apify 통합의 핵심이다. 단순한 crypto checkout이 아니라, 에이전트가 런타임에 구매 가능한 tool supply layer가 열린 것이다.

## x402의 결제 흐름

HTTP 402 Payment Required는 HTTP/1.1 시절부터 “나중에 결제에 쓰라”고 예약된 상태 코드였지만 오래 실사용되지 않았다. x402는 이 코드를 결제 프로토콜로 되살린다. [Coinbase Developer Platform 문서](https://docs.cdp.coinbase.com/x402/welcome)에 따르면 x402는 HTTP 위에서 stablecoin 결제를 처리하는 오픈 프로토콜이고, 계정 생성이나 API key 없이 클라이언트와 서버가 결제 조건을 주고받게 한다.

흐름은 네 단계다.

1. 클라이언트가 유료 리소스에 일반 HTTP request를 보낸다.
2. 서버가 HTTP 402와 `PAYMENT-REQUIRED` 헤더를 반환한다. 이 헤더에는 scheme, network, token, 금액, 수취인, 만료 조건 같은 결제 요구사항이 base64 JSON으로 들어간다.
3. 클라이언트 지갑이 결제 payload에 서명하고, 같은 요청을 `PAYMENT-SIGNATURE` 헤더와 함께 다시 보낸다.
4. 서버는 facilitator를 통해 서명을 검증하고 settlement를 처리한 뒤, 리소스와 `PAYMENT-RESPONSE` 헤더를 반환한다.

x402 v2는 이 세 헤더를 표준화했다. `PAYMENT-REQUIRED`는 서버에서 클라이언트로 가는 결제 요구, `PAYMENT-SIGNATURE`는 클라이언트가 보낸 결제 증명, `PAYMENT-RESPONSE`는 settlement 결과다. Apify 예시에서는 Base mainnet을 CAIP-2 식별자인 `eip155:8453`으로 표시하고, USDC 6 decimals 기준 `1000000`이 1달러를 뜻한다.

## EIP-3009, Permit2, facilitator가 하는 일

x402에서 “가스리스”라고 부르는 경험의 핵심은 구매자가 직접 on-chain transaction을 보내지 않는다는 점이다. EVM에서 가장 매끄러운 경로는 [EIP-3009](https://eips.ethereum.org/EIPS/eip-3009) `transferWithAuthorization`이다. 구매자는 `from`, `to`, `value`, `validAfter`, `validBefore`, `nonce` 같은 필드가 담긴 EIP-712 typed message에 서명한다. facilitator가 그 서명을 on-chain으로 제출하고 gas를 낸다. USDC와 EURC가 EIP-3009를 지원하기 때문에 x402의 기본 사례가 USDC에 집중된다.

모든 ERC-20이 EIP-3009를 지원하는 것은 아니다. 일반 ERC-20에는 Permit2를 쓴다. Permit2는 Uniswap이 만든 범용 approval/transfer 레이어이고, x402는 Permit2와 gas sponsorship extension으로 generic ERC-20 결제도 처리할 수 있게 한다. 단, gas sponsorship이 없으면 첫 결제 전에 Permit2 approval이 필요할 수 있다. 그래서 사용자 경험은 EIP-3009 지원 token이 가장 단순하다.

facilitator는 판매자가 직접 블록체인 인프라를 운영하지 않도록 해 주는 중간 서비스다. 서버는 결제 payload를 facilitator의 verify/settle 경로로 넘기고, facilitator가 signature 검증과 on-chain settlement를 처리한다. [CDP network support 문서](https://docs.cdp.coinbase.com/x402/network-support)에 따르면 Coinbase Developer Platform facilitator는 Base, Polygon, Arbitrum, World, Solana 등을 지원하며, 월 1,000건까지 무료이고 이후 건당 0.001달러를 받는다. gas는 별도다. 프로토콜 자체에는 native token이나 protocol fee가 없다.

x402가 체인 하나에 묶인 것도 아니다. [x402 network/token 문서](https://docs.x402.org/core-concepts/network-and-token-support)는 EVM, Solana, TON, Algorand, Stellar, Aptos, Hedera, Keeta, Concordium 같은 여러 네트워크 계열을 다룬다. 다만 이것은 x402와 facilitator 생태계의 확장성 이야기이고, Apify의 현재 integration은 Base USDC에 맞춰져 있다.

## 결제 scheme: exact, upto, batch-settlement

x402에서 scheme은 “얼마를 어떤 방식으로 승인하고 정산할 것인가”를 정한다.

`exact`는 고정 금액 결제다. 기사 1편, API 1회처럼 가격이 미리 정해진 리소스에 맞다. Apify처럼 실행이 끝나야 비용이 확정되는 Actor에는 약간 어색하다. Apify 발표는 이를 위해 1달러 prepaid deposit을 받고, 사용하지 않은 잔액을 나중에 환불하는 흐름을 설명한다. 직접 Actor run에서 `exact`를 쓰는 경우에는 60분 동안 active run이나 새 paid call이 없으면 남은 server-side balance가 환불된다고 Apify가 설명한다.

`upto`는 가변 비용에 더 자연스럽다. 클라이언트가 최대 금액을 승인하면 서비스가 실제 사용량만큼만 청구한다. Apify는 `upto`를 variable-cost Actor에 더 적합한 scheme으로 설명한다. 이 경우 서비스는 Actor run을 시작하고, 완료 후 실제 사용량을 계산해 승인 한도 안에서 settlement한다.

`batch-settlement`는 고빈도 micropayment를 매번 on-chain settlement하지 않고 묶어서 처리하는 방향이다. x402 문서에서는 escrow와 off-chain voucher를 batch로 redeem하는 방식으로 설명한다. Cloudflare도 crawler와 publisher 사이에서 handshake와 settlement를 분리하는 deferred scheme을 제안했다. 이런 흐름은 pay-per-crawl이나 LLM token generation처럼 요청이 많고 단가가 낮은 workload에 중요하다.

여기서 주의할 점이 있다. Apify 문서의 수동 prepaid token 경로와 Apify 발표의 direct Actor-run `exact` refund flow를 섞으면 안 된다. [Apify x402 문서](https://docs.apify.com/platform/integrations/x402)의 prepaid token은 최소 1달러, token balance가 hard cap, 구매 후 14일 만료, unused balance non-refundable이다. 반면 발표 글의 direct Actor-run `exact` flow는 1달러 deposit과 60분 inactivity 후 refund를 설명한다. 둘 다 Apify가 문서화한 흐름이지만 적용 맥락이 다르다.

## Agentic Wallet은 거래소 계정이 아니다

Coinbase라는 이름 때문에 헷갈리기 쉽다. Apify 문서가 추천하는 `awal`은 Coinbase exchange 계정이 아니라 Coinbase Agentic Wallet CLI다. 에이전트가 email OTP로 인증하고, Base USDC를 보관하고, 402 challenge를 읽어 payment payload에 서명하도록 해 주는 지갑 도구다.

중요한 사실은 자금 위치다. [Apify 문서](https://docs.apify.com/platform/integrations/x402)는 자금이 Coinbase exchange account가 아니라 지갑 자체에 있으며, Base로 USDC를 보낼 수 있는 어떤 출처에서든 채울 수 있다고 말한다. 거래소에서 출금해도 되고, 다른 wallet에서 보내도 되고, 온램프를 써도 된다. x402 프로토콜이 요구하는 것은 “지원 네트워크와 asset을 다룰 수 있는 funded wallet”이지 Coinbase 거래소 가입이 아니다.

그렇다고 지갑 리스크가 사라지는 것은 아니다. Agentic Wallet은 사람이 클릭하는 UI 대신 programmable signing surface, spending limit, 정책, audit trail이 핵심이다. 에이전트가 서명할 수 있는 지갑은 low-balance hot wallet이나 prepaid debit card처럼 다뤄야 한다. 운영자는 지갑 잔액, token별 allowance, task별 budget, 허용 Actor 목록을 별도로 정해야 한다.

## Apify의 실제 과금과 Actor 조건

Apify의 x402 경로에는 두 구매 방식이 있다.

첫째는 기존 Apify account path다. 사람이 계정을 만들고 billing을 등록하고 API token으로 Actor를 호출한다. x402가 들어와도 이 경로는 그대로 남는다. 클라이언트가 payment signature 대신 Apify token을 보내면 계정 잔액에서 결제할 수 있다.

둘째가 wallet path다. `awal`로 지갑을 인증하고, Base USDC와 최초 wallet deployment용 소량의 Base ETH를 넣고, agentic endpoint에서 결제한다. 문서상 manual prepaid token을 구매하면 그 token이 bearer token처럼 동작한다. 잔액이 남아 있는 동안 Actor run 비용이 차감되고, token balance가 absolute spending cap이 된다. token은 14일 후 만료되고 unused balance는 환불되지 않으므로 필요한 만큼만 사는 편이 맞다.

모든 Actor가 이 경로로 열리는 것은 아니다. 현재 x402 eligible Actor는 세 조건을 만족해야 한다. Pay Per Event pricing을 써야 하고, limited permissions로 실행되어야 하며, Standby mode가 아니어야 한다. 적격 Actor는 `allowsAgenticUsers=true`로 표시되어 agentic discovery에 노출된다.

판매자 쪽도 단순한 “wallet 주소만 적으면 끝”이 아니다. 일반 Apify monetization 경로를 탄다. 수익 배분은 PPE 기준 80%이고, 지급은 월 단위로 처리된다. 월 11일 invoice가 생성되고 3일 review window 뒤 14일 자동 승인된다. 최소 지급액은 PayPal/Wise 20달러, 그 외 지급 수단 100달러다. 수익을 받으려면 billing 정보, payout method, identity verification, AML/KYC를 통과해야 한다.

## Bazaar와 도구 발견 레이어

x402는 endpoint를 결제 가능하게 만들지만, 그 endpoint를 어떻게 찾을지는 별도 문제다. CDP Bazaar는 이 발견 문제를 다루는 레이어다. [CDP Bazaar 문서](https://docs.cdp.coinbase.com/x402/bazaar)에 따르면 Bazaar는 x402-enabled service를 catalog와 search endpoint로 노출하고, endpoint metadata와 on-chain activity에서 나온 trust signal을 함께 제공한다.

판매자는 route 설정에 input/output schema와 discovery metadata를 선언한다. CDP facilitator가 해당 endpoint의 settlement를 성공적으로 처리하면 metadata를 catalog에 반영한다. verify만으로는 부족하고 settle이 완료되어야 한다. 별도 등록 절차는 없다.

구매자는 `GET /v2/x402/discovery/resources`로 paginated catalog를 훑거나, `GET /v2/x402/discovery/search`로 semantic/hybrid search를 쓸 수 있다. Bazaar MCP server를 통해 MCP tool discovery와 paid call proxy를 붙이는 경로도 있다. 활동이 30일 없는 resource는 결과에서 제외되고, quality metric은 6시간 주기로 재계산된다.

에이전트 경제에서 Bazaar가 중요한 이유는 명확하다. 지갑이 결제 수단이고 x402가 결제 언어라면, Bazaar는 “무엇을 살 수 있는가”를 찾는 검색 레이어다. Apify가 Actor marketplace를 x402에 붙인 것은 이 discovery layer의 의미를 더 키운다.

## 경쟁·보완 프로토콜 지도

에이전트 결제는 x402 하나로 끝나는 시장이 아니다. 역할이 조금씩 다른 프로토콜과 네트워크가 겹친다.

- **MCP**는 agent가 tool을 발견하고 호출하는 인터페이스다. 결제 자체보다는 tool discovery와 invocation에 가깝다.
- **x402**는 HTTP resource에 결제 요구를 붙이고 wallet signature와 facilitator를 통해 settlement하는 machine-to-machine API payment rail이다.
- **Google AP2**는 Intent, Cart, Payment Mandate 같은 검증 가능한 mandate를 중심으로 결제 인가를 다룬다. 결제 수단은 card, bank transfer, crypto 등으로 열어 두고, stablecoin rail에는 x402 extension을 붙일 수 있다.
- **Skyfire**는 agent용 payment-as-a-service에 가깝다. spending cap과 identity layer를 상품화한다.
- **Stripe, Visa, Mastercard**는 기존 card/network 결제의 agent authorization과 checkout 흐름을 가져가려는 쪽이다.
- **Cloudflare**는 pay-per-crawl과 Monetization Gateway처럼 web resource 앞단에서 402와 settlement를 붙이는 edge gateway 관점을 갖고 있다.
- **Circle**은 USDC nanopayment 같은 stablecoin-native use case를 x402와 연결한다.

실전에서는 이들이 서로 배타적이라기보다 layer로 쌓일 가능성이 높다. tool discovery는 MCP, machine-to-machine API payment는 x402, retail checkout authorization은 AP2나 card-network framework, settlement asset은 stablecoin 또는 기존 rail이 되는 식이다.

## 채택 지표와 시장 전망을 읽는 법

에이전트 커머스 시장 전망은 크다. Bain, Morgan Stanley, McKinsey 같은 기관은 2030년 에이전트 커머스가 수천억 달러에서 수조 달러 규모가 될 수 있다는 전망을 낸다. 다만 이것은 실현된 매출이 아니라 forecast다. 방법론에 따라 범위가 크게 달라지고, agent가 실제 구매 주체가 되는 비중을 어디까지 볼지도 아직 열려 있다.

x402의 on-chain adoption 수치도 조심해서 읽어야 한다. 누적 거래 수나 transaction count는 test, gamified activity, self-dealing, wash-like behavior에 의해 부풀 수 있다. 특히 초기에 pay-to-mint나 incentive-driven traffic이 섞이면 “agent가 실서비스를 샀다”는 의미와 멀어진다. 그래서 cumulative volume만 보기보다 wash-adjusted volume, unique paying clients, 반복 구매, 실제 service endpoint의 settlement data를 함께 봐야 한다.

Apify 통합은 이 지점에서 흥미롭다. 아직 Apify-specific x402 volume은 충분히 공개되지 않았지만, web automation marketplace라는 실제 도구 공급망이 붙었다. 앞으로 봐야 할 임계치는 단순 transaction count가 아니라 “agent가 Actor를 반복 호출해 유의미한 업무를 끝냈는가”다.

## 한국 개발자에게 남는 제약

프로토콜 자체에는 국가 제한이 없다. x402는 HTTP와 wallet signature로 움직이고, Apify의 x402 구매 경로도 Apify account 없이 동작한다. 하지만 주변 레이어는 다르다.

첫째, 지갑과 온램프다. Coinbase exchange, onramp, hosted wallet product의 국가별 가용성은 다를 수 있다. `awal`을 쓸 계획이라면 한국에서 해당 product와 email OTP automation이 실제로 가능한지 확인해야 한다. 다만 Coinbase exchange account가 필수라는 뜻은 아니다. Base USDC를 지갑으로 보낼 수 있는 경로가 있으면 protocol requirement는 충족된다.

둘째, 판매자 KYC와 payout이다. Apify 공식 문서에서 “미국 거주자만 판매 가능”이라는 조건은 확인되지 않는다. 한국 개발자도 Apify 계정, billing information, tax document, payout method, identity verification을 준비하는 문제에 가깝다. 다만 지급 수단의 국가별 가용성, sanctions/watchlist screening, 세금 처리는 별도 이슈다.

셋째, 스테이블코인과 데이터 법이다. 한국의 stablecoin 규제는 아직 전용 체계가 정리되는 중이고, 스테이블코인 취득·보유·세무 처리는 계속 변할 수 있다. 또한 Actor를 사는 행위와 Actor가 수집하는 데이터의 합법성은 별개다. 대상 사이트 약관, 개인정보보호법, 저작권, 데이터베이스권, 업종별 규제를 Actor 단위로 봐야 한다.

KakaoPay가 x402 Foundation 참여사로 언급되는 점은 한국 결제사들도 agentic payment 표준화를 지켜보고 있다는 신호로 읽을 수 있다. 하지만 이것이 곧 국내 온램프나 원화 stablecoin settlement가 준비됐다는 뜻은 아니다. 한국에서의 production 도입은 protocol보다 주변 compliance와 payout 경로가 먼저 병목이 될 가능성이 높다.

## 운영 보안 체크리스트

실험을 시작한다면 기술보다 운영 정책을 먼저 정해야 한다.

- 지갑 잔액은 작게 유지한다. 첫 pilot은 총 10~50달러, Actor 3~5개 정도로 제한하는 식이 현실적이다.
- main wallet에서 직접 fund하지 않는다. agent wallet은 low-balance hot wallet로 취급한다.
- prepaid token과 `PAYMENT-SIGNATURE` payload는 API key처럼 다룬다. 로그, terminal output, issue, dashboard에 찍히지 않게 한다.
- Actor allowlist를 둔다. 에이전트가 “무엇이든 사도 되는” 상태를 만들지 않는다.
- `upto`나 prepaid cap으로 per-run maximum을 걸고, task-level budget도 별도로 둔다.
- side effect가 있는 작업에는 verify-then-work보다 settle-then-work를 우선한다. latency는 늘지만 grant-before-settlement와 replay window를 줄인다.
- nonce, 짧은 expiry, request path/method binding을 확인한다. proxy가 payment header를 잘못 전달하거나 재사용하지 않도록 한다.
- scraping legality를 Actor 단위로 검토한다. 도구 결제와 데이터 수집의 법적 판단은 별개다.
- email OTP 자동화는 별도 보안 표면이다. agent가 inbox를 읽을 수 있다면 그 권한도 최소화하고 감사 가능해야 한다.

## 정리

Apify의 x402 통합은 agentic payments를 데모에서 상품 규모로 끌어올린 사례다. 2만 개 넘는 Actor가 Base USDC와 HTTP 402 흐름으로 열리면서, 에이전트가 런타임에 도구를 발견하고 구매하고 실행하는 구조가 실제 marketplace에서 작동하기 시작했다.

하지만 바로 대규모 production으로 가기에는 아직 확인할 것이 많다. x402는 결제 언어이고, facilitator는 settlement 인프라를 줄여 주며, Agentic Wallet은 agent가 서명할 수 있는 지갑 표면을 만든다. 그 위에서 실제 운영 안전성은 budget cap, allowlist, token secrecy, KYC, payout, local law, scraping compliance가 결정한다.

따라서 지금의 합리적인 접근은 작게 시작하는 것이다. 낮은 잔액, 좁은 Actor allowlist, `upto` 또는 prepaid cap, settle-then-work, 명확한 로그 마스킹을 두고, 실제 Apify-specific settlement data와 x402의 wash-adjusted usage가 쌓이는지 지켜보는 편이 맞다.

## 함께 보면 좋을 자료

- [x402 판매자 quickstart](https://docs.x402.org/getting-started/quickstart-for-sellers): 직접 x402 유료 API를 만들 때의 SDK와 scheme 안내
- [Coinbase Developer Platform x402 문서](https://docs.cdp.coinbase.com/x402/welcome): 프로토콜 구조와 facilitator, 지원 네트워크
- [CDP x402 Bazaar](https://docs.cdp.coinbase.com/x402/bazaar): x402 endpoint discovery와 schema metadata 구조
- [에이전트 결제 2026년 6월 동향](/blog/agentic-payments-june-2026-x402-ucp-mpp/): x402를 포함한 결제 스택 전반의 최근 변화

## 참고 자료

- [Introducing x402 support: 10x more tools for autonomous agents](https://blog.apify.com/introducing-x402-agentic-payments/), Apify Blog, 조회일 2026-07-06
- [Apify x402 integration docs](https://docs.apify.com/platform/integrations/x402), Apify Docs, 조회일 2026-07-06
- [Monetize your Actor](https://docs.apify.com/platform/actors/publishing/monetize), Apify Docs, 조회일 2026-07-06
- [Monthly payouts](https://docs.apify.com/platform/actors/publishing/monetize/monthly-payouts), Apify Docs, 조회일 2026-07-06
- [Apify Store Publishing Terms and Conditions](https://docs.apify.com/legal/store-publishing-terms-and-conditions), Apify Legal, 조회일 2026-07-06
- [x402 overview](https://docs.cdp.coinbase.com/x402/welcome), Coinbase Developer Platform, 조회일 2026-07-06
- [Network Support](https://docs.cdp.coinbase.com/x402/network-support), Coinbase Developer Platform, 조회일 2026-07-06
- [x402 Bazaar](https://docs.cdp.coinbase.com/x402/bazaar), Coinbase Developer Platform, 조회일 2026-07-06
- [HTTP 402](https://docs.x402.org/core-concepts/http-402), x402 Docs, 조회일 2026-07-06
- [Networks & Token Support](https://docs.x402.org/core-concepts/network-and-token-support), x402 Docs, 조회일 2026-07-06
- [Introducing x402 V2](https://www.x402.org/writing/x402-v2-launch), x402 Blog, 2025-12-11
- [Introducing Agentic Wallets](https://www.coinbase.com/developer-platform/discover/launches/agentic-wallets), Coinbase Developer Platform, 2026-02-11
- [Launching the x402 Foundation with Coinbase](https://blog.cloudflare.com/x402/), Cloudflare Blog, 2025-09-23
- [Announcing Agent Payments Protocol](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol), Google Cloud
- [Five Attacks on x402 Agentic Payment Protocol](https://arxiv.org/abs/2605.11781), arXiv
- [x402 Explained: Security Risks & Controls](https://www.halborn.com/blog/post/x402-explained-security-risks-and-controls-for-http-402-micropayments), Halborn
- [Agentic Commerce Impact Could Reach $385 Billion by 2030](https://www.morganstanley.com/insights/articles/agentic-commerce-market-impact-outlook), Morgan Stanley
- [2030 Forecast: How Agentic AI Will Reshape US Retail](https://www.bain.com/insights/2030-forecast-how-agentic-ai-will-reshape-us-retail-snap-chart/), Bain & Company
- [Coinbase highlights Korea's potential as Kakao Pay enters its agentic payment alliance](https://www.koreatimes.co.kr/economy/cryptocurrency/20260416/coinbase-highlights-koreas-potential-as-kakao-pay-enters-its-agentic-payment-alliance), The Korea Times
