"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.DEX = exports.dex = exports.apiServer = exports.walletManager = exports.contractManager = exports.blockchain = void 0;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const consensus_1 = require("./core/consensus");
const vm_1 = require("./core/vm");
const server_1 = require("./api/server");
const wallet_1 = require("./wallet/wallet");
const dex_1 = require("./core/dex");
Object.defineProperty(exports, "DEX", { enumerable: true, get: function () { return dex_1.DEX; } });
// 1. Create a new Blockchain instance
const blockchain = new consensus_1.Blockchain();
exports.blockchain = blockchain;
// 2. Create a new ContractManager
const contractManager = new vm_1.ContractManager();
exports.contractManager = contractManager;
// 3. Create a new WalletManager
const walletManager = new wallet_1.WalletManager();
exports.walletManager = walletManager;
// 4. Create a new DEX instance for RojsChain
const dex = new dex_1.DEX();
exports.dex = dex;
// 5. Set up the API server on port 3000
const PORT = 3000;
const apiServer = new server_1.BlockchainAPI(blockchain, walletManager, contractManager);
exports.apiServer = apiServer;
// 6. Bootstrap sequence — automatically set up the network
console.log('⚡ Bootstrapping RojsChain network...');
const consensus = blockchain.getConsensus();
const tokenSystem = blockchain.getTokenSystem();
const GENESIS_PER_VALIDATOR = 10000000000; // 10 Billion tokens each (50B total from 100B max supply)
const STAKE_PER_VALIDATOR = 1000000000; // 1 Billion tokens staked per validator
const validatorsList = [];
for (let i = 1; i <= 5; i++) {
    // a. Create initial validator wallet
    const wallet = walletManager.createWallet();
    // b. Allocate genesis tokens to each validator (10 billion each from 100B max supply)
    blockchain.addGenesisAllocation(wallet.address, GENESIS_PER_VALIDATOR);
    wallet.balance = GENESIS_PER_VALIDATOR;
    // c. Register all 5 as validators
    consensus.registerValidator(wallet.publicKey, wallet.address);
    // d. Have each validator stake tokens and vote for themselves
    tokenSystem.stake(wallet.address, STAKE_PER_VALIDATOR);
    wallet.staked = STAKE_PER_VALIDATOR;
    wallet.balance -= STAKE_PER_VALIDATOR;
    consensus.vote(wallet.address, wallet.address, STAKE_PER_VALIDATOR, tokenSystem);
    validatorsList.push({
        index: i,
        address: wallet.address,
        publicKey: wallet.publicKey,
        balance: wallet.balance,
        staked: wallet.staked,
    });
}
// e. Log the bootstrap information to the console (addresses, balances, validator status)
console.log('\n=== Genesis Validators Bootstrapped Successfully ===');
validatorsList.forEach((v) => {
    console.log(`Validator #${v.index}:`);
    console.log(`  Address:    ${v.address}`);
    console.log(`  Public Key: ${v.publicKey}`);
    console.log(`  Balance:    ${v.balance.toLocaleString()} ECO`);
    console.log(`  Staked:     ${v.staked.toLocaleString()} ECO`);
    console.log(`  Status:     Active Genesis Validator & Block Producer`);
});
console.log('====================================================\n');
// 7. Serve the web dashboard from the API (served at /)
const dashboardPath = path_1.default.resolve(__dirname, 'web/dashboard.html');
if (fs_1.default.existsSync(dashboardPath)) {
    apiServer.serveDashboard(dashboardPath);
}
else {
    const altDashboardPath = path_1.default.resolve(__dirname, '../src/web/dashboard.html');
    if (fs_1.default.existsSync(altDashboardPath)) {
        apiServer.serveDashboard(altDashboardPath);
    }
    else {
        apiServer.serveDashboard();
    }
}
// 8. Start the API server
apiServer.start(PORT);
// 9. Log a welcome message with the URL
console.log('🚀 RojsChain is running at http://localhost:3000');
// 10. Show some example commands users can try
console.log('\n💡 Example API commands you can try:');
console.log('  1. Get Blockchain Status:');
console.log('     curl http://localhost:3000/api/chain');
console.log('  2. List All Wallets:');
console.log('     curl http://localhost:3000/api/wallets');
console.log('  3. Create New Wallet:');
console.log('     curl -X POST http://localhost:3000/api/wallets/create');
console.log('  4. View Registered Validators:');
console.log('     curl http://localhost:3000/api/validators');
console.log('  5. Send Transaction:');
console.log('     curl -X POST http://localhost:3000/api/transactions -H "Content-Type: application/json" -d \'{"from":"<pubkey_or_addr>", "to":"<pubkey_or_addr>", "amount":100, "fee":1}\'\n');
//# sourceMappingURL=index.js.map