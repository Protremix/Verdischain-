# Verdis Chain Monitoring & Alerting Guide

This guide provides technical specifications and instructions for deploying, configuring, interpreting, and maintaining full-stack monitoring for **Verdis Chain** validator nodes and infrastructure using Prometheus, Grafana, and Alertmanager.

---

## 1. Architecture Overview

Verdis Chain infrastructure monitoring utilizes standard Prometheus metric exposure and scraping:

```
┌────────────────────────────────────────────────────────┐
│                  Verdis Chain Host                     │
│  ┌────────────────────┐      ┌──────────────────────┐  │
│  │ Node (Port 9615)   │      │ Node Exporter (9100) │  │
│  │ Substrate Metrics  │      │ System CPU/RAM/Disk  │  │
│  └─────────┬──────────┘      └──────────┬───────────┘  │
└────────────┼────────────────────────────┼──────────────┘
             │                            │
             ▼                            ▼
  ┌──────────────────────────────────────────────────┐
  │         Prometheus Server (Port 9090)            │
  │     Scrapes metrics every 5s / Retains 30d      │
  └──────────┬────────────────────────────┬──────────┘
             │                            │
             ▼                            ▼
  ┌──────────────────────┐    ┌──────────────────────┐
  │ Grafana (Port 3000)  │    │ Alertmanager (9093) │
  │ Interactive Dashboards│    │ Slack / Mail / Pager │
  └──────────────────────┘    └──────────────────────┘
```

---

## 2. Infrastructure Installation via Docker Compose

Deploy Prometheus, Grafana, Alertmanager, and Node Exporter using Docker Compose on host `91.98.160.145`:

Create `/opt/verdis-monitoring/docker-compose.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.48.0
    container_name: verdis-prometheus
    restart: always
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./prometheus/alerts.yml:/etc/prometheus/alerts.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'

  grafana:
    image: grafana/grafana:10.2.0
    container_name: verdis-grafana
    restart: always
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=SuperSecureVerdisPassword123!
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro

  alertmanager:
    image: prom/alertmanager:v0.26.0
    container_name: verdis-alertmanager
    restart: always
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro

  node-exporter:
    image: prom/node-exporter:v1.7.0
    container_name: verdis-node-exporter
    restart: always
    ports:
      - "9100:9100"

volumes:
  prometheus_data:
  grafana_data:
```

Start the monitoring stack:

```bash
mkdir -p /opt/verdis-monitoring/prometheus /opt/verdis-monitoring/alertmanager /opt/verdis-monitoring/grafana/dashboards
cd /opt/verdis-monitoring
docker compose up -d
```

---

## 3. Prometheus Configuration

Configure `/opt/verdis-monitoring/prometheus/prometheus.yml` to scrape the Verdis Substrate node (`9615`) and host Node Exporter (`9100`):

```yaml
global:
  scrape_interval: 5s
  evaluation_interval: 5s

rule_files:
  - "alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

scrape_configs:
  - job_name: 'verdis-node'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['host.docker.internal:9615']
        labels:
          chain: 'verdis-mainnet'
          role: 'validator'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

---

## 4. Substrate Metrics Endpoint Overview

When running `verdis` with `--prometheus-external --prometheus-port 9615`, the node exposes key Substrate telemetry metrics:

| Metric Name | Type | Description |
| :--- | :--- | :--- |
| `substrate_block_height{status="best"}` | Gauge | Current highest known block height |
| `substrate_block_height{status="finalized"}` | Gauge | Current GRANDPA finalized block height |
| `substrate_sub_libp2p_peers_count` | Gauge | Total active connected P2P network peers |
| `substrate_process_start_time_seconds` | Gauge | Timestamp of node binary process launch |
| `substrate_ready_transactions_number` | Gauge | Count of pending transactions in txpool |
| `substrate_tasks_spawned_total` | Counter | Total background asynchronous task threads |
| `substrate_cpu_usage_percentage` | Gauge | Substrate process CPU utilization percentage |
| `substrate_memory_allocated_bytes` | Gauge | Process heap and stack memory usage |

---

## 5. Alert Rules & Thresholds

Create `/opt/verdis-monitoring/prometheus/alerts.yml` to define firing conditions for block stalls, finality lag, and system resource exhaustion:

```yaml
groups:
  - name: verdis_validator_alerts
    rules:
      - alert: BlockProductionStalled
        expr: rate(substrate_block_height{status="best"}[2m]) == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Verdis node block production stalled"
          description: "No new best block produced on node {{ $labels.instance }} for > 1 minute."

      - alert: GrandpaFinalityLag
        expr: (substrate_block_height{status="best"} - substrate_block_height{status="finalized"}) > 10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "GRANDPA finality lagging behind best block"
          description: "Finalization lag is {{ $value }} blocks behind best block."

      - alert: LowPeerCount
        expr: substrate_sub_libp2p_peers_count < 3
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "Low peer connectivity"
          description: "Node connected to only {{ $value }} peers."

      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU utilization on host"
          description: "CPU utilization exceeded 85% for 5 minutes."

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 15
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk space running critically low"
          description: "Available disk space is below 15%."
```

---

## 6. Alertmanager Configuration & Notification Setup

Configure `/opt/verdis-monitoring/alertmanager/alertmanager.yml` for Slack, Email, and Webhook dispatching:

```yaml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@verdischain.com'
  smtp_auth_username: 'alerts@verdischain.com'
  smtp_auth_password: 'SECRET_SMTP_PASSWORD'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack-notifications'

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXX────────'
        channel: '#verdis-node-alerts'
        send_resolved: true
        title: '{{ .CommonAnnotations.summary }}'
        text: '{{ .CommonAnnotations.description }}'

  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_INTEGRATION_KEY'
        send_resolved: true
```

---

## 7. Grafana Dashboard Interpretation

### Panel Breakdown

| Panel Name | Target Metric / PromQL | Normal Value | Abnormal Indicator |
| :--- | :--- | :--- | :--- |
| **Best Block vs Finalized** | `substrate_block_height` | Parallel curves, Δ ≤ 2 blocks | Delta > 10 blocks (Finality stall) |
| **P2P Peer Count** | `substrate_sub_libp2p_peers_count` | 10 to 50 peers | < 3 peers (Network isolation) |
| **Transaction Pool Size** | `substrate_ready_transactions_number` | 0 - 50 txs | > 1000 txs (Mempool congestion) |
| **CPU Utilization** | `node_cpu_seconds_total` | 15% - 40% | > 90% sustained (BABE slot miss risk) |
| **NVMe Disk IOPS** | `rate(node_disk_writes_completed_total[1m])` | Constant I/O spikes | I/O wait > 10ms (Database bottleneck) |

---

## 8. Monitoring System Maintenance

### 8.1. Backing Up Grafana Dashboards & Database
```bash
# Export Grafana state database
docker exec verdis-grafana sqlite3 /var/lib/grafana/grafana.db ".backup '/var/lib/grafana/grafana_backup.db'"
```

### 8.2. Cleaning / Rotating Prometheus Time-Series Data
Prometheus data retention is configured to 30 days (`--storage.tsdb.retention.time=30d`). To clear old metrics manually:

```bash
curl -X POST -g 'http://localhost:9090/api/v1/admin/tsdb/clean_tombstones'
```

---

## 9. Adding Custom Metrics from Pallets

To expose custom pallet metrics (e.g. `EcoPallet` total carbon credits issued):

### Step 1: Declare Prometheus Counter in Pallet Code

In `pallets/eco-pallet/src/lib.rs`:

```rust
use substrate_prometheus_endpoint::{
    register, Counter, Opts, Registry,
};

pub struct EcoPalletMetrics {
    pub carbon_credits_issued: Counter<u64>,
}

impl EcoPalletMetrics {
    pub fn register(registry: &Registry) -> Result<Self, PrometheusError> {
        Ok(Self {
            carbon_credits_issued: register(
                Counter::new("verdis_eco_carbon_credits_issued_total", "Total carbon credits minted")?,
                registry,
            )?,
        })
    }
}
```

### Step 2: Increment Metric in Pallet Dispatchable

```rust
#[pallet::weight(10_000)]
pub fn mint_carbon_credit(origin: OriginFor<T>, amount: u64) -> DispatchResult {
    ensure_signed(origin)?;
    
    // Custom logic
    
    if let Some(metrics) = &METRICS {
        metrics.carbon_credits_issued.inc_by(amount);
    }
    
    Ok(())
}
```

---

## 10. Operational Monitoring Troubleshooting

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| **Prometheus Target `DOWN`** | Node RPC or metrics endpoint not bound externally | Add `--prometheus-external` flag to `verdis` CLI. |
| **Grafana Dashboard Blank** | Data source connection failure to Prometheus | Test `http://prometheus:9090` network routing inside Grafana container. |
| **Alertmanager Notifications Failing** | Invalid Slack webhook or SMTP auth error | Run `docker logs verdis-alertmanager` to inspect HTTP dispatch errors. |
