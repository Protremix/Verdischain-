# Governance Separation & Emergency Controls (ARCH-032/033)

**Status:** Draft

---

## 1. Governance Architecture (ARCH-032)

### 1.1 Principle

Protocol governance must be separate from corporate governance. Protremix (the commercial company) must not have hidden control inside on-chain governance mechanisms.

### 1.2 Current Governance Structure

| Component | Mechanism | Control |
|-----------|----------|---------|
| Council | pallet-collective (8 members) | Council members set in genesis |
| Democracy | pallet-democracy | Referendum voting by token holders |
| Treasury | pallet-treasury | Council-approved spending |
| Technical Committee | pallet-collective (technical members) | Emergency proposals |

### 1.3 Separation Requirements

- Protremix board members must not hold majority council seats
- Council elections must be open and competitive
- Token holders have final say via referendum
- No hidden admin keys or sudo access on mainnet

### 1.4 Governance Roadmap

| Phase | Council | Democracy | Notes |
|-------|---------|-----------|-------|
| Testnet | Genesis-appointed | Not active | Testing only |
| Mainnet launch | 8 elected members | Active | Open elections |
| 6 months | 13 members | Active | Expand council |
| 12 months | Open election cycle | Full democracy | Community-driven |

---

## 2. Emergency Controls (ARCH-033)

### 2.1 Principle

Emergency powers must be bounded, time-limited, and reversible. They must not become permanent centralization vectors.

### 2.2 Emergency Actions

| Action | Trigger | Authority | Time Limit | Reversible |
|--------|---------|-----------|------------|------------|
| Emergency runtime upgrade | Chain halt or critical vulnerability | 2/3 Council + 2/3 Technical Committee | 24 hours | Yes (revert WASM) |
| Emergency treasury freeze | Suspected treasury compromise | 3/5 Multisig signers | 72 hours | Yes |
| DEX pause | DEX exploit detected | Council motion (simple majority) | 48 hours | Yes |
| Validator removal | Validator compromise | Council motion + slashing | Immediate | No (slashing is final) |

### 2.3 Constraints

- No single party can declare an emergency
- All emergency actions are logged on-chain
- Emergency actions automatically expire after their time limit
- Emergency actions must be followed by a public post-mortem
- No "permanent emergency" — all emergency powers must have an expiration

### 2.4 What Does NOT Exist on Mainnet

- No sudo (pallet_sudo removed)
- No root override key
- No hidden admin account
- No kill switch
- No centralized pause button

### 2.5 Technical Committee

The Technical Committee can fast-track emergency proposals but:
- Cannot unilaterally enact changes
- Requires council approval for execution
- Members are elected, not appointed by Protremix
- All fast-tracked proposals still go through referendum
