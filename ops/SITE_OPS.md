# Site and explorer operations

Tooling from the 2026-09-07 site audit. Every script measures live state and prints the
command output that proves its result.

## What was broken

The explorer showed `Loading...` on every metric and `BLOCK HEIGHT -`. Three independent
faults:

1. `verdis-api.service` read `127.0.0.1:9934`, which is the **testnet** (block 185k,
   finality gap 73 000) instead of mainnet on `:9960`.
2. nginx never routed `/api/v1` to the backend, so every frontend fetch matched the
   static root and returned `index.html` as **HTTP 200 with content-type text/html**.
   A status-code-only check reports that as healthy - assert the content type.
3. The shared `/assets/` logo path 404'd on 8 subdomains because each vhost has its own
   root.

## Scripts

| Script | Purpose |
|---|---|
| `switch_api_to_mainnet.py` | point the live API at mainnet, verified by genesis hash, with rollback |
| `wire_explorer_api.py` | nginx routes for `/api/v1` and `/rpc`, with a 3s micro-cache |
| `fix_assets_all_vhosts.py` | shared-asset alias on every subdomain |
| `add_network_selector.py` | mainnet/testnet/devnet registry and per-network endpoints |
| `create_devnet.py` | isolated `--dev --tmp` devnet node |
| `add_network_switcher_ui.py` | header network switcher, ~60 lines vanilla JS, no build step |
| `verify_pallets.py` | which pallets exist, proven via storage prefixes |
| `revert_banner.py` | restores the intentional TESTNET disclaimer |
| `mainnet_health.sh` | full health check: chain, hosts, headroom, API content type, genesis of every network |

## Rules worth keeping

**Identify a chain by genesis hash, never by name.** A spec file can carry the right
name and the wrong genesis; that put two validators on a private fork and the public
site on the testnet.

**`location ^~ /assets/` - the `^~` is mandatory.** nginx evaluates regex locations
before prefix locations, so a plain `location /assets/` loses to
`location ~* \.(js|css|png|...)$` and the alias silently never applies.

**Find the live backend from the process, not the filename.** `discan_api.py` looks like
the explorer API and is dead code; the real one is `verdis-api.service` serving
`verdiscan_api.py`. Use `ss -tlnp` then `systemctl status <pid>`.

**Verify a binary asset by hash, not status code.** MSYS `curl -w '%{size_download}'`
reports 0 for binary bodies, and a browser DOM caches an earlier 404. Pipe to `wc -c`
and compare `sha256sum` with the file on disk.

**The network selector fails closed.** Client input is only ever a key into an
allow-list, every endpoint's genesis is pinned and checked, an unknown network is a 400
and a configured-but-absent one is a 503. No silent fallback - a silent fallback is how
testnet data ended up under mainnet branding.

**The TESTNET banner is deliberate.** Verdis has not publicly launched and has not
passed the external audit. Mainnet running does not make that disclaimer stale.
