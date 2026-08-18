/// Verdis blockchain network configuration
class NetworkConfig {
  NetworkConfig._();

  // RPC Endpoints
  static const String rpcUrl = 'https://verdischain.com/rpc';
  static const String wsUrl = 'wss://verdischain.com/rpc';
  static const String apiUrl = 'https://verdischain.com/api/v1';
  static const String explorerUrl = 'https://verdischain.com/explorer';
  static const String faucetUrl = 'https://verdischain.com/faucet';

  // Chain Info
  static const String chainName = 'Verdis';
  static const String chainType = 'Verdis Chain';
  static const int chainId = 909;
  static const String tokenSymbol = 'VRDX';
  static const String tokenName = 'Verdis';
  static const int decimals = 9; // Verdis uses 9 decimals
  static const String genesisHash = ''; // Set after chain spec freeze
  static const int specVersion = 11;
  static const String runtimeVersion = '3.1.0';

  // Consensus
  static const String consensus = 'BABE/GRANDPA + DPoS';
  static const int validatorCount = 21;
  static const int totalNodes = 21;

  // Tokenomics
  static const int totalSupply = 100000000000; // 100B VRDX
  static const int circulatingSupply = 15000000000; // 15B at TGE

  // Explorer
  static const String explorerBaseUrl = 'https://explorer.verdischain.com';

  // API Timeouts
  static const int connectTimeout = 15000;
  static const int receiveTimeout = 30000;
  static const int sendTimeout = 15000;
}

/// App-wide constants
class AppConstants {
  AppConstants._();

  // App Info
  static const String appName = 'Verdis Wallet';
  static const String appVersion = '2.1.7';
  static const String appBuild = '27';

  // Security
  static const int pinLength = 6;
  static const int sessionTimeoutMinutes = 2;
  static const int autoLockMinutes = 1;
  static const int clipboardClearSeconds = 30;

  // Storage Keys
  static const String walletKey = 'verdis_wallet';
  static const String privateKeyKey = 'verdis_private_key';
  static const String publicKeyKey = 'verdis_public_key';
  static const String pinHashKey = 'verdis_pin_hash';
  static const String biometricEnabledKey = 'verdis_biometric';
  static const String themeModeKey = 'verdis_theme_mode';
  static const String onboardingCompleteKey = 'verdis_onboarding';
  static const String cachedBalanceKey = 'verdis_cached_balance';
  static const String cachedTransactionsKey = 'verdis_cached_txs';

  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;

  // UI
  static const double cardRadius = 16.0;
  static const double buttonRadius = 12.0;
  static const double smallRadius = 8.0;
}
