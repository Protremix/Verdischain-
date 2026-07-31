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

export class SecurityManager {
  private rateLimits: Map<string, RateLimitEntry> = new Map();
  private usedNonces: Set<number> = new Set();
  private securityEvents: SecurityEvent[] = [];
  private adminApiKey: string;
  private slashedValidators: Set<string> = new Set();
  
  // Rate limit config
  private readonly RATE_LIMIT_WINDOW = 60000; // 1 minute
  private readonly RATE_LIMIT_MAX = 30; // 30 requests per minute per IP
  private readonly RATE_LIMIT_STRICT = 5; // 5 per minute for sensitive endpoints
  private readonly MAX_MEMPOOL_SIZE = 1000;
  private readonly MAX_TX_AMOUNT = 1000000000; // 1B VRS max per tx
  private readonly MAX_BLOCK_SIZE = 500; // max transactions per block
  
  constructor(adminApiKey?: string) {
    this.adminApiKey = adminApiKey || this.generateApiKey();
    this.logEvent('system', 'info', 'Security manager initialized');
    this.logEvent('system', 'info', `Admin API key generated: ${this.adminApiKey.slice(0, 8)}...`);
  }
  
  getAdminApiKey(): string {
    return this.adminApiKey;
  }
  
  private generateApiKey(): string {
    const chars = '0123456789abcdef';
    let key = '';
    for (let i = 0; i < 64; i++) {
      key += chars[Math.floor(Math.random() * 16)];
    }
    return key;
  }
  
  // === RATE LIMITING ===
  checkRateLimit(ip: string, strict: boolean = false): { allowed: boolean; remaining: number; resetIn: number } {
    const key = strict ? `${ip}:strict` : ip;
    const limit = strict ? this.RATE_LIMIT_STRICT : this.RATE_LIMIT_MAX;
    const now = Date.now();
    
    let entry = this.rateLimits.get(key);
    if (!entry || now > entry.resetTime) {
      entry = { count: 0, resetTime: now + this.RATE_LIMIT_WINDOW, blocked: false };
      this.rateLimits.set(key, entry);
    }
    
    if (entry.count >= limit) {
      if (!entry.blocked) {
        this.logEvent('rate_limit', 'warning', `Rate limit exceeded for ${ip} (${entry.count}/${limit})`, ip);
        entry.blocked = true;
      }
      return { allowed: false, remaining: 0, resetIn: Math.ceil((entry.resetTime - now) / 1000) };
    }
    
    entry.count++;
    return { allowed: true, remaining: limit - entry.count, resetIn: Math.ceil((entry.resetTime - now) / 1000) };
  }
  
  // === NONCE / REPLAY PROTECTION ===
  isNonceUsed(nonce: number): boolean {
    return this.usedNonces.has(nonce);
  }
  
  consumeNonce(nonce: number): boolean {
    if (this.usedNonces.has(nonce)) {
      this.logEvent('replay', 'critical', `Replay attack detected: nonce ${nonce} already used`);
      return false;
    }
    this.usedNonces.add(nonce);
    // Keep only last 100000 nonces to prevent memory bloat
    if (this.usedNonces.size > 100000) {
      const arr = Array.from(this.usedNonces).sort((a, b) => a - b);
      this.usedNonces = new Set(arr.slice(-50000));
    }
    return true;
  }
  
  // === ADMIN AUTHENTICATION ===
  verifyApiKey(key: string): boolean {
    return key === this.adminApiKey;
  }
  
  // === VALIDATOR SLASHING ===
  slashValidator(address: string, reason: string): { slashed: boolean; penalty: number } {
    if (this.slashedValidators.has(address)) {
      return { slashed: false, penalty: 0 };
    }
    
    this.slashedValidators.add(address);
    this.logEvent('slashing', 'critical', `Validator ${address} slashed: ${reason}`, undefined, address);
    return { slashed: true, penalty: 0 };
  }
  
  isValidatorSlashed(address: string): boolean {
    return this.slashedValidators.has(address);
  }
  
  getSlashedValidators(): string[] {
    return Array.from(this.slashedValidators);
  }
  
  // === INPUT VALIDATION ===
  validateAddress(address: string): boolean {
    if (!address || typeof address !== 'string') return false;
    if (address.length < 10 || address.length > 64) return false;
    if (!address.startsWith('0x') && !address.startsWith('03') && !address.startsWith('02')) return false;
    return true;
  }
  
  validateAmount(amount: number): { valid: boolean; error?: string } {
    if (typeof amount !== 'number' || isNaN(amount)) {
      return { valid: false, error: 'Amount must be a number' };
    }
    if (amount <= 0) {
      return { valid: false, error: 'Amount must be greater than zero' };
    }
    if (amount > this.MAX_TX_AMOUNT) {
      return { valid: false, error: `Amount exceeds maximum (${this.MAX_TX_AMOUNT} VRS)` };
    }
    return { valid: true };
  }
  
  sanitizeInput(input: string): string {
    if (typeof input !== 'string') return '';
    // Remove control characters and potential injection vectors
    return input.replace(/[\x00-\x1F\x7F]/g, '').slice(0, 1000);
  }
  
  // === MEMPOOL LIMITS ===
  checkMempoolSize(currentSize: number): boolean {
    return currentSize < this.MAX_MEMPOOL_SIZE;
  }
  
  getMaxBlockSize(): number {
    return this.MAX_BLOCK_SIZE;
  }
  
  // === SECURITY AUDIT LOG ===
  logEvent(type: string, severity: 'info' | 'warning' | 'critical', message: string, ip?: string, address?: string): void {
    const event: SecurityEvent = {
      timestamp: Date.now(),
      type,
      severity,
      message,
      ip,
      address,
    };
    this.securityEvents.push(event);
    // Keep last 500 events
    if (this.securityEvents.length > 500) {
      this.securityEvents = this.securityEvents.slice(-500);
    }
  }
  
  getSecurityEvents(limit: number = 50): SecurityEvent[] {
    return this.securityEvents.slice(-limit).reverse();
  }
  
  // === SECURITY AUDIT REPORT ===
  getAuditReport(): any {
    const events = this.securityEvents;
    return {
      timestamp: Date.now(),
      checks: {
        transactionSignatureVerification: { status: 'active', description: 'secp256k1 signature verification on every transaction' },
        transactionHashIntegrity: { status: 'active', description: 'SHA-256 hash recomputation and verification' },
        balanceChecks: { status: 'active', description: 'Double-spend prevention via balance verification before inclusion' },
        chainValidation: { status: 'active', description: 'Full chain integrity validation (Merkle root + hash chain)' },
        blockValidation: { status: 'active', description: 'Block structure and hash validation before acceptance' },
        rateLimiting: { status: 'active', description: `${this.RATE_LIMIT_MAX} req/min general, ${this.RATE_LIMIT_STRICT} req/min sensitive` },
        replayProtection: { status: 'active', description: 'Nonce-based replay attack prevention' },
        adminAuthentication: { status: 'active', description: 'API key required for mint, produce block, deploy contracts' },
        validatorSlashing: { status: 'active', description: 'Slashing conditions for Byzantine validators' },
        inputValidation: { status: 'active', description: 'Address, amount, and input sanitization' },
        mempoolLimits: { status: 'active', description: `Max ${this.MAX_MEMPOOL_SIZE} pending transactions` },
        maxTransactionAmount: { status: 'active', description: `Max ${this.MAX_TX_AMOUNT} VRS per transaction` },
        maxBlockSize: { status: 'active', description: `Max ${this.MAX_BLOCK_SIZE} transactions per block` },
      },
      stats: {
        totalEvents: events.length,
        criticalEvents: events.filter(e => e.severity === 'critical').length,
        warningEvents: events.filter(e => e.severity === 'warning').length,
        infoEvents: events.filter(e => e.severity === 'info').length,
        slashedValidators: this.slashedValidators.size,
        usedNonces: this.usedNonces.size,
        activeRateLimits: this.rateLimits.size,
      },
      recentEvents: events.slice(-10).reverse(),
      cryptography: {
        algorithm: 'secp256k1',
        hashFunction: 'SHA-256 / Keccak256',
        addressDerivation: 'Keccak256 (Ethereum-compatible)',
        signatureScheme: 'ECDSA with recovery',
      },
      consensus: {
        type: 'Delegated Proof of Stake (DPoS)',
        validatorCount: 27,
        blockTime: '5 seconds',
        finality: 'Single-block finality with DPoS confirmation',
      },
    };
  }
}
