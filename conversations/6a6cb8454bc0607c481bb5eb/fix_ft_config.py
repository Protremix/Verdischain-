import json

config_path = "/opt/flutter/packages/flutter_tools/.dart_tool/package_config.json"
with open(config_path) as f:
    config = json.load(f)

for pkg in config["packages"]:
    if pkg["name"] == "collection":
        old_uri = pkg["rootUri"]
        pkg["rootUri"] = "file:///root/.pub-cache/hosted/pub.dev/collection-1.19.0"
        print("Updated collection: " + old_uri + " -> " + pkg["rootUri"])

with open(config_path, "w") as f:
    json.dump(config, f, indent=2)

print("Done!")
