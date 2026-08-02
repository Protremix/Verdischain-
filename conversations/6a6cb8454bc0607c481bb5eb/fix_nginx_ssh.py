#!/usr/bin/env python3
"""Fix Nginx security headers (move to server level) and SSH config."""

# === Fix Nginx ===
with open('/etc/nginx/sites-enabled/verdischain', 'r') as f:
    c = f.read()

# Move security headers to server level (after ssl_dhparam line)
# Remove them from inside location blocks first
import re

# Remove the security headers block from location / block
c = c.replace("""    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header X-DNS-Prefetch-Control "off" always;

        proxy_hide_header""", """        proxy_hide_header""")

# Also remove from /rpc block if present
c = c.replace("""    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header X-DNS-Prefetch-Control "off" always;

    proxy_pass""", """    proxy_pass""")

# Add at server level (after ssl_dhparam line)
server_headers = """    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers (applied at server level for all locations)
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header X-DNS-Prefetch-Control "off" always;"""

c = c.replace("    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;", server_headers)

with open('/etc/nginx/sites-enabled/verdischain', 'w') as f:
    f.write(c)

print("Nginx: Security headers moved to server level")

# === Fix SSH ===
with open('/etc/ssh/sshd_config', 'r') as f:
    lines = f.readlines()

new_lines = []
password_auth_set = False
for line in lines:
    stripped = line.strip()
    # Fix any PasswordAuthentication line
    if stripped.startswith('PasswordAuthentication') and not stripped.startswith('#'):
        new_lines.append('PasswordAuthentication no\n')
        password_auth_set = True
    elif stripped.startswith('#PasswordAuthentication'):
        new_lines.append('PasswordAuthentication no\n')
        password_auth_set = True
    else:
        new_lines.append(line)

if not password_auth_set:
    new_lines.append('PasswordAuthentication no\n')

with open('/etc/ssh/sshd_config', 'w') as f:
    f.writelines(new_lines)

print("SSH: PasswordAuthentication forced to no")
