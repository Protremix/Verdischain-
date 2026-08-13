# Python script to generate audit-homepage-sale.txt

audit_data = [
    # =========================================================================
    # PAGE 1: Homepage (/)
    # =========================================================================
    {
        "page": "Homepage (/)",
        "claim": "Testnet Live · Block ## · Node Live · 8 Active",
        "status": "needs verification - Block height displays raw template placeholder ('Block ##'), suggesting live node state is mock or unintegrated UI data.",
        "location": "Hero Section - Status Badge"
    },
    {
        "page": "Homepage (/)",
        "claim": "Layer-1 blockchain built with Substrate. Native DPoS consensus, AMM DEX, ink! smart contracts, and on-chain carbon credit tracking — powered by production-grade pallets in Rust.",
        "status": "needs verification - Describes core tech stack. Substrate/Rust architecture needs verification via repository inspection.",
        "location": "Hero Section - Subtitle"
    },
    {
        "page": "Homepage (/)",
        "claim": "DEX Volume -- -- 6 Pools Live",
        "status": "needs verification - DEX volume stats show empty placeholders ('--'), while claiming 6 pools are live.",
        "location": "Hero Section - DEX Volume Card"
    },
    {
        "page": "Homepage (/)",
        "claim": "Verdis Node Monitor v2.4 LIVE | Block Height #--- | Network TPS 2.4 | Active Peers --/14",
        "status": "needs verification - TPS (2.4) is static text; Block height (#---) and Active Peers (--/14) are unpopulated UI placeholders.",
        "location": "Hero Section - Node Monitor Widget"
    },
    {
        "page": "Homepage (/)",
        "claim": "Total Staked Balance VRDX Wallet ≈ $14,850 USD +12.4% 75% Staked",
        "status": "likely false - Wallet preview graphic shows mock balance ($14,850 USD) and return rate (+12.4%) prior to token launch/TGE.",
        "location": "Hero Section - Wallet Mobile Graphic"
    },
    {
        "page": "Homepage (/)",
        "claim": "Speed 6s blocks | Peers 8 Peers | Carbon 100% Net Zero",
        "status": "needs verification - 'Peers 8 Peers' conflicts with Node Monitor widget displaying '--/14'. 'Carbon 100% Net Zero' is an unverified environmental claim.",
        "location": "Hero Section - Quick Stats Cards"
    },
    {
        "page": "Homepage (/)",
        "claim": "0 Total Token Supply | 0 Runtime Pallets | 0 Tests Passing | 0 Production Pallets",
        "status": "needs verification - All dynamic counter metrics render as '0', indicating broken JavaScript API counters or unpopulated data.",
        "location": "Stats Counter Section"
    },
    {
        "page": "Homepage (/)",
        "claim": "Native DPoS Consensus: BABE block production + GRANDPA finality ... up to 21 validator slots.",
        "status": "likely true - Standard Substrate BABE/GRANDPA consensus parameter configuration.",
        "location": "Platform Features Section - DPoS Consensus Card"
    },
    {
        "page": "Homepage (/)",
        "claim": "AMM Decentralized Exchange: Native Automated Market Maker built directly into the chain. Swap tokens, provide liquidity, and earn fees — no external contracts needed.",
        "status": "needs verification - Claims chain-level native AMM DEX pallet.",
        "location": "Platform Features Section - AMM DEX Card"
    },
    {
        "page": "Homepage (/)",
        "claim": "Carbon Credit Tracking: On-chain carbon credits, green validator scoring, and reforestation logging. Every transaction contributes to measurable environmental impact.",
        "status": "needs verification - Claims custom eco-tracking runtime module.",
        "location": "Platform Features Section - Carbon Credit Tracking Card"
    },
    {
        "page": "Homepage (/)",
        "claim": "ink! Smart Contracts: Substrate-native smart contracts via pallet_contracts. Deploy ink! contracts compiled to WebAssembly with gas-metered execution and storage rent. ink! · WASM · Chain 909",
        "status": "needs verification - Claims Chain ID 909 and WASM contract execution via pallet_contracts.",
        "location": "Platform Features Section - ink! Smart Contracts Card"
    },
    {
        "page": "Homepage (/)",
        "claim": "Tokenomics & Vesting: 100B total supply with 12B investor allocation enforced on-chain. Vesting schedules with cliff periods, transfer restrictions, and mint/burn controls. 100B Supply · 12B Vesting",
        "status": "needs verification - Contradicts Tokenomics section on same page which lists Seed (3B) + Presale (2B) = 5B investor allocation (or 6.5B total public fundraising), NOT 12B.",
        "location": "Platform Features Section - Tokenomics Card"
    },
    {
        "page": "Homepage (/)",
        "claim": "Substrate + Rust Core: Built from scratch in Rust using Substrate. WASM runtime, JSON-RPC + gRPC, benchmarked weight files for 30+ pallets. Production-ready.",
        "status": "needs verification - Contradicts Architecture section on same page which lists 'Seven pallets' (7 pallets vs 30+ pallets). Also contradicts counter displaying '0 Production Pallets'.",
        "location": "Platform Features Section - Substrate Card"
    },
    {
        "page": "Homepage (/)",
        "claim": "Tokenomics Allocation: Ecosystem & Developer Grants 25B VRDX (25%), PoS Staking Rewards 20B VRDX (20%), Treasury 15B VRDX (15%), Development 10B VRDX (10%), Liquidity 10B VRDX (10%), Community 5B VRDX (5%), Seed / Strategic 3B VRDX (3%), Public Presale 2B VRDX (2%), Team & Advisors 5B VRDX (5%)",
        "status": "likely true - Sums correctly to 100B VRDX (100%).",
        "location": "Tokenomics Section - Supply Distribution List"
    },
    {
        "page": "Homepage (/)",
        "claim": "Public Presale: Public sale, 3-month cliff (2B VRDX)",
        "status": "needs verification - Contradicts Sale Page and Tokenomics Page which state Public Presale has 0 cliff (No cliff).",
        "location": "Tokenomics Section - Public Presale Item"
    },
    {
        "page": "Homepage (/)",
        "claim": "Team & Advisors: 12-month cliff, 42-month vesting (5B VRDX)",
        "status": "needs verification - Contradicts Sale and Tokenomics pages which state 12-month cliff + 36-month vesting = 48-month total vesting (42 months vs 48 months).",
        "location": "Tokenomics Section - Team & Advisors Item"
    },
    {
        "page": "Homepage (/)",
        "claim": "Architecture: Seven pallets, one ecosystem. Each pallet is independently benchmarked with real weight files. [01 DPoS Consensus (Live), 02 AMM DEX (Live), 03 Eco Module (Live), 04 ink! (Live), 05 Tokenomics (Live), 06 Vesting (Live), 07 Storage (Live)]",
        "status": "needs verification - Claims 7 specific pallets are Live and benchmarked, contradicting both '30+ pallets' claim and '0 Production Pallets' counter.",
        "location": "Architecture Section"
    },
    {
        "page": "Homepage (/)",
        "claim": "Green Validators: Top validators by green score (0x4f2a...8b9c #1 Green Score 98/100 99.8% uptime; 0x7a1b...3e4f #2 Green Score 96/100 11,203 blocks 99.5% uptime; 0x9c3d...1a2b #3 Green Score 94/100 10,891 blocks 99.2% uptime; 0x2e5f...7c8d #4 Green Score 91/100 9,447 blocks 98.9% uptime; 0x8b1c...5d6e #5 Green Score 89/100 8,712 blocks 98.5% uptime; 0x6d9e...2f3a #6 Green Score 87/100 7,895 blocks 97.8% uptime)",
        "status": "needs verification - Validator addresses and stats appear to be hardcoded UI mock data (#1 validator shows '#--- blocks').",
        "location": "Green Validators Section"
    },
    {
        "page": "Homepage (/)",
        "claim": "On-Chain Metrics: 0 Total Supply | 0 ink! Contracts | 0 Tests Passing | 0 Production Pallets",
        "status": "needs verification - Dynamic metrics render as '0', indicating unpopulated or broken API hooks.",
        "location": "On-Chain Metrics Section"
    },
    {
        "page": "Homepage (/)",
        "claim": "Roadmap Milestone 1: ✓ Completed Core Blockchain - 30+ pallets, ink! contracts, benchmarked weights",
        "status": "needs verification - Claims 30+ pallets completed, contradicting the 7 pallets architecture list.",
        "location": "Roadmap Section - Milestone 1"
    },
    {
        "page": "Homepage (/)",
        "claim": "Roadmap Milestone 2: ✓ Completed Verdiscan Explorer - Real-time block explorer, validator cards, WebSocket feed",
        "status": "needs verification - Claims Verdiscan block explorer is completed.",
        "location": "Roadmap Section - Milestone 2"
    },
    {
        "page": "Homepage (/)",
        "claim": "Roadmap Milestone 3: ● In Progress Premium Launch - SaaS interface, security audit done, SDK released, mobile wallet in development",
        "status": "likely false - Claims 'security audit done' and 'SDK released', but no audit report or SDK release links are provided.",
        "location": "Roadmap Section - Milestone 3"
    },
    {
        "page": "Homepage (/)",
        "claim": "Verdis Chain is the blockchain layer of the EvolvixOS ecosystem — an AI Engineering Operating System that builds, deploys, and secures software autonomously.",
        "status": "unverifiable - Strategic alignment claim with external EvolvixOS platform.",
        "location": "One Ecosystem Section"
    },
    {
        "page": "Homepage (/)",
        "claim": "EvolvixOS: AI Engineering OS with 5 autonomous agents that design, build, deploy, and secure software 24/7. GPT-4o Powered · 5 AI Agents · Auto-Deploy",
        "status": "unverifiable - External AI product specification claim.",
        "location": "One Ecosystem Section - EvolvixOS Card"
    },
    {
        "page": "Homepage (/)",
        "claim": "© 2026 Verdis Chain · Protremix · Open-source under MIT License | GDPR Compliant · Security",
        "status": "needs verification - Open-source licensing and GDPR compliance claims.",
        "location": "Footer Bottom"
    },
    {
        "page": "Homepage (/)",
        "claim": "Referral Program (link in footer)",
        "status": "needs verification - Listed under Community links in footer; no 10%/5%/2.5% reward structure text is stated on the Homepage body.",
        "location": "Footer - Community Navigation Column"
    },

    # =========================================================================
    # PAGE 2: Sale Page (/sale/)
    # =========================================================================
    {
        "page": "Sale page (/sale/)",
        "claim": "VRDX Token Sale — Seed Round Active",
        "status": "needs verification - States Seed round is currently active.",
        "location": "Hero Section - Sub-badge"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Seed Price $0.0015 | TGE Price $0.005 | Total Raised $18M | Current Round Price $0.0015 (70% discount to TGE)",
        "status": "contradictory - 'Total Raised $18M' contradicts 'Sold: 0 VRDX / Raised $0' in the active round box. $18M is the target raised across all 4 rounds combined ($4.5M + $3M + $8M + $2.5M), not funds already collected.",
        "location": "Hero Section - Stats Bar"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Sold: 0 VRDX (0% of 3B) | Hard Cap $4.5M | Raised $0",
        "status": "needs verification - Shows active Seed round has 0 VRDX sold and $0 raised toward $4.5M hard cap.",
        "location": "Hero Section - Current Round Card"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Round 1 Ends In 21d 06h 32m",
        "status": "needs verification - Hardcoded countdown timer in UI.",
        "location": "Hero Section - Current Round Card & Buy Form"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Token Allocation: Total Raised $18M | Total Supply 100B VRDX | FDV at TGE $500M",
        "status": "likely true mathematically - 100B total supply * $0.005 TGE price = $500M FDV. $18M is total target capital across 4 rounds.",
        "location": "Token Allocation Card"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Fundraising Rounds: VRDX token sale runs in 4 rounds. Each round offers different pricing, allocations, and vesting terms. Total raised: $18,000,000. FDV at TGE: $500,000,000.",
        "status": "needs verification - Describes 4-round fundraising structure.",
        "location": "Fundraising Rounds Section Header"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Round 1 — Seed / Strategic (Live Now): $0.0015 per VRDX | 70% discount to TGE | 12-month cliff + 24-month linear vesting | 0% TGE unlock | Allocation 3B VRDX | Capital $4.5M | Sold 0 / 3B",
        "status": "likely true mathematically - 3B * $0.0015 = $4.5M capital. 70% discount relative to $0.005 TGE price.",
        "location": "Fundraising Rounds Section - Round 1 Card"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Round 2 — Community (Upcoming): $0.003 per VRDX | 40% discount to TGE | 20% TGE unlock + 3-month cliff + 15-month linear vesting | KYC required | Allocation 1B VRDX | Capital $3M | Sold 0 / 1B",
        "status": "likely true mathematically - 1B * $0.003 = $3M capital. 40% discount relative to $0.005.",
        "location": "Fundraising Rounds Section - Round 2 Card"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Round 3 — Public Presale (Upcoming): $0.004 per VRDX | 20% discount to TGE | 25% TGE unlock + 6-month linear | Min $100, max $25,000 | KYC + whitelist required | Anti-sybil: 1 allocation per identity | Allocation 2B VRDX | Capital $8M | Sold 0 / 2B",
        "status": "likely true mathematically - 2B * $0.004 = $8M capital. 20% discount relative to $0.005.",
        "location": "Fundraising Rounds Section - Round 3 Card"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Round 4 — TGE / IDO (Upcoming): $0.005 per VRDX | 100% liquid at TGE | Initial market cap: $40M (8B circulating) | FDV: $500M | Allocation 0.5B VRDX | Capital $2.5M | Reserved 0 / 0.5B",
        "status": "likely true mathematically - 0.5B * $0.005 = $2.5M capital. Initial market cap = 8B circulating * $0.005 = $40M.",
        "location": "Fundraising Rounds Section - Round 4 Card"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Buy VRDX Tokens Form: Rate 1 USDT = 666.67 VRDX | $1,000.00 = 666,667 VRDX at $0.0015 per token (70% discount)",
        "status": "likely true mathematically - 1 / 0.0015 = 666.666... VRDX/USDT.",
        "location": "Buy VRDX Tokens Interactive Form"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "🔒 Secure payment • Tokens locked per vesting schedule • KYC required for all rounds",
        "status": "needs verification - Form compliance note.",
        "location": "Buy Form Footer"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Token Allocation: 100B max supply (Ecosystem & Grants 25% / 25B; PoS Staking 20% / 20B; Treasury 15% / 15B; Development 10% / 10B; Liquidity 10% / 10B; Community 5% / 5B; Seed / Strategic 3% / 3B / $4.5M; Public Presale 2% / 2B / $8M; Team & Advisors 5% / 5B)",
        "status": "likely true - Sums to 100B VRDX (100%). Capital raised for Seed ($4.5M) and Presale ($8M) match round terms.",
        "location": "Token Allocation Breakdown Section"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Vesting Schedule Table - Seed / Strategic: 0% TGE Unlock, 12 months cliff, 36 months vesting period, 125M / month, Status: Active",
        "status": "likely true mathematically - 3B / 24 months linear = 125M/month post 12-month cliff.",
        "location": "Vesting Schedule Table - Row 1"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Vesting Schedule Table - Community: 20% (1B) TGE Unlock, 3 months cliff, 18 months vesting period, 300M / month, Status: Upcoming",
        "status": "contradictory - Table states '20% (1B)' for a 1B total allocation (20% of 1B is 0.2B, not 1B). Also, remaining 0.8B over 18 months equals 44.4M/month, NOT 300M/month.",
        "location": "Vesting Schedule Table - Row 2"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Vesting Schedule Table - Public Presale: 25% (0.5B) TGE Unlock, None cliff, 6 months vesting period, 250M / month, Status: Upcoming",
        "status": "contradictory - Table states 0 cliff and 6-month linear vesting (1.5B / 6m = 250M/month). However, FAQ Q6 on the same page claims Public Presale has '25% unlocked at TGE, a 3-month cliff, then 6.25% per month for 12 months'.",
        "location": "Vesting Schedule Table - Row 3 & FAQ Q6"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Vesting Schedule Table - TGE / IDO: 100% TGE Unlock, None cliff, Liquid vesting period, At TGE, Status: Upcoming",
        "status": "likely true - 100% unlocked at TGE (0.5B tokens).",
        "location": "Vesting Schedule Table - Row 4"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Vesting Schedule Table - Team & Advisors: 0% TGE Unlock, 12 months cliff, 48 months vesting period, 138.9M / month, Status: Locked",
        "status": "likely true mathematically - 5B / 36 months post-cliff = 138.89M/month. Total timeline 48 months.",
        "location": "Vesting Schedule Table - Row 5"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Vesting Schedule Table - Ecosystem Grants: 4% (1B) TGE Unlock, None cliff, 120 months vesting period, 200M / month, Status: Active",
        "status": "likely true mathematically - 4% of 25B = 1B TGE unlock. Remaining 24B / 120 months = 200M/month.",
        "location": "Vesting Schedule Table - Row 6"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "0 investors already whitelisted",
        "status": "needs verification - Dynamic whitelist counter shows 0 users.",
        "location": "Join the Whitelist Section"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Whitelist Benefits (in Whitelist Modal script): Priority access, Higher allocation cap ($750,000 vs $500,000), Additional 5% bonus tokens, Early access to staking",
        "status": "contradictory - Whitelist modal advertises 'Additional 5% bonus tokens', whereas FAQ Q5 explicitly states 'No bonus tokens are offered'. Also allocation cap of '$750,000 vs $500,000' contradicts Round 3 max cap of '$25,000'.",
        "location": "Join Whitelist Modal Script"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "FAQ Q1: VERDIS (VRDX) is the native utility token ... Max supply is 100 billion tokens. This is a utility token, not an investment vehicle.",
        "status": "needs verification - Legal disclaimer positioning VRDX as a utility token.",
        "location": "FAQ Section - Question 1"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "FAQ Q2: Tokens are distributed at TGE. Seed investors have a 12-month cliff, then monthly vesting over 24 months. TGE circulating supply: 8B (8% of max supply). FDV at TGE: $500M.",
        "status": "likely true (as modeled) - Standard summary of TGE parameters.",
        "location": "FAQ Section - Question 2"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "FAQ Q3: Minimum investment for Round 1 varies; Public Presale has $100 minimum with $25,000 maximum per wallet. KYC is required for all rounds.",
        "status": "needs verification - Investment caps and KYC terms.",
        "location": "FAQ Section - Question 3"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "FAQ Q5: No bonus tokens are offered. Instead, early investors receive a discount to TGE price: Seed at 70% discount ($0.0015), Community at 40% discount ($0.003), and Presale at 20% discount ($0.004). The TGE/IDO price is $0.005.",
        "status": "contradictory - States 'No bonus tokens are offered', directly contradicting the Whitelist Modal script which promises 'Additional 5% bonus tokens'.",
        "location": "FAQ Section - Question 5"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "FAQ Q6: Seed and Private Sale tokens have a 12-month cliff with 0% at TGE, then monthly unlocks over 24 months. Presale tokens have 25% unlocked at TGE, a 3-month cliff, then 6.25% per month for 12 months. Public Sale tokens have 40% at TGE, then 10% per month for 6 months.",
        "status": "contradictory - Presale/Public Sale terms in FAQ Q6 ('3-month cliff, then 6.25%/mo for 12m') contradict both the Presale Round card ('25% TGE + 6-month linear') and the Vesting Table ('0 cliff, 6 months vesting, 250M/mo').",
        "location": "FAQ Section - Question 6"
    },
    {
        "page": "Sale page (/sale/)",
        "claim": "Referral Program (link in footer)",
        "status": "needs verification - Link in footer menu; no detailed 10%/5%/2.5% tier text present directly on Sale page body.",
        "location": "Footer - Community Navigation Column"
    },

    # =========================================================================
    # PAGE 3: Tokenomics Page (/tokenomics/)
    # =========================================================================
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "A balanced 100-billion supply distribution ... 4 fundraising rounds: Seed, Community, Presale, and TGE. Total raised: $18M. FDV: $500M.",
        "status": "contradictory - Claims 'Total raised: $18M' as an accomplished fact, whereas Seed round details below state Seed round is active with $4.5M target, Presale $8M target, etc.",
        "location": "Hero Section - Subtitle"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Total Supply 100,000,000,000 | Total Raised $18,000,000 | TGE Price $0.005 | Max Supply 100,000,000,000 VRDX Fixed Protocol Hard Cap | Distributed 100B VRDX",
        "status": "needs verification - Core protocol parameters.",
        "location": "Hero Section - Key Metrics Bar"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Fundraising Rounds: $18M Total Raised | Seed (3B) $4.5M | Community (1B) $3M | Presale (2B) $8M | TGE/IDO (0.5B) $2.5M",
        "status": "likely true mathematically - 3B*$0.0015 + 1B*$0.003 + 2B*$0.004 + 0.5B*$0.005 = $4.5M + $3M + $8M + $2.5M = $18.0M.",
        "location": "Fundraising Rounds Summary Box"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Key Metrics: TGE Price $0.005 | Seed Price $0.0015 | FDV at TGE $500M | Total Supply 100B VRDX tokens | Total Raised $18M 4 fundraising rounds | Staking Pool 20B (20%) 10-year emissions | TGE Circulating 8B (8%) At TGE launch",
        "status": "likely true (as modeled) - Standard summary metrics.",
        "location": "Key Metrics Summary Box"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "9-Category Token Allocation Table: Ecosystem & Developer Grants 25% (25,000,000,000); PoS Staking Rewards 20% (20,000,000,000); Treasury 15% (15,000,000,000); Development 10% (10,000,000,000); Liquidity 10% (10,000,000,000); Community 5% (5,000,000,000); Seed / Strategic 3% (3,000,000,000); Public Presale 2% (2,000,000,000); Team & Advisors 5% (5,000,000,000)",
        "status": "likely true - Sums exactly to 100B VRDX (100%).",
        "location": "Distribution Model Section - Allocation Table"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Category Breakdown 1: Ecosystem & Developer Grants - 25% (25B VRDX). Purpose: Developer grants, AI developers, plugin developers, dApps, smart contracts, research. Distribution: 4% (1B) at TGE for initial grants. Remaining 24B linear over 10 years. Governance-controlled with milestone-based releases. Vesting: 4% TGE + 10yr linear.",
        "status": "likely true mathematically - 4% of 25B = 1B TGE unlock. 24B / 120 months = 200M/month.",
        "location": "Detailed Category Analysis - Section 1"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Category Breakdown 2: PoS Staking Rewards - 20% (20B VRDX). Purpose: Rewards for DPoS validators, delegators. Distribution: 2.5% (0.5B) at TGE. 2B/year emission for 10 years. Target APR: 5-6.67% at 30-40% staking ratio. Vesting: 2.5% TGE + 10yr emission.",
        "status": "contradictory - Table lists monthly unlock as '162.5M / month' (19.5B / 120m), whereas 2B/year emission equals 166.67M/month (20B / 120m).",
        "location": "Detailed Category Analysis - Section 2 & Vesting Table"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Category Breakdown 3: Treasury - 15% (15B VRDX). Purpose: Infrastructure, security, ecosystem expansion, emergency reserves. Distribution: 3.33% (0.5B) at TGE. Multisig (5-of-7). Max 10% spending/month. Public dashboard with audit logs. Vesting: 3.33% TGE + 10yr governance.",
        "status": "likely true mathematically - 3.33% of 15B = ~0.5B TGE unlock. Remaining 14.5B / 120 months = ~120.8M/month (table states 120M/mo).",
        "location": "Detailed Category Analysis - Section 3"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Category Breakdown 4: Development - 10% (10B VRDX). Purpose: EvolvixOS, Verdis blockchain, AI infrastructure, SDK, developer tools. Distribution: 5% (0.5B) at TGE. 6-month cliff + 42-month linear vesting (48m total). Vesting: 5% TGE + 6mo cliff + 42mo.",
        "status": "likely true mathematically - 5% of 10B = 0.5B TGE unlock. 9.5B / 42 months = ~226M/month (table displays 223.8M/mo).",
        "location": "Detailed Category Analysis - Section 4"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Category Breakdown 5: Liquidity - 10% (10B VRDX). Purpose: DEX liquidity pools (VRDX/USDC, VRDX/ETH), CEX market making (2B). Distribution: 40% (4B) at TGE for DEX pools. 2B for CEX partnerships. 4B managed reserve over 5 years (60 months). Vesting: 40% TGE + 5yr managed.",
        "status": "contradictory - Section states 4B managed reserve over 60 months (6B remaining / 60m = 100M/month), but Vesting Table lists monthly unlock as '120M / month'.",
        "location": "Detailed Category Analysis - Section 5 & Vesting Table"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Category Breakdown 6: Community - 5% (5B VRDX). Purpose: Contributors, bug bounty, hackathons. Distribution: 20% (1B) at TGE. 3-month cliff + 15-month linear. Anti-sybil: KYC verification, 1 allocation per identity. Vesting: 20% TGE + 3mo cliff + 15mo.",
        "status": "contradictory - 20% of 5B = 1B TGE unlock. Remaining 4B / 15 months = 266.67M/month, but Vesting Table states '300M / month'.",
        "location": "Detailed Category Analysis - Section 6 & Vesting Table"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Category Breakdown 7: Seed / Strategic - 3% (3B VRDX). Purpose: Strategic investors with long vesting. Distribution: $0.0015/VRDX. $4.5M raised. 12-month cliff + 24-month linear (36 months total). 0% TGE unlock. 125M/month unlock post-cliff. Vesting: 0% TGE + 12mo cliff + 24mo.",
        "status": "likely true mathematically - 3B / 24 months = 125M/month post 12-month cliff.",
        "location": "Detailed Category Analysis - Section 7"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Category Breakdown 8: Public Presale - 2% (2B VRDX). Purpose: Public community allocation. Distribution: $0.004/VRDX. $8M raised. 25% (0.5B) at TGE + 6-month linear. Min $100, max $25,000, max 0.1% per wallet. KYC + whitelist required. Vesting: 25% TGE + 6mo linear.",
        "status": "likely true mathematically - 25% of 2B = 0.5B TGE unlock. Remaining 1.5B / 6 months = 250M/month.",
        "location": "Detailed Category Analysis - Section 8"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Category Breakdown 9: Team & Advisors - 5% (5B VRDX). Purpose: Aligns founding engineers, developers, advisors. Distribution: 12-month cliff, then linear monthly vesting over 36 months (48 months total). 0% TGE unlock. Vesting: 0% TGE + 12mo cliff + 36mo.",
        "status": "likely true mathematically - 5B / 36 months post-cliff = 138.89M/month.",
        "location": "Detailed Category Analysis - Section 9"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Vesting Schedule Table: Seed / Strategic (0% TGE, 12m cliff, 36m total, 125M/mo, Active); Community (20% / 1B, 3m cliff, 18m total, 300M/mo, Upcoming); Public Presale (25% / 0.5B, None cliff, 6m total, 250M/mo, Upcoming); IDO / TGE (100%, None cliff, Liquid, At TGE, Upcoming); Team & Advisors (0%, 12m cliff, 48m total, 138.9M/mo, Locked); Ecosystem Grants (4% / 1B, None cliff, 120m total, 200M/mo, Active); PoS Staking (2.5% / 0.5B, None cliff, 120m total, 162.5M/mo, Active); Treasury (3.33% / 0.5B, None cliff, 120m total, 120M/mo, Governance); Development (5% / 0.5B, 6m cliff, 48m total, 223.8M/mo, Locked); Liquidity (40% / 4B, None cliff, 60m total, 120M/mo, At Launch)",
        "status": "contradictory - Contains several internal monthly release discrepancies (PoS Staking, Community, Liquidity, Development) as detailed in category analysis.",
        "location": "Vesting Schedule Table"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Fundraising Rounds: Round 1 Seed ($0.0015 / 3B VRDX / $4.5M raised / FDV $150M / 70% discount); Round 2 Community ($0.003 / 1B VRDX / $3M raised / FDV $300M / 40% discount); Round 3 Presale ($0.004 / 2B VRDX / $8M raised / FDV $400M / 20% discount); Round 4 TGE/IDO ($0.005 / 0.5B VRDX / $2.5M raised / FDV $500M / Initial MCap $40M)",
        "status": "likely true mathematically - Round parameters and relative FDV valuations match pricing schedule.",
        "location": "Fundraising Rounds Section"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "10-Year Cumulative Circulating Supply Projection: TGE (Yr 0) 8B (8.0%); Year 1 20.26B (20.3%); Year 2 34.74B (34.7%); Year 3 47.62B (47.6%); Year 5 66B (66.0%); Year 7 77.6B (77.6%); Year 10 95B (95.0%)",
        "status": "needs verification - Cumulative unlock projection table. Year 10 reaches 95B (95% of max supply).",
        "location": "Circulating Supply Unlock Schedule Table"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "PoS Staking Economics: 20B VRDX staking pool with 10-year emission at 2B/year. Target staking ratio 30-40% (5-6.67% APR). APR table: 10% ratio = 20.00% APR; 20% ratio = 10.00% APR; 30% ratio = 6.67% APR; 40% ratio = 5.00% APR; 50% ratio = 4.00% APR; 60% ratio = 3.33% APR; 80% ratio = 2.50% APR.",
        "status": "likely true mathematically - 2B annual emission divided by total staked tokens (e.g. 2B / 10B = 20% APR; 2B / 30B = 6.667% APR).",
        "location": "PoS Staking Economics Section & Table"
    },
    {
        "page": "Tokenomics page (/tokenomics/)",
        "claim": "Referral Program (link in footer)",
        "status": "needs verification - Footer navigation link; no detailed 10%/5%/2.5% tier text present directly on Tokenomics page body.",
        "location": "Footer - Community Navigation Column"
    }
]

# Write to /app/conversations/6a6cb8454bc0607c481bb5eb/audit-homepage-sale.txt
out_path = "/app/conversations/6a6cb8454bc0607c481bb5eb/audit-homepage-sale.txt"

with open(out_path, "w", encoding="utf-8") as f:
    for idx, item in enumerate(audit_data):
        f.write(f"PAGE: {item['page']}\n")
        f.write(f"CLAIM: {item['claim']}\n")
        f.write(f"STATUS: {item['status']}\n")
        f.write(f"LOCATION: {item['location']}\n")
        if idx < len(audit_data) - 1:
            f.write("\n")

print(f"Successfully wrote {len(audit_data)} audited claims to {out_path}")
