/**
 * Parallel Transaction Executor
 * Groups independent transactions and executes them in parallel within a block.
 * Uses read/write set analysis to detect conflicts and maximize parallelism.
 */

class ParallelExecutor {
    constructor() {
        this.maxWorkers = 4; // Max parallel execution threads
        this.conflictThreshold = 10; // Max conflicts before falling back to sequential
    }

    /**
     * Analyze a transaction's read/write set
     * @returns { reads: Set<string>, writes: Set<string> }
     */
    analyzeTransaction(tx, tokenSystem) {
        const reads = new Set();
        const writes = new Set();

        // All transactions read the sender's balance and nonce
        reads.add(tx.from);
        reads.add(`nonce:${tx.from}`);

        if (tx.to) {
            reads.add(tx.to);
            writes.add(tx.to);
        }
        writes.add(tx.from);
        writes.add(`nonce:${tx.from}`);
        writes.add(`balance:${tx.from}`);

        // DEX swaps read/write pool state
        if (tx.type === 'swap' || tx.data?.type === 'swap') {
            const poolId = tx.data?.poolId || `${tx.data?.tokenIn}/${tx.data?.tokenOut}`;
            reads.add(`pool:${poolId}`);
            writes.add(`pool:${poolId}`);
        }

        // Contract execution reads/writes contract state
        if (tx.type === 'contract' || tx.data?.contractId) {
            reads.add(`contract:${tx.data.contractId}`);
            writes.add(`contract:${tx.data.contractId}`);
        }

        // Staking reads/writes validator state
        if (tx.type === 'stake' || tx.type === 'unstake') {
            reads.add(`stake:${tx.from}`);
            writes.add(`stake:${tx.from}`);
            if (tx.data?.validator) {
                reads.add(`validator:${tx.data.validator}`);
                writes.add(`validator:${tx.data.validator}`);
            }
        }

        return { reads, writes };
    }

    /**
     * Group transactions into parallel execution batches.
     * Transactions that don't conflict (no shared write sets) can run in parallel.
     */
    groupTransactions(txs, tokenSystem) {
        const batches = [];
        const analyzed = txs.map((tx, i) => ({
            tx,
            index: i,
            rw: this.analyzeTransaction(tx, tokenSystem)
        }));

        // Greedy conflict detection
        for (const item of analyzed) {
            let placed = false;

            for (const batch of batches) {
                // Check if this tx conflicts with any tx already in the batch
                const hasConflict = batch.some(existing => {
                    // Conflict: this tx writes something the existing tx reads (or vice versa)
                    for (const w of item.rw.writes) {
                        if (existing.rw.reads.has(w) || existing.rw.writes.has(w)) return true;
                    }
                    for (const w of existing.rw.writes) {
                        if (item.rw.reads.has(w)) return true;
                    }
                    return false;
                });

                if (!hasConflict && batch.length < this.maxWorkers) {
                    batch.push(item);
                    placed = true;
                    break;
                }
            }

            if (!placed) {
                batches.push([item]);
            }
        }

        return batches.map(batch => batch.map(item => item.tx));
    }

    /**
     * Execute a batch of non-conflicting transactions in parallel.
     * Returns array of results in the same order as input.
     */
    async executeBatch(batch, processor) {
        // Execute all txs in the batch "simultaneously"
        // In Node.js (single-threaded), we simulate parallelism with Promise.all
        const promises = batch.map(tx => {
            try {
                const result = processor(tx);
                return Promise.resolve(result);
            } catch (e) {
                return Promise.resolve({ success: false, error: e.message, tx });
            }
        });

        const results = await Promise.all(promises);
        return results;
    }

    /**
     * Process a full block of transactions with parallel execution.
     * Returns statistics about parallelism achieved.
     */
    async processBlock(txs, processor, tokenSystem) {
        if (txs.length === 0) {
            return { processed: 0, batches: 0, parallelism: 0, sequential: 0 };
        }

        // Group into parallel batches
        const batches = this.groupTransactions(txs, tokenSystem);
        
        let processed = 0;
        let sequential = 0;
        const results = [];

        for (const batch of batches) {
            if (batch.length === 1) {
                // Single tx — sequential
                sequential++;
                const result = processor(batch[0]);
                results.push(result);
                if (result.success !== false) processed++;
            } else {
                // Parallel batch
                const batchResults = await this.executeBatch(batch, processor);
                for (const r of batchResults) {
                    results.push(r);
                    if (r.success !== false) processed++;
                }
            }
        }

        const avgParallelism = batches.length > 0
            ? (txs.length / batches.length).toFixed(2)
            : 0;

        return {
            processed,
            batches: batches.length,
            totalTxs: txs.length,
            parallelTxs: txs.length - sequential,
            sequentialTxs: sequential,
            avgParallelism: parseFloat(avgParallelism),
            results,
            speedupEstimate: batches.length > 0 
                ? parseFloat((txs.length / batches.length).toFixed(2))
                : 1
        };
    }

    /**
     * Get execution statistics for dashboard display
     */
    getStats() {
        return {
            maxWorkers: this.maxWorkers,
            enabled: true,
            mode: 'read-write-set-analysis',
            conflictResolution: 'greedy-batching'
        };
    }
}

module.exports = { ParallelExecutor };
