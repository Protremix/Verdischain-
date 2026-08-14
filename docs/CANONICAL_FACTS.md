# Verdis Chain — Canonical Facts File

**Version:** 1.0  
**Last Updated:** 2026-08-14  
**Source of Truth:** This file + code (chain_spec.rs, runtime/lib.rs)

> All public documents, website pages, whitepapers, and marketing materials MUST derive from this file. If any conflict exists between this file and other documents, this file (backed by code) is authoritative.

---

## Network Status

- **Current Network:** TESTNET (not mainnet)
- **Block Production:** Active (BABE + GRANDPA consensus)
- **Pallet Sudo:** REMOVED
- **Total Pallets:** 31 (16 custom Verdis pallets + 15 Substrate standard)
- **Active Validators:** 6 (target: 21 for mainnet)
- **Nodes:** 3
- **Runtime Version:** v2.0.0

## Token (VRDX)

- **Ticker:** VRDX (NOT VERDIS)
- **Decimals:** 9
- **Total Supply:** 100,000,000,000 (100B) VRDX
- **Circulating Supply:** 8,000,000,000 (8B) VRDX at TGE
- **FDV at TGE:** 00,000,000 (at bash.005/VRDX)

## Token Allocation (100B Total)

| Category | Amount | Percentage |
|----------|--------|------------|
| Ecosystem & Developer Grants | 25B | 25% |
| PoS Staking Rewards | 20B | 20% |
| Treasury | 20B | 20% |
| Development | 10B | 10% |
| Liquidity | 10B | 10% |
| Community | 5B | 5% |
| Seed / Strategic | 3B | 3% |
| Public Presale | 2B | 2% |
| Team & Advisors | 5B | 5% |

**Total Investor Allocation:** 12B (Seed 3B + Presale 2B + Community 5B + TGE 2B)

## Fundraising (TARGET — NOT EXECUTED)

- **Funding Target:** 8,000,000
- **Funds Verified Raised:** bash
- **Status:** NOT ACTIVE — No sale has been executed

### Round Details

| Round | Price | Allocation | Target | Discount | Vesting |
|-------|-------|------------|--------|----------|---------|
| Seed | bash.0015 | 3B VRDX | .5M | 70% | 12mo cliff, linear |
| Community | bash.003 | 5B VRDX | M | 40% | 3mo cliff, linear |
| Presale | bash.004 | 2B VRDX | M | 20% | 12mo cliff, linear |
| TGE/IDO | bash.005 | 2B VRDX | .5M | 0% | Liquid at TGE |

## Security

- **External Audit:** NOT COMPLETED
- **Internal Security Review:** Completed August 2026 (72/100 initial → fixes applied)
- **Penetration Testing:** NOT COMPLETED
- **Formal Verification:** NOT COMPLETED
- **AI-Assisted Reviews:** Ongoing (Claude + Kimi) — these are development assistance, NOT independent audits

## Legal

- **Legal Entity:** Registration IN PROGRESS
- **MiCA Compliance:** NOT REVIEWED — token classification undetermined
- **Legal Counsel:** NOT YET ENGAGED
- **License:** Proprietary (NOT MIT/open-source)

## Treasury Security

- **Multisig:** 3-of-5 cold storage multisig (specification created)
- **Key Generation:** PENDING air-gapped ceremony
- **Current Code:** Uses PalletId placeholder — must be replaced before mainnet

## Environmental Claims

- **Carbon Status:** Designed for Efficiency (NOT Carbon Negative)
- **Carbon Credits:** On-chain tracking exists (not externally verified)
- **Green Validators:** Scoring system exists (1-5 scale)
- **Partnerships (Verra, WWF, UN):** NOT VERIFIED — claims removed

## Team

- **CEO:** Dorian Jean
- **Founder:** Rojs Gordons
- **CTO:** Mark Jamestown
- **Verified Members:** 5 of 6 (publicly verifiable records)
  - Rojs Gordons — Founder ✅
  - María Dolores Márquez de Prado — Legal Advisor ✅ (former Supreme Court Prosecutor)
  - Ignacio Martínez-Arrieta — Legal Advisor ✅ (Madrid Bar / EU Parliament)
  - Dorian Jean — CEO ✅ (business owner, non-crypto background)
  - Elizabeth Jefferson — Team Member ✅ (former NCAA athlete, non-crypto background)
  - Mark Jamestown — CTO ⚠️ (credentials not yet verified)

## Mainnet Blockers

1. Placeholder validator keys (need air-gapped ceremony)
2. No independent security audit
3. Legal entity registration incomplete
4. MiCA compliance review not done
5. 21-validator test not completed
6. No penetration testing
7. No chaos/stress testing
8. DPoS green_score range check (FIXED in code)
