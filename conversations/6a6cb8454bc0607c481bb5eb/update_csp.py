with open("/etc/nginx/sites-enabled/verdischain-com.conf") as f:
    content = f.read()

old_csp = "script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'"
new_csp = "script-src 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval'"
content = content.replace(old_csp, new_csp)

with open("/etc/nginx/sites-enabled/verdischain-com.conf", "w") as f:
    f.write(content)

# Verify
with open("/etc/nginx/sites-enabled/verdischain-com.conf") as f:
    c = f.read()
if "unsafe-eval' 'wasm-unsafe-eval" in c:
    print("CSP updated successfully - unsafe-eval added")
else:
    print("ERROR: CSP not updated")
