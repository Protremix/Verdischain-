# VERDIS CHAIN — TREASURY MULTISIG SECURITY SPECIFICATION

**Created:** 2026-08-14
**Status:** SPECIFICATION (implementation pending key ceremony)
**Authorization:** Rojs Gordons, CEO

---

## 1. SECURITY MODEL

### 1.1 Treasury Control

The Verdis Chain Treasury (20B VRDX) is controlled by a **3-of-5 multisignature authorization scheme**.

| Parameter | Value |
|---|---|
| Threshold | 3 of 5 signers required |
| Total signers | 5 |
| Minimum to authorize | 3 independent signatures |
| Single-signer control | **IMPOSSIBLE** — no single signer can independently authorize a Treasury transfer |

### 1.2 Key Generation

- All 5 signer keys are **independently generated** using the air-gapped key ceremony script (`scripts/air-gapped-key-ceremony.sh`)
- Keys are generated on an **air-gapped machine** with no network connectivity
- Each key pair is generated using the `sr25519` scheme (Schnorrkel/Ristretto)
- Private keys **never leave** the air-gapped environment

### 1.3 Physical Custody

Each of the 5 signer keys is stored under **separate physical custody procedures**:

- No single individual holds more than one key
- Each key is stored in a separate physical location
- Key custodians are documented and verified
- Key recovery procedures require multi-party cooperation
- Private keys are never exposed to networked systems

---

## 2. IMPLEMENTATION

### 2.1 Current State (Testnet)

| Component | Current | Status |
|---|---|---|
| Treasury account | `PalletId(*b"verdist0")` | Pallet-controlled |
| Team multisig | `PalletId(*b"verdistm")` | **PLACEHOLDER** — must be replaced |
| Spend origin | Council 2/3 (`EnsureCouncilSpend`) | Governance-based |
| Multisig pallet | `pallet_multisig` (instance 38) | Available |

### 2.2 Mainnet Target State

| Component | Target | Status |
|---|---|---|
| Treasury account | `PalletId(*b"verdist0")` | Pallet-controlled (unchanged) |
| Team multisig | **Real 3-of-5 multisig address** | Pending key ceremony |
| Spend origin | **3-of-5 multisig + Council 2/3** | Pending implementation |
| Multisig threshold | 3 | Set in genesis or first governance proposal |

### 2.3 Code Changes Required

1. **Replace PalletId placeholder**: After the air-gapped key ceremony, compute the 3-of-5 multisig address from the 5 cold-storage public keys and replace `PalletId(*b"verdistm")` in `node/src/chain_spec.rs:mainnet_genesis()`.

2. **Initialize multisig in genesis**: Add a genesis configuration to `pallet_multisig` that pre-creates the 3-of-5 multisig with the 5 cold-storage public keys as signatories.

3. **Strengthen spend origin**: Update `EnsureCouncilSpend` to additionally require the multisig threshold, or create a new origin type `EnsureMultisigTreasurySpend` that requires 3-of-5.

4. **Import keys script**: Use `scripts/import-mainnet-keys.py` to compute the multisig address from the ceremony output and patch the chain spec.

### 2.4 Multisig Address Computation

The 3-of-5 multisig address is computed as:

```
multisig_address = AccountId32(blake2_256(threshold ++ sorted_signatories))
```

Using `pallet_multisig`:
```bash
verdis-node key multisig --threshold 3 --signatories <addr1>,<addr2>,<addr3>,<addr4>,<addr5>
```

---

## 3. CEREMONY PROCEDURE

### 3.1 Pre-Requisites

- Air-gapped machine (no WiFi, no Ethernet, no Bluetooth)
- USB drive for key export (public keys only)
- `subkey` or `verdis-node key` tool installed
- 5 designated key custodians present (or sequential key generation)

### 3.2 Execution

```bash
# On air-gapped machine:
chmod +x scripts/air-gapped-key-ceremony.sh
./scripts/air-gapped-key-ceremony.sh --output /mnt/usb/ceremony-output
```

### 3.3 Post-Ceremony

1. Import public keys into chain spec:
   ```bash
   python3 scripts/import-mainnet-keys.py --ceremony-dir /path/to/ceremony-output
   ```

2. Verify the multisig address in the chain spec:
   ```bash
   verdis-node key multisig --threshold 3 --signatories <addr1>,<addr2>,<addr3>,<addr4>,<addr5>
   ```

3. Verify genesis determinism:
   ```bash
   verdis-node build-spec --chain mainnet --raw > mainnet-raw.json
   sha256sum mainnet-raw.json
   ```

---

## 4. TREASURY SPEND FLOW (MAINNET)

```
Treasury Spend Proposal
    ↓
Council approves (2/3 majority)
    ↓
3-of-5 multisig signers review
    ↓
Minimum 3 signers approve (each signs independently)
    ↓
Treasury transfer executes
```

No single point of failure. No single signer. No single governance body.

---

## 5. SECURITY GUARANTEES

| Guarantee | How Enforced |
|---|---|
| No single-signer control | 3-of-5 threshold (pallet_multisig) |
| Independent key generation | Air-gapped ceremony (scripts/air-gapped-key-ceremony.sh) |
| Separate physical custody | Documented custodians, separate locations |
| No server-side key custody | Private keys never on networked systems |
| Transparent authorization | All multisig approvals are on-chain |
| Emergency recovery | 3-of-5 threshold allows 2 key losses without lockout |

---

## 6. VERIFICATION CHECKLIST

- [ ] Air-gapped ceremony executed
- [ ] 5 cold-storage keys generated
- [ ] 3-of-5 multisig address computed
- [ ] PalletId(*b"verdistm") replaced in chain spec
- [ ] pallet_multisig genesis configured with 5 signatories
- [ ] Treasury spend origin updated to require multisig
- [ ] Genesis determinism verified (sha256sum matches across nodes)
- [ ] Key custodians documented
- [ ] Physical custody procedures documented
- [ ] Recovery procedures documented
