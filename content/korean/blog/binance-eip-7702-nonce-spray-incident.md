---
title: "바이낸스 Ethereum 지갑 유출과 EIP-7702 nonce-range spray 분석"
meta_title: ""
description: "Binance 14 위임 거래의 유효 서명 50개, 주요 유출·차단 거래와 후속 스왑을 대조하고 서명 권한 침해와 프로토콜 검증 결함을 구분합니다."
date: 2026-10-30T14:00:00+09:00
lastmod: 2026-10-30T14:53:07+09:00
image: "/images/posts/binance-eip-7702-nonce-spray-incident/cover.webp"
categories: ["Blockchain", "Security"]
tags: ["ethereum", "eip-7702", "binance", "custody", "incident-analysis"]
author: "whackur"
translationKey: "binance-eip-7702-nonce-spray-incident"
draft: false
---

<style id="binance-7702-mobile">
.content:has(#binance-7702-mobile) { overflow-wrap: anywhere; }
.content:has(#binance-7702-mobile) :not(pre) > code { white-space: normal; }
.content:has(#binance-7702-mobile) pre { max-width: 100%; overflow-x: auto; overflow-wrap: normal; }
.content:has(#binance-7702-mobile) pre code { white-space: pre; overflow-wrap: normal; }
.content:has(#binance-7702-mobile) table { display: block; max-width: 100%; overflow-x: auto; }
</style>

2026년 10월 30일 새벽, Etherscan이 **Binance 14**로 식별한 Ethereum 계정에 EIP-7702 위임이 설정됐습니다. 3분 24초 뒤 외부 실행자가 이 계정을 호출했고, ETH와 여러 ERC-20 토큰이 공격자 수취 주소로 이동했습니다. 위임 거래의 원시 바이트에는 피해 계정으로 복구되는 유효한 서명 50개가 들어 있습니다. 확인된 경로는 **유효한 위임 서명을 이용한 계정 권한 탈취**와 부합합니다. 서명 검증을 건너뛰었거나 ECDSA가 깨졌다는 증거는 확보되지 않았습니다. [위임 거래](https://etherscan.io/tx/0xad99264d5532ae0dd04b2004eebda05f25657e70dacb764f7ac8d4ccd051298b), [주요 스윕 거래](https://etherscan.io/tx/0x53bd38b816c23e74134786c29a8c18d792777998a3b9326047b583100e88e2f3)

핵심 미확정 사항은 그 유효한 서명을 누가 어떤 경로로 얻었느냐입니다. 개인키 원문 탈취, 서명 인프라 오용, 승인 정책 실패, 탈취된 사전 서명은 온체인 결과만으로 구분되지 않습니다. nonce 여러 개를 대상으로 서명한 흔적은 이 질문에 단서를 주지만 답을 확정하지는 않습니다.

이 보고서의 범위는 Ethereum의 Binance 14 위임과 대표 거래 7개, 후속 스왑 및 특정 시점의 잔액 관찰입니다. 시각은 KST로 통일했습니다. 최초 위임과 아래 주요 거래 7개의 UTC 날짜는 10월 29일입니다. [Unchained의 보도](https://unchainedcrypto.com/binance-says-user-funds-are-completely-safe-after-3-5-billion-drains-from-its-hot-wallets/)는 다른 체인과 전체 피해 규모를 함께 다루지만, 해당 총액과 총동결액을 여기서 독립 검산한 것은 아닙니다. BTC·Tron·Arbitrum·Avalanche의 침해 원인을 EIP-7702로 묶어 설명할 근거도 없습니다.

## 사건의 계정과 권한 구조

EOA(externally owned account)는 개인키에 대응하는 외부 소유 계정입니다. 전통적인 EOA는 자체 실행 코드 없이 서명한 거래를 보내는 계정으로 취급됐습니다. EIP-7702는 이 계정이 다른 주소의 코드를 자신의 실행 문맥에서 실행하도록 위임하는 기능을 제공합니다. 이후 누군가 EOA를 호출하면 위임 코드가 그 EOA의 자산과 권한을 사용해 동작할 수 있습니다. [EIP-7702 명세](https://eips.ethereum.org/EIPS/eip-7702#specification)

이 사건의 주소는 다음과 같습니다. Binance와 Exploiter 명칭은 Etherscan의 라벨이며 라벨 자체가 법적 소유자나 공격자 신원을 암호학적으로 증명하지는 않습니다.

| 역할 | 주소 |
| --- | --- |
| 피해 계정, Binance 14 | [0x28C6c06298d514Db089934071355E5743bf21d60](https://etherscan.io/address/0x28C6c06298d514Db089934071355E5743bf21d60) |
| 외부 실행자, Binance Hot Wallet Exploiter | [0x7C8601d4645b93cea45F71e118A729332e6B5CA0](https://etherscan.io/address/0x7C8601d4645b93cea45F71e118A729332e6B5CA0) |
| 주요 수취 계정, Binance Hot Wallet Exploiter 2 | [0x5227f603C1eE34CE3C06eFe6477003BDfCCB2f8c](https://etherscan.io/address/0x5227f603C1eE34CE3C06eFe6477003BDfCCB2f8c) |
| 위임 구현 | [0x63e842b054bd624a465454d533c33f573e9c6fae](https://etherscan.io/address/0x63e842b054bd624a465454d533c33f573e9c6fae) |
| 별도 송금 계정, Binance 16 | [0xDFd5293D8e347dFe59E90eFd55b2956a1343963d](https://etherscan.io/address/0xDFd5293D8e347dFe59E90eFd55b2956a1343963d) |

외부 실행자는 위임 거래를 제출하고 호출한 계정입니다. 위임을 허용하는 서명자는 Binance 14입니다. 두 역할을 나누어 봐야, Binance 14에서 시작하는 일반 출금 거래가 없어도 자금이 이동한 이유를 이해할 수 있습니다.

## 위임부터 재스윕까지의 거래 7개

아래 거래는 모두 탐색기에 전체 상태가 Success로 표시됐습니다. 토큰 수량은 거래 상세의 표시값을 보존했습니다. 가격에 따라 달라지는 달러 환산액 대신 자산별 수량을 적습니다.

### 1. 05:20:59 KST, 위임 설정

[0xad99264d5532ae0dd04b2004eebda05f25657e70dacb764f7ac8d4ccd051298b](https://etherscan.io/tx/0xad99264d5532ae0dd04b2004eebda05f25657e70dacb764f7ac8d4ccd051298b), 블록 `26300753`.

From은 외부 실행자이고 To는 Binance 14입니다. Etherscan은 Binance 14가 위 구현으로 위임됐다고 표시합니다. [Blockaid의 공개 분석](https://x.com/blockaid_/status/2115924317888495661)은 type-4 거래 하나에 서로 다른 nonce를 담은 authorization 50개를 넣어 그중 하나가 적중한 경로라고 설명했습니다. 원시 거래 검증에서도 50개라는 개수와 서명자, 위임 대상, 실제 내림차순 순서가 확인됩니다.

### 2. 05:24:23 KST, Binance 14 주요 스윕

[0x53bd38b816c23e74134786c29a8c18d792777998a3b9326047b583100e88e2f3](https://etherscan.io/tx/0x53bd38b816c23e74134786c29a8c18d792777998a3b9326047b583100e88e2f3), 블록 `26300770`.

실행자가 Binance 14를 호출합니다. 내부 전송에는 Binance 14에서 주요 수취 계정으로 이동한 `167,464.247856558836135296 ETH`가 표시됩니다. ERC-20 전송 목록은 63개 항목이며 대표 수량은 다음과 같습니다.

- `1,615,409,498.97324 USDT`
- `62,597,239.679797044969015518 RLUSD`
- `29,934.013163146020067927 wBETH`

일부 내부 호출에는 execution reverted 경고가 있지만 전체 거래 상태는 Success이고 성공한 전송이 표시됩니다. 일부 호출의 실패를 전체 스윕 실패로 읽으면 실제 자산 이동을 놓치게 됩니다. 63개 전송 항목도 곧바로 서로 다른 토큰 63종을 뜻하지는 않습니다.

### 3. 05:24:47 KST, Binance 16의 별도 ETH 송금

[0x51f263fa50966df6bbd7f8c6e6e99e3791c94444f7c4343b2fef1ee2d62fd39f](https://etherscan.io/tx/0x51f263fa50966df6bbd7f8c6e6e99e3791c94444f7c4343b2fef1ee2d62fd39f), 블록 `26300772`.

Binance 16에서 같은 수취 계정으로 `28,005.6 ETH`가 전송됩니다. Binance 14를 호출한 앞 거래와는 별개입니다. 수취인이 같다는 사실만으로 Binance 16의 최초 침해 방식까지 EIP-7702였다고 단정할 수 없습니다.

### 4. 05:41:23 KST, Hot Wallet 34의 USDC 이동

[0xdc102dd89dded5a83f1008906883ffb7c81ff3b7d7965d8c7277d170b5e17481](https://etherscan.io/tx/0xdc102dd89dded5a83f1008906883ffb7c81ff3b7d7965d8c7277d170b5e17481), 블록 `26300855`.

최상위 From은 외부 실행자, To는 Binance 14입니다. 그런데 토큰 이동의 출발지는 Etherscan 라벨 Binance: Hot Wallet 34이며, 주요 수취 계정으로 `780,000,000 USDC`가 이동합니다.

Unchained는 이를 Binance 14가 소유한 별도 스마트월렛의 권한을 행사한 경로로 설명합니다. 확인된 최상위 호출과 토큰 이동은 그 설명과 부합합니다. 다만 Hot Wallet 34의 owner storage, 전체 호출 trace, 검증된 소스까지 독립 대조하지 않았으므로 세부 권한 경로는 보도에 귀속합니다. [Unchained 보도](https://unchainedcrypto.com/binance-says-user-funds-are-completely-safe-after-3-5-billion-drains-from-its-hot-wallets/)

### 5. 06:01:35 KST, USDT 차단

[0x7baba482077843514d9c72bac0110ba0916b0814288a72917e2c3bb27a9d8659](https://etherscan.io/tx/0x7baba482077843514d9c72bac0110ba0916b0814288a72917e2c3bb27a9d8659), 블록 `26300954`.

Etherscan은 Tether가 주요 수취 계정의 USDT 사용을 차단한 거래로 표시합니다. 이 조치는 해당 토큰의 통제 기능이며 ETH 자체를 같은 방식으로 동결하는 조치가 아닙니다.

### 6. 06:04:59 KST, USDC blacklist

[0xc954c86f118e8e410e6a3eb9e3b38ff4a95fbdae9d2d58e13166afb7a1f4fc5f](https://etherscan.io/tx/0xc954c86f118e8e410e6a3eb9e3b38ff4a95fbdae9d2d58e13166afb7a1f4fc5f), 블록 `26300971`.

USDC Token에 대한 Blacklist 호출이 표시됩니다. 앞선 USDT 차단과 이 호출의 존재는 확인되지만, 두 거래만으로 보도된 총동결액을 검산할 수는 없습니다. 이후의 해제 여부나 모든 자산의 사용 가능 상태도 별도 확인 대상입니다.

### 7. 06:44:11 KST, Binance 14 재스윕

[0x55ba4dabc41b468e580751373ad31acdee6f5ba398682df2c93e5a8340870556](https://etherscan.io/tx/0x55ba4dabc41b468e580751373ad31acdee6f5ba398682df2c93e5a8340870556), 블록 `26301167`.

실행자가 Binance 14를 다시 호출합니다. 주요 수취 계정으로 `369.831856995580626695 ETH`, `200,397,771.824195 USDT` 등이 이동합니다. 이 시점 전의 모든 입금 출처를 추적한 결과는 아니지만, 위임 이후 잔여 자금이나 후속 유입도 계속 위험할 수 있음을 보여주는 거래입니다.

## 50개 서명이 덮은 것은 계정 nonce 범위

여기서 계정 nonce는 공개된 실행 상태이자 재실행 방지용 카운터입니다. ECDSA 서명 과정의 비밀값 `k`도 nonce라고 부르지만 둘은 다른 값입니다. 공개 계정 nonce를 알아내도 개인키나 서명을 생성할 능력은 생기지 않습니다.

EIP-7702의 authorization 형식과 서명 digest는 다음과 같습니다. 여기서 `address`는 자금 수취인이 아니라 실행을 위임할 구현 주소입니다. [공식 명세](https://eips.ethereum.org/EIPS/eip-7702#set-code-transaction)

```text
authorization = [chain_id, address, nonce, y_parity, r, s]
digest = keccak256(0x05 || rlp([chain_id, address, nonce]))
```

[위임 거래의 Raw Tx Hex](https://etherscan.io/getRawTx?tx=0xad99264d5532ae0dd04b2004eebda05f25657e70dacb764f7ac8d4ccd051298b)를 RLP로 디코딩하고 재인코딩하면 원래 바이트와 일치합니다. 전체 바이트의 Keccak-256도 거래 해시와 일치합니다. 따라서 탐색기의 authorization 표가 정렬된 방식과 별개로, 실제 제출된 목록의 순서를 확인할 수 있습니다.

| 원시 데이터 검증 항목 | 결과 |
| --- | --- |
| 거래 유형과 authorization 수 | type `0x04`, 50개 |
| chain ID | 모두 `1`, 범용 `0`이 아님 |
| 복구된 authority | 50개 모두 Binance 14 주소 |
| 위임 대상 | 50개 모두 `0x63e842b054bd624a465454d533c33f573e9c6fae` |
| 실제 목록 순서 | `18914824, 18914823, …, 18914775` |
| 서로 다른 ECDSA `r` | 50개 |
| 별도 cryptography/OpenSSL ECDSA 검증 | 50개 모두 통과 |
| 바깥 거래 서명에서 복구한 sender | `0x7c8601d4645b93cea45f71e118a729332e6b5ca0` |

OpenSSL 검증에는 이미 계산한 32바이트 Keccak digest를 Prehashed API로 전달했습니다. API의 해시 알고리즘 지정 때문에 SHA-256으로 다시 해싱한 결과가 아닙니다. 공개키 복구 계산과 별개인 ECDSA 검증이 같은 digest와 서명을 받아들였다는 의미입니다. 바깥 거래의 sender와 authorization의 authority도 서로 다르게 복구됩니다.

이 결과는 올바른 서명 수학과 계정의 대응 관계를 확인합니다. 합법적인 운영자가 승인했다는 뜻도, 공격자가 개인키 원문을 소유했다는 증거도 아닙니다. 서명이 생성된 장치, 시각, 요청자, 승인 절차는 원시 거래에 들어 있지 않습니다.

nonce별 digest가 달라지므로 유효한 서명 하나에서 nonce 숫자만 바꾸어 50개를 만들 수 없습니다. 이 묶음은 유효한 위임 서명들로 **계정 nonce 범위를 덮는 nonce-range spray**입니다. 무작위 서명으로 개인키를 맞히는 brute force와는 구분됩니다. 계속 움직이는 핫월렛의 포함 시점 nonce 차이를 견디려는 방법과 양립하지만, 공격자가 정확한 nonce를 몰랐는지, 언제 서명했는지까지 이 패턴이 알려주지는 않습니다. [원시 거래](https://etherscan.io/getRawTx?tx=0xad99264d5532ae0dd04b2004eebda05f25657e70dacb764f7ac8d4ccd051298b), [Blockaid 분석](https://x.com/blockaid_/status/2115924317888495661)

## 내림차순 목록에서는 하나만 적용되는 조건

Etherscan의 Authorizations 표는 nonce `18914809`만 Validity=True, 나머지 49개는 False로 표시합니다. 그러나 원시 서명 50개는 모두 암호학적 검증을 통과했습니다. 표의 False를 곧바로 잘못된 서명으로 해석하면 안 됩니다. 서명이 유효한지와 그 시점의 nonce·코드 조건에 맞아 위임이 적용되는지는 다른 검사입니다. [해당 거래의 Authorizations](https://etherscan.io/tx/0xad99264d5532ae0dd04b2004eebda05f25657e70dacb764f7ac8d4ccd051298b#authorizationlist)

명세는 authorization을 목록 순서대로 처리합니다. 복구한 authority의 코드가 비어 있거나 이미 위임된 코드인지, 계정 nonce가 서명한 nonce와 같은지 등을 확인합니다. 적용되면 코드에 `0xef0100 || address` 위임 지시자를 쓰고 authority nonce를 1 올립니다. 조건에 맞지 않는 항목은 건너뜁니다. [EIP-7702 처리 규칙](https://eips.ethereum.org/EIPS/eip-7702#behavior)

**탐색기가 표시한 당시 계정 nonce `18914809`를 전제로 하면**, 원시 목록의 처음 15개는 너무 큰 nonce라 건너뜁니다. 16번째 항목인 `18914809` 하나가 적용되면 계정 nonce는 `18914810`이 됩니다. 이후 34개는 모두 `18914808` 이하이므로 적용되지 않습니다. 이미 앞에서 지나간 `18914810`을 다시 처리하지도 않습니다. 탐색기 표는 원시 목록과 반대 방향으로 렌더링되므로 화면 정렬 순서를 실행 순서로 삼을 수 없습니다.

![내림차순 authorization 50개 중 당시 nonce와 같은 하나가 적용되고 계정 nonce가 증가한 뒤 나머지를 건너뛰는 조건부 처리](/images/posts/binance-eip-7702-nonce-spray-incident/nonce-range.svg)

탐색기에 표시된 당시 nonce를 전제로 한 순차 처리 계산입니다. 아카이브 노드에서 실제 prestate를 가져와 재실행한 결과는 아닙니다. 도식의 한 번 적용은 코드 실행 50회를 뜻하지 않습니다.

순서를 오름차순으로 가정하면 연속 적용이 가능한 다른 계산이 나옵니다. 이 사건에서는 원시 바이트가 내림차순이므로 그 가정을 사용할 수 없습니다. 동일 ECDSA `r`의 반복도 이 50개에서는 관찰되지 않았습니다. 이는 단순한 동일 `k` 재사용 패턴을 찾지 못했다는 뜻이며, 편향된 `k`, 부분 유출, MPC 구현 오류까지 배제하는 증거는 아닙니다.

## 확인된 권한 악용과 미확정인 최초 침해

서명 검증 결함은 공격자가 필요한 권한 없이 검사를 통과시키는 문제입니다. 이 사건에서 확보한 것은 올바른 digest에 대해 같은 피해 계정으로 복구되고 별도 ECDSA 검증도 통과하는 50개 서명입니다. 현재 증거는 EIP-7702 합의 규칙이나 ECDSA 검증을 우회했다는 분류를 지지하지 않습니다. 유효하게 검증되는 위조가 이론상 불가능하다는 증명까지 한 것은 아니지만, 우선 조사할 경계는 **서명을 생성하거나 획득하는 권한**입니다.

| 가능한 서명 획득 경로 | 구분에 필요한 증거 |
| --- | --- |
| 개인키 원문 유출 | 키 접근·반출 흔적, 키 관리 환경의 포렌식 |
| HSM/MPC signer 또는 서명 서비스 오용 | 서명 요청·인증·쿼럼·정책 평가 로그 |
| raw digest 서명 허용이나 승인 절차 악용 | 요청 digest와 요청자, 정책 결정, 승인 화면·기록 |
| 탈취된 사전 서명 또는 서명 유도·피싱 | 서명 생성 시각과 유통 경로, 실제 사용자 상호작용 |

이 가설들은 동시에 일부 성립할 수도 있으며 현재 온체인 자료로 하나를 선택할 수 없습니다. 모든 서명이 `chain_id=1`이라는 사실도 이 묶음을 다른 체인에서 그대로 쓰는 범용 authorization과 구분할 뿐, 다른 체인의 침해를 설명하지는 않습니다.

정상 지갑 구현의 `execute` 서명 검증이 재사용되거나 우회되는 취약점과도 구분해야 합니다. 여기에는 처음부터 공격에 사용된 구현을 가리키는 authorization이 있습니다. 정상 delegate의 실행 검증 버그를 추가로 가정하지 않아도 초기 경로를 설명할 수 있습니다. Blockaid는 해당 구현을 운영자 주소가 하드코딩된 sweeper로 분석했습니다. 여기서 sweeper라는 표현은 그 분석과 관찰된 반복 자산 이동에 근거하며, 구현 바이트코드나 접근 제어를 독립 감사했다는 뜻은 아닙니다. [Blockaid 원문](https://x.com/blockaid_/status/2115924317888495661)

## Etherscan에 공개된 Claude 재구성 소스

2026-10-30 14:49 KST에 확인한 [위임 구현의 Etherscan 코드 페이지](https://etherscan.io/address/0x63e842b054bd624a465454d533c33f573e9c6fae#code)는 `Source Code Verified / Exact Match`를 표시합니다. 컴파일러는 `v0.8.28+commit.7893614a`, optimizer는 200 runs, EVM 대상은 `cancun`으로 나옵니다. 이는 컴파일한 소스와 배포 코드의 일치 검증 표시이며 보안 감사나 안전성 보증은 아닙니다. 같은 페이지의 감사 항목은 `No Contract Security Audit Submitted`로 표시됐습니다.

공개된 `Target.sol`의 주석은 이를 원본 소스가 아닌 AI 재구성 소스로 명시합니다. 주석에 따르면 Claude가 배포된 런타임 바이트코드에서 2026-10-30 00:30 UTC(09:30 KST)에 재구성했고, `solc 0.8.28`, `via-ir`, optimizer 200 runs, `cancun`으로 컴파일하면 끝부분 메타데이터 해시를 제외한 런타임 바이트코드가 일치한다고 합니다. 컨트랙트명과 매개변수명도 추정이라고 적혀 있습니다. Claude라는 귀속과 재구성 시각은 소스 주석의 주장이며, 작성자 신원이나 업로드 시각을 독립 확인한 자료는 아닙니다. Etherscan의 `Exact Match` 표시와 이 메타데이터 단서는 구분해서 읽어야 하며, 별도 재컴파일이나 바이트코드 대조 결과는 확보하지 않았습니다. [공개 소스](https://etherscan.io/address/0x63e842b054bd624a465454d533c33f573e9c6fae#code)

이 재구성 소스에서는 `onlyAuthorized`가 호출자를 하드코딩된 `authorizedCaller`인 `0x7C8601d4645b93cea45F71e118A729332e6B5CA0`으로 제한합니다. 앞서 바깥 type-4 거래 서명에서 복구한 제출자와 같은 주소입니다. `sweep`, `withdrawETH`, `withdrawToken`, `callExecute`에 이 제한이 붙어 있어 자산 전송과 외부 실행 호출의 구조를 읽기 쉬워졌습니다. 이는 공개된 재구성 소스의 구조를 확인한 것이며 개별 거래의 실행 trace를 독립 검증한 결과는 아닙니다. [구현 코드](https://etherscan.io/address/0x63e842b054bd624a465454d533c33f573e9c6fae#code)

이 자료는 배포된 sweeper의 동작을 이해하는 데 도움을 줍니다. 기존의 유효한 위임 서명 50개라는 검증 결과는 달라지지 않으며, 서명을 누가 어떤 경로로 얻었는지도 밝혀주지 않습니다. 재구성 소스의 공개는 공격자의 원본 소스를 확보했다거나 Claude가 공격 코드를 작성했다는 증거가 아닙니다.

## 위임의 범위와 외부 지갑 권한

일반 ERC-20 `approve`는 특정 토큰의 allowance를 부여합니다. EIP-7702 authorization은 계정이 사용할 실행 코드를 정합니다. 서명에는 `chain_id`, 구현 `address`, 계정 `nonce`가 묶이지만 바깥 거래의 sender, 개별 수취인, 금액, calldata, 만료 시각은 기본 필드에 포함되지 않습니다. 세부 실행 제한은 안전한 delegate와 상위 승인 정책이 구현해야 합니다. [명세와 보안 고려사항](https://eips.ethereum.org/EIPS/eip-7702#security-considerations)

그 범위에는 ETH와 여러 토큰뿐 아니라 EOA가 외부 컨트랙트에서 가진 owner·관리자 권한도 들어갈 수 있습니다. Hot Wallet 34의 `780,000,000 USDC` 이동은 그 위험을 살펴볼 사례입니다. 다만 해당 월렛의 실제 소유권·호출 경로는 앞서 구분한 보도 수준의 설명을 유지합니다. 단순히 Binance 14의 주소 잔액만 계산하면 이런 외부 권한의 영향을 놓칠 수 있습니다.

위임은 한 번의 호출 뒤 자동으로 사라지지 않습니다. 실행 부분이 revert하더라도 앞에서 처리한 위임은 롤백되지 않습니다. 06:44:11 재스윕은 지속된 권한 아래의 추가 자산 이동을 보여줍니다. 키나 signer 침해가 계속된다면 위임을 지우는 것만으로는 복구가 끝나지 않습니다. [EIP-7702 동작](https://eips.ethereum.org/EIPS/eip-7702#behavior), [재스윕 거래](https://etherscan.io/tx/0x55ba4dabc41b468e580751373ad31acdee6f5ba398682df2c93e5a8340870556)

이런 위험은 서명 위조 여부와 별개입니다. 명세 역시 앱이 임의로 제시한 authorization을 서명하도록 노출하는 인터페이스의 위험과 지갑 측 코드 감사 필요성을 명시합니다. 프로토콜 검증 결함이 입증되지 않았다고 해서, 위임으로 넓어진 서명 권한과 지속성을 기존 출금 정책이 충분히 다뤘다고 볼 수는 없습니다. [명세의 지갑·앱 상호작용 주의사항](https://eips.ethereum.org/EIPS/eip-7702#interaction-with-applications-and-wallets)

## 13:19~13:30 KST의 잔액 관찰과 후속 스왑

다음은 **2026-10-30 13:19~13:30 KST**에 [주요 수취 주소의 페이지와 token holdings](https://etherscan.io/address/0x5227f603C1eE34CE3C06eFe6477003BDfCCB2f8c)를 확인한 값입니다. 여러 페이지를 같은 블록에 고정한 snapshot이 아니며 발행 시점의 최신 잔액도 아닙니다.

| 자산 | 탐색기 표시 잔액 |
| --- | --- |
| ETH | `17,263.271817626578868333` |
| USDT | `1,175,464,712.87536` |
| USDC | `823,000,000` |
| XAUt | `12,574.046797` |
| USD1 | `27,824,039.9368965` |
| PAXG | `1,906.66772869` |

차단된 토큰도 잔액으로 남아 표시될 수 있습니다. 탐색기의 약 21억 달러 토큰 평가액은 가격과 유동성, 차단 상태를 반영한 사용 가능 자금이나 회수 가능액이 아닙니다. 앞선 blacklist 거래의 존재와 별개로, 이 관찰에서 현재 해제 여부나 모든 자산의 지출 가능 상태를 재검증하지 않았습니다.

같은 날 **13:06:47 KST**, 블록 `26303071`의 성공한 스왑은 구체적인 후속 동작을 보여줍니다.

[0xbe98f5bdfce307e92c1e0bacde80995dfd817b77fc4303224f0283f3aacd1101](https://etherscan.io/tx/0xbe98f5bdfce307e92c1e0bacde80995dfd817b77fc4303224f0283f3aacd1101)

1. 수취 계정이 Uniswap V2 RAD/USDC pool에 `700,567.745144517222388354 RAD`를 보냅니다.
2. 그 pool에서 USDC/WETH pool로 `122,529.838325 USDC`가 이동합니다.
3. WETH를 거쳐 Router 2에서 같은 수취 계정으로 `39.178398816052027387 ETH`가 돌아옵니다.

RAD를 풀 경유로 ETH로 바꾼 경로입니다. 중간 USDC는 풀 사이에서 이동했으므로 공격자 주소에 있던 기존 USDC를 사용했다거나 blacklist를 우회했다는 증거가 아닙니다. 관찰 당시 최신 내부 전송 25개에도 여러 Uniswap V2/V3 Router에서 수취 계정으로 ETH가 들어오는 항목이 있었습니다. 토큰 청산과 ETH 집계로 해석할 수 있지만 세탁이나 현금화의 완료를 증명하지는 않습니다.

**13:10:47 KST**의 다른 거래는 외부 계정이 69 wei와 텍스트를 보낸 소액 입금입니다.

[0x98e03bf51e20c6b1a02f6759b3790fdbbc6e55c5af15f72f86ae78fb7dead479](https://etherscan.io/tx/0x98e03bf51e20c6b1a02f6759b3790fdbbc6e55c5af15f72f86ae78fb7dead479)

누구나 이런 메시지나 더스트를 보낼 수 있습니다. 텍스트의 Hyperliquid·Monero 언급은 해당 서비스로 자금이 흘렀다는 증거가 아닙니다.

대규모 ETH의 후속 주소·브리지·거래소 반출은 전체 이력으로 재구성하지 않았습니다. 최신 25개 전송만으로 전체 자금 흐름을 대신할 수 없으며, 초기 탈취량에서 관찰 잔액을 빼서 외부 반출액으로 계산할 수도 없습니다. 추가 유입, 스왑, 가스, 래핑과 다른 주소·체인의 이동을 함께 대사해야 합니다. 믹서나 특정 서비스로의 최종 도착도 이 확인 범위 밖입니다.

## 수탁 운영에서 점검할 서명 경계

이 사건이 제기하는 실무 과제는 출금 트랜잭션을 승인하는 경계와 계정의 실행 코드를 바꾸는 서명 경계를 함께 통제하는 것입니다. 바깥 거래는 다른 계정이 제출할 수 있으므로 **송신 서비스에서 type-4 출금만 막는 필터로는 충분하지 않습니다**. 다음은 관찰된 경로와 EIP의 권한 범위에서 도출되는 방어 항목입니다.

- **signer에서 authorization을 구분합니다.** EIP-7702를 사용하지 않으면 `0x05` 도메인의 위임 서명을 거부합니다. raw digest signing이 거래 정책 검사를 우회하지 못하도록 요청 형식과 권한을 통제합니다.
- **위임을 고권한 변경으로 승인합니다.** 사용해야 한다면 체인과 구현 allowlist, 실제 주소·bytecode 확인, 행위 시뮬레이션을 적용합니다. 프록시 구조라면 업그레이드 권한까지 검사합니다. 수취인·금액·calldata·실행 재사용 방지는 안전한 delegate의 정책으로 다뤄야 합니다.
- **50개 서명의 생성 경로를 추적합니다.** nonce별 digest 요청의 출처, 생성 시각, 인증과 승인 기록을 대조합니다. 키 비반출을 보장하는 HSM/MPC를 사용해도 서명 권한 오용에 대한 조사는 별도로 필요합니다.
- **계정 코드 변경과 외부 권한을 함께 감시합니다.** 위임 변경을 탐지하고 침해 주소의 자동 입금·리필을 중단합니다. 해당 EOA가 외부 월렛의 owner나 관리자인지도 조사해 권한을 분리하거나 교체합니다.
- **복구를 위임 삭제로 끝내지 않습니다.** signer·키 침해가 남았는지 확인하고 안전한 계정으로 자산과 외부 권한을 옮기는 절차를 검토합니다. 계속 유효한 서명을 만들 수 있는 공격자는 다시 위임을 설정할 수 있습니다.

확인된 사건 경로는 EIP-7702 authorization을 악용한 계정 권한 탈취와 반복 스윕입니다. 최초 서명 획득 경로, 아카이브 prestate의 nonce·코드, 재구성 소스에서 읽은 접근 제어의 실제 실행 검증, 외부 월렛의 정확한 권한 경로와 전체 반출 대사는 남아 있습니다. 이 구분을 유지해야 프로토콜 검증과 수탁 서명 정책 중 어느 경계를 추가로 조사해야 하는지 좁힐 수 있습니다.

## 함께 보면 좋을 자료

- [EIP-7702의 보안 고려사항](https://eips.ethereum.org/EIPS/eip-7702#security-considerations): delegate가 구현해야 할 실행 서명과 재사용 방지 조건입니다.
- [EIP-7702의 호환성 변화](https://eips.ethereum.org/EIPS/eip-7702#backwards-compatibility): 외부 호출로 EOA 잔액이 줄 수 있다는 보안 가정의 변화를 설명합니다.

## 참고 자료

- [EIP-7702: Set Code for EOAs](https://eips.ethereum.org/EIPS/eip-7702): Ethereum 공식 명세, 조회일 2026-10-30.
- [위임 거래 원시 바이트](https://etherscan.io/getRawTx?tx=0xad99264d5532ae0dd04b2004eebda05f25657e70dacb764f7ac8d4ccd051298b): 거래 해시·목록 순서·서명 검증의 원자료, 조회일 2026-10-30. 대표 거래 7개와 후속 거래는 해당 절에 전체 해시로 연결했습니다.
- [위임 구현의 재구성 소스](https://etherscan.io/address/0x63e842b054bd624a465454d533c33f573e9c6fae#code): Etherscan 검증 표시와 공개된 `Target.sol`, 확인 시각 2026-10-30 14:49 KST. Claude 귀속·재구성 시각·메타데이터 해시 예외는 소스 주석의 주장입니다.
- [Blockaid의 사건 분석](https://x.com/blockaid_/status/2115924317888495661): nonce-range spray와 sweeper 구현 분석의 공개 출처, 조회일 2026-10-30.
- [Binance Says User Funds Are Completely Safe After $3.5 Billion Drains From Its Hot Wallets](https://unchainedcrypto.com/binance-says-user-funds-are-completely-safe-after-3-5-billion-drains-from-its-hot-wallets/): Unchained의 보도 맥락과 외부 월렛 권한 경로 설명, 조회일 2026-10-30.
- [주요 수취 주소](https://etherscan.io/address/0x5227f603C1eE34CE3C06eFe6477003BDfCCB2f8c): 2026-10-30 13:19~13:30 KST 탐색기 관찰, 동일 블록에 고정되지 않은 잔액 자료.
