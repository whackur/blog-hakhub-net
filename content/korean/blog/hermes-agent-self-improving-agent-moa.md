---
title: "Hermes Agent v0.18: 스스로 배우는 에이전트와 MoA가 만났을 때"
meta_title: ""
description: "Nous Research의 Hermes Agent v0.18.0이 다듬은 자기개선 루프(메모리·스킬·/learn·/journey)와, MoA를 가상 모델 제공자로 에이전트 루프 안에 넣은 설계를 정리했습니다."
date: 2026-07-03T17:45:00+09:00
lastmod: 2026-07-03T17:45:00+09:00
image: ""
categories: ["AI"]
tags: ["hermes-agent", "multi-agent", "moa", "ai-agent", "skills", "memory"]
author: "whackur"
translationKey: "hermes-agent-self-improving-agent-moa"
draft: false
---

Nous Research가 만든 오픈소스 에이전트 Hermes Agent가 2026년 7월 1일 v0.18.0을 냈습니다. [릴리스 노트](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.1)는 이번 버전을 "The Judgment Release"라고 부릅니다. 새 명령어 몇 개를 더한 마이너 업데이트로 보면 핵심을 놓치기 쉽습니다. [공식 문서](https://hermes-agent.nousresearch.com/docs)는 Hermes Agent를 "스스로 배우는 AI 에이전트"라고 소개하는데, 실제로 이 프로젝트는 쓸수록 메모리와 스킬을 쌓아가는 학습 루프를 핵심 설계로 삼고 있습니다. 이 글은 그 자기개선 루프가 v0.18에서 어떻게 다듬어졌는지, 그리고 같은 버전에서 정식 모델 선택지가 된 Mixture of Agents(MoA)가 이 루프 안에서 어떤 역할을 맡는지를 정리합니다.

## Hermes Agent가 풀려는 문제

Hermes Agent는 노트북에서만 도는 CLI 도구가 아닙니다. VPS, GPU 클러스터, 서버리스 인프라 위에서 상주하도록 설계됐고, CLI·TUI·Desktop 앱·메신저 게이트웨이가 같은 코어를 공유합니다. 로컬, Docker, SSH, Daytona, Singularity, Modal 등 여러 실행 백엔드를 지원하고, Telegram·Discord·Slack·WhatsApp·Signal·Matrix·이메일을 포함한 다양한 메신저로 연결할 수 있습니다.

모델과 제공자 선택도 특정 벤더에 묶여 있지 않습니다. Nous Portal, OpenRouter, OpenAI, 사용자가 지정한 커스텀 엔드포인트를 그대로 붙일 수 있고, cron으로 예약 작업을 걸거나 서브에이전트에 작업을 위임해 병렬로 처리합니다. `execute_code`로 도구를 호출하는 스크립트를 실행하고, MCP를 지원하며, 스킬은 agentskills.io 형식과 호환됩니다. 배치 처리와 Atropos를 통한 궤적(trajectory) 추출·강화학습 연계 같은 연구용 기능도 갖추고 있습니다.

## 스스로 배우는 에이전트라는 설계

Hermes Agent의 핵심은 닫힌 학습 루프입니다. 메모리, 스킬 생성과 자기개선, 세션 간 회상, Honcho 기반 사용자 모델링이 이 루프를 이룹니다.

[메모리 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)에 따르면 영속 메모리는 두 파일로 나뉩니다. 에이전트가 스스로 남기는 노트인 `MEMORY.md`는 기본 2,200자 한도, 사용자 프로필인 `USER.md`는 기본 1,375자 한도를 둡니다. 둘 다 세션이 시작할 때 고정된 스냅샷으로 시스템 프롬프트에 주입되는데, 이렇게 하면 세션 도중 메모리가 바뀌어도 prompt cache가 깨지지 않습니다. 메모리 도구는 추가·교체·삭제를 지원하고, v0.17부터는 여러 변경을 한 번에 묶는 atomic `operations` 배열도 쓸 수 있습니다. 주입된 메모리 밖의 내용은 세션 검색으로 불러옵니다. 필요하면 Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory 같은 외부 메모리 제공자 플러그인으로 교체할 수도 있습니다.

메모리가 사실과 맥락을 저장하는 쪽이라면, [스킬](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)은 "어떻게 하는지"를 저장하는 절차적 기억에 가깝습니다. 스킬은 필요할 때만 불러오는 온디맨드 지식 문서이고, 토큰을 아끼기 위해 점진적으로 공개(progressive disclosure)됩니다. 기본 스킬 디렉터리는 `~/.hermes/skills/`이고, 여기에 번들 스킬, Skills Hub에서 설치한 스킬, 에이전트가 직접 만든 스킬이 함께 놓입니다. `/learn` 명령은 디렉터리, URL, 대화 중 작업 흐름, 붙여넣은 메모 중 무엇이든 재사용 가능한 스킬로 바꿔줍니다. 스킬은 표준 `SKILL.md` 형식을 따르고 참고자료·템플릿·스크립트·에셋을 함께 담을 수 있으며, 환경변수 요구사항과 설정값을 스스로 선언할 수 있습니다.

## v0.18이 강조하는 판단과 검증

[릴리스 노트](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.1)에 따르면 v0.17.0 이후 약 1,720개 커밋과 998개의 머지된 PR이 쌓였고, 370명 넘는 커뮤니티 기여자가 참여했습니다. 릴리스가 "Judgment"라는 이름을 내건 이유는 숫자보다 우선순위 정리입니다. 릴리스 시점에 열려 있던 P0/P1 이슈와 PR을 모두 닫아, 최우선 항목 약 700개를 정리했다고 밝히고 있습니다.

이 버전이 실제로 바꾼 것은 에이전트가 자기 작업을 검증하는 방식입니다. 코딩 작업은 검증 근거를 남기고, `/goal`은 완료 조건을 계약처럼 명시하며, `pre_verify` 훅으로 완료 전에 확인 단계를 끼워 넣을 수 있습니다. `/learn`은 앞서 설명한 스킬 생성 명령이고, `/journey`는 메모리와 스킬이 쌓여온 과정을 타임라인으로 보여줍니다(Desktop 앱에는 메모리 그래프도 있습니다). `delegate_task`는 여러 서브에이전트를 백그라운드에서 동시에 돌리고 결과를 하나로 모아 돌려줍니다.

Desktop 앱은 프로젝트 단위 작업을 위한 화면을 갖췄습니다. 코드베이스 사이드바, 코딩 레일, 리뷰 패널, git worktree 관리를 프로젝트 → 레포 → 레인 구조로 묶었습니다. 호스팅형·팀 배포를 위한 게이트웨이는 트래픽이 없을 때 자원을 0으로 줄이는 scale-to-zero와 배포 전환 시 drain 조정을 지원합니다. 자기개선 비용을 낮추기 위해 턴이 끝난 뒤의 백그라운드 리뷰를 보조 모델로 라우팅하고 컨텍스트를 요약하며, 리뷰 빈도도 상황에 맞춰 조정합니다. 긴 프롬프트를 작성할 땐 `/prompt`로 `$EDITOR`를 바로 열 수 있고, GCP 서비스 계정의 단기 OAuth 토큰으로 Gemini를 쓰는 Google Vertex AI 제공자도 추가됐습니다.

보안 쪽에서도 여러 항목을 손봤습니다.

- MCP 설정이 디스크에 저장되는 방식 강화
- cron 작업이 `base_url`을 통해 데이터를 외부로 유출하는 경로 차단
- 파일을 읽을 때 시크릿이 섞여 있으면 걸러내는 sentinel 추가
- Slack `xapp` 토큰의 로그 노출 방지(redaction)
- 브라우저 도구가 클라우드 메타데이터 엔드포인트에 접근하지 못하도록 방어선 설정
- aiohttp 관련 CVE 대응 최소 버전 지정

## MoA가 Hermes 안에서 달라지는 점

Mixture of Agents는 원래 Together AI가 제안한 연구 패턴입니다. 여러 LLM의 출력을 계층으로 쌓아 서로 참고하게 만드는 방식인데(자세한 배경은 [기존 글](/blog/mixture-of-agents-moa/) 참고), Hermes Agent는 이 패턴을 별도 파이프라인이 아니라 에이전트가 이미 쓰고 있는 모델 선택 체계 안에 넣었습니다.

[MoA 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/)에 따르면 MoA는 `moa`라는 가상 모델 제공자로 노출됩니다. 이름을 붙인 MoA preset 각각이 CLI, TUI, Desktop, 게이트웨이에서 고를 수 있는 모델 하나처럼 보입니다. preset을 선택하면 그 preset의 aggregator가 실제로 응답을 쓰고 tool call을 내는 acting 모델이 됩니다. reference 모델은 먼저 실행되어 aggregator에게 참고할 분석을 건네주는 역할만 합니다.

동작 순서는 다음과 같습니다. 선택된 preset을 찾고, reference 모델들을 tool schema 없이 실행합니다. 이때 Hermes 시스템 프롬프트나 tool-call transcript는 넘기지 않는데, 호출 비용을 줄이고 일부 제공자가 낯선 형식을 거부하는 상황을 피하기 위해서입니다. reference 출력은 aggregator를 위한 비공개 컨텍스트로 붙고, aggregator는 평소와 같은 Hermes tool schema를 받아 실제 응답을 만듭니다. aggregator가 tool을 호출하면 Hermes는 그 tool을 정상적으로 실행하고, 다음 모델 반복에서도 업데이트된 대화 전체를 놓고 같은 절차를 반복합니다. v0.18부터는 각 reference 모델의 전체 출력을 라벨이 붙은 블록으로 보여주고, aggregator의 최종 답변을 실시간으로 스트리밍합니다.

preset으로 바로 전환하는 방법은 두 가지입니다. `/moa <프롬프트>`는 그 턴에만 기본 preset으로 전환해 응답을 받고 이전 모델로 돌아오는 원샷 명령입니다. 인자 없이 `/moa`만 입력하면 사용법만 출력하고, preset 이름을 유사하게 입력해도 더 이상 자동으로 매칭해주지 않습니다. 세션 내내 MoA를 쓰려면 모델 피커로 전환해야 합니다. `/model default --provider moa`처럼 provider를 `moa`로 지정하거나, `hermes model`, Dashboard, Desktop의 모델 드롭다운에서 MoA preset 섹션을 고르면 됩니다.

설정은 Dashboard의 Models → Model Settings → Mixture of Agents, Desktop Settings의 Model → Mixture of Agents, `hermes moa configure [name]` CLI, 또는 `config.yaml`로 할 수 있습니다. 문서가 소개하는 기본 preset 구성은 다음과 같습니다.

| 역할 | 모델 |
|---|---|
| Reference 1 | GPT-5.5 (openai-codex) |
| Reference 2 | DeepSeek-V4-Pro (openrouter) |
| Aggregator | Claude Opus 4.8 (openrouter) |

`reference_temperature`와 `aggregator_temperature`는 선택 항목입니다. 값을 생략하면 temperature를 아예 보내지 않고 provider 기본값을 그대로 씁니다. 출력 길이를 제한하고 싶으면 `reference_max_tokens`를 씁니다. 이 값은 reference(advisor) 출력에만 적용되고 aggregator 출력은 잘리지 않습니다. CLI로는 `hermes moa list`, `hermes moa configure`, `hermes moa configure review`, `hermes moa delete review`처럼 preset을 관리합니다.

몇 가지는 v0.18.0 문서 수준에서 확인한 사실입니다. MoA는 `hermes tools` 목록에 없고 켜고 끄는 toolset도 아닙니다. preset의 `enabled: false`는 reference fanout만 끄고 aggregator가 혼자 응답하게 만듭니다. aggregator가 다른 MoA preset을 가리키는 재귀 구조는 막혀 있습니다. reference 모델 하나의 인증이 실패해도 턴 전체가 중단되지 않고, 실패 내용을 컨텍스트에 포함한 채 나머지 reference로 계속 진행합니다. v0.18.0 릴리스 이후 main 브랜치에서는 MoA의 fanout 주기와 provider 기본 temperature 처리를 다듬는 수정이 계속 이어지고 있어서, 이 글에 정리한 세부 동작이 앞으로 조금씩 바뀔 수 있습니다.

Hermes 자체 벤치마크인 HermesBench 기준으로 MoA(Claude Opus 4.8 aggregator + GPT-5.5 reference 구성)는 0.8202를 기록했습니다. 같은 벤치마크에서 Claude Opus 4.8 단독은 0.7607, GPT-5.5 단독은 0.7412였습니다. 가장 강한 단일 모델보다 6점가량 높은 결과입니다. 다만 이 수치는 제3자 벤치마크가 아니라 Nous Research가 자체적으로 측정하고 공개한 결과라는 점은 분명히 해둘 필요가 있습니다.

## prompt cache를 깨지 않는 MoA 설계

MoA를 도입할 때 흔히 걱정하는 지점이 있습니다. 모델을 여러 개 거치면 prompt cache가 매번 깨져서 비용과 지연이 오히려 늘어나지 않느냐는 것입니다. [MoA 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/)는 이 부분을 설계 목표로 명시합니다. MoA를 선택해도 지나간 컨텍스트를 바꾸거나, 쓰던 tool 세트를 교체하거나, 대화 중간에 시스템 프롬프트를 다시 만들지 않습니다.

reference 모델은 다듬어진 결정적(deterministic) 입력만 받기 때문에 자기 나름의 캐시가 정상적으로 쌓입니다. aggregator 쪽은 reference 출력을 최신 user turn의 끝에 비공개 안내로 덧붙이는 방식을 씁니다. 이렇게 하면 대화 앞부분의 안정적인 prefix는 그대로 유지되어 캐시가 깨지지 않습니다. MoA를 쓸 때 실제로 늘어나는 비용은 캐시 무효화가 아니라, 매 반복마다 추가되는 reference 모델 호출 자체입니다.

## 비용과 한계

MoA를 켜면 반복마다 reference 모델 수만큼 호출이 늘고 aggregator 호출이 하나 더 붙습니다. `reference_max_tokens`로 advisor 쪽 출력을 줄여 벽시계 시간을 아낄 수 있지만, 정작 최종 응답을 쓰는 aggregator 출력은 캡을 걸 수 없습니다. 재귀 MoA는 막혀 있고, reference 인증 실패는 턴을 중단시키지 않지만 그만큼 실패한 모델의 몫은 그냥 버려집니다.

이 기능은 아직 다듬어지는 중입니다. 문서화된 지 오래되지 않았고, 릴리스 이후에도 main에서 세부 동작이 계속 조정되고 있습니다. MoA가 모든 상황에서 더 낫다는 뜻도 아닙니다. 여러 모델의 관점이 실제로 도움이 되는 어려운 작업에서 의미가 있고, 그렇지 않은 평범한 요청에서는 비용과 지연만 늘어날 수 있습니다.

## 커뮤니티 반응

MoA를 다룬 외부 리뷰 몇 개를 살펴보면 시각이 조금씩 다릅니다. [Tony Reviews Things](https://www.tonyreviewsthings.com/hermes-agent-mixture-of-agents-20/)는 MoA를 커스텀 파이프라인이 아니라 평범한 모델처럼 다룰 수 있다는 점, CLI·TUI·게이트웨이·Desktop에서 동일하게 동작한다는 점을 실용적인 장점으로 꼽습니다. 다만 HermesBench 수치를 인용할 때 이것이 내부 벤치마크지 제3자 검증은 아니라고 명시합니다.

[Crypto Briefing](https://cryptobriefing.com/hermes-agent-moa-beats-claude-opus-gpt-benchmarks/)은 벤치마크 결과를 기사의 중심으로 삼으면서, Hermes Agent가 영속 메모리와 학습 루프, 외부 툴·API 연동을 함께 갖췄다는 점도 언급합니다. SWE-bench Pro 관련 맥락도 언급하지만 전체 리더보드는 공개되지 않았다고 밝히고 있어서, 이 부분은 그대로 받아들이기보다 조심스럽게 볼 필요가 있습니다.

[Noqta](https://noqta.tn/en/news/nous-hermes-mixture-of-agents-2-virtual-models-2026)는 MoA를 "가상 모델" 패키징이라는 관점에서 다루면서 "Opus보다 8%, GPT-5.5보다 11% 높다"는 상대적 수치로 풀어 설명합니다. 동시에 HermesBench의 방법론과 제3자 재현 결과가 출시 시점엔 없었다는 점, 여러 제공자를 동시에 호출하는 데 따르는 비용·지연·장애 가능성이라는 트레이드오프를 함께 짚습니다. [AgentOS 가이드](https://agentos.guide/moa-2-system-beats-model)는 더 홍보성이 짙은 글이라, "시스템이 단일 모델을 이긴다"는 주제에 대한 커뮤니티 관심을 보여주는 정도로만 참고할 만합니다.

전체적으로 보면 외부 반응은 MoA를 "커스텀 파이프라인 없이도 여러 모델을 쓸 수 있게 만든 제품화"로 주목하는 쪽이 많고, 벤치마크 수치는 대부분 Nous가 공개한 값을 그대로 인용합니다. 독립적인 재현 결과는 아직 나오지 않았습니다.

## 두 글로 나눠 다루는 이유

MoA라는 개념 자체는 이 블로그의 [기존 글](/blog/mixture-of-agents-moa/)에서 다뤘습니다. Together AI의 원 논문, 계층적 구조, AlpacaEval·FLASK 벤치마크, SMoA·RMoA 같은 변형 구조, Self-MoA가 보여준 품질 대 다양성 트레이드오프가 그 글의 내용입니다. 이 글은 그 연구 패턴을 반복하지 않고, Hermes Agent가 그 패턴을 자기개선 루프를 갖춘 실제 에이전트 안에 어떻게 넣었는지에 집중했습니다. MoA의 이론적 배경이 궁금하면 기존 글을, MoA가 실제 제품에서 어떻게 동작하는지 궁금하면 이 글을 읽으면 됩니다.

## 정리

Hermes Agent v0.18.0은 자기개선 루프를 검증 가능하게 다듬은 릴리스입니다. 메모리와 스킬로 쌓아온 학습 구조 위에 `/goal`과 `pre_verify` 같은 검증 장치를 얹었고, `/learn`과 `/journey`로 그 학습 과정을 사용자가 직접 들여다볼 수 있게 했습니다. 같은 버전에서 정식 모델 선택지가 된 MoA는 별도 파이프라인 없이 여러 모델의 관점을 이 루프 안에 끼워 넣는 방법을 보여줍니다. 비용은 늘어나고, 벤치마크는 아직 Nous 자체 측정치이며, 세부 동작은 릴리스 이후에도 계속 바뀌고 있다는 점은 그대로 감안해야 합니다.

## 함께 보면 좋을 자료

- [Mixture of Agents(MoA): 여러 LLM을 쌓아 GPT-4 Omni를 넘은 방법](/blog/mixture-of-agents-moa/): MoA의 연구 배경과 변형 구조
- [Hermes Agent 공식 문서](https://hermes-agent.nousresearch.com/docs): 전체 기능 개요
- [Hermes Agent GitHub 저장소](https://github.com/NousResearch/hermes-agent): 소스와 이슈 트래커

## 참고 자료

- [Hermes Agent v0.18.0 릴리스 노트](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.1): Nous Research, 조회일 2026-07-03
- [Hermes Agent v0.17.0 릴리스 노트](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.6.19): Nous Research, 조회일 2026-07-03
- [Mixture of Agents 공식 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents/): Nous Research, 조회일 2026-07-03
- [Skills 공식 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills): Nous Research, 조회일 2026-07-03
- [Memory 공식 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory): Nous Research, 조회일 2026-07-03
- [Tony Reviews Things: MoA 2.0 리뷰](https://www.tonyreviewsthings.com/hermes-agent-mixture-of-agents-20/): 커뮤니티 리뷰, 조회일 2026-07-03
- [Crypto Briefing: Hermes Agent MoA 벤치마크](https://cryptobriefing.com/hermes-agent-moa-beats-claude-opus-gpt-benchmarks/): 조회일 2026-07-03
- [Noqta: Nous Research Ships Mixture of Agents 2.0](https://noqta.tn/en/news/nous-hermes-mixture-of-agents-2-virtual-models-2026): 조회일 2026-07-03
