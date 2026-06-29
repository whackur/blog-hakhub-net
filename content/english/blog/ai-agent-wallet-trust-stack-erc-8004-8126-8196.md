---
title: "The AI Agent Trust Stack: ERC-8004, ERC-8126, and ERC-8196"
meta_title: ""
description: "How three Ethereum standards work together to handle AI agent identity, security verification, and policy-bound wallet execution."
date: 2026-06-30T07:00:00+09:00
lastmod: 2026-06-30T07:00:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["ai-agent", "wallet", "erc-8004", "erc-8126", "erc-8196"]
author: "hakhub"
translationKey: "ai-agent-wallet-trust-stack-erc-8004-8126-8196"
draft: true
---

When an AI agent acts on behalf of a user (spending funds, calling contracts, accessing paid APIs), the obvious question is: how do you know this agent is safe? The Ethereum community has three draft or finalized standards that address different layers of that question. They don't solve the whole problem, but they're building toward a coherent stack.

## ERC-8004: Trustless Agents

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) (Draft) provides a common registry for discovering and interacting with agents across organizational boundaries. Authors: Marco De Rossi, Davide Crapis, Jordan Ellis, Erik Reppel. It builds on ERC-721, EIP-712, EIP-155, and ERC-1271.

Three registries form the core:

**Identity Registry.** Agents are registered as ERC-721 NFTs. The `tokenId` is the `agentId`, and the `tokenURI` is the `agentURI` pointing to a JSON registration file. The global identifier looks like:

```
eip155:1:0x742...   (namespace:chainId:registryAddress)
```

The registration file contains the agent's name, description, service endpoints, and supported trust models (`reputation`, `crypto-economic`, `tee-attestation`, etc.). Importantly, registration only provides discoverability. It doesn't guarantee the agent is safe.

**Reputation Registry.** Clients post feedback on agents using tags like `starred`, `reachable`, `uptime`, `responseTime`. The registry is a generic bulletin board. Filtering to a trusted set of `clientAddresses` is the application's responsibility. Without that, Sybil attacks are trivial.

**Validation Registry.** Stores on-chain records of validation requests and validator responses. The `response` field is 0–100 (binary validation can use 0=fail, 100=pass). The `tag` field classifies the verification method: `tee-attestation`, `zkml`, `reexecution`, etc.

ERC-8004 doesn't mandate a single trust model. Low-stakes tasks and high-risk ones can use different verification approaches.

## ERC-8126: AI Agent Verification

[ERC-8126](https://eips.ethereum.org/EIPS/eip-8126) moved to Final status on June 2, 2026. Authors: Leigh Cronian and Chris Johnson. It defines the interface for specialized security verification providers that assess an ERC-8004 registered agent.

The key design constraint: verifiers don't accept raw parameters like `walletAddress` or `url` directly. They take an `agentId` and read the registration metadata through ERC-8004. This ties verification results to a registered agent identity rather than arbitrary parameters.

**Five verification types** compliant providers must implement:

- **ETV (Ethereum Token Verification)**: checks that the registered contract address is actually deployed and scans for known vulnerability patterns
- **MCV (Media Content Verification)**: checks agent images for AI-generation artifacts, provenance, and manipulation
- **SCV (Solidity Code Verification)**: scans Solidity code for reentrancy, flash loan attacks, and access control issues
- **WAV (Web Application Verification)**: validates HTTPS endpoints, TLS certificates, and common web vulnerabilities
- **WV (Wallet Verification)**: checks wallet history against threat intelligence databases, looks for mixer interactions and sanctioned address links

PDV (Private Data Verification) generates a ZKP proof so verification results can be shared without exposing sensitive details. QCV (Quantum Cryptography Verification) is an optional extension for long-lived sensitive data.

**Risk scoring.** Overall score is the average of applicable verification scores, on a 0–100 scale where 0 is safest. Low Risk is 0–20; Critical is 81–100. That's a risk score, not a trust score: lower is better.

Final status means the spec is stable enough to implement against. It doesn't mean existing verification providers are high quality.

## ERC-8196: AI Agent Authenticated Wallet

[ERC-8196](https://eips.ethereum.org/EIPS/eip-8196) (Draft) is the execution layer. Author: Leigh Cronian. Instead of handing an agent a private key, the owner registers a policy that constrains what the agent can do.

**Policy fields:**

```
agentAddress    → the authorized AI agent
ownerAddress    → the asset owner / delegator
allowedActions  → ["transfer", "swap", ...]
allowedContracts → address[] allowlist
blockedContracts → address[] blocklist
maxValuePerTx   → per-transaction ceiling
maxValuePerDay  → daily spending limit
validAfter      → policy start time
validUntil      → policy expiry
minVerificationScore → max allowable ERC-8126 risk score
```

The `minVerificationScore` name is confusing. In ERC-8126, lower score means safer. So this field is actually a ceiling on acceptable risk. Set it to 20, and only Low Risk agents (score 0–20) can execute automatically.

**Audit trail.** Each audit entry includes `previousHash`, forming a hash chain. Entries can live on IPFS with periodic Merkle roots posted to ERC-8004's Validation Registry. The chain detects tampering: delete or alter any entry and the subsequent hashes break.

**EIP-712 signing.** Actions and delegations use typed data signing, so users can read what they're approving rather than signing a blind hash.

**EIP-4337 compatible.** Can be implemented as an account abstraction wallet or a policy enforcement module over an existing AA wallet.

## How they fit together

```
ERC-8004  →  who is this agent? (identity, reputation, validation records)
     |
ERC-8126  →  is this agent safe? (wallet, code, web, media risk score)
     |
ERC-8196  →  is this specific action allowed by the owner's policy?
     |
     →  transaction execution
```

Each layer is independent. You can use ERC-8004 without ERC-8196. But for high-value automated transactions, using all three gives you a traceable path from "who is this agent" through "what is its risk score" to "did the wallet authorize this specific action."

## Honest caveats

- ERC-8004 and ERC-8196 are still Draft. Interfaces and security models may change.
- A low ERC-8126 risk score reflects verification at a point in time, not a guarantee of good intentions.
- Reputation is Sybil-attackable without careful client filtering.
- Host manipulation isn't fully eliminated by ERC-8196. The paper recommends multiple independent hosts for high-value agents.
- Verification provider quality varies. A Final ERC-8126 spec doesn't validate the providers implementing it.

## Further reading

- [ERC-8004 spec](https://eips.ethereum.org/EIPS/eip-8004) — Draft
- [ERC-8126 spec](https://eips.ethereum.org/EIPS/eip-8126) — Final
- [ERC-8196 spec](https://eips.ethereum.org/EIPS/eip-8196) — Draft
- [ERC-8126 Ethereum Magicians discussion](https://ethereum-magicians.org/t/erc-8126-ai-agent-verification/27445)

## References

- [ERC-8004: Trustless Agents](https://eips.ethereum.org/EIPS/eip-8004) — ethereum.org, Draft; accessed 2026-06-30
- [ERC-8126: AI Agent Verification](https://eips.ethereum.org/EIPS/eip-8126) — ethereum.org, Final (2026-06-02); accessed 2026-06-30
- [ERC-8196: AI Agent Authenticated Wallet](https://eips.ethereum.org/EIPS/eip-8196) — ethereum.org, Draft; accessed 2026-06-30
- [ethereum/ercs GitHub](https://github.com/ethereum/ercs) — source repository; accessed 2026-06-30
