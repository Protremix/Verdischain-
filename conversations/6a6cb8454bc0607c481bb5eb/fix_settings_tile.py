#!/usr/bin/env python3
"""Fix the email backup ListTile in settings_screen.dart"""

filepath = "/opt/verdis-wallet/mobile/lib/screens/settings_screen.dart"

with open(filepath, "r") as f:
    content = f.read()

# The actual tile has a trailing icon
old_tile = """                    ListTile(
                      title: const Text('Export Private Key / Seed', style: TextStyle(color: Color(0xFFEF4444), fontSize: 13, fontWeight: FontWeight.w600)),
                      trailing: const Icon(Icons.key, color: Color(0xFFEF4444), size: 18),
                      onTap: _showExportWalletModal,
                    ),
                  ],
                ),"""

new_tile = """                    ListTile(
                      title: const Text('Export Private Key / Seed', style: TextStyle(color: Color(0xFFEF4444), fontSize: 13, fontWeight: FontWeight.w600)),
                      trailing: const Icon(Icons.key, color: Color(0xFFEF4444), size: 18),
                      onTap: _showExportWalletModal,
                    ),
                    const Divider(color: Color(0xFF2E2E34), height: 1),
                    ListTile(
                      title: const Text('Backup to Email', style: TextStyle(color: Color(0xFF16a34a), fontSize: 13, fontWeight: FontWeight.w600)),
                      subtitle: const Text('Encrypt & store wallet recovery on server', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 11)),
                      trailing: const Icon(Icons.email_outlined, color: Color(0xFF16a34a), size: 18),
                      onTap: _showEmailBackupModal,
                    ),
                  ],
                ),"""

if old_tile in content:
    content = content.replace(old_tile, new_tile, 1)
    with open(filepath, "w") as f:
        f.write(content)
    print("Fixed: Added Backup to Email ListTile")
else:
    print("ERROR: Still could not find the tile")
    # Try even more flexible search
    import re
    pattern = r"ListTile\(\s*\n\s*title: const Text\('Export Private Key.*?onTap: _showExportWalletModal,\s*\n\s*\),"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        replacement = match.group() + """
                    const Divider(color: Color(0xFF2E2E34), height: 1),
                    ListTile(
                      title: const Text('Backup to Email', style: TextStyle(color: Color(0xFF16a34a), fontSize: 13, fontWeight: FontWeight.w600)),
                      subtitle: const Text('Encrypt & store wallet recovery on server', style: TextStyle(color: Color(0xFF94a3b8), fontSize: 11)),
                      trailing: const Icon(Icons.email_outlined, color: Color(0xFF16a34a), size: 18),
                      onTap: _showEmailBackupModal,
                    ),"""
        content = content.replace(match.group(), replacement, 1)
        with open(filepath, "w") as f:
            f.write(content)
        print("Fixed via regex: Added Backup to Email ListTile")
    else:
        print("Could not find via regex either")
