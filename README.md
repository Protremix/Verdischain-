# Verdis Wallet — Official Cross-Platform Wallet

Production-grade cross-platform wallet for the Verdis blockchain ecosystem.

## Supported Platforms
- Android (min SDK 21)
- iOS (min 13.0)
- Windows
- macOS
- Linux
- Web (future)

## Technology Stack
- **Flutter** (latest stable)
- **Dart**
- **Material 3**
- **Riverpod** — State management
- **GoRouter** — Navigation
- **Hive / Isar** — Local storage
- **Freezed** — Immutable models
- **Dio** — HTTP networking
- **Flutter Secure Storage** — Encrypted key storage
- **Local Authentication** — Biometric/PIN
- **Mobile Scanner** — QR code scanning
- **fl_chart** — Charts and graphs

## Architecture
- Clean Architecture
- Repository Pattern
- Feature Modules
- Dependency Injection
- Offline-first
- Scalable & Maintainable

## Security
- Never stores private keys remotely
- Android Keystore
- Apple Keychain
- Windows Credential Manager
- Encrypted local storage
- Biometric authentication
- PIN protection
- Auto Lock
- Session Timeout
- Secure Clipboard
- Device Integrity checks

## Features
- Onboarding (Splash, Welcome, Create/Import Wallet, Backup, Biometric, PIN)
- Home (Portfolio, Balance, Tokens, NFT, Staking, Rewards, Transactions, Network)
- Tokens (VRDX, Custom, Import, Metadata, History, Transfers)
- NFT (Collections, Assets, Gallery, Metadata, Transfer)
- Transactions (Send, Receive, QR Scanner, Fee Estimation, History, Explorer Link)
- Staking (Validators, Stake/Unstake, Rewards, History, Performance)
- DEX (Swap, Liquidity, Pools, Price Impact, Slippage, Preview)
- Explorer (Mini Explorer, Blocks, Transactions, Validators, Search, Network)

## Network
- RPC: https://rpc.verdischain.com
- WebSocket: wss://rpc.verdischain.com
- API: https://api.verdischain.com
- Explorer: https://explorer.verdischain.com
- Faucet: https://faucet.verdischain.com
- Chain: Verdis (VRDX)
- Consensus: BABE/GRANDPA + DPoS
- Total Supply: 100,000,000,000 VRDX

## Building
```bash
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
flutter run -d <device>
```

## License
Copyright © 2026 Verdis Chain. All rights reserved.
