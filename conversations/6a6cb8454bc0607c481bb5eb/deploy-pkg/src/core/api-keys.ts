/**
 * Verdis API Key Management System
 * 
 * Allows external platforms (exchanges, trackers, wallets, dApps) to:
 * - Register and generate API keys with secret keys
 * - Get scoped permissions (read, trade, write, admin)
 * - Track usage and rate limits per key
 * - Revoke and rotate keys
 * 
 * Keys are HMAC-signed for verification (no plaintext storage of secrets).
 */

import crypto from 'crypto';

export type ApiKeyScope = 'read' | 'trade' | 'write' | 'admin';

export interface ApiKey {
  keyId: string;          // Public key ID (like "vk_a1b2c3...")
  apiKey: string;         // Full API key for auth header
  secretHash: string;     // HMAC hash of secret (never store plaintext)
  name: string;           // Platform/app name
  owner: string;          // Owner address or email
  scopes: ApiKeyScope[];  // Permission scopes
  rateLimit: number;      // Requests per minute for this key
  createdAt: number;
  expiresAt: number | null;  // null = never expires
  lastUsed: number | null;
  requestCount: number;
  active: boolean;
  metadata?: {
    website?: string;
    description?: string;
    webhookUrl?: string;
    ipWhitelist?: string[];
  };
}

export interface ApiKeyResponse {
  keyId: string;
  apiKey: string;
  secretKey: string;   // Only returned ONCE at creation
  name: string;
  scopes: ApiKeyScope[];
  rateLimit: number;
  createdAt: number;
  expiresAt: number | null;
}

export class ApiKeyManager {
  private keys: Map<string, ApiKey> = new Map();
  private keyByApiKey: Map<string, ApiKey> = new Map();  // Fast lookup by API key
  private hmacSecret: string;
  
  constructor(hmacSecret?: string) {
    this.hmacSecret = hmacSecret || crypto.randomBytes(32).toString('hex');
  }

  /**
   * Generate a new API key + secret for an external platform
   */
  createKey(opts: {
    name: string;
    owner: string;
    scopes: ApiKeyScope[];
    rateLimit?: number;
    expiresInDays?: number;
    metadata?: {
      website?: string;
      description?: string;
      webhookUrl?: string;
      ipWhitelist?: string[];
    };
  }): ApiKeyResponse {
    const keyId = 'vk_' + crypto.randomBytes(6).toString('hex');
    const apiKey = 'vrs_' + crypto.randomBytes(24).toString('hex');
    const secretKey = 'vss_' + crypto.randomBytes(32).toString('hex');
    const secretHash = this.hashSecret(secretKey);

    const now = Date.now();
    const expiresAt = opts.expiresInDays 
      ? now + (opts.expiresInDays * 24 * 60 * 60 * 1000) 
      : null;

    const key: ApiKey = {
      keyId,
      apiKey,
      secretHash,
      name: opts.name,
      owner: opts.owner,
      scopes: opts.scopes,
      rateLimit: opts.rateLimit || 60,
      createdAt: now,
      expiresAt,
      lastUsed: null,
      requestCount: 0,
      active: true,
      metadata: opts.metadata,
    };

    this.keys.set(keyId, key);
    this.keyByApiKey.set(apiKey, key);

    return {
      keyId,
      apiKey,
      secretKey,  // Only returned once!
      name: opts.name,
      scopes: opts.scopes,
      rateLimit: key.rateLimit,
      createdAt: now,
      expiresAt,
    };
  }

  /**
   * Verify an API key + optional secret signature
   * Used for HMAC-signed requests (more secure)
   */
  verifyRequest(
    apiKey: string, 
    signature: string, 
    timestamp: string, 
    body: string
  ): { valid: boolean; key?: ApiKey; error?: string } {
    const key = this.keyByApiKey.get(apiKey);
    if (!key) {
      return { valid: false, error: 'Invalid API key' };
    }
    if (!key.active) {
      return { valid: false, error: 'API key revoked' };
    }
    if (key.expiresAt && Date.now() > key.expiresAt) {
      return { valid: false, error: 'API key expired' };
    }

    // Verify HMAC signature
    const expectedSig = this.signRequest(apiKey, timestamp, body, key.secretHash);
    if (signature !== expectedSig) {
      return { valid: false, error: 'Invalid signature' };
    }

    // Check timestamp (prevent replay, 5 min window)
    const tsNum = parseInt(timestamp);
    if (Math.abs(Date.now() - tsNum) > 5 * 60 * 1000) {
      return { valid: false, error: 'Request timestamp expired' };
    }

    // Update usage
    key.lastUsed = Date.now();
    key.requestCount++;

    return { valid: true, key };
  }

  /**
   * Simple API key verification (no HMAC, just key check)
   * For less sensitive endpoints
   */
  verifyApiKey(apiKey: string): { valid: boolean; key?: ApiKey; error?: string } {
    const key = this.keyByApiKey.get(apiKey);
    if (!key) {
      return { valid: false, error: 'Invalid API key' };
    }
    if (!key.active) {
      return { valid: false, error: 'API key revoked' };
    }
    if (key.expiresAt && Date.now() > key.expiresAt) {
      return { valid: false, error: 'API key expired' };
    }
    key.lastUsed = Date.now();
    key.requestCount++;
    return { valid: true, key };
  }

  /**
   * Check if a key has a specific scope
   */
  hasScope(key: ApiKey, scope: ApiKeyScope): boolean {
    if (key.scopes.includes('admin')) return true;
    if (scope === 'read') return true; // All keys can read
    return key.scopes.includes(scope);
  }

  /**
   * Revoke an API key
   */
  revokeKey(keyId: string): boolean {
    const key = this.keys.get(keyId);
    if (!key) return false;
    key.active = false;
    this.keyByApiKey.delete(key.apiKey);
    return true;
  }

  /**
   * Rotate (regenerate) an API key's secret
   */
  rotateKey(keyId: string): { apiKey: string; secretKey: string } | null {
    const key = this.keys.get(keyId);
    if (!key || !key.active) return null;
    
    this.keyByApiKey.delete(key.apiKey);
    
    const newApiKey = 'vrs_' + crypto.randomBytes(24).toString('hex');
    const newSecret = 'vss_' + crypto.randomBytes(32).toString('hex');
    
    key.apiKey = newApiKey;
    key.secretHash = this.hashSecret(newSecret);
    
    this.keyByApiKey.set(newApiKey, key);
    
    return { apiKey: newApiKey, secretKey: newSecret };
  }

  /**
   * List all API keys (for admin)
   */
  listKeys(): Omit<ApiKey, 'secretHash'>[] {
    return Array.from(this.keys.values()).map(k => {
      const { secretHash, ...rest } = k;
      return rest;
    });
  }

  /**
   * Get key stats
   */
  getKeyStats(keyId: string): any {
    const key = this.keys.get(keyId);
    if (!key) return null;
    return {
      keyId: key.keyId,
      name: key.name,
      scopes: key.scopes,
      rateLimit: key.rateLimit,
      requestCount: key.requestCount,
      lastUsed: key.lastUsed,
      active: key.active,
      createdAt: key.createdAt,
      expiresAt: key.expiresAt,
    };
  }

  /**
   * Get total stats
   */
  getStats(): any {
    const keys = Array.from(this.keys.values());
    return {
      totalKeys: keys.length,
      activeKeys: keys.filter(k => k.active).length,
      revokedKeys: keys.filter(k => !k.active).length,
      totalRequests: keys.reduce((sum, k) => sum + k.requestCount, 0),
      byScope: {
        read: keys.filter(k => k.scopes.includes('read')).length,
        trade: keys.filter(k => k.scopes.includes('trade')).length,
        write: keys.filter(k => k.scopes.includes('write')).length,
        admin: keys.filter(k => k.scopes.includes('admin')).length,
      },
    };
  }

  /**
   * Generate HMAC signature for a request
   * Clients use this to sign their requests
   */
  signRequest(apiKey: string, timestamp: string, body: string, secretHash: string): string {
    const payload = `${apiKey}.${timestamp}.${body}`;
    return crypto.createHmac('sha256', secretHash).update(payload).digest('hex');
  }

  /**
   * Hash a secret for storage (never store plaintext)
   */
  private hashSecret(secret: string): string {
    return crypto.createHash('sha256').update(secret + this.hmacSecret).digest('hex');
  }

  /**
   * Export keys for persistence
   */
  exportKeys(): any[] {
    return Array.from(this.keys.values()).map(k => ({
      ...k,
      metadata: k.metadata || {},
    }));
  }

  /**
   * Import keys from persistence
   */
  importKeys(keys: any[]): void {
    for (const k of keys) {
      this.keys.set(k.keyId, k);
      if (k.active) {
        this.keyByApiKey.set(k.apiKey, k);
      }
    }
  }
}
