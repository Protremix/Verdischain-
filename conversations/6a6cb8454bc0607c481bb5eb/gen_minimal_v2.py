#!/usr/bin/env python3
"""Generate minimal package_config.json v2."""
import json, os, re

CACHE_DIR = "/root/.pub-cache/hosted/pub.dev"
PROJECT_DIR = "/opt/verdis-wallet/mobile"
DART_TOOL = os.path.join(PROJECT_DIR, ".dart_tool")
os.makedirs(DART_TOOL, exist_ok=True)

NEEDED = {
    "provider", "http", "crypto", "path", "intl", "path_provider", "flutter_lints",
    "collection", "meta", "typed_data", "async", "clock", "web",
    "http_parser", "source_span", "string_scanner", "term_glyph",
    "path_provider_android", "path_provider_foundation", "path_provider_linux",
    "path_provider_windows", "path_provider_platform_interface",
    "plugin_platform_interface", "nested", "lints", "characters",
    "material_color_utilities", "vector_math",
    "test_api", "boolean_selector", "matcher", "stack_trace",
    "stream_channel", "fake_async", "test", "leak_tracker",
    "leak_tracker_testing", "leak_tracker_flutter_testing",
    "js", "ffi", "xdg_directories", "win32", "platform",
}

packages = {}
for entry in os.listdir(CACHE_DIR):
    full = os.path.join(CACHE_DIR, entry)
    if not os.path.isdir(full):
        continue
    m = re.match(r'^(.+)-(\d+\.\d+\.\d+(?:[-+.\w]+)?)$', entry)
    if not m:
        continue
    name = m.group(1)
    ver = m.group(2)
    if name in NEEDED:
        if name not in packages or ver > packages[name]["version"]:
            packages[name] = {"version": ver, "path": full}

flutter_pkgs = {
    "flutter": "/opt/flutter/packages/flutter",
    "flutter_test": "/opt/flutter/packages/flutter_test",
    "flutter_localizations": "/opt/flutter/packages/flutter_localizations",
    "sky_engine": "/opt/flutter/bin/cache/pkg/sky_engine",
    "flutter_web_plugins": "/opt/flutter/bin/cache/pkg/flutter_web_plugins",
    "integration_test": "/opt/flutter/packages/integration_test",
}

config = {
    "configVersion": 2,
    "packages": [],
    "generated": "2026-08-11T17:10:00Z",
    "generator": "manual",
    "flutterRoot": "/opt/flutter",
    "flutterVersion": "3.24.5"
}

for name in sorted(packages.keys()):
    pkg_path = packages[name]["path"]
    lib = os.path.join(pkg_path, "lib")
    if not os.path.isdir(lib):
        continue
    config["packages"].append({
        "name": name,
        "rootUri": "file://" + pkg_path,
        "packageUri": "lib/",
        "languageVersion": "3.5"
    })

for name, sdk_path in sorted(flutter_pkgs.items()):
    if os.path.isdir(os.path.join(sdk_path, "lib")):
        config["packages"].append({
            "name": name,
            "rootUri": "file://" + sdk_path,
            "packageUri": "lib/",
            "languageVersion": "3.5"
        })

with open(os.path.join(DART_TOOL, "package_config.json"), "w") as f:
    json.dump(config, f, indent=2)

total = len(config["packages"])
print("Generated with {} packages".format(total))
missing = NEEDED - set(packages.keys())
if missing:
    print("Missing: {}".format(missing))
else:
    print("All packages found!")
