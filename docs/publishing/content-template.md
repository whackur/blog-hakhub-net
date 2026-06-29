# 글 규격 (Hugoplate)

front matter·본문 구조·어조·출처 표기 규격. 테마는 **Hugoplate**(디렉토리 방식 다국어).

> 리서치 절차는 [research-pipeline.md](./research-pipeline.md), 발행 단계는 [workflow.md](./workflow.md).

## 파일 위치 (디렉토리 방식 다국어)

Hugoplate는 언어별 디렉토리를 쓴다. **같은 파일명**을 양 언어에 두면 Hugo가 번역쌍으로 묶는다.

```
content/korean/blog/<slug>.md      # 한국어 (기본)
content/english/blog/<slug>.md     # 영어
```

## Front matter 규격

```yaml
---
title: "글 제목"
meta_title: ""                         # SEO 제목 (비우면 title 사용)
description: "목록·검색·SNS 미리보기용 한 줄 설명"
date: 2026-06-30T10:00:00+09:00        # 작성일(최초 발행). 고정. 한/영 동일.
lastmod: 2026-06-30T10:00:00+09:00     # 최종 수정일. 수정 시 갱신(또는 git 자동).
image: "/images/posts/<slug>/cover.png"  # 대표 이미지 (static/ 기준 경로)
categories: ["AI"]                     # AI / Blockchain (subtopics go in tags, e.g. local-llm, physical-ai)
tags: ["llm", "quantization"]
author: "hakhub"                        # content/<lang>/authors/ 의 작성자 페이지
translationKey: "<slug>"               # 한/영을 묶는 키 — 양쪽 동일! (안전장치)
draft: true                             # 발행 시 false
---
```

> ⚠️ Hugoplate는 PaperMod와 front matter가 다르다: 대표 이미지는 `cover`가 아니라 **`image`**, SEO는 **`meta_title`/`description`**, 목차·읽기시간은 테마 설정으로 제어(글마다 X).

## 작성일 / 최종수정일

- `date`: 최초 발행일. 한 번 정하면 안 바꾼다. 한/영 동일.
- `lastmod`: 수정 시 갱신. 자동화하려면 `hugo.toml`에:
  ```toml
  enableGitInfo = true
  [frontmatter]
    lastmod = ["lastmod", ":git", "date"]
  ```
  ⚠️ `enableGitInfo`는 **커밋 1개 이상** 있어야 동작 (0개면 빌드 실패).

## 본문 구조 & 어조

> **문체 (필수)**: AI 티·번역투를 빼야 한다. 한국어는 [style-korean.md](./style-korean.md), 영어는 [style-english.md](./style-english.md)의 규칙을 **반드시** 적용한다.

- **구조**: 도입(왜 읽어야 하나) → 무엇인가 → 어떻게 동작 → **커뮤니티 반응** → **함께 보면 좋을 자료** → 정리 → 참고 자료
- **어조**: 친근하지만 정확하게. 설명하듯, 가르치려 들지 않기. "~합니다" 톤 일관.
- 1문단 1주제. 코드/명령은 fenced code block(언어 지정). 핵심만 굵게.
- 한국어판은 자연스러운 한국어, 영문판은 **번역투 금지**(의미 전달 우선).
- 기술 용어·코드 식별자는 원어 그대로. 약어는 첫 등장 시 풀어 쓴다.
- 단정적 주장엔 근거(출처). 추측은 추측이라 명시. 의견과 사실 구분.

## 출처 · 참고링크 표기

- **본문 인라인**: 주장 자리에서 바로 링크. 예: `[공식 문서](https://...)에 따르면…`
- **인용**: blockquote + 출처.
  ```markdown
  > 인용문
  > — 저자/출처, [링크](https://example.com)
  ```
- **커뮤니티 반응**: Reddit/HN 후기는 장점·비판 균형 있게, 각 출처 링크.
- **이미지/코드**: 출처·라이선스 표기.
- **글 하단 필수 섹션**:
  ```markdown
  ## 함께 보면 좋을 자료
  - [제목](https://...) — 한 줄 설명

  ## 참고 자료
  - [제목](https://...) — 저자/사이트, 조회일 2026-06-30
  ```
  영문판은 `## Further reading` / `## References`.
- ⚠️ **public 레포** — 내부 URL·토큰·인증정보 링크 금지.
