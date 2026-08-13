# Verdis Wallet Reference & User Guide

This document provides a technical and user reference for the **Verdis Web Wallet** and **Verdis Android Native Wallet**.

---

## 1. Supported Client Interfaces

| Interface | URL / Download Path | Access Platform |
| :--- | :--- | :--- |
| **Verdis Web Wallet** | `https://verdischain.com/wallet.html` | Cross-platform web browser |
| **Verdis Android Wallet**| `https://verdischain.com/verdis-wallet-release.apk` | Native Android devices (Android 8.0+) |

---

## 2. Security & Key Management Architecture

Verdis Wallet implements a non-custodial local security architecture. Private keys never leave the client device under any circumstances.

```
+-----------------------------------------------------------------------------------+
|                            VERDIS CLIENT KEYSTORE                                 |
+-----------------------------------------------------------------------------------+
|  12 / 24-Word BIP39 Mnemonic Seed Phrase                                          |
|                         |                                                         |
|                         v Derive Keys                                             |
|  Substrate Keypair (sr25519 / ed25519)                                            |
|                         |                                                         |
|                         v Encrypt                                                 |
|  AES-256-GCM Encrypted Local Store (Web LocalStorage / Android Keystore / Biometric)|
|                         |                                                         |
|                         v Authorize via PIN / Biometrics                          |
|  Signed Extrinsic Payload Sent to Node RPC                                       |
+-----------------------------------------------------------------------------------+
```

### Key Security Protocols
* **Derivation Standard:** Substrate SR25519 / Ed25519 key derivation over BIP39 standard mnemonics.
* **SS58 Address Formatting:** Network prefix `909` (Addresses start with `5...` or `9...` depending on encoder representation).
* **Storage Encryption:** Local keystore encrypted using AES-256-GCM with PBKDF2 key derivation from user PIN.
* **Android Biometric Integration:** Hardware-backed Android Keyostore integration supporting Fingerprint and Face Unlock mechanisms.
* **Inactivity Auto-Lock:** Wallets automatically lock session keys after **5 minutes** of idle inactivity.

---

## 3. Web Wallet (`wallet.html`) Guide

### 3.1. Account Setup & Key Recovery
1. Access `https://verdischain.com/wallet.html`.
2. Choose **Create New Wallet** or **Import Seed Phrase**.
3. **Mnemonic Phrase Backup:** Write down the generated 12 or 24-word seed phrase. Store it securely offline.
4. **Set Local Password / PIN:** Set a minimum 6-digit PIN code used to decrypt the keystore for transaction signing.

```
+-------------------------------------------------------------+
| CREATE WALLET - SEED PHRASE BACKUP                          |
|                                                             |
|  [ 1. forest ]  [ 2. green  ]  [ 3. verdis ]  [ 4. solar  ] |
|  [ 5. energy ]  [ 6. chain  ]  [ 7. Secure ]  [ 8. block  ] |
|  [ 9. node   ]  [10. proof  ]  [11. stake  ]  [12. epoch  ] |
|                                                             |
|  WARNING: Never share your seed phrase with anyone!          |
|  [ ] I have written down my 12-word recovery phrase          |
|  < Continue >                                               |
+-------------------------------------------------------------+
```

### 3.2. Sending & Receiving VRDX Tokens
* **Receive VRDX:** Copy your SS58 address or scan the displayed QR code.
* **Send VRDX:**
  1. Click **Send**.
  2. Input recipient SS58 address.
  3. Enter VRDX amount (Default precision: 9 decimal places).
  4. Review estimated network fee.
  5. Enter PIN code to unlock key, sign payload, and broadcast to `https://verdischain.com/rpc`.

---

## 4. DEX Trading & Liquidity Provision

The wallet integrates directly with `pallet_amm_dex` for decentralized token swaps and liquidity management.

```
+-------------------------------------------------------------+
| AMM DEX SWAP INTERFACE                                      |
+-------------------------------------------------------------+
| Pay:       [ 1,000.00 ] VRDX     (Balance: 12,450.00 VRDX)  |
| Receive:   [   250.00 ] vUSDT   (Slippage Tolerance: 0.5%)|
+-------------------------------------------------------------+
| Price Impact: 0.04% | Swap Fee: 0.30% (3.00 VRDX)            |
+-------------------------------------------------------------+
| < Swap VRDX for vUSDT >                                      |
+-------------------------------------------------------------+
```

### Performing a Token Swap
1. Open the **DEX** tab in the wallet.
2. Select trading pair (e.g., VRDX -> vUSDT).
3. Set maximum allowed slippage (default: `0.5%`).
4. Click **Swap**. The wallet constructs a `pallet_amm_dex::swap_exact_tokens_for_tokens` extrinsic payload.
5. Confirm transaction with PIN.

### Adding / Removing Liquidity
* **Add Liquidity:** Provide proportional amounts of Token A and Token B to earn 0.30% swap pool fees. Receives AMM-LP liquidity pool tokens.
* **Remove Liquidity:** Burn AMM-LP tokens to withdraw underlying reserve tokens from `pallet_amm_dex`.

---

## 5. DPoS Staking & Delegation

Users can stake VRDX tokens to delegate voting weight to validators or run validator nodes via `pallet_dpos`.

```
+-------------------------------------------------------------+
| DPoS STAKING DASHBOARD                                      |
+-------------------------------------------------------------+
| Staked Balance: 50,000.00 VRDX | Pending Rewards: 124.50 VRDX|
| Active Validator Delegations: 3 / 16 Max                    |
+-------------------------------------------------------------+
| SELECT VALIDATORS TO NOMINATE:                              |
| [X] EcoValidator-01 (Uptime: 99.9%, Commission: 2%, Green: 98)|
| [X] VerdisNode-Green (Uptime: 100%, Commission: 1%, Green: 95)|
+-------------------------------------------------------------+
| < Nominate Selected & Stake >                               |
+-------------------------------------------------------------+
```

### Staking Rules
* **Minimum Nominator Stake:** `100 VRDX`.
* **Max Nominated Validators:** Nominate up to 16 validators per account.
* **Unbonding Period:** `28 sessions` (~28 hours). Staked tokens remain locked and non-transferable during unbonding.
* **Claiming Rewards:** Rewards auto-accumulate every session (600 blocks) and can be claimed via the **Claim Staking Rewards** button.

---

## 6. Android Native Wallet (`verdis-wallet-release.apk`)

### Installation & System Requirements
* **APK Location:** Served directly from `https://verdischain.com/verdis-wallet-release.apk`.
* **OS Support:** Android 8.0 (API level 26) or higher.

### Android Security Features
1. **Biometric Auth Prompt:** Uses `BiometricPrompt` API to authenticate keystore access via hardware fingerprint scanner or facial recognition.
2. **Android Keystore System:** Private keys are stored in secure hardware-backed storage (TEE/StrongBox) encrypted with `AES/GCM/NoPadding`.
3. **Screen Protection:** Enables `FLAG_SECURE` to prevent screenshots and screen recording on sensitive seed phrase view screens.

---

## 7. Transaction Signing & Technical Flow

```
[Wallet UI Input]
       |
       v
1. Construct Scale-Encoded Unsigned Extrinsic
   (Call Index: Pallet 5 / Method 0 [Balances:Transfer], Params: Recipient + Amount + Nonce + Era)
       |
       v
2. Request User PIN / Biometric Auth
       |
       v
3. Decrypt Encrypted Local Private Key
       |
       v
4. Sign Extrinsic Payload using SR25519 / Ed25519 Curve
       |
       v
5. Append Signature + Era + Nonce + Tip Header
       |
       v
6. Send Hex String to Node via WebSocket / RPC (author_submitExtrinsic)
```
