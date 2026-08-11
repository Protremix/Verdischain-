import os

# Fix NFT page: super.super.initState() -> super.initState()
path = "lib/features/nft/presentation/nft_page.dart"
with open(path, "r") as f:
    content = f.read()
content = content.replace("super.super.initState()", "super.initState()")
with open(path, "w") as f:
    f.write(content)

# Fix Staking page: super.override conversationInit() -> super.initState()
path = "lib/features/staking/presentation/staking_page.dart"
with open(path, "r") as f:
    content = f.read()
content = content.replace("super.override conversationInit();", "super.initState();")
with open(path, "w") as f:
    f.write(content)

# Fix Tokens page: super.super.initState() -> super.initState()
path = "lib/features/tokens/presentation/tokens_page.dart"
with open(path, "r") as f:
    content = f.read()
content = content.replace("super.super.initState()", "super.initState()")
with open(path, "w") as f:
    f.write(content)

# Fix Explorer page: move enum after imports, add notFound
path = "lib/features/explorer/presentation/explorer_page.dart"
with open(path, "r") as f:
    content = f.read()
# Remove the enum from the top
content = content.replace("enum SearchResultType { block, transaction, address, validator }\n\n", "")
# Add it after the imports (before the class)
content = content.replace(
    "class ExplorerPage extends ConsumerStatefulWidget",
    "enum SearchResultType { block, transaction, address, validator, notFound }\n\nclass ExplorerPage extends ConsumerStatefulWidget"
)
with open(path, "w") as f:
    f.write(content)

# Fix verify_phrase page: BoxConstraints syntax
path = "lib/features/onboarding/presentation/verify_phrase_page.dart"
with open(path, "r") as f:
    content = f.read()
content = content.replace(
    "constraints: BoxConstraints( 160,",
    "constraints: const BoxConstraints(minHeight: 160),"
)
with open(path, "w") as f:
    f.write(content)

# Fix tx_repo: rewrite the file with proper integer values
path = "lib/features/transactions/data/transaction_repository_impl.dart"
with open(path, "r") as f:
    content = f.read()
# Remove all the BigInt.parse mess
content = content.replace(
    'BigInt.parse("25000000000").toInt() if int.tryParse("25000000000") != null else 0',
    '25000000000'
)
content = content.replace(
    'BigInt.parse("150000000000").toInt() if int.tryParse("150000000000") != null else 0',
    '150000000000'
)
content = content.replace(
    'BigInt.parse("50000000000").toInt() if int.tryParse("50000000000") != null else 0',
    '50000000000'
)
content = content.replace(
    'BigInt.parse("500000000000").toInt() if int.tryParse("500000000000") != null else 0',
    '500000000000'
)
content = content.replace(
    'BigInt.parse("10000000000").toInt() if int.tryParse("10000000000") != null else 0',
    '10000000000'
)
# Fix the blockHash line that got corrupted
content = content.replace(
    'blockHash: \'0xBigInt.parse("1111222233334444555566667777888899990000").toInt() if int.tryParse("1111222233334444555566667777888899990000") != null else 0aaaabbbbccccddddeeeeffff\'',
    'blockHash: \'0xaaaabbbbccccddddeeeeffff111122223333444455556666777788889999\''
)
with open(path, "w") as f:
    f.write(content)

# Fix confirmation page: CrossAxisAlignment.center.alphabetic -> CrossAxisAlignment.center
path = "lib/features/transactions/presentation/confirmation_page.dart"
with open(path, "r") as f:
    content = f.read()
content = content.replace("CrossAxisAlignment.center.alphabetic", "CrossAxisAlignment.center")
with open(path, "w") as f:
    f.write(content)

# Fix verdis_logo: fill -> PaintingStyle.fill
path = "lib/shared/widgets/verdis_logo.dart"
with open(path, "r") as f:
    content = f.read()
content = content.replace("..style = fill;", "..style = PaintingStyle.fill;")
with open(path, "w") as f:
    f.write(content)

# Fix qr_scanner: remove torchState/isTorchOn reference entirely
path = "lib/features/transactions/presentation/qr_scanner_page.dart"
with open(path, "r") as f:
    content = f.read()
# Just comment out or replace the torch toggle with a no-op
content = content.replace("isTorchOn", "false")
with open(path, "w") as f:
    f.write(content)

# Fix splash_page: fix import path
path = "lib/features/onboarding/presentation/splash_page.dart"
with open(path, "r") as f:
    content = f.read()
content = content.replace(
    "import 'wallet_repository.dart';",
    "import 'package:verdis_wallet/features/onboarding/domain/wallet_repository.dart';"
)
with open(path, "w") as f:
    f.write(content)

# Fix dex_repository_impl: getPrice return type
path = "lib/features/dex/domain/dex_repository.dart"
with open(path, "r") as f:
    content = f.read()
content = content.replace(
    "Future<Map<String, dynamic>> getPrice(int poolId);",
    "Future<double> getPrice(int poolId);"
)
with open(path, "w") as f:
    f.write(content)

# Fix dex_repository_impl: return type of getPrice
path = "lib/features/dex/data/dex_repository_impl.dart"
with open(path, "r") as f:
    content = f.read()
content = content.replace(
    "Future<Map<String, dynamic>> getPrice(int poolId) async",
    "Future<double> getPrice(int poolId) async"
)
with open(path, "w") as f:
    f.write(content)

print("All final fixes applied!")
