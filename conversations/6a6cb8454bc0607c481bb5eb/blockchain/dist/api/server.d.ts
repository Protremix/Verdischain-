import { Express } from 'express';
import { Blockchain } from '../core/consensus';
import { WalletManager } from '../wallet/wallet';
import { ContractManager } from '../core/vm';
import { SecurityManager } from '../core/security';
export declare class BlockchainAPI {
    private app;
    private blockchain;
    private walletManager;
    private contractManager;
    private dashboardHtmlPath?;
    private dex;
    private marketTracker;
    private eco;
    security: SecurityManager;
    startTime: number;
    constructor(blockchain: Blockchain, walletManager: WalletManager, contractManager: ContractManager);
    private requireAdminAuth;
    private strictRateLimit;
    setDEX(dex: any): void;
    setMarketTracker(mt: any): void;
    setEco(eco: any): void;
    serveDashboard(filePath?: string): void;
    private setupCoreRoutes;
    private setupDEXRoutes;
    private setupEcoRoutes;
    start(port: number): void;
    getApp(): Express;
}
