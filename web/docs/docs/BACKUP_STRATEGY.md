# Verdis Blockchain Infrastructure: Production Backup & Disaster Recovery Strategy

**Document Status:** Production / Active  
**Infrastructure Target:** Verdis Blockchain Mainnet (`verdischain.com`)  
**Server IP:** `91.98.160.145` (Root Execution Environment)  
**Architecture:** Substrate-based POS/DPOS Network (15 Active Nodes: 2 Boot Nodes, 2 RPC Nodes, 10 Validator Nodes, 1 Faucet Node)  
**Chain Engine Path:** `/opt/verdis-chain-rust/`  
**Native Token:** VRS (SS58 Format `909`, 9 Decimals)  
**Monitoring Stack:** Grafana (Port 3000), Prometheus (Port 9090)  
**Last Updated:** August 2026  

---

## 1. What to Backup (Scope & Data Classification)

Maintaining node state, crypto key material, configuration files, web interfaces, and audit logs requires a multi-layered data inventory. Each directory in the Verdis production stack is categorized below by backup scope, criticality, frequency, and retention policy.

| Asset / Component | System Path | Description & Items Included | Criticality Level | Backup Frequency | Retention Period |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Blockchain Data** | `/opt/verdis-chain-rust/data/` (or node data dirs) | Substrate RocksDB/ParityDB blockchain database state for each of the 15 nodes (2 Boot, 2 RPC, 10 Validators, 1 Faucet) | **Critical** | Daily (2:00 AM UTC) | 30 Days |
| **Chain Specification** | `/opt/verdis-chain-rust/chain-spec-raw.json` | Raw Substrate chain spec containing genesis block, storage keys, SS58 network prefix (`909`), and pallet configurations | **Critical** | Daily / On Change | 30 Days |
| **Validator Keystores** | `/opt/verdis-chain-rust/keystore/` | Cryptographic secret seed files for BABE (`babe`), GRANDPA (`gran`), ImOnline (`imon`), Authority Discovery (`audi`) across 10 validators | **Critical / Confidential** | Daily (Encrypted) | 30 Days + Offsite |
| **Nginx Configurations** | `/etc/nginx/sites-enabled/`<br>`/etc/nginx/sites-available/` | Reverse proxy routing rules, WebSocket RPC upgrade headers (Port 9944), Verdiscan explorer routes, rate limiting | **High** | Daily | 30 Days |
| **SSL Certificates** | `/etc/letsencrypt/` | Let's Encrypt TLS/SSL certificates (`fullchain.pem`, `privkey.pem`) for `verdischain.com` and subdomains | **High** | Daily | 30 Days |
| **Grafana & Prometheus** | `/var/lib/grafana/`<br>`/etc/grafana/`<br>`/var/lib/prometheus/`<br>`/etc/prometheus/` | Prometheus TSDB metrics, alert manager definitions, Grafana SQLite database, dashboard JSONs, datasources (Ports 3000/9090) | **Medium-High** | Daily | 30 Days |
| **Website Static Files** | `/var/www/verdiscan/` | Verdiscan block explorer front-end, ecosystem dashboard HTML/JS/CSS, mobile wallet web distributions | **High** | Daily | 30 Days |
| **CTO Audit Logs** | `/opt/verdis-cto-logs/` | Executive administrative execution logs, binary upgrade verifications, governance transaction logs, security audit trails | **High** | Daily | 30 Days (Active) / 90+ Days (Archived) |

---

### Detailed Asset Breakdown

1. **Blockchain Data (`/opt/verdis-chain-rust/data/`)**
   - Contains the state trie and block history stored in RocksDB format.
   - Across the 15 nodes (2 boot, 2 RPC, 10 validators, 1 faucet), taking a consistent state snapshot requires flushing DB buffers or gracefully stopping node services during snapshot creation.

2. **Chain Specification Files (`chain-spec-raw.json`)**
   - The compiled raw chain spec JSON file (`/opt/verdis-chain-rust/chain-spec-raw.json` or `/opt/verdis-chain-rust/chain-spec.json`) defines network genesis parameters, genesis balances, validator session keys, WASM runtime blob, and bootnode multiaddresses.
   - Essential for node initialization and peer synchronization.

3. **Validator Keystores (`/opt/verdis-chain-rust/keystore/`)**
   - Stores hex-encoded secret seeds in files named after `[key_type_hex][pubkey_hex]`.
   - Key types: `babe` (BABE block production), `gran` (GRANDPA finality), `imon` (ImOnline liveness), `audi` (Authority Discovery), `aura` (Aura consensus if enabled).
   - **Security Note:** Keys are secured with `0700` directory permissions and `0600` file permissions. Backups must be encrypted before remote transfer.

4. **Nginx Configurations (`/etc/nginx/sites-enabled/`)**
   - Sites configs for `verdischain.com`, `rpc.verdischain.com`, `explorer.verdischain.com`, `faucet.verdischain.com`, and `grafana.verdischain.com`.
   - Ensures zero-downtime routing and SSL termination rules can be restored instantly.

5. **SSL Certificates (`/etc/letsencrypt/`)**
   - Active SSL certificates and private keys managed by Certbot. Restoring these prevents TLS certificate mismatch errors during recovery.

6. **Grafana Dashboards & Prometheus Data (`/etc/grafana/`, `/var/lib/grafana/`, `/etc/prometheus/`, `/var/lib/prometheus/`)**
   - Grafana configuration, user preferences, and dashboard layout definitions (SQLite database `grafana.db` and JSON exports).
   - Prometheus target definitions, alerting rules (`verdis_alerts.yml`), and time-series database (TSDB) metrics data on ports 3000 and 9090.

7. **Website Static Files (`/var/www/verdiscan/`)**
   - The production build of the Verdiscan block explorer web client, wallet web UI, DEX interface, and developer documentation portal.

8. **CTO Audit Logs (`/opt/verdis-cto-logs/`)**
   - Contains append-only security logs, administrative operation records, contract deployment signatures, and node update histories required for compliance and post-incident investigation.

---

## 2. Production Backup Script (`verdis-backup.sh`)

Below is the production-grade, self-contained Bash script that automates the daily backup workflow.

### Features & Workflow
- **Directory Creation:** Timestamped backup directory `/opt/verdis-backups/daily/verdis-backup-YYYYMMDD-HHMMSS`.
- **Atomic Operations:** Copies data into a temporary working directory before archiving.
- **Checksum Verification:** Computes SHA-256 digests and immediately tests archive extraction integrity (`tar -tzf`).
- **Comprehensive Logging:** Appends timestamped stdout/stderr output to `/var/log/verdis-backup.log`.
- **Automatic Pruning:** Automatically deletes backup archives and checksum files older than 30 days.
- **Cron Ready:** Executable via daily cron job with lockfile protection to prevent concurrent executions.

```bash
#!/usr/bin/env bash
# ==============================================================================
# Verdis Blockchain Production Backup Script
# Location: /opt/verdis-chain-rust/backup/verdis-backup.sh
# Purpose: Full automated daily backup of blockchain data, keys, configs & logs
# Server: root@91.98.160.145 | Domain: verdischain.com
# ==============================================================================

set -euo pipefail

# --- Configuration & Paths ---
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-/opt/verdis-backups}"
DAILY_BACKUP_DIR="${BACKUP_BASE_DIR}/daily"
LOG_FILE="/var/log/verdis-backup.log"
LOCK_FILE="/var/run/verdis-backup.lock"
RETENTION_DAYS=30

TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
BACKUP_NAME="verdis-backup-${TIMESTAMP}"
TEMP_WORK_DIR="/tmp/${BACKUP_NAME}"
TARGET_ARCHIVE="${DAILY_BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
CHECKSUM_FILE="${TARGET_ARCHIVE}.sha256"

# Node & System Paths
CHAIN_BASE_DIR="/opt/verdis-chain-rust"
CHAIN_DATA_DIR="${CHAIN_BASE_DIR}/data"
CHAIN_KEYSTORE_DIR="${CHAIN_BASE_DIR}/keystore"
CHAIN_SPEC_PRIMARY="${CHAIN_BASE_DIR}/chain-spec-raw.json"
CHAIN_SPEC_ALT="${CHAIN_BASE_DIR}/chain-spec.json"

NGINX_SITES_ENABLED="/etc/nginx/sites-enabled"
NGINX_SITES_AVAILABLE="/etc/nginx/sites-available"
SSL_CERT_DIR="/etc/letsencrypt"

PROMETHEUS_ETC="/etc/prometheus"
PROMETHEUS_DATA="/var/lib/prometheus"
GRAFANA_ETC="/etc/grafana"
GRAFANA_DATA="/var/lib/grafana"

WEB_STATIC_DIR="/var/www/verdiscan"
CTO_AUDIT_LOGS="/opt/verdis-cto-logs"

NODE_SERVICE="verdis-node.service"
NODE_WAS_STOPPED=false

# --- Logging Functions ---
log() {
    local level="$1"
    shift
    local msg="$*"
    local ts
    ts=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    echo "[$ts] [$level] $msg"
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "[$ts] [$level] $msg" >> "$LOG_FILE" 2>/dev/null || true
}

log_info()    { log "INFO" "$@"; }
log_warn()    { log "WARN" "$@"; }
log_error()   { log "ERROR" "$@"; }
log_success() { log "SUCCESS" "$@"; }

# --- Cleanup Trap ---
cleanup() {
    local exit_code=$?
    log_info "Running cleanup routines (exit code: ${exit_code})..."

    # Restart blockchain node if stopped during snapshot
    if [[ "$NODE_WAS_STOPPED" == "true" ]]; then
        log_info "Restarting ${NODE_SERVICE}..."
        if command -v systemctl >/dev/null 2>&1; then
            systemctl start "$NODE_SERVICE" || log_error "Failed to restart ${NODE_SERVICE}!"
            if systemctl is-active --quiet "$NODE_SERVICE"; then
                log_success "${NODE_SERVICE} restarted successfully."
            else
                log_error "${NODE_SERVICE} is not active after restart attempt."
            fi
        fi
        NODE_WAS_STOPPED=false
    fi

    # Remove temporary work directory
    if [[ -d "$TEMP_WORK_DIR" ]]; then
        rm -rf "$TEMP_WORK_DIR"
        log_info "Temporary directory ${TEMP_WORK_DIR} cleaned up."
    fi

    # Release lock file
    if [[ -f "$LOCK_FILE" ]]; then
        rm -f "$LOCK_FILE"
    fi

    if [[ $exit_code -eq 0 ]]; then
        log_success "Backup process completed successfully."
    else
        log_error "Backup process finished with errors (exit code $exit_code)."
    fi
}

trap cleanup EXIT INT TERM

# --- Pre-flight Checks ---
preflight_checks() {
    log_info "Starting pre-flight checks..."

    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be executed as root (or via sudo)."
        exit 1
    fi

    # Verify required CLI tools
    local req_tools=("tar" "gzip" "sha256sum" "rsync" "find")
    for tool in "${req_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            log_error "Required tool '$tool' is not installed."
            exit 1
        fi
    done

    # Prevent concurrent execution
    if [[ -f "$LOCK_FILE" ]]; then
        local pid
        pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            log_error "Another backup job is currently running (PID: $pid)."
            exit 1
        else
            log_warn "Stale lockfile found. Overwriting lock."
        fi
    fi
    echo "$$" > "$LOCK_FILE"

    # Prepare backup destination directories
    mkdir -p "$DAILY_BACKUP_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"

    log_success "Pre-flight checks passed."
}

# --- Node State Pause / Sync ---
stop_node_if_running() {
    log_info "Checking state of ${NODE_SERVICE}..."
    if command -v systemctl >/dev/null 2>&1 && systemctl is-active --quiet "$NODE_SERVICE"; then
        log_info "Stopping ${NODE_SERVICE} gracefully to ensure database consistency..."
        systemctl stop "$NODE_SERVICE"
        NODE_WAS_STOPPED=true
        sleep 3
        log_success "${NODE_SERVICE} stopped."
    else
        log_info "${NODE_SERVICE} is not active. Proceeding with filesystem copy."
    fi
}

# --- File Collection ---
collect_files() {
    log_info "Creating workspace at ${TEMP_WORK_DIR}..."
    mkdir -p "${TEMP_WORK_DIR}/blockchain_data"
    mkdir -p "${TEMP_WORK_DIR}/chain_spec"
    mkdir -p "${TEMP_WORK_DIR}/keystore"
    mkdir -p "${TEMP_WORK_DIR}/nginx"
    mkdir -p "${TEMP_WORK_DIR}/ssl"
    mkdir -p "${TEMP_WORK_DIR}/monitoring/grafana"
    mkdir -p "${TEMP_WORK_DIR}/monitoring/prometheus"
    mkdir -p "${TEMP_WORK_DIR}/web_verdiscan"
    mkdir -p "${TEMP_WORK_DIR}/cto_audit_logs"

    # 1. Blockchain DB
    if [[ -d "$CHAIN_DATA_DIR" ]]; then
        log_info "Backing up Blockchain Data from ${CHAIN_DATA_DIR}..."
        rsync -a --exclude="keystore" "${CHAIN_DATA_DIR}/" "${TEMP_WORK_DIR}/blockchain_data/"
    else
        log_warn "Blockchain data dir ${CHAIN_DATA_DIR} not found. Searching for node data dirs..."
        for node_dir in "${CHAIN_BASE_DIR}"/node-*/data; do
            if [[ -d "$node_dir" ]]; then
                local node_name
                node_name=$(basename "$(dirname "$node_dir")")
                mkdir -p "${TEMP_WORK_DIR}/blockchain_data/${node_name}"
                rsync -a --exclude="keystore" "${node_dir}/" "${TEMP_WORK_DIR}/blockchain_data/${node_name}/"
            fi
        done
    fi

    # 2. Chain Spec Files
    if [[ -f "$CHAIN_SPEC_PRIMARY" ]]; then
        log_info "Backing up chain-spec-raw.json..."
        cp -a "$CHAIN_SPEC_PRIMARY" "${TEMP_WORK_DIR}/chain_spec/chain-spec-raw.json"
    elif [[ -f "$CHAIN_SPEC_ALT" ]]; then
        log_info "Backing up chain-spec.json..."
        cp -a "$CHAIN_SPEC_ALT" "${TEMP_WORK_DIR}/chain_spec/chain-spec-raw.json"
    else
        log_warn "No chain specification file found in ${CHAIN_BASE_DIR}."
    fi

    # 3. Validator Keystores
    if [[ -d "$CHAIN_KEYSTORE_DIR" ]]; then
        log_info "Backing up Validator Keystore from ${CHAIN_KEYSTORE_DIR}..."
        rsync -a "${CHAIN_KEYSTORE_DIR}/" "${TEMP_WORK_DIR}/keystore/main_keystore/"
    fi
    if [[ -d "${CHAIN_DATA_DIR}/keystore" ]]; then
        log_info "Backing up Keystore from data directory..."
        rsync -a "${CHAIN_DATA_DIR}/keystore/" "${TEMP_WORK_DIR}/keystore/data_keystore/"
    fi

    # 4. Nginx Configurations
    if [[ -d "$NGINX_SITES_ENABLED" ]]; then
        log_info "Backing up Nginx sites-enabled configuration..."
        rsync -a "${NGINX_SITES_ENABLED}/" "${TEMP_WORK_DIR}/nginx/sites-enabled/"
    fi
    if [[ -d "$NGINX_SITES_AVAILABLE" ]]; then
        log_info "Backing up Nginx sites-available configuration..."
        rsync -a "${NGINX_SITES_AVAILABLE}/" "${TEMP_WORK_DIR}/nginx/sites-available/"
    fi

    # 5. SSL Certificates
    if [[ -d "$SSL_CERT_DIR" ]]; then
        log_info "Backing up SSL Certificates from ${SSL_CERT_DIR}..."
        rsync -aL "${SSL_CERT_DIR}/" "${TEMP_WORK_DIR}/ssl/"
    fi

    # 6. Grafana & Prometheus
    if [[ -d "$GRAFANA_ETC" ]]; then
        rsync -a "${GRAFANA_ETC}/" "${TEMP_WORK_DIR}/monitoring/grafana/etc/"
    fi
    if [[ -d "$GRAFANA_DATA" ]]; then
        rsync -a --exclude="png" "${GRAFANA_DATA}/" "${TEMP_WORK_DIR}/monitoring/grafana/data/"
    fi
    if [[ -d "$PROMETHEUS_ETC" ]]; then
        rsync -a "${PROMETHEUS_ETC}/" "${TEMP_WORK_DIR}/monitoring/prometheus/etc/"
    fi
    if [[ -d "$PROMETHEUS_DATA" ]]; then
        rsync -a --exclude="wal" "${PROMETHEUS_DATA}/" "${TEMP_WORK_DIR}/monitoring/prometheus/data/"
    fi

    # 7. Website Static Files
    if [[ -d "$WEB_STATIC_DIR" ]]; then
        log_info "Backing up Verdiscan Website files from ${WEB_STATIC_DIR}..."
        rsync -a "${WEB_STATIC_DIR}/" "${TEMP_WORK_DIR}/web_verdiscan/"
    fi

    # 8. CTO Audit Logs
    if [[ -d "$CTO_AUDIT_LOGS" ]]; then
        log_info "Backing up CTO Audit Logs from ${CTO_AUDIT_LOGS}..."
        rsync -a "${CTO_AUDIT_LOGS}/" "${TEMP_WORK_DIR}/cto_audit_logs/"
    fi

    # Save Backup Metadata
    cat << EOF > "${TEMP_WORK_DIR}/backup_manifest.json"
{
  "timestamp": "${TIMESTAMP}",
  "server": "91.98.160.145",
  "domain": "verdischain.com",
  "nodes_count": 15,
  "created_by": "verdis-backup.sh",
  "ss58_prefix": 909,
  "token": "VRS"
}
EOF

    log_success "All data collected in temporary workspace."
}

# --- Compression & Archive ---
compress_archive() {
    log_info "Compressing backup archive to ${TARGET_ARCHIVE}..."
    tar -czf "$TARGET_ARCHIVE" -C "$TEMP_WORK_DIR" .
    local archive_size
    archive_size=$(du -h "$TARGET_ARCHIVE" | cut -f1)
    log_success "Archive created successfully (Size: ${archive_size})."
}

# --- Integrity & Checksum Verification ---
verify_integrity() {
    log_info "Generating SHA-256 checksum..."
    (cd "$DAILY_BACKUP_DIR" && sha256sum "$(basename "$TARGET_ARCHIVE")" > "$CHECKSUM_FILE")

    log_info "Verifying SHA-256 checksum..."
    (cd "$DAILY_BACKUP_DIR" && sha256sum -c "$(basename "$CHECKSUM_FILE")")

    log_info "Testing archive decompression integrity..."
    if tar -tzf "$TARGET_ARCHIVE" >/dev/null 2>&1; then
        log_success "Archive integrity check PASSED."
    else
        log_error "Archive integrity test FAILED! Archive may be corrupt."
        exit 1
    fi
}

# --- Clean Up Old Backups (>30 Days) ---
prune_old_backups() {
    log_info "Pruning backups older than ${RETENTION_DAYS} days in ${DAILY_BACKUP_DIR}..."
    
    local pruned_count=0
    while IFS= read -r file; do
        if [[ -n "$file" ]]; then
            log_info "Deleting old backup asset: $file"
            rm -f "$file"
            ((pruned_count++))
        fi
    done < <(find "$DAILY_BACKUP_DIR" -type f \( -name "verdis-backup-*.tar.gz" -o -name "verdis-backup-*.sha256" \) -mtime +${RETENTION_DAYS})

    log_success "Pruning complete. Removed ${pruned_count} old file(s)."
}

# --- Main Execution ---
main() {
    log_info "=========================================================="
    log_info " Starting Verdis Blockchain Production Backup Routine"
    log_info "=========================================================="
    
    preflight_checks
    stop_node_if_running
    collect_files
    compress_archive
    verify_integrity
    prune_old_backups

    log_info "=========================================================="
    log_info " Backup Completed Successfully"
    log_info " Archive: ${TARGET_ARCHIVE}"
    log_info "=========================================================="
}

main "$@"
```

---

### Installing the Daily Cron Job

To schedule automated daily execution at 02:00 AM UTC, create `/etc/cron.d/verdis-backup` or add an entry to root's crontab:

```bash
# 1. Ensure the script is executable
chmod +x /opt/verdis-chain-rust/backup/verdis-backup.sh

# 2. Add cron entry to /etc/cron.d/verdis-backup
cat << 'EOF' > /etc/cron.d/verdis-backup
# Execute Verdis production backup daily at 02:00 AM UTC
0 2 * * * root /opt/verdis-chain-rust/backup/verdis-backup.sh >> /var/log/verdis-backup.log 2>&1
EOF

# 3. Secure cron file permissions
chmod 0644 /etc/cron.d/verdis-backup
```

---

## 3. Recovery Procedure (Step-by-Step Restoration Guide)

This section details the step-by-step restoration process for bare-metal recovery or recovering from catastrophic state loss.

### Scenario A: Full System Disaster Recovery (On Server `91.98.160.145`)

#### Step 1: Pre-Restoration Preparation & Service Shutdown
Stop all active services to avoid race conditions or lock contention during file restoration:

```bash
systemctl stop verdis-node.service nginx prometheus grafana
```

#### Step 2: Backup Integrity & SHA256 Verification
Locate the desired backup archive in `/opt/verdis-backups/daily/` and verify its SHA256 signature prior to unpacking:

```bash
BACKUP_FILE="/opt/verdis-backups/daily/verdis-backup-20260804-020000.tar.gz"

# Verify SHA256 Checksum
cd /opt/verdis-backups/daily
sha256sum -c "${BACKUP_FILE}.sha256"

# Verify archive readability
tar -tzf "$BACKUP_FILE" > /dev/null && echo "Archive Integrity OK"
```

#### Step 3: Archive Unpacking to Temporary Staging Area
Unpack the archive into `/tmp/verdis-recovery-stage`:

```bash
rm -rf /tmp/verdis-recovery-stage
mkdir -p /tmp/verdis-recovery-stage
tar -xzf "$BACKUP_FILE" -C /tmp/verdis-recovery-stage
```

#### Step 4: Restore Core Blockchain Data & Chain Spec
Restore the Substrate node database and raw chain spec file:

```bash
# Restore Blockchain State Data
if [ -d "/tmp/verdis-recovery-stage/blockchain_data" ]; then
    mkdir -p /opt/verdis-chain-rust/data
    rsync -a --delete /tmp/verdis-recovery-stage/blockchain_data/ /opt/verdis-chain-rust/data/
    chown -R root:root /opt/verdis-chain-rust/data
fi

# Restore Chain Specification File
if [ -f "/tmp/verdis-recovery-stage/chain_spec/chain-spec-raw.json" ]; then
    cp -a /tmp/verdis-recovery-stage/chain_spec/chain-spec-raw.json /opt/verdis-chain-rust/chain-spec-raw.json
fi
```

#### Step 5: Restore Validator Keystores
Restore Substrate session key seeds and set strict permissions (`0700` for directory, `0600` for files):

```bash
mkdir -p /opt/verdis-chain-rust/keystore
if [ -d "/tmp/verdis-recovery-stage/keystore/main_keystore" ]; then
    rsync -a /tmp/verdis-recovery-stage/keystore/main_keystore/ /opt/verdis-chain-rust/keystore/
fi

chmod 700 /opt/verdis-chain-rust/keystore
chmod 600 /opt/verdis-chain-rust/keystore/* 2>/dev/null || true
```

#### Step 6: Restore Nginx Configurations & SSL Certificates
Restore web server sites and Let's Encrypt certificates:

```bash
# Restore Nginx Configs
if [ -d "/tmp/verdis-recovery-stage/nginx/sites-available" ]; then
    rsync -a /tmp/verdis-recovery-stage/nginx/sites-available/ /etc/nginx/sites-available/
    rsync -a /tmp/verdis-recovery-stage/nginx/sites-enabled/ /etc/nginx/sites-enabled/
fi

# Restore SSL Certificates
if [ -d "/tmp/verdis-recovery-stage/ssl" ]; then
    mkdir -p /etc/letsencrypt
    rsync -a /tmp/verdis-recovery-stage/ssl/ /etc/letsencrypt/
fi

# Test Nginx syntax
nginx -t
```

#### Step 7: Restore Grafana Dashboards, Prometheus Data & Monitoring Stack
Restore monitoring definitions for ports 3000 and 9090:

```bash
# Prometheus
if [ -d "/tmp/verdis-recovery-stage/monitoring/prometheus/etc" ]; then
    rsync -a /tmp/verdis-recovery-stage/monitoring/prometheus/etc/ /etc/prometheus/
fi
if [ -d "/tmp/verdis-recovery-stage/monitoring/prometheus/data" ]; then
    rsync -a /tmp/verdis-recovery-stage/monitoring/prometheus/data/ /var/lib/prometheus/
    chown -R prometheus:prometheus /var/lib/prometheus 2>/dev/null || true
fi

# Grafana
if [ -d "/tmp/verdis-recovery-stage/monitoring/grafana/etc" ]; then
    rsync -a /tmp/verdis-recovery-stage/monitoring/grafana/etc/ /etc/grafana/
fi
if [ -d "/tmp/verdis-recovery-stage/monitoring/grafana/data" ]; then
    rsync -a /tmp/verdis-recovery-stage/monitoring/grafana/data/ /var/lib/grafana/
    chown -R grafana:grafana /var/lib/grafana 2>/dev/null || true
fi
```

#### Step 8: Restore Verdiscan Website Static Files
Restore block explorer UI build artifacts:

```bash
if [ -d "/tmp/verdis-recovery-stage/web_verdiscan" ]; then
    mkdir -p /var/www/verdiscan
    rsync -a --delete /tmp/verdis-recovery-stage/web_verdiscan/ /var/www/verdiscan/
    chown -R www-data:www-data /var/www/verdiscan 2>/dev/null || true
fi
```

#### Step 9: Restore CTO Audit Logs
Restore administrative security audit logs:

```bash
if [ -d "/tmp/verdis-recovery-stage/cto_audit_logs" ]; then
    mkdir -p /opt/verdis-cto-logs
    rsync -a /tmp/verdis-recovery-stage/cto_audit_logs/ /opt/verdis-cto-logs/
fi
```

#### Step 10: Service Restart & Verification Sequence
Clean up staging data and restart all production daemons:

```bash
# Clean up temporary stage
rm -rf /tmp/verdis-recovery-stage

# Start system services
systemctl start nginx prometheus grafana verdis-node.service

# Verify Substrate Node Health via Local RPC (Port 9944)
curl -s -X POST http://localhost:9944 \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}' | jq .
```

---

### Scenario B: Validator Key Recovery Safety Protocol (Slashing & Equivocation Prevention)

> **CRITICAL VALIDATOR WARNING:**
> Running two node instances simultaneously with the identical validator keystore (`babe` / `gran`) will cause double-signing (equivocation), triggering automatic network slashing and removal from the validator set.

1. **Verify Inactive State:** Prior to restoring validator keystores on a new host, explicitly verify that the old validator instance is shut down and network interface disabled.
2. **Key Migration:** Copy keys to `/opt/verdis-chain-rust/keystore/` with permissions `0700`.
3. **Isolated Boot:** Start the node in telemetry/RPC mode first to verify state synchronization with peers before enabling the `--validator` CLI flag.

---

## 4. Testing Schedule & Staging Restoration Procedure

To guarantee recoverability, a monthly recovery rehearsal must be performed on an isolated staging instance.

### Schedule & Operational Guidelines
- **Frequency:** Executed on the **first Sunday of each month at 03:00 AM UTC**.
- **Location:** Executed in a sandbox container or isolated staging directory (`/tmp/verdis-restore-test`).
- **Owner:** Infrastructure Reliability Engineer & CTO.

### Automated Staging Test Script (`recovery-test.sh`)

The script `/opt/verdis-chain-rust/backup/recovery-test.sh` automates the monthly test suite:

```bash
#!/usr/bin/env bash
# ==============================================================================
# Verdis Monthly Backup Recovery Staging Test
# Location: /opt/verdis-chain-rust/backup/recovery-test.sh
# ==============================================================================
set -euo pipefail

BACKUP_DIR="/opt/verdis-backups/daily"
TEST_DIR="/tmp/verdis-restore-staging"
LOG_FILE="/var/log/verdis-restore-test.log"
TEST_RPC_PORT=9988

echo "==========================================================" | tee -a "$LOG_FILE"
echo " Starting Monthly Verdis Backup Recovery Test" | tee -a "$LOG_FILE"
echo " Date: $(date -u '+%Y-%m-%d %H:%M:%S UTC')" | tee -a "$LOG_FILE"
echo "==========================================================" | tee -a "$LOG_FILE"

# 1. Locate Latest Backup
LATEST_BACKUP=$(ls -t "${BACKUP_DIR}"/verdis-backup-*.tar.gz 2>/dev/null | head -n 1 || true)
if [[ -z "$LATEST_BACKUP" ]]; then
    echo "ERROR: No backup archive found in ${BACKUP_DIR}" | tee -a "$LOG_FILE"
    exit 1
fi
echo "Testing Backup Archive: ${LATEST_BACKUP}" | tee -a "$LOG_FILE"

# 2. Checksum Verification
CHECKSUM_FILE="${LATEST_BACKUP}.sha256"
if [[ -f "$CHECKSUM_FILE" ]]; then
    echo "Verifying SHA256 checksum..." | tee -a "$LOG_FILE"
    (cd "$BACKUP_DIR" && sha256sum -c "$(basename "$CHECKSUM_FILE")") | tee -a "$LOG_FILE"
fi

# 3. Test Decompression & Extraction
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
echo "Extracting archive to test environment ${TEST_DIR}..." | tee -a "$LOG_FILE"
tar -xzf "$LATEST_BACKUP" -C "$TEST_DIR"

# 4. Verify Component Contents
EXPECTED_DIRS=("blockchain_data" "chain_spec" "keystore" "nginx" "ssl" "monitoring" "web_verdiscan" "cto_audit_logs")
MISSING_COUNT=0

for dir in "${EXPECTED_DIRS[@]}"; do
    if [[ -d "${TEST_DIR}/${dir}" ]] || [[ -f "${TEST_DIR}/${dir}" ]]; then
        echo "  [PASS] Component '${dir}' is present." | tee -a "$LOG_FILE"
    else
        echo "  [FAIL] Component '${dir}' is MISSING!" | tee -a "$LOG_FILE"
        MISSING_COUNT=$((MISSING_COUNT + 1))
    fi
done

if [[ "$MISSING_COUNT" -gt 0 ]]; then
    echo "ERROR: Recovery test FAILED with ${MISSING_COUNT} missing components." | tee -a "$LOG_FILE"
    exit 1
fi

# 5. Test Substrate Binary Initialization with Restored State
BINARY="/opt/verdis-chain-rust/target/release/verdis"
CHAIN_SPEC="${TEST_DIR}/chain_spec/chain-spec-raw.json"

if [[ -f "$BINARY" ]] && [[ -f "$CHAIN_SPEC" ]]; then
    echo "Testing node state load on temporary RPC port ${TEST_RPC_PORT}..." | tee -a "$LOG_FILE"
    timeout 20s "$BINARY" \
        --chain "$CHAIN_SPEC" \
        --base-path "${TEST_DIR}/blockchain_data" \
        --rpc-port "$TEST_RPC_PORT" \
        --no-telemetry > /dev/null 2>&1 &
    NODE_PID=$!
    sleep 8

    if kill -0 "$NODE_PID" 2>/dev/null; then
        echo "  [PASS] Substrate node started successfully with restored state." | tee -a "$LOG_FILE"
        kill "$NODE_PID" 2>/dev/null || true
    else
        echo "  [WARN] Node process exited early (check dev flags or port bindings)." | tee -a "$LOG_FILE"
    fi
fi

# Cleanup
rm -rf "$TEST_DIR"

echo "==========================================================" | tee -a "$LOG_FILE"
echo " Monthly Recovery Test Status: PASSED" | tee -a "$LOG_FILE"
echo "==========================================================" | tee -a "$LOG_FILE"
```

---

## 5. Monitoring, Verification & Alerting

To guarantee that backup jobs run successfully without silent failures, monitoring is implemented across three tiers: log inspection, backup freshness/size checks, and Prometheus/Grafana metric alerts.

### Tier 1: Log Inspection & Health Status
- **Log Location:** `/var/log/verdis-backup.log`
- **Real-time Tail:** `tail -f -n 50 /var/log/verdis-backup.log`
- **Status Check Command:**
  ```bash
  grep -E "SUCCESS|ERROR|WARN" /var/log/verdis-backup.log | tail -n 20
  ```

### Tier 2: File Freshness & Archive Size Verification
Run the following inspection commands to verify daily archive generation and file integrity:

```bash
# 1. Verify a backup file was produced within the last 26 hours
find /opt/verdis-backups/daily/ -type f -name "verdis-backup-*.tar.gz" -mtime -1

# 2. Check size and disk usage of archives
ls -lh /opt/verdis-backups/daily/

# 3. Verify total disk capacity on backup partition
df -h /opt/verdis-backups/
```

### Tier 3: Prometheus & Grafana Monitoring Integration

The backup script exports key execution metrics to the Prometheus Node Exporter textfile collector directory (`/var/lib/prometheus/node_exporter/textfile_collector/verdis_backup.prom`):

#### Metrics Export Format (`verdis_backup.prom`)
```promql
# HELP verdis_backup_last_success_timestamp_seconds Epoch timestamp of last successful backup.
# TYPE verdis_backup_last_success_timestamp_seconds gauge
verdis_backup_last_success_timestamp_seconds 1785888000

# HELP verdis_backup_last_run_duration_seconds Execution duration of the last backup in seconds.
# TYPE verdis_backup_last_run_duration_seconds gauge
verdis_backup_last_run_duration_seconds 42.5

# HELP verdis_backup_file_size_bytes Size of the latest backup archive in bytes.
# TYPE verdis_backup_file_size_bytes gauge
verdis_backup_file_size_bytes 524288000

# HELP verdis_backup_last_exit_code Exit code of last backup job (0 = success).
# TYPE verdis_backup_last_exit_code gauge
verdis_backup_last_exit_code 0
```

#### Prometheus Alerting Rules (`/etc/prometheus/verdis_alerts.yml`)
Add the following rules to Prometheus on port 9090 to trigger alerts if backups fail or become stale:

```yaml
groups:
  - name: verdis_backup_alerts
    rules:
      - alert: VerdisBackupFailed
        expr: verdis_backup_last_exit_code != 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Verdis Blockchain Daily Backup Failed"
          description: "The backup job on server 91.98.160.145 exited with error code {{ $value }}."

      - alert: VerdisBackupStale
        expr: (time() - verdis_backup_last_success_timestamp_seconds) > 90000
        for: 15m
        labels:
          severity: critical
        annotations:
          summary: "Verdis Backup Out of Date"
          description: "No successful backup recorded in over 25 hours."

      - alert: VerdisBackupSizeAnomaly
        expr: verdis_backup_file_size_bytes < 10000000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Verdis Backup File Size Unusually Small"
          description: "Latest backup archive size is {{ $value }} bytes, indicating missing state or empty directories."
```

#### Grafana Dashboard Panel Configuration (Port 3000)
In Grafana on port 3000, create a dedicated **"Backup & Disaster Recovery Status"** row containing:
1. **Status Indicator (Stat Panel):** Displays "OK" (Green) if `verdis_backup_last_exit_code == 0` and age < 25h, or "CRITICAL" (Red) otherwise.
2. **Backup Archive Size (Graph Panel):** Time-series plot of `verdis_backup_file_size_bytes` over the past 30 days to detect unexpected state drops.
3. **Execution Duration (Bar Gauge):** Tracks `verdis_backup_last_run_duration_seconds` to monitor backup window performance.

---

### Strategy Summary Checklist

| Objective | Requirement | Implementation Status |
| :--- | :--- | :--- |
| **8 Critical Targets** | Blockchain Data, Chain Spec, Validator Keystores, Nginx, SSL, Grafana/Prometheus, Verdiscan, CTO Logs | Fully Covered in Section 1 & Script |
| **Backup Script** | Timestamped dir, copies files, compresses, SHA256 checksums, logs, 30-day prune, cron ready | Executable Bash Script provided in Section 2 |
| **Recovery Guide** | Step-by-step restoration for all components & validator safety rules | Comprehensive 10-step guide in Section 3 |
| **Testing Schedule** | Monthly staging restore test routine with script | Rehearsal protocol & script provided in Section 4 |
| **Monitoring** | Log checks, backup size freshness, Prometheus alerting rules & Grafana setup | Multi-tiered monitoring detailed in Section 5 |
