# Token Offering Compliance Architecture (ARCH-007)

**Status:** Design document — sale remains DISABLED until legal approval

---

## 1. Offering Entity Boundary

### Principle

Token sale activities (KYC, payment processing, investor management) must be isolated in a separate legal entity from protocol development and governance.

### Proposed Boundary

```
Token Offering Entity (separate legal entity)
  ├── KYC/AML verification (third-party provider)
  ├── Sanctions screening (OFAC/EU/UN)
  ├── Jurisdiction eligibility check
  ├── Payment processing
  ├── Token distribution (vesting enrollment)
  ├── Investor communications
  └── Audit log (immutable)

Protocol (separate)
  ├── Vesting pallet (enforces on-chain schedule)
  ├── Tokenomics pallet (enforces allocation caps)
  └── No direct sale functionality
```

### Data Flow

```
User → Sale Page (UI) → KYC Provider → Sanctions Check → Jurisdiction Check
  → Eligibility Decision → Payment → Offering Entity approves → TX Relay enrolls vesting
```

---

## 2. KYC/KYB Flow Design

### Individual Investors (KYC)

1. **Identity Verification**
   - Full name, date of birth, nationality
   - Government ID (passport, national ID)
   - Proof of address (utility bill, bank statement)
   - Liveness check (selfie video)

2. **Sanctions Screening**
   - OFAC SDN check
   - EU consolidated sanctions list
   - UN Security Council sanctions
   - PEP (Politically Exposed Person) screening

3. **Residency/Jurisdiction Determination**
   - Country of residence (from proof of address)
   - Nationality (from passport)
   - Dual nationality handling (most restrictive applies)

4. **Eligibility Decision**
   - Green: Allowed jurisdiction, not sanctioned → proceed
   - Yellow: Restricted jurisdiction → enhanced due diligence
   - Red: Prohibited jurisdiction or sanctioned → blocked

### Corporate Investors (KYB)

1. **Entity Verification**
   - Company registration documents
   - Beneficial ownership (UBO) declaration
   - Directors and officers list

2. **Corporate Sanctions Screening**
   - Entity-level OFAC/EU/UN check
   - UBO-level sanctions check
   - Adverse media screening

3. **Corporate Eligibility**
   - Entity jurisdiction classification
   - UBO jurisdiction classification
   - Most restrictive jurisdiction applies

---

## 3. Country Policy (Versioned)

### Version: 0.1.0-draft (NOT FINAL — requires counsel)

| Category | Countries | Requirements |
|----------|-----------|-------------|
| Prohibited | OFAC sanctioned: Cuba, Iran, North Korea, Syria, Crimea/DNR/LNR | Blocked at all layers |
| Restricted | TBD by counsel | Enhanced due diligence, higher minimum, lower max allocation |
| Allowed | TBD by counsel | Standard KYC, standard allocation limits |

### Versioning

- Country policy is versioned (semver)
- Each version has an effective date
- All eligibility decisions reference the policy version used
- Policy changes require Offering Entity + counsel approval
- Immutable audit log records which version was applied to each user

---

## 4. Enforcement Architecture

### Layer 1: UI (Sale Page)

- IP geolocation check (block prohibited countries at page level)
- KYC widget (third-party provider, e.g. Sumsub, Onfido)
- Display eligibility before payment
- No payment processing until KYC + jurisdiction approved

### Layer 2: API (TX Relay)

- Sale endpoints require KYC token (JWT from Offering Entity)
- TX Relay validates KYC token before processing sale transaction
- Rate limiting per account
- Audit log entry for every sale attempt

### Layer 3: Transaction (On-chain)

- Vesting enrollment requires Offering Entity signature
- Tokenomics pallet enforces allocation caps
- Vesting pallet enforces cliff and linear schedule
- No bypass possible (no sudo on mainnet)

### Layer 4: Audit (Immutable)

- Every eligibility decision logged with:
  - User identifier (hashed)
  - Jurisdiction determined
  - Policy version applied
  - Decision (approved/rejected/restricted)
  - Timestamp
  - Reviewer (if manual review)

---

## 5. Sale Disabled Status

**CURRENT STATE: SALE IS DISABLED**

The token sale page at verdischain.com/sale/ displays:
- "$0 verified / $18M target" (not "$18M raised")
- No payment processing active
- No KYC integration active
- TESTNET banner visible

**Sale will remain DISABLED until:**
1. Legal entity (Offering Entity) is established
2. KYC/AML provider is contracted
3. UAE/VARA licensing is completed (if required)
4. EU/MiCA compliance is confirmed (if required)
5. Global jurisdiction policy is finalized by counsel
6. Independent security audit passes with 0 critical findings
7. Rojs gives explicit approval to enable sale
