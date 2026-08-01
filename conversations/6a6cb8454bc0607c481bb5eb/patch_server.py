import sys

with open("/opt/verdis/app/dist/api/server.js") as f:
    content = f.read()

# 1. Import AI Registry
old_import = 'const jsonrpc_1 = require("./jsonrpc");'
new_import = '''const jsonrpc_1 = require("./jsonrpc");
const ai_registry_1 = require("../core/ai-registry");'''
if old_import in content:
    content = content.replace(old_import, new_import)
    print("1. Added AI Registry import")
else:
    print("1. ERROR: import not found")

# 2. Initialize AI Registry in constructor
# Find the customTokens line
old_init = 'this.customTokens = new Map();'
new_init = '''this.customTokens = new Map();
        this.aiRegistry = new ai_registry_1.AIAgentRegistry();'''
if old_init in content:
    content = content.replace(old_init, new_init, 1)
    print("2. Added AI Registry init")
else:
    print("2. ERROR: init pattern not found")

# 3. Add AI Registry endpoints before docs
marker = 'this.app.get("/api/docs"'
ai_endpoints = '''// === AI AGENT REGISTRY ===
        this.app.post("/api/ai/agent/register", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { agentId, ownerAddress, walletAddress, metadata } = req.body;
                if (!agentId || !ownerAddress || !walletAddress)
                    return res.status(400).json({ error: "agentId, ownerAddress, walletAddress required" });
                const result = this.aiRegistry.registerAgent(agentId, ownerAddress, walletAddress, metadata);
                if (!result.success)
                    return res.status(400).json({ error: result.error });
                res.json({ success: true, agent: result.agent });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.get("/api/ai/agents", (req, res) => {
            res.json(this.aiRegistry.getAllAgents());
        });
        this.app.get("/api/ai/agents/active", (req, res) => {
            res.json(this.aiRegistry.getActiveAgents());
        });
        this.app.get("/api/ai/agent/:agentId", (req, res) => {
            const agent = this.aiRegistry.getAgent(req.params.agentId);
            if (!agent) return res.status(404).json({ error: "Agent not found" });
            const perms = this.aiRegistry.getPermissions(req.params.agentId);
            res.json({ agent, permissions: perms });
        });
        this.app.post("/api/ai/agent/:agentId/permissions", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { ownerAddress, updates } = req.body;
                const result = this.aiRegistry.updatePermissions(req.params.agentId, ownerAddress, updates);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json({ success: true, permissions: result.permissions });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/ai/agent/:agentId/revoke", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { ownerAddress } = req.body;
                const result = this.aiRegistry.revokeAgent(req.params.agentId, ownerAddress);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json({ success: true });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/ai/agent/:agentId/reactivate", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { ownerAddress } = req.body;
                const result = this.aiRegistry.reactivateAgent(req.params.agentId, ownerAddress);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json({ success: true });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/ai/agent/:agentId/validate", (req, res) => {
            try {
                const { contractId, operation, gasEstimate, amount } = req.body;
                const result = this.aiRegistry.validateAgentAction(req.params.agentId, contractId, operation, gasEstimate || 0, amount || 0);
                res.json(result);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/ai/agent/:agentId/attest", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { txId, computation, proof } = req.body;
                const attestation = this.aiRegistry.submitAttestation(req.params.agentId, txId, computation, proof);
                res.json(attestation);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.get("/api/ai/agent/:agentId/attestations", (req, res) => {
            res.json(this.aiRegistry.getAttestations(req.params.agentId));
        });
        this.app.get("/api/ai/fraud/alerts", (req, res) => {
            const limit = parseInt(req.query.limit) || 50;
            res.json(this.aiRegistry.getFraudAlerts(limit));
        });
        this.app.get("/api/ai/stats", (req, res) => {
            res.json(this.aiRegistry.getStats());
        });
        this.app.get("/api/docs"'''

if marker in content:
    content = content.replace(marker, ai_endpoints, 1)
    print("3. Added AI Registry endpoints")
else:
    print("3. ERROR: docs marker not found")

with open("/opt/verdis/app/dist/api/server.js", "w") as f:
    f.write(content)
print("Server.js patched successfully!")
