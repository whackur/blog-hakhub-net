---
title: "Glamsterdam의 새 가스 모델: EIP-8037 상태 가스, EIP-8038 접근 비용, EIP-2780 기본 가스"
meta_title: ""
description: "Glamsterdam이 가스를 실행 가스와 상태 가스로 나누고, 상태 접근 비용을 올리고, 고정 21,000 기본 비용을 분해하는 방식. 2026년 10월 15일 기준 스펙에서 확인한 파라미터, 리저버 모델, 환급과 되돌리기, 개발자 영향, 아직 정해지지 않은 것."
date: 2026-10-15T01:19:45+09:00
lastmod: 2026-10-15T01:19:45+09:00
image: "/images/posts/glamsterdam-gas-model/glamsterdam-gas-cover.png"
categories: ["Blockchain"]
tags: ["ethereum", "glamsterdam", "gas", "evm", "eip-8037", "eip-8038", "eip-2780"]
author: "whackur"
translationKey: "glamsterdam-gas-model"
draft: false
---

이더리움의 다음 네트워크 업그레이드 Glamsterdam은 개별 연산 가격만 바꾸지 않습니다. 트랜잭션 가스를 세는 방식 자체가 달라집니다. 핵심은 세 개의 제안입니다. [EIP-8037](https://eips.ethereum.org/EIPS/eip-8037)은 상태 생성에 별도의 가스 차원을 주고 바이트 단위로 가격을 매깁니다. [EIP-8038](https://eips.ethereum.org/EIPS/eip-8038)은 이미 존재하는 상태를 읽고 쓰는 비용을 올립니다. [EIP-2780](https://eips.ethereum.org/EIPS/eip-2780)은 고정 21,000 기본(intrinsic) 비용을 이름 붙은 항목의 합으로 바꾸고, 상태에 따라 달라지는 부분을 유효성 검사 밖으로 옮깁니다.

하나씩 보면 흔한 가스 재조정입니다. 셋이 함께 들어오면 트랜잭션의 가스 예산 구조가 바뀝니다. `tx.gas`는 여전히 숫자 하나지만 프로토콜이 이를 두 풀(pool)로 나누고, `GAS` 연산자는 그중 하나만 봅니다. `gasleft()`로 계산하는 컨트랙트, 가스 한도를 하드코딩한 지갑, 번들러, 블록 빌더, RPC 시뮬레이터 모두 확인할 거리가 생깁니다.

이 글은 2026년 10월 15일 시점의 세 스펙을 차례로 정리합니다. 모든 수치는 ethereum/EIPs 커밋 [`5ef3801`](https://github.com/ethereum/EIPs/commit/5ef380124bd68d09c02fa90d0de0f2455f37d5ee)의 EIP 원문에서 가져왔고, [ethereum/execution-specs](https://github.com/ethereum/execution-specs/tree/16898000911c1e3caa57be08509536c10ae92d3e/src/ethereum/forks/amsterdam)의 Amsterdam 포크 코드와 대조했습니다. 공개 자료끼리 내용이 다른 곳은 따로 밝혀 둡니다.

## 2026년 10월 15일 기준 상태

이 포크를 다루는 글에서는 세 종류의 "상태"가 자주 섞입니다. 서로 다른 질문에 대한 답이라 나눠서 봅니다.

**EIP 프로세스 상태.** EIP-8037, EIP-8038, EIP-2780은 모두 `Last Call`이고 `last-call-deadline`은 2026-11-01입니다. Last Call 전환은 2026-10-06 날짜의 커밋 하나로 들어갔습니다([ethereum/EIPs PR #12442](https://github.com/ethereum/EIPs/pull/12442)). Last Call은 본문이 거의 확정됐다는 뜻이지 동결됐다는 뜻은 아닙니다. EIP-8037 본문에도 의존하는 EIP-8038 값이 "아직 최종이 아니다(not yet final)"라고 적혀 있고, EIP-2780은 자기 기본값을 "잠정치(provisional)"라고 부릅니다.

**포크 포함 여부.** Glamsterdam 메타 EIP인 [EIP-7773](https://eips.ethereum.org/EIPS/eip-7773)은 세 EIP를 모두 "포함 예정(Scheduled for Inclusion, SFI)" 목록에 올려 두었습니다. EIP-8037은 2026년 1월 포함 검토(CFI) 상태가 됐고, 토론 스레드의 저자 답변에 따르면 6월에는 이미 SFI였습니다. EIP-2780과 EIP-8038은 2026-08-05 EIP-7773 커밋에서 CFI에서 SFI로 옮겨졌습니다. EIP-7773 자체는 `Review` 상태입니다.

**네트워크 활성화.** EIP-7773의 활성화 표에는 Sepolia 한 줄만 채워져 있습니다. epoch 353024, 타임스탬프 1791294816(2026-10-06 13:53:36 UTC)입니다. Hoodi와 Mainnet 칸은 비어 있고, 메타 EIP는 클라이언트 팀이 시점을 정하면 채운다고 적고 있습니다. [이더리움 재단의 테스트넷 공지](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement)도 같은 내용입니다. Hoodi와 메인넷 활성화 날짜는 아직 정해지지 않았고, 이 공지는 메인넷 업그레이드 일정을 잡는 공지가 아니라고 명시합니다.

정리하면 "포함 예정"은 범위에 대한 결정이지 메인넷 날짜가 아닙니다. 메인넷 날짜를 밝힌 공식 자료는 아직 없습니다. 제가 10월 14일에 읽은 ethereum.org [Glamsterdam 페이지](https://ethereum.org/en/roadmap/glamsterdam/)(최종 수정일 9월 14일 표기)는 "메인넷 2026년 4분기 예상, 날짜 미확정"이라고 적었는데, 이건 예상이지 일정이 아닙니다. 커뮤니티 참여자 PyraVim은 [Ethereum Magicians에](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/50) 올린 글(50번 글, 2026년 10월 8일)에서 Glamsterdam이 예정 시각에 Sepolia에서 활성화됐다고 쓰고 첫 몇 시간의 측정치를 올렸습니다. 쓸모 있는 현장 데이터지만 관측자 한 명의 기록입니다.

## 가스 스케줄을 바꾸는 이유

세 EIP의 동기(Motivation) 절은 두 가지 문제를 가리킵니다.

첫째는 **상태 증가**입니다. EIP-8037에 따르면 2026년 1월 Geth 노드의 상태 DB는 약 390 GiB였습니다. 블록 가스 한도가 30M에서 60M으로 오른 뒤 하루 평균 새 상태는 약 105 MiB에서 약 326 MiB로 늘었고, 연간으로는 약 116 GiB입니다. 저자들은 이 반응이 선형이 아니었다고(가스 한도 2배에 하루 상태 증가 약 3배) 짚고, 이를 200M 가스 한도로 외삽하면 연간 약 387 GiB가 되어 노드 성능이 떨어지기 시작하는 650 GiB 선을 1년 안에 넘는다고 봅니다. 상태 생성 가격도 제각각이었습니다. 코드 배포는 새 바이트당 약 200 가스, 새 스토리지 슬롯은 바이트당 약 313 가스였습니다.

둘째는 **상태 접근**입니다. EIP-8038은 접근 비용이 마지막으로 오른 것이 2021년 3월 Berlin 포크의 [EIP-2929](https://eips.ethereum.org/EIPS/eip-2929)였고 그 뒤로 상태가 크게 늘었다고 지적합니다. DB가 커지면 계정이나 슬롯을 읽는 시간이 길어지지만 가스 비용은 그대로였습니다. `EXTCODESIZE`와 `EXTCODECOPY`는 DB를 두 번 읽는데도 `BALANCE`와 같은 값을 냈습니다.

트랜잭션 가격에도 작은 문제가 하나 있습니다. EIP-2780은 고정 21,000이 값이 0인 호출과 계정을 새로 만드는 송금을 똑같이 취급해서, 앞의 것은 비싸게 뒤의 것은 싸게 받는다고 봅니다.

공통점은 이런 연산이 실제 부담에 비해 싼 상태로는 가스 한도를 계속 올릴 수 없다는 것입니다. 재단의 [재조정 테스트 글](https://blog.ethereum.org/2026/08/24/glamsterdam-repricing-testing)은 이번 재조정을 가스 한도를 더 올리기 위한 전제 조건이라고 표현합니다.

## 세 EIP 한눈에 보기

| EIP | 공식 제목 | 바꾸는 것 | 가스 차원 |
| --- | --- | --- | --- |
| [EIP-8037](https://eips.ethereum.org/EIPS/eip-8037) | State Creation Gas Cost Increase | 새 상태를 바이트 단위로 가격 책정(`CPSB` = 1,530), 별도 상태 가스 차원과 리저버 모델 도입 | 상태 가스(일부 실행 가스) |
| [EIP-8038](https://eips.ethereum.org/EIPS/eip-8038) | State-access gas cost update | 콜드 계정 접근 인상, 쓰기 비용 명시, `EXTCODESIZE`/`EXTCODECOPY` 두 번째 읽기 과금 | 실행 가스 |
| [EIP-2780](https://eips.ethereum.org/EIPS/eip-2780) | Resource-based intrinsic transaction gas | 21,000을 이름 붙은 항목으로 분해, 상태 의존 비용을 런타임 단계로 이동 | 실행 가스(기본), 두 차원 모두(런타임) |

의존 관계는 순환합니다. EIP-8038은 EIP-8037을, EIP-8037은 EIP-2780과 EIP-8038을, EIP-2780은 나머지 둘을 요구합니다. 실제로는 한 묶음으로 들어갑니다. 스크린샷이나 요약에서는 EIP-8037을 "State Gas"로 줄여 부르기도 하지만 공식 제목은 위 표의 것입니다.

## EIP-8037: 상태 생성에 별도 가스 차원

### 상태 바이트당 비용

EIP-8037은 단가 하나를 도입합니다. `CPSB`(cost per state byte), 값은 **1,530 가스**입니다. 상태를 만드는 모든 연산은 바이트 수 × `CPSB`로 가격이 정해지고, 바이트 수는 고정입니다.

| 파라미터 | 값 | 의미 |
| --- | --- | --- |
| `CPSB` | 1,530 | 새 상태 1바이트당 가스 |
| `STATE_BYTES_PER_STORAGE_SET` | 64 | 32바이트 슬롯 해시 키 + 32바이트 값 |
| `STATE_BYTES_PER_NEW_ACCOUNT` | 120 | 32바이트 키 + nonce 8 + balance 16 + code hash 32 + storage root 32 |
| `STATE_BYTES_PER_AUTH_BASE` | 23 | EIP-7702 위임 표시(`0xef0100` + 20바이트 주소) |
| `SYSTEM_MAX_SSTORES_PER_CALL` | 16 | 시스템 컨트랙트 호출용 여유분 |
| `TX_MAX_TOTAL_GAS_LIMIT` | 4,294,967,295 (2^32 − 1) | `tx.gas`의 새 절대 상한 |

EIP는 이 바이트 수가 리프와 키만 센 것이고 트라이 중간 노드는 빠져 있어서 실제 증가량의 하한이라고 밝힙니다.

1,530은 Rationale 절의 짧은 계산에서 나옵니다. 기준 블록 가스 한도 150M에서 연간 상태 증가 120 GiB를 목표로 잡고, 상태 가스가 평균적으로 한도의 50%를 쓴다고 가정합니다(기본 수수료는 한도의 절반인 목표치로 수렴하기 때문). 슬롯은 12초, 연간 블록은 2,628,000개입니다. 그러면 75,000,000 × 2,628,000 ≈ 1.971 × 10^14 가스가 1년 치이고, 이를 120 × 2^30 바이트로 나누면 바이트당 약 1,530 가스입니다. EIP는 150M을 작성 당시 한도 60M과 앞으로 예상하는 300M의 중간값이라고 설명합니다. 산출에 쓰는 기준값일 뿐, 현재 메인넷 가스 한도도 아니고 앞으로의 한도를 예측한 값도 아닙니다. Rationale에는 다른 블록 한도에서의 증가율 표도 있는데, 그 표는 블록이 꽉 찬 최악의 경우라고 적으면서 위 산출은 50% 사용을 가정해서 서로 맞지 않습니다. 그래서 이 글에서는 그 표의 수치를 옮기지 않았습니다. 2025년 11월 [Magicians 스레드](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694)(8~13번 글)에서는 가스 한도에 따라 움직이는 가격이나 실제 상태 사용량에 따라 움직이는 가격 같은 대안도 논의됐지만, 현재 본문은 고정값을 쓰고 나중 EIP에서 다시 산출할 수 있다고만 적습니다.

### 새 상태의 가격

곱해 보면 가장 자주 마주칠 세 경우의 상태 가스가 나옵니다.

- **새 계정**: 120 × 1,530 = 183,600. 기존 `GAS_NEW_ACCOUNT`는 25,000이었습니다(약 7배).
- **새 스토리지 슬롯**: 64 × 1,530 = 97,920. 기존 `GAS_STORAGE_SET`은 20,000이었습니다(약 5배).
- **24 kB 컨트랙트 배포**: 계정과 코드 바이트를 합쳐 37,784,880. 이전에는 4,947,200이었습니다(약 8배, EIP가 밝힌 수치).

이 값은 상태 가스만입니다. EIP-8038의 실행 가스(`ACCOUNT_WRITE`, `STORAGE_WRITE`, 코드 해시 비용)는 따로 더해집니다. 스펙은 기존 상수를 상태 가스 몫과, 필요하면 EIP-8038 실행 가스 몫으로 하나씩 바꿉니다. `GAS_CREATE`, `GAS_NEW_ACCOUNT`, 7702의 `PER_EMPTY_ACCOUNT_COST`는 모두 120 × `CPSB`가 되고, `GAS_STORAGE_SET`은 64 × `CPSB`, 7702의 `PER_AUTH_BASE_COST`는 23 × `CPSB`에 실행 기본값 7,816을 더한 값이 됩니다. 코드 저장 비용은 바이트당 `CPSB`에 32바이트 워드당 6가스의 해시 비용이 붙습니다.

코드도 다른 상태와 같은 값을 냅니다. 바이트당 200이 아니라 1,530입니다. 동기 절은 클라이언트가 중복 바이트코드를 한 번만 저장하는데도 같은 값을 낸다고 지적하지만, 현재 스펙에 중복 할인은 없습니다.

### 두 차원, 하나의 가스 한도

구조적으로 가장 큰 변화는 가스가 **실행 가스(execution gas)**와 **상태 가스(state gas)** 두 차원으로 나뉜다는 점입니다. 상태를 만드는 연산은 "새 상태" 몫을 상태 가스에, 접근과 쓰기 몫을 실행 가스에 냅니다. 나머지는 전부 실행 가스입니다.

사용자는 둘 다 냅니다. 트랜잭션 총비용은 두 차원의 합이고, 수수료 계산 방식은 지금과 같습니다. 최종 사용 가스(환급 상한과 calldata 하한까지 적용한 값, 영수증의 `gasUsed`)에 트랜잭션의 실효 가스 가격(`effectiveGasPrice`, 실제로 낸 기본 수수료와 우선순위 수수료의 합)을 곱합니다. 그래서 가스 단위가 5배나 7배로 늘어도 ETH나 달러 비용이 그만큼 고정적으로 늘어나는 것은 아닙니다. 기본 수수료는 블록마다 수요에 따라 움직이고 ETH 가격도 따로 움직입니다. EIP-8037은 예시를 ETH로 바꿀 때 2025년 12월과 2026년 1월에 관측한 평균 기본 수수료 0.08 gwei를 쓰는데, 예시일 뿐 전망치가 아닙니다. 이 글의 다른 가스 수치도 마찬가지입니다.

바뀌는 것은 어떤 한도가 어디에 걸리느냐입니다.

- [EIP-7825](https://eips.ethereum.org/EIPS/eip-7825)의 트랜잭션당 상한(`TX_MAX_GAS_LIMIT`, 16,777,216)은 이제 실행 가스에만 걸립니다.
- `tx.gas` 전체는 `TX_MAX_TOTAL_GAS_LIMIT`(2^32 − 1)로 제한됩니다.
- 블록 헤더의 `gas_used`는 `max(block_execution_gas_used, block_state_gas_used)`가 됩니다. 블록 유효성과 기본 수수료 갱신 모두 이 값을 씁니다.

확장성 논리는 마지막 규칙에 있습니다. 블록 가스 한도가 병목인 자원 하나만 묶기 때문에, 상태 생성으로 꽉 찬 블록이 실행 예산을 잡아먹지 않고 반대도 마찬가지입니다. 7825 상한을 실행 가스에만 거는 이유도 EIP가 설명합니다. `CPSB` = 1,530에 기존 단일 상한을 그대로 두면, 생성자 실행 예산을 5M으로 잡았을 때 배포 가능한 코드가 약 7,564바이트에서 막힙니다. 차원을 나누면 2^32 − 1 총상한 아래에서 한 트랜잭션으로 약 2.8 MB의 코드 저장 비용을 낼 수 있습니다. 같은 Glamsterdam에 포함 예정인 [EIP-7954](https://eips.ethereum.org/EIPS/eip-7954)의 65,536바이트 한도의 약 43배입니다.

가스 쪽에서 트랜잭션이 포함 전에 통과해야 하는 검사는 이렇습니다. 지금처럼 `tx.gas`가 `max(intrinsic_gas, calldata_floor_gas_cost)` 이상이어야 하고, `tx.gas <= TX_MAX_TOTAL_GAS_LIMIT`, `max(intrinsic_gas, calldata_floor_gas_cost) <= TX_MAX_GAS_LIMIT`를 만족해야 하며, 차원별로 블록 잔여 예산에 들어가야 합니다(실행은 `min(TX_MAX_GAS_LIMIT, tx.gas)`, 상태는 `tx.gas`로 비교). 첫 검사에 실패하면 execution-specs의 `validate_transaction`이 "insufficient intrinsic gas" 오류를 냅니다. 이 목록은 가스 규칙만 다룬 것이고, nonce, 잔액, 수수료 상한, 트랜잭션 타입 같은 기존 검사는 그대로 적용됩니다.

### 리저버 모델

트랜잭션에는 가스 필드가 하나뿐이라 `tx.gas` 중 어디까지가 실행 예산이고 어디부터가 상태 예산인지 정하는 규칙이 필요합니다. EIP-8037은 이를 **리저버(reservoir) 모델**이라고 부릅니다.

```python
evm_gas = tx.gas - intrinsic_gas
execution_gas_budget = TX_MAX_GAS_LIMIT - intrinsic_gas
gas_left = min(execution_gas_budget, evm_gas)
state_gas_reservoir = evm_gas - gas_left
```

7825 상한까지는 익숙한 실행 풀인 `gas_left`가 되고, 상한을 넘는 몫은 `state_gas_reservoir`에 들어갑니다. [execution-specs](https://github.com/ethereum/execution-specs/blob/16898000911c1e3caa57be08509536c10ae92d3e/src/ethereum/forks/amsterdam/vm/gas.py)의 `allocate_evm_gas` 구현도 이 네 줄과 같습니다.

두 풀의 규칙은 이렇습니다.

- 실행 비용은 `gas_left`에서만 나갑니다.
- 상태 비용은 리저버에서 먼저 나갑니다. 리저버가 비면 나머지를 `gas_left`에서 가져가고, 빌려 쓴 양은 프레임 로컬 카운터 `state_gas_from_gas_left`에 기록합니다.
- 리저버는 자식 호출에 **통째로** 넘어갑니다. 63/64 규칙은 `gas_left`에만 적용됩니다. 자식이 도는 동안 부모는 리저버를 하나도 갖지 않고, 자식이 끝나면 돌려받습니다.
- `GAS` 연산자는 `gas_left`만 돌려줍니다. execution-specs 코드에서도 `GAS` 명령은 `evm.gas_meter.gas_left` 하나만 스택에 넣습니다.
- `SSTORE`의 stipend 검사(호출 stipend 2,300보다 많이 남아 있어야 `SSTORE`가 실행됨)도 `gas_left`만 봅니다. 리저버가 아무리 커도 이 검사를 통과하는 데는 도움이 되지 않습니다.

놓치기 쉬운 결과가 하나 있습니다. `tx.gas`가 16,777,216 이하인 트랜잭션은 리저버가 0에서 시작합니다. 이런 트랜잭션의 상태 비용은 모두 `gas_left`에서 나가고, `gasleft()`도 바로 그 값을 보여 줍니다. 리저버는 7825 상한보다 큰 가스를 요청한 트랜잭션에서만 의미가 있습니다.

![Glamsterdam 트랜잭션 가스 흐름: tx.gas는 상태와 무관한 기본 가스(EIP-2780)와 calldata 하한 중 큰 값 이상이어야 하고, 그 값은 실행 상한 16,777,216 이하여야 한다. 가스와 무관한 기존 유효성 검사도 함께 적용된다. 그다음 tx.gas가 16,777,216에서 기본 가스를 뺀 값까지는 gas_left로, 초과분은 state_gas_reservoir로 나뉜다(EIP-8037). 이어서 실행 전 런타임 비용(여기서 가스가 떨어져도 트랜잭션은 포함되고 실행 전 변경만 되돌아간다)과 연산자별 비용을 낸다. 상태 비용은 리저버에서 먼저 나가고 모자라면 gas_left로 넘친다. 새 스토리지 슬롯은 원래 값과 현재 값이 0이고 새 값이 0이 아닐 때만 상태 가스를 낸다. 정산에서는 실행 가스와 상태 가스를 따로 집계하고, 송신자는 최종 사용 가스에 실효 가스 가격을 곱한 수수료를 내며, 블록 헤더 gas_used는 두 블록 합계 중 큰 값이다.](/images/posts/glamsterdam-gas-model/glamsterdam-gas-flow.svg "Glamsterdam 트랜잭션 가스 흐름")

*ethereum/EIPs 커밋 `5ef3801`(Last Call, 2026-10-06)의 EIP-2780, EIP-8037, EIP-8038 본문을 바탕으로 직접 다시 그린 도식입니다. 값은 execution-specs Amsterdam 포크 코드와 대조했습니다. 메인넷 전에 파라미터가 바뀔 수 있고, 메인넷 활성화 일정은 잡혀 있지 않습니다.*

### 리필, 되돌리기, 중단

상태 생성이 취소되면 상태 가스가 돌아옵니다. EIP-8037은 이를 **리필(refill)**이라 부르고 환급(refund) 카운터와 구분합니다. 트랜잭션 시작 때 0이었고 트랜잭션 안에서 0 → x → 0으로 돌아간 스토리지 슬롯, 실패한 값 전송 `CALL`, 프레임이 되돌려진 `CREATE`가 예입니다.

리필은 후입선출(LIFO) 순서입니다. 비용을 리저버에서 먼저, `gas_left`에서 나중에 가져가므로 리필은 `gas_left`부터(`state_gas_from_gas_left`만큼까지) 채우고 남는 몫을 리저버에 돌려줍니다. 리필은 트랜잭션의 상태 가스 누계인 `evm_state_gas_used`도 줄입니다.

되돌리기(revert)와 예외적 중단(exceptional halt)은 다른 방식을 씁니다. 각 프레임은 진입 시점의 리저버 값을 `state_gas_baseline`으로 기록해 둡니다. 롤백하면 프레임의 상태 가스를 이 기준선으로 복원하고, `gas_left`에서 빌린 몫은 `gas_left`로 돌려줍니다. 두 실패의 차이는 지금과 같습니다. revert는 남은 `gas_left`를 부모에게 돌려주고, 예외적 중단은 소진합니다.

자식 프레임이 성공하면 자식이 빌린 양이 부모의 기록에 합쳐지고, 프레임은 아직 갚을 몫만큼 리저버에서 `gas_left`로 상태 가스를 옮깁니다. EIP는 이 단계가 필요한 이유를 설명합니다. `SSTORE`의 "원래 값"은 트랜잭션 시작 시점의 값이라, 한 프레임이 앞선 프레임이 할당한 슬롯을 지울 수 있고, 그러면 비용을 내지 않은 프레임에서 리필이 일어납니다. 병합 단계는 두 풀이 서로 섞여 어긋나지 않게 막습니다.

예외는 [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) 권한 위임(authorization)입니다. 최상위 프레임이 시작되기 전에 적용되고 그 프레임이 되돌려져도 취소되지 않으므로, 여기에 낸 상태 가스는 리필하면 안 됩니다. 최상위 프레임은 권한 위임 비용을 낸 뒤의 값을 기준선으로 잡고, 그 비용 중 `gas_left`에서 나간 몫은 별도 카운터 `state_gas_committed`에 "확정"으로 기록해 리필 대상에서 뺍니다. 최상위 프레임이 시작되기도 전에 트랜잭션이 실패하면 위임을 포함한 실행 전 단계 전체가 롤백되고, 그 상태 가스도 모두 리필됩니다.

### CALL, CREATE, SELFDESTRUCT

계정 생성 비용(120 × `CPSB` = 183,600)은 어디서나 조건부입니다. 잔액이 0이 아니거나, nonce가 0이 아니거나, 코드가 있으면 존재하는 계정입니다([EIP-161](https://eips.ethereum.org/EIPS/eip-161)).

- **존재하지 않는 계정으로 값을 보내는 `CALL*`**: 자식 프레임 직전에 부과합니다. 진입 전에 실패하거나(잔액 부족, 깊이 한도) 자식이 revert 또는 중단되면 리필합니다.
- **`CREATE`/`CREATE2`**: 잔액, nonce 오버플로, 깊이 검사를 통과하고, [EIP-684](https://eips.ethereum.org/EIPS/eip-684) 충돌 검사를 겸하는 대상 주소 읽기 한 번을 마친 뒤, 남은 가스의 63/64를 넘기기 *전에* 생성하는 쪽 프레임에서 부과합니다. 일부가 `gas_left`에서 나가면 자식이 받는 가스가 줄어듭니다. 대상이 이미 존재하면(예를 들어 잔액이 있으면) 계정 비용은 없고 코드 저장 비용 `L × CPSB`만 냅니다. 생성 프레임이 실패하면 리필합니다. EIP-684의 주소 충돌은 대상에 0이 아닌 nonce나 코드가 있어야 성립합니다(잔액이나 남은 스토리지만으로는 충돌이 아님). 이런 대상은 이미 존재하는 계정이라 계정 비용이 붙지 않았고, 충돌하면 생성 프레임이 예외적으로 중단되어 넘겨받은 가스를 소진합니다.
- 존재하지 않는 계정으로 잔액을 보내는 **`SELFDESTRUCT`**는 실행 시점에 183,600을 냅니다. 같은 트랜잭션에서 만든 계정의 `SELFDESTRUCT`는 상태 가스를 **리필하지 않습니다**.

`CREATE` 시점은 의도된 선택입니다. 예전 판은 생성 프레임 전에 무조건 부과하고 나중에 돌려줬습니다. 저자들은 리필 경로가 여럿 사라지고 `CREATE`가 `CALL`과 같은 방식이 된다는 이유로 조건부 방식으로 바꿨습니다. 자식 프레임 뒤에 부과하지 않는 이유도 Rationale에 있습니다. 부모 실행 가스의 최대 63/64가 자식에게 가므로, 끝나고 부과하면 멀쩡히 성공할 배포가 마지막 단계에서 실패할 수 있습니다.

같은 트랜잭션 `SELFDESTRUCT` 규칙은 아직 논쟁 중입니다. 한 [Magicians 글](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/46)(46번 글, 2026년 8월 26일)에 따르면 이 경우의 리필은 재조정 회의에서 한 번 합의되고 구현됐다가 bal-devnet-7에서 다시 빠졌습니다. 글쓴이는 입금 주소 정리(sweep)용 실행기 같은 일회성 컨트랙트가 상태에 남지도 않을 계정에 183,600을 다 낸다고 주장합니다. 이 주제는 스펙 PR과 함께 [ACDE #244 안건](https://github.com/ethereum/pm/issues/2197)(2026년 8월 27일 회의)에 올라갔습니다. 이 글의 스냅샷 시점에 EIP 본문에는 그런 리필이 없습니다.

### 정산, 환급, calldata 하한

트랜잭션이 끝나면 이렇게 계산합니다.

```python
tx_gas_used_before_refund = tx.gas - tx_output.gas_left - tx_output.state_gas_reservoir
tx_gas_refund = min(tx_gas_used_before_refund // 5, tx_output.refund_counter)
tx_gas_used_after_refund = tx_gas_used_before_refund - tx_gas_refund
tx_gas_used = max(tx_gas_used_after_refund, calldata_floor_gas_cost)
```

환급 상한은 20% 그대로이고, [EIP-7623](https://eips.ethereum.org/EIPS/eip-7623) calldata 하한은 환급 뒤에 적용됩니다. 쓰지 않은 리저버는 쓰지 않은 `gas_left`처럼 송신자에게 돌아갑니다. 하한 자체를 움직이는 변경도 둘 있습니다. 함께 포함 예정인 [EIP-7976](https://eips.ethereum.org/EIPS/eip-7976)은 하한 비용을 올리고, EIP-2780은 하한 공식 안의 고정 21,000을 트랜잭션의 분해된 기본값(`TX_BASE_COST`에, 적용되는 수신자 항목과 값 전송 항목을 더한 값)으로 바꿉니다.

블록 카운터에서 상태 가스는 순(net) `evm_state_gas_used`이고, 실행 가스는 나머지에 calldata 하한을 적용한 값입니다. 하한은 실행 몫하고만 비교하므로, 상태 생성으로 트랜잭션을 부풀려도 하한을 피할 수 없습니다. Glamsterdam에는 블록 가스 집계에서 환급을 빼지 않도록 바꾸는 [EIP-7778](https://eips.ethereum.org/EIPS/eip-7778)도 포함 예정입니다. EIP-8037은 둘을 함께 적용하는 판(실행 가스를 환급 전 기준으로 계산)을 따로 명시하고, execution-specs Amsterdam 코드는 이 판을 구현합니다. EIP는 상태 가스 리필이 7778이 말하는 환급이 아니라고 봅니다. 리필된 상태는 애초에 만들어지지 않았으므로 상태 차원에서는 계속 순액으로 계산합니다.

영수증을 파싱한다면 하나 기억해 둘 점이 있습니다. `cumulative_gas_used`는 이제 블록 헤더의 `gas_used`가 아니라 각 트랜잭션이 실제로 낸 가스의 누적합입니다. 차원이 둘이라 두 값이 달라집니다.

블록 시작 때마다 호출되는 시스템 컨트랙트([EIP-2935](https://eips.ethereum.org/EIPS/eip-2935), [EIP-4788](https://eips.ethereum.org/EIPS/eip-4788), [EIP-7002](https://eips.ethereum.org/EIPS/eip-7002), [EIP-7251](https://eips.ethereum.org/EIPS/eip-7251))의 한도는 30,000,000 + 64 × 1,530 × 16, 즉 31,566,720으로 늘어납니다. 늘어난 1,566,720은 리저버에 들어갑니다. 시스템 호출은 여전히 어느 블록 카운터에도 잡히지 않습니다.

## EIP-8038: 접근 비용과 쓰기 비용

### 세 가지 비용 요소

EIP-8038은 상태를 건드리는 비용을 최대 세 요소의 합으로 다시 씁니다.

1. **접근(access)**: 계정이나 슬롯을 불러오는 비용. `COLD_ACCOUNT_ACCESS`, `COLD_STORAGE_ACCESS`, `WARM_ACCESS`(EIP-2929 상수의 새 이름). 웜/콜드 판정 규칙은 그대로입니다.
2. **쓰기(write)**: 리프 값을 바꾸는 비용. 새 파라미터 `STORAGE_WRITE`와 `ACCOUNT_WRITE`입니다. 이전에는 `SSTORE_RESET_GAS`, `G_callvalue` 같은 합성 상수 안에 숨어 있었습니다.
3. **상태 생성**: 새 리프를 추가하는 비용. EIP-8037의 상태 가스이고 EIP-8038은 이 값을 건드리지 않습니다.

두 쓰기 비용은 규칙이 다릅니다. `STORAGE_WRITE`는 트랜잭션 단위 순액 계산입니다. 트랜잭션이 끝날 때 값이 바뀐 슬롯은 한 번 내고, 원래 값으로 되돌아온 슬롯은 돌려받습니다. `ACCOUNT_WRITE`는 연산마다 부과하고 추적하지 않습니다. 같은 주소에 값을 세 번 보내면 세 번 냅니다(7702 처리에는 EIP-2780의 별도 규칙이 있습니다).

### 새 파라미터 값

| 파라미터 | 요소 | 이전 | 이후 | 변화 |
| --- | --- | --- | --- | --- |
| `COLD_ACCOUNT_ACCESS` | 접근 | 2,600 | 3,000 | +15% |
| `COLD_STORAGE_ACCESS` | 접근 | 2,100 | 2,100 | 0 |
| `WARM_ACCESS` | 접근 | 100 | 100 | 0 |
| `ACCOUNT_WRITE` | 쓰기 | 6,700(환산) | 9,000 | +34% |
| `STORAGE_WRITE` | 쓰기 | 2,800(환산) | 10,000 | +257% |
| `CREATE_ACCESS` | 접근 + 쓰기 | 7,000(환산) | 12,000 | +71% |
| `STORAGE_CLEAR_REFUND` | 환급 | 4,800 | 11,616 | +142% |
| `ACCESS_LIST_STORAGE_KEY_COST` | 선불 접근 | 1,900 | 2,000 | +5% |
| `ACCESS_LIST_ADDRESS_COST` | 선불 접근 | 2,400 | 2,900 | +21% |

새 파라미터 셋의 "이전" 값은 EIP가 기존 합성 상수에서 뽑아낸 환산치입니다. 6,700 = `G_callvalue` 9,000 − stipend 2,300, 2,800 = `SSTORE_RESET_GAS` 5,000 − 2,100 − 100, 7,000 = `G_create` 32,000 − `G_newaccount` 25,000입니다. EIP는 기존 스케줄이 깔끔하게 나뉘지 않아서 근사치라고 밝힙니다.

몇몇 값은 다른 값에서 유도되고, execution-specs 코드도 같은 식으로 계산합니다. `STORAGE_CLEAR_REFUND = (STORAGE_WRITE + COLD_STORAGE_ACCESS) × 4800/5000`, 액세스 리스트 비용은 콜드 비용에서 `WARM_ACCESS`를 뺀 값(그래서 미리 등록해도 콜드 접근보다 비싸지지 않음), `CREATE_ACCESS = ACCOUNT_WRITE + COLD_ACCOUNT_ACCESS`입니다.

### SSTORE 실제 비용

EIP-8038은 새 `SSTORE` 비용을 슬롯의 *원래 값*(트랜잭션 시작 시점)과 *현재 값*(이 `SSTORE` 직전)으로 정의합니다.

- 접근 비용(콜드 또는 웜)은 예전과 같습니다.
- 새 값이 현재 값과 다르고 현재 값이 아직 원래 값과 같으면(트랜잭션 시작 값에서 처음 바뀌는 쓰기) `STORAGE_WRITE`를 더합니다.
- 원래 값이 0이고, 현재 값도 0이고, 새 값이 0이 아닐 때만 `GAS_STORAGE_SET`(상태 가스 97,920)을 더합니다.

상태 가스에는 세 조건이 모두 필요합니다. 트랜잭션 시작 때 0이 아니던 슬롯을 지웠다가 다시 값을 넣으면(`x → 0 → y`) 새 상태가 생기지 않으므로 상태 가스를 내지 않습니다. 이 쓰기는 접근 비용 말고는 아래에서 설명할 삭제 환급을 되돌리기만 합니다. 위 파라미터로 계산한 사례입니다.

| 쓰기 | Glamsterdam 이전 | 실행 가스 | 상태 가스 | 합계 |
| --- | --- | --- | --- | --- |
| 기존 비영(非零) 슬롯 갱신, 웜 | 2,900 | 100 + 10,000 = 10,100 | 0 | 10,100 |
| 기존 비영 슬롯 갱신, 콜드 | 5,000 | 2,100 + 10,000 = 12,100 | 0 | 12,100 |
| 새 슬롯(원래 0, 현재 0, 새 값 x), 콜드 | 22,100 | 12,100 | 97,920 | 110,020 |
| 한 트랜잭션 안에서 설정 후 삭제(원래 0: 0 → x → 0) | | 웜 100, `STORAGE_WRITE` 환급 | 97,920 리필 | 환급 상한 안에서 접근 비용만 |

사람들이 잘 놓치는 건 위의 두 줄입니다. EIP-8038은 새 상태가 전혀 없는 평범한 스토리지 갱신의 실행 가스를 약 2.4~3.5배로 올립니다. [Sepolia 커뮤니티 측정](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/50)에서도 정확히 이 값(웜 2,900 → 10,100, 콜드 5,000 → 12,100)이 나왔고, DEX 스왑이 풀의 스토리지 갱신에서 가스가 모자라 실패한 사례가 확인됐습니다.

환급 규칙도 엄격해졌습니다. 트랜잭션 시작 때 0이 아니던 슬롯을 지우면 `STORAGE_CLEAR_REFUND`가 더해지고, 같은 트랜잭션에서 다시 0이 아닌 값을 넣으면 그 환급을 뺍니다. 원래 값으로 되돌리면 `STORAGE_WRITE`를 환급합니다. EIP가 밝힌 목표는 `x → 0 → x` 같은 왕복이 결코 이득이 되지 않게 하는 것입니다. 이 되돌림 규칙은 [Magicians 스레드 논의](https://ethereum-magicians.org/t/eip-8038-state-access-gas-cost-update/25693/20)에서 예전 본문의 누락이 발견된 뒤 추가됐고, EIP 저자가 2026년 6월 22일 수정을 올렸습니다. 이 모두는 여전히 환급 카운터와 20% 상한을 거칩니다.

### CALL, CREATE, SELFDESTRUCT, EXTCODE*

- **`CALL`/`CALLCODE`**: `CALL_VALUE`가 `ACCOUNT_WRITE + CALL_STIPEND` = 9,000 + 2,300 = 11,300이 됩니다(이전 9,000). 피호출자에게 넘기는 2,300 stipend는 그대로입니다. 죽은(dead) 계정으로 값을 보내면 EIP-8037의 계정 비용을 상태 가스로 추가로 냅니다.
- **`CREATE`/`CREATE2`**: 고정 32,000이 `CREATE_ACCESS`(12,000, 실행)와 새 계정 상태 가스로 바뀝니다. EIP는 이 정의가 기존 분해와 정확히 맞지 않는다고 밝히고, 맞추지 않기로 했습니다.
- **`SELFDESTRUCT`**: 수혜자가 콜드면 `COLD_ACCOUNT_ACCESS`(웜이면 EIP-2929처럼 무료), 죽은 계정에 양의 잔액을 보내면 `ACCOUNT_WRITE`를 추가합니다.
- **`EXTCODESIZE`/`EXTCODECOPY`**: 두 번째 DB 읽기 몫으로 `WARM_ACCESS`(100)를 하나 더 냅니다.

### 수치를 정한 방법

EIP-8038은 초당 1억 가스(100 Mgas/s)를 성능 목표로 잡고, 이를 "현재 20 Mgas/s"의 5배라고 설명합니다. 각 실행 클라이언트가 연산 하나만 떼어 낸 합성 벤치마크 블록을 2026년 3월 메인넷 크기의 상태 스냅샷 위에서 돌렸고, 10 GB 스토리지 테스트는 메인넷 최대 컨트랙트 크기의 컨트랙트를 대상으로 했습니다. 비음수 최소제곱 회귀로 연산당 실행 시간을 추정하고 R² > 0.5, p < 0.05인 적합만 남긴 뒤 `가스 = 100,000,000 × 실행 시간(초)`로 환산했습니다. 파라미터마다 클라이언트 중 최악의 값을 씁니다. EIP는 이를 보수적인 선택이라고 설명합니다. 어떤 연산에서 가장 느린 클라이언트가 네트워크 전체의 가격을 정합니다.

표현 차이도 하나 알아 둘 만합니다. 재단의 8월 글은 이번 재조정이 기본 처리량을 "약 3배" 늘린다고 설명하고, EIP-8038은 5배 목표(20 → 100 Mgas/s)를 적습니다. 이 글에서는 필요한 곳에 EIP의 수치를 썼습니다.

## EIP-2780: 기본 가스와 런타임 가스

### 21,000의 분해

EIP-2780은 고정 기본값을 이름 붙은 항목으로 바꿉니다.

| 항목 | 값 | 부과 조건 |
| --- | --- | --- |
| `TX_BASE_COST` | 12,000 | 항상(서명 복구, 송신자 접근과 쓰기, 블록 포함) |
| `COLD_ACCOUNT_ACCESS` | 3,000 | `tx.to`가 다른 계정일 때(항상 콜드 요율) |
| `CREATE_ACCESS` | 12,000 | 컨트랙트 생성 트랜잭션, 수신자 접근 대신 |
| `TX_VALUE_COST` | 6,000 | 다른 계정으로 0이 아닌 값 전송. 자기 송금과 컨트랙트 생성 트랜잭션에는 부과하지 않음(잔액 쓰기와 [EIP-7708](https://eips.ethereum.org/EIPS/eip-7708) 전송 로그 몫) |
| `EXECUTION_PER_AUTH_BASE_COST` | 7,816 | EIP-7702 권한 위임 하나당 |

7,816은 EIP-8037에 정의돼 있습니다. 권한 위임 튜플 calldata 101바이트 × 16(1,616), `PRECOMPILE_ECRECOVER`(3,000), 콜드 계정 접근(3,000), 웜 접근 두 번(200)의 합입니다. calldata와 액세스 리스트 계량은 EIP-2780이 바꾸지 않습니다.

수신자와 위임 계정(authority)은 액세스 리스트로 웜 상태여도 늘 콜드 요율로 계산합니다. 기본 가스는 상태를 읽지 않고 계산할 수 있어야 하기 때문입니다.

### 기준 사례

EIP-2780의 표입니다(calldata, 액세스 리스트, 실행 코드는 제외).

| 트랜잭션 | 기본(실행) | 런타임 | 합계 |
| --- | --- | --- | --- |
| 자기 자신에게 ETH 전송 | 12,000 | 0 | 12,000 |
| EOA나 빈 계정으로 값 0인 호출 | 15,000 | 0 | 15,000 |
| 기존 EOA로 ETH 전송 | 21,000 | 0 | 21,000 |
| 7702 위임 계정으로 ETH 전송 | 21,000 | 3,000(위임 대상, 콜드) | 24,000 + 실행 |
| 새 계정을 만드는 ETH 전송 | 21,000 | 상태 183,600 | 실행 21,000 + 상태 183,600 |
| 컨트랙트 생성, 대상 주소 미존재 | 24,000 | 상태 183,600 | 24,000 + 상태 183,600 |
| 컨트랙트 생성, 대상 주소에 이미 잔액 있음 | 24,000 | 0 | 24,000 |

### 일괄 인하가 아니다

EIP-2780은 수수료 인하로 오해하기 쉽습니다. 이력 탓도 있습니다. 2025년 9월 이 EIP가 되살아났을 때, 지금도 "Reduce intrinsic cost of transactions"라는 제목인 [Magicians 스레드](https://ethereum-magicians.org/t/eip-2780-reduce-intrinsic-cost-of-transactions/4413)에 적힌 목표는 21,000을 6,000으로 내리는 것이었습니다. 현재 규범 본문은 다릅니다. [EIP-2780](https://eips.ethereum.org/EIPS/eip-2780) 초록(Abstract)은 기존 계정으로 보내는 일반 ETH 송금이 실행 가스 21,000 그대로라고 명시합니다. 21,000 아래로 내려가는 경우는 값이 0인 호출(15,000)과 자기 송금(12,000)뿐입니다. 계정을 새로 만드는 송금은 이제 합계 204,600으로 예전의 거의 10배입니다. EIP-2780 보안 절은 불변식을 직접 적어 둡니다. 다른 콜드 계정으로 값을 옮기는 트랜잭션이라면 분해된 비용의 합이 기존 21,000 이상이라는 것입니다.

EIP는 기본값이 ETH 송금으로 블록을 채운 실행 레이어 벤치마크에서 나왔다고 설명합니다. 네 종류 수신자를 대상으로 Besu, Erigon, Geth, Nethermind, Reth에서 돌리고 같은 100 Mgas/s 기준으로 환산했으며, 잠정치라고 밝힙니다.

### 런타임 단계

숫자보다 부과 시점의 변화가 더 중요합니다. EIP-2780은 예전 기본 비용을 두 종류로 나눕니다.

- **기본 가스(intrinsic gas)**: 트랜잭션 필드만으로 계산할 수 있는 비용. 유효성 검사의 유일한 입력입니다. 모자라면 트랜잭션은 무효이고 블록에 들어갈 수 없습니다.
- **런타임 가스(runtime gas)**: 상태에 따라 달라지는 비용. 수신자가 새 계정인지, 위임 계정인지, 위임 계정이 존재하는지 같은 것들입니다. 유효성 검사 뒤, 첫 EVM 프레임 전의 **실행 전(pre-execution) 단계**에서 부과합니다.

실행 전 단계는 순서가 정해져 있습니다. `gas_left`와 리저버로 가스를 나누고(EIP-8037), 7702 권한 위임을 처리하고, 수신자를 [EIP-7928](https://eips.ethereum.org/EIPS/eip-7928) 블록 수준 액세스 리스트에 넣은 뒤, 나머지 계정 생성과 접근 비용을 부과합니다.

이 단계에서 가스가 떨어져도 트랜잭션은 **무효가 되지 않습니다**. 블록에 포함되고, 송신자 nonce가 오르고, 송신자는 쓴 가스를 내며, 7702 위임을 포함한 실행 전 변경은 모두 되돌려집니다. EIP-2780은 이를 `CALL` 안의 가스 부족에 비유합니다. 블록 포함이 "호출자"이고, 런타임 실패가 그 결정을 되돌릴 수는 없다는 논리입니다. 대신 빌더는 아무것도 실행하지 않고 유효성을 판단할 수 있습니다.

실제 효과는 아래 커뮤니티 반응에서 다루는 Sepolia 보고에 드러납니다. 가스 한도 21,000을 하드코딩한 지갑이 새 주소로 ETH를 보내면, 이제 거부되지 않고 포함된 뒤 실패합니다. 수수료는 송신자가 냅니다.

### EIP-7702 권한 위임

기존 스케줄에서 최악의 경우를 미리 잡아 두던 또 하나가 권한 위임 가격이었습니다. EIP-7702는 위임마다 `PER_EMPTY_ACCOUNT_COST`(25,000)를 미리 받고, 계정이 이미 있으면 그중 일부(25,000 − 12,500 = 12,500)를 상한이 걸린 환급 카운터로 돌려줬습니다. EIP-2780에서는 7,816만 기본 가스입니다. 실행 전 단계에서 유효한 위임마다, 위임 계정당 최대 한 번씩 다음을 더합니다.

- 위임 계정이 존재하지 않으면 상태 가스 183,600
- 트랜잭션 안에서 그 계정에 대한 첫 쓰기면 `ACCOUNT_WRITE`(9,000). 이미 값을 낸 쓰기(위임 계정이 송신자, 앞선 위임이 이미 씀, 값 전송의 수신자)는 건너뜁니다.
- 0이 아닌 위임 대상을 설정하고, 트랜잭션 시작 때 위임 표시가 없었다면 상태 가스 35,190(23 × 1,530). 시작 때부터 있던 표시를 지웠다가 다시 설정하면 다시 내지 않습니다.

## 세 EIP를 합친 계산 예

자주 쓰는 트랜잭션 몇 개를 세 EIP를 합쳐 계산하면 이렇습니다(calldata, 액세스 리스트, 생성자 실행은 제외).

**새 주소로 ETH 전송.** 기본 12,000 + 3,000 + 6,000 = 21,000에 런타임 상태 183,600을 더해 **204,600**입니다. `tx.gas`를 21,000으로 주면 트랜잭션은 유효하고 포함되지만 실행 전 단계에서 실패합니다.

**컨트랙트 호출 안에서 새 스토리지 슬롯에 처음 쓰기.** 콜드 접근 2,100 + `STORAGE_WRITE` 10,000 = 실행 12,100에 상태 97,920을 더해 **110,020**입니다. 이전에는 22,100이었습니다.

**최상위 생성 트랜잭션으로 새 주소에 24,576바이트 컨트랙트 배포.** 기본 12,000 + `CREATE_ACCESS` 12,000 = 실행 24,000. 런타임 계정 상태 183,600. 코드 저장 24,576 × 1,530 = 상태 37,601,280, 해시 비용 6 × 768 = 실행 4,608. 상태 가스 합계는 37,784,880으로 EIP-8037 영향 표의 값과 같습니다. 실행 가스는 약 28,600에 생성자 실행분을 더한 정도라 실행 상한 16,777,216보다 한참 아래입니다. 상태 가스는 이 상한에 잡히지 않지만, 그 숫자의 두 배가 넘습니다. EIP-8037 없이 모든 가스가 그렇듯 상태 가스와 실행 가스가 EIP-7825 상한 하나를 함께 쓴다면, 새 가격에서는 이 배포가 트랜잭션 하나에 들어가지 않습니다. 상태 차원을 상한 밖에 둔 이유가 이것입니다. `tx.gas`를 16.7M보다 크게 주면 초과분이 리저버가 되어 코드 비용을 냅니다.

**존재하지 않는 계정으로 값을 보내는 내부 `CALL`.** 콜드 접근 3,000 + `CALL_VALUE` 11,300의 실행 가스에 상태 183,600이 더해지고, 자식 프레임 전에 부과됩니다.

## 개발자가 확인할 것

스펙의 해당 절과 재단의 [재조정 안내](https://blog.ethereum.org/2026/08/24/glamsterdam-repricing-testing)가 가리키는 목록은 거의 같습니다.

**하드코딩한 가스 한도.** 미리 서명한 트랜잭션, 스크립트, 고정 가스를 넘기는 컨트랙트가 가장 흔히 깨집니다. EIP-8037은 알아 둘 만한 예를 하나 듭니다. 고전적인 결정론적 배포 팩토리(서명된 가스 한도 100,000인 Nick's method와 `SingletonFactory`, `Create2Deployer`, `ImmutableCreate2Factory`, `CreateX` 등)는 원래 트랜잭션으로는 더 이상 배포되지 않습니다. 이미 배포된 메인넷과 L2에는 영향이 없습니다. 이 EIP를 처음부터 켠 새 데브넷과 테스트넷이 대상이고, 제네시스에 미리 넣거나 트랜잭션을 다시 만들어야 합니다.

**`gasleft()` 산술.** 리필이 리저버보다 `gas_left`를 먼저 채우므로 연산 뒤 `gas_left`가 *늘어날* 수 있습니다. 다만 되돌리는 상태 비용을 `gas_left`에서 냈을 때만 그렇습니다. EIP-8037의 예는 트랜잭션 시작 때 0이던 슬롯에 대한 `SSTORE(k, 1); GAS; SSTORE(k, 0); GAS`입니다. 첫 저장 때 리저버가 비어 있었다면(`tx.gas`가 7825 상한 이하면 항상 그렇습니다) 97,920은 `gas_left`에서 나갔고, 지우면 그 자리로 리필되어 두 번째 읽은 값이 첫 번째보다 리필에서 삭제 비용을 뺀 만큼 큽니다. 리저버가 첫 저장 비용을 냈다면 리필은 리저버로 돌아가고, 두 번째 값은 평소처럼 더 작습니다. 하위 호출이 성공하면 병합 단계가 호출자의 `gas_left`로 상태 가스를 돌려줄 수도 있습니다. `GAS`를 두 번 읽은 차이로 "사용 가스"를 계산하는 컨트랙트는 음수를 얻을 수 있고, checked 산술에서는 revert, unchecked 산술에서는 랩어라운드가 납니다. EIP는 이런 계량을 쓰는 기존 배포 컨트랙트는 고칠 수 없다고 명시합니다. 7825 상한 이하의 트랜잭션은 리저버가 0이라 모든 상태 비용이 `gasleft()`에 드러납니다.

**남은 가스로 분기하는 로직.** ChainSecurity는 `try`/`catch` 패턴에 대한 [우려를 제기했습니다](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/28)(28번 글, 2026년 6월 5일). 공격자가 내부 호출 가스를 `gasleft()` 임계값 바로 아래로 맞춰 `catch` 경로를 강제하는데, `SSTORE` 비용 대부분이 넉넉한 리저버에서 나가는 상태 가스로 옮겨 가면서 `catch` 경로의 쓰기가 이제 들어맞을 수 있다는 것입니다. 이 분석은 당시(2026년 6월) 초안의 파라미터를 썼지만, 큰 `tx.gas`가 리저버를 채우는 한 패턴 자체는 유효합니다. 같은 논의에서 다른 참여자들은 `gasleft()` 기반 분기가 이전 재조정 때도 깨진 안티패턴이라고 답했고, 이어진 답글(30번 글)은 이 패턴을 쓰는 인기 컨트랙트를 쉽게 옮길 수 없다는 점을 짚었습니다.

**가스 추정.** EIP-8037과 EIP-8038 모두 지갑과 RPC 노드가 `eth_estimateGas`를 고쳐야 한다(MUST)고 적고, EIP-8037은 돌려주는 `tx.gas`가 두 차원을 모두 덮어야 한다고 덧붙입니다. 첫날부터 도구 버그가 하나 나왔습니다. Sepolia 보고에 따르면 anvil이 새 계정으로의 송금을 21,000으로 추정했고, Foundry는 10월 7일 수정(PR #17432)을 병합했습니다. 그 이전 빌드에는 버그가 남아 있습니다.

**`eth_call`과 시뮬레이션.** 한 [Magicians 글](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/47)(47번 글, 2026년 9월 29일)은 당시 geth master 브랜치의 `eth_call`이 같은 리저버 분할을 적용해서, 50M 가스를 준 읽기 전용 호출이 실행 가스를 약 16.76M밖에 못 받는다고 지적했습니다. 그대로 갔다면 기본 RPC 가스 상한으로 잘 돌던 무거운 view 함수(온체인 SVG 렌더러, 견적기, 애그리게이터)가 실패했을 것입니다. 이 문제는 [ACDT #99 안건](https://github.com/ethereum/pm/issues/2242)에 올랐고, EIP 저자는 10월 6일 geth 수정이 있지만 아직 병합 전이며 의도한 동작을 execution-apis 스펙에 넣겠다고 답했습니다. geth는 같은 날 그 수정인 [PR #35845](https://github.com/ethereum/go-ethereum/pull/35845)를 병합하고 원래 보고(이슈 #35838)를 닫았습니다. 병합된 코드에서는 `eth_call`, `debug_traceCall`, strict가 아닌 `eth_simulateV1`이 실행 상한과 리저버 분할을 건너뛰고, `eth_estimateGas`와 strict `eth_simulateV1`은 여전히 상한에 묶입니다. 병합이 곧 배포는 아닙니다. 이 수정이 어느 geth 릴리스와 RPC 제공자에 들어갔는지, 다른 클라이언트는 어떻게 동작하는지는 이 글에서 확인하지 않았습니다. 무거운 시뮬레이션에 기대는 서비스라면 실제로 붙는 클라이언트 버전과 제공자를 확인하세요. `eth_call`로는 통과한 호출도 `eth_estimateGas`나 strict 시뮬레이션에서는 상한에 걸릴 수 있습니다.

**ERC-4337 번들.** `EntryPoint`는 `gasleft()` 차이로 사용자 연산을 계량하는데, 이 값으로는 리저버가 보이지 않습니다. 번들 안의 연산이 리저버를 공유하므로 한 연산의 리필이 다른 연산의 비용을 보이지 않게 메울 수 있습니다. EIP-8037은 번들러와 `EntryPoint` 구현이 상태 가스를 명시적으로 계산해야 한다(MUST)고 적습니다. Sepolia 보고에서는 새 nonce 키를 처음 쓸 때 검증 가스 한도 안에서 새 슬롯(상태 97,920)을 쓰느라 4337 계정이 실패한 사례가 나왔습니다.

**블록 빌더.** 차원이 둘이면 최적 패킹은 자원 두 개짜리 문제가 됩니다. EIP-8037은 이것이 정교한 빌더에게 유리할 수 있다고 인정하면서도, 한 차원이 찰 때까지 탐욕적으로 채우는 단순한 방식도 충분히 통한다고 봅니다.

**스토리지를 많이 쓰는 설계.** 슬롯을 갱신하기보다 계속 새로 만드는 컨트랙트에서 비용이 가장 크게 움직입니다. 투표 체크포인트를 쌓는 거버넌스 토큰, EIP-3009 `transferWithAuthorization` 같은 권한별 솔트, 키가 무작위인 ACL 매핑이 그렇습니다.

## 커뮤니티 반응

공개 기록은 주로 [EIP-8037 토론 스레드](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694)에 있고, 반응은 엇갈립니다.

지지 쪽에서는 OpenZeppelin의 Amxx가 이 변경이 L1의 지속 가능성과 보안에 필요하다고 [썼습니다](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/38)(38번 글, 2026년 6월 19일). 새 계정을 만들거나 자금을 넣지 않는 평범한 ERC-20 잔액 갱신에는 EIP-8037이 영향을 주지 않는다는 설명도 덧붙였습니다. 이는 상태 가스에 한한 이야기입니다. 같은 잔액 갱신도 앞의 `SSTORE` 표처럼 EIP-8038의 오른 `STORAGE_WRITE`는 그대로 냅니다. 같은 글은 비용이 늘어나는 쪽도 짚습니다. 투표 체크포인트가 있는 거버넌스 토큰, EIP-3009 권한 솔트, ACL 컨트랙트입니다. 불리언 매핑이 1비트에 32바이트 슬롯 하나를 통째로 쓴다는 지적도 있습니다. EIP 저자의 입장은 스레드에 적혀 있습니다. 이미 포함 예정이고 데브넷에서 돌고 있으며 [가스 한도를 더 올리는 데 걸림돌](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/34)이라는 것입니다.

비판은 구체적입니다. 초안 표준 ERC-7984 위에서 기밀 토큰을 만드는 팀들은 기밀 송금 한 번이 새 영구 ACL 슬롯을 최소 7개 만들고, 그러면 상태 가스가 최소 685,440이 된다고 [추산했고](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/33)(33번 글, 2026년 6월 15일), 다음 포크인 Hegotá로 미뤄 달라고 요청했습니다. 온체인 NFT 개발자 한 명은 2025년 11월, EIP 초기 판을 두고 스토리지를 많이 쓰는 앱이 L1 밖으로 밀려날 것을 [걱정했습니다](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/15). 다른 참여자는 저장 비용이 지수적으로 떨어지는데 상태 증가를 선형으로 목표 잡는 것에 [의문을 제기했고](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/20)(2026년 1월), 블록 구성이 크게 달라질지도 [의심했습니다](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/23)(2026년 2월). EIP-8038 쪽에서는 두 재조정의 잠정 파라미터로 돌린 [비용 분석](https://ethereum-magicians.org/t/eip-8038-state-access-gas-cost-update/25693/18)(2026년 6월 20일)이 표본 청산·차익 거래의 가스가 약 44~63% 늘어난다고 보고했습니다. EIP-8038 값은 그 뒤에 수정됐습니다.

첫 현장 데이터는 Sepolia 포크 뒤에 나왔습니다. [커뮤니티 보고](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694/50)(PyraVim, 2026년 10월 8일)에 따르면 포크 전 10.5시간과 비교해 포크 후 첫 10.5시간 동안 Sepolia 트랜잭션 실패율이 1.91%에서 10.97%로 올랐습니다. 늘어난 실패의 약 3분의 1은 같은 실패 호출을 반복하는 봇이었습니다. 원인으로 추적된 것은 새 계정 송금의 고정 가스 한도, 4337 nonce 키, 스토리지 쓰기였습니다. 기존 계정 송금 21,000, 값이 0인 송금 15,000, 자기 송금 12,000은 그대로라는 것도 확인했습니다. 한 사람의 노드에서 나온 초기 표본이라는 점은 감안해야 하지만, 수치는 스펙 계산과 정확히 맞습니다. 재단은 메인넷 재생(replay) 분석에서 대다수 스마트 컨트랙트가 영향을 받지 않는다고 보고, 유지보수자용 [영향 컨트랙트 검색](https://ethereum.github.io/repricing-impact/)을 공개했습니다.

## 아직 정해지지 않은 것

- **메인넷과 Hoodi 활성화**: 스냅샷 시점에 어느 공식 자료에도 정해져 있지 않습니다. [ACDT #100 안건](https://github.com/ethereum/pm/issues/2264)은 클라이언트 팀에 10월 16일까지 Hoodi 릴리스를 요청했는데, 이는 준비 단계이지 활성화 시점이 아닙니다.
- **최종 파라미터 값**: Last Call은 11월 1일까지이고, EIP-8037과 EIP-2780 모두 일부 입력값을 최종이 아니거나 잠정치라고 적습니다.
- 리저버 분할 아래에서 클라이언트별 **`eth_call` 동작**.
- 같은 트랜잭션 안의 `CREATE` + `SELFDESTRUCT`에 대한 **리필**: 요청되고 ACDE에서 논의됐지만 현재 본문에는 없습니다.

## 정리

제가 가장 주의 깊게 볼 부분은 가스를 차원으로 나눈 구조입니다. 설계상으로는 말한 대로 동작합니다. 상태 증가가 자기 예산과 가격을 갖고, 블록 한도가 더 이상 실행과 저장을 맞바꾸게 하지 않습니다. 대가는 EVM 안에서 "가스"가 한 가지 뜻이 아니게 된다는 점입니다. `gasleft()`는 예산 일부만 보여 주고, 리필 때문에 값이 올라갈 수 있으며, 리저버는 16.7M 가스를 넘는 트랜잭션에만 존재합니다. 컨트랙트 작성자와 도구가 소화해야 할 새 동작이 많습니다. 가장 나쁜 경우는 조용히 실패하면서 수수료는 나가는 트랜잭션입니다.

Sepolia 초기 수치는 설계 결함보다는 하드코딩한 한도부터 깨지는 흔한 재조정 패턴에 가까워 보입니다. 가격이 실제로 상태 사용 방식을 바꿀지는 여러 비판자가 의심하는 부분이고, 메인넷 데이터가 나와야 알 수 있습니다.

## 함께 보면 좋을 자료

- [EIP-7928: Block-Level Access Lists](https://eips.ethereum.org/EIPS/eip-7928): `CREATE`가 대상 주소를 언제 읽을 수 있는지 제약하는 헤드라이너. EIP-8038 벤치마크가 병렬 읽기를 전제하는 이유이기도 합니다
- [EIP-7778: Block Gas Accounting without Refunds](https://eips.ethereum.org/EIPS/eip-7778): EIP-8037이 함께 적용을 전제로 명시한 블록 집계 변경
- [EIP-7825: Transaction Gas Limit Cap](https://eips.ethereum.org/EIPS/eip-7825): 실행 상한 16,777,216의 출처
- [Glamsterdam 재조정 영향 검사기](https://ethereum.github.io/repricing-impact/): 영향받는 컨트랙트를 찾아보는 재단 도구
- [Forkcast: Glamsterdam](https://forkcast.org/upgrade/glamsterdam): ACD 회의를 따라가는 상태 추적기(기준 자료는 메타 EIP)

## 참고 자료

- [EIP-8037: State Creation Gas Cost Increase](https://eips.ethereum.org/EIPS/eip-8037), 원문 [ethereum/EIPs `5ef3801`](https://github.com/ethereum/EIPs/blob/5ef380124bd68d09c02fa90d0de0f2455f37d5ee/EIPS/eip-8037.md), 조회일 2026-10-15
- [EIP-8038: State-access gas cost update](https://eips.ethereum.org/EIPS/eip-8038), 원문 [`5ef3801`](https://github.com/ethereum/EIPs/blob/5ef380124bd68d09c02fa90d0de0f2455f37d5ee/EIPS/eip-8038.md), 조회일 2026-10-15
- [EIP-2780: Resource-based intrinsic transaction gas](https://eips.ethereum.org/EIPS/eip-2780), 원문 [`5ef3801`](https://github.com/ethereum/EIPs/blob/5ef380124bd68d09c02fa90d0de0f2455f37d5ee/EIPS/eip-2780.md), 조회일 2026-10-15
- [EIP-7773: Hardfork Meta - Glamsterdam](https://eips.ethereum.org/EIPS/eip-7773), 원문 [`644b847`](https://github.com/ethereum/EIPs/blob/644b84799ba6873edcb13c0e21fdd319b4efbc08/EIPS/eip-7773.md), 조회일 2026-10-15
- [ethereum/execution-specs Amsterdam 포크](https://github.com/ethereum/execution-specs/tree/16898000911c1e3caa57be08509536c10ae92d3e/src/ethereum/forks/amsterdam), `forks/amsterdam` 브랜치 `1689800`, 조회일 2026-10-15
- [Glamsterdam](https://ethereum.org/en/roadmap/glamsterdam/), ethereum.org, 페이지 최종 수정 2026-09-14, 조회일 2026-10-15
- [Glamsterdam Testnet Announcement](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement), Ethereum Foundation Blog, 2026-09-17, 조회일 2026-10-15
- [Glamsterdam repricing testing](https://blog.ethereum.org/2026/08/24/glamsterdam-repricing-testing), Ethereum Foundation Blog, 2026-08-24, 조회일 2026-10-15
- [ACDE #244 안건과 댓글](https://github.com/ethereum/pm/issues/2197), ethereum/pm, 조회일 2026-10-15
- [ACDT #99 안건과 댓글](https://github.com/ethereum/pm/issues/2242), ethereum/pm, 조회일 2026-10-15
- [ACDT #100 안건](https://github.com/ethereum/pm/issues/2264), ethereum/pm, 조회일 2026-10-15
- [go-ethereum PR #35845: core, eth, internal: skip the execution gas cap on eth_call](https://github.com/ethereum/go-ethereum/pull/35845), 2026-10-06 병합(`df4c524`), 이슈 #35838 종료, 조회일 2026-10-15
- [EIP-8037 토론 스레드](https://ethereum-magicians.org/t/eip-8037-state-creation-gas-cost-increase/25694), Ethereum Magicians, 조회일 2026-10-15
- [EIP-8038 토론 스레드](https://ethereum-magicians.org/t/eip-8038-state-access-gas-cost-update/25693), Ethereum Magicians, 조회일 2026-10-15
- [EIP-2780 토론 스레드](https://ethereum-magicians.org/t/eip-2780-reduce-intrinsic-cost-of-transactions/4413), Ethereum Magicians, 조회일 2026-10-15
