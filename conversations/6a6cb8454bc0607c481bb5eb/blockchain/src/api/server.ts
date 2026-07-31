import express, { Request, Response } from 'express';
import cors from 'cors';
import { Blockchain } from '../core/consensus';
import { TokenSystem, DPoSConsensus } from '../core/consensus';
import { TransactionBuilder } from '../core/transaction';
import { ContractManager, compileContract } from '../core/vm';
import { generateKeyPair, getAddressFromPublicKey } from '../crypto';

/**
 * REST API Server for RojsChain blockchain platform.
 * Exposes full blockchain functionality via Express endpoints.
 */
export class BlockchainAPI {
  private app: express.Application;
  private blockchain: Blockchain;
  private contractManager: ContractManager;
  private port: number;

  constructor(blockchain: Blockchain, contractManager: ContractManager, port: number) {
    this.blockchain = blockchain;
    this.contractManager = contractManager;
    this.port = port;
    this.app = express();

    this.setupMiddleware();
    this.setupRoutes();
  }

  /**
   * Configures Express middlewares.
   */
  private setupMiddleware(): void {
    this.app.use(cors());
    this.app.use(express.json());
  }

  /**
   * Sets up all REST API endpoints.
   */
  private setupRoutes(): void {
    // ------------------------------------------------------------------
    // Wallet Endpoints
    // ------------------------------------------------------------------

    /**
     * POST /api/wallet/create
     * Generates a new wallet (key pair + address).
     */
    this.app.post('/api/wallet/create', (req: Request, res: Response) => {
      try {
        const keyPair = generateKeyPair();
        const address = getAddressFromPublicKey(keyPair.publicKey);
        return res.status(201).json({
          privateKey: keyPair.privateKey,
          publicKey: keyPair.publicKey,
          address,
        });
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to create wallet' });
      }
    });

    /**
     * GET /api/wallet/:address/balance
     * Gets wallet balance.
     */
    this.app.get('/api/wallet/:address/balance', (req: Request, res: Response) => {
      try {
        const { address } = req.params;
        if (!address) {
          return res.status(400).json({ error: 'Address parameter is required' });
        }
        const balance = this.blockchain.getBalance(address);
        return res.json({ address, balance });
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to fetch balance' });
      }
    });

    /**
     * GET /api/wallet/:address/staked
     * Gets staked amount for a wallet.
     */
    this.app.get('/api/wallet/:address/staked', (req: Request, res: Response) => {
      try {
        const { address } = req.params;
        if (!address) {
          return res.status(400).json({ error: 'Address parameter is required' });
        }
        const staked = this.blockchain.getStakedAmount(address);
        return res.json({ address, staked });
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to fetch staked amount' });
      }
    });

    // ------------------------------------------------------------------
    // Transactions Endpoints
    // ------------------------------------------------------------------

    /**
     * POST /api/transaction/send
     * Body: { privateKey, from, to, amount, fee }
     * Creates, signs, and submits a transaction.
     */
    this.app.post('/api/transaction/send', (req: Request, res: Response) => {
      try {
        const { privateKey, from, to, amount, fee } = req.body;

        if (!privateKey || !from || !to || amount === undefined || fee === undefined) {
          return res.status(400).json({
            error: 'Missing required parameters: privateKey, from, to, amount, fee',
          });
        }

        if (typeof amount !== 'number' || amount <= 0) {
          return res.status(400).json({ error: 'Amount must be a positive number' });
        }

        if (typeof fee !== 'number' || fee < 0) {
          return res.status(400).json({ error: 'Fee cannot be negative' });
        }

        const txBuilder = new TransactionBuilder();
        const tx = txBuilder
          .setFrom(from)
          .setTo(to)
          .setAmount(amount)
          .setFee(fee)
          .sign(privateKey)
          .build();

        const txId = this.blockchain.submitTransaction(tx);
        return res.status(201).json({ txId, transaction: tx });
      } catch (err: any) {
        return res.status(400).json({ error: err.message || 'Failed to send transaction' });
      }
    });

    /**
     * GET /api/transaction/:txId
     * Gets transaction receipt and details.
     */
    this.app.get('/api/transaction/:txId', (req: Request, res: Response) => {
      try {
        const { txId } = req.params;
        const receipt = this.blockchain.getTransactionReceipt(txId);
        if (!receipt) {
          return res.status(404).json({ error: `Transaction '${txId}' not found` });
        }
        return res.json(receipt);
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to fetch transaction' });
      }
    });

    /**
     * GET /api/mempool
     * Gets all pending transactions.
     */
    this.app.get('/api/mempool', (req: Request, res: Response) => {
      try {
        const transactions = this.blockchain.getMempool();
        return res.json({ transactions, count: transactions.length });
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to fetch mempool' });
      }
    });

    /**
     * GET /api/mempool/size
     * Gets mempool size.
     */
    this.app.get('/api/mempool/size', (req: Request, res: Response) => {
      try {
        const size = this.blockchain.getMempoolSize();
        return res.json({ size });
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to fetch mempool size' });
      }
    });

    // ------------------------------------------------------------------
    // Blockchain Endpoints
    // ------------------------------------------------------------------

    /**
     * GET /api/blockchain/info
     * Returns chain info: height, totalSupply, maxSupply, validatorCount, blockReward.
     */
    this.app.get('/api/blockchain/info', (req: Request, res: Response) => {
      try {
        const info = this.blockchain.getChainInfo();
        return res.json({
          height: info.height,
          totalSupply: info.totalSupply,
          maxSupply: info.maxSupply,
          validatorCount: info.validatorCount,
          blockReward: info.blockReward,
        });
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to fetch blockchain info' });
      }
    });

    /**
     * GET /api/blockchain/blocks
     * Gets all blocks (paginated: ?limit=20&offset=0).
     */
    this.app.get('/api/blockchain/blocks', (req: Request, res: Response) => {
      try {
        const limit = req.query.limit ? parseInt(req.query.limit as string, 10) : 20;
        const offset = req.query.offset ? parseInt(req.query.offset as string, 10) : 0;

        if (isNaN(limit) || limit <= 0) {
          return res.status(400).json({ error: 'Limit must be a positive integer' });
        }
        if (isNaN(offset) || offset < 0) {
          return res.status(400).json({ error: 'Offset must be a non-negative integer' });
        }

        const blocks = this.blockchain.getBlocks(limit, offset);
        const total = this.blockchain.getChainHeight();
        return res.json({
          blocks,
          total,
          limit,
          offset,
        });
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to fetch blocks' });
      }
    });

    /**
     * GET /api/blockchain/block/:index
     * Gets block by index.
     */
    this.app.get('/api/blockchain/block/:index', (req: Request, res: Response) => {
      try {
        const index = parseInt(req.params.index, 10);
        if (isNaN(index)) {
          return res.status(400).json({ error: 'Block index must be a valid integer' });
        }
        const block = this.blockchain.getBlockByIndex(index);
        if (!block) {
          return res.status(404).json({ error: `Block at index ${index} not found` });
        }
        return res.json(block);
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to fetch block by index' });
      }
    });

    /**
     * GET /api/blockchain/block/hash/:hash
     * Gets block by hash.
     */
    this.app.get('/api/blockchain/block/hash/:hash', (req: Request, res: Response) => {
      try {
        const { hash } = req.params;
        const block = this.blockchain.getBlockByHash(hash);
        if (!block) {
          return res.status(404).json({ error: `Block with hash '${hash}' not found` });
        }
        return res.json(block);
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to fetch block by hash' });
      }
    });

    // ------------------------------------------------------------------
    // Consensus & Staking Endpoints
    // ------------------------------------------------------------------

    /**
     * GET /api/validators
     * Gets all validators.
     */
    this.app.get('/api/validators', (req: Request, res: Response) => {
      try {
        const validators = this.blockchain.getValidators();
        return res.json({ validators });
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to fetch validators' });
      }
    });

    /**
     * GET /api/validators/top
     * Gets top 27 validators (super representatives).
     */
    this.app.get('/api/validators/top', (req: Request, res: Response) => {
      try {
        const topValidators = this.blockchain.getTopValidators(27);
        return res.json({ validators: topValidators });
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to fetch top validators' });
      }
    });

    /**
     * POST /api/validators/register
     * Body: { publicKey }
     * Registers a new validator.
     */
    this.app.post('/api/validators/register', (req: Request, res: Response) => {
      try {
        const { publicKey } = req.body;
        if (!publicKey) {
          return res.status(400).json({ error: 'Missing required parameter: publicKey' });
        }
        const validator = this.blockchain.registerValidator(publicKey);
        return res.status(201).json({ message: 'Validator registered successfully', validator });
      } catch (err: any) {
        return res.status(400).json({ error: err.message || 'Failed to register validator' });
      }
    });

    /**
     * POST /api/validators/vote
     * Body: { privateKey, voterAddress, validatorAddress, amount }
     * Votes for a validator by staking tokens.
     */
    this.app.post('/api/validators/vote', (req: Request, res: Response) => {
      try {
        const { privateKey, voterAddress, validatorAddress, amount } = req.body;
        if (!privateKey || !voterAddress || !validatorAddress || amount === undefined) {
          return res.status(400).json({
            error: 'Missing required parameters: privateKey, voterAddress, validatorAddress, amount',
          });
        }
        if (typeof amount !== 'number' || amount <= 0) {
          return res.status(400).json({ error: 'Vote amount must be a positive number' });
        }
        const stake = this.blockchain.voteForValidator(voterAddress, validatorAddress, amount, privateKey);
        return res.json({ message: 'Vote submitted successfully', stake });
      } catch (err: any) {
        return res.status(400).json({ error: err.message || 'Failed to submit vote' });
      }
    });

    /**
     * POST /api/stake
     * Body: { address, amount, action: 'stake' | 'unstake' }
     * Stakes or unstakes tokens.
     */
    this.app.post('/api/stake', (req: Request, res: Response) => {
      try {
        const { address, amount, action } = req.body;
        if (!address || amount === undefined || !action) {
          return res.status(400).json({
            error: 'Missing required parameters: address, amount, action',
          });
        }
        if (typeof amount !== 'number' || amount <= 0) {
          return res.status(400).json({ error: 'Amount must be a positive number' });
        }
        if (action !== 'stake' && action !== 'unstake') {
          return res.status(400).json({ error: "Action must be either 'stake' or 'unstake'" });
        }

        if (action === 'stake') {
          this.blockchain.stake(address, amount);
          return res.json({ message: 'Successfully staked tokens', address, amount, action });
        } else {
          this.blockchain.unstake(address, amount);
          return res.json({ message: 'Successfully unstaked tokens', address, amount, action });
        }
      } catch (err: any) {
        return res.status(400).json({ error: err.message || 'Failed to process stake operation' });
      }
    });

    /**
     * POST /api/blockchain/produce
     * Body: { privateKey, publicKey }
     * Attempts to produce a block (must be current producer's turn).
     */
    this.app.post('/api/blockchain/produce', (req: Request, res: Response) => {
      try {
        const { privateKey, publicKey } = req.body;
        if (!privateKey || !publicKey) {
          return res.status(400).json({
            error: 'Missing required parameters: privateKey, publicKey',
          });
        }
        const block = this.blockchain.produceBlock(publicKey, privateKey);
        return res.status(201).json({ message: 'Block produced successfully', block });
      } catch (err: any) {
        return res.status(400).json({ error: err.message || 'Failed to produce block' });
      }
    });

    // ------------------------------------------------------------------
    // Smart Contracts Endpoints
    // ------------------------------------------------------------------

    /**
     * POST /api/contract/deploy
     * Body: { owner, name, source }
     * Compiles and deploys a contract, returning the contract ID.
     */
    this.app.post('/api/contract/deploy', (req: Request, res: Response) => {
      try {
        const { owner, name, source } = req.body;
        if (!owner || !name || !source) {
          return res.status(400).json({
            error: 'Missing required parameters: owner, name, source',
          });
        }
        const bytecode = compileContract(source);
        const contract = this.contractManager.deployContract(owner, name, bytecode);
        return res.status(201).json({ contractId: contract.id, contract });
      } catch (err: any) {
        return res.status(400).json({ error: err.message || 'Failed to deploy contract' });
      }
    });

    /**
     * POST /api/contract/:id/execute
     * Body: { input }
     * Executes a contract.
     */
    this.app.post('/api/contract/:id/execute', (req: Request, res: Response) => {
      try {
        const { id } = req.params;
        const { input } = req.body;
        if (input === undefined) {
          return res.status(400).json({ error: 'Missing required parameter: input' });
        }
        const result = this.contractManager.executeContract(id, input);
        return res.json({ result });
      } catch (err: any) {
        return res.status(400).json({ error: err.message || 'Failed to execute contract' });
      }
    });

    /**
     * GET /api/contract/:id
     * Gets contract info by ID.
     */
    this.app.get('/api/contract/:id', (req: Request, res: Response) => {
      try {
        const { id } = req.params;
        const contract = this.contractManager.getContract(id);
        if (!contract) {
          return res.status(404).json({ error: `Contract '${id}' not found` });
        }
        return res.json({ contract });
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to fetch contract' });
      }
    });

    /**
     * GET /api/contracts
     * Lists all deployed contracts.
     */
    this.app.get('/api/contracts', (req: Request, res: Response) => {
      try {
        const contracts = this.contractManager.getAllContracts();
        return res.json({ contracts });
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to list contracts' });
      }
    });

    /**
     * GET /api/contract/:id/state
     * Gets contract state by contract ID.
     */
    this.app.get('/api/contract/:id/state', (req: Request, res: Response) => {
      try {
        const { id } = req.params;
        const state = this.contractManager.getContractState(id);
        if (!state) {
          return res.status(404).json({ error: `Contract '${id}' state not found` });
        }
        const formattedState = state instanceof Map ? Object.fromEntries(state) : state;
        return res.json({ state: formattedState });
      } catch (err: any) {
        return res.status(500).json({ error: err.message || 'Failed to fetch contract state' });
      }
    });

    // ------------------------------------------------------------------
    // Genesis Endpoints
    // ------------------------------------------------------------------

    /**
     * POST /api/genesis/allocate
     * Body: { address, amount }
     * Allocates genesis tokens (only works before any blocks are produced).
     */
    this.app.post('/api/genesis/allocate', (req: Request, res: Response) => {
      try {
        const { address, amount } = req.body;
        if (!address || amount === undefined) {
          return res.status(400).json({
            error: 'Missing required parameters: address, amount',
          });
        }
        if (typeof amount !== 'number' || amount <= 0) {
          return res.status(400).json({ error: 'Allocation amount must be a positive number' });
        }
        this.blockchain.allocateGenesis(address, amount);
        return res.json({ message: 'Genesis tokens allocated successfully', address, amount });
      } catch (err: any) {
        return res.status(400).json({ error: err.message || 'Failed to allocate genesis tokens' });
      }
    });
  }

  /**
   * Starts the Express REST server on the designated port.
   */
  public start(): void {
    this.app.listen(this.port, () => {
      console.log(`RojsChain REST API server running on port ${this.port}`);
    });
  }

  /**
   * Returns the underlying Express application instance.
   */
  public getApp(): express.Application {
    return this.app;
  }
}

// Ensure TokenSystem and DPoSConsensus are exported or usable if required
export { TokenSystem, DPoSConsensus };
