---
title: "Bitcoin, Ethereum, and the Quantum Computing Question"
meta_title: ""
description: "Quantum risk depends on signatures, public-key exposure, and runtime. A source-grounded look at 2026 resource estimates and Bitcoin and Ethereum migration plans."
date: 2026-07-05T23:37:01+09:00
lastmod: 2026-10-16T01:03:28+09:00
image: "/images/posts/bitcoin-ethereum-quantum-computing-risk/quantum-ledgers-cover-20261016.webp"
categories: ["Blockchain"]
tags: ["bitcoin", "ethereum", "quantum-computing", "post-quantum-cryptography", "cryptography"]
author: "whackur"
translationKey: "bitcoin-ethereum-quantum-computing-risk"
draft: false
---

Quantum computers are a **long-term threat to the signatures** that protect Bitcoin and Ethereum. The public research checked on October 16, 2026 (KST), however, estimates resources for future error-corrected machines; it does not demonstrate recovery of a real secp256k1 private key on quantum hardware. Risk depends on how long a public key is exposed, how long an attack takes, and whether authentication and authority can migrate first. Bitcoin’s defenses remain proposals, while Ethereum is working on a transition across accounts, consensus, and data. [Resource-estimation paper](https://arxiv.org/html/2609.05625v1), [BIP-360](https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki), [Ethereum Foundation transition plan](https://blog.ethereum.org/2026/09/07/protocol-priorities)

## Forging signatures and attacking hashes are different jobs

A digital signature does not encrypt coins. It proves authority to approve a transaction. Write an elliptic-curve public key as `Q = d·G`: `d` is the private scalar and `G` a fixed base point. Computing `Q` from `d` is easy; recovering `d` from `Q` is the elliptic curve discrete logarithm problem, which is hard for classical computers. A sufficiently capable error-corrected quantum computer can solve it in polynomial time with Shor’s algorithm. An attacker who recovers the key can sign new transactions as its owner. [Schrottenloher’s circuit research](https://arxiv.org/html/2606.02235v1)

| Primitive | Role in Bitcoin or Ethereum | Quantum attack distinction |
| --- | --- | --- |
| secp256k1 ECDSA | Bitcoin’s existing signatures; Ethereum externally owned account (EOA) authentication | Recovering the private key with Shor enables forgery |
| secp256k1 Schnorr | Bitcoin Taproot signatures | Different signature format, same curve’s discrete-log assumption |
| BLS | Ethereum validator signatures and aggregation | Quantum-vulnerable too, but uses a different curve and parameters |
| Hashes such as SHA-256 and Keccak | Mining and commitments to addresses or data | Generic preimage search receives Grover’s quadratic speedup |

[BIP-340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki) specifies secp256k1 for Schnorr. [Ethereum’s cryptography roadmap](https://ethereum.org/roadmap/security/quantum-resistance/) treats ECDSA, BLS, and KZG commitments as distinct targets. A figure such as “1,450 logical qubits to attack secp256k1” therefore cannot be reused as a BLS attack estimate.

Grover reduces an unstructured search over `N` candidates to roughly `√N` queries. Idealized generic preimage search therefore takes about `2^128` quantum queries for a 256-bit hash and `2^80` for a 160-bit hash. These are not runtimes: every query needs a circuit and error correction. HASH160 is `RIPEMD160(SHA256(public_key))`; its ability to conceal a public key depends on hash security. [NIST’s Grover definition](https://xlinux.nist.gov/dads/HTML/groversAlgo.html), [BIP-141’s public-key hash rules](https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki)

Mining is different again from finding a preimage of one particular 256-bit digest. It races to find any hash below a difficulty target, so gate speed, parallelism, and costs against ASICs matter. The `2^128` figure alone says nothing about mining dominance, and difficulty adjustment does not itself cap an attacker’s share of block production. Section III.4 of the 2026 [Google, Ethereum Foundation, Stanford, and collaborators’ paper](https://arxiv.org/html/2603.28846v2#S3.SS4) argues that signatures are a much more plausible attack target than mining under its hardware assumptions.

## Public-key exposure determines the attack window

A Bitcoin address is not necessarily a public key. An unspent transaction output (UTXO) locks coins under spending conditions. Some outputs contain a key directly; others contain a hash of a key or script. The [SegWit rules](https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki) and [Taproot rules](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki) produce these differences:

| Target | When the attacker obtains a public key | Consequence for remaining funds |
| --- | --- | --- |
| P2PK or bare multisig | When the output is created | The exposed key allows a long computation |
| P2PKH or P2WPKH | Normally submitted when spending | Other UTXOs or later deposits using the same key remain exposed |
| P2SH or P2WSH | Revealing the spending script can disclose its keys | Depends on script contents and key reuse |
| P2TR (Taproot) | The output directly contains a 32-byte output public key | The key used for key-path validation is exposed even if the owner intends a script-path spend |
| Ethereum EOA | Recoverable from the signature of an outgoing transaction | Remaining funds, later deposits, and the account’s authority remain targets |

Taproot’s key path permits spending with a signature for the output public key. Even if a hidden script contains other safeguards, an attacker who computes that output key’s private scalar can use the key path. [BIP-341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki)

Compare two cases. If coins remain in a P2PK output, the attacker need not finish before the next block. A machine that takes days can matter. A fresh P2WPKH output whose key has not been disclosed elsewhere reveals it when its first spending transaction enters the mempool. The attacker must recover the key and get a conflicting spend included before the original confirms. Bitcoin’s average ten-minute block interval is not a guaranteed defense window. Propagation, fees, and the arrival of the next block also affect the outcome. [Joint paper, section III.2](https://arxiv.org/html/2603.28846v2#S3.SS2)

Offchain disclosure can remove the protection offered by a hashed address. Recipients of a wallet’s extended public key (xpub) or descriptor belong in the threat model. An already-spent output cannot be stolen again, but other outputs protected by the same key are a separate matter. [BIP-360’s exposure conditions](https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki)

Ethereum users commonly keep using the same account. Once its key is recoverable from a signature, a short block interval cannot prevent a long-exposure attack. An administrator account with little ETH may still control a bridge or upgrade. This is forgery of new authorized actions after key recovery, rather than decryption of old transactions. [Ethereum accounts](https://ethereum.org/developers/docs/accounts/), [Post-Quantum team FAQ](https://pq.ethereum.org/)

## Read qubit counts alongside runtime

Physical qubits are device components. Logical qubits are computational units protected by physical qubits and error-detection and correction procedures. There is no fixed conversion ratio. Error rates, connectivity, code choice, computation length, and acceptable failure probability determine the required hardware. Willow’s [below-threshold error-correction study](https://www.nature.com/articles/s41586-024-08449-y) demonstrated quantum memories whose logical errors declined as the code grew. It did not execute a complete, long cryptanalytic circuit.

A Toffoli gate reversibly flips a target bit conditional on two control bits; its count is a major circuit-cost measure. Runtime also depends on parallelism and measurement and control delays. Before comparing 2026 estimates, distinguish a complete key-recovery circuit from optimization of one internal operation.

| Research | Logical circuit resources | Meaning of physical footprint and time |
| --- | --- | --- |
| [Babbush et al., published in March](https://arxiv.org/html/2603.28846v2) | At most 1,200 logical qubits and 90 million Toffolis, or 1,450 and 70 million | Under 500,000 physical qubits estimated for superconducting hardware, planar degree-four connectivity, and `10^-3` physical errors |
| [Schrottenloher, June](https://arxiv.org/html/2606.02235v1) | Complete circuit: about 1,208 and `2^26.11` Toffolis, or 1,462 and `2^25.78` | Disclosed logical designs, not measured hardware or runtime |
| [Trapped-ion study, September](https://arxiv.org/html/2609.05625v1) | Main-text count: 1,457 logical qubits and about 39 million Toffolis | 19,397 physical qubits and about 25.7 days per attempt, for a specific error-corrected architecture |

The March paper assumes a 10μs control reaction time and 50% extra cost per gate to estimate 18 to 23 minutes. Precomputing the public-key-independent first half and waiting in that state cuts the time after learning a key to roughly 9 to 12 minutes. It assumes 1μs error-correction rounds. These are single-key resource estimates, not device measurements. Circuit details were withheld, with a zero-knowledge proof supporting resource and test results. [Sections II.1 to II.2 and appendix](https://arxiv.org/html/2603.28846v2)

The September trapped-ion design trades a smaller footprint for a long runtime. Assumptions include physical noise of `10^-4`, a 200μs physical operation cycle, and approximately 0.02950 seconds per logical measurement layer. Its low memory logical-error rates are extrapolated from simulations at higher noise. End-to-end success is not certain: the paper distinguishes an estimate of about 40.7%, starting from a rigorous algorithmic lower bound, from about 63.3%, starting from a heuristic. **It did not demonstrate an attack on an existing 19,397-qubit device.** Its relevance is to keys exposed for days or longer, rather than an ordinary mempool race. [Section II.3, Part V, and appendix E](https://arxiv.org/html/2609.05625v1)

A separate September paper, [ECDSA.Fail](https://arxiv.org/html/2609.09582v2), reports a point-addition circuit with 1,151 logical qubits and an average 1,299,453 executed Toffolis at its July 26 data cutoff. This benchmarks an internal Shor operation. The authors identify full-algorithm integration and validation as remaining work, and caution that different interfaces and accounting conventions prevent a simple claim of superiority over complete circuits. It does not mean that “1,151 qubits broke Bitcoin.”

## Choosing a standard signature does not complete migration

Among the standards NIST finalized in August 2024, [ML-KEM (FIPS 203)](https://csrc.nist.gov/pubs/fips/203/final) establishes shared secrets for communications. It does not replace a coin-spending signature. The signature standards are lattice-based [ML-DSA (FIPS 204)](https://csrc.nist.gov/pubs/fips/204/final) and stateless hash-based [SLH-DSA (FIPS 205)](https://csrc.nist.gov/pubs/fips/205/final).

The size difference is substantial. A BIP-340 Schnorr signature is 64 bytes. ML-DSA-44 uses a 1,312-byte public key and 2,420-byte signature; SLH-DSA-SHA2-128s uses a 32-byte public key and 7,856-byte signature. These are examples of specific parameter sets, not a comparison at identical security levels. [BIP-340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki), [FIPS 204 table 2](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf), [FIPS 205 table 2](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf)

Deployment must fit public-key and signature sizes and verification costs into block space, gas budgets, and node bandwidth. That motivates Ethereum’s research into verification precompiles and proof-based signature aggregation. Adopting a candidate primitive is different from migrating every account, administrative key, and consensus rule. [Ethereum post-quantum research](https://pq.ethereum.org/)

Stateful hash signatures need another distinction. XMSS combines many one-time signature keys in a tree under one top-level key, allowing multiple messages. The danger is reusing a one-time leaf index, perhaps through backup restoration or concurrent signing devices, rather than simply using the top-level key twice. Wallets must validate index management and recovery procedures too. [NIST SP 800-208](https://csrc.nist.gov/pubs/sp/800/208/final)

## Bitcoin separates output design from treatment of existing coins

Checked on October 16, 2026 (KST), **BIP-360 is a Draft proposal for P2MR (Pay-to-Merkle-Root)**. It keeps a Taproot-like script tree but removes the key-path spend and commits to a Merkle root. Its purpose is to reduce long-exposure attacks by removing a path that publishes a key directly in the output. It does not solve mempool attacks when spending still uses ECDSA or Schnorr and reveals a key. Post-quantum signatures are separate work. A document in the proposal repository is not network activation. [BIP-360](https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki)

**BIP-361 is also Draft and is an Informational document.** It depends on a post-quantum signature proposal that remains unspecified. The current text proposes Phase A, restricting sends to vulnerable addresses around three years (160,000 blocks) after activation, followed two years later by Phase B, requiring a quantum-safe rescue protocol for legacy ECDSA/Schnorr spends. This is not an adopted schedule. [BIP-361](https://github.com/bitcoin/bips/blob/master/bip-0361.mediawiki)

Rescue relies on information the authentic holder knows beyond the individual private key a quantum attacker recovers. One example is proving knowledge of a parent secret key behind hardened HD-wallet derivation. The text explicitly leaves open how much legacy supply such protocols could cover. Long inactivity does not prove a key is lost. Leaving unmigrated coins spendable or imposing additional conditions is a consensus decision involving both security and property rights. [BIP-361 rescue discussion](https://github.com/bitcoin/bips/blob/master/bip-0361.mediawiki)

## Ethereum must migrate accounts, consensus, and data

On September 7, 2026, the Ethereum Foundation’s Protocol cluster announced a **target of quantum resistance across execution, consensus, and data by December 2029**. It uses a possible 2030 attack as an aggressive planning assumption, not a Q-day forecast. The team’s readiness target is distinct from agreement on upgrades and their deployment. Its FAQ says full execution-layer user migration may take additional years. [Research team FAQ](https://pq.ethereum.org/) [EF Protocol announcement](https://blog.ethereum.org/2026/09/07/protocol-priorities)

| Layer | What must change | Approach under development |
| --- | --- | --- |
| Execution | Authentication for EOAs, smart accounts, and applications | Account abstraction, PQ signature verification, retirement of legacy key authority |
| Consensus | Validator BLS signatures | Hash signatures such as leanXMSS and proof aggregation using leanVM |
| Data | Blob KZG commitments and related mechanisms | Quantum-safe commitments and verification structures |

This is the multilayer transition described by the [official research hub](https://pq.ethereum.org/). Replacing compact aggregated BLS signatures with larger hash signatures also requires keeping propagation and verification costs manageable. Elliptic-curve setup parameters in KZG and some pairing-based proof systems need attention as well. Replacing ordinary account signatures does not automatically finish that work. [Ethereum cryptography roadmap](https://ethereum.org/roadmap/security/quantum-resistance/)

KZG commitments represent blob data as a polynomial, using a compact commitment and proof to check that a value at a particular point matches the committed data. This is the verification structure in [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844). The joint paper’s on-setup attack recovers a setup secret by solving a discrete logarithm in the public parameters; subsequent false proofs can then be produced classically. Honest erasure of ceremony secrets does not make the public parameters’ discrete-log problem quantum-safe. [Sections IV and V.5](https://arxiv.org/html/2603.28846v2#S5.SS5)

In particular, **EIP-7702 delegation does not retire the original ECDSA key**. That key can change delegation. Even if delegated code checks a post-quantum signature, an attacker who recovers the original key retains a way around it. [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702)

The September EF plan includes EIP-8141 Frame Transactions and proposals to turn accounts into full contract accounts. Separately, Draft [EIP-8151](https://eips.ethereum.org/EIPS/eip-8151) proposes returning zero from `ecRecover` for accounts whose code is neither empty nor exactly an EIP-7702 delegation indicator. It addresses legacy keys still authorizing contract actions, such as token `permit`, after migration. It does not cover every contract’s custom ECDSA implementation. [EF account-transition discussion](https://blog.ethereum.org/2026/09/07/protocol-priorities)

## Readiness includes retiring authority

Engineering checks can be more concrete than predicting a quantum computer’s release year:

- **Map keys to authority.** Include administrators, recovery agents, bridges, and upgrade keys alongside user balances. Identify onchain and offchain public-key disclosures.
- **Reduce key reuse and record exposure.** A fresh hashed Bitcoin output still reveals its key when first spent; it is not permanent post-quantum protection.
- **Test the new signature and old bypasses together.** Exercise PQ verification, recovery, backups, rotation, and retirement of legacy ECDSA authority in one scenario. Multisig alone does not give quantum resistance when every key relies on the same vulnerable mathematics.
- **Track estimates, demonstrations, and activation separately.** An estimate needs errors, connectivity, runtime, and failure probability. An upgrade needs client implementation, testing, activation, and actual user migration.

These checks apply [BIP-360’s exposure analysis](https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki), [EIP-8151’s authority problem](https://eips.ethereum.org/EIPS/eip-8151), and [EF’s migration plan](https://blog.ethereum.org/2026/09/07/protocol-priorities) to a working system. Progress in error correction or circuit optimization does not establish a year when all coins become vulnerable. Declaring migration complete likewise requires examining remaining keys and authority paths, rather than the name of a new algorithm.

## Further reading

- [BIP-341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki): output keys and the two spending paths.
- [NIST SP 800-208](https://csrc.nist.gov/pubs/sp/800/208/final): key-management constraints for stateful hash signatures.
- [Post-Quantum Ethereum](https://pq.ethereum.org/): official entry point to research and open implementations by layer.

## References

- [Securing Elliptic Curve Cryptocurrencies against Quantum Vulnerabilities](https://arxiv.org/html/2603.28846v2): Babbush et al., sections II to III and appendix, accessed October 16, 2026 (KST).
- [Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms](https://arxiv.org/html/2606.02235v1): André Schrottenloher, tables 1 to 2, accessed October 16, 2026 (KST).
- [Computing 256-bit elliptic curve discrete logarithms in 26 days](https://arxiv.org/html/2609.05625v1): section II.3, Part V, appendix E, accessed October 16, 2026 (KST).
- [ECDSA.Fail](https://arxiv.org/html/2609.09582v2): results and limitations, accessed October 16, 2026 (KST).
- [BIP-141](https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki): SegWit rules, accessed October 16, 2026 (KST).
- [BIP-340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki): secp256k1 Schnorr, accessed October 16, 2026 (KST).
- [BIP-341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki): Taproot rules, accessed October 16, 2026 (KST).
- [BIP-360](https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki): P2MR proposal, accessed October 16, 2026 (KST).
- [BIP-361](https://github.com/bitcoin/bips/blob/master/bip-0361.mediawiki): migration and rescue proposal, accessed October 16, 2026 (KST).
- [Grover’s algorithm](https://xlinux.nist.gov/dads/HTML/groversAlgo.html): NIST, accessed October 16, 2026 (KST).
- [Quantum error correction below the surface code threshold](https://www.nature.com/articles/s41586-024-08449-y): Google Quantum AI and Collaborators, Nature, accessed October 16, 2026 (KST).
- [FIPS 203](https://csrc.nist.gov/pubs/fips/203/final): NIST, ML-KEM, accessed October 16, 2026 (KST).
- [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final): NIST, ML-DSA, accessed October 16, 2026 (KST).
- [FIPS 205](https://csrc.nist.gov/pubs/fips/205/final): NIST, SLH-DSA, accessed October 16, 2026 (KST).
- [SP 800-208](https://csrc.nist.gov/pubs/sp/800/208/final): NIST, stateful hash signatures, accessed October 16, 2026 (KST).
- [Post-Quantum Ethereum](https://pq.ethereum.org/): Ethereum Foundation research team, accessed October 16, 2026 (KST).
- [EF Protocol: Current and Emerging Priorities](https://blog.ethereum.org/2026/09/07/protocol-priorities): EF Protocol cluster, September 7, 2026, accessed October 16, 2026 (KST).
- [Post-quantum cryptography on Ethereum](https://ethereum.org/roadmap/security/quantum-resistance/): ethereum.org, accessed October 16, 2026 (KST).
- [Ethereum accounts](https://ethereum.org/developers/docs/accounts/): ethereum.org, accessed October 16, 2026 (KST).
- [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844): blob and KZG verification rules, accessed October 16, 2026 (KST).
- [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702): code delegation rules, accessed October 16, 2026 (KST).
- [EIP-8151](https://eips.ethereum.org/EIPS/eip-8151): proposal to restrict legacy-key contract authorization, accessed October 16, 2026 (KST).
