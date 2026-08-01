"use strict";
/**
 * Verdis Name Service (VNS) — Human-readable wallet names
 * 
 * Maps human-readable names (e.g. "alice.verdis") to blockchain addresses.
 * Users can register, update, and transfer names.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.NameService = void 0;
const crypto_2 = require("../crypto");
class NameService {
    constructor() {
        this.names = new Map();      // name -> record
        this.addressToName = new Map(); // address -> name (reverse lookup)
        this.registrationFee = 100;  // VRS to register a name
        this.maxNameLength = 32;
        this.minNameLength = 3;
    }
    /**
     * Register a new .verdis name
     */
    register(name, ownerAddress, paymentVerified) {
        // Normalize
        const normalizedName = name.toLowerCase().trim();
        if (!normalizedName.endsWith('.verdis')) {
            return { success: false, error: "Name must end with .verdis" };
        }
        const label = normalizedName.replace('.verdis', '');
        if (label.length < this.minNameLength || label.length > this.maxNameLength) {
            return { success: false, error: `Name must be ${this.minNameLength}-${this.maxNameLength} characters before .verdis` };
        }
        if (!/^[a-z0-9-]+$/.test(label)) {
            return { success: false, error: "Name can only contain lowercase letters, numbers, and hyphens" };
        }
        if (this.names.has(normalizedName)) {
            const existing = this.names.get(normalizedName);
            if (existing.ownerAddress !== ownerAddress) {
                return { success: false, error: "Name already registered" };
            }
        }
        const record = {
            name: normalizedName,
            ownerAddress,
            registeredAt: Date.now(),
            updatedAt: Date.now(),
            expiresAt: Date.now() + (365 * 24 * 60 * 60 * 1000), // 1 year
            textRecords: {},
            transfers: 0,
        };
        this.names.set(normalizedName, record);
        this.addressToName.set(ownerAddress, normalizedName);
        return { success: true, record };
    }
    /**
     * Resolve a name to an address
     */
    resolve(name) {
        const normalizedName = name.toLowerCase().trim();
        const record = this.names.get(normalizedName);
        if (!record) return null;
        if (Date.now() > record.expiresAt) return null;
        return record.ownerAddress;
    }
    /**
     * Reverse lookup: get name from address
     */
    reverseResolve(address) {
        return this.addressToName.get(address) || null;
    }
    /**
     * Transfer a name to a new owner
     */
    transfer(name, currentOwner, newOwner) {
        const normalizedName = name.toLowerCase().trim();
        const record = this.names.get(normalizedName);
        if (!record) return { success: false, error: "Name not found" };
        if (record.ownerAddress !== currentOwner) {
            return { success: false, error: "Only the owner can transfer" };
        }
        this.addressToName.delete(record.ownerAddress);
        record.ownerAddress = newOwner;
        record.transfers++;
        record.updatedAt = Date.now();
        this.addressToName.set(newOwner, normalizedName);
        this.names.set(normalizedName, record);
        return { success: true };
    }
    /**
     * Set a text record (avatar URL, bio, etc.)
     */
    setTextRecord(name, ownerAddress, key, value) {
        const normalizedName = name.toLowerCase().trim();
        const record = this.names.get(normalizedName);
        if (!record) return { success: false, error: "Name not found" };
        if (record.ownerAddress !== ownerAddress) {
            return { success: false, error: "Only the owner can update text records" };
        }
        record.textRecords[key] = value;
        record.updatedAt = Date.now();
        this.names.set(normalizedName, record);
        return { success: true };
    }
    /**
     * Renew a name registration
     */
    renew(name, ownerAddress) {
        const normalizedName = name.toLowerCase().trim();
        const record = this.names.get(normalizedName);
        if (!record) return { success: false, error: "Name not found" };
        if (record.ownerAddress !== ownerAddress) {
            return { success: false, error: "Only the owner can renew" };
        }
        record.expiresAt = Date.now() + (365 * 24 * 60 * 60 * 1000);
        record.updatedAt = Date.now();
        this.names.set(normalizedName, record);
        return { success: true, expiresAt: record.expiresAt };
    }
    /**
     * Get all registered names
     */
    getAllNames() {
        return Array.from(this.names.values());
    }
    /**
     * Get names owned by an address
     */
    getNamesByOwner(address) {
        return Array.from(this.names.values()).filter(r => r.ownerAddress === address);
    }
    getStats() {
        return {
            totalNames: this.names.size,
            activeNames: Array.from(this.names.values()).filter(r => Date.now() < r.expiresAt).length,
            expiredNames: Array.from(this.names.values()).filter(r => Date.now() >= r.expiresAt).length,
            totalTransfers: Array.from(this.names.values()).reduce((s, r) => s + r.transfers, 0),
        };
    }
    exportState() {
        return {
            names: Array.from(this.names.entries()),
            addressToName: Array.from(this.addressToName.entries()),
        };
    }
    importState(state) {
        if (state.names) this.names = new Map(state.names);
        if (state.addressToName) this.addressToName = new Map(state.addressToName);
    }
}
exports.NameService = NameService;
