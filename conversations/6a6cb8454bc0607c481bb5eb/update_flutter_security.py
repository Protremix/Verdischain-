#!/usr/bin/env python3
"""
Update Flutter wallet onboarding providers to:
1. Register PIN on server after local PIN setup
2. Verify PIN on server during import (if already registered)
3. Add security notice page to router
"""

import re

# 1. Update onboarding_providers.dart — modify submitAndFinalizePin to register on server
ONBOARDING_PATH = '/opt/verdis-wallet/lib/features/onboarding/presentation/onboarding_providers.dart'

with open(ONBOARDING_PATH, 'r') as f:
    content = f.read()

# Add import for PinSecurityService at the top
if 'pin_security_service' not in content:
    content = content.replace(
        "import '../data/wallet_repository_impl.dart';",
        "import '../data/wallet_repository_impl.dart';\nimport 'package:verdis_wallet/core/security/pin_security_service.dart';"
    )
    print("[OK] Added PinSecurityService import")

# Modify submitAndFinalizePin to also register on server
old_finalize = """  Future<bool> submitAndFinalizePin({
    required String mnemonic,
    required String privateKey,
    required String publicKey,
    required String address,
  }) async {
    if (state.pin.length != 6 || state.confirmPin.length != 6) {
      state = state.copyWith(error: 'PIN must be 6 digits');
      return false;
    }

    if (state.pin != state.confirmPin) {
      state = state.copyWith(
        confirmPin: '',
        error: 'PINs do not match. Please try again.',
      );
      return false;
    }

    state = state.copyWith(isLoading: true, error: null);

    try {
      final pinHash = await _repository.hashPin(state.pin);
      await _repository.savePinHash(pinHash);
      await _repository.storeWallet(
        mnemonic: mnemonic,
        privateKey: privateKey,
        publicKey: publicKey,
        address: address,
      );

      state = state.copyWith(isLoading: false, isSuccess: true);
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: 'Failed to save security PIN: $e');
      return false;
    }
  }"""

new_finalize = """  Future<bool> submitAndFinalizePin({
    required String mnemonic,
    required String privateKey,
    required String publicKey,
    required String address,
  }) async {
    if (state.pin.length != 6 || state.confirmPin.length != 6) {
      state = state.copyWith(error: 'PIN must be 6 digits');
      return false;
    }

    if (state.pin != state.confirmPin) {
      state = state.copyWith(
        confirmPin: '',
        error: 'PINs do not match. Please try again.',
      );
      return false;
    }

    state = state.copyWith(isLoading: true, error: null);

    try {
      // 1. Check if this address already has a PIN on the server
      final pinStatus = await PinSecurityService.getPinStatus(address);

      if (pinStatus['has_pin'] == true) {
        // Wallet already has a PIN — verify the entered PIN matches
        if (pinStatus['locked'] == true) {
          final remaining = pinStatus['locked_remaining'] ?? 0;
          final mins = (remaining as int) ~/ 60;
          state = state.copyWith(
            isLoading: false,
            error: 'Wallet is locked. Try again in ${mins} minute(s).',
          );
          return false;
        }

        final (success, message, remaining) = await PinSecurityService.verifyPin(
          address: address,
          pin: state.pin,
        );

        if (!success) {
          if (message == 'locked') {
            state = state.copyWith(
              isLoading: false,
              error: 'Too many failed attempts. Wallet locked for 15 minutes.',
            );
          } else {
            state = state.copyWith(
              isLoading: false,
              error: 'Wrong PIN. $remaining attempts remaining.',
            );
          }
          return false;
        }
        // PIN verified — proceed
      } else {
        // New wallet — register PIN on server
        final (regSuccess, regMessage) = await PinSecurityService.registerPin(
          address: address,
          pin: state.pin,
        );
        if (!regSuccess) {
          state = state.copyWith(
            isLoading: false,
            error: 'PIN registration failed: $regMessage',
          );
          return false;
        }
      }

      // 2. Save PIN hash locally
      final pinHash = await _repository.hashPin(state.pin);
      await _repository.savePinHash(pinHash);

      // 3. Store wallet in secure storage
      await _repository.storeWallet(
        mnemonic: mnemonic,
        privateKey: privateKey,
        publicKey: publicKey,
        address: address,
      );

      state = state.copyWith(isLoading: false, isSuccess: true);
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: 'Failed to save security PIN: $e');
      return false;
    }
  }"""

if old_finalize in content:
    content = content.replace(old_finalize, new_finalize)
    print("[OK] submitAndFinalizePin updated with server-side PIN verification")
else:
    print("[WARN] Exact finalize match not found, trying regex")
    pattern = r'Future<bool> submitAndFinalizePin\(\{.*?\n  \}'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + new_finalize + content[match.end():]
        print("[OK] submitAndFinalizePin updated via regex")
    else:
        print("[ERROR] Could not find submitAndFinalizePin")
        exit(1)

with open(ONBOARDING_PATH, 'w') as f:
    f.write(content)
print("[DONE] onboarding_providers.dart updated")

# 2. Update app_router.dart to add security notice route
ROUTER_PATH = '/opt/verdis-wallet/lib/core/router/app_router.dart'

with open(ROUTER_PATH, 'r') as f:
    router_content = f.read()

# Add import for security notice page
if 'security_notice_page' not in router_content:
    # Find the last import line and add after it
    import_marker = "import 'package:verdis_wallet/features/onboarding/presentation/"
    if import_marker in router_content:
        # Find the last onboarding import
        imports = [line for line in router_content.split('\n') if import_marker in line]
        if imports:
            last_import = imports[-1]
            router_content = router_content.replace(
                last_import,
                last_import + "\nimport 'package:verdis_wallet/features/onboarding/presentation/security_notice_page.dart';"
            )
            print("[OK] Added security_notice_page import to router")

# Add security notice route
if '/security-notice' not in router_content:
    # Find the welcome route and add before it
    welcome_route = "GoRoute(path: '/welcome'"
    if welcome_route in router_content:
        security_route = """GoRoute(
        path: '/security-notice',
        name: 'SecurityNotice',
        builder: (context, state) => const SecurityNoticePage(),
      ),
      """
        router_content = router_content.replace(welcome_route, security_route + welcome_route)
        print("[OK] Added /security-notice route")
    else:
        print("[WARN] Could not find welcome route, trying alternate approach")

with open(ROUTER_PATH, 'w') as f:
    f.write(router_content)
print("[DONE] app_router.dart updated")

# 3. Update import_wallet_page.dart to navigate to security notice before PIN setup
IMPORT_PAGE_PATH = '/opt/verdis-wallet/lib/features/onboarding/presentation/import_wallet_page.dart'

with open(IMPORT_PAGE_PATH, 'r') as f:
    import_content = f.read()

# Change navigation from pinSetup to security-notice
old_nav = "unawaited(context.push(RouteNames.pinSetup));"
new_nav = "unawaited(context.push('/security-notice'));"
if old_nav in import_content:
    import_content = import_content.replace(old_nav, new_nav)
    print("[OK] Import page navigation updated to security-notice")
elif "context.push(RouteNames.pinSetup)" in import_content:
    import_content = import_content.replace("context.push(RouteNames.pinSetup)", "context.push('/security-notice')")
    print("[OK] Import page navigation updated (alt)")
else:
    print("[WARN] Could not find import navigation code")

with open(IMPORT_PAGE_PATH, 'w') as f:
    f.write(import_content)
print("[DONE] import_wallet_page.dart updated")

# 4. Update security_notice_page.dart to navigate to pinSetup after agreement
SECURITY_PAGE_PATH = '/opt/verdis-wallet/lib/features/onboarding/presentation/security_notice_page.dart'

with open(SECURITY_PAGE_PATH, 'r') as f:
    security_content = f.read()

# Update _handleContinue to go to pinSetup
old_continue = """    final nextRoute = ModalRoute.of(context)?.settings.arguments as String?;
    if (nextRoute != null) {
      context.go(nextRoute);
    } else {
      context.go('/welcome');
    }"""

new_continue = """    // Navigate to PIN setup page
    context.go('/pin-setup');"""

if old_continue in security_content:
    security_content = security_content.replace(old_continue, new_continue)
    print("[OK] Security notice page navigation updated to pin-setup")
else:
    print("[WARN] Could not find continue handler in security page")

with open(SECURITY_PAGE_PATH, 'w') as f:
    f.write(security_content)
print("[DONE] security_notice_page.dart updated")

# 5. Check if http package is in pubspec.yaml
PUBSPEC_PATH = '/opt/verdis-wallet/pubspec.yaml'
with open(PUBSPEC_PATH, 'r') as f:
    pubspec = f.read()

if 'http:' not in pubspec:
    # Add http dependency
    if 'dependencies:' in pubspec:
        pubspec = pubspec.replace(
            'dependencies:',
            'dependencies:\n  http: ^1.2.0'
        )
        print("[OK] Added http dependency to pubspec.yaml")
    else:
        print("[ERROR] Could not find dependencies in pubspec.yaml")
else:
    print("[OK] http dependency already in pubspec.yaml")

with open(PUBSPEC_PATH, 'w') as f:
    f.write(pubspec)

print("\n=== ALL FILES UPDATED ===")
