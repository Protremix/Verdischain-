# Verdis Chain Mainnet Validator Set Design

**Status:** Draft
**Date:** 2026-08-10
**Author:** EvolvixOS Engineering

## 1. Overview

This document defines the mainnet validator set architecture, staking economics, geographic distribution, session-key rotation, and bootstrapping procedure for the Verdis Chain mainnet.

## 2. Validator Set Configuration

### 2.1 Genesis Validators: 7

| Property | Value | Rationale |
|----------|-------|-----------|
| Genesis validators | 7 | Minimum for meaningful decentralization; tolerates 2 failures |
| GRANDPA threshold | 5 (ceil(2/3 × 7)) | 5/7 votes needed to finalize |
| BABE authorities | 7 | Equal block production slots |
| Fault tolerance | 2 nodes | Chain continues if ≤2 validators go offline |
| MinValidatorCount | 4 | Chain halts below 4 active validators |

### 2.2 Expansion Path

| Phase | Validators | Threshold | Timeline | Trigger |
|-------|-----------|-----------|----------|---------|
| Genesis | 7 | 5 | TGE | Mainnet launch |
| Phase 2 | 11 | 8 | Month 3-6 | 50+ registered validators, governance vote |
| Phase 3 | 21 | 15 | Month 6-12 | 100+ registered validators, stable TPS |
| Phase 4 | 42+ | 29 | Year 2+ | Full decentralization |

## 3. Staking Economics

### 3.1 Current vs Proposed

| Parameter | Testnet (Current) | Mainnet (Proposed) |
|-----------|-------------------|-------------------|
| BlockReward | 16 VRDX | 342 VRDX |
| MinValidatorStake | 10,000 VRDX | 10,000,000 VRDX (10M) |
| MaxStakePerValidator | 10B VRDX | 1B VRDX (1% of supply) |
| ActiveValidatorCount | 21 | 7 (genesis) |
| EpochLength | 500 blocks | 500 blocks (~50 min) |
| UnbondingPeriod | 201,600 blocks (14 days) | 201,600 blocks (14 days) |

### 3.2 Reward Economics

- **Annual rewards:** 1.8B VRDX (from 20B staking pool, ~11 year duration)
- **Block reward:** 342 VRDX per block
- **Block time:** 6 seconds → 14,400 blocks/day → 5,256,000 blocks/year
- **Per-validator annual (7 validators):** 257.1M VRDX
- **Target APR:** 6% at 30% stake rate (30B VRDX staked)

### 3.3 APR Scenarios

| Staked per validator | Validator own stake | Delegated | Total APR | Delegator APR (after 10% commission) |
|---------------------|--------------------|-----------|-----------|---------------------------------------|
| 100M | 10M | 90M | 257% | 231M / 90M = 257% → ~25.7% effective |
| 500M | 10M | 490M | 51.4% | 231.4M / 490M = 47.2% → ~4.7% effective |
| 1B | 10M | 990M | 25.7% | 231.3M / 990M = 23.4% → ~2.3% effective |

Early validators earn higher APR to bootstrap the network. As delegation grows, APR converges toward the 6% target.

### 3.4 Commission Structure

- Default validator commission: 10%
- Maximum commission: 20% (governance-enforced)
- Commission change: max 5% per epoch, 24h delay
- All rewards auto-compounded to validator stake

## 4. Geographic Distribution

### 4.1 Genesis Validator Locations

| # | Region | Datacenter | Provider | Purpose |
|---|--------|-----------|----------|---------|
| V1 | EU-West (Amsterdam) | eq | Hetzner | Primary block producer |
| V2 | US-East (Virginia) | dc | AWS | NA redundancy |
| V3 | EU-Central (Frankfurt) | dc | Hetzner | EU redundancy |
| V4 | AP-Southeast (Singapore) | dc | DigitalOcean | APAC presence |
| V5 | US-West (Oregon) | dc | AWS | US redundancy |
| V6 | AP-Northeast (Tokyo) | dc | Vultr | APAC redundancy |
| V7 | SA-East (São Paulo) | dc | AWS | South America presence |

### 4.2 Requirements

- Each validator on a different /24 subnet
- Minimum 4 different hosting providers
- Minimum 3 different geographic regions (EU, NA, APAC)
- Latency between any two validators < 200ms
- Each validator: 8 vCPU, 32GB RAM, 1TB NVMe SSD

## 5. Session Key Management

### 5.1 Key Types

| Key | Type | Purpose | Rotation Frequency |
|-----|------|---------|-------------------|
| BABE | sr25519 | Block production | Every epoch (500 blocks, ~50 min) |
| GRANDPA | ed25519 | Block finalization | Every 24h (governance-controlled) |
| ImOnline | sr25519 | Heartbeat | Every epoch |
| Authority Discovery | sr25519 | Peer discovery | Every epoch |

### 5.2 Key Rotation Procedure

1. **Automated (BABE/ImOnline/Discovery):** Keys rotate every epoch via . New keys generated locally, old keys wiped.

2. **Manual (GRANDPA):** Key rotation is governance-gated:
   - Step 1: Generate new ed25519 keypair on validator node
   - Step 2: Submit  via local RPC (not public)
   - Step 3: Wait 1 epoch for new key to take effect
   - Step 4: Wipe old GRANDPA key from keystore
   - Step 5: Notify other validators via secure channel

3. **Emergency Key Rotation:** In case of key compromise:
   - All validators rotate GRANDPA keys within 1 epoch
   - Chain pauses if compromised validator is online
   - 5/7 validators must rotate before chain resumes

### 5.3 Keystore Security

- Keys stored in encrypted keystore on each validator
- Keystore encrypted with node-specific passphrase
- Passphrase stored in a separate secrets manager (HashiCorp Vault or AWS Secrets Manager)
- No keys transmitted over the network
- No keys stored in git, CI, or any shared system
- Keys never handled by any AI agent or automated system beyond the node itself

## 6. Mainnet Genesis Ceremony

### 6.1 Pre-launch Checklist

- [ ] All 7 validator nodes deployed and synced to testnet
- [ ] All 7 validators have unique sr25519 + ed25519 keypairs
- [ ] All 7 validators registered on testnet with correct stake
- [ ] Chain spec finalized and verified (no testnet keys in mainnet spec)
- [ ] Security audit completed (no Critical/High findings)
- [ ] All 249 tests pass
- [ ] WASM runtime built and verified
- [ ] Docker images built and pushed
- [ ] DNS configured (verdischain.com → mainnet RPC)
- [ ] Monitoring stack deployed (Prometheus + Grafana + AlertManager)
- [ ] Each validator operator has verified their node independently

### 6.2 Genesis Ceremony Steps

1. **T-7 days:** Distribute chain spec (raw JSON) to all validator operators
2. **T-5 days:** Each operator generates keypairs and submits public keys to coordinator
3. **T-3 days:** Coordinator compiles final chain spec with all validator keys
4. **T-2 days:** Each operator verifies final chain spec hash matches
5. **T-1 day:** Each operator starts node with 
6. **T-0:** Chain launches. First block produced. GRANDPA finalizes within 3 blocks.

### 6.3 Launch Day Monitoring

- Block height, finalization lag, peer count per node
- BABE slot production rate (target: >95%)
- GRANDPA round time (target: <30s)
- ImOnline heartbeat success rate (target: 100%)
- Transaction pool depth
- Alert if any validator misses 3 consecutive epochs

## 7. Validator Onboarding (Post-Genesis)

### 7.1 Registration Process

1. Operator runs 
2. Operator stakes minimum 10M VRDX
3. Operator configures node with  flag
4. Operator inserts session keys via 
5. Validator becomes active in next epoch if:
   - Total registered validators < MaxValidators (100)
   - Validator has sufficient stake
   - Node is online (ImOnline heartbeat received)

### 7.2 Delegation

- Any token holder can delegate to a validator via 
- Delegator earns rewards proportional to their stake
- Validator takes commission (10% default)
- Delegator can unbond via  with 14-day unbonding period

## 8. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Validator key compromise | Emergency rotation procedure, encrypted keystore |
| 2+ validators go offline | Chain continues (tolerates 2 failures) |
| 3+ validators go offline | Chain halts (below threshold) — emergency recovery procedure |
| Staking pool depletion | 20B VRDX lasts 11 years at target rate |
| High inflation early | APR decreases as delegation grows, converges to 6% |
| Validator collusion | Max 20% commission, governance can slash |
| Geographic concentration | Minimum 3 regions, 4 providers |
