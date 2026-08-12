#!/usr/bin/env python3
"""
Fix three issues in APK wallet (NO design changes):
1. Splash logo: use real Verdis logo image instead of animated V-hexagon
2. Demo wallet: fix selectedAddressProvider + update after import
3. Settings access: replace settings placeholder tab with actual SettingsPage
"""
import os
import subprocess

WALLET = '/opt/verdis-wallet'

# === FIX 1: Download real Verdis logo and use in splash ===
print("Fix 1: Splash logo...")
os.makedirs(f'{WALLET}/assets/images', exist_ok=True)
subprocess.run(['cp', '/var/www/verdiscan/assets/verdis-logo-white.png', f'{WALLET}/assets/images/verdis-logo-white.png'], check=True)
print("  Logo image copied to assets/images/")

# Update splash_page.dart to use Image.asset instead of VerdisLogo
with open(f'{WALLET}/lib/features/onboarding/presentation/splash_page.dart', 'r') as f:
    splash = f.read()

# Replace the VerdisLogo widget with Image.asset
old_logo = """            // Animated V Logo
            const VerdisLogo(
              size: 130,
              color: Color(0xFF00FF88),
            ),"""
new_logo = """            // Verdis Chain logo
            Image.asset(
              'assets/images/verdis-logo-white.png',
              width: 130,
              height: 130,
              fit: BoxFit.contain,
            ),"""

if old_logo in splash:
    splash = splash.replace(old_logo, new_logo)
    # Remove unused VerdisLogo import
    splash = splash.replace("import 'package:verdis_wallet/shared/widgets/verdis_logo.dart';\n", '')
    with open(f'{WALLET}/lib/features/onboarding/presentation/splash_page.dart', 'w') as f:
        f.write(splash)
    print("  splash_page.dart patched: VerdisLogo -> Image.asset")
else:
    print("  SKIP: splash logo pattern not found")

# Make sure pubspec.yaml has the assets path
with open(f'{WALLET}/pubspec.yaml', 'r') as f:
    pubspec = f.read()
if 'assets/images/verdis-logo-white.png' not in pubspec:
    pubspec = pubspec.replace(
        '    - assets/images/',
        '    - assets/images/\n    - assets/images/verdis-logo-white.png'
    )
    with open(f'{WALLET}/pubspec.yaml', 'w') as f:
        f.write(pubspec)
    print("  pubspec.yaml updated with logo asset")
else:
    print("  pubspec.yaml already has logo asset")

# === FIX 2: Fix demo wallet — selectedAddressProvider ===
print("\nFix 2: Demo wallet address...")
with open(f'{WALLET}/lib/features/home/presentation/home_providers.dart', 'r') as f:
    providers = f.read()

# Change the default address from hardcoded Ethereum address to empty string
old_default = """final selectedAddressProvider = StateProvider<String>((ref) {
  return '0x71C7656EC7ab88b098defB751B7401B5f6d8976F';
});"""
new_default = """final selectedAddressProvider = StateProvider<String>((ref) {
  return '';
});"""

if old_default in providers:
    providers = providers.replace(old_default, new_default)
    with open(f'{WALLET}/lib/features/home/presentation/home_providers.dart', 'w') as f:
        f.write(providers)
    print("  home_providers.dart: default address -> empty string")
else:
    print("  SKIP: default address pattern not found")

# Fix pin_setup_page.dart to update selectedAddressProvider after import
with open(f'{WALLET}/lib/features/onboarding/presentation/pin_setup_page.dart', 'r') as f:
    pin_page = f.read()

old_finalize_end = """    if (success && mounted) {
      // Clear navigation history and go to Home
      context.go(RouteNames.home);
    }"""
new_finalize_end = """    if (success && mounted) {
      // Update the selectedAddressProvider with the real wallet address
      ref.read(selectedAddressProvider.notifier).state = address;
      // Clear navigation history and go to Home
      context.go(RouteNames.home);
    }"""

if old_finalize_end in pin_page:
    pin_page = pin_page.replace(old_finalize_end, new_finalize_end)
    # Add import for selectedAddressProvider
    if 'import' not in pin_page or 'home_providers' not in pin_page:
        pin_page = pin_page.replace(
            "import 'onboarding_providers.dart';",
            "import 'onboarding_providers.dart';\nimport 'package:verdis_wallet/features/home/presentation/home_providers.dart';"
        )
    with open(f'{WALLET}/lib/features/onboarding/presentation/pin_setup_page.dart', 'w') as f:
        f.write(pin_page)
    print("  pin_setup_page.dart: added selectedAddressProvider update after import")
else:
    print("  SKIP: pin finalize pattern not found")

# === FIX 3: Settings tab — replace placeholder with actual SettingsPage ===
print("\nFix 3: Settings tab access...")
with open(f'{WALLET}/lib/features/home/presentation/home_page.dart', 'r') as f:
    home_page = f.read()

old_settings_tab = """          // Tab 4: Settings View
          _buildPlaceholderTab(
            context,
            icon: Icons.settings,
            title: 'Wallet Settings',
            subtitle: 'Manage security, seed phrase backup, and RPC nodes.',
          ),"""
new_settings_tab = """          // Tab 4: Settings
          const SettingsPage(),"""

if old_settings_tab in home_page:
    home_page = home_page.replace(old_settings_tab, new_settings_tab)
    # Add import for SettingsPage
    home_page = home_page.replace(
        "import 'home_providers.dart';",
        "import 'home_providers.dart';\nimport 'package:verdis_wallet/features/settings/presentation/settings_page.dart';"
    )
    with open(f'{WALLET}/lib/features/home/presentation/home_page.dart', 'w') as f:
        f.write(home_page)
    print("  home_page.dart: settings placeholder -> SettingsPage widget")
else:
    print("  SKIP: settings tab pattern not found")

# === Bump version ===
print("\nBumping version...")
with open(f'{WALLET}/pubspec.yaml', 'r') as f:
    pubspec = f.read()
pubspec = pubspec.replace('version: 1.8.0+12', 'version: 1.9.0+13')
with open(f'{WALLET}/pubspec.yaml', 'w') as f:
    f.write(pubspec)

# Also update local.properties
with open(f'{WALLET}/android/local.properties', 'r') as f:
    lp = f.read()
lp = lp.replace('flutter.versionName=1.8.0', 'flutter.versionName=1.9.0')
lp = lp.replace('flutter.versionCode=12', 'flutter.versionCode=13')
with open(f'{WALLET}/android/local.properties', 'w') as f:
    f.write(lp)

print("Version bumped to 1.9.0+13")
print("\nAll fixes applied.")
