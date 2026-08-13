import json

report_content = """# Comprehensive Web Audit Report — Verdis Chain Website
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

"""

pages_data = [
    {
        "name": "1. Home (`/`)",
        "path": "/",
        "calls": [
            "`fetch(RPC, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', params: [], id: 1 }) })`",
            "`fetch(RPC, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'system_health', params: [], id: 2 }) })`",
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'dpos_activeValidators', params: [], id: 10 }) })`",
            "`fetch(RPC, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'amm_dex_getAllPools', params: [], id: 3 }) })`",
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', params: [], id: 9 }) })`",
            "`fetchRpc('system_health')` & `fetchRpc('chain_getHeader')` via `verdis.js` targeting `https://rpc.verdischain.com`"
        ],
        "issues": [
            "**Redundant RPC Fetches:** Duplicated fetch calls between inline scripts and `verdis.js` execution on page load.",
            "**Hardcoded Fallback Counters:** HTML uses static `data-counter` attributes (`data-counter=\"20000\"`) that animate static values when RPC network latency occurs."
        ],
        "severity": "Low"
    },
    {
        "name": "2. Verdiscan Explorer (`/explorer/`)",
        "path": "/explorer/",
        "calls": [
            "`fetch(RPC, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', id: 1 }) })`",
            "`fetch(RPC, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getBlock', id: 1 }) })`",
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'amm_dex_getAllPools', id: 1 }) })`",
            "`fetch(API + path)` targeting `https://verdischain.com/api`",
            "`fetch('/api/v1/token/holders')`",
            "`fetch('/price-history.json?_=' + Date.now())`"
        ],
        "issues": [
            "**Hardcoded Mock Arrays:** Extensive inline JS mock arrays (`const blocksData = [...]`, static sample addresses `vrd1sample...`) are embedded to display fallback table data if RPC calls fail or lag.",
            "**Timestamp Parsing Bug Workaround:** `verdis.js` contains a DOM MutationObserver explicitly listening for a '20669d ago' string bug in the recent activity table, indicating raw block timestamp formatting defects in block display logic."
        ],
        "severity": "Medium"
    },
    {
        "name": "3. Verdis DEX (`/dex/`)",
        "path": "/dex/",
        "calls": [
            "`fetch(RPC_URL, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'amm_dex_getAllPools', id: Date.now() }) })` (defines `RPC_URL = 'https://verdischain.com/rpc/'`)",
            "`fetch('/api/tx-relay', { method: 'POST', body: JSON.stringify({ action: 'swap', pool_id: pool.id, token_in: currentTokenIn, amount_in: chainAmountIn, min_amount_out: minAmountOut }) })`"
        ],
        "issues": [
            "**Transaction Relay Error Handling:** Swapping tokens posts to `/api/tx-relay`. If wallet connection or parameter validation fails, endpoint returns HTTP 400 Bad Request without detailed UI feedback.",
            "**Static Pool Fallbacks:** DEX liquidity pools fallback to static preset array when RPC pool query fails."
        ],
        "severity": "Medium"
    },
    {
        "name": "4. Whitepaper (`/whitepaper/`)",
        "path": "/whitepaper/",
        "calls": [
            "`fetch(RPC_URL, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', id: Date.now() }) })` (defines `RPC_URL = '/rpc'`)"
        ],
        "issues": [
            "None. Standard header block height fetch executed successfully."
        ],
        "severity": "Low"
    },
    {
        "name": "5. Web3 Wallet (`/wallet/`)",
        "path": "/wallet/",
        "calls": [
            "`fetch(RPC_URL, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', id: 1 }) })` (`RPC_URL = 'https://verdischain.com/rpc'`)",
            "`fetch(API_URL + path)` (`API_URL = 'https://verdischain.com/api/v1'`)",
            "`fetch('/api/v1/account/${address}')`",
            "`fetch('/api/v1/account/' + myAddr + '/transactions?limit=100')`",
            "`fetch('/api/tx-relay', { method: 'POST', body: JSON.stringify({ action: 'pin-status', address }) })`",
            "`fetch('/api/tx-relay', { method: 'POST', body: JSON.stringify({ action: 'pin-verify', address, pin }) })`",
            "`fetch('/api/tx-relay', { method: 'POST', body: JSON.stringify({ action: 'pin-register', address, pin }) })`",
            "`fetch('/api/tx-relay', { method: 'POST', body: JSON.stringify({ action: 'wallet-backup', email, ciphertext, salt, iv, address, pin }) })`",
            "`fetch('/api/tx-relay', { method: 'POST', body: JSON.stringify({ action: 'wallet-recover', email, pin }) })`",
            "`fetch(RELAY_URL, { method: 'POST', body: JSON.stringify({ action: 'submit-extrinsic', extrinsic }) })`"
        ],
        "issues": [
            "**Base API Endpoint 404:** `const API_URL = 'https://verdischain.com/api/v1'` returns HTTP 404 if accessed at root path (requires appending subpaths like `/account/${address}`).",
            "**Hardcoded Sample Address:** Uses hardcoded sample account addresses (`vrd1sample...`) for initial state rendering."
        ],
        "severity": "Medium"
    },
    {
        "name": "6. VRDX Token Sale (`/sale/`)",
        "path": "/sale/",
        "calls": [
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', params: [], id: 1 }) })`"
        ],
        "issues": [
            "**Missing Fetch Calls (High):** The presale token purchase form on `/sale/` contains no `fetch()` call or API handler to process or transmit buy orders to a backend contract or relay service. The form operates solely as a client-side calculator without transaction execution."
        ],
        "severity": "High"
    },
    {
        "name": "7. VRDX Tokenomics (`/tokenomics/`)",
        "path": "/tokenomics/",
        "calls": [
            "None (0 fetch, 0 XHR, 0 WebSocket calls found in page source)."
        ],
        "issues": [
            "**Hardcoded Data:** Token supply metrics, allocation percentages, vesting schedules, and Chart.js datasets are entirely hardcoded static numbers.",
            "**Missing Fetch Calls:** No dynamic API calls exist to query live circulating supply or token distribution stats from the blockchain."
        ],
        "severity": "Medium"
    },
    {
        "name": "8. Verdis Faucet (`/faucet/`)",
        "path": "/faucet/",
        "calls": [
            "`fetch(FAUCET_API, { method: 'POST', body: JSON.stringify({ address: addr, token: selectedToken }) })` (`FAUCET_API = 'https://verdischain.com/faucet/api'`)",
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', id: 1 }) })`",
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'system_health', id: 2 }) })`",
            "`fetch('/faucet/stats.json')`",
            "`fetch('/faucet/api/stats')`"
        ],
        "issues": [
            "**Inconsistent Faucet Stat Sources:** Page queries both `/faucet/stats.json` (returns all zeros `{\"totalDispensed\":0...}`) and `/faucet/api/stats` (returns active stats `{\"totalDispensed\":100...}`), leading to potential UI stat mismatches."
        ],
        "severity": "Medium"
    },
    {
        "name": "9. Validators & DPoS (`/validators/`)",
        "path": "/validators/",
        "calls": [
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'dpos_activeValidators', params: [], id: 1 }) })`",
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'dpos_validatorName', params: [val], id: 1 }) })`",
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'dpos_validatorStake', params: [val], id: 1 }) })`",
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'eco_getGreenScore', params: [val], id: 1 }) })`"
        ],
        "issues": [
            "**Missing Action Handlers:** Staking and nomination buttons lack an active extrinsic signing or submission call to `/api/tx-relay`."
        ],
        "severity": "Medium"
    },
    {
        "name": "10. Eco Metrics (`/eco/`)",
        "path": "/eco/",
        "calls": [
            "None (0 fetch, 0 XHR, 0 WebSocket calls found in page source)."
        ],
        "issues": [
            "**Hardcoded Data & Missing Fetch Calls (High):** Carbon offset statistics, energy savings comparisons, tree counter figures, and carbon credit proof hashes (`dummyHash`) are completely hardcoded static HTML elements with no API fetch logic."
        ],
        "severity": "High"
    },
    {
        "name": "11. Documentation (`/docs/`)",
        "path": "/docs/",
        "calls": [
            "`fetch('https://verdischain.com/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', id: 1 }) })`"
        ],
        "issues": [
            "**Documented Endpoint Failure:** Documentation examples instruct developers to connect to `wss://verdischain.com/ws`, which fails WebSocket upgrade handshakes in production (returns HTTP 200)."
        ],
        "severity": "Medium"
    },
    {
        "name": "12. Transactions Explorer (`/transactions/`)",
        "path": "/transactions/",
        "calls": [
            "`fetch(RPC, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method, params, id: 1 }) })`",
            "`new WebSocket('wss://verdischain.com/substrate-ws')` (`WS_URL = 'wss://verdischain.com/substrate-ws'`)"
        ],
        "issues": [
            "**CRITICAL BROKEN WEBSOCKET ENDPOINT:** `wss://verdischain.com/substrate-ws` fails WebSocket handshake (server returns `HTTP/1.1 200 OK` JSON/HTML instead of `101 Switching Protocols`), throwing an immediate browser WebSocket connection error and disabling live transaction streaming."
        ],
        "severity": "Critical"
    },
    {
        "name": "13. Verdis Analytics (`/analytics/`)",
        "path": "/analytics/",
        "calls": [
            "`fetch(url, { method: 'POST', body: JSON.stringify(payload) })` (where `url` contains `'http://localhost:9933'` and `'/rpc'`)"
        ],
        "issues": [
            "**CRITICAL BROKEN / WRONG ENDPOINT:** Hardcoded `http://localhost:9933` target URL in JS analytics runner. When loaded over HTTPS (`https://verdischain.com/analytics/`), browser security blocks the HTTP call due to Mixed Content restrictions and fails with `ERR_CONNECTION_REFUSED`.",
            "**Hardcoded Data:** Historical network chart analytics use static pre-populated numerical arrays."
        ],
        "severity": "Critical"
    },
    {
        "name": "14. Validator Monitor (`/monitoring/`)",
        "path": "/monitoring/",
        "calls": [
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify(payload) })`",
            "`fetch('http://localhost:9933', { method: 'POST', body: JSON.stringify(payload) })`"
        ],
        "issues": [
            "**CRITICAL BROKEN / WRONG ENDPOINT:** Explicit `fetch('http://localhost:9933')` in monitoring script causes Mixed Content blockage and connection refused errors on production deployment.",
            "**Hardcoded Data:** Validator uptime graphs and latency metrics rely on hardcoded static sample data."
        ],
        "severity": "Critical"
    },
    {
        "name": "15. Governance Protocol (`/governance/`)",
        "path": "/governance/",
        "calls": [
            "`fetch(RPC_URL, { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method, params, id: 1 }) })`",
            "`fetch('/api/governance')`",
            "`fetch(TX_RELAY_URL, { method: 'POST', body: JSON.stringify({ action: 'submit-extrinsic', ... }) })`"
        ],
        "issues": [
            "**BROKEN ENDPOINT (501 Not Implemented):** Submitting governance proposals or votes sends `POST /api/governance`, which returns HTTP `501 Not Implemented` HTML error page from the server.",
            "**Static Proposal Fallback:** Governance proposal list falls back to static hardcoded referendum objects when endpoint fails."
        ],
        "severity": "High"
    },
    {
        "name": "16. Blog (`/blog/`)",
        "path": "/blog/",
        "calls": [
            "`loadLiveStats()` via `verdis.js` calling `https://rpc.verdischain.com` (0 inline fetch calls)"
        ],
        "issues": [
            "**Hardcoded Data:** All blog articles, press releases, and publication dates are static HTML elements with no CMS or API fetch handler."
        ],
        "severity": "Low"
    },
    {
        "name": "17. Developer Portal (`/developers/`)",
        "path": "/developers/",
        "calls": [
            "`fetch(endpoint, { method: 'POST', body: JSON.stringify(payload) })` (Interactive RPC runner playground)"
        ],
        "issues": [
            "Interactive playground defaults to `/rpc` (operational), but code snippet examples reference non-functional WebSocket endpoint `wss://verdischain.com/ws`."
        ],
        "severity": "Medium"
    },
    {
        "name": "18. Download (`/download/`)",
        "path": "/download/",
        "calls": [
            "`loadLiveStats()` via `verdis.js` (0 inline fetch calls)"
        ],
        "issues": [
            "**Hardcoded Data:** Node binary version strings, SHA-256 checksums, and release download links are hardcoded static HTML strings."
        ],
        "severity": "Low"
    },
    {
        "name": "19. Referral Program (`/referral/`)",
        "path": "/referral/",
        "calls": [
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', params: [], id: 1 }) })`"
        ],
        "issues": [
            "**Hardcoded Data & Missing Fetch Calls:** Affiliate leaderboard renders hardcoded placeholder string (`No affiliates yet...`). Lacks backend API endpoint integration to fetch or register unique affiliate referral codes."
        ],
        "severity": "Medium"
    },
    {
        "name": "20. Validator Incentives (`/incentives/`)",
        "path": "/incentives/",
        "calls": [
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', id: 1 }) })`",
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method, params, id: Math.random() }) })`"
        ],
        "issues": [
            "**Hardcoded Calculations:** Reward projection calculator uses hardcoded yield multipliers rather than pulling live inflation and reward pool params via RPC."
        ],
        "severity": "Medium"
    },
    {
        "name": "21. Contact Page (`/contact/`)",
        "path": "/contact/",
        "calls": [
            "None (0 fetch, 0 XHR, 0 WebSocket calls found in page source)."
        ],
        "issues": [
            "**Missing Fetch Calls:** Contact form lacks a JavaScript event listener or `fetch()` POST endpoint handler. Submitting the form fails to send inquiry data to any backend server."
        ],
        "severity": "Medium"
    },
    {
        "name": "22. Privacy Policy (`/privacy/`)",
        "path": "/privacy/",
        "calls": [
            "None (0 fetch, 0 XHR, 0 WebSocket calls found in page source)."
        ],
        "issues": [
            "None. Static legal documentation page."
        ],
        "severity": "Low"
    },
    {
        "name": "23. Terms of Service (`/terms/`)",
        "path": "/terms/",
        "calls": [
            "None (0 fetch, 0 XHR, 0 WebSocket calls found in page source)."
        ],
        "issues": [
            "None. Static legal documentation page."
        ],
        "severity": "Low"
    },
    {
        "name": "24. Cookie Policy (`/cookies/`)",
        "path": "/cookies/",
        "calls": [
            "None (0 fetch, 0 XHR, 0 WebSocket calls found in page source)."
        ],
        "issues": [
            "None. Static legal documentation page."
        ],
        "severity": "Low"
    },
    {
        "name": "25. Security Policy (`/security/`)",
        "path": "/security/",
        "calls": [
            "None (0 fetch, 0 XHR, 0 WebSocket calls found in page source)."
        ],
        "issues": [
            "None. Static security disclosure page."
        ],
        "severity": "Low"
    },
    {
        "name": "26. Disclaimer (`/disclaimer/`)",
        "path": "/disclaimer/",
        "calls": [
            "None (0 fetch, 0 XHR, 0 WebSocket calls found in page source)."
        ],
        "issues": [
            "None. Static legal disclaimer page."
        ],
        "severity": "Low"
    },
    {
        "name": "27. Network Status (`/status/`)",
        "path": "/status/",
        "calls": [
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'chain_getHeader', id: 1 }) })`",
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'system_health', id: 2 }) })`",
            "`fetch('/rpc', { method: 'POST', body: JSON.stringify({ jsonrpc: '2.0', method: 'amm_dex_getPoolCount', id: 3 }) })`"
        ],
        "issues": [
            "**Hardcoded Operational Indicators:** Subsystem health status pills (e.g. Bridge status, API availability %) are hardcoded green UI elements rather than dynamically computed from endpoint pings."
        ],
        "severity": "Medium"
    },
    {
        "name": "28. API Documentation (`/api/`)",
        "path": "/api/",
        "calls": [
            "None (0 fetch, 0 XHR, 0 WebSocket calls found in page source)."
        ],
        "issues": [
            "**Root Endpoint 404:** Documented API root `GET https://verdischain.com/api/v1` returns HTTP 404 if requested directly without subpath."
        ],
        "severity": "Low"
    }
]

for p in pages_data:
    report_content += f"### {p['name']}\n"
    report_content += f"- **Path:** `{p['path']}`\n"
    report_content += f"- **API / Network Calls Found:**\n"
    for c in p['calls']:
        report_content += f"  - {c}\n"
    report_content += f"- **Issues Found:**\n"
    for i in p['issues']:
        report_content += f"  - {i}\n"
    report_content += f"- **Severity:** **{p['severity']}**\n\n"

report_content += """---

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
"""

with open("web_audit_report.md", "w", encoding="utf-8") as f:
    f.write(report_content)

print("Report generated successfully as web_audit_report.md")
