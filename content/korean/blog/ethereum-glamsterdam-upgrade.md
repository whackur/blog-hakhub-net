---
title: "이더리움 Glamsterdam 업그레이드: ePBS와 BAL, 전체 EIP와 달라지는 운영"
meta_title: ""
description: "Glamsterdam의 블록 구성·병렬 검증·가스·네트워크 변경을 한 번에 살펴봅니다. ePBS와 BAL의 동작, 25개 EIP의 분류, 사용자·개발자·검증자에게 미치는 영향과 활성화 상태를 설명합니다."
date: 2026-10-17T12:00:00+09:00
lastmod: 2026-10-17T12:00:00+09:00
image: "/images/posts/ethereum-glamsterdam-upgrade/glamsterdam-cover.webp"
categories: ["Blockchain"]
tags: ["ethereum", "glamsterdam", "epbs", "block-access-lists", "evm", "validators"]
author: "whackur"
slug: "ethereum-glamsterdam-upgrade"
translationKey: "ethereum-glamsterdam-upgrade"
draft: false
---

Glamsterdam은 이더리움 L1의 처리 용량을 늘리기 위해 **블록을 만드는 절차와 받은 블록을 검증하는 절차를 함께 바꾸는 업그레이드**입니다. ePBS는 블록 제안자와 빌더 사이의 약속·공개·지급을 프로토콜 안에서 처리하고, BAL은 블록 실행 중 접근한 상태와 트랜잭션별 변경값을 전달해 수신 노드가 읽기와 검증을 병렬화하도록 돕습니다. 가스 재조정과 네트워크 개선도 이 목표를 뒷받침합니다. 다만 모든 거래의 수수료 인하나 일정한 TPS를 보장하는 변경은 아닙니다. [EIP-7773](https://eips.ethereum.org/EIPS/eip-7773)이 전체 범위를, [EIP-7732](https://eips.ethereum.org/EIPS/eip-7732)와 [EIP-7928](https://eips.ethereum.org/EIPS/eip-7928)이 두 핵심 메커니즘을 정의합니다.

## Amsterdam 실행 계층과 Gloas 합의 계층

이더리움의 실행 계층(Execution Layer, EL)은 트랜잭션을 실행하고 잔액·스토리지 같은 상태를 갱신합니다. 합의 계층(Consensus Layer, CL)은 검증자의 제안과 투표, 체인 선택을 담당합니다. Glamsterdam은 EL 업그레이드 **Amsterdam**과 CL 업그레이드 **Gloas**를 합친 이름입니다. 두 클라이언트가 맞물려 동작하므로 노드 운영자는 한쪽만 업데이트해서는 충분하지 않습니다. [공식 테스트넷 공지](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement)가 이 구분과 양쪽 업데이트 필요성을 설명합니다.

각 변경의 관계는 다음과 같습니다.

| 영역 | 기존 병목 또는 문제 | Glamsterdam의 대응 |
| --- | --- | --- |
| 블록 구성과 전달 | 빌더와 제안자의 거래에 신뢰가 필요한 중계가 끼고, 합의의 촉박한 시간 안에 실행까지 검증합니다. | ePBS가 교환과 지급을 프로토콜에 넣고 합의·실행 검증의 시점을 분리합니다. |
| 상태 읽기와 실행 | 실행해 보기 전에는 필요한 계정·슬롯과 중간 변경값을 알기 어렵습니다. | BAL이 실제 접근 위치와 트랜잭션 이후 값을 전달합니다. |
| 자원 가격과 상태 증가 | 더 큰 블록에서 저평가된 접근·쓰기·새 상태 생성이 노드 부담을 키웁니다. | 실행·상태 비용과 데이터 비용을 재조정하고 블록 집계를 바꿉니다. |
| 데이터 전파와 동기화 | 큰 영수증 목록, 블롭 중복 다운로드, 상태 복구가 통신 부담을 만듭니다. | P2P 메시지와 블롭풀, BAL 기반 동기화를 개선합니다. |

이 관계는 아래 EIP들의 설계 목적을 묶은 것입니다. 실제 처리량은 클라이언트 구현, 하드웨어, 블록의 작업 구성과 네트워크 조건에 따라 달라집니다.

## 2026년 10월 17일 기준 상태

**명세의 표준화 상태, 업그레이드 포함 결정, 네트워크 활성화는 별개입니다.** 2026년 10월 17일 KST에 직접 확인한 ethereum/EIPs의 [고정 커밋 `deb8f0d`](https://github.com/ethereum/EIPs/tree/deb8f0d3ea9167bd30775fb3d45d052fce651d56/EIPS)을 기준으로 정리했습니다.

| 구분 | 확인한 내용 |
| --- | --- |
| 포함 범위 | EIP-7773의 Scheduled for Inclusion(SFI, 포함 예정)에 Core 18개가 있습니다. Other EIPs에는 Networking 5개와 Informational 2개가 별도로 있습니다. |
| 문서 상태 | 메타 EIP-7773과 Core EIP-7688은 `Review`입니다. 나머지 24개 문서의 raw 메타데이터는 `Last Call`입니다. `Final` 확정이나 모든 네트워크 적용을 뜻하지 않습니다. |
| Sepolia 일정 | epoch 353,024, UNIX 1,791,294,816, 2026년 10월 6일 13:53:36 UTC가 명시돼 있습니다. |
| Hoodi·메인넷 일정 | EIP-7773의 활성화 시각 칸은 비어 있습니다. 테스트넷 공지도 이 둘의 일정을 정하지 않았다고 명시합니다. |
| 메인넷 예상 시기 | [ethereum.org 로드맵](https://ethereum.org/en/roadmap/glamsterdam/)은 Q4 2026을 예상하며 날짜는 미확정으로 표시합니다. 페이지에 표시된 최종 갱신일은 2026년 9월 14일입니다. 확정 활성화 공지와 구분해야 합니다. |

Sepolia의 공지 시각은 지났습니다. 그러나 시각이 지났다는 사실만으로 성공적인 활성화나 특정 RPC의 구현 버전을 확인할 수는 없습니다. 아래 설명은 고정한 명세를 기준으로 하며, 실제 체인의 포크 전후 실행 시험 결과는 아닙니다. 운영 시에는 대상 네트워크의 공지, 클라이언트 릴리스 노트, 실제 노드 상태를 함께 확인해야 합니다. [EIP-7773 원문](https://github.com/ethereum/EIPs/blob/deb8f0d3ea9167bd30775fb3d45d052fce651d56/EIPS/eip-7773.md), [테스트넷 공지](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement)

## ePBS가 블록 구성과 지급을 프로토콜에 넣습니다

블록 제안자는 특정 슬롯의 블록을 제안하도록 선택된 검증자입니다. 빌더는 트랜잭션을 선택하고 순서를 정해 실행 페이로드를 구성합니다. 페이로드에는 실제로 실행할 트랜잭션과 실행 결과를 검증하는 정보가 담깁니다. 이 분업을 proposer-builder separation(PBS)이라고 합니다. 외부 중계자에게 교환을 맡기던 방식에서, [EIP-7732](https://eips.ethereum.org/EIPS/eip-7732)의 enshrined PBS(ePBS)는 그 교환을 합의 프로토콜이 처리하도록 바꿉니다.

1. **빌더가 서명한 입찰을 만듭니다.** 나중에 공개할 실행 블록의 해시와 제안자에게 지급할 값을 약속합니다.
2. **제안자가 약속을 비콘 블록에 넣습니다.** 전체 실행 페이로드 대신 서명된 약속을 포함합니다. 프로토콜은 지급값을 빌더의 비콘 체인 잔액에서 차감하고 제안자가 지정한 실행 계층 주소로 인출되도록 처리합니다.
3. **빌더가 실행 페이로드를 공개합니다.** Payload Timeliness Committee(PTC)로 선정된 검증자들은 약속한 페이로드가 제때 공개됐는지, 대응하는 블롭 데이터가 가용했는지를 증언합니다.
4. **실행의 올바름은 별도로 검증합니다.** PTC의 적시성 증언에 전체 EVM 실행 검증을 요구하지 않습니다. 실행 검증을 다음 비콘 블록 검증 시점까지 분리해, 합의 투표 직전의 촉박한 경로에서 실행 부담을 덜어냅니다.

중요한 차이는 검증을 생략하는 것이 아니라 시간을 나누는 데 있습니다. 제안자의 약속 선택, 빌더의 공개, 실행 결과 검증이 서로 다른 단계가 됩니다. 지갑과 탐색기도 페이로드를 보았다는 사실, 후속 블록에서 실행이 검증됐다는 사실, 합의의 최종성(finality)을 같은 상태로 표시해서는 안 됩니다. 이 구분은 [EIP-7732의 delayed validation 설명](https://eips.ethereum.org/EIPS/eip-7732#delayed-validation)에 근거합니다.

ePBS는 MEV(maximal extractable value), 즉 거래의 선택·순서·포함 여부에서 얻는 가치를 없애지 않습니다. 빌더는 여전히 거래를 구성합니다. 프로토콜이 기본 교환과 지급을 맡아 신뢰 부담을 줄여도, 입찰 전달·빌더 탐색·운영 정책을 위한 선택적 미들웨어까지 모두 사라지는 것은 아닙니다. 명세에는 외부에서 이행할 신뢰 기반 지급 약속도 허용됩니다. 따라서 ePBS를 모든 중계 서비스나 빌더 집중 문제의 자동 해결책으로 볼 수는 없습니다. [EIP-7732](https://eips.ethereum.org/EIPS/eip-7732)

빌더의 등록·충전·종료 경로도 함께 읽어야 합니다. [EIP-8282](https://eips.ethereum.org/EIPS/eip-8282)는 전용 실행 계층 계약과 요청 유형을 도입합니다. 포크 전환 시 초기 빌더를 편입하는 예외는 유지하지만, 포크 이후 일반 등록은 전용 빌더 예치 경로를 씁니다. EIP-7732의 초기 설명만 보고 검증자 예치 계약을 빌더 예치에 그대로 쓰면 안 됩니다. 종료 권한도 계속 입찰에 쓰는 BLS 키가 아니라 빌더의 `execution_address`를 기준으로 확인합니다.

## BAL은 실제 접근과 트랜잭션 이후 값을 전달합니다

[EIP-7928](https://eips.ethereum.org/EIPS/eip-7928)의 Block-Level Access List(BAL)는 블록 전체의 실행 기록입니다. 사용자가 선택적으로 제출하는 EIP-2930 트랜잭션 액세스 리스트와 역할이 다릅니다. 사용자가 미리 적은 주소를 그대로 옮기는 것이 아니라, **생산자가 실행 중 실제로 접근한 계정·스토리지 위치와 트랜잭션이 끝난 뒤의 변경값을 기록하고 수신자가 그 정확성을 검증합니다.**

### 생산자가 실행하면서 기록하는 내용

블록을 만드는 EL은 트랜잭션을 실행하면서 다음을 수집합니다.

- 접근한 계정과 스토리지 키: 읽기만 하고 값을 바꾸지 않은 항목도 포함합니다.
- 스토리지 변경값과 계정의 잔액·nonce·코드 변경값: 트랜잭션 이후 값을 해당 순서 인덱스와 연결합니다.
- 블록의 시스템 처리: 실행 전 처리는 인덱스 0, 트랜잭션은 1부터 n, 실행 후 처리와 인출 등은 n+1로 구분합니다.

BAL은 모든 opcode의 중간 실행 흔적을 보내는 trace가 아닙니다. 예를 들어 스토리지 읽기 전용 키는 별도로 나열하고, 같은 슬롯의 변경은 트랜잭션 이후 값으로 정리합니다. 리버트된 호출에서 실제 읽은 위치와 최종 반영되지 않은 쓰기도 구분해야 합니다. 실행하지 않은 액세스 리스트 선언을 자동으로 포함하거나, 최종 상태에 반영되지 않은 쓰기를 확정 변경처럼 보내서는 안 됩니다. 명세의 접근 조건·정렬·중복 제거 규칙이 이 기록을 결정합니다. [EIP-7928의 scope와 state change tracking](https://eips.ethereum.org/EIPS/eip-7928#scope-and-inclusion)

### 수신 노드가 미리 읽고 병렬로 검증합니다

수신자는 어떤 데이터가 필요한지 BAL에서 먼저 알 수 있으므로 디스크에서 계정과 슬롯을 병렬로 가져옵니다. 트랜잭션별 변경값은 각 트랜잭션에 필요한 선행 상태를 구성하는 데 쓰입니다. 클라이언트는 이를 활용해 트랜잭션 실행 검증과 상태 루트 계산도 병렬화할 수 있습니다. 상태 루트는 전체 상태를 대표하는 암호학적 해시값입니다. [EIP-7928](https://eips.ethereum.org/EIPS/eip-7928)

가령 같은 블록의 A가 슬롯 `x`를 5로 바꾸고 B가 그 값을 읽어 6으로 만든다고 합시다. B는 A에 의존합니다. BAL에 A 이후의 `x=5`가 있으면 수신자는 B가 읽어야 할 값을 먼저 제공해 B의 실행 검증을 준비할 수 있습니다. 동시에 A가 정말 5를 만들었는지 검증해야 합니다. A의 결과가 거짓이면 그 값으로 실행한 B가 일관돼 보여도 블록은 유효하지 않습니다. BAL은 이러한 선행 값을 전달하므로, 이점이 서로 다른 슬롯을 쓰는 거래에만 한정되지는 않습니다. 그렇다고 상태 의존성이 없어지거나 모든 작업이 같은 속도로 병렬화되는 것도 아닙니다.

### 해시 일치와 실행 정확성을 모두 확인합니다

헤더의 `block_access_list_hash`는 RLP로 인코딩한 BAL의 Keccak-256 해시입니다. 전체 BAL은 EL에서 블록과 별도로 저장하며 Engine API의 실행 페이로드 필드로 전달합니다. 해시는 전달받은 데이터가 커밋된 데이터와 같은지 확인하는 장치입니다. 내용이 올바른 실행 결과라는 증명까지 대신하지는 않습니다. [EIP-7928의 block structure](https://eips.ethereum.org/EIPS/eip-7928#block-structure-modification)

수신 EL은 실제 접근과 변경값을 계산해 제공된 BAL과 일치하는지 확인해야 합니다. 누락되거나 불필요하게 추가된 항목도 블록 무효 사유입니다. 구현은 실행 중 가상 BAL을 만들어 해시를 대조하는 방법을 쓸 수 있습니다. 생산자가 써 준 결과를 검증 없이 신뢰하는 구조가 아닙니다. [EIP-7928의 state transition 검증](https://eips.ethereum.org/EIPS/eip-7928#state-transition-function)

BAL의 변경값만 적용해 상태를 따라가는 executionless state update는 동기화에도 유용합니다. 이때도 검증된 체인 문맥과 헤더 커밋이 필요합니다. [EIP-8189](https://eips.ethereum.org/EIPS/eip-8189)는 BAL 기반 상태 복구에서 블록 순서대로 적용하고, 각 해시와 최종 상태 루트를 확인하도록 요구합니다. 이 동기화 경로를 새 블록의 실행 유효성 검증을 폐지하는 규칙으로 읽으면 안 됩니다.

![ePBS의 약속·페이로드 공개와 BAL의 실행 기록·병렬 검증을 나누어 보여 주는 흐름도](/images/posts/ethereum-glamsterdam-upgrade/block-construction-and-validation.svg)

ePBS는 블록 구성과 공개 시점을, BAL은 실행에 필요한 데이터와 그 검증을 다룹니다. 두 기능 모두 실행 검증을 유지하며, 그림은 슬롯 내부의 정확한 시간표를 나타내지 않습니다.

## 전체 EIP 목록

다음 25개는 [EIP-7773](https://github.com/ethereum/EIPs/blob/deb8f0d3ea9167bd30775fb3d45d052fce651d56/EIPS/eip-7773.md)의 세 목록을 빠짐없이 옮겨 역할별로 묶은 것입니다. 앞의 18개는 SFI Core, 뒤의 7개는 Other EIPs입니다. **25개 전체를 같은 순간에 포크로 활성화하는 합의 규칙이라고 부르면 부정확합니다.**

### SFI Core의 블록 구성·검증·합의 변경 6개

| 번호 | EIP와 명세 제목 | 역할과 주의점 |
| --- | --- | --- |
| 1 | [EIP-7732: Enshrined Proposer-Builder Separation](https://eips.ethereum.org/EIPS/eip-7732) | 빌더의 약속과 공개, 제안자 지급을 프로토콜로 처리하고 합의·실행 검증 시점을 분리합니다. PTC는 실행 전체가 아닌 적시성과 데이터 가용성을 증언합니다. |
| 2 | [EIP-7928: Block-Level Access Lists](https://eips.ethereum.org/EIPS/eip-7928) | 실제 상태 접근과 트랜잭션 이후 변경값을 전달합니다. 병렬 읽기·실행 검증·상태 루트 계산을 지원하며 BAL 자체의 정확성도 검증합니다. |
| 3 | [EIP-7688: Forward compatible consensus data structures](https://eips.ethereum.org/EIPS/eip-7688) | SSZ의 progressive 자료구조로 머클화 방식을 바꿔 이후 변경에서 증명 호환성을 높입니다. 대상 타입의 직렬화 바이트는 유지하지만 머클화가 바뀌므로 증명 도구는 전환을 반영해야 합니다. |
| 4 | [EIP-8045: Exclude slashed validators from proposing](https://eips.ethereum.org/EIPS/eip-8045) | 슬래싱된 검증자를 제안자 선택에서 제외해, 어차피 무효가 될 제안으로 슬롯을 놓치는 문제를 줄입니다. |
| 5 | [EIP-8061: Increase exit and consolidation churn](https://eips.ethereum.org/EIPS/eip-8061) | 종료 처리량을 대략 4배로 늘리고 전체 지분에 비례하도록 복원하며 통합 처리량은 대략 2배로 늘립니다. 활성화 상한은 유지합니다. 더 짧아지는 weak subjectivity 기간은 동기화 운영에도 영향을 줍니다. |
| 6 | [EIP-8282: Builder Execution Requests](https://eips.ethereum.org/EIPS/eip-8282) | 빌더 예치·충전·종료 전용 계약과 요청을 추가합니다. 포크 전환의 초기 편입 예외와 포크 이후 일반 경로를 구분해야 합니다. |

### SFI Core의 가스·데이터·상태 비용 변경 6개

| 번호 | EIP와 명세 제목 | 역할과 주의점 |
| --- | --- | --- |
| 7 | [EIP-2780: Resource-based intrinsic transaction gas](https://eips.ethereum.org/EIPS/eip-2780) | 고정 기본 비용을 자원별 항목과 intrinsic·런타임 비용으로 나눕니다. 다른 기존 일반 계정으로 보내는 단순 양의 ETH 전송은 실행 가스 21,000을 유지합니다. 모든 전송이 12,000이 되는 규칙이 아닙니다. |
| 8 | [EIP-7778: Block Gas Accounting without Refunds](https://eips.ethereum.org/EIPS/eip-7778) | 환급이 블록 한도 집계를 줄이지 않게 합니다. 사용자의 적격 가스 환급은 유지하며, 사용자 정산과 블록이 감당한 작업량을 구분합니다. |
| 9 | [EIP-7976: Increase Calldata Floor Cost](https://eips.ethereum.org/EIPS/eip-7976) | calldata의 바닥 비용을 0·비0 바이트 모두 64 gas로 높입니다. 데이터가 많은 거래의 최저 비용 규칙이며, 모든 거래의 모든 바이트를 무조건 새 단가로 청구한다는 뜻은 아닙니다. |
| 10 | [EIP-7981: Increase Access List Cost](https://eips.ethereum.org/EIPS/eip-7981) | 사용자가 제출한 액세스 리스트의 데이터 크기에 바이트당 64 gas의 추가 비용을 붙여 calldata 바닥 비용 우회를 막습니다. 수신 노드가 받는 BAL과는 다른 목록입니다. |
| 11 | [EIP-8037: State Creation Gas Cost Increase](https://eips.ethereum.org/EIPS/eip-8037) | 새 상태의 바이트당 비용과 별도 상태 가스 계량·리저버를 도입합니다. 150M 기준 블록 가스 한도에서 연평균 120 GiB 상태 증가를 목표로 가격을 산출하며, 실제 성장량의 강제 상한은 아닙니다. |
| 12 | [EIP-8038: State-access gas cost update](https://eips.ethereum.org/EIPS/eip-8038) | 콜드 계정 접근 비용을 높이고 계정·스토리지 쓰기 비용을 명시적으로 나눕니다. `EXTCODESIZE`·`EXTCODECOPY`의 두 번째 DB 읽기를 반영하며 새 상태 생성 비용은 EIP-8037이 맡습니다. |

이 변경들은 확장에 필요한 자원 비용을 맞추는 작업입니다. 특히 EIP-8037의 상태 가스는 기존 `gasLimit`과 무관하게 무료로 주어지는 예산이 아닙니다. 하나의 트랜잭션 예산 안에서 실행 가스와 별도 상태 리저버를 다루고, `gasleft()`는 리저버 잔량을 보여 주지 않습니다. Solidity의 저장·삭제·고정 내부 호출 예시는 별도 글 [Glamsterdam의 새 가스 모델](/blog/glamsterdam-gas-model/)에서 다룹니다.

### SFI Core의 EVM·개발 도구 변경 6개

| 번호 | EIP와 명세 제목 | 역할과 주의점 |
| --- | --- | --- |
| 13 | [EIP-7708: ETH transfers emit a log](https://eips.ethereum.org/EIPS/eip-7708) | 명세가 정한 양의 ETH 전송에 프로토콜 로그를 남깁니다. 트랜잭션·`CALL`·`SELFDESTRUCT`의 다른 계정 전송과 `CREATE`·`CREATE2`의 값 전달이 대상입니다. 수수료·기본 수수료 소각·인출까지 모든 잔액 변화를 기록하지는 않습니다. |
| 14 | [EIP-7843: SLOTNUM opcode](https://eips.ethereum.org/EIPS/eip-7843) | 현재 슬롯 번호를 읽는 opcode를 추가합니다. 블록 번호와 슬롯 번호를 구분하고, 슬롯 길이를 컨트랙트에 고정해 계산하는 의존을 줄입니다. |
| 15 | [EIP-7954: Increase Maximum Contract Size](https://eips.ethereum.org/EIPS/eip-7954) | 런타임 코드 상한을 24 KiB에서 64 KiB로, initcode 상한을 48 KiB에서 128 KiB로 늘립니다. 크기 허용과 실제 배포 가스 충족은 별개입니다. |
| 16 | [EIP-7997: Deterministic Factory Contract](https://eips.ethereum.org/EIPS/eip-7997) | 정해진 `CREATE2` 팩토리의 존재를 공식 요건으로 만듭니다. 같은 주소 배포에 필요한 기반이며, 모든 EVM 체인이 자동 채택하거나 임의의 배포 결과가 같아지는 보장은 아닙니다. |
| 17 | [EIP-8024: Backward compatible SWAPN, DUPN, EXCHANGE](https://eips.ethereum.org/EIPS/eip-8024) | 더 깊은 스택 항목에 접근하는 명령을 추가해 컴파일러의 스택 배치를 돕습니다. 기존 배포 바이트코드를 자동으로 다시 최적화하지는 않습니다. |
| 18 | [EIP-8246: Remove SELFDESTRUCT Burn](https://eips.ethereum.org/EIPS/eip-8246) | 같은 트랜잭션에서 생성·자기파괴하는 계약 등에 남아 있던 ETH 소각 경로를 제거합니다. 해당 정리 대상의 잔액을 보존하며, EIP-6780 이전의 광범위한 코드·스토리지 삭제를 복원하지 않습니다. |

### Other EIPs의 Networking 5개

| 번호 | EIP와 명세 제목 | 역할과 주의점 |
| --- | --- | --- |
| 19 | [EIP-7975: eth/70 - partial block receipt lists](https://eips.ethereum.org/EIPS/eip-7975) | 영수증 목록 일부를 요청하도록 해 큰 블록의 목록이 메시지 크기 제한을 넘어서 동기화가 막히는 문제를 줄입니다. |
| 20 | [EIP-8070: eth/72 - Sparse Blobpool](https://eips.ethereum.org/EIPS/eip-8070) | 일부 블롭은 전체를, 나머지는 CL custody에 맞는 셀을 표본 다운로드하도록 블롭풀을 바꿉니다. 전체 복제의 대역폭 부담을 줄이려는 설계이며 데이터 가용성 검사를 없애지 않습니다. |
| 21 | [EIP-8136: Cell-Level Deltas for Data Column Broadcast](https://eips.ethereum.org/EIPS/eip-8136) | 이미 있는 셀을 다시 받는 대신 필요한 셀만 교환하는 PeerDAS 최적화입니다. 하위 호환이며 하드포크 없이 점진 배포할 수 있습니다. 미지원 피어와는 전체 컬럼 교환을 유지합니다. |
| 22 | [EIP-8159: eth/71 - Block Access List Exchange](https://eips.ethereum.org/EIPS/eip-8159) | 피어 사이에 BAL을 요청·응답하는 메시지를 추가합니다. 실시간 Engine API 전달 외에 과거 블록과 동기화용 BAL을 구하는 경로입니다. |
| 23 | [EIP-8189: snap/2 - BAL-Based State Healing](https://eips.ethereum.org/EIPS/eip-8189) | snap 동기화의 상태 복구에 BAL을 적용합니다. 헤더 커밋·블록 순서·최종 상태 루트를 검증하며, 이전 `snap/1`과 별도 버전을 협상합니다. |

### Other EIPs의 Informational 2개

| 번호 | EIP와 명세 제목 | 역할과 주의점 |
| --- | --- | --- |
| 24 | [EIP-7904: Compute Gas Cost Analysis](https://eips.ethereum.org/EIPS/eip-7904) | BAL 관련 최적화를 반영한 클라이언트의 연산·프리컴파일 성능 분석입니다. 분석 대상이 100 Mgas/s(초당 1억 gas) 목표를 충족한다고 결론 내리며 연산 가스 재조정을 권고하지 않습니다. 네트워크 TPS 측정이나 새 opcode 가격표가 아닙니다. |
| 25 | [EIP-8261: Gas Limit Schedule](https://eips.ethereum.org/EIPS/eip-8261) | Gloas 이후 선택적 CL 설정으로 epoch별 기본 가스 선호값과 권장 최대값을 관리합니다. 운영자 설정을 허용하며 권장값 초과 블록도 그 이유만으로 무효가 되지 않습니다. 합의상 강제 상한이나 가스 한도의 즉시 상승 규칙이 아닙니다. |

## 사용자·개발자·운영자가 확인할 변화

### 사용자와 지갑

메인넷 ETH 보유자는 Sepolia 공지만으로 자산을 옮기거나 토큰을 교환할 필요가 없습니다. [공식 FAQ](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement#faq)도 메인넷은 별도 공지 대상이라고 설명합니다. 실제 체감 변화는 지갑과 RPC가 새 가스 추정을 지원하고 대상 네트워크가 해당 규칙을 적용한 뒤 나타납니다.

거래 비용은 작업에 따라 다릅니다. 데이터가 많거나 새 상태를 만드는 거래는 더 비싸질 수 있습니다. 일부 가벼운 거래의 기본 비용이 낮아져도 일반 ETH 전송 모두가 싸진다는 뜻은 아닙니다. 가스 사용량 변화와 시장 수요가 정하는 가스당 가격을 구분해야 합니다. L1 개선을 모든 L2 수수료의 일괄 인하로 환산할 수도 없습니다. [EIP-2780](https://eips.ethereum.org/EIPS/eip-2780), [EIP-7976](https://eips.ethereum.org/EIPS/eip-7976), [EIP-8037](https://eips.ethereum.org/EIPS/eip-8037)

### 애플리케이션·인덱서·컴파일러

개발자는 대상 포크를 지원하는 환경에서 가스 추정과 실패 경로를 다시 확인해야 합니다. 고정 내부 호출 가스, `gasleft()` 기반 분기, 배포 코드 크기와 배포 예산이 주요 점검 대상입니다. 새 opcode와 큰 코드 상한은 컴파일러·도구가 지원하고 대상 체인이 활성화한 뒤에 사용해야 합니다. EIP-7954의 크기 완화가 EIP-8037의 상태 비용을 상쇄하는 규칙은 아닙니다. [EIP-8037](https://eips.ethereum.org/EIPS/eip-8037), [EIP-8024](https://eips.ethereum.org/EIPS/eip-8024)

인덱서는 EIP-7708의 시스템 발신 ETH 로그를 기존 ERC-20 로그와 구분하고, 자체 추적 데이터와 중복 합산하지 않도록 해야 합니다. 수수료와 인출은 별도 집계가 필요합니다. SSZ 증명 생성·검증 도구는 EIP-7688의 머클화 전환을 확인해야 하며, 같은 주소 배포 도구는 체인별 팩토리·initcode·salt와 지원 상태를 확인해야 합니다. [EIP-7708](https://eips.ethereum.org/EIPS/eip-7708), [EIP-7688](https://eips.ethereum.org/EIPS/eip-7688), [EIP-7997](https://eips.ethereum.org/EIPS/eip-7997)

EVM 파생 체인은 자체 채택 여부도 따로 판단해야 합니다. 특히 EIP-8246은 `SELFDESTRUCT` 소각을 사용하는 OP Stack 계열의 출금 회계에 별도 이행 계획이 필요하다고 명시합니다. 이더리움 메인넷의 변경을 모든 L2에 그대로 적용할 수 있다는 전제는 위험합니다. [EIP-8246의 하위 호환성](https://eips.ethereum.org/EIPS/eip-8246#backwards-compatibility)

### 노드·검증자·빌더

운영자는 네트워크별로 호환되는 EL·CL 릴리스를 확인하고, 검증자의 비콘 노드와 Validator Client를 모두 갱신해야 합니다. ePBS의 PTC 의무, 빌더 연결과 페이로드 공개·검증 상태, Engine API 호환성도 점검 대상입니다. BAL을 받는다고 모든 클라이언트가 동일한 병렬 실행 성능을 내는 것은 아닙니다. 디스크 I/O·CPU·메모리·대역폭과 실제 실행 시간을 함께 관찰해야 합니다. [공식 운영 안내](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement), [EIP-7928](https://eips.ethereum.org/EIPS/eip-7928)

가스 한도는 문서에 큰 숫자가 있다고 자동으로 바뀌지 않습니다. EIP-8261은 지원 클라이언트의 기본값과 권고를 관리하는 선택적 설정이며, 실제 한도는 블록당 약 ±1/1024의 기존 조정 규칙을 따릅니다. EIP-8061의 종료·통합 처리량 증가는 즉시 인출을 보장하지 않으며, 명세의 계산에서 weak subjectivity 기간을 약 7일로 줄입니다. 이 기간은 오랫동안 오프라인이던 노드가 다시 동기화할 때 신뢰할 최신 체크포인트를 확보해야 하는 운영 기준과 관련됩니다. 오프라인 복귀·체크포인트·BAL 보관 정책은 적용된 명세와 클라이언트 지침을 함께 확인해야 합니다. [EIP-8261](https://eips.ethereum.org/EIPS/eip-8261), [EIP-8061](https://eips.ethereum.org/EIPS/eip-8061), [EIP-7928](https://eips.ethereum.org/EIPS/eip-7928)

빌더는 EIP-8282의 전용 예치·종료 경로와 서명 검증을 확인해야 합니다. 첫 예치의 잘못된 proof-of-possession은 원금을 잠글 수 있고, 종료는 `execution_address` 권한과 대기 잔액 조건을 따릅니다. 일반 사용자의 할 일은 아니지만 빌더 운영에서 빠뜨릴 수 없는 변경입니다. [EIP-8282의 보안 고려사항](https://eips.ethereum.org/EIPS/eip-8282#security-considerations)

Glamsterdam의 성과를 판단할 때는 목표 가스 한도 하나보다 블록 실행 검증 시간, 상태 증가, 전파 지연과 운영 안정성을 함께 봐야 합니다. ePBS가 검증 시간을 나누고 BAL이 필요한 상태 데이터를 먼저 제공하는 설계는 더 큰 블록을 처리할 기반입니다. 그 기반이 실제 용량으로 이어지는 정도는 구현과 네트워크 운영에서 확인할 문제입니다.

## 함께 보면 좋을 자료

- [Glamsterdam의 새 가스 모델](/blog/glamsterdam-gas-model/): 저장·삭제·고정 내부 호출을 Solidity 사례로 확인하는 심화 글입니다.
- [Glamsterdam 로드맵](https://ethereum.org/en/roadmap/glamsterdam/): 업그레이드의 목표와 공개된 진행 상태를 설명합니다.
- [EIP-7928 명세](https://eips.ethereum.org/EIPS/eip-7928): BAL의 자료구조·접근 조건·검증 규칙을 확인할 수 있습니다.

## 참고 자료

조회 기준은 2026년 10월 17일 KST입니다. 위 표의 각 EIP 링크가 해당 항목의 1차 출처입니다. 표준화 상태와 포함 목록은 아래 고정 원문을 기준으로 하며 이후 바뀔 수 있습니다.

- [EIP-7773 고정 원문](https://github.com/ethereum/EIPs/blob/deb8f0d3ea9167bd30775fb3d45d052fce651d56/EIPS/eip-7773.md): SFI·Other EIPs 분류와 활성화 일정입니다.
- [ethereum/EIPs 고정 스냅샷](https://github.com/ethereum/EIPs/tree/deb8f0d3ea9167bd30775fb3d45d052fce651d56/EIPS): 표에 연결한 25개 명세의 제목·메타데이터·본문을 대조한 버전입니다.
- [Glamsterdam Testnet Announcement](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement): Ethereum Foundation의 Sepolia 공지와 운영 안내입니다.
- [Glamsterdam](https://ethereum.org/en/roadmap/glamsterdam/): ethereum.org의 개요와 미확정 메인넷 예상 시기입니다.
