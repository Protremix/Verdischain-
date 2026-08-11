import os, re

for root, dirs, files in os.walk("lib"):
    for f in files:
        if not f.endswith(".dart"):
            continue
        path = os.path.join(root, f)
        with open(path, "r") as fh:
            lines = fh.readlines()
        changed = False
        for i, line in enumerate(lines):
            if 'import "package:verdis_wallet/' in line and line.rstrip().endswith("';"):
                lines[i] = line.replace('import "package:verdis_wallet/', "import 'package:verdis_wallet/")
                changed = True
        if changed:
            with open(path, "w") as fh:
                fh.writelines(lines)

print("Quote mismatch fixed!")
