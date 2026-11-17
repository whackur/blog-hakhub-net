---
title: "Orderly란 무엇인가: 여러 DEX가 함께 쓰는 무기한선물 거래 인프라"
meta_title: ""
description: "Orderly의 공유 주문장과 체결·정산 구조, 빌더의 수익 모델, ORDER 토큰, 온체인 무기한선물 시장에서의 위치를 살펴봅니다."
date: 2026-11-17T02:34:00Z
lastmod: 2026-11-17T02:34:00Z
image: "/images/posts/orderly-network-explained/cover.webp"
categories: ["Blockchain"]
tags: ["orderly", "perpetuals", "defi", "orderbook", "trading-infrastructure"]
author: "whackur"
translationKey: "orderly-network-explained"
draft: false
---

Orderly는 여러 팀이 자기 브랜드의 거래 앱을 만들 때 사용하는 **무기한선물 거래 인프라**입니다. 개발팀이 화면과 고객 접점을 맡고 Orderly가 주문 체결과 정산에 필요한 백엔드를 제공합니다. 기본 시장에서는 서로 다른 앱과 체인에서 들어온 주문이 같은 유동성을 이용합니다. 사용자가 접하는 DEX의 이름이 달라도 그 뒤에서 Orderly가 거래를 처리할 수 있습니다. [공식 소개](https://orderly.network/docs/introduction/getting-started/what-is-orderly)가 설명하는 사업 구조입니다.

이 구조는 새 거래소가 겪는 문제를 줄입니다. 화면을 만드는 일과 매수·매도 주문이 충분한 시장을 만드는 일은 다릅니다. Orderly를 쓰는 팀은 체결 엔진을 직접 운영하거나 기본 시장의 유동성을 처음부터 모으는 부담을 덜고 기존 사용자에게 맞는 거래 경험을 만드는 데 집중합니다. 다만 여러 앱이 공통 백엔드를 쓰므로 운영 장애와 보안 의존성도 공유하게 됩니다.

## 무기한선물과 거래 앱의 역할

무기한선물(perpetual futures)은 만기가 없는 파생상품입니다. 자산을 직접 보유하는 대신 가격 변동에 따른 손익을 거래하며 증거금으로 포지션을 유지합니다. 가격을 현물 기준에 가깝게 유지하려고 롱과 숏 사이에 펀딩비를 주고받습니다. 펀딩비는 거래소 수수료와 구분해야 합니다. 레버리지를 쓰면 적은 증거금으로 큰 포지션을 잡지만 손실이 커지면 청산될 수 있습니다. [Orderly의 펀딩비 문서](https://orderly.network/docs/introduction/trade-on-orderly/perpetual-futures/funding-rate)를 보면 거래 가격과 기준 가격의 차이가 펀딩 산정에 반영됩니다.

이런 서비스를 제공하려면 주문 화면 외에도 호가 관리, 체결, 증거금 계산, 청산, 입출금 처리가 필요합니다. Orderly는 이 공통 기능을 API와 SDK로 제공합니다. 직접 개발할 팀은 REST·WebSocket API나 React SDK를 쓰고 빠르게 시작하려는 팀은 Orderly One을 선택할 수 있습니다. 빌더는 자기 브랜드와 화면, 사용자에게 부과할 수수료 정책을 정합니다. [공식 홈페이지](https://orderly.network/)는 Raydium, WOOFi Pro, BTSE DEX 등을 생태계 사례로 소개합니다. 이 목록만으로 각 앱의 현재 거래 활동이나 품질까지 판단할 수는 없습니다.

## 공유 주문장과 온체인 정산은 별도 단계입니다

Orderly는 중앙지정가주문장(CLOB, central limit order book)을 사용합니다. 매수·매도 주문을 가격별로 모아 두고 조건이 맞는 주문끼리 체결하는 방식입니다. 기본 시장의 같은 종목에서는 여러 빌더와 지원 체인의 주문이 공통 주문장에 모입니다. 서로 다른 앱의 사용자가 거래 상대가 될 수 있어, 앱마다 유동성을 따로 확보할 필요가 줄어듭니다. [주문장 설계 문서](https://orderly.network/docs/introduction/trade-on-orderly/trading-basics/orderbook-design)는 이를 체인 간 유동성을 통합하는 구조로 설명합니다.

거래 흐름은 다음과 같습니다.

1. 사용자가 앱에서 주문을 내면 서명된 요청이 Orderly 인프라로 전달됩니다.
2. 요청 서명을 확인하고 오프체인 엔진이 가격·시간 우선순위로 주문을 체결합니다.
3. 사용자는 주문·체결 업데이트를 받습니다.
4. 체결된 거래 데이터를 묶어 Orderly L2의 정산 계층에 기록합니다.

즉, 화면에 체결 결과가 나타나는 시점과 블록체인 정산이 끝나는 시점은 다릅니다. 미체결·취소 주문까지 모두 정산 배치에 들어가는 것도 아닙니다. [주문 처리 문서](https://orderly.network/docs/build-on-omnichain/user-flows/order-management)에 따르면 정산 배치에는 체결 데이터가 들어갑니다.

자금의 위치도 구분해야 합니다. 지원 체인의 Asset Vault가 입출금 자산을 보관하고 별도의 정산 계층이 거래 장부를 관리합니다. 체인 사이의 입출금·잔액 메시지에는 LayerZero가 사용됩니다. 사용자는 지원 체인에서 앱을 이용하지만 내부적으로는 공통 거래·정산 체계에 연결됩니다. 공식 지원 목록에는 Ethereum, Arbitrum, Base 같은 EVM 체인과 Solana가 포함돼 있습니다. 다만 특정 앱이 지원하는 체인과 담보 자산은 따로 확인해야 합니다. [아키텍처](https://orderly.network/docs/build-on-omnichain/building-on-omnichain), [지원 체인](https://orderly.network/docs/introduction/trade-on-orderly/supported-chains)

## 빌더와 거래자가 얻는 이점

빌더에게는 개발과 시장 운영의 부담을 줄이는 효과가 있습니다. 기존 지갑이나 커뮤니티 앱에 선물 거래를 추가할 때 체결 엔진부터 새로 만들 필요가 없습니다. 공통 시장의 주문장을 쓰면서 화면, 거래 도구, 고객 지원, 사용자 확보 방식으로 차별화할 여지도 생깁니다. Orderly가 백엔드를 제공해도 고객을 모으고 제품을 운영하는 일은 빌더에게 남습니다. [공식 소개](https://orderly.network/docs/introduction/getting-started/what-is-orderly)

거래자에게는 익숙한 앱과 체인에서 다른 앱의 주문까지 만날 수 있다는 이점이 있습니다. 주문이 한곳에 모이면 유동성이 분산되는 문제를 줄일 여지가 있습니다. 다만 실제 스프레드와 슬리피지는 종목, 주문 크기, 당시 시장조성자의 호가에 따라 달라집니다. 공유 주문장이라는 구조만으로 모든 주문에 좋은 가격이 보장되지는 않습니다.

**공유 유동성의 범위에는 예외가 있습니다.** Perp Anything은 빌더가 별도 무기한선물 시장을 운영하는 기능입니다. 같은 기초자산이라도 기본 시장과 빌더 시장은 심볼, 주문장, 유동성, 위험 설정이 분리됩니다. Community Listed 시장은 격리 증거금만 사용하며 유동성은 빌더의 시장조성에 달려 있습니다. 보험기금도 빌더가 배정하는 계정 단위로 구분되며 같은 보험기금 계정을 쓰는 시장은 보장 재원을 공유합니다. 따라서 Orderly에 상장됐다는 이유로 기본 시장과 같은 깊이나 보호를 기대하면 안 됩니다. [Perp Anything 문서](https://orderly.network/docs/build-on-omnichain/perp-anything/introduction)는 Orderly가 이 시장을 운영하거나 손실을 보전하지 않는다고 명시합니다.

제품 범위도 선물에만 머물지는 않습니다. 공식 문서에는 라운드별 상승·하락을 거래하는 Orderly Predict도 있습니다. 다만 이 상품은 만기 없는 선물과 구조가 다르므로 같은 상품으로 묶어 이해하면 곤란합니다. [Orderly Predict 개요](https://orderly.network/docs/introduction/trade-on-orderly/orderly-predict/overview)

## 수수료 사업과 ORDER 토큰의 관계

Orderly의 사업 수익과 빌더의 수익, 토큰 보유자의 보상은 별개입니다. 일반적인 taker 거래에서 Orderly는 기본 수수료를 받고 빌더는 사용자에게 부과한 수수료 중 기본 수수료를 넘는 부분을 가져갑니다. Maker 수수료가 양수라면 빌더 수익이 될 수 있지만 음수 수수료로 지급하는 리베이트는 거래자에게 전달되는 혜택입니다. 이를 빌더 매출로 세면 안 됩니다. [수수료 설정 문서](https://orderly.network/docs/build-on-omnichain/user-flows/custom-fees)

ORDER는 스테이킹, 생태계 보상, 거버넌스 참여에 연결되는 토큰입니다. 최대 공급량은 10억 개로 문서화돼 있습니다. 네트워크 이름에 토큰이 붙어 있다고 해서 모든 입출금의 가스비를 ORDER로 내는 것은 아닙니다. 거래·입출금 인프라와 토큰의 보상 설계는 구분해서 볼 필요가 있습니다. [토큰 개요](https://orderly.network/docs/introduction/tokenomics/overview-of-order), [분배·발행 일정](https://orderly.network/docs/introduction/tokenomics/distribution-and-emission-schedule)

현재 보상 구조를 설명할 때는 예전 USDC 분배 방식과 섞지 않아야 합니다. 공식 스테이킹 문서는 2025년 11월 4일 도입한 새 체계에서 순수수료의 30%가 새 재원 풀에 들어가고 epoch 종료 시 ORDER 매입으로 정산된다고 설명합니다. ORDER나 esORDER를 스테이킹하면 양과 기간을 반영하는 양도 불가능한 지표 VALOR가 쌓이고 이를 esORDER 보상으로 교환합니다. 기존 USDC 풀에는 새 수익이 들어오지 않습니다. [스테이킹 문서](https://orderly.network/docs/introduction/tokenomics/order-staking/staking)

별도로 [매입 프로그램 발표](https://orderly.network/blog/buybacks)는 2주마다 순수수료의 **최대 60%**로 ORDER를 매입하고 매입 물량의 절반은 스테이커에게 esORDER로, 절반은 커뮤니티 관리 지갑으로 보낸다고 설명합니다. 커뮤니티 지갑 물량이 전부 자동 소각되는 구조는 아닙니다. esORDER는 유동 ORDER로 전환할 때 베스팅이 필요하며 문서상 90일을 채워야 100% 전환됩니다. [esORDER 문서](https://orderly.network/docs/introduction/tokenomics/esorder)

매입 재원이 있다는 사실만으로 토큰 가격 상승이 보장되지는 않습니다. 거래 활동이 실제 순수수료로 얼마나 남는지, 보상과 유통 물량이 어떻게 변하는지까지 영향을 줍니다. 거래량 증가를 토큰 보유자의 확정 수익으로 바로 연결하기는 어렵습니다.

## 온체인 선물 시장에서의 위치

Orderly는 빌더가 여러 체인의 고객에게 거래 서비스를 제공하도록 돕는 쪽에 초점을 맞춥니다. 경쟁은 다른 선물 거래소뿐 아니라, 그 거래소가 외부 앱에 제공하는 개발 도구와 유동성 접근 기능에서도 일어납니다.

| 서비스      | 구조와 초점                                          | Orderly와 비교할 지점                                   |
| ----------- | ---------------------------------------------------- | ------------------------------------------------------- |
| Orderly     | 여러 앱에 거래 백엔드와 기본 시장의 공유 주문장 제공 | 빌더의 브랜드·수수료 자율성, 지원 체인의 입출금 경험    |
| Hyperliquid | 자체 L1의 HyperCore 주문장과 HyperEVM                | 자체 거래 생태계의 유동성, 외부 앱을 위한 builder codes |
| Lighter     | 주문 처리의 증명과 Ethereum 정산·출금 경로를 강조    | 체결·청산 검증 방식과 운영자 의존성                     |
| dYdX Chain  | Cosmos SDK 기반 체인, 검증자들이 주문장을 유지       | 주문 전파·체결을 담당하는 검증자 구조                   |

각 구조는 [Hyperliquid 소개](https://hyperliquid.gitbook.io/hyperliquid-docs), [builder codes](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/builder-codes), [Lighter 아키텍처](https://docs.lighter.xyz/about-lighter/technical-architecture-lighter-core), [dYdX 아키텍처](https://docs.dydx.xyz/concepts/architecture/overview)에 근거합니다. Hyperliquid도 외부 앱이 주문을 보내고 수수료를 받는 기능을 제공하므로, 빌더 지원 자체가 Orderly만의 독점적 특징은 아닙니다.

Solana의 선물 시장을 비교할 때 자주 등장하는 Drift는 자료의 시점을 주의해야 합니다. 2026년 11월 17일 확인한 [기존 Drift 문서 주소](https://docs.drift.trade/)는 Velocity라는 이름의 선물·대출 프로토콜을 설명합니다. 같은 Solana 프로그램에서 증거금과 대출 자금을 함께 관리하는 모델로, 여러 체인에 거래 백엔드를 공급하는 Orderly와 제품 구성이 다릅니다. 과거 Drift의 구조나 수치가 현재 상태에도 적용된다고 가정해서는 안 됩니다.

### 같은 기간의 수수료로 본 규모

DeFiLlama 공개 API의 일별 데이터를 합산하면 다음과 같습니다. 기간은 **2026년 11월 10~16일 UTC의 7일**, 단위는 USD이며 조회 시각은 **2026년 11월 17일 02:32 UTC 무렵**입니다.

| DeFiLlama 집계 항목 | 7일 수수료 합계 |
| ------------------- | --------------: |
| Orderly Perps       |         $35,634 |
| Hyperliquid Perps   |     $24,642,335 |
| Lighter Perps       |      $1,474,048 |
| dYdX V4             |         $61,098 |

출처는 각각 [Orderly Perps API](https://api.llama.fi/summary/fees/orderly-perps?dataType=dailyFees), [Hyperliquid Perps API](https://api.llama.fi/summary/fees/hyperliquid-perps?dataType=dailyFees), [Lighter Perps API](https://api.llama.fi/summary/fees/lighter-perps?dataType=dailyFees), [dYdX V4 API](https://api.llama.fi/summary/fees/dydx-v4?dataType=dailyFees)입니다. Hyperliquid 항목에는 암호자산·HIP-3 선물과 빌더 수수료 외에 스테이블코인 준비금 수익 배분도 포함됩니다. 따라서 같은 기간이어도 집계 대상이 완전히 같지는 않습니다. 이 표는 수익 활동의 규모를 참고하는 자료이며 순수 거래 수수료만의 비교나 시장점유율 표가 아닙니다.

이 관측에서는 Orderly의 수수료 규모가 Hyperliquid와 Lighter보다 작습니다. 이를 공유 인프라 모델의 실패나 특정 앱의 품질로 해석할 근거는 부족합니다. 무료 거래 정책, 리베이트, 상품 구성에 따라 수수료와 거래량의 관계가 달라지기 때문입니다. Orderly의 특성은 앱들이 같은 백엔드에 거래를 모으는 데 있고 그 전략의 성과는 실제 유동성과 고객 유지로 확인해야 합니다.

거래량은 기간 중 거래한 계약의 명목금액, 미결제약정(OI)은 아직 닫히지 않은 포지션 규모, TVL은 예치·잠긴 자산 규모를 뜻합니다. 어느 것도 수수료와 같지 않습니다. 특히 Orderly 전체 거래량에 이를 사용하는 프런트엔드의 거래량을 다시 더하면 같은 거래를 중복 계산할 수 있습니다. 표의 집계 범위에는 하위 앱이나 체인 가스비 항목이 포함되지 않습니다.

## 비수탁 구조에도 운영자와 브리지 위험은 남습니다

오프체인 체결은 빠른 응답에 유리하지만 Orderly 운영 인프라가 주문 내용을 보고 처리합니다. 공식 문서가 말하는 MEV 보호도 체결 전 공개 블록체인 mempool을 이용한 선행매매 방지에 범위가 한정됩니다. 운영자가 주문을 보지 못한다거나 모든 형태의 MEV가 사라진다는 뜻은 아닙니다. [주문장 설계 문서](https://orderly.network/docs/introduction/trade-on-orderly/trading-basics/orderbook-design)

자금을 온체인 Vault에 맡기는 방식도 운영자와 무관한 상시 출금을 보장하지는 않습니다. 표준 출금 흐름에는 지갑 서명과 API 요청 처리, 체인 간 메시지 전달이 들어갑니다. [출금 문서](https://orderly.network/docs/build-on-omnichain/user-flows/withdrawal-deposit)와 [보안 문서](https://orderly.network/docs/introduction/security)를 보면 입출금 경로와 멀티시그 업그레이드 권한을 함께 살펴봐야 합니다. 감사 이력은 참고 자료이지 장애나 자산 손실이 없다는 보증은 아닙니다.

정산 계층의 보안도 별도로 확인할 부분입니다. [L2BEAT의 Orderly 평가](https://l2beat.com/scaling/projects/orderly)는 허가된 운영자의 상태 갱신, 즉시 업그레이드, 제안자 장애 때의 출금 중단 위험을 지적합니다. 데이터 가용성은 Celestia를 사용하는 구조로 분류합니다. 반면 앞서 연결한 공식 주문장 문서는 배치 데이터를 Ethereum에 게시한다고 설명합니다. 이 설명 차이만으로 실제 배포 설정을 확정하기는 어려우므로, Ethereum의 보안이 모든 거래·출금에 그대로 적용된다고 가정해서는 안 됩니다.

공유 인프라를 쓰면 빌더마다 같은 기능을 반복해서 만드는 비용을 줄입니다. 동시에 공통 엔진이나 메시징 경로의 장애가 여러 앱에 영향을 줄 가능성도 생깁니다. Orderly를 이해할 때는 화면의 브랜드와 함께 어떤 주문장, 정산 체계, 자금 보관 경로를 사용하는지 보는 편이 정확합니다.

## 함께 보면 좋을 자료

- [Orderly 빌더 온보딩](https://orderly.network/docs/introduction/getting-started/builder-onboarding): 앱 운영자 등록과 통합 경로.
- [Perp Anything](https://orderly.network/docs/build-on-omnichain/perp-anything/introduction): 기본 시장과 빌더 운영 시장의 책임·위험 차이.
- [Lighter 아키텍처](https://docs.lighter.xyz/about-lighter/technical-architecture-lighter-core): 증명과 비상 출금 경로를 중심으로 한 다른 설계.

## 참고 자료

자료 확인일은 2026년 11월 17일입니다. 문서의 기능 설명과 실제 앱별 제공 범위는 다를 수 있습니다.

- [Orderly 홈페이지](https://orderly.network/), [공식 소개](https://orderly.network/docs/introduction/getting-started/what-is-orderly), [아키텍처](https://orderly.network/docs/build-on-omnichain/building-on-omnichain), [지원 체인](https://orderly.network/docs/introduction/trade-on-orderly/supported-chains).
- [주문장 설계](https://orderly.network/docs/introduction/trade-on-orderly/trading-basics/orderbook-design), [주문 처리](https://orderly.network/docs/build-on-omnichain/user-flows/order-management), [입출금](https://orderly.network/docs/build-on-omnichain/user-flows/withdrawal-deposit), [보안](https://orderly.network/docs/introduction/security), [펀딩비](https://orderly.network/docs/introduction/trade-on-orderly/perpetual-futures/funding-rate).
- [수수료 설정](https://orderly.network/docs/build-on-omnichain/user-flows/custom-fees), [ORDER 개요](https://orderly.network/docs/introduction/tokenomics/overview-of-order), [분배·발행 일정](https://orderly.network/docs/introduction/tokenomics/distribution-and-emission-schedule), [스테이킹](https://orderly.network/docs/introduction/tokenomics/order-staking/staking), [esORDER](https://orderly.network/docs/introduction/tokenomics/esorder), [매입 프로그램 발표](https://orderly.network/blog/buybacks).
- [Perp Anything](https://orderly.network/docs/build-on-omnichain/perp-anything/introduction), [Orderly Predict](https://orderly.network/docs/introduction/trade-on-orderly/orderly-predict/overview), [L2BEAT](https://l2beat.com/scaling/projects/orderly).
- [Hyperliquid](https://hyperliquid.gitbook.io/hyperliquid-docs), [builder codes](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/builder-codes), [Lighter](https://docs.lighter.xyz/about-lighter/technical-architecture-lighter-core), [dYdX](https://docs.dydx.xyz/concepts/architecture/overview), [Drift 문서 주소의 현재 내용](https://docs.drift.trade/).
- DeFiLlama 공개 수수료 API: [Orderly](https://api.llama.fi/summary/fees/orderly-perps?dataType=dailyFees), [Hyperliquid](https://api.llama.fi/summary/fees/hyperliquid-perps?dataType=dailyFees), [Lighter](https://api.llama.fi/summary/fees/lighter-perps?dataType=dailyFees), [dYdX](https://api.llama.fi/summary/fees/dydx-v4?dataType=dailyFees).
