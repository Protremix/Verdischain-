import express, { Express, Request, Response } from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { Blockchain } from '../core/consensus';
import { WalletManager } from '../wallet/wallet';
import { ContractManager, compileContract } from '../core/vm';
import { getPublicKeyFromPrivateKey, getAddressFromPublicKey } from '../crypto';

export class BlockchainAPI {
  private app: Express;
  private blockchain: Blockchain;
  private walletManager: WalletManager;
  private contractManager: ContractManager;
  private dashboardHtmlPath?: string;
  private dex: any = null;
  private eco: any = null;

  constructor(
    blockchain: Blockchain,
    walletManager: WalletManager,
    contractManager: ContractManager
  ) {
    this.blockchain = blockchain;
    this.walletManager = walletManager;
    this.contractManager = contractManager;
    this.app = express();
    this.app.use(cors());
    this.app.use(express.json({ limit: '10mb' }));
    this.setupCoreRoutes();
  }

  public setDEX(dex: any): void {
    this.dex = dex;
    this.setupDEXRoutes();
  }

  public setEco(eco: any): void {
    this.eco = eco;
    this.setupEcoRoutes();
  }

  public serveDashboard(filePath?: string): void {
    if (filePath && fs.existsSync(filePath)) {
      this.dashboardHtmlPath = filePath;
    }
  }

  private setupCoreRoutes(): void {
    // Dashboard
    this.app.get('/', (req: Request, res: Response) => {
      if (this.dashboardHtmlPath && fs.existsSync(this.dashboardHtmlPath)) {
        res.sendFile(this.dashboardHtmlPath);
        return;
      }
      const defaultPath = path.resolve(__dirname, '../web/dashboard.html');
      if (fs.existsSync(defaultPath)) { res.sendFile(defaultPath); return; }
      res.send(`<html><body style="background:#0a0e1a;color:#00e676;font-family:sans-serif;padding:2rem"><h1>🌿 Verdis</h1><p>Height: ${this.blockchain.getChainHeight()}</p></body></html>`);
    });

    // Blockchain Info
    this.app.get('/api/blockchain/info', (req: Request, res: Response) => {
      const state = this.blockchain.getState();
      res.json({
        height: state.currentHeight,
        totalSupply: state.totalSupply,
        maxSupply: state.maxSupply,
        validatorCount: state.validatorCount,
        blockReward: state.blockReward,
        mempoolSize: this.blockchain.getMempool().size(),
        chainValid: this.blockchain.isChainValid(),
      });
    });

    this.app.get('/api/blockchain/blocks', (req: Request, res: Response) => {
      const limit = parseInt(req.query.limit as string) || 20;
      const offset = parseInt(req.query.offset as string) || 0;
      const chain = this.blockchain.getChain();
      res.json(chain.slice().reverse().slice(offset, offset + limit));
    });

    this.app.get('/api/blockchain/block/:index', (req: Request, res: Response) => {
      const block = this.blockchain.getBlockByIndex(parseInt(req.params.index));
      if (!block) { res.status(404).json({ error: 'Block not found' }); return; }
      res.json(block);
    });

    this.app.get('/api/blockchain/block/hash/:hash', (req: Request, res: Response) => {
      const block = this.blockchain.getBlockByHash(req.params.hash);
      if (!block) { res.status(404).json({ error: 'Block not found' }); return; }
      res.json(block);
    });

    // Wallet
    this.app.post('/api/wallet/create', (req: Request, res: Response) => {
      const wallet = this.walletManager.createWallet();
      res.json({
        privateKey: wallet.privateKey,
        publicKey: wallet.publicKey,
        address: wallet.address,
        balance: this.blockchain.getTokenSystem().getBalance(wallet.address),
        staked: this.blockchain.getTokenSystem().getStaked(wallet.address),
      });
    });

    this.app.get('/api/wallet/:address/balance', (req: Request, res: Response) => {
      res.json({ address: req.params.address, balance: this.blockchain.getTokenSystem().getBalance(req.params.address) });
    });

    this.app.get('/api/wallet/:address/staked', (req: Request, res: Response) => {
      res.json({ address: req.params.address, staked: this.blockchain.getTokenSystem().getStaked(req.params.address) });
    });

    // Transactions
    this.app.post('/api/transaction/send', (req: Request, res: Response) => {
      const { privateKey, from, to, amount, fee, data } = req.body;
      let wallet = this.walletManager.getAllWallets().find(w => w.address === from || w.publicKey === from);
      if (!wallet && privateKey) { wallet = this.walletManager.importWallet(privateKey); }

      if (!wallet) {
        const publicKey = privateKey ? getPublicKeyFromPrivateKey(privateKey) : from;
        const { signTransaction } = require('../crypto');
        const tx = signTransaction(privateKey, to, amount, fee || 1, Date.now(), data || null, publicKey);
        const result = this.blockchain.submitTransaction(tx);
        if (!result.success) { res.status(400).json({ error: result.error }); return; }
        res.json({ txId: tx.id, transaction: tx });
        return;
      }

      const tx = this.walletManager.signTransaction(wallet, to, amount, fee || 1, Date.now(), data);
      const result = this.blockchain.submitTransaction(tx);
      if (!result.success) { res.status(400).json({ error: result.error }); return; }
      res.json({ txId: tx.id, transaction: tx });
    });

    this.app.get('/api/transaction/:txId', (req: Request, res: Response) => {
      res.json(this.blockchain.getTransactionReceipt(req.params.txId));
    });

    this.app.get('/api/mempool', (req: Request, res: Response) => {
      res.json(this.blockchain.getMempool().getTransactions());
    });

    this.app.get('/api/mempool/size', (req: Request, res: Response) => {
      res.json({ size: this.blockchain.getMempool().size() });
    });

    // Validators & Staking
    this.app.get('/api/validators', (req: Request, res: Response) => {
      res.json(this.blockchain.getConsensus().getAllValidatorsList());
    });

    this.app.get('/api/validators/top', (req: Request, res: Response) => {
      res.json(this.blockchain.getConsensus().getTopValidators());
    });

    this.app.post('/api/validators/register', (req: Request, res: Response) => {
      const { publicKey, address } = req.body;
      res.json({ success: true, validator: this.blockchain.getConsensus().registerValidator(publicKey, address) });
    });

    this.app.post('/api/validators/vote', (req: Request, res: Response) => {
      const { voterAddress, validatorAddress, amount } = req.body;
      res.json({ success: this.blockchain.getConsensus().vote(voterAddress, validatorAddress, amount, this.blockchain.getTokenSystem()) });
    });

    this.app.post('/api/stake', (req: Request, res: Response) => {
      const { address, amount, action } = req.body;
      if (action === 'stake') { res.json({ success: this.blockchain.getTokenSystem().stake(address, amount) }); return; }
      if (action === 'unstake') { res.json({ success: this.blockchain.getTokenSystem().unstake(address, amount) }); return; }
      res.status(400).json({ error: 'Invalid action' });
    });

    // Block Production
    this.app.post('/api/blockchain/produce', (req: Request, res: Response) => {
      const { privateKey, publicKey, address } = req.body;
      const block = this.blockchain.produceBlock(privateKey, publicKey, address);
      if (!block) { res.status(400).json({ error: 'Not your turn to produce a block, or no pending transactions' }); return; }
      res.json({ success: true, block });
    });

    // Smart Contracts
    this.app.post('/api/contract/deploy', (req: Request, res: Response) => {
      const { owner, name, source } = req.body;
      const bytecode = compileContract(source);
      const contract = this.contractManager.deploy(owner, name, bytecode);
      res.json({ success: true, contractId: contract.id, name: contract.name });
    });

    this.app.post('/api/contract/:id/execute', (req: Request, res: Response) => {
      const { input } = req.body;
      res.json(this.contractManager.execute(req.params.id, input));
    });

    this.app.get('/api/contract/:id', (req: Request, res: Response) => {
      const contract = this.contractManager.getContract(req.params.id);
      if (!contract) { res.status(404).json({ error: 'Contract not found' }); return; }
      res.json({ id: contract.id, name: contract.name, owner: contract.owner, deployedAt: contract.deployedAt, bytecode: contract.bytecode });
    });

    this.app.get('/api/contracts', (req: Request, res: Response) => {
      res.json(this.contractManager.getAllContracts().map(c => ({ id: c.id, name: c.name, owner: c.owner, deployedAt: c.deployedAt })));
    });

    this.app.get('/api/contract/:id/state', (req: Request, res: Response) => {
      const contract = this.contractManager.getContract(req.params.id);
      if (!contract || !contract.state) { res.status(404).json({ error: 'Contract not found' }); return; }
      res.json(Object.fromEntries(contract.state));
    });

    // Legacy
    this.app.get('/api/chain', (req: Request, res: Response) => { res.json(this.blockchain.getState()); });
    this.app.get('/api/wallets', (req: Request, res: Response) => { res.json(this.walletManager.getAllWallets()); });
  }

  private setupDEXRoutes(): void {
    if (!this.dex) return;

    this.app.get('/api/dex/pools', (req: Request, res: Response) => { res.json(this.dex.getAllPools()); });

    this.app.post('/api/dex/pool/create', (req: Request, res: Response) => {
      const { tokenA, tokenB } = req.body;
      res.json({ success: true, pool: this.dex.createPool(tokenA, tokenB) });
    });

    this.app.post('/api/dex/liquidity/add', (req: Request, res: Response) => {
      const { provider, tokenA, tokenB, amountA, amountB } = req.body;
      res.json(this.dex.addLiquidity(provider, tokenA, tokenB, amountA, amountB));
    });

    this.app.post('/api/dex/liquidity/remove', (req: Request, res: Response) => {
      const { provider, poolId, lpAmount } = req.body;
      res.json(this.dex.removeLiquidity(provider, poolId, lpAmount));
    });

    this.app.post('/api/dex/swap', (req: Request, res: Response) => {
      const { trader, tokenIn, tokenOut, amountIn, minAmountOut } = req.body;
      const result = this.dex.swap(trader, tokenIn, tokenOut, amountIn, minAmountOut || 0);
      if (result.error) { res.status(400).json(result); return; }
      res.json(result);
    });

    this.app.get('/api/dex/quote', (req: Request, res: Response) => {
      const { tokenIn, tokenOut, amountIn } = req.query;
      res.json(this.dex.quoteSwap(tokenIn as string, tokenOut as string, parseFloat(amountIn as string)));
    });

    this.app.get('/api/dex/pool/:id/stats', (req: Request, res: Response) => {
      res.json(this.dex.getPoolStats(req.params.id));
    });
  }

  private setupEcoRoutes(): void {
    if (!this.eco) return;

    this.app.get('/api/eco/impact', (req: Request, res: Response) => { res.json(this.eco.getNetworkImpact()); });

    // Carbon Credits
    this.app.post('/api/eco/carbon/mint', (req: Request, res: Response) => {
      const { seller, projectType, amount, price, location, metadata } = req.body;
      res.json({ success: true, credit: this.eco.mintCarbonCredit(seller, projectType, amount, price, location, metadata) });
    });

    this.app.post('/api/eco/carbon/verify', (req: Request, res: Response) => {
      const { creditId, verifier } = req.body;
      res.json(this.eco.verifyCarbonCredit(creditId, verifier));
    });

    this.app.post('/api/eco/carbon/buy', (req: Request, res: Response) => {
      const { creditId, buyer, amount } = req.body;
      res.json(this.eco.buyCarbonCredit(creditId, buyer, amount));
    });

    this.app.post('/api/eco/carbon/retire', (req: Request, res: Response) => {
      const { creditId, by } = req.body;
      res.json(this.eco.retireCarbonCredit(creditId, by));
    });

    this.app.get('/api/eco/carbon/credits', (req: Request, res: Response) => {
      const filter: any = {};
      if (req.query.status) filter.status = req.query.status;
      if (req.query.projectType) filter.projectType = req.query.projectType;
      res.json(this.eco.getCarbonCredits(Object.keys(filter).length ? filter : undefined));
    });

    // Green Validators
    this.app.post('/api/eco/green/register', (req: Request, res: Response) => {
      const { address, energySource } = req.body;
      res.json({ success: true, score: this.eco.registerGreenValidator(address, energySource) });
    });

    this.app.get('/api/eco/green/top', (req: Request, res: Response) => {
      res.json(this.eco.getTopGreenValidators(parseInt(req.query.n as string) || 10));
    });

    this.app.get('/api/eco/green/:address', (req: Request, res: Response) => {
      res.json(this.eco.getGreenScore(req.params.address) || { error: 'No green score found' });
    });

    // Reforestation
    this.app.post('/api/eco/reforest/create', (req: Request, res: Response) => {
      const { owner, name, location, area, treesTarget, species } = req.body;
      res.json({ success: true, project: this.eco.createReforestationProject(owner, name, location, area, treesTarget, species) });
    });

    this.app.post('/api/eco/reforest/update', (req: Request, res: Response) => {
      const { projectId, treesPlanted } = req.body;
      const project = this.eco.updateReforestationProject(projectId, treesPlanted);
      res.json({ success: !!project, project });
    });

    this.app.post('/api/eco/reforest/verify', (req: Request, res: Response) => {
      const { projectId, verifier } = req.body;
      res.json(this.eco.verifyReforestationProject(projectId, verifier));
    });

    this.app.get('/api/eco/reforest/projects', (req: Request, res: Response) => {
      res.json(this.eco.getReforestationProjects(req.query.status as string | undefined));
    });

    // Carbon Offset Pool
    this.app.get('/api/eco/offset-pool', (req: Request, res: Response) => {
      res.json(this.eco.getCarbonOffsetPool());
    });
  }

  public start(port: number): void {
    this.app.listen(port, () => { console.log(`📡 API server listening on port ${port}`); });
  }

  public getApp(): Express { return this.app; }
}
