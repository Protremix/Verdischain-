#!/usr/bin/env python3
"""Generate .dart_tool/package_config.json from the pub cache."""
import json
import os
import re

CACHE_DIR = "/root/.pub-cache/hosted/pub.dev"
PROJECT_DIR = "/opt/verdis-wallet/mobile"
DART_TOOL = os.path.join(PROJECT_DIR, ".dart_tool")

os.makedirs(DART_TOOL, exist_ok=True)

# Parse all package directories in the cache
packages = {}
for entry in os.listdir(CACHE_DIR):
    full_path = os.path.join(CACHE_DIR, entry)
    if not os.path.isdir(full_path):
        continue
    # Match package_name-version pattern
    # Package names can contain underscores, dots, hyphens
    m = re.match(r'^(.+)-(\d+\.\d+\.\d+(?:-\w+\.\d+)?)$', entry)
    if not m:
        # Try simpler version pattern
        m = re.match(r'^(.+)-(\d+\.\d+\.\d+)$', entry)
    if not m:
        continue
    name = m.group(1)
    version = m.group(2)
    # If we already have this package, keep the higher version
    if name in packages:
        existing_ver = packages[name]["version"]
        if version > existing_ver:
            packages[name] = {"version": version, "path": full_path}
    else:
        packages[name] = {"version": version, "path": full_path}

# Read pubspec.yaml to find direct dependencies
pubspec_path = os.path.join(PROJECT_DIR, "pubspec.yaml")
with open(pubspec_path, "r") as f:
    pubspec_content = f.read()

# Build package_config.json
config = {
    "configVersion": 2,
    "packages": [],
    "generated": "2026-08-11T14:00:00.000Z",
    "generator": "manual",
    "generatorVersion": "1.0.0",
    "flutterRoot": "/opt/flutter",
    "flutterVersion": "3.24.5",
    "pubCache": "/root/.pub-cache"
}

# Add Flutter SDK packages (these are in the Flutter SDK, not pub cache)
flutter_sdk_packages = [
    "flutter", "flutter_test", "flutter_driver", "flutter_localizations",
    "integration_test", "fuchsia_remote_debug_protocol",
    "sky_engine", "flutter_web_plugins"
]

# Add all cached packages
for name in sorted(packages.keys()):
    pkg = packages[name]
    lib_path = os.path.join(pkg["path"], "lib")
    if not os.path.isdir(lib_path):
        continue
    config["packages"].append({
        "name": name,
        "rootUri": f"file://{pkg['path']}",
        "packageUri": "lib/",
        "languageVersion": "3.5"
    })

# Add Flutter SDK packages
for name in flutter_sdk_packages:
    if name == "sky_engine":
        sdk_path = "/opt/flutter/bin/cache/pkg/sky_engine"
    elif name == "flutter_web_plugins":
        sdk_path = "/opt/flutter/bin/cache/pkg/flutter_web_plugins"
    else:
        sdk_path = f"/opt/flutter/packages/{name}"
    if os.path.isdir(os.path.join(sdk_path, "lib")):
        config["packages"].append({
            "name": name,
            "rootUri": f"file://{sdk_path}",
            "packageUri": "lib/",
            "languageVersion": "3.5"
        })

# Write package_config.json
config_path = os.path.join(DART_TOOL, "package_config.json")
with open(config_path, "w") as f:
    json.dump(config, f, indent=2)

print(f"Generated {config_path} with {len(config['packages'])} packages")
print(f"Packages: {', '.join(sorted(packages.keys()))}")
