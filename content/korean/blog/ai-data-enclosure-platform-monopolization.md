---
title: "AI 시대의 데이터 폐쇄화(Data Enclosure)와 플랫폼 독점화 동향"
meta_title: ""
description: "네이버 쇼핑 검색 API 종료부터 Reddit 라이선싱, Cloudflare 보상 실험과 영국 CMA 조치까지, AI 데이터 접근권과 플랫폼 경쟁을 구분해 살펴봅니다."
date: 2026-10-15T16:00:00+09:00
lastmod: 2026-10-15T16:00:00+09:00
image: "/images/posts/ai-data-enclosure-platform-monopolization/cover.png"
categories: ["AI"]
tags: ["data-enclosure", "platforms", "competition", "data-licensing", "ai-search", "commerce"]
author: "whackur"
translationKey: "ai-data-enclosure-platform-monopolization"
draft: false
---

네이버 쇼핑 검색 API가 사라졌다는 이야기는 2026년 10월 15일 기준으로 공식 공지에서 확인됩니다. 다만 네이버의 모든 쇼핑 데이터 API가 종료됐다는 뜻은 아닙니다. **상품을 검색하는 API의 종료, 쇼핑 클릭 추이를 보는 API의 이관, 검색 데이터를 AI에 쓰는 행위의 제한**은 서로 다른 변경입니다. 이 셋을 구분해야 외부 개발자가 잃은 기능과 여전히 제공되는 기능을 정확히 설명할 수 있습니다. [쇼핑 검색 종료 공지](https://developers.naver.com/notice/article/32564), [이관 공지](https://developers.naver.com/notice/article/32530), [약관 개정 공지](https://developers.naver.com/notice/article/33400)가 각각 근거입니다.

해외에서도 데이터 접근을 제한하면서 특정 AI 기업에는 계약으로 제공하는 사례가 나타났습니다. Reddit과 Google의 제휴, Stack Overflow의 OverflowAPI, 언론사의 콘텐츠 계약이 여기에 해당합니다. 그렇다고 모든 데이터가 사라지거나 모든 계약이 독점 계약인 것은 아닙니다. 이 글은 2023년 이후의 일곱 사례를 중심으로, 공개된 정보를 누가 어떤 조건으로 다시 사용할 수 있는지 살펴봅니다. 확인일 이후의 정책 변경이나 비공개 계약 조건까지 설명하는 전수조사는 아닙니다.

핵심 판단은 이렇습니다. AI 시대의 데이터 폐쇄화는 공개 페이지의 감소만으로 측정하기 어렵습니다. 사람에게 읽히는 페이지는 남아 있어도 기계가 수집하고, 결합하고, 답변하고, 거래하는 권한은 달라집니다. 경쟁 위험은 그 차이가 대체하기 어려운 데이터와 배포 채널에 겹칠 때 커집니다. 다만 아래 사례만으로 특정 기업의 위법한 독점이 입증되지는 않습니다.

## 공개 여부보다 이용 권한을 먼저 나눠야 합니다

이 글에서 데이터 폐쇄화는 널리 이용하던 데이터의 접근 범위나 재사용 조건이 좁아지고, 운영자가 이용자를 선별하는 현상을 뜻합니다. 법률 용어로 확정된 정의가 아니라 사례를 비교하기 위한 분석 틀입니다. 완전 종료와 유료 제공, 신청 심사, 특정 용도 금지를 한 단어로 뭉치면 중요한 차이가 사라집니다.

| 이용 단계 | 실제로 확인할 권한 | 흔한 오해 |
| --- | --- | --- |
| 수집·조회 | 페이지 크롤링, API 호출, 호출량과 대상 필드 | 브라우저에서 보이면 대량 수집도 가능하다고 생각합니다. |
| 학습 | 사전학습·미세조정·평가에 데이터 사용 | 조회 비용을 냈으니 학습도 허용된다고 생각합니다. |
| 검색·RAG | 검색 증강 생성(Retrieval-Augmented Generation)을 위한 색인·검색·문맥 입력 | 학습을 안 하면 모든 AI 사용 제한을 피한다고 생각합니다. |
| 표시·재배포 | 원문·발췌·요약·출처 링크·저장·내보내기 | 링크만 달면 어떤 형태로든 재배포해도 된다고 생각합니다. |
| 거래·실행 | 장바구니 변경·주문·결제·취소와 사용자 승인 | 상품을 조회하는 권한이 구매 대행 권한까지 포함한다고 생각합니다. |

학습은 모델의 매개변수를 바꾸는 과정이고, RAG는 보통 질의 시점에 외부 정보를 찾아 문맥으로 넣는 방식입니다. 두 방식 모두 데이터를 이용하지만 계약이 허용하는 범위는 다를 수 있습니다. 검색 결과를 가져오는 API를 호출한 뒤 그 결과를 모델에 넣는 제품이라면 조회 권한과 AI 입력 권한을 따로 확인해야 합니다. 네이버의 2026년 약관 개정처럼 ‘학습’보다 넓게 AI 입력과 평가까지 명시하는 경우가 있기 때문입니다.

크롤링 신호도 별도입니다. [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html)는 robots.txt 규칙이 접근 권한을 부여하는 수단이 아니라고 설명합니다. 서버가 요청을 차단하는 인증·방화벽과 크롤러에게 행동을 요청하는 robots.txt는 다릅니다. 허용된 크롤링이 곧 저작권 이용허락이나 학습 허락이라는 결론도 나오지 않습니다. 기술적으로 받아온 사실, 계약상 허용된 목적, 법적으로 인정되는 이용 범위를 각각 검토해야 합니다.

## 네이버에서 실제로 종료된 것과 남아 있는 것

네이버 개발자센터의 [2026년 6월 30일 공지](https://developers.naver.com/notice/article/32564)는 검색의 쇼핑·책·전문자료 API를 종료 대상으로 명시하고 적용일을 2026년 7월 31일로 제시합니다. [6월 29일 등록된 이관 공지](https://developers.naver.com/notice/article/32530)의 현재 본문은 더 구체적입니다. 이 세 검색 API는 NAVER API HUB 이관 대상에서 제외되며, 유예기간 없이 기존 발급 키도 호출할 수 없고 API HUB를 포함한 별도 대체 API도 제공하지 않는다고 적습니다. 이관 공지의 수정일은 8월 10일입니다. 따라서 최초 게시 당시부터 모든 문구가 동일했다고 소급하지는 않습니다.

반대로 Search API의 나머지 이관 대상, Search Trend, Shopping Insight는 다른 일정입니다. 개발자센터의 신규 신청은 2026년 7월 31일부터 중단되고 신규 이용자는 API HUB에서 신청합니다. 기존 신청분은 공지가 정한 유예기간에 따라 2027년 6월 30일까지 개발자센터에서 지원합니다. 쇼핑 검색의 종료일을 쇼핑인사이트 전체 종료일로 옮겨 적으면 잘못된 설명이 됩니다.

| 이름 | 데이터·역할 | 확인된 범위 |
| --- | --- | --- |
| Search의 쇼핑 검색 | 검색어에 맞는 상품명·링크·가격 등 검색 결과 | 2026년 7월 31일 종료 대상. 기존 키도 예외가 없고 API HUB 대체 없음 |
| DataLab의 Shopping Insight | 분야·키워드별 쇼핑 검색 클릭 추이 | API HUB 이관 대상. 기존 신청분은 공지상 2027년 6월 30일까지 유예 |
| Commerce API | 인증된 커머스 연동의 상품·주문·정산 등 | 별도 제품으로 문서와 버전 제공. 전체 쇼핑 검색의 대체 권한을 의미하지 않음 |
| 제휴·가격비교 피드 | 판매자 상품을 플랫폼에 공급하거나 계약에 따라 연동 | 위 종료 공지만으로 개별 계약이나 공급 경로의 종료 여부를 판정할 수 없음 |

이 구분은 이름만의 문제가 아닙니다. [쇼핑인사이트 문서](https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md)는 클릭 추이를 반환하며 최댓값을 100으로 둔 상대 비율을 설명합니다. 이것은 현재 구매 가능한 상품 목록이나 실시간 최저가를 반환하는 기능과 다릅니다. [Commerce API의 현재 문서](https://apicenter.commerce.naver.com/docs/commerce-api/current)와 [인증 문서](https://apicenter.commerce.naver.com/docs/auth)는 상품·주문 등의 업무와 서버 간 인증을 다룹니다. 한 API를 다른 API 이름으로 교체한다고 필요한 데이터가 자동으로 따라오지 않습니다.

혼동을 키우는 사실도 있습니다. 확인일 현재 [옛 쇼핑 검색 레퍼런스](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md)는 여전히 열리며 호출 URL, 응답 필드와 하루 25,000회 한도를 설명합니다. 문서가 남아 있다는 사실은 확인했지만 정상 호출 가능성을 인증해서 시험한 것은 아닙니다. 이 글의 종료 판단은 요청 실패나 메뉴 삭제가 아니라, 기존 키까지 명시한 공식 공지에 근거합니다. 옛 레퍼런스의 한도를 현재 사용할 수 있는 무료 쿼터처럼 소개해서도 안 됩니다.

API가 존재하는지와 AI에 이용할 수 있는지도 구별해야 합니다. 네이버는 [2026년 8월 7일 개정 공지](https://developers.naver.com/notice/article/33400)를 내고 9월 7일부터 검색 데이터를 AI에 입력하거나 학습·개선·평가·노출 등에 활용하는 행위를 금지하는 문구를 적용했습니다. 가공 없는 검색 결과 표시와 출처 링크를 요구하고, 캐싱에는 목적별 예외와 기간을 둡니다. 이는 개발자센터 검색 API 약관의 범위입니다. NAVER API HUB, Commerce API나 별도 계약에 같은 조항이 자동 적용된다고 일반화하지 않습니다.

동시에 네이버는 [2월 26일 쇼핑 AI 에이전트 베타](https://www.navercorp.com/media/pressReleasesDetail?seq=34353)를 발표했고, [9월 17일에는 실시간 배송 정보와 주문 마감 시간을 반영한 추천](https://www.navercorp.com/media/pressReleasesDetail?seq=10034666)을 발표했습니다. 내부 서비스가 상품·리뷰·배송 맥락을 결합하는 방향은 확인됩니다. 외부 상품 검색 경로 축소와 내부 AI 고도화가 같은 시기에 일어난다는 점은 경쟁 분석의 출발점입니다. 그러나 종료 공지가 AI 경쟁 차단을 이유로 제시하지는 않습니다. 두 사건의 시간적 인접성만으로 원인을 확정하지 않습니다.

국내 동향을 설명할 때도 이 증거 범위를 지켜야 합니다. 네이버의 구체적인 공지를 카카오·다음이나 국내 플랫폼 전체의 API 종료로 확대할 근거는 없습니다. 판매자 업무 자동화가 계속 열려 있는지, 외부 비교 서비스가 접근하던 경로가 줄었는지를 나눠 보는 편이 ‘국내 플랫폼은 모두 닫혔다’는 문장보다 정확합니다.

## Reddit은 접근 제한과 제휴 제공을 함께 운영했습니다

Reddit의 [2023년 API 변경 설명](https://redditinc.com/news/apifacts)은 대량 이용 비용과 무료 이용 범위를 구분합니다. 7월 1일 적용된 호출 제한뿐 아니라 조정 도구와 접근성 앱 등에 대한 예외도 설명합니다. 정책 변경을 ‘모든 API의 완전 폐쇄’라고 부르면 남아 있던 용도와 예외를 놓칩니다. 이 문서는 당시 정책의 근거이며 현재 모든 신청자의 권리를 보증하는 문서는 아닙니다.

이후 [2024년 2월 22일 Google 제휴](https://redditinc.com/news/reddit-and-google-expand-partnership)는 구조화된 Data API 접근과 모델 학습 지원을 설명했습니다. [5월 16일 OpenAI 제휴](https://redditinc.com/news/reddit-and-oai-partner)는 실시간 콘텐츠를 ChatGPT 등에 제공하고 Reddit의 AI 기능 개발에도 협력한다고 발표했습니다. 데이터가 외부에서 사라진 것이 아니라 승인된 경로로 계속 공급된 사례입니다. 두 발표만으로 어느 한 구매자에게 배타적 권리를 줬다고 판단할 수는 없습니다.

경쟁상 확인할 지점은 계약의 존재보다 진입 조건입니다. 작은 개발자도 같은 최신성·범위·삭제 반영을 갖춘 데이터를 구매할 수 있는지, 가격과 심사가 공개돼 있는지에 따라 영향이 달라집니다. 공개된 [현재 Data API 약관](https://redditinc.com/policies/data-api-terms)은 별도로 확인해야 하며, 2024년 제휴 발표의 무료 이용 설명만으로 지금의 상업적 이용을 설계해서는 안 됩니다. 공개 발표에서 확인되지 않은 계약액이나 배타 조항은 여기서 추정하지 않습니다.

## X는 API가 남아 있어도 접근 비용이 달라지는 사례입니다

[X의 현재 가격 문서](https://docs.x.com/x-api/getting-started/pricing)는 구독 대신 선불 크레딧을 사용하는 종량제 API를 설명합니다. 일반 게시물 읽기는 반환 리소스당 0.005달러, 조건을 충족하는 자기 데이터 읽기는 0.001달러로 표시합니다. 일반 게시물 10만 개를 각각 한 번 읽는다고 단순 계산하면 500달러입니다. 이는 문서 단가를 곱한 예시이며 실제 청구서나 연구 프로젝트의 비용 측정값은 아닙니다. 중복 과금 처리와 대상 엔드포인트도 계산에 영향을 줍니다.

소규모 계정 관리 도구에는 낮은 초기 지출이 장점일 수 있습니다. 반면 대규모 관측 연구나 여러 이용자를 비교하는 제품은 읽기량에 따라 비용이 증가합니다. 비용의 크기와 정당성은 구분해야 합니다. 운영 비용을 받는다는 사실만으로 차별이 입증되지는 않지만, 어떤 제품이 경제적으로 가능한지는 달라집니다. 현행 [개발자 정책](https://developer.x.com/en/developer-terms/agreement-and-policy)도 용도 신고와 데이터 처리 조건을 요구합니다. 돈을 내고 읽는 권한을 무제한 재배포나 AI 학습 허가로 확장해서는 안 됩니다.

## Stack Overflow에서는 콘텐츠 권리와 전달 서비스가 겹칩니다

Stack Overflow는 [2024년 5월 6일 OpenAI 제휴](https://stackoverflow.co/company/press/archive/openai-partnership)를 발표했습니다. OverflowAPI를 이용해 기술 지식을 제공하고 ChatGPT 안에서 출처를 표시하며 모델 개선에도 협력한다는 내용입니다. 유료 전달 경로가 생겼다는 사실과 공개 답변의 기존 라이선스가 없어진다는 주장은 다릅니다.

[공개 기여물의 라이선스 안내](https://stackoverflow.com/help/licensing)는 게시 시기별 CC BY-SA 버전을 명시합니다. 플랫폼이 글을 호스팅한다고 모든 작성자의 저작권을 소유한다고 볼 수는 없습니다. 또한 API 계약이 제공하는 최신 데이터·정리·접속 안정성과 콘텐츠 라이선스에 따라 이용자가 이미 보유한 권한을 같은 것으로 취급하면 안 됩니다. 특정 학습 방식이 라이선스 의무를 충족하는지까지 이 제휴 발표가 판정해 주지는 않습니다.

이 구분은 창작자 보상 논의에도 중요합니다. 플랫폼이 계약 수입을 얻는 것과 기여자가 이름을 인정받거나 수익을 배분받는 것은 별개의 설계입니다. 출처 표시가 약속돼 있다면 실제 답변에서 원문과 작성자를 얼마나 찾기 쉬운지 확인해야 합니다. 계약 발표 자체를 공동체 전체의 동의나 보상 완료로 받아들이기는 어렵습니다.

## 언론사 계약은 선택적 개방의 또 다른 형태입니다

[News Corp의 2024년 5월 22일 발표](https://investors.newscorp.com/news-releases/news-release-details/news-corp-and-openai-sign-landmark-multi-year-global-partnership)는 OpenAI에 주요 매체의 현재·과거 콘텐츠 접근과 사용자 질문에 대한 표시를 허용하는 다년 계약을 설명합니다. 다른 사업의 콘텐츠는 포함하지 않는다고도 명시합니다. 독자는 이 계약이 어떤 콘텐츠와 어떤 제품을 잇는지부터 읽어야 합니다. 회사가 가진 모든 저작물의 포괄 양도나 모든 AI 서비스에 대한 개방으로 해석할 수 없습니다.

이런 계약에는 상반된 효과가 가능합니다. 취재 비용을 지불하는 수입원이 생기면 원문 생산을 유지하는 데 도움이 됩니다. 동시에 대형 매체와 대형 AI 회사만 협상할 수 있다면 작은 매체·검색 서비스는 같은 경로에 들어가기 어렵습니다. 어느 효과가 더 큰지는 실제 계약 범위, 참여 가능한 사업자 수, 독자 유입과 지급액으로 검증할 문제입니다. 발표가 공개하지 않은 금액과 배타성, 제휴 후 원문 트래픽 효과는 확인된 사실로 적지 않습니다.

## Cloudflare는 차단 뒤의 거래 조건을 실험합니다

Cloudflare는 [2025년 7월 1일 Pay Per Crawl](https://blog.cloudflare.com/introducing-pay-per-crawl/)을 비공개 베타로 발표했습니다. 콘텐츠 소유자가 크롤러의 접근에 가격을 붙이고 HTTP 402로 결제를 요구하는 방식입니다. 이는 robots.txt의 협조 요청과 달리 요청 처리에 과금 조건을 연결하려는 구현입니다. [현재 문서](https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/)도 베타로 표시합니다.

최신 변화는 [2026년 9월 30일 Pay Per Use 베타](https://blog.cloudflare.com/pay-per-use/)입니다. 구매자가 유료로 셀 이용 행위와 가격을 제안하고, 게시자가 참여 여부를 선택하며, 구매자의 사용 보고를 바탕으로 정산합니다. 페이지를 가져올 때마다 접근료를 부과하는 Pay Per Crawl과 달리, Pay Per Use는 정의된 후속 이용 행위에 과금합니다. 프로그램 조건에 학습 제한도 포함될 수 있습니다. 단순히 크롤링 한 번의 대금을 냈다고 모든 후속 이용이 허용되는 모델은 아닙니다.

이 접근은 작은 게시자에게 개별 계약 협상의 비용을 줄여 줄 가능성이 있습니다. 반대로 구매자의 자기 보고를 신뢰하고 검증하는 문제가 남습니다. 공식 발표는 사용량이 자기 보고라고 명시합니다. 따라서 베타 출시를 창작자 보상 문제의 해결이나 시장 표준 정착으로 소개할 단계는 아닙니다. 과금 단위를 정해 주는 중개자 자체에 의존하게 되는지도 살펴볼 필요가 있습니다.

## Google 검색과 AI 이용을 분리하려는 규제

Google의 [크롤러 문서](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers)는 Google-Extended를 Gemini 계열의 학습·일부 grounding 이용을 관리하는 토큰으로 설명하며 Google 검색 포함 여부나 순위에는 영향을 주지 않는다고 명시합니다. 여기서 grounding은 답변 시 외부 근거를 제공하는 이용입니다. 이 토큰의 범위를 모든 Google AI 제품의 일괄 거부 수단으로 확대해서는 안 됩니다.

영국 CMA는 [2026년 6월 3일 Google에 게시자 관련 행위 요건을 부과](https://www.gov.uk/find-digital-markets-measures/google-search-publisher-conduct-requirement)했습니다. 검색 생성형 AI의 콘텐츠 이용 통제, 설명, 이용자 참여 지표와 출처 표시가 포함됩니다. [공식 발표](https://www.gov.uk/government/news/cma-secures-fairer-deal-for-publishers-and-improves-google-search-services-in-uk)는 이행에 9개월을 부여했다고 설명합니다. 10월 현재 모든 통제가 전 세계에서 완전히 구현됐다고 쓰면 안 됩니다. 결정과 실제 이행은 별도 확인 대상입니다.

정책의 쟁점은 게시자가 검색에서 발견될 기회를 유지하면서 AI 이용 조건을 선택할 수 있느냐입니다. 검색 유입을 포기해야만 AI를 거부할 수 있다면 형식적인 선택권의 실효성이 약해질 수 있습니다. 다만 CMA는 전략적 시장 지위(SMS) 지정 자체가 반경쟁적 행위의 증거는 아니라고 명시합니다. 영국의 특정 규제 조치를 모든 나라의 독점 위법 판결로 옮겨 설명하지 않습니다.

## 데이터와 배포가 결합할 때 생기는 경쟁 위험

지금까지의 사례가 보여 주는 공통점은 데이터의 용도별 조건을 운영자가 정한다는 점입니다. 여기서부터는 관측 사실을 바탕으로 한 경제적 해석입니다. 모델이 원문을 대신 답하면 이용자는 시간을 아끼지만 게시자는 광고 노출·구독 전환·판매 기회를 잃을 수 있습니다. 반대로 출처 링크가 새로운 독자를 데려오거나 계약 수입이 손실을 상쇄할 수도 있습니다. 어느 쪽인지 알려면 방문 감소만 보지 말고 유료 이용 수입과 독자의 질도 함께 봐야 합니다.

플랫폼의 비용과 책임도 실제 판단 항목입니다. 데이터 제공에는 서버 비용, 대량 호출 대응, 스팸 방지, 개인정보 보호와 삭제 반영이 필요합니다. 무제한 무료 수집이 유일하게 공정한 기준이라고 보기는 어렵습니다. 문제는 같은 비용과 위험을 가진 이용자에게 다른 조건을 적용하는지, 자사와 제휴사만 필요한 품질을 얻는지입니다. 안전·비용이라는 이유와 경쟁을 제한하는 효과는 동시에 존재할 수 있으므로 한쪽 설명만으로 판단을 끝내서는 안 됩니다.

![콘텐츠에서 용도별 접근 조건을 거쳐 자사 서비스와 승인된 외부 이용자로 이어지고, 서비스 상호작용이 새 데이터를 만드는 개념도](/images/posts/ai-data-enclosure-platform-monopolization/selective-access.svg)

*작성: HakHub. 네이버 공지, Reddit·Stack Overflow 제휴, Cloudflare 과금 방식과 CMA 문서를 토대로 재구성한 개념도입니다. 화살표는 가능한 관계를 설명하며 시장점유율이나 효과 크기를 측정한 데이터가 아닙니다. 자사 이용도 권리·개인정보 조건을 충족해야 합니다.*

예를 들어 쇼핑 플랫폼이 상품 정보와 구매 맥락을 보유하고 추천 서비스를 배포한다고 가정해 봅니다. 더 유용한 추천이 이용자를 모으고, 그 이용자의 선택이 새로운 추천 신호를 만듭니다. 외부 서비스가 동일한 최신 상품이나 배송 조건에 접근하지 못하면 가격 비교나 추천 성능에서 불리해질 수 있습니다. 데이터 → AI 품질·배포 → 이용자 상호작용 → 새 데이터라는 되먹임입니다. 도식은 이 가능성을 보여 주며 특정 기업이 이미 이 효과를 달성했다는 실증은 아닙니다.

되먹임이 항상 강해지는 것도 아닙니다. 데이터가 오래되거나 중복되고, 좋은 대체 공급원이 있거나, 사용자가 여러 서비스를 병행하면 효과는 약해집니다. 잘못된 추천에서 얻은 행동을 학습하면 오류를 강화할 수도 있습니다. 데이터 양만으로 품질을 단정하거나, 한 번 확보한 우위가 영구적인 독점으로 이어진다고 가정할 이유는 없습니다.

외부 개발자의 전환 비용은 API 호출 코드를 바꾸는 시간보다 넓습니다. 상품 식별자를 다시 맞추고, 응답 누락을 처리하고, 저장해 둔 데이터를 정리하고, 계약과 출처 표시를 바꿔야 할 수 있습니다. 연구자는 표본 수집 경로가 바뀌면 시계열의 단절도 설명해야 합니다. 같은 질문에 대한 이전·이후 결과 차이가 사회 현상 때문인지 데이터 접근 조건 때문인지 분리하기 어려워집니다. 이는 가능한 영향 경로이며, 이 글에서 모든 개발자나 연구자의 피해 규모를 측정한 것은 아닙니다.

배타성도 계약별로 판단해야 합니다. 비배타 계약은 여러 AI 회사가 같은 자료를 이용할 여지를 남깁니다. 배타 계약은 계약 대상·기간·지역·이용 목적에 따라 특정 경쟁자의 접근을 제한할 수 있습니다. 그러나 비배타 계약이라도 큰 최소 구매액과 불투명한 심사 때문에 작은 회사가 들어가기 어렵다면 실질적인 접근 격차는 남습니다. 반대로 규모별 가격과 연구 예외가 충분하면 유료화가 지속 가능한 외부 공급을 늘릴 수도 있습니다.

여기서 ‘내부용’과 ‘내수용’을 구분할 필요도 있습니다. 플랫폼 내부 서비스에만 데이터를 쓰는 정책은 기업 경계의 문제입니다. 데이터 현지화나 소버린 AI는 어느 국가의 인프라·통제·관할에 의존하는지의 문제입니다. 국내 회사가 해외 사업자에게 비배타적으로 제공할 수도 있고 해외 회사가 국내 서버에서 처리해도 외부 재사용을 막을 수 있습니다. 데이터가 국내에 있다는 사실만으로 개발자에게 열려 있거나 닫혀 있다고 결론 내릴 수 없습니다.

## 커뮤니티는 보상과 새로운 중개 권력을 함께 걱정합니다

[2025년 7월 1일 Hacker News 토론](https://news.ycombinator.com/item?id=44432385)에서 [suyash](https://news.ycombinator.com/item?id=44432533)는 봇 트래픽 문제를 다루는 방향을 환영하면서도 권한·결제를 위한 공개 프로토콜을 선호한다고 적었습니다. [Toritori12](https://news.ycombinator.com/item?id=44432530)는 취지에는 동의하지만 우회 수집 비용과 최종 이용자에게 전가될 비용을 걱정했습니다. 지지와 비판이 같은 댓글 안에 있습니다. 이는 익명 이용자의 의견과 경험이며 전체 게시자의 대표 표본이나 우회 가능성의 실험 결과가 아닙니다.

독립 블로그 [developerWithACat의 2025년 7월 30일 글](https://developerwithacat.com/blog/202507/cloudflare-pay-per-crawl/)도 차단의 한계와 가격 합의의 어려움을 지적했습니다. 이 비판을 2026년 사용량 과금 베타의 실패 증거로 소급해서 사용할 수는 없습니다. 오히려 서로 다른 과금 방식에서 무엇을 검증해야 하는지 보여 줍니다. 크롤링 횟수, 실제 답변 이용, 원문 유입과 보상액은 서로 다른 측정값입니다.

## 개방 경로와 반증 가능한 지표

폐쇄화가 유일한 방향이라는 주장에는 반례가 있습니다. [Wikimedia의 공개 덤프](https://meta.wikimedia.org/wiki/Data_dumps)는 연구·보존·오프라인 이용을 위한 내려받기와 재사용 경로를 제공합니다. 라이선스와 덤프의 완전성·최신성 한계는 따라오지만 개별 대형 구매자와 협상해야만 이용할 수 있는 구조는 아닙니다. Stack Overflow의 공개 기여물 라이선스 역시 유료 전달 서비스와 별도로 살펴볼 재사용 조건입니다.

실무 대안으로는 권리를 확보한 자체 문서, 판매자와 직접 맺은 공급 계약, 적합한 공개 데이터와 여러 공급원을 조합하는 설계가 있습니다. 다만 공개 덤프가 오늘의 배송 가능성이나 새로 삭제된 게시물까지 대신해 주지는 않습니다. 공개 가중치 모델을 선택해도 입력 데이터의 권리가 자동으로 생기지 않습니다. 모델 선택과 데이터 조달을 분리해서 설계하는 편이 안전합니다.

이 글의 경쟁 위험 가설을 검증하려면 다음 지표를 추적할 수 있습니다. 값이 나빠질 때만 모으는 방식으로는 가설을 반증할 수 없습니다.

- 같은 용도·최신성·호출량을 기준으로 신규 외부 개발자에게 실제 발급되는 권한과 단가를 비교합니다. 표준 가격과 신청 경로가 넓어지면 접근 집중 가설은 약해집니다.
- 내부 제품과 외부 API의 필드, 갱신 지연, 누락률을 비교합니다. 개인정보·보안상 필요한 차이를 제외하고도 격차가 커지는지 봅니다.
- 출처별 방문·구독·매출과 라이선스 수입을 함께 관찰합니다. 통제 집단과 계절성을 고려한 뒤에도 순수입이 유지된다면 단순한 수익 대체 주장은 수정해야 합니다.
- 공급자 변경에 필요한 시간과 데이터 이식 범위를 기록합니다. 여러 서비스 병행 이용과 대체 공급이 쉬워지면 고착 위험은 줄어듭니다.
- 소규모 구매자·독립 연구자의 승인율과 계약 소요 기간을 확인합니다. 제휴 건수만 늘고 진입 가능한 사업자는 줄어드는지 구분합니다.
- 게시자의 AI 거부 선택이 일반 검색 발견성에 미치는 영향과 실제 출처 링크를 점검합니다. 선언된 통제와 구현된 선택권 사이의 차이를 측정합니다.

## 제품을 만들기 전의 접근권 점검표

API 목록보다 먼저 데이터의 출처와 목적을 한 줄씩 적는 것이 좋습니다. 예를 들어 ‘상품 결과 조회 → 순위 재구성 → 모델 문맥 입력 → 추천 표시 → 주문 실행’으로 흐름을 적으면 하나의 호출 성공으로 확인할 수 없는 권한이 드러납니다. 이 점검표는 개별 계약의 법적 해석을 대신하지 않고, 검토할 문서와 제품 동작을 연결합니다. 특히 사람이 검색 결과를 읽고 판단하는 화면과, 모델이 결과를 재구성해 추천하는 화면은 같은 API를 호출해도 서로 다른 검토가 필요합니다.

제품 설계를 더 구체적으로 보면 권한 차이가 드러납니다. 어떤 공급자가 상품명과 가격의 화면 표시를 허용하되 모델 입력과 장기 저장은 허용하지 않는다고 가정하겠습니다. 개발자는 검색 결과를 보여 주는 기능을 만들 수 있어도, 같은 응답을 임베딩해 추천용 색인으로 보관하는 기능은 별도로 검토해야 합니다. 임베딩이 원문과 다른 형식이라는 사실만으로 계약상 제한이 사라지지는 않습니다. 공급자가 요약을 허용하더라도 재판매나 주문 실행까지 허용했다고 해석할 근거는 되지 않습니다. 이 예시는 특정 사업자의 실제 계약을 요약한 것이 아니라 검토 항목을 나누기 위한 가정입니다.

평가 데이터에도 같은 구분이 필요합니다. 추천 품질을 매달 비교하려고 응답과 정답을 저장하면, 서비스 화면에는 잠깐 표시한 정보가 평가 저장소에는 오래 남을 수 있습니다. 삭제 요청이나 캐시 만료를 사용자 화면에만 반영하면 이런 복사본을 놓칩니다. 데이터가 어느 단계에서 복사되고 어떤 목적에 쓰이는지 기록해야 하는 이유입니다. 이용 목적을 정리한 문서에는 운영 데이터뿐 아니라 로그, 검색 색인, 평가 표본의 보관 위치와 처리 담당자도 연결하는 편이 좋습니다. 이런 비용까지 포함해야 새 공급자로 전환할 때 필요한 작업을 과소평가하지 않습니다.

| 확인 항목 | 남겨 둘 근거 |
| --- | --- |
| 제공 상태 | 공지 게시일·수정일·시행일, 신규 신청과 기존 키의 차이 |
| 데이터 범위 | 필드·최신성·누락 처리, 조회와 공급 피드의 방향 |
| 목적별 이용 | 학습·평가·RAG·표시·내보내기에 각각 적용되는 조건 |
| 보관·권리 | 캐시 기간, 삭제 반영, 출처·기여자 표시, 재배포 조건 |
| 거래 권한 | 사용자 승인, 판매자 권한, 주문·결제·취소의 책임 범위 |
| 비용·대체 경로 | 실제 반환량 기준 비용, 상한, 계약 변경 통지와 전환 계획 |

운영 중에는 API 오류를 정책 종료와 즉시 연결하지 말고 상태 코드, 인증 만료, 호출량과 공식 공지를 대조해야 합니다. 문서가 열리는 사실도 서비스의 정상 제공을 보증하지 않습니다. 네이버 사례처럼 종료 공지와 옛 레퍼런스가 함께 남을 수 있기 때문입니다. 제공자의 설명이 충돌한다면 더 구체적인 대상·날짜가 있는 공지를 기록하고, 확인되지 않은 범위는 확인되지 않았다고 남기는 것이 맞습니다.

현재 근거가 뒷받침하는 결론은 ‘인터넷 데이터가 모두 사라진다’가 아닙니다. 일부 범용 경로는 종료되고, 다른 경로는 이관되며, 특정 목적과 구매자를 위한 계약은 새로 생깁니다. 경쟁에 중요한 것은 데이터가 보이는지뿐 아니라 경쟁자가 필요한 권한을 예측 가능한 조건으로 얻는지입니다. 그 조건과 실제 이용 결과를 함께 기록해야 폐쇄화의 정도와 보상의 효과를 구분할 수 있습니다.

## 함께 보면 좋을 자료

- [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html): robots.txt가 수행하는 역할과 보안 수단의 차이를 확인할 수 있습니다.
- [Wikimedia Data dumps](https://meta.wikimedia.org/wiki/Data_dumps): 계약형 데이터 공급과 비교할 공개 재사용 경로입니다.
- [Google 게시자 행위 요건](https://www.gov.uk/find-digital-markets-measures/google-search-publisher-conduct-requirement): 생성형 AI 이용 통제와 투명성 요구를 살펴볼 수 있습니다.

## 참고 자료

모든 링크의 조회일은 2026년 10월 15일입니다. 기업 발표의 제품 효과와 의도는 해당 기업의 설명이며, 비공개 계약 조건은 확인하지 않았습니다.

- [Naver: Shopping, Book and Professional Document Search termination](https://developers.naver.com/notice/article/32564): 2026-06-30; modified 2026-07-16; 조회일 2026-10-15.
- [Naver: API termination and NAVER API HUB migration](https://developers.naver.com/notice/article/32530): 2026-06-29; modified 2026-08-10; 조회일 2026-10-15.
- [Naver: Search API terms amendment](https://developers.naver.com/notice/article/33400): 2026-08-07; effective 2026-09-07; 조회일 2026-10-15.
- [Naver: legacy Shopping Search reference](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md): Undated live reference; 조회일 2026-10-15.
- [Naver: Shopping Insight reference](https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md): Undated live reference; 조회일 2026-10-15.
- [Naver: Commerce API reference](https://apicenter.commerce.naver.com/docs/commerce-api/current): 2.90.1 listed 2026-10-07; 조회일 2026-10-15.
- [Naver: Commerce API authentication](https://apicenter.commerce.naver.com/docs/auth): Live reference; 조회일 2026-10-15.
- [Naver: shopping AI agent beta](https://www.navercorp.com/media/pressReleasesDetail?seq=34353): 2026-02-26; 조회일 2026-10-15.
- [Naver: real-time delivery recommendations](https://www.navercorp.com/media/pressReleasesDetail?seq=10034666): 2026-09-17; 조회일 2026-10-15.
- [Reddit: facts about 2023 API updates](https://redditinc.com/news/apifacts): 2023-06-15; updated 2023-06-30; 조회일 2026-10-15.
- [Reddit: expanded Google partnership](https://redditinc.com/news/reddit-and-google-expand-partnership): 2024-02-22; 조회일 2026-10-15.
- [Reddit: OpenAI partnership](https://redditinc.com/news/reddit-and-oai-partner): 2024-05-16; 조회일 2026-10-15.
- [Reddit: current Data API Terms](https://redditinc.com/policies/data-api-terms): Live terms; 조회일 2026-10-15.
- [X: pay-per-usage pricing](https://docs.x.com/x-api/getting-started/pricing): Live pricing; 조회일 2026-10-15.
- [X: developer policy](https://developer.x.com/en/developer-terms/agreement-and-policy): Live policy; 조회일 2026-10-15.
- [Stack Overflow: OpenAI partnership](https://stackoverflow.co/company/press/archive/openai-partnership): 2024-05-06; 조회일 2026-10-15.
- [Stack Overflow: public contribution licenses](https://stackoverflow.com/help/licensing): Live help; 조회일 2026-10-15.
- [News Corp: OpenAI agreement](https://investors.newscorp.com/news-releases/news-release-details/news-corp-and-openai-sign-landmark-multi-year-global-partnership): 2024-05-22; 조회일 2026-10-15.
- [Cloudflare: introducing Pay Per Crawl](https://blog.cloudflare.com/introducing-pay-per-crawl/): 2025-07-01; 조회일 2026-10-15.
- [Cloudflare: Pay Per Crawl documentation](https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/): Index last updated 2026-04-23; 조회일 2026-10-15.
- [Cloudflare: Pay Per Use beta](https://blog.cloudflare.com/pay-per-use/): 2026-09-30; 조회일 2026-10-15.
- [Google: common crawlers and Google-Extended](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers): Last updated 2026-07-14; 조회일 2026-10-15.
- [CMA: Google publisher conduct requirement](https://www.gov.uk/find-digital-markets-measures/google-search-publisher-conduct-requirement): 2026-06-03; page updated 2026-08-04; 조회일 2026-10-15.
- [CMA: publisher requirements announcement](https://www.gov.uk/government/news/cma-secures-fairer-deal-for-publishers-and-improves-google-search-services-in-uk): 2026-06-03; 조회일 2026-10-15.
- [IETF: RFC 9309 Robots Exclusion Protocol](https://www.rfc-editor.org/rfc/rfc9309.html): 2022-09, background standard; 조회일 2026-10-15.
- [Wikimedia: Data dumps](https://meta.wikimedia.org/wiki/Data_dumps): Live project documentation; modified 2026-07-23; 조회일 2026-10-15.
- [Hacker News: Cloudflare Pay Per Crawl discussion](https://news.ycombinator.com/item?id=44432385): 2025-07-01; 조회일 2026-10-15.
- [Hacker News: suyash on permissions and payment](https://news.ycombinator.com/item?id=44432533): 2025-07-01T10:46:06Z; 조회일 2026-10-15.
- [Hacker News: Toritori12 on costs](https://news.ycombinator.com/item?id=44432530): 2025-07-01T10:45:45Z; 조회일 2026-10-15.
- [developerWithACat: critique of Pay Per Crawl](https://developerwithacat.com/blog/202507/cloudflare-pay-per-crawl/): 2025-07-30; 조회일 2026-10-15.
