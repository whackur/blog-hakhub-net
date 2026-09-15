---
title: "앤트로픽은 왜 이걸 공개했나: 키미의 클로드 무단 우회와 '죽은 채널'의 전략적 가치"
meta_title: ""
description: "앤트로픽 2026년 9월 위협 보고서가 밝힌 Moonshot의 Kimi→Claude 무단 우회 사건. 민감 데이터가 들어오는 채널을 왜 조용히 유지하지 않고 공개했는지, 기업의 이해와 정보기관의 이해를 나눠 해석합니다."
date: 2026-09-15T13:30:00+09:00
lastmod: 2026-09-15T13:30:00+09:00
image: "/images/posts/anthropic-moonshot-disclosure-strategy/cover.png"
categories: ["AI"]
tags: ["llm", "distillation", "ai-security", "anthropic", "kimi"]
author: "whackur"
translationKey: "anthropic-moonshot-disclosure-strategy"
draft: false
---

앤트로픽이 2026년 9월 10일 공개한 위협 인텔리전스 보고서 [Detecting and countering misuse of AI: September 2026](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf)에는 눈을 의심하게 하는 사례가 하나 있습니다. Kimi 모델을 만드는 Moonshot AI가 자사 고객의 요청을 몰래 Claude로 전달하고, Claude의 응답을 Kimi의 답인 것처럼 고객에게 보여줬다는 주장입니다. 우회된 요청 중에는 민감한 내용도 있었습니다. 앤트로픽이 인민해방군(PLA) 연계 가능성이 높다고 평가한 사용자의 청두(成都) CCTV 추적 분석 요청, 그리고 중국 대형 국유기업 엔지니어가 올린 내부 코드와 실사용 자격증명(live credentials)이 그 예입니다.

여기서 자연스러운 의문이 생깁니다. 중국의 민감 데이터가 미국 회사 서버로 흘러 들어오는 채널이라면, 정보기관 관점에서는 최고의 감청 창구입니다. 그런데 앤트로픽은 이걸 조용히 지켜보는 대신 보고서로 공개해 채널을 스스로 죽였습니다. 왜 그랬을까요. 이 글은 보고서의 사실관계를 먼저 정리하고, 그 위에서 공개라는 선택의 전략적 계산을 해석해 봅니다.

## 보고서가 실제로 주장하는 것

먼저 사실의 층위를 분명히 하겠습니다. 아래 내용은 모두 앤트로픽 자체 조사에 근거한 보고서의 주장이며, 제3자가 독립 검증한 사실이 아닙니다.

보고서는 2025년 12월부터 2026년 8월까지 차단한 오용 사례를 다루는데, 그중 무단 증류(distillation) 섹션이 이번 논란의 중심입니다. Moonshot 건(GTG-16002)의 핵심 주장은 이렇습니다. Moonshot이 고객 요청을 Kimi로 처리하지 않고 몰래 Claude로 전달했고, 사용자는 Kimi를 쓴다고 믿었지만 실제로는 Claude의 응답을 받았습니다. 한 사례에서는 열흘 동안 30만 건 가까운 고객 요청이 앤트로픽으로 중계됐고, 대부분 Claude Opus로 라우팅됐습니다. 이 중계에는 5,380개의 위장 계정으로 구성된 proxy 네트워크가 쓰였으며, 계정 대부분은 싱가포르와 일본 소재로 위장돼 있었다고 합니다.

보고서가 공개한 증류 캠페인의 규모를 표로 정리하면 이렇습니다. 교환(exchange) 건수는 앤트로픽이 2026년 5월부터 7월까지 관측했다고 밝힌 수치이고, 나머지 수치에는 관측 구간이 따로 적혀 있지 않습니다.

| 조직 | 보고서 주장 규모 |
|------|------|
| Moonshot (Kimi) | 2,300만 건 이상의 교환. 열흘간 30만 건에 가까운 중계, 위장 계정 5,380개 |
| Alibaba (Qwen/Tongyi Lab) | 1억 5,100만 건 이상. 앤트로픽이 측정한 역대 최대 규모 |
| Xiaomi (MiMo) | 1,500개 이상 계정으로 40만 건 이상 요청 |
| DeepSeek | Moonshot과 같은 cross-session replay 전술, 유사한 무단 중계 |

기술적으로 흥미로운 부분은 chain-of-thought 추출 방법입니다. Claude는 내부 추론(reasoning) 원문을 그대로 노출하지 않고, thinking signature라는 서명 값으로 추론 내용을 봉인합니다. 추론 과정 자체가 증류하기 가장 좋은 학습 데이터라서, 원문 대신 서명만 넘겨 재사용을 막는 보호 장치입니다. 보고서에 따르면 Moonshot과 DeepSeek은 이 서명을 저장했다가 새 세션을 열어 다시 넘기는 방식(cross-session replay)으로 봉인된 추론을 복원하는 파이프라인을 만들었습니다. 보호 장치를 정면으로 우회한 셈입니다.

이 파이프라인이 언제 막혔는지는 보고서에 나오지 않습니다. 대신 대응책이 적혀 있습니다. Claude는 이제 응답 전에 내부 추론을 요약해서 내보내므로, 빼낸 기록의 학습 가치가 떨어집니다. Fable 5.1에는 preserved thinking이 들어가, 새로 만든 API 계정은 추론 앞에 오는 시스템 프롬프트와 도구 정의, 메시지를 바꿀 수 없습니다. 분류기는 Fable 5 출시에 맞춰 강화했고, 서비스 미지원 국가(중국, 러시아, 이란) 계정에는 신원 확인 절차를 붙였다고 합니다.

민감 데이터 사례는 보고서에 기술된 대로 정리하면 이렇습니다. PLA 연계 가능성이 높다고 평가된 사용자는 Kimi라고 믿은 창구에 청두 시내 수백 대의 카메라(PLA 시설과 연구소 주변 카메라 포함)에서 뽑은 특정 개인의 CCTV 아카이브 데이터를 올리고, 이 사람의 행동이 비정상적인지 분석해 달라고 요청했습니다. 중국 대형 국유기업의 엔지니어는 내부 시스템을 만들면서 여러 중국 대기업의 내부 코드와 실사용 자격증명을 노출했습니다.

여기서 주의할 점을 명확히 적어 두겠습니다. PLA 연계는 앤트로픽의 평가("likely")이지 검증된 귀속(attribution)이 아닙니다. 민감 데이터 주장 전체가 앤트로픽 자체 조사에 기대고 있습니다. "데이터가 앤트로픽 서버에 도달했다"는 것과 "미국 정부가 국가 기밀을 입수했다"는 것은 전혀 다른 명제입니다. 그리고 보고서 스스로도 Moonshot이 고객에게 우회 사실을 알렸는지 여부는 알지 못한다고 적었습니다.

## 공개라는 선택의 전략적 계산

여기서부터는 보고서의 사실을 근거로 한 해석입니다. 앤트로픽의 내심은 알 수 없으니, 회사 입장에서 계산이 어떻게 서는지를 따져 보는 방식으로 접근합니다.

### 채널은 발표 시점에 이미 죽어 있었다

보고서의 관측 구간은 2026년 5월부터 7월이고, 활동은 "disrupted", 즉 이미 차단된 상태로 기술됩니다. 발표일은 9월 10일입니다. 조용히 있는다고 해서 지켜지는 채널이 애초에 없었습니다. proxy 네트워크는 어차피 빠르게 재구축되는 소모품이라, 특정 계정군을 차단한 순간 그 창구의 정보 가치는 끝납니다. 해석하면, 공개는 살아 있는 채널을 죽인 결정이 아니라 이미 죽은 채널을 현금화한 결정입니다.

### 기업에게 그 데이터는 자산이 아니라 부채다

PLA 연계로 평가되는 감시 데이터와 국유기업의 실사용 자격증명이 자사 서버로 계속 들어온다는 사실을 알면서도 조용히 받는 회사가 있다면, 그 회사는 등록되지 않은 정보 수집 기관처럼 보이기 시작합니다. 탐지 전에 모르고 받은 것과, 탐지 후에 알면서 계속 보유하는 것은 법적으로도 평판상으로도 전혀 다른 문제입니다. 기업이 취할 수 있는 유일하게 정당한 출구는 당국과 업계 파트너에게 공유하고(보고서는 "where appropriate"라는 표현으로 이를 수행했다고 밝힙니다) 사실을 공개하는 것뿐입니다. 이 데이터를 계속 수집해서 이득을 볼 주체가 있다면 그것은 국가 기관이지, 규제와 평판 리스크를 떠안는 민간 기업이 아닙니다.

### 공개 자체가 무기다

죽은 채널을 현금화하는 방법이 바로 공개입니다. 판단하건대 효과는 최소 다섯 갈래입니다.

첫째, 우회를 실행한 연구소들의 고객 신뢰가 무너집니다. 중국 기업 고객 입장에서 "국산 모델에 준 데이터를 미국 회사가 처리했다"는 사실은 이탈과 조달 심사 강화로 직결됩니다. 둘째, 중국의 데이터 주권 규제가 역으로 중국 연구소들을 겨눌 수 있습니다. 데이터안전법(DSL)과 개인정보보호법(PIPL)은 데이터의 무단 국외 이전을 강하게 규제하는데, 이 보고서가 바로 그 증거 자료가 됩니다. 다만 [AI타임스 기사](https://www.aitimes.com/news/articleView.html?idxno=215229)가 언급한 국가인터넷정보판공실(CAC)의 조사나 제재 가능성은 어디까지나 추측이며, 확정된 사실이 아닙니다. 셋째, 억지력 광고입니다. proxy 네트워크를 조직 단위로 귀속시킬 수 있다는 능력의 공개는 모든 연구소의 증류 비용을 올립니다. 넷째, 안전장치의 실증입니다. 보고서에 따르면 Zhipu는 GLM 5.3 출시를 앞두고 처음에 사이버 안전장치가 강화된 Fable을 공격 대상으로 삼았다가, 안전장치 때문에 공격 성능이 떨어지자 포기하고 안전장치가 약하다고 판단한 Opus 4.6과 다른 미국 연구소 모델로 갈아탔습니다. 안전장치가 실제로 공격자의 선택을 바꿨다는 사례를 앤트로픽이 직접 확보한 셈입니다. 다섯째, 미국의 프론티어 모델 보호 정책 논의에 쓸 증거 패키지가 됩니다. [CNBC 보도](https://www.cnbc.com/2026/09/03/anthropic-distillation-battle-turns-to-dark-web-china-concerns-swell.html)처럼 증류 문제는 이미 다크웹 거래와 대중국 우려로 번지는 중이었고, 이 보고서는 그 서사에 1차 자료를 공급합니다.

### 채널 유지는 공짜 감청이 아니었다

간과하기 쉬운 지점입니다. 이 채널을 살려 두려면 앤트로픽이 Claude 응답을 계속 공급해야 합니다. 그 응답을 Moonshot은 자사 고객에게 서비스로 팔고, 학습 데이터로 증류합니다. 채널 유지는 곧 경쟁사의 제품 품질과 모델 성능 향상에 자금을 대는 일이었습니다. 불확실한 정보 가치와 경쟁사 육성 비용을 맞바꾸는 거래는 기업에게 명백히 손해입니다. 정보기관이라면 계산이 다를 겁니다. 경쟁사 성장은 자기 손익이 아니고 감청 창구의 가치가 훨씬 크니까요. "왜 채널을 안 살렸나"라는 처음의 의문은 사실 정보기관의 손익계산서를 기업에 적용한 데서 나온 착시입니다. 이 전제 분리가 이 사건을 읽는 열쇠라고 봅니다.

### 두 동기는 공존한다

보고서는 공개 이유를 "we believe we have a responsibility to disclose malicious misuse of our services"(우리 서비스의 악의적 오용을 공개할 책임이 있다고 믿는다)라고 밝힙니다. 이 안전 공시 의무가 진심이 아니라고 볼 근거는 없습니다. 동시에 위에서 본 전략적 이득도 실재합니다. 둘은 배타적이지 않습니다. 명분과 실리가 같은 방향을 가리킬 때 기업의 의사결정은 쉬워지고, 이번 공개가 정확히 그런 경우였다고 해석합니다.

## 커뮤니티 반응

[Hacker News의 보고서 스레드](https://news.ycombinator.com/item?id=49647300)(243개 댓글)와 [Moonshot 우회 건 별도 스레드](https://news.ycombinator.com/item?id=49656698)에서는 논점이 여러 갈래로 갈렸습니다.

가장 눈에 띄는 반발은 앤트로픽 자신을 향했습니다. 한 댓글(CrzyLngPwd)은 이 보고서를 "고객을 감시한다고 말하지 않으면서 고객을 감시한다고 말하는 방법"이라고 꼬집었습니다. 우회 사례를 이 정도로 상세히 재구성했다는 것 자체가 앤트로픽이 요청 내용을 들여다볼 수 있다는 증거라서, 기업 고객에게도 불편한 사실이라는 지적입니다.

증류 윤리를 놓고도 논쟁이 붙었습니다. 증류는 결국 공개 웹에서 배우는 것과 다르지 않다는 옹호론(esafak, jchw 등)에, 진짜 문제는 증류가 아니라 위장 계정과 도난 자격증명, 그리고 고객을 속인 중간자(man-in-the-middle) 기만이라는 반론(villish, qgin 등)이 맞섰습니다. wongarsu는 Moonshot이 "어떤 모델인지 밝히지 않는 미스터리 모델 요금제"를 공개적으로 팔았다면 문제 삼을 게 없었겠지만, Kimi를 서비스하는 척하며 Claude를 중계한 것이 잘못의 본질이라고 정리했습니다.

기술적 개연성 논쟁도 있었습니다. KronisLV는 Kimi의 thinking 출력에서 Anthropic 가이드라인을 언급하는 걸 본 적이 있다며 정황을 보탰고, realusername은 Kimi는 추론 과정을 전부 보여주는데 Claude는 숨기므로 중계가 어떻게 성립하는지 의문을 제기했습니다. echelon은 동기식 중계라면 응답 이후 사용자 행동까지 학습(RLHF)에 쓸 수 있다는 점을 짚었습니다. 벤치마크 회의론(enraged_camel: 이 연구소들이 벤치마크에서 그렇게 높은 점수를 낸 배경 아니냐), 귀속 회의론(punk_ihaq: 예멘이나 러시아, 중국에서 접속한 장비가 다른 나라 행위자의 VPN 출구일 수 있다), 정책 포석이라는 독해(echelon: 결국 "미국에서 AI를 규제해 달라"는 메시지)도 나왔습니다.

중국 사용자 관점의 댓글도 있었습니다. woctordho는 중국에서는 감시에 익숙해서 앤트로픽이 데이터를 보는 것 자체는 큰 문제가 아니라는 반응을 전했습니다. 반면 bbor는 스레드 전체가 오히려 과소반응한다며, 수백만 중국 사용자의 요청을 미국 회사로 돌리는 공유 proxy 인프라의 존재 자체가 이 사건에서 제일 비정상적인 부분이라고 반박했습니다. 사건 개요는 [TechCrunch 기사](https://techcrunch.com/2026/09/10/anthropic-details-distillation-campaigns-from-alibaba-moonshot-ai-and-deepseek/)가 잘 정리했습니다.

## 함께 보면 좋을 자료

- [Detecting and countering misuse of AI: September 2026 (PDF)](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf): 앤트로픽 원문 보고서
- [HN: Detecting and countering misuse of AI](https://news.ycombinator.com/item?id=49647300): 보고서 전체를 다룬 메인 스레드
- [HN: Moonshot serves Claude instead of Kimi](https://news.ycombinator.com/item?id=49656698): Moonshot 우회 건 집중 스레드
- [TechCrunch: Anthropic details distillation campaigns](https://techcrunch.com/2026/09/10/anthropic-details-distillation-campaigns-from-alibaba-moonshot-ai-and-deepseek/): 사건 요약 보도
- [CNBC: Anthropic's distillation battle turns to the dark web](https://www.cnbc.com/2026/09/03/anthropic-distillation-battle-turns-to-dark-web-china-concerns-swell.html): 증류 공방의 배경 맥락
- [AI타임스: 중국 '키미', 클로드 무단 우회 연결 파문](https://www.aitimes.com/news/articleView.html?idxno=215229): 한국어 보도, CAC 제재 추측 포함

## 정리

처음의 질문으로 돌아가겠습니다. 중국 민감 데이터가 흘러드는 채널을 왜 공개해서 죽였나. 답은 그 질문의 전제에 있습니다. 채널을 살려 두는 게 이득인 주체는 정보기관이지 기업이 아닙니다. 앤트로픽 입장에서 그 채널은 발표 시점에 이미 차단돼 있었고, 들어온 데이터는 자산이 아니라 법적, 평판적 부채였으며, 채널 유지는 경쟁사의 제품과 모델을 계속 키워 주는 비용이었습니다. 공개는 죽은 채널을 경쟁사 신뢰 훼손, 중국 데이터 규제를 빌린 압박, 억지력 광고, 안전장치 실증, 정책 근거라는 다섯 가지 가치로 바꾼 선택입니다. 보고서가 내세운 공시 책임과 이 전략적 이득은 충돌하지 않고 같은 결론을 가리킵니다. 다만 이 모든 사실관계가 앤트로픽 단독 조사에 기대고 있고, PLA 연계는 평가일 뿐이며, CAC 제재는 아직 추측이라는 점은 끝까지 붙들고 읽어야 합니다.

## 참고 자료

1. [Detecting and countering misuse of AI: September 2026](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf): Anthropic, 조회일 2026-09-15
2. [HN 스레드: Detecting and countering misuse of AI](https://news.ycombinator.com/item?id=49647300): Hacker News, 조회일 2026-09-15
3. [HN 스레드: Moonshot serves Claude instead of Kimi](https://news.ycombinator.com/item?id=49656698): Hacker News, 조회일 2026-09-15
4. [Anthropic details distillation campaigns from Alibaba, Moonshot AI, and DeepSeek](https://techcrunch.com/2026/09/10/anthropic-details-distillation-campaigns-from-alibaba-moonshot-ai-and-deepseek/): TechCrunch, 조회일 2026-09-15
5. [Anthropic's distillation battle turns to the dark web as China concerns swell](https://www.cnbc.com/2026/09/03/anthropic-distillation-battle-turns-to-dark-web-china-concerns-swell.html): CNBC, 조회일 2026-09-15
6. [중국 '키미', 클로드 무단 우회 연결 파문…안보·기업 기밀 유출 논란](https://www.aitimes.com/news/articleView.html?idxno=215229): AI타임스 임대준 기자, 조회일 2026-09-15
