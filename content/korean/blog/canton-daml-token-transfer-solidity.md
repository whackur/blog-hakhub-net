---
title: "Canton Daml로 토큰 전송하기: Solidity와 상태·권한 비교"
meta_title: ""
description: "같은 100 단위 전송을 Daml 보유 계약과 Solidity 잔액으로 구현하고, 생성·전송 권한과 가시성의 차이를 확인합니다."
date: 2026-10-15T15:45:00+09:00
lastmod: 2026-10-15T20:49:42+09:00
image: "/images/posts/canton-daml-token-transfer-solidity/cover-rewrite-20261015.png"
categories: ["Blockchain"]
tags: ["canton", "daml", "solidity", "smart-contracts", "tutorial"]
author: "whackur"
slug: "canton-daml-token-transfer-solidity"
translationKey: "canton-daml-token-transfer-solidity"
draft: false
---

Alice가 가진 토큰 100 단위를 Bob에게 모두 보내면, 다음에 그 100 단위를 쓸 수 있는 사람은 Bob입니다. **Solidity 예제는 주소별 잔액을 갱신하고, Canton에서 실행할 Daml 예제는 Alice의 보유 계약을 소비한 뒤 Bob의 보유 계약을 만듭니다.** 같은 전송 결과를 서로 다른 상태와 권한으로 표현합니다.

두 코드는 이 차이를 설명하기 위한 교육용 예제입니다. Daml 코드는 Canton Token Standard(CIP-0056·CIP-0112) 구현이나 Canton Coin이 아니며, Solidity 코드도 ERC-20 구현이 아닙니다. 외부 공개 네트워크에 배포한 결과를 다루지 않습니다.

## 잔액 하나와 보유 계약 하나

전송 전 Alice는 100 단위, Bob은 0 단위를 보유한다고 정합니다. 수수료와 소수 자릿수는 없고, 보유량 전체만 전송합니다. Daml에서 `TokenLot`은 보유 계약의 템플릿이고, H1·H2는 서로 다른 계약 ID를 설명하기 위한 이름입니다.

| 상태 | Solidity `BalanceBook` | Daml `TokenLot` |
| --- | --- | --- |
| 전송 전 | Alice 잔액 100, Bob 잔액 0 | H1: Issuer 발행, Alice 보유, 100 단위 |
| 전송 성공 후 | Alice 잔액 0, Bob 잔액 100 | H1은 비활성화되고 H2: Issuer 발행, Bob 보유, 100 단위 생성 |
| 다음 지출에 쓰는 값 | 같은 컨트랙트의 Bob 잔액 | 새 계약 ID H2 |

Solidity의 mapping은 주소별 합계를 저장합니다. Daml 코드는 개별 보유 건을 저장하므로 Bob에게 기존 40 단위 계약이 있었다면 전송 후 40 단위와 100 단위 계약이 따로 남습니다. 140 단위 계약으로 자동 병합되지 않습니다. Bob의 잔액을 표시하는 앱은 조회할 수 있는 활성 계약 중 holder가 Bob이고 발행자·템플릿이 같은 계약의 수량을 합산해야 합니다. 이는 아래 코드가 택한 자료 구조의 차이입니다. [Solidity mapping 문서](https://github.com/argotorg/solidity/blob/v0.8.37/docs/types/mapping-types.rst)와 [Daml 계약·choice 설명](https://docs.canton.network/appdev/modules/m3-choices)에서 각각의 동작을 확인할 수 있습니다.

## Daml은 보유 계약을 교체합니다

`daml/Lots.daml`에 다음 코드를 저장합니다. `Party`는 원장의 당사자 식별자입니다. `units`는 정수 수량이며, `ensure`는 0 이하인 계약의 생성을 거부합니다.

```haskell
module Lots where

template TokenLot
  with
    issuer : Party
    holder : Party
    units : Int
  where
    signatory issuer
    observer holder
    ensure units > 0

    choice Send : ContractId TokenLot
      with recipient : Party
      controller holder
      do
        assertMsg "recipient must differ" (recipient /= holder)
        create TokenLot with issuer; holder = recipient; units
```

Issuer가 `TokenLot issuer alice 100`을 생성하면 H1이 활성 계약이 됩니다. Alice가 H1의 `Send`를 Bob을 수신자로 실행(exercise)하면, 기본 소비형 choice가 H1을 archive하고 본문이 H2를 생성합니다. 반환값은 H2의 ID입니다. H1의 `holder`를 제자리에서 수정하는 동작이 아닙니다. 계약 필드와 기본 소비형 choice의 규칙은 [Daml 언어 참조](https://docs.canton.network/appdev/reference/daml-language-reference)에 정의돼 있습니다.

부분 전송 기능은 없습니다. 100 단위 중 30만 보내려면 입력 계약을 소비하고 Bob의 30 단위 계약과 Alice의 70 단위 잔여 계약을 같은 트랜잭션에서 생성하도록 확장해야 합니다. 입력·출력 수량 보존도 코드에서 검사해야 합니다.

### 생성 승인과 전송 승인은 다릅니다

| 선언 | 이 코드에서 부여하는 역할 |
| --- | --- |
| `signatory issuer` | 계약 생성에 Issuer의 권한이 필요합니다. |
| `observer holder` | 보유자가 계약을 볼 수 있습니다. 관찰자라는 이유만으로 전송 권한이 생기지는 않습니다. |
| `controller holder` | 현재 보유자가 `Send`를 실행합니다. |

Alice가 단독으로 `Send`를 제출해도 H2를 만드는 데 필요한 Issuer의 권한은 충족됩니다. choice의 결과 동작에는 그 choice의 실행 당사자와 원래 계약 signatory의 권한이 제공되기 때문입니다. 위임은 **그 exercise의 결과 동작 범위**에 적용됩니다. Alice가 별도의 명령으로 Issuer 명의 계약을 마음대로 발행할 권한을 얻는 것은 아닙니다. 반대로 Issuer는 H1의 signatory여도 `controller holder`인 Alice 대신 `Send`를 혼자 실행하지 못합니다. [공식 권한 모델](https://docs.canton.network/appdev/modules/m3-authorization)이 이 구분을 설명합니다.

이 짧은 모델은 발행자를 신뢰합니다. Issuer는 별도의 `TokenLot`을 추가 발행할 수 있고, signatory가 제어하는 암묵적 `Archive` choice로 계약을 종료할 수도 있습니다. 총발행량 상한이나 담보 검증은 구현하지 않았습니다. 아래 Solidity 코드에는 생성자 이후 추가 발행 경로가 없으므로 발행자 권한까지 같은 모델은 아닙니다.

Bob의 수락도 요구하지 않습니다. Bob은 H1의 `Send` controller가 아니며 H2의 signatory도 아닙니다. H2에서는 observer이자 다음 `Send`의 controller가 됩니다. 수신 동의나 수신자의 의무를 표현하려면 제안·수락 절차 또는 사전 승인 계약 등을 설계해야 합니다. `observer` 선언이 동의를 대신하지는 않습니다. 공식 권한 문서의 propose-accept 예제가 이 문제를 다룹니다.

## Solidity는 호출자 잔액을 옮깁니다

`BalanceBook.sol`은 생성자에서 지정한 주소에 100 단위를 한 번 배정합니다. `sendAll`에는 출금 주소 인자가 없고, 현재 호출자의 잔액만 읽습니다.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.37;

contract BalanceBook {
    mapping(address => uint256) public balance;

    constructor(address initialHolder) {
        require(initialHolder != address(0), "zero holder");
        balance[initialHolder] = 100;
    }

    function sendAll(address recipient) external {
        require(recipient != address(0), "zero recipient");
        require(recipient != msg.sender, "same recipient");
        uint256 units = balance[msg.sender];
        require(units > 0, "no balance");
        balance[msg.sender] = 0;
        balance[recipient] += units;
    }
}
```

Alice가 직접 호출하면 `msg.sender`는 Alice의 주소입니다. 잔액이 없는 제3자가 호출하면 그 제3자의 잔액 0을 읽어 실패합니다. 컨트랙트를 거쳐 일반적인 외부 호출을 하면 `msg.sender`는 바로 앞 호출 컨트랙트가 됩니다. 원래 사용자 주소가 자동으로 유지되는 값은 아닙니다. [Solidity 전역 변수 문서](https://github.com/argotorg/solidity/blob/v0.8.37/docs/units-and-global-variables.rst)의 정의를 적용한 동작입니다.

`public balance`에는 주소를 받아 잔액을 반환하는 getter가 생기며, 아직 설정하지 않은 주소의 값은 0입니다. 전송은 같은 컨트랙트 안에서 송신자 항목을 0으로 만들고 수신자 항목에 수량을 더합니다. 수신자에게 잔액이 있다면 합산합니다. 이 코드는 이벤트, allowance, 표준 `transfer` 등 ERC-20 인터페이스를 제공하지 않으므로 ERC-20 지갑 호환성을 기대할 수 없습니다.

Solidity 0.8의 일반 산술은 오버플로를 검사하며 이 코드에는 `unchecked`가 없습니다. `require`나 산술 검사가 실패하면 호출의 상태 변경은 되돌아갑니다. 초기 100 단위를 새로 발행하는 함수 없이 옮기는 코드이므로 정상 경로에서는 총량 100을 보존합니다. [오류 처리와 산술 규칙](https://github.com/argotorg/solidity/blob/v0.8.37/docs/control-structures.rst)을 기준으로 읽으면 됩니다.

## 실패한 전송과 보이는 정보

| 시도 | Daml 예제 | Solidity 예제 |
| --- | --- | --- |
| 다른 당사자가 Alice 자산을 전송 | H1을 볼 수 있는 Issuer도 `Send`의 controller가 아니어서 거부 | 잔액 없는 호출자는 자신의 잔액 검사에서 거부 |
| 자기 자신에게 전송 | choice의 `assertMsg`에서 거부 | `require`에서 거부 |
| 성공 후 같은 자산을 다시 지출 | 소비된 H1로 exercise할 수 없음 | Alice 잔액이 0이어서 재호출 거부 |

Daml의 소비와 생성은 한 트랜잭션입니다. choice가 실패했다고 H1만 사라진 상태가 확정되지 않습니다. archive는 활성 계약에서 제외한다는 뜻이며 과거 기록을 지운다는 뜻도 아닙니다. 소비된 ID의 재사용을 막는 [원장 규칙](https://docs.canton.network/overview/reference/ledger-model-detailed)과 Solidity의 잔액 검사는 같은 방식이 아닙니다. 여기서 재호출은 두 번째 함수 호출을 뜻하며, 서명된 트랜잭션의 네트워크 재전파나 nonce 검증과 구분해야 합니다.

정보가 보이는 범위도 다릅니다. 공개 EVM에서는 이 mapping의 잔액이 비밀이 아닙니다. `private`로 바꿔도 블록체인 데이터 자체를 숨기지는 못합니다. [Solidity 가시성 문서](https://github.com/argotorg/solidity/blob/v0.8.37/docs/contracts/visibility-and-getters.rst)는 접근 제한과 데이터 비밀성을 구분합니다.

Canton은 당사자의 역할과 트랜잭션 구조에 따라 관련 부분을 배포합니다. 이 예제에서 Issuer는 H1·H2의 signatory이고 Alice는 H1의 stakeholder이자 `Send`의 실행 당사자이므로 둘 다 그 choice의 결과인 H2 생성을 봅니다. Bob은 H2의 observer로 새 보유 계약을 봅니다. Bob만 알고 Alice와 Issuer에게는 결과가 숨겨지는 구조가 아닙니다. [원장 모델의 informee·witness 규칙](https://docs.canton.network/overview/reference/ledger-model-detailed#informee)과 [프라이버시 모델](https://docs.canton.network/overview/learn/privacy-model)이 근거입니다.

계약을 볼 수 있는 권한과 실행할 권한은 별개이며, Party의 가시성과 그 Party를 호스팅하는 participant의 데이터 취급도 구분해야 합니다. 앱 서버와 로그에 전달한 정보까지 Daml 선언만으로 보호되지는 않습니다. 실제 Ledger API 접근에는 인증·사용자 권한·Party 호스팅도 필요합니다. 로컬 테스트의 Party 할당은 이 운영 구성을 검증하지 않습니다. [Ledger API 권한 문서](https://docs.canton.network/appdev/deep-dives/authorization)를 참고하세요.

## 로컬 실행과 확인 범위

Daml은 [DPM](https://docs.canton.network/sdks-tools/cli-tools/dpm)을 준비하고 SDK `3.6.0`으로 고정했습니다. 프로젝트 루트의 `daml.yaml`은 다음과 같습니다.

```yaml
sdk-version: 3.6.0
name: transfer-comparison
version: 0.1.0
source: daml
dependencies:
  - daml-prim
  - daml-stdlib
  - daml-script
```

`daml/Checks.daml`의 두 Script는 전송 동작과 발행자 정책을 확인합니다. 권한 검사는 H1을 이미 볼 수 있는 Issuer로 제출하므로 단순한 비가시성 실패와 구분됩니다.

```haskell
module Checks where

import Daml.Script
import Lots

transferChecks : Script ()
transferChecks = script do
  issuer <- allocateParty "Issuer"
  alice <- allocateParty "Alice"
  bob <- allocateParty "Bob"
  original <- submit issuer do
    createCmd (TokenLot issuer alice 100)
  submitMustFail issuer do
    exerciseCmd original (Send bob)
  submitMustFail alice do
    exerciseCmd original (Send alice)
  unchanged <- queryContractId alice original
  assert (unchanged == Some (TokenLot issuer alice 100))
  received <- submit alice do
    exerciseCmd original (Send bob)
  old <- queryContractId issuer original
  new <- queryContractId bob received
  assert (old == None)
  assert (new == Some (TokenLot issuer bob 100))
  submitMustFail alice do
    exerciseCmd original (Send bob)

policyChecks : Script ()
policyChecks = script do
  issuer <- allocateParty "Issuer"
  alice <- allocateParty "Alice"
  bob <- allocateParty "Bob"
  submitMustFail issuer do createCmd (TokenLot issuer alice 0)
  submitMustFail issuer do createCmd (TokenLot issuer alice (-1))
  submitMustFail alice do createCmd (TokenLot issuer alice 100)
  first <- submit issuer do createCmd (TokenLot issuer alice 100)
  second <- submit issuer do createCmd (TokenLot issuer bob 40)
  _ <- submit alice do exerciseCmd first (Send bob)
  lots <- query @TokenLot bob
  assert (length lots == 2)
  assert (sum (map (\(_, lot) -> lot.units) lots) == 140)
  submitMustFail bob do exerciseCmd second Archive
  submit issuer do exerciseCmd second Archive
```

```bash
dpm install 3.6.0
dpm build
dpm test
```

새로 실행한 `dpm build`와 `dpm test`가 성공했습니다. 위 `transferChecks`와 `policyChecks`가 각각 통과했습니다. 정책 검사에서는 0·음수 계약 생성과 보유자의 임의 발행을 거부하고, Bob의 40·100 단위 계약이 별개로 남는지 확인했습니다. 보유자의 직접 `Archive`는 실패하고 Issuer의 `Archive`는 성공했습니다. 사용한 번들 SDK는 `3.6.0`, 컴파일러·Script는 `3.6.2`, Java는 `21.0.12.1`입니다. 같은 패키지에 템플릿과 테스트를 둬 `daml-script` 의존성이 포함된다는 빌드 경고가 있습니다. 배포용 패키지는 [Daml Script 안내](https://docs.canton.network/sdks-tools/cli-tools/daml-script)에 따라 테스트 패키지와 분리해야 합니다.

Solidity는 아래 설정을 `input.json`으로 저장하면 테스트와 같은 EVM target으로 컴파일할 수 있습니다. 생성자 인자는 Alice의 주소이며, 배포 후 Alice로 `sendAll(Bob 주소)`를 호출합니다.

```json
{
  "language": "Solidity",
  "sources": {"BalanceBook.sol": {"urls": ["BalanceBook.sol"]}},
  "settings": {
    "optimizer": {"enabled": false},
    "evmVersion": "shanghai",
    "outputSelection": {"*": {"*": ["abi", "evm.bytecode.object"]}}
  }
}
```

```bash
npm install --save-exact solc@0.8.37
npx solcjs --standard-json --base-path . < input.json > output.json
```

로컬 런타임 검증에는 solc-js `0.8.37`, ethers `6.15.0`, Ganache `7.9.2`, Node `26.7.0`을 사용했습니다. optimizer는 끄고 컴파일러의 EVM target과 Ganache hardfork를 `shanghai`로 맞췄습니다. Alice→Bob 전송 후 잔액 0·100, Bob→Alice 반환 후 100·0을 확인했습니다. 잔액 없는 호출자, 자기 전송, 0 주소 수신자, 두 번째 지출은 실제 채굴된 실패 트랜잭션으로 확인했고 잔액도 유지됐습니다. 0 주소로 초기 보유자를 지정한 배포도 거부됐습니다. Ganache는 해당 Node 환경에서 네이티브 µWS 대신 JavaScript fallback으로 실행됐습니다.

Daml Script의 로컬 테스트 원장과 프로세스 내부 EVM에서 확인한 결과입니다. 다중 participant 합의, 동시 제출 경쟁, 지갑 연동, 공개 네트워크 배포, 수수료·성능은 검증하지 않았습니다.

## 표준 호환성에는 별도 구현이 필요합니다

2026년 10월 15일 KST에 직접 확인한 공식 문서에서 [CIP-0056](https://github.com/canton-foundation/cips/blob/main/cip-0056/cip-0056.md)은 `Final`, [CIP-0112](https://github.com/canton-foundation/cips/blob/main/cip-0112/cip-0112.md)는 `Approved`입니다. CIP-0056은 지갑과 앱이 자산별 내부 구현에 의존하지 않고 사용할 표준 API를 정의하며, CIP-0112는 Token Standard V2의 프라이버시·성능·회계 처리를 다룹니다.

`TokenLot`의 이름을 표준의 holding과 비슷하게 바꾸거나 로컬 전송을 성공시켜도 이 인터페이스와 규칙이 구현되지는 않습니다. 실제 자산을 만들 때는 목표 네트워크가 지원하는 패키지, 전송·할당 인터페이스, 발행 정책과 수신 승인 조건을 맞춰야 합니다. CIP 상태는 특정 지갑의 지원이나 네트워크 배포·채택 여부의 증거도 아닙니다.

이 비교에서 가져갈 설계 기준은 상태의 단위와 권한입니다. 주소별 합계를 수정하는지, 특정 보유 계약을 소비하는지부터 정해야 중복 지출 처리, 잔액 조회, 수신 동의의 위치가 명확해집니다.

## 함께 보면 좋을 자료

- [Daml 권한 모델](https://docs.canton.network/appdev/modules/m3-authorization): 수신 동의와 제안·수락 패턴을 확장할 때 유용합니다.
- [Canton Token Standard 안내](https://docs.canton.network/overview/reference/cip-0056): 교육용 보유 계약 다음에 살펴볼 실제 표준 인터페이스입니다.
- [Solidity mapping](https://github.com/argotorg/solidity/blob/v0.8.37/docs/types/mapping-types.rst): 주소별 잔액과 getter의 동작을 설명합니다.

## 참고 자료

공식 문서 조회일은 2026년 10월 15일 KST입니다. 코드는 이 글을 위한 자체 교육용 예제입니다.

- [Daml language reference](https://docs.canton.network/appdev/reference/daml-language-reference)
- [Daml choices](https://docs.canton.network/appdev/modules/m3-choices)
- [Daml authorization model](https://docs.canton.network/appdev/modules/m3-authorization)
- [Detailed ledger model](https://docs.canton.network/overview/reference/ledger-model-detailed)
- [Privacy model](https://docs.canton.network/overview/learn/privacy-model)
- [Ledger API authorization](https://docs.canton.network/appdev/deep-dives/authorization)
- [DPM](https://docs.canton.network/sdks-tools/cli-tools/dpm)
- [Daml Script](https://docs.canton.network/sdks-tools/cli-tools/daml-script)
- [SDK 3.6.0 release](https://github.com/digital-asset/dpm-assembly/releases/tag/3.6.0)
- [Solidity mappings](https://github.com/argotorg/solidity/blob/v0.8.37/docs/types/mapping-types.rst)
- [Solidity global variables](https://github.com/argotorg/solidity/blob/v0.8.37/docs/units-and-global-variables.rst)
- [Solidity control structures](https://github.com/argotorg/solidity/blob/v0.8.37/docs/control-structures.rst)
- [Solidity visibility and getters](https://github.com/argotorg/solidity/blob/v0.8.37/docs/contracts/visibility-and-getters.rst)
- [CIP-0056](https://github.com/canton-foundation/cips/blob/main/cip-0056/cip-0056.md)
- [CIP-0112](https://github.com/canton-foundation/cips/blob/main/cip-0112/cip-0112.md)
