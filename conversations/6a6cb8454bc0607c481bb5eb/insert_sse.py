#!/usr/bin/env python3
"""Insert SSE endpoint into server.js properly, preserving escape sequences."""

with open('/opt/verdis/app/dist/api/server.js', 'r') as f:
    content = f.read()

# Find the constructor's closing brace - it's right before start(port) {
# The pattern is: the URL routing handler ends with }); then a blank line, then }, then start(port)
old = """            if (fs_1.default.existsSync(filePath)) { res.sendFile(filePath); } else { next(); }
        });

    }
    start(port) {"""

# Build the SSE code with proper escaping (using raw strings where needed)
sse_code = (
    "            if (fs_1.default.existsSync(filePath)) { res.sendFile(filePath); } else { next(); }\n"
    "        });\n"
    "\n"
    "        // === SERVER-SENT EVENTS (Real-time stream) ===\n"
    '        this.app.get("/api/stream/events", (req, res) => {\n'
    "            res.writeHead(200, {\n"
    '                "Content-Type": "text/event-stream",\n'
    '                "Cache-Control": "no-cache",\n'
    '                "Connection": "keep-alive",\n'
    '                "Access-Control-Allow-Origin": "*",\n'
    '                "X-Accel-Buffering": "no"\n'
    "            });\n"
    '            res.write("retry: 3000\\n\\n");\n'
    '            res.write("event: connected\\n");\n'
    '            res.write("data: " + JSON.stringify({ time: Date.now(), chainId: 909 }) + "\\n\\n");\n'
    "            let lastBlock = 0;\n"
    "            const interval = setInterval(() => {\n"
    "                try {\n"
    "                    const state = this.blockchain.getState();\n"
    "                    const h = state.height || state.blockHeight || 0;\n"
    "                    if (h > lastBlock) {\n"
    "                        lastBlock = h;\n"
    "                        const blocks = this.blockchain.getRecentBlocks(1);\n"
    "                        const b = (blocks && blocks.length > 0) ? blocks[0] : null;\n"
    '                        res.write("event: block\\n");\n'
    '                        res.write("data: " + JSON.stringify({\n'
    "                            height: h,\n"
    '                            hash: b ? b.hash : "",\n'
    '                            validator: b && b.header ? (b.header.validator || "").slice(0, 20) + "..." : "",\n'
    "                            txCount: b && b.transactions ? b.transactions.length : 0,\n"
    "                            timestamp: b && b.header ? b.header.timestamp : Date.now()\n"
    '                        }) + "\\n\\n");\n'
    "                    }\n"
    "                } catch(e) {}\n"
    "            }, 3000);\n"
    '            const hb = setInterval(() => { try { res.write(": hb\\n\\n"); } catch(e) {} }, 30000);\n'
    '            req.on("close", () => { clearInterval(interval); clearInterval(hb); });\n'
    "        });\n"
    "\n"
    "    }\n"
    "    start(port) {"
)

if old in content:
    content = content.replace(old, sse_code, 1)
    with open('/opt/verdis/app/dist/api/server.js', 'w') as f:
        f.write(content)
    print("SSE endpoint inserted successfully")
else:
    print("ERROR: Could not find insertion point")
