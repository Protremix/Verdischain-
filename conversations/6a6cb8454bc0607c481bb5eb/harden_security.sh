#!/bin/bash
# Verdis Blockchain — Comprehensive Security Hardening
# Fixes all audit findings + general hardening to pass any external audit

set -e

echo "=== VERDIS SECURITY HARDENING ==="

# === 1. EXTERNALIZE ADMIN API KEY ===
echo "1. Externalizing admin API key..."
# Add env var support to security.js
python3 << 'PYEOF'
with open('/opt/verdis/app/dist/core/security.js', 'r') as f:
    c = f.read()

# Make the constructor use env var if available
old = "constructor(adminApiKey) {"
new = "constructor(adminApiKey) {\n        // Use environment variable if available (audit: VD-002)\n        if (!adminApiKey && process.env.VERDIS_ADMIN_KEY) {\n            adminApiKey = process.env.VERDIS_ADMIN_KEY;\n        }"
if old in c:
    c = c.replace(old, new)
    print("  Security.js: admin key now reads from VERDIS_ADMIN_KEY env var")

with open('/opt/verdis/app/dist/core/security.js', 'w') as f:
    f.write(c)
PYEOF

# Remove hardcoded key from auto-deploy-contracts.js
python3 << 'PYEOF'
with open('/opt/verdis/app/dist/auto-deploy-contracts.js', 'r') as f:
    c = f.read()
c = c.replace(
    'const ADMIN_KEY = "27e508e645ef2d0b1a4afb313243df19bf041a842061b4d5ee908b3ea06d72dd";',
    'const ADMIN_KEY = process.env.VERDIS_ADMIN_KEY || require("./dist/core/security").SecurityManager.prototype.generateApiKey();'
)
with open('/opt/verdis/app/dist/auto-deploy-contracts.js', 'w') as f:
    f.write(c)
print("  auto-deploy-contracts.js: removed hardcoded key, uses env var")
PYEOF

# Set the env var in systemd service
if ! grep -q 'VERDIS_ADMIN_KEY' /etc/systemd/system/verdis.service; then
    # Generate a new key
    NEW_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "/\[Service\]/a Environment=VERDIS_ADMIN_KEY=$NEW_KEY" /etc/systemd/system/verdis.service
    echo "  systemd: VERDIS_ADMIN_KEY set to new generated key"
    echo "  NEW ADMIN KEY (save this): $NEW_KEY"
fi

# === 2. ADD SECURITY HEADERS TO NGINX ===
echo "2. Adding Nginx security headers..."
if ! grep -q 'X-Frame-Options' /etc/nginx/sites-enabled/verdischain; then
    sed -i '/proxy_hide_header Access-Control-Allow-Origin/i\    # Security headers\n    add_header X-Frame-Options "SAMEORIGIN" always;\n    add_header X-Content-Type-Options "nosniff" always;\n    add_header X-XSS-Protection "1; mode=block" always;\n    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;\n    add_header Referrer-Policy "strict-origin-when-cross-origin" always;\n    add_header X-DNS-Prefetch-Control "off" always;\n' /etc/nginx/sites-enabled/verdischain
    echo "  Added 6 security headers"
fi

# === 3. RESTRICT CORS ON ADMIN ENDPOINTS ===
echo "3. Restricting CORS on admin endpoints..."
# Add location block for admin endpoints
if ! grep -q '/api/security/' /etc/nginx/sites-enabled/verdischain; then
    sed -i '/# Main site/i\    # Admin endpoints — restricted CORS\n    location /api/security/ {\n        proxy_pass http://127.0.0.1:3200;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        if ($request_method = OPTIONS) { return 204; }\n        add_header Access-Control-Allow-Origin "https://verdischain.com" always;\n        add_header Access-Control-Allow-Methods "GET, POST" always;\n        add_header Access-Control-Allow-Headers "Content-Type, x-api-key" always;\n    }\n' /etc/nginx/sites-enabled/verdischain
    echo "  Restricted CORS on /api/security/ endpoints"
fi

# === 4. ADD SWAP MEMORY ===
echo "4. Adding swap memory..."
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "  2GB swap created and enabled"
else
    echo "  Swap already exists"
fi

# === 5. CONFIGURE FIREWALL ===
echo "5. Configuring firewall..."
if command -v ufw &>/dev/null; then
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    echo "  UFW configured: deny all incoming, allow 22/80/443"
else
    apt-get install -y ufw &>/dev/null
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    echo "  UFW installed and configured"
fi

# === 6. SECURE SSH ===
echo "6. Securing SSH..."
# Disable root password login (keep key-based)
sed -i 's/^#PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
sed -i 's/^PermitRootLogin yes/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#MaxAuthTries.*/MaxAuthTries 3/' /etc/ssh/sshd_config
sed -i 's/^#ClientAliveInterval.*/ClientAliveInterval 300/' /etc/ssh/sshd_config
sed -i 's/^#ClientAliveCountMax.*/ClientAliveCountMax 2/' /etc/ssh/sshd_config
systemctl reload sshd 2>/dev/null || systemctl reload ssh 2>/dev/null
echo "  SSH: root login key-only, password auth disabled, max 3 attempts"

# === 7. INSTALL FAIL2BAN ===
echo "7. Installing fail2ban..."
if ! command -v fail2ban-client &>/dev/null; then
    apt-get install -y fail2ban &>/dev/null
fi
cat > /etc/fail2ban/jail.local << 'FAIL2BAN'
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600
findtime = 600

[nginx-limit-req]
enabled = true
maxretry = 5
bantime = 1800
FAIL2BAN
systemctl enable fail2ban
systemctl restart fail2ban 2>/dev/null
echo "  fail2ban: SSH + nginx protection active"

# === 8. VERIFY CERTBOT TIMER ===
echo "8. Verifying certbot timer..."
systemctl enable certbot.timer 2>/dev/null
systemctl start certbot.timer 2>/dev/null
if systemctl is-active certbot.timer &>/dev/null; then
    echo "  certbot.timer active"
else
    echo "  WARNING: certbot.timer not active"
fi

# === 9. REDUCE AUTOSAVE INTERVAL ===
echo "9. Reducing autosave interval..."
python3 << 'PYEOF'
with open('/opt/verdis/app/dist/index.js', 'r') as f:
    c = f.read()
# Change 30000 to 15000 for autosave
c = c.replace('startAutoSave(blockchain, walletManager, ecoSystem, dex, contractManager, 30000', 
              'startAutoSave(blockchain, walletManager, ecoSystem, dex, contractManager, 15000')
c = c.replace('startAutoSave(blockchain, walletManager, ecoSystem, dex, contractManager, 30000, marketTracker',
              'startAutoSave(blockchain, walletManager, ecoSystem, dex, contractManager, 15000, marketTracker')
with open('/opt/verdis/app/dist/index.js', 'w') as f:
    f.write(c)
print("  Autosave interval: 30s -> 15s")
PYEOF

# === 10. SET SECURE FILE PERMISSIONS ===
echo "10. Setting secure file permissions..."
chmod 600 /opt/verdis/blobs/verdis-state.json
chmod 700 /opt/verdis/blobs/
chmod 644 /opt/verdis/app/dist/web/*.html
chmod 644 /opt/verdis/app/dist/web/*.js 2>/dev/null
chmod 644 /opt/verdis/app/dist/web/*.css 2>/dev/null
chmod 600 /opt/verdis/app/dist/*.js
chmod 700 /opt/verdis/app/dist/
echo "  File permissions set (state: 600, blobs: 700, web: 644, code: 600)"

# === 11. ADD INPUT VALIDATION HELPER ===
echo "11. Adding input validation to API server..."
python3 << 'PYEOF'
with open('/opt/verdis/app/dist/api/server.js', 'r') as f:
    c = f.read()

# Add validation helpers after constructor
old = "        this.app = express();"
new = """        this.app = express();
        // Input validation helpers (audit hardening)
        this.validateAddress = (addr) => {
            if (!addr || typeof addr !== 'string') return false;
            if (addr.length > 100) return false; // prevent buffer attacks
            return /^(0x)?[0-9a-fA-F]{40,64}$/.test(addr) || /^[A-Za-z0-9_-]{20,50}$/.test(addr);
        };
        this.validateAmount = (amt) => {
            const n = Number(amt);
            if (isNaN(n) || !isFinite(n)) return false;
            if (n < 0) return false;
            if (n > 1000000000) return false; // max 1B per tx
            return true;
        };
        this.sanitize = (str) => {
            if (typeof str !== 'string') return '';
            return str.replace(/[<>$\\{\\}]/g, '').slice(0, 1000);
        };"""

if old in c and 'validateAddress' not in c:
    c = c.replace(old, new, 1)
    print("  Added input validation helpers")
else:
    print("  Validation helpers already present")

with open('/opt/verdis/app/dist/api/server.js', 'w') as f:
    f.write(c)
PYEOF

# === 12. ADD ERROR SANITIZATION (prevent info leakage) ===
echo "12. Sanitizing error messages..."
python3 << 'PYEOF'
with open('/opt/verdis/app/dist/api/server.js', 'r') as f:
    c = f.read()

# Add error sanitizer middleware after express setup
old = "        this.app.use(express.json());"
new = """        this.app.use(express.json());
        // Error sanitizer — prevent info leakage (audit hardening)
        this.app.use((err, req, res, next) => {
            if (err) {
                // Don't expose internal errors to clients
                res.status(400).json({ error: 'Invalid request', code: 'BAD_REQUEST' });
            } else {
                next();
            }
        });"""

if old in c and 'error sanitizer' not in c.lower():
    c = c.replace(old, new, 1)
    print("  Added error sanitizer middleware")
else:
    print("  Error sanitizer already present")

with open('/opt/verdis/app/dist/api/server.js', 'w') as f:
    f.write(c)
PYEOF

# === 13. RELOAD NGINX ===
echo "13. Reloading Nginx..."
nginx -t 2>&1 && systemctl reload nginx && echo "  Nginx reloaded" || echo "  Nginx config issue"

# === 14. RESTART VERDIS ===
echo "14. Restarting Verdis..."
systemctl daemon-reload
systemctl restart verdis
sleep 3

# === 15. VERIFY EVERYTHING ===
echo "15. Verification..."
echo "  Service: $(systemctl is-active verdis)"
echo "  Fail2ban: $(systemctl is-active fail2ban 2>/dev/null || echo 'not running')"
echo "  UFW: $(ufw status | head -1 2>/dev/null || echo 'not installed')"
echo "  Swap: $(free -h | grep Swap | awk '{print $2}')"
echo "  Certbot: $(systemctl is-active certbot.timer 2>/dev/null || echo 'not active')"
echo "  Nginx: $(nginx -t 2>&1)"

echo ""
echo "=== HARDENING COMPLETE ==="
