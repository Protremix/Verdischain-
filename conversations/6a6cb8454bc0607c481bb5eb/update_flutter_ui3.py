#!/usr/bin/env python3
"""Update remaining Flutter screens with Verdis Chain design."""

BASE = '/opt/verdis-wallet/mobile'

# 7. Update dashboard_screen.dart - replace old colors with new ones
with open(f'{BASE}/lib/screens/dashboard_screen.dart', 'r') as f:
    content = f.read()

# Replace old colors
replacements = [
    ('Color(0xFF18181A)', 'Color(0xFF040806)'),
    ('Color(0xFF1E1E22)', 'Color(0xFF0D1410)'),
    ('Color(0xFF00D97E)', 'Color(0xFF16a34a)'),
    ('Color(0xFFE4E4E7)', 'Color(0xFFFFFFFF)'),
    ('Color(0xFF8B8B8F)', 'Color(0xFF94a3b8)'),
    ('Color(0xFF2A2A2E)', 'Color(0xFF152017)'),
    ('Color(0xFF3A3A3E)', 'Color(0xFF1a2520)'),
    ('withOpacity(0.25)', 'withOpacity(0.15)'),
    ('withOpacity(0.1)', 'withOpacity(0.08)'),
]
for old, new in replacements:
    content = content.replace(old, new)

# Add gradient to home tab header
old_home = '''  Widget _buildHomeTab() {'''
new_home = '''  Widget _buildHomeTab() {'''
# This is complex, just do color replacements for now

with open(f'{BASE}/lib/screens/dashboard_screen.dart', 'w') as f:
    f.write(content)
print("Updated dashboard_screen.dart colors")

# 8. Update all other screens with color replacements
screens = [
    'send_screen.dart',
    'receive_screen.dart',
    'staking_screen.dart',
    'dex_screen.dart',
    'eco_screen.dart',
    'settings_screen.dart',
]

for screen in screens:
    path = f'{BASE}/lib/screens/{screen}'
    try:
        with open(path, 'r') as f:
            content = f.read()
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        with open(path, 'w') as f:
            f.write(content)
        print(f"Updated {screen}")
    except FileNotFoundError:
        print(f"Skipped {screen} (not found)")

# 9. Add lastGeneratedMnemonic to wallet_service.dart
with open(f'{BASE}/lib/services/wallet_service.dart', 'r') as f:
    ws_content = f.read()

if 'lastGeneratedMnemonic' not in ws_content:
    # Add the field after _recentTransactions
    old_field = '  List<TransactionRecord> _recentTransactions = [];'
    new_field = '  List<TransactionRecord> _recentTransactions = [];\n  String lastGeneratedMnemonic = "";'
    ws_content = ws_content.replace(old_field, new_field)
    
    # Store the mnemonic when creating a wallet
    old_create = 'final seed = seedPhrase ?? generateSeedPhrase();'
    new_create = 'final seed = seedPhrase ?? generateSeedPhrase();\n      lastGeneratedMnemonic = seed;'
    ws_content = ws_content.replace(old_create, new_create)
    
    with open(f'{BASE}/lib/services/wallet_service.dart', 'w') as f:
        f.write(ws_content)
    print("Added lastGeneratedMnemonic to wallet_service.dart")
else:
    print("lastGeneratedMnemonic already exists")

print("All screen updates done")
