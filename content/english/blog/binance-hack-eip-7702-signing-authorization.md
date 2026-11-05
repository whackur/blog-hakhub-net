---
title: "Understanding EIP-7702 Through the Binance Hack"
meta_title: ""
description: "An opinion on EIP-7702 delegation risks and compromised signing authority in the Binance hack."
date: 2026-11-05T19:29:27+09:00
lastmod: 2026-11-05T19:29:27+09:00
image: "/images/posts/binance-hack-eip-7702-signing-authorization/cover.webp"
categories: ["Blockchain", "Security"]
tags: ["ethereum", "eip-7702", "binance", "signing-authorization", "account-delegation"]
author: "whackur"
translationKey: "binance-hack-eip-7702-signing-authorization"
draft: false
---

I am sharing some additional thoughts on the recent hack of Binance’s Ethereum withdrawal account (hot wallet).
Many articles have treated EIP-7702 as though it were a dangerous specification in the wake of this incident. I am writing this to understand the specification and the structure of the attack more accurately.

## The risk of EIP-7702 is fundamentally the same issue of 'signing authorization' as ERC-20 approve

EIP-7702 is dangerous enough that an incorrect authorization can have irreversible consequences. But the same is true of the ERC-20 `approve` function.
Given how smart contracts work, responsibility for signatures and authorizations lies with the account and its signer. In other words, an incorrectly executed ERC-20 `approve` and an incorrectly signed EIP-7702 delegation are fundamentally the same kind of risk.

The difference that arguably makes EIP-7702 somewhat more dangerous is its scope. `approve` limits authority to the approved token and amount. By contrast, if an account delegates to a malicious contract through EIP-7702, that contract gains authority over the entire account rather than an individual token. It can therefore freely withdraw not only the ETH and all ERC-20 tokens the account currently holds, but also any assets that arrive before the delegation is revoked.

This was something I worried about when EIP-7702 first appeared. On reflection, though, I see it as an understandable design, because the root cause here is also an incorrect signing authorization.

## Common misconceptions

- **"Systems that use EIP-7702 are dangerous?"**→ No. MetaMask’s Smart Account feature currently uses EIP-7702 too. If using EIP-7702 alone made a system dangerous, that would mean all the many MetaMask wallets already using this feature are in danger right now.
- **"Binance was hacked because it was using EIP-7702?"**→ No. Binance’s EOA withdrawal account (Binance 14) has no history of 7702 delegation before the incident ([reference](https://etherscan.io/address/0x28C6c06298d514Db089934071355E5743bf21d60#authlist7702)). According to Binance’s [November 3 initial investigation report](https://x.com/binance/status/2117626126214504729), this account was an MPC (Multi-Party Computation) wallet, and the attacker used unauthorized access to the internal wallet signing service, rather than a private key. Also, because the MPC setup had no single private key that could immediately sign a revocation, Binance had to develop and execute a separate procedure to create an authorization that revoked delegation by specifying the 0x0 address. As a result, delegation was not revoked until October 30 at 00:10 (UTC), roughly four hours after it took effect. In other words, Binance had no procedure in place to revoke EIP-7702 delegation immediately.

## The spray attack

### What is a spray attack?

The name 'spray' makes it easy to imagine an attack on public-key cryptography or a brute-force attack, in which one of many attempts eventually succeeds.

But this attack was not an attempt to guess a key. The moment the attacker could request arbitrary signatures from the MPC wallet’s signing service, the wallet was already effectively compromised. The MPC key itself was not broken; the system that signed with that key had been taken over. The attacker obtained delegation signatures through unauthorized use of the internal wallet signing service.

The attacker then put those signatures into a transaction submitted from an external account under their control, rather than from Binance’s account. An EIP-7702 authorization is applied on-chain regardless of who submits it, as long as the signature is valid and the chain ID and nonce conditions are met. What matters here, therefore, is not who sent the transaction, but that Binance’s signing system produced valid signatures for the attacker.

### Why do it this way?

An exchange’s withdrawal account continuously processes users’ withdrawal requests in real time. The account’s nonce therefore keeps increasing even between the moment the attacker obtains a delegation signature and the moment that delegation actually takes effect on-chain. If the attacker obtains a signature for only one nonce value, a normal withdrawal might consume that nonce first, invalidating the delegation.

The attacker can thus be understood as having obtained delegation signatures for several upcoming nonce values at once and 'sprayed' them. The idea was to have one apply as long as the nonce at execution fell within the signed range. This is possible because an EIP-7702 transaction can contain multiple authorizations, and an authorization with a mismatched nonce is simply skipped rather than causing the entire transaction to fail.

The actual delegation transaction contained 50 authorizations for nonces 18914775 through 18914824 in descending order (18914824 → 18914775), and all 50 had valid signatures from Binance 14. Only the one for 18914809, which matched the account’s nonce at the time, was applied. The account’s nonce then increased to 18914810, but entries with higher nonces had already been skipped earlier and were not checked again ([detailed analysis](https://blog.hakhub.net/blog/binance-eip-7702-nonce-spray-incident/)).

## Why did the attacker use EIP-7702?

- EIP-7702 is a relatively recently introduced specification.
- The attacker may have targeted a path that was harder for Binance’s anomaly detection system to respond to.
- Once signatures have been obtained, an external account can submit the transaction, so there is no need to send a transaction from Binance’s account.
- Until the EOA signs again to change the delegation, operations can continue at the delegated-contract level. In other words, the approved malicious contract can keep exercising the account’s authority without additional signatures.
- Multiple operations can be bundled into a single transaction.

## Blaming EIP-7702

Four Pillars’ recent article [Reflections on the Binance Exploit](https://research.4pillars.io/ko/research/reflections-on-the-binance-exploit) provides a good account of this incident. I find it difficult to agree with its arguments that hold the EIP-7702 protocol responsible, so I would like to respond to them.

### Claim 1: Delegation made it possible to move the assets in a single call

> Without delegation, the attacker would have had to send a transaction for each token to move more than 60 assets, and many of those transactions would have failed while competing with Binance’s normal withdrawals for nonces. Delegation allowed the attacker to move $2.53B in a single call.

**Response:** The key question is whether the theft could have succeeded. If the signing system had already been taken over, the attacker could have obtained signatures for multiple transactions with consecutive nonces and submitted them within a single block, even without EIP-7702, moving assets before the detection system could react. EIP-7702 did increase the attack’s likelihood of success and its scale, but delegation was not the cause of the compromise.

The opposing position presented in the Four Pillars article makes the same point.

> An attacker who could sign 50 delegation authorizations could just as easily sign ordinary transfers. In fact, at the same time, Binance 16 and wallets on nine other chains were drained through ordinary signatures without EIP-7702.

### Claim 2: Delegation eliminates the time available to detect and respond

> Even if the signing system was breached, previously an attacker had to obtain a fresh signature for each transaction, and cutting off access stopped the outflow. Delegation hands over the entire account at once, eliminating the time available to detect and respond.
>
> In fact, after the first sweep, the attacker took new deposits for more than two hours without signatures from Binance 14.
>
> Withdrawal limits and rate limits are basic security measures because they buy time to respond, but delegation removes that time.

**Response:** Withdrawal limits and rate limits can reduce the damage, but they are not a fundamental solution to this incident. As discussed earlier, the issue of response time can also be largely bypassed by submitting multiple transactions in advance within a single block. A system that revoked delegation immediately upon detecting the block containing it might have provided somewhat better protection, but that too is not a fundamental solution.

As noted earlier, being able to continue exercising the account’s authority until delegation was revoked was a clear advantage for the attacker. But that only let the attacker use already-compromised authority for longer; it was not the cause of the compromise.

EIP-7702 made it possible to execute an ERC-20 token’s `approve` and `transfer` together, but the same functionality can also be abused in a hack like this one. The problem lies in the compromise of signing authority rather than the functionality itself.

## Should EIP-7702 be scrapped?

- This does not mean the specification is unconditionally good. It has, however, already become part of the protocol, and it enables many benefits.
- Realistically, scrapping it now would also be difficult. EIP-7702 is already active on mainnet through the Pectra hard fork. Removing it would require another hard fork and would also affect accounts already using delegation.
- It makes fee sponsorship simpler to implement than approaches that require separate infrastructure, such as ERC-4337 (paymaster) or ERC-2771 (meta-transactions), and it can also be used alongside ERC-4337 infrastructure.

## Closing thoughts

This incident is easier to understand if you think of remote-control apps used in voice phishing. The victim’s OTP or security card was not stolen. The attacker remotely controlled the victim’s already-authenticated phone and pressed the transfer button. Because the request came from a legitimate device with legitimate authentication, protecting the authentication method alone would be unlikely to stop it.

EIP-7702 is a powerful specification, and signing incorrectly can cause substantial damage. But the essence of this incident is that a system with signing authority was taken over, rather than a flaw in the specification. I think the discussion should focus on securing signing systems and building detection and response mechanisms for delegation authorizations, rather than scrapping the specification.

## References

- [Binance, 29 October Binance Security Incident: Initial Findings and Response Update](https://x.com/binance/status/2117626126214504729)
- [Four Pillars, Reflections on the Binance Exploit](https://research.4pillars.io/ko/research/reflections-on-the-binance-exploit)
- [Halborn, Binance Hack Report: The Signing Service Answered, Four Days On](https://www.halborn.com/blog/post/binance-hack-report-signing-service-eip-7702-mpc)
- [Hypernative, Inside the Largest Crypto Theft of All Time](https://www.hypernative.io/insights/blog/inside-the-largest-crypto-theft-of-all-time-the-6-3b-binance-hot-wallet-drain)
- [Binance Ethereum Wallet Drain and EIP-7702 Nonce-Range Spray Analysis](https://blog.hakhub.net/blog/binance-eip-7702-nonce-spray-incident/)
- [EIP-7702: Set Code for EOAs](https://eips.ethereum.org/EIPS/eip-7702)
