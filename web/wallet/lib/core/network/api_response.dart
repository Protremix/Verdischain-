import 'package:dio/dio.dart';

/// Generic API response wrapper
class ApiResponse<T> {

  ApiResponse.success(this.data) : isSuccess = true, error = null;
  ApiResponse.failure(this.error) : isSuccess = false, data = null;

  factory ApiResponse.fromResponse(Response response, T Function(dynamic) parser) {
    if (response.statusCode == 200) {
      return ApiResponse.success(parser(response.data));
    }
    return ApiResponse.failure('Request failed: ${response.statusCode}');
  }
  final T? data;
  final String? error;
  final bool isSuccess;
}
