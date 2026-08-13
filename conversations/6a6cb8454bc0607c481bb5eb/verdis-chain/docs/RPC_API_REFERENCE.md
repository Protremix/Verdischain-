# VERDIS CHAIN — RPC API REFERENCE

**Version:** 1.0
**Date:** 2026-08-14
**Base URL:** `http://localhost:9933` (HTTP) or `ws://localhost:9944` (WebSocket)
**Format:** JSON-RPC 2.0

---

## AUTHENTICATION

No authentication required for read methods. Write methods require signed transactions submitted via TX Relay.

---

## CHAIN METHODS

### chain_getHeader
Get the latest block header (or by hash).

```json
{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}
```
**Params:** `[blockHash?]` — optional block hash

### chain_getBlock
Get a full block by hash.

```json
{"jsonrpc":"2.0","method":"chain_getBlock","params":["0x..."],"id":1}
```
**Params:** `[blockHash]`

### chain_getBlockHash
Get block hash by block number.

```json
{"jsonrpc":"2.0","method":"chain_getBlockHash","params":[42],"id":1}
```
**Params:** `[blockNumber]`

### chain_getFinalizedHead
Get the latest finalized block hash.

```json
{"jsonrpc":"2.0","method":"chain_getFinalizedHead","params":[],"id":1}
```

---

## SYSTEM METHODS

### system_health
Get node health status.

```json
{"jsonrpc":"2.0","method":"system_health","params":[],"id":1}
```
**Returns:** `{ peers, isSyncing, shouldHavePeers }`

### system_peers
Get connected peers.

```json
{"jsonrpc":"2.0","method":"system_peers","params":[],"id":1}
```
**Returns:** Array of `{ peerId, roles, bestBlock }`

### system_properties
Get chain properties.

```json
{"jsonrpc":"2.0","method":"system_properties","params":[],"id":1}
```
**Returns:** `{ tokenSymbol: "VRDX", tokenDecimals: 9, ss58Format: 909 }`

### system_version
Get node version.

```json
{"jsonrpc":"2.0","method":"system_version","params":[],"id":1}
```

---

## ACCOUNT / BALANCE METHODS

### system_account
Get account info (nonce, balance, etc).

```json
{"jsonrpc":"2.0","method":"system_account","params":["SS58_ADDRESS"],"id":1}
```
**Returns:** `{ nonce, consumers, providers, sufficients, data: { free, reserved, miscFrozen, feeFrozen } }`

### account_nextIndex
Get the next transaction index for an account.

```json
{"jsonrpc":"2.0","method":"account_nextIndex","params":["SS58_ADDRESS"],"id":1}
```

---

## DPoS / STAKING METHODS

### dpos_allValidators
Get all registered validators.

```json
{"jsonrpc":"2.0","method":"dpos_allValidators","params":[],"id":1}
```
**Returns:** Array of `{ accountId, stake, isActive, greenScore, energySource }`

### dpos_validatorStake
Get a specific validator's stake.

```json
{"jsonrpc":"2.0","method":"dpos_validatorStake","params":["SS58_ADDRESS"],"id":1}
```
**Returns:** `u128` — stake amount in smallest units (9 decimals)

### dpos_validatorName
Get a validator's registered name.

```json
{"jsonrpc":"2.0","method":"dpos_validatorName","params":["SS58_ADDRESS"],"id":1}
```
**Returns:** `String` — validator name

### dpos_activeValidators
Get currently active validators (in the session set).

```json
{"jsonrpc":"2.0","method":"dpos_activeValidators","params":[],"id":1}
```

### dpos_totalStaked
Get total staked amount across all validators.

```json
{"jsonrpc":"2.0","method":"dpos_totalStaked","params":[],"id":1}
```

---

## ECO / CARBON METHODS

### eco_getGreenScore
Get a validator's green score (1-5).

```json
{"jsonrpc":"2.0","method":"eco_getGreenScore","params":["SS58_ADDRESS"],"id":1}
```
**Returns:** `u32` — green score (1-5, higher is greener)

### eco_getAllGreenValidators
Get all validators with green scores > 0.

```json
{"jsonrpc":"2.0","method":"eco_getAllGreenValidators","params":[],"id":1}
```

### eco_getGreenValidatorCount
Get count of green validators.

```json
{"jsonrpc":"2.0","method":"eco_getGreenValidatorCount","params":[],"id":1}
```

### eco_getCarbonCredits
Get all carbon credits.

```json
{"jsonrpc":"2.0","method":"eco_getCarbonCredits","params":[],"id":1}
```

### eco_getReforestProjects
Get all reforestation projects.

```json
{"jsonrpc":"2.0","method":"eco_getReforestProjects","params":[],"id":1}
```

### eco_getTotalCarbonOffset
Get total carbon offset (network-wide).

```json
{"jsonrpc":"2.0","method":"eco_getTotalCarbonOffset","params":[],"id":1}
```

### eco_getTotalTrees
Get total trees planted (network-wide).

```json
{"jsonrpc":"2.0","method":"eco_getTotalTrees","params":[],"id":1}
```

---

## AMM DEX METHODS

### amm_getAllPools
Get all DEX pools.

```json
{"jsonrpc":"2.0","method":"amm_getAllPools","params":[],"id":1}
```
**Returns:** Array of `{ poolId, tokenA, tokenB, reserveA, reserveB, totalSupply }`

### amm_getPoolInfo
Get specific pool info.

```json
{"jsonrpc":"2.0","method":"amm_getPoolInfo","params":[0],"id":1}
```
**Params:** `[poolId]`

### amm_getPoolCount
Get total number of pools.

```json
{"jsonrpc":"2.0","method":"amm_getPoolCount","params":[],"id":1}
```

---

## TOKENOMICS METHODS

### tokenomics_getAllocation
Get token allocation for a category.

```json
{"jsonrpc":"2.0","method":"tokenomics_getAllocation","params":["eco"],"id":1}
```
**Params:** `[category]` — one of: eco, staking, treasury, dev, liquidity, community, seed, presale, team

### tokenomics_getTotalSupply
Get total token supply.

```json
{"jsonrpc":"2.0","method":"tokenomics_getTotalSupply","params":[],"id":1}
```

### tokenomics_getCirculatingSupply
Get circulating supply (unlocked tokens).

```json
{"jsonrpc":"2.0","method":"tokenomics_getCirculatingSupply","params":[],"id":1}
```

---

## VESTING METHODS

### vesting_getSchedule
Get vesting schedule for a category.

```json
{"jsonrpc":"2.0","method":"vesting_getSchedule","params":["seed"],"id":1}
```

### vesting_getVested
Get vested amount for an account.

```json
{"jsonrpc":"2.0","method":"vesting_getVested","params":["SS58_ADDRESS"],"id":1}
```

---

## PRESALE METHODS

### presale_getRound
Get presale round info.

```json
{"jsonrpc":"2.0","method":"presale_getRound","params":[0],"id":1}
```

### presale_getContributions
Get contributions for an account.

```json
{"jsonrpc":"2.0","method":"presale_getContributions","params":["SS58_ADDRESS"],"id":1}
```

### presale_getWhitelist
Get whitelisted addresses for a round.

```json
{"jsonrpc":"2.0","method":"presale_getWhitelist","params":[0],"id":1}
```

---

## GOVERNANCE METHODS

### democracy_referendas
Get all active referendums.

```json
{"jsonrpc":"2.0","method":"democracy_referendas","params":[],"id":1}
```

### council_members
Get council members.

```json
{"jsonrpc":"2.0","method":"council_members","params":[],"id":1}
```

### treasury_proposals
Get treasury proposals.

```json
{"jsonrpc":"2.0","method":"treasury_proposals","params":[],"id":1}
```

---

## SUBSCRIPTION METHODS (WebSocket only)

### Subscribe to new blocks

```json
{"jsonrpc":"2.0","method":"chain_subscribeNewHeads","params":[],"id":1}
```

### Subscribe to finalized heads

```json
{"jsonrpc":"2.0","method":"chain_subscribeFinalizedHeads","params":[],"id":1}
```

### Subscribe to storage changes

```json
{"jsonrpc":"2.0","method":"state_subscribeStorage","params":[["0xSTORAGE_KEY"]],"id":1}
```

---

## TX RELAY API

### Submit Transaction (non-custodial)

```
POST https://verdischain.com/api/tx-relay/submit
Content-Type: application/json

{
  "method": "dpos",
  "call": "register_validator",
  "args": {
    "green_score": 3,
    "energy_source": "solar"
  },
  "signer": "SS58_ADDRESS"
}
```

### Derive Address from Mnemonic

```
POST https://verdischain.com/api/tx-relay/derive-address
Content-Type: application/json

{
  "mnemonic": "word1 word2 ... word12"
}
```
**Returns:** `{ address: "SS58_ADDRESS" }` — address only, private key never exposed

### Get Balance

```
GET https://verdischain.com/api/tx-relay/balance/:address
```
**Returns:** `{ free, reserved, nonce }`

---

## ERRORS

| Code | Meaning |
|---|---|
| -32600 | Invalid request |
| -32601 | Method not found |
| -32602 | Invalid params |
| -32603 | Internal error |
| 1 | Bad origin (not signed) |
| 2 | Bad signature |
| 3 | Stale nonce |
| 1001 | Pool not found |
| 2001 | Validator not found |
| 3001 | Insufficient balance |
| 4001 | Not whitelisted |

---

## SDK

For programmatic access, use the Verdis JavaScript SDK:
- Location: `sdk/verdis-sdk.js`
- Methods: 51
- Zero dependencies
- Native WebSocket support

```javascript
const Verdis = require('./verdis-sdk.js');
const client = new Verdis('ws://localhost:9944');

// Get latest block
const header = await client.chain.getHeader();

// Get all validators
const validators = await client.dpos.allValidators();

// Subscribe to new blocks
client.chain.subscribeNewHeads((header) => {
  console.log(`New block: #${header.number}`);
});
```
