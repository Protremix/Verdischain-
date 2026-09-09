# Verdis Blockchain Monitoring Stack

Complete production-grade monitoring, alerting, and observability stack for the **Verdis Blockchain** (Rust + Substrate, BABE + GRANDPA consensus).

---

## 🚀 Quick Overview

- **Server IP:** `91.98.160.145`
- **Domain:** `verdischain.com` (Grafana proxy: `grafana.verdischain.com`)
- **Node Binary:** `/opt/verdis-chain-rust/target/release/verdis`
- **Systemd Service:** `verdis-node.service`
- **Token:** VRS (100 Billion total supply)
- **Consensus Parameters:** 6s block time, 600 blocks per epoch (~1 hour), 600 blocks per session

---

## 📐 Architecture & Ports

| Component | Container Name | Port | Description |
| :--- | :--- | :--- | :--- |
| **Prometheus** | `verdis-prometheus` | `9090` | Metrics scraper, time-series DB & alert engine |
| **Grafana** | `verdis-grafana` | `3000` | Visual dashboards (dark theme #18181a) |
| **Alertmanager** | `verdis-alertmanager` | `9093` | Alert routing, grouping, Slack/Email/Webhook notifications |
| **Node Exporter** | `verdis-node-exporter` | `9100` | Host hardware & OS metrics (CPU, RAM, Disk, Net) |
| **Substrate Node** | Systemd host service | `9615` | Substrate Prometheus metrics exporter endpoint |

---

## 📁 Directory Structure

```text
monitoring/
├── docker-compose.yml
├── install.sh
├── README.md
├── alertmanager/
│   └── alertmanager.yml
├── prometheus/
│   ├── prometheus.yml
│   └── alert-rules.yml
└── grafana/
    ├── dashboards/
    │   ├── verdis-overview.json
    │   ├── verdis-validator.json
    │   └── verdis-consensus.json
    └── provisioning/
        ├── dashboards/
        │   └── dashboard.yml
        └── datasources/
            └── datasource.yml
```

---

## 🛠️ Prerequisites & Node Configuration

Ensure your Verdis Substrate node service (`verdis-node.service`) is running with the Prometheus exporter enabled on port `9615`.

Sample systemd unit file snippet (`/etc/systemd/system/verdis-node.service`):
```ini
[Unit]
Description=Verdis Blockchain Validator Node
After=network.target

[Service]
Type=simple
User=verdis
ExecStart=/opt/verdis-chain-rust/target/release/verdis \
  --validator \
  --chain=mainnet \
  --port 30333 \
  --rpc-port 9944 \
  --prometheus-external \
  --prometheus-port 9615 \
  --name "Verdis-Validator-01"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## ⚡ Installation & Quick Start

To deploy or update the stack on server `91.98.160.145`:

```bash
cd /opt/verdis-monitoring # or the directory containing monitoring/
sudo ./install.sh
```

### What `install.sh` handles automatically:
1. Installs Docker & Docker Compose if missing.
2. Copies stack files to `/opt/verdis-monitoring/`.
3. Opens firewall ports (`9090`, `3000`, `9093`) via UFW.
4. Generates `.env` with default or custom Grafana admin credentials (`VerdisSecurePass2026!`).
5. Launches containers (`docker compose up -d`).
6. Performs health checks on all endpoints.
7. Configures Nginx reverse proxy for `grafana.verdischain.com`.

---

## 📊 Grafana Dashboards

The stack auto-provisions three pre-configured Grafana dashboards in dark theme (`#18181a`):

1. **Verdis Overview (`verdis-overview.json`)**
   - Best & Finalized block heights
   - Block production rate (1m rate)
   - GRANDPA finality lag
   - Peer count & Epoch transition count
   - RPC request duration & latency
   - Host CPU, RAM, Disk, and Network I/O throughput

2. **Verdis Validator (`verdis-validator.json`)**
   - Active validator count
   - Validator session keys status
   - Validator uptime (24h)
   - BABE block authorship count per validator
   - GRANDPA precommit & prevote rates
   - Im-online heartbeats & Authority discovery known peers

3. **Verdis Consensus (`verdis-consensus.json`)**
   - BABE epoch progress bar (600 blocks per epoch)
   - Estimated time until next epoch
   - Current GRANDPA round number
   - Consensus warnings & equivocation counter
   - Finality lag gauge & distribution
   - Block import vs. export rates
   - Active chain forks & reorg count

---

## 🔔 Alert Rules (`alert-rules.yml`)

Prometheus evaluates rules every 10 seconds. Alerts trigger for:

- **Block Production Stalled:** No new best block produced in 60s.
- **GRANDPA Finality Lagging:** Lag exceeds 10 blocks.
- **Epoch Transition Failure:** No epoch transition recorded in 75m.
- **Node Down:** Substrate node endpoint `up == 0` for 1m.
- **Validator Peer Count Zero:** 0 connected peers on validator node for 1m.
- **High RPC Latency:** Average RPC response duration > 100ms over 5m.
- **BABE Slot Frequency Deviation:** Block rate deviates significantly from 6s slot target.
- **High CPU Usage:** CPU usage > 80% for 5m.
- **High Memory Usage:** RAM usage > 85% for 5m.
- **Low Disk Space:** Available disk space on `/` < 10%.

---

## 📬 Alertmanager Integration (`alertmanager.yml`)

Configure your webhook URLs, Slack API tokens, or SMTP credentials in `alertmanager/alertmanager.yml`:

```yaml
receivers:
  - name: 'critical-alerts-group'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK_URL'
        channel: '#verdis-node-alerts-critical'
    email_configs:
      - to: 'devops@verdischain.com'
```

Apply changes by reloading Prometheus/Alertmanager:
```bash
docker exec -it verdis-prometheus kill -SIGHUP 1
docker exec -it verdis-alertmanager kill -SIGHUP 1
```

---

## 🔒 Security & Domain Proxy (`grafana.verdischain.com`)

To issue an SSL certificate for Grafana via Certbot:
```bash
sudo certbot --nginx -d grafana.verdischain.com
```

---

## 🔍 Useful Maintenance Commands

```bash
# View stack status
docker compose ps

# View container logs
docker compose logs -f prometheus
docker compose logs -f grafana
docker compose logs -f alertmanager

# Restart monitoring services
docker compose restart

# Test Substrate metrics endpoint manually
curl -s http://localhost:9615/metrics | grep substrate_
```
