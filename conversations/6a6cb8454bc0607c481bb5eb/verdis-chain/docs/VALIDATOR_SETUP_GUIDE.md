# VERDIS CHAIN — VALIDATOR SETUP GUIDE

**Version:** 1.0
**Date:** 2026-08-14
**Status:** Draft (mainnet not live)

---

## PREREQUISITES

### Hardware Requirements

| Requirement | Minimum | Recommended |
|---|---|---|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Storage | 100 GB SSD | 500 GB NVMe SSD |
| Network | 100 Mbps | 1 Gbps |
| Uptime | 99% | 99.9% |
| OS | Ubuntu 22.04 LTS | Ubuntu 24.04 LTS |

### Software Requirements

- Rust (stable toolchain)
- LLVM/Clang (for Substrate compilation)
- protobuf-compiler
- libssl-dev, pkg-config
- Docker (optional, for containerized setup)

### Token Requirements

- **Minimum stake:** 10,000 VRDX (10M units with 9 decimals)
- **Recommended stake:** 50,000+ VRDX (for competitive selection)
- Stake must be in your controller account

---

## STEP 1: BUILD THE NODE

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
rustup default stable

# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
  build-essential \
  clang \
  libclang-dev \
  libssl-dev \
  protobuf-compiler \
  pkg-config

# Clone the repository
git clone https://github.com/Protremix/Verdischain-.git
cd Verdischain-

# Build the node
cargo build --release

# Verify the binary
./target/release/verdis --version
```

---

## STEP 2: GENERATE VALIDATOR KEYS

**CRITICAL: Generate keys on an air-gapped machine. Never expose private keys.**

### 2.1 Generate Session Keys

Verdis Chain uses two key types for consensus:
- **BABE key** (sr25519): Block production
- **GRANDPA key** (ed25519): Block finality

```bash
# On an air-gapped machine:
subkey generate --scheme sr25519
# Output: Public key (SS58) + Mnemonic (WRITE DOWN SECURELY)

subkey generate --scheme ed25519
# Output: Public key (SS58) + Mnemonic (WRITE DOWN SECURELY)
```

### 2.2 Insert Keys into Node

```bash
# Insert BABE key (sr25519)
./target/release/verdis key insert \
  --base-path /opt/verdis-validator \
  --chain mainnet \
  --scheme sr25519 \
  --suri "YOUR_MNEMONIC" \
  --key-type babe

# Insert GRANDPA key (ed25519)
./target/release/verdis key insert \
  --base-path /opt/verdis-validator \
  --chain mainnet \
  --scheme ed25519 \
  --suri "YOUR_MNEMONIC" \
  --key-type gran
```

### 2.3 Export Public Keys (for registration)

```bash
./target/release/verdis key inspect --scheme sr25519 "YOUR_BABE_MNEMONIC"
# Note the SS58 address

./target/release/verdis key inspect --scheme ed25519 "YOUR_GRANDPA_MNEMONIC"
# Note the SS58 address
```

---

## STEP 3: REGISTER AS VALIDATOR

### 3.1 Fund Your Account

Ensure your controller account has at least 10,001 VRDX (stake + existential deposit).

### 3.2 Register via DPoS Pallet

```bash
# Via TX Relay API
curl -X POST https://verdischain.com/api/tx-relay/submit \
  -H "Content-Type: application/json" \
  -d '{
    "method": "dpos",
    "call": "register_validator",
    "args": {
      "green_score": 3,
      "energy_source": "solar"
    },
    "signer": "YOUR_SS58_ADDRESS"
  }'
```

### 3.3 Set Session Keys

```bash
curl -X POST https://verdischain.com/api/tx-relay/submit \
  -H "Content-Type: application/json" \
  -d '{
    "method": "session",
    "call": "set_keys",
    "args": {
      "keys": {
        "babe": "0xYOUR_BABE_PUBLIC_KEY",
        "grandpa": "0xYOUR_GRANDPA_PUBLIC_KEY"
      },
      "proof": "0x"
    },
    "signer": "YOUR_SS58_ADDRESS"
  }'
```

---

## STEP 4: START THE NODE

### 4.1 As a Systemd Service

```bash
sudo tee /etc/systemd/system/verdis-validator.service << 'SERVICE'
[Unit]
Description=Verdis Chain Validator
After=network.target

[Service]
Type=simple
User=verdis
ExecStart=/opt/verdis-chain/target/release/verdis \
  --chain mainnet \
  --base-path /opt/verdis-validator-data \
  --validator \
  --name "YOUR_VALIDATOR_NAME" \
  --port 30333 \
  --rpc-port 9933 \
  --rpc-methods=Safe \
  --no-telemetry
Restart=always
RestartSec=10
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable verdis-validator
sudo systemctl start verdis-validator
```

### 4.2 Verify Node is Running

```bash
# Check service status
sudo systemctl status verdis-validator

# Check block sync
curl -X POST http://localhost:9933 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}'

# Check peer count
curl -X POST http://localhost:9933 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"system_peers","params":[],"id":1}'
```

---

## STEP 5: DELEGATE (FOR DELEGATORS)

If you are a delegator (not running your own node):

```bash
curl -X POST https://verdischain.com/api/tx-relay/submit \
  -H "Content-Type: application/json" \
  -d '{
    "method": "dpos",
    "call": "delegate",
    "args": {
      "validator": "VALIDATOR_SS58_ADDRESS",
      "amount": 5000000000000
    },
    "signer": "YOUR_SS58_ADDRESS"
  }'
```

---

## STEP 6: MONITORING

### Health Check

```bash
# Block height (should be increasing)
curl -s -X POST http://localhost:9933 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}' \
  | python3 -c "import sys,json; print(f'Block #{json.loads(sys.stdin.read())[\"result\"][\"number\"]}')"

# Peer count (should be >0)
curl -s -X POST http://localhost:9933 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"system_peers","params":[],"id":1}' \
  | python3 -c "import sys,json; print(f'Peers: {len(json.loads(sys.stdin.read())[\"result\"])}')"

# Your validator status
curl -s -X POST http://localhost:9933 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"dpos_validatorInfo","params":["YOUR_SS58_ADDRESS"],"id":1}'
```

### Logs

```bash
journalctl -u verdis-validator -f
```

---

## SECURITY BEST PRACTICES

1. **Never share your mnemonic** — Write it down on paper, store in a safe
2. **Use a dedicated machine** — Don't run other services on your validator
3. **Keep software updated** — Regularly pull and rebuild from the repository
4. **Monitor uptime** — Set up alerts for node downtime
5. **Use a firewall** — Only allow P2P (30333) and SSH (22, key-only)
6. **Backup your keystore** — Keep encrypted backups of your session keys
7. **Use sentry nodes** — For production, run sentry nodes to protect your validator's IP

---

## TROUBLESHOOTING

| Issue | Solution |
|---|---|
| Node not syncing | Check peers: `system_peers`. Ensure P2P port 30333 is open. |
| Not producing blocks | Verify session keys are set. Check if you're in the active validator set. |
| Low peer count | Add bootnodes. Check firewall. Verify P2P port. |
| "Invalid genesis" | Ensure you're using the correct chain spec (`--chain mainnet`). |
| Keys not found | Re-insert keys with `verdis key insert`. Verify base-path. |

---

## RPC REFERENCE

### Key Methods

| Method | Description |
|---|---|
| `chain_getHeader` | Get latest block header |
| `chain_getBlock` | Get full block by hash |
| `system_peers` | Get connected peers |
| `system_health` | Get node health |
| `dpos_allValidators` | List all validators |
| `dpos_validatorStake` | Get validator stake |
| `dpos_validatorName` | Get validator name |
| `eco_getGreenScore` | Get validator green score |
| `eco_getAllGreenValidators` | List green validators |
| `amm_getAllPools` | List DEX pools |
| `amm_getPoolInfo` | Get pool details |

---

## DISCLAIMER

This guide is for the Verdis Chain testnet. Mainnet is not yet live. Validator requirements and parameters may change before mainnet launch. Always verify against the latest chain spec.
