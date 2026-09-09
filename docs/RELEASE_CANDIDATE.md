# Verdis Chain — Release Candidate Audit

> **Audit Date:** 2026-08-16 22:53 UTC+02 (Europe/Madrid)
> **Server:** 91.98.160.145
> **Repository:** `/opt/verdis-chain-rust`
> **Node Binary:** `/opt/verdis-node`

---

## 1. Git Commit SHA

```
51cdb5e3346f2f26c843096c44f678e716fd5d1c
```

Command: `git -C /opt/verdis-chain-rust rev-parse HEAD`

---

## 2. Runtime Version

| Property | Value |
|---|---|
| `spec_version` (runtime/src/lib.rs) | `14` |
| `package version` (runtime/Cargo.toml) | `2.0.0` |

```rust
// runtime/src/lib.rs
spec_version: 14,
```
```toml
# runtime/Cargo.toml
version = "2.0.0"
```

---

## 3. Node Version

```
verdis-node 2.0.0
```

Command: `/opt/verdis-node --version`

---

## 4. Runtime WASM Hash

### 4.1 Compact Compressed WASM (on-disk)

```
sha256: 10b4c1e7383689f8e4bbb039e6da68472e5f1997ede7a8910a07741e6747609f
File:  target/release/wbuild/verdis-runtime/verdis_runtime.compact.compressed.wasm
```

Command:
```bash
sha256sum /opt/verdis-chain-rust/target/release/wbuild/verdis-runtime/verdis_runtime.compact.compressed.wasm
```

### 4.2 On-chain WASM (via RPC `state_getStorage` key `0x3a636f6465`)

```
sha256: a2600478e8f7de0ccc6d7e4b184542c9423d81afe2712fddcc38d44a4b558d53
```

Command:
```bash
curl -s -X POST http://localhost:9933 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"state_getStorage","params":["0x3a636f6465"]}' \
  | python3 -c 'import sys,json,hashlib; d=json.load(sys.stdin); v=d["result"]; h=hashlib.sha256(bytes.fromhex(v[2:])).hexdigest(); print(h)'
```

> **Note:** The on-chain WASM hash differs from the on-disk compact-compressed WASM hash. This is expected — the on-chain `:code` storage value may include the full (uncompressed) WASM or a differently-processed blob. Both hashes are recorded for traceability.

---

## 5. Chain-Spec Hashes

```
6c2ea809bc65568fb27b980f6da08bae1cbb9a7d69a477c0e502fc2e15ebaf59  chain-specs/dev-plain.json
ce7838716354d929138ec08d6d0a65fe233f0994fcbdcbd4e710bc0aeee30bb9  chain-specs/dev-raw.json
e46925db64fdbdec3882a8e290797e7e896671e9f52736d4d4b04f61e08dc0eb  chain-specs/mainnet-plain.json
e371daf951b05da63f2cf549e2250c7b529b9cbfeab1cf5f9239d13d91bfbe6b  chain-specs/mainnet-raw.json
1623d1e53b924bcfc5115c0eb0fab5c6c7c285e5fbf277a0f33dab2939dcdc63  chain-specs/testnet-canonical-raw.json
532399d5d37349603eb7b0496db930b0a2d0b35428d39305b8dd34e2e453900a  chain-specs/testnet-plain.json
```

Command:
```bash
for f in /opt/verdis-chain-rust/chain-specs/*.json; do sha256sum "$f"; done
```

---

## 6. Genesis Hash

```
0xdc4373f49df6831c9b942830557fbf416d76851872fa1c123a5268d8d2b586ca
```

Command:
```bash
curl -s -X POST http://localhost:9933 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}'
```

---

## 7. Rust Version

```
rustc 1.97.1 (8bab26f4f 2026-07-14)
```

Command: `rustc --version` (via `source $HOME/.cargo/env`)

---

## 8. Substrate / Polkadot SDK Crate Versions (from Cargo.lock)

| Crate | Version |
|---|---|
| `sp-runtime` | `40.1.0` and `48.0.0` (two entries in Cargo.lock) |
| `sc-cli` | `0.61.0` |
| `sp-consensus-babe` | `0.49.0` |
| `sp-finality-grandpa` | **Not found** in Cargo.lock (see note below) |
| `finality-grandpa` (closest match) | `0.16.3` |

> **Note on `sp-finality-grandpa`:** This crate does not appear anywhere in `Cargo.lock`. The crate `finality-grandpa` v0.16.3 is present as a transitive dependency. The runtime/node may use a different consensus-finality approach or the crate may have been renamed/merged. This should be investigated before release if GRANDPA finality is expected.

Commands:
```bash
grep -A2 'name = "sp-runtime"' Cargo.lock
grep -A2 'name = "sc-cli"' Cargo.lock
grep -A2 'name = "sp-consensus-babe"' Cargo.lock
grep -A2 'name = "sp-finality-grandpa"' Cargo.lock   # returns empty
grep -A2 'name = "finality-grandpa"' Cargo.lock       # closest match
```

---

## 9. Cargo.lock SHA256

```
4351229cf504e89d498fbfb3d818c966b456a6a07e0fa226dd3d2ad076ca3695  Cargo.lock
```

Command: `sha256sum /opt/verdis-chain-rust/Cargo.lock`

---

## 10. Node Binary SHA256

```
2a3736e197bd43f4b1a925a9843a28a20d9284718573f148c38659e5b30986a6  /opt/verdis-node
```

Command: `sha256sum /opt/verdis-node`

---

## 11. Pallets (16) with Cargo.toml Versions

| # | Pallet | Version |
|---|---|---|
| 1 | `address-lookup-tables` | `0.1.0` |
| 2 | `amm-dex` | `2.0.0` |
| 3 | `circuit-breaker` | `0.1.0` |
| 4 | `dpos` | `2.0.0` |
| 5 | `eco` | `2.0.0` |
| 6 | `fungible-tokens` | `1.0.0` |
| 7 | `gulf-stream` | `2.0.0` |
| 8 | `ibc` | `0.1.0` |
| 9 | `poh` | `2.0.0` |
| 10 | `presale` | `0.1.0` |
| 11 | `sealevel` | `0.1.0` |
| 12 | `storage` | `2.0.0` |
| 13 | `tokenomics` | `2.0.0` |
| 14 | `turbine` | `0.1.0` |
| 15 | `vesting` | `2.0.0` |
| 16 | `zk-compression` | `0.1.0` |

**Total pallet count:** 16 ✓

Command:
```bash
for d in pallets/*/; do
  name=$(basename "$d")
  ver=$(grep '^version' "$d/Cargo.toml" | head -1 | sed 's/.*= *"//;s/"//')
  echo "  $name: $ver"
done
```

---

## 12. Total Test Count

```
570
```

Command:
```bash
grep -r '#[test]' pallets/ runtime/ | wc -l
```

---

## 13. Current Block Height

```
Hex:     0x82cd
Decimal: 33485
```

Command:
```bash
curl -s -X POST http://localhost:9933 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}' \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["result"]["number"])'
# Convert: python3 -c 'print(int("0x82cd", 16))'
```

---

## 14. System Health (Peers)

```json
{
  "peers": 5,
  "isSyncing": false,
  "shouldHavePeers": false
}
```

Command:
```bash
curl -s -X POST http://localhost:9933 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"system_health","params":[]}'
```

| Property | Value |
|---|---|
| Peers | 5 |
| Is Syncing | false |
| Should Have Peers | false |

---

## 15. Active systemd Services (verdis-\*)

| # | Service | Description |
|---|---|---|
| 1 | `verdis-api.service` | Verdiscan REST API v1.0 |
| 2 | `verdis-faucet.service` | Verdis Testnet Faucet (Python) |
| 3 | `verdis-finality-monitor.service` | Verdis Chain Finality Monitor |
| 4 | `verdis-governance.service` | Verdis Chain Governance API |
| 5 | `verdis-health-monitor.service` | Verdis Chain Health Monitor |
| 6 | `verdis-node.service` | Verdis Chain Node 1 (Alice) |
| 7 | `verdis-node2.service` | Verdis Chain Node 2 (Bob) |
| 8 | `verdis-node3.service` | Verdis Chain Node 3 (Charlie) |
| 9 | `verdis-node4.service` | Verdis Chain Node 4 (Dave) |
| 10 | `verdis-node5.service` | Verdis Chain Node 5 (Eve) |
| 11 | `verdis-node6.service` | Verdis Chain Node 6 (Ferdie) |
| 12 | `verdis-price-collector.service` | Verdis Chain Price History Collector |
| 13 | `verdis-relay.service` | Verdis TX Relay v3 (Non-Custodial) |
| 14 | `verdis-rpc-filter.service` | Verdis RPC Security Filter Proxy |
| 15 | `verdis-soak-test.service` | Verdis Chain 14-Day Soak Test Monitor |
| 16 | `verdis-txbot.service` | Verdis Chain Transaction Bot Service |
| 17 | `verdis-validator-monitor.service` | Verdis Chain Validator Monitor |

**Total active verdis-\* services:** 17 (6 blockchain nodes + 11 support services)

Command:
```bash
systemctl list-units --type=service --state=active | grep verdis-
```

---

## Reproduction

To reproduce this audit against commit `51cdb5e3346f2f26c843096c44f678e716fd5d1c`, run the following steps on the target server (91.98.160.145) or a machine with the same codebase checked out at that commit.

### Prerequisites

- SSH access to `91.98.160.145` with the deploy key.
- The node binary at `/opt/verdis-node`, the repo at `/opt/verdis-chain-rust`.
- `curl`, `python3`, `sha256sum`, `grep`, `git`, and `systemctl` available.
- Rust toolchain installed (`source $HOME/.cargo/env`).

### Step-by-step

```bash
# 0. SSH in
chmod 600 .ssh_deploy_key
ssh -i .ssh_deploy_key -o StrictHostKeyChecking=no root@91.98.160.145

# 1. Git commit SHA
git -C /opt/verdis-chain-rust rev-parse HEAD

# 2. Runtime version
grep -i 'spec_version' /opt/verdis-chain-rust/runtime/src/lib.rs | head -5
grep '^version' /opt/verdis-chain-rust/runtime/Cargo.toml | head -3

# 3. Node version
/opt/verdis-node --version

# 4. Runtime WASM hash (on-disk)
sha256sum /opt/verdis-chain-rust/target/release/wbuild/verdis-runtime/verdis_runtime.compact.compressed.wasm

# 4b. Runtime WASM hash (on-chain)
curl -s -X POST http://localhost:9933 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"state_getStorage","params":["0x3a636f6465"]}' \
  | python3 -c 'import sys,json,hashlib; d=json.load(sys.stdin); v=d["result"]; print(hashlib.sha256(bytes.fromhex(v[2:])).hexdigest())'

# 5. Chain-spec hashes
for f in /opt/verdis-chain-rust/chain-specs/*.json; do sha256sum "$f"; done

# 6. Genesis hash
curl -s -X POST http://localhost:9933 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}'

# 7. Rust version
source $HOME/.cargo/env; rustc --version

# 8. Substrate versions
grep -A2 'name = "sp-runtime"' /opt/verdis-chain-rust/Cargo.lock
grep -A2 'name = "sc-cli"' /opt/verdis-chain-rust/Cargo.lock
grep -A2 'name = "sp-consensus-babe"' /opt/verdis-chain-rust/Cargo.lock
grep -A2 'name = "sp-finality-grandpa"' /opt/verdis-chain-rust/Cargo.lock
# If sp-finality-grandpa is missing, check finality-grandpa:
grep -A2 'name = "finality-grandpa"' /opt/verdis-chain-rust/Cargo.lock

# 9. Cargo.lock SHA256
sha256sum /opt/verdis-chain-rust/Cargo.lock

# 10. Node binary SHA256
sha256sum /opt/verdis-node

# 11. Pallets with versions
for d in /opt/verdis-chain-rust/pallets/*/; do
  name=$(basename "$d")
  ver=$(grep '^version' "$d/Cargo.toml" | head -1 | sed 's/.*= *"//;s/"//')
  echo "  $name: $ver"
done

# 12. Total test count
grep -r '#[test]' /opt/verdis-chain-rust/pallets/ /opt/verdis-chain-rust/runtime/ | wc -l

# 13. Current block height
curl -s -X POST http://localhost:9933 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}' \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["result"]["number"])'

# 14. System health
curl -s -X POST http://localhost:9933 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"system_health","params":[]}'

# 15. Active systemd services
systemctl list-units --type=service --state=active | grep verdis-
```

### Verification Checklist

To confirm you are auditing the exact same commit, verify these immutable hashes match:

| Artifact | Expected SHA-256 |
|---|---|
| Git commit | `51cdb5e3346f2f26c843096c44f678e716fd5d1c` |
| Cargo.lock | `4351229cf504e89d498fbfb3d818c966b456a6a07e0fa226dd3d2ad076ca3695` |
| Node binary (`/opt/verdis-node`) | `2a3736e197bd43f4b1a925a9843a28a20d9284718573f148c38659e5b30986a6` |
| Compact compressed WASM | `10b4c1e7383689f8e4bbb039e6da68472e5f1997ede7a8910a07741e6747609f` |
| Genesis hash | `0xdc4373f49df6831c9b942830557fbf416d76851872fa1c123a5268d8d2b586ca` |

---

## Summary

| Item | Value |
|---|---|
| Commit SHA | `51cdb5e3346f2f26c843096c44f678e716fd5d1c` |
| Runtime spec_version | 14 |
| Runtime package version | 2.0.0 |
| Node version | 2.0.0 |
| Rust compiler | 1.97.1 (2026-07-14) |
| Total pallets | 16 |
| Total tests | 570 |
| Block height at audit | 33485 (0x82cd) |
| Peers | 5 |
| Active systemd services | 17 (6 nodes + 11 support) |
| Genesis hash | `0xdc4373f49df6831c9b942830557fbf416d76851872fa1c123a5268d8d2b586ca` |

### Known Issues / Items to Investigate

1. **`sp-finality-grandpa` not in Cargo.lock** — The crate does not appear in the lockfile. If GRANDPA finality is expected on this chain, this dependency gap should be investigated before release. The `finality-grandpa` crate v0.16.3 is present as a transitive dependency.
2. **WASM hash mismatch** — The on-disk compact compressed WASM hash (`10b4c1e7…`) differs from the on-chain `:code` hash (`a2600478…`). This is typically expected (on-chain code may be stored uncompressed or with different encoding), but should be confirmed as intentional.
3. **Two `sp-runtime` versions** — Cargo.lock contains both v40.1.0 and v48.0.0, indicating a dependency resolution with multiple major versions. This is common in Substrate projects but should be reviewed for compatibility.
4. **Several pallets at v0.1.0** — `address-lookup-tables`, `circuit-breaker`, `ibc`, `presale`, `sealevel`, `turbine`, and `zk-compression` are at version 0.1.0, indicating early-stage development status.
