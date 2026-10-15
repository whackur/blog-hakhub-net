---
title: "Transfer 100 Units in Canton Daml: State and Authorization Compared with Solidity"
meta_title: ""
description: "Build a tiny whole-holding Daml transfer, compare it with a Solidity balance mapping, and test authorization and failure cases locally."
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

Alice sends her entire holding of 100 units to Bob. In Solidity, a small implementation updates two balances in the same contract. In Daml, the language used to write Canton smart contracts, the transfer consumes Alice's holding contract and creates a new holding for Bob. The quantities match; the state model and the placement of authorization checks differ.

This tutorial runs that comparison with three parties: Issuer, Alice and Bob. It leaves out partial transfers, fees and wallet connections. Both examples were written for teaching. The Daml token is neither Canton Coin nor a Canton Token Standard implementation. It is not ERC-20 or an asset deployed on an external network.

## Toolchain and specification baseline

**Sources were checked on October 15, 2026, KST.** The latest stable bundle in the [official SDK distribution repository](https://github.com/digital-asset/dpm-assembly/releases/tag/3.6.0) is `3.6.0`, published October 8. That is the bundle used here. Its [component manifest](https://github.com/digital-asset/dpm-assembly/blob/3.6.0/latest/open-source/3.6.yaml) pins the Daml compiler and Script to `3.6.2`, Canton to `3.6.1`, and DPM to `1.0.22`. A bundle version does not identify every bundled component's version.

The [official compatibility dashboard](https://docs.canton.network/shared/version-compatibility-dashboard), updated October 14, separately lists MainNet with SDK `3.5.12`, Canton `3.5.19` and Splice `0.8.4`. It lists DevNet with SDK `3.6.0`, Canton `3.6.1` and Splice `0.9.1`. These are dashboard observations, not live node measurements performed for this exercise. A new SDK release does not establish that MainNet has adopted it.

Daml is the source language for contracts and their authorization rules. Daml-LF is the intermediate language produced by compilation. The SDK packages development tools. The Canton protocol, Canton runtime software, Splice applications and Token Standard packages have separate roles and version numbers. A DAR packages Daml-LF programs, dependencies and metadata for distribution. The [compiler documentation](https://docs.canton.network/sdks-tools/development-tools/daml-compiler) describes that pipeline.

## Exact state before and after

The units in this exercise have no fractional part. Daml's `Int` is a signed 64-bit integer, so positive quantities range from `1` to `9,223,372,036,854,775,807`. The Solidity example uses `uint64` and caps initial issuance at that same maximum. Both examples reject zero-value transfers and self-transfers. This avoids floating-point conversion or decimal scaling while comparing state transitions. See the [Daml language reference](https://docs.canton.network/appdev/reference/daml-language-reference) and [Solidity integer types](https://github.com/argotorg/solidity/blob/v0.8.37/docs/types/value-types.rst).

| Point in time | Solidity current storage | Daml active holding contracts |
| --- | --- | --- |
| Before transfer | `balance[Alice] = 100`, `balance[Bob] = 0` | `H1 = Holding(Issuer, Alice, 100)` |
| After successful transfer | `balance[Alice] = 0`, `balance[Bob] = 100` | `H2 = Holding(Issuer, Bob, 100)` |
| Treatment of the old state | Update entries in the same mapping | Archive H1; H2 has a new contract ID |

![Solidity updates a balance mapping while Daml consumes Alice's H1 and creates Bob's H2](/images/posts/canton-daml-token-transfer-solidity/cover.png)

*Original diagram of the two examples. Daml consumption and creation belong to one atomic transaction. H1 and H2 are explanatory labels, not actual contract IDs.*

## A small Solidity balance mapping

Save the following as `TinyToken.sol`. The constructor initializes Alice's balance. `transferAll` adds the caller's entire balance to the recipient's balance. There are no ERC-20 events, allowances or `totalSupply` API, so this contract must not be treated as an ERC-20 implementation.

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

When Alice calls `transferAll(Bob)`, `msg.sender` is Alice's address. There is no `from` argument that another caller can use to select her balance. A third party with no balance reads its own zero balance and fails the positive-quantity check. In a contract-to-contract call, `msg.sender` is the immediate calling contract; it is not always the original user's wallet address. That is the definition in the [Solidity global variables documentation](https://github.com/argotorg/solidity/blob/v0.8.37/docs/units-and-global-variables.rst).

A successful call changes two mapping entries at the same deployed contract address. If Bob already has a balance, it is aggregated. Ordinary Solidity 0.8 arithmetic checks for overflow, and this example uses no `unchecked` block. Issuance happens only in the constructor and is capped as described above, so valid transfers cannot push aggregate balances beyond `uint64`. If a `require` or arithmetic check fails, the call's storage changes revert. See [control structures and error handling](https://github.com/argotorg/solidity/blob/v0.8.37/docs/control-structures.rst).

## A small Daml holding contract

Put the following in `daml/Token.daml`. A `template` defines a contract's data and permitted behavior. `create` instantiates an individual contract from it. Many holdings can share the same template, each identified by its own contract ID.

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

The fields `issuer`, `owner` and `quantity` are fixed when a contract is created. There is no operation that edits an existing contract's `owner` in place. `create this with owner = newOwner` copies the data, substitutes the owner, and **creates a new contract**. The original contract's payload stays unchanged. The [language reference](https://docs.canton.network/appdev/reference/daml-language-reference) documents templates and choices.

`Transfer` has no `nonconsuming` modifier, so it is a consuming choice by default. When Alice exercises it, H1 is consumed and the choice body creates H2. The returned `ContractId Holding` identifies Bob's new holding. One input becomes one output here, preserving both `issuer` and `quantity`.

If Bob already had a 40-unit holding, this transfer would not automatically merge it into a 140-unit contract. The existing 40-unit contract and the new 100-unit contract would remain separate. A balance view must aggregate active holdings for the same template and issuer, within the querying party's authorized view. This example has no merge operation either.

There is no transfer-amount argument. Alice cannot send only 30 of her 100 units. A partial-transfer implementation would validate the requested quantity and create both Bob's 30-unit holding and Alice's 70-unit change holding in the same transaction. It would also need to enforce conservation across inputs and outputs. Daml does not invent change automatically; that functionality is deliberately omitted from this example.

## Signatories, controllers and delegated authority

A `Party` is a ledger identity used in authorization. Supplying an arbitrary Party value does not give the caller that party's authority. A real integration also needs an authenticated submitter with rights to act for the party and an appropriate party-hosting relationship with a participant. The Script tests below allocate local test parties, so no external account provisioning is needed. See the [authorization deep dive](https://docs.canton.network/appdev/deep-dives/authorization).

| Declaration | Party in this example | Meaning |
| --- | --- | --- |
| `signatory issuer` | Issuer | Authorizes contract creation and delegates its authority to the defined choice consequences |
| `observer owner` | Alice, then Bob | Can see the corresponding holding contract |
| `controller owner` | Alice on H1 | Has authority to exercise `Transfer` |

Direct creation of H1 needs Issuer's authority. Alice can see H1 as an observer, but observation itself grants no transfer right. Her transfer authority comes from `controller owner`. Issuer also sees H1, yet cannot exercise Alice's `Transfer` alone. Being a signatory does not make a party the controller of every choice.

Creating H2 needs `signatory issuer` again. Alice can nevertheless submit the transfer alone because exercising H1 makes that contract's signatory authority available to the consequences of its choice. Issuer authorized these code-defined consequences when H1 was created. Issuer does not sign a fresh approval for every spend. The delegation is scoped to the exercise: Alice cannot use it to issue arbitrary unrelated holdings in Issuer's name. The [authorization rules](https://docs.canton.network/appdev/modules/m3-authorization) explain this boundary.

The issuer trust is substantial. Issuer can independently create more `Holding` contracts and can terminate holdings using the implicit signatory-controlled `Archive` choice. This model has no total-supply cap or reserve verification. The Solidity contract has no post-constructor issuance path, so the two examples do not have identical issuer powers. They compare transfer-state representation and authorization.

Bob's acceptance is absent by design. Bob is an observer of the new contract, not its signatory, so this transfer does not require a separate authorization from him. Preventing unsolicited receipt or binding a recipient to obligations requires an acceptance choice, a proposal-and-acceptance workflow or explicitly modeled preapproval. An observer declaration alone does not represent consent.

## Reuse, double spending and failure

Once H1 has been successfully consumed, another transfer using that same ID fails. Two concurrent transfers cannot both consume H1 and produce two successful spends of the same 100 units. Preventing reuse of consumed contracts is part of the [ledger validity rules](https://docs.canton.network/overview/reference/ledger-model-detailed). Applications still need to handle failed submissions and refresh their active-contract state.

Consumption and creation are atomic. A failed self-transfer check or output creation does not commit a state where only H1 has disappeared. The failed transaction has no committed effects, so H1 remains active. Archival also does not mean erasing historical evidence. It removes the contract from the active set; retention, historical queries and pruning are separate operational concerns.

In Solidity, the second spend fails because Alice's balance is now zero. In Daml, it fails because the particular input contract has been consumed. Submitting a second EVM function call is also different from rebroadcasting the same signed transaction. The tests here cover the second function call; they neither implement nor test Ethereum's nonce-based replay protection.

## Who can see the transfer

Treating the Daml ledger as a global balance table readable by everyone leads to incorrect query designs. Canton distributes relevant subtransactions to the parties that need them. A party's view and a participant's stored data are related but distinct concepts. Apply the visibility rules described in the [privacy model](https://docs.canton.network/overview/learn/privacy-model).

Issuer is a signatory of both H1 and H2. Alice is a stakeholder of the original contract and observes the consequences of this default consuming choice. Bob is an observer of H2. It would therefore be wrong to say that only Bob knows the output while the issuer and previous owner are excluded. Visibility depends on the contract and choice definitions. Application servers, hosting participants and logging policies also remain trust considerations. This differs from the public EVM mapping example, but writing Daml does not make every piece of information secret.

## Run the examples locally

Prepare DPM using the [official installation guide](https://docs.canton.network/sdks-tools/cli-tools/dpm) and pin SDK `3.6.0`. The tests here used Java `21.0.12.1`. Create `daml/Token.daml`, `daml/Test.daml` and the following `daml.yaml` in an empty directory.

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

Use this `daml/Test.daml`. The unauthorized-transfer test deliberately submits as Issuer, who can already see the contract. That distinguishes a controller-authorization failure from an attempt that fails merely because the contract is invisible. `submitMustFail` is a test assertion for rejected submissions, not production error-recovery logic.

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

`dpm build` produced the DAR, and all six validation scenarios passed under `dpm test`. The runner also executes the shared `setup` helper as a Script, so its output contains seven `ok` entries. The scenarios cover a successful transfer, unauthorized transfer, reuse of a consumed ID, zero/negative quantities, self-transfer, and rejection of owner-initiated issuance and archival. The compiler warns that combining templates and tests in one package also brings `daml-script` into its deployment dependencies. This local exercise retains that small layout. Separate the contract and test packages before producing a deployment DAR, as recommended by the [Daml Script guide](https://docs.canton.network/sdks-tools/cli-tools/daml-script).

The Solidity example pins the [official `0.8.37` release](https://github.com/argotorg/solidity/releases/tag/v0.8.37). In a separate local directory, save `TinyToken.sol` and the following `test.cjs`. The optimizer is disabled; the compiler's EVM target and Ganache hardfork are both `shanghai`. This fixes the execution environment instead of depending on a new compiler's default target.

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

All five test groups passed with Node `26.7.0` and solc-js `0.8.37+commit.f401782d`. Ganache `7.9.2` lacked a native µWS binary for that Node ABI and ran using its JavaScript fallback. Negative quantities are rejected during `uint64` ABI encoding; zero and values above the comparison bound are rejected by the constructor. Those failure stages differ from Daml's negative/zero contract-creation checks.

Daml ran on the Script local test ledger; Solidity ran on an in-process Ganache EVM. Public DevNet/MainNet, multi-participant consensus, real authentication and party hosting, recipient-acceptance UI, performance and fees were outside the validation scope.

## Moving to actual token standards

Naming a template `Holding` does not provide standard wallet compatibility. [CIP-0056](https://github.com/canton-foundation/cips/blob/main/cip-0056/cip-0056.md) defines standard holding, transfer and allocation interfaces; its checked status is `Final`. [CIP-0112](https://github.com/canton-foundation/cips/blob/main/cip-0112/cip-0112.md) defines Token Standard V2 improvements for privacy, performance and traditional accounting; its checked status is `Approved`. Their approval dates are March 31, 2025 and June 12, 2026 respectively.

Consult the current [Splice API guide](https://docs.canton.network/sdks-tools/api-reference/splice-apis) and [Token Standard reference](https://docs.canton.network/overview/reference/cip-0056) for interfaces and compatibility conditions. The dashboard's Token Standard `1.14.0` is a package-version label. It is not interchangeable with the V1/V2 standard generation or a Daml SDK version. CIP approval alone does not establish that every asset or wallet supports V2 behavior.

A real asset implementation needs a target network's supported packages, a registry, authorization and recipient-consent policies, and issuance/burning constraints. The transferable lesson from this exercise is the `create → exercise → consume/archive → create` lifecycle and the explicit authorization at each step. Once that small transfer is clear, it is easier to distinguish data replacement from business approval when implementing standard interfaces.

## Further reading

- [Daml authorization deep dive](https://docs.canton.network/appdev/deep-dives/authorization): The scope of delegated authority in nested choices.
- [Detailed ledger model](https://docs.canton.network/overview/reference/ledger-model-detailed): Consumption, atomicity and ledger validity rules.
- [CIP-0056 guide](https://docs.canton.network/overview/reference/cip-0056): Actual asset interfaces to study after the teaching example.

## References

All sources were checked on October 15, 2026, KST. Code and the comparison diagram were written for this tutorial.

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
