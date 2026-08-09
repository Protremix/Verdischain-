# Verdis Chain Network Upgrade Guide

This guide provides technical procedures for conducting node binary updates, forkless runtime upgrades, emergency recovery, and consensus upgrades across the **Verdis Chain** network.

---

## 1. Overview & Upgrade Classifications

Verdis Chain supports two primary mechanisms for network upgrades:

| Upgrade Type | Scope & Impact | Requires Chain Restart? | Mechanism |
| :--- | :--- | :--- | :--- |
| **Client Upgrade** | Node binary, RPC interface, P2P networking, RocksDB storage optimizations. | **Yes** (rolling restart per validator) | Git pull + `cargo build --release` + systemd restart |
| **Runtime Upgrade** | On-chain state logic, pallet rules, transaction fees, governance logic. | **No** (Forkless live execution) | WASM runtime blob submission via `system.setCode` |
| **Consensus / Hard Upgrade** | Breaking changes to consensus state formats, BABE/GRANDPA epoch structures. | **Yes** (Synchronized epoch window) | Coordinated binary release + runtime upgrade submission |

---

## 2. Pre-Upgrade Checklist

Complete this checklist prior to initiating any production upgrade on `verdischain.com` or mainnet validator nodes:

* [ ] **Staging Verification:** Upgrade tested and verified on staging testnet for a minimum of 24 hours (10,000+ blocks).
* [ ] **WASM Integrity Check:** Verify `srtool` or `subwasm` hash digest matches expected runtime build hash.
* [ ] **System Backup Executed:** Complete snapshot of RocksDB data (`/opt/verdis-chain-rust/data`) and keystore.
* [ ] **Community & Validator Notification:** Publish upgrade schedule to validator operators at least 48 hours in advance.
* [ ] **Epoch Timing Scheduled:** Ensure runtime upgrades are submitted near the start of a session window (e.g., block slot 50-100 of the 600-block epoch).
* [ ] **Emergency Rollback Plan:** Keep previous node binary (`verdis.v2.0.0.bak`) and database snapshots available.

---

## 3. Client Binary Upgrade Procedure

Client updates upgrade the underlying executable without resetting or purging chain state.

### Step 1: Backup Current Binary & Database
```bash
sudo systemctl stop verdis-node.service

# Copy existing binary backup
cp /opt/verdis-chain-rust/target/release/verdis /opt/verdis-chain-rust/target/release/verdis.v2.0.0.bak

# Execute snapshot backup script
/opt/verdis-backup.sh
```

### Step 2: Fetch & Rebuild Source
```bash
cd /opt/verdis-chain-rust
git fetch origin
git checkout tags/v2.1.0

# Verify Rust version matches requirement (1.78+)
rustc --version

# Rebuild release binary
cargo build --release
```

### Step 3: Restart Service & Verify Sync
```bash
sudo systemctl start verdis-node.service
sudo systemctl status verdis-node.service

# Check version output
/opt/verdis-chain-rust/target/release/verdis --version

# Stream logs to ensure node connects to peers and resumes block production
journalctl -u verdis-node.service -f -o cat
```

---

## 4. Forkless Runtime Upgrade Process

Substrate enables forkless runtime upgrades by compiling state transition logic into a WebAssembly (WASM) binary and executing it on-chain via the `System` pallet.

```
       [ Source Code ] 
              │
              ▼ (cargo build --release)
   [ verdis_runtime.compact.compressed.wasm ]
              │
              ▼ (Submit Extrinsic)
  [ System.setCode / Sudo / Democracy ]
              │
              ▼ (State Transition)
  [ On-Chain Runtime Updated Live @ Next Block ]
```

### Step 1: Build & Compress WASM Runtime

```bash
cd /opt/verdis-chain-rust

# Build the WASM runtime blob
cargo build --release -p verdis-runtime

# Locate compiled compressed WASM runtime binary
ls -la target/release/wbuild/verdis-runtime/verdis_runtime.compact.compressed.wasm
```

### Step 2: Compute WASM Hash Digest

Use `subwasm` or `sha256sum` to verify the compiled runtime hash:

```bash
sha256sum target/release/wbuild/verdis-runtime/verdis_runtime.compact.compressed.wasm
```

### Step 3: Submit `system.setCode` Extrinsic via Sudo or Governance

#### Option A: Governance / Sudo Extrinsic (Dev/Initial Mainnet)
1. Open Polkadot.js Apps / Verdis Explorer UI connected to `wss://verdischain.com`.
2. Navigate to **Developer → Sudo** (or **Governance → Democracy** proposal).
3. Select call: `system → setCode(code)`.
4. Upload `verdis_runtime.compact.compressed.wasm`.
5. Submit and sign extrinsic.

#### Option B: Programmatic Sudo Submission via RPC / Subxt Script
```typescript
import { ApiPromise, WsProvider, Keyring } from '@polkadot/api';
import fs from 'fs';

async function performRuntimeUpgrade() {
  const provider = new WsProvider('ws://127.0.0.1:9944');
  const api = await ApiPromise.create({ provider });
  const keyring = new Keyring({ type: 'sr25519' });
  const sudoAccount = keyring.addFromUri('//Alice'); // Sudo key

  const wasmCode = fs.readFileSync('target/release/wbuild/verdis-runtime/verdis_runtime.compact.compressed.wasm');
  const hexCode = '0x' + wasmCode.toString('hex');

  const setCodeTx = api.tx.system.setCode(hexCode);
  const sudoTx = api.tx.sudo.sudoUncheckedWeight(setCodeTx, { refTime: 1000000000, proofSize: 0 });

  await sudoTx.signAndSend(sudoAccount, ({ status, events }) => {
    console.log(`Transaction status: ${status.type}`);
    if (status.isInBlock) {
      console.log(`Included in block: ${status.asInBlock}`);
    }
  });
}

performRuntimeUpgrade();
```

### Step 4: Verify Runtime Upgrade Execution

Query system spec version via RPC to verify upgrade success:

```bash
curl -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method": "state_getRuntimeVersion", "params":[]}' \
  http://localhost:9944
```

Verify `specVersion` has incremented (e.g., from `200` to `201`).

---

## 5. Emergency Upgrade & Rollback Procedures

### 5.1. Emergency Halt or Consensus Stall Recovery

If bad runtime code causes block production or GRANDPA finality to halt:

1. **Stop Validator Nodes:**
   ```bash
   sudo systemctl stop verdis-node.service
   ```

2. **Revert Node Binary to Previous Stable Version:**
   ```bash
   cp /opt/verdis-chain-rust/target/release/verdis.v2.0.0.bak /opt/verdis-chain-rust/target/release/verdis
   ```

3. **Restore Last Valid Database Backup (if state corruption occurred):**
   ```bash
   rm -rf /opt/verdis-chain-rust/data/chains/verdis_chain/db
   tar -xzf /var/backups/verdis/daily/verdis_backup_latest.tar.gz -C /opt/verdis-chain-rust/data/
   ```

4. **Restart Node with Emergency CLI Overrides:**
   ```bash
   /opt/verdis-chain-rust/target/release/verdis \
     --chain /opt/verdis-chain-rust/customSpecRaw.json \
     --base-path /opt/verdis-chain-rust/data \
     --validator \
     --force-authoring
   ```

---

## 6. Multi-Node Rolling Upgrade Coordination

For a multi-validator network (101 validators):

1. **Window Alignment:** Do not perform client restarts during epoch transition boundaries (block numbers equal to `0 mod 600`).
2. **Rolling Staggering:** Upgrade validators in batches of 10-20% at a time.
3. **Liveness Threshold:** Ensure at least 67% (`2/3 + 1`) of total GRANDPA voting weight remains online at all times to prevent finality stalls.

---

## 7. Version Compatibility Matrix

| Client Version | Runtime Spec | Spec Version | BABE Epoch Length | Supported Pallets | Compatibility Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `v1.0.0` | `verdis-200` | `200` | 600 blocks | 15 Pallets | Initial launch version |
| `v2.0.0` | `verdis-200` | `200` | 600 blocks | 17 Pallets | Added EcoPallet & CarbonPallet |
| `v2.1.0` | `verdis-201` | `201` | 600 blocks | 17 Pallets | Performance & DPoS reward tuning |

---

## 8. Post-Upgrade Verification Checklist

After applying an upgrade, verify the following:

```bash
# 1. Check block production progress (best block incrementing every 6s)
curl -s -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "chain_getHeader", "params":[]}' http://localhost:9944 | jq .

# 2. Check GRANDPA finality block
curl -s -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "chain_getFinalizedHead", "params":[]}' http://localhost:9944 | jq .

# 3. Verify total VRDX token supply on-chain via pallet balances query
curl -s -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "state_getStorage", "params":["REDACTED_KEY"]}' http://localhost:9944
```

---

## 9. Upgrade Troubleshooting

| Error / Failure | Cause | Solution |
| :--- | :--- | :--- |
| `CodeTooLarge` | Runtime WASM binary exceeds maximum code size limit | Enable WASM compression (`wasm-opt -O3` or compact build). |
| `BadOrigin` | Extrinsic submitted without root or sudo privilege | Ensure caller account possesses Sudo key or Democracy proposal passed. |
| `SpecVersionNotHigher` | New WASM spec version equals or is lower than on-chain spec version | Increment `spec_version` in `runtime/src/lib.rs` and recompile WASM. |
| GRANDPA Finality Stalled | Insufficient online validators during rolling restart | Verify active validator quorum (>67% voting power online). |

---

## 10. Community & Operator Communication Plan

When executing scheduled network upgrades:

1. **T-48 Hours:** Publish formal Upgrade Notice on GitHub Release Notes and community announcement channels.
2. **T-2 Hours:** Send final readiness check ping to validator operator channels.
3. **T-0 Hours:** Execute `system.setCode` extrinsic or launch rolling binary update.
4. **T+1 Hour:** Publish Upgrade Completion report verifying network block production and finality metrics.
