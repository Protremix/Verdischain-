"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DEX = void 0;
const crypto_1 = require("../crypto");
/**
 * AMM-based Decentralized Exchange (DEX) supporting liquidity provision,
 * token swapping, LP token minting/burning, and carbon credit trading.
 */
class DEX {
    constructor() {
        this.pools = new Map();
        this.tokenBalances = new Map();
        this.carbonTokens = new Map();
    }
    /**
     * Generates a deterministic pool ID by sorting token names alphabetically
     * and concatenating with '_' (e.g. 'ECO' and 'TREE' -> 'ECO_TREE').
     */
    getPoolId(tokenA, tokenB) {
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
    createPool(tokenA, tokenB, fee = 0.003) {
        const poolId = this.getPoolId(tokenA, tokenB);
        const existing = this.getPool(poolId);
        if (existing) {
            return existing;
        }
        const [sortedA, sortedB] = [tokenA, tokenB].sort();
        const newPool = {
            id: poolId,
            tokenA: sortedA,
            tokenB: sortedB,
            reserveA: 0,
            reserveB: 0,
            totalLP: 0,
            fee,
            lpBalances: new Map(),
            createdAt: Date.now(),
        };
        this.pools.set(poolId, newPool);
        return newPool;
    }
    /**
     * Gets a pool by its ID. Supports looking up via canonical or inverted ID.
     */
    getPool(poolId) {
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
    getAllPools() {
        return Array.from(this.pools.values());
    }
    /**
     * Adds liquidity to a pool.
     * If the pool is new, LP tokens = sqrt(amountA * amountB).
     * If pool exists, LP tokens = min(amountA * totalLP / reserveA, amountB * totalLP / reserveB).
     * Updates reserves and LP balance.
     */
    addLiquidity(provider, tokenA, tokenB, amountA, amountB) {
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
        let lpTokens;
        if (pool.totalLP === 0 || pool.reserveA === 0 || pool.reserveB === 0) {
            lpTokens = Math.sqrt(amtForReserveA * amtForReserveB);
        }
        else {
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
        return { lpTokens, pool };
    }
    /**
     * Removes liquidity from a pool.
     * Returns proportional share of reserves. Burns LP tokens.
     */
    removeLiquidity(provider, poolId, lpAmount) {
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
        return { amountA, amountB };
    }
    /**
     * Performs a token swap using the constant product formula x * y = k.
     * Calculates amountOut = (reserveOut * amountIn * (1-fee)) / (reserveIn + amountIn * (1-fee)).
     * Applies the pool fee (default 0.3%). Enforces slippage protection via minAmountOut.
     */
    swap(trader, tokenIn, tokenOut, amountIn, minAmountOut) {
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
        }
        else {
            pool.reserveB += amountIn;
            pool.reserveA -= amountOut;
        }
        // Credit trader balance for tokenOut if tracked
        this.addTokenBalanceIfTracked(tokenOut, trader, amountOut);
        return { amountOut, fee, pool };
    }
    /**
     * Returns the current spot price ratio from the pool (price of tokenIn in terms of tokenOut).
     */
    getPrice(tokenIn, tokenOut) {
        const poolId = this.getPoolId(tokenIn, tokenOut);
        const pool = this.getPool(poolId);
        if (!pool) {
            throw new Error(`Pool not found for ${tokenIn} and ${tokenOut}`);
        }
        if (tokenIn === pool.tokenA) {
            if (pool.reserveA === 0)
                return 0;
            return pool.reserveB / pool.reserveA;
        }
        else {
            if (pool.reserveB === 0)
                return 0;
            return pool.reserveA / pool.reserveB;
        }
    }
    /**
     * Returns the LP token balance for a provider in a given pool.
     */
    getLPTokenBalance(provider, poolId) {
        const pool = this.getPool(poolId);
        if (!pool)
            return 0;
        return pool.lpBalances.get(provider) ?? 0;
    }
    /**
     * Returns pool statistics including reserves, total LP, price, and TVL.
     */
    getPoolStats(poolId) {
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
     * Quotes a swap without executing it or altering pool state.
     * Calculates price impact as the percentage change in spot price caused by the swap.
     */
    quoteSwap(tokenIn, tokenOut, amountIn) {
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
        // Initial spot price before swap
        const spotPriceBefore = reserveOut / reserveIn;
        // Spot price after swap would be completed
        const newReserveIn = reserveIn + amountIn;
        const newReserveOut = reserveOut - amountOut;
        const spotPriceAfter = newReserveOut / newReserveIn;
        // Percentage change in spot price
        const priceImpact = spotPriceBefore > 0
            ? ((spotPriceBefore - spotPriceAfter) / spotPriceBefore) * 100
            : 0;
        return {
            amountOut,
            fee,
            priceImpact: Math.max(0, priceImpact),
        };
    }
    // --- Non-native token management helpers ---
    getTokenBalance(token, address) {
        return this.tokenBalances.get(token)?.get(address) ?? 0;
    }
    setTokenBalance(token, address, balance) {
        if (!this.tokenBalances.has(token)) {
            this.tokenBalances.set(token, new Map());
        }
        this.tokenBalances.get(token).set(address, Math.max(0, balance));
    }
    depositToken(token, address, amount) {
        const current = this.getTokenBalance(token, address);
        const updated = current + amount;
        this.setTokenBalance(token, address, updated);
        return updated;
    }
    // --- Carbon Credit / Eco Trading support ---
    /**
     * Registers a carbon credit token for eco-friendly trading on RojsChain.
     */
    registerCarbonToken(details) {
        this.carbonTokens.set(details.symbol, details);
    }
    /**
     * Fetches metadata for a registered carbon credit token.
     */
    getCarbonToken(symbol) {
        return this.carbonTokens.get(symbol);
    }
    /**
     * Returns all registered carbon credit tokens.
     */
    getAllCarbonTokens() {
        return Array.from(this.carbonTokens.values());
    }
    /**
     * Helper method to generate a transaction hash representation for DEX actions.
     */
    generateActionTxHash(action, actor, details) {
        const payload = `${action}:${actor}:${details}:${Date.now()}`;
        return (0, crypto_1.sha256)(payload);
    }
    // --- Private Helpers ---
    deductTokenBalanceIfTracked(token, address, amount) {
        const userMap = this.tokenBalances.get(token);
        if (userMap && userMap.has(address)) {
            const current = userMap.get(address) ?? 0;
            if (current < amount) {
                throw new Error(`Insufficient ${token} balance for ${address}. Required: ${amount}, Available: ${current}`);
            }
            userMap.set(address, current - amount);
        }
    }
    addTokenBalanceIfTracked(token, address, amount) {
        const userMap = this.tokenBalances.get(token);
        if (userMap) {
            const current = userMap.get(address) ?? 0;
            userMap.set(address, current + amount);
        }
    }
}
exports.DEX = DEX;
//# sourceMappingURL=dex.js.map