export interface BlockHeader {
    index: number;
    previousHash: string;
    timestamp: number;
    merkleRoot: string;
    validator: string;
    validatorSignature: string;
    difficulty: number;
    nonce: number;
    gasUsed?: number;
    gasLimit?: number;
    baseFee?: number;
    extraData?: string;
    withdrawalsRoot?: string | null;
    withdrawals?: any[];
    blobGasUsed?: number;
    excessBlobGas?: number;
    parentBeaconBlockRoot?: string | null;
}
export interface Block {
    header: BlockHeader;
    transactions: Transaction[];
    hash: string;
}
export interface Transaction {
    id: string;
    from: string;
    publicKey: string;
    to: string;
    amount: number;
    fee: number;
    timestamp: number;
    nonce: number;
    data: string | null;
    signature: string;
    recovery: number;
    type?: number;
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
    bytecode: number[];
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
