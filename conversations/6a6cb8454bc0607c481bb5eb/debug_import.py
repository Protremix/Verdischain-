with open("/var/www/verdiscan/wallet/index.html") as f:
    content = f.read()

# Add debug alert at the start of importWallet
old = "window.importWallet = async function() {\n  const input = document.getElementById('importInput').value.trim();"
new = "window.importWallet = async function() {\n  console.log('[DEBUG] importWallet called');\n  alert('[DEBUG] importWallet called! PolkadotCrypto=' + (typeof window.PolkadotCrypto));\n  const input = document.getElementById('importInput').value.trim();"
content = content.replace(old, new)

with open("/var/www/verdiscan/wallet/index.html", "w") as f:
    f.write(content)

print("Debug alert added to importWallet")
