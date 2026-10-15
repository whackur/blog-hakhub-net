---
title: "Transferring Tokens with Canton Daml: State and Authorization Compared with Solidity"
meta_title: ""
description: "Compare a Daml holding-contract transfer with Solidity balance updates, including authorization, visibility and local verification."
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

When Alice sends all 100 token units to Bob, Bob becomes the person who can spend them next. **The Solidity example updates balances by address; the Daml example for Canton consumes Alice's holding contract and creates Bob's.** They express the same transfer outcome with different units of state and different authorization checks.

Both are teaching examples. The Daml code implements neither the Canton Token Standard (CIP-0056 or CIP-0112) nor Canton Coin. The Solidity code is not an ERC-20 implementation. Neither example is presented as a deployment on a public network.

## One balance versus one holding contract

Start with Alice holding 100 units and Bob holding none. There are no fees or fractional units, and each operation transfers the entire holding. In Daml, `TokenLot` is the template for a holding contract. H1 and H2 below are explanatory names for distinct contract IDs.

| State | Solidity `BalanceBook` | Daml `TokenLot` |
| --- | --- | --- |
| Before | Alice balance 100, Bob balance 0 | H1: issued by Issuer, held by Alice, 100 units |
| After success | Alice balance 0, Bob balance 100 | H1 inactive; H2 created: issued by Issuer, held by Bob, 100 units |
| Input to the next spend | Bob's balance in the same contract | New contract ID H2 |

The Solidity mapping stores an aggregate for each address. The Daml code stores individual lots. If Bob already had a 40-unit contract, receiving 100 leaves him with two contracts, for 40 and 100 units. They do not automatically merge into a 140-unit contract. To display Bob's balance, an app needs to sum visible active lots whose holder is Bob and whose issuer and template match. This difference follows from the data structures chosen below. See the [Solidity mapping reference](https://github.com/argotorg/solidity/blob/v0.8.37/docs/types/mapping-types.rst) and [Daml contracts and choices](https://docs.canton.network/appdev/modules/m3-choices).

## Daml replaces the holding contract

Save this as `daml/Lots.daml`. `Party` identifies a party on the ledger. `units` is an integer quantity; `ensure` rejects creation with a value of zero or less.

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

Issuer creates `TokenLot issuer alice 100`, making H1 active. Alice exercises H1's `Send` with Bob as recipient. The default consuming choice archives H1, and its body creates H2. The return value is H2's ID. It does not modify H1's `holder` field in place. The [Daml language reference](https://docs.canton.network/appdev/reference/daml-language-reference) defines contract fields and default choice consumption.

There is no partial transfer. Sending 30 of the 100 units would require consuming the input and creating a 30-unit lot for Bob and a 70-unit remainder for Alice in the same transaction. The code would also need to check conservation between inputs and outputs.

### Creating and transferring require different authority

| Declaration | Role in this code |
| --- | --- |
| `signatory issuer` | Creating the contract requires Issuer's authority. |
| `observer holder` | The holder can see the contract. Observation alone grants no transfer authority. |
| `controller holder` | The current holder can exercise `Send`. |

Alice can submit `Send` alone while still satisfying the authority needed to create H2. The consequences of an exercise have the authority of its actors and the signatories of the contract being exercised. That delegation is scoped to **the consequences of that exercise**. It does not let Alice issue arbitrary contracts as Issuer in a separate command. Conversely, being H1's signatory does not let Issuer exercise `Send` alone when Alice is its controller. The [official authorization model](https://docs.canton.network/appdev/modules/m3-authorization) explains these rules.

This small model trusts the issuer. Issuer can create additional `TokenLot` contracts and end a holding through the implicit `Archive` choice controlled by the signatories. There is no supply cap or collateral check. The Solidity example below has no issuance path after its constructor, so the two examples do not give the issuer equivalent powers.

Bob's acceptance is also absent. He is not a controller of H1's `Send` or a signatory of H2. On H2, he becomes both an observer and the controller of the next `Send`. Recipient consent or obligations require a proposal-and-acceptance flow, a preauthorization contract, or another explicit design. Declaring an observer does not collect consent. The propose-accept examples in the authorization documentation address this problem.

## Solidity moves the caller's balance

`BalanceBook.sol` assigns 100 units once, to the address supplied to its constructor. `sendAll` has no source-address argument: it reads only the current caller's balance.

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

When Alice calls directly, `msg.sender` is Alice's address. A third party with no balance reads their own zero balance and fails. In an ordinary external call through another contract, `msg.sender` is the immediately calling contract. It does not automatically preserve the original user's address. This follows the definition in the [Solidity global variables reference](https://github.com/argotorg/solidity/blob/v0.8.37/docs/units-and-global-variables.rst).

The `public balance` declaration generates a getter taking an address, and an unset address has a balance of zero. A transfer sets the sender's entry to zero and adds the quantity to the recipient's entry in the same deployed contract. The received units are added to any existing balance. This code does not provide events, allowances or the standard `transfer` interface, so it does not provide ERC-20 wallet compatibility.

Ordinary Solidity 0.8 arithmetic checks overflow; this code contains no `unchecked` block. A failed `require` or arithmetic check reverts the call's state changes. With no function to issue more units, normal transfers preserve the initial total of 100. See the [error handling and arithmetic rules](https://github.com/argotorg/solidity/blob/v0.8.37/docs/control-structures.rst).

## Rejected transfers and visible information

| Attempt | Daml example | Solidity example |
| --- | --- | --- |
| Someone else transfers Alice's asset | Even Issuer, who can see H1, is rejected as a non-controller of `Send` | An unfunded caller fails the check on their own balance |
| Transfer to self | Rejected by the choice's `assertMsg` | Rejected by `require` |
| Spend the same asset after success | Consumed H1 cannot be exercised again | Alice's balance is zero, so another call fails |

Daml consumption and creation belong to one transaction. A failed choice does not commit a state where only H1 has disappeared. Archiving removes a contract from the active set; it does not erase historical records. The [ledger rules](https://docs.canton.network/overview/reference/ledger-model-detailed) that prevent reuse of a consumed ID differ from a Solidity balance check. A repeated function call here is also distinct from rebroadcasting a signed transaction or checking its nonce.

Visibility differs too. On a public EVM, this mapping's balances are not secret. Changing its declaration to `private` would not conceal the underlying blockchain data. The [Solidity visibility documentation](https://github.com/argotorg/solidity/blob/v0.8.37/docs/contracts/visibility-and-getters.rst) distinguishes access control from confidentiality.

Canton distributes relevant parts according to parties' roles and the transaction structure. Issuer is a signatory of H1 and H2. Alice is a stakeholder of H1 and an actor of `Send`, so both see the creation of H2 as a consequence of that choice. Bob sees the new holding as H2's observer. This does not hide the outcome from Alice and Issuer while revealing it only to Bob. See the ledger model's [informee and witness rules](https://docs.canton.network/overview/reference/ledger-model-detailed#informee) and the [privacy model](https://docs.canton.network/overview/learn/privacy-model).

Permission to see a contract differs from permission to act on it. A party's visibility also differs from how its hosting participant handles data. Daml declarations alone cannot protect information subsequently passed to application servers or logs. Real Ledger API access also needs authentication, user rights and party hosting. Allocating parties in a local test does not validate that operational setup. See the [Ledger API authorization documentation](https://docs.canton.network/appdev/deep-dives/authorization).

## Local execution and verification scope

Prepare [DPM](https://docs.canton.network/sdks-tools/cli-tools/dpm) and pin SDK `3.6.0`. Save this project-root `daml.yaml`:

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

The two scripts in `daml/Checks.daml` below check transfer behavior and issuer policy. The authorization test submits as Issuer, who can already see H1, separating a controller failure from mere lack of visibility.

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

Fresh runs of `dpm build` and `dpm test` succeeded. Both `transferChecks` and `policyChecks` above passed. The policy checks rejected zero/negative lots and arbitrary issuance by the holder, and confirmed that Bob's 40- and 100-unit lots remain separate. Direct `Archive` by the holder failed; `Archive` by Issuer succeeded. The bundle SDK was `3.6.0`, compiler and Script `3.6.2`, and Java `21.0.12.1`. The build warns that keeping templates and tests together includes `daml-script` as a dependency. Separate deployment and test packages as described in the [Daml Script guide](https://docs.canton.network/sdks-tools/cli-tools/daml-script).

Save the settings below as `input.json` to compile for the same EVM target used in testing. Supply Alice's address to the constructor, then call `sendAll(Bob's address)` as Alice after deployment.

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

Local runtime checks used solc-js `0.8.37`, ethers `6.15.0`, Ganache `7.9.2` and Node `26.7.0`. Optimization was disabled; both the compiler EVM target and Ganache hardfork were `shanghai`. Alice→Bob produced balances 0 and 100; Bob→Alice restored 100 and 0. An unfunded caller, self-transfer, a zero-address recipient and a second spend were checked as mined failed transactions, with balances retained. Deployment with a zero-address initial holder was also rejected. Ganache used its JavaScript fallback instead of native µWS in this Node environment.

These results cover a Daml Script local test ledger and an in-process EVM. They do not validate multi-participant consensus, concurrent submission races, wallet integration, public-network deployment, fees or performance.

## Standard compatibility needs its own implementation

The official documents fetched on October 15, 2026, KST mark [CIP-0056](https://github.com/canton-foundation/cips/blob/main/cip-0056/cip-0056.md) as `Final` and [CIP-0112](https://github.com/canton-foundation/cips/blob/main/cip-0112/cip-0112.md) as `Approved`. CIP-0056 defines standard APIs that wallets and applications can use without relying on each asset's internal implementation. CIP-0112 addresses privacy, performance and accounting in Token Standard V2.

Renaming `TokenLot` to resemble a standard holding, or completing a local transfer, does not implement those interfaces and rules. An actual asset needs to match the packages supported by its target network, transfer and allocation interfaces, issuance policy and recipient authorization requirements. A CIP's status does not establish support by a particular wallet or deployment and adoption on a network.

The useful design distinction is the unit of state and authority: an aggregate balance updated by address, or a particular holding contract consumed by an authorized choice. That decision determines where to handle repeated spending, balance queries and recipient consent.

## Further reading

- [Daml authorization model](https://docs.canton.network/appdev/modules/m3-authorization): Extend the example with recipient consent and propose-accept patterns.
- [Canton Token Standard guide](https://docs.canton.network/overview/reference/cip-0056): The actual standard interfaces to study after the teaching model.
- [Solidity mappings](https://github.com/argotorg/solidity/blob/v0.8.37/docs/types/mapping-types.rst): Address-indexed balances and generated getters.

## References

Official documentation accessed October 15, 2026, KST. The code is original educational material for this article.

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
