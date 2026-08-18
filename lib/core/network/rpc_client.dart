import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/network_config.dart';

final rpcClientProvider = Provider<RpcClient>((ref) => RpcClient());

class RpcClient {
  RpcClient() {
    _dio = Dio(BaseOptions(
      baseUrl: NetworkConfig.rpcUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {'Content-Type': 'application/json'},
    ),);
    // Reject all invalid certificates (cert pinning is enforced at OS level via network_security_config.xml)
    (_dio.httpClientAdapter as dynamic).onHttpClientCreate = (client) {
      client.badCertificateCallback = (cert, host, port) {
        // Reject any cert that is not for verdischain.com
        return false;
      };
    };
  }
  late final Dio _dio;

  Future<T> call<T>(String method, [List<dynamic>? params]) async {
    final response = await _dio.post('/', data: {
      'jsonrpc': '2.0',
      'id': '1',
      'method': method,
      'params': params ?? [],
    },);
    return response.data['result'] as T;
  }

  Future<Map<String, dynamic>> getHealth() async {
    final result = await call('system_health');
    return result as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getSyncState() async {
    final result = await call('system_syncState');
    return result as Map<String, dynamic>;
  }

  Future<String> getFinalizedHead() async {
    final result = await call('chain_getFinalizedHead');
    return result.toString();
  }

  Future<String> getChainName() async {
    final result = await call('system_chain');
    return result.toString();
  }

  Future<String> getChainType() async {
    final result = await call('system_chainType');
    return result.toString();
  }

  Future<Map<String, dynamic>> getRuntimeVersion() async {
    final result = await call('state_getRuntimeVersion');
    return result as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getHeader([int? blockNumber]) async {
    final hash = blockNumber != null
        ? await call('chain_getBlockHash', [blockNumber])
        : null;
    final result = await call('chain_getHeader', [hash]);
    return result as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getBlock([String? hash]) async {
    final result = await call('chain_getBlock', [hash]);
    return result as Map<String, dynamic>;
  }

  Future<String> getBlockHash([int? blockNumber]) async {
    final result = await call('chain_getBlockHash', [blockNumber]);
    return result.toString();
  }

  Future<List<dynamic>> getStorageKeys(String key) async {
    final result = await call('state_getStorageKeys', [key]);
    return result as List<dynamic>;
  }

  Future<dynamic> getStorage(String key) async {
    final result = await call('state_getStorage', [key]);
    return result;
  }

  Future<int> getExistentialDeposit() async {
    // Default existential deposit for Verdis
    return 1000000;
  }

  Future<Map<String, dynamic>> getProperties() async {
    final result = await call('system_properties');
    return result as Map<String, dynamic>;
  }

  // DEX RPC methods
  Future<List<dynamic>> getAllDexPools() async {
    return await call('amm_dex_getAllPools') as List<dynamic>;
  }

  Future<Map<String, dynamic>> getDexPool(int poolId) async {
    final result = await call('amm_dex_getPool', [poolId]);
    return result as Map<String, dynamic>;
  }

  Future<double> getDexPrice(int poolId) async {
    final result = await call('amm_dex_getPrice', [poolId]);
    return (result as num).toDouble();
  }

  Future<Map<String, dynamic>> getDexLiquidity(int poolId) async {
    final result = await call('amm_dex_getLiquidity', [poolId]);
    return result as Map<String, dynamic>;
  }

  // Transaction submission
  Future<String> submitExtrinsic(String encodedTx) async {
    final result = await call('author_submitExtrinsic', [encodedTx]);
    return result.toString();
  }

  // Get nonce for an account
  Future<int> getNonce(String address) async {
    final result = await call('system_accountNextIndex', [address]);
    return (result as num).toInt();
  }

  // Get account info
  Future<Map<String, dynamic>> getAccountInfo(String address) async {
    final result = await call('system_account', [address]);
    return result as Map<String, dynamic>;
  }
}
