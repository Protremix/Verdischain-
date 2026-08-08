import re

content = open("/var/www/verdiscan/explorer/index.html").read()

# Find all footer-related CSS
print("=== EXPLORER FOOTER CSS ===")
footer_css = re.findall(r"\.footer[^{]*\{[^}]+\}", content)
for css in footer_css:
    print("  " + css[:200])

print("\n=== EXPLORER :root VARS ===")
root_match = re.search(r":root\s*\{([^}]+)\}", content)
if root_match:
    print(root_match.group(0)[:1000])
else:
    print("  NO :root found")

print("\n=== EXPLORER --hero-bg ===")
hero_bg = re.findall(r"--hero-bg[^;]*", content)
for h in hero_bg:
    print("  " + h)

# Check what the footer tag looks like
print("\n=== EXPLORER FOOTER TAG ===")
footer_match = re.search(r"<footer[^>]*>", content)
if footer_match:
    print("  " + footer_match.group(0))
else:
    print("  NO <footer> tag found")

# Check what variables the footer CSS uses
print("\n=== EXPLORER CSS VARS USED IN FOOTER ===")
for css in footer_css:
    vars_used = re.findall(r"var\(([^)]+)\)", css)
    for v in vars_used:
        print("  var(" + v + ")")
