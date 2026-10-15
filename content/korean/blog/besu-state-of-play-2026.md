---
title: "Besu 이해하기: 이더리움 실행부터 은행의 토큰 결제까지"
meta_title: "Besu 설명 가이드: EVM, 실행 클라이언트, 허가형 네트워크와 프로젝트 한강"
description: "Java 기반 이더리움 실행 클라이언트 Besu가 거래와 상태를 처리하는 원리, 메인넷과 허가형 네트워크의 차이, 한국은행 프로젝트 한강 사례와 최근 기술 동향을 설명합니다."
date: 2026-10-15T11:37:00+09:00
lastmod: 2026-10-15T12:03:15+00:00
image: "/images/posts/besu-state-of-play-2026/execution-settlement-cover-20261015.webp"
categories: ["Blockchain"]
tags: ["besu", "ethereum", "execution-client", "qbft", "enterprise-blockchain"]
author: "whackur"
translationKey: "besu-state-of-play-2026"
draft: false
---

**Besu는 스마트 계약을 실행하고 그 결과를 검증·저장하는 Java 기반 Ethereum 클라이언트입니다.** 은행은 이 소프트웨어로 예금 토큰과 은행 간 결제 자산을 함께 처리하는 원장을 구성할 수 있습니다. Ethereum 메인넷의 실행 노드로도 쓰입니다. 어느 쪽이든 실행 기술은 공유하지만, 돈의 발행자와 원장을 확정하는 주체는 네트워크마다 달라집니다. [Besu 공식 문서](https://docs.besu-eth.org/)

은행의 Besu 도입을 이해할 때 핵심은 **어떤 잔액을 바꾸며, 누가 그 변화를 승인하는지**입니다. 한국은행 프로젝트 한강의 1단계 결과보고서는 Besu와 QBFT, ERC-20 준수 계약의 실제 사용을 명시합니다. 그 위에서 일반인은 은행의 예금 토큰을 사용하고 은행끼리는 중앙은행 화폐로 결제했습니다. Ethereum 기술이 금융에 연결되는 구체적인 지점입니다. [한국은행 1단계 보고서, 부록 42~44쪽](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216)

## 은행은 고객의 예금과 은행 간 결제를 함께 처리합니다

은행 A의 고객이 은행 B의 고객에게 1만 원을 지급한다고 가정하겠습니다. 예금 토큰은 발행 은행에 대한 예금 청구권을 원장 위에 표현합니다. A의 토큰을 그대로 넘기면 수취인은 A에 대한 청구권을 갖게 됩니다. 수취인이 자신의 거래 은행 B에 대한 예금으로 받는 구조라면, A와 B 사이의 결제도 필요합니다. 한국은행이 한강에서 채택한 burn-and-issue는 송금 은행의 토큰을 소각하고 수취 은행의 토큰을 발행하면서 그 사이를 중앙은행 화폐로 결제하는 방식입니다. [1단계 보고서, 부록 43쪽](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216)

아래는 이 원리를 1만 원 지급으로 단순화한 예입니다. 충분한 잔액과 발행 권한이 있고 수수료는 없다고 가정합니다. 실제 한강의 계약 호출이나 회계 분개를 재현한 표는 아닙니다.

| 바뀌는 기록 | 지급에 따른 변화 | 의미 |
| --- | --- | --- |
| A 고객의 A 예금 토큰 | 1만 원 감소 | A가 고객에게 진 예금 채무 감소 |
| A의 기관용 결제 자산 | 1만 원 감소 | A가 은행 간 결제 대금 지급 |
| B의 기관용 결제 자산 | 1만 원 증가 | B가 결제 대금 수취 |
| B 고객의 B 예금 토큰 | 1만 원 증가 | B가 수취 고객에게 진 예금 채무 증가 |

같은 원장에 이 자산들이 있으면 스마트 계약으로 변경을 한 거래에 묶을 수 있습니다. 중간 단계가 실패할 때 전체 거래를 취소하도록 만들면, 송금인의 토큰만 줄고 수취인의 토큰은 늘지 않는 부분 지급을 막습니다. 이것이 원자적 결제의 의미입니다. 한강 보고서도 은행 간 지급의 세 단계를 모두 성공해야 완료되도록 설계했다고 설명합니다. 같은 은행 고객 사이에서는 소각·재발행과 은행 간 결제 없이 직접 토큰을 옮겼습니다. [1단계 보고서, 부록 43~44쪽](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216)

이 장점은 계약이 통제하는 상태 안에서 성립합니다. 계약 실행에 연계해 애플리케이션이 외부 은행 시스템에 보낸 요청이나 이미 배송된 물건까지 EVM이 되돌리지는 못합니다. 외부 자산과 연결할 때는 어느 시스템의 기록을 완료로 인정할지 별도의 절차가 필요합니다.

## Besu는 서명된 요청을 상태 변화로 재현합니다

이 지급을 처리하려면 거래의 뜻을 코드로 정해야 합니다. Solidity로 작성한 계약은 컴파일된 바이트코드로 배포됩니다. **Ethereum Virtual Machine(EVM)**은 그 바이트코드를 실행하는 규칙과 환경입니다. 계약의 조건을 검사하고 storage를 읽거나 쓰며, 작업량을 gas로 계산합니다. [Ethereum EVM 설명](https://ethereum.org/en/developers/docs/evm/), [Solidity 컴파일러](https://docs.soliditylang.org/en/latest/using-the-compiler.html)

Besu는 EVM을 포함하는 노드 소프트웨어입니다. 거래 수신, 다른 노드와의 통신, 실행 결과의 검증과 디스크 저장, 애플리케이션의 JSON-RPC 요청 처리를 맡습니다. Geth와 Nethermind도 이 층위의 실행 클라이언트입니다. 네트워크는 이 노드들이 같은 규칙 아래 공유하는 원장입니다. Besu로 메인넷에 참여할 수도 있고 별도 genesis에서 은행용 체인을 시작할 수도 있으므로, Besu라는 제품명만으로 어느 돈과 원장을 다루는지 알 수는 없습니다. [Besu 소개](https://docs.besu-eth.org/), [Ethereum 노드와 클라이언트](https://ethereum.org/en/developers/docs/nodes-and-clients/)

### 토큰 10개를 보내면 바뀌는 것

실행 과정을 좁혀서, 일반적인 ERC-20 계약에서 Alice가 Bob에게 토큰 10개를 보내는 예를 보겠습니다. 전송 수수료나 추가 제한이 없는 계약을 가정하며, 10은 소수 자릿수를 반영해 사람이 읽는 수량입니다. 앞의 은행 간 지급에는 별도의 소각·발행·권한 처리가 필요합니다.

1. **지갑이 토큰 계약을 호출하는 거래를 만듭니다.** 목적지 `to`는 Bob이 아니라 계약 주소이고, 호출 데이터에 `transfer(Bob, amount)`가 들어갑니다. 기본 통화 전송액인 `value`와 토큰 수량은 다른 값입니다. ERC-20 잔액은 토큰 계약의 storage로 관리하며 계정의 기본 통화 잔액과 구별합니다. [ERC-20](https://eips.ethereum.org/EIPS/eip-20), [Ethereum 계정](https://ethereum.org/en/developers/docs/accounts/)
2. **서명자가 요청을 승인하고 노드에 제출합니다.** 거래에는 계정의 거래 순서를 나타내는 nonce와 gas 한도 등이 포함됩니다. 서명된 거래를 `eth_sendRawTransaction`으로 Besu에 보낼 수 있습니다. 반환된 거래 해시는 식별자이며 아직 지급 완료의 증거는 아닙니다. [거래 구조](https://ethereum.org/en/developers/docs/transactions/), [JSON-RPC](https://ethereum.org/en/developers/docs/apis/json-rpc/#eth_sendrawtransaction)
3. **블록에 포함된 거래를 실행합니다.** 가정한 계약에서 Alice의 잔액이 100, Bob의 잔액이 0이었다면 성공 후에는 90과 10이 됩니다. 계약은 `Transfer` 이벤트도 남깁니다. 잔액 부족 등의 조건으로 실행이 revert되면 해당 호출의 상태 변경은 취소됩니다. 블록에 포함된 실패 거래에도 실행 gas 비용은 발생할 수 있습니다. [ERC-20](https://eips.ethereum.org/EIPS/eip-20), [Ethereum 거래](https://ethereum.org/en/developers/docs/transactions/)
4. **애플리케이션이 실행 결과와 확정을 확인합니다.** receipt의 status와 로그를 읽고 계약이 의도한 상태가 됐는지 확인합니다. ERC-20은 `false`를 반환하는 구현도 허용하므로 receipt 성공만으로 모든 토큰의 전송 성공을 단정할 수 없습니다. 그 거래를 담은 블록이 네트워크 규칙에 따라 확정됐는지도 따로 확인합니다. [Receipt API](https://ethereum.org/en/developers/docs/apis/json-rpc/#eth_gettransactionreceipt), [ERC-20의 반환값 규칙](https://eips.ethereum.org/EIPS/eip-20)

다른 노드들은 정해진 블록의 거래 순서와 실행 규칙에 따라 결과를 검증합니다. 상태 루트(state root)는 실행 후 계정·저장소 상태를 암호학적으로 요약한 값입니다. 계약에 적힌 잔액 계산을 함께 재현한다는 뜻이며, 그 토큰의 발행 은행이 실제 상환할 능력이 있는지까지 증명하는 값은 아닙니다. [EVM의 상태 전이](https://ethereum.org/en/developers/docs/evm/)

### 병렬 실행은 충돌 없는 계산 결과를 재사용합니다

이 구조를 알면 최근 Besu의 성능 개발도 구체적으로 읽힙니다. Besu의 낙관적 병렬 실행은 거래들을 백그라운드에서 미리 계산하고, 정해진 순서로 처리하면서 앞선 거래와 충돌하지 않는 결과를 재사용합니다. 충돌하면 다시 실행하고, 미리 계산이 끝나지 않았으면 순차 실행합니다. 처리 순서가 바뀌어 잔액이 달라지는 최적화는 아닙니다. 같은 계정이나 공통 유동성 상태에 접근하는 업무에서는 재실행이 늘 수 있으므로 일반 송금의 성능을 은행 결제망 전체의 TPS로 옮겨 쓸 수 없습니다. [Besu 병렬 실행 문서](https://docs.besu-eth.org/public-networks/concepts/parallel-transaction-execution)

결과를 얼마나 오래 조회할지도 별도 문제입니다. 기본 저장 형식인 Bonsai는 현재·최근 상태 접근에 맞춰져 있습니다. 지금 잔액을 읽는 서비스와 수년 전 시점의 계약 상태를 재현하는 서비스는 보관 요구가 다릅니다. 최신 블록을 검증하는 노드가 모든 과거 상태 질의까지 제공한다고 가정하면 감사 시스템의 요구를 놓치게 됩니다. [저장 형식 문서](https://docs.besu-eth.org/public-networks/concepts/data-storage-formats)

## 검증자는 공유할 블록과 신뢰 구조를 결정합니다

계산 결과가 맞는지와 어느 블록을 공동 원장으로 받아들일지는 연결돼 있지만 서로 다른 일입니다. Ethereum 메인넷에서 Besu는 실행 계층을 맡습니다. Teku 같은 합의 클라이언트와 인증된 Engine API로 연결하고, 합의 계층은 지분증명(Proof of Stake, PoS) 규칙으로 체인을 추적합니다. 블록 제안·투표에 참여하는 validator 기능은 일반 노드 운영에 추가하는 역할입니다. Besu 실행만으로 스테이킹 구성이 완성되지는 않습니다. [Besu·Teku 메인넷 구성](https://docs.besu-eth.org/public-networks/tutorials/besu-teku-mainnet)

은행들이 별도 망을 만들 때는 승인된 validator들이 합의하도록 구성할 수 있습니다. Besu 문서가 권장하는 **Quorum Byzantine Fault Tolerance(QBFT)**는 이런 권위증명(Proof of Authority, PoA) 프로토콜입니다. 정해진 validator들이 번갈아 블록을 제안하고 필요한 다수의 서명을 모아 확정합니다. 이 경로에 메인넷용 beacon 합의 클라이언트를 붙일 필요는 없습니다. [QBFT 문서](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft)

| 판단할 항목 | Ethereum 메인넷의 Besu 노드 | 별도 QBFT 네트워크 |
| --- | --- | --- |
| 실행하는 거래 | 메인넷 상태와 계약의 거래 | 그 망에 배포한 계약의 거래 |
| 합의 참여 구조 | 별도 합의 클라이언트와 PoS validator 체계 | 승인된 QBFT validator 집합 |
| 신뢰할 운영 주체 | Ethereum의 공개 프로토콜과 validator 체계 | validator 선정·변경 권한을 정한 기관들 |
| 자산과 수수료 | 메인넷 자산, ETH로 내는 실행 수수료 | 자체 발행·상환 규칙, 별도로 정하는 gas 가격 |

QBFT도 참여 조건을 충족해야 진행됩니다. 공식 문서는 validator의 3분의 1을 넘게 잃으면 블록 생성이 멈춘다고 경고합니다. 네 validator 구성에서 세 대가 협력하는 상황과 두 대가 동시에 빠진 상황은 다릅니다. 네 서버를 한 회사가 같은 관리 계정으로 운영한다면 기관 네 곳이 독립적으로 검증하는 것과도 신뢰 구조가 다릅니다. [QBFT의 장애 조건](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft)

자체 망은 gas 가격을 0으로 정할 수 있습니다. 고객이 수수료용 코인을 구입하지 않게 할 수 있지만, 거래와 블록의 gas 한도 및 서버 자원 비용은 남습니다. 토큰으로 표시한 원화 금액과 계약 실행에 필요한 계산량은 서로 다른 단위입니다. [Free gas 구성](https://docs.besu-eth.org/private-networks/how-to/configure/free-gas)

### 클라이언트 버전과 네트워크 적용 시점도 다릅니다

**2026년 10월 15일 확인한 최신 정식 릴리스는 26.9.0이며, UTC 기준 9월 25일 공개됐습니다.** 이 릴리스는 보안 수정을 포함하고 Sepolia의 Amsterdam 실행 계층 업그레이드 일정을 반영합니다. Ethereum Foundation의 Glamsterdam 공지도 Sepolia와 메인넷 일정을 구분하며, 확인 시점의 공지에서 메인넷 일정은 미정입니다. 특정 규칙을 구현한 Besu가 출시됐다는 사실만으로 모든 네트워크에 그 규칙이 적용됐다고 볼 수 없습니다. [공식 릴리스](https://github.com/besu-eth/besu/releases/tag/26.9.0), [Ethereum Foundation 공지](https://blog.ethereum.org/en/2026/09/17/glamsterdam-testnet-announcement)

계약 이식에도 같은 구분이 필요합니다. Solidity의 `evmVersion`은 대상 체인이 활성화한 실행 규칙과 맞춰야 합니다. 같은 코드를 별도 망에 배포해도 원래 계약의 잔액이나 담보, 오라클과 유동성이 따라오지는 않습니다. Besu가 제공하는 코드·도구 호환성과 다른 원장의 자산을 연결하는 작업은 별도입니다. [Solidity의 EVM 대상 설정](https://docs.soliditylang.org/en/latest/using-the-compiler.html#setting-the-evm-version-to-target)

## 한강은 중앙은행 결제로 서로 다른 은행의 토큰을 연결했습니다

한국은행의 **2025년 12월 1단계 결과보고서**는 DCS(Digital Currency System)를 Besu 기반 허가형 원장으로 설명합니다. 부록 42쪽은 QBFT 합의와 ERC-20을 준수하는 digital money 계약, 중앙은행과 은행의 권한을 나누는 역할 기반 접근 통제를 명시합니다. 이는 해당 실험의 구현 근거입니다. ERC-20을 사용했다는 사실이 익명 참여나 Ethereum 메인넷 결제를 뜻하지는 않습니다. [1단계 보고서](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216)

실거래 실험은 **2025년 4월 1일부터 6월 30일**까지 진행됐습니다. 한국은행 연구진의 ECB Forum 2026 논문은 일곱 은행, 약 8만 명과 약 1만 2천 가맹점의 참여를 기록합니다. 이용자가 예금을 토큰으로 바꿔 지급하고 은행 간에는 기관용 중앙은행 화폐로 결제하는 구조입니다. Besu 사용 은행 일곱 곳이 각각 독립적인 상용 체인을 운영했다는 의미는 아닙니다. [한강 논문, 3.2절·16쪽](https://www.ecb.europa.eu/pub/pdf/sintra/ecb.forumcentbankpub2026_Shin_paper.sk.pdf)

이 논문은 중앙은행을 원장 확정의 권위 있는 주체로 설명합니다. 앞의 QBFT 일반론만 보고 은행들이 중앙은행과 동등한 권한을 갖는다고 추정할 수는 없습니다. 합의 알고리즘의 이름과 참여 기관의 제도적 권한은 함께 확인해야 합니다. [한강 논문, 2.1절·4~6쪽](https://www.ecb.europa.eu/pub/pdf/sintra/ecb.forumcentbankpub2026_Shin_paper.sk.pdf)

실험에서 드러난 제약은 원장 바깥의 연결이었습니다. 논문에 기록된 DCS와 기존 한은금융망 BOK-Wire+는 직접 실시간 연결되지 않았고, 사전에 기관용 결제 유동성을 확보한 뒤 오프라인으로 잔액을 대사했습니다. 원장 안의 원자적 결제가 기존 중앙은행 계좌 시스템과의 상시 자동 연결까지 완성했다는 뜻은 아닙니다. [한강 논문, 3.1~3.2절·14~17쪽](https://www.ecb.europa.eu/pub/pdf/sintra/ecb.forumcentbankpub2026_Shin_paper.sk.pdf)

2026년에는 사용 범위를 넓히는 단계가 진행됐습니다. 한국은행의 **10월 8일 설명**에 따르면 전기차 중속 충전시설 보조금 사업은 진행 중이며, 일반인 대상 후속 실거래는 연내 재개를 준비 중입니다. 완료한 1단계 실험, 진행 중인 보조금 사업, 앞으로 재개할 일반인 실거래를 구분해서 볼 필요가 있습니다. 이 자료만으로 2026년 전체 망의 노드 구성이나 Besu 버전까지 확인되지는 않습니다. [한국은행 10월 8일 자료](https://www.bok.or.kr/portal/bbs/B0000347/view.do?nttId=11065408&menuNo=201106)

## 은행은 발행 권한과 데이터 공개 범위를 따로 설계합니다

블록을 검증할 권한과 예금 토큰을 발행할 권한은 별개입니다. validator가 유효한 실행인지 검사하더라도, 발행 요청을 허용할 계정과 한도는 계약과 업무 규칙으로 정해야 합니다. 고객 확인, 상환, 결제 유동성과 분쟁 처리도 기관의 책임으로 남습니다. 한강이 역할 기반 계약 권한을 별도로 둔 이유를 이 구분에서 이해할 수 있습니다. [1단계 보고서, 부록 42~44쪽](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216)

Permissioning은 노드 접속이나 거래 제출을 허용할 대상을 정합니다. Besu의 로컬 allowlist는 각 노드에 적용합니다. 이 기능만으로 실행에 참여하는 기관 사이에서 거래 금액이나 계약 상태까지 숨겨지는 것은 아닙니다. **참여 허가와 데이터 비공개는 다른 요구사항**입니다. 현재 기능을 볼 때는 Tessera privacy와 기존 onchain node/account permissioning이 25.6.0에서 제거됐다는 점도 중요합니다. 옛 튜토리얼의 privacy 기능을 그대로 도입 근거로 삼을 수는 없습니다. [로컬 permissioning](https://docs.besu-eth.org/private-networks/how-to/use-local-permissioning), [25.6.0 릴리스](https://github.com/besu-eth/besu/releases/tag/25.6.0)

한강의 1단계 보고서는 지급에 필요한 지갑 주소·금액·시각 등의 원장 기록과 추가 신원·자금세탁방지 정보를 구분하고, 후자는 off-chain 메시지 채널로 교환했다고 설명합니다. 은행의 키 관리 시스템과 기존 전산 연결도 별도 구성요소였습니다. 이는 Besu 밖에서 개인정보와 서명·업무 연동을 설계한 실제 예이며, 모든 거래 정보가 암호학적으로 은폐된다는 보장은 아닙니다. Besu 자체도 클라이언트 내부의 사용자 키 관리를 제공하지 않습니다. [1단계 보고서, 부록 44~46쪽](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216), [Besu의 키 관리 범위](https://docs.besu-eth.org/)

Besu의 도입 이유는 여러 기관의 자산과 지급 조건을 같은 실행 환경에 올리고 결과를 함께 검증하려는 필요에서 찾을 수 있습니다. 그 필요가 없다면 기존 데이터베이스와 업무 연계 방식도 비교 대상입니다. 한강 사례에서 얻을 수 있는 구체적인 판단 기준은 분명합니다. EVM 호환 계약을 실행할 원장, 그 원장을 확정할 기관, 원장 위 돈을 발행·상환할 기관을 구분해야 토큰 결제의 성과와 남은 과제를 평가할 수 있습니다.

## 함께 보면 좋을 자료

- [Ethereum 노드와 클라이언트](https://ethereum.org/en/developers/docs/nodes-and-clients/): 실행 노드와 합의·validator 역할을 구분합니다.
- [ERC-20 표준](https://eips.ethereum.org/EIPS/eip-20): 토큰의 인터페이스와 반환값·이벤트 규칙을 확인할 수 있습니다.
- [한국은행 프로젝트 한강 1단계 보고서](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216): 부록에 합의·계약·은행 전산 연동 구조가 나옵니다.

## 참고 자료

자료 확인일은 2026년 10월 15일입니다. 릴리스는 해당 버전의 기록이며 한강의 1단계 구현과 2026년 후속 계획은 구분했습니다.

- [Besu 공식 문서](https://docs.besu-eth.org/), [메인넷 구성](https://docs.besu-eth.org/public-networks/tutorials/besu-teku-mainnet), [QBFT](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft).
- [EVM](https://ethereum.org/en/developers/docs/evm/), [계정](https://ethereum.org/en/developers/docs/accounts/), [거래](https://ethereum.org/en/developers/docs/transactions/), [JSON-RPC](https://ethereum.org/en/developers/docs/apis/json-rpc/), [ERC-20](https://eips.ethereum.org/EIPS/eip-20), [Solidity 컴파일러](https://docs.soliditylang.org/en/latest/using-the-compiler.html).
- [병렬 실행](https://docs.besu-eth.org/public-networks/concepts/parallel-transaction-execution), [저장 형식](https://docs.besu-eth.org/public-networks/concepts/data-storage-formats), [free gas](https://docs.besu-eth.org/private-networks/how-to/configure/free-gas), [로컬 permissioning](https://docs.besu-eth.org/private-networks/how-to/use-local-permissioning).
- [Besu 26.9.0](https://github.com/besu-eth/besu/releases/tag/26.9.0), [25.6.0](https://github.com/besu-eth/besu/releases/tag/25.6.0), [Glamsterdam 테스트넷 공지](https://blog.ethereum.org/en/2026/09/17/glamsterdam-testnet-announcement).
- [Project Hangang: Live Pilot of a Unified Ledger Integrating Wholesale CBDCs and Tokenized Deposits](https://www.bok.or.kr/eng/bbs/E0000654/view.do?menuNo=400048&nttId=10095216): 한국은행, 2025년 12월.
- [A unified ledger in practice: lessons from Project Hangang](https://www.ecb.europa.eu/pub/pdf/sintra/ecb.forumcentbankpub2026_Shin_paper.sk.pdf): Ryu·Shin·Sung·Yun, ECB Forum 2026, 7월 1일 발표 후 수정본. 저자들의 견해를 담은 연구 논문입니다.
- [프로젝트 한강의 기관용 디지털화폐, 일반인용 CBDC와 어떻게 다를까](https://www.bok.or.kr/portal/bbs/B0000347/view.do?nttId=11065408&menuNo=201106): 한국은행, 2026년 10월 8일.
