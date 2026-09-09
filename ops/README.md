# Verdis Chain — Operations

Operational tooling and audit records for the **Verdis Chain** Substrate mainnet, built during the infrastructure recovery of 2026-09-07.

Every script here reads live state and prints measured numbers. Nothing estimates.

## Chain facts

```
chain      Verdis Mainnet
genesis    0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e
runtime    verdis-chain specVersion 16
token      VRDX, 9 decimals, ss58Format 909
consensus  BABE (production) + GRANDPA (finality), pallet_dpos validator set
```

**21 GRANDPA authorities, finality threshold 15.** That ratio governs every procedure in this repo: with 21 running, six may fail before finality stops.

## Fleet

| Host | Role | Validators |
|---|---|---|
| 185.84.224.91 | HostKey DE | 5 + public RPC node |
| 195.154.80.40 | Online.net | 6 |
| 213.136.78.63 | Contabo | 6 |
| 5.223.77.19 | Hetzner SIN | 4 |

No single host holds more than 6, so losing any one machine leaves at least 15 and finality continues. That property is checked on every monitoring run.

## Monitoring

`mainnet_health.sh` — the one script to run when asking "is the chain fine?"

```
chain    best / finalized / lag / peers
         authorities and threshold read from the runtime
per host validator counts
         headroom, and whether any single host failure would halt finality
rpc      authority RPC must be unreachable from the internet
public   rpc.verdischain.com and /rpc must serve MAINNET, not testnet
keys     equivocation events
web      domains reachable
```

Exit code `0` OK, `1` WARN, `2` CRIT. Runs every 30 minutes via cron, silent unless something needs attention.

`install_watchdog.sh` deploys a 2-minute systemd timer per host that restarts any validator that is enabled but not running. Measured recovery: about 4–5 minutes of frozen finality, then automatic catch-up.

## What each group of scripts does

**Health and audit**
- `mainnet_health.sh` — live status, used by cron
- `audit_collect.sh` — full evidence dump: identity, consensus, measured finality rate, pallets, security posture, port scan, resources, logs, TLS
- `gap_analysis.sh` — what is still weak
- `count_mainnet_validators.sh` — authoritative validator count for one host

**Keys**
- `audit_keys.sh` — reconcile the on-chain authority set against keys present on disk; detect duplicates
- `backup_keystores.sh` — hash-verified keystore archives, pulled locally
- `check_ceremony_zip.py` — match a ceremony archive against the on-chain set

**Deployment**
- `deploy_6_validators.py` — bring new validators online one at a time, with duplicate checks and rollback
- `redistribute_validators.py`, `redistribute_final.py` — move validators between hosts so no host can halt finality
- `create_public_rpc.sh` — keyless full node for public RPC

**Hardening**
- `harden_195_firewall.sh` — restrict RPC ports to localhost, persist rules
- `remove_unsafe_flags.py` — strip `--unsafe-rpc-external` / `--rpc-methods=unsafe` per node, verifying finality between each
- `harden_ssh.sh` — disable password auth, enable fail2ban, cap journals, enable units at boot
- `add_bootnodes.sh` — multiple bootnodes instead of a single point of failure

**Public endpoints**
- `check_public_chain.sh` — which chain does the website actually talk to
- `switch_web_to_mainnet.sh`, `fix_rpc_location.sh`, `switch_ws_to_mainnet.sh` — repoint nginx and the WS filter at mainnet

## Audit reports

- `AUDIT_MAINNET_2026-09-07.md` — findings with the command output that proves each one
- `AUDIT_TESTNET_2026-09-07.md` — testnet, kept separate because it is a different chain
- `ANSWER_no_keys.md` — analysis of what happens if lost validator keys are never recovered

## Hard-won rules

These cost real downtime to learn. Read before editing a unit file.

**One node at a time.** Never restart two validators together. Confirm `is-active`, then read the finalized height, before touching the next.

**Quote `--name` or the node dies.** `ExecStart` contains `--name=Verdis Validator V18` — a value with spaces. Building a drop-in with `echo` drops the quotes, systemd re-splits the line, and the node crash-loops with `status=2/INVALIDARGUMENT`. Use Python and `shlex.quote`, then assert:

```python
parts = shlex.split(generated)
assert [p for p in parts if p.startswith("--name")] == ["--name=Verdis Validator V18"]
```

**`systemctl show -p ExecStart` returns several entries** once drop-ins exist. Take `tail -1`, not `head -1`.

**Drop-in order is lexical.** `10-x.conf` loses to `90-y.conf`. Check the effective `ExecStart` after `daemon-reload`.

**`mainnet-raw.json` is not the same file on every host.** One host carried a spec producing a different genesis; a node built from it silently joined a private fork with 1 peer. Verify the spec by sha256 (`aca92919e13da10f`) and the running node by `chain_getBlockHash(0)`.

**Count validators by evidence, not by name.** Unit names drift (`verdis-validator`, `verdis-validator-v18`, `verdis-v16b`, `verdis-v13m`). Glob lists undercount after a rename; counting `--validator` alone overcounts because one host also runs a testnet validator; and a unit without `--rpc-port` is invisible unless the default port is probed. Require `--validator` **and** the mainnet genesis.

**Verify a "blocked" RPC method with valid params.** Bad params return `-32602 Invalid params`, which says nothing about safety. A blocked method returns `-32601 RPC call is unsafe to be called externally`.

**`sshd` honours the first occurrence of a directive.** `50-cloud-init.conf` sets `PasswordAuthentication yes`, so a `99-` file never applies. Name it `00-`.

**Provider panels apply SSH keys only at OS install.** Adding a key to a Hetzner, Online.net or Contabo panel does nothing to a running server. Use rescue mode: it netboots a RAM image and leaves disks intact. `INSTALL` formats the disk — never press it.

**Append, never overwrite, `authorized_keys`.** Use `>>`. A single `>` removes the key you are logged in with.

## Secrets

`secrets/` is gitignored and never committed: credentials, keystore backups, and the ceremony archive live there, encrypted and permission-restricted. Scripts read them from disk at runtime.
