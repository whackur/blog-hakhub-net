---
title: "Canton Daml로 100 단위 전송하기: Solidity와 상태·권한 비교"
meta_title: ""
description: "Daml 보유 계약 하나를 소비하고 새로 만드는 작은 전송을 Solidity 잔액 mapping과 비교하고, 권한과 실패 경로를 로컬 테스트로 확인합니다."
date: 2026-10-15T15:45:00+09:00
lastmod: 2026-10-15T15:45:00+09:00
image: "/images/posts/canton-daml-token-transfer-solidity/cover.png"
categories: ["Blockchain"]
tags: ["canton", "daml", "solidity", "smart-contracts", "tutorial"]
author: "whackur"
slug: "canton-daml-token-transfer-solidity"
translationKey: "canton-daml-token-transfer-solidity"
draft: false
---

Alice가 가진 100 단위를 Bob에게 전부 보냅니다. Solidity에서는 같은 컨트랙트의 잔액 두 칸을 바꾸면 됩니다. Canton에서 사용하는 Daml에서는 Alice의 보유 계약을 소비하고 Bob의 보유 계약을 새로 만듭니다. 결과 수량은 같지만, 상태를 표현하는 단위와 실행 권한을 검사하는 위치가 다릅니다.

이 글은 그 차이를 직접 실행해 보는 개발자 튜토리얼입니다. 발행자 Issuer, 소유자 Alice, 수신자 Bob만 등장합니다. 부분 전송, 수수료, 지갑 연결은 생략했습니다. 두 예제는 교육용으로 직접 작성했으며, Daml 예제는 Canton Coin도, Canton Token Standard 구현도, ERC-20도 아닙니다. 외부 네트워크에 배포한 토큰도 없습니다.

## 실행 도구와 사양의 기준

**확인일은 2026년 10월 15일 KST입니다.** [공식 SDK 배포 저장소](https://github.com/digital-asset/dpm-assembly/releases/tag/3.6.0)의 최신 안정 번들은 10월 8일 공개된 `3.6.0`입니다. 이 글도 해당 버전을 사용했습니다. [번들 구성표](https://github.com/digital-asset/dpm-assembly/blob/3.6.0/latest/open-source/3.6.yaml)를 보면 내부 Daml 컴파일러와 Script는 `3.6.2`, Canton은 `3.6.1`, DPM은 `1.0.22`입니다. 번들의 번호가 모든 구성요소의 번호와 같지는 않습니다.

이와 별도로 10월 14일 갱신된 [공식 호환성 대시보드](https://docs.canton.network/shared/version-compatibility-dashboard)는 MainNet에 SDK `3.5.12`, Canton `3.5.19`, Splice `0.8.4`를 표시합니다. DevNet은 SDK `3.6.0`, Canton `3.6.1`, Splice `0.9.1`입니다. 이는 대시보드에서 확인한 값이며, 이 실습에서 네트워크 노드를 직접 조회한 결과는 아닙니다. 최신 SDK 출시만으로 MainNet이 같은 버전을 채택했다고 판단하면 안 됩니다.

Daml은 계약과 권한을 작성하는 언어이고, Daml-LF는 컴파일된 프로그램을 표현하는 중간 언어입니다. SDK는 컴파일·테스트 도구 묶음입니다. Canton 프로토콜과 그 실행 소프트웨어, Splice 애플리케이션, Token Standard 패키지도 각각 구분해야 합니다. DAR는 Daml-LF 프로그램과 의존성·메타데이터를 담는 배포 파일입니다. [컴파일러 문서](https://docs.canton.network/sdks-tools/development-tools/daml-compiler)가 이 관계를 설명합니다.

## 전송 전후의 정확한 상태

이 실습의 단위에는 소수점이 없습니다. Daml의 `Int`는 부호 있는 64비트 정수이므로 양수 범위는 `1`부터 `9,223,372,036,854,775,807`까지입니다. Solidity에서는 `uint64`를 사용하되 최초 발행량의 상한을 같은 값으로 제한했습니다. 양쪽 모두 0 단위 전송과 자기 자신에게 보내기를 허용하지 않습니다. 부동소수점 환산이나 소수 자릿수 변환 없이 상태 변경만 비교하려는 선택입니다. [Daml 언어 참조](https://docs.canton.network/appdev/reference/daml-language-reference), [Solidity 정수형](https://github.com/argotorg/solidity/blob/v0.8.37/docs/types/value-types.rst)을 기준으로 했습니다.

| 시점 | Solidity의 현재 저장값 | Daml의 활성 보유 계약 |
| --- | --- | --- |
| 전송 전 | `balance[Alice] = 100`, `balance[Bob] = 0` | `H1 = Holding(Issuer, Alice, 100)` |
| 전송 성공 후 | `balance[Alice] = 0`, `balance[Bob] = 100` | `H2 = Holding(Issuer, Bob, 100)` |
| 이전 상태의 취급 | 같은 mapping의 값을 갱신 | H1은 archive, H2는 새로운 계약 ID |

![Solidity는 잔액 mapping을 갱신하고 Daml은 Alice의 H1을 소비한 뒤 Bob의 H2를 생성하는 비교도](/images/posts/canton-daml-token-transfer-solidity/cover.png)

*직접 작성한 두 예제의 상태 변화입니다. Daml의 소비와 생성은 하나의 원자적 트랜잭션에 포함됩니다. H1·H2는 설명용 이름이며 실제 계약 ID가 아닙니다.*

## Solidity의 작은 잔액 mapping

`TinyToken.sol`을 다음과 같이 작성합니다. 생성자에서 Alice의 잔액을 설정하고, `transferAll`은 호출자의 잔액 전부를 수신자 잔액에 더합니다. 이벤트, allowance, `totalSupply` 같은 ERC-20 API를 구현하지 않았으므로 ERC-20 토큰으로 사용하면 안 됩니다.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.37;

contract TinyToken {
    mapping(address => uint64) public balance;

    constructor(address alice, uint64 quantity) {
        require(alice != address(0), "zero owner");
        require(quantity > 0 && quantity <= uint64(type(int64).max), "quantity");
        balance[alice] = quantity;
    }

    function transferAll(address to) external {
        require(to != address(0) && to != msg.sender, "recipient");
        uint64 quantity = balance[msg.sender];
        require(quantity > 0, "empty holding");
        balance[msg.sender] = 0;
        balance[to] += quantity;
    }
}
```

Alice가 `transferAll(Bob)`을 호출하면 `msg.sender`는 Alice의 주소입니다. 코드에 `from` 인자가 없으므로 다른 주소를 넣어 Alice의 잔액을 지정할 수 없습니다. 잔액이 없는 제3자가 같은 함수를 호출하면 자신의 잔액 0을 읽고 실패합니다. 일반적인 컨트랙트 간 호출에서는 `msg.sender`가 바로 앞 호출 컨트랙트라는 점도 구분해야 합니다. 사용자 지갑 주소가 항상 그대로 전달되는 값은 아닙니다. [Solidity 전역 변수 문서](https://github.com/argotorg/solidity/blob/v0.8.37/docs/units-and-global-variables.rst)의 정의입니다.

성공 시 같은 컨트랙트 주소 안에서 mapping의 두 항목이 바뀝니다. Bob이 이미 잔액을 가졌다면 그 잔액에 합산합니다. Solidity 0.8 계열의 일반 정수 연산은 오버플로를 검사하며, 이 코드에는 `unchecked`가 없습니다. 발행은 생성자 한 번뿐이고 총량도 위 상한 이하라 정상 경로의 합산이 `uint64` 범위를 넘지 않습니다. 중간에 `require`나 산술 검사가 실패하면 해당 호출의 상태 변경은 revert됩니다. [제어 구조와 오류 처리](https://github.com/argotorg/solidity/blob/v0.8.37/docs/control-structures.rst)를 참고하세요.

## Daml의 작은 보유 계약

Daml 프로젝트의 `daml/Token.daml`에는 다음 코드를 넣습니다. `template`은 계약의 자료형과 허용 동작을 정의하고, `create`는 그 템플릿으로 개별 계약 인스턴스를 만듭니다. 같은 템플릿으로 여러 보유 계약을 만들 수 있으며 각 계약은 고유한 ID로 구분됩니다.

```haskell
module Token where

template Holding
  with
    issuer : Party
    owner : Party
    quantity : Int
  where
    ensure quantity > 0
    signatory issuer
    observer owner

    choice Transfer : ContractId Holding
      with newOwner : Party
      controller owner
      do
        assertMsg "self-transfer is disabled" (newOwner /= owner)
        create this with owner = newOwner
```

`issuer`, `owner`, `quantity`는 계약 생성 때 정해지는 필드입니다. 생성된 계약의 `owner` 필드를 제자리에서 수정하는 연산은 없습니다. `create this with owner = newOwner`는 기존 필드들을 복사하고 소유자만 바꾼 **새 계약을 생성**합니다. 원래 계약의 내용을 변경하지 않습니다. [템플릿·선택지 언어 참조](https://docs.canton.network/appdev/reference/daml-language-reference)를 기준으로 읽으면 됩니다.

`Transfer` 앞에 `nonconsuming`을 쓰지 않았으므로 기본 consuming choice입니다. Alice가 이를 exercise하면 H1을 소비하고 본문에서 H2를 만듭니다. choice가 반환하는 `ContractId Holding`은 Bob의 새 보유 계약을 가리킵니다. 이 예제에서는 H1 하나가 H2 하나로 바뀌며 `issuer`와 `quantity`는 보존됩니다.

이때 Bob에게 기존 40 단위 계약이 있었다면 140 단위 계약으로 자동 합쳐지지 않습니다. 기존 40 단위 계약과 새 100 단위 계약이 따로 남습니다. 잔액 화면이 필요하면 같은 템플릿·발행자에 속하고 조회 권한이 있는 활성 보유 계약들을 모아 수량을 합산해야 합니다. 이 예제에는 계약 병합 기능도 없습니다.

여기에는 수량을 받는 전송 인자가 없습니다. 따라서 Alice의 100 단위 중 30만 보내는 동작도 없습니다. 부분 전송을 추가하려면 보낼 수량을 검사하고, Bob의 30 단위 계약과 Alice의 70 단위 잔여 계약을 같은 트랜잭션에서 만들어야 합니다. 그때는 입력과 출력의 총량 보존 조건도 코드로 확인해야 합니다. 여기서 단순성을 위해 생략한 기능이지, Daml이 자동으로 잔돈을 만드는 것은 아닙니다.

## signatory와 controller의 권한

`Party`는 원장에서 권한을 부여하는 당사자 식별자입니다. 코드에 임의의 Party 값을 적는다고 그 당사자의 권한을 얻지는 않습니다. 실제 시스템에서는 인증된 제출자가 어떤 Party로 명령을 제출할 수 있는지, 해당 Party를 어떤 participant가 호스팅하는지 등도 맞아야 합니다. 아래 Script는 로컬 테스트용 Party를 할당하므로 외부 계정 발급이 필요 없습니다. [권한 설명](https://docs.canton.network/appdev/deep-dives/authorization)을 참고하세요.

| 선언 | 이 예제의 당사자 | 의미 |
| --- | --- | --- |
| `signatory issuer` | Issuer | 계약 생성을 승인하고, 정의된 choice 결과에 필요한 자신의 권한을 위임 |
| `observer owner` | Alice, 전송 후 Bob | 해당 보유 계약을 볼 수 있음 |
| `controller owner` | H1에서는 Alice | `Transfer`를 실행할 권한이 있음 |

처음 H1을 직접 생성할 때는 Issuer의 권한이 필요합니다. Alice는 observer이므로 H1을 볼 수 있지만, 관찰 권한 자체가 전송 권한은 아닙니다. Alice가 전송할 수 있는 근거는 `controller owner`입니다. Issuer 역시 H1을 볼 수 있어도 Alice가 소유한 H1의 `Transfer`를 혼자 실행하지 못합니다. signatory와 모든 choice의 controller는 같은 개념이 아닙니다.

H2 생성에는 다시 `signatory issuer`가 필요합니다. 그런데 Alice 혼자 전송을 제출해도 되는 이유는 H1의 choice를 실행하는 동안 해당 계약 signatory의 권한이 결과 동작에 전달되기 때문입니다. Issuer는 H1 생성 시 이 코드가 허용하는 결과를 승인한 것입니다. 매 지출마다 Issuer가 새로 서명해야 한다는 뜻이 아닙니다. 해당 exercise의 범위에서 허용된 위임이며, Alice가 임의의 계약을 Issuer 명의로 발행할 권한까지 얻는 것도 아닙니다. [권한 규칙](https://docs.canton.network/appdev/modules/m3-authorization)이 이 구분을 설명합니다.

이 모델에는 분명한 발행자 신뢰가 남습니다. Issuer는 별개의 `Holding`을 추가 생성할 수 있고, signatory가 제어하는 암묵적 `Archive`로 보유 계약을 종료할 수도 있습니다. 총발행량 상한이나 준비금 검증은 없습니다. Solidity 예제는 생성자 이후 추가 발행 경로가 없으므로 두 예제의 발행자 권한까지 같다고 보면 안 됩니다. 비교 대상은 전송 시 상태와 권한의 표현입니다.

Bob의 수락도 자동으로 생기지 않습니다. Bob은 새 계약의 observer이며 signatory가 아니기 때문에 Alice의 전송에 Bob의 별도 승인을 요구하지 않습니다. 원치 않는 자산 수령을 막거나 수신자의 의무를 모델링하려면 수락 choice, 제안·수락 절차 또는 명시적 사전 승인을 추가해야 합니다. 단순히 `observer newOwner`를 적는 것으로 수신 동의를 표현할 수는 없습니다.

## 재사용 방지와 트랜잭션 실패

H1을 성공적으로 소비한 뒤 같은 ID로 전송을 다시 요청하면 실패합니다. 동시에 두 전송이 H1을 사용하려고 해도 둘 다 성공해 100 단위가 두 번 나가서는 안 됩니다. 소비된 계약의 재사용을 막는 것은 [원장 유효성 규칙](https://docs.canton.network/overview/reference/ledger-model-detailed)의 일부입니다. 애플리케이션은 실패한 제출을 처리하고 현재 활성 계약을 다시 조회해야 합니다.

소비와 생성은 원자적입니다. 자기 자신에게 보내기 검사나 새 계약 생성이 실패했다고 H1만 먼저 사라지는 상태가 확정되지 않습니다. 실패한 트랜잭션의 효과가 반영되지 않아 원래 H1은 활성 상태로 남습니다. H1의 과거 기록이 삭제된다는 뜻도 아닙니다. archive는 활성 집합에서 제외한다는 뜻이며, 이력의 보존·조회와 pruning은 별도 운영 문제입니다.

Solidity에서는 첫 전송 후 Alice의 잔액이 0이므로 두 번째 지출이 실패합니다. Daml에서는 특정 입력 계약이 이미 소비되어 실패합니다. 두 번째 EVM 트랜잭션을 제출하는 행위와 서명한 원본 트랜잭션의 네트워크 재전파도 구분해야 합니다. 여기서 테스트한 것은 함수의 두 번째 호출이며, EVM nonce 기반 재전파 방어를 새로 구현하거나 시험한 것이 아닙니다.

## 데이터가 보이는 범위

Daml 원장을 모든 참여자가 같은 전역 잔액표를 읽는 시스템으로 생각하면 조회 설계를 잘못하기 쉽습니다. Canton은 관련 당사자가 필요한 하위 트랜잭션을 보도록 데이터를 배포하며, Party의 관점과 participant의 데이터 보관 범위를 구분합니다. [프라이버시 모델](https://docs.canton.network/overview/learn/privacy-model)에 설명된 가시성 규칙을 적용해야 합니다.

이 예제에서 Issuer는 H1과 H2의 signatory입니다. Alice는 기본 consuming choice의 이해관계자이므로 전송 결과도 관찰합니다. Bob은 H2의 observer입니다. 따라서 “Bob만 잔액을 알고 발행자와 이전 소유자에게는 전송 결과가 숨겨진다”는 설명은 틀립니다. 관찰 범위는 계약과 choice 구성에 따라 달라지며, 앱 서버·호스팅 participant·로그에 대한 신뢰까지 자동으로 사라지지 않습니다. 공개 EVM의 mapping 예제와 정보 배포 방식은 다르지만, Daml을 쓰기만 하면 모든 데이터가 비밀이 되는 것은 아닙니다.

## 로컬에서 예제 검증하기

[DPM 설치 안내](https://docs.canton.network/sdks-tools/cli-tools/dpm)에 따라 도구를 준비하고 SDK `3.6.0`을 고정합니다. 아래 테스트에서는 Java `21.0.12.1`을 사용했습니다. 빈 디렉터리에 `daml/Token.daml`, `daml/Test.daml`, `daml.yaml`을 만들면 됩니다. 설정은 다음과 같습니다.

```yaml
sdk-version: 3.6.0
name: tiny-transfer
source: daml
version: 0.1.0
dependencies:
  - daml-prim
  - daml-stdlib
  - daml-script
```

`daml/Test.daml`은 아래와 같습니다. 특히 권한 실패 테스트는 계약을 볼 수 있는 Issuer가 소유자의 전송을 시도하게 했습니다. 덕분에 단순히 계약이 안 보여 실패하는 상황과 controller 권한 부족을 혼동하지 않습니다. `submitMustFail`은 제출 실패를 기대하는 테스트 도구이며, 운영 애플리케이션의 오류 복구 코드는 아닙니다.

```haskell
module Test where

import Daml.Script
import Token

setup : Script (Party, Party, Party, ContractId Holding)
setup = script do
  issuer <- allocateParty "Issuer"
  alice <- allocateParty "Alice"
  bob <- allocateParty "Bob"
  cid <- submit issuer do createCmd (Holding issuer alice 100)
  pure (issuer, alice, bob, cid)

success : Script ()
success = script do
  (issuer, alice, bob, cid) <- setup
  newCid <- submit alice do exerciseCmd cid (Transfer bob)
  old <- queryContractId issuer cid
  current <- queryContractId bob newCid
  assert (old == None)
  assert (current == Some (Holding issuer bob 100))
  aliceHoldings <- query @Holding alice
  assert (null aliceHoldings)

unauthorized : Script ()
unauthorized = script do
  (issuer, alice, bob, cid) <- setup
  submitMustFail issuer do exerciseCmd cid (Transfer bob)
  current <- queryContractId alice cid
  assert (current == Some (Holding issuer alice 100))

replay : Script ()
replay = script do
  (issuer, alice, bob, cid) <- setup
  _ <- submit alice do exerciseCmd cid (Transfer bob)
  submitMustFail alice do exerciseCmd cid (Transfer bob)

quantityInvariant : Script ()
quantityInvariant = script do
  issuer <- allocateParty "Issuer"
  alice <- allocateParty "Alice"
  submitMustFail issuer do createCmd (Holding issuer alice 0)
  submitMustFail issuer do createCmd (Holding issuer alice (-1))
  holdings <- query @Holding issuer
  assert (null holdings)

selfTransfer : Script ()
selfTransfer = script do
  (issuer, alice, bob, cid) <- setup
  submitMustFail alice do exerciseCmd cid (Transfer alice)
  current <- queryContractId alice cid
  assert (current == Some (Holding issuer alice 100))

issuanceAuthority : Script ()
issuanceAuthority = script do
  (issuer, alice, bob, cid) <- setup
  submitMustFail alice do createCmd (Holding issuer alice 100)
  submitMustFail alice do exerciseCmd cid Archive
```

```bash
dpm install 3.6.0
dpm build
dpm test
```

`dpm build`가 DAR를 생성했고, `dpm test`에서 여섯 검증 시나리오가 모두 통과했습니다. 테스트 도구는 공통 준비 함수 `setup`도 Script로 실행하므로 출력에는 총 일곱 개의 `ok` 항목이 나옵니다. 성공 전송, 권한 없는 전송, 소비된 ID 재사용, 0·음수 수량, 자기 자신에게 전송, 소유자의 무단 발행·archive 거부를 확인했습니다. 컴파일러는 테스트와 템플릿을 같은 패키지에 넣으면 `daml-script` 의존성도 배포된다고 경고합니다. 이 글의 로컬 실습은 한 패키지로 유지했습니다. 실제 배포용 DAR를 만들 때는 계약 패키지와 테스트 패키지를 분리하세요. [Daml Script 안내](https://docs.canton.network/sdks-tools/cli-tools/daml-script)도 이 구성을 권장합니다.

Solidity는 [공식 `0.8.37` 릴리스](https://github.com/argotorg/solidity/releases/tag/v0.8.37)로 고정했습니다. 별도의 로컬 디렉터리에 `TinyToken.sol`과 다음 `test.cjs`를 저장합니다. 컴파일러 optimizer는 끄고 EVM target과 Ganache hardfork는 모두 `shanghai`로 지정했습니다. 최신 컴파일러의 기본 target에 의존하지 않도록 실행 조건을 고정한 것입니다.

```javascript
const fs = require('node:fs');
const assert = require('node:assert/strict');
const solc = require('solc');
const ganache = require('ganache');
const { ethers } = require('ethers');

async function main() {
  console.log('Node', process.version, 'solc', solc.version());
  console.log('ethers', ethers.version, 'ganache', require('ganache/package.json').version);
  const input = {language:'Solidity', sources:{'TinyToken.sol':{content:fs.readFileSync('TinyToken.sol','utf8')}}, settings:{optimizer:{enabled:false}, evmVersion:'shanghai', outputSelection:{'*':{'*':['abi','evm.bytecode.object']}}}};
  const output = JSON.parse(solc.compile(JSON.stringify(input)));
  fs.writeFileSync('compiled.json', JSON.stringify(output,null,2));
  assert.equal((output.errors || []).filter(e => e.severity === 'error').length,0,JSON.stringify(output.errors));
  const artifact = output.contracts['TinyToken.sol'].TinyToken;
  const server = ganache.provider({logging:{quiet:true},chain:{hardfork:'shanghai'},wallet:{totalAccounts:4}});
  const provider = new ethers.BrowserProvider(server);
  const [deployer,alice,bob,eve] = await Promise.all([0,1,2,3].map(i=>provider.getSigner(i)));
  const a = await alice.getAddress(), b = await bob.getAddress();
  const factory = new ethers.ContractFactory(artifact.abi,artifact.evm.bytecode.object,deployer);
  async function deploy(q=100n) { const c=await factory.deploy(a,q);await c.waitForDeployment();return c; }
  async function rejected(p) { await assert.rejects(async()=>{const tx=await p; if(tx.wait) await tx.wait();}); }
  let c=await deploy();
  assert.equal(await c.balance(a),100n);assert.equal(await c.balance(b),0n);
  await (await c.connect(alice).transferAll(b)).wait();
  assert.equal(await c.balance(a),0n);assert.equal(await c.balance(b),100n);
  console.log('PASS success: Alice 100 -> 0, Bob 0 -> 100');
  c=await deploy();
  await rejected(c.connect(eve).transferAll(b));assert.equal(await c.balance(a),100n);
  console.log('PASS unauthorized account cannot spend Alice balance');
  await (await c.connect(alice).transferAll(b)).wait();
  await rejected(c.connect(alice).transferAll(b));assert.equal(await c.balance(b),100n);
  console.log('PASS second spend rejected (empty balance; no CID in EVM)');
  await rejected(factory.deploy(a,0n));await rejected(factory.deploy(a,2n**63n));
  assert.throws(()=>factory.interface.encodeDeploy([a,-1n]));
  console.log('PASS quantity: zero/above Int64 max revert; negative rejected by ABI uint64');
  c=await deploy();await rejected(c.connect(alice).transferAll(a));await rejected(c.connect(alice).transferAll(ethers.ZeroAddress));
  assert.equal(await c.balance(a),100n);
  console.log('PASS self/zero recipient rejected; original balance retained');
  await server.disconnect();
}
main().catch(e=>{console.error(e);process.exitCode=1;});
```

```bash
npm install --save-exact solc@0.8.37 ethers@6.15.0 ganache@7.9.2
node test.cjs
```

Node `26.7.0`, solc-js `0.8.37+commit.f401782d`에서 위 다섯 테스트 묶음이 통과했습니다. Ganache `7.9.2`는 해당 Node ABI용 네이티브 µWS가 없어 JavaScript 구현으로 실행했습니다. 음수는 Solidity의 `uint64` ABI 인코딩 단계에서 거부되며, 0과 비교 범위 초과는 생성자가 거부합니다. Daml의 음수·0 생성 실패와 실패 단계까지 같다고 해석하면 안 됩니다.

Daml은 Script의 로컬 테스트 원장에서 실행했고, Solidity는 프로세스 내부 Ganache EVM에서 실행했습니다. 공개 DevNet·MainNet, 여러 participant 사이의 합의, 실제 인증·Party 호스팅, 수신자 수락 UI, 성능·수수료는 검증 범위에 포함하지 않았습니다.

## 실제 토큰 표준으로 확장할 때

이 `Holding` 템플릿의 이름이 표준의 Holding과 비슷해도 지갑 호환성은 생기지 않습니다. [CIP-0056](https://github.com/canton-foundation/cips/blob/main/cip-0056/cip-0056.md)은 보유·전송·할당을 위한 표준 인터페이스를 정의하며, 확인일의 상태는 `Final`입니다. [CIP-0112](https://github.com/canton-foundation/cips/blob/main/cip-0112/cip-0112.md)는 프라이버시·성능·전통 금융 계정 처리를 개선하는 Token Standard V2이며 `Approved` 상태입니다. 각각 승인일은 2025년 3월 31일과 2026년 6월 12일입니다.

현재 [Splice API 안내](https://docs.canton.network/sdks-tools/api-reference/splice-apis)와 [Token Standard 참조](https://docs.canton.network/overview/reference/cip-0056)에서 인터페이스와 호환 조건을 확인할 수 있습니다. 대시보드의 Token Standard `1.14.0`은 패키지 버전 표기입니다. V1·V2라는 표준 세대 번호나 Daml SDK 버전과 교환해서 읽으면 안 됩니다. CIP 승인만으로 모든 토큰·지갑이 V2 동작을 지원한다고 보장할 수도 없습니다.

실제 자산 개발에서는 목표 네트워크의 지원 패키지, registry, 권한·수신 동의 정책, 발행·소각 제약을 먼저 정해야 합니다. 이 튜토리얼에서 가져갈 부분은 `create → exercise → consume/archive → create` 흐름과, 각 단계의 권한을 계약에 명시하는 방식입니다. 작은 전송 코드를 이해한 다음에 표준 인터페이스를 적용하면 단순한 필드 변경과 업무상 승인을 구분하기가 쉬워집니다.

## 함께 보면 좋을 자료

- [Daml 권한 심화](https://docs.canton.network/appdev/deep-dives/authorization): 중첩된 choice에서 권한이 전달되는 범위.
- [원장 모델 상세](https://docs.canton.network/overview/reference/ledger-model-detailed): 계약 소비, 원자성, 원장의 유효성 규칙.
- [CIP-0056 표준 안내](https://docs.canton.network/overview/reference/cip-0056): 교육용 계약 이후에 확인할 실제 자산 인터페이스.

## 참고 자료

모두 2026년 10월 15일 KST에 확인했습니다. 예제 코드와 비교도는 이 튜토리얼을 위해 직접 작성했습니다.

- [Daml SDK 3.6.0 release](https://github.com/digital-asset/dpm-assembly/releases/tag/3.6.0)
- [SDK component manifest](https://github.com/digital-asset/dpm-assembly/blob/3.6.0/latest/open-source/3.6.yaml)
- [Version Compatibility Dashboard](https://docs.canton.network/shared/version-compatibility-dashboard)
- [Daml language reference](https://docs.canton.network/appdev/reference/daml-language-reference)
- [Daml authorization](https://docs.canton.network/appdev/deep-dives/authorization)
- [Daml authorization module](https://docs.canton.network/appdev/modules/m3-authorization)
- [Daml compiler](https://docs.canton.network/sdks-tools/development-tools/daml-compiler)
- [Daml-LF reference](https://docs.canton.network/appdev/reference/daml-lf-reference)
- [Ledger model](https://docs.canton.network/overview/reference/ledger-model-detailed)
- [Privacy model](https://docs.canton.network/overview/learn/privacy-model)
- [DPM](https://docs.canton.network/sdks-tools/cli-tools/dpm)
- [Daml Script](https://docs.canton.network/sdks-tools/cli-tools/daml-script)
- [Solidity 0.8.37 release](https://github.com/argotorg/solidity/releases/tag/v0.8.37)
- [Solidity value types](https://github.com/argotorg/solidity/blob/v0.8.37/docs/types/value-types.rst)
- [Solidity control structures](https://github.com/argotorg/solidity/blob/v0.8.37/docs/control-structures.rst)
- [Solidity global variables](https://github.com/argotorg/solidity/blob/v0.8.37/docs/units-and-global-variables.rst)
- [CIP-0056](https://github.com/canton-foundation/cips/blob/main/cip-0056/cip-0056.md)
- [CIP-0112](https://github.com/canton-foundation/cips/blob/main/cip-0112/cip-0112.md)
- [Splice APIs](https://docs.canton.network/sdks-tools/api-reference/splice-apis)
- [Token Standard guide](https://docs.canton.network/overview/reference/cip-0056)
