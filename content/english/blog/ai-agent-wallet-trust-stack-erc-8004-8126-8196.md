---
title: "The AI Agent Trust Stack: ERC-8004, ERC-8126, and ERC-8196"
meta_title: ""
description: "How three Ethereum standards work together to handle AI agent identity, security verification, and policy-bound wallet execution."
date: 2026-06-30T07:00:00+09:00
lastmod: 2026-07-17T17:50:08+09:00
image: ""
categories: ["Blockchain"]
tags: ["ai-agent", "wallet", "erc-8004", "erc-8126", "erc-8196"]
author: "whackur"
translationKey: "ai-agent-wallet-trust-stack-erc-8004-8126-8196"
draft: false
---

When an AI agent acts on behalf of a user (spending funds, calling contracts, accessing paid APIs), the obvious question is: how do you know this agent is safe? The Ethereum community has three standards that address different layers of that question. They don't solve the whole problem, but they're building toward a coherent stack.

## The trust problem with autonomous agents

When a person signs a transaction in MetaMask, the signing party is unambiguous. When an AI agent executes transactions automatically, three distinct problems arise.

**Identity.** Agents from different organizations need a shared registry to interact. An agent claiming to be a "payment agent" is unverifiable without one. Without a common scheme, every platform builds its own allowlist, which fragments at scale.

**Verification.** Registration says an agent exists; it says nothing about whether it's safe. The smart contract code may have a reentrancy bug. The wallet may have prior interactions with sanctioned addresses. A separate security assessment layer is needed, independent of the identity registry.

**Execution scope.** Giving an agent a private key means unconstrained access. Owners need to express delegation boundaries: this agent can swap up to $100 per day on these contracts, and nothing else. Those constraints need to be enforced at execution time rather than agreed informally.

Ethereum addresses these three problems with separate ERC standards. ERC-8004 handles identity. ERC-8126 (Final) handles verification. ERC-8196 (Last Call) handles execution policy. Each can be used independently, but high-value automated transactions benefit from all three.

## ERC-8004: Trustless Agents

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) provides a common registry for discovering and interacting with agents across organizational boundaries. It deployed on Ethereum mainnet on 2026-01-29 and has since been studied across Ethereum, BSC, and Base. The ethereum/ercs process status is Draft. Authors: Marco De Rossi, Davide Crapis, Jordan Ellis, Erik Reppel. It builds on ERC-721, EIP-712, EIP-155, and ERC-1271.

Three registries form the core:

**Identity Registry.** Agents are registered as ERC-721 NFTs. The `tokenId` is the `agentId`, and the `tokenURI` is the `agentURI` pointing to a JSON registration file. The global identifier looks like:

```
eip155:1:0x742...   (namespace:chainId:registryAddress)
```

The registration file contains the agent's name, description, service endpoints, and supported trust models (`reputation`, `crypto-economic`, `tee-attestation`, etc.). Importantly, registration only provides discoverability. It doesn't guarantee the agent is safe.

**Reputation Registry.** Clients post feedback on agents using tags like `starred`, `reachable`, `uptime`, `responseTime`. The registry is a generic bulletin board. Filtering to a trusted set of `clientAddresses` is the application's responsibility. Without that, Sybil attacks are trivial. As of May 2026, a large share of registered agents are placeholders with little real activity, so the reputation data itself is still thin.

**Validation Registry.** Stores on-chain records of validation requests and validator responses. The `response` field is 0-100 (binary validation can use 0=fail, 100=pass). The `tag` field classifies the verification method: `tee-attestation`, `zkml`, `reexecution`, etc.

ERC-8004 doesn't mandate a single trust model. Low-stakes tasks and high-risk ones can use different verification approaches.

## ERC-8126: AI Agent Verification

ERC-8004 records that an agent exists and who owns it. It says nothing about whether that agent is trustworthy. ERC-8126 is the verification layer: it defines the interface for external security assessment providers who evaluate a registered agent across wallet history, contract code, web endpoints, and media, then return a 0-100 risk score. Lower score means lower risk.

[ERC-8126](https://eips.ethereum.org/EIPS/eip-8126) moved to Final status on June 2, 2026. Authors: Leigh Cronian and Chris Johnson.

The key design constraint: verifiers don't accept raw parameters like `walletAddress` or `url` directly. They take an `agentId` and read the registration metadata through ERC-8004. This ties verification results to a registered agent identity rather than arbitrary parameters.

**Five verification types** compliant providers must implement:

- **ETV (Ethereum Token Verification)**: checks that the registered contract address is actually deployed and scans for known vulnerability patterns
- **MCV (Media Content Verification)**: checks agent images for AI-generation artifacts, provenance, and manipulation
- **SCV (Solidity Code Verification)**: scans Solidity code for reentrancy, flash loan attacks, and access control issues
- **WAV (Web Application Verification)**: validates HTTPS endpoints, TLS certificates, and common web vulnerabilities
- **WV (Wallet Verification)**: checks wallet history against threat intelligence databases, looks for mixer interactions and sanctioned address links

PDV (Private Data Verification) generates a ZKP (zero-knowledge proof) so verification results can be shared without exposing sensitive details. QCV (Quantum Cryptography Verification) is an optional extension for long-lived sensitive data.

**Risk scoring.** Overall score is the average of applicable verification scores, on a 0-100 scale where 0 is safest. Low Risk is 0-20; Critical is 81-100. That's a risk score, not a trust score: lower is better.

Final status means the spec is stable enough to implement against. It doesn't mean existing verification providers are high quality.

## ERC-8196: AI Agent Authenticated Wallet

Having an agent's identity (ERC-8004) and risk score (ERC-8126) still leaves the execution scope problem open. A private key gives an agent unconstrained access to all funds in the wallet. ERC-8196 defines a policy structure that sits in front of execution: the owner registers permitted actions, a contract allowlist, per-transaction and daily spending limits, and an expiry time. The smart wallet checks the active policy before executing any agent request. The agent receives a scoped delegation, not a key.

[ERC-8196](https://eips.ethereum.org/EIPS/eip-8196)'s process status is Last Call, with a last-call-deadline of 2026-07-14. Last Call is still peer review, not Final, so the interface and security model can still change during review. Authors: Leigh Cronian and Chris Johnson.

**Policy fields:**

```
agentAddress    → the authorized AI agent
agentId         → the agent's tokenId in the ERC-8004 Identity Registry
ownerAddress    → the asset owner / delegator
allowedActions  → ["transfer", "swap", ...]
allowedContracts → address[] allowlist
blockedContracts → address[] blocklist
maxValuePerTx   → per-transaction ceiling
maxValuePerDay  → daily spending limit (optional)
validAfter      → policy start time
validUntil      → policy expiry
minVerificationScore → max allowable ERC-8126 risk score
```

`agentId` is a required field. It's registered alongside the agent address in `registerPolicy` and carried through to the ERC-8126 check at execution time. Implementations MUST call `getLatestRiskScore` with the policy's `agentId` before processing `executeAction`.

The `minVerificationScore` name is confusing. In ERC-8126, lower score means safer. So this field is actually a ceiling on acceptable risk: execution is rejected once the retrieved score exceeds it. Set it to 20, and only Low Risk agents (score 0-20) can execute automatically.

**Interface.** Four core functions: `registerPolicy` registers the agent address and `agentId` along with action/contract allowlists, limits, a validity window, and `minVerificationScore`. `executeAction` takes `policyHash`, a target address, value, calldata, a nonce, an entropy commitment, and a signature, and returns `(bool success, bytes32 auditEntryId)`. `revokePolicy` and `getPolicy` round out the interface. Events: `PolicyRegistered`, `ActionExecuted`, `PolicyRevoked`, `AuditEntryLogged`. Errors: `PolicyExpired`, `ValueExceedsLimit`, `InvalidSignature`, `EntropyVerificationFailed`, `PolicyViolation`.

**Audit trail.** Each audit entry includes `previousHash`, forming a hash chain. Entries can live on IPFS with periodic Merkle roots posted to ERC-8004's Validation Registry. The chain detects tampering: delete or alter any entry and the subsequent hashes break.

**EIP-712 signing.** Actions and delegations use typed data signing, so users can read what they're approving rather than signing a blind hash.

**EIP-4337 compatible.** Can be implemented as an account abstraction wallet or a policy enforcement module over an existing AA wallet.

## How they fit together

![Diagram of the AI agent wallet trust stack: ERC-8004 identity, reputation, and validation registries feed into an ERC-8126 risk score, which an ERC-8196 policy check evaluates before wallet transaction execution.](/images/posts/ai-agent-wallet-trust-stack-erc-8004-8126-8196/trust-stack-layers.svg)

*This diagram is a conceptual composition of ERC-8004, ERC-8126, and ERC-8196 into one flow. It doesn't mean the three standards must be implemented as a single mandatory coupling. Each layer can also be used on its own.*

Each layer is independent. You can use ERC-8004 without ERC-8196. But for high-value automated transactions, using all three gives you a traceable path from "who is this agent" through "what is its risk score" to "did the wallet authorize this specific action."

## Limitations

- A registration file provides discoverability only. It does not vouch for the agent's safety.
- ERC-8004 is deployed on mainnet but its ethereum/ercs process status remains Draft; the interface specification may still change.
- ERC-8196's process status is Last Call (last-call-deadline: 2026-07-14). That's still peer review, not Final, so the interface and security model can still change during review.
- A low ERC-8126 risk score reflects verification at a point in time, not a guarantee of good intentions.
- Reputation is Sybil-attackable without careful client filtering.
- Host manipulation isn't fully eliminated by ERC-8196. The paper recommends multiple independent hosts for high-value agents.
- Verification provider quality varies. A Final ERC-8126 spec doesn't validate the providers implementing it.

## Further reading

- [ERC-8004 Agent Reputation: On-Chain Registration and Lookup](../erc8004-agent-reputation-registry-lookup) — hands-on guide to the Reputation Registry (this blog)
- [ERC-8004 spec](https://eips.ethereum.org/EIPS/eip-8004) — Draft (process); deployed on Ethereum mainnet 2026-01-29
- [ERC-8004.org launch](https://www.8004.org/blog/welcome-to-8004) — official site; 2026-01-29
- [ERC-8126 spec](https://eips.ethereum.org/EIPS/eip-8126) — Final
- [ERC-8196 spec](https://eips.ethereum.org/EIPS/eip-8196) — Last Call (deadline 2026-07-14)
- [ERC-8126 Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8126-ai-agent-verification/27445)

## References

- [ERC-8004: Trustless Agents](https://eips.ethereum.org/EIPS/eip-8004) — ethereum.org, Draft (process); deployed mainnet 2026-01-29; accessed 2026-07-04
- [ERC-8126: AI Agent Verification](https://eips.ethereum.org/EIPS/eip-8126) — ethereum.org, Final (2026-06-02); accessed 2026-07-04
- [ERC-8196: AI Agent Authenticated Wallet](https://eips.ethereum.org/EIPS/eip-8196) — ethereum.org, Last Call (last-call-deadline 2026-07-14); accessed 2026-07-15
- [ethereum/ercs GitHub](https://github.com/ethereum/ercs) — source repository; accessed 2026-07-04
- [8004.org launch post](https://www.8004.org/blog/welcome-to-8004) — ERC-8004 official site, launched 2026-01-29; accessed 2026-06-30
- [arXiv 2606.26028v1](https://arxiv.org/abs/2606.26028) — cross-chain deployment study (Ethereum, BSC, Base); accessed 2026-06-30
