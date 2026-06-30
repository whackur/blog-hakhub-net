---
title: "ERC-8004 Agent Reputation: On-Chain Registration and Lookup"
meta_title: ""
description: "How to register agent feedback on-chain using ERC-8004's giveFeedback(), query it with getSummary() against a trusted client set, and which services exist today to browse registered agents and their reputation data."
date: 2026-06-30T15:00:00+09:00
lastmod: 2026-06-30T15:00:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["ai-agent", "erc-8004", "reputation", "smart-contract", "onchain"]
author: "whackur"
translationKey: "erc8004-agent-reputation-registry-lookup"
draft: false
---

A [prior post on this blog](../ai-agent-wallet-trust-stack-erc-8004-8126-8196) covered the ERC-8004/8126/8196 trust stack: three Ethereum registries that handle agent identity, reputation, and validation. If you want the conceptual overview first, start there. This post is about something narrower: how feedback actually gets written to the Reputation Registry, how to read it back, and what services are available today to browse and index that data.

ERC-8004 is currently a Draft standard, authored by Marco De Rossi, Davide Crapis, Jordan Ellis, and Erik Reppel. Payment is explicitly out of scope. The spec fills a gap that A2A and MCP don't address: discovery and trust.

## The Reputation Registry

The Reputation Registry is a permissionless on-chain bulletin board. Any address can post feedback about any registered agent. The registry imposes no access control and makes no judgment about whether a submission is accurate.

Sybil resistance is the application's job, not the registry's. When querying, callers must supply a non-empty set of trusted client addresses. The registry returns a filtered aggregate over that set. An empty client set is rejected by the contract. This design shifts the question from "what is this agent's score?" to "which raters do I trust?" Each application answers that differently.

## What gets stored

The on-chain `Feedback` struct holds four fields:

- `score` (uint8, 0-100): the fixed-point `value`/`valueDecimals` input, normalized to a 0-100 integer for storage.
- `tag1`, `tag2` (bytes32): classification tags, indexed as keccak256 hash topics for efficient log filtering.
- `isRevoked` (bool): whether this feedback entry has been revoked.

`feedbackURI` and `feedbackHash` are not stored in the struct. They are emitted as events. This keeps on-chain storage costs down while allowing off-chain indexers to reconstruct the full record.

Indexing is three-dimensional: `agentId -> clientAddress -> feedbackIndex`. Indexes are 1-based. `_lastIndex[agentId][client] == 0` means that client has left no feedback for that agent.

## Registering feedback

```solidity
function giveFeedback(
    uint256 agentId,
    int128 value,
    uint8 valueDecimals,
    string tag1,
    string tag2,
    string endpoint,
    string feedbackURI,
    bytes32 feedbackHash
) external;
```

Field by field:

- **agentId**: the ERC-721 token ID of the target agent in the Identity Registry.
- **value, valueDecimals**: fixed-point score. For a quality score of 85, use `value=85, valueDecimals=0` (85 / 10^0 = 85). For 99.5% uptime, use `value=9950, valueDecimals=2`. The contract normalizes this to a uint8 score (0-100) for storage.
- **tag1, tag2**: free-form string tags. Empty strings are valid.
- **endpoint**: the specific agent endpoint this feedback applies to. Use an empty string for feedback about the agent in general.
- **feedbackURI**: off-chain URI for the full feedback payload. IPFS is preferred for content-addressability; HTTPS works but is less durable.
- **feedbackHash**: keccak256 of the content at `feedbackURI`. Lets consumers detect tampering without fetching the URI.

The wallet sending the transaction (`msg.sender`) becomes the `clientAddress` in the emitted event. One feedback entry = one transaction. No gating, no approval required at the registry layer.

**Example.** Registering a quality score of 85 for agent ID 42:

```
agentId        = 42
value          = 85
valueDecimals  = 0
tag1           = "quality"
tag2           = ""
endpoint       = ""
feedbackURI    = "ipfs://Qm..."
feedbackHash   = 0xabc123...
```

The contract stores `score = 85` as a uint8. Tag indexing uses the keccak256 of the tag string as an event topic. With viem, pass the human-readable string; viem handles the encoding.

## Querying reputation

```solidity
function getSummary(
    uint256 agentId,
    address[] calldata clientAddresses,
    string calldata tag1,
    string calldata tag2
) external view returns (...);
```

The return value is a tuple containing the aggregated score and feedback count across the trusted set. Check the current ABI for exact field names and types.

`clientAddresses` must be non-empty. This is the Sybil-resistance mechanism, not a validation quirk. Anyone can post feedback, including an agent's operators. A raw aggregate across all submitters is trivially manipulable. Callers must supply a set of addresses they trust, and the contract aggregates only from that set.

What goes into `clientAddresses` is the application's call. Options include a curated list of known clients in your ecosystem, a set validated by a third-party attestation service, or addresses derived from your own user base.

Other read functions:

- `getClients(agentId)`: returns all client addresses that have posted at least one feedback entry for the agent. Useful for building or checking a trusted set.
- `getResponseCount(...)`: called with `feedbackIndex == 0`, returns the total count of feedback entries from a specific client for a given agent.

For reading a single entry directly, verify the index is in range: `index >= 1 && index <= _lastIndex[agentId][clientAddress]`.

## Deployed contract addresses

ERC-8004 registries are deployed at deterministic CREATE2 addresses. The same address holds across all supported chains, and the contracts are byte-identical on Ethereum, Base, BNB Chain, Arbitrum, OP Mainnet, Polygon, Avalanche, Mantle, Scroll, and Gnosis.

| Registry | Address |
|----------|---------|
| Identity Registry | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| Reputation Registry | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` |
| Validation Registry | not yet on mainnet (testnet only) |

The `0x8004` prefix is a vanity prefix. All contracts are visible on standard block explorers (Etherscan, Basescan, BSCScan, and so on). Testnet addresses differ from mainnet; check the [QuickNode ERC-8004 Explorer contract docs](https://erc-8004.quicknode.com) before using any address.

Address data sourced from QuickNode ERC-8004 Explorer contract documentation, updated 2026-05-05.

## Ecosystem services

Several services index or browse ERC-8004 registry data:

| Service | URL | What it does |
|---------|-----|-------------|
| Agentscan | [agentscan.info](https://agentscan.info) | Operated by Alias (AliasAI). Searches and browses ERC-8004 agents across 21+ chains. Applies OASF taxonomy classification, displays reputation scores and on-chain activity. Indexes both public agents and StarCards-based private agents. |
| QuickNode ERC-8004 Explorer | [erc-8004.quicknode.com](https://erc-8004.quicknode.com) | Agent explorer, developer tutorials for feedback submission (viem) and read queries, contract address and ABI documentation, and a chain indexer config. Aggregates by convention tags: quality, safety, cost, speed, accuracy. |
| 8004agents.ai | [8004agents.ai](https://8004agents.ai) | Multichain ERC-8004 agent tracker. Shows reputation scores and validation status. (Some details unconfirmed.) |
| 8004.org | [8004.org](https://www.8004.org) | Official ERC-8004 site, launched 2026-01-29 alongside the mainnet deployment. |
| DeepWiki erc-8004-contracts | [deepwiki.com/erc-8004/erc-8004-contracts](https://deepwiki.com/erc-8004/erc-8004-contracts) | Reference contract API and storage documentation. Developer-focused. |
| Allium blog | [allium.so](https://www.allium.so) | On-chain analytics and analysis of ERC-8004 deployment data. Contributors include MetaMask, Ethereum Foundation, Google, and Coinbase. |

## Tag conventions

The ERC-8004 spec lists example tags: `starred`, `reachable`, `uptime`, `responseTime`. QuickNode's explorer aggregates a different convention set: `quality`, `safety`, `cost`, `speed`, `accuracy`.

Tags are free-form strings. Any value is valid, but only entries sharing the exact same label aggregate together. `"quality"` and `"Quality"` are distinct tags. Each application or explorer defines its own convention and aggregates by it. This is the design working as intended: the registry defines the bulletin board structure, not the scoring rubric. Custom tags work fine within a closed ecosystem, but they won't appear in aggregates from other services using different label conventions.

## Caveats

**Draft status.** ERC-8004 is a Draft ([github.com/ethereum/ERCs](https://github.com/ethereum/ERCs/blob/master/ERCS/erc-8004.md)). The interface can change before finalization. Track the spec and reference implementation before building production integrations.

**Placeholder-heavy registry.** As of May 2026, a significant share of registered agents are placeholders with little real activity. Reputation data is sparse at this stage, and scores reflect that.

**Sybil exposure.** Permissionless writes mean any actor can flood the registry with self-reviews. A poorly chosen `clientAddresses` set in `getSummary()` exposes callers to inflated or manipulated aggregates. The client set is where the actual trust decision lives.

**Off-chain URI durability.** `feedbackHash` detects tampering, but if an HTTPS-hosted `feedbackURI` goes offline, the full feedback payload is unrecoverable. IPFS or another content-addressed store reduces this risk.

**Validation Registry not on mainnet.** The TEE attestation flow is still being finalized. The Validation Registry runs on testnet only; task verification is not available in production yet.

## Takeaway

The Reputation Registry's architecture is intentionally simple: permissionless writes, application-filtered reads. `giveFeedback()` records one entry per transaction; `getSummary()` aggregates only over the client set the caller specifies. The same contracts run at the same addresses across 10+ chains, thanks to CREATE2 deterministic deployment. Agentscan and QuickNode's explorer are the main places to browse that data today.

The standing limitation is that the standard is still a Draft, actual reputation data is thin, and Sybil resistance depends entirely on how well applications curate their trusted client sets. Those are tractable problems, but unsolved in mid-2026.

## Further reading

- [AI Agent Identity, Verification, and Policy: The ERC-8004/8126/8196 Trust Stack](../ai-agent-wallet-trust-stack-erc-8004-8126-8196) — conceptual overview (this blog)
- [QuickNode ERC-8004 Explorer](https://erc-8004.quicknode.com) — agent browser and developer feedback submission guide
- [Agentscan](https://agentscan.info) — multichain agent search and reputation browser
- [erc-8004-contracts reference implementation](https://github.com/erc-8004/erc-8004-contracts) — source for ABI and storage layout

## References

- [EIP-8004 (Draft)](https://eips.ethereum.org/EIPS/eip-8004) — Ethereum Improvement Proposals, accessed 2026-06-30
- [ethereum/ERCs: ERC-8004](https://github.com/ethereum/ERCs/blob/master/ERCS/erc-8004.md) — EIP source text, accessed 2026-06-30
- [erc-8004/erc-8004-contracts](https://github.com/erc-8004/erc-8004-contracts) — reference contract implementation, accessed 2026-06-30
- [QuickNode ERC-8004 Explorer](https://erc-8004.quicknode.com) — contract addresses, ABI docs, and tutorials, accessed 2026-06-30
- [Agentscan](https://agentscan.info) — AI agent explorer, accessed 2026-06-30
- [8004.org](https://www.8004.org) — official ERC-8004 site, accessed 2026-06-30
- [DeepWiki: erc-8004-contracts](https://deepwiki.com/erc-8004/erc-8004-contracts) — reference contract API docs, accessed 2026-06-30
- [Allium](https://www.allium.so) — on-chain AI identity analytics, accessed 2026-06-30
- [arXiv 2606.26028: Can Trustless Agents Be Trusted?](https://arxiv.org/abs/2606.26028) — empirical study of ERC-8004 across Ethereum/BSC/Base, accessed 2026-06-30
