---
title: "Figure: HELOC 대출에서 블록체인 자본시장 플랫폼으로"
meta_title: ""
description: "Figure Technology Solutions는 미국 HELOC 비은행 대출 1위에서 출발해 Provenance Blockchain 기반 자본시장 플랫폼으로 진화했습니다. DART 소유권 레지스트리, YLDS 이자부 증권, Democratized Prime 대출 마켓 구조를 정리합니다."
date: 2026-06-30T07:00:00+09:00
lastmod: 2026-06-30T07:00:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["rwa", "provenance", "capital-markets", "tokenization", "heloc", "ylds"]
author: "hakhub"
translationKey: "figure-blockchain-capital-markets"
draft: true
---

Figure라는 이름은 두 개의 회사를 가리킨다. 하나는 휴머노이드 로봇으로 알려진 Figure AI이고, 다른 하나는 이 글의 주제인 [Figure Technology Solutions](https://www.figure.com/)다. 두 회사는 무관하다.

Figure Technology Solutions는 미국 주택담보대출 시장에서 출발한 금융 회사로, 현재는 Provenance Blockchain 위에서 대출 생성, 소유권 등록, 토큰화 마켓, 이자부 정산 자산을 수직으로 통합하는 구조를 만들고 있다. Nasdaq에 FIGR 티커로 상장되어 있다.

## Figure 모델의 차별점

Figure의 접근 방식을 "RWA를 블록체인에 올린다"로 요약하면 핵심을 놓친다. 회사가 하려는 일은 대출 생성 단계부터 블록체인 기록을 쓰고, 거기서 만들어진 자산을 법적 소유권 등록, 거래 마켓, 이자부 현금성 자산까지 하나의 rail로 연결하는 것이다.

[Figure의 Investor Relations 페이지](https://investors.figure.com/investor-relations)는 회사를 "blockchain-native capital marketplace for the origination, funding, sale and trading of on-chain loan products and tokenized assets"로 설명한다.

## 핵심 시스템

### HELOC과 대출 생성

Figure의 소비자 핵심 상품은 HELOC(Home Equity Line of Credit)이다. 공식 사이트는 5분 심사, 최대 $750,000 대출, 빠르면 5일 funding을 내세운다. 이 대출 자체가 이후 DART 등록, 마켓 거래, 담보화로 이어지는 토큰화 파이프라인의 원천 자산이다.

LOS(Loan Origination System)가 대출 신청, 심사, 감정, 담보권 확인, 소득 검증, 원격 클로징을 자동화한다. Figure는 AI 협업으로 문서 처리와 파트너 온보딩 비용을 줄이고 있다고 밝혔지만, 이 수치는 독립 검증이 필요한 회사 발표 기반이다.

### DART: 온체인 소유권 레지스트리

DART(Digital Asset Registry Technology)는 Figure 생태계에서 대출 소유권과 담보권의 기록 레이어다. [Provenance 공식 사이트](https://provenance.io/)는 DART를 "first blockchain-based system for real-time loan ownership updates"라고 설명하며, ESIGN/UETA 준수를 명시한다.

DART가 담당하는 역할은 대출 소유권 업데이트, 담보권(lien) 정보 연결, eNote와 servicer 정보 관리, 토큰화 대출과 법적 소유권의 연결이다.

한 가지 주의할 점이 있다. ESIGN/UETA 준수는 전자기록·전자서명 측면의 주장이다. 미국 모든 주에서 기존 MERS 등기 방식과 완전히 동일한 법적 효과를 가진다는 의미로 단정하기는 이르다.

### Provenance Blockchain

Provenance는 금융 상품을 위해 설계된 분산 지분증명(PoS) 블록체인이다. Figure의 주요 시스템이 record, settlement, tokenization rail로 Provenance를 사용한다. 다만 차용인의 개인정보(PII) 같은 민감 데이터는 그대로 온체인에 올라가지 않는 구조다.

### Figure Connect: 소비자 대출 마켓플레이스

Figure Connect는 대출 originator와 자본 공급자를 연결하는 소비자 신용 대출 마켓플레이스다. HELOC, DSCR, 개인대출 등 소비자 대출 자산을 거래·자금조달 가능한 형태로 만든다. [IR 발표](https://investors.figure.com/investor-relations) 기준 2026년 Q1 Figure Connect 거래량은 $1.6B로 소비자 대출 마켓 전체의 56%에 해당한다.

### YLDS: SEC 등록 이자부 증권

YLDS는 전송과 정산이 스테이블코인처럼 작동하지만, 공식 사이트는 "registered fixed-income security, not a stablecoin"이라고 명시한다.

주요 특징은 다음과 같다. Figure Certificate Company가 발행하고, SEC에 등록된 fixed-income security다. 1 YLDS = 1 Certificate = $0.01 NAV 구조이고, SOFR minus 35bps 기반 변동 수익이 매일 accrual된다. Provenance, Solana, Stellar 등 복수 체인에서 24/7 peer-to-peer 전송과 정산을 지원한다.

2026년 5월 IR 기준 유통 중인 $YLDS는 $557M이다.

해석하면, YLDS는 Figure 마켓 안에서 idle cash, 대출 공급, 정산 자산, 현금성 treasury 자산 역할을 하는 규제된 yield-bearing primitive다. 스테이블코인이 아니라 증권이라는 법적 위치가 핵심이다.

### Democratized Prime: 온체인 대출·차입 마켓

Democratized Prime은 Figure Markets의 온체인 lending 마켓플레이스다. 현금이나 암호화폐를 대출하거나 RWA·마진 트레이더를 통해 수익을 얻고, 암호화폐 담보 대출과 HELOC 기반 풀을 연결한다. 2026년 5월 기준 Matched Offers Balance $385M, 차용인 수요 $412M, 대출자 공급 가능 규모 $500M이다.

## 공개 지표 요약

[Figure IR](https://investors.figure.com/investor-relations)에서 확인 가능한 주요 수치다.

- 2026년 5월 소비자 대출 마켓플레이스 거래량: $1,402M
- 2026년 Q1 소비자 대출 마켓플레이스 거래량: $2.9B
- 2026년 Q1 Figure Connect 거래량: $1.6B
- 2026년 Q1 순매출: $167M, 순이익: $45M, 조정 EBITDA: $83M

반면 독립 검증이 필요한 항목도 있다. "#1 non-bank HELOC lender", "75% RWA 토큰화 시장점유율", "$130B+ revenue opportunity", AAA 등급 securitization 관련 세부 방법론 등은 회사 발표 기반이다.

## 주요 리스크

수직 통합 구조는 효율적이지만 리스크도 따른다.

YLDS는 스테이블코인이 아니라 등록 증권이라는 법적 포지션이 핵심이며, 미국 디지털 자산 입법 변화에 따라 제약이 달라질 수 있다. DART 레지스트리의 각 주별 lien perfection 효과는 별도 법적 검토가 필요하다. HELOC, DSCR, 암호화폐 담보 대출은 부동산 가격, 금리, 담보 변동성에 노출된다. origination, 레지스트리, 마켓플레이스, 대출 풀, 정산 자산이 같은 생태계에 묶이면 이해상충과 거버넌스 리스크가 커진다.

## 함께 보면 좋을 자료

- [Provenance Blockchain](https://provenance.io/) — Figure의 record, settlement, tokenization rail
- [DART](https://dartinc.io/) — 온체인 대출 소유권·담보권 레지스트리
- [YLDS](https://www.ylds.com/) — SEC 등록 이자부 증권 공식 사이트
- [Figure Markets](https://www.figuremarkets.com/) — 거래소, Democratized Prime, HASH

## 참고 자료

- [Figure 공식 사이트](https://www.figure.com/) — figure.com, 조회일 2026-06-30
- [Figure Investor Relations](https://investors.figure.com/investor-relations) — 조회일 2026-06-30
- [SEC Prospectus](https://www.sec.gov/Archives/edgar/data/2064124/000206412425000013/figuretechnologysolutionsi.htm) — 2025 IPO 서류, 조회일 2026-06-30
- [Figure Markets](https://www.figuremarkets.com/) — 조회일 2026-06-30
- [Provenance Blockchain](https://provenance.io/) — 조회일 2026-06-30
- [DART](https://dartinc.io/) — 조회일 2026-06-30
- [YLDS](https://www.ylds.com/) — 조회일 2026-06-30
