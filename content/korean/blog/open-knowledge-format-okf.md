---
title: "Open Knowledge Format(OKF): 에이전트용 지식 표현 개방형 포맷"
meta_title: ""
description: "Google Cloud가 제안한 AI 에이전트용 지식 교환 표준 OKF v0.1. YAML frontmatter + Markdown 기반 Knowledge Bundle 구조, LLM Wiki·AGENTS.md·MCP와의 관계를 정리합니다."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-07-02T11:47:08+09:00
image: ""
categories: ["AI"]
tags: ["ai-agent", "knowledge-management", "metadata", "open-standard", "okf", "google-cloud", "mcp"]
author: "whackur"
translationKey: "open-knowledge-format-okf"
draft: false
---

AI 에이전트가 실패하는 원인을 들여다보면 모델 성능보다 맥락의 부재가 먼저 나오는 경우가 많습니다. 테이블 스키마, 지표 계산법, 장애 대응 런북, 두 시스템 사이의 join path가 카탈로그 벤더, 사내 위키, 코드 주석, 개인 노트에 흩어져 있고, 에이전트 개발자마다 같은 context assembly 문제를 처음부터 다시 풉니다.

Open Knowledge Format(OKF)은 [Google Cloud](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/)가 2026년 6월 공개한 AI 에이전트용 지식 표현 포맷입니다. 새 서비스나 플랫폼이 아니라, YAML frontmatter가 붙은 Markdown 파일들의 디렉터리로 지식을 표현하는 최소 상호운용 규약입니다. [공식 repo](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)에서 v0.1 draft 명세를 볼 수 있습니다.

## 배경: 맥락 조립 비용

현재 조직 지식은 대개 이렇게 흩어져 있습니다.

- 테이블 스키마와 데이터셋의 비즈니스 의미
- 회사가 정의한 지표 계산식
- 장애 대응 런북과 운영 플레이북
- 두 시스템 사이의 join path
- API 폐기 공지와 비즈니스 프로세스

카탈로그 벤더, 사내 위키, shared drive, 코드 주석이 각자 다른 API와 포맷에 묶여 있어 에이전트가 읽을 수 있는 통일된 형태가 없습니다. OKF는 포맷 자체를 공용어로 만들자는 접근입니다.

## LLM Wiki와의 관계

Andrej Karpathy가 공개한 [LLM Wiki 아이디어](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)는 RAG처럼 매 질문마다 문서 조각을 다시 검색하게 하지 말고, 시간이 지날수록 정제되는 Markdown 기반 지식 라이브러리를 에이전트와 함께 유지하자는 패턴입니다.

핵심 관찰은 LLM에게는 지루함이 없고, cross-reference 갱신을 잊지 않으며, 한 번에 여러 파일을 동시에 수정할 수 있다는 점입니다. 사람이 개인 위키에서 포기하기 쉬운 장부 작업(cross-reference 갱신, 중복 병합, 구조 정리)이 오히려 LLM에게 맞는다는 이야기입니다. OKF는 이 패턴을 조직·도구·에이전트 간 상호운용 가능한 명세로 정리하려는 시도입니다.

## OKF v0.1 명세

### Knowledge Bundle

Knowledge Bundle은 Markdown 디렉터리 트리로 표현되는 배포 단위입니다.

```text
path/to/bundle/
├── index.md        # 선택. 디렉터리 목록 / progressive disclosure
├── log.md          # 선택. 변경 이력
├── <concept>.md    # 루트 개념 문서
└── <subdirectory>/
    ├── index.md
    └── <concept>.md
```

Git 저장소로 관리하는 것이 권장됩니다. history, attribution, diff, review가 모두 가능합니다. tarball/zip도 허용하며, 큰 repo의 하위 디렉터리로도 쓸 수 있습니다.

### Concept와 Concept ID

Concept는 번들 안의 지식 단위이며, Markdown 파일 하나로 표현됩니다.

- tangible asset: 테이블, 데이터셋, API, 대시보드
- abstract concept: 지표, 프로세스, 플레이북, 참고 자료

**Concept ID는 파일 경로에서 `.md`를 제거한 값**입니다. `tables/users.md`의 Concept ID는 `tables/users`입니다. 파일 경로가 곧 지식의 identity이므로, 경로 설계가 taxonomy 설계입니다.

### Frontmatter 필드

모든 concept 문서는 UTF-8 Markdown이고, 맨 위에 YAML frontmatter를 둡니다.

```yaml
---
type: <Type name>        # 유일한 필수 필드
title: <표시명>
description: <한 줄 요약>
resource: <canonical URI>
tags: [<tag>, <tag>]
timestamp: <ISO 8601 datetime>
---
```

`type`만 필수이며, 값은 중앙 등록되지 않습니다. `BigQuery Table`, `Metric`, `API Endpoint`, `Playbook`, `Reference` 등 생산자가 자유롭게 명명합니다. 소비자는 모르는 type이나 추가 key를 만나도 generic concept로 처리해야 합니다.

### 본문과 Cross-linking

본문은 자유 Markdown입니다. heading, list, table, fenced code block 같은 구조화 Markdown을 권장합니다. 관례적 섹션은 `# Schema`, `# Examples`, `# Citations`입니다.

Concept 간 관계는 표준 Markdown 링크로 표현합니다. bundle root 기준 절대 링크(`[customers](/tables/customers.md)`)를 권장하고 상대 링크(`[neighbor](./other.md)`)도 허용합니다. broken link도 허용합니다. 아직 작성되지 않은 지식을 가리키는 링크일 수 있기 때문입니다.

### 예약 파일명

`index.md`와 `log.md`는 어느 디렉터리 레벨에도 올 수 있는 예약 파일명이며, concept 문서로 쓰면 안 됩니다.

- `index.md`: progressive disclosure 파일. 해당 디렉터리 내용을 먼저 훑어볼 수 있게 합니다. root `index.md`에 `okf_version: "0.1"` 선언 가능.
- `log.md`: 변경 이력 파일. `## YYYY-MM-DD` 날짜 heading, 최신 항목 우선. `**Update**`, `**Creation**`, `**Deprecation**` 접두어 관례.

### Conformance 기준

OKF v0.1 conformant bundle의 최소 조건은 세 가지입니다.

1. 모든 비예약 `.md` 파일에 parse 가능한 YAML frontmatter가 있다.
2. 모든 frontmatter에 비어 있지 않은 `type` 필드가 있다.
3. `index.md`, `log.md`가 존재하면 각각의 구조 규칙을 따른다.

선택 필드 누락, 알 수 없는 type, 알 수 없는 추가 key, broken link, `index.md` 부재만으로는 bundle을 거부해서는 안 됩니다.

## 공식 repo와 예시

[GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)의 `okf/` 디렉터리에는 명세와 함께 reference POC가 있습니다.

- `SPEC.md`: OKF v0.1 draft 명세
- `bundles/`: GA4, Stack Overflow, Bitcoin public dataset 예시 bundle
- `src/enrichment_agent/`: Google ADK + Gemini 기반 enrichment agent (BigQuery metadata를 OKF concept 문서로 생성)
- `viz.html`: sample bundle을 그래프 뷰로 보는 visualizer

README는 "format itself is the contribution"이라고 강조합니다. enrichment agent나 visualizer는 OKF를 생산·소비하는 예시일 뿐, OKF 자체는 특정 에이전트 프레임워크·모델·시각화 도구를 요구하지 않습니다.

## 주변 도구·표준과의 관계

### AGENTS.md / CLAUDE.md

[AGENTS.md](https://agents.md/)는 "README for agents"를 지향하는 repo 관례 파일입니다. OKF와 같은 계열의 흐름이지만 범위가 다릅니다.

- AGENTS.md: 특정 repo에서 코딩 에이전트가 따라야 할 setup·test·style 규칙
- OKF: 에이전트와 사람이 공유하는 지식 corpus 전체를 표현하는 포맷

OKF의 출발점은 AGENTS.md, CLAUDE.md, index.md, log.md 같은 파일들이 이미 LLM Wiki식 관례로 쓰이고 있지만 필드·구조·링크 의미가 제각각이라 상호운용이 어렵다는 관찰입니다. OKF는 이 관례들을 최소 규칙으로 묶으려 합니다.

### Avro / Protobuf / OpenAPI

OKF SPEC의 non-goals는 Avro, Protobuf, OpenAPI 같은 domain-specific schema를 대체하지 않는다고 명시합니다. OKF는 이들을 포섭하지 않고 참조합니다.

- OpenAPI: API 계약 자체
- Protobuf/Avro: 직렬화·메시지 schema
- OKF: 그 schema 주변의 사람/에이전트용 맥락, 예시, 운영 지식, join path

OKF는 schema layer 위에 얹는 context layer입니다.

### Model Context Protocol(MCP)

[MCP](https://modelcontextprotocol.io/introduction)는 AI 애플리케이션이 외부 시스템, 데이터 소스, 도구와 연결되는 open protocol입니다. OKF와 MCP는 경쟁 관계가 아닙니다.

- MCP: 에이전트가 외부 도구·데이터와 어떻게 연결되는가 (연결과 호출 방식)
- OKF: 에이전트가 읽고 교환할 지식을 어떤 파일 포맷으로 표현하는가

MCP server가 OKF bundle을 resource로 노출하거나, 에이전트가 MCP로 데이터 카탈로그를 조회한 뒤 OKF bundle로 정리하는 구성이 가능합니다.

## OKF가 유용한 상황

OKF가 잘 맞는 경우:

- 여러 에이전트·도구가 같은 조직 지식을 읽어야 할 때
- 데이터 카탈로그, 지표 정의, 플레이북, API 문서가 흩어져 있을 때
- git diff·review로 지식 변경을 관리하고 싶을 때
- 특정 벤더 API 없이 지식 corpus를 교환하고 싶을 때

OKF가 과한 경우:

- 단일 앱 내부에서만 쓰는 임시 prompt/context 파일
- schema 자체가 이미 OpenAPI/Protobuf 등으로 충분한 경우
- runtime DB에서만 동적으로 생성·소멸하는 ephemeral context

## 유의사항

v0.1은 draft입니다. optional field나 예약 파일명 규칙이 향후 버전에서 바뀔 수 있습니다. [PyTorchKR 한국어 해설](https://discuss.pytorch.kr/t/open-knowledge-format-okf-google-ai-feat-llm-wiki/10701)과 [Google Cloud Blog 글](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/)은 좋은 입문 자료지만, 최종 규칙 판단은 공식 [SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)를 1차 근거로 삼아야 합니다.

## 함께 보면 좋을 자료

- [GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf): 공식 repo, 명세·예시 bundle·enrichment agent
- [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): LLM Wiki 패턴 원문
- [AGENTS.md](https://agents.md/): 에이전트용 README 관례
- [Model Context Protocol](https://modelcontextprotocol.io/introduction): 에이전트-도구 연결 open protocol
- [Google Cloud Blog: OKF](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/): Google Cloud 측 배경·목적 설명

## 참고 자료

- [Open Knowledge Format SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md): GoogleCloudPlatform/knowledge-catalog, 조회일 2026-06-30
- [GoogleCloudPlatform/knowledge-catalog OKF README](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf): GitHub, 조회일 2026-06-30
- [Google Cloud Blog: How the Open Knowledge Format can improve data sharing](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/): Google Cloud, 조회일 2026-06-30
- [PyTorchKR: Open Knowledge Format(OKF) 해설](https://discuss.pytorch.kr/t/open-knowledge-format-okf-google-ai-feat-llm-wiki/10701): discuss.pytorch.kr, 조회일 2026-06-30
- [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): Andrej Karpathy, 조회일 2026-06-30
- [AGENTS.md](https://agents.md/): agents.md, 조회일 2026-06-30
- [Model Context Protocol Introduction](https://modelcontextprotocol.io/introduction): modelcontextprotocol.io, 조회일 2026-06-30
