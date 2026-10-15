---
title: "Kimi 요청을 Claude로 보냈다는 앤트로픽 보고서, 왜 공개했을까"
meta_title: ""
description: "Kimi 요청의 Claude 중계 의혹을 바탕으로, 민감한 입력의 관측보다 공개가 유리할 수 있는 이유와 추론 재사용·개인정보 문제를 짚습니다."
date: 2026-09-15T13:30:00+09:00
lastmod: 2026-10-15T11:40:30+00:00
image: "/images/posts/anthropic-moonshot-disclosure-strategy/disclosure-cover-20261015.webp"
categories: ["AI"]
tags: ["llm", "distillation", "ai-security", "anthropic", "kimi"]
author: "whackur"
translationKey: "anthropic-moonshot-disclosure-strategy"
draft: false
---

민감한 정보가 Claude에 들어오고 있었다면, 앤트로픽은 왜 그 사실을 공개했을까요. **모델 제공사에는 그 입력을 더 관측하는 이익보다 무단 이용을 줄이고 고객의 데이터 처리 문제를 알리는 이익이 더 클 수 있습니다.** 경쟁사의 요청에 계속 답하면 연산 자원을 쓰면서 경쟁 모델의 학습 자료까지 만들어 주는 셈입니다. 공개는 계정 차단만으로 닿기 어려운 이용자와 기업 고객에게도 문제를 알립니다. 다만 이는 공개의 이해관계를 설명하는 추론이며, 회사 내부의 의사결정이 확인됐다는 뜻은 아닙니다.

앤트로픽이 [2026년 9월 보고서](https://www.anthropic.com/threat-intelligence-report-september-2026)에서 밝힌 이유는 악의적인 서비스 오용을 공개할 책임입니다. 다른 개발사의 탐지와 사회의 대응에 도움이 되기를 바란다고도 설명합니다. Moonshot의 Kimi 요청이 Claude로 넘어왔다는 주장은 그 보고서의 한 사례입니다. 민감한 입력을 받았다는 사실을 곧 정보 수집의 성공으로 읽으면, 서비스를 보호해야 하는 회사의 입장과 입력을 보낸 이용자의 권리가 빠집니다.

## 고객 요청을 처리하면서 학습 자료도 모았다는 주장

보고서의 Moonshot 사례(GTG-16002)는 두 행동을 연결합니다. Moonshot이 일부 고객 요청을 Kimi 대신 Claude에 보내 그 응답을 이용자에게 돌려줬고, 그중 일부 대화를 저장해 모델 학습용 추론 기록을 추출했다는 것입니다. **중계는 당장의 요청 처리 방식이고, 증류는 모은 출력을 다른 모델의 학습에 쓰는 방식입니다.** 중계만 확인됐다고 학습까지 입증되는 것은 아니며, 앤트로픽은 이번 사례에서 둘 다 있었다고 주장합니다. ([원문 PDF, 148~149쪽](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf))

보고서가 제시한 흐름은 이용자 요청이 Moonshot을 거쳐 중계 계정망으로 들어가고, Claude가 만든 응답이 다시 이용자에게 돌아오는 것입니다. 한 사례에서는 열흘 동안 약 30만 건이 전달됐고 대부분 Opus를 사용했다고 합니다. 앤트로픽은 위장 계정 5,380개가 쓰였으며 겉으로는 대부분 싱가포르와 일본에 있는 것처럼 보였다고 적었습니다. 정확한 라우팅 구현과 계정별 운영 기록은 공개하지 않았습니다.

이 흐름은 미리 만든 질문을 모델에 대량으로 보내 답을 수집하는 방식과 다릅니다. 실제 이용자의 작업이 질문을 공급하고, 모델의 응답이 서비스 결과인 동시에 학습 자료 후보가 됩니다. 보고서의 주장대로라면 요청에 딸린 기업 문서나 코드도 함께 넘어갑니다. 모든 Kimi 요청이 중계됐다거나 Kimi의 성능 전체가 Claude에서 나왔다는 주장은 보고서로 뒷받침되지 않습니다.

민감 데이터 사례는 이를 구체적으로 보여 줍니다. 앤트로픽은 한 사용자가 청두의 CCTV 수백 대에서 모은 자료로 특정 인물의 행동이 평소와 다른지 물었다고 설명합니다. 이 사용자가 중국 인민해방군(PLA)과 연계됐을 가능성이 높다는 귀속은 앤트로픽의 평가입니다. 다른 사례에서는 중국 대형 국유기업 엔지니어의 요청에 여러 기업의 내부 코드와 당시 유효했던 접속 자격증명이 들어 있었다고 합니다. 현재도 그 자격증명이 유효하다는 뜻은 아닙니다. ([PDF, 149쪽](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf))

보고서는 Moonshot이 고객에게 중계 사실을 알렸는지 모른다고 명시합니다. 이 때문에 모든 고객이 몰랐다고 일반화할 수는 없습니다. 그래도 고객이 선택한 서비스와 실제 입력을 받은 사업자가 달랐다는 주장은 데이터 처리 약속을 따져 볼 충분한 이유가 됩니다. 이 사례의 귀속과 내용은 앤트로픽의 자체 조사에 근거하며, 인용한 자료에는 독립 감사 결과가 없습니다.

## 암호화된 추론을 다시 사용하게 하는 API

모델 학습 자료에는 최종 답변 외에 문제를 푸는 중간 추론 기록(chain of thought, CoT)도 쓰일 수 있습니다. 앤트로픽은 Moonshot이 이 기록을 얻으려고 Claude의 thinking 기능을 악용했다고 주장합니다. 이해하려면 화면에 보이는 추론문과 API가 다음 호출에 돌려받는 데이터를 나눠 봐야 합니다.

[현재 Claude API 문서](https://platform.claude.com/docs/en/build-with-claude/thinking#thinking-encryption)는 다음을 구분합니다.

| API 항목 | 문서가 설명하는 역할 |
| --- | --- |
| `thinking` block의 `thinking` 필드 | 모델과 설정에 따라 읽을 수 있는 추론문이나 요약을 담으며, 빈 문자열일 수도 있습니다. |
| 같은 block의 `signature` 필드 | 암호화된 전체 추론을 담습니다. API는 이를 검증에 사용하며 호출자는 값을 해석하거나 파싱하지 않고 그대로 돌려보냅니다. |
| `redacted_thinking` block의 `data` 필드 | 안전상 가려진 추론을 암호화해 담습니다. 일반 `thinking` block과는 별도 형식입니다. |

따라서 `signature`를 읽을 수 있는 추론문 자체로 설명해도 틀리고, 추론 데이터와 관계없는 검증용 꼬리표로만 설명해도 부정확합니다. 필드 이름은 signature이지만 현재 문서는 암호화된 전체 추론이 들어간다고 명시합니다.

이전 추론을 API에 다시 보내는 행위 자체는 정상 기능입니다. Claude가 도구를 호출한 뒤 결과를 기다릴 때, 호출자는 이전 thinking block을 수정하지 않고 함께 돌려보내 같은 응답을 이어 가게 합니다. ([도구 사용 시 thinking 보존](https://platform.claude.com/docs/en/build-with-claude/thinking#preserving-thinking-blocks))

보고서가 cross-session replay라고 부르는 행위는 저장한 signature를 새 세션에서 재사용하고 Claude가 연결된 추론 기록을 다시 서술하도록 유도했다는 것입니다. 이는 암호문을 외부에서 직접 해독했다는 주장과 다릅니다. 암호화된 데이터를 모델이 다시 활용하는 기능과, 그 내용을 사용자에게 노출하지 않는 통제가 함께 안전해야 한다는 문제입니다. 보고서는 Moonshot의 실제 요청 전문이나 재현 코드를 공개하지 않았으므로 정확한 성공 조건까지 확인할 수는 없습니다. ([PDF, 148~149쪽](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf))

앤트로픽은 대응책으로 추론 요약과 preserved thinking을 설명합니다. 현재 문서상 Fable 5.1부터의 preserved thinking은 앞선 시스템 프롬프트·도구·메시지가 바뀌었는지 검사합니다. 이 선행 맥락 검사는 2026년 8월 31일 00:00 UTC 이후 생성한 계정에 기본 적용되며, 그보다 오래된 계정은 지정된 설정을 보낸 요청에 적용됩니다. 이런 조건부 방어를 모든 계정의 모든 replay가 불가능해졌다는 보장으로 읽어서는 안 됩니다. ([현재 API의 적용 조건](https://platform.claude.com/docs/en/build-with-claude/thinking#preserved-thinking))

## 더 관측하는 이익과 서비스를 보호하는 이익

민감한 요청에는 조사 가치가 있을 수 있습니다. 그러나 그 요청을 계속 받는 동안 Claude는 응답을 만들어야 하고, 그 출력과 추론이 경쟁 모델에 쓰일 수 있습니다. 앤트로픽의 이해관계에는 입력을 관찰하는 것뿐 아니라 연산 비용, 접근 제한, 모델 능력의 무단 수집을 줄이는 일이 들어갑니다. 민감 데이터를 받으면 열람 권한과 보존 범위, 사고 대응에 필요한 자료도 관리해야 합니다. 정보가 민감하다는 이유만으로 계속 받을 유인이 더 크다고 단정하기 어렵습니다.

여기에는 안전 문제도 연결됩니다. 앤트로픽은 증류로 일반 추론 능력이 향상되면 수집 당시 겨냥하지 않은 생물학·사이버 분야의 능력도 좋아질 수 있고, Claude의 안전장치가 함께 이전되지는 않는다고 주장합니다. 이는 모델 제공사가 제시한 위험 논거이지, Moonshot의 특정 모델에서 그 결과를 독립적으로 측정했다는 뜻은 아닙니다. ([PDF, 146쪽](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf))

차단과 공개는 목적이 겹치면서도 수단이 다릅니다. 계정 차단은 해당 접근을 막습니다. 공개는 고객과 다른 사업자에게 데이터 흐름을 묻게 하고, 비슷한 운영을 탐지할 단서를 줍니다. 앤트로픽은 캠페인을 탐지하고 방해했다고 보고했지만 Moonshot의 모든 접근 경로가 공개 전에 닫혔다고 입증하지는 않았습니다. ‘이미 아무것도 관측할 수 없으니 공개했다’는 설명도 확인된 사실로 쓸 수 없습니다.

## 공개하면 경쟁사뿐 아니라 앤트로픽도 질문을 받습니다

고객에게 가장 직접적인 쟁점은 어느 회사의 모델이 더 잘 답했느냐보다 누가 입력을 처리했느냐입니다. 중계를 알게 된 기업 고객은 실제 처리 사업자와 보존 조건을 확인하고 계약상 약속과 비교할 수 있습니다. 이런 확인 요구가 늘면 Moonshot에는 설명과 대응 부담이 생깁니다. 앤트로픽에는 자사의 탐지 능력과 모델 보호 주장을 알리는 효과가 있습니다. 고객 신뢰와 정책 논의에서 유리하게 작용할 가능성은 있지만, 실제 매출 효과나 공개 결정에서 각 동기가 차지한 비중은 확인되지 않았습니다.

그 효과를 전부 앤트로픽의 이익으로 볼 수도 없습니다. 상세한 사례를 공개할수록 앤트로픽이 요청 내용을 얼마나 보관하고 누가 읽는지도 관심을 받습니다. [Hacker News의 Moonshot 토론](https://news.ycombinator.com/item?id=49656698)에서 wongarsu는 다른 모델로 보낼 수 있다고 고지한 서비스와 Kimi를 제공한다고 하면서 Claude로 보내는 서비스를 구분했습니다. 같은 토론의 AlanYx는 오용 조사에 따른 보존 범위가 고객의 예상보다 넓을 수 있다고 우려했습니다. 전자는 중계의 투명성, 후자는 조사 사업자의 데이터 처리 권한을 묻는 의견입니다. 댓글이 사건을 독립적으로 입증하는 것은 아닙니다.

[Reddit 토론의 작성자](https://www.reddit.com/r/ClaudeAI/comments/1wdz975/anthropics_new_report_has_no_winners_and_the_part/)도 이용자가 최종적으로 어느 제공사에 입력이 도착하는지 알기 어렵다는 점을 문제 삼았습니다. 이 지적은 앤트로픽이 모든 이용자를 무제한 감시했다는 주장으로 확대할 필요 없이 검토할 수 있습니다.

앤트로픽의 [현재 상용 제품 보존 안내](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data)는 API 입력·출력을 원칙적으로 30일 이내 삭제하되 계약, 정책 집행, 법률 등에 따른 예외를 둡니다. 자동 시스템이 정책 위반으로 표시한 대화의 입력·출력은 최대 2년, 분류 점수는 최대 7년 보존한다고 설명합니다. 이것이 이번 중계 계정에 실제 적용된 계약이나 보존 기간을 알려 주는 것은 아닙니다. 다만 오용 탐지와 개인정보 보호를 함께 검토해야 할 근거는 됩니다.

국경을 넘는 처리의 적법성도 개별 조건을 따져야 합니다. 보고서가 제기한 개인정보 문제만으로 특정 법 위반이나 제재를 확정할 수는 없습니다. 고객 통지, 접근 차단, 제한된 정보 공유, 공개 보고서는 각각 별도 조치이며 공개가 유일한 법적 대응이었다는 근거도 없습니다. 보고서 서문의 적절한 경우 당국과 정보를 공유했다는 설명 역시 특정 정부가 Moonshot 고객의 자료를 입수했다는 증거가 아닙니다.

공개 보고서는 계속 비공개로 관측하는 것과 다른 이익을 만듭니다. 무단 수집 문제를 고객이 확인할 수 있는 데이터 처리 문제로 바꾸고, 앤트로픽의 서비스 보호 주장을 외부에 전달합니다. 동시에 그 주장을 뒷받침하려면 앤트로픽도 조사 근거와 보존 관행을 설명해야 합니다. 공개의 설득력은 경쟁사를 지목하는 강도보다 양쪽의 데이터 처리를 얼마나 검증할 수 있느냐에 달려 있습니다.

## 함께 보면 좋을 자료

- [Claude API Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking): 추론 표시, 암호화, 정상적인 재사용과 현재 적용 조건을 확인할 문서입니다.
- [상용 제품 데이터 보존 안내](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data): 오용 조사와 보존 예외를 함께 읽을 자료입니다.

## 참고 자료

- [Detecting and countering misuse of AI: September 2026, PDF](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf): Anthropic, 특히 146·148~149·153쪽. 조회일 2026-10-15.
- [보고서 웹판](https://www.anthropic.com/threat-intelligence-report-september-2026): Anthropic, 공개 이유와 사례 설명. 조회일 2026-10-15.
- [Thinking](https://platform.claude.com/docs/en/build-with-claude/thinking): Claude Platform Docs. 조회일 2026-10-15.
- [How long do you store my organization’s data?](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data): Anthropic Privacy Center. 조회일 2026-10-15.
- [Moonshot serves Claude instead of Kimi and collects exchanges for model training](https://news.ycombinator.com/item?id=49656698): Hacker News 토론. 조회일 2026-10-15.
- [Anthropic’s new report has no winners](https://www.reddit.com/r/ClaudeAI/comments/1wdz975/anthropics_new_report_has_no_winners_and_the_part/): Reddit r/ClaudeAI의 개인정보 관련 의견. 조회일 2026-10-15.
