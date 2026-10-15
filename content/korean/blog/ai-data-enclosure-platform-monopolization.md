---
title: "AI 시대의 데이터 폐쇄화(Data Enclosure)와 플랫폼 독점화 동향"
meta_title: ""
description: "네이버 쇼핑 검색 API 종료와 Reddit·X·Cloudflare 사례로 데이터 접근의 종료, 용도 제한, 계약과 과금이 플랫폼 경쟁에 미치는 영향을 살펴봅니다."
date: 2026-10-15T16:00:00+09:00
lastmod: 2026-10-15T17:46:01+09:00
image: "/images/posts/ai-data-enclosure-platform-monopolization/cover.png"
categories: ["AI"]
tags: ["data-enclosure", "platforms", "competition", "data-licensing", "ai-search", "commerce"]
author: "whackur"
translationKey: "ai-data-enclosure-platform-monopolization"
draft: false
---

**AI 시대의 데이터 폐쇄화는 누가 어떤 목적으로 데이터를 다시 쓸 수 있는지를 플랫폼이 정하는 문제입니다.** API를 끝내는 곳도 있지만, 특정 AI 기업과 계약하거나 사용량에 따라 요금을 받는 곳도 있습니다. 아래 사례들은 접근 조건의 재편을 보여 줍니다. 이것만으로 특정 기업의 독점이나 위법 행위가 입증되지는 않습니다.

| 사례 | 확인된 조치 | 구분할 점 |
| --- | --- | --- |
| [네이버](https://developers.naver.com/notice/article/32564) | 2026년 7월 31일 쇼핑·책·전문자료 검색 API 종료 | 쇼핑 관련 API 전체의 종료는 아님 |
| [Reddit](https://redditinc.com/news/reddit-and-google-expand-partnership) | Google 등에 계약형 데이터 제공 | 제휴는 모든 개발자에게 같은 권한을 주는 개방과 다름 |
| [X](https://docs.x.com/x-api/getting-started/pricing) | API 종량제 운영 | 접근 비용과 이용 목적의 허용 범위는 별개 |
| [Cloudflare](https://blog.cloudflare.com/pay-per-use/) | 크롤링 접근료에 이어 후속 이용 과금 실험 | Pay Per Use는 베타이며 구매자가 사용을 보고 |

경쟁에 중요한 것은 **새로운 사업자도 필요한 최신 데이터와 이용 권한을 감당할 만한 조건으로 확보할 수 있느냐**입니다. 같은 데이터라도 화면에 표시하는 권한, 모델을 학습시키는 권한, 답변 생성에 쓰는 권한은 다를 수 있습니다.

## 네이버는 쇼핑 검색을 종료하고 다른 API는 이관했습니다

네이버의 [종료 공지](https://developers.naver.com/notice/article/32564)는 쇼핑·책·전문자료 검색 API의 종료일을 2026년 7월 31일로 명시합니다. [이관 공지](https://developers.naver.com/notice/article/32530)는 이 세 API에 유예기간이 없고 기존 키도 호출할 수 없으며, NAVER API HUB를 포함한 대체 API를 제공하지 않는다고 설명합니다.

이름에 ‘쇼핑’이 들어가는 API가 모두 같은 기능을 하는 것은 아닙니다.

| 구분 | 제공하는 기능 | 종료·이관 범위 |
| --- | --- | --- |
| [쇼핑 검색](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md) | 검색어에 맞는 상품 검색 결과 | 종료 대상 |
| [쇼핑인사이트](https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md) | 분야·키워드별 검색 클릭 추이 | API HUB 이관 대상 |
| [Commerce API](https://apicenter.commerce.naver.com/docs/commerce-api/current) | 상품·주문·정산 등 커머스 업무 | 별도 API로 문서 제공 |

나머지 이관 대상 검색 API와 검색어 트렌드, 쇼핑인사이트는 개발자센터의 신규 신청이 2026년 7월 31일부터 중단됐습니다. 기존 신청분은 2027년 6월 30일까지 지원한다는 일정입니다. 따라서 쇼핑인사이트 이관을 상품 검색의 대체 경로로 읽으면 안 됩니다. 별도 제휴·공급 계약의 상태도 이 공지만으로 판정할 수 없습니다. [이관 공지](https://developers.naver.com/notice/article/32530)

이용 목적에도 별도 변화가 있었습니다. [9월 7일 시행된 검색 API 약관 개정](https://developers.naver.com/notice/article/33400)은 검색 데이터를 AI 입력·학습·개선·평가·노출 등에 활용하는 행위를 금지합니다. 모델 학습을 하지 않고 답변 생성에만 쓰더라도 ‘AI 입력’ 제한을 따로 봐야 합니다. 이 조항이 API HUB나 Commerce API, 별도 계약에 자동 적용된다고 일반화할 근거는 없습니다.

확인된 국내 사례는 특정 상품 검색 경로의 종료입니다. 종료 공지는 AI 경쟁을 원인으로 제시하지 않았으므로, 자사 AI를 보호하려고 닫았다고 단정할 수는 없습니다.

## Reddit은 승인과 제휴로 외부 제공 범위를 정합니다

Reddit의 [현행 Data API 약관](https://redditinc.com/policies/data-api-terms)은 상업적 이용 등에 별도 계약을 요구합니다. 사용자 콘텐츠의 소유자는 사용자이며, 일반 API 이용허락이 권리자의 명시적 허락 없는 모델 학습까지 포함하지 않는다고도 명시합니다.

외부 AI 기업을 위한 제공 경로는 따로 있습니다. [2024년 2월 22일 Google 제휴 발표](https://redditinc.com/news/reddit-and-google-expand-partnership)는 구조화된 데이터 접근과 콘텐츠 표시, 모델 학습 지원을 설명했습니다. [같은 해 5월 16일 OpenAI 제휴](https://redditinc.com/news/reddit-and-oai-partner)는 실시간 Data API 콘텐츠를 ChatGPT 등에 제공한다고 밝혔습니다.

이는 이용자와 목적을 정해 데이터를 제공하는 사례입니다. 공개 발표는 이 계약들이 배타적이라거나 같은 조건으로 누구나 구매할 수 있다고 말하지 않습니다. 제휴가 늘어나는 것과 신규 사업자의 접근성이 넓어지는 것은 따로 판단해야 합니다.

## X는 접근량에 가격을 붙입니다

2026년 10월 15일 확인한 [X의 가격 문서](https://docs.x.com/x-api/getting-started/pricing)는 선불 크레딧을 사용하는 종량제를 안내합니다. 일반 게시물 읽기는 반환 리소스당 0.005달러, 요건을 충족하는 자기 데이터 조회인 Owned Reads는 0.001달러입니다. 같은 API에서도 조회 대상에 따라 비용이 달라집니다.

이 구조에서는 적은 양을 읽는 도구와 대규모 데이터를 수집하는 서비스의 부담이 달라질 수 있습니다. 유료화 자체가 불공정하다는 뜻은 아니지만, 데이터 확보 비용이 제품의 가능 범위를 바꿉니다. [개발자 정책](https://docs.x.com/developer-terms/policy)도 승인된 용도와 콘텐츠 처리 규칙의 준수를 요구하므로, 요금을 냈다는 사실만으로 모든 재사용 권한이 생기지는 않습니다.

## Cloudflare는 접근과 실제 이용을 나눠 과금합니다

Cloudflare는 [2025년 7월 1일 Pay Per Crawl을 비공개 베타로 발표](https://blog.cloudflare.com/introducing-pay-per-crawl/)했습니다. 사이트 운영자가 크롤러를 허용하거나 차단하고, 요청마다 가격을 붙이는 방식입니다. HTTP 402 응답으로 결제를 요구할 수 있으며, [현재 문서](https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/)도 베타로 표시합니다.

[2026년 9월 30일 발표한 Pay Per Use](https://blog.cloudflare.com/pay-per-use/)는 후속 이용을 과금 단위로 삼는 베타입니다. AI 기업이 유료로 셀 이용 행위와 가격을 제안하고, 게시자가 참여 여부를 선택합니다. 구매자가 사용을 보고하면 Cloudflare가 요금 청구와 지급을 처리합니다. 프로그램 조건에는 학습 제한이 포함될 수 있습니다.

개별 계약을 맺기 어려운 게시자에게는 거래 절차를 줄일 가능성이 있습니다. 다만 사용량은 구매자의 자기 보고에 의존합니다. 베타 발표만으로 보상이 충분해졌거나 상업적으로 정착했다고 판단할 수는 없습니다. 접근료를 받는 것과 실제 콘텐츠 이용에 대가를 지급하는 것 사이에는 여전히 검증할 차이가 남습니다.

## 접근 변화는 네 가지로 구분할 수 있습니다

사례를 비교하면 같은 ‘폐쇄화’ 안에서도 외부 서비스가 부딪히는 조건은 다릅니다.

- **종료:** 기존 조회 경로가 없어집니다. 다른 목적의 API가 남아 있어도 같은 기능을 대신하지는 못합니다.
- **용도 제한:** 데이터 조회는 허용해도 AI 입력이나 학습 같은 후속 이용은 제한합니다.
- **선택적 계약:** 특정 상대와 목적에 맞춰 데이터를 제공합니다. 계약 범위와 신규 참여 조건이 중요합니다.
- **사용량 과금:** 반환 데이터, 크롤링 요청, 후속 이용 등 무엇을 세느냐에 따라 비용이 달라집니다.

이 유형들은 함께 적용될 수 있습니다. API가 유료로 남아 있어도 필요한 AI 이용은 허용되지 않을 수 있고, 기존 API가 끝난 뒤 별도 계약만 남을 수도 있습니다. 그래서 API의 존재 여부만으로 개방성을 판단하기는 어렵습니다.

## 제한과 선택적 개방에는 서로 다른 경제적 유인이 있습니다

AI 답변이 원문 방문을 대신한다면 플랫폼이나 게시자는 광고·구독·판매 기회를 잃을 수 있습니다. 이런 조건에서는 데이터 이용료를 받거나 자기 서비스 안에서 이용자를 유지하려는 유인이 생깁니다. 반대로 출처 링크가 방문을 늘리거나 계약 수입이 손실을 상쇄한다면 외부 제공이 유리할 수도 있습니다.

대량 요청 처리, 개인정보 보호와 삭제 반영에도 비용이 듭니다. 승인과 과금은 이를 감당하는 수단이 될 수 있습니다. 그러나 비슷한 비용과 위험을 가진 외부 사업자에게 필요한 데이터를 주지 않고 자사 서비스에만 제공한다면 경쟁자의 진입을 어렵게 할 가능성도 있습니다.

대체하기 어려운 데이터와 이용자를 모으는 서비스가 결합할 때 이 위험은 커질 수 있습니다. 데이터가 추천 품질을 높이고, 더 많은 이용자의 선택이 다시 새 데이터를 만드는 구조를 생각할 수 있기 때문입니다. 이는 데이터와 서비스의 결합이 경쟁에 미칠 영향을 설명하는 가설입니다. 충분한 대체 데이터와 여러 서비스의 병행 이용은 이런 효과를 줄일 수 있습니다.

## 영향과 전망은 접근 조건에 달려 있습니다

독립 개발사와 연구자는 조회 비용뿐 아니라 계약 협상과 데이터 공급자 변경 부담을 안게 될 수 있습니다. 이용자에게는 통합된 AI 서비스의 편리함이 생기는 한편, 비교·추천 서비스의 선택지가 줄어들 위험도 있습니다. 게시자에게는 새 수입원이 될 수 있지만, 플랫폼의 계약 수입이 개별 기여자 보상으로 자동 연결되는 것은 아닙니다.

선택권을 보완하려는 규제도 나왔습니다. 영국 경쟁시장청(CMA)은 [2026년 6월 3일 Google 검색에 게시자 관련 행위 요건을 부과](https://www.gov.uk/government/news/cma-secures-fairer-deal-for-publishers-and-improves-google-search-services-in-uk/)했습니다. 검색의 AI 기능에 콘텐츠가 쓰이는 것을 거부할 통제와 명확한 출처 링크 등을 요구하며, 전체 변경의 이행에는 9개월을 부여했습니다. 전 세계에서 이행이 끝났다는 뜻은 아닙니다. CMA는 전략적 시장 지위 지정 자체가 반경쟁적 행위를 의미하지 않는다고도 설명합니다.

앞으로의 쟁점은 계약 건수보다 참여 조건입니다. 작은 사업자도 예측 가능한 가격으로 필요한 데이터를 얻는다면 유료 제공은 외부 생태계를 유지할 수 있습니다. 반대로 자사와 일부 제휴사만 핵심 데이터에 접근한다면 시장 집중 위험은 커집니다. 데이터 폐쇄화와 독점화의 연결은 그 접근 격차가 얼마나 크고, 대체하기 얼마나 어려운지에 달려 있습니다.

## 함께 보면 좋을 자료

- [Reddit Data API 약관](https://redditinc.com/policies/data-api-terms): 데이터 접근과 사용자 콘텐츠의 이용 권한을 구분합니다.
- [영국 CMA의 Google 검색 조치](https://www.gov.uk/government/news/cma-secures-fairer-deal-for-publishers-and-improves-google-search-services-in-uk/): 게시자의 AI 이용 선택권과 출처 표시를 다룹니다.

## 참고 자료

조회일: 2026년 10월 15일. 제휴 발표는 발표 당시 공개된 범위를 기준으로 설명했습니다.

- 네이버: [쇼핑·책·전문자료 검색 종료](https://developers.naver.com/notice/article/32564), [API HUB 이관](https://developers.naver.com/notice/article/32530), [검색 API 약관 개정](https://developers.naver.com/notice/article/33400).
- 네이버 API 문서: [쇼핑 검색 레퍼런스](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md), [쇼핑인사이트](https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md), [Commerce API](https://apicenter.commerce.naver.com/docs/commerce-api/current).
- Reddit: [Google 제휴, 2024-02-22](https://redditinc.com/news/reddit-and-google-expand-partnership), [OpenAI 제휴, 2024-05-16](https://redditinc.com/news/reddit-and-oai-partner), [Data API 약관](https://redditinc.com/policies/data-api-terms).
- X: [API 가격](https://docs.x.com/x-api/getting-started/pricing), [개발자 정책](https://docs.x.com/developer-terms/policy).
- Cloudflare: [Pay Per Crawl, 2025-07-01](https://blog.cloudflare.com/introducing-pay-per-crawl/), [베타 문서](https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/), [Pay Per Use, 2026-09-30](https://blog.cloudflare.com/pay-per-use/).
- 영국 CMA: [Google 검색 조치, 2026-06-03](https://www.gov.uk/government/news/cma-secures-fairer-deal-for-publishers-and-improves-google-search-services-in-uk/).
