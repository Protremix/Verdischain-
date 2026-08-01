#!/usr/bin/env python3
"""Fix the trust-connect route formatting in server.js"""

with open("/opt/verdis/app/dist/api/server.js", "r") as f:
    content = f.read()

# The badly formatted line
bad_line = "this.app.get('/trust-connect', (req, res) => {            const p = path_1.default.resolve(__dirname, '../web/trust-connect.html');            if (fs_1.default.existsSync(p)) { res.sendFile(p); }            else { res.status(404).send('Trust connect page not found'); }        });"

# Well formatted version
good_lines = """        this.app.get('/trust-connect', (req, res) => {
            const p = path_1.default.resolve(__dirname, '../web/trust-connect.html');
            if (fs_1.default.existsSync(p)) { res.sendFile(p); return; }
            res.status(404).send('Trust connect page not found');
        });"""

if bad_line in content:
    content = content.replace(bad_line, good_lines)
    print("Fixed trust-connect route formatting")
else:
    print("Bad line not found - checking if route already exists properly")
    if "this.app.get('/trust-connect'" in content:
        print("Route exists - checking if it works")
    else:
        # Need to add it after explorer route
        explorer_end = "            res.status(404).send('Explorer page not found');\n        });"
        if explorer_end in content:
            content = content.replace(explorer_end, explorer_end + "\n" + good_lines)
            print("Added trust-connect route after explorer")
        else:
            print("ERROR: Could not find explorer route end")

with open("/opt/verdis/app/dist/api/server.js", "w") as f:
    f.write(content)

# Verify syntax
import subprocess
result = subprocess.run(["node", "-c", "/opt/verdis/app/dist/api/server.js"], capture_output=True, text=True)
if result.returncode == 0:
    print("✓ Syntax OK")
else:
    print("✗ Syntax error:", result.stderr[:200])
