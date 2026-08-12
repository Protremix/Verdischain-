import re

with open('/opt/verdis-wallet/lib/features/transactions/data/transaction_repository_impl.dart', 'r') as f:
    content = f.read()

# Remove the _BlockExtrinsics class that was incorrectly placed inside the main class
old_helper = """/// Helper class for block extrinsics during async fetching
class _BlockExtrinsics {
  final int blockNumber;
  final String blockHash;
  final List<dynamic>? extrinsics;
  _BlockExtrinsics(this.blockNumber, this.blockHash, this.extrinsics);
}

  // === SS58 decoding ==="""

new_section = """  // === SS58 decoding ==="""

content = content.replace(old_helper, new_section)

# Add the _BlockExtrinsics class at the very end of the file (top level, after the closing brace of the main class)
# Find the last closing brace
content = content.rstrip() + "\n\n/// Helper class for block extrinsics during async fetching\nclass _BlockExtrinsics {\n  final int blockNumber;\n  final String blockHash;\n  final List<dynamic>? extrinsics;\n  _BlockExtrinsics(this.blockNumber, this.blockHash, this.extrinsics);\n}\n"

with open('/opt/verdis-wallet/lib/features/transactions/data/transaction_repository_impl.dart', 'w') as f:
    f.write(content)
print('Fixed: _BlockExtrinsics moved to top level.')
