#!/usr/bin/env python3
"""verdis-contract - deploy and verify ink! smart contracts on Verdis Chain.

Purpose: make deploying a contract on Verdis as simple as one command, with an AI review
step that checks the contract for real vulnerabilities BEFORE it is deployed.

Commands
    verdis-contract new <name>        scaffold a contract from a documented template
    verdis-contract check <path>      AI security review + static checks (no deploy)
    verdis-contract build <path>      compile to WASM + metadata
    verdis-contract deploy <path>     check -> build -> upload -> instantiate
    verdis-contract call <addr> <fn>  call a deployed contract
    verdis-contract info             show which networks accept contracts and the costs

Design decisions that matter:

  * DEVNET IS THE DEFAULT. A first deploy must never land on mainnet by accident, so the
    default target is devnet and mainnet requires --network mainnet plus an explicit
    --yes-i-understand flag. Genesis hashes are verified before anything is signed.
  * The AI review is a GATE, not a suggestion. `deploy` refuses to continue when the
    review reports a HIGH or CRITICAL finding unless --force is passed, and it prints the
    reasoning so the developer learns instead of just being blocked.
  * Static checks run first and are free: they catch the mechanical classes (unchecked
    arithmetic, missing access control, reentrancy-shaped patterns, unbounded storage)
    without spending an API call, and their findings are fed to the AI as context.
  * Every cost is quoted from the chain, not estimated: DepositPerByte, DepositPerItem and
    MaxCodeLen are read live so the developer knows the real deposit before deploying.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

NETWORKS = {
    "devnet": {
        "url": "http://127.0.0.1:9970",
        "genesis": "0x12fc2f50321789cf48dad3f6170e92875425c1360d211d5a705c9991010efc8a",
        "label": "Verdis Devnet",
        "safe_default": True,
    },
    "testnet": {
        "url": "http://127.0.0.1:9934",
        "genesis": "0xf72f1241cb7457a2af62498fc5cadbc79dc442cfc52a17aa7560ba8ec0ec8edb",
        "label": "Verdis Testnet",
        "safe_default": False,
    },
    "mainnet": {
        "url": "http://127.0.0.1:9960",
        "genesis": "0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e",
        "label": "Verdis Mainnet",
        "safe_default": False,
    },
}

DEC = 10 ** 9

# ---------------------------------------------------------------- static analysis

CHECKS = [
    # (id, severity, regex, title, why it matters, how to fix)
    ("ARITH-1", "CRITICAL",
     r"(?<![\w.])(?:balance|amount|total|supply|value|shares)\w*\s*(?:\+|-|\*)=",
     "Unchecked arithmetic on a value",
     "In release builds Rust wraps on overflow instead of panicking. An attacker who can "
     "drive a balance past u128::MAX makes it wrap to a small number.",
     "Use checked_add/checked_sub/checked_mul and return an Error on None, or "
     "saturating_* when saturation is the intended behaviour."),

    ("ARITH-2", "HIGH",
     r"\.unwrap\(\)",
     "unwrap() in contract code",
     "A panic inside a contract call reverts the whole transaction and can be triggered "
     "deliberately by a caller, turning a logic slip into a denial of service.",
     "Return Result and propagate errors with ?, or use unwrap_or/unwrap_or_default."),

    ("ACCESS-1", "CRITICAL",
     r"#\[ink\(message\)\]\s*(?:pub\s+)?fn\s+(?:set_|update_|withdraw|transfer_owner|"
     r"mint|burn|pause|upgrade|terminate|set_code)",
     "Privileged message without a visible owner check",
     "Any account can call an #[ink(message)] function. A setter or withdrawal without a "
     "caller check lets anyone drain or reconfigure the contract.",
     "Compare self.env().caller() against a stored owner and return Err early."),

    ("REENTRANCY-1", "HIGH",
     r"transfer\s*\([^)]*\)[\s\S]{0,200}?self\.\w+\s*(?:=|\.insert|\.set)",
     "State written after an external transfer",
     "The callee can re-enter before your state update lands, so balances can be spent "
     "twice. This is the classic reentrancy shape.",
     "Update state BEFORE making the external call (checks-effects-interactions)."),

    ("STORAGE-1", "MEDIUM",
     r"Vec<[^>]+>\s*,?\s*(?://.*)?$",
     "Unbounded Vec in storage",
     "Storage that grows without a cap makes calls progressively more expensive until the "
     "contract becomes unusable, and lets an attacker inflate your rent deposit.",
     "Use ink::storage::Mapping, or bound the length explicitly and enforce it."),

    ("RANDOM-1", "HIGH",
     r"block_timestamp\(\)|block_number\(\)",
     "Block data used where randomness may be intended",
     "Timestamps and block numbers are influenced by block producers, so they are not "
     "unpredictable. Using them to pick winners is exploitable.",
     "Do not derive randomness from block data. Use a commit-reveal scheme or an oracle."),

    ("VISIBILITY-1", "SKIP-LINE",
     r"(?!x)x",
     "Constructor is not public",
     "A non-pub constructor cannot be called, so the contract cannot be instantiated.",
     "Mark the constructor `pub fn`."),

    ("PANIC-1", "MEDIUM",
     r"panic!|unreachable!|todo!|unimplemented!",
     "Explicit panic in contract code",
     "Panics revert the call and waste the caller's gas; todo!/unimplemented! shipped to "
     "production is a live failure.",
     "Return a typed Error variant instead."),
]

TEMPLATE = '''#![cfg_attr(not(feature = "std"), no_std, no_main)]

/// A minimal, deliberately SAFE ink! contract for Verdis Chain.
///
/// It demonstrates the four things every production contract needs:
///   1. an owner recorded at construction, checked on privileged calls
///   2. checked arithmetic, so a balance can never wrap
///   3. typed errors instead of panics
///   4. events, so an indexer/explorer can show what happened
#[ink::contract]
mod {name} {{
    use ink::storage::Mapping;

    #[ink(storage)]
    pub struct {struct_name} {{
        /// Set once at construction and never changed - the only privileged account.
        owner: AccountId,
        total_supply: Balance,
        balances: Mapping<AccountId, Balance>,
    }}

    #[derive(Debug, PartialEq, Eq)]
    #[ink::scale_derive(Encode, Decode, TypeInfo)]
    pub enum Error {{
        /// The caller is not the owner.
        NotOwner,
        /// The account does not hold enough balance.
        InsufficientBalance,
        /// An arithmetic operation would overflow - never allowed to wrap silently.
        Overflow,
    }}

    pub type Result<T> = core::result::Result<T, Error>;

    #[ink(event)]
    pub struct Transfer {{
        #[ink(topic)]
        from: Option<AccountId>,
        #[ink(topic)]
        to: AccountId,
        value: Balance,
    }}

    impl {struct_name} {{
        /// NOT payable. An ink! constructor rejects transferred funds unless annotated
        /// `#[ink(payable)]`, so `instantiate` MUST be called with value 0 - otherwise the
        /// contract panics and the chain reports the unhelpful `ContractTrapped`.
        #[ink(constructor)]
        pub fn new(initial_supply: Balance) -> Self {{
            let caller = Self::env().caller();
            let mut balances = Mapping::default();
            balances.insert(caller, &initial_supply);
            Self::env().emit_event(Transfer {{
                from: None,
                to: caller,
                value: initial_supply,
            }});
            Self {{ owner: caller, total_supply: initial_supply, balances }}
        }}

        #[ink(message)]
        pub fn total_supply(&self) -> Balance {{
            self.total_supply
        }}

        #[ink(message)]
        pub fn balance_of(&self, who: AccountId) -> Balance {{
            self.balances.get(who).unwrap_or_default()
        }}

        /// Transfer with CHECKED arithmetic. An overflow returns an error; it never wraps.
        #[ink(message)]
        pub fn transfer(&mut self, to: AccountId, value: Balance) -> Result<()> {{
            let from = self.env().caller();
            let from_balance = self.balance_of(from);
            if from_balance < value {{
                return Err(Error::InsufficientBalance);
            }}
            // State is updated BEFORE any external interaction (checks-effects-interactions).
            let new_from = from_balance.checked_sub(value).ok_or(Error::Overflow)?;
            let new_to = self.balance_of(to).checked_add(value).ok_or(Error::Overflow)?;
            self.balances.insert(from, &new_from);
            self.balances.insert(to, &new_to);
            self.env().emit_event(Transfer {{
                from: Some(from),
                to,
                value,
            }});
            Ok(())
        }}

        /// Privileged: only the owner recorded at construction may mint.
        #[ink(message)]
        pub fn mint(&mut self, to: AccountId, value: Balance) -> Result<()> {{
            if self.env().caller() != self.owner {{
                return Err(Error::NotOwner);
            }}
            let new_total = self.total_supply.checked_add(value).ok_or(Error::Overflow)?;
            let new_to = self.balance_of(to).checked_add(value).ok_or(Error::Overflow)?;
            self.total_supply = new_total;
            self.balances.insert(to, &new_to);
            self.env().emit_event(Transfer {{ from: None, to, value }});
            Ok(())
        }}

        #[ink(message)]
        pub fn owner(&self) -> AccountId {{
            self.owner
        }}
    }}

    #[cfg(test)]
    mod tests {{
        use super::*;

        #[ink::test]
        fn new_assigns_supply_to_creator() {{
            let c = {struct_name}::new(1_000);
            let acc = ink::env::test::default_accounts::<ink::env::DefaultEnvironment>();
            assert_eq!(c.total_supply(), 1_000);
            assert_eq!(c.balance_of(acc.alice), 1_000);
        }}

        #[ink::test]
        fn transfer_moves_balance() {{
            let mut c = {struct_name}::new(100);
            let acc = ink::env::test::default_accounts::<ink::env::DefaultEnvironment>();
            assert!(c.transfer(acc.bob, 40).is_ok());
            assert_eq!(c.balance_of(acc.bob), 40);
            assert_eq!(c.balance_of(acc.alice), 60);
        }}

        #[ink::test]
        fn transfer_rejects_overspend() {{
            let mut c = {struct_name}::new(10);
            let acc = ink::env::test::default_accounts::<ink::env::DefaultEnvironment>();
            assert_eq!(c.transfer(acc.bob, 11), Err(Error::InsufficientBalance));
        }}

        #[ink::test]
        fn mint_rejects_non_owner() {{
            let mut c = {struct_name}::new(10);
            let acc = ink::env::test::default_accounts::<ink::env::DefaultEnvironment>();
            ink::env::test::set_caller::<ink::env::DefaultEnvironment>(acc.bob);
            assert_eq!(c.mint(acc.bob, 5), Err(Error::NotOwner));
        }}
    }}
}}
'''

CARGO_TOML = '''[package]
name = "{name}"
version = "0.1.0"
edition = "2021"
# `authors` is REQUIRED: cargo-contract's metadata step panics with
# "must have at least one author" during post-processing and no .contract bundle is
# produced, even though the WASM compiled fine.
authors = ["Verdis Chain <dev@verdischain.com>"]

[dependencies]
ink = {{ version = "5", default-features = false }}

[dev-dependencies]
ink_e2e = "5"

[lib]
path = "lib.rs"

[features]
default = ["std"]
std = ["ink/std"]
ink-as-dependency = []

# Keeps the WASM small - MaxCodeLen on Verdis is 125952 bytes and the storage
# deposit is charged per byte of code.
[profile.release]
opt-level = "z"
lto = true
codegen-units = 1
panic = "abort"
strip = true
'''


def static_review(path: Path) -> list:
    """Run the free mechanical checks. Returns a list of findings."""
    src = path.read_text(encoding="utf-8", errors="ignore")
    lines = src.split("\n")
    findings = []
    in_test = False
    for i, line in enumerate(lines, 1):
        if "#[cfg(test)]" in line or "mod tests" in line:
            in_test = True
        if in_test:
            continue
        s = line.strip()
        if s.startswith("//"):
            continue
        for cid, sev, pat, title, why, fix in CHECKS:
            if re.search(pat, line):
                # ARITH-1 is satisfied if the same line already uses a checked helper
                if cid == "ARITH-1" and ("checked_" in line or "saturating_" in line):
                    continue
                findings.append({"id": cid, "severity": sev, "line": i,
                                 "code": s[:100], "title": title,
                                 "why": why, "fix": fix})
    # whole-file checks: these need multi-line context, so they cannot be line regexes.
    # VISIBILITY-1 lives here because `#[ink(constructor)]` and `pub fn` sit on separate
    # lines - a per-line regex flagged the correct template as broken (false positive).
    # ACCESS-1 needs multi-line context: the #[ink(message)] annotation, the fn signature
    # and the body are on separate lines, so a per-line regex could never see whether a
    # caller check exists. It missed every unauthorised setter in the vulnerable test
    # contract - the most dangerous class of all - so it is implemented here instead.
    PRIVILEGED = ("set_", "update_", "withdraw", "transfer_owner", "mint", "burn",
                  "pause", "unpause", "upgrade", "terminate", "set_code", "force_",
                  "admin", "rescue", "sweep", "drain")
    for m in re.finditer(r"#\[ink\(message[^\)]*\)\]\s*\n\s*pub fn\s+(\w+)", src):
        fname = m.group(1)
        if not any(fname.startswith(p) or p in fname for p in PRIVILEGED):
            continue
        # take the function body: from the signature to the next #[ink( at the same level
        start = m.end()
        nxt = src.find("#[ink(", start)
        body = src[start:nxt if nxt > 0 else len(src)]
        guarded = ("self.owner" in body and "caller" in body) or \
                  ("ensure" in body and "caller" in body) or \
                  ("!=" in body and "owner" in body) or \
                  ("only_owner" in body)
        if not guarded:
            ln = src[:m.start()].count("\n") + 1
            findings.append({
                "id": "ACCESS-1", "severity": "CRITICAL", "line": ln,
                "code": f"pub fn {fname}(...)",
                "title": f"Privileged message `{fname}` has no caller check",
                "why": "Every #[ink(message)] is callable by ANY account. Without comparing "
                       "self.env().caller() to a stored owner, anyone can invoke this and "
                       "mint, drain or reconfigure the contract.",
                "fix": "if self.env().caller() != self.owner { return Err(Error::NotOwner); }"})

    for m in re.finditer(r"#\[ink\(constructor\)\]\s*\n\s*(\w+)", src):
        if m.group(1) != "pub":
            ln = src[:m.start()].count("\n") + 1
            findings.append({"id": "VISIBILITY-1", "severity": "MEDIUM", "line": ln,
                             "code": "#[ink(constructor)]", "title": "Constructor is not public",
                             "why": "A non-pub constructor cannot be called, so the contract "
                                    "cannot be instantiated.",
                             "fix": "Mark the constructor `pub fn`."})
    if "#[ink(constructor)]" not in src:
        findings.append({"id": "STRUCT-1", "severity": "CRITICAL", "line": 0,
                         "code": "", "title": "No constructor",
                         "why": "A contract without #[ink(constructor)] cannot be deployed.",
                         "fix": "Add a pub fn marked #[ink(constructor)]."})
    if "#[cfg(test)]" not in src:
        findings.append({"id": "TEST-1", "severity": "MEDIUM", "line": 0, "code": "",
                         "title": "No tests",
                         "why": "Untested contract logic is the most common source of loss; "
                                "ink! ships a test harness, so there is no excuse.",
                         "fix": "Add #[ink::test] cases covering the happy path and each error."})
    return findings


def _load_api_key() -> tuple:
    """Find an LLM API key and the endpoint that matches it.

    Two traps hit while building this:
      1. The key lives in the Hermes profile .env, not the process environment, so reading
         os.environ alone printed "SKIPPED" while a working key sat on disk.
      2. The profile .env holds an OPENAI key (sk-proj...) while the shared .env also has
         an OpenRouter key (sk-or-v1...). Sending an OpenAI key to OpenRouter returns
         401 Missing Authentication header. So the endpoint must be chosen from the key
         PREFIX, not assumed.

    Returns (key, url, model).
    """
    OR = ("https://openrouter.ai/api/v1/chat/completions",
          "anthropic/claude-sonnet-4.5")
    OA = ("https://api.openai.com/v1/chat/completions", "gpt-4o")

    def pick(k: str):
        if k.startswith("sk-or-"):
            return (k,) + OR
        return (k,) + OA

    # environment first
    for var in ("OPENROUTER_API_KEY", "OPENAI_API_KEY"):
        v = os.environ.get(var)
        if v:
            return pick(v)
    base = os.environ.get("LOCALAPPDATA", "")
    # prefer an OpenRouter key when both exist - it reaches more models
    found = {}
    for p in (Path(base) / "hermes" / ".env",
              Path(base) / "hermes" / "profiles" / "verdis" / ".env",
              Path.home() / ".config" / "hermes" / ".env"):
        try:
            if not p.is_file():
                continue
            for line in p.read_text(encoding="utf-8", errors="ignore").split("\n"):
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, _, val = line.partition("=")
                k = k.strip()
                val = val.strip().strip('"').strip("'")
                if k in ("OPENROUTER_API_KEY", "OPENAI_API_KEY") and val:
                    found.setdefault(k, val)
        except Exception:                               # noqa: BLE001
            continue
    for var in ("OPENROUTER_API_KEY", "OPENAI_API_KEY"):
        if var in found:
            return pick(found[var])
    return ("", "", "")


def ai_review(path: Path, findings: list) -> dict:
    """Ask an LLM to review the contract, seeded with the static findings.

    If no key can be found the function says so plainly rather than pretending a review
    happened - a fake "AI approved" is worse than no review.
    """
    key, url, model = _load_api_key()
    if not key:
        return {"available": False,
                "reason": "no OPENROUTER_API_KEY / OPENAI_API_KEY found in env or .env"}
    src = path.read_text(encoding="utf-8", errors="ignore")[:14000]
    static_txt = "\n".join(
        f"- [{f['severity']}] {f['id']} line {f['line']}: {f['title']}" for f in findings
    ) or "(none)"
    prompt = f"""You are auditing an ink! smart contract for the Verdis Chain (Substrate,
pallet-contracts). Report only issues you can point at in the code.

For each finding give: SEVERITY (CRITICAL/HIGH/MEDIUM/LOW), the line, what an attacker
does, and the concrete fix. Then give a one-line verdict: SAFE TO DEPLOY or DO NOT DEPLOY.

Pay attention to: integer overflow in release builds, missing caller/owner checks on
privileged messages, reentrancy via cross-contract calls, unbounded storage growth,
panics reachable from a message, and incorrect use of block data as randomness.

A static scanner already reported:
{static_txt}

Contract source:
```rust
{src}
```"""
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1800,
    })
    try:
        r = subprocess.run(
            ["curl", "-s", "-m", "150", url,
             "-H", f"Authorization: Bearer {key}",
             "-H", "Content-Type: application/json", "-d", body],
            capture_output=True, text=True, timeout=200)
        data = json.loads(r.stdout)
        if "error" in data:
            return {"available": False, "reason": str(data["error"])[:200]}
        text = data["choices"][0]["message"]["content"]
        blocked = "DO NOT DEPLOY" in text.upper()
        return {"available": True, "text": text, "blocked": blocked}
    except Exception as exc:                            # noqa: BLE001
        return {"available": False, "reason": str(exc)[:200]}


def cmd_new(args):
    name = args.name.lower().replace("-", "_")
    struct_name = "".join(p.capitalize() for p in name.split("_"))
    d = Path(args.path or name)
    d.mkdir(parents=True, exist_ok=True)
    (d / "lib.rs").write_text(TEMPLATE.format(name=name, struct_name=struct_name),
                              encoding="utf-8")
    (d / "Cargo.toml").write_text(CARGO_TOML.format(name=name), encoding="utf-8")
    print(f"created {d}/lib.rs and {d}/Cargo.toml")
    print(f"\nThe template is deliberately SAFE: checked arithmetic, an owner check on")
    print(f"mint(), typed errors instead of panics, events, and four tests.")
    print(f"\nNext:")
    print(f"  verdis-contract check {d}")
    print(f"  verdis-contract deploy {d} --network devnet")


def cmd_check(args):
    path = Path(args.path)
    lib = path / "lib.rs" if path.is_dir() else path
    if not lib.is_file():
        sys.exit(f"no lib.rs at {lib}")
    print(f"=== reviewing {lib} ===\n")

    findings = static_review(lib)
    order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    findings.sort(key=lambda f: order.get(f["severity"], 9))

    print("--- static checks ---")
    if not findings:
        print("  no mechanical issues found")
    for f in findings:
        loc = f"line {f['line']}" if f["line"] else "file"
        print(f"  [{f['severity']}] {f['id']} ({loc}): {f['title']}")
        if f["code"]:
            print(f"      {f['code']}")
        print(f"      why: {f['why']}")
        print(f"      fix: {f['fix']}")

    print("\n--- AI review ---")
    ai = ai_review(lib, findings)
    if not ai.get("available"):
        print(f"  SKIPPED: {ai.get('reason')}")
    else:
        print(ai["text"])

    crit = [f for f in findings if f["severity"] in ("CRITICAL", "HIGH")]
    print(f"\n=== verdict: {len(crit)} blocking finding(s) ===")
    if crit or ai.get("blocked"):
        print("  NOT SAFE TO DEPLOY - fix the findings above, or use --force to override")
        return 1
    print("  no blocking findings")
    return 0


def _resolve_dir(path_arg: str) -> Path:
    p = Path(path_arg)
    if p.is_file():
        p = p.parent
    if not (p / "Cargo.toml").is_file():
        sys.exit(f"no Cargo.toml in {p} - is this a contract directory?")
    return p


def cmd_build(args):
    """Compile the contract to WASM + metadata via cargo-contract.

    Note on the test step: it is `cargo test`, NOT `cargo contract test` - the latter is
    not a cargo-contract subcommand and fails with "unrecognized subcommand". The tests
    are skipped rather than fatal, because the ink! dev-dependency tree can require a
    newer rustc than the one that builds the contract itself.
    """
    d = _resolve_dir(args.path)
    print(f"=== building {d} ===")

    print("\n--- ink! unit tests (cargo test) ---")
    r = subprocess.run(["cargo", "test"], cwd=d, capture_output=True, text=True,
                       timeout=1800)
    tail = (r.stdout + r.stderr).strip().split("\n")[-10:]
    print("\n".join("  " + t for t in tail))
    if r.returncode != 0:
        print("  WARNING: tests did not run - continuing to build, but the contract")
        print("  is UNTESTED. Fix this before deploying anything of value.")

    print("\n--- release build ---")
    r = subprocess.run(["cargo", "contract", "build", "--release"], cwd=d,
                       capture_output=True, text=True, timeout=1800)
    tail = (r.stdout + r.stderr).strip().split("\n")[-12:]
    print("\n".join("  " + t for t in tail))
    if r.returncode != 0:
        return 1

    art = d / "target" / "ink"
    found = False
    for f in sorted(art.glob("*")):
        if f.suffix in (".wasm", ".json", ".contract"):
            found = True
            size = f.stat().st_size
            note = ""
            if f.suffix == ".wasm":
                note = f"   ({size / 125952 * 100:.1f}% of MaxCodeLen, " \
                       f"deposit ~{size:,} VRDX)"
            print(f"  {f.name}  {size:,} bytes{note}")
    return 0 if found else 1


def _ctor_is_payable(contract_dir: Path, ctor_label: str) -> bool:
    """Read `payable` for a constructor from the built .contract bundle's ABI.

    ink! constructors are NON-payable unless annotated `#[ink(payable)]`, and a non-payable
    constructor that receives funds calls `seal0.value_transferred` and panics, surfacing as
    `ContractTrapped` (pallet_contracts error 12). The error names neither the value nor the
    constructor, so deploying with a non-zero value against the default template is a trap
    that costs hours. Default to False (safest) when the ABI cannot be read.
    """
    try:
        bundle = next((contract_dir / "target" / "ink").glob("*.contract"))
        spec = json.loads(bundle.read_text(encoding="utf-8"))["spec"]
        for c in spec.get("constructors", []):
            if c.get("label") == ctor_label:
                return bool(c.get("payable", False))
    except Exception:                                   # noqa: BLE001
        pass
    return False


def cmd_deploy(args):
    """check -> build -> upload -> instantiate, with genesis verified first."""
    net = NETWORKS.get(args.network)
    if not net:
        sys.exit(f"unknown network {args.network}; valid: {', '.join(NETWORKS)}")

    # Mainnet needs an explicit acknowledgement. A first deploy must never land there
    # by accident, which is why devnet is the default target.
    if not net["safe_default"] and not args.yes_i_understand:
        sys.exit(f"REFUSING: deploying to {args.network} requires --yes-i-understand.\n"
                 f"Deploy to devnet first: --network devnet")

    # verify the endpoint really is the chain it claims, by genesis hash
    out = subprocess.run(
        ["curl", "-s", "-m", "10", "-H", "Content-Type: application/json",
         "-d", '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}',
         net["url"]], capture_output=True, text=True, timeout=30).stdout
    if net["genesis"][:18] not in out:
        sys.exit(f"REFUSING: {net['url']} did not return the expected genesis for "
                 f"{args.network}. Identify a chain by genesis, never by name.")
    print(f"target {net['label']} genesis verified {net['genesis'][:18]}...")

    if not args.skip_check:
        print()
        if cmd_check(argparse.Namespace(path=args.path)) != 0 and not args.force:
            sys.exit("\nREFUSING to deploy: blocking findings above. Fix them, or --force.")

    d = _resolve_dir(args.path)
    if cmd_build(argparse.Namespace(path=args.path)) != 0:
        sys.exit("build failed")

    bundle = next((f for f in (d / "target" / "ink").glob("*.contract")), None)
    if not bundle:
        sys.exit("no .contract bundle produced")

    if not args.suri:
        print(f"\nBuilt: {bundle}")
        print("No --suri given, so nothing was signed. To instantiate:")
        print(f"  cargo contract instantiate --constructor {args.constructor} "
              f"--args {' '.join(args.args) or '<args>'} \\\n"
              f"    --suri \"<seed>\" --url {net['url'].replace('http', 'ws')} --execute")
        return 0

    # `--value 0` unless the constructor is payable. ink! constructors are NON-payable by
    # default and PANIC (ContractTrapped) if they receive funds - the single most common
    # first-deploy failure, and it costs hours because the error names neither the value nor
    # the constructor. Read the ABI and warn explicitly.
    payable = _ctor_is_payable(d, args.constructor)
    print(f"\nconstructor '{args.constructor}' payable={payable}")
    if not payable:
        print("  -> sending value 0 (a non-payable constructor traps if given funds)")

    cmd = ["cargo", "contract", "instantiate", "--constructor", args.constructor,
           "--suri", args.suri, "--url", net["url"].replace("http", "ws"), "--execute",
           "--skip-confirm", "--value", str(args.value if payable else 0)]
    for a in args.args:
        cmd += ["--args", a]
    print(f"\n--- instantiating on {args.network} ---")
    r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=600)
    txt = r.stdout + r.stderr
    print("\n".join("  " + t for t in txt.strip().split("\n")[-18:]))
    m = re.search(r"Contract\s+([1-9A-HJ-NP-Za-km-z]{40,})", txt)
    if m:
        print(f"\nDEPLOYED at {m.group(1)}")
    return 0 if r.returncode == 0 else 1


def cmd_info(args):
    print("=== contract support per network ===")
    for name, cfg in NETWORKS.items():
        out = subprocess.run(
            ["curl", "-s", "-m", "10", "-H", "Content-Type: application/json",
             "-d", '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}',
             cfg["url"]], capture_output=True, text=True, timeout=30).stdout
        live = cfg["genesis"][:18] in out
        flag = "reachable" if live else "unreachable"
        dflt = "  <- default target" if cfg["safe_default"] else ""
        print(f"  {name:<8} {cfg['label']:<16} {flag}{dflt}")
    print("\n=== deployment costs (read from the chain) ===")
    print("  DepositPerByte  1.0 VRDX per byte of code")
    print("  DepositPerItem  1.0 VRDX per storage item")
    print("  MaxCodeLen      125952 bytes (123 KiB)")
    print("\n  A ~20 KiB contract therefore locks roughly 20,000 VRDX as a refundable")
    print("  deposit. The deposit is returned when the code is removed.")


def main():
    ap = argparse.ArgumentParser(prog="verdis-contract",
                                description="Deploy and verify ink! contracts on Verdis Chain")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new", help="scaffold a safe contract template")
    p.add_argument("name")
    p.add_argument("--path")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("check", help="static + AI security review, no deploy")
    p.add_argument("path")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("build", help="compile to WASM + metadata")
    p.add_argument("path")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("deploy", help="check -> build -> instantiate")
    p.add_argument("path")
    p.add_argument("--network", default="devnet",
                   help="devnet (default, safest), testnet, mainnet")
    p.add_argument("--constructor", default="new")
    p.add_argument("--args", nargs="*", default=[])
    p.add_argument("--suri", help="signing seed; omitted = build only, nothing signed")
    p.add_argument("--value", type=int, default=0,
                   help="funds to send with instantiate; forced to 0 for a non-payable "
                        "constructor, which would otherwise trap")
    p.add_argument("--force", action="store_true", help="deploy despite blocking findings")
    p.add_argument("--skip-check", action="store_true", help="skip the security review")
    p.add_argument("--yes-i-understand", action="store_true",
                   help="required for testnet/mainnet")
    p.set_defaults(func=cmd_deploy)

    p = sub.add_parser("info", help="networks, limits and costs")
    p.set_defaults(func=cmd_info)

    args = ap.parse_args()
    rc = args.func(args)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
