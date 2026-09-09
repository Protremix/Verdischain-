# VARA Legal Briefing Package: Verdis Chain Project

**Document Type:** Formal Instructions and Briefing Package for Qualified Legal Counsel  
**Target Jurisdiction:** Dubai, United Arab Emirates (Virtual Assets Regulatory Authority - VARA)  
**Project Name:** Verdis Chain  
**Native Token Ticker:** VRDX  
**Development Stage:** Testnet Operational Phase (Server IP: `91.98.160.145` / Domain: `verdischain.com`)  
**Core Architecture:** Substrate-based Layer-1 | 16 Custom Pallets | 503 Passing Unit & Integration Tests  
**Date of Preparation:** August 2026  

---

### IMPORTANT NOTICE & LEGAL DISCLAIMER
> **LEGAL NOTICE TO COUNSEL:** THIS DOCUMENT IS A PREPARATORY BRIEFING PACKAGE PREPARED EXCLUSIVELY FOR QUALIFIED LEGAL COUNSEL OPERATING IN DUBAI AND THE UNITED ARAB EMIRATES. IT DOES NOT CONSTITUTE A LEGAL OPINION, FORMAL LEGAL DETERMINATION, OR REGULATORY FILING. NEITHER PROTREMIX S.L. NOR ANY AFFILIATED ENTITIES OR PERSONS CLAIM OR ASSUME COMPLIANCE WITH VARA REGULATIONS, UAE FEDERAL LAWS, OR CBUAE/SCA RULES PRIOR TO FORMAL COUNSEL REVIEW AND ISSUANCE OF A FINAL LEGAL OPINION. ALL REGULATORY CLASSIFICATIONS, LICENSING REQUIREMENTS, AND LEGAL CONCLUSIONS SET FORTH HEREIN ARE MARKED AS **UNDETERMINED** PENDING FORMAL LEGAL ADVICE FROM LICENSED UAE COUNSEL.

---

## 1. Executive Summary & Project Overview

Verdis Chain is an enterprise-grade, specialized Substrate-based Layer-1 blockchain system engineered for high-throughput transaction processing, decentralized finance (DeFi), eco-performance tracking, and on-chain governance. The protocol relies on a Delegated Proof-of-Stake (DPoS) consensus model utilizing BABE block production and GRANDPA finality gadget, paired with a custom eco-scoring engine that incentivizes energy-efficient validator node operation.

### Key Technical & Protocol Parameters
- **Blockchain Framework:** Substrate (Rust-based Layer-1 modular blockchain framework)
- **Consensus Mechanism:** Delegated Proof-of-Stake (DPoS) with BABE block production and GRANDPA block finality
- **Native Utility Token:** VRDX
- **Total Token Supply:** 100,000,000,000 VRDX (100 Billion fixed max supply; hard-capped in genesis)
- **Token Precision:** 9 decimal places (`1 VRDX = 1,000,000,000 plancks`)
- **Core Runtime Architecture:** 16 custom modular pallets (including DEX AMM, Staking, Governance, Treasury, Eco-Scoring, Identity, Multisig, and Transaction Fees)
- **Operational Status:** Public Testnet active on host server `91.98.160.145` (`verdischain.com`)
- **Testing Verification:** 503 passing unit, benchmarking, integration, and security test cases
- **Client Ecosystem:** Non-custodial Web Wallet, Transaction Relay (TX Relay) non-custodial signing service, and WebSocket/HTTP RPC node endpoints

### Corporate & Entity Framework Strategy
To ensure appropriate legal isolation, operational efficiency, and regulatory compliance, the project structure involves three distinct corporate elements:
1. **Protremix S.L. (Development Entity):** A private limited company incorporated in Spain (EU Member State). Protremix acts purely as a software engineering and technology provider, developing open-source core node software, smart contracts/pallets, and frontend interfaces. Protremix does not intend to operate as an exchange, custodian, or financial broker.
2. **Verdis Chain Foundation (Planned UAE Entity):** A non-profit foundation entity planned for establishment in Dubai, UAE (e.g., within Dubai World Trade Centre / DWTC, DMCC, or DDA jurisdiction). The Foundation will oversee community governance, ecosystem developer grants, brand assets, and core protocol stewardship.
3. **Token Offering Entity (Planned SPV):** A dedicated Special Purpose Vehicle (SPV) planned for incorporation in an appropriate jurisdiction (to be determined upon counsel recommendation) to conduct token distribution, public sales, and private presale activities.

---

## 2. Dubai / UAE Jurisdiction Assumptions & Regulatory Framework Scope

This briefing assumes that key operational, governance, foundation management, marketing, or token ecosystem functions may be conducted from or directed towards the Emirate of Dubai, UAE. Consequently, the regulatory framework governed by the **Virtual Assets Regulatory Authority (VARA)** under Dubai Law No. (4) of 2022 and Cabinet Decision No. 111 of 2022 is directly applicable.

### VARA Jurisdictional Boundary Assumptions
- **Territorial Scope:** VARA exercises regulatory authority across all virtual asset activities throughout the Emirate of Dubai, including Special Development Zones and Free Zones, but excluding the Dubai International Financial Centre (DIFC).
- **Applicable Regulatory Baseline:** Virtual Assets and Related Activities Regulations 2023, encompassing Full Market Product (FMP) Regulations, Company Rulebooks, and specific Activity Rulebooks (Exchange, Custody, Broker-Dealer, Transfer & Settlement, Management & Investment, Advisory, and Issuance).
- **Federal UAE Alignment:** Compliance considerations relative to the Central Bank of the UAE (CBUAE) Stated Value Token (SVT) regulations and Securities and Commodities Authority (SCA) federal joint oversight.

---

## 3. Comprehensive Activity Breakdown & Legal Analysis Framework

The following section breaks down all planned Verdis Chain activities. For each activity, the briefing details what the software/project does, the performing entity, the user base, money and token flows, possible VARA classifications, available technical evidence, and the specific question formulated for legal counsel.

### Activity 1: VRDX Native Token Issuance
- **What Verdis Does:** Minting a fixed supply of 100 Billion VRDX native tokens at chain genesis via Substrate runtime configuration (`pallet-balances`).
- **Entity Performing It:** Verdis Protocol / Planned UAE Foundation / Token Offering SPV.
- **Users / Counterparties:** Protocol ecosystem, future token holders, node operators.
- **Money / Token Flow:** Genesis token allocation distributed to on-chain treasury, team vesting contracts, community staking reserves, and sale distribution pools. No direct cash flow at genesis minting.
- **Possible Regulatory Classification:** Virtual Asset Issuance / Anomaly Regulations [UNDETERMINED].
- **Technical Evidence:** `chain_spec.rs`, `pallet-balances/src/lib.rs`, `add_tokenomics_tests.py`.
- **Question for Counsel:** Does the initial genesis creation of a native Layer-1 utility token require prior VARA Virtual Asset Issuance clearance or Whitepaper approval if no immediate sale occurs?

### Activity 2: Token Sale Operations (Seed, Presale, IDO)
- **What Verdis Does:** Selling VRDX tokens to global purchasers in exchange for stablecoins (USDT/USDC) or crypto-assets (ETH/BNB) through structured sale rounds.
- **Entity Performing It:** Planned Token Offering SPV / UAE Foundation.
- **Users / Counterparties:** Retail purchasers, institutional investors, Web3 ecosystem funds.
- **Money / Token Flow:** Purchasers transfer USDT/USDC/ETH to SPV treasury addresses -> SPV credits purchasers with locked or vested VRDX tokens according to smart contract schedules.
- **Possible Regulatory Classification:** Virtual Asset Issuance & Public Offering Services [UNDETERMINED].
- **Technical Evidence:** `add_ido.py`, `add_tge_vesting.py`, `audit-homepage-sale.txt`.
- **Question for Counsel:** What specific Whitepaper filing, disclosure, and VARA prior approval requirements apply to selling VRDX tokens to purchasers residing in or accessed from Dubai?

### Activity 3: Decentralized Exchange (DEX AMM Pallet)
- **What Verdis Does:** Autonomous Automated Market Maker (`pallet-dex`) built directly into the Substrate runtime, enabling liquidity provision and algorithmic token swaps without an order book.
- **Entity Performing It:** Autonomous Substrate Runtime Protocol; code published by Protremix S.L.
- **Users / Counterparties:** Peer-to-peer traders and liquidity pool providers.
- **Money / Token Flow:** Users deposit token pairs into pallet liquidity pools; traders swap tokens against pools with automated pool fees (e.g., 0.3%) deducted and distributed to liquidity providers.
- **Possible Regulatory Classification:** Virtual Asset Exchange Services [UNDETERMINED].
- **Technical Evidence:** `alt-pallet/src/lib.rs`, `amm_dex_benchmarking.rs`, `pallet-dex` code.
- **Question for Counsel:** Does publishing open-source Wasm runtime code for an autonomous on-chain AMM DEX subject the code developers or Foundation to VARA Virtual Asset Exchange licensing?

### Activity 4: Web Wallet Client Provision
- **What Verdis Does:** Providing web-based user interface software (`App.tsx`, `Sr25519Service.kt`) that enables users to generate sr25519/ed25519 private keys locally in browser memory.
- **Entity Performing It:** Protremix S.L. (Software Publisher).
- **Users / Counterparties:** Self-custody end users.
- **Money / Token Flow:** Software is provided free of charge. Users interact directly with the blockchain RPC node. Software never receives, transmits, or stores user private keys or funds.
- **Possible Regulatory Classification:** Non-Custodial Technology Provision / Unregulated Software Distribution [UNDETERMINED].
- **Technical Evidence:** `Sr25519Service.kt`, `account_abstraction.js`, `App.tsx`.
- **Question for Counsel:** Does hosting a web frontend for non-custodial wallet key generation trigger VARA Virtual Asset Management or Custody rules, or does it qualify for technology provider exemption?

### Activity 5: Key Architecture & Non-Custodial Security Model
- **What Verdis Does:** Enforcing a strict non-custodial key architecture across all wallet applications where private keys are encrypted on user client devices.
- **Entity Performing It:** None (End-user local self-custody).
- **Users / Counterparties:** Blockchain network users.
- **Money / Token Flow:** Users sign transaction payloads locally using their own private keys and broadcast signed payloads directly to network consensus nodes.
- **Possible Regulatory Classification:** Virtual Asset Custody Services [Exemption UNDETERMINED].
- **Technical Evidence:** `Sr25519Service.kt`, `account_abstraction.js`, Security Audit Reports.
- **Question for Counsel:** Does the complete technical absence of server-side key escrow or administrative withdrawal authority fully exempt Verdis entities from VARA Virtual Asset Custody Services License obligations?

### Activity 6: On-Chain Transfer & Settlement Services
- **What Verdis Does:** Executing peer-to-peer token transfers across validator nodes using `pallet-balances` and transaction propagation algorithms.
- **Entity Performing It:** Decentralized Consensus Validator Network.
- **Users / Counterparties:** Transaction senders and recipients globally.
- **Money / Token Flow:** Sender submits signed balance transfer -> Nodes validate signatures and update ledger state -> Gas fees in VRDX deducted automatically.
- **Possible Regulatory Classification:** Virtual Asset Transfer & Settlement Services [UNDETERMINED].
- **Technical Evidence:** `pallet-balances/src/lib.rs`, Substrate block execution engine.
- **Question for Counsel:** Is decentralized blockchain transaction propagation and block validation classified as a regulated Transfer & Settlement Service under VARA rules?

### Activity 7: Delegated Proof-of-Stake (DPoS) Staking
- **What Verdis Does:** Allowing token holders to lock VRDX tokens on-chain (`pallet-staking`) to nominate validator nodes and receive block inflation rewards.
- **Entity Performing It:** Protocol Runtime Engine / Independent Token Holders.
- **Users / Counterparties:** Token nominators and validator node operators.
- **Money / Token Flow:** Nominators lock VRDX in staking pallet -> Runtime emits block rewards -> Rewards distributed proportionally to nominators and validators.
- **Possible Regulatory Classification:** Virtual Asset Management & Investment Services / Staking Guidelines [UNDETERMINED].
- **Technical Evidence:** `pallets/staking/src/lib.rs`, `audit_data_validators.json`.
- **Question for Counsel:** How does VARA regulate native protocol-level DPoS staking rewards, and does staking delegation trigger collective investment or asset management rules?

### Activity 8: Validator Node Operation
- **What Verdis Does:** Running core consensus validation servers (BABE/GRANDPA) that propose blocks, validate state transitions, and maintain network consensus.
- **Entity Performing It:** UAE Foundation, Protremix S.L., and third-party node operators worldwide.
- **Users / Counterparties:** Blockchain network.
- **Money / Token Flow:** Validator node operators incur hosting/electricity costs -> Earn block authoring rewards and transaction gas fees in VRDX.
- **Possible Regulatory Classification:** Virtual Asset Infrastructure Provider / IT Node Operation [UNDETERMINED].
- **Technical Evidence:** `Dockerfile.worker`, `Dockerfile.gateway`, Server Host `91.98.160.145`.
- **Question for Counsel:** Is operating a Substrate validator node physically located in or managed from Dubai considered a regulated Virtual Asset activity requiring VARA authorization?

### Activity 9: Brokerage & Swap Interface Routing
- **What Verdis Does:** Providing web UI routing and swap parameters that allow users to interface with `pallet-dex` liquidity pools.
- **Entity Performing It:** Protremix S.L. / UAE Foundation.
- **Users / Counterparties:** Frontend web application users.
- **Money / Token Flow:** Web UI formats transaction parameters into RPC calls; user signs payload and broadcasts to node. No intermediary asset holding or mark-up fee by UI.
- **Possible Regulatory Classification:** Virtual Asset Broker-Dealer Services [UNDETERMINED].
- **Technical Evidence:** `LandingCTA.tsx`, `add_sections.py`, `app.js`.
- **Question for Counsel:** Does hosting a web user interface that simplifies transaction formatting for an on-chain AMM constitute Broker-Dealer activity under VARA regulations?

### Activity 10: API & RPC Infrastructure Hosting
- **What Verdis Does:** Operating public WebSocket and HTTP RPC endpoints (`91.98.160.145`) allowing applications to query blockchain state and broadcast signed transactions.
- **Entity Performing It:** Protremix S.L. / UAE Foundation.
- **Users / Counterparties:** Developers, wallets, block explorers, and end users.
- **Money / Token Flow:** RPC nodes provide public data access free of charge or via rate-limited API keys.
- **Possible Regulatory Classification:** IT Infrastructure Provision / Advisory Services [UNDETERMINED].
- **Technical Evidence:** `add_endpoints.py`, `add_sse_endpoint.sh`, `api.ts`.
- **Question for Counsel:** Does operating public node RPC infrastructure servicing users in Dubai trigger VARA regulatory oversight or data privacy/log retention requirements?

### Activity 11: On-Chain Governance & Voting
- **What Verdis Does:** Token-weighted voting system (`pallet-governance`) enabling VRDX holders to vote on runtime code upgrades and parameter adjustments.
- **Entity Performing It:** Decentralized VRDX Token Holder Community.
- **Users / Counterparties:** Network token holders holding voting weight proportional to locked VRDX.
- **Money / Token Flow:** Proposal submitters deposit VRDX locks; deposits refunded upon successful vote or burned upon rejection.
- **Possible Regulatory Classification:** Unregulated Protocol DAO / Governance Framework [UNDETERMINED].
- **Technical Evidence:** `pallets/governance/src/lib.rs`, proposal execution benchmarks.
- **Question for Counsel:** What legal liabilities apply to foundation board members who execute Wasm runtime upgrades passed by an on-chain DAO token holder vote?

### Activity 12: On-Chain Treasury Management (3-of-5 Multisig)
- **What Verdis Does:** Managing protocol reserve funds in an on-chain treasury pallet controlled by a 3-of-5 multisig council.
- **Entity Performing It:** Designated Foundation Council Keyholders.
- **Users / Counterparties:** Developer grant recipients, ecosystem projects, security auditors.
- **Money / Token Flow:** Treasury releases VRDX tokens to recipient wallet addresses only upon receiving valid signatures from 3 out of 5 authorized council keys.
- **Possible Regulatory Classification:** Virtual Asset Management & Custody Services [UNDETERMINED].
- **Technical Evidence:** `pallets/treasury/src/lib.rs`, multisig key management specifications.
- **Question for Counsel:** Does serving as a keyholder in a 3-of-5 multisig controlling an on-chain protocol treasury constitute regulated Asset Management or Custody under VARA?

### Activity 13: Marketing, Advertising & Promotional Operations
- **What Verdis Does:** Publishing educational content, whitepapers, social media announcements, and promotional campaigns regarding Verdis Chain and VRDX.
- **Entity Performing It:** Protremix S.L. / UAE Foundation.
- **Users / Counterparties:** Global public, including Dubai and UAE residents.
- **Money / Token Flow:** Marketing expenses paid to agencies, media outlets, and advertising platforms.
- **Possible Regulatory Classification:** VARA Administrative Order on Virtual Asset Marketing, Advertising and Promotions [UNDETERMINED].
- **Technical Evidence:** `LandingCTA.tsx`, `LandingNavBar.tsx`, marketing scripts.
- **Question for Counsel:** What specific disclaimers, risk warnings, and prior VARA marketing authorization filings are mandatory before publishing promotional material targeting UAE residents?

### Activity 14: Global Market Targeting & Cross-Border Provision
- **What Verdis Does:** Operating globally accessible websites and RPC node infrastructure without geographic IP restrictions during testnet phase.
- **Entity Performing It:** Protremix S.L.
- **Users / Counterparties:** Crypto users worldwide.
- **Money / Token Flow:** Cross-border peer-to-peer token transfers and DEX trades.
- **Possible Regulatory Classification:** Cross-Border Virtual Asset Provision / Reverse Solicitation [UNDETERMINED].
- **Technical Evidence:** Global server infrastructure (`verdischain.com`, IP: `91.98.160.145`).
- **Question for Counsel:** What reverse-solicitation guidelines or geofencing measures must be implemented under VARA rules to avoid unauthorized targeting of retail investors in Dubai?

### Activity 15: Transaction Relay (TX Relay Non-Custodial Signer)
- **What Verdis Does:** Providing a gasless transaction relay service (`account_abstraction.js`) that forwards user-signed meta-transactions to node operators.
- **Entity Performing It:** Protremix S.L. / Relay Operators.
- **Users / Counterparties:** Mobile and web wallet end users.
- **Money / Token Flow:** Relay node pays native gas fee on behalf of user; user reimburses relay in VRDX or secondary token via signed payload.
- **Possible Regulatory Classification:** Virtual Asset Transfer / Brokerage Intermediation [UNDETERMINED].
- **Technical Evidence:** `account_abstraction.js`, TX Relay server implementation.
- **Question for Counsel:** Does running a meta-transaction relay for non-custodial signed payloads trigger VARA Brokerage or Transfer Service licensing requirements?

---

## 4. VARA Regulatory Overview & Knowledge Gaps

### Summary of Known VARA Regulations
Based on publicly available VARA regulatory publications (2023 Full Market Product Regulations):
1. **Licensing Categories:** VARA establishes separate license categories for Exchange Services, Custody Services, Broker-Dealer Services, Transfer & Settlement Services, Management & Investment Services, Advisory Services, and Virtual Asset Issuance.
2. **Marketing Directive:** Strict administrative rules govern all virtual asset marketing, requiring clear disclaimers, prohibition of misleading gain claims, and pre-authorization for public campaigns in Dubai.
3. **AML/CFT Framework:** Full compliance with UAE Federal Law No. (20) of 2018 on Anti-Money Laundering and FATF Travel Rule obligations for virtual asset transfers above threshold amounts.

### Key Matters for Legal Counsel Determination
Counsel must evaluate and advise on the following critical gaps:
- Whether an open-source Layer-1 blockchain foundation qualifies for specific exemptions under VARA's technology provider or decentralized protocol guidelines.
- The precise legal boundary separating software development (Protremix Spain) from virtual asset service provision (UAE Foundation).
- The regulatory process for obtaining Whitepaper approval or exemption for native token distribution.

---

## 5. Numbered Specific Questions for VARA Legal Counsel

Legal counsel is requested to provide explicit, numbered responses to the following 15 questions in their formal legal briefing output:

1. **Licensing Trigger Identification:** Which specific VARA FMP Category License(s) (if any) are required for the planned UAE Foundation?
2. **Token Issuance & Whitepaper Approval:** Is VRDX categorized as an "Approved Virtual Asset," and what process governs Whitepaper clearance under VARA Virtual Asset Issuance rules?
3. **Software Developer Safe Harbor:** Does Protremix S.L. (Spain) incur VARA regulatory jurisdiction solely by publishing open-source software accessed by Dubai residents?
4. **DEX AMM Operator Liability:** Is an autonomous Substrate AMM pallet considered a regulated Virtual Asset Exchange, and who is legally deemed the "operator"?
5. **Non-Custodial Exemption Scope:** Does client-side local private key generation (`Sr25519Service.kt`) conclusively exempt the project from VARA Custody Services licensing?
6. **Transaction Relay (TX Relay):** Does operating a gasless meta-transaction relay service trigger VARA Transfer or Brokerage licensing?
7. **Staking Yield Regulation:** Are protocol-level DPoS staking rewards subject to VARA Investment/Management rules or collective investment regulations?
8. **Validator Node Licensing:** Does operating a consensus validator node physically located in Dubai require a VARA commercial license or registration?
9. **Treasury Multisig Legal Exposure:** What individual legal liability attaches to council keyholders managing a 3-of-5 multisig on-chain protocol treasury?
10. **Marketing Compliance Requirements:** What specific disclaimers, risk warnings, and pre-approval filings are mandatory before launching marketing campaigns targeting Dubai residents?
11. **Reverse Solicitation Boundaries:** What criteria govern reverse solicitation under VARA for cross-border token distribution to Dubai-based users?
12. **Free Zone Entity Selection:** Is a Dubai World Trade Centre (DWTC), DMCC, or DDA foundation entity preferable for obtaining VARA approval?
13. **AML/CFT & Travel Rule Applicability:** How do FATF Travel Rule obligations apply to unhosted, non-custodial DEX and wallet transactions on Verdis Chain?
14. **Testnet Regulatory Exposure:** Does operating a public testnet (`91.98.160.145`) without monetary value trigger VARA oversight or registration requirements?
15. **Protocol Gas Fee Taxation & Licensing Impact:** Does taking a protocol-level transaction fee in native VRDX alter the regulatory classification of the blockchain operator?

---
*End of Briefing Package — Prepared for VARA Legal Counsel Review*
