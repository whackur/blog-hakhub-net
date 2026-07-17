---
title: "Eval 없는 Agent Skill은 배포하지 마라: Philipp Schmid의 스킬 테스트 방법론과 SkillsBench"
meta_title: "Agent Skills Eval 방법론과 SkillsBench 정리"
description: "Google DeepMind Philipp Schmid의 스킬 eval 방법론을 정리하고, SkillsBench 논문 수치와 skill-eval-harness 등 관련 오픈소스를 함께 살펴봅니다."
date: 2026-07-18T01:00:00+09:00
lastmod: 2026-07-18T01:00:00+09:00
image: ""
categories: ["AI"]
tags: ["agent-skills", "evals", "coding-agent", "llm-agents"]
author: "whackur"
translationKey: "agent-skills-evals-skillsbench"
draft: false
---

Claude Code, Gemini CLI, Codex 같은 코딩 에이전트를 쓰다 보면 자연스럽게 스킬(Agent Skill)을 만들게 된다. 사내 코딩 컨벤션, 특정 SDK 사용법, 배포 절차 같은 지식을 Markdown 파일로 정리해 에이전트에게 물려주는 방식이다. 문제는 거의 아무도 이 스킬을 테스트하지 않는다는 점이다. 코드는 테스트 없이 배포하지 않으면서, 에이전트의 행동을 바꾸는 스킬은 몇 번 돌려 보고 "괜찮네" 수준의 감으로 배포한다.

Google DeepMind의 Philipp Schmid가 AI Engineer 강연 [Don't Ship Skills Without Evals](https://www.youtube.com/watch?v=0vphxNt4wyk)와 블로그 글 [Practical Guide to Evaluating and Testing Agent Skills](https://www.philschmid.de/testing-skills)에서 이 문제를 정면으로 다뤘다. 이 글은 강연과 원문 가이드의 방법론을 정리하고, 근거로 인용된 SkillsBench 논문, 그리고 실제로 가져다 쓸 수 있는 오픈소스 eval 도구들을 함께 살펴본다.

## Agent Skill의 구조

Agent Skill은 모델을 재훈련하거나 fine-tuning하지 않고 에이전트의 능력을 확장하는 "지시문, 스크립트, 리소스 폴더"다. [Anthropic의 Agent Skills 규격](https://agentskills.io/)이 사실상의 표준이 됐고, Claude Code와 Gemini CLI 등 여러 하네스가 같은 구조를 읽는다.

최소 단위는 `SKILL.md` 파일 하나이며 세 부분으로 구성된다.

- **frontmatter**: YAML로 쓴 `name`과 `description`. 에이전트가 이 스킬을 언제 로드할지 판단하는 트리거라서 가장 중요한 부분이다.
- **body**: API 사용법, 패턴, 함정 같은 실제 지시문.
- **resources(선택)**: `scripts/`, `examples/`, `references/` 폴더. 에이전트가 필요할 때만 읽는다.

이 구조가 progressive disclosure 패턴이다. 에이전트는 평소에 description만 보고 있다가, 관련 작업이 오면 body를 읽고, 세부가 필요하면 참조 파일까지 내려간다. 컨텍스트 토큰을 아끼면서 깊은 지식을 담는 방식이다.

## 스킬에 eval이 필요한 이유

에이전트는 비결정적이다. 같은 프롬프트를 넣어도 실행마다 다른 경로로 문제를 푼다. 스킬을 붙인 에이전트가 작업에 실패했을 때, 모델 한계인지 스킬 설계 결함인지 스킬이 아예 트리거되지 않은 것인지 구분하려면 반복 실행과 측정이 필요하다.

현실은 반대다. 커뮤니티 조사에 따르면 6,300여 개 저장소에서 47,000개가 넘는 스킬이 발견됐지만, eval을 갖춘 사례는 거의 없었고 상당수는 AI가 생성한 것이었다. Schmid의 표현을 빌리면 "테스트 없이 코드를 배포하지 않으면서, 왜 스킬은 eval 없이 배포하는가"이다.

Schmid는 실패의 절반가량이 스킬 내용이 아니라 **호출 단계**에서 발생한다고 지적한다. description이 모호하면 에이전트가 스킬을 아예 안 읽거나, 반대로 무관한 작업에서 잘못 트리거된다. 이건 스킬 body를 아무리 다듬어도 고쳐지지 않고, 테스트를 돌려야만 보인다.

## Capability 스킬과 Preference 스킬

Schmid는 스킬을 두 종류로 나눈다. 이 구분이 중요한 이유는 유지보수 전략이 다르기 때문이다.

**Capability 스킬**은 현재 모델이 일관되게 못 하는 작업을 보완한다. 최신 SDK 문법, 새 API 사용법, 모델 지식 컷오프 이후에 나온 도구가 여기 해당한다. 이 스킬은 애초에 한시적이다. 모델이 업데이트되어 그 지식을 흡수하면 스킬은 토큰 낭비이자 잠재적 혼란 요인이 된다.

**Preference 스킬**은 조직 고유의 스타일, 워크플로우, 컨벤션을 담는다. 모델이 아무리 똑똑해져도 우리 팀의 커밋 메시지 규칙이나 배포 절차를 알 수는 없으므로, 이 스킬은 계속 보호하고 관리할 자산이다.

은퇴 기준은 명확하다. **스킬을 끈 상태로 eval을 돌렸는데도 통과하면, 모델이 그 스킬의 가치를 이미 흡수한 것이므로 은퇴시킨다.** eval이 없으면 이 판단 자체가 불가능하다. eval을 유지하는 진짜 이유는 스킬을 지키기 위해서가 아니라, 모델의 진화에 맞춰 스킬을 과감하게 버리거나 고치기 위해서다.

## 좋은 스킬을 작성하는 원칙

강연과 가이드에서 제시한 작성 원칙을 정리하면 다음과 같다.

1. **description에 가장 공을 들인다.** 스킬 호출 실패의 절반이 여기서 발생한다. API 전문 용어가 아니라 사용자 의도 중심으로, '왜·언제·어떻게' 쓰는지 구체적으로 쓴다.
2. **권고가 아니라 지시로 쓴다.** "권장됩니다"보다 "항상 사용하세요"가 실제로 더 잘 작동한다.
3. **간결하게 유지한다.** `SKILL.md`는 500줄 이하. 과도한 정보는 토큰을 낭비하고 모델을 혼란시킨다.
4. **정보를 계층화한다.** 핵심은 상단에, 세부 참조는 외부 파일로 분리해 필요할 때만 읽게 한다.
5. **워크플로우 나열 대신 목표와 제약을 쓴다.** 단계별 절차가 길어지면 스킬이 아니라 스크립트로 만드는 편이 낫다.
6. **하지 말아야 할 것을 명시한다.** 부정 케이스를 정의해야 오작동을 막는다.
7. **no-op을 제거한다.** "읽기 쉬운 코드를 작성하세요"처럼 모델이 이미 아는 상식적 지시는 성능을 떨어뜨리고 비용만 늘린다.
8. **초기부터 eval로 테스트한다.** 해피 패스 5개, 부정 케이스 5개면 시작하기에 충분하다.

## Eval 하네스는 이렇게 단순해도 된다

Schmid의 핵심 메시지는 스킬 eval이 거창한 인프라를 요구하지 않는다는 것이다. 원문 가이드의 하네스는 Python 스크립트 하나 수준이다.

![테스트 케이스를 에이전트 CLI로 실행하고 regex 검사와 LLM judge로 검증한 뒤 ablation 리포트로 모으는 흐름도](/images/posts/agent-skills-evals-skillsbench/eval-harness-flow.svg)

*스킬 eval 하네스의 기본 구조. philschmid.de 가이드의 내용을 재구성한 도식.*

**1) 테스트 케이스 정의.** JSON이나 YAML로 프롬프트와 기대 검사 항목을 적는다. 스킬이 트리거되면 안 되는 부정 케이스(`should_trigger: false`)를 반드시 포함한다.

```json
{
  "id": "py_basic_generation",
  "prompt": "Write a Python script that sends text to Gemini and prints the response",
  "should_trigger": true,
  "expected_checks": ["correct_sdk", "no_old_sdk", "current_model"]
}
```

**2) 에이전트 실행.** 에이전트 CLI를 subprocess로 호출하고 JSON 출력을 파싱한다. 케이스마다 깨끗한 환경에서 3~5회 반복 실행해 단일 결과가 아니라 분포를 본다.

**3) 결정적 검사.** 출력 코드에 정규식을 돌린다. 올바른 SDK import가 있는지, 폐기된 모델 ID(`gemini-1.5-pro` 등)가 없는지, 지정한 API 호출 패턴을 따르는지 같은 검사는 regex로 충분하다. 빠르고 공짜다.

**4) 필요할 때만 LLM-as-judge.** 디자인 품질처럼 regex로 못 잡는 정성적 기준은 Pydantic 스키마를 붙인 structured output으로 LLM에게 채점시킨다. 비용과 지연이 생기므로 선택적으로 쓴다.

**5) Ablation.** 같은 테스트를 스킬 on/off 두 조건으로 돌려 통과율 차이를 잰다. 이 차이가 스킬의 기여도이고, 차이가 사라지면 은퇴 시점이다.

여기서 중요한 원칙 하나가 "경로가 아니라 결과를 평가하라"이다. 에이전트는 창의적인 방식으로 문제를 풀기 때문에, 특정 순서로 도구를 쓰는지 검사하면 멀쩡한 해법을 실패로 판정하게 된다.

이 방법의 실효성은 가이드의 사례 연구가 보여준다. Gemini Interactions API 스킬을 17개 케이스(Python 12, TypeScript 5)로 테스트했더니 초기 통과율이 66.7%였는데, description을 API 용어에서 사용자 의도 중심으로 다시 쓰고 권고문을 지시문으로 바꾸는 두 가지 수정만으로 100%에 도달했다. 실패 대부분이 스킬 내용이 아니라 트리거 문제였다는 뜻이다.

## SkillsBench: 스킬 효과를 체계적으로 잰 벤치마크

강연에서 인용된 조사와 별개로, 스킬 효과를 학술적으로 측정한 것이 [SkillsBench 논문](https://arxiv.org/abs/2602.12670)과 [benchflow-ai/skillsbench](https://github.com/benchflow-ai/skillsbench) 저장소(Apache 2.0)다.

구조는 gym 스타일이다. 태스크마다 `task.md`, Docker 환경과 스킬 폴더, 정답 스크립트(oracle), 결정적 검증기(verifier)가 붙는다. "oracle이 먼저 통과해야 에이전트를 돌린다"는 원칙으로 태스크 자체의 검증 가능성을 보장한다.

논문의 핵심 수치는 다음과 같다.

- 8개 도메인 87개 태스크에서, 사람이 다듬은(curated) 스킬은 평균 통과율을 33.9%에서 50.5%로 올렸다(+16.6%p).
- 효과는 구성에 따라 +4.1~+25.7%p로 편차가 크고, 도메인별로는 Software Engineering +4.5%p부터 Healthcare +51.9%p까지 벌어진다. 모델이 사전학습에서 약한 도메인일수록 스킬 효과가 커진다는 해석이 자연스럽다.
- 일부 태스크에서는 스킬이 오히려 성능을 떨어뜨렸다(negative delta). 스킬이 항상 공짜 이득이 아니라는 뜻이다.

특히 눈에 띄는 결과는 에이전트가 스스로 생성한 스킬(self-generated skills)이 거의 효과가 없거나 오히려 해로웠다는 점이다. 사람이 실패를 관찰하고 피드백으로 다듬은 스킬과, 모델이 자기 지식만으로 뽑아낸 스킬의 격차가 컸다. Schmid의 "eval 돌리고 description을 고쳐라"라는 실무 조언과 정확히 같은 방향의 근거다.

## 커뮤니티 반응

SkillsBench는 [Hacker News에서 364포인트, 댓글 171개](https://news.ycombinator.com/item?id=47040430)의 큰 토론을 만들었다. 주요 논점을 정리하면 다음과 같다.

- 스킬 자동 생성 실험 설정에 방법론 비판이 집중됐다. 모델이 외부 정보 없이 자기 지식만으로 스킬을 쓰게 한 것은 실무의 스킬 작성 방식과 다르다는 지적이다.
- 실무자들 사이에서는 "스킬의 진짜 가치는 실패를 관찰하고 피드백으로 개선하는 루프에 있다"는 의견이 반복됐다. 스킬은 새 정보를 만들어 내는 장치가 아니라 맥락 특화 메모장이라는 정리도 나왔다.
- Healthcare +51.9%p와 Software Engineering +4.5%p의 격차를 두고, 모델이 약한 도메인일수록 스킬이 잘 듣는다는 해석이 힘을 얻었다.
- 논문 저자도 스레드에 참여해 피드백 기반 스킬과 자동 생성 스킬의 차이를 재확인했다.

Schmid의 원문 가이드 자체도 [별도 HN 스레드](https://news.ycombinator.com/item?id=46822519)에서 논의됐고, OpenAI 역시 같은 시기에 [유사한 스킬 eval 가이드](https://developers.openai.com/blog/eval-skills)를 냈다. 스킬 테스트가 특정 벤더가 아니라 에이전트 생태계 공통의 관심사로 자리 잡는 흐름이다.

## 바로 가져다 쓸 수 있는 오픈소스

강연의 접근을 실제로 따라 해 보려는 경우 참고할 만한 프로젝트들이다.

- [philschmid.de/testing-skills](https://www.philschmid.de/testing-skills): 전용 저장소는 없지만 글 안의 Python 하네스 코드가 사실상의 레퍼런스 구현이다. 사례 연구 대상인 [google-gemini/gemini-skills](https://github.com/google-gemini/gemini-skills)와 [anthropics/claude-code](https://github.com/anthropics/claude-code)의 스킬 예제도 함께 보면 좋다.
- [benchflow-ai/skillsbench](https://github.com/benchflow-ai/skillsbench): 위에서 다룬 벤치마크. Docker 기반 태스크 정의와 verifier 구조는 자체 eval을 설계할 때 좋은 참고가 된다.
- [adewale/skill-eval-harness](https://github.com/adewale/skill-eval-harness): 스킬 on/off 페어 비교, trace 아티팩트 저장, 러너 어댑터를 지원하는 전용 하네스.
- [mgechev/skillgrade](https://github.com/mgechev/skillgrade): 스킬용 "유닛 테스트"를 표방하는 경량 도구.
- [darkrishabh/agent-skills-eval](https://github.com/darkrishabh/agent-skills-eval): agentskills.io 형식 스킬을 위한 테스트 러너.
- [aws-samples/sample-agent-skill-eval](https://github.com/aws-samples/sample-agent-skill-eval): AWS의 스킬 eval 샘플.
- [benchflow-ai/awesome-evals](https://github.com/benchflow-ai/awesome-evals): 에이전트 평가 전반의 논문·블로그·도구 큐레이션.

## 함께 보면 좋을 자료

- [AI 자기개선은 모델 밖 하네스에서 먼저 온다](/blog/harness-engineering-self-improvement/): 스킬·메모리를 포함한 하네스 구성이 에이전트 성능을 좌우한다는 관점의 글
- [DeepSWE: 코딩 에이전트를 장기 과제로 평가하는 벤치마크](/blog/deepswe-coding-agent-benchmark/): 코딩 에이전트를 검증 가능한 태스크로 평가하는 또 다른 벤치마크
- [LLM Observability 오픈소스 스택: LangSmith 대안 5종 비교](/blog/llm-observability-langsmith-alternatives/): eval을 운영 단계에서 지속하려 할 때 살펴볼 관측 도구들

## 정리

스킬은 에이전트 시대의 새로운 배포 단위가 되고 있지만, 테스트 문화는 아직 코드의 10년 전 수준이다. Schmid의 방법론에서 기억할 것은 세 가지다. 첫째, 스킬 실패의 절반은 내용이 아니라 description(트리거) 문제이므로 거기서부터 고친다. 둘째, eval은 JSON 케이스 10~20개와 regex 검사면 시작할 수 있고, 완벽한 프레임워크를 기다릴 이유가 없다. 셋째, ablation으로 스킬의 기여도를 계속 재고, 모델이 따라잡으면 미련 없이 은퇴시킨다.

SkillsBench 수치는 이 조언에 정량적 근거를 더한다. 잘 다듬은 스킬은 평균 16%p 이상의 통과율 개선을 만들지만, 대충 만든 스킬은 효과가 없거나 해롭다. 지금 가장 많이 쓰는 스킬 하나를 골라 테스트 케이스 5개부터 작성해 보는 것이 시작점이다.

## 참고 자료

- [Don't Ship Skills Without Evals](https://www.youtube.com/watch?v=0vphxNt4wyk): Philipp Schmid, AI Engineer 강연 (YouTube). 조회일 2026-07-18
- [Practical Guide to Evaluating and Testing Agent Skills](https://www.philschmid.de/testing-skills): philschmid.de. 조회일 2026-07-18
- [SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks](https://arxiv.org/abs/2602.12670): arXiv:2602.12670
- [benchflow-ai/skillsbench](https://github.com/benchflow-ai/skillsbench): GitHub, Apache 2.0
- [SkillsBench Hacker News 토론](https://news.ycombinator.com/item?id=47040430): 364포인트, 댓글 171개. 조회일 2026-07-18
- [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills): OpenAI Developers
- [Agent Skills 규격](https://agentskills.io/): agentskills.io
