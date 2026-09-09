# Runtime Upgrade Process (ARCH-029)

**Status:** Must be tested with try-runtime before mainnet

---

## 1. Overview

Runtime upgrades on Verdis Chain follow the Substrate storage migration pattern. Upgrades are high-risk operations that can brick the chain if done incorrectly.

## 2. Pre-Upgrade Checklist

- [ ] All tests pass on the new runtime (`cargo test --workspace`)
- [ ] `try-runtime` migration tested on a fork of live state
- [ ] Genesis config changes verified for consistency (`scripts/check_genesis_consistency.py`)
- [ ] Storage version incremented if migrations are needed
- [ ] Weight calculations updated for any modified dispatchables
- [ ] No pallet removed without storage migration (or deliberate storage clear)
- [ ] No pallet added without genesis config
- [ ] CI release gates pass (fmt, clippy, test, tokenomics, release build, WASM build, hygiene)

## 3. Upgrade Process

### 3.1 Development
1. Create new runtime version in `runtime/src/lib.rs` (increment `spec_version`)
2. Implement any storage migrations in the pallet's `on_runtime_upgrade` hook
3. Update tests
4. Run `cargo test --workspace`

### 3.2 Testing
1. Build new WASM runtime: `cargo build --release --target wasm32-unknown-unknown -p verdis-runtime`
2. Use `try-runtime` to test migration on live state:
   ```
   try-runtime --runtime target/wasm32-unknown-unknown/release/verdis_runtime.wasm \
     on-runtime-upgrade live --uri ws://localhost:9944
   ```
3. Verify all storage migrations succeed
4. Verify no panics in `on_runtime_upgrade`

### 3.3 Deployment
1. Submit `set_code` extrinsic via governance (council motion + referendum)
2. Monitor block production after upgrade
3. Verify all pallets functional post-upgrade
4. If failure: emergency rollback via previous WASM (if available)

### 3.4 Post-Upgrade
1. Verify block production continues
2. Run health checks (RPC, DEX, staking, vesting)
3. Update documentation with new spec_version
4. Publish upgrade summary

## 4. Emergency Rollback

If a runtime upgrade causes a chain halt:
1. Validators coordinate to revert to previous runtime WASM
2. Use `set_code` with the previous WASM blob
3. Requires 2/3+ council approval (or emergency root if available)
4. Document the failure in post-mortem

## 5. Governance

- Mainnet: Runtime upgrades require council motion + referendum
- No sudo on mainnet (removed)
- Emergency upgrades require supermajority council approval
- No single party can unilaterally upgrade the runtime

## Governance origins (measured from runtime/src/lib.rs, not assumed)

`construct_runtime` mapping:

| Instance | Pallet | Index |
|---|---|---|
| `Instance1` | **Council** | 43 |
| `Instance2` | **TechnicalCommittee** | 61 |

Democracy `Config` origins — **every one of these is `Instance1` = Council**:

| Config type | Required origin | Line |
|---|---|---|
| `ExternalOrigin` | Council 1/2 | 1424 |
| `ExternalMajorityOrigin` | Council 2/3 | 1426 |
| `ExternalDefaultOrigin` | Council 1/2 | 1428 |
| `SubmitOrigin` | any signed account | 1430 |
| `FastTrackOrigin` | **Council 2/3** | 1431 |
| `InstantOrigin` | Council 1/1 (unanimous) | 1433 |
| `CancellationOrigin` | Council 2/3 | 1435 |
| `BlacklistOrigin` | Council 2/3 | 1438 |
| `CancelProposalOrigin` | Council 2/3 | 1441 |
| `VetoOrigin` | any signed account | 1443 |

**The TechnicalCommittee has no Democracy origin at all.** It exists in the runtime but grants no
governance power over upgrades. A `fast_track` submitted through it returns `BadOrigin`.

### Runtime governance parameters (read live from chain)

| Parameter | Value | At 6 s/block |
|---|---|---|
| `FastTrackVotingPeriod` | 300 blocks | ~30 min |
| `VotingPeriod` | 600 blocks | ~60 min |
| `LaunchPeriod` | 600 blocks | ~60 min |
| `EnactmentPeriod` | 600 blocks | ~60 min |
| `CooloffPeriod` | 600 blocks | ~60 min |
| `MinimumDeposit` | 1 000 VRDX | — |
| `InstantAllowed` | `false` | — |

`InstantAllowed = false` means **no upgrade can bypass the 300-block voting period**, even with a
unanimous Council. The floor on any emergency runtime upgrade is ~30 minutes.

### Working upgrade procedure (executed on testnet, spec 17 -> 18)

`EnsureProportionAtLeast<_, Instance1, 2, 3>` checks the **motion's threshold** against member
count. With 3 members it requires `threshold >= 2`. Setting `threshold = 3` demands unanimity and
fails the 2/3 check when only 2 members vote aye.

1. `Preimage.note_preimage(System.set_code(wasm))` — any signed account; ~1.49 MB, deposit reserved
2. `Council.propose(threshold=2, Democracy.external_propose_majority(Lookup{hash,len}))`
   → 2 ayes → `close` → sets `Democracy.NextExternal`
3. `Council.propose(threshold=2, Democracy.fast_track(hash, voting_period>=300, delay=0))`
   → 2 ayes → `close` → creates the referendum
4. `Democracy.vote(ref_index, Standard{aye, Locked1x, balance})` from Council members
5. referendum ends → dispatched as **Root** → `set_code` executes → new `specVersion`

### Pitfalls that cost real attempts

- **Read storage after a submit, never sample once.** A vote read immediately after submission
  shows a stale tally; the vote had in fact landed. Poll until the value changes.
- **Duplicate votes fail with a module error** (Collective rejects re-voting), so blind retries
  produce misleading `ExtrinsicFailed` events.
- `substrate-interface`'s `is_success` crashes on this runtime with
  `ValueError: Provided data is not in supported format: provided '<class 'list'>'` — it re-fetches
  and re-decodes the block. Submit with `wait_for_inclusion=False` and verify via storage/events.

## EVM activation traps (measured on testnet, spec 17 -> 18)

Both of these affect ANY chain that is UPGRADED into the EVM runtime rather than started with it.
A dev chain that begins on the EVM runtime shows neither, which is why they only surfaced on testnet.

### Trap 1: `GenesisConfig` never runs on a runtime upgrade

`EVMChainId::ChainId` read **0** after the upgrade, and `eth_chainId` answered `0x0` on a chain with a
fully working EVM. Genesis executes only at block 0, so a pallet introduced by `set_code` starts with
**empty storage** and any value that was supposed to come from genesis is silently absent.

Measured evidence:

- `EVMChainId::ChainId` raw storage = `None` -> reads as the type default `0`
- `pallet-evm-chain-id` exposes **no extrinsic** (metadata: `EVMChainId: []`)
- `BaseFee` was fine (10000 / 125000) because those come from `ValueQuery` defaults, not genesis

**Why it is a security bug, not cosmetic:** a live EVM answering `eth_chainId = 0` lets a transaction
signed for chain 0 be replayed on any other chain that also reports 0.

**Fix: an `OnRuntimeUpgrade` migration, not `System::set_storage`.** `set_storage` needs a second
governance cycle after the upgrade, leaving a window where the chain runs with chain id 0, and it
writes raw bytes to a raw key with no type checking. The migration is atomic with the upgrade and
visible in the diff an auditor reads:

```rust
pub const VERDIS_EVM_CHAIN_ID: u64 = 414;

pub struct SetEvmChainId;
impl frame_support::traits::OnRuntimeUpgrade for SetEvmChainId {
    fn on_runtime_upgrade() -> Weight { /* writes only when the value is 0 */ }
}

pub type Migrations = (SetEvmChainId,);
// Executive takes Migrations as its 6th generic argument
```

Idempotent on purpose: it writes only when the value is unset, so it is safe on a genesis chain, on a
chain already corrected by hand, and on repeat runs. Governance can later change the chain id without
a future upgrade reverting that decision.

Two tests cover it, and the pre-existing `chain_id_is_414` could not - that test BUILDS genesis, which
is the case that already worked:

- `migration_sets_chain_id_on_upgrade` - starts from EMPTY storage, i.e. the upgrade case
- `migration_is_idempotent` - a set value must survive

### Trap 2: `MappingSyncWorker` `sync_from` must be the activation height

Symptom: `eth_blockNumber` stayed `0` and

```
eth_getBalance(addr, "latest")  -> UnknownBlock("State already discarded for 0xf9fa412b…")
eth_getBalance(addr, "0x12a9")  -> 0x48beb9e8600 = 4999.0000 VRDX   ✅
eth_getBalance(addr, "pending") -> 0x48beb9e8600                    ✅
```

`0xf9fa412b` is the testnet **genesis** hash, so `latest` was resolving to block 0. Queries by
explicit block number returned the correct balance, which proves the EVM, the runtime API and
`HashedAddressMapping` were all working - only the Ethereum block index was stuck.

Cause: `MappingSyncWorker::new(...)` takes `sync_from` (vendored `fc-mapping-sync`,
`kv/worker.rs:92`). It was passed `0`, so the worker tried to index from genesis, whose state is
pruned on a long-running chain, and never advanced.

Fix: read the activation height from the environment so one binary serves all three networks.

```rust
std::env::var("VERDIS_EVM_SYNC_FROM").ok()
    .and_then(|v| v.parse::<u32>().ok())
    .unwrap_or(0)
    .into(),
```

Default `0` keeps dev and fresh chains behaving exactly as before. On testnet the unit sets
`Environment=VERDIS_EVM_SYNC_FROM=4360`, the block where spec 18 went live.

The `frontier` KV directory under `<base-path>/chains/<chain>/` must be cleared when changing this,
because it holds the partial index from the failed genesis-start attempts. It is a DERIVED index
rebuilt from chain data - no chain state, no keys.

### Mainnet order of operations

1. Build the runtime **with** `SetEvmChainId` in `Migrations`
2. Roll the new binary to all 21 validators, one at a time (42 vs 40 host functions - `set_code`
   before this makes every node fail to execute the block, permanently)
3. Note the activation block, then set `VERDIS_EVM_SYNC_FROM` to it on every node
4. `set_code` via Council 2/3 -> `fast_track` (>= 300 blocks) -> referendum
5. Verify `eth_chainId` = 414 **and** `eth_blockNumber` advancing **and** `eth_getBalance @latest`
6. Only after a clean Halborn report
