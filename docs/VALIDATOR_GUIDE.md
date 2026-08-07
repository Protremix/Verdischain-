# Verdis Chain Validator Onboarding & Staking Guide

This guide provides step-by-step technical instructions for setting up, registering, and running an active **Verdis Chain v2.0.0** validator node.

---

## 1. Validator Role & Network Parameters

Validators maintain consensus by producing block slots (via BABE) and voting on deterministic chain finality (via GRANDPA).

| Parameter | Value |
| :--- | :--- |
| **Max Active Validator Set** | `101` active validators |
| **Session Rotation Interval**| `600 blocks` (~1 hour) |
| **Minimum Validator Self-Stake**| `100,000 VRS` |
| **Unbonding Lockup Period** | `28 sessions` (~28 hours) |
| **Session Keys Required** | BABE (`sr25519`) + GRANDPA (`ed25519`) |
| **Green Multiplier Factor** | Up to +15% reward boost for green-certified hardware |

---

## 2. Step 1: Generating Account Keys

Validators require two distinct account keys:
1. **Stash Account:** Holds the validator's primary funds (`100,000+ VRS` self-stake). Kept in cold storage or secure wallet.
2. **Controller Account:** Manages staking parameters, session key linking, and reward payout preferences.

```bash
# Generate Stash keypair using subkey tool (SS58 Format 909)
subkey generate --scheme sr25519 --network verdis

# Output Example:
# Secret seed:       0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
# Public key (hex):  0x9c3d4f1e5a8b7c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d
# SS58 Address:      5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY
```

---

## 3. Step 2: Node Setup & Execution Parameters

Deploy the Verdis node host on high-performance infrastructure with the `--validator` flag enabled.

```bash
/opt/verdis/bin/verdis \
  --chain mainnet \
  --base-path /opt/verdis/data \
  --port 30333 \
  --rpc-port 9944 \
  --rpc-methods Safe \
  --validator \
  --name "Node-Validator-01"
```

Verify that block synchronization has reached the latest chain height before binding session keys.

---

## 4. Step 3: Generating Session Keys (`author_rotateKeys`)

Connect to the validator server via local terminal or SSH and execute the `author_rotateKeys` RPC call to generate hot consensus keypairs in the node's local keystore (`/opt/verdis/data/chains/verdis_mainnet/keystore/`):

```bash
curl -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"author_rotateKeys","params":[],"id":1}' \
  http://127.0.0.1:9944
```

* **Output Result:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x9c3d4f1e5a8b7c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d"
}
```

Copy the 128-character hex string output. This string contains the public keys for BABE and GRANDPA.

---

## 5. Step 4: Binding Session Keys & Joining DPoS Election

Submit the `session.setKeys` extrinsic to register your node's hot session keys on-chain.

```
[Stash / Controller Account]
          |
          v Submit Extrinsic
  [ session.setKeys(keys, proof) ]
          |
          v Submit Extrinsic
  [ dpos.bond(controller, stake_amount, reward_destination) ]
          |
          v Submit Extrinsic
  [ dpos.validate(commission_rate) ]
```

1. Go to **Verdis Web Wallet** or **Verdiscan Explorer Extrinsic Builder**.
2. Call `session.setKeys(keys, proof = 0x00)`:
   * `keys`: Insert the hex output from `author_rotateKeys`.
   * `proof`: `0x00`.
3. Call `dpos.bond(amount = 100000 VRS, payee = Staked)` to bond your minimum self-stake.
4. Call `dpos.validate(commission = 5%)` to enter the active validator candidate pool.

At the beginning of the next **600-block session round**, `pallet_dpos` ranks all candidates by total stake (self-stake + nominator stake). The top 101 candidates are elected into the active validator set.

---

## 6. Green Validator Scoring Engine (`pallet_eco`)

Verdis Chain incentivizes eco-friendly infrastructure by evaluating green performance parameters:

```
Total Reward Weight = Base Stake Weight * (1.0 + Green Multiplier)
```

### Green Score Factors
* **100% Renewable Energy Operation:** Submit datacenter power certificates to `pallet_eco` verifiers (+8% boost).
* **Carbon Credit Retirement:** Purchase and retire verified carbon offsets via `pallet_eco::retire_carbon_credits` (+5% boost).
* **Hardware Efficiency Standard:** Operating on low-wattage server architecture (+2% boost).

Green scores are updated on-chain every session and visible on the Verdiscan **Validators** tab.

---

## 7. Rewards & Slashing Conditions

### Reward Distribution
* **Block Authoring Rewards:** Minted per successfully authored BABE block.
* **Finality Voting Rewards:** Distributed to active GRANDPA consensus voters per finalized block.
* **Payout Split:** Block rewards are split automatically between validator commission and nominators proportional to stake.

### Slashing Penalty Rules

```
+-----------------------------------------------------------------------------------+
| SLASHING PENALTY MATRIX                                                           |
+-----------------------------------------------------------------------------------+
| Violation Type              | Penalty Severity | Consequence                      |
| --------------------------- | ---------------- | -------------------------------- |
| Unresponsiveness / Offline  | Low (0.1% - 1%)  | Chilled from validator set       |
| GRANDPA Equivocation        | High (100%)      | Full stake slash & perm-ban      |
| BABE Double Block Authoring | High (100%)      | Full stake slash & perm-ban      |
+-----------------------------------------------------------------------------------+
```

1. **Unresponsiveness / Missing Blocks:** If a validator misses slots continuously for more than 10% of a session (~60 blocks), they suffer a minor slash and are automatically **chilled** (removed from active set).
2. **Equivocation (Double Signing):** Signing two different blocks at the same slot height or submitting double GRANDPA finality votes triggers an automated cryptographic proof report resulting in a **100% stake slash** and permanent ban.
