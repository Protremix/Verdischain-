const http = require('http');
const { ApiPromise, WsProvider, Keyring } = require('@polkadot/api');
const fs = require('fs');

const RPC_URL = 'ws://localhost:9933';
const FAUCET_SEED = '//Alice';
const AMOUNT = '1000000000000';
const RATE_FILE = '/tmp/faucet-rate-limits.json';
const STATS_FILE = '/tmp/faucet-stats.json';

let api, keyring, faucetPair, currentNonce = null;

async function init() {
    const ws = new WsProvider(RPC_URL);
    api = await ApiPromise.create({ provider: ws });
    keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
    faucetPair = keyring.addFromUri(FAUCET_SEED);
    console.log('Faucet running on :8080');
}

if (!fs.existsSync(RATE_FILE)) fs.writeFileSync(RATE_FILE, '{}');

// Initialize stats file
if (!fs.existsSync(STATS_FILE)) {
    fs.writeFileSync(STATS_FILE, JSON.stringify({
        totalDispensed: 0,
        uniqueRecipients: 0,
        totalRequests: 0,
        dailyRequests: {},
        distributions: []
    }));
}

function getStats() {
    const limits = JSON.parse(fs.readFileSync(RATE_FILE, 'utf8'));
    const stats = JSON.parse(fs.readFileSync(STATS_FILE, 'utf8'));
    const today = new Date().toISOString().split('T')[0];
    const todayCount = stats.dailyRequests[today] || 0;
    
    const uniqueCount = Object.keys(limits).length;
    const totalDispensed = uniqueCount * 1000;
    
    const result = {
        totalDispensed: totalDispensed,
        uniqueRecipients: uniqueCount,
        todayRequests: todayCount,
        totalRequests: stats.totalRequests || 0,
        distributions: stats.distributions || []
    };
    
    // Write stats to a static file for nginx to serve
    try {
        fs.writeFileSync('/var/www/verdiscan/faucet/stats.json', JSON.stringify(result));
    } catch(e) {}
    
    return result;
}

function recordDistribution(address, amount, txHash) {
    const stats = JSON.parse(fs.readFileSync(STATS_FILE, 'utf8'));
    const today = new Date().toISOString().split('T')[0];
    
    stats.totalRequests = (stats.totalRequests || 0) + 1;
    stats.dailyRequests[today] = (stats.dailyRequests[today] || 0) + 1;
    
    stats.distributions.unshift({
        address: address.substring(0, 8) + '...' + address.slice(-4),
        amount: amount,
        txHash: txHash.substring(0, 10) + '...',
        time: new Date().toISOString()
    });
    
    // Keep only last 50
    if (stats.distributions.length > 50) stats.distributions = stats.distributions.slice(0, 50);
    
    fs.writeFileSync(STATS_FILE, JSON.stringify(stats));
}

async function handleRequest(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    
    if (req.method === 'GET' && req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end('OK');
        return;
    }
    
    if (req.method === 'GET' && req.url === '/stats') {
        const stats = getStats();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(stats));
        return;
    }
    
    if (req.method === 'GET' && req.url === '/') {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end('<html><body><h1>Verdis Testnet Faucet</h1><p>1000 VRDX per address per 24h</p></body></html>');
        return;
    }
    
    if (req.method === 'POST') {
        let body = '';
        req.on('data', c => body += c);
        req.on('end', async () => {
            const address = body.split('address=')[1] ? body.split('address=')[1].replace(/\+/g,' ').trim() : '';
            if (!address || !address.startsWith('5') && !address.startsWith('k')) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Invalid address' }));
                return;
            }
            
            const limits = JSON.parse(fs.readFileSync(RATE_FILE, 'utf8'));
            const now = Math.floor(Date.now() / 1000);
            if (now - (limits[address] || 0) < 86400) {
                const hoursLeft = 24 - Math.floor((now - limits[address]) / 3600);
                res.writeHead(429, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Rate limited. Try in ' + hoursLeft + 'h' }));
                return;
            }
            
            try {
                const destPubKey = keyring.decodeAddress(address);
                
                if (currentNonce === null) {
                    const account = await api.query.system.account(faucetPair.publicKey);
                    currentNonce = account.nonce.toNumber();
                }
                const nonce = currentNonce++;
                
                const tx = api.tx.balances.transferAllowDeath(destPubKey, AMOUNT);
                await tx.signAsync(faucetPair, { nonce });
                const result = await api.rpc.author.submitExtrinsic(tx.toHex());
                
                limits[address] = now;
                fs.writeFileSync(RATE_FILE, JSON.stringify(limits));
                
                recordDistribution(address, '1000', result.toHex());
                
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, amount: '1000', unit: 'VRDX', tx_hash: result.toHex() }));
            } catch (e) {
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: e.message }));
            }
        });
    }
}

init().then(() => {
    // Write stats file immediately and every 30s
    getStats();
    setInterval(getStats, 30000);
    
    const server = http.createServer(handleRequest);
    server.listen(8080, '0.0.0.0', () => console.log('Faucet listening on 8080'));
}).catch(e => {
    console.error('Init failed:', e);
    process.exit(1);
});
