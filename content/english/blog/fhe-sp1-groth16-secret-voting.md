---
title: "Secret Voting Architecture with FHE, SP1, and Groth16"
meta_title: ""
description: "How to design on-chain secret voting using FHE for encrypted tallying, SP1 for execution proofs, and Groth16 for EVM-friendly verification, with a full security assumptions checklist."
date: 2026-06-30T02:00:00+09:00
lastmod: 2026-06-30T02:00:00+09:00
image: ""
categories: ["Blockchain"]
tags: ["fhe", "zk-proof", "groth16", "sp1", "voting", "privacy", "zero-knowledge", "maci", "semaphore"]
author: "whackur"
translationKey: "fhe-sp1-groth16-secret-voting"
draft: false
---

On-chain secret voting creates three tensions at once. Votes must stay hidden while still being tallied. Off-chain computation cannot be trusted without proof, yet results need to land on-chain. And the EVM cannot run heavy cryptographic operations natively, but it still needs to verify them. FHE (Fully Homomorphic Encryption), SP1 zkVM, and Groth16 each take on one of these.

The short summary holds up: FHE adds ciphertexts without decrypting, SP1 proves that aggregation and verification logic ran correctly, and Groth16 wraps that proof into a small constant-size SNARK the EVM can check cheaply. What the summary leaves out is the coprocessor, gateway, KMS threshold decryption, nullifier-based double-vote prevention, and trusted setup assumptions that production deployments require. This post covers each piece in detail, compares alternative privacy voting patterns, and offers a security assumptions checklist.

## What each component does

### FHE: tally over ciphertexts

FHE's job is to aggregate votes without decrypting them. A voter encrypts a ballot (`yes=1`, `no=0`) under the FHE public key and submits the ciphertext. The coprocessor runs `FHE.add` across all submitted ciphertexts. The running tally never appears as plaintext during aggregation.

[Zama Protocol](https://docs.zama.ai/protocol/protocol/overview) documents the supported operations on encrypted integers: `add`, `sub`, `mul`, `min`, `max`, comparison, bitwise ops, and `FHE.select`. Division and modulo work only with plaintext divisors. The EVM does not run FHE operations itself. The host contract emits symbolic events, and the off-chain [coprocessor](https://docs.zama.ai/protocol/protocol/overview/coprocessor) performs the actual TFHE-rs computation.

### SP1: execution integrity proof

[SP1](https://docs.succinct.xyz/docs/sp1/introduction) is a zkVM for Rust programs compiled to RISC-V. In a secret voting context, a Rust program verifies that voter eligibility checks, nullifier deduplication, ciphertext handle lists, aggregation rules, and public-value digests are all consistent, then produces a proof of that execution.

One thing worth being precise about: re-executing all FHE homomorphic operations inside SP1 for proof purposes gets expensive. In practice, the FHE computation path and the ZK verification boundary are separated. SP1's role is closer to proving that the aggregation transcript and public inputs are internally consistent, not re-running every FHE operation from scratch.

### Groth16: on-chain verification wrapper

[SP1 supports four proof modes](https://docs.succinct.xyz/docs/sp1/generating-proofs/proof-types):

| Type | Size | On-chain gas | Use case |
|------|------|-------------|----------|
| Core | proportional to execution | high | off-chain verification |
| Compressed | constant-size STARK | high | recursive aggregation, not for on-chain |
| Groth16 | ~260 bytes | ~270k gas | on-chain deployment, recommended |
| PLONK | ~868 bytes | ~300k gas | alternative without a trusted setup ceremony |

Groth16 compresses the large execution proof into a constant-size SNARK suited for EVM verification. Calling it a "260-byte receipt" captures the idea, but the full verification takes proof bytes, public values, a program verification key, and verifier routing together. PLONK is the alternative if the trusted setup ceremony is a hard constraint.

## End-to-end flow

1. **Voter registration**: voters register in a group membership or allowlist. For anonymous one-person-one-vote, a Semaphore-style identity commitment with nullifiers works well.

2. **Ballot submission**: the browser encrypts the vote under the FHE public key, then proves via ZK proof that the voter is registered, has not yet spent their nullifier in this election, and the ciphertext encodes a valid value. The on-chain contract verifies the proof and nullifier, then records the ciphertext handle.

3. **Ciphertext aggregation**: the host contract emits FHE operations as symbolic events. The off-chain coprocessor performs the actual `add` and `select` operations and posts the resulting ciphertext commitment.

4. **Execution integrity proof**: an SP1 program checks consistency across the public input list, nullifier set, ciphertext handles, aggregation rules, commitment/digest, and final public values. The proof is wrapped in Groth16 or PLONK and verified on Ethereum or Base.

5. **Decryption**: after the voting period, the [KMS](https://docs.zama.ai/protocol/protocol/overview/kms) performs threshold decryption. Zama's documentation describes an example structure requiring 9 of 13 MPC nodes, with the private key secret-shared so no single party can access it directly.

6. **On-chain finalization**: the Ethereum or Base contract verifies the Groth16/PLONK proof and the decryption result, then records the final tally. On L2s like Base, the same gas cost translates to a lower USD fee.

## Other private voting patterns

The right approach depends on which property matters most: anonymous one-person-one-vote, bribery resistance, hiding interim results, or keeping even the coordinator blind.

### Semaphore

[Semaphore](https://docs.semaphore.pse.dev/) proves that an anonymous group member has signaled exactly once. An identity commitment goes into a Merkle tree; the proof verifies "I am a member, and I have not yet signaled under this external nullifier." It fits simple anonymous voting and DAO signaling. It does not provide bribery resistance on its own.

### MACI

[MACI (Minimal Anti-Collusion Infrastructure)](https://maci.pse.dev/docs/introduction) targets both privacy and collusion/bribery resistance. Users submit encrypted vote messages; a coordinator processes them off-chain and proves the tally is correct via zk-SNARK. A key-change message can invalidate a prior vote, which makes it hard for a briber to trust that a voter's disclosed ballot is their actual final choice. The remaining trust assumption: the coordinator sees individual votes, even though the zk-SNARK prevents it from manipulating the result.

### Shutter Network / threshold encryption

[Shutter Network](https://docs.shutter.network/) hides ballot contents until the deadline to reduce front-running, bandwagon effects, and last-minute bribery. A keyper committee manages a threshold key and publishes decryption key shares after the voting period ends. This requires honesty and liveness from at least t-of-n keypers.

### FHE plus ZK hybrid

Combining FHE aggregation with ZK/SP1 proofs means the coordinator never sees plaintext votes at all. The tradeoff is a more complex trust model: coprocessor, gateway, KMS, threshold decryption, trusted setup, and proof generation costs all need to appear explicitly in the security model.

## Design decision guide

- **Simple anonymous one-person-one-vote**: Semaphore/nullifier is the most straightforward path.
- **Bribery and collusion resistance is the priority**: start with MACI.
- **Hide interim results until the deadline**: Shutter-style threshold encryption or timelock encryption.
- **Coordinator must not see plaintext votes**: FHE aggregation combined with threshold decryption and ZK/SP1 integrity proofs.
- **Minimize on-chain verification cost on Ethereum/Base**: SP1 with the Groth16 verifier, with trusted setup assumptions documented. If the trusted setup ceremony is not acceptable, evaluate PLONK.

## Security assumptions checklist

Before building, have clear answers to these:

- What is the voter eligibility source? (allowlist, token snapshot, identity credential, Semaphore group)
- Is the nullifier domain isolated per election?
- Is there a range proof that each ballot ciphertext encodes a valid value (0/1, candidate index)?
- What is the policy on double-voting, revoting, and key changes?
- How is the FHE coprocessor output verified against a commitment or signature?
- What is the KMS threshold (t-of-n), and how are early decryption, decryption refusal, and collusion scenarios handled?
- What digests and state roots go into SP1 public inputs?
- Is the Groth16 trusted setup assumption documented, or is PLONK used and why?
- Is only the final tally published, or could turnout metadata create a privacy leak?

## Further reading

- [Zama Protocol Documentation](https://docs.zama.ai/protocol/protocol/overview): FHE on-chain architecture, coprocessor, KMS design
- [Succinct SP1 Documentation](https://docs.succinct.xyz/docs/sp1/introduction): zkVM overview and proof type comparison
- [SP1 Contracts](https://github.com/succinctlabs/sp1-contracts): verifier contracts for Ethereum and Base deployment
- [MACI Documentation](https://maci.pse.dev/docs/introduction): anti-collusion voting system
- [Semaphore Documentation](https://docs.semaphore.pse.dev/): anonymous group membership proofs
- [Shutter Network Documentation](https://docs.shutter.network/): threshold encryption for front-running prevention

## References

- [Zama Protocol Overview](https://docs.zama.ai/protocol/protocol/overview): docs.zama.ai, accessed 2026-06-30
- [Zama Protocol: Operations on encrypted types](https://docs.zama.ai/protocol/solidity-guides/smart-contract/operations): docs.zama.ai, accessed 2026-06-30
- [Zama Protocol: KMS](https://docs.zama.ai/protocol/protocol/overview/kms): docs.zama.ai, accessed 2026-06-30
- [Succinct SP1 Introduction](https://docs.succinct.xyz/docs/sp1/introduction): docs.succinct.xyz, accessed 2026-06-30
- [SP1 Proof Types](https://docs.succinct.xyz/docs/sp1/generating-proofs/proof-types): docs.succinct.xyz, accessed 2026-06-30
- [SP1 Contracts](https://github.com/succinctlabs/sp1-contracts): GitHub, succinctlabs, accessed 2026-06-30
- [MACI Introduction](https://maci.pse.dev/docs/introduction): maci.pse.dev, accessed 2026-06-30
- [Semaphore Documentation](https://docs.semaphore.pse.dev/): docs.semaphore.pse.dev, accessed 2026-06-30
- [Shutter Network Documentation](https://docs.shutter.network/): docs.shutter.network, accessed 2026-06-30
