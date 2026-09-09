# Verdis Chain Economic Source of Truth

**Document Version:** 1.0.0  
**Last Updated:** August 13, 2026  
**Status:** Authoritative Specification (Ratified by Project Owner Rojs Gordons)  
**Repository Path:** `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md`  

---

## Document Overview & Methodology

This document serves as the absolute, authoritative economic and tokenomic specification for the **Verdis Chain** network (`VRDX`). Every parameter, allocation, formula, and financial model presented herein is backed by five required tracking attributes:

1. **SOURCE**: The originating authority, stakeholder approval, or technical specification.
2. **FORMULA**: The exact mathematical calculation or logic determining the figure.
3. **CODE LOCATION**: The specific source file, constant, struct, or configuration in the codebase.
4. **DOCUMENT LOCATION**: Supporting references in internal documentation, chain specifications, or manifest files.
5. **STATUS**: The current state of verification (e.g., `Approved`, `Verified On-Chain`, `Proposed`, `Requires Legal Counsel`, `Requires Documentation`).

---

## 1. Legal Entity and Jurisdiction

> **STATUS: REQUIRES COUNSEL**

| Attribute | Specification Details |
|---|---|
| **Project Owner / Founder** | Rojs Gordons (Co-Founder & CEO / Marketing Lead) |
| **Development Company** | Protremix (Software Development Company) |
| **Key Leadership & Legal Team** | • **Dorian Jean**: CEO / Founder<br>• **Mark Jamestown**: Chief Technology Officer (CTO)<br>• **Elizabeth Jefferson**: Head of Product<br>• **Rojs Gordons**: Co-Founder & Community/Marketing Lead<br>• **Maria Dolores Marquez de Prado**: Legal Counsel<br>• **Ignacio Martinez-Arrieta**: Legal & Compliance Officer |
| **Operational Region & Timezone** | Europe (Europe/Madrid Timezone) |
| **Primary Network Servers** | • `verdischain.com` (IP: `91.98.160.145`) — Primary Portal & Node<br>• `evolvixos.com` (IP: `62.238.61.145`) — Infrastructure & Core Services |
| **Incorporation Entity** | Protremix / TBD Legal Entity |
| **Jurisdiction of Issuance** | TO BE DETERMINED — Requires formal legal opinion and jurisdiction structuring |
| **Source** | Executive Team Directives & Corporate Records |
| **Formula** | N/A (Organizational Structure) |
| **Code Location** | N/A |
| **Document Location** | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md`, `README.md` |
| **Verification Status** | **REQUIRES COUNSEL** — Requires final opinion from qualified legal counsel (Maria Dolores Marquez de Prado & Ignacio Martinez-Arrieta) |

---

## 2. Token Classification

> **STATUS: REQUIRES COUNSEL**

| Assessment Parameter | Analysis & Status |
|---|---|
| **Token Identifier** | VRDX (Native Utility Token) |
| **EU MiCA Classification** | Under evaluation for Utility Token classification under EU Markets in Crypto-Assets (MiCA) regulation. |
| **US SEC Howey Test Evaluation** | Subject to legal review; designed as a decentralised functional utility token for gas fees, governance, and consensus participation. |
| **Swiss FINMA Guidelines** | Asset vs. Utility vs. Payment token classification under Swiss financial market law pending review. |
| **Primary Functional Utility** | 1. Payment of network execution fees (gas).<br>2. Validator staking and DPoS consensus security.<br>3. On-chain DAO governance voting.<br>4. Native DEX liquidity pairing and AMM routing. |
| **Legal Opinion Status** | Pending formal written legal opinion from legal team (Maria Dolores Marquez de Prado & Ignacio Martinez-Arrieta) prior to TGE. |
| **Source** | Legal & Compliance Working Group |
| **Formula** | N/A (Regulatory Classification Framework) |
| **Code Location** | N/A |
| **Document Location** | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` |
| **Verification Status** | **REQUIRES COUNSEL** — Mandatory legal clearance required prior to token distribution |

---

## 3. Maximum Supply and Issuance

| Parameter | Specification | Source | Formula | Code Location | Document Location | Status |
|---|---|---|---|---|---|---|
| **Token Ticker** | VRDX (NOT VERDIS) | Project Spec | N/A | `runtime/src/lib.rs` (L137) | `docs/data-manifest.md` (L10) | Approved |
| **Token Decimals** | 9 | Substrate Spec | `1 VRDX = 10^9 Planck` | `runtime/src/lib.rs` (L135) | `docs/data-manifest.md` (L12) | Verified |
| **Planck Multiplier** | 1,000,000,000 Planck | Substrate Balance | `10^9 Planck / VRDX` | `runtime/src/lib.rs` (L135 `UNITS`) | `docs/data-manifest.md` (L16) | Verified |
| **Maximum Supply** | 100,000,000,000 VRDX | Project Owner Approval | `100,000,000,000 * 10^9 Planck` | `runtime/src/lib.rs` (L137 `TOTAL_SUPPLY`) | `chain-specs/mainnet-plain.json` (`maxSupply`) | Approved / Verified |
| **SS58 Address Prefix** | 909 | Substrate Registry | Substrate Address Format | `runtime/src/lib.rs` (L147 `SS58Prefix`) | `docs/data-manifest.md` (L13) | Verified |
| **Target Block Time** | 6.0 seconds | Consensus Spec | `6000 milliseconds` | `runtime/src/lib.rs` (L132 `MILLISECS_PER_BLOCK`) | `docs/data-manifest.md` (L27) | Verified |
| **Block Reward Emission** | 342 VRDX / block | Economic Model | `342 * 10^9 Planck / block` | `runtime/src/lib.rs` (L584 `BlockReward`) | `docs/data-manifest.md` | Verified |
| **Annual Emission Rate** | ~1,798,783,200 VRDX / year | Inflation Formula | `(365.25 * 86400 / 6) * 342` | `runtime/src/lib.rs` (L584) & `pallets/tokenomics/src/lib.rs` | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Verified |
| **Annual Inflation Rate** | ~1.80% / year | Annual Emission Ratio | `1.798B VRDX / 100B VRDX` | `pallets/tokenomics/src/economic_invariants.rs` (L215) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Verified |

---

## 4. Allocation Table (All 9 Categories)

### Master Summary Table

| Category | Allocation (VRDX) | Percentage | Vesting / Lock Overview | Status |
|---|---|---|---|---|
| **Ecosystem & Developer Grants** | 25,000,000,000 VRDX | 25.0% | Governance-controlled linear release | Approved |
| **PoS Staking Rewards** | 20,000,000,000 VRDX | 20.0% | Emitted per block (342 VRDX/block) | Approved |
| **Treasury** | 20,000,000,000 VRDX | 20.0% | DAO multi-sig & council governed (updated from 15B) | Approved |
| **Development** | 10,000,000,000 VRDX | 10.0% | Milestone-based engineering unlocks | Approved |
| **Liquidity** | 10,000,000,000 VRDX | 10.0% | Initial DEX pools & CEX market making | Approved |
| **Community** | 5,000,000,000 VRDX | 5.0% | Airdrops, user incentives, community programs | Approved |
| **Seed / Strategic** | 3,000,000,000 VRDX | 3.0% | 365-day cliff, 730 days linear vesting | Approved / Spec |
| **Public Presale** | 2,000,000,000 VRDX | 2.0% | 180-day cliff, 365 days linear vesting | Approved / Spec |
| **Team & Advisors** | 5,000,000,000 VRDX | 5.0% | 365-day cliff, 1095 days linear vesting | Approved / Spec |
| **TOTAL** | **100,000,000,000 VRDX** | **100.0%** | **Full 100B Supply Distributed** | **Approved** |

---

### Detailed Allocation Category Tables

#### Allocation 1: Ecosystem & Developer Grants
| Metadata Field | Value / Details |
|---|---|
| **Category Name** | Ecosystem & Developer Grants |
| **Allocation Amount** | 25,000,000,000 VRDX |
| **Percentage of Total Supply** | 25.0% |
| **Source** | Confirmed & Approved by Project Owner Rojs Gordons |
| **Formula** | `100,000,000,000 VRDX * 0.250 = 25,000,000,000 VRDX` |
| **Code Location** | `pallets/tokenomics/src/lib.rs` & `pallets/tokenomics/src/economic_invariants.rs` |
| **Document Location** | `docs/data-manifest.md` (L20), `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` |
| **Status** | Approved |

#### Allocation 2: PoS Staking Rewards
| Metadata Field | Value / Details |
|---|---|
| **Category Name** | PoS Staking Rewards |
| **Allocation Amount** | 20,000,000,000 VRDX |
| **Percentage of Total Supply** | 20.0% |
| **Source** | Confirmed & Approved by Project Owner Rojs Gordons |
| **Formula** | `100,000,000,000 VRDX * 0.200 = 20,000,000,000 VRDX` |
| **Code Location** | `runtime/src/lib.rs` (L584 `BlockReward`), `pallets/dpos/src/lib.rs` (L968) |
| **Document Location** | `docs/data-manifest.md` (L21), `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` |
| **Status** | Approved |

#### Allocation 3: Treasury
| Metadata Field | Value / Details |
|---|---|
| **Category Name** | Treasury |
| **Allocation Amount** | 20,000,000,000 VRDX *(Note: Increased from 15B to 20B to finalize exact 100B distribution)* |
| **Percentage of Total Supply** | 20.0% |
| **Source** | Confirmed & Approved by Project Owner Rojs Gordons |
| **Formula** | `100,000,000,000 VRDX * 0.200 = 20,000,000,000 VRDX` |
| **Code Location** | `runtime/src/lib.rs` (L1252 `GreenTreasuryPalletId`), `pallets/tokenomics/src/lib.rs` |
| **Document Location** | `docs/data-manifest.md` (L22 - updated), `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` |
| **Status** | Approved |

#### Allocation 4: Development
| Metadata Field | Value / Details |
|---|---|
| **Category Name** | Development |
| **Allocation Amount** | 10,000,000,000 VRDX |
| **Percentage of Total Supply** | 10.0% |
| **Source** | Confirmed & Approved by Project Owner Rojs Gordons |
| **Formula** | `100,000,000,000 VRDX * 0.100 = 10,000,000,000 VRDX` |
| **Code Location** | `pallets/tokenomics/src/lib.rs` & `pallets/tokenomics/src/economic_invariants.rs` |
| **Document Location** | `docs/data-manifest.md` (L23), `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` |
| **Status** | Approved |

#### Allocation 5: Liquidity
| Metadata Field | Value / Details |
|---|---|
| **Category Name** | Liquidity |
| **Allocation Amount** | 10,000,000,000 VRDX |
| **Percentage of Total Supply** | 10.0% |
| **Source** | Confirmed & Approved by Project Owner Rojs Gordons |
| **Formula** | `100,000,000,000 VRDX * 0.100 = 10,000,000,000 VRDX` |
| **Code Location** | `pallets/amm-dex/src/lib.rs` & `pallets/tokenomics/src/lib.rs` |
| **Document Location** | `docs/data-manifest.md` (L24), `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` |
| **Status** | Approved |

#### Allocation 6: Community
| Metadata Field | Value / Details |
|---|---|
| **Category Name** | Community |
| **Allocation Amount** | 5,000,000,000 VRDX |
| **Percentage of Total Supply** | 5.0% |
| **Source** | Confirmed & Approved by Project Owner Rojs Gordons |
| **Formula** | `100,000,000,000 VRDX * 0.050 = 5,000,000,000 VRDX` |
| **Code Location** | `pallets/tokenomics/src/lib.rs` & `pallets/tokenomics/src/economic_invariants.rs` |
| **Document Location** | `docs/data-manifest.md` (L25), `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` |
| **Status** | Approved |

#### Allocation 7: Seed / Strategic
| Metadata Field | Value / Details |
|---|---|
| **Category Name** | Seed / Strategic |
| **Allocation Amount** | 3,000,000,000 VRDX |
| **Percentage of Total Supply** | 3.0% |
| **Source** | Confirmed & Approved by Project Owner Rojs Gordons |
| **Formula** | `100,000,000,000 VRDX * 0.030 = 3,000,000,000 VRDX` |
| **Code Location** | `chain-specs/mainnet-plain.json` (`vestingSchedules`: `seed`), `pallets/vesting/src/lib.rs` |
| **Document Location** | `docs/data-manifest.md` (L26), `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` |
| **Status** | Approved / Verified in Chain Spec |

#### Allocation 8: Public Presale
| Metadata Field | Value / Details |
|---|---|
| **Category Name** | Public Presale |
| **Allocation Amount** | 2,000,000,000 VRDX |
| **Percentage of Total Supply** | 2.0% |
| **Source** | Confirmed & Approved by Project Owner Rojs Gordons |
| **Formula** | `100,000,000,000 VRDX * 0.020 = 2,000,000,000 VRDX` |
| **Code Location** | `chain-specs/mainnet-plain.json` (`vestingSchedules`: `presale`), `pallets/presale/src/lib.rs` |
| **Document Location** | `docs/data-manifest.md` (L27), `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` |
| **Status** | Approved / Verified in Chain Spec |

#### Allocation 9: Team & Advisors
| Metadata Field | Value / Details |
|---|---|
| **Category Name** | Team & Advisors |
| **Allocation Amount** | 5,000,000,000 VRDX |
| **Percentage of Total Supply** | 5.0% |
| **Source** | Confirmed & Approved by Project Owner Rojs Gordons |
| **Formula** | `100,000,000,000 VRDX * 0.050 = 5,000,000,000 VRDX` |
| **Code Location** | `chain-specs/mainnet-plain.json` (`vestingSchedules`: `team`), `pallets/vesting/src/lib.rs` |
| **Document Location** | `docs/data-manifest.md` (L28), `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` |
| **Status** | Approved / Verified in Chain Spec |

---

## 5. Fundraising

| Fundraising Round | Token Allocation | Price per VRDX | Total USD Raised | Source | Formula | Code Location | Document Location | Status |
|---|---|---|---|---|---|---|---|---|
| **Seed / Strategic** | 3,000,000,000 VRDX | $0.0015 | $4,500,000 | Project Spec | `3,000,000,000 * 0.0015` | `pallets/presale/src/lib.rs` & `chain-specs/mainnet-plain.json` | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Approved |
| **Community Round** | 1,000,000,000 VRDX | $0.0030 | $3,000,000 | Project Spec | `1,000,000,000 * 0.0030` | `pallets/presale/src/lib.rs` | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Approved |
| **Public Presale** | 2,000,000,000 VRDX | $0.0040 | $8,000,000 | Project Spec | `2,000,000,000 * 0.0040` | `pallets/presale/src/lib.rs` & `chain-specs/mainnet-plain.json` | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Approved |
| **TGE / IDO Round** | 500,000,000 VRDX | $0.0050 | $2,500,000 | Project Spec | `500,000,000 * 0.0050` | `pallets/presale/src/lib.rs` | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Approved |
| **TOTAL FUNDRAISING** | **6,500,000,000 VRDX** | **—** | **$18,000,000** | **Aggregated Roster** | `Sum(USD Raised)` | **`pallets/presale/src/lib.rs`** | **`docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md`** | **Approved** |

### Aggregate Valuation Metrics

| Metric | Value | Source | Formula | Code Location | Document Location | Status |
|---|---|---|---|---|---|---|
| **Total Raised (Hard Cap)** | $18,000,000 USD | Financial Plan | `$4.5M + $3.0M + $8.0M + $2.5M` | `pallets/presale/src/lib.rs` | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Approved |
| **Fully Diluted Valuation (FDV)** | $500,000,000 USD | Valuation Model | `100,000,000,000 VRDX * $0.0050` | `pallets/tokenomics/src/lib.rs` | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Approved |
| **Tokens Sold in Fundraising** | 6.50B VRDX (6.5% Supply) | Fundraising Model | `3.0B + 1.0B + 2.0B + 0.5B` | `chain-specs/mainnet-plain.json` | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Approved |

---

## 6. TGE / Circulating Supply

| Parameter | Value | Source | Formula | Code Location | Document Location | Status |
|---|---|---|---|---|---|---|
| **TGE Circulating Supply** | 8,000,000,000 VRDX | Chain Runtime Constant | `100B VRDX * 0.08` | `runtime/src/lib.rs` (L138 `CIRCULATING_SUPPLY`) | `chain-specs/mainnet-plain.json` (`circulatingSupply`) | Verified On-Chain |
| **TGE Circulating Percentage** | 8.0% of Total Supply | Tokenomics Spec | `8B / 100B * 100%` | `runtime/src/lib.rs` (L138) | `docs/data-manifest.md` | Verified |
| **Initial Circulating Market Cap** | $40,000,000 USD | Market Cap Model | `8,000,000,000 VRDX * $0.0050` | N/A | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Calculated |

### TGE Liquid Unlock Composition

| Unlock Segment | Liquid Amount (VRDX) | % Total Supply | Description & Purpose | Code Location | Status |
|---|---|---|---|---|---|
| **TGE / IDO Unlocked** | 500,000,000 VRDX | 0.5% | 100% liquid unlock at TGE for IDO participants | `pallets/presale/src/lib.rs` | Approved |
| **Initial Liquidity Seed** | 2,500,000,000 VRDX | 2.5% | Seeding native AMM DEX pools and CEX market making | `pallets/amm-dex/src/lib.rs` | Approved |
| **Ecosystem & Grants Liquid** | 5,000,000,000 VRDX | 5.0% | Initial operational grants, partnership pools, community drops | `pallets/tokenomics/src/lib.rs` | Approved |
| **TOTAL TGE CIRCULATING** | **8,000,000,000 VRDX** | **8.0%** | **Total initial liquid supply in circulation at block 0** | **`runtime/src/lib.rs` (L138)** | **Verified** |

---

## 7. Vesting Schedules

| Target Allocation | Total Tokens | Cliff Period | Linear Vesting Duration | Source | Formula | Code / Chain Spec Location | Document Location | Status |
|---|---|---|---|---|---|---|---|---|
| **Seed / Strategic** | 3,000,000,000 VRDX | 365 days (12 months) | 730 days (24 months) | Genesis Spec | `Linear per block after cliff` | `chain-specs/mainnet-plain.json` (`vestingSchedules`: `seed`) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Verified in Spec |
| **Public Presale** | 2,000,000,000 VRDX | 180 days (6 months) | 365 days (12 months) | Genesis Spec | `Linear per block after cliff` | `chain-specs/mainnet-plain.json` (`vestingSchedules`: `presale`) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Verified in Spec |
| **Team & Advisors** | 5,000,000,000 VRDX | 365 days (12 months) | 1095 days (36 months) | Genesis Spec | `Linear per block after cliff` | `chain-specs/mainnet-plain.json` (`vestingSchedules`: `team`) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Verified in Spec |

### Vesting Implementation Mechanics
- **Pallet**: `pallets/vesting/src/lib.rs`
- **Lock Identifier**: `VESTING_LOCK_ID` (`*b"v/vsting"`, L51)
- **Schedule Structure**: Defined via `VestingSchedule<Balance>` (L59) containing `vesting_days` (L62) and `cliff_days` (L63).
- **On-Chain Enforcement**: Enforced natively at the substrate runtime level via balance locks preventing transfers of unvested tokens.

---

## 8. Staking and Validator Economics

| Metric / Parameter | Value | Source | Formula | Code Location | Document Location | Status |
|---|---|---|---|---|---|---|
| **Consensus Mechanism** | DPoS (BABE + GRANDPA) | Architecture Spec | BABE block production + GRANDPA finality | `runtime/src/lib.rs` & `pallets/dpos/src/lib.rs` | `docs/ARCHITECTURE.md` | Verified |
| **Genesis Active Validators** | 21 validators | Consensus Spec | Fixed active genesis set | `runtime/src/lib.rs` (L582 `ValidatorCount`) | `docs/data-manifest.md` (L38) | Verified |
| **Max Validator Capacity** | Expandable to 200+ | Network Roadmap | Configured limit in runtime / pallet | `runtime/src/lib.rs` (L581 `MaxValidators` = 100, `pallets/dpos/src/lib.rs` L1172 = 1000) | `docs/data-manifest.md` | Verified |
| **Minimum Validator Stake** | 100,000,000 VRDX | Security Spec | `0.1% * 100B VRDX` | `runtime/src/lib.rs` (L580 `MinValidatorStake`) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Verified |
| **Max Stake Per Validator** | 1,000,000,000 VRDX | Sybil Protection | `1.0% * 100B VRDX` | `runtime/src/lib.rs` (L576 `MaxStakePerValidator`) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Verified |
| **Maximum Commission Cap** | 20% | Validator Protection | `20 / 100` | `runtime/src/lib.rs` (L578 `MaxCommission`) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Verified |
| **Block Reward Emission** | 342 VRDX / block | Economic Spec | `342 * 10^9 Planck` | `runtime/src/lib.rs` (L584 `BlockReward`), `pallets/dpos/src/lib.rs` (L969) | `docs/data-manifest.md` | Verified |
| **Native DEX Pools Target** | 6 initial pools | DEX Architecture | Configured pools (runtime max pool cap = 50) | `pallets/amm-dex/src/lib.rs` & `runtime/src/lib.rs` (L615 `MaxPools`) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Verified |
| **Green Score Range** | 1 to 5 | Eco Pallet Spec | Range `[1, 5]` | `runtime/src/lib.rs` (L701-702 `MinGreenScore`/`MaxGreenScore`) & `pallets/eco/src/lib.rs` (L638-639) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Verified |

---

## 9. Protocol Fee Model (PROPOSED)

> **STATUS: PROPOSED — SUBJECT TO GOVERNANCE & LEGAL REVIEW**

| Fee Routing Target | Proposed Share | Purpose & Mechanics | Source | Formula | Code Location | Document Location | Status |
|---|---|---|---|---|---|---|---|
| **Validators & Stakers** | 40.0% | Staking yield booster & validator operation incentive | Proposed Specification | `Total_Fee * 0.40` | `pallets/tokenomics/src/lib.rs` & `runtime/src/lib.rs` | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | **PROPOSED** |
| **Treasury (DAO)** | 30.0% | Reserve growth, security funds, public goods | Proposed Specification | `Total_Fee * 0.30` | `runtime/src/lib.rs` (L1252 `GreenTreasuryPalletId`) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | **PROPOSED** |
| **Ecosystem & Development** | 20.0% | Grants, core maintenance, tooling development | Proposed Specification | `Total_Fee * 0.20` | `pallets/tokenomics/src/lib.rs` | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | **PROPOSED** |
| **Permanent VRDX Burn** | 10.0% | Deflationary sink (permanent token retirement) | Proposed Specification | `Total_Fee * 0.10` | `pallets/fungible-tokens/src/lib.rs` (L369) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | **PROPOSED** |

### Default Transaction Fee Configuration
- **Default Transfer Fee Rate**: 50 Basis Points (0.50%)  
  *Code Reference*: `runtime/src/lib.rs` (L1254 `pub const DefaultTransferFeeBps: u32 = 50;`)
- **Priority Fee Multiplier**: 1000x Maximum Priority Fee  
  *Code Reference*: `runtime/src/lib.rs` (L1253 `pub const MaxPriorityFeeMultiplier: u32 = 1000;`)

---

## 10. Burn Mechanism

| Burn Component | Specification | Source | Formula | Code Location | Document Location | Status |
|---|---|---|---|---|---|---|
| **Supply Base Preservation** | Treasury Burn set to 0% in current runtime to preserve 100B base supply | Runtime Spec | `Permill::from_percent(0)` | `runtime/src/lib.rs` (L1082 `TreasuryBurn`) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Verified On-Chain |
| **Proposed Protocol Fee Burn** | 10.0% of all transaction and protocol fees burned permanently | Proposed Spec | `Burn_Amount = Transaction_Fee * 0.10` | `pallets/tokenomics/src/lib.rs` & `pallets/fungible-tokens/src/lib.rs` (L369) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | **PROPOSED** |
| **Native Burn Extrinsic** | Unconditional token burning function exposed in fungible tokens pallet | Pallet Function | `total_supply = total_supply - burn_amount` | `pallets/fungible-tokens/src/lib.rs` (L369 `pub fn burn`) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Verified |

---

## 11. Team Compensation

> **STATUS: REQUIRES DOCUMENTATION**

| Component | Specification | Source | Formula | Code Location | Document Location | Status |
|---|---|---|---|---|---|---|
| **Team Total Pool** | 5,000,000,000 VRDX (5.0% Total Supply) | Approved Allocation | `100B VRDX * 0.05` | `chain-specs/mainnet-plain.json` (`vestingSchedules`: `team`) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Approved Pool |
| **Individual Member Grant Roster** | Detailed individual allocation breakdown per executive/engineer | HR / Executive Board | Individual Grant Schedule | N/A (Internal Contracts) | N/A | **REQUIRES DOCUMENTATION** |
| **Vesting Enforcement** | 365 days cliff + 1095 days linear vesting | Genesis Spec | `Linear unlock over 36 months after 12-month cliff` | `chain-specs/mainnet-plain.json` & `pallets/vesting/src/lib.rs` | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Verified in Spec |
| **Executive Salaries & Bonuses** | Fiat/Token compensation packages for executives | Board HR Policy | Corporate HR Formula | N/A | N/A | **REQUIRES DOCUMENTATION** |

---

## 12. Treasury Spending Rules

| Governance Tier | Transaction Threshold | Approval Requirement | Source | Formula | Code Location | Document Location | Status |
|---|---|---|---|---|---|---|---|
| **Micro Grants & Operational Costs** | < 1,000,000 VRDX | Multi-Sig Committee (3 of 5 signatures) | Treasury Rules | `Amount < 1,000,000 VRDX` | `runtime/src/lib.rs` (L1252 `GreenTreasuryPalletId`) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Approved |
| **Medium Grants & Development** | 1,000,000 - 50,000,000 VRDX | Council Majority Vote (Simple Majority) | Governance Spec | `1M VRDX <= Amount <= 50M VRDX` | `runtime/src/lib.rs` (`pallet_collective`/`council`) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Approved |
| **Major Ecosystem Allocations** | > 50,000,000 VRDX | Full On-Chain Referendum & Token Holder Vote | DAO Governance | `Amount > 50,000,000 VRDX` | `runtime/src/lib.rs` (`pallet_democracy`) | `docs/VERDISCHAIN_ECONOMIC_SOURCE_OF_TRUTH.md` | Approved |

### Treasury Infrastructure & Control
- **Treasury Pallet ID**: `PalletId(*b"vrds/trs")`  
  *Code Reference*: `runtime/src/lib.rs` (L1252)
- **Governance Modules**: Substrate `pallet_treasury`, `pallet_collective` (Council), and `pallet_democracy`.
- **Transparency Mandate**: All expenditures must be published on-chain with attached IPFS/Arweave proposal manifests.

---
