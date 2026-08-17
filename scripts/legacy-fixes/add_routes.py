#!/usr/bin/env python3
import sys

# 1. Add download page route to server
with open("/opt/verdis/app/dist/api/server.js", "r") as f:
    content = f.read()

if '/download"' not in content:
    old = "// === New page routes ==="
    new = """// === Download page ===
        this.app.get("/download", (req, res) => {
            const p = path_1.default.resolve(__dirname, "../web/download.html");
            if (fs_1.default.existsSync(p)) {
                res.sendFile(p);
            }
            else {
                res.status(404).json({ error: "Download page not found" });
            }
        });

        // === New page routes ==="""
    content = content.replace(old, new)
    with open("/opt/verdis/app/dist/api/server.js", "w") as f:
        f.write(content)
    print("Server route added!")
else:
    print("Server route already exists")

# 2. Add download link to landing page
with open("/opt/verdis/app/dist/web/landing.html", "r") as f:
    landing = f.read()

if "/download" not in landing:
    landing = landing.replace(
        "</nav>",
        '<a href="/download" style="color:#00ff88;font-weight:600;text-decoration:none;margin-left:12px;">Get App</a></nav>'
    )
    with open("/opt/verdis/app/dist/web/landing.html", "w") as f:
        f.write(landing)
    print("Landing page link added!")
else:
    print("Landing page already has download link")

# 3. Add download link to dashboard
with open("/opt/verdis/app/dist/web/dashboard.html", "r") as f:
    dash = f.read()

if "/download" not in dash:
    dash = dash.replace(
        "</header>",
        '<a href="/download" style="position:fixed;top:14px;right:60px;z-index:200;background:rgba(0,255,136,0.12);color:#00ff88;padding:6px 12px;border-radius:8px;font-size:12px;font-weight:600;border:1px solid rgba(0,255,136,0.4);text-decoration:none;">Get App</a></header>'
    )
    with open("/opt/verdis/app/dist/web/dashboard.html", "w") as f:
        f.write(dash)
    print("Dashboard link added!")
else:
    print("Dashboard already has download link")
