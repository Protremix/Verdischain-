import express from 'express';
import { Blockchain } from '../core/consensus';
import { TokenSystem, DPoSConsensus } from '../core/consensus';
import { ContractManager } from '../core/vm';
/**
 * REST API Server for RojsChain blockchain platform.
 * Exposes full blockchain functionality via Express endpoints.
 */
export declare class BlockchainAPI {
    private app;
    private blockchain;
    private contractManager;
    private port;
    constructor(blockchain: Blockchain, contractManager: ContractManager, port: number);
    /**
     * Configures Express middlewares.
     */
    private setupMiddleware;
    /**
     * Sets up all REST API endpoints.
     */
    private setupRoutes;
    /**
     * Starts the Express REST server on the designated port.
     */
    start(): void;
    /**
     * Returns the underlying Express application instance.
     */
    getApp(): express.Application;
}
export { TokenSystem, DPoSConsensus };
