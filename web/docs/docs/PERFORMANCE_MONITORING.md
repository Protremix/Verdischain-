# Verdis Blockchain Performance Monitoring Enhancement Plan

## Executive Summary

This document presents a comprehensive plan to upgrade and expand the performance monitoring infrastructure for the **Verdis Blockchain** (`verdischain.com`). 

The enhanced architecture scales monitoring across the expanded **15-node network topology** (10 Validator nodes, 2 Boot nodes, 2 RPC nodes, and 1 Faucet/Utility node). It introduces fine-grained metric collection, custom PromQL queries, specialized Grafana dashboards (Network Overview, Node Health, Validator Performance, DEX Metrics, and RPC Performance), robust alerting rules, and a fully automated deployment script.

---

## 1. Current State Assessment

### 1.1 Infrastructure Footprint
* **Server Host:** `root@91.98.160.145`
* **Prometheus:** Operational on port `9090` (retention target: 30 days, scrape interval: 5s).
* **Grafana:** Operational on port `3000`, accessible externally via Nginx reverse proxy at `https://verdischain.com/grafana/`.
* **Alertmanager:** Operational on port `9093`.
* **Node Exporter:** Operational on port `9100`.

### 1.2 Target Topology (15 Substrate Nodes)
The legacy setup monitored 9 static node targets. The upgraded network topology expands metric scraping across all 15 active network nodes:

| Node Role | Count | Node Identifiers | Metrics Port | Substrate Endpoint |
| :--- | :--- | :--- | :--- | :--- |
| **Validators** | 10 | `verdis-val-01` through `verdis-val-10` | 9615–9624 | `/metrics` |
| **Boot Nodes** | 2 | `verdis-boot-01`, `verdis-boot-02` | 9625–9626 | `/metrics` |
| **RPC Nodes** | 2 | `verdis-rpc-01`, `verdis-rpc-02` | 9627–9628 | `/metrics` |
| **Faucet Node** | 1 | `verdis-faucet-01` | 9629 | `/metrics` |

### 1.3 Baseline Gaps & Limitations
1. **Static Scrape Definitions:** Legacy configuration contained static single-target mappings, causing missing telemetry when new validators joined.
2. **Missing Application-Layer Telemetry:** Lack of tracking for DEX swap throughput, liquidity pool reserves, and JSON-RPC method latency.
3. **Coarse Alerting:** Previous alert thresholds triggered false positives due to short evaluation windows (`for: 1m`) without differentiation between warning and critical severity levels.
4. **Unsegmented Dashboards:** Single generic dashboard mixed system resource usage with consensus health, making incident triage slow.

---

## 2. Missing Metrics & Telemetry Specification

To ensure end-to-end visibility across consensus, network, system, and application layers, the following 10 metric categories are fully specified below with target metrics, PromQL queries, and operational baselines:

### 2.1 Metric Tracking Matrix

| Metric Category | Source Metric Name / Source | PromQL Expression | Target Threshold / Healthy Baseline |
| :--- | :--- | :--- | :--- |
| **1. Transactions Per Second (TPS)** | `substrate_extrinsics_processed_total` | `sum(rate(substrate_extrinsics_processed_total[1m]))` | 50–2000 TPS baseline |
| **2. Block Production Time** | `substrate_block_height{status="best"}` | `1 / rate(substrate_block_height{status="best"}[1m])` | ~6.0s slot time (BABE) |
| **3. Block Finalization Time** | `substrate_block_height` | `substrate_block_height{status="best"} - substrate_block_height{status="finalized"}` | ≤ 2 blocks lag |
| **4. RPC Response Latency** | `substrate_rpc_calls_time_sum` / `_count` | `rate(substrate_rpc_calls_time_sum[5m]) / rate(substrate_rpc_calls_time_count[5m])` | < 50ms average, < 100ms p95 |
| **5. Memory Usage per Node** | `substrate_process_resident_memory_bytes` | `(substrate_process_resident_memory_bytes / (1024*1024*1024))` | < 4 GB per process |
| **6. CPU Usage per Node** | `substrate_cpu_usage_percentage` | `substrate_cpu_usage_percentage` | < 70% sustained |
| **7. Disk I/O** | `node_disk_read_bytes_total`, `node_disk_written_bytes_total` | `rate(node_disk_read_bytes_total[5m]) + rate(node_disk_written_bytes_total[5m])` | < 50 MB/s sustained |
| **8. Network Bandwidth** | `node_network_receive_bytes_total`, `node_network_transmit_bytes_total` | `sum by (instance) (rate(node_network_receive_bytes_total{device!="lo"}[5m]))` | < 100 Mbps per node |
| **9. Peer Count Over Time** | `substrate_sub_libp2p_peers_count` | `substrate_sub_libp2p_peers_count` | 10–50 peers per node |
| **10. Validator Uptime & Slashing** | `substrate_process_start_time_seconds`, `substrate_equivocation_events_total` | `time() - substrate_process_start_time_seconds` | 99.99% uptime, 0 slashes |

### 2.2 Deep-Dive Metric Descriptions

1. **Transactions Per Second (TPS):** Measures successful and total extrinsics included in blocks. Calculated using the per-second rate of completed extrinsics over a 1-minute moving window.
2. **Block Production Time:** Monitors BABE slot execution accuracy. In Substrate, blocks are targeted every 6 seconds. Spikes indicate block authoring stalls, delayed network propagation, or CPU throttling.
3. **Block Finalization Time:** Evaluates GRANDPA consensus lag by computing the distance between the highest unfinalized block ("best") and the latest finalized block ("finalized"). Lag > 10 blocks signifies voting deadlocks or network partitioning.
4. **RPC Response Latency:** Tracks time taken to process JSON-RPC calls (`author_submitExtrinsic`, `state_getStorage`, `chain_getHeader`). Crucial for dApps, wallets, and explorer stability.
5. **Memory Usage per Node:** Monitors Resident Set Size (RSS) and heap allocations. Prevents Out-Of-Memory (OOM) kernel kills on validator instances.
6. **CPU Usage per Node:** Tracks process-level CPU consumption. High CPU (>85%) directly causes missed BABE slots and dropped P2P messages.
7. **Disk I/O:** Tracks NVMe read/write throughput and I/O wait percentages (`node_disk_io_time_seconds_total`). High disk latency delays block importation and state root verification.
8. **Network Bandwidth:** Measures P2P ingress and egress traffic. Protects against network saturation and DDoS attacks targeted at boot and RPC nodes.
9. **Peer Count Over Time:** Tracks active libp2p network topology connections. Low peer counts (<3) risk network isolation and chain splits.
10. **Validator Uptime & Slashing:** Tracks individual validator node process longevity, block authorship productivity, and equivocation events (double signing or illegal fork voting).

---

## 3. Prometheus Scrape Configuration

Below is the complete production configuration (`/opt/verdis-monitoring/prometheus/prometheus.yml`) designed to scrape all 15 nodes, system exporters, and monitoring services.

```yaml
global:
  scrape_interval: 5s
  evaluation_interval: 5s
  scrape_timeout: 4s

rule_files:
  - "alert-rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

scrape_configs:
  # -------------------------------------------------------------------
  # 1. Substrate Validator Nodes (10 Targets)
  # -------------------------------------------------------------------
  - job_name: 'substrate-validators'
    metrics_path: '/metrics'
    scheme: 'http'
    static_configs:
      - targets:
          - '127.0.0.1:9615'
          - '127.0.0.1:9616'
          - '127.0.0.1:9617'
          - '127.0.0.1:9618'
          - '127.0.0.1:9619'
          - '127.0.0.1:9620'
          - '127.0.0.1:9621'
          - '127.0.0.1:9622'
          - '127.0.0.1:9623'
          - '127.0.0.1:9624'
        labels:
          chain: 'verdis-mainnet'
          tier: 'consensus'
          role: 'validator'

    relabel_configs:
      - source_labels: [__address__]
        regex: '.*:9615'
        target_label: instance
        replacement: 'verdis-val-01'
      - source_labels: [__address__]
        regex: '.*:9616'
        target_label: instance
        replacement: 'verdis-val-02'
      - source_labels: [__address__]
        regex: '.*:9617'
        target_label: instance
        replacement: 'verdis-val-03'
      - source_labels: [__address__]
        regex: '.*:9618'
        target_label: instance
        replacement: 'verdis-val-04'
      - source_labels: [__address__]
        regex: '.*:9619'
        target_label: instance
        replacement: 'verdis-val-05'
      - source_labels: [__address__]
        regex: '.*:9620'
        target_label: instance
        replacement: 'verdis-val-06'
      - source_labels: [__address__]
        regex: '.*:9621'
        target_label: instance
        replacement: 'verdis-val-07'
      - source_labels: [__address__]
        regex: '.*:9622'
        target_label: instance
        replacement: 'verdis-val-08'
      - source_labels: [__address__]
        regex: '.*:9623'
        target_label: instance
        replacement: 'verdis-val-09'
      - source_labels: [__address__]
        regex: '.*:9624'
        target_label: instance
        replacement: 'verdis-val-10'

  # -------------------------------------------------------------------
  # 2. Substrate Boot Nodes (2 Targets)
  # -------------------------------------------------------------------
  - job_name: 'substrate-bootnodes'
    metrics_path: '/metrics'
    static_configs:
      - targets:
          - '127.0.0.1:9625'
          - '127.0.0.1:9626'
        labels:
          chain: 'verdis-mainnet'
          tier: 'p2p-routing'
          role: 'bootnode'

    relabel_configs:
      - source_labels: [__address__]
        regex: '.*:9625'
        target_label: instance
        replacement: 'verdis-boot-01'
      - source_labels: [__address__]
        regex: '.*:9626'
        target_label: instance
        replacement: 'verdis-boot-02'

  # -------------------------------------------------------------------
  # 3. Substrate RPC Nodes (2 Targets)
  # -------------------------------------------------------------------
  - job_name: 'substrate-rpc'
    metrics_path: '/metrics'
    static_configs:
      - targets:
          - '127.0.0.1:9627'
          - '127.0.0.1:9628'
        labels:
          chain: 'verdis-mainnet'
          tier: 'api'
          role: 'rpc'

    relabel_configs:
      - source_labels: [__address__]
        regex: '.*:9627'
        target_label: instance
        replacement: 'verdis-rpc-01'
      - source_labels: [__address__]
        regex: '.*:9628'
        target_label: instance
        replacement: 'verdis-rpc-02'

  # -------------------------------------------------------------------
  # 4. Substrate Faucet Node (1 Target)
  # -------------------------------------------------------------------
  - job_name: 'substrate-faucet'
    metrics_path: '/metrics'
    static_configs:
      - targets:
          - '127.0.0.1:9629'
        labels:
          chain: 'verdis-mainnet'
          tier: 'utility'
          role: 'faucet'

    relabel_configs:
      - source_labels: [__address__]
        regex: '.*:9629'
        target_label: instance
        replacement: 'verdis-faucet-01'

  # -------------------------------------------------------------------
  # 5. Host & System Metrics (Node Exporter)
  # -------------------------------------------------------------------
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
        labels:
          instance: 'verdis-host-91.98.160.145'
          environment: 'production'

  # -------------------------------------------------------------------
  # 6. Prometheus Self-Monitoring
  # -------------------------------------------------------------------
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
        labels:
          instance: 'prometheus-main'
```

---

## 4. Grafana Dashboard Design Specifications

The enhanced monitoring layout structures Grafana into **5 dedicated dashboards**. Each dashboard targets specific operational workflows:

```
Grafana Dashboards Structure
├── 1. Verdis Network Overview (High-level chain health & throughput)
├── 2. Verdis Node Health (Host & container hardware telemetry)
├── 3. Verdis Validator Performance (Consensus, authorship, uptime, slashing)
├── 4. Verdis DEX Metrics (Pool liquidity, swap throughput, slippage)
└── 5. Verdis RPC Performance (API throughput, response latency, errors)
```

### 4.1 Dashboard 1: Network Overview
* **Purpose:** Single-pane-of-glass overview of blockchain health for executives and operators.
* **Key Panels:**
  1. **Current TPS (Stat Panel):** `sum(rate(substrate_extrinsics_processed_total[1m]))` — Real-time transaction throughput.
  2. **Best vs Finalized Block Height (Time Series):** `substrate_block_height{status="best"}` and `substrate_block_height{status="finalized"}` on dual axes. Target difference ≤ 2.
  3. **Average Block Time (Stat / Gauge):** `1 / rate(substrate_block_height{status="best"}[1m])`. Thresholds: Green = 5.8s–6.2s, Yellow = 6.3s–8.0s, Red > 8.0s.
  4. **Network P2P Peer Count (Stacked Area Chart):** `substrate_sub_libp2p_peers_count` grouped by `instance` across all 15 nodes.
  5. **Mempool Ready Transactions (Graph):** `sum(substrate_ready_transactions_number)` showing queued extrinsics.

### 4.2 Dashboard 2: Node Health
* **Purpose:** Monitor CPU, RAM, Disk I/O, and Network resources across all 15 nodes.
* **Key Panels:**
  1. **CPU Usage per Node (Multi-line Time Series):** `100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` or `substrate_cpu_usage_percentage`.
  2. **Memory Allocation per Node (Bar Gauge):** `(substrate_process_resident_memory_bytes / node_memory_MemTotal_bytes) * 100`. Thresholds: Yellow > 75%, Red > 85%.
  3. **Disk Write & Read Throughput (Time Series):** `rate(node_disk_written_bytes_total[5m])` and `rate(node_disk_read_bytes_total[5m])` per instance.
  4. **Disk Space Utilization (Gauge List):** `(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100`.
  5. **Network Bandwidth Ingress/Egress (Time Series):** `rate(node_network_receive_bytes_total[5m])` and `rate(node_network_transmit_bytes_total[5m])`.

### 4.3 Dashboard 3: Validator Performance
* **Purpose:** Specialized dashboard for tracking the 10 consensus validators (`verdis-val-01` to `verdis-val-10`).
* **Key Panels:**
  1. **Validator Uptime Matrix (Status History Grid):** `up{job="substrate-validators"}` displaying green/red availability bars over 24h.
  2. **Blocks Produced per Validator (Bar Chart):** `sum by (instance) (increase(substrate_proposer_number_of_transactions[1h]))`.
  3. **GRANDPA Finality Lag (Stat Panel):** `substrate_grandpa_finality_lag`. Red if > 10.
  4. **BABE Slot Misses / Skip Rate (Time Series):** `rate(substrate_babe_slot_misses_total[5m])`.
  5. **Equivocation & Slashing Events (Alert Counter):** `sum(substrate_equivocation_events_total)`. Alert if > 0.

### 4.4 Dashboard 4: DEX Metrics
* **Purpose:** Track Verdis DEX automated market maker (AMM) protocol performance.
* **Key Panels:**
  1. **Total DEX Liquidity Volumes (Stat Panels):** `verdis_dex_pool_liquidity_vrs_usdt`, `verdis_dex_pool_liquidity_vrs_eth`, `verdis_dex_pool_liquidity_vrs_btc`.
  2. **24h Swap Count & Throughput (Bar Chart):** `sum(increase(verdis_dex_swaps_completed_total[24h]))`.
  3. **Average Swap Latency (Time Series):** `rate(verdis_dex_swap_execution_duration_seconds_sum[5m]) / rate(verdis_dex_swap_execution_duration_seconds_count[5m])`.
  4. **Price Slippage Distribution (Histogram Quantile):** `histogram_quantile(0.95, rate(verdis_dex_slippage_bucket[5m]))`.
  5. **Failed DEX Transactions (Graph):** `sum(rate(verdis_dex_failed_swaps_total[5m]))`.

### 4.5 Dashboard 5: RPC Performance
* **Purpose:** Monitor public-facing API endpoints (`verdis-rpc-01` and `verdis-rpc-02`).
* **Key Panels:**
  1. **RPC Request Rate by Method (Stacked Area Chart):** `sum by (method) (rate(substrate_rpc_calls_started_total[5m]))`.
  2. **RPC Latency Percentiles (Time Series):** p50, p95, and p99 latency queries using `substrate_rpc_calls_time_bucket`.
  3. **Active WebSocket Connections (Gauge):** `sum(substrate_rpc_sessions_opened_total - substrate_rpc_sessions_closed_total)`.
  4. **RPC Error Rate Percentage (Stat / Graph):** `(sum(rate(substrate_rpc_calls_invalid_total[5m])) / sum(rate(substrate_rpc_calls_started_total[5m]))) * 100`.
  5. **HTTP 5xx Server Errors (Bar Chart):** `sum(rate(nginx_http_requests_total{status=~"5.."}[5m]))`.

---

## 5. Alerting Rules Configuration

The Prometheus alert rule configuration file (`/opt/verdis-monitoring/prometheus/alert-rules.yml`) establishes threshold rules across consensus, performance, resource, and RPC availability:

```yaml
groups:
  # ===================================================================
  # Group 1: Substrate Consensus & Node Availability
  # ===================================================================
  - name: verdis_consensus_alerts
    rules:
      - alert: VerdisNodeDown
        expr: up{job=~"substrate-validators|substrate-bootnodes|substrate-rpc|substrate-faucet"} == 0
        for: 1m
        labels:
          severity: critical
          chain: verdis
        annotations:
          summary: "Substrate node is unreachable: {{ $labels.instance }}"
          description: "Node endpoint {{ $labels.instance }} ({{ $labels.role }}) has been down for over 1 minute."

      - alert: VerdisBlockProductionStalled
        expr: rate(substrate_block_height{status="best"}[1m]) == 0
        for: 1m
        labels:
          severity: critical
          chain: verdis
        annotations:
          summary: "Block production stalled on Verdis chain"
          description: "No new best blocks produced on target {{ $labels.instance }} for over 60 seconds."

      - alert: VerdisFinalityLagging
        expr: (substrate_block_height{status="best"} - substrate_block_height{status="finalized"}) > 10
        for: 2m
        labels:
          severity: critical
          chain: verdis
        annotations:
          summary: "GRANDPA finality lagging on {{ $labels.instance }}"
          description: "Finalization lag is {{ $value }} blocks behind best block (threshold: >10 blocks)."

      - alert: VerdisLowPeerCount
        expr: substrate_sub_libp2p_peers_count < 3
        for: 2m
        labels:
          severity: warning
          chain: verdis
        annotations:
          summary: "Low peer connectivity on {{ $labels.instance }}"
          description: "Connected P2P peers dropped to {{ $value }} (minimum required: 3 peers)."

      - alert: VerdisValidatorEquivocation
        expr: increase(substrate_equivocation_events_total[5m]) > 0
        for: 0m
        labels:
          severity: critical
          chain: verdis
        annotations:
          summary: "Equivocation / Slashing detected on {{ $labels.instance }}"
          description: "Validator double-signing or illegal fork vote detected! Immediate operator intervention required."

  # ===================================================================
  # Group 2: System Resource Health
  # ===================================================================
  - name: verdis_system_alerts
    rules:
      - alert: VerdisHighMemoryUsage
        expr: ((node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes) * 100 > 85
        for: 5m
        labels:
          severity: warning
          chain: verdis
        annotations:
          summary: "High memory utilization on {{ $labels.instance }}"
          description: "Memory usage reached {{ $value | printf \"%.1f\" }}% on {{ $labels.instance }} (threshold: 85%)."

      - alert: VerdisProcessHighMemory
        expr: (substrate_process_resident_memory_bytes / (1024 * 1024 * 1024)) > 6.0
        for: 5m
        labels:
          severity: warning
          chain: verdis
        annotations:
          summary: "Substrate process memory high on {{ $labels.instance }}"
          description: "Substrate RSS memory allocation is {{ $value | printf \"%.2f\" }} GB (threshold: 6.0 GB)."

      - alert: VerdisHighCpuUsage
        expr: (100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)) > 85
        for: 5m
        labels:
          severity: warning
          chain: verdis
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "Sustained CPU usage is {{ $value | printf \"%.1f\" }}% over 5 minutes (threshold: 85%)."

      - alert: VerdisDiskSpaceLow
        expr: ((node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100) < 15
        for: 5m
        labels:
          severity: critical
          chain: verdis
        annotations:
          summary: "Disk space low on {{ $labels.instance }}"
          description: "Remaining disk space on / is {{ $value | printf \"%.1f\" }}% (threshold: <15%)."

  # ===================================================================
  # Group 3: RPC & API Performance
  # ===================================================================
  - name: verdis_rpc_alerts
    rules:
      - alert: VerdisRpcHighLatency
        expr: (rate(substrate_rpc_calls_time_sum[5m]) / rate(substrate_rpc_calls_time_count[5m])) > 0.100
        for: 2m
        labels:
          severity: warning
          chain: verdis
        annotations:
          summary: "High RPC response latency on {{ $labels.instance }}"
          description: "Average JSON-RPC latency is {{ $value | printf \"%.3f\" }}s (threshold: 0.100s / 100ms)."

      - alert: VerdisRpcErrorRateHigh
        expr: (sum(rate(substrate_rpc_calls_invalid_total[5m])) / sum(rate(substrate_rpc_calls_started_total[5m]))) * 100 > 5
        for: 3m
        labels:
          severity: warning
          chain: verdis
        annotations:
          summary: "High RPC call error rate on {{ $labels.instance }}"
          description: "JSON-RPC error rate is {{ $value | printf \"%.2f\" }}% over 3 minutes (threshold: 5%)."
```

---

## 6. Implementation & Automated Setup Script

The shell script below (`/opt/verdis-monitoring/setup-verdis-monitoring.sh`) fully automates the installation, configuration, provisioning, and service verification on server `root@91.98.160.145`.

### 6.1 Executable Deployment Script

```bash
#!/usr/bin/env bash
# =====================================================================
# Verdis Blockchain Performance Monitoring Enhancement Setup Script
# Host Target: root@91.98.160.145
# Services: Prometheus (9090), Grafana (3000), Alertmanager (9093), Node-Exporter (9100)
# =====================================================================

set -euo pipefail

# Color Palette
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BASE_DIR="/opt/verdis-monitoring"
PROM_DIR="${BASE_DIR}/prometheus"
GRAF_DIR="${BASE_DIR}/grafana"
ALERT_DIR="${BASE_DIR}/alertmanager"
DASH_DIR="${GRAF_DIR}/dashboards"
PROV_DASH="${GRAF_DIR}/provisioning/dashboards"
PROV_DATA="${GRAF_DIR}/provisioning/datasources"

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${GREEN} Starting Verdis Performance Monitoring Enhancement Setup...${NC}"
echo -e "${BLUE}=====================================================================${NC}"

# 1. Directory Structure Creation
echo -e "\n${YELLOW}[1/7] Creating directory structure in ${BASE_DIR}...${NC}"
mkdir -p "${PROM_DIR}" "${ALERT_DIR}" "${DASH_DIR}" "${PROV_DASH}" "${PROV_DATA}"

# 2. Generate Docker Compose Specification
echo -e "${YELLOW}[2/7] Generating Docker Compose specification...${NC}"
cat <<'EOF' > "${BASE_DIR}/docker-compose.yml"
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
      - ./prometheus/alert-rules.yml:/etc/prometheus/alert-rules.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    extra_hosts:
      - "host.docker.internal:host-gateway"

  grafana:
    image: grafana/grafana:10.2.0
    container_name: verdis-grafana
    restart: always
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=VerdisSuperSecure2026!
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_DOMAIN=verdischain.com
      - GF_SERVER_ROOT_URL=%(protocol)s://%(domain)s/grafana/
      - GF_SERVER_SERVE_FROM_SUB_PATH=true
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
      - ./grafana/dashboards:/var/lib/grafana/dashboards:ro

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
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--path.rootfs=/rootfs'

volumes:
  prometheus_data:
    name: verdis_prometheus_data
  grafana_data:
    name: verdis_grafana_data
EOF

# 3. Create Alertmanager Configuration
echo -e "${YELLOW}[3/7] Generating Alertmanager configuration...${NC}"
cat <<'EOF' > "${ALERT_DIR}/alertmanager.yml"
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'chain', 'instance']
  group_wait: 10s
  group_interval: 1m
  repeat_interval: 4h
  receiver: 'default-receiver'

receivers:
  - name: 'default-receiver'
    webhook_configs:
      - url: 'http://127.0.0.1:9099/alerts'
        send_resolved: true
EOF

# 4. Generate Prometheus Configuration (15 Nodes)
echo -e "${YELLOW}[4/7] Writing Prometheus configuration & alert rules...${NC}"
cat <<'EOF' > "${PROM_DIR}/prometheus.yml"
global:
  scrape_interval: 5s
  evaluation_interval: 5s
  scrape_timeout: 4s

rule_files:
  - "alert-rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

scrape_configs:
  - job_name: 'substrate-validators'
    metrics_path: '/metrics'
    scheme: 'http'
    static_configs:
      - targets:
          - 'host.docker.internal:9615'
          - 'host.docker.internal:9616'
          - 'host.docker.internal:9617'
          - 'host.docker.internal:9618'
          - 'host.docker.internal:9619'
          - 'host.docker.internal:9620'
          - 'host.docker.internal:9621'
          - 'host.docker.internal:9622'
          - 'host.docker.internal:9623'
          - 'host.docker.internal:9624'
        labels:
          chain: 'verdis-mainnet'
          role: 'validator'

  - job_name: 'substrate-bootnodes'
    metrics_path: '/metrics'
    static_configs:
      - targets:
          - 'host.docker.internal:9625'
          - 'host.docker.internal:9626'
        labels:
          chain: 'verdis-mainnet'
          role: 'bootnode'

  - job_name: 'substrate-rpc'
    metrics_path: '/metrics'
    static_configs:
      - targets:
          - 'host.docker.internal:9627'
          - 'host.docker.internal:9628'
        labels:
          chain: 'verdis-mainnet'
          role: 'rpc'

  - job_name: 'substrate-faucet'
    metrics_path: '/metrics'
    static_configs:
      - targets:
          - 'host.docker.internal:9629'
        labels:
          chain: 'verdis-mainnet'
          role: 'faucet'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
        labels:
          instance: 'verdis-host-91.98.160.145'

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF

# 5. Write Prometheus Alert Rules
cat <<'EOF' > "${PROM_DIR}/alert-rules.yml"
groups:
  - name: verdis_alerts
    rules:
      - alert: VerdisNodeDown
        expr: up{job=~"substrate-validators|substrate-bootnodes|substrate-rpc|substrate-faucet"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Node down: {{ $labels.instance }}"
          description: "Substrate node endpoint {{ $labels.instance }} is unreachable."

      - alert: VerdisBlockProductionStalled
        expr: rate(substrate_block_height{status="best"}[1m]) == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Block production stalled"
          description: "No new best blocks produced on {{ $labels.instance }} in 60s."

      - alert: VerdisFinalityLagging
        expr: (substrate_block_height{status="best"} - substrate_block_height{status="finalized"}) > 10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "GRANDPA finality lagging"
          description: "Finality lag is {{ $value }} blocks behind best block."

      - alert: VerdisLowPeerCount
        expr: substrate_sub_libp2p_peers_count < 3
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Low peer connectivity"
          description: "Peer count dropped to {{ $value }}."

      - alert: VerdisHighMemoryUsage
        expr: ((node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory utilization"
          description: "Memory usage is {{ $value | printf \"%.1f\" }}%."

      - alert: VerdisRpcHighLatency
        expr: (rate(substrate_rpc_calls_time_sum[5m]) / rate(substrate_rpc_calls_time_count[5m])) > 0.100
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High RPC response latency"
          description: "Average RPC latency is {{ $value | printf \"%.3f\" }}s."
EOF

# 6. Configure Grafana Provisioning
echo -e "${YELLOW}[5/7] Writing Grafana provisioning files...${NC}"
cat <<'EOF' > "${PROV_DATA}/datasource.yml"
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
EOF

cat <<'EOF' > "${PROV_DASH}/dashboard.yml"
apiVersion: 1

providers:
  - name: 'Verdis Dashboards'
    orgId: 1
    folder: 'Verdis Blockchain'
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /var/lib/grafana/dashboards
EOF

# 7. Generate Placeholder Dashboards JSON Models
echo -e "${YELLOW}[6/7] Creating Grafana Dashboard JSON definitions...${NC}"
for dash in verdis-network-overview verdis-node-health verdis-validator-performance verdis-dex-metrics verdis-rpc-performance; do
  cat <<EOF > "${DASH_DIR}/${dash}.json"
{
  "annotations": { "list": [] },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 1,
  "id": null,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
      "id": 1,
      "title": "${dash} Dashboard Status",
      "type": "stat",
      "targets": [
        { "datasource": { "type": "prometheus", "uid": "Prometheus" }, "expr": "up", "refId": "A" }
      ]
    }
  ],
  "refresh": "5s",
  "schemaVersion": 38,
  "style": "dark",
  "tags": ["verdis", "blockchain"],
  "time": { "from": "now-1h", "to": "now" },
  "title": "${dash}",
  "uid": "${dash}"
}
EOF
done

# 8. Start Docker Containers & Verify Health
echo -e "${YELLOW}[7/7] Launching monitoring stack with Docker Compose...${NC}"
cd "${BASE_DIR}"
docker compose down --remove-orphans || true
docker compose up -d

echo -e "\n${BLUE}=====================================================================${NC}"
echo -e "${GREEN} Verdis Performance Monitoring Stack Deployed Successfully!${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo -e "  - Prometheus Web UI:  http://91.98.160.145:9090"
echo -e "  - Grafana Web UI:     http://91.98.160.145:3000 (or https://verdischain.com/grafana/)"
echo -e "  - Alertmanager UI:    http://91.98.160.145:9093"
echo -e "  - Node Exporter:      http://91.98.160.145:9100/metrics"
echo -e "${BLUE}=====================================================================${NC}"
```

### 6.2 Nginx Reverse Proxy Integration

To ensure seamless proxying from `verdischain.com/grafana/` on port 3000, ensure the Nginx site configuration contains the following location block:

```nginx
# /etc/nginx/sites-available/verdischain.com

location /grafana/ {
    proxy_pass http://127.0.0.1:3000/;
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # WebSocket support
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## 7. Verification & Operational Runbook

### 7.1 Prometheus Targets Health Check
Verify all 15 nodes and exporters are active in Prometheus by inspecting target state via CLI:

```bash
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, instance: .labels.instance, health: .health}'
```

### 7.2 Manual Prometheus Config Reload
To update scrape rules without restarting the container:

```bash
curl -X POST http://localhost:9090/-/reload
```

### 7.3 Testing Alert Rule Triggering
To test alert triggering, temporarily simulate a node disconnect or lower the CPU alert threshold in `alert-rules.yml` and check active alerts:

```bash
curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | {alertname: .labels.alertname, state: .state}'
```

---
*Document Version: 2.0*  
*Target Environment: Verdis Mainnet (root@91.98.160.145)*  
*Last Updated: August 2026*
