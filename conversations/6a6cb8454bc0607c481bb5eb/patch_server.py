#!/usr/bin/env python3
"""Patch server.js directly - add static serving, page routes, and missing endpoints."""
import re

path = "/opt/verdis/app/dist/api/server.js"
with open(path) as f:
    c = f.read()

changes = []

# 1. Add static file serving after cors line
cors_marker = "this.app.use((0, cors_1.default)());"
if cors_marker in c and "express_1.default.static" not in c:
    static_code = '\n        // Static files\n        const webDir = path_1.default.resolve(__dirname, "../web");\n        this.app.use("/css", express_1.default.static(path_1.default.join(webDir, "css")));\n        this.app.use(express_1.default.static(webDir));'
    c = c.replace(cors_marker, cors_marker + static_code)
    changes.append("Added static file serving (/css, /web)")
elif "express_1.default.static" in c:
    changes.append("Static serving already present")

# 2. Add page routes before the /api/network/info route
network_marker = "this.app.get('/api/network/info'"
if network_marker in c and 'this.app.get("/ecosystem"' not in c:
    page_routes = '''        // Page routes
        this.app.get("/ecosystem", (req, res) => { try { res.sendFile(path_1.default.resolve(__dirname, "../web/ecosystem.html")); } catch(e) { res.status(404).send("Not found"); } });
        this.app.get("/whitepaper", (req, res) => { try { res.sendFile(path_1.default.resolve(__dirname, "../web/whitepaper.html")); } catch(e) { res.status(404).send("Not found"); } });
        this.app.get("/api-docs", (req, res) => { try { res.sendFile(path_1.default.resolve(__dirname, "../web/api-docs.html")); } catch(e) { res.status(404).send("Not found"); } });
        this.app.get("/status", (req, res) => { try { res.sendFile(path_1.default.resolve(__dirname, "../web/status.html")); } catch(e) { res.status(404).send("Not found"); } });
        this.app.get("/templates", (req, res) => { try { res.sendFile(path_1.default.resolve(__dirname, "../web/templates.html")); } catch(e) { res.status(404).send("Not found"); } });
        this.app.get("/token-sale", (req, res) => { try { res.sendFile(path_1.default.resolve(__dirname, "../web/token-sale.html")); } catch(e) { res.status(404).send("Not found"); } });
        this.app.get("/bridge", (req, res) => { try { res.sendFile(path_1.default.resolve(__dirname, "../web/bridge.html")); } catch(e) { res.status(404).send("Not found"); } });
        this.app.get("/markets", (req, res) => { try { res.sendFile(path_1.default.resolve(__dirname, "../web/markets.html")); } catch(e) { res.status(404).send("Not found"); } });
        this.app.get("/explorer", (req, res) => { try { res.sendFile(path_1.default.resolve(__dirname, "../web/explorer.html")); } catch(e) { res.status(404).send("Not found"); } });
        this.app.get("/download", (req, res) => { try { res.sendFile(path_1.default.resolve(__dirname, "../web/download.html")); } catch(e) { res.status(404).send("Not found"); } });
        this.app.get("/trust-connect", (req, res) => { try { res.sendFile(path_1.default.resolve(__dirname, "../web/trust-connect.html")); } catch(e) { res.status(404).send("Not found"); } });
        this.app.get("/docs", (req, res) => { try { res.sendFile(path_1.default.resolve(__dirname, "../web/api-docs.html")); } catch(e) { res.status(404).send("Not found"); } });
        this.app.get("/download/verdis-wallet.apk", (req, res) => { const apkPath = path_1.default.resolve(__dirname, "../web/verdis-wallet.apk"); if (fs_1.default.existsSync(apkPath)) { res.download(apkPath, "verdis-wallet.apk"); } else { res.status(404).send("APK not found"); } });

'''
    c = c.replace(network_marker, page_routes + "        " + network_marker)
    changes.append("Added 12 page routes")
elif 'this.app.get("/ecosystem"' in c:
    changes.append("Page routes already present")

# 3. Add analytics/track endpoint
if "analytics/track" not in c:
    analytics = 'this.app.post("/api/analytics/track", (req, res) => { res.json({ success: true }); });\n        this.app.get("/api/analytics/track", (req, res) => { res.json({ success: true }); });\n        '
    c = c.replace("this.app.get('/api/blockchain/info'", analytics + "this.app.get('/api/blockchain/info'")
    changes.append("Added /api/analytics/track")
else:
    changes.append("analytics/track already present")

# 4. Add blockchain/transactions endpoint
if "blockchain/transactions" not in c:
    tx_ep = 'this.app.get("/api/blockchain/transactions", (req, res) => { try { const limit = parseInt(req.query.limit) || 20; const chain = this.blockchain.getChain(); const allTxs = []; for (const block of chain) { for (const tx of block.transactions) { allTxs.push({ ...tx, blockIndex: block.header.index, timestamp: block.header.timestamp }); } } res.json(allTxs.reverse().slice(0, limit)); } catch (error) { res.status(500).json({ error: error.message }); } });\n        '
    c = c.replace("this.app.get('/api/blockchain/blocks'", tx_ep + "this.app.get('/api/blockchain/blocks'")
    changes.append("Added /api/blockchain/transactions")
else:
    changes.append("blockchain/transactions already present")

# 5. Add wallet/create-mnemonic endpoint
if "create-mnemonic" not in c:
    mn_ep = 'this.app.post("/api/wallet/create-mnemonic", (req, res) => { try { const { mnemonic, privateKey } = req.body; let wallet; if (privateKey && privateKey.trim()) { const pk = privateKey.startsWith("0x") ? privateKey : "0x" + privateKey; wallet = this.walletManager.importWallet(pk); } else if (mnemonic && mnemonic.trim()) { const seed = (0, crypto_1.sha256)(mnemonic.trim()); wallet = this.walletManager.importWallet("0x" + seed); } else { wallet = this.walletManager.createWallet(); } res.json({ privateKey: wallet.privateKey, publicKey: wallet.publicKey, address: wallet.address, balance: this.blockchain.getTokenSystem().getBalance(wallet.address), staked: this.blockchain.getTokenSystem().getStaked(wallet.address) }); } catch (error) { res.status(400).json({ error: error.message }); } });\n        '
    c = c.replace("this.app.post('/api/wallet/create'", mn_ep + "this.app.post('/api/wallet/create'")
    changes.append("Added /api/wallet/create-mnemonic")
else:
    changes.append("create-mnemonic already present")

# 6. Add faucet endpoint
if "faucet/claim" not in c:
    faucet = 'this.faucetClaims = new Map();\n        this.app.post("/api/faucet/claim", this.strictRateLimit.bind(this), (req, res) => { try { const { address } = req.body; if (!address) return res.status(400).json({ error: "Address required" }); const now = Date.now(); const lastClaim = this.faucetClaims.get(address) || 0; const cooldown = 3600000; if (now - lastClaim < cooldown) { return res.status(429).json({ error: "Cooldown active", retryAfterMinutes: Math.ceil((cooldown - (now - lastClaim)) / 60000) }); } this.blockchain.getTokenSystem().addBalance(address, 1000); this.faucetClaims.set(address, now); res.json({ success: true, address, amount: 1000, message: "1000 VCO sent", nextClaim: new Date(now + cooldown).toISOString() }); } catch (error) { res.status(500).json({ error: error.message }); } });\n        this.app.get("/api/faucet/status", (req, res) => { const address = req.query.address; if (address) { const lastClaim = this.faucetClaims.get(address) || 0; res.json({ address, lastClaim: new Date(lastClaim).toISOString(), cooldownMinutes: 60 }); } else { res.json({ amount: 1000, cooldownMinutes: 60, totalClaims: this.faucetClaims.size }); } });\n        '
    c = c.replace("this.app.get('/api/validators'", faucet + "this.app.get('/api/validators'")
    changes.append("Added /api/faucet/claim + /api/faucet/status")
else:
    changes.append("faucet already present")

# 7. Fix any remaining VRS in faucet messages
c = c.replace("1000 VRS sent", "1000 VCO sent")

# 8. Fix VRS in network/info
c = c.replace("symbol: 'VRS'", "symbol: 'VCO'")
c = c.replace("symbol: \"VRS\"", "symbol: \"VCO\"")

# 9. Fix VRS in features list
c = c.replace("Native VRS wallet", "Native VCO wallet")

# 10. Fix VRS in dashboard fallback HTML
c = c.replace("VRS Supply", "VCO Supply")
c = c.replace("'VRS'", "'VCO'")

with open(path, "w") as f:
    f.write(c)

print("=== PATCH SUMMARY ===")
for ch in changes:
    print(f"  {ch}")
print(f"\nTotal file size: {len(c)} bytes")
