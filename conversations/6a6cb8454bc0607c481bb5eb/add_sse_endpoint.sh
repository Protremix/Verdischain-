#!/usr/bin/env bash
set -e

# =====================================================
# STEP 1: Add SSE endpoint to API server
# =====================================================
python3 << 'PYEOF'
with open('/opt/verdis/app/dist/api/server.js', 'r') as f:
    content = f.read()

# Add SSE endpoint before the start() method
sse_code = '''
        // === SERVER-SENT EVENTS (Real-time stream) ===
        this.app.get("/api/stream/events", (req, res) => {
            res.writeHead(200, {
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "X-Accel-Buffering": "no"
            });
            res.write("retry: 3000\\n\\n");
            
            // Send initial connection event
            res.write("event: connected\\n");
            res.write("data: " + JSON.stringify({ time: Date.now(), chainId: 909 }) + "\\n\\n");
            
            // Track last sent block height
            let lastBlock = 0;
            let lastTxCount = 0;
            
            // Poll for new blocks and transactions every 3s
            const interval = setInterval(async () => {
                try {
                    const chainInfo = this.blockchain.getState();
                    const currentHeight = chainInfo.height || chainInfo.blockHeight || 0;
                    
                    // New block detected
                    if (currentHeight > lastBlock) {
                        lastBlock = currentHeight;
                        const blocks = this.blockchain.getRecentBlocks(1);
                        const latestBlock = blocks && blocks.length > 0 ? blocks[0] : null;
                        
                        res.write("event: block\\n");
                        res.write("data: " + JSON.stringify({
                            height: currentHeight,
                            hash: latestBlock?.hash || "",
                            validator: latestBlock?.header?.validator?.slice(0, 20) + "..." || "",
                            txCount: latestBlock?.transactions?.length || 0,
                            timestamp: latestBlock?.header?.timestamp || Date.now(),
                            gasUsed: latestBlock?.header?.gasUsed || 0,
                            gasLimit: latestBlock?.header?.gasLimit || 30000000
                        }) + "\\n\\n");
                    }
                    
                    // Check for new transactions
                    const mempool = this.blockchain.getMempool ? this.blockchain.getMempool() : [];
                    const txs = this.blockchain.getRecentTransactions ? this.blockchain.getRecentTransactions(5) : [];
                    if (txs && txs.length > lastTxCount) {
                        const newTxs = txs.slice(0, txs.length - lastTxCount);
                        lastTxCount = txs.length;
                        for (const tx of newTxs) {
                            res.write("event: transaction\\n");
                            res.write("data: " + JSON.stringify({
                                id: tx.id || tx.hash || "",
                                from: tx.from || "",
                                to: tx.to || "",
                                amount: tx.amount || 0,
                                fee: tx.fee || 0,
                                blockIndex: tx.blockIndex || 0,
                                timestamp: tx.timestamp || Date.now()
                            }) + "\\n\\n");
                        }
                    }
                    
                    // Send stats update every 5s
                    if (Date.now() % 5000 < 3000) {
                        const stats = {
                            height: currentHeight,
                            mempoolSize: mempool.length || 0,
                            validators: this.blockchain.getConsensus()?.getAllValidatorsList()?.length || 5,
                            timestamp: Date.now()
                        };
                        res.write("event: stats\\n");
                        res.write("data: " + JSON.stringify(stats) + "\\n\\n");
                    }
                } catch (e) {
                    // Silent error, keep stream alive
                }
            }, 3000);
            
            // Heartbeat every 30s
            const heartbeat = setInterval(() => {
                try {
                    res.write(": heartbeat\\n\\n");
                } catch (e) {}
            }, 30000);
            
            // Clean up on disconnect
            req.on("close", () => {
                clearInterval(interval);
                clearInterval(heartbeat);
            });
        });
        
'''

# Insert before the start() method
content = content.replace(
    '    start(port) {',
    sse_code + '    start(port) {',
    1
)

with open('/opt/verdis/app/dist/api/server.js', 'w') as f:
    f.write(content)
print('SSE endpoint added to server.js')
PYEOF

echo "Step 1 done: SSE endpoint added"
