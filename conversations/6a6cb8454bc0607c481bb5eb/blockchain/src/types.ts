// Core type definitions shared across all blockchain modules

export interface BlockHeader {
  index: number;
  previousHash: string;
  timestamp: number;
  merkleRoot: string;
  validator: string; // public key of the block producer
  validatorSignature: string;
  difficulty: number;
  nonce: number;
}

export interface Block {
  header: BlockHeader;
  transactions: Transaction[];
  hash: string;
}

export interface Transaction {
  id: string; // tx hash
  from: string; // sender public key
  to: string; // recipient public key
  amount: number;
  fee: number;
  timestamp: number;
  nonce: number;
  data: string | null; // for smart contract calls
  signature: string;
  recovery: number; // recovery bit for signature
}

export interface Wallet {
  privateKey: string;
  publicKey: string;
  address: string;
  balance: number;
  staked: number;
}

export interface Validator {
  publicKey: string;
  address: string;
  votes: number;
  isProducer: boolean;
  blocksProduced: number;
  totalRewards: number;
}

export interface Stake {
  voter: string;
  validator: string;
  amount: number;
  timestamp: number;
}

export interface SmartContract {
  id: string;
  owner: string;
  bytecode: number[]; // compiled instructions
  state: Map<string, any>;
  deployedAt: number;
  name: string;
}

export interface BlockchainState {
  chain: Block[];
  mempool: Transaction[];
  validators: Map<string, Validator>;
  stakes: Stake[];
  balances: Map<string, number>;
  contracts: Map<string, SmartContract>;
  totalSupply: number;
  maxSupply: number;
  blockReward: number;
  validatorCount: number;
  currentHeight: number;
}
