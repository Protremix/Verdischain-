"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.apiServer = exports.ecoSystem = exports.dex = exports.walletManager = exports.contractManager = exports.blockchain = void 0;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const consensus_1 = require("./core/consensus");
const vm_1 = require("./core/vm");
const server_1 = require("./api/server");
const wallet_1 = require("./wallet/wallet");
const dex_1 = require("./core/dex");
const eco_1 = require("./core/eco");
// === Initialize Core Systems ===
const blockchain = new consensus_1.Blockchain();
exports.blockchain = blockchain;
const contractManager = new vm_1.ContractManager();
exports.contractManager = contractManager;
const walletManager = new wallet_1.WalletManager();
exports.walletManager = walletManager;
const dex = new dex_1.DEX();
exports.dex = dex;
const ecoSystem = new eco_1.EcoSystem();
exports.ecoSystem = ecoSystem;
// === API Server ===
const PORT = 3001;
const apiServer = new server_1.BlockchainAPI(blockchain, walletManager, contractManager);
exports.apiServer = apiServer;
apiServer.setDEX(dex);
apiServer.setEco(ecoSystem);
// === Bootstrap: Set up 5 genesis validators ===
console.log('⚡ Bootstrapping Verdis network...');
const consensus = blockchain.getConsensus();
const tokenSystem = blockchain.getTokenSystem();
const GENESIS_PER_VALIDATOR = 10000000000; // 10 billion VRS each (50B total from 100B max)
const STAKE_PER_VALIDATOR = 1000000000; // 1 billion VRS staked per validator
const validatorsList = [];
const energySources = ['solar', 'wind', 'hydro', 'geothermal', 'solar'];
for (let i = 1; i <= 5; i++) {
    // a. Create validator wallet
    const wallet = walletManager.createWallet();
    // b. Allocate genesis tokens
    blockchain.addGenesisAllocation(wallet.address, GENESIS_PER_VALIDATOR);
    wallet.balance = GENESIS_PER_VALIDATOR;
    // c. Register as validator
    consensus.registerValidator(wallet.publicKey, wallet.address);
    // d. Stake tokens and vote for self
    tokenSystem.stake(wallet.address, STAKE_PER_VALIDATOR);
    wallet.staked = STAKE_PER_VALIDATOR;
    wallet.balance -= STAKE_PER_VALIDATOR;
    consensus.vote(wallet.address, wallet.address, STAKE_PER_VALIDATOR, tokenSystem);
    // e. Register as green validator with eco system
    ecoSystem.registerGreenValidator(wallet.address, energySources[i - 1]);
    validatorsList.push({
        index: i,
        address: wallet.address,
        publicKey: wallet.publicKey,
        balance: wallet.balance,
        staked: wallet.staked,
    });
}
// === Log bootstrap info ===
console.log('\n╔══════════════════════════════════════════════════╗');
console.log('║         🌿 Verdis Network Bootstrapped            ║');
console.log('╠══════════════════════════════════════════════════╣');
validatorsList.forEach((v) => {
    console.log(`║  Validator #${v.index}: ${v.address.slice(0, 16)}...`);
    console.log(`║    Balance: ${v.balance.toLocaleString()} VRS`);
    console.log(`║    Staked:  ${v.staked.toLocaleString()} VRS`);
    console.log(`║    Energy:  ${energySources[v.index - 1]}`);
});
console.log('╠══════════════════════════════════════════════════╣');
console.log(`║  Total Supply:    ${tokenSystem.getTotalSupply().toLocaleString()} VRS`);
console.log(`║  Max Supply:      ${tokenSystem.getMaxSupply().toLocaleString()} VRS`);
console.log(`║  Validators:      ${consensus.getAllValidatorsList().length}`);
console.log(`║  Green Validators: ${ecoSystem.getTopGreenValidators(5).length}`);
console.log('╚══════════════════════════════════════════════════╝\n');
// === Serve Dashboard ===
const dashboardPath = path_1.default.resolve(__dirname, 'web/dashboard.html');
if (fs_1.default.existsSync(dashboardPath)) {
    apiServer.serveDashboard(dashboardPath);
}
else {
    const altPath = path_1.default.resolve(__dirname, '../src/web/dashboard.html');
    if (fs_1.default.existsSync(altPath)) {
        apiServer.serveDashboard(altPath);
    }
}
// === Start the node ===
apiServer.start(PORT);
console.log('🚀 Verdis is running at http://localhost:3000');
console.log('\n💡 Try these commands:');
console.log('   curl http://localhost:3000/api/blockchain/info');
console.log('   curl http://localhost:3000/api/validators');
console.log('   curl http://localhost:3000/api/eco/impact');
console.log('   curl -X POST http://localhost:3000/api/wallet/create');
console.log('   curl http://localhost:3000/api/dex/pools');
console.log('');
//# sourceMappingURL=index.js.map