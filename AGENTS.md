# AGENTS.md

이 저장소에서 작업하는 AI 에이전트(및 사람)를 위한 운영 가이드입니다.
이 파일이 단일 소스(single source of truth)이며, `CLAUDE.md`는 이 파일을 가리키는 심볼릭 링크입니다.
로컬 전용 메모·진행 상태는 `CLAUDE.local.md`(gitignore)에 있습니다.

## 이 프로젝트는 무엇인가

**GitHub Pages**에서 호스팅하는 무료 정적 블로그입니다.

| 항목         | 값                                                  |
| ------------ | --------------------------------------------------- |
| 생성기       | Hugo extended (v0.163.3)                            |
| 테마         | Hugoplate (Tailwind) — Hugo Modules + Node/npm + Tailwind 빌드 |
| 저장소       | `whackur/blog-hakhub-net` (**public**)              |
| 호스팅       | https://blog.hakhub.net (GitHub Pages)              |
| 배포         | GitHub Actions (Node/npm → Tailwind → Hugo → Pages) |
| 언어         | 한국어 기본 + 영어. **디렉토리 방식 다국어**(`content/korean`, `content/english`), 한/영 동시 발행 원칙 |

## 보안 — 이 저장소는 PUBLIC 입니다

여기 있는 모든 것은 전 세계에 공개된다고 가정하세요.

- 시크릿은 **절대** 커밋 금지: API 키, 토큰, `.env`, 배포 키, 비밀번호,
  비공개 DNS/인프라 정보. `.gitignore`가 흔한 경우를 막아 주지만,
  최종 방어선은 작성자입니다 — 커밋 전 모든 diff를 검토하세요.
- 키가 필요한 연동(애널리틱스, 댓글 등)은 **GitHub Actions secrets**에 두고
  추적되는 파일에는 절대 넣지 마세요. 플레이스홀더는 `*.example` 파일로만.
- 개인정보(실명+연락처 등)는 이미 공개되어 발행 목적이 명확한 경우가 아니면
  글에 넣지 마세요.
- 로컬 전용 메모는 `CLAUDE.local.md` 또는 gitignore된 파일에. (`.atl/`는 추적 안 함)

## 콘텐츠 주제

IT 기술 블로그입니다. 주력 주제:

- **AI** — 모델, 도구, 활용, 동향, Local LLM(온디바이스/셀프호스팅), Physical AI(로보틱스·임베디드 AI)
- **Blockchain / Web3** — Solidity, 스마트 컨트랙트, 프로토콜

카테고리(`categories`)는 **AI / Blockchain** 2개로 운영한다. 세부 주제(local-llm, physical-ai 등)는 `tags`로.

## 글 발행 — `docs/publishing/` 참조

발행 관련 상세 규격은 별도 문서로 분리되어 있습니다. **글을 쓰기 전 반드시 해당 문서를 따르세요.**

- [docs/publishing/research-pipeline.md](docs/publishing/research-pipeline.md) — 소스(GitHub·논문·도구·링크) → 리서치(1차 소스 + Reddit·HN 후기 + 외부 블로그 + 함께 볼 자료) → 종합
- [docs/publishing/content-template.md](docs/publishing/content-template.md) — front matter 규격·본문 구조·어조·출처 표기 (Hugoplate)
- [docs/publishing/workflow.md](docs/publishing/workflow.md) — 중복 방지 → 작성 → 미리보기 → 발행 단계
- [docs/publishing/style-korean.md](docs/publishing/style-korean.md) — **한국어 문체**: 번역투·AI 티 제거 (어색하지 않게)
- [docs/publishing/style-english.md](docs/publishing/style-english.md) — **영어 문체**: AI 글쓰기 패턴 제거

**핵심 원칙(요약)**: 한/영 동시 발행 · 같은 주제 중복 발행 금지(있으면 "신규 vs 업데이트" 되묻기) · 모든 주장에 출처 · 후기는 장점·비판 균형 · public 레포라 시크릿/내부정보 링크 금지.

## 브랜치 전략

| 브랜치 | 역할 |
| ------ | ---- |
| `develop` | 기본 작업 브랜치. 블로그 글 작성·수정은 여기서 시작 |
| `post/*`, `fix/*` 등 | 병렬 작업 시 `develop`에서 분기, 완료 후 `develop`으로 병합 |
| `main` | **배포 브랜치**. `develop`(또는 작업 브랜치)이 검증된 후 여기 병합 → 자동 배포 |

- **일상 작업**: `develop` 체크아웃 상태에서 작업.
- **병렬 작업(에이전트 등)**: `develop`에서 작업 브랜치를 생성 → 검토 후 `develop` 병합 → `main` 병합.
- `main`에 직접 커밋·push하지 마세요. 반드시 병합 경로를 거칩니다.
- GitHub 기본 브랜치는 `develop`으로 설정되어 있습니다.

## 로컬 작업 흐름

```bash
npm run dev      # Tailwind 감시 + hugo server → http://localhost:1313 (draft 포함)
npm run build    # 프로덕션 빌드 → /public (gitignore됨)
```

`/public`, `/resources/_gen`은 커밋하지 마세요 — CI가 빌드합니다.

## 배포

- `main`에 push(병합) → GitHub Actions가 빌드·배포.
- 커스텀 도메인 유지를 위해 `static/CNAME` = `blog.hakhub.net`.
- GitHub Pages: Settings → Pages → Source = **GitHub Actions**, 커스텀 도메인 `blog.hakhub.net`, **Enforce HTTPS** 켜기.

## 에이전트 규칙

- 기존 구조와 활성 테마의 규칙을 따르세요. 이유 없이 레이아웃을 재구성하지 마세요.
- 커밋은 conventional 형식으로 (예: `feat:`, `fix:`, `content:`). AI 표기(attribution)는 넣지 마세요.
- 발행해도 안전한지 확신이 서지 않으면, 멈추고 물어보세요.
- 블로그 글에 사용자의 개인 프로젝트 맥락, 비공개 메모, 사적 계획 내용을 사용자 명시적 요청 없이 삽입하거나 언급하지 마세요. 모든 발행 콘텐츠는 공개된 소스에 근거해서 작성합니다. 개인 작업 파일은 소스 정보를 추출하는 용도로만 쓰고, 그 안의 개인 컨텍스트(프로젝트명, 내부 계획, 개인 경험 등)는 글에 반영하지 않습니다.
