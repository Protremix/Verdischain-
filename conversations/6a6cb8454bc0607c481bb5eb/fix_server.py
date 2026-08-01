#!/usr/bin/env python3
"""Fix the server.js to add /trust-connect route"""

with open("/opt/verdis/app/dist/api/server.js", "r") as f:
    content = f.read()

# Find the explorer route block
explorer_end = "else { res.status(404).send('Explorer page not found'); }\n        });"

if explorer_end in content:
    # Add trust-connect route right after the explorer route
    trust_connect_route = explorer_end + """
        this.app.get('/trust-connect', (req, res) => {
            const p = path_1.default.resolve(__dirname, '../web/trust-connect.html');
            if (fs_1.default.existsSync(p)) { res.sendFile(p); }
            else { res.status(404).send('Trust connect page not found'); }
        });"""
    content = content.replace(explorer_end, trust_connect_route)
    print("Added /trust-connect route after /explorer")
else:
    print("ERROR: Could not find explorer route block")

# Add /trust-connect to pageRoutes array
old_routes = "'/api/explorer/stats']"
new_routes = "'/api/explorer/stats', '/trust-connect']"
if old_routes in content:
    content = content.replace(old_routes, new_routes)
    print("Added /trust-connect to pageRoutes")
else:
    print("Could not find pageRoutes to update")

with open("/opt/verdis/app/dist/api/server.js", "w") as f:
    f.write(content)
print("Server.js updated!")
