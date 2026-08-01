"use strict";
/**
 * Verdis Fraud Detection System
 * 
 * Real-time on-chain fraud and anomaly detection.
 * Monitors all transactions for suspicious patterns.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.FraudDetection = void 0;
class FraudDetection {
    constructor() {
        this.txHistory = new Map();    // address -> recent transactions
        this.alerts = [];
        this.blacklistedAddresses = new Set();
        this.whitelistedAddresses = new Set();
        this.rules = {
            velocityThreshold: 30,       // max txs per minute
            amountSpikeMultiplier: 10,   // tx > 10x average
            largeTxThreshold: 1000000,  // > 1M VRS in single tx
            newAccountThreshold: 1000,  // large tx from account < 1 min old
            rapidOutflowMultiplier: 5,  // outflow > 5x inflow in 10 min
            duplicateTxThreshold: 5,    // same amount+recipient > 5 times
        };
    }
    /**
     * Analyze a transaction before it's included in a block.
     * Returns risk assessment with score 0-100.
     */
    analyzeTransaction(tx) {
        const risk = { score: 0, alerts: [], recommendation: 'allow' };
        const now = Date.now();
        let history = this.txHistory.get(tx.from) || [];
        history.push({ to: tx.to, amount: tx.amount, fee: tx.fee, timestamp: now });
        // Keep last 200 transactions
        if (history.length > 200) history = history.slice(-200);
        this.txHistory.set(tx.from, history);
        // Rule 1: Velocity check
        const lastMinute = history.filter(t => now - t.timestamp < 60000);
        if (lastMinute.length > this.rules.velocityThreshold) {
            risk.score += 30;
            risk.alerts.push({
                type: 'high_velocity',
                severity: 'high',
                message: `${lastMinute.length} transactions in 1 minute (threshold: ${this.rules.velocityThreshold})`,
            });
        }
        // Rule 2: Amount spike
        if (history.length > 5) {
            const recent = history.slice(-6, -1);
            const avgAmount = recent.reduce((s, t) => s + t.amount, 0) / recent.length;
            if (tx.amount > avgAmount * this.rules.amountSpikeMultiplier && avgAmount > 0) {
                risk.score += 25;
                risk.alerts.push({
                    type: 'amount_spike',
                    severity: 'medium',
                    message: `Amount ${tx.amount} is ${this.rules.amountSpikeMultiplier}x average of ${avgAmount.toFixed(2)}`,
                });
            }
        }
        // Rule 3: Large transaction
        if (tx.amount > this.rules.largeTxThreshold) {
            risk.score += 20;
            risk.alerts.push({
                type: 'large_transaction',
                severity: 'medium',
                message: `Large transaction: ${tx.amount} VRS (threshold: ${this.rules.largeTxThreshold})`,
            });
        }
        // Rule 4: Duplicate transactions (same recipient + amount)
        if (history.length > 3) {
            const duplicates = history.filter(t => t.to === tx.to && t.amount === tx.amount);
            if (duplicates.length > this.rules.duplicateTxThreshold) {
                risk.score += 20;
                risk.alerts.push({
                    type: 'duplicate_pattern',
                    severity: 'medium',
                    message: `${duplicates.length} identical transactions to ${tx.to.slice(0, 12)}...`,
                });
            }
        }
        // Rule 5: Rapid outflow
        const last10Min = history.filter(t => now - t.timestamp < 600000);
        const outflow = last10Min.reduce((s, t) => s + t.amount, 0);
        if (outflow > tx.amount * this.rules.rapidOutflowMultiplier && outflow > 50000) {
            risk.score += 15;
            risk.alerts.push({
                type: 'rapid_outflow',
                severity: 'low',
                message: `Rapid outflow: ${outflow} VRS in 10 minutes`,
            });
        }
        // Rule 6: Blacklisted address
        if (this.blacklistedAddresses.has(tx.from) || this.blacklistedAddresses.has(tx.to)) {
            risk.score = 100;
            risk.alerts.push({
                type: 'blacklisted_address',
                severity: 'critical',
                message: `Transaction involves blacklisted address`,
            });
        }
        // Whitelisted addresses get reduced scrutiny
        if (this.whitelistedAddresses.has(tx.from)) {
            risk.score = Math.floor(risk.score * 0.3);
        }
        // Determine recommendation
        if (risk.score >= 80) risk.recommendation = 'block';
        else if (risk.score >= 50) risk.recommendation = 'flag';
        else if (risk.score >= 25) risk.recommendation = 'monitor';
        else risk.recommendation = 'allow';
        // Record alerts
        if (risk.alerts.length > 0) {
            this.alerts.push({ tx, risk, timestamp: now });
            if (this.alerts.length > 1000) this.alerts = this.alerts.slice(-1000);
        }
        return risk;
    }
    /**
     * Blacklist an address (admin only)
     */
    blacklist(address, reason) {
        this.blacklistedAddresses.add(address);
        this.alerts.push({
            type: 'blacklist_added',
            severity: 'critical',
            message: `Address ${address.slice(0, 16)}... blacklisted: ${reason}`,
            timestamp: Date.now(),
        });
    }
    /**
     * Whitelist an address (trusted validators, contracts)
     */
    whitelist(address) {
        this.whitelistedAddresses.add(address);
    }
    removeFromBlacklist(address) {
        this.blacklistedAddresses.delete(address);
    }
    isBlacklisted(address) {
        return this.blacklistedAddresses.has(address);
    }
    getAlerts(limit = 50) {
        return this.alerts.slice(-limit).reverse();
    }
    getStats() {
        return {
            totalAlerts: this.alerts.length,
            blacklistedAddresses: this.blacklistedAddresses.size,
            whitelistedAddresses: this.whitelistedAddresses.size,
            monitoredAddresses: this.txHistory.size,
            alertsBySeverity: {
                critical: this.alerts.filter(a => a.severity === 'critical').length,
                high: this.alerts.filter(a => a.severity === 'high').length,
                medium: this.alerts.filter(a => a.severity === 'medium').length,
                low: this.alerts.filter(a => a.severity === 'low').length,
            },
        };
    }
    exportState() {
        return {
            txHistory: Array.from(this.txHistory.entries()),
            alerts: this.alerts,
            blacklistedAddresses: Array.from(this.blacklistedAddresses),
            whitelistedAddresses: Array.from(this.whitelistedAddresses),
        };
    }
    importState(state) {
        if (state.txHistory) this.txHistory = new Map(state.txHistory);
        if (state.alerts) this.alerts = state.alerts;
        if (state.blacklistedAddresses) this.blacklistedAddresses = new Set(state.blacklistedAddresses);
        if (state.whitelistedAddresses) this.whitelistedAddresses = new Set(state.whitelistedAddresses);
    }
}
exports.FraudDetection = FraudDetection;
