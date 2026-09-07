# tools/

Developer and operator helpers. Nothing here runs continuously; each script is invoked
by hand or from a documented procedure.

| File | Purpose |
|---|---|
| `epoch-monitor.js` | watch epoch/session transitions |
| `faucet.js`, `faucet.py` | faucet clients (the live service is `services/faucet_py.py`) |
| `soak-test-monitor.sh` | soak-test observation, see `docs/SOAK_TEST_LOG.md` |
| `load-test.js`, `load-test-v2.js` | throughput tests, results in `docs/testnet-report.md` |
| `seed_dex.js` | seed DEX liquidity pools |
| `fund-accounts.js` | fund test accounts |
| `upgrade_runtime.js` | submit a runtime upgrade |
| `ws_proxy.js` | minimal WebSocket proxy for local debugging |
| `verdis_audit.py` | ad-hoc chain audit queries |
| `tx_relay.py` | earlier relay generation, kept for reference |

For live mainnet operations use `ops/` instead — those scripts read real state and
print measured numbers.
