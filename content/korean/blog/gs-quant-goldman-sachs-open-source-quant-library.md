---
title: "gs-quant: 골드만삭스가 퀀트 코드를 오픈소스로 공개한 방식과 그 경계"
meta_title: "gs-quant 골드만삭스 오픈소스 퀀트 라이브러리 리뷰"
description: "골드만삭스의 Python 퀀트 툴킷 gs-quant가 무엇인지, 2018년 저장소 생성부터 OSPO 출범까지의 공개 배경, 코드 구조에서 드러나는 로컬 영역과 Marquee API 영역의 경계, 커뮤니티 반응과 한계를 연구·교육 관점에서 정리합니다."
date: 2026-08-26T10:00:00+09:00
lastmod: 2026-08-26T10:00:00+09:00
image: "/images/posts/gs-quant-goldman-sachs-open-source-quant-library/local-vs-api-boundary-1200.png"
categories: ["Finance"]
tags: ["quant-finance", "open-source", "python", "goldman-sachs"]
author: "whackur"
translationKey: "gs-quant-goldman-sachs-open-source-quant-library"
draft: false
---

투자은행의 트레이딩 코드가 GitHub에 올라와 있다고 하면 대부분 두 가지 반응으로 갈린다. "그걸 왜 공개하지"와 "진짜 중요한 건 안 올렸겠지". [goldmansachs/gs-quant](https://github.com/goldmansachs/gs-quant)는 이 두 반응이 모두 절반씩 맞는 사례다. 2018년 12월에 만들어진 이 저장소는 2026년 8월 기준 스타 12,000개를 넘겼고, 확인한 당일에도 push가 있을 만큼 활발하게 관리된다. 동시에 README는 가격결정과 리스크 API를 쓰려면 골드만삭스 기관 고객이어야 한다고 못박는다.

이 글은 gs-quant를 투자 도구로 소개하는 글이 아니다. 대형 은행이 자기 퀀트 코드를 어떤 형태로, 어디까지 공개했는지를 코드 구조와 공개 이력으로 읽어 보는 연구·교육용 코드 리뷰다. 퀀트 금융 툴킷이 무슨 일을 하는지부터 시작해서, Marquee, SecDB, Slang 같은 낯선 이름을 하나씩 풀고, 커뮤니티가 왜 "API 뒤에 다 있다"고 말하는지까지 따라간다. 이 글의 수치와 인용은 2026년 8월 26일에 GitHub API, PyPI, 공식 문서, 언론 기사, Hacker News 스레드를 직접 확인한 값이다.

## gs-quant는 골드만 엔진의 Python 인터페이스다

퀀트 금융 툴킷은 크게 세 가지 일을 한다. 시장 데이터를 가져와 정리하고, 금융 상품(옵션, 스왑, 채권 등 파생상품 포함)의 가격과 리스크를 계산하고, 그 계산을 묶어 전략을 시험하거나 포트폴리오를 관리한다. 이 중 두 번째가 가장 어렵다. 파생상품 가격결정 모델은 금리 곡선, 변동성 표면, 상관관계 같은 시장 파라미터를 끊임없이 갱신해야 하고, 은행은 이 계산 엔진을 수십 년에 걸쳐 쌓아 왔다.

gs-quant는 골드만삭스의 퀀트 개발자들이 만들고 유지하는 Python 툴킷이다. README는 "quantitative finance를 위한 Python toolkit"이자 "세계에서 가장 강력한 리스크 이전(risk transfer) 플랫폼 중 하나 위에 만들어졌고, 25년의 글로벌 시장 경험으로 다듬어졌다"고 소개한다. 트레이딩 전략 개발과 파생상품 분석을 빠르게 하도록 설계됐다는 설명이 붙는다. 여기서 "플랫폼 위에"라는 표현이 이 라이브러리의 성격을 결정한다. gs-quant는 가격결정 엔진 그 자체가 아니라, 골드만 내부 엔진에 접근하는 Python 인터페이스에 가깝다.

그 엔진이 있는 곳이 **Marquee**다. Marquee는 골드만삭스가 기관 고객에게 제공하는 디지털 플랫폼으로, PyPI의 gs-quant 홈페이지 주소도 marquee.gs.com이다. README는 API를 쓰려면 client id와 secret이 필요하고, 이는 골드만삭스 기관 고객에게 제공되며 세일즈 담당자나 Marquee Sales에 문의하라고 안내한다. [Marquee의 gs-quant 소개 페이지](https://marquee.gs.com/welcome/our-platform/gs-quant)는 FX 파생상품을 폭넓게 다룬다는 점을 내세운다.

골드만이 2022년 LinuxCon Japan에서 발표한 [OSPO 소개 자료](https://static.sched.com/hosted_files/ossjapan2022/01/2022-LinuxCon-GS-OSPO.pdf)는 이 분석 도구를 골드만 내부에서 1천 명 이상의 퀀트 개발자가 매일 사용해 글로벌 트레이딩 비즈니스를 관리한다고 설명한다. 같은 문구가 [공식 문서](https://developer.gs.com/docs/gsquant/)의 Key Features에도 "Designed by our quants"라는 제목으로 실려 있다. 즉 gs-quant의 1차 사용자는 골드만 내부와 기관 고객이고, GitHub의 일반 사용자는 그 다음이다.

## 공개의 역사

gs-quant의 공개 시점을 하나의 날짜로 말하기는 어렵다. 저장소와 언론 보도가 보여 주는 흐름은 다음과 같다.

- **2018년 12월 14일**: GitHub 저장소 생성(첫 commit "Initial commit"). 같은 달 23일에 PyPI 첫 배포(0.4.8).
- **2019년 4월 3일**: WSJ가 "Goldman's Trading Floor Is Going Open-Source, Kind of"라는 기사를 낸다. 요지는 골드만이 그달 안에 자사 트레이더와 엔지니어가 증권 가격결정과 리스크 분석·관리에 쓰는 코드 일부를 GitHub에 공개할 계획이라는 것이었다. 같은 날 [Hacker News 스레드](https://news.ycombinator.com/item?id=19562224)가 만들어졌다. WSJ [영상](https://www.wsj.com/video/the-latest-on-goldman-sachs-open-source-trading-floor/4C614C58-03BC-4EB8-A65C-DE923E09FA90)은 개발자들이 리스크 평가와 파생상품 가격결정에 쓰이던 비공개 코드에 접근할 수 있게 됐다고 요약했다.
- **2019년 11월 20일**: CNBC가 [골드만이 월스트리트에 소프트웨어를 무료로 내놓는다](https://www.cnbc.com/2019/11/20/goldman-sachs-is-giving-away-software-to-wall-street-for-free.html)고 보도한다. 이 기사의 주제는 gs-quant가 아니라 데이터 모델링 플랫폼 Legend(당시 Alloy)다.
- **2020년 10월 19일**: Linux Foundation이 [골드만이 Legend를 FINOS에 오픈소스로 기부했다](https://www.linuxfoundation.org/press/press-release/goldman-sachs-open-sources-its-data-modeling-platform-through-finos)고 발표한다. FINOS(Fintech Open Source Foundation)는 금융권 오픈소스 협업을 위한 Linux Foundation 산하 재단이다.
- **2021년**: 골드만삭스 OSPO(Open Source Program Office)가 4월에 승인(chartered)되고 8월에 공식 출범한다.

저장소가 2018년 12월에 이미 존재했으니 WSJ 기사는 "처음 공개"가 아니라 공개 범위 확대의 예고로 읽는 편이 맞다. "2020년 3월 공개"라는 특정 시점 역시 이번에 확인한 어떤 언론 보도로도 뒷받침되지 않았다. 이 글에서는 위의 타임라인만 사실로 다루고 특정 공개일을 단정하지 않는다.

이 흐름에서 보이는 것은 gs-quant가 단독 이벤트가 아니었다는 점이다. 2019년의 gs-quant 공개 확대, 2019~2020년의 Legend 기부, 2021년의 OSPO 설립은 골드만이 오픈소스를 일회성 홍보가 아니라 조직 기능으로 편입한 과정이다. 골드만은 지금도 [developer.gs.com의 오픈소스 포털](https://developer.gs.com/discover/open-source)에서 공개 프로젝트를 모아 보여 준다.

## 코드 구조로 보는 실제 동작 방식

GitHub contents API로 확인한 `gs_quant/` 패키지 하위 구조는 다음과 같다.

```text
gs_quant/
  analytics/      api/          backtests/    config/
  content/        data/         datetime/     documentation/
  entities/       instrument/   interfaces/   markets/
  mcp/            models/       quote_reports/ risk/
  skills/         target/       session.py    priceable.py
```

공식 문서의 목차와 나란히 놓으면 구조가 읽힌다. 문서는 Overview, Getting Started, Authentication(Sessions, GS Session, Proxy), Data(Data Environment, Accessing Data, Data Analytics, Data Visualization), Pricing and Risk(Instruments, Measures, Pricing Context, Portfolios, Scenarios), Markets(Assets and SecurityMaster, Relative Dates), Hedging(Hedging Using ML), Contribute, SDK Reference 순이다. Authentication이 Data와 Pricing 앞에 온다는 점이 이 라이브러리의 사용 순서를 그대로 말해 준다.

![gs-quant에서 로컬로 동작하는 timeseries·datetime·instrument 정의·backtests 골격 코드 영역과, GsSession을 거쳐 Marquee 원격 API로 호출되는 Pricing and Risk·Data·Markets·Hedging 영역을 나눈 구조도](/images/posts/gs-quant-goldman-sachs-open-source-quant-library/local-vs-api-boundary.svg)

*gs-quant의 로컬 영역과 API 영역. README와 공식 문서 구조를 바탕으로 재구성한 도식이며, 모듈별 세부 동작은 저장소 코드에서 확인해야 한다.*

동작 방식은 두 층으로 나뉜다.

**로컬에서 도는 층.** timeseries 계열의 통계·분석 헬퍼, 영업일 계산 같은 datetime 유틸리티, 그리고 금융 상품을 타입이 있는 Python 객체로 표현하는 instrument 정의는 계정 없이 설치만 하면 쓸 수 있다. backtests와 models 디렉터리의 전략 골격 코드도 저장소 안에 있지만, 전략을 실제로 평가하는 단계는 다시 API를 부르는 구조로 보인다. README와 구조로 확인되는 범위에서는 이 정도가 순수 로컬 영역이다. Hacker News에서 한 사용자가 `timeseries/statistics.py` 안에 전염병 확산을 모델링하는 SIR/SEIR 컴파트먼트 모델 클래스가 들어 있다는 것을 발견했는데, 2020년 3월 코로나 시기에 추가된 것으로 추정하는 댓글이 있었다. 금융 툴킷에 역학 모델이 들어 있는 것이 어색해 보이지만, 로컬 계산 층이 실제로 "그냥 Python 코드"라는 점을 보여 주는 예이기도 하다.

**API를 호출하는 층.** 파생상품 가격결정, 리스크 측정치, 시나리오 분석, 데이터셋 조회, SecurityMaster를 통한 자산 식별, ML 기반 헤징은 전부 Marquee 쪽 엔진이 계산한다. Python 객체는 요청을 구성하고 결과를 받아 오는 역할이다. 이 층에 들어가는 문은 `gs_quant/session.py`의 `GsSession`이다.

설치는 Python 3.9 이상에서 pip로 한다.

```bash
pip install gs-quant
```

세션의 개념은 이렇게 잡으면 된다. 실제 인증 정보는 코드에 쓰지 않고 환경 변수나 별도 설정 파일로 관리하는 것이 안전하다.

```python
from gs_quant.session import GsSession, Environment

# GsSession.use(...)로 Marquee 세션을 연다.
# client id / secret은 기관 고객에게 발급되며,
# 코드에 직접 쓰지 말고 환경 변수 등 외부에서 주입한다.
```

여기서 API 게이팅이 왜 중요한지가 드러난다. 오픈소스 라이선스는 Apache-2.0이지만, 라이브러리가 하는 일의 핵심(가격결정·리스크·데이터)은 라이선스가 적용되는 코드 밖, 즉 골드만 서버 안에 있다. 코드를 읽고 수정하고 재배포할 자유는 있지만, 그 코드가 의미 있는 결과를 내려면 계약 관계가 필요하다. 오픈소스 클라이언트와 비공개 서비스의 조합이라는 점에서, 클라우드 SDK를 오픈소스로 풀고 서비스는 유료로 파는 구조와 같은 종류다.

패키지 구조에서 눈에 띄는 최근 변화가 `gs_quant/mcp/`다. client.py, config.py, dependencies.py, middleware.py, run.py, session_utils.py와 tools/ 디렉터리로 구성된 MCP(Model Context Protocol) 서버 통합이 들어 있다. 저장소 루트에는 Claude Code용 `.claude/skills` 디렉터리도 있고, 2026년 8월 18일에는 OpenAgentSkill에 ["Gs Quant: Finance & Market Analysis for AI Agents"](https://www.openagentskill.com/skills/goldmansachs-gs-quant)라는 이름으로 등록됐다. 은행의 퀀트 툴킷이 AI 에이전트가 호출하는 도구 형태를 갖추기 시작했다는 뜻인데, 물론 이 경로도 Marquee 계정이라는 같은 문을 지나야 한다.

## 커뮤니티 반응

반응은 두 시점으로 나뉜다. 공개 확대가 예고된 2019년 4월과, 라이브러리가 자리 잡은 뒤의 2024년 6월이다. 두 스레드의 논점을 패러프레이즈로 정리한다.

[2019년 4월 3일 스레드](https://news.ycombinator.com/item?id=19562224)(189포인트, 댓글 96개)는 회의론이 많았다. 호의적인 쪽의 대표는 이런 논리였다. 시장보다 정확한 가격결정 기술이었다면 돈을 찍어낼 수 있으니 공개하지 않았을 테고, 결국 표준적이고 잘 알려진 가격·리스크 모델의 구현이겠지만, 그래도 직접 만드는 비용이 들기 때문에 유용하다. 반대편에는 PR이나 마케팅에 가깝다는 시선, 골드만이 잘 아는 코드를 많은 투자자가 쓰면 골드만에 유리한 방향으로 시장이 움직일 수 있다는 의심, NSA가 암호 스킴에 심은 magic number 같은 "독약"이 들어 있을지 모른다는 농담까지 있었다. 그 시점에 GitHub에는 LICENSE 파일만 올라와 있다는 지적도 나왔다. 몇 년 전 골드만 개발자가 업무 환경에서 GitHub 웹사이트조차 열 수 없었다는 일화를 들어, 가장 폐쇄적이던 회사가 바뀌는 중이라는 관찰도 있었다.

가장 밀도 있는 토론은 [2024년 6월 29일 스레드](https://news.ycombinator.com/item?id=40831991)(285포인트, 댓글 60개)다. 5년 사이 질문은 "정말 공개하나"에서 "공개된 것으로 무엇을 할 수 있나"로 옮겨 갔다.

비판의 중심은 예상대로 API 게이팅이었다. 외부인에게 실제로 유용한 부분은 전부 골드만 데이터 API 뒤에 있어서 설계를 공부하는 용도 이상은 어렵다는 지적, 툴킷은 무료여도 데이터는 매우 비싸다는 지적이 나왔다. README가 외부에 유용한 정보보다 골드만이 무엇을 하는지 알리는 광고에 가깝다는 평가도 있었다. 실습 자료 측면에서는 영상 링크 몇 개가 있을 뿐이라 코드를 영상에서 베껴 써야 하느냐는 불만이 있었다.

코드 자체의 성격을 두고는 의견이 갈렸다. 기본적인 금융 데이터 구조 클래스 모음에 가깝다는 평가에, 도메인 라이브러리는 대부분 그 수준이라는 반론이 붙었다. 이 논쟁은 gs-quant의 로컬 층을 어떻게 보느냐의 문제다. 계산 엔진을 기대하면 실망하고, 잘 정리된 도메인 모델과 API 클라이언트로 보면 평가가 달라진다.

스레드에서 **SecDB**와 **Slang** 이야기가 나온 것도 짚어 둘 만하다. 한 댓글은 Slang이 여전히 핵심이고 SecDB, 즉 마켓 비즈니스의 신경계를 구동한다고 설명했다. SecDB는 골드만 내부의 증권·리스크 데이터베이스 겸 계산 시스템으로, Slang은 그 위에서 쓰는 자체 언어로 알려져 있다. 이 맥락에서 gs-quant를 보면 위치가 분명해진다. gs-quant는 SecDB를 대체하거나 공개한 것이 아니고, 그 시스템의 결과물을 Python에서 받아 쓰는 바깥쪽 껍질이다. 골드만이 공개한 것은 껍질이고, 신경계는 여전히 안에 있다.

마지막으로 "이걸로 당신이 돈을 버는 게 아니다"라는 취지의 댓글이 있었다. 개인이 오픈소스 퀀트 코드를 만났을 때 가장 먼저 새겨야 할 문장이라고 생각한다.

## 현재 상태와 유지보수

2026년 8월 26일에 확인한 저장소 상태다.

| 항목 | 값 |
| --- | --- |
| stars / forks / watchers | 12,491 / 1,669 / 164 |
| license | Apache-2.0 |
| 기본 브랜치 / 언어 | master / Python |
| 저장소 생성 | 2018-12-14 |
| 마지막 push | 2026-08-26 (확인 당일) |
| commit 수 | 약 569개 |
| 최신 GitHub release | release-2.1.4 (2026-08-17) |
| PyPI | 최신 2.1.4, 첫 배포 0.4.8 (2018-12-23), 누적 버전 533개 |

최근 릴리스는 release-2.1.1(2026-07-15), 2.1.2(2026-08-03), 2.1.3(2026-08-07), 2.1.4(2026-08-17)로 수일에서 수주 간격이다. GitHub Releases API에서 확인되는 가장 오래된 태그 릴리스는 release-0.8.131(2020-05-18)인데, PyPI 첫 배포가 2018년 12월이므로 초기 버전은 GitHub Release 없이 PyPI로만 나갔다고 보는 게 자연스럽다. PyPI 누적 버전 533개는 이 라이브러리가 내부 배포 주기에 맞춰 잦은 소규모 릴리스를 반복해 왔다는 신호다.

유지보수 주체는 골드만삭스로 보인다. 외부 기여가 어느 정도 받아들여지는지는 이번에 확인하지 못했으므로 수치로 말하지 않는다. 공식 문서에 Contribute 섹션이 있다는 점만 적어 둔다.

생태계 쪽 신호도 있다. [MSCI와 골드만삭스의 협업 발표](https://ir.msci.com/news-releases/news-release-details/goldman-sachs-and-msci-collaborate-deliver-improved-risk)는 MSCI의 리스크 팩터 모델을 골드만 API와 GS Quant로 제공한다고 밝혔다. gs-quant가 골드만 내부 모델뿐 아니라 제3자 리스크 모델의 배포 채널 역할도 한다는 뜻이다. 커뮤니티 큐레이션 쪽에서는 [HelloGitHub](https://hellogithub.com/en/repository/goldmansachs/gs-quant)가 Active 상태의 Apache-2.0 프로젝트로 등재하고 있다.

## 대안과 비교

gs-quant를 다른 도구와 비교할 때 스타 수나 기능 개수보다 중요한 것은 **계산이 어디서 일어나는가**다.

- **QuantLib**: C++로 짜인 완전 로컬 오픈소스 가격결정 라이브러리로, Python 바인딩이 있다. 금리 곡선 구축, 옵션 가격결정, 채권 분석 같은 계산이 전부 사용자 머신에서 돈다. 모델을 직접 고칠 수 있고 계정도 필요 없다. 대신 시장 데이터를 구해 오는 일과 모델 파라미터를 유지하는 일이 전부 사용자 몫이다.
- **OpenBB**: HN 스레드에서 대안으로 언급된 오픈소스 금융 데이터 플랫폼이다. 여러 데이터 소스를 하나의 인터페이스로 묶는 데 초점을 둔다.
- **QuantConnect**: 같은 스레드에서 언급된 알고리즘 트레이딩 플랫폼으로, 백테스팅 인프라와 데이터를 플랫폼이 제공한다.

gs-quant의 차별점은 "은행의 프로덕션 리스크 엔진을 호출한다"는 한 가지다. 같은 모델과 같은 시장 데이터로 골드만 내부 퀀트가 보는 숫자를 받는다는 것은 다른 오픈소스 도구가 줄 수 없는 것이다. 그 대가가 API 종속성이다. QuantLib이 "엔진을 주지만 데이터는 네가 구해라"라면, gs-quant는 "엔진과 데이터를 주지만 계약을 맺어라"에 가깝다. 어느 쪽이 나은지는 목적에 따라 갈리고, 이 글에서는 세부 수치 비교를 하지 않는다.

## 한계와 리스크

- **핵심 기능의 계정 의존.** 가격결정, 리스크, 데이터, 마켓 조회는 Marquee client id와 secret이 필요하고, 발급 대상은 기관 고객이다. 개인 개발자가 pip install 뒤에 할 수 있는 일은 로컬 계산 층과 코드 읽기로 한정된다.
- **오픈소스의 범위.** Apache-2.0은 저장소 안의 코드에만 적용된다. 계산 결과를 만드는 엔진은 공개 대상이 아니다. "골드만이 퀀트 코드를 오픈소스로 풀었다"는 문장은 이 범위를 명시하지 않으면 과장이 된다.
- **유지보수 구조.** 골드만 단독 주도로 보이며, 외부 기여 수용 규모는 확인하지 못했다. 회사 전략이 바뀌면 프로젝트 방향도 바뀔 수 있는 구조다.
- **학습 자료.** HN에서 지적된 대로 외부 사용자용 예제와 튜토리얼이 충분하다고 보기 어렵다. 공식 문서는 구조는 갖췄지만 실습은 API 접근을 전제한다.
- **오해의 위험.** 이 라이브러리는 투자 판단을 대신해 주지 않는다. 계산 결과를 받아 오는 도구이고, 그 결과를 어떻게 해석하고 무엇을 할지는 전적으로 사용자 책임이다. 이 글도 투자 조언이 아니다.

## 독자별 활용 방식

**읽어 볼 만한 사람.** 금융 도메인 모델을 Python 타입으로 어떻게 표현하는지 궁금한 개발자, 대형 은행이 오픈소스 클라이언트와 비공개 서비스를 어떻게 나누는지 사례를 찾는 사람, MCP 통합이 금융 툴킷에서 어떤 모양으로 들어가는지 보고 싶은 사람에게 코드 자체가 교재가 된다.

**써볼 만한 사람.** Marquee 계정이 있는 기관 사용자다. 이 경우 gs-quant는 골드만 엔진의 Python 인터페이스로서 본래 목적에 맞게 동작한다.

**기대를 조정해야 하는 사람.** 계정 없이 파생상품 가격을 계산하려는 개인이나 학생이다. 그 목적이라면 QuantLib 쪽이 맞고, gs-quant는 설계 참고용으로 곁에 두는 편이 낫다.

## 함께 보면 좋을 자료

- [Goldman Sachs 오픈소스 포털](https://developer.gs.com/discover/open-source): gs-quant 외에 골드만이 공개한 프로젝트 목록
- [Building the Open Source Program Office at Goldman Sachs (PDF)](https://static.sched.com/hosted_files/ossjapan2022/01/2022-LinuxCon-GS-OSPO.pdf): OSPO 설립 과정과 gs-quant의 내부 위치를 설명한 LinuxCon Japan 2022 발표 자료
- [Goldman Sachs Open Sources its Data Modeling Platform through FINOS](https://www.linuxfoundation.org/press/press-release/goldman-sachs-open-sources-its-data-modeling-platform-through-finos): 같은 시기의 Legend 기부 발표
- [Goldman Sachs open source toolkit: GS Quant](https://dev.to/mahlonzy/goldman-sachs-open-source-toolkit-gs-quant-4mg5): DEV Community의 외부 소개 글
- [Goldman Sachs GS-Quant: A Python Quant Toolkit Used on Wall Street](https://medium.com/coding-nexus/goldman-sachs-gs-quant-a-python-quant-toolkit-used-on-wall-street-764ef510a8d7): Medium(Coding Nexus)의 외부 리뷰

## 정리

gs-quant는 "골드만이 퀀트 코드를 공개했다"와 "핵심은 공개하지 않았다"가 동시에 참인 프로젝트다. 공개된 것은 도메인 모델, 시계열 헬퍼, 그리고 Marquee 엔진을 부르는 잘 만든 Python 클라이언트다. 공개되지 않은 것은 SecDB로 대표되는 계산 엔진과 데이터다. 2018년 저장소 생성, 2019년 WSJ 보도, 2020년 Legend 기부, 2021년 OSPO 출범으로 이어지는 흐름은 이 경계 설정이 즉흥이 아니라 조직 차원의 선택이었음을 보여 준다.

개인 개발자에게 이 저장소의 가치는 실행보다 독해에 있다. 은행이 금융 상품을 어떤 객체로 표현하고, 어디까지를 클라이언트에 두고 어디부터를 서버에 두는지, 그리고 최근에는 MCP와 에이전트 스킬을 어떻게 얹는지를 코드로 볼 수 있다. 그 이상을 기대하면 HN 댓글이 말한 대로 실망하게 된다.

## 참고 자료

- [goldmansachs/gs-quant](https://github.com/goldmansachs/gs-quant): GitHub, Apache-2.0. 조회일 2026-08-26
- [gs-quant on PyPI](https://pypi.org/project/gs-quant/): PyPI 릴리스 이력. 조회일 2026-08-26
- [GS Quant 공식 문서](https://developer.gs.com/docs/gsquant/): developer.gs.com. 조회일 2026-08-26
- [GS Quant on Marquee](https://marquee.gs.com/welcome/our-platform/gs-quant): Goldman Sachs Marquee. 조회일 2026-08-26
- [Goldman's Trading Floor Is Going Open-Source, Kind of](https://www.wsj.com/articles/goldmans-trading-floor-is-going-open-source-kind-of-11554285602): The Wall Street Journal, 2019-04-03 (구독 기사, 본문은 요약만 반영)
- [The Latest on Goldman Sachs's Open-Source Trading Floor](https://www.wsj.com/video/the-latest-on-goldman-sachs-open-source-trading-floor/4C614C58-03BC-4EB8-A65C-DE923E09FA90): The Wall Street Journal 영상
- [Goldman Sachs will open-source some of its trading software](https://news.ycombinator.com/item?id=19562224): Hacker News, 2019-04-03, 189포인트 댓글 96개. 조회일 2026-08-26
- [GS Quant 논의 스레드](https://news.ycombinator.com/item?id=40831991): Hacker News, 2024-06-29, 285포인트 댓글 60개. 조회일 2026-08-26
- [Goldman Sachs is giving away software to Wall Street for free](https://www.cnbc.com/2019/11/20/goldman-sachs-is-giving-away-software-to-wall-street-for-free.html): CNBC, 2019-11-20
- [Goldman Sachs Open Sources its Data Modeling Platform through FINOS](https://www.linuxfoundation.org/press/press-release/goldman-sachs-open-sources-its-data-modeling-platform-through-finos): Linux Foundation, 2020-10-19
- [Building the Open Source Program Office at Goldman Sachs](https://static.sched.com/hosted_files/ossjapan2022/01/2022-LinuxCon-GS-OSPO.pdf): LinuxCon Japan 2022 발표 자료
- [Goldman Sachs and MSCI Collaborate to Deliver Improved Risk Analytics](https://ir.msci.com/news-releases/news-release-details/goldman-sachs-and-msci-collaborate-deliver-improved-risk): MSCI Investor Relations
- [Gs Quant: Finance & Market Analysis for AI Agents](https://www.openagentskill.com/skills/goldmansachs-gs-quant): OpenAgentSkill, 2026-08-18 등록
- [HelloGitHub: goldmansachs/gs-quant](https://hellogithub.com/en/repository/goldmansachs/gs-quant): HelloGitHub. 조회일 2026-08-26
- [Goldman Sachs open source toolkit: GS Quant](https://dev.to/mahlonzy/goldman-sachs-open-source-toolkit-gs-quant-4mg5): Mahlon Clottey, DEV Community
- [Goldman Sachs GS-Quant: A Python Quant Toolkit Used on Wall Street](https://medium.com/coding-nexus/goldman-sachs-gs-quant-a-python-quant-toolkit-used-on-wall-street-764ef510a8d7): Coding Nexus, Medium
