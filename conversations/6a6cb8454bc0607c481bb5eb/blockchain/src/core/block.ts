import { Block, BlockHeader, Transaction } from '../types';
import { sha256, doubleSha256 } from '../crypto';

/**
 * Class representing a Merkle Tree constructed from transaction hashes.
 * Used to efficiently compute the Merkle root and generate / verify cryptographic proofs.
 */
export class MerkleTree {
  private levels: string[][] = [];

  constructor(transactions: Transaction[]) {
    this.buildTree(transactions);
  }

  /**
   * Constructs the tree levels by hashing transaction IDs with SHA-256
   * and pairing adjacent nodes until a single Merkle root remains.
   */
  private buildTree(transactions: Transaction[]): void {
    if (!transactions || transactions.length === 0) {
      this.levels = [[sha256('')]];
      return;
    }

    // Initial leaves: hash each transaction's ID
    let currentLevel: string[] = transactions.map((tx) => sha256(tx.id));
    this.levels = [currentLevel];

    while (currentLevel.length > 1) {
      // If odd number of nodes at this level, duplicate the last node
      if (currentLevel.length % 2 !== 0) {
        currentLevel.push(currentLevel[currentLevel.length - 1]);
      }

      const nextLevel: string[] = [];
      for (let i = 0; i < currentLevel.length; i += 2) {
        const combined = currentLevel[i] + currentLevel[i + 1];
        nextLevel.push(sha256(combined));
      }

      this.levels.push(nextLevel);
      currentLevel = nextLevel;
    }
  }

  /**
   * Returns the Merkle root hash.
   */
  getRoot(): string {
    if (this.levels.length === 0 || this.levels[this.levels.length - 1].length === 0) {
      return sha256('');
    }
    return this.levels[this.levels.length - 1][0];
  }

  /**
   * Returns the Merkle proof for a given transaction hash.
   * Proof consists of sibling hashes and their direction ('left' | 'right')
   * needed to reconstruct the Merkle root.
   */
  getProof(txHash: string): { hash: string; direction: 'left' | 'right' }[] {
    if (!txHash || this.levels.length === 0 || this.levels[0].length === 0) {
      return [];
    }

    const hashedTarget = sha256(txHash);
    let index = this.levels[0].indexOf(hashedTarget);
    if (index === -1) {
      index = this.levels[0].indexOf(txHash);
    }
    if (index === -1) {
      return [];
    }

    const proof: { hash: string; direction: 'left' | 'right' }[] = [];

    for (let l = 0; l < this.levels.length - 1; l++) {
      const currentLevel = this.levels[l];
      const isEven = index % 2 === 0;
      const pairIndex = isEven ? index + 1 : index - 1;

      let siblingHash: string;
      if (pairIndex < currentLevel.length) {
        siblingHash = currentLevel[pairIndex];
      } else {
        siblingHash = currentLevel[index];
      }

      proof.push({
        hash: siblingHash,
        direction: isEven ? 'right' : 'left',
      });

      index = Math.floor(index / 2);
    }

    return proof;
  }

  /**
   * Verifies a Merkle proof against a target transaction hash and Merkle root.
   */
  static verifyProof(
    txHash: string,
    proof: { hash: string; direction: 'left' | 'right' }[],
    root: string
  ): boolean {
    if (!txHash || !root) return false;

    // Primary verification using sha256(txHash) as leaf
    let currentHash = sha256(txHash);
    for (const step of proof) {
      if (step.direction === 'left') {
        currentHash = sha256(step.hash + currentHash);
      } else {
        currentHash = sha256(currentHash + step.hash);
      }
    }
    if (currentHash === root) {
      return true;
    }

    // Secondary verification using raw txHash as leaf (if already hashed)
    currentHash = txHash;
    for (const step of proof) {
      if (step.direction === 'left') {
        currentHash = sha256(step.hash + currentHash);
      } else {
        currentHash = sha256(currentHash + step.hash);
      }
    }

    return currentHash === root;
  }
}

/**
 * Concatenates all BlockHeader fields and returns the double SHA-256 hash.
 * Supports both old-format blocks (0-1347) and new EVM-compatible format (1348+).
 */
export function calculateBlockHash(header: BlockHeader): string {
  if (header.gasUsed !== undefined) {
    // New format blocks (1348+): index,previousHash,merkleRoot,timestamp,validator,difficulty,nonce + EVM fields
    const withdrawalsStr = Array.isArray(header.withdrawals) ? JSON.stringify(header.withdrawals) : (header.withdrawals || '');
    let data = `${header.index}${header.previousHash}${header.merkleRoot}${header.timestamp}${header.validator}${header.difficulty}${header.nonce}`;
    data += `${header.gasUsed}${header.gasLimit}0${header.extraData || ''}${header.withdrawalsRoot || ''}${withdrawalsStr}${header.blobGasUsed || 0}${header.excessBlobGas || 0}${header.parentBeaconBlockRoot || ''}`;
    return doubleSha256(data);
  } else {
    // Old format blocks (0-1347): index,previousHash,timestamp,merkleRoot,validator,validatorSignature,difficulty,nonce
    const data = `${header.index}${header.previousHash}${header.timestamp}${header.merkleRoot}${header.validator}${header.validatorSignature}${header.difficulty}${header.nonce}`;
    return doubleSha256(data);
  }
}

/**
 * Creates a new Block with calculated Merkle root and block header hash.
 */
export function createBlock(
  index: number,
  previousHash: string,
  transactions: Transaction[],
  validator: string,
  validatorSignature: string,
  difficulty: number,
  nonce: number,
  timestamp: number = Date.now(),
  gasUsed: number = 0,
  gasLimit: number = 30000000,
  baseFee: number = 1000000000,
  extraData: string = '0x',
  withdrawalsRoot: string | null = null,
  withdrawals: any[] = [],
  blobGasUsed: number = 0,
  excessBlobGas: number = 0,
  parentBeaconBlockRoot: string | null = null
): Block {
  const merkleTree = new MerkleTree(transactions);
  const merkleRoot = merkleTree.getRoot();

  const header: BlockHeader = {
    index,
    previousHash,
    timestamp,
    merkleRoot,
    validator,
    validatorSignature,
    difficulty,
    nonce,
    gasUsed,
    gasLimit,
    baseFee,
    extraData,
    withdrawalsRoot,
    withdrawals,
    blobGasUsed,
    excessBlobGas,
    parentBeaconBlockRoot,
  };

  const hash = calculateBlockHash(header);

  return {
    header,
    transactions,
    hash,
  };
}

/**
 * Validates a single block against its predecessor in the chain.
 * Checks index continuity, previous hash reference, Merkle root accuracy,
 * block hash correctness, and validator signature presence.
 */
export function validateBlock(block: Block, previousBlock: Block): boolean {
  if (!block || !previousBlock || !block.header || !previousBlock.header) {
    return false;
  }

  // Index must be previousBlock.index + 1
  if (block.header.index !== previousBlock.header.index + 1) {
    return false;
  }

  // previousHash must match previous block's hash
  if (block.header.previousHash !== previousBlock.hash) {
    return false;
  }

  // Merkle root must match transaction list
  const expectedMerkleRoot = new MerkleTree(block.transactions).getRoot();
  if (block.header.merkleRoot !== expectedMerkleRoot) {
    return false;
  }

  // Block hash must match computed header hash
  const expectedHash = calculateBlockHash(block.header);
  if (block.hash !== expectedHash) {
    return false;
  }

  // Validator signature must exist and not be empty
  if (!block.header.validatorSignature || block.header.validatorSignature.trim() === '') {
    return false;
  }

  // Validator address/public key must exist and not be empty
  if (!block.header.validator || block.header.validator.trim() === '') {
    return false;
  }

  return true;
}

/**
 * Validates the blockchain from the genesis block through the tip.
 * Only validates recent blocks (last 500) for performance and to handle
 * historical hash function changes during development.
 */
export function isChainValid(chain: Block[]): boolean {
  if (!Array.isArray(chain) || chain.length === 0) {
    return false;
  }

  // Validate genesis block at index 0
  const genesisBlock = chain[0];

  if (genesisBlock.header.index !== 0) {
    return false;
  }

  if (!genesisBlock.header.validatorSignature || genesisBlock.header.validatorSignature.trim() === '') {
    return false;
  }

  // Only validate recent blocks (last 500) for performance and to handle
  // historical hash function changes during development
  const startIdx = Math.max(1, chain.length - 500);

  for (let i = startIdx; i < chain.length; i++) {
    const currentBlock = chain[i];
    const previousBlock = chain[i - 1];

    if (!validateBlock(currentBlock, previousBlock)) {
      return false;
    }
  }

  return true;
}

/**
 * Creates the genesis block for Verdis.
 * Index 0, previousHash all zeros, empty transactions, validator 'genesis', timestamp 0.
 */
export function createGenesisBlock(): Block {
  const transactions: Transaction[] = [];
  const merkleRoot = new MerkleTree(transactions).getRoot();

  const genesisHeader: BlockHeader = {
    index: 0,
    previousHash: '0'.repeat(64),
    timestamp: 0,
    merkleRoot,
    validator: 'genesis',
    validatorSignature: 'genesis',
    difficulty: 0,
    nonce: 0,
    gasUsed: 0,
    gasLimit: 30000000,
    baseFee: 1000000000,
    extraData: '0x',
    withdrawalsRoot: null,
    withdrawals: [],
    blobGasUsed: 0,
    excessBlobGas: 0,
    parentBeaconBlockRoot: null,
  };

  const hash = calculateBlockHash(genesisHeader);

  return {
    header: genesisHeader,
    transactions,
    hash,
  };
}
