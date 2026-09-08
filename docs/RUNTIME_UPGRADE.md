# Runtime Upgrades on Verdis Chain

Mainnet has no `pallet-sudo`. This document records the upgrade path that **actually works**,
established by upgrading mainnet from spec 16 to spec 17 on 2026-09-08, plus the two mistakes
that path avoids.

## The trap: a Council motion cannot call `System::set_code`

The obvious route — a Council motion wrapping `System.set_code` — reaches `Executed` and then
fails inside with `frame_system::Error::CallFiltered` (variant 5).

Cause, in `runtime/src/lib.rs:217`:

```rust
impl Contains<RuntimeCall> for VerdisBaseCallFilter {
    fn contains(call: &RuntimeCall) -> bool {
        match call {
            RuntimeCall::System(frame_system::Call::set_code { .. }) => false,
            ...
```

`pallet-collective` dispatches an approved motion with `RawOrigin::Members(yes, count)`, and
`BaseCallFilter` applies to it. Root is the only origin that bypasses the filter —
`construct_runtime!` generates:

```rust
// Root bypasses all filters
OriginCaller::system(frame_system::RawOrigin::Root) => true,
```

`pallet-democracy` enacts an approved referendum via the scheduler with Root, so routing the
same call through Democracy bypasses the filter legitimately, with no runtime change needed.

## The working path

```
1. Preimage.note_preimage(System.set_code(<runtime wasm>))
2. Council motion (threshold 2/3) -> Democracy.external_propose_majority(hash)
3. Council motion (threshold 2/3) -> Democracy.fast_track(hash, voting_period, delay)
4. Democracy.vote(ref_index, aye)
5. Wait: Democracy.Passed -> Scheduler.Scheduled -> Scheduler.Dispatched (as Root)
   -> System.CodeUpdated
```

Mainnet record for spec 16 → 17:

```
preimage  0x8d5fab5d301d23d559bafc18cdee98c325b7c421d4a11b249077863c2e150b1f  (1,249,146 bytes)
block 58353  Democracy.Passed{ref_index:0}, Scheduler.Scheduled{when:58354}, Preimage.Requested
block 58354  System.CodeUpdated 0xf0fa100615acaf4b5dd19333185d9e8ab49f036714681c004015dfcd6ed1c4ea
             Scheduler.Dispatched{result: Ok}
```

Scripts: `tools/mainnet-upgrade-step1.py` … `step4.py`, `tools/watch-mainnet-upgrade.py`.

## Mandatory pre-flight: host function compatibility

After `set_code` the **new WASM runs inside the old node binaries**. If the new runtime imports
a host function the running binary does not provide, every validator fails to execute blocks
and the chain stops. There is no recovery by governance at that point — the runtime that would
fix it cannot execute either.

So before any `set_code`, compare the imported host functions of the old and new runtime:

```bash
tools/compare-runtime-imports.sh   # old vs new; must report 0 new imports
```

For spec 16 → 17 the result was 40 vs 40, 0 new, 0 removed — hence no binary rollout was
needed.

Two ways this check gives a **false** answer, both encountered:

* **Do not scan the node binary with `strings`.** Host functions are registered in wasmtime
  linker tables, not stored as literals. The binary reports 0 imports and the check appears to
  fail.
* **Decompress the runtime blob first.** Substrate runtimes are zstd-compressed with the magic
  prefix `52bc537646db8e05` (`sp_maybe_compressed_blob::ZSTD_PREFIX`). Scanning the compressed
  blob yields garbage such as `ext_key30ext_...`.

## Rehearse on devnet, not on mainnet

`tools/prove-root-bypass.py` runs the whole path on devnet and asserts the outcome by writing a
probe key that `BaseCallFilter` forbids (`System.set_storage`):

```
external_propose_majority Ok -> fast_track Ok -> Democracy.Started -> 3000 ayes
block 783  Democracy.Passed + Scheduler.Scheduled{when:784}
block 784  Scheduler.Dispatched{result: Ok}
probe key 0xdeadbeef present  -> a filtered call executed as Root
```

## Signing

Council seeds never leave the operator's machine. Because mainnet's public WS endpoint is not
proxied and port 9944 is a validator with a Host filter (HTTP 403), sign over an SSH tunnel to
the keyless full node:

```bash
ssh -L 19955:127.0.0.1:9955 root@185.84.224.91
# then use ws://127.0.0.1:19955
```

`substrate-interface` requires **websockets** for `wait_for_inclusion`; over HTTP it raises
`Result handlers only available for websockets` and submits nothing.

## Timeline constants

| Constant | Blocks | At 6 s |
|---|---|---|
| `LaunchPeriod` | 600 | 60 min |
| `VotingPeriod` | 600 | 60 min |
| `FastTrackVotingPeriod` | 300 | 30 min |
| `EnactmentPeriod` | 600 | 60 min |
| `InstantAllowed` | `false` | — |
