---
title: "Apify x402와 Coinbase 지갑: 에이전트가 웹 자동화 도구를 직접 사는 방식"
meta_title: ""
description: "Apify가 2만 개 넘는 Actor를 x402 결제로 열었다. HTTP 402 결제 흐름, Coinbase Agentic Wallet(awal)과 거래소 계정의 차이, Base USDC 선불 토큰, 판매자 KYC와 정산, 한국을 포함한 국가별 제약 레이어를 정리한다."
date: 2026-07-05T01:10:00+09:00
lastmod: 2026-07-05T01:10:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["x402", "agentic-payments", "apify", "coinbase", "ai-agent", "usdc", "base"]
author: "whackur"
translationKey: "apify-x402-agentic-payments-coinbase-wallet"
draft: false
---

웹 스크래핑 플랫폼 Apify가 [x402 결제 지원](https://blog.apify.com/introducing-x402-agentic-payments/)을 발표했다. AI 에이전트가 Apify 계정도 API 키도 없이, Base 체인의 USDC로 결제하고 2만 개가 넘는 Actor를 바로 실행할 수 있다는 내용이다. Apify는 기존 x402 생태계를 약 2,000개 엔드포인트 규모로 보고, 이번 통합으로 그 규모가 약 10배로 늘었다고 설명한다.

숫자보다 구조 변화가 흥미롭다. 사람이 가입하고 결제 수단을 등록해야 쓸 수 있던 웹 자동화 마켓플레이스가, 에이전트가 실행 시점에 발견하고 그 자리에서 구매하는 도구 공급 레이어로 바뀌었다. 다만 실제 도입을 가르는 질문은 프로토콜 동작이 아니라 그 주변에 있다. 지갑에 돈을 어떻게 넣는가, 지출 한도를 어떻게 거는가, 판매자 KYC와 정산은 어떻게 돌아가는가, 그리고 한국을 포함해 나라마다 어떤 레이어에서 제약이 걸리는가. 이 글은 공식 문서를 기준으로 이 질문들을 하나씩 짚는다.

## Apify Actors가 에이전트의 도구 공급망이 된다

Apify는 웹 스크래핑과 브라우저 자동화를 클라우드에서 돌리는 플랫폼이다. 실행 단위는 Actor라고 부르는 서버리스 프로그램이고, 개발자가 만든 Actor를 [Apify Store](https://docs.apify.com/platform/actors/publishing/monetize)에 올려 판매할 수 있다. 검색 결과 수집기, SNS 크롤러, 사이트 모니터링 같은 도구가 이미 상품으로 등록되어 있는 마켓플레이스다.

지금까지 이 마켓의 고객은 사람이었다. 가입하고, 카드나 크레딧을 등록하고, API 토큰을 발급받아 호출하는 흐름이다. x402 통합은 이 전제를 바꾼다. [Apify 발표](https://blog.apify.com/introducing-x402-agentic-payments/)에 따르면 에이전트는 Model Context Protocol(MCP)로 Actor의 메타데이터를 조회하다가 결제가 필요하다는 응답을 만나면, 지갑으로 결제를 승인하고 자동으로 재시도한다. 사람의 개입 없이 도구 발견부터 결제, 실행까지 이어진다. Apify는 MCP용 범용 CLI 클라이언트인 `mcpc`에도 x402 지원을 넣었다.

에이전트 입장에서 보면 "쓸 수 있는 도구 목록"이 코드 배포 시점에 고정되지 않고 런타임에 열린다. 필요한 스크래퍼를 그때그때 찾아 1달러어치 사서 쓰는 방식이 가능해진 셈이다.

## x402는 HTTP 402를 결제 흐름으로 되살린다

HTTP 402 Payment Required는 HTTP/1.1 시절부터 예약만 되어 있던 상태 코드다. x402는 이 코드를 실제 결제 흐름으로 쓴다. [Coinbase Developer Platform 문서](https://docs.cdp.coinbase.com/x402/welcome)에 따르면 x402는 Coinbase가 만들었고 지금은 Linux Foundation 산하에서 관리되는 오픈소스 프로토콜로, 계정이나 세션, 복잡한 인증 없이 HTTP 위에서 스테이블코인 결제를 처리한다.

흐름은 단순하다. 클라이언트가 유료 리소스를 요청하면 서버가 402 응답과 함께 결제 조건(체인, 토큰, 금액, 지원 scheme)을 돌려준다. 지갑이 USDC 전송을 오프체인에서 서명하고, 클라이언트는 `PAYMENT-SIGNATURE` 헤더에 결제 페이로드를 담아 재요청한다. 서버는 facilitator라는 중간 서비스로 서명을 검증하고 온체인 정산을 처리한 뒤 리소스를 반환한다. [Apify의 예시 challenge](https://blog.apify.com/introducing-x402-agentic-payments/)를 보면 네트워크는 CAIP-2 식별자 `eip155:8453`(Base 메인넷), 토큰은 소수점 6자리 USDC, 금액 `1000000`은 1달러다.

결제 scheme은 두 가지를 기억하면 된다. `exact`는 고정 가격 결제로, 선불 예치 후 잔액을 환불받는 패턴과 함께 쓸 수 있다. `upto`는 x402 v2에서 들어온 방식인데, 클라이언트가 최대 금액을 승인하면 서비스가 실제 사용량만큼만 청구한다. 실행이 끝나야 비용이 확정되는 가변 비용 Actor에 맞는 구조다. [판매자 quickstart](https://docs.x402.org/getting-started/quickstart-for-sellers)에는 `batch-settlement`까지 세 가지 scheme이 정리되어 있다.

프로토콜 자체는 특정 체인에 묶여 있지 않다. [Apify 문서](https://docs.apify.com/platform/integrations/x402)는 EVM 계열과 Solana를 지원하는 표준이라고 설명하고, CDP facilitator는 Base, Polygon, Arbitrum, World, Solana의 ERC-20 결제를 처리한다. 다만 Apify가 실제로 쓰는 조합은 Base의 USDC 하나다. 참고로 [x402.org](https://www.x402.org/)가 2026년 7월 5일 조회 시점에 표시한 생태계 지표는 누적 7,541만 건 거래, 2,424만 달러 규모였다. 변동이 큰 수치라 스냅샷으로만 봐야 한다.

## 구매자는 Apify 계정 또는 지갑 중 하나를 선택한다

Apify Actor를 유료로 쓰는 경로는 이제 둘이다.

첫째는 기존 경로다. Apify 계정을 만들고 카드나 크레딧을 등록한 뒤 API 토큰으로 호출한다. 사람이 관리하는 워크플로나 이미 Apify를 쓰는 팀이라면 바뀔 이유가 없다. x402 통합 이후에도 [클라이언트가 결제 서명 대신 Apify 토큰을 보내면 계정 잔액에서 결제](https://blog.apify.com/introducing-x402-agentic-payments/)할 수 있다.

둘째가 x402 지갑 경로다. [Apify x402 문서](https://docs.apify.com/platform/integrations/x402)가 밝히는 준비물은 네 가지다. Coinbase Agentic Wallet(`awal`) CLI, Base 메인넷의 USDC 최소 1달러, 최초 지갑 배포 가스비로 쓸 소량의 Base ETH(약 0.000001 ETH), 그리고 지갑 인증용 이메일 주소. 이메일 OTP로 인증하기 때문에 에이전트가 완전 자율로 돌려면 받은편지함에서 인증 코드를 읽을 수 있어야 한다. Apify 계정은 필요 없다.

이 경로에서 실제로 손에 쥐는 것은 선불 토큰이다. Apify의 agentic 엔드포인트에서 USDC로 잔액을 사면 그 잔액에 묶인 토큰이 발급되고, 잔액이 남아 있는 동안 API 토큰처럼 동작한다. 조건이 몇 가지 붙는다. 최소 거래 금액은 1달러, 토큰 잔액이 절대 지출 상한이 되고, 구매 후 14일이 지나면 만료되며, 남은 잔액은 환불되지 않는다. Apify는 이 기능 전체를 아직 실험(experimental) 단계로 표시하고 있다.

모든 Actor가 이 경로로 열리는 것도 아니다. Pay Per Event(PPE) 과금을 쓰고, 제한된 권한으로 실행되며, Standby 모드가 아닌 Actor만 대상이다.

## Coinbase 지갑은 편의 도구이고 거래소 계정은 필수가 아니다

여기서 헷갈리기 쉬운 지점이 Coinbase라는 이름이다. `awal`은 Coinbase 거래소 계정이 아니다. [Agentic Wallet CLI 문서](https://docs.cdp.coinbase.com/agentic-wallet/cli/welcome)에 따르면 이것은 AI 에이전트에게 주는 독립형 지갑이다. 에이전트는 이메일 OTP로 인증하고 USDC를 보관, 전송, 결제하는데, 개인키에는 접근하지 못한다. 키는 Coinbase 인프라에 남고, 지출 한도(spending limit)와 KYT(자금 흐름 추적), OFAC 제재 스크리닝이 지갑 레이어에서 걸린다. 지원 네트워크는 Base, Base Sepolia, Polygon, Solana, Solana Devnet이다.

중요한 건 자금의 위치다. [Apify 문서](https://docs.apify.com/platform/integrations/x402)는 자금이 Coinbase 거래소 계정이 아니라 지갑 자체에 있고, Base로 USDC를 보낼 수 있는 어떤 출처에서든 채울 수 있다고 명시한다. 거래소에서 출금해도 되고, 다른 지갑에서 보내도 되고, 온램프 서비스를 써도 된다. x402 프로토콜 차원의 요구사항은 "지원되는 자산과 네트워크를 다룰 수 있는, 잔액이 있는 지갑"이지 Coinbase 거래소 가입이 아니다. `awal`은 Apify가 현재 문서화한 가장 쉬운 경로일 뿐이고, x402 표준 자체는 그보다 넓다.

물론 편의 도구로서의 가치는 있다. 402 challenge를 읽고 서명까지 알아서 처리하므로, 셸 명령을 실행하고 로컬 상태를 유지할 수 있는 코딩 에이전트 런타임과 잘 맞는다고 Apify도 설명한다.

## 한국과 다른 국가에서 걸리는 제약은 프로토콜이 아니라 주변 레이어에 있다

x402 자체에는 국가 제한이 없다. [x402.org](https://www.x402.org/)는 계정 개설이나 개인정보 없이 동작하는 개방형 표준이라고 소개한다. 그런데 이 말이 "어느 나라에서든 아무 문제 없이 쓸 수 있다"는 뜻은 아니다. 제약은 프로토콜을 둘러싼 세 레이어에서 각각 걸린다.

먼저 판매자 레이어. Apify Technologies는 체코 프라하에 등록된 회사이고, [Store 퍼블리싱 약관](https://docs.apify.com/legal/store-publishing-terms-and-conditions)에 따라 수익을 받으려면 만 18세 이상이어야 하며 신원 확인과 KYC를 통과해야 한다. 정부 발급 신분증, 주소 증빙, 세금 서류, 실소유자 정보까지 요구될 수 있다. 제재 대상이거나 감시 목록에 걸리면 지급이 보류되거나 계정이 정지될 수 있다. 이 글을 쓰며 확인한 공식 문서 어디에도 "미국인만 판매 가능" 같은 조항은 없다. 한국 개발자라면 미국 거주 요건이 아니라 신분증, 청구 정보, 세금 서류, 지급 수단 검증을 준비하면 된다. 다만 지급 수단 가용성이나 제재 스크리닝이 나라별로 다르게 작동할 수 있다는 점은 남는다.

다음은 구매자 자금 조달 레이어. Coinbase의 거래소, 온램프, 호스티드 지갑 제품은 국가별로 제공 여부가 다르다. 한국에서 특정 Coinbase 제품을 쓸 수 없다고 해서 x402가 막히는 것은 아니다. 프로토콜이 요구하는 것은 Base USDC를 보낼 수 있는 지갑이고, 그 지갑을 채우는 경로는 여러 가지다. 그래도 프로덕션에서 `awal`에 의존할 계획이라면 해당 제품의 자국 가용성과 이메일 OTP 자동화 가능 여부를 먼저 확인하는 편이 안전하다.

마지막으로 현지 법 레이어. 스테이블코인 취득과 세금 처리, 그리고 Actor가 하는 일 자체(스크래핑 대상 사이트의 약관, 개인정보와 데이터 관련 법)는 나라마다 다르다. 이 부분은 Apify도 Coinbase도 대신 판단해 주지 않는다. CDP 문서의 facilitator 로드맵에 판매자 attestation으로 KYC나 지역 제한을 표현하는 기능이 언급되어 있지만 로드맵일 뿐이고, 현재의 x402가 법적 제약을 프로토콜 차원에서 처리해 주는 것은 아니다.

정리하면 이렇다. 판매는 Apify의 KYC와 정산 규정, 구매 자금은 지갑과 온램프의 국가별 가용성, 활용은 현지 법. 세 레이어를 따로 점검해야 하고, 어느 하나가 막혀도 나머지 경로가 자동으로 막히지는 않는다.

## 판매자는 Apify 수익화와 KYC를 통과해야 한다

판매자 쪽에 별도의 "셀러 계정" 같은 것은 없다. Apify 계정에서 [수익화 설정](https://docs.apify.com/platform/actors/publishing/monetize)을 하면 된다. Console에 청구 정보를 입력하고 Actor의 Publication 메뉴에서 가격 모델을 고른다. 과금 모델은 이벤트 단위로 청구하는 Pay Per Event와 사용량 기반의 Pay Per Usage가 있다.

수익 배분은 [약관 기준](https://docs.apify.com/legal/store-publishing-terms-and-conditions)으로 지원 가격 모델 수수료의 80%인데, 설정에 따라 플랫폼 사용 비용이 차감될 수 있다. 정산은 [월 단위](https://docs.apify.com/platform/actors/publishing/monetize/monthly-payouts)로 돌아간다. 매월 11일에 지급 인보이스가 생성되고 3일의 검토 기간 후 14일에 자동 승인된다. 최소 지급액은 PayPal과 Wise가 20달러, 그 외 수단은 100달러다. PPE Actor의 월 수익이 마이너스면 0으로 처리되어 다른 Actor의 수익을 깎지 않는다.

지급을 받으려면 AML/KYC를 통과해야 한다. 개인은 신분증과 일치하는 실명, 고해상도 신분증 사진이 필요하고 법인은 공식 상호와 사업자 등록 정보를 낸다. 지급 시점까지 검증이 끝나지 않으면 수익은 다음 달로 이월된다. KYC는 일회성이 아니라 계속 유지되는 의무이고, 12개월 연속으로 해결되지 않으면 미지급 잔액이 몰수될 수 있다는 조항도 있다.

에이전트 구매자에게 노출되는 조건은 앞서 본 것과 같다. PPE 과금, 제한된 권한, Standby 미사용. 이 조건을 만족하는 Actor는 `allowsAgenticUsers=true` 플래그가 붙어 자동으로 agentic 검색에 노출된다. 별도 옵트인 절차는 없다. Store API에서도 이 플래그로 필터링해 검색할 수 있다.

흐름 전체를 붙여 보면, 구매자가 x402로 지불한 돈도 판매자에게는 Apify의 일반 정산 경로로 도착한다. 결제가 온체인이라고 해서 정산까지 온체인은 아니다.

## 실무에서 먼저 정해야 할 정책

프로토콜과 지갑이 준비됐다고 바로 돌릴 일은 아니다. 운영 전에 정해야 할 것들이 있다.

- 지갑 잔액은 작게 유지한다. 선불 토큰의 잔액이 절대 상한이고 `awal`에도 지출 한도가 있지만, 한도는 도구가 아니라 운영자가 정하는 정책이다. 14일 만료와 환불 불가를 감안하면 필요한 만큼만 충전하는 편이 맞다.
- 선불 토큰은 API 키와 동일하게 다룬다. 잔액이 남아 있는 동안 그 자체로 결제 능력이므로 로그나 출력에 찍히지 않게 하고 저장 위치를 통제한다.
- 에이전트가 어떤 Actor를 호출할 수 있는지 허용 목록을 정한다. 가변 비용 작업에는 `upto`나 선불 상한이 안전장치가 되지만, 무엇을 사도 되는지는 결국 운영자의 정책 문제다.
- 스크래핑의 법적 리스크를 Actor 단위로 본다. 도구를 사는 행위가 합법이어도 그 도구가 수집하는 데이터는 대상 사이트 약관과 현지 법의 적용을 받는다. Actor를 만드는 쪽도 한계를 문서화하고 대상 서비스의 공식 도구인 것처럼 오인되게 하면 안 된다.
- 자율 운영이라면 이메일 OTP 처리를 설계에 포함한다. `awal` 인증 코드는 이메일로 오기 때문에 받은편지함 접근이 자동화 경로에 들어가야 하고, 그 접근 권한 자체가 또 하나의 보안 표면이 된다.

## 정리

Apify의 x402 통합은 에이전트 결제 논의를 데모에서 상품 규모로 옮겼다. 2만 개 넘는 Actor가 계정 없이 지갑만으로 열린다는 것은, 에이전트의 도구 목록이 배포 시점이 아니라 실행 시점에 결정되는 구조가 실제 마켓플레이스 하나에서 작동하기 시작했다는 뜻이다.

동시에 이 통합은 어디에 마찰이 남는지도 보여준다. 결제 프로토콜은 국경이 없지만 지갑 제품, 온램프, 판매자 KYC, 세금과 스크래핑 법은 국경이 있다. Coinbase 거래소 계정이 필수라는 오해, Apify 판매가 특정 국가 전용이라는 오해 모두 문서 기준으로는 사실이 아니다. 대신 각자의 나라에서 지갑을 어떻게 채울지, 지급 검증을 어떻게 통과할지, 수집한 데이터가 합법인지를 레이어별로 확인해야 한다. 기능 자체가 아직 실험 단계라는 Apify의 표시까지 감안하면, 지금은 소액과 좁은 허용 목록으로 시작하는 것이 합리적인 출발점이다.

## 함께 보면 좋을 자료

- [x402 판매자 quickstart](https://docs.x402.org/getting-started/quickstart-for-sellers): 직접 x402 유료 API를 만들 때의 SDK와 scheme 안내
- [Coinbase Developer Platform x402 문서](https://docs.cdp.coinbase.com/x402/welcome): 프로토콜 구조와 facilitator, 지원 네트워크
- [에이전트 결제 2026년 6월 동향](/blog/agentic-payments-june-2026-x402-ucp-mpp/): x402를 포함한 결제 스택 전반의 최근 변화

## 참고 자료

- [Introducing x402 support: 10x more tools for autonomous agents](https://blog.apify.com/introducing-x402-agentic-payments/), Apify Blog, 조회일 2026-07-05
- [Apify x402 integration docs](https://docs.apify.com/platform/integrations/x402), Apify Docs, 조회일 2026-07-05
- [x402 welcome](https://docs.cdp.coinbase.com/x402/welcome), Coinbase Developer Platform, 조회일 2026-07-05
- [Agentic Wallet CLI](https://docs.cdp.coinbase.com/agentic-wallet/cli/welcome), Coinbase Developer Platform, 조회일 2026-07-05
- [x402.org](https://www.x402.org/), x402 프로젝트 홈, 조회일 2026-07-05
- [Quickstart for sellers](https://docs.x402.org/getting-started/quickstart-for-sellers), x402 Docs, 조회일 2026-07-05
- [Monetize your Actor](https://docs.apify.com/platform/actors/publishing/monetize), Apify Docs, 조회일 2026-07-05
- [Monthly payouts](https://docs.apify.com/platform/actors/publishing/monetize/monthly-payouts), Apify Docs, 조회일 2026-07-05
- [Apify Store Publishing Terms and Conditions](https://docs.apify.com/legal/store-publishing-terms-and-conditions), Apify Legal, 조회일 2026-07-05
