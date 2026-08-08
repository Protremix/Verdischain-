#!/usr/bin/env python3
with open("/var/www/verdiscan/incentives/index.html") as f:
    html = f.read()

html = html.replace(
    '<div class="sub">28% of supply</div>',
    '<div class="sub">Testnet staking</div>'
)

with open("/var/www/verdiscan/incentives/index.html", "w") as f:
    f.write(html)

print("Incentives page fixed")
