# VARA Activity & Regulatory Classification Matrix

**Project:** Verdis Chain (`VRDX`)  
**Target Jurisdiction:** Dubai, United Arab Emirates (Virtual Assets Regulatory Authority - VARA)  
**Document Type:** Comprehensive Regulatory Mapping & Activity Grid  
**Status:** **UNDETERMINED — ALL POSITIONS PENDING FORMAL LEGAL COUNSEL REVIEW**  

---

## 1. Executive Summary & Purpose of Matrix

This document provides a structured activity-by-activity mapping for all 16 technical and operational capabilities planned within the Verdis Chain ecosystem. Each activity is evaluated against the regulatory categories set forth under Dubai Law No. (4) of 2022 and VARA's Virtual Assets and Related Activities Regulations 2023.

### Column Standard Definitions
- **Activity:** The functional name of the technical or operational activity.
- **What Verdis Does:** Concrete technical breakdown of the pallet, code module, or operational task.
- **Entity:** The corporate entity performing or hosting the activity (Protremix Spain, UAE Foundation, or Offering SPV).
- **Users:** Primary counterparties, network participants, or end-users.
- **Money/Token Flow:** Financial inputs, outputs, token minting, lockups, or gas fee deductions.
- **Possible Regulatory Classification:** Potential VARA Rulebook category [Marked **UNDETERMINED**].
- **Evidence:** File paths, code modules, configuration files, or server IP endpoints.
- **Question for Counsel:** Formulated legal question for VARA counsel determination.

---

## 2. Master Activity Assessment Table

| Activity | What Verdis Does | Entity | Users | Money/Token Flow | Possible Regulatory Classification | Evidence | Question for Counsel |
|---|---|---|---|---|---|---|---|
| **1. VRDX Token Issuance** | Minting 100B native tokens at genesis via Substrate `pallet-balances` | UAE Foundation / Offering SPV | Network users & buyers | Genesis allocation to treasury, vesting contracts, and pools | Virtual Asset Issuance [UNDETERMINED] | `chain_spec.rs`, `pallet-balances`, `add_tokenomics_tests.py` | Does genesis minting of a Layer-1 native utility token require prior VARA approval or whitepaper clearance? |
| **2. Public Token Sale** | Selling VRDX tokens for USDT/USDC/ETH in seed, presale, and public IDO phases | Token Offering Entity (SPV) | Global purchasers & investors | Purchaser pays USDT/USDC -> Entity receives funds -> Issues locked VRDX | Virtual Asset Distribution & Issuance [UNDETERMINED] | `add_ido.py`, `add_tge_vesting.py`, `audit-homepage-sale.txt` | Can a Dubai-domiciled entity conduct a token sale, and what whitepaper registration/approval process is mandated? |
| **3. Decentralized Exchange (DEX)** | Automated Market Maker (`pallet-dex`) executing peer-to-peer token swaps without order books | Autonomous Substrate Runtime / Protremix dev | Peer-to-peer traders & LPs | Users deposit token pairs to pools; swap fees auto-deducted in VRDX | Virtual Asset Exchange Services [UNDETERMINED] | `amm_dex_benchmarking.rs`, `alt-pallet/src/lib.rs` | Does deploying an autonomous open-source AMM pallet classify as operating a Virtual Asset Exchange under VARA? |
| **4. Non-Custodial Web Wallet** | Web client (`App.tsx`, `Sr25519Service.kt`) generating sr25519/ed25519 keys locally in browser | Protremix S.L. (Software Publisher) | Self-custody wallet users | No money flow through entity; user signs transactions client-side | Technology Software Provision [UNDETERMINED] | `Sr25519Service.kt`, `account_abstraction.js`, `App.tsx` | Is publishing open-source, unhosted web wallet software subject to VARA licensing or exemption filing? |
| **5. Self-Custody Architecture** | Complete self-custody model where users retain exclusive control over private seed phrases | None (Protocol User Self-Custody) | End users | Private keys never transmitted or stored on servers | Virtual Asset Custody Services [Exemption UNDETERMINED] | `Sr25519Service.kt`, Security Audit Reports | Does complete non-custodial architecture conclusively exempt the developer from Custody Services licensing? |
| **6. On-Chain Transfer Services** | Processing native peer-to-peer VRDX transfers via Substrate consensus nodes | Decentralized Validator Network | Senders & recipients | Direct ledger state mutation; gas fees paid in VRDX | Virtual Asset Transfer & Settlement Services [UNDETERMINED] | `pallet-balances`, block execution logs | Is node-level transaction relay and block settlement categorized as a VARA Transfer & Settlement service? |
| **7. DPoS Staking Mechanism** | Token locking in `pallet-staking` to delegate voting power to consensus validators | Protocol Runtime / Token Holders | Nominators & Validators | Tokens locked on-chain; staking rewards generated via inflation | Virtual Asset Management & Investment Services [UNDETERMINED] | `pallet-staking`, `audit_data_validators.json` | Are protocol-level DPoS staking rewards treated as regulated yield generation or collective investment schemes? |
| **8. Validator Node Operation** | Operating core BABE/GRANDPA consensus nodes producing block proposals | UAE Foundation / Protremix / Independent Operators | Blockchain Network | Operators spend hosting costs -> Receive VRDX block rewards | Virtual Asset Infrastructure / Node Operation [UNDETERMINED] | `Dockerfile.worker`, `Dockerfile.gateway`, server `91.98.160.145` | Does operating a validation server physically located or managed from Dubai require a VARA commercial license? |
| **9. Brokerage & Swap UI Routing** | Web interface facilitating swap parameter construction for execution on `pallet-dex` | Protremix S.L. / UAE Foundation | Frontend Web App Users | Interface constructs RPC payload; user executes directly with node | Virtual Asset Broker-Dealer Services [UNDETERMINED] | `LandingCTA.tsx`, `add_sections.py`, `app.js` | Does providing a web user interface that interacts with an on-chain AMM constitute Broker-Dealer activity? |
| **10. RPC & API Infrastructure** | Hosting public HTTP/WebSocket RPC nodes providing ledger queries and TX submission | Protremix S.L. / UAE Foundation | Developers, Explorers, App Users | Free query access / rate-limited RPC endpoints | Virtual Asset IT Infrastructure / Advisory [UNDETERMINED] | `add_endpoints.py`, `add_sse_endpoint.sh`, `api.ts` | Does operating public node RPC infrastructure servicing UAE users trigger VARA regulatory oversight? |
| **11. On-Chain Governance** | Token-weighted voting (`pallet-governance`) for runtime upgrades and parameter tweaks | Decentralized Community / Token Holders | VRDX Token Holders | Proposal deposits locked in VRDX; refunded or burned upon vote outcome | Unregulated DAO / Governance Framework [UNDETERMINED] | `pallet-governance`, voting execution specs | How does VARA regulate foundation entities executing runtime code upgrades passed by DAO token votes? |
| **12. On-Chain Treasury Management** | Managing protocol treasury pallet funds via a 3-of-5 multisig council | Planned UAE Foundation Council | Grant Recipients & Core Devs | Treasury allocates VRDX funds upon 3-of-5 multisig signature execution | Virtual Asset Management & Custody [UNDETERMINED] | `pallet-treasury`, multisig key management specs | What specific VARA licensing or personal keyholder liability applies to managing a 3-of-5 multisig treasury? |
| **13. Marketing & Promotion** | Publishing website, social media content, whitepapers, and promotional materials | Protremix S.L. / UAE Foundation | Global public & UAE residents | Promotional expenditures paid to media channels & agencies | VARA Administrative Order on Marketing & Advertising [UNDETERMINED] | `LandingCTA.tsx`, `LandingNavBar.tsx`, marketing scripts | What pre-approval, disclosures, and risk warnings are required before promoting VRDX to Dubai residents? |
| **14. Cross-Border Targeting** | Operating globally accessible web apps and node RPCs accessible to Dubai IPs | Protremix S.L. | Global crypto users | Cross-border peer-to-peer token transfers | Cross-Border Virtual Asset Provision [UNDETERMINED] | Server `91.98.160.145`, `verdischain.com` domain | What reverse-solicitation or geofencing measures must be deployed to avoid unintended VARA jurisdiction? |
| **15. TX Relay Signing Service** | Non-custodial transaction signing relay allowing gasless/meta-transactions | Protremix S.L. / Relay Operators | Mobile & Web Users | Relay submits signed payload to node; gas paid via fee arrangement | Virtual Asset Transfer / Brokerage Intermediation [UNDETERMINED] | `account_abstraction.js`, TX Relay backend code | Does operating a transaction relay for non-custodial meta-transactions trigger VARA transfer broker licensing? |
| **16. Eco/Green Scoring Engine** | Tracking energy metrics and issuing eco-scores to validators via pallet logic | Autonomous Protocol Engine | Validator Nodes | High eco-scores grant boosted validator selection probability | Unregulated Protocol Metric / Technical Function [UNDETERMINED] | `audit_data_eco.json`, eco-scoring pallet code | Does eco-scoring or carbon offset credit integration trigger environmental or virtual asset licensing? |

---

## 3. Detailed Individual Activity Legal Profiles

### Activity 1: Native Token Issuance (`VRDX`)
- **Technical Mechanism:** Hardcoded initial minting in Substrate genesis block (`chain_spec.rs`). Hard cap of 100,000,000,000 VRDX tokens with 9 decimal precision.
- **Performing Entity:** Verdis Protocol / UAE Foundation (Planned).
- **Target Counterparties:** Network ecosystem, node operators, public participants.
- **Financial Dynamics:** Pre-allocated genesis pools locked in runtime pallets (`pallet-treasury`, vesting contracts).
- **Possible Regulatory Classification:** Virtual Asset Issuance [UNDETERMINED].
- **Technical Evidence:** `chain_spec.rs`, `pallet-balances`, `add_tokenomics_tests.py`.
- **Formulated Question for Counsel:** Is genesis token creation for a native Layer-1 utility token classified as Virtual Asset Issuance under VARA FMP rules? Does pre-allocation to non-profit foundation reserves trigger prior registration requirements?

### Activity 2: Token Sale Operations (Seed, Presale, Public Sale)
- **Technical Mechanism:** Smart contract and Python automation scripts (`add_ido.py`, `add_tge_vesting.py`) handling multi-tier token sales with linear lockup enforcement.
- **Performing Entity:** Special Purpose Vehicle (Token Offering Entity) / UAE Foundation.
- **Target Counterparties:** Global retail buyers, accredited investors, Web3 funds.
- **Financial Dynamics:** Purchasers remit stablecoins (USDT/USDC) or crypto (ETH); receive locked VRDX claims.
- **Possible Regulatory Classification:** Virtual Asset Distribution & Issuance Services [UNDETERMINED].
- **Technical Evidence:** `add_ido.py`, `add_tge_vesting.py`, `audit-homepage-sale.txt`.
- **Formulated Question for Counsel:** Can a UAE-domiciled entity conduct a token sale targeting international purchasers? What Whitepaper approval, disclosure, and investor suitability rules apply under VARA regulations?

### Activity 3: Decentralized Exchange (`pallet-dex`)
- **Technical Mechanism:** Substrate runtime pallet implementing constant-product Automated Market Maker (AMM) liquidity pools, swap routing, and LP token accounting (`alt-pallet/src/lib.rs`).
- **Performing Entity:** Autonomous Substrate Protocol Runtime (Software authored by Protremix S.L.).
- **Target Counterparties:** Peer-to-peer liquidity providers and traders.
- **Financial Dynamics:** Automated pool trading fees (e.g., 0.3%) auto-collected and distributed to LP token holders.
- **Possible Regulatory Classification:** Virtual Asset Exchange Services [UNDETERMINED].
- **Technical Evidence:** `amm_dex_benchmarking.rs`, `alt-pallet/src/lib.rs`.
- **Formulated Question for Counsel:** Does deploying an open-source AMM pallet constitute operating an unlicensed Virtual Asset Exchange under VARA rules? Does software open-sourcing insulate developers from exchange operator liability?

### Activity 4: Non-Custodial Web Wallet Software
- **Technical Mechanism:** React/TypeScript web application (`App.tsx`, `Sr25519Service.kt`) utilizing local Web Crypto APIs for sr25519 key generation and transaction signing.
- **Performing Entity:** Protremix S.L. (Spain).
- **Target Counterparties:** Self-custody end users.
- **Financial Dynamics:** Free software distribution; zero fee collection or custody of user assets by developer.
- **Possible Regulatory Classification:** Unregulated Technology Software Provision [UNDETERMINED].
- **Technical Evidence:** `Sr25519Service.kt`, `account_abstraction.js`, `App.tsx`.
- **Formulated Question for Counsel:** Does providing unhosted web wallet software constitute a regulated Virtual Asset activity under VARA, or does it fall under the pure software developer exemption?

### Activity 5: Self-Custody Architecture & Key Storage
- **Technical Mechanism:** User seed phrases and private keys are encrypted locally on client devices (`account_abstraction.js`). Key material is never transmitted over network calls or saved on servers.
- **Performing Entity:** None (User Self-Custody).
- **Target Counterparties:** Individual token holders.
- **Financial Dynamics:** Direct user interaction with blockchain nodes.
- **Possible Regulatory Classification:** Virtual Asset Custody Services [Exemption UNDETERMINED].
- **Technical Evidence:** `Sr25519Service.kt`, Security Audit Reports.
- **Formulated Question for Counsel:** Does complete technical non-custody provide absolute immunity from VARA Virtual Asset Custody Services License requirements?

### Activity 6: On-Chain Transfer Services
- **Technical Mechanism:** Substrate `pallet-balances` handling peer-to-peer ledger state changes, gas fee deduction, and nonce management.
- **Performing Entity:** Decentralized Validator Network.
- **Target Counterparties:** Network senders and recipients.
- **Financial Dynamics:** Native gas fee paid in VRDX per transaction.
- **Possible Regulatory Classification:** Virtual Asset Transfer & Settlement Services [UNDETERMINED].
- **Technical Evidence:** `pallet-balances/src/lib.rs`, block execution logs.
- **Formulated Question for Counsel:** Is decentralized block validation and transfer execution classified as a regulated Transfer & Settlement service under VARA rules?

### Activity 7: Delegated Proof-of-Stake (DPoS) Staking
- **Technical Mechanism:** Token locking via `pallet-staking` where nominators bond VRDX to back validator candidates and share in block inflation rewards.
- **Performing Entity:** Protocol Staking Pallet / Independent Token Holders.
- **Target Counterparties:** Staking nominators and validator node operators.
- **Financial Dynamics:** Dynamic inflation emissions minted programmatically and distributed to stakers.
- **Possible Regulatory Classification:** Virtual Asset Management & Investment Services [UNDETERMINED].
- **Technical Evidence:** `pallet-staking/src/lib.rs`, `audit_data_validators.json`.
- **Formulated Question for Counsel:** Are native staking rewards treated as regulated yield generation or collective investment schemes under UAE financial laws?

### Activity 8: Validator Node Operation
- **Technical Mechanism:** Dockerized Substrate node binaries (`Dockerfile.worker`, `Dockerfile.gateway`) participating in BABE block authoring and GRANDPA finality consensus.
- **Performing Entity:** UAE Foundation, Protremix S.L., and independent global operators.
- **Target Counterparties:** Blockchain network consensus layer.
- **Financial Dynamics:** Operators incur infrastructure costs and earn VRDX block rewards.
- **Possible Regulatory Classification:** Virtual Asset Infrastructure Provider / IT Node Operation [UNDETERMINED].
- **Technical Evidence:** `Dockerfile.worker`, `Dockerfile.gateway`, server `91.98.160.145`.
- **Formulated Question for Counsel:** Does running a blockchain consensus validator node inside Dubai require a VARA commercial license or registration?

### Activity 9: Brokerage & Swap UI Routing
- **Technical Mechanism:** Web frontend interface (`LandingCTA.tsx`, `app.js`) that constructs swap RPC payloads for submission to `pallet-dex`.
- **Performing Entity:** Protremix S.L. / UAE Foundation.
- **Target Counterparties:** Web application users.
- **Financial Dynamics:** UI routes transactions without collecting intermediate markups or holding user funds.
- **Possible Regulatory Classification:** Virtual Asset Broker-Dealer Services [UNDETERMINED].
- **Technical Evidence:** `LandingCTA.tsx`, `add_sections.py`, `app.js`.
- **Formulated Question for Counsel:** Does hosting a web frontend that formats transactions for an on-chain AMM constitute regulated Broker-Dealer activity under VARA rules?

### Activity 10: Public RPC & API Node Hosting
- **Technical Mechanism:** HTTP and WebSocket RPC infrastructure (`add_endpoints.py`, `api.ts`) servicing blockchain state queries and transaction propagation.
- **Performing Entity:** Protremix S.L. / UAE Foundation.
- **Target Counterparties:** Developers, block explorers, end users.
- **Financial Dynamics:** Free public endpoint access or rate-limited API plans.
- **Possible Regulatory Classification:** IT Infrastructure Provision / Advisory Services [UNDETERMINED].
- **Technical Evidence:** `add_endpoints.py`, `add_sse_endpoint.sh`, `api.ts`.
- **Formulated Question for Counsel:** Does operating public RPC nodes accessible to Dubai residents trigger VARA IT infrastructure oversight or data privacy rules?

### Activity 11: On-Chain Governance & DAO Voting
- **Technical Mechanism:** Substrate `pallet-governance` enabling token-weighted voting on referenda, parameter changes, and Wasm runtime upgrades.
- **Performing Entity:** Decentralized VRDX Token Holder Community.
- **Target Counterparties:** Token holders holding locked voting power.
- **Financial Dynamics:** Proposal deposits locked and refunded or burned based on vote outcome.
- **Possible Regulatory Classification:** Unregulated Protocol DAO / Governance Framework [UNDETERMINED].
- **Technical Evidence:** `pallet-governance/src/lib.rs`, proposal execution benchmarks.
- **Formulated Question for Counsel:** How does VARA regulate foundation entities executing technical upgrades passed by on-chain token voting?

### Activity 12: Treasury Multisig Governance (3-of-5)
- **Technical Mechanism:** Protocol reserve treasury pallet (`pallet-treasury`) managed by a 3-of-5 multisig council key configuration.
- **Performing Entity:** Designated UAE Foundation Council Keyholders.
- **Target Counterparties:** Grant recipients, core contributors, auditors.
- **Financial Dynamics:** Treasury dispatches VRDX funds upon obtaining 3 out of 5 valid signatures.
- **Possible Regulatory Classification:** Virtual Asset Management & Custody [UNDETERMINED].
- **Technical Evidence:** `pallet-treasury/src/lib.rs`, multisig key management specs.
- **Formulated Question for Counsel:** Does holding 1 of 5 keys in a protocol treasury multisig constitute personal asset management or custody liability under UAE law?

### Activity 13: Marketing & Promotional Operations
- **Technical Mechanism:** Website copy, lightpapers, social media campaigns, and public announcements promoting Verdis Chain.
- **Performing Entity:** Protremix S.L. / UAE Foundation.
- **Target Counterparties:** Global public and UAE residents.
- **Financial Dynamics:** Promotional expenditures paid to media platforms and advertising networks.
- **Possible Regulatory Classification:** VARA Administrative Order on Marketing & Advertising [UNDETERMINED].
- **Technical Evidence:** `LandingCTA.tsx`, `LandingNavBar.tsx`, marketing scripts.
- **Formulated Question for Counsel:** What specific pre-approval filings, disclaimers, and risk warnings are required under VARA Administrative Orders on Marketing?

### Activity 14: Global Market Targeting & Cross-Border Offerings
- **Technical Mechanism:** Globally accessible public testnet endpoints (`verdischain.com`, IP: `91.98.160.145`) operating without geographic IP blocking.
- **Performing Entity:** Protremix S.L.
- **Target Counterparties:** Global crypto users.
- **Financial Dynamics:** Cross-border peer-to-peer token movements.
- **Possible Regulatory Classification:** Cross-Border Virtual Asset Provision [UNDETERMINED].
- **Technical Evidence:** Server `91.98.160.145`, `verdischain.com` domain.
- **Formulated Question for Counsel:** What reverse-solicitation or geofencing measures must be deployed to avoid unintended VARA jurisdiction?

### Activity 15: Non-Custodial TX Relay Signing Service
- **Technical Mechanism:** Meta-transaction relay script (`account_abstraction.js`) forwarding user-signed transaction payloads to consensus nodes.
- **Performing Entity:** Protremix S.L. / Relay Operators.
- **Target Counterparties:** Mobile and web wallet users.
- **Financial Dynamics:** Relay submits transaction paying gas; recovers fee from user via signed payload.
- **Possible Regulatory Classification:** Virtual Asset Transfer / Brokerage Intermediation [UNDETERMINED].
- **Technical Evidence:** `account_abstraction.js`, TX Relay backend code.
- **Formulated Question for Counsel:** Does running a non-custodial transaction signing relay trigger VARA Transfer or Brokerage licensing requirements?

### Activity 16: Eco/Green Scoring Protocol Engine
- **Technical Mechanism:** On-chain metric evaluation tracking validator energy efficiency and assigning eco-scores (`audit_data_eco.json`).
- **Performing Entity:** Autonomous Protocol Runtime.
- **Target Counterparties:** Validator node operators.
- **Financial Dynamics:** High eco-scores grant boosted validator selection probability and block rewards.
- **Possible Regulatory Classification:** Unregulated Protocol Metric / Technical Function [UNDETERMINED].
- **Technical Evidence:** `audit_data_eco.json`, eco-scoring pallet code.
- **Formulated Question for Counsel:** Does integrating eco-scoring or carbon tracking metrics trigger environmental disclosure or virtual asset regulatory obligations?

---

## 4. Corporate Entity Activity Responsibility Mapping

| Corporate Entity | Primary Responsible Activities | Legal Jurisdiction | Regulatory Strategy |
|---|---|---|---|
| **Protremix S.L.** | Activities 4, 9, 10, 14, 15 (Software engineering, UI hosting, RPC nodes) | Spain (EU) | Claim Open-Source Software Developer Safe Harbor; avoid asset custody. |
| **UAE Foundation (Planned)** | Activities 1, 7, 8, 11, 12, 13 (Ecosystem stewardship, Treasury multisig, Marketing) | Dubai, UAE | Apply for VARA FMP License or Exemption as Non-Profit Protocol Foundation. |
| **Token Offering SPV (Planned)** | Activity 2 (Token Sales, IDO, Presale distribution) | Cayman / BVI / UAE Free Zone | Register Whitepaper under VARA / offshore regulations for compliant offering. |

---
*End of VARA Activity Matrix — Prepared for VARA Legal Counsel Review*
