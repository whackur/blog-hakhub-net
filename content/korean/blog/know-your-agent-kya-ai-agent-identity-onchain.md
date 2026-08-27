---
title: "KYA(Know Your Agent): AI 에이전트 신원 검증, 표준 경쟁과 온체인 실태"
meta_title: ""
description: "KYC의 실사 프레임을 AI 에이전트에 적용한 KYA 개념을 정리하고, ERC-8004·Visa TAP·Trulioo·Sumsub의 표준 경쟁, NIST·EU·싱가포르 규제 신호, 평판 레지스트리 vouch spam 같은 온체인 실태를 짚습니다."
date: 2026-08-27T10:00:00+09:00
lastmod: 2026-08-27T10:00:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["ai-agent", "kya", "identity", "erc-8004", "reputation", "compliance"]
author: "whackur"
translationKey: "know-your-agent-kya-ai-agent-identity-onchain"
draft: false
---

은행 계좌를 열 때 신분증을 내고, 거래소에 가입할 때 얼굴을 찍는 절차를 KYC(Know Your Customer)라고 부릅니다. 이 절차는 1989년 FATF 설립 이후 금융의 진입점에서 불법 자금을 걸러내는 표준 관행이 됐습니다. 이제 사람이 아니라 AI 에이전트가 계약을 맺고, 결제를 보내고, DEX에서 토큰을 바꾸는 시대가 오면서 같은 질문이 다시 나옵니다. 지금 내 API에 결제 요청을 보낸 이 에이전트는 누구이고, 누가 만들었고, 어디까지 권한을 받았는가. 이 질문에 답하는 신뢰 계층을 업계는 KYA(Know Your Agent)라고 부르기 시작했습니다.

이 블로그는 앞서 [ERC-8004·8126·8196 신뢰 스택](/blog/ai-agent-wallet-trust-stack-erc-8004-8126-8196/)과 [ERC-8004 평판 레지스트리 조회 실무](/blog/erc8004-agent-reputation-registry-lookup/)를 다뤘습니다. 이 글은 개별 스펙을 다시 설명하지 않습니다. 대신 KYC/AML 실사(due diligence, 거래 상대를 사전에 조사하고 위험을 평가하는 절차) 관행에서 출발해서, 온체인 레지스트리를 그 실사의 한 구현 방식으로 놓고 표준 경쟁, 규제 신호, 실제 온체인 데이터가 말해주는 것을 종합합니다.

## KYA가 무엇인가

KYA는 KYC의 AI 에이전트 버전입니다. 에이전트가 자율적으로 계약·결제·거래를 실행하기 전에 "이 에이전트가 누구인지"를 사전에 검증하는 신뢰 계층으로, 2025년부터 주목받기 시작했습니다. [Agentica 위키](https://agentica.wiki/articles/know-your-agent)(2026-03-18 갱신)는 KYA를 여섯 차원으로 정리합니다.

| 차원 | 확인하는 것 |
|------|------------|
| 신원(identity) | 이 에이전트가 고유하게 식별되는가 |
| 소유자 바인딩(ownership binding) | 어느 사람 또는 조직이 이 에이전트에 책임지는가 |
| 권한 범위(authorization scope) | 무엇을 할 수 있도록 위임받았는가 |
| 출처·무결성(provenance) | 어떤 모델·코드로 만들어졌고 변조되지 않았는가 |
| 런타임 준수(runtime compliance) | 실행 중에도 정책 안에 머무는가 |
| 감사 가능성(auditability) | 나중에 행동을 추적하고 책임을 물을 수 있는가 |

KYC와 나란히 놓으면 차이가 보입니다. KYC는 신분증과 주소처럼 잘 바뀌지 않는 속성을 한 번 확인합니다. KYA의 여섯 차원 가운데 셋(권한 범위, 런타임 준수, 감사 가능성)은 등록 시점이 아니라 실행 중에 계속 검사해야 하는 항목입니다. 에이전트는 모델 업데이트 한 번으로 행동이 바뀌기 때문에, 한 번 통과한 검증이 다음 주에도 유효하다고 보기 어렵습니다. 이 점이 뒤에 나오는 비판 대부분의 뿌리입니다.

KYA가 모든 곳에 필요한 것은 아닙니다. [Tiger Research의 2026년 보고서](https://reports.tiger-research.com/p/2026-know-your-agent-eng)는 Google·OpenAI·Coinbase 같은 중앙 플랫폼 안에서는 플랫폼 계정에 이미 붙어 있는 KYC로 충분하다고 봅니다. KYA가 필요한 지점은 플랫폼 밖입니다. 개별 배포된 자율 에이전트가 DEX, 에이전트 간(A2A) 결제, 상거래 사이트에 접촉할 때 상대방은 이 에이전트를 보증해 줄 플랫폼이 없습니다. 같은 보고서는 KYC가 금융 시장 진입의 전제 조건이 된 것처럼 KYA 인프라 보유 여부가 다음 라운드 시장 진입을 결정할 것이라고 전망합니다. 전망은 전망이고, 아래 규제 섹션에서 보듯 아직 어떤 관할권도 이를 강제하지는 않습니다.

## 표준 경쟁 구도

KYA라는 이름은 하나지만 "신뢰를 어디에 고정하는가"는 진영마다 다릅니다. 네 가지 접근이 눈에 띕니다.

![ERC-8004 온체인 레지스트리, Visa TAP 서명 HTTP 요청, Trulioo 인증기관 모델, Sumsub 검증된 인간 바인딩 네 가지 KYA 접근의 신뢰 앵커·상태·수치 비교표](/images/posts/know-your-agent-kya-ai-agent-identity-onchain/kya-four-approaches.svg)

*네 접근이 신뢰를 고정하는 지점(온체인 레지스트리, 서명된 HTTP 요청, 인증기관, 검증된 인간)을 비교한 정리도. 수치는 본문 출처 기준입니다.*

### 온체인 레지스트리: ERC-8004와 그 위의 계층

[ERC-8004 "Trustless Agents"](https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-8004.md)는 에이전트 신원을 ERC-721 토큰으로 등록하고, 평판 신호와 독립 검증 결과를 각각 별도 레지스트리에 쌓는 구조입니다. 등록 파일(`agentURI`가 가리키는 JSON)에는 A2A/MCP/ENS/DID 같은 서비스 엔드포인트, `x402Support`, `supportedTrust` 필드가 들어가고, `agentWallet`(에이전트가 실제로 자산을 다루는 지갑 주소)은 EIP-712/ERC-1271 서명으로만 바인딩되며 NFT가 이전되면 자동으로 해제됩니다. 신뢰 모델은 플러그형이라 평판, 스테이킹 기반 재실행, zkML, TEE attestation(신뢰 실행 환경이 발행하는 무결성 증명) 가운데 골라 쓸 수 있습니다.

상태를 정확히 쓰면 이렇습니다. ERC-8004는 표준 프로세스상 Draft 단계이지만, 2026-01-29 이더리움 메인넷에 배포된 뒤 30개 이상 체인에 싱글톤으로 올라가 실제로 쓰이고 있으며 2026년 6월 기준 등록 수가 약 9만 건입니다. 스펙이 바뀔 수 있다는 것과 배포가 살아 있다는 것은 별개의 사실이고, 둘 다 참입니다.

KYA의 여섯 차원에 대응시키면 ERC-8004는 신원과 (부분적으로) 소유자 바인딩을 맡습니다. 그 위의 [ERC-8126 "AI Agent Verification"](https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-8126.md)(Final, 2026-01-15 생성)이 5종 검증과 0~100 리스크 스코어로 출처·무결성 검증을 담당하고, [ERC-8196 "AI Agent Authenticated Wallet"](https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-8196.md)(Final, 2026-03-14 생성)이 정책 바인딩 실행과 불변 감사 추적으로 런타임 준수와 감사 가능성을 채웁니다. 세 표준의 인터페이스와 검증 유형은 [기존 글](/blog/ai-agent-wallet-trust-stack-erc-8004-8126-8196/)에 정리해 두었습니다.

한 가지 짚을 점은 이 스택에 인간 신원 바인딩이 없다는 것입니다. NFT 소유자 주소는 있지만 그 주소 뒤에 누가 있는지는 스펙이 묻지 않습니다. [Concordium](https://www.concordium.com/article/erc-8004-explained-what-it-solves-and-the-gap-it-leaves)은 이 빈칸을 책임(accountability) 갭이라고 부르며 대응 표준 CIS-8004를 내놓았습니다. 에이전트 간 통신 프로토콜인 A2A/MCP는 KYA 자체가 아니라 상호보완 관계입니다. 통신은 A2A/MCP가, 발견과 신뢰는 ERC-8004가 맡는 분업입니다.

### 결제 네트워크: Visa TAP과 Mastercard Agent Pay

[Visa Trusted Agent Protocol(TAP)](https://developer.visa.com/use-cases/trusted-agent-protocol)은 2025-10-14 Visa와 Cloudflare가 함께 [발표](https://investor.visa.com/news/news-details/2025/Visa-Introduces-Trusted-Agent-Protocol-An-Ecosystem-Led-Framework-for-AI-Commerce/default.aspx)했습니다. 블록체인은 전혀 쓰지 않습니다. Web Bot Auth 기반 HTTP 메시지 서명으로 에이전트 신원을 요청 헤더에 서명해 보내고, 상점 쪽이 이를 검증합니다. 서명은 세 종류입니다. 에이전트 자체의 정당성(legitimacy), 위임자(delegator, 이 에이전트를 시킨 사람), 결제 수단(payment method). 런치 파트너는 Adyen, Ant International, Checkout.com 등 12곳입니다. 배경에는 미국 리테일 사이트의 AI 트래픽이 4,700% 급증했다는 수치가 있습니다. 상점 입장에서 봇을 전부 막을 수도, 전부 받을 수도 없으니 "좋은 봇"을 구별할 서명이 필요해진 것입니다.

Mastercard는 2025년 4월 Agent Pay를 발표했습니다. SD-JWT 기반의 검증 가능한 의도(verifiable intent)를 3레이어 8개 제약 유형으로 표현하고, 2026년 1월 Agent Suite로 확장했습니다. Santander(EU), DBS/UOB(싱가포르) 배포가 보고됐습니다.

두 결제 네트워크 접근은 KYA의 "소유자 바인딩"과 "권한 범위"를 카드 네트워크가 이미 가진 가맹점·발급사 관계 위에 얹습니다. 신뢰의 뿌리는 체인이 아니라 네트워크 운영자입니다.

### 신원 벤더: Trulioo의 인증기관 모델과 Sumsub

Trulioo는 SSL 인증기관(CA) 모델을 그대로 빌려 왔습니다. DPA(Digital Personhood Authority)가 DAP(Digital Agent Passport)를 발급하고, 상대방은 브라우저가 TLS 인증서를 확인하듯 이 여권을 확인합니다. Trulioo가 PYMNTS Intelligence와 함께 리스크·컴플라이언스 리더 350명을 조사한 결과, 기업 약 90%가 봇 관리를 주요 과제로 꼽았고 낡은 신원 통제로 연간 약 1,000억 달러 손실이 난다고 추정했습니다. 벤더 공동 조사라는 점은 감안해서 읽어야 합니다.

Sumsub은 2026년 1월 AI Agent Verification을 출시했습니다. 접근은 가장 KYC에 가깝습니다. 에이전트를 검증된 인간 신원에 바인딩하고, 그 인간에게 liveness 체크(실제 사람이 지금 앞에 있는지 확인)를 요구합니다. "이 에이전트의 행동에 법적으로 책임지는 사람"을 즉시 지목해야 하는 자리에 맞는 설계입니다. Prove도 공유 신뢰 레지스트리 기반의 Verified Agent 솔루션을 내놓았습니다.

### 메타데이터 표준과 인덱서

[AgentFacts](https://agentfacts.org/kya/)(Jared Grogan, [arXiv 2506.13794](https://arxiv.org/abs/2506.13794))는 특정 체인이나 벤더에 묶이지 않는 10-카테고리 메타데이터 표준입니다. Identity/Capability/Compliance/Provenance 네 기둥 아래 DID, EU AI Act 분류, NIST AI RMF 정렬 필드를 두어, 위의 어느 진영이 이기든 붙일 수 있는 공통 서술 계층을 노립니다.

[knowyouragent.network](https://knowyouragent.network/)는 반대로 이미 온체인에 있는 것을 읽는 쪽입니다. 12개 체인에서 15만 개 이상 에이전트를 인덱스하고, 지갑 tenure(주소가 활동한 기간), 소유권 이력, ERC-8004 사기 탐지를 합쳐 RNWY 스코어를 냅니다. 레지스트리가 게시판이라면 이런 인덱서가 실제 실사 도구 역할을 하는 구조입니다.

## 온체인 실태

표준 문서와 벤더 발표를 떠나 실제 레지스트리에 무엇이 쌓여 있는지 보면 KYA의 현재 위치가 더 정직하게 보입니다. [Blokz의 온체인 감사](https://www.blokz.dev/articles/erc-8004-agent-registries-onchain)(2026-06-12 시점)가 좋은 출발점입니다.

등록 규모는 Base 약 55,210건, 이더리움 메인넷 약 34,437건으로 합치면 약 89,600건이고, 메인넷 런치 후 19주 만의 수치입니다. 홀더는 Base 16,652 / 이더리움 8,573이라 홀더 하나가 평균 3.3~4개 에이전트를 들고 있습니다. 개인이 하나씩 등록한 것이 아니라 플랫폼이 대량 민팅한 결과입니다. 비용은 진입 장벽이 되지 못합니다. Base에서 ERC-4337 번들로 등록하면 273,820 gas, 총 수수료 0.0000017 ETH, ETH 1,667달러 기준 약 0.0028달러입니다. 실제 등록 예로 agentId 55,210 "Bob — Crypto Trading Agent"(0xWork 플랫폼)는 registration-v1 파일에 9 USDC 서비스 가격을 명시합니다.

문제는 평판 레지스트리입니다. Blokz는 단일 에이전트(id 25,975)에 48초 동안 피드백 이벤트 10개가 들어온 사례를 잡아냈습니다. 전부 value=1, tag는 miner-vouch/botcoin, 그리고 `feedbackHash`가 0x0이었습니다. feedbackHash가 0이라는 것은 이 피드백을 뒷받침하는 증거를 어디에도 커밋하지 않았다는 뜻입니다. 개별 "클라이언트" 주소가 수천 번씩 vouch(보증 피드백)를 남기는 패턴도 확인됐습니다. 이런 vouch spam이 가능한 이유는 스펙이 Sybil 저항(한 주체가 여러 신원을 만들어 신호를 부풀리는 공격에 대한 방어)을 온체인이 아니라 오프체인 집계에 위임했기 때문입니다. 컨트랙트는 누구의 피드백이든 받아 적습니다.

Blokz의 결론은 평판 레지스트리를 "이벤트 버스처럼 소비하라"는 것입니다. 신뢰하는 클라이언트 주소를 allowlist로 두고, feedbackHash가 0이 아닌 것만 고르고, feedbackURI의 증거를 확인한 다음에야 집계하라는 처방입니다. 감사 글의 문장을 빌리면, "평판이라는 단어가 컨트랙트 이름에 있다고 신뢰 문제가 풀린 게 아니다." 이 처방을 실제 조회 코드로 옮기는 방법은 [평판 레지스트리 조회 글](/blog/erc8004-agent-reputation-registry-lookup/)에서 다뤘습니다.

학계도 같은 데이터를 보고 있습니다. [arXiv 2606.26028](https://arxiv.org/abs/2606.26028)은 Ethereum, BNB/BSC, Base 3개 체인에서 2026-05-13까지의 Identity·Reputation 이벤트, 오프체인 등록 파일, x402 결제까지 크롤링한 실증 연구입니다. 온체인 KYA를 논할 때 벤더 백서가 아니라 이런 측정 데이터를 근거로 삼을 수 있게 된 것은 올해의 변화입니다.

## 규제·정책 신호

KYA를 법으로 요구하는 곳은 아직 없습니다. 다만 방향을 보여 주는 신호는 셋 있습니다.

미국 NIST NCCoE는 2026-02-05 개념 논문 ["Accelerating the Adoption of Software and AI Agent Identity and Authorization"](https://csrc.nist.gov/pubs/other/2026/02/05/accelerating-the-adoption-of-software-and-ai-agent/ipd)(Initial Public Draft)을 냈고 코멘트를 2026-04-02까지 받았습니다. AI Agent Standards Initiative의 일부로, 앞선 RFI에 930건 이상이 제출됐습니다. 논문은 에이전트 신원, 위임 체인(사람이 에이전트에, 에이전트가 다른 에이전트에 권한을 넘기는 사슬) 권한, 감사 요건을 명시적으로 다룹니다. KYA의 여섯 차원과 상당 부분 겹치는 주제입니다.

EU AI Act는 고위험 AI 시스템의 행동 로그에 운영자 신원을 기록하도록 의무화합니다. "에이전트 신원 검증"이라는 이름은 아니지만, 로그에 운영자를 남기려면 결국 에이전트와 운영자를 바인딩하는 무언가가 있어야 합니다. 싱가포르는 최초의 국가 단위 agentic AI 거버넌스 프레임워크를 발표했습니다.

[Agentica](https://agentica.wiki/articles/know-your-agent)에 따르면 2026년 3월 시점에 KYA를 명시적으로 요구하는 관할권은 없고, 조직들은 규제에 앞서 선제적으로 도입하는 중입니다. 위 벤더 움직임을 규제 대응으로 읽으면 과합니다. 지금은 규제가 아니라 상거래 사이트의 봇 트래픽과 결제 네트워크의 사기 비용이 KYA를 끌고 있습니다.

## 비판과 열린 문제

KYA에 대한 비판은 대부분 "KYC 비유가 어디서 깨지는가"로 정리됩니다.

**Sybil 저항.** 온체인 레지스트리 진영의 가장 큰 약점입니다. 등록 비용이 0.003달러 수준이고 평판 피드백은 누구나 남길 수 있으니, 위의 vouch spam은 버그가 아니라 설계의 자연스러운 결과입니다. 스펙은 필터링을 애플리케이션에 맡기고, 그 필터링을 누가 어떤 기준으로 하는지는 다시 오프체인 신뢰 문제로 돌아옵니다. Visa TAP이나 Sumsub은 이 문제를 겪지 않지만, 대신 네트워크 운영자나 벤더가 유일한 관문이 됩니다.

**프라이버시.** 소유자 바인딩을 강하게 할수록 에이전트의 모든 거래가 특정 사람에게 연결됩니다. Sumsub 방식은 이를 정면으로 받아들이고, ERC-8126은 PDV(Private Data Verification)로 검증 상세를 ZKP로 숨기고 결과를 에이전트 지갑 보유자만 열람하게 하는 절충을 둡니다. 어느 쪽도 "책임은 물을 수 있되 일상 거래는 추적되지 않는" 지점을 아직 깔끔하게 잡지 못했습니다.

**파편화.** 네 진영이 서로 다른 신뢰 앵커를 쓰고, 지금까지 어느 하나로 수렴할 신호는 없습니다. 카드 결제를 하는 에이전트는 TAP 서명이, DEX를 쓰는 에이전트는 ERC-8004 등록이, 규제 금융을 만나는 에이전트는 Sumsub류 인간 바인딩이 각각 필요해질 수 있습니다. AgentFacts 같은 메타데이터 계층이 접착제를 자처하지만 채택은 별개 문제입니다.

**에이전트 행동의 가변성.** KYC는 사람이 내일도 같은 사람이라는 가정 위에 섭니다. 에이전트는 모델 교체, 프롬프트 수정, 도구 추가로 행동이 바뀝니다. 등록 시점의 검증이 실행 시점의 안전을 말해 주지 않기 때문에 ERC-8196 같은 런타임 정책 계층이 따로 필요해졌습니다.

**강제력 부재.** 어떤 관할권도 KYA를 요구하지 않는 지금, 도입은 자발적이고 따라서 불균등합니다. 성실한 운영자만 등록하고 악의적인 운영자는 등록하지 않는다면, 레지스트리는 좋은 에이전트 목록이 될 뿐 나쁜 에이전트를 걸러내는 필터는 되지 못합니다. KYC가 효과를 낸 것은 자발적이어서가 아니라 의무였기 때문입니다.

## 커뮤니티 반응

KYA 자체를 놓고 벌어진 활발한 커뮤니티 토론은 아직 확인하지 못했습니다. Hacker News에는 Esther Dyson의 Substack 글 ["Know Your .agent?"](https://estherdyson.substack.com/p/know-your-agent)가 2026-05-06 올라왔지만 댓글은 0개였습니다. 2026-02-23의 x402 API Show HN에서는 서버가 ERC-8004 Agent #18763으로 Base에 등록된 사례가 보이는데, 이는 "실제로 쓰는 사람이 있다"는 신호이지 KYA 논쟁은 아닙니다. 이 글이 커뮤니티 후기 대신 Blokz 감사와 arXiv 실증 연구를 비판의 근거로 쓴 이유입니다.

## 함께 보면 좋을 자료

- [AI 에이전트 신뢰 스택: ERC-8004, ERC-8126, ERC-8196](/blog/ai-agent-wallet-trust-stack-erc-8004-8126-8196/): 이 글이 재설명하지 않은 세 표준의 인터페이스와 검증 유형 (이 블로그)
- [ERC-8004 에이전트 평판: 온체인 등록과 조회](/blog/erc8004-agent-reputation-registry-lookup/): 평판 레지스트리를 allowlist와 증거 확인으로 필터링하는 실무 (이 블로그)
- [Tiger Research: 2026 Know Your Agent](https://reports.tiger-research.com/p/2026-know-your-agent-eng): KYC 역사와 견줘 KYA 시장을 전망한 보고서
- [AgentFacts KYA 페이지](https://agentfacts.org/kya/): 체인·벤더 중립 메타데이터 표준
- [NIST NCCoE 개념 논문](https://csrc.nist.gov/pubs/other/2026/02/05/accelerating-the-adoption-of-software-and-ai-agent/ipd): 에이전트 신원·위임·감사에 대한 미국 표준 기관의 초안

## 정리

KYA는 새 기술이 아니라 오래된 규제 관행을 새 행위자에게 옮기는 시도입니다. 그 과정에서 KYC 비유는 절반만 맞습니다. 신원과 소유자 바인딩은 옮겨지지만, 권한 범위·런타임 준수·감사 가능성은 등록 한 번으로 끝나지 않는 지속 검사의 문제입니다.

온체인 진영은 배포 속도에서 앞서 있습니다. ERC-8004는 30개 이상 체인에서 약 9만 건 등록을 모았습니다. 다만 그 숫자의 상당 부분이 플랫폼 대량 민팅이고 평판 레지스트리에는 증거 없는 vouch가 쌓이고 있어서, "레지스트리에 있다"와 "믿을 수 있다"는 여전히 다른 말입니다. 결제 네트워크와 신원 벤더는 각자 이미 가진 관계(가맹점, KYC 고객)를 앵커로 삼아 Sybil 문제를 우회하지만, 그 대가로 단일 관문에 의존합니다.

제 판단으로는, 당장 에이전트를 운영하거나 에이전트 트래픽을 받는 쪽이 할 일은 진영을 고르는 것이 아닙니다. 어떤 레지스트리든 이벤트 버스로 취급하고 자기 기준으로 필터링하는 습관, 그리고 에이전트와 책임자를 바인딩하는 기록을 지금부터 남기는 일입니다. 규제가 오면 그 기록이 필요할 것이고, 오지 않더라도 사고가 났을 때 필요할 것입니다.

## 참고 자료

- [ERC-8004: Trustless Agents](https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-8004.md): ethereum/ERCs, Draft(표준 프로세스), 2026-01-29 메인넷 배포, 조회일 2026-08-27
- [ERC-8126: AI Agent Verification](https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-8126.md): ethereum/ERCs, Final, 조회일 2026-08-27
- [ERC-8196: AI Agent Authenticated Wallet](https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-8196.md): ethereum/ERCs, Final, 조회일 2026-08-27
- [2026 Know Your Agent](https://reports.tiger-research.com/p/2026-know-your-agent-eng): Tiger Research, 조회일 2026-08-27
- [ERC-8004 Agent Registries On-chain](https://www.blokz.dev/articles/erc-8004-agent-registries-onchain): Blokz, 2026-06-12 시점 감사, 조회일 2026-08-27
- [Know Your Agent](https://agentica.wiki/articles/know-your-agent): Agentica 위키, 2026-03-18 갱신, 조회일 2026-08-27
- [AgentFacts KYA](https://agentfacts.org/kya/) 및 [arXiv 2506.13794](https://arxiv.org/abs/2506.13794): Jared Grogan, 조회일 2026-08-27
- [Visa Trusted Agent Protocol](https://developer.visa.com/use-cases/trusted-agent-protocol) 및 [발표 보도자료](https://investor.visa.com/news/news-details/2025/Visa-Introduces-Trusted-Agent-Protocol-An-Ecosystem-Led-Framework-for-AI-Commerce/default.aspx): Visa, 2025-10-14, 조회일 2026-08-27
- [Accelerating the Adoption of Software and AI Agent Identity and Authorization](https://csrc.nist.gov/pubs/other/2026/02/05/accelerating-the-adoption-of-software-and-ai-agent/ipd): NIST NCCoE, Initial Public Draft 2026-02-05, 조회일 2026-08-27
- [knowyouragent.network](https://knowyouragent.network/): RNWY 스코어 인덱서, 조회일 2026-08-27
- [ERC-8004 Explained: What It Solves and the Gap It Leaves](https://www.concordium.com/article/erc-8004-explained-what-it-solves-and-the-gap-it-leaves): Concordium(CIS-8004), 조회일 2026-08-27
- [arXiv 2606.26028](https://arxiv.org/abs/2606.26028): ERC-8004 3체인 실증 연구, 조회일 2026-08-27
- [Know Your .agent?](https://estherdyson.substack.com/p/know-your-agent): Esther Dyson, 2026-05-06, 조회일 2026-08-27
