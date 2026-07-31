# Wrapped Verdis (wVRS) BSC Deployment Guide

## Overview
This deploys a wrapped VRS token (wVRS) on Binance Smart Chain that can be traded on PancakeSwap. Users lock VRS on the Verdis chain → bridge mints wVRS on BSC → trade on PancakeSwap.

## Step 1: Deploy wVRS Token
1. Go to https://remix.ethereum.org
2. Create new file `WVRS.sol` and paste the contract
3. Compile with Solidity 0.8.20+
4. Connect MetaMask to BSC Mainnet (Chain ID: 56)
5. Deploy the contract
6. Copy the contract address

## Step 2: Deploy Bridge
1. Create new file `VerdisBridge.sol`
2. Compile and deploy with the wVRS address as constructor arg
3. Call `wVRS.proposeBridgeOperator(bridgeAddress)` on the wVRS contract
4. Call `bridge.acceptBridgeOperator()` on the bridge contract

## Step 3: Create PancakeSwap Pool
1. Go to https://pancakeswap.finance
2. Go to Liquidity → Add
3. Select wVRS (paste contract address) and BNB or USDT
4. Set initial price ratio
5. Add liquidity
6. Your wVRS/BNB or wVRS/USDT pair is now tradable

## Step 4: Add to CoinMarketCap / DexScreener
- Submit wVRS contract address to DexScreener for auto-listing
- Apply to CoinMarketCap with contract address + docs

## Bridge Flow
```
Lock VRS on Verdis → Operator verifies → Mint wVRS on BSC → Trade on PancakeSwap
Burn wVRS on BSC → Operator verifies → Unlock VRS on Verdis
```

## Network Details
- BSC Chain ID: 56
- BSC RPC: https://bsc-dataseed.binance.org
- PancakeSwap Router: 0x10ED43C718714eb63d5aA57B78B54704E256024E
