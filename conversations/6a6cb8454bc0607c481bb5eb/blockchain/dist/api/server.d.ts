import { Express } from 'express';
import { Blockchain } from '../core/consensus';
import { WalletManager } from '../wallet/wallet';
import { ContractManager } from '../core/vm';
export declare class BlockchainAPI {
    private app;
    private blockchain;
    private walletManager;
    private contractManager;
    private dashboardHtmlPath?;
    constructor(blockchain: Blockchain, walletManager: WalletManager, contractManager: ContractManager);
    private setupMiddleware;
    serveDashboard(filePath?: string): void;
    private setupRoutes;
    start(port: number): void;
    getApp(): Express;
}
