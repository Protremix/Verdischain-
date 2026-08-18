import 'package:verdis_wallet/core/router/route_names.dart';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';
import 'onboarding_providers.dart';
import 'package:verdis_wallet/core/config/remote_config.dart';

/// Page to enable or skip Biometric Authentication (Face ID / Fingerprint)
class BiometricSetupPage extends ConsumerStatefulWidget {
  const BiometricSetupPage({super.key});

  @override
  ConsumerState<BiometricSetupPage> createState() => _BiometricSetupPageState();
}

class _BiometricSetupPageState extends ConsumerState<BiometricSetupPage> {
  @override
  Widget build(BuildContext context) {
    final bioState = ref.watch(biometricSetupProvider);
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E0A),
      appBar: AppBar(
        title: const Text('Biometric Security'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            children: [
              const Spacer(),

              // Biometric Icon Container
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: const Color(0xFF00FF88).withOpacity(0.12),
                  border: Border.all(
                    color: const Color(0xFF00FF88).withOpacity(0.3),
                    width: 2,
                  ),
                ),
                child: const Icon(
                  Icons.fingerprint_rounded,
                  size: 64,
                  color: Color(0xFF00FF88),
                ),
              ),
              const SizedBox(height: 32),

              // Title & Description
              Text(
                'Enable Biometric Auth',
                textAlign: TextAlign.center,
                style: theme.textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFFE8F0E8),
                ),
              ),
              const SizedBox(height: 12),

              Text(
                'Use Face ID or Fingerprint for seamless, ultra-fast login and secure transaction authorization.',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: const Color(0xFF8B9D8B),
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 40),

              // Status Card with Toggle
              VerdisCard(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1A211A),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Icon(
                        bioState.isAvailable ? Icons.security : Icons.security_sharp,
                        color: const Color(0xFF00FF88),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            bioState.isAvailable
                                ? 'Biometrics Available'
                                : 'Hardware Not Supported',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Color(0xFFE8F0E8),
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            bioState.isAvailable
                                ? 'Touch ID / Face ID / Fingerprint'
                                : 'PIN code will be used for authentication',
                            style: const TextStyle(
                              fontSize: 12,
                              color: Color(0xFF8B9D8B),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Switch(
                      value: bioState.isEnabled,
                      onChanged: (bioState.isAvailable && ref.read(remoteConfigProvider).isFeatureEnabled('biometric_auth'))
                          ? (val) {
                              ref
                                  .read(biometricSetupProvider.notifier)
                                  .toggleBiometric(val);
                            }
                          : null,
                    ),
                  ],
                ),
              ),

              if (bioState.error != null) ...[
                const SizedBox(height: 12),
                Text(
                  bioState.error!,
                  style: const TextStyle(
                    color: Color(0xFFCF6679),
                    fontSize: 12,
                  ),
                ),
              ],

              const Spacer(),

              // Action Buttons
              VerdisButton(
                label: bioState.isEnabled ? 'Continue' : 'Enable & Continue',
                icon: Icons.arrow_forward,
                onPressed: () async {
                  if (!bioState.isEnabled && bioState.isAvailable) {
                    await ref
                        .read(biometricSetupProvider.notifier)
                        .toggleBiometric(true);
                  }
                  if (context.mounted) {
                    unawaited(context.push(RouteNames.pinSetup));
                  }
                },
              ),
              const SizedBox(height: 12),

              VerdisButton(
                label: 'Skip for Now',
                isOutlined: true,
                onPressed: () {
                  unawaited(context.push(RouteNames.pinSetup));
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
