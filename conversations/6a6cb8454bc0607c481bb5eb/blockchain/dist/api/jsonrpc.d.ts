/**
 * Ethereum JSON-RPC Compatibility Layer for Trust Wallet
 *
 * Implements standard Ethereum JSON-RPC methods so that Trust Wallet
 * (and MetaMask, etc.) can connect to Verdis as a custom network.
 *
 * Network config for Trust Wallet:
 *   Network Name: Verdis
 *   RPC URL: http://localhost:3200/rpc
 *   Chain ID: 909
 *   Symbol: VRS
 *   Explorer: http://localhost:3200
 */
import { Express } from 'express';
import { Blockchain } from '../core/consensus';
import { WalletManager } from '../wallet/wallet';
export declare const VERDIS_CHAIN_ID = 909;
/**
 * Derives an Ethereum-compatible address from a public key using keccak256.
 * Takes the uncompressed public key (64 bytes without prefix), keccak256 hashes it,
 * and takes the last 20 bytes.
 */
export declare function getEvmAddress(publicKey: string): string;
/**
 * Converts an address to EIP-55 checksum format.
 */
export declare function toChecksumAddress(address: string): string;
/**
 * Sets up JSON-RPC endpoints on the Express app.
 */
export declare function setupJsonRpc(app: Express, blockchain: Blockchain, walletManager: WalletManager): void;
