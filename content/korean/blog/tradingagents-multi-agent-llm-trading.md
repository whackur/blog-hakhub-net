---
title: "TradingAgents: LLM 에이전트로 만든 트레이딩 회사, 논문과 코드 읽기"
meta_title: ""
description: "애널리스트, 리서처 토론, 트레이더, 리스크 팀으로 역할을 나눈 멀티 에이전트 트레이딩 프레임워크 TradingAgents를 논문과 코드로 뜯어봤습니다. 백테스트 수치를 어디까지 믿을 수 있는지도 함께 짚습니다."
date: 2026-07-03T14:30:00+09:00
lastmod: 2026-07-03T15:10:00+09:00
image: ""
categories: ["AI"]
tags: ["multi-agent", "llm-agents", "trading", "langgraph", "fintech", "agent-debate"]
author: "whackur"
translationKey: "tradingagents-multi-agent-llm-trading"
draft: false
---

먼저 밝혀둡니다. 이 글은 투자 조언이 아니고, 매수나 매도를 권하지도 않습니다. LLM 에이전트를 어떻게 조직해 하나의 의사결정을 만들어내는지, 그 설계를 연구와 코드 관점에서 읽는 글입니다. 트레이딩은 그 설계가 적용된 도메인일 뿐입니다.

[TradingAgents](https://github.com/TauricResearch/TradingAgents)가 흥미로운 이유는 "LLM으로 돈 버는 봇"이라서가 아닙니다. 실제 트레이딩 회사의 조직도를 그대로 에이전트로 옮겨놨기 때문입니다. 애널리스트가 리포트를 쓰고, 강세론자와 약세론자가 토론하고, 트레이더가 결정을 내리고, 리스크 팀이 다시 그 결정을 뜯어보는 흐름이 코드로 구현돼 있습니다. GitHub 스타는 약 9만 개, 포크는 약 1.7만 개로, 멀티 에이전트 설계를 공부하려는 사람에게는 좋은 교재입니다.

## TradingAgents가 무엇인가

두 개의 산출물이 있습니다. 하나는 논문 [arXiv:2412.20138](https://arxiv.org/abs/2412.20138)이고, 다른 하나는 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 저장소입니다.

논문 제목은 "TradingAgents: Multi-Agents LLM Financial Trading Framework"입니다. 저자는 Yijia Xiao, Edward Sun, Di Luo, Wei Wang이고 소속은 UCLA, MIT, Tauric Research입니다. 2024년 12월 처음 공개돼 현재 v7까지 개정됐고, 분류는 q-fin.TR(계량 금융 트레이딩)입니다. arXiv 코멘트에는 "Multi-Agent AI in the Real World" 워크숍 구두 발표로 채택됐다고 적혀 있습니다.

저장소는 Apache-2.0 라이선스이고 기본 브랜치는 `main`입니다. 2024년 12월 말에 만들어졌고, 최신 릴리스는 2026년 6월의 `v0.3.0`입니다. 논문이 아이디어와 실험이라면, 저장소는 그 아이디어를 계속 다듬어온 실행 코드입니다. 뒤에서 보겠지만 v0.3.0 시점의 저장소는 논문 데모보다 훨씬 제품에 가까워졌습니다.

논문이 지적하는 문제의식은 두 가지입니다. 첫째, 기존 금융 LLM 에이전트는 단일 에이전트이거나, 멀티 에이전트라도 실제 회사의 협업 구조를 충분히 모사하지 못한다는 점입니다. 둘째, 긴 자연어 대화 기록에만 기대는 소통 방식이 "telephone effect"를 일으켜 정보가 왜곡되고 상태가 손상된다는 점입니다. 전화 게임처럼 메시지가 여러 에이전트를 거치며 원래 뜻이 흐려지는 문제입니다.

## 트레이딩 회사를 본뜬 조직 구조

핵심 아이디어는 역할 분담입니다. 하나의 거대한 에이전트가 모든 걸 판단하는 대신, 기능별로 나눈 에이전트가 각자 리포트를 쓰고 그 리포트가 다음 단계로 넘어갑니다. 긴 대화 기록 대신 구조화된 리포트를 공유 상태처럼 쓰는 것이 정보 손실을 줄이는 장치입니다.

전체 흐름은 이렇게 이어집니다.

| 단계 | 구성원 | 하는 일 |
|---|---|---|
| Analyst Team | market, social/sentiment, news, fundamentals 애널리스트 | 데이터를 끌어와 각자 전문 영역 리포트 작성 |
| Researcher Team | Bull Researcher, Bear Researcher, Research Manager | 강세와 약세가 토론하고 리서치 매니저가 정리 |
| Trader | Trader | 애널리스트와 리서처 결과로 결정 신호 생성 |
| Risk Management Team | Aggressive, Neutral, Conservative, Portfolio Manager | 세 관점에서 리스크를 토론하고 최종 판단 |

논문은 이 흐름에 ReAct 프롬프팅을 쓰고, 리포트와 문서를 전역 상태처럼 활용해 긴 메시지 기록에만 의존하지 않도록 했다고 설명합니다.

토론이 무한정 돌지 않도록 코드에는 종료 조건이 박혀 있습니다. 저장소의 `ConditionalLogic`을 보면, 강세와 약세 토론은 `2 * max_debate_rounds`만큼 왕복한 뒤 리서치 매니저로 넘어갑니다. 리스크 토론은 공격적, 중립적, 보수적 세 관점이 참여하므로 `3 * max_risk_discuss_rounds`만큼 돌고 나서 포트폴리오 매니저로 넘어갑니다. 토론 깊이가 설정값으로 노출돼 있어, 몇 라운드를 돌릴지 사용자가 직접 정합니다.

## 논문의 조직도가 코드로 어떻게 남았나

논문의 조직도와 저장소 디렉터리가 거의 1:1로 대응합니다. 여기서 "논문에만 있는 개념"과 "코드로 구현된 부분"의 간극이 크지 않다는 점이 이 프로젝트의 장점입니다.

| 논문 개념 | 코드 위치 |
|---|---|
| 애널리스트 팀 | `tradingagents/agents/analysts/` (`create_market_analyst` 등 팩토리) |
| 강세/약세 토론 | `tradingagents/agents/researchers/` + `graph/` 조건 로직 |
| 트레이더 | `tradingagents/agents/trader/` |
| 리스크 토론과 매니저 | `tradingagents/agents/risk_mgmt/`, `tradingagents/agents/managers/` |
| 그래프 조립 | `tradingagents/graph/setup.py`의 `GraphSetup.setup_graph()` |

오케스트레이션은 [LangGraph](https://langchain-ai.github.io/langgraph/)의 `StateGraph`로 짜여 있습니다. 애널리스트가 정해진 순서로 도구를 호출하고 메시지를 정리한 뒤 강세 리서처로 넘어가고, 이후 리서치 매니저에서 트레이더로, 리스크 토론을 거쳐 포트폴리오 매니저에서 끝나는 경로가 그래프의 노드와 엣지로 표현됩니다. 실행이 끝나면 `tradingagents/reporting.py`가 애널리스트, 리서치, 트레이더, 리스크, 포트폴리오 매니저의 결과를 마크다운 트리와 `complete_report.md`로 저장합니다. 결정 하나가 어떤 근거를 거쳐 나왔는지 추적할 수 있는 감사 기록이 남습니다.

모델은 두 단계로 나눠 씁니다. `default_config.py`의 기본값은 깊은 추론용 `deep_think_llm`에 `gpt-5.5`, 빠른 처리용 `quick_think_llm`에 `gpt-5.4-mini`입니다. 무거운 판단에는 강한 모델을, 반복적인 잔손질에는 저렴한 모델을 붙이는 구성입니다. 제공자는 OpenAI, Google Gemini, Anthropic Claude, xAI Grok, DeepSeek, Qwen(DashScope), GLM(Zhipu), MiniMax, OpenRouter, Ollama, Azure OpenAI, AWS Bedrock 등 폭넓게 지원합니다. 데이터 vendor는 기본적으로 주가와 기술적 지표, 기본적 분석, 뉴스에 `yfinance`, 거시 지표에 `fred`, 예측 시장 데이터에 `polymarket`을 씁니다.

## 메모리와 재현성

논문에서 흥미로웠던 반성(reflection) 루프가 코드에도 들어 있습니다. 완료된 실행은 결정을 `~/.tradingagents/memory/trading_memory.md`에 append합니다. 같은 종목을 다시 돌릴 때 실현 수익과 SPY 대비 알파를 계산하고, 짧은 반성 문장을 만들어 이후 포트폴리오 매니저 프롬프트에 넣습니다. 가중치를 바꾸지 않고도 과거 결과를 다음 판단의 맥락으로 되먹이는, 가벼운 학습 루프입니다.

체크포인트 재개는 `--checkpoint` 옵션이나 설정으로 켜는 선택 사항이고, 종목별 SQLite 데이터베이스가 `~/.tradingagents/cache/checkpoints/` 아래에 저장됩니다.

여기서 중요한 재현성 경고가 하나 나옵니다. README는 LLM 샘플링, 추론 모델의 특성, 그리고 실시간 뉴스와 소셜 데이터의 변화 때문에 같은 종목과 날짜라도 실행마다 결과가 달라질 수 있다고 명시합니다. 그래서 "백테스트 결과가 어떤 발표 수치와도 일치한다고 보장하지 않는다"고 못 박고, 이 프레임워크를 고정 수익 전략이 아니라 멀티 에이전트 분석을 위한 연구용 scaffold로 보라고 설명합니다. 만든 사람들 스스로가 그렇게 선을 긋고 있다는 점을 기억해두면 좋습니다.

## v0.3.0에서 바뀐 것

저장소를 논문 데모가 아니라 "관리되는 연구 도구"로 만든 변화가 v0.3.0에 몰려 있습니다.

가장 눈에 띄는 것은 검증된 데이터 접근 규약(verified data-access contract)입니다. 심볼 정규화, 명시적인 vendor chain, 타입이 정해진 `VendorError`, 미래 데이터를 참조하지 않는 뉴스 윈도우(look-ahead-safe), 오래된 OHLCV 데이터 거부가 여기에 들어갑니다. 특히 `interface.py`는 지정된 vendor chain만 사용하고, 선택하지 않은 vendor로 조용히 fallback하지 않도록 설계돼 있습니다. 데이터가 어디서 왔는지 모른 채 결과만 받는 상황을 막으려는 장치입니다.

그 밖의 변화는 다음과 같습니다.

- 제공자 레지스트리 확장: NVIDIA, Kimi, Groq, Mistral, Bedrock, OpenAI 호환 엔드포인트를 추가했습니다.
- FRED 거시 지표와 Polymarket 이벤트 확률을 데이터 소스로 편입했습니다.
- `TradingAgentsGraph.save_reports()`로 리포트를 프로그램에서 저장하는 경로가 생겼습니다.
- 추론 깊이를 환경 변수로 조절할 수 있게 됐습니다.
- CI 게이트가 추가됐습니다. Python 3.10부터 3.13까지 매트릭스로 pytest를 돌리고, 설치 스모크 테스트와 엄격한 `ruff check`를 통과해야 합니다.

한 단계 앞선 `v0.2.5`에는 짚어둘 만한 수정이 있습니다. 이전 흐름에서는 Sentiment Analyst가 프롬프트 압박을 받으면 소셜 게시글을 지어낼 여지가 있었는데, 이를 실제 Yahoo News, StockTwits, Reddit 데이터를 읽도록 고쳤다고 설명합니다. LLM 에이전트가 근거 없이 그럴듯한 내용을 만들어내는 문제를 데이터 grounding으로 막은 사례입니다.

## 백테스트 수치를 조심해서 봐야 하는 이유

논문의 실험 결과부터 보겠습니다. 백테스트 기간은 2024년 1월 1일부터 3월 29일까지이고, 비교 대상은 Buy and Hold, MACD, KDJ+RSI, ZMR, SMA 같은 규칙 기반 전략입니다. 지표는 누적 수익(CR), 연환산 수익(ARR), Sharpe Ratio(SR), 최대 낙폭(MDD)을 씁니다. 논문 Table 1은 세 종목을 비교합니다.

| 종목 | 누적 수익 | 연환산 수익 | Sharpe Ratio | 최대 낙폭 |
|---|---|---|---|---|
| AAPL | 26.62% | 30.5% | 8.21 | 0.91% |
| GOOGL | 24.36% | 27.58% | 6.39 | 1.69% |
| AMZN | 23.21% | 24.90% | 5.60 | 2.11% |

논문은 표본 종목에서 최소 23.21%의 누적 수익과 24.90%의 연환산 수익을 달성했고, 가장 좋은 베이스라인보다 6.1%p 이상 앞섰다고 설명합니다. 숫자만 보면 인상적입니다. 하지만 그대로 받아들이기 전에 짚어야 할 것이 여러 개 있습니다.

Sharpe Ratio가 이례적으로 높습니다. 보통 SR이 2를 넘으면 매우 좋음, 3을 넘으면 탁월함으로 봅니다. AAPL의 8.21은 그 기준을 한참 벗어납니다. 흥미로운 점은 저자들 스스로 이 값이 예상 범위보다 높다고 인정한다는 것입니다. 해당 기간 동안 TradingAgents의 낙폭이 거의 없었던 현상 때문이라고 해석하는데, 뒤집어 말하면 3개월이라는 특정 구간의 우호적인 시장 상황에 크게 기댄 수치라는 뜻이기도 합니다.

기간과 종목이 좁습니다. 3개월, 몇 개의 대형 기술주에 한정된 결과입니다. 왜 이렇게 짧았을까요. 논문은 주석에서 예측 하나에 "11번의 LLM 호출과 20번 이상의 도구 호출"이 들어가서, LLM과 도구 사용 비용이 무거워 긴 백테스트가 어려웠다고 밝힙니다. 비용이 실험 범위를 제약한 것이고, 이 비용은 실제 운용에서도 그대로 부담이 됩니다.

가장 중요한 경고는 데이터 오염(contamination) 위험입니다. 논문은 미래 데이터를 쓰지 않았다(no future data)고 주장하지만, LLM은 사전 학습 과정에서 2024년 1분기의 뉴스와 주가 흐름을 이미 봤을 가능성이 있습니다. 백테스트 코드가 미래 데이터를 넣지 않았더라도, 모델의 가중치 안에 이미 그 시기의 결과가 들어 있다면 진짜 예측이 아니라 기억을 재생하는 것일 수 있습니다. LLM 백테스트가 가진 근본적인 약점이고, README가 강조하는 재현성 경고와 함께 비판적으로 봐야 합니다.

백테스트는 라이브 트레이딩이 아닙니다. 슬리피지, 거래 비용, 실시간 데이터 변동, 시장 국면 변화가 모두 빠져 있습니다. 이 수치들은 "이 방식으로 돈을 벌 수 있다"는 증거가 아니라, "역할을 나눈 에이전트 조직이 감사 가능한 결정을 만들어냈다"는 설계 실험의 결과로 읽는 편이 맞습니다.

## 커뮤니티 반응

Reddit r/AI_Agents에도 TradingAgents를 소개하는 글이 하나 보입니다. 이 프레임워크를 단순한 트레이딩 wrapper가 아니라 여러 역할을 가진 에이전트로 이뤄진 hedge fund에 가깝게 소개하는 시각입니다. 다만 공개적으로 확인되는 반응 규모는 크지 않고, 독립적인 사용 후기보다는 프로젝트 소개에 가까워 보입니다. 그래서 실제 사용자가 부딪히는 지점은 GitHub 이슈에서 더 구체적으로 드러납니다.

GitHub 이슈를 보면 사람들이 실제로 어디서 막히는지 드러납니다. 아래는 공개된 이슈에서 확인한 흐름입니다.

관심이 많은 방향은 확장입니다. [#82](https://github.com/TauricResearch/TradingAgents/issues/82)는 크립토 트레이딩으로 넓힐 수 있는지 묻습니다. 반복 비용을 줄이려는 시도도 활발합니다. [#750](https://github.com/TauricResearch/TradingAgents/issues/750)은 프롬프트 구성 방식 탓에 LLM API의 prompt cache 적중률이 사실상 0이라는 문제를 제기하고, [#1032](https://github.com/TauricResearch/TradingAgents/issues/1032)는 로컬 LLM 응답 캐시로 API 비용을 줄이려는 PR입니다. 예측 하나에 열 번 넘는 LLM 호출이 든다는 구조를 생각하면, 비용은 커뮤니티의 핵심 관심사입니다.

설정과 제공자 연동에서 걸리는 사례도 많습니다. [#227](https://github.com/TauricResearch/TradingAgents/issues/227)은 OpenRouter 키를 쓸 때 OpenAI SDK 관련 오류가 난다는 보고이고, [#148](https://github.com/TauricResearch/TradingAgents/issues/148)은 Gemini 사용 문제, [#174](https://github.com/TauricResearch/TradingAgents/issues/174)와 [#158](https://github.com/TauricResearch/TradingAgents/issues/158)은 모델 선택과 커스텀 설정에 관한 질문입니다.

가장 뼈아픈 지적은 데이터 품질입니다. [#214](https://github.com/TauricResearch/TradingAgents/issues/214)는 기본 데이터(PE, PB 등)가 틀렸다는 강한 문제 제기이고, [#130](https://github.com/TauricResearch/TradingAgents/issues/130)은 중국 A주 가격 오류, [#162](https://github.com/TauricResearch/TradingAgents/issues/162)는 잘못된 데이터 전반을 다룹니다. 앞서 본 v0.3.0의 검증된 데이터 접근 규약은 바로 이런 신호에 대한 대응으로 읽힙니다. 설계 측면의 개선 제안도 있습니다. [#542](https://github.com/TauricResearch/TradingAgents/issues/542)는 지표 계산을 LLM 분석에서 분리하자는 제안이고, [#717](https://github.com/TauricResearch/TradingAgents/issues/717)은 반성 루프가 운 좋은 승리에 과학습하지 않도록 surprise ratio로 가중치를 주자는 아이디어, [#1105](https://github.com/TauricResearch/TradingAgents/issues/1105)는 근거 원장(evidence ledger)과 인용, 가드레일을 붙이는 PR입니다.

종합하면 커뮤니티의 관심은 두 축입니다. 하나는 비용을 어떻게 줄일 것인가, 다른 하나는 데이터를 어떻게 믿을 수 있게 만들 것인가입니다. 둘 다 "그럴듯한 결정을 내는 것"과 "믿을 만한 결정을 내는 것" 사이의 간극을 가리킵니다.

## 함께 보면 좋을 자료

- [TradingAgents 공식 문서](https://tauricresearch.github.io/TradingAgents/): 저장소와 함께 제공되는 GitHub Pages 문서
- [Mixture of Agents(MoA)](/korean/blog/mixture-of-agents-moa/): 여러 LLM을 계층으로 쌓는 또 다른 멀티 에이전트 설계
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/): TradingAgents가 오케스트레이션에 쓰는 그래프 런타임
- [arXiv q-fin.TR](https://arxiv.org/list/q-fin.TR/recent): 계량 금융 트레이딩 분야의 최근 논문 목록

## 정리

TradingAgents는 "LLM으로 돈 버는 봇"이 아니라, 애널리스트에서 토론과 트레이더, 리스크 토론, 매니저로 이어지는 역할 분담형 에이전트 구조를 금융 도메인에 깔끔하게 구현한 연구용 scaffold입니다. 논문의 조직도가 코드에 거의 그대로 남아 있어 멀티 에이전트 설계를 공부하기에 좋고, v0.3.0에 오면서 데이터 검증과 CI, 제공자 연동이 크게 강화돼 데모보다 훨씬 다듬어진 도구가 됐습니다.

다만 백테스트 수치는 짧은 기간, 좁은 종목, 이례적으로 높은 Sharpe Ratio, 무거운 LLM과 도구 비용, 그리고 데이터 오염 위험을 함께 놓고 봐야 합니다. 만든 사람들조차 이 결과가 어떤 발표 수치와도 일치한다고 보장하지 않는다고 적어뒀습니다. 이 프로젝트의 진짜 가치는 수익률이 아니라, 토론과 반성과 구조화된 소통으로 감사 가능한 결정을 만들어내는 에이전트 설계 그 자체에 있습니다.

## 참고 자료

- [arXiv:2412.20138: TradingAgents: Multi-Agents LLM Financial Trading Framework](https://arxiv.org/abs/2412.20138): Yijia Xiao, Edward Sun, Di Luo, Wei Wang, 조회일 2026-07-03
- [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents): GitHub, Apache-2.0, 조회일 2026-07-03
- [TradingAgents 공식 문서](https://tauricresearch.github.io/TradingAgents/): Tauric Research, 조회일 2026-07-03
- [TradingAgents v0.3.0 릴리스](https://github.com/TauricResearch/TradingAgents/releases): GitHub Releases, 조회일 2026-07-03
