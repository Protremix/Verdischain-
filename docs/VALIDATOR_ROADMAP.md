# Verdis Chain Validator Roadmap (ARCH-018)

**Status:** Testnet (6 active validators, 21 registered)
**Target:** 21 independent validators at mainnet, 50+ within 6 months, 100+ within 12 months

---

## Current State

- 21 validators registered in genesis spec (placeholder keys)
- 6 active validators (Alice-Ferdie) with session keys
- 15 standby validators (1M stake each)
- All validators on single Hetzner server (centralization risk)
- DPoS consensus: BABE/GRANDPA, green_score scoring

## Milestones

### Phase 1: Testnet Hardening (Current — Pre-Mainnet)
- [ ] Generate 21 real validator keypairs via air-gapped ceremony
- [ ] Replace placeholder genesis keys with real keys
- [ ] Verify genesis determinism with new keys
- [ ] Test session rotation with all 21 validators
- [ ] Test slashing and recovery paths
- [ ] Test validator onboarding (register_validator extrinsic)
- [ ] Test validator offboarding (unregister_validator extrinsic)
- [ ] Publish validator setup guide (DONE: docs/VALIDATOR_SETUP_GUIDE.md)

### Phase 2: Mainnet Launch (21 Validators)
- [ ] 21 independent validators (no single operator >33% of stake)
- [ ] Geographic diversity (minimum 3 countries, 3 ASNs)
- [ ] Each validator independently operated (not all on Protremix infra)
- [ ] Protremix + Foundation combined stake <= 33%
- [ ] Nakamoto coefficient >= 7
- [ ] Top-10 stake concentration < 50%

### Phase 3: Expansion (50+ Validators, 6 months post-mainnet)
- [ ] Permissionless validator onboarding (no whitelist)
- [ ] Public technical/staking requirements documented
- [ ] Automated eligibility check (stake >= minimum, green_score valid)
- [ ] Validator monitoring dashboard public
- [ ] Geographic distribution across 5+ countries

### Phase 4: Scale (100+ Validators, 12 months post-mainnet)
- [ ] 100+ independent validators
- [ ] Client diversity roadmap (alternative client development)
- [ ] Independent RPC providers
- [ ] Nakamoto coefficient >= 21
- [ ] Top-10 stake concentration < 33%

## Technical Requirements (per validator)

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Storage | 100 GB SSD | 500 GB NVMe |
| Bandwidth | 100 Mbps | 1 Gbps |
| Uptime | 99% | 99.9% |
| Minimum stake | 1,000 VRDX | 10,000 VRDX |
| Green score | 0-100 | 50+ (renewable energy preferred) |

## Decentralization Targets

| KPI | Mainnet | 6 months | 12 months |
|-----|---------|---------|-----------|
| Independent validators | 21 | 50+ | 100+ |
| Protremix + Foundation stake | <=33% | <=25% | <=20% |
| Nakamoto coefficient | >=7 | >=15 | >=21 |
| Countries | 3+ | 5+ | 10+ |
| ASNs | 3+ | 5+ | 10+ |
| Top-10 concentration | <50% | <40% | <33% |
