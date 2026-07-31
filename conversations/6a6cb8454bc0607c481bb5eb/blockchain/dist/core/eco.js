"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EcoSystem = void 0;
const crypto_1 = require("../crypto");
/**
 * Common list of renewable energy source keywords.
 */
const RENEWABLE_SOURCES = [
    'solar',
    'wind',
    'hydro',
    'hydroelectric',
    'geothermal',
    'biomass',
    'tidal',
    'wave',
    'ocean',
    'renewable',
];
/**
 * 5. EcoSystem Class
 * Core eco features engine for EcoChain tracking real environmental impact.
 */
class EcoSystem {
    constructor() {
        this.carbonCredits = new Map();
        this.greenScores = new Map();
        this.reforestationProjects = new Map();
        this.carbonOffsetPool = {
            totalCollected: 0,
            totalOffset: 0,
            txFeeOffsetRate: 0.1, // 10% default
            offsetProjects: [],
        };
    }
    // ==========================================
    // CARBON CREDIT LIFECYCLE METHODS
    // ==========================================
    /**
     * Mints a new carbon credit representing verifiable CO2 offset.
     */
    mintCarbonCredit(seller, projectType, amount, price, location, metadata) {
        const validTypes = [
            'reforestation',
            'renewable_energy',
            'methane_capture',
            'direct_air_capture',
            'ocean_restoration',
        ];
        const typeLower = (projectType || '').toLowerCase();
        const finalType = validTypes.includes(typeLower)
            ? typeLower
            : 'reforestation';
        const timestamp = Date.now();
        const nonce = Math.floor(Math.random() * 1000000);
        const id = (0, crypto_1.sha256)(`credit:${seller}:${finalType}:${amount}:${location}:${timestamp}:${nonce}`);
        const project = metadata?.project ||
            metadata?.name ||
            `${finalType.replace(/_/g, ' ').toUpperCase()} Offset Project (${location})`;
        const credit = {
            id,
            project,
            projectType: finalType,
            amount: Math.max(0, amount),
            price: Math.max(0, price),
            seller,
            currentOwner: seller,
            status: 'available',
            verified: false,
            verifier: '',
            verifiedAt: null,
            location,
            createdAt: timestamp,
            retiredAt: null,
            retiredBy: null,
            metadata: {
                lat: metadata?.lat,
                lng: metadata?.lng,
                images: metadata?.images || [],
                description: metadata?.description,
                ...metadata,
            },
        };
        this.carbonCredits.set(id, credit);
        return credit;
    }
    /**
     * Verifies a carbon credit before it is retired.
     */
    verifyCarbonCredit(creditId, verifier) {
        const credit = this.carbonCredits.get(creditId);
        if (!credit) {
            return { success: false, error: 'Carbon credit not found' };
        }
        if (credit.status === 'retired') {
            return { success: false, error: 'Cannot verify a retired carbon credit' };
        }
        credit.verified = true;
        credit.verifier = verifier;
        credit.verifiedAt = Date.now();
        return { success: true };
    }
    /**
     * Purchases carbon credits from the marketplace.
     */
    buyCarbonCredit(creditId, buyer, amount) {
        const credit = this.carbonCredits.get(creditId);
        if (!credit) {
            return { success: false, error: 'Carbon credit not found' };
        }
        if (credit.status === 'retired') {
            return { success: false, error: 'Carbon credit is retired and cannot be bought' };
        }
        if (credit.status !== 'available') {
            return { success: false, error: 'Carbon credit is not available for purchase' };
        }
        if (amount <= 0 || amount > credit.amount) {
            return { success: false, error: 'Invalid purchase amount requested' };
        }
        if (amount === credit.amount) {
            credit.currentOwner = buyer;
            credit.status = 'sold';
        }
        else {
            // Split credit for partial purchase
            credit.amount -= amount;
            const timestamp = Date.now();
            const nonce = Math.floor(Math.random() * 1000000);
            const boughtCreditId = (0, crypto_1.sha256)(`credit:bought:${credit.id}:${buyer}:${timestamp}:${nonce}`);
            const boughtCredit = {
                id: boughtCreditId,
                project: credit.project,
                projectType: credit.projectType,
                amount,
                price: credit.price,
                seller: credit.seller,
                currentOwner: buyer,
                status: 'sold',
                verified: credit.verified,
                verifier: credit.verifier,
                verifiedAt: credit.verifiedAt,
                location: credit.location,
                createdAt: timestamp,
                retiredAt: null,
                retiredBy: null,
                metadata: { ...credit.metadata },
            };
            this.carbonCredits.set(boughtCreditId, boughtCredit);
        }
        return { success: true };
    }
    /**
     * Permanently retires carbon credits to neutralize carbon footprint.
     */
    retireCarbonCredit(creditId, by) {
        const credit = this.carbonCredits.get(creditId);
        if (!credit) {
            return { success: false, error: 'Carbon credit not found' };
        }
        if (credit.status === 'retired') {
            return { success: false, error: 'Carbon credit is already retired' };
        }
        credit.status = 'retired';
        credit.retiredAt = Date.now();
        credit.retiredBy = by;
        // Increment offset pool tracking
        this.carbonOffsetPool.totalOffset += credit.amount;
        // Update retiring validator's green score if validator is registered
        if (this.greenScores.has(by)) {
            const currentOffset = this.greenScores.get(by).carbonOffset;
            this.updateGreenScore(by, { carbonOffset: currentOffset + credit.amount });
        }
        return { success: true };
    }
    /**
     * Retrieves carbon credits with optional status and projectType filters.
     */
    getCarbonCredits(filter) {
        let credits = Array.from(this.carbonCredits.values());
        if (filter?.status) {
            credits = credits.filter((c) => c.status === filter.status);
        }
        if (filter?.projectType) {
            credits = credits.filter((c) => c.projectType === filter.projectType);
        }
        return credits;
    }
    /**
     * Retrieves a single carbon credit by ID.
     */
    getCarbonCredit(creditId) {
        return this.carbonCredits.get(creditId);
    }
    // ==========================================
    // GREEN VALIDATOR SCORING METHODS
    // ==========================================
    /**
     * Checks if an energy source qualifies as renewable.
     */
    isRenewableEnergySource(energySource) {
        if (!energySource)
            return false;
        const lower = energySource.toLowerCase();
        return RENEWABLE_SOURCES.some((src) => lower.includes(src));
    }
    /**
     * Recalculates GreenScore (0-100) based on mathematical formula:
     * - Renewable Energy: +40 points
     * - Carbon Offset: +1 point per ton up to 30 points
     * - Trees Planted: +1 point per tree up to 30 points
     */
    calculateGreenScoreValue(renewableEnergy, carbonOffset, treesPlanted) {
        const renewablePoints = renewableEnergy ? 40 : 0;
        const offsetPoints = Math.min(30, Math.max(0, carbonOffset));
        const treesPoints = Math.min(30, Math.max(0, treesPlanted));
        const rawScore = renewablePoints + offsetPoints + treesPoints;
        return Math.min(100, Math.max(0, Math.round(rawScore)));
    }
    /**
     * Registers a validator with their energy source and initial green score.
     */
    registerGreenValidator(address, energySource) {
        const isRenewable = this.isRenewableEnergySource(energySource);
        const existing = this.greenScores.get(address);
        const carbonOffset = existing ? existing.carbonOffset : 0;
        const treesPlanted = existing ? existing.treesPlanted : 0;
        const score = this.calculateGreenScoreValue(isRenewable, carbonOffset, treesPlanted);
        const greenScore = {
            address,
            renewableEnergy: isRenewable,
            energySource,
            carbonOffset,
            treesPlanted,
            score,
            lastUpdated: Date.now(),
        };
        this.greenScores.set(address, greenScore);
        return greenScore;
    }
    /**
     * Updates validator's green parameters and recalculates 0-100 score.
     */
    updateGreenScore(address, updates) {
        let current = this.greenScores.get(address);
        if (!current) {
            current = {
                address,
                renewableEnergy: false,
                energySource: 'unknown',
                carbonOffset: 0,
                treesPlanted: 0,
                score: 0,
                lastUpdated: Date.now(),
            };
        }
        if (updates.energySource !== undefined) {
            current.energySource = updates.energySource;
            if (updates.renewableEnergy === undefined) {
                current.renewableEnergy = this.isRenewableEnergySource(updates.energySource);
            }
        }
        if (updates.renewableEnergy !== undefined) {
            current.renewableEnergy = updates.renewableEnergy;
        }
        if (updates.carbonOffset !== undefined) {
            current.carbonOffset = Math.max(0, updates.carbonOffset);
        }
        if (updates.treesPlanted !== undefined) {
            current.treesPlanted = Math.max(0, updates.treesPlanted);
        }
        current.score = this.calculateGreenScoreValue(current.renewableEnergy, current.carbonOffset, current.treesPlanted);
        current.lastUpdated = Date.now();
        this.greenScores.set(address, current);
        return current;
    }
    /**
     * Gets green score for a specific validator address.
     */
    getGreenScore(address) {
        return this.greenScores.get(address);
    }
    /**
     * Returns top N validators ranked by green score.
     */
    getTopGreenValidators(n) {
        const list = Array.from(this.greenScores.values());
        list.sort((a, b) => b.score - a.score);
        return list.slice(0, Math.max(0, n));
    }
    // ==========================================
    // REFORESTATION VERIFICATION METHODS
    // ==========================================
    /**
     * Creates a new reforestation project tracking tree planting targets.
     */
    createReforestationProject(owner, name, location, area, treesTarget, species) {
        const timestamp = Date.now();
        const nonce = Math.floor(Math.random() * 1000000);
        const id = (0, crypto_1.sha256)(`reforestation:${owner}:${name}:${timestamp}:${nonce}`);
        const project = {
            id,
            name,
            location,
            area: Math.max(0, area),
            treesPlanted: 0,
            treesTarget: Math.max(0, treesTarget),
            species: species || [],
            status: 'planned',
            owner,
            startedAt: timestamp,
            co2Sequestered: 0,
            verifiers: [],
            lastVerifiedAt: null,
        };
        this.reforestationProjects.set(id, project);
        return project;
    }
    /**
     * Updates planted trees count and recalculates CO2 sequestered.
     * CO2 Sequestration standard: 22 kg CO2 per tree per year.
     */
    updateReforestationProject(projectId, treesPlanted) {
        const project = this.reforestationProjects.get(projectId);
        if (!project) {
            return null;
        }
        project.treesPlanted = Math.max(0, treesPlanted);
        // Calculate CO2 sequestered using 22 kg CO2 per tree per year
        const msPerYear = 365.25 * 24 * 60 * 60 * 1000;
        const yearsElapsed = Math.max(0, (Date.now() - project.startedAt) / msPerYear);
        const kgCO2 = project.treesPlanted * 22 * yearsElapsed;
        project.co2Sequestered = Math.max(0, kgCO2 / 1000); // metric tons
        // Update project status based on progress
        if (project.treesPlanted > 0 && project.status === 'planned') {
            project.status = 'planting';
        }
        if (project.treesPlanted >= project.treesTarget && project.status === 'planting') {
            project.status = 'growing';
        }
        // If project owner is a registered validator, update validator treesPlanted
        if (this.greenScores.has(project.owner)) {
            const currentTrees = this.greenScores.get(project.owner).treesPlanted;
            this.updateGreenScore(project.owner, { treesPlanted: currentTrees + project.treesPlanted });
        }
        return project;
    }
    /**
     * Verifies a reforestation project with an authorized verifier address.
     */
    verifyReforestationProject(projectId, verifier) {
        const project = this.reforestationProjects.get(projectId);
        if (!project) {
            return { success: false, error: 'Reforestation project not found' };
        }
        if (!project.verifiers.includes(verifier)) {
            project.verifiers.push(verifier);
        }
        project.lastVerifiedAt = Date.now();
        if (project.status === 'growing' || project.status === 'planting') {
            if (project.treesPlanted >= project.treesTarget) {
                project.status = 'completed';
            }
            else {
                project.status = 'verified';
            }
        }
        return { success: true };
    }
    /**
     * Returns reforestation projects, optionally filtered by status.
     */
    getReforestationProjects(status) {
        const projects = Array.from(this.reforestationProjects.values());
        if (status) {
            return projects.filter((p) => p.status === status);
        }
        return projects;
    }
    /**
     * Returns a single reforestation project by ID.
     */
    getReforestationProject(projectId) {
        return this.reforestationProjects.get(projectId);
    }
    // ==========================================
    // CARBON OFFSET POOL METHODS
    // ==========================================
    /**
     * Collects transaction fee and allocates txFeeOffsetRate portion to carbon offset pool.
     */
    collectOffsetFee(amount) {
        if (amount <= 0)
            return;
        const offsetAmount = amount * this.carbonOffsetPool.txFeeOffsetRate;
        this.carbonOffsetPool.totalCollected += offsetAmount;
    }
    /**
     * Funds a reforestation project using collected carbon offset pool funds.
     */
    fundOffsetProject(projectId, amount) {
        const project = this.reforestationProjects.get(projectId);
        if (!project) {
            return { success: false, error: 'Reforestation project not found' };
        }
        if (amount <= 0) {
            return { success: false, error: 'Invalid funding amount' };
        }
        if (amount > this.carbonOffsetPool.totalCollected) {
            return { success: false, error: 'Insufficient funds in carbon offset pool' };
        }
        this.carbonOffsetPool.totalCollected -= amount;
        if (!this.carbonOffsetPool.offsetProjects.includes(projectId)) {
            this.carbonOffsetPool.offsetProjects.push(projectId);
        }
        return { success: true };
    }
    /**
     * Returns the current carbon offset pool status.
     */
    getCarbonOffsetPool() {
        return this.carbonOffsetPool;
    }
    /**
     * Aggregates total environmental impact across EcoChain network.
     */
    getNetworkImpact() {
        let creditsRetiredCount = 0;
        let retiredCreditCO2 = 0;
        for (const credit of this.carbonCredits.values()) {
            if (credit.status === 'retired') {
                creditsRetiredCount++;
                retiredCreditCO2 += credit.amount;
            }
        }
        let totalProjectTrees = 0;
        let totalProjectArea = 0;
        let totalSequesteredCO2 = 0;
        for (const project of this.reforestationProjects.values()) {
            totalProjectTrees += project.treesPlanted;
            totalProjectArea += project.area;
            totalSequesteredCO2 += project.co2Sequestered;
        }
        const greenValidatorsCount = Array.from(this.greenScores.values()).filter((g) => g.renewableEnergy || g.score > 0).length;
        return {
            totalCO2Offset: retiredCreditCO2 + totalSequesteredCO2 + this.carbonOffsetPool.totalOffset,
            totalTrees: totalProjectTrees,
            totalArea: totalProjectArea,
            greenValidators: greenValidatorsCount,
            creditsRetired: creditsRetiredCount,
            offsetFundBalance: this.carbonOffsetPool.totalCollected,
        };
    }
}
exports.EcoSystem = EcoSystem;
//# sourceMappingURL=eco.js.map