#!/usr/bin/env python3
"""
Deploy TokensView, DexView, StakingView to the server and update home_page.dart
"""

import subprocess
import sys

WALLET = '/opt/verdis-wallet'

# Write the three view files
files = {
    'lib/features/home/presentation/tokens_view.dart': open('/tmp/tokens_view.dart').read(),
    'lib/features/home/presentation/dex_view.dart': open('/tmp/dex_view.dart').read(),
    'lib/features/home/presentation/staking_view.dart': open('/tmp/staking_view.dart').read(),
}

for path, content in files.items():
    full_path = f'{WALLET}/{path}'
    with open(full_path, 'w') as f:
        f.write(content)
    print(f"  Written: {path}")

# Update home_page.dart to use real views instead of placeholders
print("\nUpdating home_page.dart...")
with open(f'{WALLET}/lib/features/home/presentation/home_page.dart', 'r') as f:
    home_page = f.read()

# Add imports
home_page = home_page.replace(
    "import 'portfolio_view.dart';",
    "import 'portfolio_view.dart';\nimport 'tokens_view.dart';\nimport 'dex_view.dart';\nimport 'staking_view.dart';"
)

# Replace placeholder tabs with real views
old_tab1 = """          // Tab 1: Tokens View
          _buildPlaceholderTab(
            context,
            icon: Icons.toll,
            title: 'Token Assets',
            subtitle: 'View and manage all eco-tokens on the Verdis Network.',
          ),"""
new_tab1 = """          // Tab 1: Tokens View
          const TokensView(),"""

old_tab2 = """          // Tab 2: DEX View
          _buildPlaceholderTab(
            context,
            icon: Icons.swap_horizontal_circle,
            title: 'Verdis DEX',
            subtitle: 'Decentralized exchange with automated yield pools.',
          ),"""
new_tab2 = """          // Tab 2: DEX View
          const DexView(),"""

old_tab3 = """          // Tab 3: Staking View
          _buildPlaceholderTab(
            context,
            icon: Icons.energy_savings_leaf,
            title: 'Staking & Governance',
            subtitle: 'Stake VRDX with green validator nodes to earn rewards.',
          ),"""
new_tab3 = """          // Tab 3: Staking View
          const StakingView(),"""

home_page = home_page.replace(old_tab1, new_tab1)
home_page = home_page.replace(old_tab2, new_tab2)
home_page = home_page.replace(old_tab3, new_tab3)

# Remove the _buildPlaceholderTab method since it's no longer used
old_method = """  Widget _buildPlaceholderTab(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
  }) {
    return Center(
      child: EmptyState(
        icon: icon,
        title: title,
        subtitle: subtitle,
        actionLabel: 'Return to Home',
        onAction: () {},
      ),
    );
  }
"""
home_page = home_page.replace(old_method, "")

# Remove unused VerdisWidgets import if EmptyState is no longer used
# Check if EmptyState is still used
if 'EmptyState' not in home_page:
    # Keep the import since VerdisWidgets has other widgets used
    pass

with open(f'{WALLET}/lib/features/home/presentation/home_page.dart', 'w') as f:
    f.write(home_page)
print("  home_page.dart updated with real views")

# Bump version
print("\nBumping version...")
with open(f'{WALLET}/pubspec.yaml', 'r') as f:
    pubspec = f.read()
pubspec = pubspec.replace('version: 1.9.2+15', 'version: 2.0.0+16')
with open(f'{WALLET}/pubspec.yaml', 'w') as f:
    f.write(pubspec)

with open(f'{WALLET}/android/local.properties', 'r') as f:
    lp = f.read()
lp = lp.replace('flutter.versionName=1.9.2', 'flutter.versionName=2.0.0')
lp = lp.replace('flutter.versionCode=15', 'flutter.versionCode=16')
with open(f'{WALLET}/android/local.properties', 'w') as f:
    f.write(lp)
print("  Version bumped to 2.0.0+16")
print("\nAll views deployed.")
