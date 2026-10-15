---
title: "Besu 이해하기: 이더리움 실행부터 은행의 토큰 결제까지"
meta_title: "Besu 설명 가이드: EVM, 실행 클라이언트, 허가형 네트워크와 프로젝트 한강"
description: "Java 기반 이더리움 실행 클라이언트 Besu가 거래와 상태를 처리하는 원리, 메인넷과 허가형 네트워크의 차이, 한국은행 프로젝트 한강 사례와 최근 기술 동향을 설명합니다."
date: 2026-10-15T11:37:00+09:00
lastmod: 2026-10-15T13:33:05+09:00
image: "/images/posts/besu-state-of-play-2026/cover.png"
categories: ["Blockchain"]
tags: ["besu", "ethereum", "execution-client", "qbft", "enterprise-blockchain"]
author: "whackur"
translationKey: "besu-state-of-play-2026"
draft: false
---

Besu는 Java로 작성한 오픈소스 이더리움 실행 클라이언트입니다. 이더리움 메인넷의 거래를 검증하는 데도 쓰이고, 참여 기관을 정해 운영하는 별도 블록체인을 만드는 데도 쓰입니다. 같은 소프트웨어를 사용해도 두 네트워크의 돈, 참여자, 합의 방식이 같아지는 것은 아닙니다. 이 차이를 알아야 금융기관의 Besu 도입 소식을 제대로 읽을 수 있습니다. [Besu 공식 문서](https://docs.besu-eth.org/)

가령 은행들이 Besu로 토큰 결제망을 만들었다고 합시다. Solidity 계약과 익숙한 Ethereum 개발 도구를 활용할 여지는 큽니다. 그러나 그 망의 예금 토큰이 메인넷의 ETH가 되거나, 메인넷 검증자들이 은행 간 결제를 보증해 주지는 않습니다. 클라이언트가 제공하는 실행 기능과 기관들이 정하는 신뢰 관계를 나눠 살펴봐야 합니다.

이 글은 먼저 EVM과 클라이언트, 네트워크의 관계를 설명하고 토큰 전송 하나를 따라갑니다. 이어 허가형 합의와 은행 간 결제 설계를 살펴본 뒤, 한국은행 프로젝트 한강과 최근 Besu 개발을 연결합니다. 시점에 따라 달라지는 릴리스·지원 범위는 **2026년 10월 15일 확인 기준**으로 따로 표시했습니다.

## EVM, 클라이언트, 네트워크의 관계

이더리움 가상 머신(Ethereum Virtual Machine, EVM)은 스마트 계약의 바이트코드를 실행하는 규칙과 실행 환경입니다. 덧셈, 조건 분기, 저장소 읽기·쓰기 같은 명령을 정의하며 실행에 필요한 gas도 계산합니다. Solidity는 계약을 작성하는 언어이고, 컴파일러가 만든 바이트코드를 EVM이 실행합니다. Solidity 소스 파일 자체가 노드 사이를 돌아다니며 실행되는 구조는 아닙니다. [Solidity 컴파일러 문서](https://docs.soliditylang.org/en/latest/using-the-compiler.html)

Besu는 이 실행 환경을 포함하는 **노드 소프트웨어 전체**입니다. 거래를 받고, 다른 노드와 통신하고, 블록과 상태를 저장하고, 계약을 실행하고, 애플리케이션에 JSON-RPC를 제공합니다. JSON-RPC는 원격 프로시저 호출(Remote Procedure Call, RPC)을 JSON 메시지로 요청하는 인터페이스입니다. EVM은 이 가운데 실행을 맡습니다. Besu를 EVM과 같은 말로 쓰면 거래 전파나 디스크 저장, 합의 연결이 설명에서 빠집니다. [공식 소개](https://docs.besu-eth.org/)

Geth와 Nethermind도 이더리움 실행 클라이언트입니다. Besu와 경쟁하거나 함께 네트워크를 구성하는 구현체이며, Besu 옆에 놓인 다른 종류의 가상 머신이라는 뜻이 아닙니다. 같은 네트워크에 참여하려면 적용된 프로토콜 규칙에 따라 같은 거래 순서에서 같은 실행 결과를 내야 합니다. 내부 자료구조와 실행 최적화는 달라도 됩니다. [Ethereum 노드와 클라이언트](https://ethereum.org/en/developers/docs/nodes-and-clients/)

네트워크는 그 소프트웨어로 참여하는 공동의 원장입니다. 어떤 genesis에서 출발하는지, 어느 chain ID를 쓰는지, 어떤 시점에 프로토콜 변경을 적용하는지, 누가 블록을 확정하는지가 네트워크의 경계를 만듭니다. Besu 두 대를 설치했다고 자동으로 같은 체인에 연결되지는 않습니다. 메인넷 설정을 쓰는 노드와 별도 genesis를 쓰는 은행 노드는 서로 다른 상태를 기록합니다. [Besu 네트워크 설정](https://docs.besu-eth.org/public-networks/reference/options)

| 구분 | 담당하는 것 | Besu와의 관계 |
| --- | --- | --- |
| Solidity | 계약의 동작을 소스로 표현 | 컴파일 결과를 배포해 실행 |
| EVM | 바이트코드 실행과 gas 계산 | Besu 안의 실행 구성요소 |
| 실행 클라이언트 | 거래·상태·블록·RPC 처리 | Besu, Geth, Nethermind 등의 구현 |
| 네트워크 | 공유할 원장과 프로토콜·합의 규칙 | 같은 클라이언트로도 별도 네트워크 구성 가능 |

이 구분은 이식성을 판단할 때도 유용합니다. 같은 EVM 계열이면 코드를 재사용하기 쉽지만, 같은 자산을 공유한다는 뜻은 아닙니다. 실행 규칙의 호환성과 원장의 연속성은 별개의 문제입니다.

## 계정과 상태가 나타내는 것

이더리움의 상태에는 계정별 잔액, nonce, 코드와 저장소 정보가 들어갑니다. 일반적인 개인 키 기반 계정은 서명으로 거래를 승인하고, 계약 계정은 배포된 코드를 실행합니다. 여기서 기본 통화 잔액과 ERC-20 잔액을 구별해야 합니다. ERC-20 토큰 잔액은 보통 토큰 계약의 storage에 기록된 값입니다. 노드가 모든 토큰을 기본 통화와 같은 계정 잔액 필드에 보관하지는 않습니다. [Ethereum 계정](https://ethereum.org/en/developers/docs/accounts/), [ERC-20 표준](https://eips.ethereum.org/EIPS/eip-20)

예를 들어 토큰 계약의 `balanceOf(Alice)`가 100이라고 합시다. 이 값은 그 네트워크의 그 계약이 관리하는 상태입니다. Alice가 다른 체인에서도 같은 주소를 사용한다고 해서 100이 따라오지 않습니다. 주소 문자열이 같아도 참조하는 원장과 계약 코드가 다르면 경제적 의미가 달라집니다. 지갑 화면에서 네트워크를 바꾸는 동작은 자산 이전이 아닙니다.

거래는 이 상태를 바꾸자는 요청입니다. 노드는 블록 순서에 맞춰 거래를 실행하고 결과 상태가 블록의 약속과 일치하는지 검증합니다. 상태 루트(state root)는 전체 상태를 암호학적으로 요약한 값입니다. 각 기관이 엑셀 파일을 따로 고친 뒤 합계를 비교하는 방식과 달리, 노드들은 동일한 실행 규칙으로 상태 전이를 재현합니다. 다만 코드가 현실의 채권이나 소유권을 올바르게 표현하는지는 애플리케이션과 제도의 책임입니다. [거래의 구조](https://ethereum.org/en/developers/docs/transactions/)

## ERC-20 전송 하나가 처리되는 과정

Alice가 Bob에게 토큰 10개를 보내는 단순한 예를 보겠습니다. 이미 배포된 계약은 표준적인 ERC-20이며, 특별한 수수료나 전송 제한은 없다고 가정합니다. 숫자는 읽기 편하게 표시한 값이고 실제 호출에는 계약의 소수 자릿수를 반영한 정수를 넣습니다. 아래 흐름은 설명용이며 특정 금융 시스템의 내부 구현을 재현한 것은 아닙니다.

1. **지갑이 호출 데이터를 만듭니다.** 목적지는 Bob이 아니라 토큰 계약 주소입니다. `data`에는 `transfer(Bob, amount)`의 함수 식별자와 인수를 인코딩합니다. 단순 토큰 전송이라면 기본 통화를 보내는 `value`는 보통 0입니다. 토큰 수량과 기본 통화 전송액을 혼동하면 전혀 다른 거래를 만들게 됩니다.
2. **서명자가 거래를 승인합니다.** 발신 계정의 nonce, chain ID, gas 한도와 네트워크에 맞는 수수료 필드를 포함해 서명합니다. nonce는 같은 계정의 거래 순서를 관리합니다. Besu가 애플리케이션 사용자의 키를 대신 보관한다고 가정하면 안 됩니다. 공식 문서는 외부 서명 도구와 키 관리를 별도로 안내합니다.
3. **RPC 노드가 서명된 거래를 받습니다.** 지갑이나 백엔드는 `eth_sendRawTransaction`으로 거래를 제출합니다. 노드는 서명과 nonce, 자금·수수료 조건 등 유효성을 검사하고, 적용되는 permissioning 규칙도 확인합니다. 응답으로 받은 거래 해시는 접수한 거래를 식별할 뿐, 블록 포함이나 전송 성공을 보증하지 않습니다.
4. **거래가 블록 후보에 들어갑니다.** 거래 풀에 남은 요청 중 일부가 선택됩니다. 누가 블록 제안 권한을 갖는지는 메인넷 지분증명(Proof of Stake, PoS)과 허가형 QBFT에서 다릅니다. RPC를 받은 노드가 반드시 블록을 만드는 노드일 필요도 없습니다.
5. **EVM이 계약을 실행합니다.** 계약은 발신자 잔액과 조건을 확인하고 Alice와 Bob의 잔액 저장소를 갱신합니다. 정상 전송이면 ERC-20의 `Transfer` 이벤트도 남깁니다. 이벤트는 애플리케이션이 변화를 추적하는 기록이고 현재 잔액 자체는 storage에서 읽습니다.
6. **다른 노드가 결과를 검증합니다.** 정해진 블록 순서로 실행해 같은 상태 전이를 확인합니다. 합의 절차를 거친 뒤 애플리케이션은 receipt의 실행 상태와 로그를 확인하고 필요한 확정 수준까지 기다립니다. 실패해 revert된 거래도 블록에 포함될 수 있으며 실행에 쓴 gas는 별도입니다.

호출 형식과 이벤트는 [ERC-20](https://eips.ethereum.org/EIPS/eip-20), 거래 필드·수명주기·revert와 gas의 관계는 [Ethereum 거래 문서](https://ethereum.org/en/developers/docs/transactions/), 키 관리와 RPC의 역할은 [Besu 소개](https://docs.besu-eth.org/)를 바탕으로 설명했습니다.

이 흐름에서 RPC는 입구, EVM은 실행 규칙, storage는 실행 결과, 합의는 공유할 블록을 결정하는 절차입니다. 한 계층이 다른 계층을 대신하지 않습니다. RPC가 정상 응답해도 계약이 revert될 수 있고, 계약이 로컬 시뮬레이션에서 성공해도 실제 포함 순서에서 잔액이나 가격이 달라질 수 있습니다. `eth_call`로 미리 읽거나 실행해 보는 것과 서명된 거래를 확정하는 것도 구별해야 합니다.

애플리케이션은 거래 해시를 주문 번호처럼 보관하되, 사업상 결제 완료 판정은 실행 결과와 네트워크의 확정 규칙에 연결하는 편이 안전합니다. 재시도할 때도 새 거래를 무조건 만들면 중복 지급 위험이 생깁니다. 지급 의도에 고유 식별자를 두고 계약 상태와 백엔드 기록을 맞추는 설계는 Besu를 선택한 뒤에도 남는 일입니다. 이는 특정 제품의 보장 기능이 아니라 위 거래 흐름에서 도출한 설계 권고입니다.

## Solidity 호환성과 이식의 경계

Besu에서 Solidity 계약을 실행할 수 있다는 설명에는 조건이 붙습니다. 컴파일러의 `evmVersion`과 네트워크가 활성화한 fork 규칙이 맞아야 합니다. 새 opcode를 사용하는 바이트코드를 그 명령이 없는 체인에 배포하면 실행이 실패할 수 있습니다. 사용할 precompile과 gas 규칙도 대상 네트워크에서 확인해야 합니다. “EVM 호환”이라는 이름만으로 모든 시점의 모든 바이트코드를 보증할 수는 없습니다. [Solidity의 EVM 대상 설정](https://docs.soliditylang.org/en/latest/using-the-compiler.html#setting-the-evm-version-to-target)

개발 도구도 같은 원리입니다. JSON-RPC와 계약의 호출 형식을 정의하는 ABI(Application Binary Interface)를 활용하는 지갑·라이브러리·테스트 도구를 재사용하기 좋지만, RPC namespace, 반환 형식, tracing 지원과 수수료 추정 방식은 점검해야 합니다. 예를 들어 [26.9.0 릴리스](https://github.com/besu-eth/besu/releases/tag/26.9.0)는 `eth_feeHistory` 인수 검증을 더 엄격하게 바꿨습니다. 표준을 따른다는 설명과 기존 애플리케이션 호출이 수정 없이 동작한다는 약속은 다릅니다.

계약의 외부 의존성은 더 큰 문제입니다. 메인넷의 가격 오라클, 특정 토큰 주소, 유동성 풀, bridge, 다른 계약을 참조하는 애플리케이션은 코드만 옮겨서 완성되지 않습니다. 대상 체인에 해당 계약과 데이터 공급자가 있어야 하고, 가격의 의미와 자산 상환 조건도 같아야 합니다. 로컬 테스트에서 호출을 가짜 응답으로 대체한 결과는 실제 시장의 유동성을 검증하지 않습니다.

다른 네트워크에 같은 소스를 재배포하면 별도 인스턴스가 생깁니다. 예전 사용자 잔액, 계약 storage, 관리자 권한과 예치 자산은 자동 복제되지 않습니다. bridge나 상태 이전을 도입한다면 누가 원본을 잠그거나 소각하는지, 어느 증명을 믿는지, 양쪽 공급량을 어떻게 맞출지를 추가로 설계해야 합니다. Besu는 이 경제적 연결을 클라이언트 설치만으로 만들어 주지 않습니다.

### London·Prague·Osaka와 적용 규칙

Besu의 소프트웨어 버전과 EVM 실행 규칙의 개정 이름은 구분해야 합니다. `26.9.0`은 Besu 배포판 번호이고, London·Prague·Osaka는 Ethereum 실행 계층의 하드포크 이름입니다. 이런 개정에는 EVM 명령뿐 아니라 gas 계산이나 거래 검증 규칙의 변경도 포함됩니다. Besu는 London이나 Prague에 고정된 클라이언트가 아니라 여러 시기의 규칙을 구현합니다. 26.9.0 태그의 Java 구현 [`MainnetEVMs`](https://github.com/besu-eth/besu/blob/26.9.0/evm/src/main/java/org/hyperledger/besu/evm/MainnetEVMs.java)에는 London·Prague·Osaka용 EVM 구성 함수가 각각 있습니다.

구현된 규칙 중 무엇을 적용할지는 체인의 활성화 일정으로 결정합니다. 같은 태그의 [메인넷 설정](https://github.com/besu-eth/besu/blob/26.9.0/config/src/main/resources/mainnet.json)은 다음 값을 담고 있습니다. London은 블록 번호, Prague와 Osaka는 블록 timestamp 기준입니다. 이는 패키지 버전 비교와 다른 선택 기준입니다.

| 실행 계층 개정 | 26.9.0 메인넷 설정 | 활성화 기준 |
| --- | --- | --- |
| London | `londonBlock: 12965000` | 블록 12,965,000부터 |
| Prague | `pragueTime: 1746612311` | 해당 Unix timestamp부터 |
| Osaka | `osakaTime: 1764798551` | 해당 Unix timestamp부터 |

Osaka 지원 근거는 설정 이름만이 아닙니다. [25.11.0 릴리스](https://github.com/besu-eth/besu/releases/tag/25.11.0)는 Fusaka 메인넷 준비 릴리스라고 밝히며 Osaka·BPO1·BPO2 활성화 시각 추가를 명시합니다. 이후 26.9.0의 코드와 메인넷 설정에도 Osaka가 반영돼 있습니다. 반대로 26.9.0 [릴리스](https://github.com/besu-eth/besu/releases/tag/26.9.0)와 [Sepolia 설정](https://github.com/besu-eth/besu/blob/26.9.0/config/src/main/resources/sepolia.json)에 Amsterdam 일정이 있다는 사실을 메인넷 활성화로 읽으면 안 됩니다. 같은 태그의 메인넷 설정에는 Amsterdam 시각이 없습니다.

과거 블록을 검증할 때도 이 구분이 작동합니다. 최신 바이너리가 과거 거래를 무조건 가장 새 규칙으로 다시 실행하지는 않습니다. 블록의 번호·시각과 체인 일정을 대조해 그 블록에 적용되는 규칙을 선택합니다. 태그의 [`DefaultProtocolSchedule.getByBlockHeader`](https://github.com/besu-eth/besu/blob/26.9.0/ethereum/core/src/main/java/org/hyperledger/besu/ethereum/mainnet/DefaultProtocolSchedule.java)가 이 선택을 구현합니다. 과거 실행을 재현할 규칙을 아는 것과 필요한 과거 상태 데이터를 보유하는 것은 별개이므로, 뒤에서 설명할 archive 요구도 여전히 남습니다.

자체 허가형 체인은 운영자가 합의한 genesis·포크 일정과 해당 Besu 버전의 구현을 함께 확인해야 합니다. 바이너리 업그레이드만으로 원하는 새 규칙의 활성화가 보장되지는 않습니다. [Genesis 설정 문서](https://docs.besu-eth.org/public-networks/reference/genesis-items)의 milestone 항목을 출발점으로 삼되, 포크마다 합의 방식의 전제와 필요한 시스템 계약도 검증해야 합니다. 위 메인넷 근거는 모든 포크가 QBFT에서 그대로 동작한다는 보증이 아닙니다. 여기서 확인한 범위는 태그된 소스·설정과 릴리스이며 실시간 RPC로 체인의 현재 실행 규칙을 측정한 결과는 아닙니다.

## 메인넷과 허가형 네트워크의 합의

Ethereum 메인넷에서 Besu는 실행 계층(Execution Layer, EL)을 담당합니다. Teku 같은 합의 계층(Consensus Layer, CL) 클라이언트와 Engine API로 연결해 실행 payload를 만들고 검증합니다. 두 프로세스는 JWT로 인증하며, 스테이킹을 하려면 합의 측 validator 역할도 구성합니다. 일반 노드 운영과 검증자 운영은 구별됩니다. Besu 프로세스 하나만 켰다고 메인넷 스테이킹 구성이 완성되지는 않습니다. [Besu와 Teku 구성](https://docs.besu-eth.org/public-networks/tutorials/besu-teku-mainnet)

자체 허가형 체인에서는 승인된 Besu validator들이 블록에 합의하도록 구성할 수 있습니다. 공식 문서는 새 기업용 구성에 Quorum Byzantine Fault Tolerance(QBFT)를 권장하며 Istanbul Byzantine Fault Tolerance(IBFT) 2.0도 문서화합니다. 이 합의 경로에는 메인넷의 beacon 합의 클라이언트를 붙일 필요가 없습니다. [QBFT](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft), [IBFT 2.0](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/ibft)

![메인넷에서는 합의 클라이언트가 Engine API로 Besu와 연결됩니다. 허가형 네트워크에서는 승인된 Besu validator들이 QBFT 또는 IBFT 2.0으로 합의합니다. 두 구성은 EVM·거래 풀·저장소를 공유하지만 서명, RPC 접근 통제와 프라이버시는 따로 설계합니다.](/images/posts/besu-state-of-play-2026/besu-deployment-roles.svg)

*공식 메인넷·QBFT 문서를 바탕으로 직접 그린 개념도입니다. 특정 금융기관의 실제 배치도는 아닙니다.* [SVG 확대](/images/posts/besu-state-of-play-2026/besu-deployment-roles.svg)

QBFT에서는 validator들이 번갈아 블록을 제안하고 3분의 2 이상 서명으로 블록을 승인합니다. 문서는 3분의 1을 넘는 validator가 참여하지 못하면 블록 생성이 멈춘다고 경고합니다. 네 대를 운영한다고 가정하면 한 대 장애를 고려한 구성에서도 두 대가 동시에 빠지는 상황은 문제가 됩니다. 블록 확정에 필요한 참여 조건과 계약 실행 성공 여부는 서로 다른 검사입니다. [QBFT 합의 조건](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft)

서버 수와 독립적인 운영 주체 수도 다릅니다. 같은 회사가 같은 클라우드 계정에서 네 대를 운영하면 장애나 관리 권한이 한곳에 모일 수 있습니다. 누가 validator를 추가·제거하는지, 규칙 변경에 누구의 동의가 필요한지, 분쟁 때 어떤 기록을 인정할지도 정해야 합니다. 공개 이더리움의 참여 구조와 경제적 보안을 작은 승인 집합이 그대로 물려받지는 않습니다. 이 부분은 소프트웨어 성능보다 운영 주체의 관계와 공동 규칙을 평가할 문제입니다.

## Gas 가격을 0으로 정해도 남는 제약

허가형 체인은 사용자가 기본 통화를 구매해 수수료를 내지 않도록 구성할 수 있습니다. Besu의 [free gas 문서](https://docs.besu-eth.org/private-networks/how-to/configure/free-gas)는 최소 gas 가격과 London 이후 base fee 설정 등을 설명합니다. 거래를 받아 주는 노드와 지갑의 수수료 설정까지 맞아야 하므로 옵션 하나만 바꾸면 끝나는 일은 아닙니다.

**Gas는 계산량의 단위이고 gas 가격은 그 단위의 가격입니다.** 가격이 0이어도 거래 gas 한도와 블록 gas 한도는 남습니다. 무한 반복이나 과도한 storage 쓰기를 제한할 필요도 사라지지 않습니다. 서버의 CPU·디스크·네트워크 비용은 운영 기관이 부담합니다. 이용료를 사용자에게 직접 청구하지 않는 정책과 자원이 무제한이라는 주장은 전혀 다릅니다.

앞의 ERC-20 전송에서도 잔액 변경에 필요한 실행량은 존재합니다. gas 한도가 부족하면 토큰 가격과 무관하게 실행이 실패할 수 있습니다. 은행 고객에게 원화 금액만 보여주는 앱을 만들더라도 백엔드는 gas 추정, 제출 제한과 과부하 대응을 설계해야 합니다. 이것은 금융 자산의 액면가와 네트워크 자원 가격을 분리해서 볼 이유이기도 합니다.

## 참여 허가와 거래 비공개의 차이

Permissioning은 누가 노드로 연결하거나 어느 계정이 거래를 보낼지 통제하는 기능입니다. Besu의 로컬 node·account allowlist는 각 노드가 적용하는 규칙이므로 전체 망의 정책을 맞춰 운영해야 합니다. 모든 노드가 자동으로 같은 허가 목록을 공유한다는 뜻은 아닙니다. [로컬 permissioning](https://docs.besu-eth.org/private-networks/how-to/use-local-permissioning)

접속 가능한 기관을 제한해도, 거래를 실행하고 상태를 복제하는 참여자에게 그 데이터가 자동으로 숨겨지지는 않습니다. 외부 인터넷에 공개하지 않는 네트워크와 참여 은행 사이에서도 거래별 비밀을 보장하는 네트워크는 요구사항이 다릅니다. 고객 이름을 주소로 바꿔도 거래 관계나 금액에서 정보가 드러날 수 있습니다. 프라이버시 검토는 어떤 참여자가 어떤 원문·상태·로그를 읽는지부터 시작해야 합니다.

과거 Besu 튜토리얼의 Tessera private transaction을 현재 기능으로 소개하면 오류입니다. [25.6.0](https://github.com/besu-eth/besu/releases/tag/25.6.0)은 Tessera privacy와 계약 기반 onchain node·account permissioning 제거를, [25.7.0](https://github.com/besu-eth/besu/releases/tag/25.7.0)은 `EEA`·`PRIV` RPC 그룹 제거를 기록했습니다. QBFT의 계약 기반 validator 선택은 제거된 permissioning과 다른 기능입니다.

금융 시스템은 별도 암호화·선택적 공개·데이터 분리 방식을 평가할 수 있지만, 각 방식의 검증 가능성과 신뢰 주체를 밝혀야 합니다. 특정 플러그인이 옛 privacy API의 완전한 대체물이라고 가정해서도 안 됩니다. 공개해야 할 감사 정보와 숨겨야 할 고객 정보를 정하는 일은 Besu를 선택하기 전에 요구사항으로 정리할 가치가 있습니다.

## 은행 간 토큰 결제의 설계 예시

은행 A 고객이 은행 B 고객에게 1만 원을 지급하는 상황을 생각해 보겠습니다. 아래는 EVM 원장으로 가능한 구조를 설명하는 가상 예시입니다. 프로젝트 한강의 계약 주소, API, 배치 순서를 나타내지 않으며 ERC-20 채택 여부도 주장하지 않습니다.

동일 은행의 토큰 하나를 단순 전송하면 수취인은 그 토큰 발행 은행에 대한 청구권을 받습니다. 수취인이 거래하는 은행의 예금으로 받게 하려면 이야기가 달라집니다. A의 예금 토큰을 줄이고 B의 예금 토큰을 늘리는 것에 더해 은행 사이의 결제 자산도 이전해야 합니다. 고객 화면의 송금 한 번이 원장에서는 여러 종류의 상태 변경을 묶는 작업이 됩니다.

같은 원장에 두 은행의 예금 토큰과 기관 간 결제 자산이 있고 필요한 권한을 갖춘 계약이 있다고 가정합시다. 계약은 A 고객의 토큰을 소각하고, A에서 B로 결제 자산을 이전한 뒤, B 고객에게 예금 토큰을 발행하도록 설계할 수 있습니다. 모든 단계를 하나의 거래 안에서 실행하고 오류를 전체 revert로 전파하면 부분 지급을 막는 원자적 처리가 가능합니다. 반대로 외부 은행 시스템의 API 호출을 끼워 넣으면 EVM의 원자성만으로 바깥 시스템까지 되돌릴 수는 없습니다.

여기에는 권한과 자금 조건이 따라붙습니다. 누구나 예금 토큰을 발행하게 해서는 안 되고 A에 결제 유동성이 부족할 때 처리 방식을 정해야 합니다. 고객 확인과 제재 대상 검사, 환불·분쟁 절차도 필요합니다. 계약의 발행 권한과 validator의 블록 제안 권한을 분리해야 할 이유도 여기 있습니다. 블록을 만든다는 권한이 은행의 부채를 임의로 발행할 권한과 같아서는 안 됩니다.

외부 정보에 조건을 걸면 오라클 문제도 생깁니다. “물품 배송 완료”를 EVM이 현실에서 직접 관찰하지는 못합니다. 누군가 제공한 데이터를 어느 권한으로 받아들일지 정해야 합니다. 여러 기관이 같은 계약을 실행한다는 사실은 잘못 입력한 배송 상태를 참으로 바꾸지 않습니다. 이런 설계의 장점은 공유 상태에서 여러 자산을 함께 처리하는 데 있고, 현실의 사실 판정과 법적 책임을 없애는 데 있지 않습니다.

## 한국에서 확인되는 프로젝트 한강

국내 사례로는 한국은행의 프로젝트 한강이 구체적인 근거를 제공합니다. 한국은행 소속 Jaemin Ryu, Hyun Song Shin, Joonyi Sung, Sung Guan Yun이 쓴 [*A unified ledger in practice: lessons from Project Hangang*](https://www.ecb.europa.eu/pub/pdf/sintra/ecb.forumcentbankpub2026_Shin_paper.sk.pdf)은 ECB의 2026년 7월 1일 포럼 발표 후 소폭 수정된 논문입니다. 저자들은 견해가 한국은행이나 금융통화위원회의 공식 견해와 반드시 같지는 않다고 밝힙니다(1쪽).

이 논문은 한강의 Digital Currency System(DCS)과 Project Agorá가 모두 Hyperledger Besu를 기반 기술로 사용한다고 명시합니다(4.2절, 24쪽). 1차 실거래 실험은 **2025년 4월 1일부터 6월 30일**까지 약 8만 명과 1만 2천 가맹점이 참여한 실험입니다. 참여 은행은 KB국민·신한·우리·하나·IBK기업·NH농협·부산은행입니다(3.2절, 16쪽). 이를 일곱 은행이 각자 별도의 Besu 상용망을 구축했다는 뜻으로 읽으면 안 됩니다.

소매 이용자는 예금 토큰을 사용하고 은행 간에는 도매 중앙은행 화폐로 결제합니다. 송금 은행의 토큰 소각, 은행 간 결제, 수취 은행의 토큰 발행을 묶는 burn-and-issue 구조가 이중 은행 체계를 유지하도록 설계됐습니다(2.3절, 8~9쪽). 논문은 중앙은행을 authoritative validator로 두는 권위증명(Proof of Authority, PoA) 구성을 설명합니다(2.1절, 4~6쪽). 이 자료만으로 구체적인 QBFT 설정을 단정하지 않으며 Ethereum 메인넷 결제로 설명하지도 않습니다.

2026년 후속 단계는 성과와 계획을 구분해 읽어야 합니다. 논문 3.3절(18~19쪽)은 참여 은행 확대, 이용 편의 개선과 국고금 활용을 계획으로 설명합니다. 이 일정만으로 10월 현재 모든 계획의 실행 완료를 확인할 수는 없습니다. 1차 실험의 실시간 총액결제(Real-Time Gross Settlement, RTGS) 시스템 직접 연결 부재와 사전 유동성 확보·오프라인 대사 부담도 기록돼 있습니다(17쪽). 상용화를 위한 운영시간·법적 성격·유동성 과제와 Agorá 연결 검토 역시 남아 있습니다(7쪽, 24~26쪽). 연결 가능성은 이미 배포된 국제 연결망의 증거가 아닙니다.

이 글에서 국내 Besu 활용으로 직접 확인해 소개하는 범위는 한강 DCS입니다. Hyperledger 회원 가입이나 Fabric 도입만으로 다른 국내 기관을 Besu 사용자에 넣지 않았습니다. 한강이 보여주는 것은 이더리움 실행 기술을 제도권 결제 설계에 활용한 사례이지, 공개 이더리움의 통화나 참여 구조를 그대로 채택한 사례가 아닙니다.

## Fabric 및 공개 이더리움과 비교할 기준

Hyperledger라는 이름으로 묶였던 프로젝트라도 Fabric과 Besu의 애플리케이션 구조는 다릅니다. Fabric의 기본 거래 흐름에서는 제안받은 chaincode를 endorsing peer가 시뮬레이션하고, endorsement와 읽기·쓰기 집합을 담은 거래를 ordering service가 정렬합니다. peer는 endorsement 정책과 상태 충돌 등을 검증한 뒤 유효한 쓰기를 반영합니다. Ethereum의 EVM 거래 실행 모델과 같은 개발·배포 경로로 취급하기 어렵습니다. [Fabric 거래 흐름](https://hyperledger-fabric.readthedocs.io/en/latest/txflow.html)

Besu의 장점은 Ethereum 계정 모델, Solidity 바이트코드와 도구 경험을 활용하면서 별도 망을 구성할 수 있다는 데 있습니다. Fabric은 조직별 endorsement 정책을 중심으로 설계할 때 비교할 대상입니다. 어느 쪽이 무조건 기업에 적합하다는 결론보다 기존 계약·개발 역량, 거래별 참여 정책과 데이터 공개 범위를 먼저 놓고 비교하는 편이 낫습니다. 프레임워크 이름이 규제 준수나 프라이버시를 대신 보장하지는 않습니다.

공개 Ethereum을 선택하면 공통 원장에 이미 존재하는 자산·애플리케이션과 연결할 기회를 얻습니다. 대신 공개 검증, 네트워크 수수료와 해당 프로토콜의 규칙을 받아들입니다. 별도 허가형 망은 참여자와 변경 절차를 기관들이 정하기 쉽지만 유동성과 접근성을 직접 구축해야 합니다. 공개망의 탈중앙화 정도나 생태계가 클라이언트 바이너리에 담겨 복사되지는 않습니다. [Ethereum 노드 구조](https://ethereum.org/en/developers/docs/nodes-and-clients/)

제 판단으로는 Besu 평가의 첫 질문은 TPS 목표보다 “어떤 기관들이 하나의 상태를 공유하며 누가 규칙을 바꿀 수 있는가”에 가깝습니다. 한 조직이 모든 권한을 보유하고 외부 검증도 필요 없다면 일반 데이터베이스와 비교할 이유가 있습니다. 여러 기관이 계약 실행 결과를 공동 검증하고 여러 자산을 한 거래로 묶어야 한다면 공유 실행 원장의 가치가 더 구체적으로 드러납니다.

## 상태 저장과 과거 데이터 조회

노드가 최신 블록까지 따라왔다는 사실만으로 모든 과거 질문에 답할 수 있지는 않습니다. 현재 잔액, 오래전 시점의 계약 실행, 과거 거래 receipt, 상태 증명은 서로 다른 데이터 요구입니다. 앞의 결제 앱도 현재 잔액만 보여줄 때와 수년치 지급을 감사할 때 필요한 노드 구성이 달라집니다.

Besu의 기본 world state 저장 형식은 Bonsai입니다. 현재 상태 접근과 저장 공간 효율을 고려한 구조이며 Forest of Tries도 문서에 남아 있습니다. 일반 Bonsai의 기본 historical block limit은 512입니다. 이 값을 단순한 디스크 절감량 설정으로 읽거나, 숫자만 늘리면 모든 archive 기능이 확보된다고 기대하면 안 됩니다. [저장 형식과 데이터 접근](https://docs.besu-eth.org/public-networks/concepts/data-storage-formats)

공식 문서가 제시하는 약 1.14 TB의 Bonsai SNAP full node와 약 12 TB의 Forest FULL archive node는 서비스 범위가 다릅니다. 전자는 2026년 5월의 특정 AWS 환경에서 얻은 추정입니다. 이를 같은 기능을 수행하는 DB의 압축률이나 영구적인 최소 디스크 사양으로 비교할 수 없습니다. 과거 상태 보관의 비용을 확인하려면 애플리케이션이 요구하는 조회 범위를 먼저 고정해야 합니다.

Bonsai Archive는 별도의 실험적 개발 경로입니다. [26.4.0](https://github.com/besu-eth/besu/releases/tag/26.4.0)과 [26.5.0](https://github.com/besu-eth/besu/releases/tag/26.5.0)은 저장 구조 변경에 따른 전체 재동기화 필요성을 경고했습니다. History expiry로 옛 block body와 receipt를 지우는 일도 과거 world state 보관과 별개입니다. 공식 문서상 header와 genesis는 남지만, receipt에 의존하는 인덱서는 영향을 받습니다. [History expiry](https://docs.besu-eth.org/public-networks/how-to/pre-merge-history-expiry)

커뮤니티의 운영 관찰도 이 구분을 뒷받침합니다. [Eth Docker 운영자 글](https://www.reddit.com/r/ethstaker/comments/1vtatpn/eth_docker_2681_with_5_months_rolling_expiry/)은 Besu의 실험적 rolling expiry 지원을 소개하면서 receipt에 의존하는 하위 서비스의 제약을 함께 설명합니다. 디스크 절감이라는 이점과 서비스 호환성 부담을 같이 볼 사례입니다. 특정 도구 운영자의 관찰이므로 모든 배포의 보존 정책이나 커뮤니티 전체 평가로 일반화하지 않습니다.

## 성능 개선이 실제로 바꾸는 부분

Besu의 최적화는 EVM 명령 실행에만 머물지 않습니다. 상태 읽기·쓰기와 상태 루트 계산도 블록 처리 시간에 영향을 줍니다. 공식 [병렬 실행 설명](https://docs.besu-eth.org/public-networks/concepts/parallel-transaction-execution)은 백그라운드에서 거래를 낙관적으로 실행한 뒤, 정해진 순차 처리 과정에서 충돌 없는 결과를 재사용하는 방식을 설명합니다. 충돌하거나 준비되지 않은 결과는 다시 실행하거나 기존 경로로 처리합니다. 이 최적화가 블록의 거래 순서를 임의로 바꾸는 것은 아닙니다.

같은 계정이나 storage를 반복해서 수정하는 업무와 서로 독립적인 계정을 수정하는 업무는 병렬화의 이득이 다릅니다. 다수 이용자의 단순 송금 실험이 공통 유동성 풀을 갱신하는 계약의 성능을 그대로 예측하지 못하는 이유입니다. 기본 옵션과 실험 조건도 확인해야 합니다. 현재 [옵션 문서](https://docs.besu-eth.org/public-networks/reference/options#bonsai-parallel-tx-processing-enabled)는 Bonsai 병렬 거래 처리를 기본 활성화로 표시합니다.

상태 루트 계산의 병렬화는 [26.1.0](https://github.com/besu-eth/besu/releases/tag/26.1.0)에 기본 적용됐습니다. 유지보수자 Karim Taam과 Ameziane Hamlat의 [2026년 4월 20일 설명](https://www.lfdecentralizedtrust.org/blog/optimizing-besu-performance-parallelizing-state-root-computation)은 trie의 독립 분기 처리와 일괄 저장을 소개합니다. 저자들의 8코어·8스레드 비NVMe 환경에서는 블록 처리 시간이 최대 40% 줄었지만, NVMe에서는 이득이 작을 것으로 예상했습니다. 이를 임의의 금융망 TPS 보증으로 바꾸지는 않습니다.

[26.7.0](https://github.com/besu-eth/besu/releases/tag/26.7.0)의 Block Access List 병렬 실행도 구현 진전입니다. 출시 코드에 기능이 있다는 사실, 테스트넷 설정, 메인넷 활성화는 별도 증거가 필요합니다. 비교 실험을 읽을 때는 하드웨어, 상태 snapshot, 블록 workload와 재실행 조건을 함께 봐야 합니다. 다른 클라이언트 팀인 Nethermind의 [벤치마크 방법 설명](https://www.nethermind.io/blog/getting-ethereum-ready-for-gigagas)도 이런 조건을 명시합니다. 경쟁 프로젝트의 실험이며 현재의 보편적 순위표로 사용하지는 않습니다.

## 현재 프로젝트와 지원 범위

Besu는 Apache 2.0 라이선스의 LF Decentralized Trust(LFDT) 프로젝트입니다. 재단의 [2024년 9월 16일 출범 발표](https://www.lfdecentralizedtrust.org/announcements/linux-foundation-decentralized-trust-launches-with-17-projects-100-founding-members)는 Hyperledger Besu가 Besu 이름을 사용한다고 설명했습니다. 현재 저장소는 [`besu-eth/besu`](https://github.com/besu-eth/besu)이며 [26.4.0](https://github.com/besu-eth/besu/releases/tag/26.4.0)에 이전 안내가 있습니다. 옛 이름으로 검색되는 문서가 모두 현재 기능을 설명하는 것은 아닙니다.

2026년 10월 15일 공식 GitHub API에서 확인한 최신 정식 릴리스는 **26.9.0**, 공개 시각은 9월 25일 22:22 UTC입니다. [릴리스 원문](https://github.com/besu-eth/besu/releases/tag/26.9.0)은 native tracer 추가, RPC 검증 변경과 메모리 부족 시 프로세스 종료 기본값 등을 기록합니다. [26.6.0](https://github.com/besu-eth/besu/releases/tag/26.6.0)부터는 JDK 25가 필요합니다. 이는 현재 실행 환경을 판단할 정보이며 Besu의 기본 개념 자체가 해마다 바뀐다는 뜻은 아닙니다.

지원 범위도 구체적으로 읽어야 합니다. [26.2.0](https://github.com/besu-eth/besu/releases/tag/26.2.0)은 Fast Sync 제거를, [26.4.0](https://github.com/besu-eth/besu/releases/tag/26.4.0)은 순수 Clique 체인 시작·채굴 기능 제거를 기록했습니다. Clique에서 PoS로 전환한 체인의 이력 동기화는 별도로 유지합니다. 플러그인 모듈 분리와 이후 API·lifecycle 변경 예고도 있지만 [26.9.0](https://github.com/besu-eth/besu/releases/tag/26.9.0)은 재노출 모듈을 통한 기존 호환 경로를 명시합니다. 향후 계획을 이미 완료된 제거로 바꿔 읽으면 안 됩니다.

재단 소속과 유지보수 다양성도 구별됩니다. LFDT의 [2026 연례 보고](https://lf-decentralized-trust.github.io/governance/project-updates/2026/2026-annual-Besu/)는 2025년을 돌아보며 활성 유지보수자 21명 중 약 19명이 Consensys 소속이라고 적었습니다. 이는 당시 조직 편중의 근거이지 10월의 실시간 인원 조사나 개인별 대체 가능성 측정은 아닙니다. 활발한 개발과 특정 조직 의존 위험은 동시에 존재할 수 있습니다.

채택 자료는 프로젝트 단위로 읽는 편이 정확합니다. LFDT가 Ledger Insights에 의뢰한 [기관 채택 보고](https://www.lfdecentralizedtrust.org/ledger-insights-report-2026)는 Citi Token Services, Fnality, Clearstream D7 등을 Besu 사례로 열거합니다. 상용 운영과 상용화 준비가 섞인 자료이며 전체 LFDT 사례 수가 Besu 고객 수는 아닙니다. stake 비중, 접근 가능한 노드 수, 운영 기관 수와 거래액 역시 서로 다른 지표입니다. 이 글은 현재 시장점유율을 추정하지 않습니다.

## 보안 수정 이력을 읽는 방법

버전 숫자만 확인하는 것으로 보안 검토가 끝나지는 않습니다. 2026년 10월 14일 공개된 [서명 복구 권고](https://github.com/besu-eth/besu/security/advisories/GHSA-4h4f-925g-8h9p)와 [typed transaction decoding 권고](https://github.com/besu-eth/besu/security/advisories/GHSA-cgvq-9xfq-c54j)는 수정 버전을 26.8.0으로 표시합니다. 공개일과 패치 출시일은 다를 수 있으며 권고 공개가 실제 공격 관측을 뜻하지도 않습니다.

Tracing step 제한의 개별 수정 [`ebaf89e162`](https://github.com/besu-eth/besu/compare/ebaf89e162...26.9.0)와 [`facf43ddb9`](https://github.com/besu-eth/besu/compare/facf43ddb9...26.9.0)는 26.9.0에 포함됐습니다. 이후 병합된 [PR #11378](https://github.com/besu-eth/besu/pull/11378)은 출시 커밋을 `main`에 반영한 reconciliation입니다. 병합일이 늦다는 이유로 패치가 출시되지 않았다고 판단하면 오류입니다.

별도 후속 커밋 [`7f904a379c`](https://github.com/besu-eth/besu/commit/7f904a379cf5b59e7016118d64f6d68abadf69a2)은 batch `debug_traceBlock` 계열에서도 step ceiling을 적용하도록 보완했으며 26.9.0에는 포함되지 않았습니다. 기존 수정의 출시와 추가 경로 보완을 구분해야 합니다. 공개 RPC의 `DEBUG`·`TRACE` 제한과 [QBFT P2P 가용성 권고](https://github.com/besu-eth/besu/security/advisories/GHSA-g5j7-4r2x-rx9j)에 대한 대응 역시 다른 경계를 보호합니다. 특정 버전을 모든 경로에서 안전하다고 인증하는 설명은 아닙니다.

## 도입 검토를 실제 요구사항으로 연결하기

앞의 설명을 실무 검토로 옮기면 다음 정도의 짧은 목록으로 시작할 수 있습니다. 이는 문서의 보장 항목이 아니라 이 글의 설계 권고입니다.

- 메인넷 실행 노드인지 별도 허가형 원장인지 정하고, 합의 참여자와 변경 권한을 기록합니다.
- 계약의 fork·opcode·precompile, 외부 계약·오라클·유동성 의존성을 대상 체인에서 검증합니다.
- 애플리케이션 서명 키, validator 키와 RPC 권한을 나누고 거래별 데이터 열람 범위를 확인합니다.
- 현재 상태·과거 상태·receipt·증명 중 필요한 서비스를 정한 뒤 저장소와 복구 시험을 선택합니다.
- 목표 릴리스와 보안 수정, Java·플러그인 호환성을 함께 확인하고 장애 상황에서 합의가 유지되는지 시험합니다.

Besu를 이해하면 “이더리움 기술을 쓴다”는 말을 더 구체적으로 나눌 수 있습니다. 공유하는 것은 실행 규칙과 도구일 수 있고, 별도로 정해야 하는 것은 돈의 법적 의미와 원장 참여 규칙일 수 있습니다. 한강 같은 사례를 읽을 때도 이 구분을 유지하면 기술 채택의 성과와 아직 남은 제도·운영 과제를 함께 볼 수 있습니다.

## 함께 보면 좋을 자료

- [Ethereum 노드와 클라이언트](https://ethereum.org/en/developers/docs/nodes-and-clients/): 실행·합의 클라이언트와 공개망 노드 역할을 설명합니다.
- [ERC-20 표준](https://eips.ethereum.org/EIPS/eip-20): 토큰 인터페이스와 이벤트의 원문입니다.
- [Fabric 거래 흐름](https://hyperledger-fabric.readthedocs.io/en/latest/txflow.html): endorsement·ordering·validation 구조를 비교할 수 있습니다.

## 참고 자료

아래 자료는 2026년 10월 15일 확인했습니다. 릴리스 날짜는 UTC 기준이며, 계속 수정되는 문서와 특정 시점의 보고서를 구분했습니다.

- [Besu 문서](https://docs.besu-eth.org/), [소스 저장소](https://github.com/besu-eth/besu), [옵션](https://docs.besu-eth.org/public-networks/reference/options).
- [Ethereum 계정](https://ethereum.org/en/developers/docs/accounts/), [거래](https://ethereum.org/en/developers/docs/transactions/), [Solidity 컴파일러](https://docs.soliditylang.org/en/latest/using-the-compiler.html).
- [Besu·Teku 메인넷](https://docs.besu-eth.org/public-networks/tutorials/besu-teku-mainnet), [QBFT](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft), [IBFT](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/ibft), [무료 gas 구성](https://docs.besu-eth.org/private-networks/how-to/configure/free-gas), [로컬 permissioning](https://docs.besu-eth.org/private-networks/how-to/use-local-permissioning).
- [한강 논문](https://www.ecb.europa.eu/pub/pdf/sintra/ecb.forumcentbankpub2026_Shin_paper.sk.pdf): Ryu·Shin·Sung·Yun, ECB Forum 2026, 7월 1일 발표 후 수정본. 본문에 절·인쇄 쪽수 표시.
- [저장 형식](https://docs.besu-eth.org/public-networks/concepts/data-storage-formats), [history expiry](https://docs.besu-eth.org/public-networks/how-to/pre-merge-history-expiry), [병렬 거래 실행](https://docs.besu-eth.org/public-networks/concepts/parallel-transaction-execution), [상태 루트 병렬화](https://www.lfdecentralizedtrust.org/blog/optimizing-besu-performance-parallelizing-state-root-computation), [Nethermind 벤치마크 방법](https://www.nethermind.io/blog/getting-ethereum-ready-for-gigagas).
- [공식 릴리스](https://github.com/besu-eth/besu/releases): 본문에 연결한 25.6.0·25.7.0·26.1.0·26.2.0·26.4.0·26.5.0·26.6.0·26.7.0·26.9.0의 지원 범위와 변경 근거.
- [보안 권고](https://github.com/besu-eth/besu/security/advisories), [출시 이력 reconciliation](https://github.com/besu-eth/besu/pull/11378), [tracing 후속 보완](https://github.com/besu-eth/besu/commit/7f904a379cf5b59e7016118d64f6d68abadf69a2). 개별 수정의 태그 포함 비교는 본문 링크 참조.
- [LFDT 출범](https://www.lfdecentralizedtrust.org/announcements/linux-foundation-decentralized-trust-launches-with-17-projects-100-founding-members), [Besu 연례 보고](https://lf-decentralized-trust.github.io/governance/project-updates/2026/2026-annual-Besu/), [기관 채택 보고](https://www.lfdecentralizedtrust.org/ledger-insights-report-2026).
- [Eth Docker 운영자 관찰](https://www.reddit.com/r/ethstaker/comments/1vtatpn/eth_docker_2681_with_5_months_rolling_expiry/): 실험적 rolling expiry와 하위 서비스 receipt 의존성. 정확한 게시일은 단정하지 않았습니다.
- [태그된 메인넷 설정](https://github.com/besu-eth/besu/blob/26.9.0/config/src/main/resources/mainnet.json), [Sepolia 설정](https://github.com/besu-eth/besu/blob/26.9.0/config/src/main/resources/sepolia.json), [EVM 구현](https://github.com/besu-eth/besu/blob/26.9.0/evm/src/main/java/org/hyperledger/besu/evm/MainnetEVMs.java), [프로토콜 선택 코드](https://github.com/besu-eth/besu/blob/26.9.0/ethereum/core/src/main/java/org/hyperledger/besu/ethereum/mainnet/DefaultProtocolSchedule.java), [25.11.0](https://github.com/besu-eth/besu/releases/tag/25.11.0), [genesis milestone 문서](https://docs.besu-eth.org/public-networks/reference/genesis-items): 실행 규칙 구현과 체인 활성화의 구분 근거.
