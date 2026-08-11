#!/usr/bin/env python3
"""Generate a MINIMAL .dart_tool/package_config.json with only needed packages."""
import json
import os
import re

CACHE_DIR = "/root/.pub-cache/hosted/pub.dev"
PROJECT_DIR = "/opt/verdis-wallet/mobile"
DART_TOOL = os.path.join(PROJECT_DIR, ".dart_tool")
os.makedirs(DART_TOOL, exist_ok=True)

# Minimal set of packages needed (direct + transitive)
# Determined from pubspec.yaml and dependency tracing
NEEDED_PACKAGES = {
    # Direct deps
    "provider", "http", "crypto", "path", "intl", "path_provider",
    "flutter_lints",
    # Transitive deps
    "collection", "meta", "typed_data", "async", "clock", "web",
    "http_parser", "source_span", "string_scanner", "term_glyph",
    "path_provider_android", "path_provider_foundation", "path_provider_linux",
    "path_provider_windows", "path_provider_platform_interface",
    "plugin_platform_interface", "nested", "lints", "characters",
    "material_color_utilities", "vector_math",
    # Test deps (needed by flutter_test)
    "test_api", "boolean_selector", "matcher", "stack_trace",
    "stream_channel", "fake_async", "test", "leak_tracker",
    "leak_tracker_testing", "leak_tracker_flutter_testing",
    # Other commonly needed
    "js", "ffi",
}

# Find the best version for each needed package
packages = {}
for entry in os.listdir(CACHE_DIR):
    full_path = os.path.join(CACHE_DIR, entry)
    if not os.path.isdir(full_path):
        continue
    m = re.match(r'^(.+)-(\d+\.\d+\.\d+(?:[-+.\w]+)?)$', entry)
    if not m:
        continue
    name = m.group(1)
    version = m.group(2)
    if name in NEEDED_PACKAGES:
        if name not in packages or version > packages[name]["version"]:
            packages[name] = {"version": version, "path": full_path}

# Flutter SDK packages
flutter_sdk_packages = {
    "flutter": "/opt/flutter/packages/flutter",
    "flutter_test": "/opt/flutter/packages/flutter_test",
    "flutter_driver": "/opt/flutter/packages/flutter_driver",
    "flutter_localizations": "/opt/flutter/packages/flutter_localizations",
    "integration_test": "/opt/flutter/packages/integration_test",
    "sky_engine": "/opt/flutter/bin/cache/pkg/sky_engine",
    "flutter_web_plugins": "/opt/flutter/bin/cache/pkg/flutter_web_plugins",
    "fuchsia_remote_debug_protocol": "/opt/flutter/packages/fuchsia_remote_debug_protocol",
}

config = {
    "configVersion": 2,
    "packages": [],
    "generated": "2026-08-11T17:00:00.000Z",
    "generator": "manual-minimal",
    "generatorVersion": "1.0.0",
    "flutterRoot": "/opt/flutter",
    "flutterVersion": "3.24.5",
    "pubCache": "/root/.pub-cache"
}

# Add cached packages
for name in sorted(packages.keys()):
    pkg = packages[name]
    lib_path = os.path.join(pkg["path"], "lib")
    if not os.path.isdir(lib_path):
        print(f"WARNING: {name} has no lib/ directory, skipping")
        continue
    config["packages"].append({
        "name": name,
        "rootUri": f"file://{pkg['path']}",
        "packageUri": "lib/",
        "languageVersion": "3.5"
    })

# Add Flutter SDK packages
for name, sdk_path in sorted(flutter_sdk_packages.items()):
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
missing = NEEDED_PACKAGES - set(packages.keys())
if missing:
    print(f"WARNING: Missing packages not found in cache: {missing}")
else:
    print("All needed packages found in cache!")
