import "dart:convert";
import "dart:io";
import "package:path/path.dart" as p;
import "package:path_provider/path_provider.dart";
import "secure_crypto.dart";

class AccountRecord {
  final int? id;
  final String address;
  final String name;
  final String encryptedKey;
  final String createdAt;
  final bool isActive;

  AccountRecord({
    this.id,
    required this.address,
    required this.name,
    required this.encryptedKey,
    required this.createdAt,
    this.isActive = false,
  });

  Map<String, dynamic> toMap() => {
    if (id != null) "id": id,
    "address": address,
    "name": name,
    "encrypted_key": encryptedKey,
    "created_at": createdAt,
    "is_active": isActive ? 1 : 0,
  };

  factory AccountRecord.fromMap(Map<String, dynamic> map) => AccountRecord(
    id: map["id"] as int?,
    address: map["address"] as String? ?? "",
    name: map["name"] as String? ?? "",
    encryptedKey: map["encrypted_key"] as String? ?? "",
    createdAt: map["created_at"] as String? ?? "",
    isActive: (map["is_active"] as int? ?? 0) == 1,
  );
}

class TransactionRecord {
  final int? id;
  final String hash;
  final String fromAddress;
  final String toAddress;
  final double amount;
  final int timestamp;
  final String status;
  final String txType;

  TransactionRecord({
    this.id,
    required this.hash,
    required this.fromAddress,
    required this.toAddress,
    required this.amount,
    required this.timestamp,
    required this.status,
    required this.txType,
  });

  Map<String, dynamic> toMap() => {
    if (id != null) "id": id,
    "hash": hash,
    "from_address": fromAddress,
    "to_address": toAddress,
    "amount": amount,
    "timestamp": timestamp,
    "status": status,
    "tx_type": txType,
  };

  factory TransactionRecord.fromMap(Map<String, dynamic> map) => TransactionRecord(
    id: map["id"] as int?,
    hash: map["hash"] as String? ?? "",
    fromAddress: map["from_address"] as String? ?? "",
    toAddress: map["to_address"] as String? ?? "",
    amount: (map["amount"] as num? ?? 0.0).toDouble(),
    timestamp: map["timestamp"] as int? ?? DateTime.now().millisecondsSinceEpoch,
    status: map["status"] as String? ?? "Pending",
    txType: map["tx_type"] as String? ?? "Transfer",
  );
}

class ContactRecord {
  final int? id;
  final String address;
  final String name;

  ContactRecord({this.id, required this.address, required this.name});

  Map<String, dynamic> toMap() => {
    if (id != null) "id": id,
    "address": address,
    "name": name,
  };

  factory ContactRecord.fromMap(Map<String, dynamic> map) => ContactRecord(
    id: map["id"] as int?,
    address: map["address"] as String? ?? "",
    name: map["name"] as String? ?? "",
  );
}

class DatabaseService {
  static final DatabaseService instance = DatabaseService._init();
  static Map<String, dynamic>? _data;
  static int _nextId = 1;

  DatabaseService._init();

  Future<String> _getDbPath() async {
    final dir = await getApplicationDocumentsDirectory();
    return p.join(dir.path, "verdis_wallet.json");
  }

  Future<Map<String, dynamic>> _load() async {
    if (_data != null) return _data!;
    try {
      final path = await _getDbPath();
      final file = File(path);
      if (await file.exists()) {
        _data = jsonDecode(await file.readAsString());
        final accounts = _data!["accounts"] as List? ?? [];
        final txs = _data!["transactions"] as List? ?? [];
        final contacts = _data!["contacts"] as List? ?? [];
        int maxId = 0;
        for (final m in [...accounts, ...txs, ...contacts]) {
          final id = (m as Map)["id"] as int?;
          if (id != null && id > maxId) maxId = id;
        }
        _nextId = maxId + 1;
      } else {
        _data = {"accounts": [], "transactions": [], "contacts": []};
      }
    } catch (e) {
      _data = {"accounts": [], "transactions": [], "contacts": []};
    }
    return _data!;
  }

  Future<void> _save() async {
    try {
      final path = await _getDbPath();
      final file = File(path);
      await file.writeAsString(jsonEncode(_data));
    } catch (e) {
      // Ignore save errors
    }
  }

  int _nextAccountId() => _nextId++;

  // --- Account CRUD ---

  /// Insert a new account with the mnemonic encrypted using the PIN
  Future<int> insertAccount(AccountRecord account, {String pin = ""}) async {
    final data = await _load();
    final accounts = (data["accounts"] as List).cast<Map<String, dynamic>>();

    // Encrypt the key material using SecureCrypto
    String storedKey = account.encryptedKey;
    if (pin.isNotEmpty) {
      try {
        String mnemonic = account.encryptedKey;
        if (mnemonic.startsWith("eyJ")) {
          // Old base64 format - decode first
          mnemonic = utf8.decode(base64.decode(mnemonic));
        }
        storedKey = SecureCrypto.encrypt(mnemonic, pin);
      } catch (e) {
        storedKey = account.encryptedKey;
      }
    }

    if (account.isActive) {
      for (final a in accounts) {
        a["is_active"] = 0;
      }
    }
    final newAccount = account.toMap();
    newAccount["encrypted_key"] = storedKey;
    newAccount["id"] = _nextAccountId();
    accounts.add(newAccount);
    data["accounts"] = accounts;
    await _save();
    return newAccount["id"] as int;
  }

  /// Decrypt and retrieve the mnemonic for an account
  Future<String?> getMnemonic(AccountRecord account, String pin) async {
    try {
      final encrypted = account.encryptedKey;
      // Try SecureCrypto decryption first
      final decrypted = SecureCrypto.decrypt(encrypted, pin);
      if (decrypted != null) return decrypted;
      // Fall back: try base64 decode for legacy accounts
      if (encrypted.startsWith("eyJ")) {
        return utf8.decode(base64.decode(encrypted));
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  /// Re-encrypt all accounts from old base64 format to SecureCrypto encryption
  Future<void> migrateEncryption(String pin) async {
    if (pin.isEmpty) return;
    final data = await _load();
    final accounts = (data["accounts"] as List).cast<Map<String, dynamic>>();
    bool changed = false;
    for (final a in accounts) {
      final key = a["encrypted_key"] as String? ?? "";
      // Check if it is old base64 format
      if (key.isNotEmpty && key.startsWith("eyJ")) {
        try {
          final mnemonic = utf8.decode(base64.decode(key));
          a["encrypted_key"] = SecureCrypto.encrypt(mnemonic, pin);
          changed = true;
        } catch (_) {}
      }
    }
    if (changed) await _save();
  }

  Future<List<AccountRecord>> getAccounts() async {
    final data = await _load();
    final accounts = (data["accounts"] as List).cast<Map<String, dynamic>>();
    accounts.sort((a, b) => (a["id"] as int? ?? 0).compareTo(b["id"] as int? ?? 0));
    return accounts.map((m) => AccountRecord.fromMap(Map.from(m))).toList();
  }

  Future<AccountRecord?> getActiveAccount() async {
    final data = await _load();
    final accounts = (data["accounts"] as List).cast<Map<String, dynamic>>();
    for (final a in accounts) {
      if ((a["is_active"] as int? ?? 0) == 1) {
        return AccountRecord.fromMap(Map.from(a));
      }
    }
    if (accounts.isNotEmpty) {
      return AccountRecord.fromMap(Map.from(accounts.first));
    }
    return null;
  }

  Future<void> setActiveAccount(String address) async {
    final data = await _load();
    final accounts = (data["accounts"] as List).cast<Map<String, dynamic>>();
    for (final a in accounts) {
      a["is_active"] = (a["address"] == address) ? 1 : 0;
    }
    await _save();
  }

  Future<int> deleteAccount(String address) async {
    final data = await _load();
    final accounts = (data["accounts"] as List).cast<Map<String, dynamic>>();
    final before = accounts.length;
    accounts.removeWhere((a) => a["address"] == address);
    await _save();
    return before - accounts.length;
  }

  // --- Transaction CRUD ---
  Future<int> insertTransaction(TransactionRecord tx) async {
    final data = await _load();
    final txs = (data["transactions"] as List).cast<Map<String, dynamic>>();
    final newTx = tx.toMap();
    newTx["id"] = _nextAccountId();
    txs.add(newTx);
    data["transactions"] = txs;
    await _save();
    return newTx["id"] as int;
  }

  Future<List<TransactionRecord>> getTransactions({String? address}) async {
    final data = await _load();
    final txs = (data["transactions"] as List).cast<Map<String, dynamic>>();
    List<Map<String, dynamic>> filtered;
    if (address != null && address.isNotEmpty) {
      filtered = txs.where((t) =>
        t["from_address"] == address || t["to_address"] == address
      ).toList();
    } else {
      filtered = txs.toList();
    }
    filtered.sort((a, b) => (b["timestamp"] as int? ?? 0).compareTo(a["timestamp"] as int? ?? 0));
    return filtered.map((m) => TransactionRecord.fromMap(Map.from(m))).toList();
  }

  // --- Contacts CRUD ---
  Future<int> insertContact(ContactRecord contact) async {
    final data = await _load();
    final contacts = (data["contacts"] as List).cast<Map<String, dynamic>>();
    final newContact = contact.toMap();
    newContact["id"] = _nextAccountId();
    contacts.add(newContact);
    data["contacts"] = contacts;
    await _save();
    return newContact["id"] as int;
  }

  Future<List<ContactRecord>> getContacts() async {
    final data = await _load();
    final contacts = (data["contacts"] as List).cast<Map<String, dynamic>>();
    contacts.sort((a, b) => (a["name"] as String? ?? "").compareTo(b["name"] as String? ?? ""));
    return contacts.map((m) => ContactRecord.fromMap(Map.from(m))).toList();
  }

  Future<int> deleteContact(int id) async {
    final data = await _load();
    final contacts = (data["contacts"] as List).cast<Map<String, dynamic>>();
    final before = contacts.length;
    contacts.removeWhere((c) => c["id"] == id);
    await _save();
    return before - contacts.length;
  }

  Future<void> clearAll() async {
    _data = {"accounts": [], "transactions": [], "contacts": []};
    await _save();
  }
}
