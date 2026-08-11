#!/usr/bin/env python3
"""Fix namespace in old Flutter plugin build.gradle files."""
import os
import re
import glob

CACHE_DIR = "/root/.pub-cache/hosted/pub.dev"

fixed = []
skipped = []

for pkg_dir in os.listdir(CACHE_DIR):
    full_path = os.path.join(CACHE_DIR, pkg_dir)
    if not os.path.isdir(full_path):
        continue
    
    build_gradle = os.path.join(full_path, "android", "build.gradle")
    if not os.path.exists(build_gradle):
        continue
    
    with open(build_gradle, "r") as f:
        content = f.read()
    
    # Check if namespace is already declared
    if "namespace" in content:
        skipped.append(pkg_dir)
        continue
    
    # Try to find package name from AndroidManifest.xml
    manifest = os.path.join(full_path, "android", "src", "main", "AndroidManifest.xml")
    package_name = None
    if os.path.exists(manifest):
        with open(manifest, "r") as f:
            manifest_content = f.read()
        m = re.search(r'package\s*=\s*"([^"]+)"', manifest_content)
        if m:
            package_name = m.group(1)
    
    if not package_name:
        # Try to guess from group declaration
        m = re.search(r"group\s+['\"]([^'\"]+)['\"]", content)
        if m:
            package_name = m.group(1)
        else:
            # Skip if we can't determine the package name
            skipped.append(f"{pkg_dir} (no package name)")
            continue
    
    # Add namespace after the 'group' line or at the beginning of android block
    if "android {" in content:
        content = content.replace(
            "android {",
            f"android {{\n    namespace '{package_name}'",
            1
        )
    elif "android{" in content:
        content = content.replace(
            "android{",
            f"android {{\n    namespace '{package_name}'",
            1
        )
    else:
        # Add at the top after the group/version lines
        content = f"\nandroid {{\n    namespace '{package_name}'\n}}\n" + content
    
    with open(build_gradle, "w") as f:
        f.write(content)
    
    fixed.append(f"{pkg_dir} -> {package_name}")

print(f"Fixed {len(fixed)} plugins:")
for f in fixed:
    print(f"  {f}")
print(f"\nSkipped {len(skipped)} plugins (already have namespace or no package)")
for s in skipped[:10]:
    print(f"  {s}")
