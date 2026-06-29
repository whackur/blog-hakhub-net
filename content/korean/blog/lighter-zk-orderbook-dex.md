---
title: "Lighter: Ethereum 위에서 동작하는 zk-SNARK 오더북 DEX"
meta_title: ""
description: "Lighter는 Ethereum 위의 애플리케이션 특화 zk-rollup으로, SNARK 기반 실행 증명을 통해 CEX 수준의 오더북 UX를 비수탁 환경에서 제공하려는 DEX입니다. 구조, MEV 저감 방식, Hyperliquid와의 차이를 정리합니다."
date: 2026-06-30T07:00:00+09:00
lastmod: 2026-06-30T07:00:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["zk-rollup", "orderbook", "dex", "mev", "ethereum", "snark"]
author: "hakhub"
translationKey: "lighter-zk-orderbook-dex"
draft: true
---

중앙화 거래소(CEX) 수준의 오더북 UX를 비수탁 환경에서 구현하려는 시도는 오랫동안 DEX 개발자들의 목표였다. Lighter는 그 답을 Ethereum 위의 애플리케이션 특화 zk-rollup에서 찾는다. 매칭 로직의 정당성을 SNARK로 증명하고 Ethereum에서 검증함으로써, 오퍼레이터를 신뢰하지 않아도 거래 결과를 검증할 수 있게 하는 구조다.

## Lighter의 포지션

Lighter를 이해하는 가장 빠른 방법은 Hyperliquid와 비교하는 것이다. 두 프로젝트 모두 AMM이 아니라 price-time priority 오더북을 핵심으로 삼고, CEX 수준의 거래 경험을 목표로 한다. 그러나 검증 구조가 다르다.

[Hyperliquid](https://hyperliquid.gitbook.io/hyperliquid-docs)는 자체 L1을 운영한다. HyperBFT 합의 위에 HyperCore 오더북이 올라가 있고, 모든 주문·취소·청산이 L1 한 블록 finality를 상속한다. 공식 문서 기준 200,000 orders/sec를 지원한다.

[Lighter](https://lighter.xyz/)는 Ethereum 위의 애플리케이션 특화 zk-rollup이다. Sequencer가 빠른 실행과 soft finality를 담당하고, Prover가 exchange operation의 정당성을 SNARK로 증명한다. Ethereum smart contract가 proof와 state root를 검증·보관하며, Escape Hatch와 priority request를 통해 비수탁 출금과 검열 저항을 구현한다.

## 핵심 구성 요소

### Sequencer

Sequencer는 저지연 실행 엔진이다. 사용자 트랜잭션을 순차 처리해 block/batch로 구성하고, 트랜잭션 영수증과 상태 변경 내역을 Indexer와 Prover에 전달한다. 문서와 whitepaper 기준으로 priority request와 일반 주문 모두 선입선출(FIFO) 큐로 처리한다. 사용자 입장에서는 soft finality를 즉시 제공하지만, canonical 상태 확정은 Ethereum proof 검증 이후다.

### Prover와 실행 증명

Prover는 Sequencer의 실행 피드, 이전 상태, 사용자 트랜잭션 배치를 입력으로 받아 exchange operation의 correctness proof를 생성한다. [Lighter 기술 문서](https://docs.lighter.xyz/about-lighter/technical-architecture-lighter-core)에 따르면 주문 매칭, 리스크 체크, 계정 업데이트, 청산 로직의 정당성을 SNARK로 증명한다.

여기서 중요한 구분이 있다. Lighter가 사용하는 zk-SNARK는 영지식성(zero-knowledge, 프라이버시)보다 **실행 정당성 검증**에 초점을 맞춘다. 매칭 연산이 공개된 규칙에 따라 올바르게 수행됐는지를 효율적으로 증명하는 용도다.

### Order Book Tree

SNARK 안에서 오더북 매칭을 효율적으로 증명하기 위해 Lighter는 Order Book Tree라는 특화 자료구조를 사용한다. 내부 노드가 하위 leaf의 집계 주문 데이터를 담고, leaf index가 주문 우선순위를 인코딩하는 prefix-tree 유사 구조다. 일반 Merkle tree 대비 매칭 연산 증명 비용을 줄이는 것이 목적이다.

### Ethereum 앵커링과 데이터 블롭

Ethereum smart contract는 사용자가 예치한 자산과 canonical Lighter state root를 보관한다. 상태 업데이트 제안은 proof와 Ethereum data blob을 동반한다. blob 데이터는 사용자가 자신의 계정 상태를 독립적으로 재구성하고 검증할 수 있는 최소 정보를 담는다. proof 검증이 완료되면 canonical state root가 업데이트된다.

### Priority Request와 Escape Hatch

사용자는 Ethereum smart contract를 통해 priority transaction을 직접 제출할 수 있다. Sequencer가 정해진 기한 안에 이를 포함하지 않으면 거래소 상태가 freeze되고 Escape Hatch가 활성화된다. 이 장치는 일반 주문의 front-running 방지보다는 출금·liveness·검열 저항을 위한 안전장치에 가깝다.

## MEV와 front-running에 대한 정확한 이해

"zk로 증명하므로 front-running이 불가능하다"는 표현은 정확하지 않다. [Lighter whitepaper](https://assets.lighter.xyz/whitepaper.pdf)는 MEV를 "substantially reducing"하는 방향으로 표현하고, 향후 fair sequencing, 트랜잭션 암호화, pre-commitment scheme을 언급한다.

더 정확하게 표현하면 이렇다. SNARK proof는 "공개된 회로와 규칙에 따라 상태 전이가 올바르게 계산됐는지"를 증명한다. 실제 네트워크 수신 순서, sequencer가 관측한 순서, 외부 주문 전파 경쟁까지 자동으로 증명하지는 않는다. FIFO 정책은 문서상 명시되어 있지만, 실제 주문 도착 공정성 검증은 별도 메커니즘이 필요하다.

즉, Lighter의 zk 구조는 **오퍼레이터의 매칭 조작, priority 변경, 일부 MEV 유인을 구조적으로 제한**하지만, "front-running 완전 불가능"보다는 "front-running/priority manipulation 리스크를 구조적으로 축소"라고 보는 것이 정확하다.

## 성능 수치

[Lighter API 문서](https://apidocs.lighter.xyz/docs/account-types)에 공개된 계정 tier별 latency는 다음과 같다.

- **Standard Account**: maker/cancel 200ms, taker 300ms, 수수료 0%
- **Plus Account**: maker/cancel 200ms, taker 300ms, 수수료 0.5bps
- **Premium Account**: maker/cancel 0ms, taker 200ms(LIT 스테이킹 규모에 따라 140ms까지 단축)

공식 사이트는 초당 수만 건의 주문·취소와 밀리초 단위 latency를 제시한다. 단, 실제 체감 latency는 계정 tier, 스테이킹 규모, 네트워크 조건, API 경로에 따라 달라진다.

## 남은 과제

Lighter가 내세우는 구조는 흥미롭지만 확인이 필요한 영역도 있다.

거래량, 미결제약정(OI), 시장 점유율, 활성 사용자 수, 시장 깊이는 별도 데이터로 검증해야 한다. Soft finality와 Ethereum proof finality 사이의 시간 차이는 운영 리스크로 봐야 한다. 비용 절감을 위해 모든 상세 데이터를 올리지 않고 압축해 게시하는 data availability 구조도 주시할 필요가 있다.

## 함께 보면 좋을 자료

- [Hyperliquid Docs](https://hyperliquid.gitbook.io/hyperliquid-docs) — 자체 L1 기반 오더북 DEX의 반대 접근법
- [Lighter Whitepaper](https://assets.lighter.xyz/whitepaper.pdf) — zk-rollup 오더북 설계 원문
- [Lighter Technical Architecture](https://docs.lighter.xyz/about-lighter/technical-architecture-lighter-core) — Sequencer, Prover, 스마트 컨트랙트 구조 설명

## 참고 자료

- [Lighter 공식 사이트](https://lighter.xyz/) — lighter.xyz, 조회일 2026-06-30
- [Lighter Docs](https://docs.lighter.xyz/) — 공식 기술 문서, 조회일 2026-06-30
- [Lighter Technical Architecture](https://docs.lighter.xyz/about-lighter/technical-architecture-lighter-core) — 조회일 2026-06-30
- [Order Types & Matching](https://docs.lighter.xyz/trading/order-types-and-matching) — 조회일 2026-06-30
- [Lighter API Account Types](https://apidocs.lighter.xyz/docs/account-types) — 조회일 2026-06-30
- [Lighter Whitepaper](https://assets.lighter.xyz/whitepaper.pdf) — 조회일 2026-06-30
- [Hyperliquid Docs](https://hyperliquid.gitbook.io/hyperliquid-docs) — 조회일 2026-06-30
