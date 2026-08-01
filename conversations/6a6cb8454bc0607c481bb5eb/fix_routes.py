#!/usr/bin/env python3
import sys

path = "/opt/verdis/app/src/api/server.ts"
with open(path) as f:
    c = f.read()

# Remove the broken page routes block
broken_start = "// Page routes"
broken_end_text = "res.status(404).send('APK not found');"
if broken_start in c:
    start_idx = c.index(broken_start)
    end_idx = c.index(broken_end_text) + len(broken_end_text)
    # Find the closing of that block
    remaining = c[end_idx:]
    close_idx = remaining.index("});") + 3
    c = c[:start_idx] + c[end_idx + close_idx:]
    print("Removed broken page routes")

# Add correct page routes
marker = "this.app.use(express_1.default.static(webDir));"
if marker in c:
    new_code = """
        // Page routes
        this.app.get("/ecosystem", (req, res) => res.sendFile(path_1.default.resolve(__dirname, "../web/ecosystem.html")));
        this.app.get("/whitepaper", (req, res) => res.sendFile(path_1.default.resolve(__dirname, "../web/whitepaper.html")));
        this.app.get("/api-docs", (req, res) => res.sendFile(path_1.default.resolve(__dirname, "../web/api-docs.html")));
        this.app.get("/status", (req, res) => res.sendFile(path_1.default.resolve(__dirname, "../web/status.html")));
        this.app.get("/templates", (req, res) => res.sendFile(path_1.default.resolve(__dirname, "../web/templates.html")));
        this.app.get("/token-sale", (req, res) => res.sendFile(path_1.default.resolve(__dirname, "../web/token-sale.html")));
        this.app.get("/bridge", (req, res) => res.sendFile(path_1.default.resolve(__dirname, "../web/bridge.html")));
        this.app.get("/markets", (req, res) => res.sendFile(path_1.default.resolve(__dirname, "../web/markets.html")));
        this.app.get("/explorer", (req, res) => res.sendFile(path_1.default.resolve(__dirname, "../web/explorer.html")));
        this.app.get("/download", (req, res) => res.sendFile(path_1.default.resolve(__dirname, "../web/download.html")));
        this.app.get("/trust-connect", (req, res) => res.sendFile(path_1.default.resolve(__dirname, "../web/trust-connect.html")));
        this.app.get("/docs", (req, res) => res.sendFile(path_1.default.resolve(__dirname, "../web/api-docs.html")));
        this.app.get("/download/verdis-wallet.apk", (req, res) => {
            const apkPath = path_1.default.resolve(__dirname, "../web/verdis-wallet.apk");
            if (fs_1.default.existsSync(apkPath)) { res.download(apkPath, "verdis-wallet.apk"); }
            else { res.status(404).send("APK not found"); }
        });"""
    c = c.replace(marker, marker + "\n" + new_code)
    with open(path, "w") as f:
        f.write(c)
    print("Added corrected page routes")
else:
    print("ERROR: Marker not found")
