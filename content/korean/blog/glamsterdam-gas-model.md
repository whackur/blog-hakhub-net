---
title: "Glamsterdam의 새 가스 모델: EIP-8037 상태 가스, EIP-8038 접근 비용, EIP-2780 기본 가스"
meta_title: ""
description: "Glamsterdam의 세 가스 제안이 Solidity의 새 슬롯·기존 값 갱신·삭제·고정 내부 호출에 미치는 영향. 실행·상태 예산과 최종 청구량, 명세 상태와 네트워크 활성화를 구분합니다."
date: 2026-10-15T01:19:45+09:00
lastmod: 2026-10-15T16:10:31Z
image: "/images/posts/glamsterdam-gas-model/glamsterdam-resource-costs-20261015.webp"
categories: ["Blockchain"]
tags: ["ethereum", "glamsterdam", "gas", "evm", "eip-8037", "eip-8038", "eip-2780"]
author: "whackur"
translationKey: "glamsterdam-gas-model"
draft: false
---

Glamsterdam의 세 가스 제안은 **새 상태를 영구 저장하는 비용과 기존 상태를 갱신하는 비용을 올리고**, 작업이 적은 일부 트랜잭션의 기본 비용을 낮춥니다. 명세상 새 콜드 스토리지 슬롯에 쓰면 실행 가스 12,100에 상태 가스 97,920이 붙고, 기존 슬롯의 트랜잭션 시작 값이 0이 아니고 콜드 상태에서 그 값과 다르게 처음 바꾸면 실행 가스 12,100이 들며 상태 가스는 들지 않습니다. 두 비용 모두 트랜잭션의 `gasLimit` 하나로 충당하지만 `gasleft()`는 별도 상태 가스 리저버를 보여 주지 않습니다. 이 숫자는 명세의 구성 비용이며 Solidity 함수 전체의 측정값이나 메인넷 적용 공지가 아닙니다. [EIP-8037](https://eips.ethereum.org/EIPS/eip-8037), [EIP-8038](https://eips.ethereum.org/EIPS/eip-8038), [EIP-2780](https://eips.ethereum.org/EIPS/eip-2780)이 이 변경을 함께 정의합니다.

## 명세 상태와 네트워크 활성화

2026년 10월 15일 UTC에 확인한 ethereum/EIPs 커밋 [`8b1cae5`](https://github.com/ethereum/EIPs/tree/8b1cae50601fb194452db0ed857f4c237ca62c1f/EIPS)의 상태는 다음과 같습니다.

| 구분 | 공개된 내용 |
| --- | --- |
| 명세 확정 절차 | 세 제안 모두 `Last Call`, 마감일은 2026년 11월 1일입니다. EIP-8037은 의존하는 파라미터가 아직 최종값이 아니라고 밝히고, EIP-2780은 가격 산출값을 잠정치라고 설명합니다. |
| Glamsterdam 포함 여부 | [EIP-7773](https://eips.ethereum.org/EIPS/eip-7773)의 포함 예정(Scheduled for Inclusion) 목록에 셋 모두 있습니다. 메타 EIP 자체는 `Review`입니다. |
| 공개된 활성화 시각 | Sepolia: epoch 353,024, 타임스탬프 1,791,294,816, 2026년 10월 6일 13:53:36 UTC입니다. Hoodi와 Mainnet 칸은 비어 있습니다. |

[이더리움 재단의 테스트넷 공지](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement)는 Sepolia를 대상으로 하며 메인넷 일정을 잡는 공지가 아니라고 명시합니다. 확인 시점에는 Sepolia의 공지된 활성화 시각이 지났으므로, 변경을 시험할 네트워크로 공지된 곳은 Sepolia입니다. 다만 일정만으로는 그 이후의 명세 수정 중 어디까지 특정 클라이언트나 RPC 제공자가 구현했는지 알 수 없습니다. 아래 사례는 확인한 명세의 동작을 설명하며 실제 체인에서 수행한 포크 전후 벤치마크가 아닙니다. 포크 포함 결정, 문서 확정, 특정 네트워크 활성화는 서로 다른 사실입니다.

## 트랜잭션 필드에서 실행 예산까지

세 제안은 같은 트랜잭션의 서로 다른 부분을 맡습니다. EIP-2780은 블록 포함 비용을 정하고 상태에 따라 달라지는 비용을 런타임으로 옮깁니다. EIP-8038은 상태 접근과 쓰기에, EIP-8037은 새 상태와 두 차원 가스 집계에 적용됩니다.

calldata, 액세스 리스트 항목, 권한 위임, 수신자 코드 실행이 없는 단순 트랜잭션에서는 EIP-2780이 고정 21,000을 다음처럼 나눕니다.

| 트랜잭션 형태 | 실행 가스 | 상태 가스 | 합계 |
| --- | ---: | ---: | ---: |
| 일반 비위임 송신자가 자기 자신에게 전송 | 12,000 | 0 | 12,000 |
| 다른 일반 EOA 또는 빈 주소로 값 0인 호출 | 12,000 + 3,000 | 0 | 15,000 |
| 다른 기존 일반 EOA로 양의 ETH 전송 | 12,000 + 3,000 + 6,000 | 0 | 21,000 |
| 계정을 새로 만드는 양의 ETH 전송 | 21,000 | 183,600 | 204,600 |

EOA는 외부 소유 계정(externally owned account)입니다. 기본 12,000은 송신자 처리와 블록 포함, 3,000은 수신자 접근, 6,000은 수신자 잔액 쓰기와 [EIP-7708](https://eips.ethereum.org/EIPS/eip-7708) 전송 로그 비용입니다. 컨트랙트 코드를 호출하면 실행 비용이 더해집니다. EIP-7702 위임 계정이 수신자라면 위임 대상에 접근하는 런타임 비용도 붙습니다. 콜드면 3,000, 이미 웜이면 100이고 위임된 코드 실행 비용은 별도입니다. 따라서 “ETH 송금은 이제 12,000 가스”라고 설명하면 조건이 빠집니다. [EIP-2780의 기준 사례](https://eips.ethereum.org/EIPS/eip-2780#transaction-reference-cases)는 이 경로들을 구분합니다.

기본 가스(intrinsic gas)는 상태를 읽지 않고 트랜잭션 필드로 계산합니다. 수신자가 액세스 리스트에 있어도 기본 가스의 수신자 접근은 콜드 요율로 계산합니다. 새 계정이 필요한지는 나중에 판정합니다. 트랜잭션의 블록 포함 검사를 통과한 뒤 첫 EVM 호출 프레임에 들어가기 전인 실행 전(pre-execution) 단계에서 확인하고 부과합니다.

따라서 새 주소로 송금하면서 한도를 21,000으로 설정하면, 가스 관련 기본 검사는 통과해도 상태 가스 183,600을 내는 단계에서 가스가 부족해질 수 있습니다. 다른 유효성 검사까지 통과해 블록에 포함됐다면 실패 처리되고 송신자 nonce가 증가하며 가스 수수료가 듭니다. ETH 송금은 완료되지 않습니다. 무효라서 거부된 트랜잭션과 포함된 뒤 실패한 트랜잭션의 결과는 다릅니다. 지갑은 모든 ETH 송금에 상수를 쓰는 대신 두 차원을 반영하는 추정기가 필요합니다. [EIP-2780](https://eips.ethereum.org/EIPS/eip-2780#runtime-gas-costs)

## 같은 Solidity 대입문의 서로 다른 스토리지 경로

다음 작은 컨트랙트는 다른 업무 로직 없이 세 연산을 보여 줍니다.

```solidity
pragma solidity 0.8.30;

contract Slot {
    uint256 public value;

    function write(uint256 next) external {
        value = next;
    }

    function clear() external {
        delete value;
    }
}
```

아래 비교는 `value`를 바꾸는 `SSTORE` opcode의 비용입니다. 함수 전체 비용은 아닙니다. 함수 선택, ABI 디코딩, 스택 연산, 필요한 메모리 작업은 실행 가스를 더 씁니다. 최종 영수증에는 트랜잭션 기본 가스와 calldata도 반영됩니다. 예제는 Solidity 0.8.30, optimizer 활성화 및 200 runs, `viaIR: false`, `evmVersion: "prague"`로 컴파일했습니다. 컴파일은 코드와 생성된 명령을 확인하는 절차이며, 이전·새 포크에서 런타임 비용을 측정했다는 뜻은 아닙니다.

콜드 행은 액세스 리스트가 없고 해당 트랜잭션에서 이 스토리지 키를 앞서 건드리지 않았다고 가정합니다. “원래 값”은 트랜잭션 시작 시점, “현재 값”은 해당 `SSTORE` 직전의 값입니다. 이전 트랜잭션으로 초기값을 만들 수는 있지만 웜 상태가 다음 트랜잭션까지 유지되지는 않습니다. 변경 전 비교값은 [EIP-2200](https://eips.ethereum.org/EIPS/eip-2200), [EIP-2929](https://eips.ethereum.org/EIPS/eip-2929), [EIP-3529](https://eips.ethereum.org/EIPS/eip-3529)의 스케줄을 따릅니다.

| 연산과 초기 조건 | 이전 스케줄의 실행 가스 | 제안된 실행 가스 | 제안된 상태 가스 |
| --- | ---: | ---: | ---: |
| `write(7)`, 원래 값 = 현재 값 = 0, 콜드 | 22,100 | 2,100 + 10,000 = 12,100 | 97,920 |
| `write(9)`, 원래 값 = 현재 값 = 7, 콜드 | 5,000 | 12,100 | 0 |
| 같은 비영 값 갱신, 같은 트랜잭션의 앞선 읽기로 키가 웜 | 2,900 | 100 + 10,000 = 10,100 | 0 |
| `clear()`, 원래 값 = 현재 값 = 7, 콜드 | 5,000, 환급 크레딧 4,800 추가 | 12,100, 환급 크레딧 11,616 추가 | 0 |

### 새 슬롯과 기존 값 갱신

새로 배포한 뒤 `value`가 아직 0일 때 `write(7)`을 호출합니다. EIP-8037은 새 스토리지 리프와 키에 합계 64바이트의 계량값을 부여합니다. `CPSB`(cost per state byte, 상태 바이트당 비용)가 1,530이므로 64 × 1,530 = 97,920 상태 가스입니다. EIP-8038의 콜드 접근과 첫 쓰기 비용까지 합치면 이 opcode의 두 차원 합계는 110,020입니다. 함수 전체에는 이보다 더 많은 가스가 필요합니다.

기존 값 사례는 먼저 별도 트랜잭션에서 `write(7)`을 완료한 뒤, 평가 대상 트랜잭션에서 `write(9)`를 호출합니다. 새 스토리지 리프가 없으므로 상태 생성 비용은 없지만, 원래 값에서 처음 바꾸는 쓰기에는 여전히 `STORAGE_WRITE` 10,000이 붙습니다. 새 상태를 만들지 않아도 실행 가스 인상은 적용됩니다. 같은 트랜잭션 안에서 앞서 읽으면 뒤의 쓰기는 웜이 되지만, 그 읽기도 가스를 씁니다. [EIP-8038의 SSTORE 규칙](https://eips.ethereum.org/EIPS/eip-8038#sstore-pricing)

이미 바꾼 슬롯에 다시 쓸 때마다 10,000이 붙지는 않습니다. 원래 값 7 → 현재 값 9 → 새 값 11이라면 두 번째 쓰기는 웜 접근 비용만 냅니다. 7로 복원하면 환급 카운터에 `STORAGE_WRITE`를 더합니다. 원래 값으로 돌아온 뒤 다시 다른 값으로 바꾸면 쓰기 비용이 다시 붙을 수 있습니다. 각 소스 코드 대입문을 독립적으로 세는 대신 트랜잭션 전체의 원래 값·현재 값·새 값 관계를 따릅니다.

### 삭제 환급은 삭제한 트랜잭션에 적용

이전 트랜잭션에서 `value`를 7로 만든 뒤 `clear()`를 호출합니다. 제안된 11,616은 그 트랜잭션의 환급 카운터에 쌓이는 크레딧입니다. 호출 프레임의 남은 가스에 즉시 더하지 않습니다. 실제 적용액은 환급 전 사용량의 5분의 1로 제한하고, calldata 하한 때문에 혜택이 더 줄 수도 있습니다. 가령 환급 전 사용량이 30,000이고 카운터가 11,616인 가상 트랜잭션은 6,000만 환급받습니다. 하한이 영향을 주지 않으면 최종 청구량은 24,000입니다. 이는 정산 계산 예시이며 `clear()`의 측정값이 아닙니다. [EIP-8037 정산 규칙](https://eips.ethereum.org/EIPS/eip-8037#transaction-gas-used)

나중에 `value`를 읽을 때 저장값이 0이라고 할인되지는 않습니다. 콜드 `SLOAD`는 2,100, 웜은 100이며 getter의 다른 명령은 추가 비용입니다. 온체인 getter 호출은 가스를 씁니다. 오프체인 `eth_call`은 노드의 시뮬레이션 한도 안에서 실행하며 호출자에게 온체인 트랜잭션 수수료를 청구하지 않습니다.

### 한 트랜잭션 안에서 설정 후 삭제

슬롯이 0으로 시작해 7로 바뀌었다가 같은 트랜잭션 안에서 다시 0으로 돌아오면, 삭제하는 쓰기에 두 가지 규칙이 적용됩니다.

- EIP-8037은 새 리프가 더는 필요하지 않으므로 상태 가스 97,920을 리필(refill)합니다.
- EIP-8038은 웜 실행 가스 100을 받고, 원래 값을 복원했으므로 상한이 있는 환급 카운터에 10,000을 더합니다.

이 경로에는 트랜잭션 시작 때부터 0이 아니던 슬롯을 삭제할 때의 11,616 크레딧이 중복 적용되지 않습니다. 반대로 원래 0이 아니던 슬롯을 지웠다가 다시 설정하면 삭제 크레딧을 취소하며 새 상태 가스는 부과하지 않습니다. 영구 저장된 값을 지우는 경우와 같은 트랜잭션의 왕복 쓰기는 다른 사례입니다. [EIP-8037](https://eips.ethereum.org/EIPS/eip-8037#gas-accounting-for-sstore-opcode-level), [EIP-8038](https://eips.ethereum.org/EIPS/eip-8038#sstore-pricing)

## 고정 내부 가스 한도와 바깥 트랜잭션의 실패는 별개

자식 호출이 실패했을 때 호출자가 어떻게 처리하는지도 중요합니다. 다음 래퍼는 위의 `Slot` 컨트랙트를 호출합니다.

```solidity
pragma solidity 0.8.30;

contract FixedAllowance {
    uint256 public marker;
    uint256 public immutable childGasCap;

    constructor(uint256 cap) {
        childGasCap = cap;
    }

    function run(address target, uint256 next, bool mustSucceed)
        external returns (bool ok)
    {
        marker = next;
        (ok,) = target.call{gas: childGasCap}(
            abi.encodeWithSignature("write(uint256)", next)
        );
        if (mustSucceed) require(ok, "child failed");
    }
}
```

`target`에는 코드 없는 주소가 아니라 실제 `Slot` 주소를 넣습니다. 이전 트랜잭션에서 `Slot.value`와 `FixedAllowance.marker`를 모두 7로 초기화하고 `run(target, 9, ...)`를 호출합니다. 비교할 때마다 같은 상태에서 시작하고 자식의 슬롯은 콜드로 둡니다. 호출자 비용과 63/64 규칙을 적용한 뒤에도 고정 한도를 전부 넘길 수 있도록 바깥 트랜잭션 가스를 충분히 줍니다. 두 쓰기 모두 기존의 0이 아닌 값을 바꾸므로 상태 생성 비용 없이 실행 가스 재조정만 비교합니다.

고정 한도가 이전 컴파일 코드 경로에는 충분하고 재조정된 경로에는 부족하다면, 이전에는 성공하던 자식이 변경 후 OOG(out-of-gas, 가스 부족)로 실패할 수 있습니다. 여기서는 숫자로 된 경계값이나 재현된 회귀를 주장하지 않습니다. 경계값은 표의 `SSTORE`만이 아니라 자식의 컴파일된 전체 실행 코드에 달려 있습니다. 바깥 트랜잭션 한도를 올려도 `childGasCap`은 늘지 않으므로 내부 한도나 호출 설계를 바꿔야 합니다.

`mustSucceed = false`라면 자식 OOG는 `false`를 반환합니다. 래퍼는 정상 종료해 `marker = 9`를 유지할 수 있지만 자식의 쓰기는 롤백됩니다. `mustSucceed = true`라면 `require(ok)`가 래퍼 프레임도 revert해 marker까지 되돌립니다. 결과를 처리할 호출자 가스가 충분하다는 조건입니다. 자식의 `REVERT`는 쓰지 않은 실행 가스를 돌려주고 OOG 같은 예외적 중단은 전달된 실행 예산을 소진합니다. 어느 쪽도 low-level 호출자의 자동 revert를 뜻하지 않습니다. [EIP-140](https://eips.ethereum.org/EIPS/eip-140), [EIP-8037 롤백 규칙](https://eips.ethereum.org/EIPS/eip-8037#gas-accounting-for-halts-and-reverts)

그대로 유지되는 2,300 stipend는 이 쓰기의 회귀 사례로 적절하지 않습니다. `SSTORE` 검사는 남은 실행 가스가 2,300 이하인 프레임을 이미 거부하며 리저버도 이 검사를 우회하지 못합니다. 이전 규칙에서도 실패하던 쓰기를 새로운 Glamsterdam 실패로 볼 수는 없습니다.

## 리저버가 gasleft의 관측 범위를 바꾸는 방식

[EIP-8037](https://eips.ethereum.org/EIPS/eip-8037#transaction-level-gas-accounting-reservoir-model)은 기본 비용을 뺀 가스를 다음처럼 나눕니다.

```text
C = 16,777,216
evm_gas = tx.gas - intrinsic_gas
gas_left = min(C - intrinsic_gas, evm_gas)
state_gas_reservoir = evm_gas - gas_left
```

유효한 트랜잭션의 `tx.gas`가 `C` 이하면 리저버는 0으로 시작합니다. 이때 상태 비용도 실행 비용과 함께 `gas_left`에서 나갑니다. `C`를 넘으면 초과분이 리저버에 들어갑니다. 기본 가스를 15,000, `tx.gas`를 20,000,000으로 가정하면 런타임 비용을 내기 전 두 풀의 초기값은 16,762,216과 3,222,784입니다. 15,000은 calldata 등 추가 비용을 제외한 가정이며 ABI 호출 전체의 추정값이 아닙니다.

실행 비용은 `gas_left`에서만 낼 수 있습니다. 상태 비용은 리저버를 먼저 쓰고 부족한 만큼 `gas_left`에서 가져옵니다. 따라서 상한을 넘는 가스를 공급하면 상태 예산이 늘어나며 실행 예산은 늘지 않습니다. 전체 `tx.gas` 상한은 4,294,967,295이고 블록 포함 시 각 차원의 남은 예산에도 들어가야 합니다. 잔액, nonce, 수수료 같은 기존 검사도 적용됩니다.

`GAS` opcode로 구현되는 `gasleft()`는 `gas_left`만 봅니다. 리저버는 자식에게 통째로 넘어가며 63/64 규칙은 자식의 실행 예산에만 적용됩니다. 따라서 작은 고정 실행 한도가 있다고 해서 자식이 공유 리저버에서 쓸 수 있는 상태 가스까지 그 한도로 제한되지는 않습니다.

리필은 해당 프레임이 상태 비용을 `gas_left`에서 냈던 미복원분만큼 `gas_left`를 먼저 채우고, 나머지를 리저버로 돌립니다. 이 때문에 `gasleft()`가 증가할 수 있습니다. 명세의 `SSTORE(k, 1); GAS; SSTORE(k, 0); GAS` 순서에서 슬롯의 원래 값이 0이고 리저버도 비어 있었다면, 두 번째 읽기에는 97,920 리필에서 사이에 든 실행 비용을 뺀 만큼이 반영됩니다. 두 쓰기 전체를 감싸서 측정하면 비용 부과와 취소가 모두 포함됩니다. 성공한 자식 프레임을 병합할 때도 복원된 상태 예산이 호출자의 `gas_left`로 이동할 수 있습니다. 그러면 `beforeGas - gasleft()` 같은 뺄셈이 Solidity의 검사 산술에서 언더플로를 일으킬 수 있습니다. [EIP-8037의 계량 경고](https://eips.ethereum.org/EIPS/eip-8037#gas_left-can-increase)

롤백 시 프레임은 리저버 기준선을 복원하고 되돌린 변경의 상태 비용을 취소합니다. revert한 자식은 그 결과 남은 실행 가스를 돌려주지만 예외적으로 중단된 자식은 이를 소진합니다. 성공한 자식을 병합할 때 추가 계산이 필요한 이유는 한 프레임이 앞선 프레임이 만든 상태를 지울 수 있기 때문입니다. 이 규칙은 삭제 호출이 실패해 원래 상태가 복원됐는데도 리필만 남는 일을 막습니다.

## 미사용 예산, 환급, 최종 청구량

비용을 줄이는 세 가지 금액은 규칙이 다릅니다.

| 항목 | 적용 시점 | 주요 제약 |
| --- | --- | --- |
| 미사용 예산 | 정산할 때 실행·리저버의 쓰지 않은 예산 반환 | 미사용 예산이므로 삭제 크레딧의 20% 환급 상한 대상이 아님 |
| 환급 카운터 | 정산할 때 원래 비영 슬롯 삭제 등의 크레딧 적용 | 환급 전 사용량의 최대 20%, 이후 calldata 하한 적용 |
| 상태 리필 | 같은 트랜잭션에서 새 슬롯을 지우는 등 상태 비용을 실행 중 취소 | 출금한 풀과 롤백 규칙을 따르며 상한 있는 카운터와 별개 |

EIP-8037은 마지막 프레임의 남은 예산으로 다음처럼 계산합니다.

```text
used_before_refund = tx.gas - gas_left - state_gas_reservoir
refund = min(used_before_refund // 5, refund_counter)
charged_gas = max(used_before_refund - refund, calldata_floor_gas_cost)
```

리필은 이미 남은 풀과 상태 집계에 반영됐으므로 환급 카운터 크레딧으로 다시 빼지 않습니다. 송신자는 `charged_gas × effectiveGasPrice`를 냅니다. 실효 가스 가격도 바뀌므로 가스 단위의 증가만으로 ETH나 법정화폐 비용의 고정 배율을 알 수는 없습니다. 하한은 데이터가 많은 트랜잭션의 청구량이 내려갈 수 있는 범위를 제한합니다. EIP-2780은 하한의 기존 기본값 21,000을 해당 트랜잭션에 맞게 분해한 기본값으로 바꾸며, calldata 가격에는 별도 포함 예정 변경인 [EIP-7976](https://eips.ethereum.org/EIPS/eip-7976)도 있습니다.

블록 용량은 다르게 합산합니다. 헤더의 `gas_used`는 누적 실행 가스와 누적 상태 가스 중 큰 값입니다. 각 차원은 블록 한도 안에 들어가야 하고 이 최댓값이 기본 수수료 갱신에도 쓰입니다. 함께 포함 예정인 [EIP-7778](https://eips.ethereum.org/EIPS/eip-7778)을 적용하면 환급 카운터 크레딧은 블록의 실행 가스 집계량을 줄이지 않습니다. 상태 리필은 계속 순 상태 사용량을 줄입니다. 반면 영수증의 `cumulative_gas_used`는 환급과 하한 적용 후 트랜잭션에 청구한 양을 합칩니다. 연속한 두 영수증의 차이는 해당 트랜잭션의 유료 가스이며 블록의 최댓값에 더한 몫이 아닙니다. [EIP-8037의 통합·영수증 규칙](https://eips.ethereum.org/EIPS/eip-8037#integration-with-eip-7778)

## 배포, 계정, 위임 코드에 붙는 비용

상태 바이트 계량값은 `SSTORE` 밖의 연산에도 적용됩니다.

| 추가하는 상태 | 명세의 상태 가스 |
| --- | ---: |
| 새 계정 리프와 키, 계량값 120바이트 | 183,600 |
| 새 스토리지 리프와 키, 계량값 64바이트 | 97,920 |
| 새 EIP-7702 위임 표시, 23바이트 | 35,190 |
| 저장하는 런타임 코드 | 바이트당 1,530 |

이는 물리 DB의 모든 바이트를 세는 값이 아닙니다. EIP-8037은 트라이 중간 노드를 제외합니다. 단가 산출은 기준 블록 한도 150M과 평균 사용률 가정에서 연간 상태 증가 120 GiB를 목표로 삼습니다. 이 기준값을 현재 메인넷 한도나 보장된 증가 상한으로 해석해서는 안 됩니다. EIP-8038은 별도로 클라이언트 벤치마크를 사용해 상태 접근·갱신 작업의 가격을 정합니다. [EIP-8037 산출 근거](https://eips.ethereum.org/EIPS/eip-8037#rationale), [EIP-8038 산출 근거](https://eips.ethereum.org/EIPS/eip-8038#rationale)

존재하지 않는 주소로 최상위 배포 트랜잭션을 보내 런타임 코드 24,576바이트를 저장한다면, 계정과 코드의 상태 비용은 183,600 + 24,576 × 1,530 = 37,784,880입니다. 실행 구성 비용에는 트랜잭션 기본값과 생성 접근을 합친 24,000, 코드 해시 비용 6 × ceil(24,576 / 32) = 4,608이 포함됩니다. initcode calldata, initcode 워드 비용, 생성자 명령과 다른 작업은 추가입니다. 이는 구성 비용 계산이며 배포 전체의 추정값이 아닙니다. 차원을 나누면 충분히 채운 리저버가 16,777,216 실행 상한 밖에서 코드 저장 상태 비용을 낼 수 있습니다. 컨트랙트 크기 제한까지 없어지는 것은 아닙니다.

nonce가 0이고 코드가 없어도 잔액이 0이 아니면 이미 존재하는 주소입니다. 이런 사전 입금 주소로 유효하게 배포하면 새 계정 비용은 빠지지만 코드 저장과 실행 비용은 냅니다. 앞선 입금이 계정을 새로 만들었다면 그때 상태 비용을 냈으므로 총 상태 비용이 사라지지는 않습니다. 내부 `CREATE`/`CREATE2`는 선행 검사와 목적지 접근을 마친 뒤 가스를 넘기기 전에 생성 연산을 실행하는 프레임에서 조건부 계정 비용을 냅니다. 이 비용이 부족하면 생성하는 쪽이 중단될 수 있으므로 단순히 자식이 실패 플래그를 반환한다고 설명하면 안 됩니다. 확인한 본문에서 같은 트랜잭션의 `SELFDESTRUCT`는 생성 계정의 상태 비용을 리필하지 않습니다. [EIP-8037 계정 규칙](https://eips.ethereum.org/EIPS/eip-8037#gas-accounting-for-new-accounts)

일반 내부 호출의 콜드 계정 접근은 2,600에서 3,000으로 오르고 웜 접근은 100 그대로입니다. 값을 보내는 `CALL`에는 `CALL_VALUE` 실행 구성 비용 9,000 + 2,300 = 11,300도 붙고 계정을 새로 만들면 상태 가스가 추가됩니다. 계정 쓰기 비용은 트랜잭션 단위로 계산하는 스토리지 쓰기와 달리 연산마다 냅니다. `EXTCODESIZE`와 `EXTCODECOPY`는 계정 접근, 필요한 복사·메모리 비용 외에 두 번째 DB 읽기 몫 100을 더 냅니다. 모두 opcode 구성 비용이며 송금이나 복사 전체의 수수료가 아닙니다. [EIP-8038 계정 가격](https://eips.ethereum.org/EIPS/eip-8038#account-access-pricing)

EIP-7702 권한 위임 처리는 별도 규칙을 따릅니다. 위임 항목마다 기본 실행 가스 7,816을 냅니다. 유효한 위임은 정해진 조건에 따라 계정 생성에 상태 가스 183,600, 첫 계정 쓰기에 실행 가스 9,000, 새 위임 바이트에 상태 가스 35,190을 더하며 각 항목은 위임 계정당 최대 한 번 부과합니다. 송신자 기본 비용, 앞선 위임, 값을 보내는 수신자 비용으로 쓰기가 이미 충당됐다면 계정 쓰기 비용은 건너뜁니다. 트랜잭션 시작 때 위임 표시가 있었다면 지웠다가 다시 설정해도 새 위임 바이트 비용을 내지 않으며 표시를 지워도 그 비용의 리필은 없습니다.

위임 처리는 첫 EVM 프레임보다 앞섭니다. 실행 전 단계에서 실패하면 위임도 롤백됩니다. 그 뒤 최상위 프레임이 revert하거나 OOG로 중단되면 이미 적용한 위임은 남습니다. 따라서 그 상태 비용도 사용한 것으로 남아야 하며, 유지되는 상태의 비용을 롤백으로 리필해서는 안 됩니다. 런타임에 위임 코드를 불러오는 접근은 포인터를 설정하는 작업과 별개입니다. [EIP-2780 위임 처리 규칙](https://eips.ethereum.org/EIPS/eip-2780#eip-7702-authorization-processing)

## 바뀐 가정을 드러내는 테스트

컨트랙트 관리자가 비교할 것은 컴파일러 설정, 트랜잭션 입력, 초기 상태를 고정한 같은 연산의 두 스케줄입니다. 새 슬롯, 이전 트랜잭션에서 초기화한 비영 값 갱신, 삭제, 같은 트랜잭션의 왕복 쓰기, 콜드 경로와 의도적으로 웜으로 만든 경로를 포함합니다. 고정 내부 호출은 영수증과 함께 자식 성공 플래그, 호출자의 최종 상태를 기록합니다. 수수료 추정만으로 실패 처리가 올바른지 확인할 수는 없습니다.

지갑·RPC 관리자는 `eth_estimateGas`에 두 차원과 상태 의존 실행 전 비용을 반영해야 합니다. `eth_call` 성공은 선택한 한도의 트랜잭션이 포함돼 성공한다는 증거가 아닙니다. 클라이언트·제공자별로 시뮬레이션 가스 정책이 다를 수 있으므로 실제 노드 버전과 포크 설정을 시험해야 합니다. ERC-4337 번들러에서는 `gasleft()` 차이만으로 번들의 공유 리저버가 낸 상태 비용을 연산별로 배분할 수 없고 한 연산의 리필이 다른 연산에 영향을 줄 수 있습니다. EIP-8037은 번들러와 `EntryPoint` 구현이 이 차이에만 의존하지 말고 상태 가스를 따로 계산하도록 명시합니다. [호환성](https://eips.ethereum.org/EIPS/eip-8037#backwards-compatibility), [번들 집계](https://eips.ethereum.org/EIPS/eip-8037#interaction-with-erc-4337-bundles)

배포 도구는 고정 한도를 가진 사전 서명 팩토리 트랜잭션도 따로 확인해야 합니다. EIP-8037은 재조정이 처음부터 켜진 새 네트워크에서 기존 한도가 부족할 수 있다고 경고합니다. 이미 배포된 팩토리가 포크 때문에 다시 배포되는 것은 아닙니다. 실제 대응 대상은 시스템이 상태를 새로 만드는 지점, 가스를 고정해 넘기는 지점, `gasleft()`를 전체 예산으로 취급하는 지점입니다.

## 함께 보면 좋을 자료

- [EIP-7825: Transaction Gas Limit Cap](https://eips.ethereum.org/EIPS/eip-7825): 리저버 모델에서도 유지하는 실행 가스 상한입니다.
- [EIP-7928: Block-Level Access Lists](https://eips.ethereum.org/EIPS/eip-7928): 상태 접근 기록과 생성 연산의 접근 시점 제약입니다.
- [EIP-7778: Block Gas Accounting without Refunds](https://eips.ethereum.org/EIPS/eip-7778): 유료 트랜잭션 가스와 블록 용량 집계가 달라지는 이유입니다.

## 참고 자료

- [EIP-8037](https://eips.ethereum.org/EIPS/eip-8037), [고정 커밋 원문](https://github.com/ethereum/EIPs/blob/8b1cae50601fb194452db0ed857f4c237ca62c1f/EIPS/eip-8037.md): Ethereum EIPs, 조회일 2026년 10월 15일 UTC.
- [EIP-8038](https://eips.ethereum.org/EIPS/eip-8038), [고정 커밋 원문](https://github.com/ethereum/EIPs/blob/8b1cae50601fb194452db0ed857f4c237ca62c1f/EIPS/eip-8038.md): Ethereum EIPs, 조회일 2026년 10월 15일 UTC.
- [EIP-2780](https://eips.ethereum.org/EIPS/eip-2780), [고정 커밋 원문](https://github.com/ethereum/EIPs/blob/8b1cae50601fb194452db0ed857f4c237ca62c1f/EIPS/eip-2780.md): Ethereum EIPs, 조회일 2026년 10월 15일 UTC.
- [EIP-7773](https://eips.ethereum.org/EIPS/eip-7773), [고정 커밋 원문](https://github.com/ethereum/EIPs/blob/8b1cae50601fb194452db0ed857f4c237ca62c1f/EIPS/eip-7773.md): 포크 범위와 활성화 표, 조회일 2026년 10월 15일 UTC.
- [Glamsterdam Testnet Announcement](https://blog.ethereum.org/2026/09/17/glamsterdam-testnet-announcement): 이더리움 재단, 조회일 2026년 10월 15일 UTC.
- [EIP-2200](https://eips.ethereum.org/EIPS/eip-2200), [EIP-2929](https://eips.ethereum.org/EIPS/eip-2929), [EIP-3529](https://eips.ethereum.org/EIPS/eip-3529): 비교 기준 스토리지·환급 규칙, 조회일 2026년 10월 15일 UTC.
- [EIP-140](https://eips.ethereum.org/EIPS/eip-140): `REVERT`, 조회일 2026년 10월 15일 UTC.
- [EIP-7623](https://eips.ethereum.org/EIPS/eip-7623), [EIP-7976](https://eips.ethereum.org/EIPS/eip-7976), [EIP-7708](https://eips.ethereum.org/EIPS/eip-7708): calldata 하한과 전송 로그, 조회일 2026년 10월 15일 UTC.
