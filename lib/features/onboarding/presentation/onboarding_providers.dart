import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:verdis_wallet/core/security/biometric_auth.dart';
import 'package:verdis_wallet/core/security/secure_storage.dart';
import '../data/wallet_repository_impl.dart';
import 'package:verdis_wallet/core/security/pin_security_service.dart';
import '../domain/wallet_repository.dart';

// Override default repository provider with concrete implementation
final onboardingWalletProvider = Provider<WalletRepository>((ref) {
  final secureStorage = ref.watch(secureStorageProvider);
  return WalletRepositoryImpl(secureStorage);
});

// ==========================================
// 1. WALLET CREATION STATE & NOTIFIER
// ==========================================

class WalletCreationState {

  const WalletCreationState({
    this.mnemonic = '',
    this.address = '',
    this.publicKey = '',
    this.privateKey = '',
    this.isLoading = false,
    this.isSavedConfirmed = false,
    this.error,
  });
  final String mnemonic;
  final String address;
  final String publicKey;
  final String privateKey;
  final bool isLoading;
  final bool isSavedConfirmed;
  final String? error;

  List<String> get mnemonicWords => mnemonic.trim().isEmpty ? [] : mnemonic.trim().split(' ');

  WalletCreationState copyWith({
    String? mnemonic,
    String? address,
    String? publicKey,
    String? privateKey,
    bool? isLoading,
    bool? isSavedConfirmed,
    String? error,
  }) {
    return WalletCreationState(
      mnemonic: mnemonic ?? this.mnemonic,
      address: address ?? this.address,
      publicKey: publicKey ?? this.publicKey,
      privateKey: privateKey ?? this.privateKey,
      isLoading: isLoading ?? this.isLoading,
      isSavedConfirmed: isSavedConfirmed ?? this.isSavedConfirmed,
      error: error,
    );
  }
}

class WalletCreationNotifier extends StateNotifier<WalletCreationState> {

  WalletCreationNotifier(this._repository) : super(const WalletCreationState());
  final WalletRepository _repository;

  Future<void> generateNewWallet() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final mnemonic = await _repository.generateMnemonic();
      final keypair = await _repository.deriveKeypair(mnemonic);

      state = state.copyWith(
        mnemonic: mnemonic,
        address: keypair['address'] ?? '',
        publicKey: keypair['publicKey'] ?? '',
        privateKey: keypair['privateKey'] ?? '',
        isLoading: false,
        isSavedConfirmed: false,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: 'Failed to generate wallet: $e');
    }
  }

  void toggleSavedConfirmed(bool value) {
    state = state.copyWith(isSavedConfirmed: value);
  }
}

final walletCreationProvider =
    StateNotifierProvider<WalletCreationNotifier, WalletCreationState>((ref) {
  return WalletCreationNotifier(ref.watch(onboardingWalletProvider));
});

// ==========================================
// 2. WALLET IMPORT STATE & NOTIFIER
// ==========================================

class WalletImportState {

  const WalletImportState({
    this.mnemonicInput = '',
    this.wordCount = 12,
    this.isValid = false,
    this.isLoading = false,
    this.derivedAddress,
    this.derivedPrivateKey,
    this.derivedPublicKey,
    this.error,
  });
  final String mnemonicInput;
  final int wordCount;
  final bool isValid;
  final bool isLoading;
  final String? derivedAddress;
  final String? derivedPrivateKey;
  final String? derivedPublicKey;
  final String? error;

  WalletImportState copyWith({
    String? mnemonicInput,
    int? wordCount,
    bool? isValid,
    bool? isLoading,
    String? derivedAddress,
    String? derivedPrivateKey,
    String? derivedPublicKey,
    String? error,
  }) {
    return WalletImportState(
      mnemonicInput: mnemonicInput ?? this.mnemonicInput,
      wordCount: wordCount ?? this.wordCount,
      isValid: isValid ?? this.isValid,
      isLoading: isLoading ?? this.isLoading,
      derivedAddress: derivedAddress ?? this.derivedAddress,
      derivedPrivateKey: derivedPrivateKey ?? this.derivedPrivateKey,
      derivedPublicKey: derivedPublicKey ?? this.derivedPublicKey,
      error: error,
    );
  }
}

class WalletImportNotifier extends StateNotifier<WalletImportState> {

  WalletImportNotifier(this._repository) : super(const WalletImportState());
  final WalletRepository _repository;

  void setWordCount(int count) {
    state = state.copyWith(wordCount: count);
    validateInput(state.mnemonicInput);
  }

  Future<void> updateMnemonicInput(String text) async {
    state = state.copyWith(mnemonicInput: text, error: null);
    await validateInput(text);
  }

  Future<bool> validateInput(String input) async {
    final cleaned = input.trim().replaceAll(RegExp(r'\s+'), ' ');
    if (cleaned.isEmpty) {
      state = state.copyWith(isValid: false, error: null);
      return false;
    }
    final words = cleaned.split(' ');
    if (words.length != 12 && words.length != 24) {
      state = state.copyWith(
        isValid: false,
        error: 'Please enter exactly 12 or 24 words (${words.length} entered)',
      );
      return false;
    }

    final isValidChecksum = await _repository.validateMnemonic(cleaned);
    if (!isValidChecksum) {
      state = state.copyWith(isValid: false, error: 'Invalid seed phrase checksum. Check word spelling.');
      return false;
    }

    state = state.copyWith(isValid: true, error: null);
    return true;
  }

  Future<bool> importWallet() async {
    final cleaned = state.mnemonicInput.trim().replaceAll(RegExp(r'\s+'), ' ');
    state = state.copyWith(isLoading: true, error: null);
    try {
      final keypair = await _repository.importFromMnemonic(cleaned);
      state = state.copyWith(
        isLoading: false,
        derivedAddress: keypair['address'],
        derivedPrivateKey: keypair['privateKey'],
        derivedPublicKey: keypair['publicKey'],
        isValid: true,
      );
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }
}

final walletImportProvider =
    StateNotifierProvider<WalletImportNotifier, WalletImportState>((ref) {
  return WalletImportNotifier(ref.watch(onboardingWalletProvider));
});

// ==========================================
// 3. PIN SETUP STATE & NOTIFIER
// ==========================================

class PinSetupState {

  const PinSetupState({
    this.pin = '',
    this.confirmPin = '',
    this.isConfirming = false,
    this.isLoading = false,
    this.isSuccess = false,
    this.error,
  });
  final String pin;
  final String confirmPin;
  final bool isConfirming;
  final bool isLoading;
  final bool isSuccess;
  final String? error;

  PinSetupState copyWith({
    String? pin,
    String? confirmPin,
    bool? isConfirming,
    bool? isLoading,
    bool? isSuccess,
    String? error,
  }) {
    return PinSetupState(
      pin: pin ?? this.pin,
      confirmPin: confirmPin ?? this.confirmPin,
      isConfirming: isConfirming ?? this.isConfirming,
      isLoading: isLoading ?? this.isLoading,
      isSuccess: isSuccess ?? this.isSuccess,
      error: error,
    );
  }
}

class PinSetupNotifier extends StateNotifier<PinSetupState> {

  PinSetupNotifier(this._repository) : super(const PinSetupState());
  final WalletRepository _repository;

  void appendDigit(String digit) {
    if (state.isLoading || state.isSuccess) return;

    if (!state.isConfirming) {
      if (state.pin.length < 6) {
        final newPin = state.pin + digit;
        state = state.copyWith(pin: newPin, error: null);
        if (newPin.length == 6) {
          state = state.copyWith(isConfirming: true);
        }
      }
    } else {
      if (state.confirmPin.length < 6) {
        final newConfirm = state.confirmPin + digit;
        state = state.copyWith(confirmPin: newConfirm, error: null);
      }
    }
  }

  void deleteDigit() {
    if (state.isLoading || state.isSuccess) return;

    if (state.isConfirming) {
      if (state.confirmPin.isNotEmpty) {
        state = state.copyWith(
          confirmPin: state.confirmPin.substring(0, state.confirmPin.length - 1),
          error: null,
        );
      } else {
        // Step back to first PIN phase if confirmPin is empty
        state = state.copyWith(isConfirming: false, pin: '');
      }
    } else {
      if (state.pin.isNotEmpty) {
        state = state.copyWith(
          pin: state.pin.substring(0, state.pin.length - 1),
          error: null,
        );
      }
    }
  }

  void clearPin() {
    state = const PinSetupState();
  }

  Future<bool> submitAndFinalizePin({
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
            error: 'Wallet is locked. Try again in $mins minute(s).',
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

      // 3. Store wallet in secure storage (with PIN for mnemonic encryption)
      await _repository.storeWallet(
        mnemonic: mnemonic,
        privateKey: privateKey,
        publicKey: publicKey,
        address: address,
        pin: state.pin,
      );

      state = state.copyWith(isLoading: false, isSuccess: true);
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: 'Failed to save security PIN: $e');
      return false;
    }
  }
}

final pinSetupProvider =
    StateNotifierProvider<PinSetupNotifier, PinSetupState>((ref) {
  return PinSetupNotifier(ref.watch(onboardingWalletProvider));
});

// ==========================================
// 4. BIOMETRIC SETUP STATE & NOTIFIER
// ==========================================

class BiometricSetupState {

  const BiometricSetupState({
    this.isAvailable = false,
    this.isEnabled = false,
    this.isLoading = false,
    this.error,
  });
  final bool isAvailable;
  final bool isEnabled;
  final bool isLoading;
  final String? error;

  BiometricSetupState copyWith({
    bool? isAvailable,
    bool? isEnabled,
    bool? isLoading,
    String? error,
  }) {
    return BiometricSetupState(
      isAvailable: isAvailable ?? this.isAvailable,
      isEnabled: isEnabled ?? this.isEnabled,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class BiometricSetupNotifier extends StateNotifier<BiometricSetupState> {

  BiometricSetupNotifier(this._biometricManager, this._repository)
      : super(const BiometricSetupState()) {
    checkAvailability();
  }
  final BiometricManager _biometricManager;
  final WalletRepository _repository;

  Future<void> checkAvailability() async {
    state = state.copyWith(isLoading: true);
    try {
      final available = await _biometricManager.isAvailable();
      final enabled = await _repository.isBiometricEnabled();
      state = state.copyWith(
        isAvailable: available,
        isEnabled: enabled,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<bool> toggleBiometric(bool enabled) async {
    if (enabled && state.isAvailable) {
      final authenticated = await _biometricManager.authenticate(
        reason: 'Enable biometric authentication for Verdis Wallet',
      );
      if (!authenticated) {
        state = state.copyWith(
          isEnabled: false,
          error: 'Biometric authentication cancelled or failed',
        );
        return false;
      }
    }

    await _repository.setBiometricEnabled(enabled);
    state = state.copyWith(isEnabled: enabled, error: null);
    return true;
  }
}

final biometricSetupProvider =
    StateNotifierProvider<BiometricSetupNotifier, BiometricSetupState>((ref) {
  final biometricManager = ref.watch(biometricAuthProvider);
  final walletRepository = ref.watch(onboardingWalletProvider);
  return BiometricSetupNotifier(biometricManager, walletRepository);
});
