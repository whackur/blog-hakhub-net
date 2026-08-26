---
title: "gs-quant: How Goldman Sachs Open-Sourced Its Quant Code, and Where the Line Is"
meta_title: "gs-quant Review: Goldman Sachs Open-Source Quant Library"
description: "What Goldman Sachs' Python quant toolkit gs-quant is, the history from the 2018 repo to the 2021 OSPO, the local-vs-Marquee-API boundary visible in the code structure, community reactions, and its limits, reviewed for research and education."
date: 2026-08-26T10:00:00+09:00
lastmod: 2026-08-26T10:00:00+09:00
image: ""
categories: ["Finance"]
tags: ["quant-finance", "open-source", "python", "goldman-sachs"]
author: "whackur"
translationKey: "gs-quant-goldman-sachs-open-source-quant-library"
draft: false
---

Tell someone that an investment bank's trading code is on GitHub and you usually get one of two reactions: "why would they do that" or "they kept the important parts, surely." [goldmansachs/gs-quant](https://github.com/goldmansachs/gs-quant) is a case where both reactions are half right. The repository was created in December 2018, passed 12,000 stars as of August 2026, and had a push on the very day I checked. The README also states plainly that you need to be an institutional client of Goldman Sachs to use the pricing and risk APIs.

This post is a code review for research and education, not a recommendation of gs-quant as an investment tool: what a large bank chose to publish, in what form, and where it drew the line, read through the code structure and the release history. I start with what a quant finance toolkit does, unpack unfamiliar names like Marquee, SecDB, and Slang one at a time, and follow the community's complaint that "everything useful is behind the API." All numbers and citations were checked on 2026-08-26 against the GitHub API, PyPI, the official docs, press coverage, and Hacker News threads.

## gs-quant is a Python interface to Goldman's engines

A quant finance toolkit does three broad jobs. It fetches and organizes market data, it computes prices and risk for financial instruments (including derivatives such as options and swaps), and it ties those computations together to test strategies or manage portfolios. The second job is the hard one. Derivative pricing models depend on constantly refreshed market parameters (rate curves, volatility surfaces, correlations), and banks have spent decades building the engines that do this.

gs-quant is a Python toolkit built and maintained by quantitative developers at Goldman Sachs. The README calls it a "Python toolkit for quantitative finance" created "on top of one of the world's most powerful risk transfer platforms" and "crafted over 25 years of experience navigating global markets," designed to speed up development of trading strategies and risk management. The phrase "on top of" defines the library's character. gs-quant is not the pricing engine itself; it is closer to a Python interface to Goldman's internal engines.

Those engines live behind **Marquee**, Goldman Sachs' digital platform for institutional clients. The PyPI homepage for gs-quant points to marquee.gs.com. The README says API access requires a client id and secret, available to institutional clients, and directs readers to their sales coverage or Marquee Sales. The [Marquee page for gs-quant](https://marquee.gs.com/welcome/our-platform/gs-quant) highlights coverage of an extensive range of FX derivatives.

Goldman's [OSPO presentation at LinuxCon Japan 2022](https://static.sched.com/hosted_files/ossjapan2022/01/2022-LinuxCon-GS-OSPO.pdf) describes these analytics tools as trusted daily by over a thousand quantitative developers at Goldman Sachs to manage its global trading business. The same claim appears under "Designed by our quants" in the Key Features section of the [official docs](https://developer.gs.com/docs/gsquant/). The primary users are Goldman's own quants and institutional clients. GitHub visitors come after.

## The release history

There is no single date on which gs-quant "went open source." The repository and the press record show this sequence:

- **2018-12-14**: GitHub repository created (first commit "Initial commit"). First PyPI release, 0.4.8, on 2018-12-23.
- **2019-04-03**: The Wall Street Journal publishes "Goldman's Trading Floor Is Going Open-Source, Kind of." In summary, Goldman planned to release on GitHub later that month some of the code its traders and engineers use to price securities and analyze and manage risk. A [Hacker News thread](https://news.ycombinator.com/item?id=19562224) appeared the same day. A WSJ [video segment](https://www.wsj.com/video/the-latest-on-goldman-sachs-open-source-trading-floor/4C614C58-03BC-4EB8-A65C-DE923E09FA90) framed it as developers gaining access to previously proprietary code used to assess risk and price derivatives.
- **2019-11-20**: CNBC reports that [Goldman is giving away software to Wall Street for free](https://www.cnbc.com/2019/11/20/goldman-sachs-is-giving-away-software-to-wall-street-for-free.html). That story is about the data modeling platform Legend (then called Alloy), not gs-quant.
- **2020-10-19**: The Linux Foundation announces that [Goldman has contributed Legend to FINOS](https://www.linuxfoundation.org/press/press-release/goldman-sachs-open-sources-its-data-modeling-platform-through-finos) as open source. FINOS (the Fintech Open Source Foundation) is the Linux Foundation body for open-source collaboration in financial services.
- **2021**: Goldman Sachs' Open Source Program Office (OSPO) is chartered in April and formally launched in August.

Since the repository already existed in December 2018, the WSJ story reads as a widening of scope rather than a first release. A specific "March 2020 release" date was likewise not supported by any press coverage I could find. This post treats only the timeline above as fact and does not assert a single launch date.

The pattern matters more than any one date. The 2019 expansion of gs-quant, the 2019 to 2020 Legend contribution, and the 2021 OSPO show Goldman turning open source from a one-off announcement into an organizational function. The bank still lists its public projects on the [developer.gs.com open source portal](https://developer.gs.com/discover/open-source).

## How it actually works, read from the code structure

The `gs_quant/` package, as returned by the GitHub contents API, looks like this:

```text
gs_quant/
  analytics/      api/          backtests/    config/
  content/        data/         datetime/     documentation/
  entities/       instrument/   interfaces/   markets/
  mcp/            models/       quote_reports/ risk/
  skills/         target/       session.py    priceable.py
```

Put this next to the official docs' table of contents and the structure becomes legible. The docs run Overview, Getting Started, Authentication (Sessions, GS Session, Proxy), Data (Data Environment, Accessing Data, Data Analytics, Data Visualization), Pricing and Risk (Instruments, Measures, Pricing Context, Portfolios, Scenarios), Markets (Assets and SecurityMaster, Relative Dates), Hedging (Hedging Using ML), Contribute, and SDK Reference. Authentication comes before Data and Pricing. That ordering is the usage order.

![Diagram splitting gs-quant into a local region (timeseries and analytics helpers, datetime and instrument definitions, backtest framework code) and a remote Marquee API region (Pricing and Risk, Data, Markets and SecurityMaster, Hedging) connected through GsSession](/images/posts/gs-quant-goldman-sachs-open-source-quant-library/local-vs-api-boundary.svg)

*The local and API regions of gs-quant. Reconstructed from the README and the official docs structure; per-module behavior should be confirmed in the repository code.*

The library splits into two layers.

**The layer that runs locally.** Statistical and analytics helpers in the timeseries family, datetime utilities such as business-day logic, and instrument definitions that represent financial products as typed Python objects all work with nothing more than a pip install. The backtests and models directories hold strategy framework code as well, though the step that actually values a strategy appears to call back into the API. Within what the README and the structure confirm, that is the purely local territory. One Hacker News user noticed that `timeseries/statistics.py` contains SIR/SEIR compartment model classes for modeling epidemic spread, and a comment guessed they were added around March 2020 during the COVID period. Epidemiology in a finance toolkit looks out of place, but it also demonstrates that the local layer really is just ordinary Python code.

**The layer that calls the API.** Derivative pricing, risk measures, scenario analysis, dataset queries, asset identification through SecurityMaster, and ML-based hedging are all computed by engines on the Marquee side. The Python objects build requests and receive results. The door into this layer is `GsSession` in `gs_quant/session.py`.

Installation needs Python 3.9 or later and pip.

```bash
pip install gs-quant
```

The session concept is best understood like this. Real credentials should never live in code; keep them in environment variables or a separate configuration file.

```python
from gs_quant.session import GsSession, Environment

# GsSession.use(...) opens a Marquee session.
# The client id and secret are issued to institutional clients.
# Inject them from the environment instead of writing them in code.
```

This is where API gating becomes the central fact about the project. The license is Apache-2.0, but the substance of what the library does (pricing, risk, data) sits outside the licensed code, on Goldman's servers. You are free to read, modify, and redistribute the code, but for it to produce meaningful output you need a contractual relationship. As an open-source client for a closed service, it belongs to the same family as cloud vendors that open-source their SDKs and charge for the service behind them.

The most recent notable addition to the package is `gs_quant/mcp/`. It contains client.py, config.py, dependencies.py, middleware.py, run.py, session_utils.py, and a tools/ directory: an MCP (Model Context Protocol) server integration. The repository root also has a `.claude/skills` directory for Claude Code, and on 2026-08-18 the project was listed on OpenAgentSkill as ["Gs Quant: Finance & Market Analysis for AI Agents"](https://www.openagentskill.com/skills/goldmansachs-gs-quant). A bank's quant toolkit is starting to take the shape of a tool that AI agents call. That path, of course, goes through the same Marquee account door.

## Community reaction

Reactions come from two moments: April 2019, when the wider release was announced, and June 2024, after the library had settled in. The main points from both threads, paraphrased:

The [2019-04-03 thread](https://news.ycombinator.com/item?id=19562224) (189 points, 96 comments) leaned skeptical. The representative favorable argument ran like this: if the pricing technology were more accurate than the market, Goldman could print money and would never publish it, so this is probably an implementation of standard, well-known pricing and risk models, but those still cost effort to build, so it is useful. On the other side were suspicions that it was mostly PR or marketing, a worry that if many investors used code Goldman knows intimately the market might move in Goldman's favor, and a joke that it might contain a "poison pill" like the magic numbers the NSA planted in cryptographic schemes. One commenter noted that at that point only a LICENSE file was on GitHub. Another recalled talking to a Goldman developer a few years earlier who could not even open the GitHub website at work, and read the announcement as a sign that one of the most closed companies was changing.

The densest discussion is the [2024-06-29 thread](https://news.ycombinator.com/item?id=40831991) (285 points, 60 comments). In five years the question moved from "are they really publishing it" to "what can you do with what was published."

The criticism centered, predictably, on API gating. Commenters said everything useful to an outsider sits behind Goldman's data API, leaving only design study as a realistic use, and that while the toolkit is free the data is very expensive. One described the README as closer to an advertisement of what Goldman does than to information useful to outsiders. On learning materials, someone complained that there were only a few video links and asked whether they were meant to copy code off a video.

Opinions split on the code itself. One view held that it amounts to a collection of basic financial data structure classes; others answered that most domain libraries are exactly that. This disagreement is really about how you view the local layer. Expect a pricing engine and you will be disappointed; view it as a well-organized domain model plus API client and the assessment changes.

The thread's mentions of **SecDB** and **Slang** are worth pausing on. One commenter explained that Slang remains central and drives SecDB, which they called the nervous system of the markets business. SecDB is widely described as Goldman's internal securities and risk database and computation system, with Slang as its in-house language. In that context gs-quant's position becomes clear. It does not replace or expose SecDB; it is the outer shell that receives that system's output in Python. Goldman published the shell. The nervous system stays inside.

Finally, one comment made the point that this is not the thing that makes you money. I think that is the first sentence anyone should internalize when encountering open-source quant code as an individual.

## Current state and maintenance

Repository status as checked on 2026-08-26:

| Item | Value |
| --- | --- |
| stars / forks / watchers | 12,491 / 1,669 / 164 |
| license | Apache-2.0 |
| default branch / language | master / Python |
| created | 2018-12-14 |
| last push | 2026-08-26 (the day of the check) |
| commits | about 569 |
| latest GitHub release | release-2.1.4 (2026-08-17) |
| PyPI | latest 2.1.4, first release 0.4.8 (2018-12-23), 533 versions total |

Recent releases came at intervals of days to weeks: release-2.1.1 (2026-07-15), 2.1.2 (2026-08-03), 2.1.3 (2026-08-07), 2.1.4 (2026-08-17). The oldest tagged release visible through the GitHub Releases API is release-0.8.131 (2020-05-18); since PyPI shows a first release in December 2018, the early versions evidently shipped to PyPI without GitHub Releases. The 533 cumulative PyPI versions suggest a cadence of frequent small releases tied to an internal cycle.

Maintenance appears to be led by Goldman Sachs. I could not verify how much external contribution is accepted, so I am not quoting a figure. The official docs do have a Contribute section.

There are ecosystem signals too. An [MSCI and Goldman Sachs collaboration announcement](https://ir.msci.com/news-releases/news-release-details/goldman-sachs-and-msci-collaborate-deliver-improved-risk) states that MSCI's risk factor models will be available via Goldman Sachs APIs and GS Quant, which means gs-quant serves as a distribution channel for third-party risk models as well as Goldman's own. On the curation side, [HelloGitHub](https://hellogithub.com/en/repository/goldmansachs/gs-quant) lists it as an Active, Apache-2.0 project.

## Alternatives and how they differ

When comparing gs-quant with other tools, the question that matters more than star counts or feature lists is **where the computation happens**.

- **QuantLib**: a fully local open-source pricing library written in C++ with Python bindings. Curve construction, option pricing, and bond analytics all run on your machine. You can modify the models and you need no account. In exchange, sourcing market data and maintaining model parameters is entirely your job.
- **OpenBB**: an open-source financial data platform mentioned as an alternative in the HN thread, focused on unifying many data sources behind one interface.
- **QuantConnect**: an algorithmic trading platform also mentioned in the thread, where the platform provides backtesting infrastructure and data.

gs-quant's distinguishing feature is exactly one thing: it calls a bank's production risk engine. Getting the same numbers Goldman's internal quants see, from the same models and the same market data, is something no other open-source tool offers. The price is API dependency. If QuantLib says "here is the engine, bring your own data," gs-quant says "here are the engine and the data, sign a contract." Which is better depends on your purpose, and this post does not attempt a detailed numerical comparison.

## Limits and risks

- **Core functionality depends on an account.** Pricing, risk, data, and market lookups need a Marquee client id and secret, issued to institutional clients. After pip install, an individual developer is limited to the local computation layer and reading code.
- **Scope of the open source.** Apache-2.0 covers only the code in the repository. The engines that produce the results are not part of the release. The sentence "Goldman open-sourced its quant code" is an exaggeration unless this scope is stated.
- **Maintenance structure.** It appears to be Goldman-led, and the scale of external contribution could not be verified. If the company's strategy changes, the project's direction can change with it.
- **Learning materials.** As HN pointed out, examples and tutorials for outside users are thin. The official docs have structure, but hands-on practice presumes API access.
- **Risk of misunderstanding.** The library does not make investment decisions for you. It fetches computed results; how you interpret them and what you do next is entirely your responsibility. This post is not investment advice.

## Who it fits, by use

**Worth reading for**: developers curious how financial domain models are expressed as Python types, anyone looking for a case study in how a large bank splits an open-source client from a closed service, and anyone who wants to see what an MCP integration looks like inside a finance toolkit. The code itself is the textbook.

**Worth trying for**: institutional users with a Marquee account. For them gs-quant does what it was built to do, as the Python interface to Goldman's engines.

**Adjust expectations if**: you are an individual or student hoping to price derivatives without an account. For that goal QuantLib is the right fit, and gs-quant is better kept nearby as a design reference.

## Further reading

- [Goldman Sachs open source portal](https://developer.gs.com/discover/open-source): Goldman's public projects beyond gs-quant
- [Building the Open Source Program Office at Goldman Sachs (PDF)](https://static.sched.com/hosted_files/ossjapan2022/01/2022-LinuxCon-GS-OSPO.pdf): LinuxCon Japan 2022 slides on the OSPO and gs-quant's internal role
- [Goldman Sachs Open Sources its Data Modeling Platform through FINOS](https://www.linuxfoundation.org/press/press-release/goldman-sachs-open-sources-its-data-modeling-platform-through-finos): the Legend contribution from the same period
- [Goldman Sachs open source toolkit: GS Quant](https://dev.to/mahlonzy/goldman-sachs-open-source-toolkit-gs-quant-4mg5): an outside introduction on DEV Community
- [Goldman Sachs GS-Quant: A Python Quant Toolkit Used on Wall Street](https://medium.com/coding-nexus/goldman-sachs-gs-quant-a-python-quant-toolkit-used-on-wall-street-764ef510a8d7): an outside review on Medium (Coding Nexus)

## Summary

gs-quant is a project where "Goldman published its quant code" and "Goldman kept the core" are both true. What was published: the domain model, timeseries helpers, and a well-built Python client for the Marquee engines. What was not: the computation engines represented by SecDB, and the data. The sequence from the 2018 repository, through the 2019 WSJ coverage and the 2020 Legend contribution, to the 2021 OSPO shows that this boundary was an organizational choice rather than an improvisation.

For an individual developer, the value of this repository is in reading rather than running. You can see how a bank represents financial instruments as objects, where it puts the client-server line, and, lately, how it layers on MCP and agent skills. Expect more than that and, as the HN comments warned, you will be disappointed.

## References

- [goldmansachs/gs-quant](https://github.com/goldmansachs/gs-quant): GitHub, Apache-2.0. Accessed 2026-08-26
- [gs-quant on PyPI](https://pypi.org/project/gs-quant/): PyPI release history. Accessed 2026-08-26
- [GS Quant official documentation](https://developer.gs.com/docs/gsquant/): developer.gs.com. Accessed 2026-08-26
- [GS Quant on Marquee](https://marquee.gs.com/welcome/our-platform/gs-quant): Goldman Sachs Marquee. Accessed 2026-08-26
- [Goldman's Trading Floor Is Going Open-Source, Kind of](https://www.wsj.com/articles/goldmans-trading-floor-is-going-open-source-kind-of-11554285602): The Wall Street Journal, 2019-04-03 (paywalled; summarized only)
- [The Latest on Goldman Sachs's Open-Source Trading Floor](https://www.wsj.com/video/the-latest-on-goldman-sachs-open-source-trading-floor/4C614C58-03BC-4EB8-A65C-DE923E09FA90): The Wall Street Journal video
- [Goldman Sachs will open-source some of its trading software](https://news.ycombinator.com/item?id=19562224): Hacker News, 2019-04-03, 189 points, 96 comments. Accessed 2026-08-26
- [GS Quant discussion thread](https://news.ycombinator.com/item?id=40831991): Hacker News, 2024-06-29, 285 points, 60 comments. Accessed 2026-08-26
- [Goldman Sachs is giving away software to Wall Street for free](https://www.cnbc.com/2019/11/20/goldman-sachs-is-giving-away-software-to-wall-street-for-free.html): CNBC, 2019-11-20
- [Goldman Sachs Open Sources its Data Modeling Platform through FINOS](https://www.linuxfoundation.org/press/press-release/goldman-sachs-open-sources-its-data-modeling-platform-through-finos): Linux Foundation, 2020-10-19
- [Building the Open Source Program Office at Goldman Sachs](https://static.sched.com/hosted_files/ossjapan2022/01/2022-LinuxCon-GS-OSPO.pdf): LinuxCon Japan 2022 slides
- [Goldman Sachs and MSCI Collaborate to Deliver Improved Risk Analytics](https://ir.msci.com/news-releases/news-release-details/goldman-sachs-and-msci-collaborate-deliver-improved-risk): MSCI Investor Relations
- [Gs Quant: Finance & Market Analysis for AI Agents](https://www.openagentskill.com/skills/goldmansachs-gs-quant): OpenAgentSkill, listed 2026-08-18
- [HelloGitHub: goldmansachs/gs-quant](https://hellogithub.com/en/repository/goldmansachs/gs-quant): HelloGitHub. Accessed 2026-08-26
- [Goldman Sachs open source toolkit: GS Quant](https://dev.to/mahlonzy/goldman-sachs-open-source-toolkit-gs-quant-4mg5): Mahlon Clottey, DEV Community
- [Goldman Sachs GS-Quant: A Python Quant Toolkit Used on Wall Street](https://medium.com/coding-nexus/goldman-sachs-gs-quant-a-python-quant-toolkit-used-on-wall-street-764ef510a8d7): Coding Nexus, Medium
