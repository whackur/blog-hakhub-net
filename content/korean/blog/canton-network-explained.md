---
title: "Canton Network 이해하기: 금융 프라이버시와 원자적 결제, 기관 도입 현황"
meta_title: "Canton Network 구조와 기관 도입 현황 (2026년 10월)"
description: "Daml 계약, 선택적 정보 공유, Global Synchronizer와 Canton Coin의 역할을 설명하고 DTCC·Tradeweb·MUFG 등 기관 발표의 실제 진행 단계를 구분합니다."
date: 2026-10-15T09:00:00+09:00
lastmod: 2026-10-15T09:00:00+09:00
image: "/images/posts/canton-network-explained/cover.png"
categories: ["Blockchain"]
tags: ["canton", "daml", "tokenization", "institutional-finance", "privacy", "settlement"]
author: "whackur"
translationKey: "canton-network-explained"
draft: false
---

증권을 산다는 행위에는 여러 원장이 관여합니다. 거래소나 거래 플랫폼에는 체결 기록이 남고, 수탁기관에는 증권 보유 기록이 남습니다. 지급을 담당하는 은행은 현금 장부를 따로 관리합니다. 서로 다른 기관이 같은 거래를 각자의 시스템에 기록하므로, 거래 후에는 금액과 권리, 처리 상태를 다시 맞추는 대사 작업이 필요합니다. 모든 기관이 하나의 공개 장부를 사용하면 단순해 보이지만 고객 잔액과 거래 전략까지 공개할 수는 없습니다.

Canton은 이 문제에서 출발한 분산원장 프로토콜입니다. **계약에 관여하는 주체끼리 필요한 상태를 공유하고, 여러 애플리케이션의 상태 변경을 하나의 거래로 묶는 것**이 설계의 중심입니다. 참여자 모두에게 금융 데이터를 방송하는 대신 계약 권한에 따라 정보를 나눕니다. 그 위에 연결된 애플리케이션과 운영 인프라의 생태계가 Canton Network입니다. [프로토콜 명세](https://docs.canton.network/overview/reference/canton-protocol-specification)가 이 구분의 출발점입니다.

이 글은 먼저 계약과 합의 구조를 설명한 다음 기관 도입 현황을 살펴봅니다. 현황 확인 기준일은 **2026년 10월 15일 KST**입니다. 공식 문서와 아래에 연결한 기관 발표를 확인했으며, 모든 기관의 비공개 거래 원장이나 실시간 운영 상태를 조사한 결과는 아닙니다. 거래 완료, 제품 지원, 개념검증(PoC), 출시 계획을 구별해서 읽어야 실제 진척을 판단할 수 있습니다.

## 금융기관이 공유해야 하는 상태

매수자가 돈을 지급했는데 증권을 받지 못하거나, 매도자가 증권을 넘겼는데 돈을 받지 못하면 결제 위험이 발생합니다. 증권 인도와 대금 지급을 연결하는 DvP(Delivery versus Payment)는 이 위험을 줄이는 방식입니다. Canton에서는 적절히 모델링한 증권 계약과 현금 계약을 같은 Daml 트랜잭션에서 소비하고 새 보유 계약을 만드는 방식으로 두 상태 변경을 결합합니다. [공식 DvP 예제](https://docs.canton.network/overview/reference/cross-sync-dvp-example)는 이 조합을 구체적으로 설명합니다.

공유 범위는 업무마다 다릅니다. 증권 등록기관은 증권 소유권 변경을 알아야 하지만 매수자의 전체 현금 잔액까지 알 필요는 없습니다. 지급 은행도 거래 상대방의 모든 증권 포트폴리오를 볼 이유가 없습니다. Canton은 거래 전체를 무조건 복제하지 않고 관련 하위 거래의 정보를 필요한 participant에 전달합니다. 이는 단순히 화면에서 민감한 열을 숨기는 방식과 다릅니다. [프라이버시 모델](https://docs.canton.network/overview/learn/privacy-model)을 계약 설계와 함께 읽어야 하는 이유입니다.

대사가 모두 사라지는 것은 아닙니다. 원장 안에서 공유하는 계약 상태는 일치시킬 수 있지만, 외부 은행 처리나 수탁 장부, 기업행사, 가격 데이터는 연결해야 합니다. 토큰이 나타내는 권리의 법적 근거도 별도로 존재합니다. 기술의 효과를 평가하려면 어떤 기록을 공동으로 관리하고 어떤 기록은 외부 시스템에 남기는지 먼저 정해야 합니다. 단순히 블록체인을 도입했다는 사실만으로 업무의 모든 경계가 없어지지는 않습니다.

## Daml에서 Canton Coin까지의 역할

Canton 관련 자료에는 언어, 프로토콜, 네트워크, 토큰이 함께 등장합니다. 다음 구분을 잡아 두면 기관 발표도 읽기 쉬워집니다. [Splice 아키텍처](https://docs.canton.network/sdks-tools/api-reference/splice-architecture)는 공통 인프라 위에서 동작하는 운영 애플리케이션을 설명합니다.

| 이름 | 담당하는 역할 |
| --- | --- |
| Daml | 계약 데이터, 행위, 권한을 기술하는 스마트컨트랙트 언어입니다. 컴파일된 실행 표현은 Daml-LF입니다. |
| Canton Protocol | 계약의 분산 검증, 선택적 정보 공유, 순서와 결과 조정, 계약 이동을 정의합니다. |
| Canton Network | Canton 기반 애플리케이션, 참여기관, 동기화 인프라가 연결된 생태계입니다. |
| Synchronizer | 연결된 participant 사이에서 메시지 순서와 거래 결과를 조정하는 서비스입니다. |
| Global Synchronizer(GS) | 생태계가 공동으로 사용하는 공개 동기화 인프라입니다. 전용 Synchronizer도 존재할 수 있습니다. |
| Splice | GS 거버넌스, Canton Coin, validator 운영 등에 필요한 애플리케이션을 구현합니다. |
| Canton Coin(CC) | GS traffic 구매와 네트워크 기여 보상에 연결된 유틸리티 토큰입니다. |

Canton 소프트웨어로 기관 전용 환경을 운영하는 일과 공개 GS에 연결하는 일은 구별해야 합니다. 어떤 기관이 Daml 애플리케이션을 사용한다는 사실만으로 모든 거래가 GS를 거치거나 같은 양의 CC를 소비한다고 계산할 수 없습니다. 특정 금융 상품의 자산 규모도 네트워크 사용료와 직접 대응하지 않습니다. 연결된 생태계라는 표현은 모든 기관이 같은 데이터베이스나 동일한 운영 정책을 사용한다는 뜻이 아닙니다.

역사에도 세 기준점이 있습니다. [2020년 2월 4일자 백서](https://www.canton.io/publications/canton-whitepaper.pdf)는 이미 Daml 기반 원장 상호운용 프로토콜을 설명합니다. Digital Asset과 참여기관이 [Canton Network를 발표한 날짜](https://blog.digitalasset.com/press-release/new-global-blockchain-network-of-networks-for-financial-market-participants-and-institutional-assets)는 2023년 5월 9일입니다. [GS와 CC의 가동 발표](https://www.prnewswire.com/news-releases/the-canton-networks-global-synchronizer-and-canton-coin-go-live-302186479.html)는 2024년 7월 1일에 나왔습니다. 언어와 프로토콜의 역사, 기관 네트워크 발표, 공개 공통 인프라의 가동은 각각 다른 사건입니다.

## 계약의 생성과 소비로 표현하는 업무

Daml의 계약 인스턴스는 생성된 뒤 내용을 직접 덮어쓰지 않습니다. 보유자가 바뀌면 기존 계약을 소비하고 새로운 보유자를 나타내는 계약을 만듭니다. 이를 UTXO와 연결해 설명하기도 하지만 Bitcoin의 결제 스크립트와 동일한 모델은 아닙니다. Daml은 금융 자산뿐 아니라 거래 제안, 수탁 위임, 담보 요청처럼 여러 주체의 권한이 얽힌 업무도 계약으로 표현합니다. [상세 원장 모델](https://docs.canton.network/overview/reference/ledger-model-detailed)이 상태 변경과 권한을 정의합니다.

`template`은 계약 데이터와 규칙의 정의이고, 실제 계약 인스턴스에는 고유한 식별자가 붙습니다. `choice`는 그 계약에서 수행할 업무 행위입니다. 기본적인 consuming choice가 성공하면 입력 계약은 더 이상 소비할 수 없습니다. 새 계약이 만들어졌다면 애플리케이션은 새 식별자를 추적해야 합니다. `nonconsuming` choice는 원 계약을 남기지만 다른 계약을 만들거나 소비하는 업무를 포함할 수 있습니다. 이름만 보고 아무 상태도 바꾸지 않는 조회라고 해석하면 안 됩니다. [Daml 언어 참조](https://docs.canton.network/appdev/reference/daml-language-reference)를 기준으로 구별할 수 있습니다.

권한을 나타내는 주요 역할은 다음과 같습니다.

| 역할 | 의미 |
| --- | --- |
| `signatory` | 계약 생성에 필요한 권한을 제공하는 주체입니다. |
| `controller` | 특정 choice를 실행할 권한을 가진 주체입니다. |
| `observer` | 계약 정보를 볼 수 있는 추가 주체입니다. 관찰 권한만으로 choice 실행 권한을 얻지는 않습니다. |

예를 들어 A가 거래 제안을 만들고 B가 이를 수락하는 업무를 생각할 수 있습니다. A의 제안 계약에 B를 관찰자로 두고, B가 실행하는 수락 choice에서 양측 권한을 결합해 최종 계약을 생성합니다. 제안을 소비하면 같은 제안을 다시 수락하는 문제도 막습니다. 이 설명은 권한 모델의 예시이며 증권 발행이나 은행 지급을 구현한 완성된 금융 계약은 아닙니다.

로그인, API 권한, 계약 권한도 다른 층입니다. 웹 서비스에 로그인했다고 모든 party의 명령을 제출할 수 있는 것은 아닙니다. API의 `actAs`와 `readAs`, 계약의 controller와 observer, 실제 서명 주체가 각각 맞아야 합니다. 계약 식별자를 알고 있다는 사실도 실행 권한을 대신하지 않습니다. 따라서 코드 리뷰에서는 화면에 표시한 사용자가 누구인지와 원장이 인정하는 권한 주체가 누구인지를 함께 확인해야 합니다. [보안 지침](https://docs.canton.network/appdev/modules/m7-security)은 애플리케이션과 원장의 경계를 다룹니다.

## Party와 participant, Super Validator

Party는 원장에서 계약 주체와 권한을 나타내는 식별자입니다. 사람, 법인, 업무 시스템에 대응시킬 수 있지만 Ethereum 주소나 은행 고객번호와 자동으로 같아지지는 않습니다. Participant는 party를 호스팅하고 계약 데이터를 보관하며 명령을 실행·검증하는 노드입니다. 하나의 participant가 여러 party를 호스팅할 수 있습니다. Party의 호스팅과 확인 정책에 여러 participant가 관여하는 구성도 가능합니다. [Smart Contract Consensus](https://docs.canton.network/overview/reference/smart-contract-consensus)는 이 관계를 설명합니다.

Validator라는 말은 운영 배포 단위를 가리킬 때가 많습니다. Participant와 Splice validator 애플리케이션, 사용자 관리, traffic 관리 등이 함께 묶일 수 있습니다. Super Validator(SV)는 공개 GS의 sequencing, mediation, 거버넌스에 참여하는 별도 역할입니다. 일반 사용자의 participant와 SV를 같은 종류의 전역 실행 검증자로 생각하면 프라이버시 구조를 이해하기 어렵습니다. SV들은 공동으로 호스팅하는 DSO(Decentralized Synchronizer Operator) party를 기반으로 운영 변경을 조정합니다. [거버넌스 문서](https://docs.canton.network/overview/reference/sv-governance-reference)는 이 공동 운영 절차를 설명합니다. SV에 참여한 기업의 이름이 늘었다고 그 기업의 모든 금융 서비스가 Canton에서 운영된다고 판단할 수도 없습니다.

![Canton의 party가 각 participant를 이용하고, participant가 계약 정보를 보관·검증하며, 공통 Synchronizer의 sequencer와 mediator가 암호화된 메시지의 순서와 결과를 조정하는 구조](/images/posts/canton-network-explained/architecture.svg)

직접 작성한 개념도입니다. [프로토콜 명세](https://docs.canton.network/overview/reference/canton-protocol-specification)와 [ordering 설명](https://docs.canton.network/overview/reference/ordering-consensus)을 바탕으로 구성했습니다. 화살표는 논리적인 메시지 왕복이며 participant와 mediator 사이의 프로토콜 메시지도 sequencer를 거칩니다. 실제 거래의 발행자·수탁기관과 상세 topology는 생략했습니다. [원본 SVG 크게 보기](/images/posts/canton-network-explained/architecture.svg)

## 실행 확인과 순서 합의

Canton은 거래 실행의 유효성 확인과 메시지 순서 합의를 분리합니다. 관련 participant는 자신에게 허용된 거래 view를 받아 계약 활성 상태, 권한, 실행 결과 등 필요한 조건을 검증합니다. Synchronizer의 sequencer는 메시지에 순서를 부여하고 전달합니다. Mediator는 요구되는 확인을 모아 승인, 거부, 시간초과 결과를 정합니다. 금융 payload를 읽는 전역 실행자가 이 모든 일을 대신하는 구조가 아닙니다. [실행 확인](https://docs.canton.network/overview/reference/smart-contract-consensus)과 [순서 합의](https://docs.canton.network/overview/reference/ordering-consensus)를 나눠 읽어야 합니다.

Proof of Stakeholder의 stakeholder는 계약의 이해관계자를 뜻합니다. **CC 보유량에 비례해 금융 계약을 검증하는 일반적인 Proof of Stake와 다릅니다.** 필요한 확인 주체와 threshold는 프로토콜 정책과 호스팅 topology에 따라 정해집니다. 모든 observer가 거래 때마다 지갑을 열어 수동 서명한다는 의미도 아닙니다. 사용자의 외부 서명과 participant가 보내는 프로토콜 확인은 서로 다른 절차입니다.

거래를 제출하면 제출 participant가 명령을 해석하고 관련 계약과 party, 패키지, 동기화 경로를 확인합니다. 필요한 view를 암호화해 보내면 수신 participant가 검증하고 확인을 회신합니다. 조정 결과가 전달된 뒤 승인된 변경을 각 participant의 가시성 범위에 반영합니다. 순서는 각 Synchronizer의 범위에서 정해집니다. 네트워크 전체가 언제나 하나의 공개 블록 순서와 완전한 금융 상태를 공유한다고 설명하면 맞지 않습니다.

이 분리는 운영 책임도 나눕니다. Participant 운영자는 데이터와 실행 환경을 관리하고, Synchronizer 운영자는 메시지 전달과 순서, 조정 서비스의 가용성을 담당합니다. 전용 Synchronizer가 한 운영자에게 의존하는지, GS 같은 공동 운영 인프라를 사용하는지는 신뢰 판단에 영향을 줍니다. 운영자가 분산되어 있다는 설명만으로 개별 배포의 장애 허용 조건을 알 수는 없습니다. 실제 구성과 정책을 확인해야 합니다.

## 선택적 정보 공유의 효과와 경계

Canton의 프라이버시는 계약 권한, 선택적 복제, 암호화된 메시지 전달에 기반합니다. 거래를 여러 view로 나누므로 관계없는 participant가 모든 입력과 출력을 받아 실행할 필요가 없습니다. 다만 자신의 party를 호스팅하는 participant는 해당 데이터를 처리합니다. 외부 서명 키를 하드웨어 지갑에 보관하더라도 호스팅 운영자가 처리하는 계약 데이터까지 자동으로 가려지지는 않습니다. [외부 party 설명](https://docs.canton.network/overview/reference/external-party)은 서명과 호스팅의 구별을 이해하는 데 도움이 됩니다.

Observer는 필드별 마스킹 기능이 아닙니다. 어떤 계약의 observer로 지정한 상대에게 UI에서 금액을 숨겼다고 원장 수준의 접근 권한이 줄어들지는 않습니다. 요약 정보만 공유하려면 민감 데이터와 보고용 계약을 나누는 설계가 필요합니다. `fetch`, 명시적인 계약 공개, 다른 계약과의 조합도 정보 노출 범위에 영향을 줍니다. [원장 모델](https://docs.canton.network/overview/reference/ledger-model-detailed)의 가시성 규칙과 실제 API 결과를 함께 살펴야 합니다.

Synchronizer가 금융 내용을 복호화하지 않더라도 메시지 시간, 크기, 수신자 같은 메타데이터는 별도 문제입니다. 거래 상대방이 이미 받은 정보를 회수할 수도 없습니다. 운영자의 데이터 접근, 로그와 백업, 규제 보고 범위 역시 설계해야 합니다. 이 때문에 선택적 공개를 완전한 익명성이나 자동 개인정보 규정 준수로 표현해서는 안 됩니다. 감독기관의 접근도 해당 기관이 필요한 권한을 갖도록 구성해야 합니다. [프라이버시 문서](https://docs.canton.network/overview/learn/privacy-model)는 업무별 공유 정책과 함께 읽을 자료입니다.

## 하나의 DvP가 완성되는 조건

매수자 Alice의 현금 계약은 Payments Synchronizer에 있고 매도자 Bob의 증권 계약은 Securities Synchronizer에 있다고 가정하겠습니다. 둘을 교환하려면 필요한 계약을 공통 결제 Synchronizer에서 사용할 수 있어야 합니다. **하나의 Daml 트랜잭션의 모든 입력 계약은 같은 Synchronizer에 배정되어야 합니다.** 서로 다른 곳에 그대로 둔 채 임의의 두 거래를 동시에 실행하는 설명과는 차이가 있습니다. [Multi-Synchronizer 아키텍처](https://docs.canton.network/overview/learn/multi-synchronizer)와 [DvP 예제](https://docs.canton.network/overview/reference/cross-sync-dvp-example)가 이 조건을 명시합니다.

1. 매수자, 매도자, 지급 은행, 증권 등록기관 등 필요한 주체가 사용할 공통 Synchronizer를 고릅니다. 관련 participant의 연결, party hosting, 패키지 vetting과 자산 정책이 맞아야 합니다.
2. 다른 Synchronizer에 있는 계약은 reassignment로 옮깁니다. 원래 위치에서 unassign한 뒤 대상에 assign합니다. 이동 중인 계약을 두 위치에서 동시에 소비할 수는 없습니다.
3. 거래 조건과 일치하는 현금·증권 입력 또는 allocation을 준비합니다. 자산 종류, 수량, 상대방, 실행 주체와 기한을 확인합니다.
4. 공통 Synchronizer에서 한 Daml 트랜잭션으로 양쪽 입력을 소비하고 새 현금·증권 계약을 만듭니다. 요구 조건을 충족하지 못하면 그 트랜잭션의 두 leg가 함께 실패합니다.
5. 실제 완료 결과를 확인합니다. 업무상 필요하면 결과 계약을 다시 다른 Synchronizer로 옮깁니다.

Reassignment는 준비 과정의 일부입니다. Unassign은 됐는데 assign이 끝나지 않았다면 계약을 잠시 업무에 사용하지 못할 수 있습니다. 자산 발행자가 공통 Synchronizer 사용을 허용하지 않거나 필요한 패키지가 준비되지 않은 경우도 있습니다. 모든 Canton 자산이 이름만으로 즉시 조합되는 것은 아닙니다. 업무 트랜잭션의 원자성과 준비·이동 절차 전체의 즉시 완료는 별개입니다.

원자성의 범위도 분명해야 합니다. 한 트랜잭션 안의 계약 변경을 함께 성공시키는 성질은 은행 지급의 법적 확정성, 수탁기관 장부의 권리 이전, 발행자의 상환 능력까지 대신하지 않습니다. 토큰이 외부 기록을 표현한다면 그 기록과 토큰의 관계가 중요합니다. 외부 블록체인으로의 이동도 별도 프로토콜과 신뢰 조건을 갖습니다. Canton 내부 DvP의 설명을 임의의 외부 체인 전체에 대한 원자성 보장으로 확장하면 안 됩니다.

## 전형적인 공개 EVM 모델과의 차이

다음은 기본 실행 방식의 비교입니다. 개별 EVM 체인의 프라이버시 확장이나 특수한 운영 모델을 모두 포괄하지 않습니다. [Canton의 Ethereum 개발자용 설명](https://docs.canton.network/appdev/modules/m2-canton-for-ethereum-devs)을 기준으로 읽을 수 있습니다.

| 항목 | 전형적인 공개 EVM | Canton의 Daml 실행 모델 |
| --- | --- | --- |
| 상태 변경 | 계정과 컨트랙트 storage를 갱신합니다. | 계약 인스턴스를 생성·소비합니다. |
| 권한 | 함수 코드와 접근제어 로직으로 표현합니다. | signatory, controller, observer가 모델에 포함됩니다. |
| 데이터 | 공개 상태와 이벤트를 널리 복제합니다. | 관련 participant에 필요한 view를 전달합니다. |
| 검증 | 체인의 실행·블록 합의 구조를 따릅니다. | 실행 확인과 동기화 서비스의 순서를 분리합니다. |
| 개발 접점 | Solidity, ABI, Ethereum JSON-RPC가 대표적입니다. | Daml, Ledger API, 토큰·지갑 표준을 사용합니다. |

Canton의 native Daml 환경은 EVM 호환 실행 환경이 아닙니다. Solidity 계약을 그대로 배포하거나 Ethereum RPC를 같은 의미로 호출한다고 가정할 수 없습니다. 별도의 EVM 연동 환경이나 middleware를 다루는 제안·제품이 있어도 그것을 native 실행 모델 전체와 동일시해서는 안 됩니다. 기존 도구를 가져오려면 지원하는 환경과 자산, 권한, 배포 상태를 구체적으로 확인해야 합니다.

접근 권한도 층별로 다릅니다. 공개 코드를 읽고 로컬 앱을 만드는 일, 운영 네트워크의 validator를 신청하는 일, 특정 증권을 매매하는 일은 같은 허가가 아닙니다. [공식 FAQ](https://www.canton.network/faq)는 validator 요청에 현재 sponsor가 필요하다고 설명하고 앱별 permission을 구분합니다. 증권의 KYC, 고객 자격, 양도 제한은 상품과 운영기관이 정합니다. 공개 네트워크라는 표현이 모든 금융 자산의 무제한 접근권을 뜻하지는 않습니다.

## 지갑과 자산을 연결하는 표준

자산마다 서로 다른 Daml template과 choice를 제공하면 지갑과 거래 앱이 매번 별도 통합을 해야 합니다. Canton Token Standard는 자산의 내부 구현을 유지하면서 보유 조회, 이전, 결제용 자산 할당 같은 공통 접점을 제공합니다. 자산을 운영하는 registry, 지갑·수탁 시스템, 거래·정산 앱 사이의 약속입니다. 모든 자산의 법적 권리나 발행 정책을 같은 것으로 만드는 규칙은 아닙니다. [CIP-0056](https://github.com/canton-foundation/cips/blob/main/cip-0056/cip-0056.md)이 V1의 기준입니다.

단순 이전인 FOP(Free of Payment)는 대가 leg를 같은 이전에 결합하지 않는다는 뜻입니다. 수수료가 없다는 뜻은 아닙니다. DvP에서는 특정 거래 조건을 위해 자산을 allocation한 다음 여러 leg를 결합합니다. 지갑은 요청된 자산과 수량, 실행 주체, 기한을 사용자에게 보여주고 승인해야 합니다. 표준을 지원한다는 표시 하나만으로 모든 자산의 수신 승인이나 상환 조건이 같다고 볼 수 없습니다.

V2인 [CIP-0112](https://github.com/canton-foundation/cips/blob/main/cip-0112/cip-0112.md)는 다층 수탁 계정, 가시성을 조정하는 배치 정산, 자금 할당과 재사용 등을 확장합니다. 기관 수탁자가 고객별 귀속을 관리하거나 거래소가 여러 거래를 함께 정산할 때 필요한 기능입니다. 2026년 10월 15일 확인한 원문 헤더에서 V1은 `Final`, V2는 `Approved`입니다. V2 승인일은 2026년 6월 12일입니다. 이를 모든 메인넷 지갑과 자산의 V2 지원 완료로 읽을 수는 없습니다.

[구버전과 혼합해서 사용하는 통합](https://github.com/canton-foundation/cips/blob/main/cip-0112/cip-0112.md)에서는 지원 기능을 확인해야 합니다. 예를 들어 반복 정산 권한을 이해하지 못하는 지갑이 한 번의 송금처럼 표시하면 사용자가 승인하는 범위가 달라집니다. 지원하지 않는 조건은 안전하게 거부하고 실제 서명 대상과 화면을 맞춰야 합니다. 표준이 지향하는 호환성과 개별 제품의 지원 수준은 따로 검증할 대상입니다.

지갑과 dApp을 연결하는 [CIP-0103](https://github.com/canton-foundation/cips/blob/main/cip-0103/cip-0103.md)은 자산 표준과 또 다른 층입니다. 계정과 네트워크 확인, 거래 준비·서명·실행 등의 접점을 표준화합니다. 원문 상태는 `Active`, 승인일은 2026년 1월 29일입니다. 앱이 특정 노드나 키 관리 제품에 고정되지 않도록 돕지만 지갑의 보안이나 사용자 심사를 대신하지는 않습니다. 외부 서명에서도 준비된 거래 내용과 해시를 검증하고 원장 완료를 확인해야 합니다. [서명 가이드](https://docs.canton.network/sdks-tools/sdks/wallet-sdk/guides/preparing-and-signing-a-transaction)가 이 절차를 설명합니다.

운영 버전은 이 표준 세대와 별개입니다. 10월 14일 갱신된 대시보드의 MainNet 조합은 Canton 3.5.19와 Splice 0.8.4를 제시합니다. 반면 [Canton 최신 릴리스](https://github.com/digital-asset/canton/releases/tag/v3.6.1)는 10월 5일 공개된 3.6.1입니다. 이는 공식 문서의 조합과 릴리스 메타데이터를 대조한 결과이며 모든 운영 노드를 직접 조회한 값은 아닙니다. [공식 호환성 대시보드](https://docs.canton.network/shared/version-compatibility-dashboard)에서 환경별 조합을 확인하고, 바이너리의 최신 릴리스를 실제 MainNet 배포와 구분해야 합니다. 패키지 번호가 올라갔다고 모든 V2 기능이 켜졌다고 판단하거나 DevNet의 기능을 운영 환경에서 바로 사용할 수 있다고 가정하면 통합 오류가 생깁니다.

## Canton Coin과 금융 거래의 현금 leg

CC는 GS traffic 구매와 기여 보상에 연결됩니다. Traffic을 구매하면 CC가 소각되고, 정해진 조건에 맞는 운영자와 애플리케이션 기여에는 보상이 발행됩니다. Burn과 mint는 서로 다른 흐름입니다. 거래 자산의 명목 금액이 크다고 같은 비율로 CC가 소각되는 구조라고 계산할 수는 없습니다. [GS tokenomics](https://docs.canton.network/overview/reference/tokenomics-of-gs)가 가격과 보상, traffic의 관계를 설명합니다.

네트워크 사용 비용과 자산 이전 비용도 구별해야 합니다. [CIP-0078](https://github.com/canton-foundation/cips/blob/main/cip-0078/cip-0078.md)의 CC 수수료 제거는 GS traffic이나 수탁 서비스, 다른 토큰 registry의 모든 비용이 무료라는 선언이 아닙니다. 사용자가 비용을 직접 내지 않는 화면에서도 앱이나 운영자가 traffic을 부담할 수 있습니다. 보상 역시 자격과 정책에 따르므로 단순 계약 생성량만으로 수익을 추정해서는 안 됩니다.

금융 거래의 현금 leg에는 다른 자산을 사용할 수 있습니다. Circle은 [2025년 12월 4일 USDCx 가용화](https://www.circle.com/blog/usdcx-on-canton-now-available-via-circle-xreserve)를 발표했습니다. Ethereum의 xReserve에 USDC를 예치하면 Canton의 분산 프로토콜이 USDCx 발행을 시작하는 구조입니다. USDCx는 USDC로 뒷받침되는 프로토콜 토큰이며 Circle이 직접 발행하는 USDC와 같은 토큰이라고 표현하면 부정확합니다. 발행과 상환 경로를 확인해야 합니다.

USDCx로 증권 대금을 결제하는 행위와 CC로 GS traffic을 구매하는 행위는 다릅니다. 기관의 담보·결제 사용이 늘어나는 것, GS 사용이 늘어나는 것, CC의 순소각이 늘어나는 것, 시장 가격이 오르는 것은 각각 별도 주장입니다. 공급과 보상, 사용량과 유동성 자료 없이 이를 한 줄로 연결할 근거는 없습니다. 이 글에서 다루는 것은 기술과 확인 가능한 도입 단계입니다.

## 기관 도입 현황

아래 표의 단계는 발표 주체가 확인한 범위입니다. 제공업체의 발표를 개별 거래 원장, 수탁 기록, 실제 고객 배포의 독립 검증으로 취급하지 않았습니다. 자료에 등장하는 기관 전체를 같은 운영 단계로 묶지 않기 위해 사건별로 분리했습니다.

| 발표일 | 기관·사건 | 확인한 단계와 범위 |
| --- | --- | --- |
| 2026-10-05 | [Ripple Custody 1.43](https://docs.ripple.com/products/custody/support/change-history/v143) | 제품 지원. CC와 CIP-56 토큰 보유·이전, 외부 validator 연결을 지원합니다. 온프레미스 및 하이브리드 방식의 SaaS에서 제공하며, ledger accounting refactor phase 2가 필요합니다. 이 릴리스의 Canton 관리는 API 중심입니다. 고객별 실제 운영 규모는 제시하지 않습니다. |
| 2026-09-28 | [LSEG Super Validator 임명](https://www.lseg.com/en/media-centre/press-releases/2026/lseg-appointed-as-a-super-validator-on-canton-network) | 인프라·거버넌스 참여. DiSH cash를 이용한 repo는 발표에서 PoC로 구분합니다. |
| 2026-08-27 | [Virtu·M1X·Tradeweb repo](https://www.tradeweb.com/newsroom/media-center/in-the-news/first-fully-onchain-repo-transaction-completed-using-sovereign-digital-bond) | 완료 거래 발표. Sovereign digital bond인 USDM1을 담보로 실행·환매 cycle을 수행했습니다. |
| 2026-08-19 | [Ledger의 Canton 지원](https://www.ledger.com/blog-canton-coin-on-ledger-wallet) | CC 제품 지원. 제품 본문은 다른 privacy-enabled assets를 후속 지원 대상으로 설명합니다. |
| 2026-08-13 | [MUFG 등의 JGB repo](https://www.mufg.jp/dam/pressrelease/2026/pdf/news-20260813-002_en.pdf) | PoC 개시. 장부대체 국채와 블록체인을 연결하는 검증입니다. 상용 repo 시장 전체의 가동 발표는 아닙니다. |
| 2026-07-15 | [DTCC의 DTC-tokenized assets 거래](https://www.dtcc.com/press-releases/2026/dtcc-turns-tokenization-into-reality) | Production 거래 완료 발표. Canton과 DTCC의 private Besu에서 수행했습니다. 일반 서비스 출시는 10월 계획으로 별도 설명합니다. |
| 2026-07-01 | [Tradeweb 미국 국채 거래](https://www.tradeweb.com/newsroom/media-center/news-releases/tradeweb-facilitates-landmark-on-chain-u.s.-treasuries-transaction-on-the-canton-network) | 완료 거래 발표. Franklin Templeton이 매도하고 Virtu가 매수했으며 USDCx를 대금으로 사용했습니다. |
| 2026-02-25 | [Chainlink 데이터 서비스](https://www.prnewswire.com/news-releases/chainlink-now-live-on-canton-accelerating-institutional-grade-tokenization-at-scale-302696344.html) | Data Streams·SmartData·Proof of Reserve 가동 발표. CCIP의 Canton 가동은 당시 향후 계획입니다. |
| 2025-12-04 | [Circle xReserve와 USDCx](https://www.circle.com/blog/usdcx-on-canton-now-available-via-circle-xreserve) | 출시와 live 거래 발표. USDC 예치와 프로토콜 USDCx 발행을 연결합니다. |
| 2025-06-26 | [Nasdaq Calypso·QCP 등](https://ir.nasdaq.com/news-releases/news-release-details/nasdaq-and-qcp-set-new-standard-capital-efficiency-connecting) | Margin·collateral 업무 연결 시연. Nasdaq 주식시장 전체가 Canton으로 이전했다는 발표는 아닙니다. |

DTCC의 7월 발표는 실제 production 거래라는 점에서 단순 시연과 구분됩니다. 그러나 이를 10월 서비스의 정식 출시 완료로 바꾸어 쓰면 진행 단계를 앞당기게 됩니다. 10월 15일 확인한 [Canton의 DTCC 준비 페이지](https://www.canton.network/dtcc-tokenization-service-on-canton)는 여전히 10월 출시에 대비한 기술 준비를 안내했습니다. 확인한 DTCC 공식 발표와 해당 준비 페이지에서는 전면 출시 완료를 확인하지 못했습니다. 이는 그 범위에서의 관찰이며 모든 공식 채널을 실시간으로 전수 확인했다는 뜻은 아닙니다.

Tradeweb의 두 거래는 자산 구조도 다릅니다. 7월 사례는 미국 국채와 USDCx의 결제를 다뤘고, 8월 사례는 미국 국채로 담보된 Marshall Islands의 디지털 국채 USDM1을 repo 담보로 사용했습니다. USDM1을 미국 정부가 직접 발행한 국채나 스테이블코인으로 바꾸어 설명하면 안 됩니다. 개별 거래 완료는 기술과 업무 연결의 증거지만 반복 거래량, 고객 확대, 유동성은 추가로 확인해야 합니다.

MUFG 사례는 기존 장부대체 국채의 법적 성질을 유지하면서 온체인 repo 업무를 검증하는 PoC입니다. 관련 [Secured Finance 발표](https://blog.digitalasset.com/press-release/secured-finance-to-provide-lending-protocol-for-mitsubishi-ufj-trust-and-bankings-proof-of-concept-for-on-chain-japanese-government-bond-jgb-repo-transactions)도 프로토콜 제공 역할을 설명합니다. 계약과 담보 이동을 블록체인으로 옮기는 일과 법적 소유 기록 전체를 대체하는 일이 다를 수 있음을 보여주는 사례입니다.

수탁과 운영 인프라의 변화는 거래 뉴스와 다른 의미를 갖습니다. Ripple 지원은 기관의 기존 승인 정책과 Canton 자산 관리를 연결하는 제품 기능입니다. Ledger 지원은 CC를 하드웨어 서명으로 관리하는 접근 경로를 넓힙니다. LSEG의 SV 임명은 공통 인프라와 거버넌스 역할을 확대합니다. 어느 경우든 제품 지원이나 직책만으로 전체 고객의 실자산 사용량을 산출할 수는 없습니다.

Chainlink도 데이터와 외부 연결을 나눠 봐야 합니다. [공식 Data Streams 변경 기록](https://docs.chain.link/changelog/data-streams-expands-to-canton)은 Canton 확장을 확인해 줍니다. 이후의 [2026년 9월 28일 CCIP 2.0 발표](https://chain.link/blog/introducing-ccip-2-0) 자체는 Canton의 지원 개시를 명시하지 않습니다. 확인한 자료에서는 이를 Canton CCIP 가동 증거로 삼지 않았습니다. 오라클 데이터 가용성, 개별 앱 사용, 외부 체인 전송은 각각 확인해야 할 기능입니다.

## 공개 논의와 숫자를 읽는 기준

공개 토론에서는 기관 활용에 대한 기대와 네트워크 접근·통제에 대한 의문이 함께 나타납니다. [Reddit의 atomicity·privacy 토론](https://www.reddit.com/r/defi/comments/1s69u2y/chains_with_atomicity_privacy_features/)에는 Canton의 permissioning을 문제 삼는 의견이 있습니다. 이 짧은 토론을 사용자 전체의 평가나 성능 검증으로 일반화할 수는 없습니다. 다만 공개 인프라, validator 가입, 상품 접근을 구분해서 설명해야 한다는 독자의 질문을 보여줍니다.

개발자 관점에서는 [공식 포럼](https://forum.canton.network/top)에 participant별 조회, 수탁 계정, reassignment, 패키지 호환성 같은 질문이 올라옵니다. 연결 가능한 표준과 프라이버시는 개발의 출발점이고, 실제 통합에서는 권한과 가시성, 장애 복구를 구체적으로 맞춰야 한다는 점을 읽을 수 있습니다. 포럼 질문의 존재를 현재 버전의 확정된 결함으로 취급하거나, 반대로 제공업체 설명을 독립적인 실사용 평가로 취급하지는 않았습니다.

큰 숫자일수록 단위를 확인해야 합니다. DTCC가 소개하는 2025년 **114조 달러**는 예탁 자회사의 custody·asset servicing 배경 규모입니다. Canton TVL이나 이미 토큰화한 금액이 아닙니다. Repo의 일간·월간 명목 처리액도 반복해서 거래된 흐름입니다. 같은 담보가 여러 번 사용될 수 있으므로 특정 시점에 묶인 자산 재고와 비교할 수 없습니다. 기관 전체의 고객 자산이나 거래 플랫폼 전체의 처리량을 Canton에 예치된 자산으로 합산하면 규모를 과장하게 됩니다. [DTCC 원문](https://www.dtcc.com/press-releases/2026/dtcc-turns-tokenization-into-reality)의 수치가 설명하는 대상을 유지해야 합니다.

Canton을 평가할 때 남는 질문은 구체적입니다. 어떤 자산과 현금이 같은 거래에서 움직였는지, 어떤 기관이 필요한 정보를 보았는지, 실제로 어느 Synchronizer를 사용했는지 확인해야 합니다. 반복 운영 여부와 상환·법적 권리도 따로 봐야 합니다. 공식 발표에서 확인되는 진척은 담보와 결제 업무의 연결, 수탁 접점, 공동 인프라 참여입니다. 이 진척을 이해하려면 코인 가격보다 계약과 운영 경계를 먼저 읽는 편이 정확합니다.

## 함께 보면 좋을 자료

- [Canton Protocol Specification](https://docs.canton.network/overview/reference/canton-protocol-specification): 계약 view와 확인 절차를 더 자세히 설명합니다.
- [Cross-Synchronizer DvP Example](https://docs.canton.network/overview/reference/cross-sync-dvp-example): 계약 이동과 공통 결제 지점의 조건을 따라갈 수 있습니다.
- [Canton Token Standard](https://docs.sync.global/app_dev/token_standard/index.html): 자산 registry와 지갑, 정산 앱 사이의 연동을 다룹니다.

## 참고 자료

모든 웹 자료의 확인일은 2026년 10월 15일입니다. 날짜를 적은 기관 발표는 해당 발표일 기준이며, 본문의 완료·PoC·지원·계획 구분을 적용했습니다.

- [2020 Canton 백서](https://www.canton.io/publications/canton-whitepaper.pdf), [2023 Network 발표](https://blog.digitalasset.com/press-release/new-global-blockchain-network-of-networks-for-financial-market-participants-and-institutional-assets), [2024 GS·CC 가동](https://www.prnewswire.com/news-releases/the-canton-networks-global-synchronizer-and-canton-coin-go-live-302186479.html).
- [Splice 아키텍처](https://docs.canton.network/sdks-tools/api-reference/splice-architecture), [원장 모델](https://docs.canton.network/overview/reference/ledger-model-detailed), [Daml 언어](https://docs.canton.network/appdev/reference/daml-language-reference), [보안 지침](https://docs.canton.network/appdev/modules/m7-security).
- [Smart Contract Consensus](https://docs.canton.network/overview/reference/smart-contract-consensus), [Ordering Consensus](https://docs.canton.network/overview/reference/ordering-consensus), [프라이버시](https://docs.canton.network/overview/learn/privacy-model), [Multi-Synchronizer](https://docs.canton.network/overview/learn/multi-synchronizer).
- [Ethereum 개발자용 설명](https://docs.canton.network/appdev/modules/m2-canton-for-ethereum-devs), [외부 party](https://docs.canton.network/overview/reference/external-party), [서명 절차](https://docs.canton.network/sdks-tools/sdks/wallet-sdk/guides/preparing-and-signing-a-transaction), [FAQ](https://www.canton.network/faq), [버전 대시보드](https://docs.canton.network/shared/version-compatibility-dashboard).
- [CIP-0056](https://github.com/canton-foundation/cips/blob/main/cip-0056/cip-0056.md), [CIP-0112](https://github.com/canton-foundation/cips/blob/main/cip-0112/cip-0112.md), [CIP-0103](https://github.com/canton-foundation/cips/blob/main/cip-0103/cip-0103.md), [CIP-0078](https://github.com/canton-foundation/cips/blob/main/cip-0078/cip-0078.md), [GS tokenomics](https://docs.canton.network/overview/reference/tokenomics-of-gs), [SV 거버넌스](https://docs.canton.network/overview/reference/sv-governance-reference), [Canton 3.6.1 릴리스](https://github.com/digital-asset/canton/releases/tag/v3.6.1).
- [DTCC production 거래](https://www.dtcc.com/press-releases/2026/dtcc-turns-tokenization-into-reality), [DTCC 연결 준비](https://www.canton.network/dtcc-tokenization-service-on-canton), [Tradeweb 국채 거래](https://www.tradeweb.com/newsroom/media-center/news-releases/tradeweb-facilitates-landmark-on-chain-u.s.-treasuries-transaction-on-the-canton-network), [Tradeweb repo](https://www.tradeweb.com/newsroom/media-center/in-the-news/first-fully-onchain-repo-transaction-completed-using-sovereign-digital-bond).
- [MUFG PoC](https://www.mufg.jp/dam/pressrelease/2026/pdf/news-20260813-002_en.pdf), [Secured Finance 역할](https://blog.digitalasset.com/press-release/secured-finance-to-provide-lending-protocol-for-mitsubishi-ufj-trust-and-bankings-proof-of-concept-for-on-chain-japanese-government-bond-jgb-repo-transactions), [Circle USDCx](https://www.circle.com/blog/usdcx-on-canton-now-available-via-circle-xreserve).
- [Ripple Custody 1.43](https://docs.ripple.com/products/custody/support/change-history/v143), [Ledger 지원](https://www.ledger.com/blog-canton-coin-on-ledger-wallet), [LSEG SV 임명](https://www.lseg.com/en/media-centre/press-releases/2026/lseg-appointed-as-a-super-validator-on-canton-network), [Nasdaq Calypso](https://ir.nasdaq.com/news-releases/news-release-details/nasdaq-and-qcp-set-new-standard-capital-efficiency-connecting).
- [Chainlink 공동 발표](https://www.prnewswire.com/news-releases/chainlink-now-live-on-canton-accelerating-institutional-grade-tokenization-at-scale-302696344.html), [Data Streams 변경 기록](https://docs.chain.link/changelog/data-streams-expands-to-canton), [CCIP 2.0](https://chain.link/blog/introducing-ccip-2-0).
- [Canton 개발자 포럼](https://forum.canton.network/top), [Reddit의 privacy·atomicity 토론](https://www.reddit.com/r/defi/comments/1s69u2y/chains_with_atomicity_privacy_features/). 의견과 질문의 출처이며 프로토콜 검증 자료는 아닙니다.
