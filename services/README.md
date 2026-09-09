# services/

Long-running production services. These files are the **source** of what runs on the
web host at `/opt/verdis-chain-rust/`.

The repository does not deploy them. Editing a file here changes nothing in production
until it is copied to the server and the unit is restarted.

| File | systemd unit | What breaks if it stops |
|---|---|---|
| `ws_filter_proxy.py` | `verdis-ws-filter` | wallet and explorer live subscriptions (`wss://.../ws`) |
| `rpc_filter_proxy.py` | `verdis-rpc-filter` | method filtering in front of the public JSON-RPC |
| `tx_relay_v3.py` | `verdis-relay` | transaction relay |
| `faucet_py.py` | `verdis-faucet` | faucet API |
| `governance_api.py` | `verdis-governance` | governance endpoints |
| `validator-monitor.py` | `verdis-validator-monitor` | validator status feed |
| `health-monitor.sh` | `verdis-health-monitor` | health checks |
| `backup.sh` | `verdis-backup.timer` | scheduled backups |
| `txbot.py`, `transfer_bot.js` | `verdis-txbot` | synthetic transaction load |
| `discan_api.py` | deployed by `scripts/deploy-verdiscan-api.sh` | explorer API |
| `balance_api.py` | — | balance lookups |
| `wallet_pin_store.json` | read by `tx_relay_v3.py` | runtime state, not a config |

Before deleting anything here, check whether a unit references it:

```bash
systemctl list-units 'verdis*' --all --no-legend --no-pager | awk '{print $1}' \
  | while read u; do systemctl show -p ExecStart --value "$u"; done | grep -o '[^ ]*\.py'
```
