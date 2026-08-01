"use strict";
/**
 * Verdis Account Abstraction — Smart Wallets by Default
 * 
 * Native account abstraction allowing:
 * - Social recovery (no seed phrases needed)
 * - Multi-signature controls
 * - Gas sponsorship from dApps
 * - Session keys for dApp interactions
 * - Daily spending limits
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.AccountAbstraction = void 0;
const crypto_2 = require("../crypto");
class AccountAbstraction {
    constructor() {
        this.smartWallets = new Map();     // address -> SmartWallet
        this.sessionKeys = new Map();       // sessionKey -> Session
        this.recoveryRequests = new Map(); // address -> RecoveryRequest
    }
    /**
     * Create a smart wallet with advanced features
     */
    createSmartWallet(ownerAddress, config) {
        const wallet = {
            address: ownerAddress,
            owners: [ownerAddress],
            threshold: config?.threshold || 1,
            guardians: config?.guardians || [],
            guardianThreshold: config?.guardianThreshold || 2,
            dailyLimit: config?.dailyLimit || 100000,
            spentToday: 0,
            spendResetAt: this.nextDayReset(),
            sessionKeys: [],
            allowedContracts: config?.allowedContracts || ['*'],
            socialRecoveryEnabled: config?.socialRecovery !== false,
            createdAt: Date.now(),
            lastUsedAt: 0,
        };
        this.smartWallets.set(ownerAddress, wallet);
        return { success: true, wallet };
    }
    /**
     * Add a guardian for social recovery
     */
    addGuardian(walletAddress, ownerAddress, guardianAddress) {
        const wallet = this.smartWallets.get(walletAddress);
        if (!wallet) return { success: false, error: "Smart wallet not found" };
        if (!wallet.owners.includes(ownerAddress)) return { success: false, error: "Not a wallet owner" };
        if (wallet.guardians.includes(guardianAddress)) return { success: false, error: "Already a guardian" };
        wallet.guardians.push(guardianAddress);
        this.smartWallets.set(walletAddress, wallet);
        return { success: true, guardians: wallet.guardians };
    }
    /**
     * Initiate social recovery (guardians can recover wallet for owner)
     */
    initiateRecovery(walletAddress, newOwnerAddress) {
        const wallet = this.smartWallets.get(walletAddress);
        if (!wallet) return { success: false, error: "Smart wallet not found" };
        if (!wallet.socialRecoveryEnabled) return { success: false, error: "Social recovery disabled" };
        const request = {
            walletAddress,
            newOwnerAddress,
            approvals: new Set(),
            initiatedAt: Date.now(),
            expiresAt: Date.now() + (24 * 60 * 60 * 1000), // 24h to collect approvals
            completed: false,
        };
        this.recoveryRequests.set(walletAddress, request);
        return { success: true, message: `Recovery initiated. Needs ${wallet.guardianThreshold} guardian approvals.` };
    }
    /**
     * Guardian approves recovery
     */
    approveRecovery(walletAddress, guardianAddress) {
        const request = this.recoveryRequests.get(walletAddress);
        if (!request) return { success: false, error: "No recovery request found" };
        if (request.completed) return { success: false, error: "Recovery already completed" };
        if (Date.now() > request.expiresAt) return { success: false, error: "Recovery request expired" };
        const wallet = this.smartWallets.get(walletAddress);
        if (!wallet) return { success: false, error: "Smart wallet not found" };
        if (!wallet.guardians.includes(guardianAddress)) {
            return { success: false, error: "Not a guardian" };
        }
        request.approvals.add(guardianAddress);
        // Check if threshold met
        if (request.approvals.size >= wallet.guardianThreshold) {
            wallet.owners.push(request.newOwnerAddress);
            request.completed = true;
            this.smartWallets.set(walletAddress, wallet);
            this.recoveryRequests.set(walletAddress, request);
            return { success: true, completed: true, message: "Recovery completed — new owner added" };
        }
        return {
            success: true,
            completed: false,
            approvals: request.approvals.size,
            needed: wallet.guardianThreshold,
        };
    }
    /**
     * Create a session key for dApp interaction
     */
    createSessionKey(walletAddress, ownerAddress, dappContract, permissions, expiryMinutes) {
        const wallet = this.smartWallets.get(walletAddress);
        if (!wallet) return { success: false, error: "Smart wallet not found" };
        if (!wallet.owners.includes(ownerAddress)) return { success: false, error: "Not a wallet owner" };
        // Generate a session key
        const { privateKey, publicKey } = (0, crypto_2.generateKeyPair)();
        const sessionAddress = (0, crypto_2.getAddressFromPublicKey)(publicKey);
        const session = {
            sessionAddress,
            sessionPrivateKey: privateKey,
            walletAddress,
            dappContract,
            permissions: permissions || ['read', 'execute'],
            maxSpend: 10000,
            spent: 0,
            createdAt: Date.now(),
            expiresAt: Date.now() + (expiryMinutes || 60) * 60 * 1000,
            active: true,
        };
        wallet.sessionKeys.push(sessionAddress);
        this.smartWallets.set(walletAddress, wallet);
        this.sessionKeys.set(sessionAddress, session);
        return { success: true, session };
    }
    /**
     * Validate a session key action
     */
    validateSessionAction(sessionAddress, contractId, operation, amount) {
        const session = this.sessionKeys.get(sessionAddress);
        if (!session) return { allowed: false, error: "Session not found" };
        if (!session.active) return { allowed: false, error: "Session inactive" };
        if (Date.now() > session.expiresAt) {
            session.active = false;
            this.sessionKeys.set(sessionAddress, session);
            return { allowed: false, error: "Session expired" };
        }
        if (session.dappContract !== contractId && session.dappContract !== '*') {
            return { allowed: false, error: "Contract not in session scope" };
        }
        if (!session.permissions.includes(operation) && !session.permissions.includes('*')) {
            return { allowed: false, error: `Operation '${operation}' not permitted" };
        }
        if (session.spent + amount > session.maxSpend) {
            return { allowed: false, error: "Session spend limit exceeded" };
        }
        session.spent += amount;
        this.sessionKeys.set(sessionAddress, session);
        return { allowed: true };
    }
    /**
     * Revoke a session key
     */
    revokeSessionKey(sessionAddress, ownerAddress) {
        const session = this.sessionKeys.get(sessionAddress);
        if (!session) return { success: false, error: "Session not found" };
        const wallet = this.smartWallets.get(session.walletAddress);
        if (wallet && !wallet.owners.includes(ownerAddress)) {
            return { success: false, error: "Not a wallet owner" };
        }
        session.active = false;
        this.sessionKeys.set(sessionAddress, session);
        return { success: true };
    }
    /**
     * Check daily spend limit for a smart wallet
     */
    checkSpendLimit(walletAddress, amount) {
        const wallet = this.smartWallets.get(walletAddress);
        if (!wallet) return { allowed: true }; // Not a smart wallet, no limit
        // Reset daily spend if new day
        if (Date.now() > wallet.spendResetAt) {
            wallet.spentToday = 0;
            wallet.spendResetAt = this.nextDayReset();
        }
        if (wallet.spentToday + amount > wallet.dailyLimit) {
            return {
                allowed: false,
                error: `Daily limit exceeded: ${wallet.spentToday}/${wallet.dailyLimit} VRS`,
                spent: wallet.spentToday,
                limit: wallet.dailyLimit,
            };
        }
        wallet.spentToday += amount;
        wallet.lastUsedAt = Date.now();
        this.smartWallets.set(walletAddress, wallet);
        return { allowed: true, spent: wallet.spentToday, limit: wallet.dailyLimit };
    }
    nextDayReset() {
        const d = new Date();
        d.setHours(24, 0, 0, 0);
        return d.getTime();
    }
    getSmartWallet(address) {
        return this.smartWallets.get(address);
    }
    getAllSmartWallets() {
        return Array.from(this.smartWallets.values());
    }
    getActiveSessions() {
        return Array.from(this.sessionKeys.values()).filter(s => s.active && Date.now() < s.expiresAt);
    }
    getStats() {
        return {
            totalSmartWallets: this.smartWallets.size,
            activeSessions: this.getActiveSessions().length,
            pendingRecoveries: Array.from(this.recoveryRequests.values()).filter(r => !r.completed && Date.now() < r.expiresAt).length,
            totalGuardians: Array.from(this.smartWallets.values()).reduce((s, w) => s + w.guardians.length, 0),
        };
    }
    exportState() {
        return {
            smartWallets: Array.from(this.smartWallets.entries()),
            sessionKeys: Array.from(this.sessionKeys.entries()),
            recoveryRequests: Array.from(this.recoveryRequests.entries()),
        };
    }
    importState(state) {
        if (state.smartWallets) this.smartWallets = new Map(state.smartWallets);
        if (state.sessionKeys) this.sessionKeys = new Map(state.sessionKeys);
        if (state.recoveryRequests) {
            const entries = state.recoveryRequests;
            for (const [key, val] of entries) {
                if (val.approvals && Array.isArray(val.approvals)) {
                    val.approvals = new Set(val.approvals);
                }
                this.recoveryRequests.set(key, val);
            }
        }
    }
}
exports.AccountAbstraction = AccountAbstraction;
