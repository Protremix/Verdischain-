# Deploying Smart Contracts on Verdis Chain

Verdis runs **ink! contracts** through `pallet-contracts` (WASM), the same technology
Astar and Aleph Zero use. This is verified on all three networks:

```
network   Contracts pallet   upload_code   instantiate_with_code   call
mainnet   present            index 3       index 7                 index 6
testnet   present            index 3       index 7                 index 6
devnet    present            index 3       index 7                 index 6
```

If you have written Solidity before: ink! is Rust, not Solidity. The concepts map
directly (storage, messages instead of functions, events, constructors), but the
language and tooling are Rust's.

---

## 1. What you need

Install once. `cargo-contract` is the official ink! build tool.

```bash
# Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add wasm32-unknown-unknown
rustup component add rust-src

# ink! build tool (verified working version)
cargo install --locked cargo-contract --version ^5
cargo contract --version     # cargo-contract-contract 5.0.3
```

On Ubuntu you also need the native build dependencies, or the build fails on
`libclang.so`:

```bash
apt-get install -y clang libclang-dev protobuf-compiler pkg-config libssl-dev
```

---

## 2. Create a contract

```bash
verdis-contract new my_token
```

This writes `my_token/lib.rs` and `my_token/Cargo.toml`. The template is deliberately
**safe by construction** and shows the four things every production contract needs:

1. **An owner recorded at construction** and checked on privileged calls.
2. **Checked arithmetic** — `checked_add` / `checked_sub`, so a balance can never wrap.
3. **Typed errors instead of panics** — a panic reverts the whole call and wastes the
   caller's gas.
4. **Events**, so the explorer and indexer can show what happened.

It also ships four `#[ink::test]` cases, including one proving `mint()` rejects a
non-owner.

---

## 3. Check it BEFORE you deploy

```bash
verdis-contract check my_token
```

Two layers run:

**Static checks** (free, instant) catch the mechanical vulnerability classes:

| ID | Severity | What it catches |
|---|---|---|
| ARITH-1 | CRITICAL | Raw `+=` / `-=` on a balance — wraps silently in release builds |
| ACCESS-1 | CRITICAL | Privileged message (`mint`, `withdraw`, `set_*`) with no caller check |
| REENTRANCY-1 | HIGH | State written *after* an external transfer |
| ARITH-2 | HIGH | `unwrap()` reachable from a message — caller-triggerable DoS |
| RANDOM-1 | HIGH | Block timestamp/number used as randomness — producers can influence it |
| STORAGE-1 | MEDIUM | Unbounded `Vec` in storage — grows until the contract is unusable |
| PANIC-1 | MEDIUM | Explicit `panic!` / `todo!` / `unimplemented!` |
| TEST-1 | MEDIUM | No tests at all |

**AI review** then audits the source with the static findings as context, and explains
each issue as *what an attacker actually does* plus the concrete fix.

The check is a **gate**: `deploy` refuses to continue on a CRITICAL or HIGH finding
unless you pass `--force`.

### Proof it works

Run against a deliberately vulnerable contract
(`test-contracts/vulnerable/lib.rs`), the static layer reports **11 findings**:

```
[CRITICAL] ARITH-1  (line 37): Unchecked arithmetic on a value
[CRITICAL] ACCESS-1 (line 44): Privileged message `withdraw_all` has no caller check
[CRITICAL] ACCESS-1 (line 53): Privileged message `force_take` has no caller check
[CRITICAL] ACCESS-1 (line 63): Privileged message `set_owner` has no caller check
[CRITICAL] ACCESS-1 (line 77): Privileged message `mint` has no caller check
[HIGH]     ARITH-2  (line 48): unwrap() in contract code
[HIGH]     ARITH-2  (line 55): unwrap() in contract code
[HIGH]     RANDOM-1 (line 71): Block data used where randomness may be intended
[MEDIUM]   STORAGE-1 (line 17): Unbounded Vec in storage
[MEDIUM]   PANIC-1  (line 57): Explicit panic in contract code
[MEDIUM]   TEST-1   (file):    No tests
=== verdict: 8 blocking finding(s) ===
  NOT SAFE TO DEPLOY
```

The AI layer independently found the same issues and described the attacks, e.g. for
the overflow: *"Attacker deposits `u128::MAX - current_balance + 1` to wrap balance to
zero, then repeats to drain contract value while maintaining zero recorded balance."*

Run against the generated template: **0 blocking findings, no false positives.**

---

## 4. Build

```bash
cd my_token
cargo contract test           # run the ink! unit tests first
cargo contract build --release
```

Produces in `target/ink/`:

- `my_token.wasm` — the code that goes on chain
- `my_token.json` — the ABI (metadata) the explorer and frontends need
- `my_token.contract` — both bundled together, this is what you deploy

---

## 5. Deploy

**Always deploy to devnet first.** `verdis-contract` defaults to devnet for exactly this
reason; mainnet requires `--network mainnet --yes-i-understand`.

```bash
verdis-contract deploy my_token --network devnet
```

The tool verifies the target's **genesis hash** before signing anything, so a devnet
deploy can never accidentally land on mainnet:

```
mainnet  0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e
testnet  0xf72f1241cb7457a2af62498fc5cadbc79dc442cfc52a17aa7560ba8ec0ec8edb
devnet   0x12fc2f50321789cf48dad3f6170e92875425c1360d211d5a705c9991010efc8a
```

Manually with `cargo contract` the same deploy is:

```bash
cargo contract instantiate \
  --constructor new --args 1000000 \
  --suri "<your seed>" \
  --url ws://127.0.0.1:9970 \
  --execute
```

---

## 6. What it costs

Read live from the chain, not estimated:

```
DepositPerByte                1.0 VRDX per byte of code
DepositPerItem                1.0 VRDX per storage item
MaxCodeLen                    125952 bytes (123 KiB)
CodeHashLockupDepositPercent  30%
```

A ~20 KiB contract therefore locks roughly **20,000 VRDX** as a storage deposit. This
is a **deposit, not a fee** — it is returned when the code is removed with
`remove_code`. Contracts larger than 123 KiB are rejected outright, so keep the WASM
small (`--release` and `opt-level = "z"`).

---

## 7. Calling a deployed contract

```bash
# read-only (free, no transaction)
cargo contract call --contract <addr> --message balance_of \
  --args <account> --url ws://127.0.0.1:9970 --suri "<seed>" --dry-run

# state-changing (signs and submits)
cargo contract call --contract <addr> --message transfer \
  --args <account> 100 --url ws://127.0.0.1:9970 --suri "<seed>" --execute
```

---

## 8. The rules that actually prevent losses

These are the failure modes that cost real money on other chains:

- **Never use raw `+=` on balances.** Rust wraps on overflow in release builds; it does
  not panic. Use `checked_*` and return an error.
- **Every `#[ink(message)]` is callable by anyone.** There is no `private`. If a
  function should be owner-only, compare `self.env().caller()` yourself.
- **Update state before external calls.** The callee can re-enter before your write
  lands (checks-effects-interactions).
- **Block data is not random.** Producers influence timestamps and block numbers.
- **Bound your storage.** Use `Mapping`, not a `Vec` that anyone can append to.
- **Test on devnet, then testnet, then mainnet.** In that order, every time.

---

## Command reference

```
verdis-contract new <name>          scaffold a safe template
verdis-contract check <path>        static + AI security review (no deploy)
verdis-contract build <path>        compile to WASM + metadata
verdis-contract deploy <path>       check -> build -> upload -> instantiate
verdis-contract call <addr> <fn>    call a deployed contract
verdis-contract info                networks, limits and live costs
```
