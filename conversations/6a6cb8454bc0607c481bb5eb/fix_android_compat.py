#!/usr/bin/env python3
"""Fix Android API compatibility issues."""

filepath = "/opt/verdis/app/dist/api/server.js"
with open(filepath, "r") as f:
    content = f.read()

patches = []

# FIX 1: Add /api/transaction/submit as alias for /api/transaction/send
# Find the existing /api/transaction/send route and add an alias after it
old_send = "this.app.post('/api/transaction/send', this.strictRateLimit.bind(this), (req, res) => {"
new_with_alias = "this.app.post('/api/transaction/submit', this.strictRateLimit.bind(this), (req, res) => {\n            // Alias - forward to same handler\n            const nextHandler = () => {};\n        });\n        this.app.post('/api/transaction/send', this.strictRateLimit.bind(this), (req, res) => {"

# Actually, a better approach: add a simple alias before the real route
# Let me find the exact location
if "this.app.post('/api/transaction/submit'" not in content:
    # Add submit alias right before the send route
    content = content.replace(
        old_send,
        "this.app.post('/api/transaction/submit', this.strictRateLimit.bind(this), (req, res) => {\n            // Alias for Android app compatibility - delegates to /api/transaction/send logic\n            const { from, to, amount, fee, nonce, signature, publicKey } = req.body;\n            try {\n                const tx = this.blockchain.createTransaction(from, to, parseFloat(amount), parseFloat(fee || 0), parseInt(nonce || 0), signature, publicKey);\n                const added = this.blockchain.getMempool().addTransaction(tx, this.blockchain.getTokenSystem().getBalancesMap());\n                if (!added) { res.status(400).json({ success: false, error: 'Transaction rejected by mempool' }); return; }\n                res.json({ success: true, txId: tx.id, hash: tx.hash, message: 'Transaction submitted to mempool' });\n            } catch (error) { res.status(400).json({ success: false, error: error.message }); }\n        });\n        " + old_send
    )
    patches.append("Fix 1: Added /api/transaction/submit alias for Android compatibility")

# FIX 2: Add ECOGR to DEX token balances endpoint
old_tokens = "const tokens = ['CARBON', 'ECO', 'TREE', 'GREEN', 'REDD'];"
new_tokens = "const tokens = ['CARBON', 'ECO', 'TREE', 'GREEN', 'REDD', 'ECOGR'];"
if old_tokens in content:
    content = content.replace(old_tokens, new_tokens)
    patches.append("Fix 2: Added ECOGR to DEX token balances endpoint")

with open(filepath, "w") as f:
    f.write(content)

print("Patches applied:")
for p in patches:
    print("  OK: " + p)
