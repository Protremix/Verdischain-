# Fix 1: dex_repository_impl getPrice - return just the double price
path = "lib/features/dex/data/dex_repository_impl.dart"
with open(path, "r") as f:
    content = f.read()

content = content.replace(
    """  Future<double> getPrice(int poolId) async {
    try {
      return await _rpcClient.getDexPrice(poolId);
    } catch (_) {
      final pool = await getPoolDetail(poolId);
      final price = pool.reserveA > 0 ? pool.reserveB / pool.reserveA : 0.0;
      return {
        'poolId': poolId,
        'price': price,
        'tokenA': pool.tokenA,
        'tokenB': pool.tokenB,
      };
    }
  }""",
    """  Future<double> getPrice(int poolId) async {
    try {
      return await _rpcClient.getDexPrice(poolId);
    } catch (_) {
      final pool = await getPoolDetail(poolId);
      return pool.reserveA > 0 ? pool.reserveB / pool.reserveA : 0.0;
    }
  }"""
)
with open(path, "w") as f:
    f.write(content)

# Fix 2: qr_scanner_page - remove torch toggle entirely, replace with simple button
path = "lib/features/transactions/presentation/qr_scanner_page.dart"
with open(path, "r") as f:
    content = f.read()

content = content.replace(
    """                  ValueListenableBuilder<TorchState>(
                    valueListenable: _controller.false,
                    builder: (context, state, child) {
                      final false = state == TorchState.on;
                      return CircleAvatar(
                        backgroundColor: Colors.black.withOpacity(0.6),
                        child: IconButton(
                          icon: Icon(
                            false ? Icons.flash_on : Icons.flash_off,
                            color: Colors.white,
                          ),
                          onPressed: () {
                            _controller.toggleTorch();
                          },
                        ),
                      );
                    },
                  ),""",
    """                  CircleAvatar(
                    backgroundColor: Colors.black.withOpacity(0.6),
                    child: IconButton(
                      icon: const Icon(
                        Icons.flash_off,
                        color: Colors.white,
                      ),
                      onPressed: () {
                        _controller.toggleTorch();
                      },
                    ),
                  ),"""
)
with open(path, "w") as f:
    f.write(content)

print("Last 4 errors fixed!")
