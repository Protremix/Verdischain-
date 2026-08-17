import os, re

for root, dirs, files in os.walk("lib/features"):
    for f in files:
        if not f.endswith(".dart"):
            continue
        path = os.path.join(root, f)
        with open(path, "r") as fh:
            content = fh.read()
        original = content
        content = re.sub(
            r'import [\'"](\.\./)+core/',
            'import "package:verdis_wallet/core/',
            content
        )
        content = re.sub(
            r'import [\'"](\.\./)+shared/',
            'import "package:verdis_wallet/shared/',
            content
        )
        content = re.sub(
            r'import [\'"](\.\./)+config/network_config\.dart[\'"]',
            'import "package:verdis_wallet/core/config/network_config.dart"',
            content
        )
        if content != original:
            with open(path, "w") as fh:
                fh.write(content)

for root, dirs, files in os.walk("lib/core"):
    for f in files:
        if not f.endswith(".dart"):
            continue
        path = os.path.join(root, f)
        with open(path, "r") as fh:
            content = fh.read()
        original = content
        content = re.sub(
            r'import [\'"](\.\./)+core/',
            'import "package:verdis_wallet/core/',
            content
        )
        if content != original:
            with open(path, "w") as fh:
                fh.write(content)

print("All imports converted to package imports!")
