---
title: "gs-quant: 골드만삭스가 퀀트 코드를 오픈소스로 공개한 방식과 그 경계"
meta_title: "gs-quant 골드만삭스 오픈소스 퀀트 라이브러리 리뷰"
description: "GS Quant에서 계정 없이 실행하는 시계열 계산과 상품 정의, 인증·데이터 권한이 필요한 Marquee 조회와 가격 평가를 실제 코드와 예제로 구분합니다."
date: 2026-08-26T10:00:00+09:00
lastmod: 2026-10-15T15:51:21Z
image: "/images/posts/gs-quant-goldman-sachs-open-source-quant-library/quant-local-marquee-editorial-20261016.webp"
categories: ["Finance"]
tags: ["quant-finance", "open-source", "python", "goldman-sachs"]
author: "whackur"
translationKey: "gs-quant-goldman-sachs-open-source-quant-library"
draft: false
---

GS Quant는 **내가 준비한 데이터의 시계열 계산과 금융 상품 객체 정의는 로컬에서 실행하고, Marquee의 데이터 조회·가격 평가·리스크 계산은 인증된 서비스로 요청하는 Python 툴킷**입니다. 공개 코드의 Apache-2.0 라이선스와 원격 서비스·데이터를 사용할 권한은 별개입니다. 설치했다고 골드만삭스의 가격 평가 서비스를 함께 받은 것은 아니지만, 계정 없이 실행할 수 있는 분석 코드도 있습니다. [공개 소스](https://github.com/goldmansachs/gs-quant)에서 이 두 영역을 함수별로 구분해야 합니다.

예를 들어 CSV에서 읽은 가격의 수익률을 구하는 일과, 옵션의 현재 가치를 골드만삭스 모델로 평가하는 일은 요구 조건이 다릅니다. 전자는 입력값과 Python 환경으로 충분합니다. 후자는 상품 조건뿐 아니라 원격 모델과 시장 데이터, 그 서비스를 호출할 권한까지 필요합니다. 용도에 따라 필요한 것을 나누면 다음과 같습니다.

| 하려는 일 | 실행 위치와 필요한 것 |
| --- | --- |
| 직접 준비한 가격 시계열로 수익률 계산 | 로컬 Python, 입력 데이터 |
| 스왑의 통화·만기·명목금액을 객체로 표현 | 로컬 객체 생성, 명시한 계약 조건 |
| 기본 `Dataset` 공급자로 Marquee 데이터 조회 | 원격 API, 세션, 데이터셋별 접근 권한 |
| 기본 상품 구현의 `price()`·리스크 계산 | 원격 가격 평가 API, 관련 권한과 시장 데이터 |
| 특정 거래소·통화의 휴일 달력 사용 | 휴일 데이터 조회 경로까지 확인 필요 |

이 구분은 패키지 이름이나 폴더 목록이 아니라 아래의 [시계열 함수](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/timeseries/econometrics.py), [데이터 공급자](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/data/dataset.py), [상품의 기본 API 공급자](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/instrument/core.py), [휴일 달력 구현](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/datetime/gscalendar.py)에 근거합니다. 연구·교육용 사용 범위를 설명하며 투자 판단이나 거래 실행을 다루지는 않습니다.

## 설치한 패키지와 원격 서비스의 버전은 다릅니다

2026년 10월 16일 한국시간 확인 기준 최신 GitHub 릴리스는 [`release-2.2.1`](https://github.com/goldmansachs/gs-quant/releases/tag/release-2.2.1)입니다. 공개 시각은 2026년 10월 13일 10:41:56 UTC이며, [PyPI의 최신 패키지](https://pypi.org/project/gs-quant/2.2.1/)도 2.2.1입니다. PyPI 메타데이터와 README는 **Python 3.10 이상**을 요구합니다.

```bash
python -m pip install "gs-quant==2.2.1"
```

버전을 고정하면 예제와 클라이언트 구현을 다시 확인하기 쉽습니다. 다만 이 번호는 설치한 Python 코드의 버전입니다. 원격 데이터의 갱신 시점이나 서버 모델의 버전, 내 애플리케이션에 허용된 기능까지 고정하지는 않습니다. 아래 코드 근거는 이 릴리스 태그의 커밋 [`bbe7071`](https://github.com/goldmansachs/gs-quant/tree/bbe7071653ccfc0d431e11c3a31dbd511afc394f)에 연결했습니다.

## 계정 없이 실행하는 시계열 계산

GS Quant의 가치를 코드 독해에만 한정할 필요는 없습니다. `returns()`는 전달받은 가격 시계열을 한 관측치씩 이동한 시계열로 나누어 기본 단순수익률을 구합니다. 입력이 이미 메모리에 있다면 이 계산에 Marquee 세션은 필요하지 않습니다. [구현의 계산식](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/timeseries/econometrics.py#L273)은 `현재 가격 / 이전 가격 - 1`입니다.

```python
import pandas as pd
from gs_quant.timeseries import returns

prices = pd.Series(
    [100.0, 102.0, 101.0],
    index=pd.date_range("2026-01-05", periods=3),
)
print(returns(prices).dropna().round(6).tolist())
# [0.02, -0.009804]
```

가상의 가격 100, 102, 101에서 두 번째 관측치의 수익률은 2%, 세 번째는 약 -0.9804%입니다. 반환값은 퍼센트 표기가 아닌 소수입니다. 첫 관측치에는 이전 가격이 없어 결측값이 생기므로 출력에서 제거했습니다. 이 예제와 다음 객체 생성 예제는 GS Quant 2.2.1, Python 3.12 환경에서 네트워크 연결을 차단한 상태로 실행했습니다. 실제 시장 데이터를 가져오거나 미래 수익을 예측한 결과가 아닙니다.

상품 객체도 같은 방식으로 구분할 수 있습니다. 다음 코드는 고정금리를 지급하는 달러 금리 스왑의 조건을 담습니다. 금리 스왑은 같은 통화에서 고정금리와 변동금리에 따른 현금흐름을 교환하는 상품입니다.

```python
from gs_quant.instrument import IRSwap

swap = IRSwap(
    "Pay", "5y", "USD",
    fixed_rate=0.03,
    notional_amount=1_000_000,
)
print(swap.termination_date, swap.notional_amount)
# 5y 1000000
```

여기에는 만기 5년, 고정금리 3%, 명목금액 100만 달러라는 입력이 들어 있을 뿐입니다. 명목금액은 현금흐름 계산의 기준이며 현재 가치가 아닙니다. 객체를 만들었다고 지급 일정과 시장 관행이 모두 확정되거나 가격이 계산되지는 않습니다. 공식 [Instruments 문서](https://developer.gs.com/docs/gsquant/pricing-and-risk/instruments/)가 설명하는 `resolve()`는 상대적인 조건과 기본 관행을 구체화하는 별도 단계입니다. 기본 구현에서는 이 단계도 서비스 경로를 사용합니다. `price()`나 `calc()`까지 로컬이라고 확대해서 해석하면 안 됩니다.

폴더 단위의 구분도 주의해야 합니다. 날짜 유틸리티처럼 보이는 `GsCalendar`는 거래소나 통화를 지정하면 `HOLIDAY`·`HOLIDAY_CURRENCY` 데이터셋의 커버리지와 휴일 데이터를 조회합니다. [해당 코드](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/datetime/gscalendar.py#L87)는 조회 대상이 비어 있을 때만 일찍 반환합니다. “datetime 모듈은 전부 오프라인”이라는 설명으로는 실제 의존성을 놓칩니다.

## 인증 성공과 데이터 이용 권한은 별개입니다

Marquee는 골드만삭스의 서비스 플랫폼이며 GS Quant는 그 API를 호출하는 클라이언트 역할도 합니다. [README](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/README.md)는 기관 고객이 client id와 secret을 발급받는 경로를 안내합니다. [인증 문서](https://developer.gs.com/docs/gsquant/authentication/gs-session/)에서는 애플리케이션 등록과 OAuth 인증, 애플리케이션에 연결된 scope를 설명합니다. 이 안내를 패키지의 모든 기능이 기관 전용이거나 유료라는 주장으로 넓힐 수는 없습니다.

`GsSession.use()`에 애플리케이션 자격 증명을 전달하면 세션을 초기화하고 현재 세션으로 설정합니다. [OAuth 구현](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/session.py#L1289)은 `client_credentials` 방식으로 액세스 토큰을 받아 이후 요청의 Bearer 헤더에 넣습니다. scope는 애플리케이션이 요청하는 기능 범위입니다. 코드에 scope 문자열을 추가한다고 서버가 새 권한을 부여하지는 않습니다.

원격 예제는 이미 적절한 애플리케이션 자격 증명을 발급받았다는 조건에서 읽어야 합니다. 실제 값은 환경에서 주입하고 코드에 저장하지 않습니다.

```python
import os
from datetime import date
from gs_quant.session import GsSession
from gs_quant.data import Dataset

GsSession.use(
    client_id=os.environ["MARQUEE_CLIENT_ID"],
    client_secret=os.environ["MARQUEE_CLIENT_SECRET"],
)
weather = Dataset("WEATHER")
frame = weather.get_data(
    date(2016, 1, 1), date(2016, 1, 31), city=["Boston"]
)
```

`Dataset("WEATHER")`는 데이터셋을 가리키는 객체를 만듭니다. `get_data()`가 기본 공급자인 `GsDataApi`로 조회하고 결과를 pandas DataFrame으로 돌려주는 단계입니다. 직접 다른 공급자를 지정할 수도 있으므로 모든 `Dataset` 사용을 Marquee 호출이라고 단정해서는 안 됩니다. 기본 공급자 선택과 쿼리 호출은 [Dataset 소스](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/data/dataset.py)에서 확인할 수 있습니다.

공식 [Datasets 안내](https://developer.gs.com/docs/gsquant/data/data-environment/datasets/)는 `WEATHER`가 모든 애플리케이션에 제공되며 별도 요청이 필요 없다고 설명합니다. 동시에 [조회 튜토리얼](https://developer.gs.com/docs/gsquant/data/accessing-data/querying-data/)은 초기화된 세션과 데이터 구독을 전제합니다. 공개 예제 데이터의 기본 접근 권한과 익명 HTTP 접근은 같은 뜻이 아닙니다. 다른 데이터셋은 카탈로그에서 이용 가능 여부와 권한을 확인해야 합니다. 이 예제는 문서·호출 형식을 확인한 코드이며 인증된 실제 응답을 검증한 것은 아닙니다.

[Apache-2.0 라이선스](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/LICENSE)는 공개 코드의 사용·수정·배포 조건을 정합니다. 특정 데이터의 조회·재배포 권한이나 서비스 요금을 대신 정하지 않습니다. “무료 패키지이므로 데이터도 자유롭게 쓴다”와 “모든 API는 유료다”는 모두 이 자료만으로 성립하지 않습니다.

## 가격 평가는 상품 조건을 원격 계산 요청으로 바꿉니다

스왑의 가치를 구하려면 입력한 고정금리와 명목금액 외에도 평가일, 금리 곡선 등 평가에 필요한 시장 정보와 모델이 있어야 합니다. GS Quant의 기본 상품 구현은 [`GsRiskApi`](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/instrument/core.py)를 공급자로 사용합니다. [`price()`](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/priceable.py#L75)는 가격 측정치를 지정한 `calc()`로 이어지고, [리스크 API 구현](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/api/gs/risk.py#L63)은 세션으로 `/risk/calculate` 또는 `/risk/calculate/bulk`에 요청합니다.

따라서 Python 소스에서 볼 수 있는 것은 상품 표현, 요청 구성, 결과 처리입니다. 이 경로에서 호출하는 서버 측 가격 평가 모델을 패키지 설치만으로 로컬에서 실행할 수는 없습니다. 서버의 내부 구현을 특정 사내 시스템과 동일하다고 추정할 이유도 없습니다.

인증과 해당 상품의 평가 권한이 있는 환경에서는 앞에서 만든 `swap`을 다음처럼 평가할 수 있습니다. 반환되는 현재 가치는 계정의 접근 권한, 시장 데이터와 평가 조건에 따라 달라집니다.

```python
from datetime import date
from gs_quant.markets import PricingContext

with PricingContext(pricing_date=date(2026, 1, 5)):
    value_future = swap.price()

value = value_future.result()
```

[`PricingContext`](https://developer.gs.com/docs/gsquant/pricing-and-risk/pricing-context/)는 평가일, 시장 데이터 기준일과 위치, 비동기·배치 처리 같은 공통 조건을 관리합니다. context 안의 계산은 블록을 나갈 때 묶어 전송하며, 안에서 받은 future의 결과는 블록 밖에서 읽습니다. `is_async`는 호출 측의 대기 방식을 조절하는 설정입니다. 로컬 객체를 만들거나 비동기 옵션을 켜는 일이 원격 계산을 오프라인 계산으로 바꾸지는 않습니다.

동일한 결과를 다시 얻어야 한다면 패키지 버전 외에 상품 조건과 평가일, 시장 데이터 기준일·위치, 사용한 데이터와 권한 범위도 기록해야 합니다. GitHub 커밋은 클라이언트 구현을 고정하는 근거이지 서버 모델과 데이터까지 고정됐다는 증거는 아닙니다.

## MCP 통합도 기존 세션을 사용합니다

2.2.1 소스에는 [실험 단계의 MCP 통합](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/mcp/README.md)이 있습니다. MCP(Model Context Protocol)는 AI 클라이언트가 도구를 호출하는 인터페이스이며, 이 구현은 FastMCP 기반 서버와 클라이언트를 제공합니다. 별도의 `mcp` 선택 의존성이 필요하고 README는 API·CLI·설정이 바뀔 수 있다고 명시합니다.

인증 방식에 따라 어떤 계정으로 요청하는지도 달라집니다. `local`은 서버가 만든 한 세션을 도구 호출에 재사용합니다. `passthrough`는 요청에 전달된 인증 정보로 호출자의 세션을 구성합니다. [미들웨어 구현](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/mcp/middleware.py)에서도 이 차이가 드러납니다. AI 클라이언트를 연결해도 데이터 구독이나 가격 평가 권한이 새로 생기지 않습니다. `local`은 계산 위치를 뜻하는 이름도 아닙니다. 해당 세션을 사용하는 도구는 여전히 Marquee API를 호출할 수 있습니다.

## API 의존성에 대한 비판과 용도 선택

2024년 6월 29일 [Hacker News 토론](https://news.ycombinator.com/item?id=40831991)에서 `kingkongjaffa`는 유용한 기능이 GS 전용 API 뒤에 있다는 점을 비판했습니다. 같은 대화에서 `ironSkillet`은 추상화와 사용자 인터페이스, 연구자가 도구를 사용하는 방식을 코드로 공부할 가치가 있다고 설명했습니다. 둘 다 당시 사용자의 평가이며 현재 가격표나 접근 정책의 근거는 아닙니다.

이 비판은 완성된 오프라인 파생상품 평가 도구를 기대할 때 특히 타당합니다. 다만 위의 수익률 계산처럼 로컬에서 실행하는 코드까지 쓸모없다는 결론으로 이어지지는 않습니다. 반대로 Marquee 접근 권한이 있는 사용자는 데이터 조회와 상품·리스크 요청을 Python 작업 흐름에 연결하는 구현을 얻습니다. 접근 권한이 있어도 원하는 상품과 데이터셋이 허용됐는지는 별도로 확인해야 합니다.

목적이 **모델을 직접 실행하고 수정하는 학습**이라면 [QuantLib](https://www.quantlib.org/)도 함께 살펴볼 만합니다. C++ 기반의 오픈소스 금융 모델링·리스크 라이브러리이며 Python 바인딩을 제공합니다. 여기서의 비교 기준은 수치 정확도나 수익성이 아니라 필요한 계산 구현을 로컬에서 확보하는가입니다. 시장 데이터와 평가 가정을 준비하는 문제는 여전히 남습니다.

GS Quant를 선택할 때 가장 먼저 확인할 것은 필요한 함수의 입력과 호출 경로입니다. 이미 가진 데이터를 분석할 목적이면 로컬 함수부터 실행하고, Marquee 결과가 목적이면 세션과 서비스·데이터별 권한부터 확인하는 편이 맞습니다.

## 함께 보면 좋을 자료

- [GS Quant 시계열 함수 소스](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/timeseries/econometrics.py): 입력 시계열에서 어떤 계산이 수행되는지 확인하기 좋습니다.
- [Pricing Context 공식 안내](https://developer.gs.com/docs/gsquant/pricing-and-risk/pricing-context/): 평가일·시장 데이터·future와 요청 묶음 처리의 관계를 설명합니다.
- [QuantLib 공식 사이트](https://www.quantlib.org/): 모델 구현을 직접 다루는 금융 라이브러리를 비교할 때 참고할 자료입니다.

## 참고 자료

확인일은 모두 2026년 10월 16일(한국시간)입니다. 코드 링크는 별도 표시가 없으면 2.2.1 태그의 커밋 `bbe7071653ccfc0d431e11c3a31dbd511afc394f`를 가리킵니다.

- [GS Quant README](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/README.md), [LICENSE](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/LICENSE): 프로젝트 범위, 요구 환경, 코드 라이선스.
- [GitHub release-2.2.1](https://github.com/goldmansachs/gs-quant/releases/tag/release-2.2.1), [PyPI 2.2.1](https://pypi.org/project/gs-quant/2.2.1/): 릴리스와 설치 패키지의 현재 기준.
- [Session 구현](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/session.py), [GsSession 안내](https://developer.gs.com/docs/gsquant/authentication/gs-session/): OAuth, scope, 현재 세션.
- [Dataset 구현](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/data/dataset.py), [Datasets 안내](https://developer.gs.com/docs/gsquant/data/data-environment/datasets/), [조회 예제](https://developer.gs.com/docs/gsquant/data/accessing-data/querying-data/): 공급자, WEATHER, 데이터 접근 조건.
- [Instruments 안내](https://developer.gs.com/docs/gsquant/pricing-and-risk/instruments/), [리스크 API 소스](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/api/gs/risk.py), [휴일 달력 소스](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/datetime/gscalendar.py): 객체 정의와 원격 호출의 경계.
- [GS Quant MCP README](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/mcp/README.md), [인증 미들웨어](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/mcp/middleware.py): 실험 상태와 세션 재사용 방식.
- [Hacker News 토론](https://news.ycombinator.com/item?id=40831991): 2024년 6월 29일의 API 의존성과 설계 학습에 관한 의견.
