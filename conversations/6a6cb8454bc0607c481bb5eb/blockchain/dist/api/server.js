"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.BlockchainAPI = void 0;
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
class BlockchainAPI {
    constructor(blockchain, walletManager, contractManager) {
        this.blockchain = blockchain;
        this.walletManager = walletManager;
        this.contractManager = contractManager;
        this.app = (0, express_1.default)();
        this.setupMiddleware();
        this.setupRoutes();
    }
    setupMiddleware() {
        this.app.use((0, cors_1.default)());
        this.app.use(express_1.default.json());
    }
    serveDashboard(filePath) {
        if (filePath && fs_1.default.existsSync(filePath)) {
            this.dashboardHtmlPath = filePath;
        }
    }
    setupRoutes() {
        // Web Dashboard route
        this.app.get('/', (req, res) => {
            if (this.dashboardHtmlPath && fs_1.default.existsSync(this.dashboardHtmlPath)) {
                res.sendFile(this.dashboardHtmlPath);
                return;
            }
            const defaultDashboardPath = path_1.default.resolve(__dirname, '../web/dashboard.html');
            if (fs_1.default.existsSync(defaultDashboardPath)) {
                res.sendFile(defaultDashboardPath);
                return;
            }
            res.send(`
        <!DOCTYPE html>
        <html>
        <head><title>Verdis Dashboard</title></head>
        <body style="font-family: sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem;">
          <h1>🚀 Verdis Node Running</h1>
          <p>Status: Active</p>
          <p>Height: ${this.blockchain.getChain().length - 1}</p>
        </body>
        </html>
      `);
        });
        // API Routes
        this.app.get('/api/chain', (req, res) => {
            res.json(this.blockchain.getState());
        });
        this.app.get('/api/wallets', (req, res) => {
            res.json(this.walletManager.getAllWallets());
        });
        this.app.post('/api/wallets/create', (req, res) => {
            const wallet = this.walletManager.createWallet();
            res.json(wallet);
        });
        this.app.get('/api/validators', (req, res) => {
            const validators = this.blockchain.getConsensus().getAllValidatorsList();
            res.json(validators);
        });
        this.app.post('/api/transactions', (req, res) => {
            const { from, to, amount, fee, nonce, data } = req.body;
            const wallet = this.walletManager.getAllWallets().find((w) => w.publicKey === from || w.address === from);
            if (!wallet) {
                res.status(400).json({ error: 'Sender wallet not found in WalletManager' });
                return;
            }
            const tx = this.walletManager.signTransaction(wallet, to, amount, fee, nonce || 0, data);
            this.blockchain.getMempool().addTransaction(tx);
            res.json({ status: 'Transaction submitted', transaction: tx });
        });
    }
    start(port) {
        this.app.listen(port, () => {
            // API Listening
        });
    }
    getApp() {
        return this.app;
    }
}
exports.BlockchainAPI = BlockchainAPI;
//# sourceMappingURL=server.js.map