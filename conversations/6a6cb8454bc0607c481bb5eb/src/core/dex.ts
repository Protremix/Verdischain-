import { Transaction } from '../types';
import { sha256 } from '../crypto';

/**
 * Liquidity pool structure representing an Automated Market Maker (AMM) pool.
 */
export interface LiquidityPool {
  id: string;
  tokenA: string; // Token identifier ('ECO' for native token)
  tokenB: string; // Token identifier
  reserveA: number; // Reserve of tokenA in the pool
  reserveB: number; // Reserve of tokenB in the pool
  totalLP: number; // Total liquidity provider tokens minted
  fee: number; // Swap fee percentage (default 0.003 = 0.3%)
  lpBalances: Map<string, number>; // Address -> LP token balance
  createdAt: number; // Timestamp of creation
}

/**
 * Interface representing carbon credit token metadata for eco-focused trading.
 */
export interface CarbonCreditToken {
  symbol: string;
  name: string;
  projectCategory: string; // e.g., 'Reforestation', 'Solar', 'Wind', 'Methane Capture'
  certificationStandard: string; // e.g., 'Verra VCS', 'Gold Standard', 'Plan Vivo'
  vintageYear: number;
  totalIssued: number;
}

/**
 * AMM-based Decentralized Exchange (DEX) supporting liquidity provision,
 * token swapping, LP token minting/burning, and carbon credit trading.
 */
export class DEX {
  private pools: Map<string, LiquidityPool>;
  private tokenBalances: Map<string, Map<string, number>>; // token -> address -> balance
  private carbonTokens: Map<string, CarbonCreditToken>;
  private onStateChange?: () => void;

  constructor() {
    this.pools = new Map<string, LiquidityPool>();
    this.tokenBalances = new Map<string, Map<string, number>>();
    this.carbonTokens = new Map<string, CarbonCreditToken>();
  }

  public setOnStateChange(callback: () => void): void {
    this.onStateChange = callback;
  }

  private notifyStateChange(): void {
    if (this.onStateChange) {
      try {
        this.onStateChange();
      } catch (err) {
        console.error('Error in DEX onStateChange listener:', err);
      }
    }
  }

  /**
   * Generates a deterministic pool ID by sorting token names alphabetically
   * and concatenating with '_' (e.g. 'ECO' and 'TREE' -> 'ECO_TREE').
   */
  public getPoolId(tokenA: string, tokenB: string): string {
    if (!tokenA || !tokenB) {
      throw new Error('Token symbols must not be empty');
    }
    if (tokenA === tokenB) {
      throw new Error('Cannot create or query a pool with identical tokens');
    }
    const sorted = [tokenA, tokenB].sort();
    return `${sorted[0]}_${sorted[1]}`;
  }

  /**
   * Creates a new liquidity pool if it doesn't already exist.
   * Ensures tokenA and tokenB are sorted alphabetically in the pool.
   */
  public createPool(tokenA: string, tokenB: string, fee: number = 0.003): LiquidityPool {
    const poolId = this.getPoolId(tokenA, tokenB);
    const existing = this.getPool(poolId);
    if (existing) {
      return existing;
    }

    const [sortedA, sortedB] = [tokenA, tokenB].sort();
    const newPool: LiquidityPool = {
      id: poolId,
      tokenA: sortedA,
      tokenB: sortedB,
      reserveA: 0,
      reserveB: 0,
      totalLP: 0,
      fee,
      lpBalances: new Map<string, number>(),
      createdAt: Date.now(),
    };

    this.pools.set(poolId, newPool);
    this.notifyStateChange();
    return newPool;
  }

  /**
   * Gets a pool by its ID. Supports looking up via canonical or inverted ID.
   */
  public getPool(poolId: string): LiquidityPool | undefined {
    if (this.pools.has(poolId)) {
      return this.pools.get(poolId);
    }
    if (poolId.includes('_')) {
      const parts = poolId.split('_');
      if (parts.length === 2) {
        const canonical = `${[parts[0], parts[1]].sort().join('_')}`;
        return this.pools.get(canonical);
      }
    }
    return undefined;
  }

  /**
   * Returns all liquidity pools.
   */
  public getAllPools(): LiquidityPool[] {
    return Array.from(this.pools.values());
  }

  /**
   * Adds liquidity to a pool.
   * If the pool is new, LP tokens = sqrt(amountA * amountB).
   * If pool exists, LP tokens = min(amountA * totalLP / reserveA, amountB * totalLP / reserveB).
   * Updates reserves and LP balance.
   */
  public addLiquidity(
    provider: string,
    tokenA: string,
    tokenB: string,
    amountA: number,
    amountB: number
  ): { lpTokens: number; pool: LiquidityPool } {
    if (amountA <= 0 || amountB <= 0) {
      throw new Error('Liquidity amounts must be greater than zero');
    }

    const poolId = this.getPoolId(tokenA, tokenB);
    let pool = this.getPool(poolId);
    if (!pool) {
      pool = this.createPool(tokenA, tokenB);
    }

    // Determine ordering relative to pool.tokenA and pool.tokenB
    const isTokenAFirst = tokenA === pool.tokenA;
    const amtForReserveA = isTokenAFirst ? amountA : amountB;
    const amtForReserveB = isTokenAFirst ? amountB : amountA;

    // Deduct user balances if tracked in tokenBalances
    this.deductTokenBalanceIfTracked(pool.tokenA, provider, amtForReserveA);
    this.deductTokenBalanceIfTracked(pool.tokenB, provider, amtForReserveB);

    let lpTokens: number;
    if (pool.totalLP === 0 || pool.reserveA === 0 || pool.reserveB === 0) {
      lpTokens = Math.sqrt(amtForReserveA * amtForReserveB);
    } else {
      const shareA = (amtForReserveA * pool.totalLP) / pool.reserveA;
      const shareB = (amtForReserveB * pool.totalLP) / pool.reserveB;
      lpTokens = Math.min(shareA, shareB);
    }

    if (lpTokens <= 0) {
      throw new Error('Insufficient liquidity amount provided');
    }

    // Update pool reserves and total LP
    pool.reserveA += amtForReserveA;
    pool.reserveB += amtForReserveB;
    pool.totalLP += lpTokens;

    // Update provider's LP token balance
    const currentLP = pool.lpBalances.get(provider) ?? 0;
    pool.lpBalances.set(provider, currentLP + lpTokens);

    this.notifyStateChange();
    return { lpTokens, pool };
  }

  /**
   * Removes liquidity from a pool.
   * Returns proportional share of reserves. Burns LP tokens.
   */
  public removeLiquidity(
    provider: string,
    poolId: string,
    lpAmount: number
  ): { amountA: number; amountB: number } {
    if (lpAmount <= 0) {
      throw new Error('LP amount to remove must be greater than zero');
    }

    const pool = this.getPool(poolId);
    if (!pool) {
      throw new Error(`Pool ${poolId} not found`);
    }

    const userLP = pool.lpBalances.get(provider) ?? 0;
    if (userLP < lpAmount) {
      throw new Error(`Insufficient LP token balance. Has: ${userLP}, Requested: ${lpAmount}`);
    }

    if (pool.totalLP <= 0) {
      throw new Error('Pool has no liquidity');
    }

    const amountA = (lpAmount * pool.reserveA) / pool.totalLP;
    const amountB = (lpAmount * pool.reserveB) / pool.totalLP;

    // Update reserves and total LP
    pool.reserveA -= amountA;
    pool.reserveB -= amountB;
    pool.totalLP -= lpAmount;
    pool.lpBalances.set(provider, userLP - lpAmount);

    // Credit user non-native token balances if tracked
    this.addTokenBalanceIfTracked(pool.tokenA, provider, amountA);
    this.addTokenBalanceIfTracked(pool.tokenB, provider, amountB);

    this.notifyStateChange();
    return { amountA, amountB };
  }

  /**
   * Performs a token swap using the constant product formula x * y = k.
   * Calculates amountOut = (reserveOut * amountIn * (1-fee)) / (reserveIn + amountIn * (1-fee)).
   * Applies the pool fee (default 0.3%). Enforces slippage protection via minAmountOut.
   */
  public swap(
    trader: string,
    tokenIn: string,
    tokenOut: string,
    amountIn: number,
    minAmountOut: number
  ): { amountOut: number; fee: number; pool: LiquidityPool } {
    if (amountIn <= 0) {
      throw new Error('Swap input amount must be greater than zero');
    }

    const poolId = this.getPoolId(tokenIn, tokenOut);
    const pool = this.getPool(poolId);
    if (!pool) {
      throw new Error(`Pool not found for ${tokenIn} and ${tokenOut}`);
    }

    const isTokenAIn = tokenIn === pool.tokenA;
    const reserveIn = isTokenAIn ? pool.reserveA : pool.reserveB;
    const reserveOut = isTokenAIn ? pool.reserveB : pool.reserveA;

    if (reserveIn <= 0 || reserveOut <= 0) {
      throw new Error('Insufficient liquidity in pool to complete swap');
    }

    // Deduct trader balance for tokenIn if tracked
    this.deductTokenBalanceIfTracked(tokenIn, trader, amountIn);

    const fee = amountIn * pool.fee;
    const amountInWithFee = amountIn * (1 - pool.fee);
    const amountOut = (reserveOut * amountInWithFee) / (reserveIn + amountInWithFee);

    if (amountOut < minAmountOut) {
      throw new Error(`Slippage limit exceeded: expected at least ${minAmountOut}, got ${amountOut}`);
    }

    // Update pool reserves
    if (isTokenAIn) {
      pool.reserveA += amountIn;
      pool.reserveB -= amountOut;
    } else {
      pool.reserveB += amountIn;
      pool.reserveA -= amountOut;
    }

    // Credit trader balance for tokenOut if tracked
    this.addTokenBalanceIfTracked(tokenOut, trader, amountOut);

    this.notifyStateChange();
    return { amountOut, fee, pool };
  }

  /**
   * Returns the current spot price ratio from the pool (price of tokenIn in terms of tokenOut).
   */
  public getPrice(tokenIn: string, tokenOut: string): number {
    const poolId = this.getPoolId(tokenIn, tokenOut);
    const pool = this.getPool(poolId);
    if (!pool) {
      throw new Error(`Pool not found for ${tokenIn} and ${tokenOut}`);
    }

    if (tokenIn === pool.tokenA) {
      if (pool.reserveA === 0) return 0;
      return pool.reserveB / pool.reserveA;
    } else {
      if (pool.reserveB === 0) return 0;
      return pool.reserveA / pool.reserveB;
    }
  }

  /**
   * Returns the LP token balance for a provider in a given pool.
   */
  public getLPTokenBalance(provider: string, poolId: string): number {
    const pool = this.getPool(poolId);
    if (!pool) return 0;
    return pool.lpBalances.get(provider) ?? 0;
  }

  /**
   * Returns pool statistics including reserves, total LP, price, and TVL.
   */
  public getPoolStats(poolId: string): {
    reserveA: number;
    reserveB: number;
    totalLP: number;
    price: number;
    tvl: number;
  } {
    const pool = this.getPool(poolId);
    if (!pool) {
      throw new Error(`Pool ${poolId} not found`);
    }

    const price = pool.reserveA > 0 ? pool.reserveB / pool.reserveA : 0;
    // Total Value Locked (TVL) in terms of tokenB: reserveA * price + reserveB = 2 * reserveB
    const tvl = pool.reserveA > 0 && pool.reserveB > 0 ? 2 * pool.reserveB : 0;

    return {
      reserveA: pool.reserveA,
      reserveB: pool.reserveB,
      totalLP: pool.totalLP,
      price,
      tvl,
    };
  }

  /**
   * Calculates estimated output amount for a potential swap without executing it.
   */
  public quoteSwap(tokenIn: string, tokenOut: string, amountIn: number): { amountOut: number; fee: number; priceImpact: number } {
    if (amountIn <= 0) {
      return { amountOut: 0, fee: 0, priceImpact: 0 };
    }

    const poolId = this.getPoolId(tokenIn, tokenOut);
    const pool = this.getPool(poolId);
    if (!pool) {
      throw new Error(`Pool not found for ${tokenIn} and ${tokenOut}`);
    }

    const isTokenAIn = tokenIn === pool.tokenA;
    const reserveIn = isTokenAIn ? pool.reserveA : pool.reserveB;
    const reserveOut = isTokenAIn ? pool.reserveB : pool.reserveA;

    if (reserveIn <= 0 || reserveOut <= 0) {
      return { amountOut: 0, fee: 0, priceImpact: 0 };
    }

    const fee = amountIn * pool.fee;
    const amountInWithFee = amountIn * (1 - pool.fee);
    const amountOut = (reserveOut * amountInWithFee) / (reserveIn + amountInWithFee);

    // Calculate price impact relative to spot price
    const spotPrice = reserveOut / reserveIn;
    const executionPrice = amountOut / amountIn;
    const priceImpact = Math.max(0, (spotPrice - executionPrice) / spotPrice);

    return { amountOut, fee, priceImpact };
  }

  // --- Non-native Token Balance Tracking ---

  public setTokenBalance(token: string, address: string, amount: number): void {
    if (!this.tokenBalances.has(token)) {
      this.tokenBalances.set(token, new Map<string, number>());
    }
    this.tokenBalances.get(token)!.set(address, Math.max(0, amount));
    this.notifyStateChange();
  }

  public getTokenBalance(token: string, address: string): number {
    const userMap = this.tokenBalances.get(token);
    if (!userMap) return 0;
    return userMap.get(address) ?? 0;
  }

  public depositToken(token: string, address: string, amount: number): number {
    const current = this.getTokenBalance(token, address);
    const updated = current + amount;
    this.setTokenBalance(token, address, updated);
    return updated;
  }

  // --- Carbon Credit / Eco Trading support ---

  /**
   * Registers a carbon credit token for eco-friendly trading on RojsChain.
   */
  public registerCarbonToken(details: CarbonCreditToken): void {
    this.carbonTokens.set(details.symbol, details);
    this.notifyStateChange();
  }

  /**
   * Fetches metadata for a registered carbon credit token.
   */
  public getCarbonToken(symbol: string): CarbonCreditToken | undefined {
    return this.carbonTokens.get(symbol);
  }

  /**
   * Returns all registered carbon credit tokens.
   */
  public getAllCarbonTokens(): CarbonCreditToken[] {
    return Array.from(this.carbonTokens.values());
  }

  /**
   * Helper method to generate a transaction hash representation for DEX actions.
   */
  public generateActionTxHash(action: string, actor: string, details: string): string {
    const payload = `${action}:${actor}:${details}:${Date.now()}`;
    return sha256(payload);
  }

  /**
   * Exports all DEX pools, balances, and carbon tokens.
   */
  public exportState(): {
    pools: Array<{
      id: string;
      tokenA: string;
      tokenB: string;
      reserveA: number;
      reserveB: number;
      totalLP: number;
      fee: number;
      lpBalances: [string, number][];
      createdAt: number;
    }>;
    tokenBalances: Array<[string, [string, number][]]>;
    carbonTokens: Array<[string, CarbonCreditToken]>;
  } {
    const poolsSerialized = Array.from(this.pools.values()).map(pool => ({
      ...pool,
      lpBalances: Array.from(pool.lpBalances.entries()),
    }));

    const tokenBalancesSerialized = Array.from(this.tokenBalances.entries()).map(([token, map]) => [
      token,
      Array.from(map.entries()),
    ] as [string, [string, number][]]);

    const carbonTokensSerialized = Array.from(this.carbonTokens.entries());

    return {
      pools: poolsSerialized,
      tokenBalances: tokenBalancesSerialized,
      carbonTokens: carbonTokensSerialized,
    };
  }

  /**
   * Restores DEX pools, balances, and carbon tokens.
   */
  public importState(data: {
    pools?: any[];
    tokenBalances?: Array<[string, any]>;
    carbonTokens?: Array<[string, CarbonCreditToken]>;
  }): void {
    if (!data) return;
    if (Array.isArray(data.pools)) {
      this.pools.clear();
      for (const p of data.pools) {
        let lpBalancesMap = new Map<string, number>();
        if (Array.isArray(p.lpBalances)) {
          lpBalancesMap = new Map(p.lpBalances);
        } else if (p.lpBalances && typeof p.lpBalances === 'object') {
          lpBalancesMap = new Map(Object.entries(p.lpBalances));
        }
        this.pools.set(p.id, {
          ...p,
          lpBalances: lpBalancesMap,
        });
      }
    }

    if (Array.isArray(data.tokenBalances)) {
      this.tokenBalances.clear();
      for (const [token, entries] of data.tokenBalances) {
        if (Array.isArray(entries)) {
          this.tokenBalances.set(token, new Map(entries));
        } else if (entries && typeof entries === 'object') {
          this.tokenBalances.set(token, new Map(Object.entries(entries) as [string, number][]));
        }
      }
    }

    if (Array.isArray(data.carbonTokens)) {
      this.carbonTokens.clear();
      for (const [symbol, token] of data.carbonTokens) {
        this.carbonTokens.set(symbol, token);
      }
    }
  }

  // --- Private Helpers ---

  private deductTokenBalanceIfTracked(token: string, address: string, amount: number): void {
    const userMap = this.tokenBalances.get(token);
    if (userMap && userMap.has(address)) {
      const current = userMap.get(address) ?? 0;
      if (current < amount) {
        throw new Error(`Insufficient ${token} balance for ${address}. Required: ${amount}, Available: ${current}`);
      }
      userMap.set(address, current - amount);
    }
  }

  private addTokenBalanceIfTracked(token: string, address: string, amount: number): void {
    const userMap = this.tokenBalances.get(token);
    if (userMap) {
      const current = userMap.get(address) ?? 0;
      userMap.set(address, current + amount);
    }
  }
}
