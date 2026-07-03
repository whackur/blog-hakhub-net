---
title: "WebAuthn PRF 확장으로 passkey에서 암호화 키 꺼내기"
meta_title: ""
description: "WebAuthn PRF 확장과 CTAP2 hmac-secret의 관계, 암호화 설계 원칙, 기기·플랫폼 지원 현황을 구현 시 주의점과 함께 정리합니다."
date: 2026-07-03T14:52:00+09:00
lastmod: 2026-07-03T14:52:00+09:00
image: ""
categories: ["Security"]
tags: ["passkey", "webauthn", "fido2", "security", "cryptography"]
author: "whackur"
translationKey: "webauthn-prf-passkeys"
draft: false
---

passkey는 이제 로그인 화면에서 흔히 보이는 옵션이 됐습니다. 그런데 passkey를 쥔 authenticator에서 로그인 말고 암호화 키까지 뽑아 쓸 수 있다는 사실은 상대적으로 덜 알려져 있습니다. WebAuthn의 `prf` 확장이 그 통로입니다. 이 글은 PRF가 무엇을 돌려주는지, CTAP2 `hmac-secret`과 어떤 관계인지, 그리고 실제 암호화 설계에 넣을 때 조심해야 할 지점을 정리합니다.

## WebAuthn과 passkey, 짧은 정리

WebAuthn은 RP(Relying Party, 로그인을 요구하는 서비스)마다 스코프가 분리된 공개키 credential을 만듭니다. authenticator(기기의 보안 모듈, 예를 들어 secure enclave나 TPM)가 개인키를 쥐고, 서버는 공개키만 저장한 채 서버가 보낸 challenge와 client/authenticator data에 대한 서명을 검증합니다. 개인키가 서버로 넘어가는 구간이 아예 없습니다.

passkey는 화면 잠금, 생체 인증, PIN, 패턴으로 잠금 해제되는 WebAuthn/FIDO credential입니다. 생체 데이터 자체는 기기 밖으로 나가지 않습니다. 이 두 가지, RP 스코프 분리와 로컬 검증이 passkey를 비밀번호보다 피싱에 강하게 만드는 핵심입니다.

## PRF 확장이 돌려주는 것

WebAuthn의 `prf` 확장은 credential 하나와 호출자가 넘긴 입력값(salt)에 묶인 의사난수 출력을 한두 개 돌려줍니다. [W3C WebAuthn Level 3 명세](https://www.w3.org/TR/webauthn-3/#prf-extension)가 정의하는 확장이며, [W3C의 PRF 익스플레이너](https://raw.githubusercontent.com/w3c/webauthn/main/explainers/prf-extension.md)에 배경과 사용 사례가 정리되어 있습니다.

같은 credential에 같은 입력을 넣으면 항상 같은 출력이 나옵니다. 반대로 authenticator가 쥔 비밀 없이는 그 출력이 무작위처럼 보입니다. 실무적으로는 무작위 키로 강한 해시 함수를 돌리는 HMAC과 같은 모델로 이해하면 됩니다. credential마다, salt마다 서로 다른 출력이 나오는 구조입니다.

여기서 중요한 경계선이 있습니다. PRF는 그 자체로 데이터를 암호화하지 않습니다. WebAuthn 의식(ceremony)이 끝난 뒤 credential에 묶인 키 재료를 하나 내줄 뿐입니다. 이 키 재료로 실제 암호화를 하려면 애플리케이션이 WebCrypto 같은 별도의 암호화 계층을 붙여야 합니다.

## CTAP2 hmac-secret과의 관계

PRF 확장은 인증기기와 브라우저/OS 사이의 저수준 프로토콜인 CTAP2의 `hmac-secret` 확장과 맞닿아 있습니다. [MDN의 WebAuthn 확장 문서](https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API/WebAuthn_extensions)에 따르면 PRF는 브라우저 레벨의 WebAuthn API가 이 하드웨어 기능을 노출하는 창구 역할을 합니다. authenticator가 CTAP2 `hmac-secret`을 지원해야 브라우저가 `prf`를 지원할 수 있는 구조입니다. 즉 PRF의 실제 계산은 authenticator 내부에서 일어나고, 브라우저는 그 결과를 애플리케이션에 전달하는 계층입니다.

## 입력과 출력: eval.first, eval.second

MDN 문서 기준으로 호출자는 `eval.first`(필수)와 `eval.second`(선택)에 salt를 넣어 요청하고, 결과는 `prf.results.first`, 옵션으로 `prf.results.second`로 돌아옵니다. 두 개의 출력을 요청할 수 있다는 점이 실용적인 이유가 있습니다. 예를 들어 "현재 키"와 "다음 키" 또는 키 로테이션 패턴을 하나의 요청으로 구성할 수 있습니다.

주의할 점이 하나 있습니다. credential을 만드는 시점(`create()`)에 PRF 출력을 바로 받는 기능은 assertion 시점(`get()`)에 받는 기능보다 지원 범위가 좁습니다. `create()`에서는 `prf: { enabled: false }`처럼 PRF가 활성화만 되고 실제 출력은 없을 수 있고, `get()`에서 지원하지 않는 environment는 아예 빈 객체 `prf: {}`를 돌려줄 수 있습니다. 코드에서 이 두 경우를 구분해서 처리해야 합니다.

또 하나 짚어야 할 점은, PRF 평가가 일반 WebAuthn UI와 authenticator 활성화 절차를 그대로 거친다는 사실입니다. 사용자 상호작용 없이 백그라운드에서 조용히 호출할 수 있는 API가 아닙니다. 생체 인증이나 PIN 입력 같은 사용자 동작이 매 호출마다(또는 세션 정책에 따라) 필요합니다.

## 암호화 설계에 넣을 때

PRF 출력을 실제 서비스에 쓰려면 최소한 다음 세 가지를 애플리케이션이 직접 책임져야 합니다.

- **AES-GCM nonce 유일성**: PRF 출력을 AES-GCM 키로 쓴다면 nonce/IV 재사용을 반드시 막아야 합니다. 같은 키로 nonce가 겹치면 기밀성이 깨집니다. PRF가 이 부분을 대신 보장해 주지 않습니다.
- **다중 credential을 위한 envelope encryption**: 사용자가 credential을 여러 개(여러 기기) 갖고 있으면, 데이터를 각 credential의 PRF 출력으로 직접 암호화하는 대신 데이터 키를 한 번 만들고 그 데이터 키를 credential별로 감싸는 envelope 구조가 일반적으로 더 관리하기 쉽습니다.
- **계정 복구**: authenticator를 분실하면 PRF로 파생한 키도 함께 사라집니다. 복구 경로(백업 credential, 서버 측 키 이스크로 등)를 설계 단계에서 결정해야 합니다. WebAuthn/PRF 자체는 복구 메커니즘을 제공하지 않습니다.

## 기기·플랫폼 지원 현황

지원 여부는 OS, 브라우저, credential provider, authenticator 종류에 따라 갈립니다. 아래는 [passkeys.dev 기기 지원 매트릭스](https://passkeys.dev/device-support/)(2026-05-20 갱신 기준)를 요약한 것으로, 실제 배포 전에는 대상 환경에서 `prf.enabled`와 `prf.results` 값을 직접 확인해야 합니다.

| 기능 | 지원 환경 |
|------|-----------|
| 동기화 passkey | Android v9+, ChromeOS v129+, iOS/iPadOS v16+, macOS v13+, Ubuntu(브라우저 확장 경유). Windows는 계획 중이며, 기기 종속 passkey는 이미 지원 |
| Autofill UI / Conditional Get | Android Chrome 108+ · Edge 122+, ChromeOS v129+, iOS/iPadOS 16.1+(Safari/Chrome/Edge/Firefox), macOS Safari 16.1+ · Chrome 108+ · Firefox 122+ · Edge 122+, Ubuntu(브라우저 확장), Windows Chrome 108+ · Firefox 122+ · Edge 122+(Windows 11 22H2+ 각주) |
| Passkey 업그레이드 / Conditional Create | Android Chrome 142+, ChromeOS 136+, iOS 18+(브라우저/provider 지원 각주), macOS Safari 18+ · Chrome 136+, Ubuntu Chrome 136+, Windows Chrome 136+(OS/credential manager 지원 필요) |
| Cross-device 인증 클라이언트 | Android v9+, ChromeOS v108+, iOS v16+, macOS v13+, Ubuntu Chrome/Edge, Windows 23H2+ |
| 서드파티 credential manager | Android v14+, iOS v17+, macOS v14+, Windows v25H2+, ChromeOS/Ubuntu는 브라우저 확장 경유 |

Windows는 별도로 짚을 부분이 많습니다. [Microsoft Learn 문서](https://learn.microsoft.com/en-us/windows/security/identity-protection/passkeys/)(2026-05-13 갱신)에 따르면 Windows Hello로 passkey를 만들고 저장할 수 있고 생체 인증이나 PIN으로 잠금을 해제하며, 동반 휴대폰/태블릿 사용도 지원합니다. Windows 11 22H2에 KB5030310을 적용하면 네이티브 passkey 관리가 가능하고, Windows 11 24H2부터는 앱이 passkey에 접근하기 전에 프라이버시 동의를 요구합니다. cross-device 인증에는 Windows와 모바일 기기 양쪽에 블루투스가 켜져 있어야 하고 인터넷 연결도 필요합니다.

여기서 절대 넘겨짚지 말아야 할 것이 하나 있습니다. "passkey를 지원하면 PRF도 당연히 된다"는 가정은 성립하지 않습니다. PRF 지원은 passkey 지원보다 좁은 부분집합이고, 같은 OS라도 authenticator나 credential provider에 따라 달라질 수 있습니다. 프로덕션 코드는 반드시 런타임에 `prf.enabled`와 `prf.results`를 확인하고, 미지원 시 대체 흐름(예: 서버 측 키 관리)을 준비해야 합니다.

Apple 쪽 배경 지식으로는 [Apple 공식 지원 문서](https://support.apple.com/en-us/102195)가 passkey 보안 모델을 설명하고, iCloud Keychain을 통한 동기화와 기기 종속 옵션을 함께 다룹니다. Chrome 구현 세부는 [Chrome for Developers의 WebAuthn 강력 인증 문서](https://developer.chrome.com/docs/identity/webauthn)에서 확인할 수 있습니다.

## 정리

PRF 확장은 passkey를 단순 로그인 수단을 넘어 credential 스코프의 키 파생 도구로 만들어 줍니다. 다만 PRF가 해 주는 일은 "credential과 salt에 묶인 안정적인 유사난수 출력을 돌려주는 것"까지입니다. 실제 암호화(AES-GCM nonce 관리), 다중 기기 대응(envelope encryption), 복구 경로 설계는 여전히 애플리케이션의 몫입니다. 그리고 지원 여부는 기기·OS·브라우저·credential provider 조합에 따라 갈리므로, 타깃 환경에서 직접 확인하는 절차를 배포 전 체크리스트에 반드시 넣어야 합니다.

## 참고 자료

- [W3C Web Authentication Level 3, PRF Extension](https://www.w3.org/TR/webauthn-3/#prf-extension): W3C Candidate Recommendation Snapshot, 2026-05-26
- [W3C WebAuthn PRF explainer](https://raw.githubusercontent.com/w3c/webauthn/main/explainers/prf-extension.md): GitHub, w3c/webauthn
- [MDN Web Authentication extensions](https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API/WebAuthn_extensions): MDN, 최종 수정 2025-06-23
- [Google Passkeys overview](https://developers.google.com/identity/passkeys): Google for Developers, 최종 갱신 2026-04-15
- [passkeys.dev 기기 지원 매트릭스](https://passkeys.dev/device-support/): passkeys.dev, 최종 갱신 2026-05-20
- [About the security of passkeys](https://support.apple.com/en-us/102195): Apple 공식 지원 문서
- [Support for passkeys in Windows](https://learn.microsoft.com/en-us/windows/security/identity-protection/passkeys/): Microsoft Learn, 최종 갱신 2026-05-13
- [Enabling Strong Authentication with WebAuthn](https://developer.chrome.com/docs/identity/webauthn): Chrome for Developers
