#!/usr/bin/env python3
"""Fix eco system: add save endpoint, fix reforest update, fix green score persistence."""

# === 1. Add save endpoint to API ===
with open("/opt/verdis/app/dist/api/server.js", "r") as f:
    c = f.read()

# Add save endpoint after the network info endpoint
old_endpoint = "get('/api/network/info', (req, res) => {"
save_endpoint = """get('/api/network/info', (req, res) => {
        }, 200);
        this.app.get('/api/save', (req, res) => {
            try {
                this.saveStateNow();
                res.json({ success: true, message: 'State saved' });
            } catch (e) {
                res.json({ success: false });
            }
        });
        this.app.get('/api/network/info2', (req, res) => {"""

# Actually, let me use a simpler approach - just add the save endpoint
if "/api/save" not in c:
    # Find a good place to add it - after the public-url endpoint
    c = c.replace(
        "get('/api/public-url', (req, res) => {",
        "get('/api/save', (req, res) => {\n            try {\n                this.saveStateNow();\n                res.json({ success: true });\n            } catch(e) { res.json({ success: false }); }\n        });\n        this.app.get('/api/public-url', (req, res) => {"
    )
    print("Added /api/save endpoint")

# Add saveStateNow method to the class
if "saveStateNow" not in c:
    # Add after the constructor area, before the routes
    c = c.replace(
        "    }",
        "\n    saveStateNow() {\n        const { saveState } = require('../core/persistence');\n        saveState(this.blockchain, this.walletManager, this.eco, this.dex, this.contractManager, this.marketTracker);\n    }\n    }",
        1
    )
    print("Added saveStateNow method")

with open("/opt/verdis/app/dist/api/server.js", "w") as f:
    f.write(c)

# === 2. Fix reforest update to accept co2Sequestered and status ===
with open("/opt/verdis/app/dist/core/eco.js", "r") as f:
    c = f.read()

old_update = """updateReforestationProject(projectId, treesPlanted) {
        const project = this.reforestationProjects.get(projectId);
        if (!project) {
            return null;
        }
        project.treesPlanted = Math.max(0, treesPlanted);"""

new_update = """updateReforestationProject(projectId, treesPlanted, co2Override, statusOverride) {
        const project = this.reforestationProjects.get(projectId);
        if (!project) {
            return null;
        }
        project.treesPlanted = Math.max(0, treesPlanted);"""

if old_update in c:
    c = c.replace(old_update, new_update)

# Add co2 override after the calculation
old_co2 = "project.co2Sequestered = Math.max(0, kgCO2 / 1000); // metric tons"
new_co2 = """project.co2Sequestered = co2Override != null ? co2Override : Math.max(0, kgCO2 / 1000); // metric tons
        if (statusOverride) { project.status = statusOverride; }"""

if old_co2 in c:
    c = c.replace(old_co2, new_co2)
    print("Fixed reforest update to accept co2 and status overrides")

with open("/opt/verdis/app/dist/core/eco.js", "w") as f:
    f.write(c)

# === 3. Fix the reforest update API endpoint to pass co2 and status ===
with open("/opt/verdis/app/dist/api/server.js", "r") as f:
    c = f.read()

old_api = "const project = this.eco.updateReforestationProject(projectId, treesPlanted);"
new_api = "const project = this.eco.updateReforestationProject(projectId, treesPlanted, req.body.co2Sequestered, req.body.status);"

if old_api in c:
    c = c.replace(old_api, new_api)
    print("Fixed API endpoint to pass co2 and status")

with open("/opt/verdis/app/dist/api/server.js", "w") as f:
    f.write(c)

print("All eco fixes applied!")
