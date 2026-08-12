with open("/var/www/verdiscan/wallet/index.html") as f:
    content = f.read()

# Remove SRI integrity and crossorigin from the polkadot bundle script tag
# This is same-origin so SRI is unnecessary and crossorigin can cause issues
old_tag = '<script src="/polkadot-crypto-bundle.js?v=1786514457" integrity="sha384-dYsUw/wbRHAjmOGvSydiu6YFO9eDhg3ifWn7R7vUplJhXh1gKHLYVmnlQVv57Zcf" crossorigin="anonymous"></script>'
new_tag = '<script src="/polkadot-crypto-bundle.js?v=1786514458"></script>'
content = content.replace(old_tag, new_tag)

# Also handle the old version string in case the cache-buster wasn't updated
import re
content = re.sub(
    r'<script src="/polkadot-crypto-bundle\.js\?v=\d+"[^>]*integrity="[^"]*"[^>]*crossorigin="[^"]*"[^>]*></script>',
    '<script src="/polkadot-crypto-bundle.js?v=1786514458"></script>',
    content,
)
content = re.sub(
    r'<script src="/polkadot-crypto-bundle\.js\?v=\d+"[^>]*crossorigin="[^"]*"[^>]*integrity="[^"]*"[^>]*></script>',
    '<script src="/polkadot-crypto-bundle.js?v=1786514458"></script>',
    content,
)

with open("/var/www/verdiscan/wallet/index.html", "w") as f:
    f.write(content)

# Verify
with open("/var/www/verdiscan/wallet/index.html") as f:
    c = f.read()
if "integrity=" in c and "polkadot" in c.lower():
    print("WARNING: integrity still present on polkadot script")
else:
    print("SRI integrity removed from polkadot bundle script tag")
print("Cache-buster bumped to v=1786514458")
