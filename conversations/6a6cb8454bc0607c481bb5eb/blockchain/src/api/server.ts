import express, { Express, Request, Response } from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { Blockchain } from '../core/consensus';
import { WalletManager } from '../wallet/wallet';
import { ContractManager } from '../core/vm';

export class BlockchainAPI {
  private app: Express;
  private blockchain: Blockchain;
  private walletManager: WalletManager;
  private contractManager: ContractManager;
  private dashboardHtmlPath?: string;

  constructor(
    blockchain: Blockchain,
    walletManager: WalletManager,
    contractManager: ContractManager
  ) {
    this.blockchain = blockchain;
    this.walletManager = walletManager;
    this.contractManager = contractManager;
    this.app = express();

    this.setupMiddleware();
    this.setupRoutes();
  }

  private setupMiddleware(): void {
    this.app.use(cors());
    this.app.use(express.json());
  }

  public serveDashboard(filePath?: string): void {
    if (filePath && fs.existsSync(filePath)) {
      this.dashboardHtmlPath = filePath;
    }
  }

  private setupRoutes(): void {
    // Web Dashboard route
    this.app.get('/', (req: Request, res: Response) => {
      if (this.dashboardHtmlPath && fs.existsSync(this.dashboardHtmlPath)) {
        res.sendFile(this.dashboardHtmlPath);
        return;
      }

      const defaultDashboardPath = path.resolve(__dirname, '../web/dashboard.html');
      if (fs.existsSync(defaultDashboardPath)) {
        res.sendFile(defaultDashboardPath);
        return;
      }

      res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>RojsChain Dashboard</title></head>
        <body style="font-family: sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem;">
          <h1>🚀 RojsChain Node Running</h1>
          <p>Status: Active</p>
          <p>Height: ${this.blockchain.getChain().length - 1}</p>
        </body>
        </html>
      `);
    });

    // API Routes
    this.app.get('/api/chain', (req: Request, res: Response) => {
      res.json(this.blockchain.getState());
    });

    this.app.get('/api/wallets', (req: Request, res: Response) => {
      res.json(this.walletManager.getAllWallets());
    });

    this.app.post('/api/wallets/create', (req: Request, res: Response) => {
      const wallet = this.walletManager.createWallet();
      res.json(wallet);
    });

    this.app.get('/api/validators', (req: Request, res: Response) => {
      const validators = this.blockchain.getConsensus().getAllValidatorsList();
      res.json(validators);
    });

    this.app.post('/api/transactions', (req: Request, res: Response) => {
      const { from, to, amount, fee, nonce, data } = req.body;
      const wallet = this.walletManager.getAllWallets().find(
        (w) => w.publicKey === from || w.address === from
      );

      if (!wallet) {
        res.status(400).json({ error: 'Sender wallet not found in WalletManager' });
        return;
      }

      const tx = this.walletManager.signTransaction(
        wallet,
        to,
        amount,
        fee,
        nonce || 0,
        data
      );
      this.blockchain.getMempool().addTransaction(tx);
      res.json({ status: 'Transaction submitted', transaction: tx });
    });
  }

  public start(port: number): void {
    this.app.listen(port, () => {
      // API Listening
    });
  }

  public getApp(): Express {
    return this.app;
  }
}
