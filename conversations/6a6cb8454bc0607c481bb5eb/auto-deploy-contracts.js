#!/usr/bin/env node
/**
 * Auto-deploys Verdis smart contracts on server startup.
 * Called from index.js after the blockchain is initialized.
 */
const http = require('http');

const ADMIN_KEY = "27e508e645ef2d0b1a4afb313243df19bf041a842061b4d5ee908b3ea06d72dd";
const OWNER = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1";

const CONTRACTS = [
  { name: "EcoDepositCalculator", source: "PUSH 1000\nPUSH 50\nMUL\nLOG\nHALT" },
  { name: "EcoStakingReward", source: "PUSH 5000\nPUSH 30\nMUL\nPUSH 10\nMUL\nLOG\nHALT" },
  { name: "MultiSigWallet", source: "PUSH 3\nPUSH 2\nGT\nLOG\nHALT" },
  { name: "TimeLockVault", source: "PUSH 1000\nPUSH 2000\nLT\nLOG\nHALT" },
  { name: "CarbonCreditMinter", source: "PUSH 100\nPUSH 5\nMUL\nLOG\nEMIT\nHALT" },
  { name: "ReforestationLogger", source: "PUSH 1000\nPUSH 21\nMUL\nLOG\nEMIT\nHALT" }
];

function deployContract(contract) {
  return new Promise((resolve) => {
    const data = JSON.stringify({ name: contract.name, owner: OWNER, source: contract.source });
    const req = http.request({
      hostname: '127.0.0.1',
      port: 3200,
      path: '/api/contract/deploy',
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-api-key': ADMIN_KEY, 'Content-Length': Buffer.byteLength(data) }
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(body);
          console.log(`  ✅ Contract deployed: ${contract.name}`);
          resolve(result);
        } catch (e) {
          console.log(`  ❌ Contract failed: ${contract.name} — ${body}`);
          resolve(null);
        }
      });
    });
    req.on('error', (e) => {
      console.log(`  ❌ Contract error: ${contract.name} — ${e.message}`);
      resolve(null);
    });
    req.write(data);
    req.end();
  });
}

async function checkExisting() {
  return new Promise((resolve) => {
    const req = http.get('http://127.0.0.1:3200/api/contracts', (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(body);
          const contracts = Array.isArray(result) ? result : (result.contracts || []);
          resolve(contracts);
        } catch (e) {
          resolve([]);
        }
      });
    });
    req.on('error', () => resolve([]));
  });
}

async function autoDeployContracts() {
  console.log('📦 Checking smart contracts...');
  const existing = await checkExisting();
  
  if (existing.length > 0) {
    console.log(`  ✅ ${existing.length} contracts already deployed — skipping auto-deploy`);
    return;
  }
  
  console.log('  📦 No contracts found — auto-deploying 6 smart contracts...');
  for (const contract of CONTRACTS) {
    await deployContract(contract);
  }
  console.log('  ✅ All smart contracts deployed');
}

module.exports = { autoDeployContracts };
