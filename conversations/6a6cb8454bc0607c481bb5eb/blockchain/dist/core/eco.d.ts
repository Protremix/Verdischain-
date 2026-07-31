/**
 * 1. CarbonCredit Interface
 * Represents a verified or unverified carbon credit asset on EcoChain.
 */
export interface CarbonCredit {
    id: string;
    project: string;
    projectType: 'reforestation' | 'renewable_energy' | 'methane_capture' | 'direct_air_capture' | 'ocean_restoration';
    amount: number;
    price: number;
    seller: string;
    currentOwner: string;
    status: 'available' | 'sold' | 'retired';
    verified: boolean;
    verifier: string;
    verifiedAt: number | null;
    location: string;
    createdAt: number;
    retiredAt: number | null;
    retiredBy: string | null;
    metadata: {
        lat?: number;
        lng?: number;
        images?: string[];
        description?: string;
        [key: string]: any;
    };
}
/**
 * 2. GreenScore Interface
 * Represents environmental performance score for network validators.
 */
export interface GreenScore {
    address: string;
    renewableEnergy: boolean;
    energySource: string;
    carbonOffset: number;
    treesPlanted: number;
    score: number;
    lastUpdated: number;
}
/**
 * 3. ReforestationProject Interface
 * Represents real-world tree planting and CO2 sequestration projects.
 */
export interface ReforestationProject {
    id: string;
    name: string;
    location: {
        lat: number;
        lng: number;
        country: string;
    };
    area: number;
    treesPlanted: number;
    treesTarget: number;
    species: string[];
    status: 'planned' | 'planting' | 'growing' | 'verified' | 'completed';
    owner: string;
    startedAt: number;
    co2Sequestered: number;
    verifiers: string[];
    lastVerifiedAt: number | null;
}
/**
 * 4. CarbonOffsetPool Interface
 * Protocol-level carbon offset pool derived from transaction fee collection.
 */
export interface CarbonOffsetPool {
    totalCollected: number;
    totalOffset: number;
    txFeeOffsetRate: number;
    offsetProjects: string[];
}
/**
 * 5. EcoSystem Class
 * Core eco features engine for EcoChain tracking real environmental impact.
 */
export declare class EcoSystem {
    private carbonCredits;
    private greenScores;
    private reforestationProjects;
    private carbonOffsetPool;
    constructor();
    /**
     * Mints a new carbon credit representing verifiable CO2 offset.
     */
    mintCarbonCredit(seller: string, projectType: string, amount: number, price: number, location: string, metadata?: any): CarbonCredit;
    /**
     * Verifies a carbon credit before it is retired.
     */
    verifyCarbonCredit(creditId: string, verifier: string): {
        success: boolean;
        error?: string;
    };
    /**
     * Purchases carbon credits from the marketplace.
     */
    buyCarbonCredit(creditId: string, buyer: string, amount: number): {
        success: boolean;
        error?: string;
    };
    /**
     * Permanently retires carbon credits to neutralize carbon footprint.
     */
    retireCarbonCredit(creditId: string, by: string): {
        success: boolean;
        error?: string;
    };
    /**
     * Retrieves carbon credits with optional status and projectType filters.
     */
    getCarbonCredits(filter?: {
        status?: string;
        projectType?: string;
    }): CarbonCredit[];
    /**
     * Retrieves a single carbon credit by ID.
     */
    getCarbonCredit(creditId: string): CarbonCredit | undefined;
    /**
     * Checks if an energy source qualifies as renewable.
     */
    private isRenewableEnergySource;
    /**
     * Recalculates GreenScore (0-100) based on mathematical formula:
     * - Renewable Energy: +40 points
     * - Carbon Offset: +1 point per ton up to 30 points
     * - Trees Planted: +1 point per tree up to 30 points
     */
    private calculateGreenScoreValue;
    /**
     * Registers a validator with their energy source and initial green score.
     */
    registerGreenValidator(address: string, energySource: string): GreenScore;
    /**
     * Updates validator's green parameters and recalculates 0-100 score.
     */
    updateGreenScore(address: string, updates: Partial<GreenScore>): GreenScore;
    /**
     * Gets green score for a specific validator address.
     */
    getGreenScore(address: string): GreenScore | undefined;
    /**
     * Returns top N validators ranked by green score.
     */
    getTopGreenValidators(n: number): GreenScore[];
    /**
     * Returns all green scores.
     */
    getAllGreenScores(): GreenScore[];
    /**
     * Creates a new reforestation project tracking tree planting targets.
     */
    createReforestationProject(owner: string, name: string, location: {
        lat: number;
        lng: number;
        country: string;
    }, area: number, treesTarget: number, species: string[]): ReforestationProject;
    /**
     * Updates planted trees count and recalculates CO2 sequestered.
     * CO2 Sequestration standard: 22 kg CO2 per tree per year.
     */
    updateReforestationProject(projectId: string, treesPlanted: number): ReforestationProject | null;
    /**
     * Verifies a reforestation project with an authorized verifier address.
     */
    verifyReforestationProject(projectId: string, verifier: string): {
        success: boolean;
        error?: string;
    };
    /**
     * Returns reforestation projects, optionally filtered by status.
     */
    getReforestationProjects(status?: string): ReforestationProject[];
    /**
     * Returns a single reforestation project by ID.
     */
    getReforestationProject(projectId: string): ReforestationProject | undefined;
    /**
     * Collects transaction fee and allocates txFeeOffsetRate portion to carbon offset pool.
     */
    collectOffsetFee(amount: number): void;
    /**
     * Funds a reforestation project using collected carbon offset pool funds.
     */
    fundOffsetProject(projectId: string, amount: number): {
        success: boolean;
        error?: string;
    };
    /**
     * Returns the current carbon offset pool status.
     */
    getCarbonOffsetPool(): CarbonOffsetPool;
    /**
     * Aggregates total environmental impact across EcoChain network.
     */
    getNetworkImpact(): {
        totalCO2Offset: number;
        totalTrees: number;
        totalArea: number;
        greenValidators: number;
        creditsRetired: number;
        offsetFundBalance: number;
    };
}
