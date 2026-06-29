# 발행 워크플로우

소스 → 글 → 미리보기 → 발행까지의 단계별 절차. 한/영 동시 발행 원칙.

> 리서치는 [research-pipeline.md](./research-pipeline.md), 글 규격은 [content-template.md](./content-template.md).

## 0. 중복 발행 방지 (필수, 글 만들기 전)

같은 주제의 기존 글이 있는지 **먼저** 확인한다.

1. `rg -l "translationKey: \"<slug>\"" content/` 또는 제목/키워드로 검색
2. **없으면** → 신규 진행
3. **있으면(동일·유사 주제)** → 임의로 두 번째 글 만들지 말고 **사용자에게 되묻는다**:
   - (a) **신규 글**: 관점·범위가 충분히 다른가? → 슬러그/제목 구분
   - (b) **기존 글 업데이트**: 보강·갱신인가? → 기존 파일 수정 + `lastmod` 갱신
4. 사용자 확인 없이 중복 주제 발행 금지.

## 0.5 적합성 확인 (필수)

글감이 이 블로그에 맞는지 확인한다.

- **카테고리 적합성**: 메인 카테고리(AI / Blockchain) 중 하나에 들어가는가? (Local LLM·Physical AI 등 세부 주제는 `tags`로 표현)
- **플로우 적합성**: 표준 발행 플로우(한/영 동시, 리서치 기반, 출처 표기)에 맞는 형태인가?

→ 어느 하나라도 **맞지 않으면(애매한 주제, 새 카테고리가 필요해 보임, 형식이 다른 글 등) 임의로 진행하지 말고 사용자에게 되묻는다**:
- 새 카테고리를 추가할지, 기존 카테고리(AI/Blockchain)에 편입하고 태그로 세분화할지
- 표준 플로우 예외로 다룰지 (그렇다면 어떻게)

## 1. 리서치

[research-pipeline.md](./research-pipeline.md) 수행 — 1차 소스 + Reddit/HN 후기 + 외부 블로그 + 함께 볼 자료 수집·검증.

## 2. 슬러그 결정

영문 kebab-case, 한/영 공통. 예: `local-llm-quantization`

## 3. 두 파일 작성

```
content/korean/blog/<slug>.md      # 한국어 (기본)
content/english/blog/<slug>.md     # 영어
```
[content-template.md](./content-template.md) front matter 규격 적용. `translationKey`는 양쪽 동일. 본문 구조·어조·출처 규칙 준수.

## 4. 로컬 미리보기 (발행 전, push 전까지 비공개)

```bash
npm run dev        # 또는 pnpm dev — Tailwind 감시 + hugo server
# http://localhost:1313
```
양 언어, 언어 전환 버튼, 검색, 다크모드 동작 확인. `draft: true`는 dev에서 보임.

## 5. 발행

1. 양쪽 front matter `draft: false`
2. 커밋 (conventional, 예: `content: add <slug> post`)
3. `main`에 push → GitHub Actions가 빌드·배포

## 6. 수정 시

기존 파일 수정 → `lastmod` 갱신(git 자동화 시 커밋만) → push.

## 배포 메모

- GitHub Actions 워크플로우가 **Node/pnpm → Tailwind 빌드 → Hugo(모듈 포함) 빌드 → Pages 배포** 순으로 동작해야 한다 (Hugoplate는 Hugo Modules + Tailwind 의존).
- `static/CNAME` = `blog.hakhub.net` 유지.
- `/public`, `/resources/_gen`은 커밋 금지 (CI가 빌드).
