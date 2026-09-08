# Audit Scope — Verdis Chain

Prepared for the Halborn engagement. Every figure below was read from the live chain, not
estimated. Commands to reproduce each reading are given so the auditor can verify
independently rather than trusting this document.

## 1. What is live right now

| Property | Value | How to verify |
|---|---|---|
| Mainnet genesis | `0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e` | `chain_getBlockHash(0)` |
| Runtime spec | 17 | `state_getRuntimeVersion` |
| Pallets | 36 | `GET /api/v2/runtime` |
| Validators | 21 (GRANDPA threshold 15) | `Session.Validators` |
| Block time | 6 s | measured over the last 60 indexed blocks |
| Total issuance | 100,000,002,998.809011738 VRDX | `Balances.TotalIssuance` |
| Sudo | **absent** | not in `construct_runtime!` |
| ink! contracts | live on mainnet | `GET /api/v2/contracts` |
| EVM / Solidity | **not implemented** | `Evm`, `Ethereum` absent from metadata |

Identify a chain by its **genesis hash**, never by name. Mainnet is `0x2284393d…`, testnet is
`0xf9fa412b…`, and devnet's hash changes on every spec rebuild.

```bash
curl -s -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' \
  https://rpc.verdischain.com
```

## 2. Governance — there is no Sudo

`pallet-sudo` is absent from the mainnet runtime. All privileged operations run through
`Council` (3 members) and `Democracy`.

**A Council motion alone cannot upgrade the runtime.** `VerdisBaseCallFilter`
(`runtime/src/lib.rs:217`) blocks `System::set_code`, and `pallet-collective` dispatches an
approved motion with `RawOrigin::Members`, which the filter applies to. Only a system-Root
dispatch bypasses `BaseCallFilter` (see `construct_runtime` `filter_call`), and
`pallet-democracy` enacts approved referenda with Root.

The working upgrade path, exercised on mainnet on 2026-09-08:

```
Preimage.note_preimage(System.set_code(wasm))
Council motion (2/3) -> Democracy.external_propose_majority
Council motion (2/3) -> Democracy.fast_track
Democracy.vote
enactment dispatched as Root -> filter bypassed -> System.CodeUpdated
```

Recorded on chain:

```
block 58353  Democracy.Passed / Scheduler.Scheduled / Preimage.Requested
block 58354  System.CodeUpdated 0xf0fa100615acaf4b…  Scheduler.Dispatched Ok
             specVersion 16 -> 17
```

Timeline constants: `VotingPeriod` 600, `FastTrackVotingPeriod` 300, `EnactmentPeriod` 600
blocks. `InstantAllowed = false`, so instant enactment is unavailable by design.

**Areas we consider worth the auditor's attention:** the Council is 3 members with a 2/3
threshold — key custody is the dominant risk, not the code path. `VetoOrigin` is
`EnsureSigned<AccountId>`, i.e. any signed account can veto an external proposal; we believe
this is intentional but flag it explicitly.

## 3. Smart contracts (ink! / pallet-contracts)

Working on mainnet as of spec 17. Proof:

```
block 58442  Contracts.Instantiated  kiYEc1bsNd1fAM7gKEjXrquXqYfEui4u31jdmPz9d3eGT1mUq
block 58454  Contracts.Called + ContractEmitted
             total_supply 1,000,000  deployer 999,900  recipient 100
storage deposit 8.0972 VRDX for 5,251 bytes
```

Two runtime defects were found and fixed to get here; both are in scope for review:

1. **`MaxSupplyCurrency` had an empty `impl fungible::Mutate`.** `transfer` fell through to
   frame_support's default, which ends in `let _ = increase_balance(...)` — the result is
   discarded, so `frame_system::inc_providers` was never called. `pallet-contracts` transfers
   the existential deposit to the new contract account and then calls `inc_consumers`, which
   fails when `providers == 0` → every `instantiate` returned `NoProviders`. Fixed by
   delegating `transfer`/`mint_into`/`burn_from` and `MutateHold::{hold,release}` to
   `pallet_balances`. Transfers and holds do not change total issuance, so the supply cap is
   unaffected; `mint_into` keeps its `check_mint` guard.

2. **`WeightInfo = ()` on `pallet_contracts::Config`**, meaning every benchmarked weight was
   zero. Replaced with `pallet_contracts::weights::SubstrateWeight<Runtime>`.

`DepositPerByte`/`DepositPerItem` were repriced from `1 * UNITS` to `UNITS / 1_000`: at 1 VRDX
per byte a 20 KiB contract locked 20,480 VRDX, pricing third-party developers out.

## 4. Tests

```
cargo test --workspace   ->  37 binaries, 734 passed, 0 failed
toolchain: rustc 1.98.0 (pinned in rust-toolchain.toml)
```

Reproduce on a clean clone; `BUILD.md` lists the native dependencies, including `libclang`.

Note for the record: an earlier "734 tests" claim was true only in a working directory, not on
`master` — six test configs did not compile from a fresh clone (`error[E0046]`, missing
`AdminOrigin`/`Treasury`). Fixed in `0b9ccd24` and `b52afcf3`; the figure above is measured on
a clean clone of `master`.

## 5. Known gaps — stated rather than hidden

| Gap | Status |
|---|---|
| EVM / Solidity | Not implemented. Advertised on the site until 2026-09-08; the claims were removed and marked roadmap. Frontier integration is in progress on a branch and will enter audit scope before any mainnet deployment. |
| Load / TPS figures | `NOT_MEASURED` on mainnet. No published TPS claim. |
| Signed transactions on mainnet | 17 total, all produced by us during commissioning. The chain is pre-launch; zero user activity is expected, and no synthetic data has been added to make it look otherwise. |
| Web stack single point of failure | site, explorer API, indexer and the public RPC tunnel all run on 91.98.160.145. |
| `VetoOrigin = EnsureSigned` | any signed account can veto an external proposal. |

## 6. Retracted findings

Two items from our own earlier review were withdrawn after reading the code rather than
grepping it. They are listed so the auditor does not chase them:

* **`gulf-stream` unbounded `Vec`** — not a defect. `ForwardedTxs<T>` is bounded by
  `MaxForwardedHistory` with pruning.
* **`dpos` iterating storage inside an extrinsic** — not a defect. No dispatchable in
  `pallet-dpos` iterates storage; `Votes::<T>::iter()` lives in the internal `do_slash` used by
  the offence handler.

## 7. Data integrity of the explorer

The indexer wrote blocks at the chain tip before finalisation and never revisited them, so
3,812 rows held hashes of blocks that had been reorged out. Repaired, and the cause fixed: the
indexer now re-verifies every row below the finalised head on each pass and heals reorgs
(`healed 277 reorged block(s)` in the first pass). Current state:

```
chain-integrity breaks: 0        (row N parent_hash == row N-1 hash, for all N)
missing heights:        0
```

## 8. Reproducing our claims

`tools/audit-claims-check.py` verifies every public statement against the live chain and exits
non-zero on any discrepancy. It currently passes 11/11.

```bash
python3 tools/audit-claims-check.py
```
