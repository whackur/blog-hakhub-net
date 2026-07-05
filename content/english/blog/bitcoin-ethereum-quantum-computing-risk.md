---
title: "Bitcoin, Ethereum, and the Quantum Computing Question"
meta_title: ""
description: "A March 2026 paper from Google, the Ethereum Foundation, and Stanford cut the qubit budget for attacking secp256k1 dramatically. Here is what changed, what did not, and what developers should do now."
date: 2026-07-05T23:37:01+09:00
lastmod: 2026-07-05T23:37:01+09:00
image: ""
categories: ["Blockchain"]
tags: ["bitcoin", "ethereum", "quantum-computing", "post-quantum-cryptography", "cryptography"]
author: "whackur"
translationKey: "bitcoin-ethereum-quantum-computing-risk"
draft: false
---

On March 30, 2026, a joint paper from Google Quantum AI, the Ethereum Foundation, and Stanford shook up the crypto community. It estimated that the physical qubit count needed to recover a secp256k1 private key (the elliptic curve behind Bitcoin and Ethereum signatures) had dropped nearly 20x from the previous best estimate. A threat that used to sound like "millions of qubits, decades away" now reads as "under 500,000, maybe within this decade."

That does not mean wallets get drained tomorrow. As of June 2026, the strongest quantum hardware sits around 2,500 physical qubits, still hundreds of times short of what an attack would require. But algorithmic progress has been closing that gap faster than hardware has, and millions of coins already sit with their public keys exposed on-chain. Both of those facts are reasons for blockchain developers to start paying attention now. This post walks through the research and proposals from the past few months to separate the real risk from the hype.

## The quantum attack on ECDSA signatures

ECDSA, the signature scheme behind Bitcoin and Ethereum, relies on the elliptic curve discrete logarithm problem (ECDLP): given a public key `Q = d·G`, recovering the private scalar `d` is computationally infeasible for classical computers. Shor's algorithm, run on a quantum computer, solves this in polynomial time using period finding via the quantum Fourier transform. Once ECDLP falls, the private key follows directly from the public key.

Bitcoin mining, based on SHA-256, is a different story. Grover's algorithm only offers a quadratic speedup on unstructured search, which weakens SHA-256's effective security from 256 bits to 128 bits. That is still an astronomically large number, so it is not a practical threat. There is effectively no quantum threat to proof-of-work mining: Grover parallelizes poorly, and Bitcoin's difficulty retarget every 2,016 blocks would absorb any speed advantage a quantum miner might briefly gain.

So the real threat narrows down to one thing: ECDLP, the math underneath ECDSA signatures.

## The fast decline in resource estimates

Assume the same hardware, and better algorithms still shrink the resource requirement. The pace of that shrinkage is worth tracking on its own.

- **2017 (Microsoft Research, Roetteler et al.)**: roughly 2,330 logical qubits for a P-256-class curve. A logical qubit is an error-corrected, stable unit built from many noisy physical qubits bundled together.
- **2023 (Litinski)**: about 9 million physical qubits using a photonic architecture.
- **March 2026 (Google, Ethereum Foundation, Stanford, arXiv:2603.28846)**: 1,200 to 1,450 logical qubits, translating to under 500,000 physical qubits under a surface-code error correction scheme (a method that suppresses physical qubit errors exponentially). That is roughly a 20x drop in physical qubits and a 10x drop in spacetime volume (total computation) compared to Litinski's estimate.

The headline number from this paper is an average of 9 minutes to recover a private key after a public key is exposed. That figure comes with caveats. The raw circuit, without priming, processes 70 to 90 million Toffoli gates and takes 18 to 23 minutes. Priming, precomputing the first half of the algorithm ahead of time, cuts the post-exposure time in half, to roughly 9 (or 12) minutes. That number matters because it sits close to Bitcoin's average 10-minute block time. It is also a single-instance estimate: it attacks one key at a time, and targeting multiple keys simultaneously would require additional dedicated machines.

Craig Gidney, from the same research circle, lowered the qubit budget for factoring RSA-2048 to under 1 million in May 2025 (arXiv:2505.15917), a 20x reduction from his own 2019 estimate of 20 million. Both papers point to the same pattern: attacks always get better.

Hardware has not caught up, though. Google's Willow chip (December 2024) demonstrated below-threshold error correction for the first time at 105 qubits. In April 2026, Project Eleven awarded its Q-Day Prize to an independent researcher who broke a 15-bit ECC key on public cloud quantum hardware, searching a space of 32,767 possibilities. That is nowhere near a 256-bit key, but the fact that it was done on cloud infrastructure rather than a national lab or dedicated chip suggests progress is shifting from a physics problem toward an engineering one.

## The real near-term risk is public keys already exposed

There is a risk that predates any working quantum computer. Classic harvest-now-decrypt-later (HNDL) attacks collect encrypted data now to decrypt later. On a blockchain, the public key itself is already permanently recorded on the ledger. Addresses with exposed public keys have effectively already been harvested; an attacker only needs to wait for Q-day.

Bitcoin address types differ in whether they expose a public key at all.

| Address type | What is recorded on-chain | Public key always exposed |
|---|---|---|
| P2PK, P2MS | The public key itself | Yes, always |
| P2PKH / P2WPKH | Hash of the public key (HASH160) | No, until first spend; permanently after reuse |
| P2SH / P2WSH | Hash of a script | Only when the script reveals a key |
| P2TR (Taproot) | Tweaked 32-byte public key | Yes, for key-path spends |

Taproot is the newest address format, but because it stores the tweaked public key directly in the script without a hash layer, the Google paper explicitly calls this a "security regression" back to P2PK-level exposure from a quantum security standpoint.

A March 2026 joint whitepaper from ARK Invest and Unchained, "Bitcoin and Quantum Computing," put the total exposed supply at about 34.6% (roughly 6.9 million BTC). Of that, about 1.7 million BTC (8.6%) sits in Satoshi-era P2PK addresses with no known private key holder, presumed lost and effectively unmovable. The remaining roughly 5 million BTC comes from reused addresses that could still be moved if their holders act. Estimates vary by source: Chaincode Labs put reused-key exposure as high as 6.26 million BTC, while Ledger Donjon estimated about 25% by value.

Attack timing splits into two categories. Public keys that are always exposed, P2PK and reused addresses, are "at-rest" targets where an attacker faces no time pressure. Hash-type addresses only expose their public key briefly, inside the signature broadcast to the mempool at spend time, an "on-spend" attack that requires recovering the private key and redirecting funds before the next block confirms (about 10 minutes on average). The Google paper modeled a roughly 41% success probability under ideal conditions (a single-signature P2WPKH spend, 9-minute key recovery, instant syndication). Faster chains cut that probability sharply: under 3% for Litecoin (2.5-minute blocks), under 1 in 1,300 for Zcash (75 seconds), under 1 in 8,000 for Dogecoin (1 minute).

## The post-quantum crypto standards already exist

The cryptography side of the homework is largely done. NIST finalized its post-quantum cryptography (PQC) standards on August 13, 2024, after an eight-year standardization process.

- **FIPS 203 (ML-KEM, formerly Kyber)**: lattice-based key exchange, a key encapsulation mechanism rather than a signature scheme.
- **FIPS 204 (ML-DSA, formerly Dilithium)**: lattice-based general-purpose signatures, about 2,420 bytes for ML-DSA-44, and stateless, meaning it is safe to sign multiple messages with the same key, making it well-suited for wallets.
- **FIPS 205 (SLH-DSA, formerly SPHINCS+)**: hash-based signatures, up to roughly 49 KB, considered a conservative fallback in case lattice-based schemes are broken later.
- **FIPS 206 (FN-DSA, formerly Falcon, expected 2027)**: NTRU lattice-based, the smallest signatures at about 666 bytes, but its floating-point implementation is difficult to get right and carries side-channel risk without a well-vetted library.

Bolting these onto a blockchain involves real tradeoffs. ECDSA signatures run 64 to 72 bytes; ML-DSA-44 is 40 to 50 times larger, and SLH-DSA can be hundreds of times larger, both with direct implications for block space and gas costs. Stateful hash-based signatures like XMSS leak the private key if the same key signs twice, which conflicts badly with the UTXO model and wallet backup restoration. That is why stateless ML-DSA is the leading candidate for wallets, while XMSS-family schemes remain viable for consensus-layer contexts like validator keys where state can be tightly managed. Research into STARK-based signature aggregation is also underway to ease the size problem.

## Two different migration paths

**Bitcoin's path runs through BIP-360.** Hunter Beast proposed it in June 2024. It originally tried to bundle PQC signatures directly, but that piece was split off into a separate future BIP to keep the debates independent. The current form is P2MR (Pay-to-Merkle-Root, renamed from P2TSH in February 2026), which removes Taproot's quantum-vulnerable key-path spend using SegWit v2 and a bc1z prefix. It merged into the official Bitcoin repository on February 11, 2026, though no activation timeline has been set.

The more contentious proposal is BIP-361 (Post Quantum Migration and Legacy Signature Sunset), submitted April 14, 2026 by Jameson Lopp and five co-authors. It defines three phases: block new transfers into legacy addresses about three years after activation (Phase A), fully invalidate legacy signatures about five years after activation, permanently freezing un-migrated coins (Phase B), and open a zero-knowledge-proof remedy for holders who can present their seed phrase (Phase C). The debate is sharp. Lopp argues he would rather freeze more than 5.5 million dormant BTC than let hackers steal it; Binance founder CZ proposed in June 2026 freezing Satoshi's roughly 1.1 million BTC after a 6-to-12-month migration window. Opponents call it a violation of permissionless system principles. This is a head-on collision between absolute property rights and network security, and as of July 2026 there is neither consensus nor an activation timeline.

**Ethereum's path is comparatively clear**, largely because account abstraction (ERC-4337, EIP-7702) already gives it flexibility to swap signature schemes. In January 2026, the Ethereum Foundation designated post-quantum cryptography a top strategic priority and put up a $2 million research prize. In March, the pq.ethereum.org hub launched, with more than ten client teams running weekly interoperability devnets. On the consensus layer, work is underway to replace validators' BLS signatures with hash-based leanXMSS. On the execution layer, proposals like EIP-8141 (allowing arbitrary signature schemes) and EIP-7851 (permanently disabling legacy ECDSA keys after migration) are under discussion. Priority order runs from user accounts (EOAs, the largest pool of value, exposed after first transaction), to exchange/bridge/custody hot wallets, to governance keys, to validator keys. Justin Drake has cited 2030 as a target for Ethereum reaching post-quantum security.

Other chains are moving on their own timelines. QRL has been the first post-quantum chain since 2018, using hash-based XMSS exclusively. Algorand has protected its infrastructure with Falcon-based State Proofs since 2022, though account signatures still use classical Ed25519. Ripple targets 2028, and Solana is exploring optional primitives like Winternitz Vault.

## Rushing the transition may be riskier than waiting

Dan Boneh, a Stanford cryptographer and co-author of the Google paper, delivered a counterintuitive message in a May 2026 interview: a rushed post-quantum transition is more likely to introduce a critical bug than a quantum computer is to break the underlying cryptography. His reasoning rests on the different risk profiles of encryption and signatures. Encryption needs to migrate now because of HNDL risk. Signatures face no such time pressure, so caution beats haste. He advocates hybrid signatures, combining existing ECC with PQC, as a gradual transition path, and rates a CRQC (cryptographically relevant quantum computer) before 2035 as "possible but improbable given current funding levels." a16z crypto has made a similar argument: PQC encryption should deploy immediately because of HNDL, but PQ signatures warrant a careful, non-immediate migration given their size, performance, and implementation-maturity concerns, since a hasty move risks locking into a suboptimal scheme or requiring a second migration after a bug surfaces.

Past Bitcoin protocol upgrades like SegWit and Taproot suggest a full transition typically takes five to seven years. Even an emergency response to a sudden quantum breakthrough would likely need around two years.

## What developers should do now

There is no imminent threat, but preparing now makes the eventual transition much smoother.

1. **Minimize public key exposure.** Enforce address-reuse prevention in code and UX, and avoid exposing HD wallet xpubs. For Bitcoin, design around P2WPKH (bc1q) and be cautious about Taproot (bc1p) key-path exposure.
2. **Build crypto-agility.** Abstract signature verification logic so algorithms can be swapped later. On Ethereum, account abstraction via ERC-4337/EIP-7702 gives you a head start on a signature-scheme migration path.
3. **Track the signals that matter.** BIP-360/BIP-361 governance debates, progress on pq.ethereum.org devnets, NIST finalizing FIPS 206 (Falcon), IBM's Starling (targeted 2029) and Quantinuum's (targeted 2030) hardware milestones, and follow-up challenges to the Project Eleven Q-Day Prize.
4. **Consider hybrid signatures for the medium term.** Combining existing ECC with PQC reduces both single-scheme lock-in and implementation-bug risk. Stateless ML-DSA is a reasonable default for wallets; FN-DSA (Falcon) is worth evaluating where signature size is tightly constrained, provided you use a well-vetted library.
5. **Plan for mempool-window attacks.** If your design exposes a public key at spend time, look into private mempools or commit-reveal schemes, which the Google paper also recommends.

## Separating hype from substance

A few caveats are easy to lose in the coverage of this topic.

A CRQC does not exist yet. The paper's "9 minutes, under 500,000 qubits" is a resource estimate for scaling up a demonstrated platform, not a demonstrated capability. The circuit itself remains undisclosed for responsible-disclosure reasons, and its cost has only been verified via zero-knowledge proofs. Headlines claiming "Bitcoin collapses in 9 minutes" dress up an estimate for a machine that does not exist as established fact.

Timeline estimates span a wide range. Adam Back puts it at 20 to 40 years (median in the mid-to-late 2030s), while Justin Drake estimates at least a 10% probability of recovering a secp256k1 private key from an exposed public key by 2032, and Vitalik Buterin puts the probability before 2030 at 20%. An independent June 2026 study, "Quantum Horizon," ran a Monte Carlo forecast putting the probability of CRQC arrival at about 1 in 6 by 2035, roughly 30% by 2040, and about 60% by 2050. Claims that pin down a specific year are, more often than not, overstated.

It is also worth remembering that most of the cryptography and engineering homework is already done, as QRL and Algorand demonstrate in production. The genuinely hard problem left is deployment and governance, particularly in a system like Bitcoin's emergent consensus, which has no formal voting mechanism to coordinate a large-scale migration.

## Wrapping up

As of July 2026, a quantum-driven collapse of Bitcoin or Ethereum is not a viable near-term threat. The gap between available hardware and what an attack would require is still hundreds of times wide. But algorithmic progress has closed that gap faster than hardware has advanced, and the fact remains that nearly 6.9 million BTC sit with exposed public keys today. NIST standards exist, and Ethereum has a migration path through account abstraction, but Bitcoin's governance debate shows that social consensus can be harder than the technical problem itself. The most practical thing developers can do right now is avoid public key reuse, build in the flexibility to swap signature schemes later, and keep watching the standards and governance discussions rather than rushing to act.

## References

- [Securing Elliptic Curve Cryptocurrencies against Quantum Vulnerabilities](https://arxiv.org/abs/2603.28846), Babbush, Zalcman, Gidney, et al., arXiv:2603.28846, accessed 2026-07-05
- [How to factor 2048 bit RSA integers with fewer than one million noisy qubits](https://arxiv.org/abs/2505.15917), Craig Gidney, arXiv:2505.15917, accessed 2026-07-05
- [FIPS 203, 204, 205](https://csrc.nist.gov/pubs/fips/203/final), NIST, finalized August 13, 2024
- [BIP-360](https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki), Hunter Beast, Ethan Heilman, Isabel Foxen Duke, official Bitcoin BIPs repository
- [pq.ethereum.org](https://pq.ethereum.org/), Ethereum Foundation post-quantum roadmap hub
- [Project Eleven Q-Day Prize](https://www.prnewswire.com/news-releases/project-eleven-awards-1-btc-q-day-prize-for-largest-quantum-attack-on-elliptic-curve-cryptography-to-date-302752439.html), announcement of the 15-bit ECC key demonstration on public quantum hardware
