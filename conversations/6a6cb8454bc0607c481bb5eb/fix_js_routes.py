#!/usr/bin/env python3
path = "/opt/verdis/app/dist/api/server.js"
with open(path) as f:
    c = f.read()

if "/ecosystem" in c and "sendFile" in c and c.count("/ecosystem") > 0:
    # Check if it's a route definition (not just in a comment)
    if 'this.app.get("/ecosystem"' in c or "this.app.get('/ecosystem'" in c:
        print("Page routes already exist in compiled JS")
        exit(0)

# Find the cors line
marker = "this.app.use((0, cors_1.default)());"
if marker not in c:
    print("ERROR: cors marker not found")
    exit(1)

routes = '''
        // Static files
        const webDir = path_1.default.resolve(__dirname, "../web");
        this.app.use("/css", express_1.default.static(path_1.default.join(webDir, "css")));
        this.app.use(express_1.default.static(webDir));
        // Page routes
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
        this.app.get("/download/verdis-wallet.apk", (req, res) => { const apkPath = path_1.default.resolve(__dirname, "../web/verdis-wallet.apk"); if (fs_1.default.existsSync(apkPath)) { res.download(apkPath, "verdis-wallet.apk"); } else { res.status(404).send("APK not found"); } });'''

c = c.replace(marker, marker + "\n" + routes)
with open(path, "w") as f:
    f.write(c)
print("Added static + page routes to compiled JS")
