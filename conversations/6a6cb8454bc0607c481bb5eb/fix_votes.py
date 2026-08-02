import re

with open("/opt/verdis/app/dist/web/wallet.html", "r") as f:
    content = f.read()

# Fix the broken votes line
content = content.replace(
    "v.votes.toLocaleString()\xc2\xb7 Blocks:",
    "v.votes.toLocaleString() + ' | Blocks: "
)
# Also try without the unicode middle dot
content = re.sub(
    r"v\.votes\.toLocaleString\(\)\s*\xb7\s*Blocks:",
    "v.votes.toLocaleString() + ' | Blocks: ",
    content
)
# Also try the literal bytes
content = content.replace(
    "v.votes.toLocaleString()\xc2\xb7 Blocks:",
    "v.votes.toLocaleString() + ' | Blocks: "
)

with open("/opt/verdis/app/dist/web/wallet.html", "w") as f:
    f.write(content)

# Verify
for line in content.split("\n"):
    if "v.votes" in line and "Blocks" in line:
        print("Fixed:", line.strip()[:150])
        break
