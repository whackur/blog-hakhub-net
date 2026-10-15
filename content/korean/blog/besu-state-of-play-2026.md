---
title: "2026년 Besu 현황과 운영자가 확인할 변화"
meta_title: "Besu 2026 기술 현황: 실행 클라이언트, QBFT, 저장소와 업그레이드"
description: "2026년 10월 15일 기준 Besu의 릴리스·거버넌스·성능·저장소 변화를 살펴보고 메인넷과 허가형 네트워크 운영 시 확인할 항목을 정리합니다."
date: 2026-10-15T11:37:00+09:00
lastmod: 2026-10-15T11:37:00+09:00
image: "/images/posts/besu-state-of-play-2026/cover.png"
categories: ["Blockchain"]
tags: ["besu", "ethereum", "execution-client", "qbft", "enterprise-blockchain"]
author: "whackur"
translationKey: "besu-state-of-play-2026"
draft: false
---

Besu를 오래된 Hyperledger 튜토리얼로 접했다면 지금의 지원 범위를 다시 확인할 필요가 있습니다. 이름과 저장소 주소가 바뀌었고, Ethereum 메인넷 실행 성능을 개선하는 동안 일부 기업용 기능은 본체에서 빠졌습니다. 허가형 네트워크 지원은 계속되지만, 과거 설정 파일을 그대로 가져오면 같은 시스템이 재현된다고 기대하기 어렵습니다.

이 글의 확인 기준은 **2026년 10월 15일 KST**입니다. 공식 GitHub에서 조회한 최신 정식 릴리스는 **26.9.0**이며 발행 시각은 9월 25일 22:22 UTC, 한국 시간으로 9월 26일입니다. 릴리스 날짜는 아래에서 UTC로 통일합니다. 보안 권고에는 10월 14일에 공개된 자료도 있습니다. 조회일과 각 자료가 설명하는 시점은 구분해야 합니다. [공식 릴리스](https://github.com/besu-eth/besu/releases), [보안 권고](https://github.com/besu-eth/besu/security/advisories)

읽으면서 기억할 변화는 세 가지입니다. Besu는 메인넷과 허가형 체인에서 서로 다른 합의 구성을 사용합니다. 성능 개선은 이더리움 가상 머신(Ethereum Virtual Machine, EVM) 실행뿐 아니라 상태 접근과 상태 루트 계산까지 이어집니다. 업그레이드는 바이너리 교체에 더해 Java, 원격 프로시저 호출(Remote Procedure Call, RPC) 형식, 저장소, 플러그인 호환성을 함께 점검하는 작업이 됐습니다.

## 현재 이름과 프로젝트의 소속

현재 공식 이름은 Besu이며 LF Decentralized Trust 프로젝트입니다. Linux Foundation의 2024년 9월 16일 [출범 발표](https://www.lfdecentralizedtrust.org/announcements/linux-foundation-decentralized-trust-launches-with-17-projects-100-founding-members)는 Hyperledger Foundation 산하 기술들이 새 조직의 프로젝트가 되며 Hyperledger Besu가 Besu라는 이름을 쓴다고 설명했습니다. 2026년에 갑자기 새 클라이언트가 생긴 것은 아닙니다.

현재 소스 저장소는 [`besu-eth/besu`](https://github.com/besu-eth/besu)입니다. [26.4.0 릴리스](https://github.com/besu-eth/besu/releases/tag/26.4.0)는 `hyperledger/besu`에서 이전했고 기존 GitHub 링크는 리디렉션된다고 명시합니다. 문서의 현재 주소도 [docs.besu-eth.org](https://docs.besu-eth.org/)입니다. 옛 이름이 붙은 글이 검색되는 것 자체는 오류가 아니지만, 그 글의 설치 명령과 기능 목록까지 현재 유효하다는 뜻은 아닙니다.

이름, 재단 소속, 코드 유지보수 조직은 따로 봐야 합니다. 오픈소스 재단이 프로젝트를 호스팅한다는 사실만으로 여러 회사가 같은 비중으로 코드를 유지보수한다고 판단할 수는 없습니다. 뒤에서 살펴볼 유지보수자 분포가 운영 지속성을 평가할 때 더 직접적인 자료입니다.

## 메인넷과 허가형 체인에서 맡는 역할

Besu는 Apache 2.0 라이선스로 공개된 Java 기반 Ethereum 클라이언트입니다. EVM으로 트랜잭션을 실행하고 상태를 갱신하며, 노드 운영을 위한 명령줄 인터페이스(CLI)와 JSON-RPC를 제공합니다. Solidity 애플리케이션이 익숙한 Ethereum 도구와 API를 활용할 수 있는 이유도 이 실행 환경에 있습니다. 다만 EVM 호환성이 모든 RPC 세부 동작이나 배포 구성이 같다는 보증은 아닙니다. [공식 소개](https://docs.besu-eth.org/)

Ethereum 메인넷에서 Besu는 실행 클라이언트(Execution Layer, EL)입니다. Teku 같은 합의 클라이언트(Consensus Layer, CL)와 Engine API로 연결해 실행 payload를 만들고 검증합니다. 두 클라이언트는 JSON Web Token(JWT) 인증 정보를 공유합니다. 스테이킹을 하려면 합의 측에 validator 역할도 구성해야 합니다. Besu 프로세스만 실행했다고 Ethereum validator가 완성되지는 않습니다. [Besu와 Teku 메인넷 구성](https://docs.besu-eth.org/public-networks/tutorials/besu-teku-mainnet)

허가형 네트워크에서는 구성이 달라집니다. Besu validator들이 Quorum Byzantine Fault Tolerance(QBFT) 또는 Istanbul Byzantine Fault Tolerance(IBFT) 2.0으로 블록 합의에 참여합니다. 이 경로에 Ethereum 메인넷용 beacon 합의 클라이언트를 추가할 필요는 없습니다. 공식 문서는 새 허가형 구성에 QBFT를 권장하며, [IBFT 2.0 문서](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/ibft)도 계속 제공합니다. [QBFT 문서](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft)

![메인넷에서는 합의 클라이언트가 Engine API로 Besu 실행 계층과 연결되고, 허가형 체인에서는 Besu validator들이 Quorum Byzantine Fault Tolerance(QBFT) 또는 Istanbul Byzantine Fault Tolerance(IBFT) 2.0으로 합의하는 구성도. 서명·RPC 접근제어·데이터 프라이버시는 별도로 설계합니다.](/images/posts/besu-state-of-play-2026/besu-deployment-roles.svg)

*공식 메인넷·QBFT 문서를 바탕으로 직접 그린 개념도입니다. 공통 실행 기능과 서로 다른 합의 경계를 표시했으며, 외부 제품이나 플러그인을 필수 구성으로 지정하지 않았습니다.* [SVG 원본 확대](/images/posts/besu-state-of-play-2026/besu-deployment-roles.svg)

QBFT는 승인된 validator 집합을 전제로 합니다. 문서는 블록에 validator의 3분의 2 이상 서명이 필요하며 3분의 1을 넘는 validator가 참여하지 않으면 블록 생성이 멈춘다고 경고합니다. 네 대짜리 구성에서 한 대씩 순서대로 교체하더라도, 남은 노드 하나가 이미 느리거나 연결이 끊겼다면 정상적인 rolling upgrade가 되지 않습니다. 실제 참여 상태를 확인하는 절차가 필요합니다. [QBFT 운영 제약](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft)

역할을 더 나눌 필요도 있습니다. 애플리케이션의 트랜잭션 서명, 노드의 peer-to-peer(P2P) 신원, QBFT validator 키, 메인넷 스테이킹 키는 같은 개념이 아닙니다. 공식 소개가 클라이언트 내부의 애플리케이션 키 관리를 제공하지 않고 Web3Signer 같은 외부 서명기를 안내한다고 해서, Besu 노드에 필요한 모든 키가 사라지는 것은 아닙니다. 운영 문서에는 각 키의 소유자와 복구 책임을 따로 적는 편이 좋습니다. [키 관리 안내](https://docs.besu-eth.org/)

## 릴리스에서 확인되는 2026년 변화

공식 GitHub API의 릴리스 목록에는 26.1.0부터 26.9.0까지 2026년에 발행된 정식 릴리스가 11개 있습니다. 릴리스 후보(RC)는 제외한 수입니다. 태그 이름의 월처럼 보이는 숫자와 실제 발행일도 구분해야 합니다. 예를 들어 26.2.0은 3월 5일에 발행됐습니다. 이 기록은 개발이 이어진다는 근거지만 운영 안정성을 자동으로 증명하지는 않습니다. [릴리스 목록](https://github.com/besu-eth/besu/releases)

아래 표는 주요 변화가 있는 릴리스를 골라 정리했습니다.

| 실제 발행일(UTC) | 릴리스 | 운영자가 확인할 내용 |
| --- | --- | --- |
| 2026-02-03 | [26.1.0](https://github.com/besu-eth/besu/releases/tag/26.1.0) | Bonsai 상태 루트 계산 병렬화 |
| 2026-03-05 | [26.2.0](https://github.com/besu-eth/besu/releases/tag/26.2.0) | Fast Sync와 Ethereum Classic 지원 제거 |
| 2026-04-22 | [26.4.0](https://github.com/besu-eth/besu/releases/tag/26.4.0) | 저장소 이전, 순수 Clique 네트워크 지원 제거 |
| 2026-05-12 | [26.5.0](https://github.com/besu-eth/besu/releases/tag/26.5.0) | 실험적 Bonsai Archive 저장 구조 변경과 재동기화 요구 |
| 2026-06-04 | [26.6.0](https://github.com/besu-eth/besu/releases/tag/26.6.0) | Java Development Kit(JDK) 25 필수화, RPC 인자 검증 강화, BFT 혼합 버전 호환 옵션 |
| 2026-07-13 | [26.7.0](https://github.com/besu-eth/besu/releases/tag/26.7.0) | Block Access List를 활용하는 병렬 실행 구현 |
| 2026-08-19 | [26.8.0](https://github.com/besu-eth/besu/releases/tag/26.8.0) | discovery 설정 변경, 플러그인 API 모듈 분리 |
| 2026-09-01 | [26.8.1](https://github.com/besu-eth/besu/releases/tag/26.8.1) | 로그 필터 주소 수 제한, 개발 네트워크 옵션 제거 |
| 2026-09-25 | [26.9.0](https://github.com/besu-eth/besu/releases/tag/26.9.0) | 보안 업데이트 공지, native tracer 추가, 메모리 부족(Out of Memory, OOM) 시 종료 기본값 |

## 병렬화의 대상과 성능 수치의 범위

Besu의 성능 개선을 이해하려면 트랜잭션 실행과 상태 루트 계산을 나눠 보는 편이 쉽습니다. 전자는 EVM 연산과 상태 읽기·쓰기를 처리하는 과정이고, 후자는 실행 결과가 반영된 상태 트리의 해시를 계산하는 과정입니다. 어느 한쪽만 빨라져도 다른 쪽이 병목으로 남을 수 있습니다.

[Bonsai 병렬 트랜잭션 실행 문서](https://docs.besu-eth.org/public-networks/concepts/parallel-transaction-execution)는 낙관적 실행을 설명합니다. 백그라운드에서 트랜잭션을 병렬 실행하면서 순차 처리도 진행합니다. 순서가 돌아온 트랜잭션의 결과가 준비됐고 앞선 상태 변경과 충돌하지 않으면 그 결과를 적용합니다. 충돌하면 다시 실행하고, 결과가 아직 없으면 순차 실행합니다. Ethereum이 정한 트랜잭션 순서를 임의로 바꾸는 기능은 아닙니다.

이 방식의 이득은 작업 부하에 달려 있습니다. 여러 트랜잭션이 같은 storage slot을 반복해서 수정하면 독립적인 상태를 다루는 경우보다 재실행이 많아질 수 있습니다. 현재 [옵션 문서](https://docs.besu-eth.org/public-networks/reference/options#bonsai-parallel-tx-processing-enabled)는 Bonsai 병렬 처리의 기본값을 `true`로 설명합니다. 설정을 켰는지만 확인하기보다 실제 처리 시간과 충돌·재실행 양상을 함께 측정하는 편이 유용합니다.

상태 루트 계산에도 병렬화가 들어갔습니다. 2026년 4월 20일 유지보수자 [설명 글](https://www.lfdecentralizedtrust.org/blog/optimizing-besu-performance-parallelizing-state-root-computation)은 변경할 키를 모아 정렬하고 trie의 독립적인 하위 경로로 나누는 방식을 소개합니다. 하위 작업의 결과를 모아 부모 해시를 계산하고 저장은 묶어서 처리합니다. 글이 나온 날과 기능 출시일은 다릅니다. 기본 적용은 2월 3일 발행된 26.1.0부터입니다.

저자들은 8코어·8스레드, 비 NVMe 환경에서 메인넷 블록 처리 시간이 최대 40% 줄었다고 보고했습니다. 같은 글은 NVMe 환경에서 상대적 이득이 더 작을 것으로 예상하고, 물리 코어 수와 저장장치 특성이 결과에 영향을 준다고 설명합니다. 따라서 이 수치를 모든 서버의 초당 트랜잭션 수(TPS)가 40% 증가한다는 뜻으로 옮기면 안 됩니다. 블록 처리 시간 감소율과 네트워크 전체 처리량 증가율은 측정 대상도 다릅니다.

외부 비교 자료로는 Nethermind가 2025년 12월 16일 공개한 [GigaGas 벤치마크](https://www.nethermind.io/blog/getting-ethereum-ready-for-gigagas)가 있습니다. 같은 snapshot과 하드웨어에서 같은 블록을 재생하고, 실제 블록과 여러 블록을 합친 합성 부하를 구분합니다. 경쟁 클라이언트 팀의 원본 실험이므로 방법과 당시 조건을 읽는 자료로 적합합니다. 당시 순위를 2026년 10월 바이너리의 우열로 재사용할 근거는 없습니다.

## 저장소와 과거 데이터의 서비스 범위

현재 공식 문서는 Bonsai를 기본 저장 형식으로 안내합니다. 최근 상태를 직접 읽는 데 유리하고 저장 공간을 줄이는 구조입니다. Forest도 문서에 남아 있습니다. Forest 관련 명령 일부가 제거됐다는 릴리스 문구를 보고 저장 형식 전체가 제거됐다고 해석하면 안 됩니다. [저장 형식 문서](https://docs.besu-eth.org/public-networks/concepts/data-storage-formats), [26.2.0](https://github.com/besu-eth/besu/releases/tag/26.2.0)

저장 용량 숫자는 노드가 제공하는 서비스와 함께 읽어야 합니다. 문서는 Bonsai SNAP full node를 약 1.14 TB, Forest FULL archive node를 약 12 TB로 제시합니다. 전자는 2026년 5월 26.5.0 burn-in의 AWS `m8g.2xlarge` 결과에 근거한 추정입니다. 두 노드는 과거 상태 조회 범위가 다릅니다. 같은 기능을 제공하는 두 DB의 압축률 비교나 영구적인 최소 디스크 사양이 아닙니다.

일반 Bonsai의 과거 상태 조회와 Bonsai Archive도 구분해야 합니다. 문서에 나온 일반 Bonsai의 기본 historical block limit은 512입니다. 이 값은 얼마나 과거까지 상태를 재구성해 읽을지 제한하는 설정이며, 값을 바꾼다고 그만큼 디스크가 줄어드는 옵션은 아닙니다. 서비스가 오래된 `eth_call`이나 `eth_getProof`를 요구한다면 단순히 현재 블록이 동기화됐는지 확인하는 것으로는 부족합니다. [과거 데이터 접근](https://docs.besu-eth.org/public-networks/concepts/data-storage-formats#accessing-data)

Bonsai Archive 개발은 진행됐지만 안정적인 일반 Bonsai와 같은 취급을 하기 어렵습니다. [26.4.0](https://github.com/besu-eth/besu/releases/tag/26.4.0)과 [26.5.0](https://github.com/besu-eth/besu/releases/tag/26.5.0)은 실험적 Archive의 column family 변경 때문에 전체 재동기화가 필요하다고 경고했습니다. Archive를 평가한다면 잔액 조회, 과거 실행, 상태 증명, 장애 후 복구를 각각 검증해야 합니다. 로드맵에 archive proofs가 있다는 사실만으로 모든 과거 블록의 증명을 운영 환경에서 보장한다고 읽을 수는 없습니다.

History expiry는 또 다른 축입니다. 과거 블록 body와 receipt를 지우는 것과 과거 world state를 보관하는 것은 다른 문제입니다. 공식 [pre-merge 정리 문서](https://docs.besu-eth.org/public-networks/how-to/pre-merge-history-expiry)는 body와 receipt를 제거해도 header와 genesis는 남는다고 설명합니다. 기존 온라인 옵션 `--history-expiry-prune`는 26.1.0부터 deprecated 상태입니다. 인덱서가 오래된 receipt를 필요로 한다면 먼저 보존 범위를 합의하고 복구 경로를 준비해야 합니다. 공간 회수만 보고 pruning을 실행하면 애플리케이션의 데이터 계약이 깨질 수 있습니다.

## 제거된 기업용 기능과 남은 확장 경로

과거 Besu 소개에 자주 등장하던 Tessera 기반 privacy는 현재 기능 목록에 넣으면 안 됩니다. [25.6.0](https://github.com/besu-eth/besu/releases/tag/25.6.0)은 Tessera privacy와 smart-contract-based onchain permissioning 제거를 기록했고, [25.7.0](https://github.com/besu-eth/besu/releases/tag/25.7.0)은 `EEA`, `PRIV` RPC 그룹 제거를 명시했습니다. 이것은 단순한 비권장 안내를 넘어 이미 출시된 제거입니다.

로컬 node·account permissioning과 permissioning 플러그인은 별개로 남아 있습니다. QBFT 문서가 설명하는 contract 기반 validator 선택도 제거된 onchain node·account permissioning과 다른 기능입니다. 이름에 contract가 들어간다는 이유로 한꺼번에 지원 종료라고 묶으면 구성 판단이 틀어집니다. [로컬 permissioning](https://docs.besu-eth.org/private-networks/how-to/use-local-permissioning), [QBFT validator 선택](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft)

허가된 참여자만 연결하도록 제한해도 복제된 EVM 상태가 참여자 사이에서 자동으로 비밀이 되지는 않습니다. 금융 네트워크가 거래별 비공개 상태나 선택적 공개를 요구한다면 별도 프라이버시 계층의 신뢰 가정과 데이터 배포 방식을 검토해야 합니다. 옛 private transaction API를 새로운 플러그인이 그대로 대체한다고 가정해서도 안 됩니다.

동기화와 합의 지원 범위도 달라졌습니다. 26.2.0에서 Fast Sync가 제거됐고 26.4.0에서는 순수 Clique 체인을 시작하거나 채굴하는 기능이 제거됐습니다. Clique로 시작해 PoS로 전환한 체인의 이력 동기화는 계속 지원한다고 명시합니다. 따라서 “Clique 지원”이라는 한 줄보다 현재 합의와 과거 이력의 처리를 나눠 확인하는 것이 정확합니다. [26.2.0](https://github.com/besu-eth/besu/releases/tag/26.2.0), [26.4.0](https://github.com/besu-eth/besu/releases/tag/26.4.0)

## 출시된 코드와 아직 확인해야 할 계획

2월 4일 유지보수자 [회고와 목표](https://www.lfdecentralizedtrust.org/blog/a-deep-dive-into-besu-milestones-2025-highlights-and-2026-goals)는 peer discovery, Bonsai Archive, 플러그인 확장을 2026년 과제로 설명합니다. 이 문서를 현재 상태표로 그대로 사용하면 뒤처집니다. 26.8.0에는 이미 `--discovery-mode`의 V4·V5·BOTH 선택과 기본 V4 동작이 명시돼 있습니다. 예전 `v5Bootnodes`도 통합 `bootnodes`로 옮겨졌습니다. [26.8.0](https://github.com/besu-eth/besu/releases/tag/26.8.0)

Block Access List(BAL) 병렬 실행은 26.7.0에 구현됐습니다. 하지만 구현, 테스트넷 일정, 메인넷 활성화는 서로 다른 증거가 필요합니다. 26.9.0은 Sepolia의 Amsterdam 일정을 2026년 10월 6일 13:53:36 UTC로 설정합니다. 같은 태그의 [Sepolia 설정](https://github.com/besu-eth/besu/blob/26.9.0/config/src/main/resources/sepolia.json)에는 그 시각이 있고 [메인넷 설정](https://github.com/besu-eth/besu/blob/26.9.0/config/src/main/resources/mainnet.json)에는 Amsterdam 활성화 시각이 없습니다. 이 자료만으로 메인넷에서 새 규칙이 가동됐다고 주장하지 않습니다. [26.7.0](https://github.com/besu-eth/besu/releases/tag/26.7.0), [26.9.0](https://github.com/besu-eth/besu/releases/tag/26.9.0)

플러그인 API도 같은 구분이 필요합니다. 기능별 모듈 분리는 진행됐으며 기존 `besu-plugin-api`가 재노출하는 경로도 있습니다. 26.9.0은 향후 package·signature·lifecycle 변경이 source-compatible하지 않을 것이라고 예고합니다. 이미 모든 플러그인이 깨졌다는 뜻은 아니지만, 본체를 추적하는 플러그인 운영자는 API 변경을 별도 업그레이드 항목으로 관리해야 합니다. [플러그인 변경 공지](https://github.com/besu-eth/besu/releases/tag/26.9.0)

## 10월 보안 권고와 수정 버전 확인

9월 릴리스 이후 공개된 권고도 읽어야 합니다. 10월 14일 공개된 [서명 복구 권고](https://github.com/besu-eth/besu/security/advisories/GHSA-4h4f-925g-8h9p)와 [typed transaction decoding 권고](https://github.com/besu-eth/besu/security/advisories/GHSA-cgvq-9xfq-c54j)는 합의 결과 불일치 가능성을 다루며 수정 버전을 26.8.0으로 표시합니다. 공개일은 취약점이 생긴 날이나 실제 공격이 관찰된 날을 뜻하지 않습니다.

[tracing 제한 관련 권고](https://github.com/besu-eth/besu/security/advisories/GHSA-qfmh-cxw4-9h66)의 개별 수정 커밋 [`ebaf89e162`](https://github.com/besu-eth/besu/compare/ebaf89e162...26.9.0)와 [`facf43ddb9`](https://github.com/besu-eth/besu/compare/facf43ddb9...26.9.0)는 26.9.0 태그에 포함돼 있습니다. 태그의 [`DebugTraceTransaction.java`](https://github.com/besu-eth/besu/blob/26.9.0/ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/methods/DebugTraceTransaction.java)에서도 서버 측 step limit 적용을 확인할 수 있습니다. 9월 30일 병합된 [PR #11378](https://github.com/besu-eth/besu/pull/11378)은 출시된 커밋을 `main` 이력에 반영한 후속 작업입니다.

출시된 제한과 이후 보완은 구분해야 합니다. 9월 30일의 추가 커밋 [`7f904a379c`](https://github.com/besu-eth/besu/commit/7f904a379cf5b59e7016118d64f6d68abadf69a2)은 batch JSON-RPC의 `debug_traceBlock` 계열에서도 step ceiling을 적용하도록 보완했습니다. 이 후속 커밋은 26.9.0 태그에 포함되지 않습니다. 따라서 기존 제한이 출시됐다는 사실을 모든 tracing 경로의 안전성 보증으로 확대하지 않습니다.

운영자는 사용하는 artifact의 수정 내역과 활성화한 RPC 경로를 확인하고, `DEBUG`·`TRACE` 접근을 신뢰된 호출자로 제한하거나 사용하지 않는 namespace를 비활성화하는 대응을 검토할 수 있습니다. QBFT의 P2P 경로에도 [별도 가용성 권고](https://github.com/besu-eth/besu/security/advisories/GHSA-g5j7-4r2x-rx9j)가 있습니다. RPC와 합의 통신 경로는 각각 보호해야 합니다.

## 유지보수와 채택 자료가 보여주는 범위

LFDT의 [2026년 연례 보고서](https://lf-decentralized-trust.github.io/governance/project-updates/2026/2026-annual-Besu/)는 2025년을 돌아보며 활성 유지보수자 21명 중 약 19명이 Consensys 소속이라고 적습니다. 이는 조직 편중을 검토할 근거입니다. 다만 10월 15일의 실시간 인원 조사도 아니고, 개인별 작업량이나 대체 가능성을 측정한 수치도 아닙니다. 제 판단으로는 릴리스 활동과 조직 다양성을 따로 평가하는 편이 맞습니다. 개발이 활발해도 인력 공급의 집중 위험은 남습니다.

같은 보고서의 메인넷 EL stake 비중 추정치를 현재 시장점유율로 제시하지는 않겠습니다. reachable node 비중, stake 비중, 운영 기관 수는 분모가 다릅니다. 조사 방법과 기준 시각 없이 숫자를 합치면 클라이언트 다양성을 잘못 읽게 됩니다.

기관 채택에는 이름이 확인되는 사례가 있습니다. LFDT가 Ledger Insights에 의뢰한 [2026 기관 채택 자료](https://www.lfdecentralizedtrust.org/ledger-insights-report-2026)는 Citi Token Services, Fnality, Clearstream D7 등을 Besu 사용 프로젝트로 열거합니다. 다만 보고서는 상용 운영 중이거나 상용화를 준비하는 프로젝트를 함께 다룹니다. 전체 LFDT 기술의 사례 수를 Besu 고객 수로 바꾸거나, 기관 전체 수탁 자산을 Besu 온체인 거래액으로 읽으면 안 됩니다. 구체적 사례는 존재하지만 공개 자료만으로 전체 설치 수나 상용화 비율을 계산하기는 어렵습니다.

## 커뮤니티 운영 관찰

[Eth Docker 운영자 글](https://www.reddit.com/r/ethstaker/comments/1vtatpn/eth_docker_2681_with_5_months_rolling_expiry/)은 실험적 rolling expiry와 receipt를 필요로 하는 하위 서비스의 제약을 함께 언급합니다. 디스크 절감 기능에 대한 관심과 호환성 부담이 동시에 드러나는 사례입니다. 특정 운영 도구와 서비스의 설명이므로 모든 Besu 배포의 pruning 정책이나 커뮤니티 전체의 평가로 일반화하지 않습니다.

## 운영자를 위한 업그레이드 점검표

아래 항목은 릴리스의 변경 사항을 바탕으로 제안하는 점검 순서입니다. 실제 네트워크의 가용성 기준과 데이터 보존 정책에 맞춰 조정해야 합니다.

1. **현재 역할과 의존성을 기록합니다.** 메인넷 EL, 허가형 validator, RPC, indexer용 archive 중 무엇을 운영하는지 적고 CL·플러그인·외부 서명기 버전도 묶습니다. 같은 Besu 버전이라도 필요한 검증이 달라집니다.
2. **원본 릴리스와 보안 권고를 대조합니다.** 목표 태그뿐 아니라 현재 버전부터 사이에 낀 breaking change를 읽습니다. 관련 수정이 목표 태그에 포함됐는지 개별 커밋과 릴리스 소스로 확인합니다.
3. **Java와 프로세스 복구를 먼저 시험합니다.** 26.6.0부터 JDK 25가 필요합니다. 26.9.0은 OOM 시 종료가 기본입니다. 운영 Java 가상 머신(JVM)과 서비스 매니저의 재시작 정책, 반복 종료 알림을 함께 확인합니다. [26.6.0](https://github.com/besu-eth/besu/releases/tag/26.6.0), [26.9.0](https://github.com/besu-eth/besu/releases/tag/26.9.0)
4. **RPC 요청과 응답을 실제 호출로 검증합니다.** 26.6.0의 hex 인자 강제, 26.8.1의 기본 1,000개 로그 필터 주소 제한, 26.9.0의 `eth_feeHistory` 검증 변경을 애플리케이션 테스트에 반영합니다. 성공 응답뿐 아니라 오류 코드 처리도 확인합니다. [26.8.1](https://github.com/besu-eth/besu/releases/tag/26.8.1), [26.9.0](https://github.com/besu-eth/besu/releases/tag/26.9.0)
5. **BFT 혼합 버전을 사전 환경에서 재현합니다.** 26.6.0은 25.x 노드와의 rolling upgrade에 `--Xbft-legacy-protocol-encoding`을 안내합니다. 문서의 호환 옵션을 영구 설정으로 복사하지 말고 교체 순서와 제거 시점을 정합니다. 매 단계에서 실제 블록 높이와 합의 참여를 확인합니다. [26.6.0 BFT 수정](https://github.com/besu-eth/besu/releases/tag/26.6.0)
6. **복구와 과거 조회를 별도로 검사합니다.** DB 백업을 만들었다는 기록보다 복구된 노드가 필요한 블록·receipt·상태 증명을 반환하는지가 중요합니다. pruning과 실험적 archive 변경은 재동기화 시간까지 반영해 결정합니다.
7. **부하별 지표를 비교합니다.** 블록 처리 시간, RPC 지연, heap·가비지 컬렉션(GC), 디스크 여유, peer 연결, QBFT round change를 교체 전후 같은 조건에서 봅니다. 동기화 완료나 프로세스 생존만으로 서비스 정상 여부를 판단하지 않습니다.

현재 Besu를 평가할 때는 Java 기반 실행 환경과 QBFT 지원이라는 선택 이유가 여전히 유효합니다. 동시에 제거된 privacy 기능, 실험적 archive의 변경 비용, 플러그인 API 계획을 설계에 반영해야 합니다. 최신 태그를 고른 다음 실제 운영 계약에 맞는지 검증하는 과정까지가 업그레이드입니다.

## 함께 보면 좋을 자료

- [Besu와 Teku 메인넷 구성](https://docs.besu-eth.org/public-networks/tutorials/besu-teku-mainnet): EL·CL 연결과 서명 역할을 확인하는 출발점입니다.
- [QBFT 설정](https://docs.besu-eth.org/private-networks/how-to/configure/consensus/qbft): validator 관리와 장애 허용 조건을 확인합니다.
- [Nethermind의 GigaGas 실험](https://www.nethermind.io/blog/getting-ethereum-ready-for-gigagas): 클라이언트 성능 비교에서 부하와 재현 조건을 읽는 데 도움이 됩니다.

## 참고 자료

아래 자료와 본문의 릴리스·권고 링크는 2026년 10월 15일 KST에 확인했습니다. 날짜 없는 문서는 조회 시점의 설명이며, 측정 결과에는 본문에 적은 별도 증거 날짜가 적용됩니다.

- [Besu 저장소와 릴리스](https://github.com/besu-eth/besu/releases): Besu maintainers, 각 태그의 실제 발행일 참조.
- [LFDT 출범 발표](https://www.lfdecentralizedtrust.org/announcements/linux-foundation-decentralized-trust-launches-with-17-projects-100-founding-members): LF Decentralized Trust, 2024-09-16.
- [공식 문서](https://docs.besu-eth.org/), [저장 형식](https://docs.besu-eth.org/public-networks/concepts/data-storage-formats), [병렬 실행](https://docs.besu-eth.org/public-networks/concepts/parallel-transaction-execution), [옵션](https://docs.besu-eth.org/public-networks/reference/options), [history expiry](https://docs.besu-eth.org/public-networks/how-to/pre-merge-history-expiry), [로컬 permissioning](https://docs.besu-eth.org/private-networks/how-to/use-local-permissioning): Besu documentation.
- [2025 성능 회고와 2026 로드맵](https://www.lfdecentralizedtrust.org/blog/boosting-besu-performance-2025-accomplishments-and-2026-roadmap): Besu maintainers, 2025-11-19.
- [2025 주요 작업과 2026 목표](https://www.lfdecentralizedtrust.org/blog/a-deep-dive-into-besu-milestones-2025-highlights-and-2026-goals): Besu maintainers, 2026-02-04.
- [상태 루트 계산 병렬화](https://www.lfdecentralizedtrust.org/blog/optimizing-besu-performance-parallelizing-state-root-computation): Karim Taam·Ameziane Hamlat, 2026-04-20.
- [2026년 연례 프로젝트 보고서](https://lf-decentralized-trust.github.io/governance/project-updates/2026/2026-annual-Besu/): LFDT TAC에 제출된 2025년 회고, 정확한 발행일은 별도 표시되지 않음.
- [2026 기관 채택 자료](https://www.lfdecentralizedtrust.org/ledger-insights-report-2026): LFDT·Ledger Insights, 2026년 보고서.
- [Besu 보안 권고 목록](https://github.com/besu-eth/besu/security/advisories): 개별 공개일과 수정 근거는 본문 링크 참조.
- [Eth Docker와 rolling expiry](https://www.reddit.com/r/ethstaker/comments/1vtatpn/eth_docker_2681_with_5_months_rolling_expiry/): yorickdowne, r/ethstaker, 운영 도구와 하위 서비스 호환성 설명.
