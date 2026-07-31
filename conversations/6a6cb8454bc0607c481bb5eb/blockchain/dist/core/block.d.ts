import { Block, BlockHeader, Transaction } from '../types';
/**
 * Class representing a Merkle Tree constructed from transaction hashes.
 * Used to efficiently compute the Merkle root and generate / verify cryptographic proofs.
 */
export declare class MerkleTree {
    private levels;
    constructor(transactions: Transaction[]);
    /**
     * Constructs the tree levels by hashing transaction IDs with SHA-256
     * and pairing adjacent nodes until a single Merkle root remains.
     */
    private buildTree;
    /**
     * Returns the Merkle root hash.
     */
    getRoot(): string;
    /**
     * Returns the Merkle proof for a given transaction hash.
     * Proof consists of sibling hashes and their direction ('left' | 'right')
     * needed to reconstruct the Merkle root.
     */
    getProof(txHash: string): {
        hash: string;
        direction: 'left' | 'right';
    }[];
    /**
     * Verifies a Merkle proof against a target transaction hash and Merkle root.
     */
    static verifyProof(txHash: string, proof: {
        hash: string;
        direction: 'left' | 'right';
    }[], root: string): boolean;
}
/**
 * Concatenates all BlockHeader fields and returns the double SHA-256 hash.
 */
export declare function calculateBlockHash(header: BlockHeader): string;
/**
 * Creates a new Block with calculated Merkle root and block header hash.
 */
export declare function createBlock(index: number, previousHash: string, transactions: Transaction[], validator: string, validatorSignature: string, difficulty: number, nonce: number, timestamp?: number): Block;
/**
 * Validates a single block against its predecessor in the chain.
 * Checks index continuity, previous hash reference, Merkle root accuracy,
 * block hash correctness, and validator signature presence.
 */
export declare function validateBlock(block: Block, previousBlock: Block): boolean;
/**
 * Validates the entire blockchain from the genesis block through the tip.
 */
export declare function isChainValid(chain: Block[]): boolean;
/**
 * Creates the genesis block for Verdis.
 * Index 0, previousHash all zeros, empty transactions, validator 'genesis', timestamp 0.
 */
export declare function createGenesisBlock(): Block;
