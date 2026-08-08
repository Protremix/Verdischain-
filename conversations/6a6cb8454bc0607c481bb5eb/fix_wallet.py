import re

with open('/opt/verdis-wallet/mobile/lib/services/wallet_service.dart', 'r') as f:
    content = f.read()

# Fix 1: Remove leftover staking data in fetchBalance
content = content.replace(
    """      } catch (_) {
        // No simulated fallback — real RPC only
        // Balance will show 0 if RPC unavailable
          _stakedAmount = 500.0;
          _stakingRewards = 14.25;
        }
      }""",
    """      } catch (_) {
        // Balance will show 0 if RPC unavailable
      }
    }"""
)

# Fix 2: Fix the sendTokens function — find and replace the broken TX Relay code
# Find the sendTokens function and replace it entirely
import re

# Match from "Future<bool> sendTokens" to the next function at same indentation
match = re.search(r'(  Future<bool> sendTokens\({.*?}\) async \{.*?\n  \})', content, re.DOTALL)
if match:
    new_send = """  Future<bool> sendTokens({required String recipient, required double amount}) async {
    if (_activeAccount == null) return false;
    if (amount <= 0 || amount > _vrdxBalance) {
      _errorMessage = 'Insufficient balance';
      notifyListeners();
      return false;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    String txHash = '0xpending';
    try {
      final relayRes = await http.post(
        Uri.parse('https://verdischain.com/api/tx-relay'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'action': 'transfer',
          'to': recipient,
          'amount': (amount * 1e9).round(),
        }),
      );
      final relayData = json.decode(relayRes.body);
      if relayData['ok'] == true:
        txHash = relayData['extrinsic_hash'] ?? '0xpending';
      else:
        throw Exception(relayData['error'] ?? 'TX Relay failed');

      _vrdxBalance -= amount;

      final tx = TransactionRecord(
        hash: txHash,
        fromAddress: _activeAccount!.address,
        toAddress: recipient,
        amount: amount,
        timestamp: DateTime.now(),
        status: 'submitted',
        type: 'transfer',
      );
      _transactions.insert(0, tx);
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = 'Transaction failed: $e';
      notifyListeners();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }"""
    content = content[:match.start()] + new_send + content[match.end():]
    print("Fixed sendTokens")
else:
    print("sendTokens not found with regex")

# Fix 3: Replace ALL remaining fake sha256 tx hashes with simple pending hash
# Pattern: final txHash = '0x' + sha256.convert(...)
content = re.sub(
    r"final txHash = '0x\$\{[^}]+\}';",
    "String txHash = '0xpending';",
    content
)
print("Replaced remaining fake tx hashes")

with open('/opt/verdis-wallet/mobile/lib/services/wallet_service.dart', 'w') as f:
    f.write(content)

print("Done")
