#!/usr/bin/env python3
"""Wire governance into index.js and add API endpoints"""

# 1. Update index.js to import and initialize governance
with open('/opt/verdis/app/dist/index.js') as f:
    index = f.read()

old_import = "const account_abstraction_1 = require(\"./core/account-abstraction\");"
new_import = """const account_abstraction_1 = require("./core/account-abstraction");
const governance_1 = require("./core/governance");
const verdis_sdk_1 = require("./core/verdis-sdk");"""
if old_import in index:
    index = index.replace(old_import, new_import)
    print("1. Added governance + SDK imports to index.js")
else:
    print("1. ERROR: import not found")

old_init = "const accountAbstraction = new account_abstraction_1.AccountAbstraction();\nexports.accountAbstraction = accountAbstraction;"
new_init = """const accountAbstraction = new account_abstraction_1.AccountAbstraction();
exports.accountAbstraction = accountAbstraction;
const governance = new governance_1.Governance(blockchain.getTokenSystem());
exports.governance = governance;"""
if old_init in index:
    index = index.replace(old_init, new_init)
    print("2. Added governance initialization")
else:
    print("2. ERROR: init not found")

old_wire = "apiServer.accountAbstraction = accountAbstraction;"
new_wire = "apiServer.accountAbstraction = accountAbstraction;\napiServer.governance = governance;"
if old_wire in index:
    index = index.replace(old_wire, new_wire)
    print("3. Wired governance to API server")
else:
    print("3. ERROR: wire not found")

with open('/opt/verdis/app/dist/index.js', 'w') as f:
    f.write(index)
print("index.js updated for governance\n")

# 2. Add governance API endpoints to server.js
with open('/opt/verdis/app/dist/api/server.js') as f:
    server = f.read()

marker = '// === NAME SERVICE (Human-Readable Addresses) ==='

gov_endpoints = '''// === GOVERNANCE ===
        this.app.post("/api/governance/proposal/create", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { proposer, title, description, proposalType, actions } = req.body;
                const ts = this.blockchain.getTokenSystem();
                const result = this.governance.createProposal(proposer, title, description, proposalType, actions, 0);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json(result);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/governance/vote", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { voter, proposalId, vote } = req.body;
                const result = this.governance.castVote(voter, proposalId, vote);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json(result);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.get("/api/governance/proposals", (req, res) => {
            res.json(this.governance.getAllProposals());
        });
        this.app.get("/api/governance/proposals/active", (req, res) => {
            res.json(this.governance.getActiveProposals());
        });
        this.app.get("/api/governance/proposal/:id", (req, res) => {
            const p = this.governance.getProposal(parseInt(req.params.id));
            if (!p) return res.status(404).json({ error: "Proposal not found" });
            res.json(p);
        });
        this.app.post("/api/governance/tally", (req, res) => {
            try {
                const { proposalId } = req.body;
                const result = this.governance.tallyVotes(proposalId);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json(result);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/governance/execute", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { proposalId, callerAddress } = req.body;
                const result = this.governance.executeProposal(proposalId, callerAddress);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json(result);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/governance/cancel", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { proposalId, callerAddress } = req.body;
                const result = this.governance.cancelProposal(proposalId, callerAddress);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json(result);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.get("/api/governance/stats", (req, res) => {
            res.json(this.governance.getStats());
        });

'''

if marker in server:
    server = server.replace(marker, gov_endpoints + marker, 1)
    print("4. Added governance API endpoints")
else:
    print("4. ERROR: marker not found")

# 3. Add SDK documentation endpoint
sdk_endpoint = '''
        // === SDK INFO ===
        this.app.get("/api/sdk/info", (req, res) => {
            res.json({
                name: "Verdis SDK",
                version: "1.0.0",
                install: "npm install verdis-sdk",
                rpcUrl: "https://rpc.verdischain.com",
                chainId: 909,
                features: ["wallet", "transactions", "dex", "contracts", "governance", "ai-agents", "name-service", "account-abstraction", "eco", "fraud-detection"],
                docs: "https://verdischain.com/api-docs",
            });
        });

'''
marker2 = '// === TOKENOMICS & GAS ABSTRACTION ==='
if marker2 in server:
    server = server.replace(marker2, sdk_endpoint + marker2, 1)
    print("5. Added SDK info endpoint")

with open('/opt/verdis/app/dist/api/server.js', 'w') as f:
    f.write(server)
print("server.js updated with governance + SDK endpoints!")
