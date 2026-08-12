import hashlib, base64

# Calculate correct SRI hash
with open("/var/www/verdiscan/wallet/polkadot-crypto-bundle.js", "rb") as f:
    file_bytes = f.read()

hash_bytes = hashlib.sha384(file_bytes).digest()
sri_hash = base64.b64encode(hash_bytes).decode("utf-8")
new_integrity = "sha384-" + sri_hash

print("New SRI hash: " + new_integrity)

# Update the HTML
with open("/var/www/verdiscan/wallet/index.html") as f:
    content = f.read()

# Replace old integrity with new
old_integrity = 'integrity="sha384-2QXsXbfa3TM9LfvO3HH9+yTkUxC18OUn4AaH3iz6DqKDVswqkF6vrvttF/nDCjMa"'
new_integrity_attr = 'integrity="' + new_integrity + '"'
content = content.replace(old_integrity, new_integrity_attr)

# Also bump the cache-buster version
content = content.replace("?v=1786514456", "?v=1786514457")

with open("/var/www/verdiscan/wallet/index.html", "w") as f:
    f.write(content)

print("SRI hash updated in index.html")
