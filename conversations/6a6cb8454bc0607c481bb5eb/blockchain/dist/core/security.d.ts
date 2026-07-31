/**
 * Verdis Security Layer
 * - Rate limiting
 * - API key authentication
 * - Replay protection (nonce tracking)
 * - Validator slashing conditions
 * - Input validation
 * - Security audit logging
 */
export interface RateLimitEntry {
    count: number;
    resetTime: number;
    blocked: boolean;
}
export interface SecurityEvent {
    timestamp: number;
    type: string;
    severity: 'info' | 'warning' | 'critical';
    message: string;
    ip?: string;
    address?: string;
}
export declare class SecurityManager {
    private rateLimits;
    private usedNonces;
    private securityEvents;
    private adminApiKey;
    private slashedValidators;
    private readonly RATE_LIMIT_WINDOW;
    private readonly RATE_LIMIT_MAX;
    private readonly RATE_LIMIT_STRICT;
    private readonly MAX_MEMPOOL_SIZE;
    private readonly MAX_TX_AMOUNT;
    private readonly MAX_BLOCK_SIZE;
    constructor(adminApiKey?: string);
    getAdminApiKey(): string;
    private generateApiKey;
    checkRateLimit(ip: string, strict?: boolean): {
        allowed: boolean;
        remaining: number;
        resetIn: number;
    };
    isNonceUsed(nonce: number): boolean;
    consumeNonce(nonce: number): boolean;
    verifyApiKey(key: string): boolean;
    slashValidator(address: string, reason: string): {
        slashed: boolean;
        penalty: number;
    };
    isValidatorSlashed(address: string): boolean;
    getSlashedValidators(): string[];
    validateAddress(address: string): boolean;
    validateAmount(amount: number): {
        valid: boolean;
        error?: string;
    };
    sanitizeInput(input: string): string;
    checkMempoolSize(currentSize: number): boolean;
    getMaxBlockSize(): number;
    logEvent(type: string, severity: 'info' | 'warning' | 'critical', message: string, ip?: string, address?: string): void;
    getSecurityEvents(limit?: number): SecurityEvent[];
    getAuditReport(): any;
}
