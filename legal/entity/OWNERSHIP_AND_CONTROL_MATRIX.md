# VERDIS CHAIN — OWNERSHIP AND CONTROL MATRIX

> **PREPARED FOR:** Rojs and Corporate Counsel Execution  
> **PROJECT:** Verdis Chain (Substrate Layer-1 Blockchain) | Native Token: VRDX (100B supply, 9 decimals)  
> **PROJECT STATUS:** Testnet Live | Token Sale: DISABLED | Funds Raised: $0  
> **DEVELOPMENT COMPANY:** Protremix S.L. (Spain) | **GOVERNANCE FOUNDATION:** Planned (UAE)  
> **TOKEN OFFERING ENTITY:** TBD (Subject to Counsel Advice and Execution)  
> **IMPORTANT NOTICE:** This matrix is an architectural governance document. **No entity has been registered**, **no regulatory status is claimed**, and **no control transfers have occurred**.

---

## 1. Entity Relationships Architecture

The Verdis Chain ecosystem is structured across four distinct operational entities and stakeholder groups to enforce legal separation, decentralization, and regulatory compliance.

```
+-----------------------------------------------------------------------------------+
|                                PROTREMIX S.L.                                     |
|                               (Registered: Spain)                                 |
|  * Substrate Core Engineering & Codebase Maintenance                              |
|  * Frontend UI/UX (Non-custodial Wallet, AMM DEX Interface)                       |
|  * Technical Service Provider under Contract                                      |
+-----------------------------------------------------------------------------------+
                                   |
                                   | Development Services Contract
                                   v
+-----------------------------------------------------------------------------------+
|                           VERDIS FOUNDATION (PLANNED)                             |
|                           (Target Jurisdiction: UAE)                              |
|  * Protocol Governance & Ecosystem Treasury Stewardship                           |
|  * Grant Programs & Developer Incentives                                          |
|  * Non-profit / Purpose-bound Entity                                              |
+-----------------------------------------------------------------------------------+
                                   |
                                   | Protocol Grant & Treasury Allocation
                                   v
+-----------------------------------------------------------------------------------+
|                           TOKEN OFFERING ENTITY (TBD)                             |
|                        (Target Jurisdiction: TBD / SPV)                           |
|  * Public VRDX Token Distribution & Sale Portal (Sale Currently DISABLED)         |
|  * Investor Onboarding, KYC/AML Compliance Enforcement                            |
|  * Exchange Listing & Market Counterparty Relations                               |
+-----------------------------------------------------------------------------------+
                                   |
                                   | Decentralized Consensus Network
                                   v
+-----------------------------------------------------------------------------------+
|                           VALIDATOR OPERATORS NETWORK                             |
|                      (Independent Global Node Operators)                          |
|  * Substrate DPoS Block Production & State Validation                             |
|  * Decentralized Staking Infrastructure                                           |
|  * Independent Consensus Governance                                               |
+-----------------------------------------------------------------------------------+
```

---

## 2. Ownership Structure & Equity Breakdown

### 2.1 Corporate Ownership & Ultimate Beneficial Ownership (UBO)

| Entity Name | Jurisdiction | Legal Structure | Ownership Breakdown | UBO Disclosure Requirements |
| :--- | :--- | :--- | :--- | :--- |
| **Protremix S.L.** | Spain | Sociedad de Responsabilidad Limitada (S.L.) | 100% owned by Founders / Shareholders. | Spanish Commercial Registry (Registro Mercantil) & UBO Register (RETIR). |
| **Verdis Foundation** | UAE (Planned) | Foundation / Non-Profit Guarantee Co. | Memberless / Controlled by Foundation Council. | UAE Ministry of Economy UBO Register & Free Zone Authority. |
| **Offering Entity** | TBD | LLC / SPV / Subsidiary | 100% owned by Foundation OR Held by SPV Trust. | Target Registrar UBO Register (full disclosure for >10% interest). |
| **Validator Network** | Global | Decentralized Permissionless Operators | Zero corporate ownership; independent operators. | N/A (Decentralized consensus participant network). |

### 2.2 UBO Thresholds & Disclosure Policy
- Any individual holding **10% or more** of direct/indirect voting equity or capital interest in Protremix S.L. or the Offering Entity must undergo complete AML/KYC background checks.
- Beneficial owners with control rights over Foundation Council appointments must be disclosed to regulatory authorities upon whitepaper filing.

---

## 3. Comprehensive Control Matrix

The control matrix delineates operational control, administrative credentials, cryptographic key authority, and emergency procedures across all core components of Verdis Chain.

| Ecosystem Asset / Component | Primary Controller | Secondary / Backup Controller | Control Mechanism & Credentials | Governance Rule / Approval Threshold |
| :--- | :--- | :--- | :--- | :--- |
| **Domain Names** (`verdis.chain`, `protremix.com`) | Protremix S.L. IT Admin | Foundation Nominee | Registrar Account + Hardware Key 2FA | Requires 2-person approval for DNS record changes. |
| **GitHub Repositories** (Substrate Runtime) | Protremix Tech Lead | Foundation Core Dev | Organization Admin + Branch Protection | Main branch merges require 2 senior developer reviews + CI tests. |
| **Testnet Seed Nodes & Telemetry** | Protremix DevOps Team | Community Operators | SSH Key Authentication + Cloud IAM | Managed by Protremix during Testnet; transitioned to community on Mainnet. |
| **SUDO Key (Substrate Testnet)** | Protremix CTO | Lead Security Engineer | Hardware Wallet Multi-sig | SUDO active on Testnet; **MUST be removed prior to Mainnet launch**. |
| **Protocol Governance Keys** | Foundation Council | On-chain Council Multi-sig | 3-of-5 Hardware Multi-sig | Protocol upgrades require 3-of-5 Council sign-off + on-chain referendum. |
| **Treasury Reserve Wallets** | Foundation Council | Custody Agent | 3-of-5 Hardware Multi-sig (Fireblocks/Safe) | Outflows >1M VRDX require formal board resolution & public announcement. |
| **Token Sale Portal Infrastructure** | Offering Entity Ops | Protremix Web Team | Cloudflare Enterprise + AWS IAM | Web portal deployment requires sign-off from Legal & Compliance. |
| **KYC/AML Admin Dashboard** | Offering Entity Compliance | Compliance Lead | SSO + MFA + IP Whitelisting | Patient/Participant data access restricted to compliance team. |
| **Social Channels** (Telegram, Discord, X) | Community Lead | Marketing Director | Password Vault + Hardware 2FA | No public announcements without dual sign-off from Marketing & Legal. |

---

## 4. Separation Principles & Decentralization Safeguards

To prevent single points of failure, regulatory classification as a centralized scheme, and unilateral network control, the following strict separation principles are established:

### 4.1 Consensus Decentralization Cap (33% Rule)
- **Rule:** Neither Protremix S.L., the Foundation, nor the Offering Entity shall operate or control more than **33% of total active validator stake** on Verdis Chain.
- **Enforcement:** DPoS staking parameters enforce maximum validator self-stake caps and delegation limits to ensure network consensus remains in the hands of independent global operators.

### 4.2 Treasury Multi-Signature Governance
- **Rule:** All Foundation treasury funds, reserve allocations, and token sale escrow accounts require a **3-of-5 multi-signature authorization threshold**.
- **Signatory Composition:**
  - Signatory 1: Foundation Director / Executive
  - Signatory 2: Core Engineering Lead (Protremix)
  - Signatory 3: Independent Foundation Council Member
  - Signatory 4: Legal / Compliance Officer
  - Signatory 5: External Custodial Escrow Agent

### 4.3 Operational & Legal Firewalls
- **Software Development vs. Offering:** Protremix S.L. shall NOT issue, market, or sell VRDX tokens directly. Its sole role is providing technical development services to the Foundation and Offering Entity under written contract.
- **Financial Independence:** Proceeds from token sales received by the Offering Entity shall be held in dedicated bank/crypto accounts and shall NOT be commingled with Protremix corporate operating capital.

---

## 5. Required Intercompany Contracts

Corporate counsel must draft and execute the following formal legal agreements prior to token offering launch:

```
+------------------+     Software Services & IP License Agreement     +------------------+
|  Protremix S.L.  | <==============================================> |  UAE Foundation  |
|     (Spain)      |      (Technical Development & IP Transfer)       |    (Planned)     |
+------------------+                                                  +------------------+
                                                                               ^
                                                                               | Token Grant & Distribution
                                                                               | Allocation Contract
                                                                               v
                                                                      +------------------+
                                                                      | Offering Entity  |
                                                                      |      (TBD)       |
                                                                      +------------------+
```

1. **Software Development & Maintenance Agreement (Protremix ↔ Foundation):**
   - Outlines scope of work for Substrate runtime development, mobile wallet updates, and AMM DEX code maintenance.
   - Defines arm's-length service fees paid by Foundation to Protremix.
   - Assigns intellectual property (IP) rights and open-source licensing terms (e.g., Apache 2.0 / GPLv3).

2. **Token Allocation & Distribution Grant Agreement (Foundation ↔ Offering Entity):**
   - Authorizes Offering Entity to act as designated distributor for VRDX token public offerings.
   - Specifies exact VRDX token tranche allocations, vesting schedules, and price parameters.
   - Mandates strict compliance with target jurisdiction KYC/AML laws.

3. **Data Processing & Privacy Agreement (GDPR / UAE Data Law):**
   - Governs the handling of participant PII data collected during KYC/AML onboarding.
   - Ensures compliance with EU GDPR (Regulation 2016/679) and UAE Data Protection Law.

---

## 6. Change of Control Procedures & Contingency Protocols

### 6.1 Key Migration & Progressive Decentralization Schedule
- **Phase 1 (Testnet - Current):** Protremix holds SUDO key and core telemetry for rapid bug fixing.
- **Phase 2 (Mainnet Launch):** SUDO key is permanently removed (`pallet_sudo` removed from Substrate runtime). Control transitions to 3-of-5 Council Multi-sig.
- **Phase 3 (Full Decentralization):** Governance transitions to on-chain VRDX token holder voting for runtime upgrades and treasury spending.

### 6.2 Emergency Incident Response & Key Compromise Protocol
- If 1 of 5 treasury multi-sig keys is compromised, remaining 4 signatories execute an immediate key-rotation transaction to revoke the compromised key.
- If DNS or public communications channels are compromised, official backup communications channels published on GitHub and Substrate Telemetry will be activated within 2 hours.

### 6.3 Insolvency & Regulatory Firewall
- In the event of legal action, regulatory inquiry, or insolvency affecting Protremix S.L. in Spain, the Foundation in the UAE and the Offering Entity shall operate completely independently, ensuring continuity of the Verdis Chain blockchain network and token treasury.
