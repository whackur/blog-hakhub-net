---
title: "gs-quant: How Goldman Sachs Open-Sourced Its Quant Code, and Where the Line Is"
meta_title: "gs-quant Review: Goldman Sachs Open-Source Quant Library"
description: "What GS Quant runs locally, what needs authenticated Marquee services, and how code licensing differs from data entitlements, with source-checked Python examples."
date: 2026-08-26T10:00:00+09:00
lastmod: 2026-10-15T15:51:21Z
image: "/images/posts/gs-quant-goldman-sachs-open-source-quant-library/quant-local-marquee-editorial-20261016.webp"
categories: ["Finance"]
tags: ["quant-finance", "open-source", "python", "goldman-sachs"]
author: "whackur"
translationKey: "gs-quant-goldman-sachs-open-source-quant-library"
draft: false
---

GS Quant is a Python toolkit that **runs time-series calculations on data you supply and constructs financial instrument objects locally, while sending Marquee data queries, valuations, and risk calculations to authenticated services**. Its Apache-2.0 code license is separate from permission to use those services and their data. Installing the package does not install Goldman Sachs' valuation service, but it does provide analysis code you can run without an account. The distinction needs to be made function by function in the [public source](https://github.com/goldmansachs/gs-quant).

Calculating returns from prices in a CSV and valuing an option with Goldman Sachs' models have different requirements. The first needs your input and a Python environment. The second also needs remote models, market data, and permission to call the service. The requirements depend on the task:

| Task | Where it runs and what it needs |
| --- | --- |
| Calculate returns from prices you supply | Local Python and input data |
| Represent a swap's currency, maturity, and notional | Local object construction and explicit contract terms |
| Query Marquee through the default `Dataset` provider | Remote API, a session, and dataset entitlements |
| Call `price()` or calculate risk using the default instrument implementation | Remote valuation API, relevant entitlements, and market data |
| Use a particular exchange or currency holiday calendar | Check the holiday-data retrieval path as well |

These distinctions follow the [time-series functions](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/timeseries/econometrics.py), [data provider](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/data/dataset.py), [default instrument API provider](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/instrument/core.py), and [holiday-calendar implementation](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/datetime/gscalendar.py), rather than package names or directory listings. This is a research and education discussion of the software's scope; it does not cover investment decisions or trade execution.

## The installed package and remote service have separate versions

As checked on October 16, 2026 (KST), the latest GitHub release is [`release-2.2.1`](https://github.com/goldmansachs/gs-quant/releases/tag/release-2.2.1), published on October 13, 2026 at 10:41:56 UTC. The [latest PyPI package](https://pypi.org/project/gs-quant/2.2.1/) is also 2.2.1. Both the PyPI metadata and README require **Python 3.10 or later**.

```bash
python -m pip install "gs-quant==2.2.1"
```

Pinning a version makes the examples and client implementation easier to revisit. This number identifies the Python code you install. It does not fix the remote data's update time, the server's model version, or the capabilities your application is allowed to use. The code evidence below links to commit [`bbe7071`](https://github.com/goldmansachs/gs-quant/tree/bbe7071653ccfc0d431e11c3a31dbd511afc394f), which the release tag resolves to.

## Time-series calculations without an account

GS Quant's value is not limited to reading its design. `returns()` divides the supplied price series by a series shifted by one observation to calculate simple returns by default. When the input is already in memory, this calculation needs no Marquee session. The [implementation's formula](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/timeseries/econometrics.py#L273) is `current price / previous price - 1`.

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

For the synthetic prices 100, 102, and 101, the second observation has a return of 2% and the third approximately -0.9804%. The function returns decimal values, not percentages. The first observation has no previous price, so its missing value is dropped from the output. This example and the object-construction example below were executed with GS Quant 2.2.1 on Python 3.12 with network connections blocked. They neither retrieve live market data nor predict future returns.

The same distinction applies to instrument objects. This code describes the terms of a US dollar interest rate swap that pays a fixed rate. An interest rate swap exchanges fixed-rate and floating-rate cash flows in the same currency.

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

The inputs specify a five-year maturity, a 3% fixed rate, and a $1 million notional. Notional is the basis for calculating cash flows, not the present value. Constructing the object does not establish a complete payment schedule and market conventions or calculate a price. The official [Instruments guide](https://developer.gs.com/docs/gsquant/pricing-and-risk/instruments/) describes `resolve()` as a separate step that makes relative terms and default conventions concrete. That step also uses the service path in the default implementation. Local construction does not establish that `price()` or `calc()` runs locally.

Directory-level classifications are also unreliable. Although `GsCalendar` looks like a date utility, specifying an exchange or currency leads it to query coverage and holiday data from the `HOLIDAY` and `HOLIDAY_CURRENCY` datasets. The [code](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/datetime/gscalendar.py#L87) returns early when the query targets are empty. Calling the whole datetime module offline would hide this dependency.

## Authentication and data entitlements are separate

Marquee is Goldman Sachs' service platform, and GS Quant also acts as a client for its APIs. The [README](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/README.md) describes a route for institutional clients to obtain a client id and secret. The [authentication guide](https://developer.gs.com/docs/gsquant/authentication/gs-session/) explains application registration, OAuth, and application-linked scopes. Those instructions do not establish that every package feature is institutional-only or paid.

Passing application credentials to `GsSession.use()` initializes a session and makes it current. The [OAuth implementation](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/session.py#L1289) uses the `client_credentials` grant to obtain an access token, then places it in the Bearer header of subsequent requests. Scopes specify capabilities an application requests. Adding a scope string to your code does not grant a new server-side permission.

The remote example assumes you have already obtained appropriate application credentials. Inject their actual values from the environment rather than storing them in code.

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

`Dataset("WEATHER")` creates an object referring to a dataset. `get_data()` performs the query through the default provider, `GsDataApi`, and returns a pandas DataFrame. You can explicitly supply another provider, so not every use of `Dataset` is necessarily a Marquee call. The default provider selection and query dispatch are visible in the [Dataset source](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/data/dataset.py).

The official [Datasets guide](https://developer.gs.com/docs/gsquant/data/data-environment/datasets/) says `WEATHER` is available to all applications without an explicit access request. The [query tutorial](https://developer.gs.com/docs/gsquant/data/accessing-data/querying-data/) also assumes an initialized session and a data subscription. A default entitlement to public example data does not mean anonymous HTTP access. For other datasets, check availability and entitlements in the catalog. This example was checked against the documentation and call signatures; an authenticated response was not tested.

The [Apache-2.0 license](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/LICENSE) governs use, modification, and distribution of the public code. It does not set service fees or grant retrieval and redistribution rights for a particular dataset. Neither “the package is free, so all data can be used freely” nor “every API is paid” follows from these sources.

## Valuation turns instrument terms into a remote request

Valuing the swap requires more than its stated fixed rate and notional: it also needs a valuation date, market information such as interest rate curves, and a model. GS Quant's default instrument implementation uses [`GsRiskApi`](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/instrument/core.py) as its provider. [`price()`](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/priceable.py#L75) delegates to `calc()` with a price measure, and the [risk API implementation](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/api/gs/risk.py#L63) sends a session request to `/risk/calculate` or `/risk/calculate/bulk`.

The Python source exposes instrument representation, request construction, and result handling. Installing the package does not let you execute the server-side valuation models used by this path locally. Nor does the call path establish that the server's internal implementation is identical to a particular proprietary in-house system.

In an environment with authentication and entitlement to value the instrument, the earlier `swap` can be evaluated as follows. The returned present value depends on account entitlements, market data, and valuation conditions.

```python
from datetime import date
from gs_quant.markets import PricingContext

with PricingContext(pricing_date=date(2026, 1, 5)):
    value_future = swap.price()

value = value_future.result()
```

[`PricingContext`](https://developer.gs.com/docs/gsquant/pricing-and-risk/pricing-context/) manages shared conditions such as valuation date, market-data date and location, and asynchronous or batch processing. Calculations made inside the context are grouped for dispatch when the block exits; read the futures' results outside the block. `is_async` controls how the caller waits. Creating a local object or enabling asynchronous behavior does not turn the remote calculation into an offline one.

To reproduce a result, record more than the package version: preserve the instrument terms, valuation date, market-data date and location, the data used, and the scope of your entitlements. A GitHub commit pins the client implementation; it is not evidence that the server model and data are fixed too.

## MCP integration uses the existing sessions

The 2.2.1 source includes an [experimental MCP integration](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/mcp/README.md). MCP, the Model Context Protocol, gives AI clients an interface for calling tools. This implementation supplies a FastMCP-based server and client. It needs the separate `mcp` optional dependencies, and its README warns that the API, CLI, and configuration may change.

The authentication mode determines whose account makes requests. `local` reuses one server-created session for tool calls. `passthrough` constructs the caller's session from authentication material passed in the request. The [middleware implementation](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/mcp/middleware.py) shows this distinction. Connecting an AI client does not create a new data subscription or valuation entitlement. Nor does `local` describe where calculations run: tools using that session can still call Marquee APIs.

## API dependency and choosing a use case

In the June 29, 2024 [Hacker News discussion](https://news.ycombinator.com/item?id=40831991), `kingkongjaffa` criticized useful functionality being behind GS-specific APIs. In the same conversation, `ironSkillet` described the value of studying the abstractions, user interfaces, and how researchers interact with the tool. These are dated user assessments, not evidence of current prices or access policies.

The criticism is particularly relevant if you expect a complete offline derivatives valuation tool. It does not establish that locally executable code, such as the returns example, has no use. Users with Marquee access instead get an implementation that connects data retrieval and instrument or risk requests to Python workflows. Access alone still does not establish entitlement to every instrument or dataset.

For **learning to execute and modify models yourself**, [QuantLib](https://www.quantlib.org/) is also worth examining. It is an open-source C++ library for financial modeling and risk management with Python bindings. The comparison here concerns whether the calculation implementation is available locally, rather than numerical accuracy or profitability. You still need to supply market data and valuation assumptions.

The first thing to check when choosing GS Quant is the input and call path of the functions you need. Start with local functions if you want to analyze data you already have. If you need Marquee results, establish the session and service or dataset entitlements first.

## Further reading

- [GS Quant time-series source](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/timeseries/econometrics.py): useful for following the calculations performed on an input series.
- [Official Pricing Context guide](https://developer.gs.com/docs/gsquant/pricing-and-risk/pricing-context/): explains valuation dates, market data, futures, and grouped requests.
- [QuantLib official site](https://www.quantlib.org/): a reference for comparing libraries that expose model implementations directly.

## References

All sources were checked on October 16, 2026 (KST). Unless otherwise stated, code links point to commit `bbe7071653ccfc0d431e11c3a31dbd511afc394f` from the 2.2.1 tag.

- [GS Quant README](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/README.md), [LICENSE](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/LICENSE): project scope, requirements, and code license.
- [GitHub release-2.2.1](https://github.com/goldmansachs/gs-quant/releases/tag/release-2.2.1), [PyPI 2.2.1](https://pypi.org/project/gs-quant/2.2.1/): the current release and installable package baseline.
- [Session implementation](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/session.py), [GsSession guide](https://developer.gs.com/docs/gsquant/authentication/gs-session/): OAuth, scopes, and current sessions.
- [Dataset implementation](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/data/dataset.py), [Datasets guide](https://developer.gs.com/docs/gsquant/data/data-environment/datasets/), [query example](https://developer.gs.com/docs/gsquant/data/accessing-data/querying-data/): providers, WEATHER, and data access conditions.
- [Instruments guide](https://developer.gs.com/docs/gsquant/pricing-and-risk/instruments/), [risk API source](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/api/gs/risk.py), [holiday-calendar source](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/datetime/gscalendar.py): the boundary between object definition and remote calls.
- [GS Quant MCP README](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/mcp/README.md), [authentication middleware](https://github.com/goldmansachs/gs-quant/blob/bbe7071653ccfc0d431e11c3a31dbd511afc394f/gs_quant/mcp/middleware.py): experimental status and session reuse.
- [Hacker News discussion](https://news.ycombinator.com/item?id=40831991): June 29, 2024 opinions on API dependency and learning from the design.
