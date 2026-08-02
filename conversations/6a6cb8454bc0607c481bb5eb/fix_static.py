with open("/opt/verdis/app/dist/api/server.js", "r") as f:
    c = f.read()

# Find the express.json line and add static serving after it
import re

# The line we're looking for has single quotes around 10mb
match = re.search(r"this\.app\.use\(express_1\.default\.json\(\{ limit: '10mb' \}\)\);", c)
if match:
    old_line = match.group(0)
    new_code = old_line + """
        // Serve all static HTML files from web directory
        const webDir = path_1.default.resolve(__dirname, '../web');
        this.app.use(express_1.default.static(webDir));
        // Route without .html extension -> serve .html file
        this.app.use((req, res, next) => {
            if (req.method === 'GET' && !req.path.startsWith('/api') && !req.path.startsWith('/rpc')) {
                const cleanPath = req.path.split('?')[0].replace(/^\\//, '').replace(/\\/$/, '');
                if (cleanPath && !cleanPath.includes('.')) {
                    const candidate = path_1.default.resolve(webDir, cleanPath + '.html');
                    if (fs_1.default.existsSync(candidate) && fs_1.default.statSync(candidate).isFile()) {
                        return res.sendFile(candidate);
                    }
                }
            }
            next();
        });"""
    c = c.replace(old_line, new_code, 1)
    print("Static file serving added")
else:
    print("ERROR: Could not find express.json line")

with open("/opt/verdis/app/dist/api/server.js", "w") as f:
    f.write(c)
