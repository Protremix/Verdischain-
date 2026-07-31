/**
 * Liquidity pool structure representing an Automated Market Maker (AMM) pool.
 */
export interface LiquidityPool {
    id: string;
    tokenA: string;
    tokenB: string;
    reserveA: number;
    reserveB: number;
    totalLP: number;
    fee: number;
    lpBalances: Map<string, number>;
    createdAt: number;
}
/**
 * Interface representing carbon credit token metadata for eco-focused trading.
 */
export interface CarbonCreditToken {
    symbol: string;
    name: string;
    projectCategory: string;
    certificationStandard: string;
    vintageYear: number;
    totalIssued: number;
}
/**
 * AMM-based Decentralized Exchange (DEX) supporting liquidity provision,
 * token swapping, LP token minting/burning, and carbon credit trading.
 */
export declare class DEX {
    private pools;
    private tokenBalances;
    private carbonTokens;
    constructor();
    /**
     * Generates a deterministic pool ID by sorting token names alphabetically
     * and concatenating with '_' (e.g. 'ECO' and 'TREE' -> 'ECO_TREE').
     */
    getPoolId(tokenA: string, tokenB: string): string;
    /**
     * Creates a new liquidity pool if it doesn't already exist.
     * Ensures tokenA and tokenB are sorted alphabetically in the pool.
     */
    createPool(tokenA: string, tokenB: string, fee?: number): LiquidityPool;
    /**
     * Gets a pool by its ID. Supports looking up via canonical or inverted ID.
     */
    getPool(poolId: string): LiquidityPool | undefined;
    /**
     * Returns all liquidity pools.
     */
    getAllPools(): LiquidityPool[];
    /**
     * Adds liquidity to a pool.
     * If the pool is new, LP tokens = sqrt(amountA * amountB).
     * If pool exists, LP tokens = min(amountA * totalLP / reserveA, amountB * totalLP / reserveB).
     * Updates reserves and LP balance.
     */
    addLiquidity(provider: string, tokenA: string, tokenB: string, amountA: number, amountB: number): {
        lpTokens: number;
        pool: LiquidityPool;
    };
    /**
     * Removes liquidity from a pool.
     * Returns proportional share of reserves. Burns LP tokens.
     */
    removeLiquidity(provider: string, poolId: string, lpAmount: number): {
        amountA: number;
        amountB: number;
    };
    /**
     * Performs a token swap using the constant product formula x * y = k.
     * Calculates amountOut = (reserveOut * amountIn * (1-fee)) / (reserveIn + amountIn * (1-fee)).
     * Applies the pool fee (default 0.3%). Enforces slippage protection via minAmountOut.
     */
    swap(trader: string, tokenIn: string, tokenOut: string, amountIn: number, minAmountOut: number): {
        amountOut: number;
        fee: number;
        pool: LiquidityPool;
    };
    /**
     * Returns the current spot price ratio from the pool (price of tokenIn in terms of tokenOut).
     */
    getPrice(tokenIn: string, tokenOut: string): number;
    /**
     * Returns the LP token balance for a provider in a given pool.
     */
    getLPTokenBalance(provider: string, poolId: string): number;
    /**
     * Returns pool statistics including reserves, total LP, price, and TVL.
     */
    getPoolStats(poolId: string): {
        reserveA: number;
        reserveB: number;
        totalLP: number;
        price: number;
        tvl: number;
    };
    /**
     * Quotes a swap without executing it or altering pool state.
     * Calculates price impact as the percentage change in spot price caused by the swap.
     */
    quoteSwap(tokenIn: string, tokenOut: string, amountIn: number): {
        amountOut: number;
        fee: number;
        priceImpact: number;
    };
    getTokenBalance(token: string, address: string): number;
    setTokenBalance(token: string, address: string, balance: number): void;
    depositToken(token: string, address: string, amount: number): number;
    /**
     * Registers a carbon credit token for eco-friendly trading on RojsChain.
     */
    registerCarbonToken(details: CarbonCreditToken): void;
    /**
     * Fetches metadata for a registered carbon credit token.
     */
    getCarbonToken(symbol: string): CarbonCreditToken | undefined;
    /**
     * Returns all registered carbon credit tokens.
     */
    getAllCarbonTokens(): CarbonCreditToken[];
    /**
     * Helper method to generate a transaction hash representation for DEX actions.
     */
    generateActionTxHash(action: string, actor: string, details: string): string;
    private deductTokenBalanceIfTracked;
    private addTokenBalanceIfTracked;
}
