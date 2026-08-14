# Corporate & Regulatory Structure Briefing Pack (ARCH-001/002/003/004)

**Prepared:** 2026-08-14
**Status:** Draft for Rojs review and external counsel engagement

---

## 1. Target Org/Role Map

### Proposed Entity Structure

```
Verdis Foundation (Non-profit, jurisdiction TBD)
  ├── Protocol governance (council, democracy, treasury)
  ├── Validator coordination (non-operational)
  └── Community grants

Protremix (Commercial entity, Spain/EU)
  ├── Development services (contracted to Foundation)
  ├── Infrastructure operations (contracted)
  └── No protocol governance authority

Token Offering Entity (separate legal entity, jurisdiction TBD)
  ├── KYC/AML compliance
  ├── Token sale execution
  ├── Investor relations
  └── Regulatory licensing (VARA/MiCA)
```

### Separation Principles

1. **Foundation** holds no operational keys — governance only
2. **Protremix** is a contractor — no permanent protocol control
3. **Offering Entity** is firewalled — handles only token sale compliance
4. No entity holds majority validator stake
5. Treasury multisig (3-of-5) spans multiple entities

### Role Matrix

| Function | Foundation | Protremix | Offering Entity | External Counsel |
|----------|-----------|-----------|-----------------|-----------------|
| Protocol governance | YES | NO | NO | Advisory |
| Development | Contract | YES (contractor) | NO | NO |
| Infrastructure ops | Contract | YES (contractor) | NO | NO |
| Token sale | NO | NO | YES | YES |
| KYC/AML | NO | NO | YES | YES |
| Treasury management | 3-of-5 multisig | 1 signer | 0 signers | Advisory |
| Validator operation | NO | Limited (<=33%) | NO | NO |
| Legal compliance | NO | NO | YES | YES |
| Security audit | Contract | NO (independent) | NO | NO |

---

## 2. Entity/Function Responsibility Matrix

| Responsibility | Owner | Backup | Evidence Required |
|---------------|-------|--------|------------------|
| Protocol source code | Protremix → GitHub | Foundation copy | Public GitHub repo |
| Validator keys | Individual operators | Air-gapped backup | Key ceremony record |
| Treasury keys (3-of-5) | 5 independent custodians | N/A | Key ceremony record |
| DNS (verdischain.com) | Protremix | Foundation | Domain registration records |
| DNS (evolvixos.com) | Protremix | Foundation | Domain registration records |
| Server (91.98.160.145) | Protremix | Hetzner rescue | Server contract |
| Server (62.238.61.145) | Protremix | TBD | Server contract |
| CI/CD | GitHub Actions | Foundation GitHub | .github/workflows/ |
| RPC endpoints | Protremix (testnet) | Independent operators (mainnet) | On-chain peer list |
| TX Relay | Protremix | Any operator (optional) | Open source |
| Web wallet | Protremix → GitHub | Any operator | Public repo |
| Chain spec | Foundation | GitHub | Signed genesis document |

---

## 3. Counsel Briefing Pack — UAE/VARA

### Questions for UAE/VARA Counsel

1. **Entity classification:** Does the Verdis Foundation need to be registered in Dubai/UAE to issue VRDX under VARA jurisdiction?

2. **VARA issuance category:** Under the VARA Virtual Asset Issuance Rulebook, which issuance category applies to VRDX?
   - Category 1 (full issuance)
   - Category 2 (limited issuance)
   - Exempt issuance

3. **Whitepaper requirement:** VARA requires a whitepaper for non-exempt VAs. Does the current Verdis whitepaper meet VARA's content requirements?

4. **Separate VA activities:** In addition to issuance, which VARA activity licenses are required?
   - VA Exchange
   - VA Custody
   - VA Broker-Dealer
   - VA Transfer/Settlement
   - VA Management

5. **DEX operations:** Does the on-chain AMM DEX constitute a VA Exchange activity requiring a VARA license?

6. **Wallet operations:** Does the non-custodial wallet require any VARA licensing?

7. **Staking:** Does PoS staking reward distribution require any VARA authorization?

8. **Timeline and cost:** What is the expected timeline and cost for VARA licensing?

### VARA Context (from Action Pack)

- VARA's Virtual Asset Issuance Rulebook applies to entities in Dubai issuing virtual assets in the course of business
- Contains Category 1, Category 2, and exempt issuance paths
- Issuance rules operate IN ADDITION to rules for separate VA activities
- Whitepaper required for non-exempt VAs, published before asset is available to public
- Counsel brief must cover BOTH issuance AND any separate activities (exchange, custody, broker-dealer, transfer/settlement)

---

## 4. Counsel Briefing Pack — EU/MiCA

### Questions for EU/MiCA Counsel

1. **VRDX classification:** Under MiCA, is VRDX:
   - An ordinary crypto-asset (Article 4)?
   - An asset-referenced token (ART)?
   - An e-money token (EMT)?
   - A financial instrument (MiFID II)?
   - Potentially excluded under Article 4(2)?

2. **Whitepaper requirement:** If VRDX is an ordinary crypto-asset, does the current whitepaper meet MiCA Article 5 content requirements?

3. **Notification:** Does VRDX require notification to the competent authority under Article 4(1)?

4. **Territorial scope:** Which EU member states' competent authorities have jurisdiction?

5. **Marketing communications:** Do current marketing materials comply with MiCA Article 6?

6. **Offeror obligations:** What are the specific offeror obligations under Articles 7-10?

7. **Exemptions:** Does any MiCA exemption apply (Article 4(2))? If so, which?

8. **DEX under MiCA:** Does the on-chain DEX constitute a crypto-asset service requiring CASP authorization?

9. **Staking under MiCA:** Does PoS staking constitute a CASP service?

10. **Timeline and cost:** What is the expected timeline and cost for MiCA compliance?

### MiCA Context (from Action Pack)

- For an ordinary crypto-asset (not ART/EMT), MiCA Article 4 requires: legal person, crypto-asset white paper, notification, publication, compliant marketing, compliance with offeror obligations
- VRDX classification memo must FIRST determine whether VRDX is ordinary crypto-asset, ART, EMT, or financial instrument
- NO website claim such as "MiCA Compliant" should be published before legal analysis is completed

---

## 5. Evidence Index — VA Activities

| Activity | Current State | Evidence | Legal Status |
|----------|-------------|----------|-------------|
| Token issuance (VRDX) | Testnet only, genesis config | chain_spec.rs, CI check | Not licensed |
| DEX (AMM) | 6 pools on testnet | pallet-amm-dex source | Not licensed |
| Wallet (non-custodial) | Web + Android | web/wallet/ source | No custody (non-custodial) |
| Custody | NOT OFFERED | N/A | N/A |
| Transfer/Settlement | On-chain transfers | pallet-balances | Not licensed |
| Exchange (DEX swap) | On-chain AMM | pallet-amm-dex | Not licensed |
| Staking | PoS/DPoS on testnet | pallet-dpos | Not licensed |
| Validator operation | 6 active (testnet) | systemd services | Not licensed |

---

## 6. Global Jurisdiction Policy (ARCH-004)

### Proposed Policy

| Jurisdiction Category | Action | Examples |
|----------------------|--------|----------|
| Allowed | Users can participate | TBD by counsel |
| Restricted | KYC + enhanced due diligence | TBD by counsel |
| Prohibited | Blocked at UI, API, transaction layer | Sanctioned countries (OFAC, EU, UN) |

### Enforcement Layers

1. **UI Layer:** Sale page geoblocks prohibited jurisdictions via IP + KYC
2. **API Layer:** TX Relay checks KYC status before accepting sale transactions
3. **Transaction Layer:** Sale contract requires KYC attestation
4. **Audit Log:** Immutable record of jurisdiction determination per user

### Blocked Jurisstances (Sanctions List — Pre-counsel)

Based on OFAC, EU, UN sanctions lists:
- Cuba, Iran, North Korea, Syria, Crimea/DNR/LNR regions
- Additional jurisdictions TBD by counsel

### Pending Counsel Determination

- All non-sanctioned jurisdictions need classification (allowed/restricted/prohibited)
- This requires licensed legal opinion per jurisdiction
- Sale MUST remain disabled until this policy is finalized
