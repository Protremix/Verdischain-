import 'package:verdis_wallet/core/router/route_names.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';
import 'package:verdis_wallet/shared/widgets/verdis_widgets.dart';

/// Onboarding Welcome Carousel page
class WelcomePage extends StatefulWidget {
  const WelcomePage({super.key});

  @override
  State<WelcomePage> createState() => _WelcomePageState();
}

class _WelcomePageState extends State<WelcomePage> {
  final PageController _pageController = PageController();

  final List<OnboardingSlide> _slides = const [
    OnboardingSlide(
      icon: Icons.eco_rounded,
      title: 'Welcome to Verdis',
      subtitle: 'The high-performance, carbon-negative blockchain built for a sustainable digital economy.',
      accentColor: Color(0xFF00FF88),
    ),
    OnboardingSlide(
      icon: Icons.energy_savings_leaf_rounded,
      title: 'Carbon-Negative Blockchain',
      subtitle: 'Powered by BABE/GRANDPA + DPoS proof-of-green consensus with sub-second finality and zero emissions.',
      accentColor: Color(0xFF00FF88),
    ),
    OnboardingSlide(
      icon: Icons.account_balance_wallet_rounded,
      title: 'Your Green Wallet',
      subtitle: 'Full self-custody control of VRDX tokens, native DEX liquidity, cross-chain bridge, and green staking.',
      accentColor: Color(0xFF00E676),
    ),
  ];

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E0A),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
          child: Column(
            children: [
              // Top Bar with Skip Button
              Align(
                alignment: Alignment.topRight,
                child: TextButton(
                  onPressed: () => context.push(RouteNames.createWallet),
                  child: Text(
                    'Skip',
                    style: TextStyle(
                      color: theme.colorScheme.onSurfaceVariant,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),

              // Carousel
              Expanded(
                child: PageView.builder(
                  controller: _pageController,
                  itemCount: _slides.length,
                  onPageChanged: (index) {
                    setState(() {
                    });
                  },
                  itemBuilder: (context, index) {
                    final slide = _slides[index];
                    return Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        // Icon Badge
                        Container(
                          width: 120,
                          height: 120,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: slide.accentColor.withOpacity(0.12),
                            border: Border.all(
                              color: slide.accentColor.withOpacity(0.3),
                              width: 2,
                            ),
                          ),
                          child: Icon(
                            slide.icon,
                            size: 60,
                            color: slide.accentColor,
                          ),
                        ),
                        const SizedBox(height: 40),

                        // Title
                        Text(
                          slide.title,
                          textAlign: TextAlign.center,
                          style: theme.textTheme.displaySmall?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: const Color(0xFFE8F0E8),
                          ),
                        ),
                        const SizedBox(height: 16),

                        // Subtitle
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          child: Text(
                            slide.subtitle,
                            textAlign: TextAlign.center,
                            style: theme.textTheme.bodyLarge?.copyWith(
                              color: const Color(0xFF8B9D8B),
                              height: 1.5,
                            ),
                          ),
                        ),
                      ],
                    );
                  },
                ),
              ),

              // Page Indicator
              SmoothPageIndicator(
                controller: _pageController,
                count: _slides.length,
                effect: const ExpandingDotsEffect(
                  activeDotColor: Color(0xFF00FF88),
                  dotColor: Color(0xFF2A332A),
                  dotHeight: 8,
                  dotWidth: 8,
                  expansionFactor: 3,
                  spacing: 6,
                ),
              ),
              const SizedBox(height: 40),

              // Action Buttons
              Column(
                children: [
                  VerdisButton(
                    label: 'Get Started (Create Wallet)',
                    icon: Icons.add_circle_outline_rounded,
                    onPressed: () {
                      context.push(RouteNames.createWallet);
                    },
                  ),
                  const SizedBox(height: 12),

                  VerdisButton(
                    label: 'Import Existing Wallet',
                    isOutlined: true,
                    icon: Icons.download_rounded,
                    onPressed: () {
                      context.push(RouteNames.importWallet);
                    },
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class OnboardingSlide {

  const OnboardingSlide({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.accentColor,
  });
  final IconData icon;
  final String title;
  final String subtitle;
  final Color accentColor;
}
