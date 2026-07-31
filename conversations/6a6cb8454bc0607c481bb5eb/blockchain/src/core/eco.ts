import { sha256 } from '../crypto';

/**
 * 1. CarbonCredit Interface
 * Represents a verified or unverified carbon credit asset on EcoChain.
 */
export interface CarbonCredit {
  id: string;
  project: string; // name of the offset project
  projectType: 'reforestation' | 'renewable_energy' | 'methane_capture' | 'direct_air_capture' | 'ocean_restoration';
  amount: number; // tons of CO2
  price: number; // price in ECO tokens per ton
  seller: string; // address
  currentOwner: string; // address
  status: 'available' | 'sold' | 'retired';
  verified: boolean;
  verifier: string; // address of the verifier
  verifiedAt: number | null;
  location: string; // geographic location
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
  renewableEnergy: boolean; // validator uses renewable energy
  energySource: string; // solar, wind, hydro, geothermal, etc.
  carbonOffset: number; // total tons of CO2 offset by this validator
  treesPlanted: number;
  score: number; // 0-100 green score
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
  area: number; // hectares
  treesPlanted: number;
  treesTarget: number;
  species: string[];
  status: 'planned' | 'planting' | 'growing' | 'verified' | 'completed';
  owner: string; // address
  startedAt: number;
  co2Sequestered: number; // tons, calculated from trees and age
  verifiers: string[]; // addresses of verifiers
  lastVerifiedAt: number | null;
}

/**
 * 4. CarbonOffsetPool Interface
 * Protocol-level carbon offset pool derived from transaction fee collection.
 */
export interface CarbonOffsetPool {
  totalCollected: number; // ECO tokens collected from transaction fees
  totalOffset: number; // tons of CO2 offset
  txFeeOffsetRate: number; // percentage of tx fee that goes to carbon offset, default 0.1 = 10%
  offsetProjects: string[]; // project IDs funded
}

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
export class EcoSystem {
  private carbonCredits: Map<string, CarbonCredit>;
  private greenScores: Map<string, GreenScore>;
  private reforestationProjects: Map<string, ReforestationProject>;
  private carbonOffsetPool: CarbonOffsetPool;

  constructor() {
    this.carbonCredits = new Map<string, CarbonCredit>();
    this.greenScores = new Map<string, GreenScore>();
    this.reforestationProjects = new Map<string, ReforestationProject>();
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
  public mintCarbonCredit(
    seller: string,
    projectType: string,
    amount: number,
    price: number,
    location: string,
    metadata?: any
  ): CarbonCredit {
    const validTypes: Array<CarbonCredit['projectType']> = [
      'reforestation',
      'renewable_energy',
      'methane_capture',
      'direct_air_capture',
      'ocean_restoration',
    ];

    const typeLower = (projectType || '').toLowerCase() as CarbonCredit['projectType'];
    const finalType: CarbonCredit['projectType'] = validTypes.includes(typeLower)
      ? typeLower
      : 'reforestation';

    const timestamp = Date.now();
    const nonce = Math.floor(Math.random() * 1000000);
    const id = sha256(`credit:${seller}:${finalType}:${amount}:${location}:${timestamp}:${nonce}`);

    const project =
      metadata?.project ||
      metadata?.name ||
      `${finalType.replace(/_/g, ' ').toUpperCase()} Offset Project (${location})`;

    const credit: CarbonCredit = {
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
  public verifyCarbonCredit(
    creditId: string,
    verifier: string
  ): { success: boolean; error?: string } {
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
  public buyCarbonCredit(
    creditId: string,
    buyer: string,
    amount: number
  ): { success: boolean; error?: string } {
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
    } else {
      // Split credit for partial purchase
      credit.amount -= amount;

      const timestamp = Date.now();
      const nonce = Math.floor(Math.random() * 1000000);
      const boughtCreditId = sha256(`credit:bought:${credit.id}:${buyer}:${timestamp}:${nonce}`);

      const boughtCredit: CarbonCredit = {
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
  public retireCarbonCredit(
    creditId: string,
    by: string
  ): { success: boolean; error?: string } {
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
      const currentOffset = this.greenScores.get(by)!.carbonOffset;
      this.updateGreenScore(by, { carbonOffset: currentOffset + credit.amount });
    }

    return { success: true };
  }

  /**
   * Retrieves carbon credits with optional status and projectType filters.
   */
  public getCarbonCredits(filter?: { status?: string; projectType?: string }): CarbonCredit[] {
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
  public getCarbonCredit(creditId: string): CarbonCredit | undefined {
    return this.carbonCredits.get(creditId);
  }

  // ==========================================
  // GREEN VALIDATOR SCORING METHODS
  // ==========================================

  /**
   * Checks if an energy source qualifies as renewable.
   */
  private isRenewableEnergySource(energySource: string): boolean {
    if (!energySource) return false;
    const lower = energySource.toLowerCase();
    return RENEWABLE_SOURCES.some((src) => lower.includes(src));
  }

  /**
   * Recalculates GreenScore (0-100) based on mathematical formula:
   * - Renewable Energy: +40 points
   * - Carbon Offset: +1 point per ton up to 30 points
   * - Trees Planted: +1 point per tree up to 30 points
   */
  private calculateGreenScoreValue(
    renewableEnergy: boolean,
    carbonOffset: number,
    treesPlanted: number
  ): number {
    const renewablePoints = renewableEnergy ? 40 : 0;
    const offsetPoints = Math.min(30, Math.max(0, carbonOffset));
    const treesPoints = Math.min(30, Math.max(0, treesPlanted));
    const rawScore = renewablePoints + offsetPoints + treesPoints;
    return Math.min(100, Math.max(0, Math.round(rawScore)));
  }

  /**
   * Registers a validator with their energy source and initial green score.
   */
  public registerGreenValidator(address: string, energySource: string): GreenScore {
    const isRenewable = this.isRenewableEnergySource(energySource);
    const existing = this.greenScores.get(address);

    const carbonOffset = existing ? existing.carbonOffset : 0;
    const treesPlanted = existing ? existing.treesPlanted : 0;
    const score = this.calculateGreenScoreValue(isRenewable, carbonOffset, treesPlanted);

    const greenScore: GreenScore = {
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
  public updateGreenScore(address: string, updates: Partial<GreenScore>): GreenScore {
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

    current.score = this.calculateGreenScoreValue(
      current.renewableEnergy,
      current.carbonOffset,
      current.treesPlanted
    );
    current.lastUpdated = Date.now();

    this.greenScores.set(address, current);
    return current;
  }

  /**
   * Gets green score for a specific validator address.
   */
  public getGreenScore(address: string): GreenScore | undefined {
    return this.greenScores.get(address);
  }

  /**
   * Returns top N validators ranked by green score.
   */
  public getTopGreenValidators(n: number): GreenScore[] {
    const list = Array.from(this.greenScores.values());
    list.sort((a, b) => b.score - a.score);
    return list.slice(0, Math.max(0, n));
  }

  /**
   * Returns all green scores.
   */
  public getAllGreenScores(): GreenScore[] {
    return Array.from(this.greenScores.values());
  }

  // ==========================================
  // REFORESTATION VERIFICATION METHODS
  // ==========================================

  /**
   * Creates a new reforestation project tracking tree planting targets.
   */
  public createReforestationProject(
    owner: string,
    name: string,
    location: { lat: number; lng: number; country: string },
    area: number,
    treesTarget: number,
    species: string[]
  ): ReforestationProject {
    const timestamp = Date.now();
    const nonce = Math.floor(Math.random() * 1000000);
    const id = sha256(`reforestation:${owner}:${name}:${timestamp}:${nonce}`);

    const project: ReforestationProject = {
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
  public updateReforestationProject(
    projectId: string,
    treesPlanted: number
  ): ReforestationProject | null {
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
      const currentTrees = this.greenScores.get(project.owner)!.treesPlanted;
      this.updateGreenScore(project.owner, { treesPlanted: currentTrees + project.treesPlanted });
    }

    return project;
  }

  /**
   * Verifies a reforestation project with an authorized verifier address.
   */
  public verifyReforestationProject(
    projectId: string,
    verifier: string
  ): { success: boolean; error?: string } {
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
      } else {
        project.status = 'verified';
      }
    }

    return { success: true };
  }

  /**
   * Returns reforestation projects, optionally filtered by status.
   */
  public getReforestationProjects(status?: string): ReforestationProject[] {
    const projects = Array.from(this.reforestationProjects.values());
    if (status) {
      return projects.filter((p) => p.status === status);
    }
    return projects;
  }

  /**
   * Returns a single reforestation project by ID.
   */
  public getReforestationProject(projectId: string): ReforestationProject | undefined {
    return this.reforestationProjects.get(projectId);
  }

  // ==========================================
  // CARBON OFFSET POOL METHODS
  // ==========================================

  /**
   * Collects transaction fee and allocates txFeeOffsetRate portion to carbon offset pool.
   */
  public collectOffsetFee(amount: number): void {
    if (amount <= 0) return;
    const offsetAmount = amount * this.carbonOffsetPool.txFeeOffsetRate;
    this.carbonOffsetPool.totalCollected += offsetAmount;
  }

  /**
   * Funds a reforestation project using collected carbon offset pool funds.
   */
  public fundOffsetProject(
    projectId: string,
    amount: number
  ): { success: boolean; error?: string } {
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
  public getCarbonOffsetPool(): CarbonOffsetPool {
    return this.carbonOffsetPool;
  }

  /**
   * Aggregates total environmental impact across EcoChain network.
   */
  public getNetworkImpact(): {
    totalCO2Offset: number;
    totalTrees: number;
    totalArea: number;
    greenValidators: number;
    creditsRetired: number;
    offsetFundBalance: number;
  } {
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

    const greenValidatorsCount = Array.from(this.greenScores.values()).filter(
      (g) => g.renewableEnergy || g.score > 0
    ).length;

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
