---
title: "AI Agent Commerce and Coordination: ERC-8183, ERC-8226, ERC-8001, ERC-8041"
meta_title: ""
description: "The application layer above the ERC-8004/8126/8196 trust stack: job escrow (ERC-8183), regulated-asset compliance delegation (ERC-8226), multi-agent coordination (ERC-8001, Final), and fixed-supply agent collections (ERC-8041), with a builder's view of what is usable now."
date: 2026-07-01T09:00:00+09:00
lastmod: 2026-07-02T15:08:14+09:00
image: ""
categories: ["Blockchain"]
tags: ["ai-agent", "ethereum", "eip", "erc-8183", "erc-8226", "erc-8001", "erc-8041"]
author: "whackur"
translationKey: "ai-agent-commerce-coordination-erc-8183-8226-8001"
draft: true
---

The [ERC-8004/8126/8196 trust stack](../ai-agent-wallet-trust-stack-erc-8004-8126-8196) defines three layers: agent identity, security verification, and policy-constrained execution. It identifies an agent, scores its risk, and keeps it acting within the limits an owner has set. All of that answers one question: can I trust this agent to act on my behalf?

The harder part starts after that trust exists. Even a trusted agent still needs a way to provide a service and get paid, permission to touch regulated assets, and a way to split one job across several agents. The trust stack does not define any of that. Trust is a precondition; what a trusted agent can actually do lives in a separate application layer.

This post looks at four ERC proposals that try to standardize that application layer. First, the status, because it matters throughout. **ERC-8001 is Final. ERC-8183, ERC-8226, and ERC-8041 are all Draft, and the underlying ERC-8004 is Draft too.** A Draft spec can change anything from function names to struct fields, so read the drafts as design in progress, not as settled interfaces.

## The four proposals at a glance

| ERC | Name | Role | Status | Created |
|-----|------|------|--------|---------|
| ERC-8001 | Agent Coordination Framework | Multi-party coordination with EIP-712 acceptance attestations | Final | 2025-08-02 |
| ERC-8041 | Fixed-Supply Agent NFT Collections | Fixed-supply layer over ERC-8004 collections | Draft | 2025-10-11 |
| ERC-8183 | Agentic Commerce | Job escrow with evaluator attestation | Draft | 2026-02-25 |
| ERC-8226 | Regulated Agent Mandate | Compliance delegation for regulated tokenized assets | Draft | 2026-04-12 |

For the status and role of the underlying ERC-8004 (Draft), ERC-8126 (Final), and ERC-8196 (Review), see the previous post.

## The trust stack and the application layer

The trust stack and these four proposals sit at different layers.

The trust stack (ERC-8004/8126/8196) covers an agent's identity, its risk, and its permitted actions. ERC-8004 on its own runs three registries, Identity, Reputation, and Validation, and lets you discover, choose, and interact with agents across organizational boundaries without any prior trust. But ERC-8004 puts payments explicitly out of scope. Identity and reputation are as far as it goes.

Payments, coordination, compliance, and supply have to be built on top. Four gaps remain for the application layer to fill.

**Settlement.** When an agent finishes a job, there is no standard way to lock payment in escrow and release it on verified completion. Without one, requester and agent fall back on trusting each other informally.

**Coordination.** Complex workflows chain agents in sequence or in parallel. When agent A hands a subtask to agent B, no standard records that handoff on-chain or proves the terms B accepted.

**Compliance.** Tokenized securities, real estate vehicles, and bonds carry KYC/AML checks, accreditation requirements, and jurisdiction-specific transfer rules. An AI agent operating on these assets needs a structured way to receive compliance authorization and prove it.

**Supply.** ERC-8004 sits on ERC-721, which has no built-in cap. Some deployments need a tamper-proof maximum supply.

## ERC-8183: Agentic Commerce

ERC-8183 proposes a standard for how AI agents provide services and get paid on-chain. The authors call it the Agentic Commerce Protocol (ACP), a minimal escrow protocol for jobs performed by agents. Two pieces carry the design: **escrow** and a **single evaluator attestation**.

### The problem

Every platform that pays AI agents today implements its own logic, so nothing is portable across platforms. When a requester wants to pay only on verified completion, there is no standard way to lock funds and release them against a confirmed result. And the agent has no standard way to prove it did the work.

### The job lifecycle

ERC-8183 models a job as a state machine. Conceptually the flow is Open → Funded → Submitted → Terminal, where Terminal resolves to Completed, Rejected, or Expired. The concrete state enum has six members: Open, Funded, Submitted, Completed, Rejected, Expired. Each contract uses a single ERC-20 as its payment token.

The allowed transitions are:

| Transition | Meaning |
|------------|---------|
| Open → Funded | Client escrows the payment |
| Open → Rejected | Job rejected before funding |
| Funded → Submitted | Provider submits the work |
| Funded → Rejected | Evaluator rejects even before submission |
| Funded → Expired | Deadline passes |
| Submitted → Completed | Evaluator rules complete |
| Submitted → Rejected | Evaluator rules rejected |
| Submitted → Expired | No ruling before the deadline |

A Completed job pays the provider from escrow. A Rejected or Expired job refunds the client.

### Three roles: client, provider, evaluator

Three parties appear in ERC-8183.

- **Client**: creates the job, funds it, and receives refunds on rejection or expiry.
- **Provider**: performs the work, submits the result, and receives payment on a Completed ruling. The work itself can happen off-chain.
- **Evaluator**: a single address per job that decides complete or rejected. While a job is in the Submitted state, only the evaluator can move it to Completed or Rejected.

The evaluator can be an EOA or a smart contract. The spec does not require it to be a neutral third party. The client can act as its own evaluator, or the role can go to another AI agent, a DAO, or a dedicated verification service. Who plays evaluator is fixed at job-creation time and cannot change afterward.

That pre-commitment is what makes the commerce trustless. Both client and provider know and accept the evaluator before the job begins, so neither can flip the outcome unilaterally later.

### Attestation, audit, and reputation

An evaluator's ruling can optionally carry a reason and a hash. Those values support audit trails, and they compose with a reputation registry like ERC-8004 to build a signal of what a provider has completed and how. The commerce record itself becomes source data for reputation.

### What it does not cover

ERC-8183 is deliberately minimal. It leaves out the evaluator-trust problem (who verifies the evaluator?), the oracle problem of tying off-chain results to on-chain attestations, partial completion for multi-stage jobs, and reputation, dispute resolution, and complex arbitration.

**Status**: Draft (created 2026-02-25, requires ERC-20). Authors: Davide Crapis, Bryan Lim, Tay Weixiong, Chooi Zuhwa. Official page: [eips.ethereum.org/EIPS/eip-8183](https://eips.ethereum.org/EIPS/eip-8183). Discussion: [Ethereum Magicians](https://ethereum-magicians.org/t/erc-8183-agentic-commerce/27902).

## ERC-8226: Regulated Agent Mandate

ERC-8226 proposes a compliance delegation standard for AI agents operating on regulated tokenized assets. The spec names it the Regulated Agent Mandate Standard (RAMS): a layer that lets a verified principal delegate limited authority to an on-chain or AI agent.

### Regulated assets, for background

On-chain assets split into two kinds. Some move freely with no identity checks (most ERC-20s). Others are **regulated assets** carrying KYC/AML verification, accredited-investor restrictions, and jurisdiction-specific transfer rules. Tokenized securities, tokenized real estate, and government bonds fall here, and their token contracts often enforce compliance at the contract level.

When a person trades regulated assets through a broker, the broker handles the compliance. When an AI agent operates on them autonomously, there needs to be a standard that records the agent is authorized to act within the applicable constraints. Without one, the agent either has unchecked access or cannot touch the asset at all.

### The mandate structure and its limits

ERC-8226 defines an on-chain mandate, a structured authorization record that narrows an agent's authority along several axes.

- **Action and asset scope**: which actions (buy, sell, transfer, and so on) the agent may take on which regulated asset contracts.
- **Time bounds**: a start and an expiry.
- **Financial caps**: a per-transaction cap and a cumulative cap together. That blocks both a single oversized trade and a stream of smaller ones.
- **Legal traceability**: identity references and metadata tie the mandate back to a real principal.

An agent can only execute regulated-asset transactions that fall inside an active mandate's scope; anything outside it fails at the contract level. One design rule matters here: asset contracts should validate mandates atomically at execution time. Verification and execution must not be separable across transactions, or the check can be bypassed.

The spec is agnostic to agent identity systems (such as ERC-8004), token standards (ERC-20, ERC-721, ERC-1155), and regulated token frameworks (ERC-7943, ERC-3643).

### Two interfaces: compliance provider and agent mandate

The implementation splits into two interfaces. `IComplianceProvider` verifies a principal's eligibility, identity, reason codes, and expiry. `IAgentMandate` manages the mandate records. The two should deploy separately by default, though they may be combined into one contract. Both must implement ERC-165.

`IComplianceProvider` carries one firm requirement: a binary oracle that returns only true or false is non-conformant. It has to verify principal eligibility and return structured data, so downstream logic can see why a principal passed and which constraints apply, rather than only whether it passed.

### Relation to ERC-8196

Where ERC-8196 (Authenticated Wallet) lets an owner define which contracts and action types an agent policy covers, ERC-8226 sits above it and adds the compliance requirements specific to regulated assets. ERC-8196 controls what the agent can do; ERC-8226 controls whether it is authorized to handle a given regulated asset. The two are complementary.

### What it does not cover

ERC-8226 defines the delegation framework, not compliance itself. Whether the underlying KYC data is accurate, whether mandate parameters match a jurisdiction's actual regulatory requirements, and how mandates stay current as regulations change are all outside the spec.

**Status**: Draft (created 2026-04-12, requires EIP-165, EIP-712, EIP-1271). Authors: Ludovico Rossi, Dario Lo Buglio, Thamer Dridi, Nabil El Alami Khalifi. Official page: [eips.ethereum.org/EIPS/eip-8226](https://eips.ethereum.org/EIPS/eip-8226). Discussion: [Ethereum Magicians](https://ethereum-magicians.org/t/erc-8226-regulated-agent-mandate/28208).

## ERC-8001: Agent Coordination Framework

ERC-8001 is a finalized standard for recording multi-party agent coordination on-chain, built on **EIP-712 acceptance attestations**. It is a minimal, single-chain, multi-party primitive.

### The coordination problem

Single-agent tasks are simple. Complex workflows are not. Picture a data-collection agent, an analysis agent, and an execution agent working as a pipeline. Each one needs to accept the terms of its own role in a verifiable form, so that if a dispute arises later over what was agreed, it can be settled on-chain.

Right now each agent framework handles coordination privately, inside its own platform. There is no common interface across platforms and no standard audit trail.

### EIP-712 acceptance attestations

EIP-712 is Ethereum's standard for signing typed structured data. It presents the signed content in a human-readable form and lets anyone verify the signature on-chain. ERC-8001 uses it as the evidence of coordination acceptance.

The basic flow:

1. An **initiator** defines an intent (task scope, role assignments, completion criteria, deadlines) as a coordination struct and posts it on-chain.
2. Each **participant** signs an EIP-712 attestation accepting the terms of its role. The signed attestation is recorded on-chain.
3. The coordination becomes executable (Ready) once the required participant set has all accepted, the intent has not expired, and every acceptance is still fresh.
4. The record tracks state through a canonical enum. None → Proposed → Ready → Executed is the main path; an abandoned coordination goes to Cancelled, a timed-out one to Expired.

### Core structs and signature schemes

ERC-8001 centers on three structs, `AgentIntent`, `CoordinationPayload`, and `AcceptanceAttestation`. Around them it defines the EIP-712 typed data and domain, the hashing rules for intents and acceptances, lifecycle semantics, mandatory events, status codes, and verification rules. Each acceptance attestation references the intent's payload hash (payloadHash), binding it to one specific coordination payload. The participant list must be unique and strictly ascending by address, which rules out duplicate signers and ambiguous ordering.

Signature verification supports several schemes: ECDSA signatures from EOAs, contract-wallet signatures via ERC-1271, compact signatures via EIP-2098, and domain discovery via EIP-5267. The initiator can be another agent, a smart contract, or a person. The one thing the spec insists on is that coordination terms are published before any participant attests acceptance.

### What it does not cover

ERC-8001 deliberately omits privacy, reputation, threshold policies, bonding and slashing, and cross-chain semantics. It records coordination agreements and their acceptance. It does not verify that agents actually performed their roles correctly; that requires a separate mechanism, such as ERC-8183's evaluator attestation.

**Status**: Final (created 2025-08-02, requires EIP-712, EIP-1271, EIP-2098, EIP-5267). Author: Kwame Bryan. Official page: [eips.ethereum.org/EIPS/eip-8001](https://eips.ethereum.org/EIPS/eip-8001).

## ERC-8041: Fixed-Supply Agent NFT Collections

ERC-8041 proposes an interface for grouping the agent NFTs registered in an ERC-8004 Agent Registry into **fixed-supply collections**.

### The supply problem

ERC-8004 provides a singleton registry for agent identity NFTs with unlimited minting. For most deployments that is the right default. Some, though, need a cap.

If a collection promises 100 agents and no more, buyers and integrators need an on-chain guarantee that no further minting is possible. Without a standard interface for that guarantee, every collection writes its own cap logic and there is no common way to verify it from outside. ERC-8041 adds limited collections on top of ERC-8004's unlimited minting while preserving the on-chain association between agents and their collections.

### What it adds

- **Required collection properties**: `maxSupply`, `currentSupply`, `startBlock`, and `open` (whether the collection accepts new mints). Every compliant collection contract must maintain these four.
- **Standard interface**: `IERC8041Collection`. `getAgentMintNumber(agentId)` returns an agent's mint number within its collection (for example, "5 of 1000"); `getCollectionSupply()` returns current supply state.
- **Required events**: `CollectionUpdated` when collection parameters are created or updated, and `AgentMinted` when an agent is minted.

Combined with ERC-8119's parameterized metadata keys, a single agent can belong to multiple collections. That opens up collection metadata, mint-number tracking, time-gated releases, and curated drops.

### Relation to ERC-8004

A contract that implements ERC-8041 is itself a valid ERC-8004 agent registry. It adds the fixed-supply constraint without changing how identity records or registry lookups work. So agents registered in an ERC-8041 collection still appear in the ERC-8004 identity system and share the same reputation and validation registries as any other registered agent.

### What it does not cover

The fixed-supply guarantee applies only to minting within that specific contract. It does not stop the same agent logic from being redeployed in a different contract. For supply scarcity to translate into economic value, the ecosystem has to agree on treating this contract as the canonical collection.

**Status**: Draft (created 2025-10-11, requires EIP-7572, ERC-8004, ERC-8119). Author: Prem Makeig. Official page: [eips.ethereum.org/EIPS/eip-8041](https://eips.ethereum.org/EIPS/eip-8041). Discussion: [Ethereum Magicians](https://ethereum-magicians.org/t/erc-8041-fixed-supply-agent-nft-collections/25656).

## How the layers fit together

The two groups can be used independently. In real deployments, though, the application layer naturally stacks on top of the trust stack.

| Layer | Responsibility |
|-------|----------------|
| ERC-8004/8126/8196 | Identity, risk scoring, policy enforcement |
| ERC-8001 | Recording multi-agent coordination agreements |
| ERC-8041 | Fixed-supply management for agent collections |
| ERC-8183 | Agent service commerce (escrow and settlement) |
| ERC-8226 | Compliance delegation for regulated assets |

One end-to-end scenario shows the overlap. Take an agent registered in ERC-8004, cleared by ERC-8126, and operating within an ERC-8196 policy. It uses ERC-8001 to divide roles with other agents and leave acceptance attestations, wins jobs through ERC-8183 escrow and settles on a completion ruling, and touches regulated assets only within an ERC-8226 mandate. Identity through settlement runs in a single line. And the ERC-8183 completion attestation can flow back into the ERC-8004 reputation registry as a trust signal for the next job.

## What this means for builders

Here is how far you can actually take these standards today.

### Usable now

ERC-8001 is Final. The EIP-712 domain, the hashing rules for intents and acceptances, the state enum, the mandatory events, and the verification rules are settled, so code written against this interface will not have the signatures pulled out from under it. It supports EOAs (ECDSA), contract wallets (ERC-1271), and compact signatures (EIP-2098), so it works regardless of wallet type. Just remember that ERC-8001 records the coordination agreement and nothing more. Actually doing and verifying the work is left to the application or to a separate layer like ERC-8183.

### Still unstable

ERC-8183, ERC-8226, and ERC-8041 are Draft. Function names, struct fields, and state enums can shift during review, so it is risky for a production contract to hardcode a dependency on these interfaces. On top of that, the ERC-8004 that ERC-8041 and the ERC-8183/ERC-8226 composition lean on is itself still Draft; when the base moves, everything above it moves too. Good for experiments and prototypes, but do not stake mainnet assets on them without budgeting for migration.

### Worth watching

- **The Ethereum Magicians threads.** They are the first place each draft's interface direction shows up. See the discussion links in each section above.
- **Reference implementations and audits.** Moving from Draft to Final takes community review, reference implementations, and security audits. When those land is the signal for real adoption.
- **ERC-8226's structured-data requirement.** How the ban on binary oracles, and the demand for structured compliance data, gets refined in real implementations is the thing to track.
- **ERC-8183's evaluator and oracle gap.** Tying off-chain results to on-chain rulings is left outside the spec. The patterns that fill it are worth watching.
- **Convergence with a payments layer.** ERC-8004 keeps payments out of scope but notes that payments such as x402 can enrich its feedback signals. How commerce (ERC-8183) meshes with a payment protocol is the next thing to watch.

## Takeaways

ERC-8001 has reached Final on the Ethereum standards track. The other three (ERC-8183, ERC-8226, ERC-8041) are still Draft. It cannot be said too often: do not treat a Draft as a settled production foundation.

The direction is clear. As AI agents take on more substantive on-chain roles as service providers, collaborators, and compliance participants, the trust stack alone is not enough. Agents need standard ways to earn fees, coordinate with other agents, satisfy compliance, and operate within defined collection parameters. These four proposals are moving that way. Whether these specific drafts reach Final or get replaced by revised proposals is still open. When the specs settle, this post will be updated.

## Further reading

- [The AI Agent Trust Stack: ERC-8004, ERC-8126, ERC-8196](../ai-agent-wallet-trust-stack-erc-8004-8126-8196): the previous post, covering the three trust-stack layers in detail.
- [ERC-8183 discussion thread](https://ethereum-magicians.org/t/erc-8183-agentic-commerce/27902): the Agentic Commerce discussion on Ethereum Magicians.
- [ERC-8226 discussion thread](https://ethereum-magicians.org/t/erc-8226-regulated-agent-mandate/28208): the Regulated Agent Mandate discussion.
- [ERC-8041 discussion thread](https://ethereum-magicians.org/t/erc-8041-fixed-supply-agent-nft-collections/25656): the Fixed-Supply Agent NFT Collections discussion.
- [ERC-8004: Trustless Agents](https://eips.ethereum.org/EIPS/eip-8004): the Identity, Reputation, and Validation registries behind trustless agent interaction.

## References

- [ERC-8183: Agentic Commerce](https://eips.ethereum.org/EIPS/eip-8183): ethereum.org, accessed 2026-07-02
- [ERC-8226: Regulated Agent Mandate](https://eips.ethereum.org/EIPS/eip-8226): ethereum.org, accessed 2026-07-02
- [ERC-8001: Agent Coordination Framework](https://eips.ethereum.org/EIPS/eip-8001): ethereum.org, accessed 2026-07-02
- [ERC-8041: Fixed-Supply Agent NFT Collections](https://eips.ethereum.org/EIPS/eip-8041): ethereum.org, accessed 2026-07-02
- [ERC-8004: Trustless Agents](https://eips.ethereum.org/EIPS/eip-8004): ethereum.org, accessed 2026-07-02 (trust stack context)
