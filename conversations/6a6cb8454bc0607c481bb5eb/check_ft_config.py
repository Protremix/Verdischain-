import json, os

config_path = "/opt/flutter/packages/flutter_tools/.dart_tool/package_config.json"
with open(config_path) as f:
    config = json.load(f)

missing = []
for pkg in config["packages"]:
    root = pkg["rootUri"].replace("file://", "")
    pubspec = os.path.join(root, "pubspec.yaml")
    if not os.path.exists(pubspec):
        missing.append(pkg["name"])

print("Total packages: " + str(len(config["packages"])))
print("Missing pubspec: " + str(len(missing)))
if missing:
    print("Missing:", missing[:10])
else:
    print("All packages valid!")
