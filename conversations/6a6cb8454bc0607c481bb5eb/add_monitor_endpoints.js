#!/usr/bin/env node
/**
 * Add /api/monitor/alert endpoint to collect alerts from the monitoring daemon
 */

const fs = require('fs');
const SERVER_PATH = '/opt/verdis/app/dist/api/server.js';

let code = fs.readFileSync(SERVER_PATH, 'utf8');

if (code.includes('/api/monitor/alert')) {
  console.log('✅ Alert endpoint already exists — skipping');
  process.exit(0);
}

// Add alerts storage in constructor
const marker = 'this.startTime = Date.now();';
if (!code.includes(marker)) {
  console.error('❌ Cannot find constructor marker');
  process.exit(1);
}

code = code.replace(
  marker,
  marker + '\n        this.monitorAlerts = [];'
);

// Add POST endpoint for alerts + GET endpoint to retrieve them
// Insert before the static file catch-all
const staticMarker = "this.app.get('/:page'";

const alertEndpoints = `
        // Monitor alert ingestion
        this.app.post('/api/monitor/alert', (req, res) => {
            try {
                const alert = {
                    ...req.body,
                    receivedAt: new Date().toISOString()
                };
                this.monitorAlerts.push(alert);
                // Keep only last 100 alerts
                if (this.monitorAlerts.length > 100) {
                    this.monitorAlerts = this.monitorAlerts.slice(-100);
                }
                console.log('🚨 Monitor alert:', alert.severity, alert.message);
                res.json({ success: true, alertId: this.monitorAlerts.length });
            } catch (e) {
                res.status(500).json({ error: e.message });
            }
        });

        // Get recent alerts
        this.app.get('/api/monitor/alerts', (req, res) => {
            res.json({ 
                success: true, 
                alerts: this.monitorAlerts.slice(-20),
                totalAlerts: this.monitorAlerts.length
            });
        });

        // Combined monitoring endpoint — health + alerts + system status
        this.app.get('/api/monitor/status', (req, res) => {
            try {
                const chain = this.blockchain.getChain();
                const lastBlock = chain[chain.length - 1];
                const now = Date.now();
                const lastBlockTime = lastBlock ? lastBlock.header.timestamp : 0;
                const blockStaleness = now - lastBlockTime;
                const isHealthy = blockStaleness < 30000 && this.blockchain.isChainValid();
                
                res.json({
                    success: true,
                    status: isHealthy ? 'healthy' : 'unhealthy',
                    blockHeight: this.blockchain.getChainHeight(),
                    chainValid: this.blockchain.isChainValid(),
                    blockStalenessMs: blockStaleness,
                    lastBlockTime: lastBlockTime ? new Date(lastBlockTime).toISOString() : null,
                    mempoolSize: this.blockchain.getMempool().size(),
                    totalSupply: this.blockchain.getTokenSystem().getTotalSupply(),
                    validatorCount: this.blockchain.getConsensus().getAllValidatorsList().length,
                    uptime: Math.floor((now - this.startTime) / 1000),
                    recentAlerts: this.monitorAlerts.slice(-5),
                    unacknowledgedAlerts: this.monitorAlerts.filter(a => a.severity === 'CRITICAL').length
                });
            } catch (e) {
                res.status(500).json({ success: false, error: e.message });
            }
        });

`;

code = code.replace(staticMarker, alertEndpoints + staticMarker);

fs.writeFileSync(SERVER_PATH, code, 'utf8');
console.log('✅ Monitor alert endpoints added to server.js');
