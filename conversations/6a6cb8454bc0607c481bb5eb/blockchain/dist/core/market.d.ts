/**
 * Token Market Data & Volume Tracking
 *
 * Extends DEX with volume tracking, price history, and market data.
 * Makes VCO a live, tradable token with real market activity.
 */
import { DEX } from './dex';
export interface SwapRecord {
    timestamp: number;
    trader: string;
    tokenIn: string;
    tokenOut: string;
    amountIn: number;
    amountOut: number;
    fee: number;
    poolId: string;
    blockNumber: number;
}
export interface PricePoint {
    timestamp: number;
    blockNumber: number;
    price: number;
    poolId: string;
    pair: string;
}
export interface MarketStats {
    symbol: string;
    priceUSD: number;
    priceChange24h: number;
    volume24h: number;
    totalVolume: number;
    totalSwaps: number;
    liquidity: number;
    marketCap: number;
    circulatingSupply: number;
    pools: Array<{
        pair: string;
        price: number;
        reserves: {
            tokenA: string;
            tokenB: string;
            reserveA: number;
            reserveB: number;
        };
        tvl: number;
        volume24h: number;
        swaps24h: number;
    }>;
    recentSwaps: SwapRecord[];
    priceHistory: PricePoint[];
}
/**
 * Wraps the DEX to add market data tracking.
 * Must be called on every swap to record the trade.
 */
export declare class MarketTracker {
    private dex;
    private swapHistory;
    private priceHistory;
    private totalVolumeAllTime;
    private totalSwapCount;
    constructor(dex: DEX);
    /**
     * Records a swap after it executes. Called by the API layer.
     */
    recordSwap(trader: string, tokenIn: string, tokenOut: string, amountIn: number, amountOut: number, fee: number, poolId: string, blockNumber: number): void;
    /**
     * Records a price snapshot for all pools.
     */
    recordPrices(blockNumber: number): void;
    /**
     * Returns comprehensive market statistics for a given token.
     */
    getMarketStats(tokenSymbol: string, circulatingSupply: number, maxSupply: number): MarketStats;
    /**
     * Returns recent swap history.
     */
    getSwapHistory(limit?: number): SwapRecord[];
    /**
     * Returns price history for a pool.
     */
    getPriceHistory(poolId: string, limit?: number): PricePoint[];
    /**
     * Serializes market data for persistence.
     */
    exportData(): any;
    /**
     * Restores market data from persistence.
     */
    importData(data: any): void;
}
