# design-explorer-ui

## When to Use
When the user requests a blockchain explorer UI (blocks, transactions, validators, AMM DEX).

## Workflow

1. **Clarify** — Ask (if not provided):
   - Which project (almost always `verdis`)
   - What views: blocks, transactions, addresses, validators, pools, eco-metrics?
   - Real-time WebSocket or API polling?

2. **Select Theme** — Load `Verdis Dark` theme via `getTheme`

3. **Generate** — Build a self-contained HTML file:
   - Navbar: Verdiscan logo, nav links, live status indicator
   - Search bar: search by block number, hash, or address
   - Stats grid: block height, TPS, finalized blocks, validators, peers, supply
   - Tabs: Blocks | Validators | AMM Pools | Eco Metrics
   - Blocks table: block #, hash, extrinsics, events, validator, time
   - Block detail: expandable view with full block header info
   - Validator cards: avatar, name, address, stake, green score, status
   - AMM pool rows: pair tokens, reserves, 24h volume, APR
   - Eco metrics: carbon credits, trees, CO₂ offset, green projects

4. **WebSocket Integration**
   - Connect to Substrate node via `wss://hostname/substrate-ws`
   - Subscribe to `chain_newHeads` for real-time block updates
   - JSON-RPC calls for block data, health, peers

5. **Apply Tokens**
   - Verdis green (#00ff88) for primary actions and links
   - JetBrains Mono for all numeric values and hashes
   - Tag pills: green (active), teal (info), yellow (warning), red (error)
   - Data-dense tables, no zebra striping, hover highlight only

6. **Responsive + Accessible** — Run all quality gates

7. **Persist** — Call `generatePage` then `publishArtifact`

## Deploy Target
- Verdis explorer → `91.98.160.145:/opt/verdis-repo/dist/web/explorer.html`
- Never deploy explorer UI to EvolvixOS server
