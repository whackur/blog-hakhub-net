---
title: "KYA(Know Your Agent): AI 에이전트 신원 검증, 표준 경쟁과 온체인 실태"
meta_title: ""
description: "AI 에이전트의 신원·인증·권한·평판을 구분하고, ERC-8004의 표준 상태와 실제 메인넷 활동, Visa TAP·Trulioo·Sumsub이 제공하는 검증의 범위와 한계를 설명합니다."
date: 2026-08-27T10:00:00+09:00
lastmod: 2026-10-15T15:36:42Z
image: "/images/posts/know-your-agent-kya-ai-agent-identity-onchain/kya-identity-editorial-20261016.webp"
categories: ["Blockchain"]
tags: ["ai-agent", "kya", "identity", "erc-8004", "reputation", "compliance"]
author: "whackur"
translationKey: "know-your-agent-kya-ai-agent-identity-onchain"
draft: false
---

AI 에이전트가 신원 인증서나 온체인 등록 번호를 제시해도, 그 사실만으로 결제나 데이터 접근을 허용해서는 안 됩니다. **어느 에이전트인지, 요청자가 그 신원을 통제하는지, 지금 하려는 행동을 위임받았는지, 과거 평가를 얼마나 믿을지**는 서로 다른 확인입니다. KYA(Know Your Agent)는 이런 확인을 묶어 부르는 이름입니다. ERC-8004는 식별자와 공개된 신뢰 신호를 제공하고, Visa TAP이나 신원 검증 업체는 요청·조직·사람을 확인하는 다른 방식을 제공합니다. 최종 접근 결정은 서비스를 제공하는 쪽에 남습니다. [ERC-8004 명세](https://eips.ethereum.org/EIPS/eip-8004)와 [Trulioo의 제품 설명](https://www.trulioo.com/products/kya-verification)도 각각 등록과 검증이 보장하는 범위를 제한합니다.

*표준 상태와 제품 설명 확인: 2026년 10월 16일 KST. 과거 측정 결과에는 별도의 관찰 기간을 표시했습니다.*

## 신원·인증·권한·평판의 구분

쇼핑 에이전트가 상품을 검색하다가 구매 API를 호출했다고 가정해 보겠습니다. 등록 번호가 맞는지 확인하는 것과 구매를 승인하는 것은 다른 작업입니다.

| 구분 | 확인하는 내용 | 구매 요청에서 필요한 증거 |
| --- | --- | --- |
| 신원(identity) | 어떤 에이전트를 가리키는가 | 레지스트리 주소와 에이전트 ID, 운영 조직 정보 |
| 인증(authentication) | 요청자가 해당 신원의 키나 자격 증명을 통제하는가 | 서명 검증, 신뢰하는 발급자·키와의 연결, 요청의 유효 시간 |
| 권한(authorization) | 이 주체가 이 행동을 해도 되는가 | 사용자가 허용한 상점·상품·금액·기간, 재위임 조건 |
| 평판(reputation) | 과거 평가가 이번 결정에 얼마나 도움이 되는가 | 평가자, 평가 대상 작업, 점수 단위, 근거와 철회 여부 |

가령 사용자가 특정 상점에서 총 10만 원까지, 30분 동안만 구매하도록 허용했다면 유효한 에이전트 서명도 12만 원짜리 주문을 정당화하지 못합니다. 이 금액과 시간은 권한 설계의 예시입니다. 검색 권한과 구매 권한을 나누고, 구매 API나 지갑이 실행 직전에 조건을 검사해야 합니다. 좋은 평판이 있다고 한도를 넘겨도 되는 것은 아닙니다.

운영자 확인도 별도입니다. 키를 통제하는 주소를 알아도 그 뒤의 법인이나 사람을 바로 알 수는 없습니다. 모델·코드의 출처를 기록하는 일 역시 요청 서명과 다릅니다. [NIST는 에이전트에 사용자 자격 증명을 그대로 넘기거나 넓은 권한을 오래 유지하는 관행](https://www.nist.gov/blogs/cybersecurity-insights/back-future-why-agentic-ai-needs-strong-identity-foundation)이 책임 추적과 접근 통제를 약화한다고 지적합니다. 중앙 플랫폼 안에서도 이 구분은 필요합니다.

## ERC-8004가 연결하는 정보

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004)는 Identity, Reputation, Validation 레지스트리를 정의합니다. Identity는 ERC-721 토큰으로 에이전트를 식별하고, Reputation은 피드백을 기록하며, Validation은 검증 요청과 검증자의 응답을 연결합니다. 결제 자체는 명세의 범위 밖입니다.

Identity를 조회할 때는 `agentId`만으로 부족합니다. 같은 번호가 여러 체인과 레지스트리에 존재할 수 있으므로 체인·레지스트리를 나타내는 `agentRegistry`와 `agentId`를 함께 사용합니다. 토큰의 `agentURI`가 가리키는 등록 파일에는 이름과 설명, Agent2Agent(A2A)의 AgentCard나 Model Context Protocol(MCP) 서비스 주소, 지원하는 신뢰 방식 등이 들어갑니다. 이 정보는 상대를 찾는 출발점이며, 선언한 기능이 실제로 동작하거나 안전하다는 보증은 아닙니다.

등록 파일과 서비스 주소의 연결도 확인해야 합니다. 명세에는 서비스 도메인에 `/.well-known/agent-registration.json`을 게시하고 등록 정보를 맞춰 보는 선택적 도메인 검증 절차가 있습니다. 아무 도메인이나 등록 파일에 적는 것과 그 도메인을 통제한다는 증거는 다릅니다. 소유자나 승인된 관리자가 `agentURI`를 바꿀 수도 있으므로, 중요한 거래에서는 조회 시점의 파일과 소유권을 기록하는 편이 좋습니다.

`agentWallet`은 **대금을 받는 주소**입니다. 등록 때는 소유자 주소로 설정되고, 다른 주소로 바꾸려면 새 지갑의 통제권을 EIP-712 서명 또는 스마트 컨트랙트 지갑의 ERC-1271 검증으로 증명해야 합니다. 토큰이 이전되면 이 연결은 해제됩니다. 이는 수취 주소의 연결 절차이며, 사용자 자산을 지출할 권한이나 운영자의 실명을 증명하지 않습니다. [참조 구현](https://github.com/erc-8004/erc-8004-contracts)도 이 초기화·변경·이전 규칙을 설명합니다.

Validation은 작업 입력과 출력 등의 자료에 대한 요청 해시를 남기고 지정한 검증자가 응답하도록 하는 인터페이스입니다. 재실행, 영지식 머신러닝(zkML) 증명, 신뢰 실행 환경(TEE) 기반 검증 등을 연결할 수 있지만, 레지스트리가 그 모든 검증을 자동 수행하지는 않습니다. 무엇을 검증했는지, 어떤 검증자를 신뢰하는지까지 확인해야 합니다.

## 표준 상태와 메인넷 활동은 서로 다른 증거입니다

공식 원문의 상태와 구현 저장소가 보여 주는 배포 정보를 구분하면 다음과 같습니다.

| 문서 | 공식 프로세스 상태 | 문서가 다루는 범위 | 상태만으로 판단할 수 없는 것 |
| --- | --- | --- | --- |
| [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) | Draft | 에이전트 식별·평판·검증 레지스트리 | 배포된 버전의 일치 여부, 사용량, 서비스 품질 |
| [ERC-8126](https://eips.ethereum.org/EIPS/eip-8126) | Final | AI Agent Verification | 실제 검증 사업자의 배포와 검증 품질 |
| [ERC-8196](https://eips.ethereum.org/EIPS/eip-8196) | Final | 정책에 맞는 증명을 동반한 지갑 실행과 위임 | 특정 지갑의 구현·운영·채택 여부 |

Draft여도 컨트랙트를 배포하고 사용할 수 있습니다. Final은 [EIP 프로세스의 문서 상태](https://eips.ethereum.org/EIPS/eip-1)이며, 네트워크 활성화나 보안 인증을 뜻하지 않습니다. 이 세 문서를 모든 KYA 서비스가 반드시 함께 구현해야 하는 단일 스택으로 볼 근거도 없습니다.

ERC-8004의 [참조 구현 저장소](https://github.com/erc-8004/erc-8004-contracts)는 Ethereum과 Base 메인넷의 Identity·Reputation 주소를 공개합니다. Ethereum Identity 주소 `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`에서는 **2026년 10월 15일 15:17:23 UTC, 블록 26,198,758의 성공한 등록 트랜잭션**에 `Registered` 이벤트와 `agentId = 54155`가 기록됐습니다. [해당 트랜잭션](https://eth.blockscout.com/tx/0x97c640ad052770b66f9744c1318555ccd894e2e0cea215c41dbd86754aa34308)은 명세만 존재하는 단계가 아니라 실제 등록 호출이 있다는 구체적인 증거입니다. [Reputation 주소의 로그](https://eth.blockscout.com/address/0x8004BAa17C55a88189AE136b182e5fdA19dE9b63?tab=logs)에서도 `NewFeedback` 이벤트가 확인됩니다.

이 이벤트로 유료 고객 수나 자율적으로 일하는 에이전트 수를 계산할 수는 없습니다. ID는 식별 번호이고, 등록은 서비스 실행과 다릅니다. 참조 저장소는 Validation Registry 부분이 TEE 커뮤니티와 논의하며 갱신 중이라고도 경고합니다. 배포 목록에 있는 Identity·Reputation을 근거로 세 레지스트리가 같은 수준으로 운영된다고 확대 해석해서는 안 됩니다.

등록과 실제 서비스의 차이는 실증 연구에서도 드러납니다. Xiong 등의 [ERC-8004 연구 v2](https://arxiv.org/html/2606.26028v2)는 배포 초기부터 **2026년 5월 13일까지** Ethereum·BNB Smart Chain(BSC)·Base를 관찰했습니다. 본문의 분류 기준인 ‘읽을 수 있는 등록 파일이 정해진 `type` 값을 갖고 서비스를 하나 이상 선언한 경우’는 각 체인 등록의 약 **3%·4%·15%**였습니다. 이는 해당 기간과 분류 기준의 결과입니다. 서비스 선언을 과업 수행 능력으로 보거나, 이 비율을 10월의 가동률로 읽으면 안 됩니다.

## 평판은 평가자와 단위까지 읽어야 합니다

[Reputation 명세](https://eips.ethereum.org/EIPS/eip-8004#reputation-registry)의 `value`와 `valueDecimals`는 범용 숫자 표현입니다. 예를 들어 `9977`과 `2`는 `99.77`을 나타내지만, 가동률인지 점수인지는 태그와 근거를 봐야 합니다. 응답 시간과 별점, 누적 매출을 한 점수처럼 평균 내면 의미가 사라집니다.

에이전트 소유자와 승인된 운영자는 자신의 에이전트에 피드백을 남길 수 없습니다. 그러나 이 제한이 한 주체의 여러 주소 생성을 막지는 못합니다. 명세도 Sybil 공격 가능성을 인정하며, `getSummary`에는 비어 있지 않은 `clientAddresses` 목록을 요구합니다. 집계하는 쪽이 어떤 평가자를 신뢰하는지 선택해야 한다는 뜻입니다.

근거 파일도 세심하게 읽어야 합니다. `feedbackURI`와 `feedbackHash`는 선택 항목입니다. 특히 **`feedbackHash = 0`만으로 근거가 없다고 단정할 수 없습니다.** IPFS처럼 콘텐츠 자체로 주소를 정하는 URI는 별도 해시를 생략할 수 있습니다. 반대로 해시가 있다고 평가 내용이 사실이 되는 것도 아닙니다. 해시는 파일의 무결성을 확인하는 수단입니다.

실제 의사결정에서는 신뢰하는 평가자의 기록을 고르고, 태그·단위·철회 여부를 확인한 뒤, 필요한 경우 근거 파일을 가져와 무결성과 작업 내용을 대조하는 순서가 적절합니다. 결제 증거가 붙어 있어도 결제 사실과 결과 품질은 구분해야 합니다. 명세에 있는 선택적 `proofOfPayment`도 품질 보증서가 아닙니다.

## Visa·Trulioo·Sumsub이 확인하는 대상

이 접근들은 같은 기능을 놓고 겨루는 완전한 대체재가 아닙니다. 레지스트리에 등록된 에이전트가 HTTP 요청에 서명하면서 별도의 조직 검증도 받을 수 있습니다.

| 접근 | 확인 방법과 신뢰하는 주체 | 적용할 때 남는 조건 |
| --- | --- | --- |
| ERC-8004 | 온체인 소유권과 공개된 피드백·검증 기록 | 요청 인증, 운영자 실사, 평가자 선정과 실행 권한은 별도 |
| Visa Trusted Agent Protocol(TAP) | 공개 키와 HTTP 메시지 서명으로 에이전트 요청·행동 맥락 확인 | 키의 신뢰성, 요청의 유효성, 상점의 정책 판단 필요 |
| Trulioo KYA | 개발 조직 확인과 에이전트 정보를 서명된 DAP에 연결 | Alpha 제품의 제공 범위와 자격 증명 상태, 접근 정책 확인 |
| Sumsub AI Agent Verification | 자동화 탐지와 위험 평가, 검증된 사람과의 연결 | 위험에 따른 추가 검사와 필요한 시점의 사람 확인 |

[Visa의 공식 저장소](https://github.com/visa/trusted-agent-protocol)는 RFC 9421 기반 HTTP 메시지 서명과 키 레지스트리, 상점의 검증 흐름을 예제로 제공합니다. 상점은 요청에서 서명 대상 문자열을 재구성하고 공개 키로 검증합니다. 시간과 세션 정보, 도메인·행동 맥락을 확인하는 것도 필요합니다. 이 방식의 핵심은 요청을 검증하는 것이며, ERC-8004 등록을 전제로 하지 않습니다. 공개된 샘플 구현을 전체 가맹점의 도입 실적으로 볼 수도 없습니다.

[Trulioo의 현재 제품 페이지](https://www.trulioo.com/products/kya-verification)는 DAP를 **Digital Agent Profile**이라고 부릅니다. 개발 조직의 기업 신원 확인(KYB)·자금세탁방지(AML) 검사와 도메인 통제 확인, 에이전트의 목적·권한 등 정보를 묶고, 기간과 범위를 정한 서명 자격 증명 및 상태 조회를 설명합니다. 페이지는 KYA를 Alpha로 표시하며 조직 도메인이 활성화된 경우 등록할 수 있다고 안내합니다. 업체도 자격 증명이 향후 안전한 행동을 보장하지 않으며 접근 결정은 이용 조직이 내린다고 명시합니다.

[Sumsub의 2026년 1월 29일 발표](https://sumsub.com/newsroom/sumsubs-ai-agent-verification-introduces-agent-to-human-binding-to-establish-human-accountability-in-ai/)는 에이전트 활동을 검증된 사람과 연결하는 접근입니다. 먼저 자동화를 탐지하고 위험을 평가하며, 위험이 높은 경우 등에 필요한 추가 검사로 실제 사람이 있는지 확인하는 liveness 검사를 요구할 수 있다고 설명합니다. 모든 행동마다 얼굴 확인을 받는 방식으로 일반화해서는 안 됩니다. 사람과의 연결은 책임 추적에 도움이 되는 정보지만, 특정 행위의 법적 책임을 그 연결만으로 확정하지는 못합니다.

## 실행 시점에 남는 통제

KYA를 도입할 때는 등록 방식보다 먼저 허용할 행동을 정하는 편이 실용적입니다. 공개 문서 검색, 개인정보 열람, 결제는 잘못 실행됐을 때의 영향이 다르기 때문입니다. 앞의 구매 예시라면 다음 조건을 실제 API나 지갑이 집행해야 합니다.

1. 등록 정보·조직 자격 증명과 요청 서명을 확인하고, 키나 자격 증명이 만료·철회됐으면 거부합니다.
2. 위임한 사람, 허용 상점, 총액과 유효 기간을 구매 요청에 대조합니다. 하위 에이전트로 넘길 때는 원래보다 넓은 권한을 주지 않습니다.
3. 중복 요청과 한도 소비를 실행 시점에 처리합니다. 이미 쓴 예산을 평판이나 과거 승인으로 다시 사용할 수 없게 합니다.
4. 판단에 사용한 정책·자격 증명·작업 버전과 실행 결과를 기록합니다. 모델·프롬프트·도구가 바뀌면 이전 검증이 무엇까지 설명하는지 다시 평가합니다.

이 순서는 특정 표준의 의무 절차가 아니라, 신원 확인과 행동 허가를 분리하는 설계 예시입니다. [NIST의 현재 프로젝트 허브](https://pages.nist.gov/nccoe-ai-identity/)도 기존 신원·권한 표준을 에이전트에 적용하는 실무 지침과 SP 1800 계열 가이드를 목표로 제시합니다. 이를 법으로 의무화된 KYA 인증 제도로 읽어서는 안 됩니다. NIST는 사람 승인을 지나치게 자주 요구하면 승인 피로 때문에 통제가 약해진다는 점도 [지적합니다](https://www.nist.gov/blogs/cybersecurity-insights/back-future-why-agentic-ai-needs-strong-identity-foundation).

공개 레지스트리에 실명이나 상세 작업 기록을 남기는 방식도 신중히 정해야 합니다. 식별자와 공개 주소를 연결하는 정보는 장기 추적을 쉽게 만들 수 있습니다. 필요한 증명과 공개 범위를 구분하고 민감한 자료는 접근을 통제하는 설계가 적절합니다.

온체인 기록이 주는 이점은 서로 다른 조직이 같은 식별자와 기록을 조회할 수 있다는 데 있습니다. 그 기록에서 신뢰할 평가자의 평가를 고르고, 현재 요청을 인증하고, 위임 범위 안에서 실행하도록 만드는 일은 서비스를 운영하는 쪽의 책임으로 남습니다.

## 함께 보면 좋을 자료

- [ERC-8004 참조 구현](https://github.com/erc-8004/erc-8004-contracts): 배포 주소, 등록·평판 조회 흐름과 Validation의 갱신 상태.
- [Visa TAP 샘플 구현](https://github.com/visa/trusted-agent-protocol): 요청 서명과 상점 검증을 구성하는 예제.
- [NIST 에이전트 신원·권한 리소스 허브](https://pages.nist.gov/nccoe-ai-identity/): 기업 환경의 신원·위임·접근 통제 논의.

## 참고 자료

아래 자료는 2026년 10월 16일 KST에 확인했습니다.

- [ERC-8004: Trustless Agents](https://eips.ethereum.org/EIPS/eip-8004), [공식 raw 원문](https://raw.githubusercontent.com/ethereum/ERCs/master/ERCS/erc-8004.md): 식별·평판·검증과 보안상 제한.
- [ERC-8126: AI Agent Verification](https://eips.ethereum.org/EIPS/eip-8126), [ERC-8196: AI Agent Authenticated Wallet](https://eips.ethereum.org/EIPS/eip-8196), [EIP-1](https://eips.ethereum.org/EIPS/eip-1): 인터페이스와 표준 프로세스 상태.
- [ERC-8004 contracts](https://github.com/erc-8004/erc-8004-contracts): 배포 목록과 참조 구현.
- [Ethereum 등록 트랜잭션](https://eth.blockscout.com/tx/0x97c640ad052770b66f9744c1318555ccd894e2e0cea215c41dbd86754aa34308), [Reputation 로그](https://eth.blockscout.com/address/0x8004BAa17C55a88189AE136b182e5fdA19dE9b63?tab=logs): 실제 레지스트리 활동의 사례.
- [Can Trustless Agents Be Trusted? v2](https://arxiv.org/html/2606.26028v2): Xiong 외, 2026년 7월 8일 개정. 5월 13일까지의 3체인 관찰, 특히 등록 파일 분류와 연구 한계.
- [Visa Trusted Agent Protocol](https://github.com/visa/trusted-agent-protocol): 공식 설명과 샘플 구현.
- [Trulioo KYA](https://www.trulioo.com/products/kya-verification): Digital Agent Profile, Alpha 제공 조건과 검증 범위.
- [Sumsub AI Agent Verification](https://sumsub.com/newsroom/sumsubs-ai-agent-verification-introduces-agent-to-human-binding-to-establish-human-accountability-in-ai/): 위험에 따른 사람 확인과 에이전트 연결.
- [NIST 프로젝트 허브](https://pages.nist.gov/nccoe-ai-identity/), [Back to the Future: Why Agentic AI Needs a Strong Identity Foundation](https://www.nist.gov/blogs/cybersecurity-insights/back-future-why-agentic-ai-needs-strong-identity-foundation): 프로젝트 목표와 신원·권한 관리의 실패 양상.
