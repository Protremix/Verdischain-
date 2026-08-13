# Comprehensive Web Audit Report — Verdis Chain Website
**Target:** https://verdischain.com  
**Audit Date:** August 13, 2026  
**Pages Audited:** 28 Pages  

---

## Executive Summary & Global Findings

During the full-site audit of `https://verdischain.com`, all 28 target pages were fetched, parsed, and analyzed for JavaScript network requests (`fetch()`, `XMLHttpRequest`, `WebSocket`), API endpoint configurations, hardcoded/mock data dependencies, and endpoint availability.

### Key Global Findings & Critical Vulnerabilities:
1. **Broken WebSocket Handshakes (Critical Severity):**
   - Endpoints `wss://verdischain.com/substrate-ws` and `wss://verdischain.com/ws` fail WebSocket protocol upgrade handshakes. Instead of returning `HTTP/1.1 101 Switching Protocols`, Nginx returns `HTTP/1.1 200 OK` (JSON/HTML payload). As a result, browser `new WebSocket(...)` instantiations on `/transactions/` and `/docs/` throw immediate connection errors, breaking real-time transaction streaming.
2. **Localhost Endpoint Fallbacks in Production (Critical Severity):**
   - Pages `/analytics/` and `/monitoring/` contain hardcoded `fetch("http://localhost:9933")` calls. On production (`https://verdischain.com`), browsers block these requests due to Mixed Content (HTTPS page calling HTTP endpoint) and throw `ERR_CONNECTION_REFUSED` errors.
3. **Non-Functional / 501 Endpoint Returns (High Severity):**
   - The governance voting submission endpoint `POST /api/governance` returns `HTTP 501 Not Implemented`, rendering governance voting and proposal submissions inoperable.
4. **Presale & Contact Form Missing Backend Integrations (High / Medium Severity):**
   - On `/sale/`, the VRDX purchase form lacks an API / fetch endpoint integration to process token purchases.
   - On `/contact/`, the contact form submission handler has no JS event listener or `fetch()` call to submit inquiry data.
5. **Static / Hardcoded Data Fallbacks:**
   - Multiple pages (`/tokenomics/`, `/eco/`, `/explorer/`, `/analytics/`, `/monitoring/`, `/referral/`) rely on hardcoded static data arrays, mock transaction hashes, or hardcoded Chart.js datasets instead of live on-chain queries.

---

## Detailed Page-by-Page Audit Findings

### 1. Home (`/`)
- **Path:** `/`
- **API / Network Calls Found:**
  - `fetch(RPC, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', params: [], id: 1 }) })`
  - `fetch(RPC, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'system_health', params: [], id: 2 }) })`
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'dpos_activeValidators', params: [], id: 10 }) })`
  - `fetch(RPC, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'amm_dex_getAllPools', params: [], id: 3 }) })`
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', params: [], id: 9 }) })`
  - `fetchRpc('system_health')` & `fetchRpc('chain_getHeader')` via `verdis.js` targeting `https://rpc.verdischain.com`
- **Issues Found:**
  - **Redundant RPC Fetches:** Duplicated fetch calls between inline scripts and `verdis.js` execution on page load.
  - **Hardcoded Fallback Counters:** HTML uses static `data-counter` attributes (`data-counter="20000"`) that animate static values when RPC network latency occurs.
- **Severity:** **Low**

### 2. Verdiscan Explorer (`/explorer/`)
- **Path:** `/explorer/`
- **API / Network Calls Found:**
  - `fetch(RPC, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', id: 1 }) })`
  - `fetch(RPC, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getBlock', id: 1 }) })`
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'amm_dex_getAllPools', id: 1 }) })`
  - `fetch(API + path)` targeting `https://verdischain.com/api`
  - `fetch('/api/v1/token/holders')`
  - `fetch('/price-history.json?_=' + Date.now())`
- **Issues Found:**
  - **Hardcoded Mock Arrays:** Extensive inline JS mock arrays (`const blocksData = [...]`, static sample addresses `vrd1sample...`) are embedded to display fallback table data if RPC calls fail or lag.
  - **Timestamp Parsing Bug Workaround:** `verdis.js` contains a DOM MutationObserver explicitly listening for a '20669d ago' string bug in the recent activity table, indicating raw block timestamp formatting defects in block display logic.
- **Severity:** **Medium**

### 3. Verdis DEX (`/dex/`)
- **Path:** `/dex/`
- **API / Network Calls Found:**
  - `fetch(RPC_URL, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'amm_dex_getAllPools', id: Date.now() }) })` (defines `RPC_URL = 'https://verdischain.com/rpc/'`)
  - `fetch('/api/tx-relay', { method: 'POST', body: JSON.stringify({ action: 'swap', pool_id: pool.id, token_in: currentTokenIn, amount_in: chainAmountIn, min_amount_out: minAmountOut }) })`
- **Issues Found:**
  - **Transaction Relay Error Handling:** Swapping tokens posts to `/api/tx-relay`. If wallet connection or parameter validation fails, endpoint returns HTTP 400 Bad Request without detailed UI feedback.
  - **Static Pool Fallbacks:** DEX liquidity pools fallback to static preset array when RPC pool query fails.
- **Severity:** **Medium**

### 4. Whitepaper (`/whitepaper/`)
- **Path:** `/whitepaper/`
- **API / Network Calls Found:**
  - `fetch(RPC_URL, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', id: Date.now() }) })` (defines `RPC_URL = '/rpc'`)
- **Issues Found:**
  - None. Standard header block height fetch executed successfully.
- **Severity:** **Low**

### 5. Web3 Wallet (`/wallet/`)
- **Path:** `/wallet/`
- **API / Network Calls Found:**
  - `fetch(RPC_URL, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', id: 1 }) })` (`RPC_URL = 'https://verdischain.com/rpc'`)
  - `fetch(API_URL + path)` (`API_URL = 'https://verdischain.com/api/v1'`)
  - `fetch('/api/v1/account/${address}')`
  - `fetch('/api/v1/account/' + myAddr + '/transactions?limit=100')`
  - `fetch('/api/tx-relay', { method: 'POST', body: JSON.stringify({ action: 'pin-status', address }) })`
  - `fetch('/api/tx-relay', { method: 'POST', body: JSON.stringify({ action: 'pin-verify', address, pin }) })`
  - `fetch('/api/tx-relay', { method: 'POST', body: JSON.stringify({ action: 'pin-register', address, pin }) })`
  - `fetch('/api/tx-relay', { method: 'POST', body: JSON.stringify({ action: 'wallet-backup', email, ciphertext, salt, iv, address, pin }) })`
  - `fetch('/api/tx-relay', { method: 'POST', body: JSON.stringify({ action: 'wallet-recover', email, pin }) })`
  - `fetch(RELAY_URL, { method: 'POST', body: JSON.stringify({ action: 'submit-extrinsic', extrinsic }) })`
- **Issues Found:**
  - **Base API Endpoint 404:** `const API_URL = 'https://verdischain.com/api/v1'` returns HTTP 404 if accessed at root path (requires appending subpaths like `/account/${address}`).
  - **Hardcoded Sample Address:** Uses hardcoded sample account addresses (`vrd1sample...`) for initial state rendering.
- **Severity:** **Medium**

### 6. VRDX Token Sale (`/sale/`)
- **Path:** `/sale/`
- **API / Network Calls Found:**
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', params: [], id: 1 }) })`
- **Issues Found:**
  - **Missing Fetch Calls (High):** The presale token purchase form on `/sale/` contains no `fetch()` call or API handler to process or transmit buy orders to a backend contract or relay service. The form operates solely as a client-side calculator without transaction execution.
- **Severity:** **High**

### 7. VRDX Tokenomics (`/tokenomics/`)
- **Path:** `/tokenomics/`
- **API / Network Calls Found:**
  - None (0 fetch, 0 XHR, 0 WebSocket calls found in page source).
- **Issues Found:**
  - **Hardcoded Data:** Token supply metrics, allocation percentages, vesting schedules, and Chart.js datasets are entirely hardcoded static numbers.
  - **Missing Fetch Calls:** No dynamic API calls exist to query live circulating supply or token distribution stats from the blockchain.
- **Severity:** **Medium**

### 8. Verdis Faucet (`/faucet/`)
- **Path:** `/faucet/`
- **API / Network Calls Found:**
  - `fetch(FAUCET_API, { method: 'POST', body: JSON.stringify({ address: addr, token: selectedToken }) })` (`FAUCET_API = 'https://verdischain.com/faucet/api'`)
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', id: 1 }) })`
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'system_health', id: 2 }) })`
  - `fetch('/faucet/stats.json')`
  - `fetch('/faucet/api/stats')`
- **Issues Found:**
  - **Inconsistent Faucet Stat Sources:** Page queries both `/faucet/stats.json` (returns all zeros `{"totalDispensed":0...}`) and `/faucet/api/stats` (returns active stats `{"totalDispensed":100...}`), leading to potential UI stat mismatches.
- **Severity:** **Medium**

### 9. Validators & DPoS (`/validators/`)
- **Path:** `/validators/`
- **API / Network Calls Found:**
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'dpos_activeValidators', params: [], id: 1 }) })`
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'dpos_validatorName', params: [val], id: 1 }) })`
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'dpos_validatorStake', params: [val], id: 1 }) })`
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'eco_getGreenScore', params: [val], id: 1 }) })`
- **Issues Found:**
  - **Missing Action Handlers:** Staking and nomination buttons lack an active extrinsic signing or submission call to `/api/tx-relay`.
- **Severity:** **Medium**

### 10. Eco Metrics (`/eco/`)
- **Path:** `/eco/`
- **API / Network Calls Found:**
  - None (0 fetch, 0 XHR, 0 WebSocket calls found in page source).
- **Issues Found:**
  - **Hardcoded Data & Missing Fetch Calls (High):** Carbon offset statistics, energy savings comparisons, tree counter figures, and carbon credit proof hashes (`dummyHash`) are completely hardcoded static HTML elements with no API fetch logic.
- **Severity:** **High**

### 11. Documentation (`/docs/`)
- **Path:** `/docs/`
- **API / Network Calls Found:**
  - `fetch('https://verdischain.com/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', id: 1 }) })`
- **Issues Found:**
  - **Documented Endpoint Failure:** Documentation examples instruct developers to connect to `wss://verdischain.com/ws`, which fails WebSocket upgrade handshakes in production (returns HTTP 200).
- **Severity:** **Medium**

### 12. Transactions Explorer (`/transactions/`)
- **Path:** `/transactions/`
- **API / Network Calls Found:**
  - `fetch(RPC, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method, params, id: 1 }) })`
  - `new WebSocket('wss://verdischain.com/substrate-ws')` (`WS_URL = 'wss://verdischain.com/substrate-ws'`)
- **Issues Found:**
  - **CRITICAL BROKEN WEBSOCKET ENDPOINT:** `wss://verdischain.com/substrate-ws` fails WebSocket handshake (server returns `HTTP/1.1 200 OK` JSON/HTML instead of `101 Switching Protocols`), throwing an immediate browser WebSocket connection error and disabling live transaction streaming.
- **Severity:** **Critical**

### 13. Verdis Analytics (`/analytics/`)
- **Path:** `/analytics/`
- **API / Network Calls Found:**
  - `fetch(url, { method: 'POST', body: JSON.stringify(payload) })` (where `url` contains `'http://localhost:9933'` and `'/rpc'`)
- **Issues Found:**
  - **CRITICAL BROKEN / WRONG ENDPOINT:** Hardcoded `http://localhost:9933` target URL in JS analytics runner. When loaded over HTTPS (`https://verdischain.com/analytics/`), browser security blocks the HTTP call due to Mixed Content restrictions and fails with `ERR_CONNECTION_REFUSED`.
  - **Hardcoded Data:** Historical network chart analytics use static pre-populated numerical arrays.
- **Severity:** **Critical**

### 14. Validator Monitor (`/monitoring/`)
- **Path:** `/monitoring/`
- **API / Network Calls Found:**
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify(payload) })`
  - `fetch('http://localhost:9933', { method: 'POST', body: JSON.stringify(payload) })`
- **Issues Found:**
  - **CRITICAL BROKEN / WRONG ENDPOINT:** Explicit `fetch('http://localhost:9933')` in monitoring script causes Mixed Content blockage and connection refused errors on production deployment.
  - **Hardcoded Data:** Validator uptime graphs and latency metrics rely on hardcoded static sample data.
- **Severity:** **Critical**

### 15. Governance Protocol (`/governance/`)
- **Path:** `/governance/`
- **API / Network Calls Found:**
  - `fetch(RPC_URL, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method, params, id: 1 }) })`
  - `fetch('/api/governance')`
  - `fetch(TX_RELAY_URL, { method: 'POST', body: JSON.stringify({ action: 'submit-extrinsic', ... }) })`
- **Issues Found:**
  - **BROKEN ENDPOINT (501 Not Implemented):** Submitting governance proposals or votes sends `POST /api/governance`, which returns HTTP `501 Not Implemented` HTML error page from the server.
  - **Static Proposal Fallback:** Governance proposal list falls back to static hardcoded referendum objects when endpoint fails.
- **Severity:** **High**

### 16. Blog (`/blog/`)
- **Path:** `/blog/`
- **API / Network Calls Found:**
  - `loadLiveStats()` via `verdis.js` calling `https://rpc.verdischain.com` (0 inline fetch calls)
- **Issues Found:**
  - **Hardcoded Data:** All blog articles, press releases, and publication dates are static HTML elements with no CMS or API fetch handler.
- **Severity:** **Low**

### 17. Developer Portal (`/developers/`)
- **Path:** `/developers/`
- **API / Network Calls Found:**
  - `fetch(endpoint, { method: 'POST', body: JSON.stringify(payload) })` (Interactive RPC runner playground)
- **Issues Found:**
  - Interactive playground defaults to `/rpc` (operational), but code snippet examples reference non-functional WebSocket endpoint `wss://verdischain.com/ws`.
- **Severity:** **Medium**

### 18. Download (`/download/`)
- **Path:** `/download/`
- **API / Network Calls Found:**
  - `loadLiveStats()` via `verdis.js` (0 inline fetch calls)
- **Issues Found:**
  - **Hardcoded Data:** Node binary version strings, SHA-256 checksums, and release download links are hardcoded static HTML strings.
- **Severity:** **Low**

### 19. Referral Program (`/referral/`)
- **Path:** `/referral/`
- **API / Network Calls Found:**
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', params: [], id: 1 }) })`
- **Issues Found:**
  - **Hardcoded Data & Missing Fetch Calls:** Affiliate leaderboard renders hardcoded placeholder string (`No affiliates yet...`). Lacks backend API endpoint integration to fetch or register unique affiliate referral codes.
- **Severity:** **Medium**

### 20. Validator Incentives (`/incentives/`)
- **Path:** `/incentives/`
- **API / Network Calls Found:**
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', id: 1 }) })`
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method, params, id: Math.random() }) })`
- **Issues Found:**
  - **Hardcoded Calculations:** Reward projection calculator uses hardcoded yield multipliers rather than pulling live inflation and reward pool params via RPC.
- **Severity:** **Medium**

### 21. Contact Page (`/contact/`)
- **Path:** `/contact/`
- **API / Network Calls Found:**
  - None (0 fetch, 0 XHR, 0 WebSocket calls found in page source).
- **Issues Found:**
  - **Missing Fetch Calls:** Contact form lacks a JavaScript event listener or `fetch()` POST endpoint handler. Submitting the form fails to send inquiry data to any backend server.
- **Severity:** **Medium**

### 22. Privacy Policy (`/privacy/`)
- **Path:** `/privacy/`
- **API / Network Calls Found:**
  - None (0 fetch, 0 XHR, 0 WebSocket calls found in page source).
- **Issues Found:**
  - None. Static legal documentation page.
- **Severity:** **Low**

### 23. Terms of Service (`/terms/`)
- **Path:** `/terms/`
- **API / Network Calls Found:**
  - None (0 fetch, 0 XHR, 0 WebSocket calls found in page source).
- **Issues Found:**
  - None. Static legal documentation page.
- **Severity:** **Low**

### 24. Cookie Policy (`/cookies/`)
- **Path:** `/cookies/`
- **API / Network Calls Found:**
  - None (0 fetch, 0 XHR, 0 WebSocket calls found in page source).
- **Issues Found:**
  - None. Static legal documentation page.
- **Severity:** **Low**

### 25. Security Policy (`/security/`)
- **Path:** `/security/`
- **API / Network Calls Found:**
  - None (0 fetch, 0 XHR, 0 WebSocket calls found in page source).
- **Issues Found:**
  - None. Static security disclosure page.
- **Severity:** **Low**

### 26. Disclaimer (`/disclaimer/`)
- **Path:** `/disclaimer/`
- **API / Network Calls Found:**
  - None (0 fetch, 0 XHR, 0 WebSocket calls found in page source).
- **Issues Found:**
  - None. Static legal disclaimer page.
- **Severity:** **Low**

### 27. Network Status (`/status/`)
- **Path:** `/status/`
- **API / Network Calls Found:**
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', id: 1 }) })`
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'system_health', id: 2 }) })`
  - `fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'amm_dex_getPoolCount', id: 3 }) })`
- **Issues Found:**
  - **Hardcoded Operational Indicators:** Subsystem health status pills (e.g. Bridge status, API availability %) are hardcoded green UI elements rather than dynamically computed from endpoint pings.
- **Severity:** **Medium**

### 28. API Documentation (`/api/`)
- **Path:** `/api/`
- **API / Network Calls Found:**
  - None (0 fetch, 0 XHR, 0 WebSocket calls found in page source).
- **Issues Found:**
  - **Root Endpoint 404:** Documented API root `GET https://verdischain.com/api/v1` returns HTTP 404 if requested directly without subpath.
- **Severity:** **Low**

---

## Severity Summary Matrix

| Severity | Count | Affected Pages | Summary of Issues |
| :--- | :---: | :--- | :--- |
| **Critical** | **3** | `/transactions/`, `/analytics/`, `/monitoring/` | Broken WebSockets returning 200 OK (`wss://.../substrate-ws`), and production pages making `http://localhost:9933` calls blocked by Mixed Content. |
| **High** | **3** | `/governance/`, `/sale/`, `/eco/` | `POST /api/governance` returning HTTP 501 Not Implemented; presale purchase form missing backend endpoint integration; entire eco metric dashboard using hardcoded mock values (`dummyHash`). |
| **Medium** | **11** | `/explorer/`, `/dex/`, `/wallet/`, `/tokenomics/`, `/faucet/`, `/validators/`, `/docs/`, `/developers/`, `/referral/`, `/incentives/`, `/contact/`, `/status/` | Mock data array fallbacks, timestamp formatting bugs, API 404 root returns, faucet stat file discrepancies, missing contact form POST handler. |
| **Low** | **11** | `/`, `/whitepaper/`, `/blog/`, `/download/`, `/privacy/`, `/terms/`, `/cookies/`, `/security/`, `/disclaimer/`, `/api/` | Minor RPC redundancy, static legal/documentation pages, static version string displays. |

---

## Recommended Remediation Steps

1. **Fix Nginx / Proxy WebSocket Upgrade Rules:**
   - Update Nginx configuration for location blocks `/substrate-ws` and `/ws` to properly handle `Upgrade` and `Connection` HTTP headers:
     ```nginx
     location /substrate-ws {
         proxy_pass http://127.0.0.1:9944;
         proxy_http_version 1.1;
         proxy_set_header Upgrade $http_upgrade;
         proxy_set_header Connection "Upgrade";
     }
     ```
2. **Replace Localhost Endpoints:**
   - Update `/analytics/` and `/monitoring/` JS source code to replace `"http://localhost:9933"` with relative relative endpoint `"/rpc"` or relative RPC URL `"https://verdischain.com/rpc"`.
3. **Implement Governance API Backend:**
   - Deploy backend router logic for `POST /api/governance` or proxy requests to Substrate governance extrinsics to resolve the HTTP 501 Not Implemented error.
4. **Wire Presale & Contact Form Submissions:**
   - Attach `fetch()` submit handlers on `/sale/` (sending order details to `/api/tx-relay` or payment processor) and on `/contact/` (sending form data to `/api/contact` or mail relay).
5. **Replace Mock Data with Dynamic RPC/API Calls:**
   - Replace static mock arrays on `/tokenomics/`, `/eco/`, `/explorer/`, and `/referral/` with dynamic queries to `/rpc` (`chain_getHeader`, `dpos_activeValidators`, `amm_dex_getAllPools`) and `/api/v1/...`.
