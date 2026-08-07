# Verdis Backup & Disaster Recovery

Complete backup and recovery system for the Verdis blockchain.

## Overview

| Backup Type | Frequency | Retention | Contents |
|-------------|-----------|-----------|----------|
| Full backup | Daily (2 AM) | 7 daily, 4 weekly, 12 monthly | Chain DB, keys, config, nginx, SSL |
| Config backup | Hourly | 24 hours | Config files only |
| Key backup | Weekly | 5 backups | Encrypted keystore (GPG) |

## Files

| Script | Purpose |
|--------|---------|
| `verdis-backup.sh` | Full daily backup (stops node, snapshots, restarts) |
| `verdis-restore.sh` | Full restore from backup archive |
| `verdis-config-backup.sh` | Lightweight config-only backup (hourly) |
| `verdis-key-backup.sh` | Encrypted key backup (GPG) |
| `verify-backup.sh` | Verify backup archive integrity and contents |
| `recovery-test.sh` | Test restore to temp directory and verify |
| `backup-cron.sh` | Install cron schedules for all backups |

## Quick Start

```bash
# Install cron schedules
./backup-cron.sh

# Manual full backup
./verdis-backup.sh

# Restore from backup
./verdis-restore.sh /opt/verdis-backups/verdis-full-20260803.tar.gz

# Verify a backup
./verify-backup.sh /opt/verdis-backups/verdis-full-20260803.tar.gz

# Test recovery
./recovery-test.sh

# Encrypted key backup
./verdis-key-backup.sh admin@verdischain.com
```

## Backup Contents

### Full Backup
- Chain database (RocksDB snapshot)
- Keystore (BABE, GRANDPA, session keys)
- Chain specification
- Nginx configuration
- SSL certificates (Let's Encrypt)
- Systemd service files
- Logrotate configuration
- Monitoring configs (if present)

### Config Backup
- Nginx config
- Systemd services
- Chain spec
- Logrotate config

### Key Backup
- Encrypted keystore (GPG)
- Node keys (libp2p)

## Backup Location

Default: `/opt/verdis-backups/`
```
/opt/verdis-backups/
├── full/
│   ├── verdis-full-20260803.tar.gz
│   ├── verdis-full-20260803.sha256
│   └── ...
├── config/
│   ├── verdis-config-20260803-0200.tar.gz
│   └── ...
├── keys/
│   ├── verdis-keys-20260803.gpg
│   └── ...
└── logs/
    └── verdis-backup.log
```

## Recovery Procedure

### Full Recovery
1. Stop the node: `systemctl stop verdis-node`
2. Run restore: `./verdis-restore.sh /path/to/backup.tar.gz`
3. Verify: `./verify-backup.sh /path/to/backup.tar.gz`
4. Start node: `systemctl start verdis-node`
5. Check sync: `curl -X POST http://localhost:9944 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}'`

### Emergency Recovery (New Server)
1. Install Rust and build binary
2. Transfer backup archive to new server
3. Run restore script
4. Configure firewall and nginx
5. Start node and verify sync

## Testing

Run the recovery test regularly:
```bash
./recovery-test.sh
```

This creates a temporary restore, verifies contents, and tests node startup.

## Logs

Backup logs: `/var/log/verdis-backup.log`
```bash
tail -f /var/log/verdis-backup.log
```
