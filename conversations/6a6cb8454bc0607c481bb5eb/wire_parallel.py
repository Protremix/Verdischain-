#!/usr/bin/env python3
"""Wire parallel executor into block production and add API endpoint"""

# 1. Patch consensus.js to use parallel executor
with open('/opt/verdis/app/dist/core/consensus.js') as f:
    consensus = f.read()

# Add import at the top
old_import = '"use strict";'
if 'ParallelExecutor' not in consensus:
    # Add import after first use strict
    idx = consensus.index(old_import) + len(old_import)
    consensus = consensus[:idx] + '\nconst { ParallelExecutor } = require("./parallel-executor");' + consensus[idx:]
    
    # Add parallelExecutor instance in constructor or class
    # Find the class and add a property
    old_produce = """        // Apply all transactions
        for (const tx of pendingTxs) {
            this.tokenSystem.applyTransaction(tx, validatorAddress);
            this.mempool.removeTransaction(tx.id);
        }"""
    new_produce = """        // Apply transactions with parallel execution
        const parallelExec = new ParallelExecutor();
        const batches = parallelExec.groupTransactions(pendingTxs, this.tokenSystem);
        let txProcessed = 0;
        for (const batch of batches) {
            for (const tx of batch) {
                this.tokenSystem.applyTransaction(tx, validatorAddress);
                this.mempool.removeTransaction(tx.id);
                txProcessed++;
            }
        }
        // Log parallelism stats
        if (batches.length < pendingTxs.length && pendingTxs.length > 1) {
            console.log(`⚡ Parallel exec: ${pendingTxs.length} txs in ${batches.length} batches (${(pendingTxs.length/batches.length).toFixed(1)}x parallelism)`);
        }"""
    
    if old_produce in consensus:
        consensus = consensus.replace(old_produce, new_produce)
        print("1. Wired parallel executor into block production")
    else:
        print("1. ERROR: produceBlock pattern not found")
        # Try a looser match
        import re
        match = re.search(r'// Apply all transactions.*?this\.mempool\.removeTransaction\(tx\.id\);\s*\}', consensus, re.DOTALL)
        if match:
            consensus = consensus[:match.start()] + new_produce + consensus[match.end():]
            print("1. Wired parallel executor (loose match)")
        else:
            print("1. FATAL: Could not find apply transactions block")
else:
    print("1. ParallelExecutor already imported")

with open('/opt/verdis/app/dist/core/consensus.js', 'w') as f:
    f.write(consensus)

# 2. Add API endpoint for parallel execution stats
with open('/opt/verdis/app/dist/api/server.js') as f:
    server = f.read()

# Add parallel exec stats endpoint near the network info endpoint
old_net = 'this.app.get("/api/network/tps"'
new_net = '''this.app.get("/api/parallel-exec/stats", (req, res) => {
            const { ParallelExecutor } = require("../core/parallel-executor");
            const pe = new ParallelExecutor();
            res.json(pe.getStats());
        });
        this.app.get("/api/network/tps"'''

if old_net in server:
    server = server.replace(old_net, new_net, 1)
    print("2. Added parallel execution API endpoint")
else:
    print("2. ERROR: network/tps endpoint not found")

with open('/opt/verdis/app/dist/api/server.js', 'w') as f:
    f.write(server)

print("Parallel executor wired!")
