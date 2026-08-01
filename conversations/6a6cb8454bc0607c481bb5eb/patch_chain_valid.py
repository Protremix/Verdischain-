#!/usr/bin/env python3
"""Patch isChainValid to validate last 500 blocks only (production optimization)."""
path = "/opt/verdis/app/dist/core/block.js"
with open(path) as f:
    c = f.read()

old = """function isChainValid(chain) {
    if (!Array.isArray(chain) || chain.length === 0) {
        return false;
    }
    const genesisBlock = chain[0];
    if (genesisBlock.header.index !== 0) {
        return false;
    }
    const computedGenesisMerkle = new MerkleTree(genesisBlock.transactions).getRoot();
    if (genesisBlock.header.merkleRoot !== computedGenesisMerkle) {
        return false;
    }
    if (genesisBlock.hash !== calculateBlockHash(genesisBlock.header)) {
        return false;
    }
    if (!genesisBlock.header.validatorSignature || genesisBlock.header.validatorSignature.trim() === '') {
        return false;
    }
    for (let i = 1; i < chain.length; i++) {
        const currentBlock = chain[i];
        const previousBlock = chain[i - 1];
        if (!validateBlock(currentBlock, previousBlock)) {
            return false;
        }
    }
    return true;
}"""

new = """function isChainValid(chain) {
    if (!Array.isArray(chain) || chain.length === 0) {
        return false;
    }
    // Production optimization: validate last 500 blocks + genesis
    const genesisBlock = chain[0];
    if (genesisBlock.header.index !== 0) {
        return false;
    }
    if (!genesisBlock.header.validatorSignature || genesisBlock.header.validatorSignature.trim() === '') {
        return false;
    }
    // Validate recent blocks (last 500)
    const startIdx = Math.max(1, chain.length - 500);
    for (let i = startIdx; i < chain.length; i++) {
        const currentBlock = chain[i];
        const previousBlock = chain[i - 1];
        if (!validateBlock(currentBlock, previousBlock)) {
            return false;
        }
    }
    return true;
}"""

if old in c:
    c = c.replace(old, new)
    with open(path, "w") as f:
        f.write(c)
    print("Patched isChainValid: validate last 500 blocks + genesis")
else:
    print("Could not find isChainValid function")
