---
title: "TradingAgents: Reading the Paper and Code Behind an LLM Trading Desk"
meta_title: ""
description: "A look at TradingAgents, a multi-agent trading framework that splits work across analysts, a bull/bear debate, a trader, and a risk team. We read the paper against the code and ask how far the backtest numbers can be trusted."
date: 2026-07-03T14:30:00+09:00
lastmod: 2026-07-03T15:10:00+09:00
image: ""
categories: ["AI"]
tags: ["multi-agent", "llm-agents", "trading", "langgraph", "fintech", "agent-debate"]
author: "whackur"
translationKey: "tradingagents-multi-agent-llm-trading"
draft: false
---

Up front: this is not investment advice, and nothing here recommends buying or selling anything. It is a read of how you organize LLM agents into a single decision, looked at from the research and the code. Trading is just the domain the design happens to target.

[TradingAgents](https://github.com/TauricResearch/TradingAgents) is interesting not because it is a money machine, but because it copies the org chart of an actual trading firm straight into agents. Analysts write reports, a bull and a bear argue, a trader makes the call, and a risk team picks that call apart again. All of it lives in code. The repo sits at roughly 90k GitHub stars and 17.4k forks, which makes it a good text for studying multi-agent design.

## What TradingAgents is

There are two artifacts. One is the paper, [arXiv:2412.20138](https://arxiv.org/abs/2412.20138). The other is the [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) repository.

The paper is titled "TradingAgents: Multi-Agents LLM Financial Trading Framework." The authors are Yijia Xiao, Edward Sun, Di Luo, and Wei Wang, from UCLA, MIT, and Tauric Research. It first appeared in December 2024 and has been revised through v7, classified under q-fin.TR (quantitative finance, trading). The arXiv comment notes an oral acceptance at the "Multi-Agent AI in the Real World" workshop.

The repo is Apache-2.0, default branch `main`, created in late December 2024. Its latest release is `v0.3.0` from June 2026. If the paper is the idea and the experiment, the repo is the working code that has kept refining that idea. As we will see, the v0.3.0 repo is much closer to a product than the paper demo was.

The paper frames two problems. First, existing financial LLM agents tend to be single-agent, or if multi-agent, they do not really reproduce how a firm divides labor and deliberates. Second, communication built on long natural-language message histories creates what the paper calls a "telephone effect": as messages pass through agents, meaning drifts, information is lost, and state gets corrupted.

## An org chart rebuilt from agents

The core idea is division of labor. Instead of one giant agent judging everything, function-specific agents each write a report, and those reports move to the next stage. Sharing structured reports as a kind of global state, rather than leaning on a long chat log, is the mechanism that keeps information from leaking away.

The flow runs like this:

| Stage | Members | Job |
|---|---|---|
| Analyst Team | market, social/sentiment, news, fundamentals analysts | Pull data and each write a specialist report |
| Researcher Team | Bull Researcher, Bear Researcher, Research Manager | Bull and bear debate, then the manager synthesizes |
| Trader | Trader | Turn analyst and researcher output into a decision signal |
| Risk Management Team | Aggressive, Neutral, Conservative, Portfolio Manager | Debate risk from three angles, then decide |

The paper uses ReAct prompting for this flow and treats reports and documents as global state so the system does not depend only on a long message history.

To keep the debates from spinning forever, the code hard-codes stopping conditions. In the repo's `ConditionalLogic`, the bull/bear debate runs for `2 * max_debate_rounds` before handing off to the Research Manager. The risk debate involves three views (aggressive, neutral, conservative), so it runs for `3 * max_risk_discuss_rounds` before the Portfolio Manager takes over. Debate depth is exposed as config, so you decide how many rounds to run.

## How the paper's org chart survives in the code

The paper's org chart maps almost one-to-one onto the repo's directories. The gap between "a concept in the paper" and "code that implements it" is small here, which is the project's real strength.

| Paper concept | Code location |
|---|---|
| Analyst team | `tradingagents/agents/analysts/` (factories like `create_market_analyst`) |
| Bull/bear debate | `tradingagents/agents/researchers/` plus `graph/` conditional logic |
| Trader | `tradingagents/agents/trader/` |
| Risk debate and managers | `tradingagents/agents/risk_mgmt/`, `tradingagents/agents/managers/` |
| Graph assembly | `GraphSetup.setup_graph()` in `tradingagents/graph/setup.py` |

Orchestration is built on a [LangGraph](https://langchain-ai.github.io/langgraph/) `StateGraph`. Analysts call tools in a set order and tidy up messages before handing off to the Bull Researcher; from there the path goes Research Manager to Trader, through the risk debate, and ends at the Portfolio Manager, all expressed as graph nodes and edges. When a run finishes, `tradingagents/reporting.py` saves the analyst, research, trader, risk, and portfolio-manager output as a markdown tree and a `complete_report.md`. You get an audit trail of what led to each decision.

Models come in two tiers. The `default_config.py` defaults are `gpt-5.5` for the deep-reasoning `deep_think_llm` and `gpt-5.4-mini` for the fast `quick_think_llm`: a strong model for the heavy judgment, a cheap one for the routine cleanup. Provider support is broad, covering OpenAI, Google Gemini, Anthropic Claude, xAI Grok, DeepSeek, Qwen (DashScope), GLM (Zhipu), MiniMax, OpenRouter, Ollama, Azure OpenAI, and AWS Bedrock. For data vendors, the defaults use `yfinance` for prices, technical indicators, fundamentals, and news, `fred` for macro indicators, and `polymarket` for prediction-market data.

## Memory and reproducibility

The reflection loop that was interesting in the paper is in the code too. A completed run appends its decision to `~/.tradingagents/memory/trading_memory.md`. On the next run for the same ticker, the system computes the realized return and alpha versus SPY, writes a short reflection, and feeds it into the later Portfolio Manager prompt. It is a lightweight learning loop that conditions future judgments on past outcomes without touching any weights.

Checkpoint resume is opt-in through the `--checkpoint` flag or config, and per-ticker SQLite databases live under `~/.tradingagents/cache/checkpoints/`.

Here comes a reproducibility warning worth reading twice. The README states plainly that LLM sampling, the behavior of reasoning models, and shifts in live news and social data mean the same ticker and date can produce different runs. So it says backtest results are not guaranteed to match any published figure, and it asks you to treat the framework as a research scaffold for multi-agent analysis, not a fixed-return strategy. The people who built it draw that line themselves, and that is worth remembering.

## What changed by v0.3.0

The changes that turned the repo from a paper demo into a maintained research tool cluster in v0.3.0.

The headline is a verified data-access contract. It covers symbol normalization, an explicit vendor chain, a typed `VendorError`, look-ahead-safe news windows, and rejection of stale OHLCV data. In particular, `interface.py` is designed to use only the specified vendor chain and to never silently fall back to a vendor you did not choose. It is a guard against receiving results without knowing where the data came from.

The rest of the changes:

- Expanded provider registry: NVIDIA, Kimi, Groq, Mistral, Bedrock, and an OpenAI-compatible endpoint.
- FRED macro indicators and Polymarket event probabilities added as data sources.
- `TradingAgentsGraph.save_reports()` for saving reports programmatically.
- Environment-configurable reasoning depth.
- A CI gate. It runs pytest across a Python 3.10 through 3.13 matrix and requires a clean-install smoke test and a strict `ruff check` to pass.

One release earlier, `v0.2.5` shipped a fix worth calling out. In the older flow, the Sentiment Analyst could fabricate social posts under prompt pressure. The fix has it read real Yahoo News, StockTwits, and Reddit data instead. It is a clean case of stopping an LLM agent from inventing plausible content by grounding it in actual data.

## Why the backtest numbers deserve skepticism

Start with the experiment. The backtest window runs from January 1 to March 29, 2024, against rule-based baselines like Buy and Hold, MACD, KDJ+RSI, ZMR, and SMA. The metrics are cumulative return (CR), annualized return (ARR), Sharpe Ratio (SR), and maximum drawdown (MDD). Table 1 of the paper compares three tickers.

| Ticker | Cumulative return | Annualized return | Sharpe Ratio | Max drawdown |
|---|---|---|---|---|
| AAPL | 26.62% | 30.5% | 8.21 | 0.91% |
| GOOGL | 24.36% | 27.58% | 6.39 | 1.69% |
| AMZN | 23.21% | 24.90% | 5.60 | 2.11% |

The paper reports that on its sampled stocks TradingAgents reached at least 23.21% cumulative and 24.90% annualized return, beating the best baseline by more than 6.1 percentage points. The numbers look strong. Before taking them at face value, several things need flagging.

The Sharpe Ratio is unusually high. An SR above 2 is typically considered very good and above 3 excellent. AAPL's 8.21 is far past that. The telling part is that the authors themselves note the value is higher than they would expect, attributing it to TradingAgents having almost no pullback during the window. Turn that around and it means the figure leans heavily on a favorable three-month stretch of the market.

The window and the ticker set are narrow. Three months, a handful of large-cap tech names. Why so short? In a footnote the paper explains that each prediction involves "11 LLM calls and 20+ tool calls," so the cost of LLM and tool usage made a longer backtest impractical. Cost constrained the experiment, and that same cost carries over to any real deployment.

The most important warning is contamination risk. The paper claims it used no future data, but an LLM may already have seen the news and price action of Q1 2024 during pretraining. Even if the backtest code fed in no future data, if the outcomes of that period already sit inside the model's weights, it may be replaying memory rather than truly predicting. This is the fundamental weakness of any LLM backtest, and it deserves a critical read alongside the README's reproducibility warning.

A backtest is not live trading. Slippage, transaction costs, live data variance, and regime shifts are all absent. These numbers are better read as the result of a design experiment ("a role-split agent org produced auditable decisions") than as evidence that the approach makes money.

## Community reaction

A Reddit post in r/AI_Agents framed TradingAgents as closer to a hedge fund made of agents than a simple trading wrapper. The visible discussion is small, though, and reads more like a project introduction than an independent review, so the more concrete signals still come from GitHub issues.

The GitHub issues show where people actually get stuck. The signals below come from public issues.

Extension draws a lot of interest. [#82](https://github.com/TauricResearch/TradingAgents/issues/82) asks about extending to crypto trading. Cutting the per-run cost is an active theme too. [#750](https://github.com/TauricResearch/TradingAgents/issues/750) reports that the prompt construction leaves the LLM API's prompt cache hit rate at essentially zero, and [#1032](https://github.com/TauricResearch/TradingAgents/issues/1032) is a PR that uses a local LLM response cache to reduce API cost. Given that a single prediction fans out to more than ten LLM calls, cost is a core community concern.

Configuration and provider wiring trip people up as well. [#227](https://github.com/TauricResearch/TradingAgents/issues/227) reports an OpenAI SDK error when using an OpenRouter key, [#148](https://github.com/TauricResearch/TradingAgents/issues/148) covers a Gemini usage problem, and [#174](https://github.com/TauricResearch/TradingAgents/issues/174) and [#158](https://github.com/TauricResearch/TradingAgents/issues/158) are questions about model selection and custom config.

The sharpest criticism is about data quality. [#214](https://github.com/TauricResearch/TradingAgents/issues/214) raises a strong complaint that the default data (PE, PB, and so on) is wrong, [#130](https://github.com/TauricResearch/TradingAgents/issues/130) reports incorrect China A-share prices, and [#162](https://github.com/TauricResearch/TradingAgents/issues/162) covers wrong data more broadly. The verified data-access contract in v0.3.0 reads as a direct response to exactly these signals. There are design-level proposals too. [#542](https://github.com/TauricResearch/TradingAgents/issues/542) suggests separating indicator calculation from LLM analysis, [#717](https://github.com/TauricResearch/TradingAgents/issues/717) proposes weighting the reflection loop by a surprise ratio so it does not overlearn from lucky wins, and [#1105](https://github.com/TauricResearch/TradingAgents/issues/1105) is a PR adding an evidence ledger, citations, and guardrails.

Two axes run through the community's attention: how to cut the cost, and how to make the data trustworthy. Both point at the gap between making a plausible decision and making a reliable one.

## Further reading

- [TradingAgents documentation](https://tauricresearch.github.io/TradingAgents/): the GitHub Pages docs that ship with the repo
- [Mixture of Agents (MoA)](/english/blog/mixture-of-agents-moa/): another multi-agent design that stacks several LLMs into layers
- [LangGraph docs](https://langchain-ai.github.io/langgraph/): the graph runtime TradingAgents uses for orchestration
- [arXiv q-fin.TR](https://arxiv.org/list/q-fin.TR/recent): recent papers in quantitative finance and trading

## Conclusion

TradingAgents is not a money machine. It is a clean research scaffold that implements a role-split agent structure, from analysts through debate, a trader, a risk debate, and a manager, in the financial domain. The paper's org chart survives almost intact in the code, which makes it good material for studying multi-agent design, and by v0.3.0 the data validation, CI, and provider wiring have hardened it into something well beyond a demo.

The backtest numbers, though, have to be read together with the short window, the narrow ticker set, the unusually high Sharpe Ratio, the heavy LLM and tool cost, and the contamination risk. Even the authors wrote that the results are not guaranteed to match any published figure. The real value of this project is not the returns. It is the agent design itself: debate, reflection, and structured communication producing decisions you can actually audit.

## References

- [arXiv:2412.20138: TradingAgents: Multi-Agents LLM Financial Trading Framework](https://arxiv.org/abs/2412.20138): Yijia Xiao, Edward Sun, Di Luo, Wei Wang, accessed 2026-07-03
- [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents): GitHub, Apache-2.0, accessed 2026-07-03
- [TradingAgents documentation](https://tauricresearch.github.io/TradingAgents/): Tauric Research, accessed 2026-07-03
- [TradingAgents v0.3.0 release](https://github.com/TauricResearch/TradingAgents/releases): GitHub Releases, accessed 2026-07-03
