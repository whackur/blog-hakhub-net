---
title: "Pulling Encryption Keys Out of Passkeys with the WebAuthn PRF Extension"
meta_title: ""
description: "How the WebAuthn PRF extension relates to CTAP2 hmac-secret, the encryption design decisions it leaves to your app, and current device and platform support."
date: 2026-07-03T14:52:00+09:00
lastmod: 2026-07-03T14:52:00+09:00
image: ""
categories: ["Security"]
tags: ["passkey", "webauthn", "fido2", "security", "cryptography"]
author: "whackur"
translationKey: "webauthn-prf-passkeys"
draft: false
---

Passkeys show up on login screens everywhere now. What's less well known is that the same authenticator holding your passkey can also hand out key material for encryption, not just authentication. The `prf` extension in WebAuthn is that path. This post covers what PRF actually returns, how it relates to the CTAP2 `hmac-secret` extension, and what you still have to build yourself before it's usable for real encryption.

## WebAuthn and passkeys in short

WebAuthn creates public-key credentials scoped to a Relying Party, the service requesting the login. The authenticator, a device security module such as a secure enclave or TPM, holds the private key. The server stores only the public key and verifies a signature over a server-issued challenge plus client and authenticator data. The private key never leaves the authenticator.

A passkey is a WebAuthn/FIDO credential unlocked by a device's screen lock, biometric sensor, PIN, or pattern. Biometric data itself stays on-device. Those two properties, RP-scoping and local verification, are what make passkeys more phishing-resistant than passwords.

## What the PRF extension returns

The WebAuthn `prf` extension returns one or two pseudo-random outputs tied to a specific credential and to caller-supplied input values called salts. It's defined in the [W3C WebAuthn Level 3 specification](https://www.w3.org/TR/webauthn-3/#prf-extension), with background and use cases in the [W3C PRF explainer](https://raw.githubusercontent.com/w3c/webauthn/main/explainers/prf-extension.md).

The same credential and the same salt always produce the same output. Without the secret held by the authenticator, that output looks random. The practical mental model is HMAC with a random key and a strong hash function: different credentials or different salts produce unrelated outputs.

There's an important boundary here. PRF does not encrypt anything by itself. It hands back credential-scoped key material after a WebAuthn ceremony completes. To turn that into actual encryption, the application still needs a separate crypto layer, typically WebCrypto.

## How it relates to CTAP2 hmac-secret

The PRF extension sits on top of `hmac-secret`, an extension in CTAP2, the lower-level protocol between an authenticator and the browser or OS. Per [MDN's WebAuthn extensions documentation](https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API/WebAuthn_extensions), PRF is the browser-level API surface for this hardware capability. An authenticator needs CTAP2 `hmac-secret` support before a browser can expose `prf`. The actual computation happens inside the authenticator; the browser is just the layer that passes the result to the application.

## Inputs and outputs: eval.first and eval.second

Per MDN, callers pass salts through `eval.first` (required) and an optional `eval.second`, and results come back as `prf.results.first` with an optional `prf.results.second`. Supporting two outputs in one call has a practical use: it lets an app request a "current key" and a "next key" in a single round trip, which fits key rotation patterns.

One caveat worth flagging: getting a PRF output at credential creation time (`create()`) is less widely supported than getting one at assertion time (`get()`). A `create()` call can report `prf: { enabled: false }`, meaning PRF is available on the authenticator but no output came back yet. An environment that doesn't support PRF at all on `get()` can simply return an empty `prf: {}`. Application code needs to branch on both cases explicitly.

It's also worth being direct about this: PRF evaluation goes through normal WebAuthn UI and authenticator activation. It is not something you can call silently in the background. Biometric confirmation or a PIN entry happens on each call, subject to whatever session policy the platform applies.

## What's still your job in the encryption design

Using PRF output in a real system means your application, not the extension, owns at least three things:

- **AES-GCM nonce uniqueness.** If you use a PRF output as an AES-GCM key, you must prevent nonce or IV reuse under that key. Reusing a nonce with the same key breaks confidentiality, and PRF gives you no protection against that mistake.
- **Envelope encryption for multiple credentials.** Users often have more than one credential across devices. Rather than encrypting data directly with each credential's PRF output, it's generally easier to manage a single data encryption key, then wrap that key separately per credential.
- **Account recovery.** Lose the authenticator and the PRF-derived key material is gone with it. A recovery path, whether a backup credential or a server-side key escrow, needs to be designed up front. Neither WebAuthn nor PRF provides one.

## Device and platform support

Support varies by OS, browser, credential provider, and authenticator. The table below summarizes the [passkeys.dev device support matrix](https://passkeys.dev/device-support/) (last updated 2026-05-20). Before shipping, verify `prf.enabled` and `prf.results` directly in your target environments rather than relying on this snapshot.

| Feature | Supported on |
|---------|---------------|
| Synced passkeys | Android v9+, ChromeOS v129+, iOS/iPadOS v16+, macOS v13+, Ubuntu (via browser extensions). Windows support is planned; device-bound passkeys are already supported |
| Autofill UI / Conditional Get | Android Chrome 108+ / Edge 122+, ChromeOS v129+, iOS/iPadOS 16.1+ (Safari, Chrome, Edge, Firefox), macOS Safari 16.1+ / Chrome 108+ / Firefox 122+ / Edge 122+, Ubuntu (browser extensions), Windows Chrome 108+ / Firefox 122+ / Edge 122+ (with a Windows 11 22H2+ footnote) |
| Passkey upgrades / Conditional Create | Android Chrome 142+, ChromeOS 136+, iOS 18+ (footnoted on browser/provider support), macOS Safari 18+ / Chrome 136+, Ubuntu Chrome 136+, Windows Chrome 136+ (requires OS and credential manager support) |
| Cross-device authentication client | Android v9+, ChromeOS v108+, iOS v16+, macOS v13+, Ubuntu Chrome/Edge, Windows 23H2+ |
| Third-party credential managers | Android v14+, iOS v17+, macOS v14+, Windows v25H2+, ChromeOS/Ubuntu via browser extensions |

Windows deserves its own note. Per [Microsoft Learn](https://learn.microsoft.com/en-us/windows/security/identity-protection/passkeys/) (updated 2026-05-13), Windows Hello can create and store passkeys, unlocked by biometrics or PIN, and companion phone or tablet use is supported. Windows 11 version 22H2 with KB5030310 adds native passkey management, and Windows 11 24H2 prompts users for privacy consent before an app can access passkeys. Cross-device authentication requires Bluetooth enabled on both the Windows machine and the mobile device, plus an internet connection.

One assumption to avoid: passkey support does not imply PRF support. PRF availability is a narrower subset, and it can vary by authenticator or credential provider even on the same OS. Production code needs to check `prf.enabled` and `prf.results` at runtime and have a fallback, such as server-managed keys, when PRF isn't there.

For background on Apple's model, see [Apple's official support document](https://support.apple.com/en-us/102195), which covers the passkey security model along with iCloud Keychain sync and device-bound options. Chrome's implementation details are in [Chrome for Developers' WebAuthn documentation](https://developer.chrome.com/docs/identity/webauthn).

## Takeaways

The PRF extension turns a passkey into more than a login mechanism: it becomes a credential-scoped key derivation tool. But what PRF actually does stops at "return a stable pseudo-random output tied to a credential and a salt." Real encryption (AES-GCM nonce management), multi-device support (envelope encryption), and recovery design are still on the application. And because support depends on the specific device, OS, browser, and credential provider combination, checking it directly in your target environments belongs on the pre-launch checklist.

## References

- [W3C Web Authentication Level 3, PRF Extension](https://www.w3.org/TR/webauthn-3/#prf-extension): W3C Candidate Recommendation Snapshot, 2026-05-26
- [W3C WebAuthn PRF explainer](https://raw.githubusercontent.com/w3c/webauthn/main/explainers/prf-extension.md): GitHub, w3c/webauthn
- [MDN Web Authentication extensions](https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API/WebAuthn_extensions): MDN, last modified 2025-06-23
- [Google Passkeys overview](https://developers.google.com/identity/passkeys): Google for Developers, last updated 2026-04-15
- [passkeys.dev device support matrix](https://passkeys.dev/device-support/): passkeys.dev, last updated 2026-05-20
- [About the security of passkeys](https://support.apple.com/en-us/102195): Apple official support document
- [Support for passkeys in Windows](https://learn.microsoft.com/en-us/windows/security/identity-protection/passkeys/): Microsoft Learn, last updated 2026-05-13
- [Enabling Strong Authentication with WebAuthn](https://developer.chrome.com/docs/identity/webauthn): Chrome for Developers
