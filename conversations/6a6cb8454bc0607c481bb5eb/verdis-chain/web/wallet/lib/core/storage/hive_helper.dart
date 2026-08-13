import 'package:hive/hive.dart';
import 'package:path_provider/path_provider.dart';

/// Hive local storage helper for non-sensitive data
class HiveHelper {
  static const String _settingsBox = 'verdis_settings';
  static const String _cacheBox = 'verdis_cache';
  static const String _transactionBox = 'verdis_transactions';
  static const String _tokenBox = 'verdis_tokens';
  static const String _nftBox = 'verdis_nfts';

  static bool _initialized = false;

  static Future<void> init() async {
    if (_initialized) return;

    final dir = await getApplicationDocumentsDirectory();
    Hive.init(dir.path);

    await Hive.openBox(_settingsBox);
    await Hive.openBox(_cacheBox);
    await Hive.openBox(_transactionBox);
    await Hive.openBox(_tokenBox);
    await Hive.openBox(_nftBox);

    _initialized = true;
  }

  static Box get settings => Hive.box(_settingsBox);
  static Box get cache => Hive.box(_cacheBox);
  static Box get transactions => Hive.box(_transactionBox);
  static Box get tokens => Hive.box(_tokenBox);
  static Box get nfts => Hive.box(_nftBox);

  // Settings helpers
  static T? getSetting<T>(String key) => settings.get(key) as T?;
  static Future<void> setSetting(String key, dynamic value) => settings.put(key, value);
  static Future<void> removeSetting(String key) => settings.delete(key);

  // Cache helpers
  static T? getCache<T>(String key) => cache.get(key) as T?;
  static Future<void> setCache(String key, dynamic value) => cache.put(key, value);
  static Future<void> clearCache() => cache.clear();

  // Transaction helpers
  static List<dynamic> getCachedTransactions() => transactions.values.toList();
  static Future<void> cacheTransaction(Map<String, dynamic> tx) async {
    await transactions.put(tx['hash'], tx);
  }
  static Future<void> clearTransactions() => transactions.clear();

  // Token helpers
  static List<dynamic> getCachedTokens() => tokens.values.toList();
  static Future<void> cacheToken(String tokenId, Map<String, dynamic> token) async {
    await tokens.put(tokenId, token);
  }
  static Future<void> removeToken(String tokenId) => tokens.delete(tokenId);

  // NFT helpers
  static List<dynamic> getCachedNfts() => nfts.values.toList();
  static Future<void> cacheNft(String nftId, Map<String, dynamic> nft) async {
    await nfts.put(nftId, nft);
  }
  static Future<void> removeNft(String nftId) => nfts.delete(nftId);
}
