---
title: "Bitcoin, Ethereum, and the Quantum Computing Question"
meta_title: ""
description: "A March 2026 paper from Google, the Ethereum Foundation, and Stanford cut the qubit budget for attacking secp256k1 dramatically. Here is what changed, what did not, and what developers should do now."
date: 2026-07-05T23:37:01+09:00
lastmod: 2026-07-06T00:09:52+09:00
image: ""
categories: ["Blockchain"]
tags: ["bitcoin", "ethereum", "quantum-computing", "post-quantum-cryptography", "cryptography"]
author: "whackur"
translationKey: "bitcoin-ethereum-quantum-computing-risk"
draft: false
---

On March 30, 2026, a joint paper from Google Quantum AI, the Ethereum Foundation, and Stanford shook up the crypto community. It estimated that the physical qubit count needed to recover a private key on secp256k1 (the elliptic curve behind Bitcoin and Ethereum signatures) had dropped nearly 20x from the previous best estimate. A threat that used to sound like "millions of qubits, decades away" now reads as "under 500,000, maybe within this decade."

That does not mean wallets get drained tomorrow. As of June 2026, the strongest quantum hardware sits around 2,500 physical qubits, still hundreds of times short of what an attack would require. But algorithmic progress has been closing that gap faster than hardware has, and millions of coins already sit with their public keys exposed on-chain. Both facts are reasons for blockchain developers to start paying attention now. This post works through the research and proposals from the past few months to separate the real risk from the hype.

## Key findings

- **No collapse today.** Breaking secp256k1 needs under 500,000 physical qubits (1,200 to 1,450 logical qubits), while the best current hardware sits around 2,500. The gap is still hundreds of times wide. That requirement, however, has fallen sharply from 2017-era estimates through algorithmic improvements alone.
- **Timeline estimates have compressed fast, but the range stays wide.** Expert estimates run from Adam Back's 20 to 40 years, to Justin Drake's "at least 10% probability of recovering a secp256k1 private key from an exposed public key by 2032," to Vitalik Buterin's "20% probability before 2030." Governments and industry are treating 2029 to 2035 as the migration deadline.
- **The near-term risk that matters is public keys already exposed.** About 6.9 million BTC (34.6% of total supply) sit in addresses with public keys visible on-chain, per the March 2026 ARK Invest and Unchained joint whitepaper. Of that, roughly 1.7 million BTC (8.6%) sit in unmovable Satoshi-era P2PK addresses. What developers can do now: stop reusing public keys, build crypto-agility, and track BIP-360 and Ethereum's account-abstraction roadmap.

## The quantum attack on ECDSA signatures

ECDSA, the signature scheme behind Bitcoin and Ethereum, depends on the elliptic curve discrete logarithm problem (ECDLP). The public key is computed as `Q = d·G`, where `G` is a fixed base point on the curve and `d` is the private scalar. Given `Q` and `G`, recovering `d` is effectively impossible for a classical computer. Unlike division, the inverse of multiplication, this is a problem of retracing how many times a point addition was repeated on the curve.

Shor's algorithm attacks this structure directly. Using a quantum Fourier transform to find the period of a specific function, it solves ECDLP in polynomial time. Once the discrete log problem falls, the private key follows directly from the public key. This affects ECDSA on secp256k1 and Schnorr signatures (Bitcoin Taproot) equally, since both rely on the same discrete-log assumption on the same curve. Whether the scheme is ECDSA or Schnorr does not matter; as long as the curve is secp256k1, both stand in the same position against Shor's algorithm.

Bitcoin mining, which relies on the SHA-256 hash function, is a different story entirely. Hash functions do not rest on an algebraic structure like a discrete logarithm; they are closer to an unstructured search problem, which puts them in Grover's algorithm's territory instead of Shor's. And Grover's algorithm has a fundamental ceiling: it only offers a quadratic speedup.

## Grover's algorithm and the safety margin on hash functions

Grover's algorithm gives a quadratic speedup over an unstructured search space. SHA-256's preimage resistance drops in theory from 2^256 to 2^128. That is still an astronomically large number and not a practical threat. Bitcoin's address hash, HASH160 (SHA-256 layered on RIPEMD-160), has the thinnest margin, dropping from 160 bits to 80 bits, but that margin only matters in the specific case where address reuse exposes additional hash preimages.

The real picture is worse than this simple calculation suggests. A fault-tolerant SHA-256 preimage attack has been estimated to require roughly 2^166 logical-qubit-cycles, up to 275 billion times more expensive than a naive query-count analysis implies. Error-correction overhead eats up most of Grover's theoretical gain.

That is also why there is effectively no quantum threat to proof-of-work mining, for two reasons. First, Grover's quadratic gain is mostly consumed by quantum error-correction overhead. Second, Grover parallelizes poorly, while Bitcoin mining is built for massive parallelization and dedicated hardware (ASIC) acceleration. On top of that, the difficulty retarget every 2,016 blocks would quickly absorb any speed advantage a quantum miner might briefly hold. The idea that "quantum computers will take over mining" is closer to a misconception; some estimates put the physical qubits needed for a SHA-256 attack at around 10^23, a resource scale approaching the energy output of a star.

That narrows the real threat down to one thing: the ECDLP problem shared by ECDSA and Schnorr signatures.

## Logical qubits, physical qubits, and the error-correction wall

The qubits in today's quantum hardware are noisy and error-prone. Practical computation requires bundling many physical qubits together into a single error-suppressed logical qubit. The surface code is the leading method for this: it arranges physical qubits in a lattice and repeatedly detects and corrects errors, suppressing the logical error rate exponentially.

There is one condition that has to hold: the physical error rate must sit below a certain threshold. Below that threshold, bundling more qubits together reduces the logical error rate. Above it, adding more qubits does not help at all.

Breaking secp256k1 needs about 1,200 to 1,450 logical qubits, but once the surface code's overhead is factored in, the physical qubit requirement jumps to under 500,000. That gap, the number of physical qubits needed to build one logical qubit, is the "error-correction overhead." The Google, Ethereum Foundation, and Stanford paper assumed a physical error rate of 10^-3, degree-4 planar connectivity (each qubit connected only to its four neighbors), a 1-microsecond cycle time, and a 10-microsecond control response time for this calculation.

More aggressive assumptions exist too. Using degree-7 qLDPC (quantum low-density parity-check) codes, which rely on non-local connectivity beyond the plane, could push the physical qubit requirement below 100,000. But that level of qubit-to-qubit connectivity has not been demonstrated in real hardware yet. That is why the paper adopted the validated planar degree-4 connectivity and the 500,000-qubit estimate as "the better-understood, more achievable engineering path."

## The fast decline in resource estimates

Assume the same hardware, and better algorithms alone shrink the resource requirement. Tracking this timeline shows how fast the compression has been.

- **2017 (Microsoft Research, Roetteler et al.)**: proposed a formula requiring `9n + 2⌈log₂n⌉ + 10` logical qubits and `448n³log₂n + 4090n³` Toffoli gates for an n-bit prime field curve. Applied to a P-256-class curve, that works out to about 2,330 logical qubits and about 126 billion Toffoli gates. It also reconfirmed a 2003 result from Proos and Zalka: elliptic curve cryptography is an easier quantum target than RSA at an equivalent classical security level.
- **2023 (Litinski)**: assuming a photonic architecture, about 9 million physical qubits and about 200 million Toffoli gates for a single instance.
- **March 2026 (Google, Ethereum Foundation, Stanford, arXiv:2603.28846)**: presented two circuit variants. The low-qubit variant uses up to 1,200 logical qubits and up to 90 million Toffoli gates; the low-gate variant uses up to 1,450 logical qubits and up to 70 million Toffoli gates. Under the surface-code conditions described above (10^-3 physical error rate, degree-4 connectivity, 1-microsecond cycle), both variants converge to under 500,000 physical qubits. Compared with Litinski's 2023 estimate, that is roughly a 20x drop in physical qubits and a 10x drop in total computation (spacetime volume).

The number that drew the most attention from this paper is an average of 9 minutes to recover a private key after a public key is exposed. That comes with a caveat. The raw circuit, run without priming, processes 70 to 90 million Toffoli gates and takes 18 to 23 minutes. Priming, precomputing the first half of the algorithm ahead of time, cuts the post-exposure time roughly in half, down to about 9 minutes (sometimes 12). The paper frames this as "a first-generation fast-clock CRQC could solve secp256k1 ECDLP in about 9 minutes on average," a number that matters because it sits close to Bitcoin's average block time of 10 minutes.

One more condition worth noting: this figure is a single-instance estimate. It assumes a machine dedicated entirely to attacking one key at a time, and deliberately excludes batch optimization. Attacking multiple keys at once would require multiple primed machines; running 11 of them in parallel, for instance, could give roughly a 6.5x speedup.

Craig Gidney, from the same research circle, lowered the qubit budget for factoring RSA-2048 to under 1 million in May 2025 (arXiv:2505.15917), a 20x reduction from his own 2019 estimate of 20 million qubits. He combined three innovations, approximate residue arithmetic, the yoked surface code, and magic state cultivation, to cut the Toffoli gate count by more than 100x compared with prior work. Both papers point to the same pattern: attacks always get better. RSA-2048's physical qubit estimate has dropped roughly 20x with each new paper.

## How far hardware and roadmaps have come

The pace at which resource estimates are shrinking is one thing; actual hardware catching up is another.

**Google's Willow chip (December 2024)** demonstrated below-threshold error correction for the first time, using 105 qubits. The logical error rate halved each time the lattice scaled up, from 3x3 to 5x5 to 7x7, with an error-suppression factor of Λ=2.14±0.02. On a distance-7 code, the per-cycle logical error rate dropped to 0.143%±0.003%. Real-time decoding and "beyond break-even" performance, where a logical qubit's lifetime reached 2.4x that of its individual physical qubits, were both demonstrated for the first time here as well.

**IBM**, separately from Willow, published in Nature in 2024 that qLDPC-family bivariate bicycle codes could cut physical qubit overhead by about 90%. Its roadmap runs through Loon (2025), Kookaburra (2026), and Cockatoo (2027), reaching Starling in 2029 (200 logical qubits, 100 million gates) and Blue Jay in 2033 (2,000 logical qubits, 1 billion gates). IBM has also set a goal of reaching quantum advantage within 2026.

**Quantinuum** is pursuing a trapped-ion approach targeting full fault tolerance around 2030, and demonstrated 12 logical qubits in collaboration with Microsoft in 2024.

Separate from these roadmaps, there is already a case of publicly available hardware breaking a discrete-log problem. **On April 24, 2026, Project Eleven** awarded its Q-Day Prize (1 BTC) to independent researcher Giancarlo Lelli, who ran a variant of Shor's algorithm on publicly accessible cloud quantum hardware to break a 15-bit ECC key (a search space of 32,767 possibilities) and derive the private key from the public key. That is a 512x jump from the previous record of 6 bits, set in September 2025.

It would be a stretch to compare this demonstration directly against 256-bit secp256k1. Shor circuit size scales roughly with bit count, so a massive hardware gap remains between 15 bits and 256 bits. Still, it is worth noting that this result came from commercial cloud infrastructure rather than a national lab or dedicated equipment. Project Eleven CEO Alex Pruden put it plainly: "This wasn't a national lab. It wasn't a custom chip." That reads as a signal that progress is shifting from a physics problem toward an engineering one.

## The real near-term risk is public keys already exposed

There is a risk that predates the existence of a working quantum computer. The classic harvest-now-decrypt-later (HNDL) attack collects encrypted data now to decrypt it later. On a blockchain, the risk goes one step further: the public key itself is already permanently recorded on the ledger. Addresses with exposed public keys have effectively already been harvested; an attacker only needs to wait for Q-Day. A Federal Reserve working paper treats Bitcoin as an HNDL case study and points out that even after a switch to post-quantum signatures, the data privacy of past transactions already on the ledger remains vulnerable.

Bitcoin address types differ in whether they expose a public key at all.

| Address type | What gets recorded on-chain | Public key always exposed |
|---|---|---|
| P2PK, P2MS | The public key itself | Yes, always |
| P2PKH / P2WPKH | Hash of the public key (HASH160) | No, until first spend; permanently after reuse |
| P2SH / P2WSH | Hash of a script | Only when the script reveals a key |
| P2TR (Taproot) | Tweaked 32-byte public key | Yes, for key-path spends |

Taproot is the newest address format, but because it stores the tweaked public key directly in the script without a hash layer, it is actually a step backward from a quantum-security standpoint. The Google paper explicitly calls this a "security regression" back to P2PK-level exposure.

The **March 2026 joint whitepaper from ARK Invest and Unchained, "Bitcoin and Quantum Computing,"** puts the total exposed supply at about 34.6%, roughly 6.9 million BTC. That breaks down as follows:

- About 1.7 million BTC (8.6%): Satoshi-era P2PK addresses, including early miners and Satoshi's own estimated holdings (about 1.1 million BTC). Presumed to have no surviving private key holder and so effectively unmovable.
- About 5 million BTC (25%): reused addresses that could still be moved today if their holders act.
- About 200,000 BTC (1%): P2TR (Taproot) addresses.
- The remaining roughly 65% sits in address types that have not yet exposed a public key.

Estimates vary by source. A 2025 Chaincode Labs study put reused-key exposure as high as 6.26 million BTC, while Ledger Donjon estimated about 25% by value. The methodologies differ, but the Google paper and Project Eleven both converge on a figure near 6.9 million BTC.

Attack timing splits into two categories. Public keys that stay exposed permanently, P2PK, reused addresses, and Taproot, are "at-rest" targets, where an attacker faces no time pressure at all. Hash-type addresses only expose their public key briefly, inside the signature broadcast to the mempool at spend time, an "on-spend" attack that requires recovering the private key and redirecting funds before the next block confirms (about 10 minutes on average). Block mining is a Poisson process with a mean and standard deviation both around 10 minutes, so the Google paper modeled a roughly 41% success probability under ideal conditions (a single-signature P2WPKH spend, 9-minute key recovery, instant public-key propagation, no mempool congestion). Faster chains cut that probability sharply: under 3% for Litecoin (2.5-minute blocks), under 1 in 1,300 for Zcash (75 seconds), under 1 in 8,000 for Dogecoin (1 minute). This does not favor defenders unconditionally, though. The paper notes that with a high enough fee, or during a period of low congestion, any transaction looks practically safe if an attacker cannot break it within 30 minutes to an hour, but it also points out that an attacker could flood the mempool with high-fee transactions to buy more time.

## The post-quantum crypto standards already exist

The cryptography side of this problem is largely solved. NIST finalized its post-quantum cryptography (PQC) standards on August 13, 2024, closing out an eight-year standardization process.

| Standard | Algorithm | Basis | Signature/key size | Notes |
|---|---|---|---|---|
| FIPS 203 | ML-KEM (formerly Kyber) | Lattice (MLWE) | Key encapsulation, not a signature | For key exchange |
| FIPS 204 | ML-DSA (formerly Dilithium) | Lattice (MLWE/MSIS) | ML-DSA-44 about 2,420 bytes | General purpose, stateless, signs in about 0.65ms |
| FIPS 205 | SLH-DSA (formerly SPHINCS+) | Hash-based | Up to about 49 KB | Conservative fallback in case lattice schemes break |
| FIPS 206 (draft, expected 2027) | FN-DSA (formerly Falcon) | NTRU lattice | FN-DSA-512 about 666 bytes | Smallest signatures, but floating-point implementation is difficult and carries side-channel risk |

Bolting these onto a blockchain involves real tradeoffs. ECDSA signatures run 64 to 72 bytes; ML-DSA-44 is 40 to 50 times larger, and SLH-DSA can run hundreds of times larger. Both have a direct impact on block space and gas costs.

State management is another obstacle. Stateful hash-based signatures like XMSS leak the private key if the same key signs twice, which conflicts badly with the UTXO model, address reuse, and wallet backup restoration. XMSS's underlying component, WOTS (Winternitz One-Time Signature), is safe for exactly one signature per key by design, which makes it a poor fit for wallets, where controlling exactly when and how often a key signs is hard. That is why stateless ML-DSA is the leading candidate for wallets, while XMSS-family schemes remain a viable option for consensus-layer contexts like validator keys, where state can be tightly managed.

Research is also underway to ease the signature-size problem: STARK-based signature aggregation, which compresses multiple signatures into a single proof, and precompiles for vector arithmetic operations that lower the verification cost itself.

## Bitcoin's migration path

**BIP-360** was proposed by Hunter Beast in June 2024. Its initial form, P2QRH, tried to introduce PQC signatures directly, but that piece was split off into a separate future BIP to keep the debates independent. Its current form is P2MR (Pay-to-Merkle-Root), renamed from P2TSH on February 10, 2026, which removes Taproot's quantum-vulnerable key-path spend. It uses a SegWit v2 structure with a bc1z prefix (Bech32m) and commits to a 32-byte script-tree merkle root, giving it the same 128-bit collision resistance and 256-bit preimage resistance as P2WSH. It merged into the official Bitcoin repository on February 11, 2026, and was assigned a BIP number, but no activation timeline has been set; it remains in draft form. The PQ signature piece is managed separately, as a plan to redefine OP_SUCCESSx into opcodes like OP_CHECKMLSIG to add ML-DSA and SLH-DSA to tapscript. It is included only as an informational plan and could activate independently. One point of contention: hash-based signatures (WOTS/Lamport) are one-time-use, which risks signing twice with the same key during common practices like RBF (fee replacement) or CPFP (child-pays-for-parent). That is part of why stateless schemes are preferred.

The more contentious proposal is **BIP-361 (Post Quantum Migration and Legacy Signature Sunset)**, submitted on April 14, 2026 by Jameson Lopp (Casa co-founder and CSO) and five co-authors to the official Bitcoin proposal repository. It defines three phases:

- **Phase A** (about 3 years after activation): bans new transfers into legacy addresses.
- **Phase B** (about 5 years): fully invalidates legacy ECDSA and Schnorr signatures, permanently freezing coins that were not migrated in time.
- **Phase C**: opens a zero-knowledge-proof remedy mechanism for holders who can present their seed phrase.

The BIP-361 document itself states that, as of March 1, 2026, more than 34% of all Bitcoin has its public key exposed on-chain. The community has split three ways: freeze at the protocol level (the BIP-361 position), accept the quantum theft risk and do nothing ("code is law"), or route around the problem with a legal trust model (an approach proposed by investor Nic Carter). Lopp argues he would rather freeze more than 5.5 million dormant BTC than let hackers steal it. Binance founder CZ proposed on a June 18, 2026 podcast freezing Satoshi's roughly 1.1 million BTC after a 6-to-12-month migration window. On the other side, Bitcoin Magazine editor Brian Trollz, TFTC founder Marty Bent, Metaplanet's Phil Geiger, and investor Michael Terpin, among others, object strongly, calling it a violation of permissionless-system principles. Bitwise CIO Matt Hougan backs Nic Carter's legal-trust proposal instead. This is, at bottom, a head-on collision between absolute property rights ("your keys, your coins") and network security (the trust collapse that could follow if 6.9 million BTC worth of theft hit the market), and as of July 2026 there is neither consensus nor an activation timeline. Grayscale's head of research described this as "a social problem more than a technical one."

Past protocol upgrades offer some guidance on timing. SegWit took from 2015 to 2017, and Taproot took years to activate despite broad conceptual support. Based on that history, a full post-quantum transition is generally estimated to take five to seven years, and even an emergency response to a sudden quantum breakthrough would likely need around two years. Bitcoin's emergent consensus structure, which has no formal voting procedure or central leadership, is the fundamental constraint on that timeline.

## Ethereum's post-quantum roadmap

Ethereum already has a flexible way to swap signature schemes, thanks to account abstraction (ERC-4337, EIP-7702), which gives it a much clearer migration path than Bitcoin.

In January 2026, the Ethereum Foundation designated post-quantum cryptography a "top strategic priority" and put up a $2 million research prize for practical migration solutions. On March 24-25, 2026, the **pq.ethereum.org** hub launched, and more than ten client teams now run weekly post-quantum interoperability devnets. What started as STARK-based signature-aggregation research back in 2018 has grown into a multi-team open-source project. In February 2026, Vitalik Buterin identified four vulnerable areas in the roadmap.

On the **consensus layer**, work is underway to replace validators' BLS signatures (which depend on elliptic-curve pairing) with hash-based **leanXMSS**. That effort consists of leanSig (a Rust implementation), leanMultisig (a minimal zkVM for signature aggregation), and leanSpec (a Python specification referenced by about ten client teams). leanSig is based on XMSS and Winternitz (WOTS+), optimized for SNARK verification, and designed for an 8-year key lifetime. WOTS+, using the w=16 parameter, signs a single message using 64 hash chains plus 3 checksum chains, 67 chains in total.

On the **execution layer**, account abstraction (ERC-4337, EIP-7702) is the core strategy, aiming to support gradual opt-in migration without a separate "flag day," using a vector-arithmetic precompile for PQ signature verification. EIP-8141 (a Hegotá candidate proposal) moves toward allowing arbitrary signature schemes, while EIP-7851 permanently disables an account's legacy ECDSA private key once it has migrated via EIP-7702, with the precompile adding a marker byte and a 7-day cancellation window. Candidate schemes under evaluation include Falcon, Dilithium, and SPHINCS+.

The priority order is clear: (1) user accounts (EOAs), which hold the largest pool of value and expose their public key after the first transaction; (2) exchange, bridge, and custody hot wallets; (3) governance and upgrade keys (admin multisigs); (4) validator keys. **Lean Ethereum** is aiming to move away from every node re-executing every transaction, toward recursive STARK verification instead. STARKs depend only on hash functions, which makes them quantum-resistant by design. Quantum-safe blob design has already been in progress for months, as part of the broader "The Splurge" roadmap that also covers consensus redesign (1-to-2-round finality), multidimensional gas pricing, and a new state architecture. Justin Drake has cited 2030 as a target date for Ethereum to reach post-quantum security.

## How other chains are responding

- **QRL (Quantum Resistant Ledger)** has been the first purpose-built post-quantum chain since 2018, using only hash-based XMSS (a NIST-approved scheme) as its signature method. QRL 2.0 is preparing EVM compatibility alongside a stateless SPHINCS+ testnet, and it is frequently cited as proof that "the engineering is already solved; adoption is the remaining problem."
- **Algorand** has protected part of its infrastructure with Falcon-based State Proofs (signing its history every 256 blocks) since September 2022. Account signatures still run on classical Ed25519, though, so this protection covers the infrastructure layer, not user funds directly. Its 2026 roadmap includes native Falcon verification and hard-fork-free on-chain voting.
- **Ripple/XRP** targets full quantum resistance by 2028 through a four-phase plan. It is running ML-DSA signatures on AlphaNet test instances and collaborating with Project Eleven on validator testing.
- **Solana** is evaluating Winternitz Vault, a WOTS-based optional primitive (a SIMD proposal). Each vault transaction generates a one-time Winternitz keypair and derives a PDA (Program-Derived Address) from a Keccak-256 hash truncated to 224 bits. The protocol layer itself still runs on Ed25519 and is not quantum-safe. A Dilithium testnet ran in December 2025, and the Anza and Firedancer teams are researching a Falcon migration.
- **Zcash** is inherently quantum-resistant because its STARK-based structure depends only on hash functions, and its Tachyon upgrade strengthens that direction further.

## Rushing the transition may be riskier than waiting

Dan Boneh, a Stanford cryptographer and co-author of the Google paper, delivered a counterintuitive message in a May 25, 2026 interview with Isabel Foxen Duke: a rushed post-quantum transition is more likely to introduce a critical bug than a quantum computer is to break the underlying cryptography. His reasoning starts from the fact that encryption and signatures carry different risk profiles. Encryption needs to migrate now, because of HNDL risk: data collected today can be decrypted later once a quantum computer exists. Signatures do not face that same time pressure; a signature made today is not threatened by a future quantum computer the way encrypted data is, so caution wins out over haste.

Boneh advocates **hybrid signatures**, combining existing ECC with PQC, as a way to transition gradually. He rated the odds of a CRQC (a cryptographically relevant quantum computer, one powerful enough to matter) appearing before 2035 as "possible but improbable given current funding levels," and called an appearance within this decade "very aggressive." His summary: "Don't panic, but don't ignore it either." As for claims that Bitcoin will not survive this transition, he called that "nonsense."

a16z crypto makes a similar case. PQC encryption should deploy immediately because of HNDL risk, but PQ signatures call for a careful, non-immediate migration, given open questions around size, performance, and implementation maturity. Research into aggregatable signatures and post-quantum SNARKs still needs several more years to mature, and moving too fast risks locking into a suboptimal scheme, or needing a second migration later after an implementation bug surfaces.

## Q-Day scenarios and the signals worth watching

Experts generally split Q-Day, the moment a CRQC actually appears, into two scenarios.

In the **gradual scenario**, hardware develops on roughly its current roadmap, migration keeps pace ahead of it, and the transition gets absorbed without major disruption. Chains with a clear path, like Ethereum's account abstraction, are well positioned for this outcome.

In the **abrupt scenario**, an earlier-than-expected quantum breakthrough collides with an incomplete migration. In that case, market panic is likely to arrive before any actual theft of funds. Lopp warns that even just credible evidence that someone can recover coins with a quantum computer would trigger an immediate market-wide panic. The Google paper offers a concrete example of the stakes: a fast-clock CRQC could break Ethereum's top 1,000 highest-value accounts, holding roughly 20.5 million ETH between them, within 9 days.

There are three concrete signals that would mean it is time to shift from preparation to execution: public quantum hardware demonstrating a break of an ECC key between 100 and 256 bits (the current record is 15 bits); real hardware approaching 1,000 logical qubits; or IBM's Starling (targeted for 2029) or a competitor reaching 200 or more logical qubits on schedule. If any one of these becomes reality, migration needs to move from "preparing" to "executing."

## What developers should do now

There is no imminent threat, but preparing now makes the eventual transition much smoother.

1. **Minimize public key exposure.** Enforce address-reuse prevention in code and UX, and avoid exposing HD wallet xpubs. For Bitcoin, design around P2WPKH (bc1q) and be cautious about Taproot's (bc1p) key-path exposure. This lines up with the user-facing recommendations in the Google paper itself.
2. **Build crypto-agility.** Abstract your signature verification logic so the underlying algorithm can be swapped later without a rewrite. On Ethereum, account abstraction via ERC-4337/EIP-7702 gives you a head start on a signature-scheme migration path.
3. **Track the signals that matter.** Watch the BIP-360/BIP-361 governance debate, progress on pq.ethereum.org devnets, NIST finalizing FIPS 206 (Falcon, expected 2027), IBM's Starling (targeted 2029) and Quantinuum's (targeted 2030) hardware milestones, and any follow-up challenges to the Project Eleven Q-Day Prize (which could plausibly expand toward combining AI with quantum cryptanalysis).
4. **Consider hybrid signatures for the medium term.** Combining existing ECC with PQC reduces both single-scheme lock-in and implementation-bug risk. Stateless ML-DSA (FIPS 204) is a reasonable default for wallets; FN-DSA (Falcon) is worth evaluating where signature size is tightly constrained, provided you use a well-vetted library; XMSS and leanXMSS remain sensible where state can be tightly managed, such as consensus-layer validator keys.
5. **Plan for mempool-window attacks.** If your design exposes a public key briefly at spend time, look into private mempools or commit-reveal schemes, which the Google paper also recommends.
6. **Watch STARK-based aggregation for the signature-size problem.** Techniques that bundle multiple signatures into one, along with vector-arithmetic precompiles, are a practical way to ease the pressure on block space and gas costs.

## Separating hype from substance

A few premises are easy to lose when this topic gets covered in the press.

**A CRQC does not exist yet.** The paper's "9 minutes, under 500,000 qubits" is a resource estimate for scaling up an already-demonstrated platform, not a demonstrated capability in itself. The circuit itself was not disclosed, for responsible-disclosure reasons, and its resource cost has only been verified through zero-knowledge proofs. Headlines claiming "Bitcoin collapses in 9 minutes" dress up an estimate for a machine that does not exist as established fact. The actual raw circuit, run without priming, takes 18 to 23 minutes; the 9-minute figure is an adoption assumption that presumes a primed, single, dedicated machine.

**It is also a single-instance estimate.** The paper's core numbers (1,200 to 1,450 logical qubits, 9 minutes) assume attacking one key at a time on a machine dedicated entirely to that task, and deliberately exclude batch optimization. Attacking multiple keys simultaneously would require additional primed machines.

**Timeline estimates span a wide range.** Adam Back puts it at 20 to 40 years, with a median in the mid-to-late 2030s, while Justin Drake estimates at least a 10% probability of recovering a secp256k1 private key from an exposed public key by 2032, and Vitalik Buterin puts the probability before 2030 at 20%. An independent June 2026 study, "Quantum Horizon" (Gershteyn and Alber), ran a Monte Carlo forecast and produced a bimodal distribution: about a 1-in-6 chance of CRQC arrival by 2035, roughly 30% by 2040, and about 60% by 2050. ARK Invest classified quantum computing as "Stage 0" (no commercially meaningful capability yet) as of March 2026. Claims that pin down a specific year are, more often than not, overstated.

**Market prices and technical reality should be kept separate.** Recent crypto price swings have been driven mostly by macroeconomic factors, not the quantum threat (as of July 5, 2026, ETH traded around $1,771, with the market Fear and Greed Index at 27, "Fear"). That said, quantum risk is gradually being priced in as a kind of risk premium, and if credible attack evidence emerges, market panic could well arrive before any actual technical collapse. Polymarket's odds on "will Satoshi move BTC in 2026" rose from 4.5% at the start of the year to about 9.3%, but the market's reaction to the BIP-361 announcement itself was muted, still treated as a governance-level discussion rather than an imminent risk.

**Governance is the real bottleneck.** Most of the cryptography and engineering work is already done, as QRL and Algorand demonstrate in production. The genuinely hard problem left is deployment and governance, particularly how to handle immovable legacy supply (Satoshi-era coins, for instance) in a system like Bitcoin's, which has no formal voting mechanism or emergency-response procedure to coordinate a large-scale migration.

**The mining threat is a common misconception.** The idea that "quantum computers will overwhelm Bitcoin mining" does not hold up. Grover's quadratic gain gets offset by error-correction overhead, parallelization limits, and difficulty retargeting, none of which add up to a practical threat.

## Wrapping up

As of July 2026, a quantum-driven collapse of Bitcoin or Ethereum is not a viable near-term threat. The gap between available hardware and what an attack would require is still hundreds of times wide. But algorithmic progress has closed that gap faster than hardware has advanced, and nearly 6.9 million BTC still sit with exposed public keys today. NIST's standards exist, and Ethereum has a clear migration path through account abstraction, but Bitcoin's governance debate shows that reaching social consensus can be harder than solving the technical problem itself. The most practical thing developers can do right now is avoid public key reuse, build in the flexibility to swap signature schemes later, and keep watching the standards and governance discussions rather than rushing to act.

## References

- [Securing Elliptic Curve Cryptocurrencies against Quantum Vulnerabilities](https://arxiv.org/abs/2603.28846), Babbush, Zalcman, Gidney, et al., arXiv:2603.28846, accessed 2026-07-05
- [How to factor 2048 bit RSA integers with fewer than one million noisy qubits](https://arxiv.org/abs/2505.15917), Craig Gidney, arXiv:2505.15917, accessed 2026-07-05
- [FIPS 203, 204, 205](https://csrc.nist.gov/pubs/fips/203/final), NIST, finalized August 13, 2024
- [BIP-360](https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki), Hunter Beast, Ethan Heilman, Isabel Foxen Duke, official Bitcoin BIPs repository
- [pq.ethereum.org](https://pq.ethereum.org/), Ethereum Foundation post-quantum roadmap hub
- [Project Eleven Q-Day Prize](https://www.prnewswire.com/news-releases/project-eleven-awards-1-btc-q-day-prize-for-largest-quantum-attack-on-elliptic-curve-cryptography-to-date-302752439.html), announcement of the 15-bit ECC key demonstration on public quantum hardware
