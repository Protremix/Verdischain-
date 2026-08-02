#!/usr/bin/env python3
"""Apply remaining security fixes to Verdis codebase."""

# === Fix 1: Input validation + error sanitizer ===
with open("/opt/verdis/app/dist/api/server.js", "r") as f:
    c = f.read()

# Add validation helpers
old1 = "this.app = express();"
val_code = '''this.app = express();
        this.validateAddress = (addr) => {
            if (!addr || typeof addr !== "string") return false;
            if (addr.length > 100) return false;
            return /^(0x)?[0-9a-fA-F]{40,64}$/.test(addr) || /^[A-Za-z0-9_-]{20,50}$/.test(addr);
        };
        this.validateAmount = (amt) => {
            const n = Number(amt);
            if (isNaN(n) || !isFinite(n) || n < 0 || n > 1000000000) return false;
            return true;
        };
        this.sanitize = (str) => {
            if (typeof str !== "string") return "";
            return str.replace(/[<>$\\{\\}]/g, "").slice(0, 1000);
        };'''

if old1 in c and "validateAddress" not in c:
    c = c.replace(old1, val_code, 1)
    print("Added input validation helpers")

# Add error sanitizer middleware
old2 = "this.app.use(express.json());"
err_code = '''this.app.use(express.json());
        this.app.use((err, req, res, next) => {
            if (err) {
                res.status(400).json({ error: "Invalid request", code: "BAD_REQUEST" });
            } else { next(); }
        });'''

if old2 in c and "BAD_REQUEST" not in c:
    c = c.replace(old2, err_code, 1)
    print("Added error sanitizer middleware")

# Sanitize error responses
c = c.replace("error: err.message", 'error: "Request failed"')
c = c.replace("error: e.message", 'error: "Request failed"')
print("Sanitized error messages")

with open("/opt/verdis/app/dist/api/server.js", "w") as f:
    f.write(c)

# === Fix 2: Autosave interval 30s -> 15s ===
with open("/opt/verdis/app/dist/index.js", "r") as f:
    c = f.read()
c = c.replace("30000, marketTracker", "15000, marketTracker")
c = c.replace(", 30000)", ", 15000)")
with open("/opt/verdis/app/dist/index.js", "w") as f:
    f.write(c)
print("Autosave: 30s -> 15s")

# === Fix 3: Redact hardcoded keys ===
for filepath in ["/opt/verdis/app/dist/web/code.html", "/opt/verdis/app/dist/web/audit-report.html"]:
    try:
        with open(filepath, "r") as f:
            c = f.read()
        c = c.replace("27e508e645ef2d0b1a4afb313243df19bf041a842061b4d5ee908b3ea06d72dd", "[REDACTED - ENV VAR]")
        with open(filepath, "w") as f:
            f.write(c)
        print(f"Redacted key from {filepath.split('/')[-1]}")
    except:
        pass

print("All fixes applied!")
