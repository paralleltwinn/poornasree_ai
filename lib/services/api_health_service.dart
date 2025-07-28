import 'package:http/http.dart' as http;
import 'dart:convert';
import '../utils/constants.dart';

class ApiHealthService {
  static String get apiBaseUrl => AppConstants.apiBaseUrl;

  /// Get comprehensive health status from the API
  static Future<Map<String, dynamic>> getDetailedHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/health/detailed'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        // Parse the Indian timestamp from the API
        if (data['timestamp'] != null) {
          try {
            data['timestamp_parsed'] = DateTime.parse(data['timestamp']);
            data['timestamp_local'] = data['timestamp'];
          } catch (e) {
            data['timestamp_parsed'] = DateTime.now();
          }
        }
        
        return data;
      } else {
        return {
          'status': 'unhealthy',
          'api_accessible': false,
          'error': 'HTTP ${response.statusCode}'
        };
      }
    } catch (e) {
      return {
        'status': 'unhealthy',
        'api_accessible': false,
        'error': e.toString(),
        'timestamp_parsed': DateTime.now(),
      };
    }
  }

  /// Quick ping to check API availability
  static Future<bool> pingApi() async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/ping'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 5));

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Get basic health status
  static Future<Map<String, dynamic>> getBasicHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        // Parse the Indian timestamp from the API
        if (data['timestamp'] != null) {
          try {
            data['timestamp_parsed'] = DateTime.parse(data['timestamp']);
          } catch (e) {
            data['timestamp_parsed'] = DateTime.now();
          }
        }
        
        return data;
      } else {
        return {
          'status': 'unhealthy',
          'timestamp_parsed': DateTime.now(),
        };
      }
    } catch (e) {
      return {
        'status': 'unhealthy',
        'error': e.toString(),
        'timestamp_parsed': DateTime.now(),
      };
    }
  }

  /// Check AI service specific health
  static Future<Map<String, dynamic>> getAiHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/health/ai'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        // Parse the Indian timestamp from the API
        if (data['timestamp'] != null) {
          try {
            data['timestamp_parsed'] = DateTime.parse(data['timestamp']);
          } catch (e) {
            data['timestamp_parsed'] = DateTime.now();
          }
        }
        
        return data;
      } else {
        return {
          'status': 'unhealthy',
          'ai_accessible': false,
          'timestamp_parsed': DateTime.now(),
        };
      }
    } catch (e) {
      return {
        'status': 'unhealthy',
        'ai_accessible': false,
        'error': e.toString(),
        'timestamp_parsed': DateTime.now(),
      };
    }
  }

  /// Format Indian time for display
  static String formatIndianTime(DateTime? dateTime) {
    if (dateTime == null) return 'Unknown';
    
    // The API already provides IST timestamps
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} '
           '${dateTime.hour.toString().padLeft(2, '0')}:'
           '${dateTime.minute.toString().padLeft(2, '0')}:'
           '${dateTime.second.toString().padLeft(2, '0')} IST';
  }

  /// Check connection status with detailed info
  static Future<Map<String, dynamic>> checkConnection() async {
    final Map<String, dynamic> result = {
      'ping_success': false,
      'health_success': false,
      'ai_success': false,
      'overall_status': 'disconnected',
      'timestamp': DateTime.now(),
    };

    try {
      // Test basic ping
      result['ping_success'] = await pingApi();
      print('DEBUG: Ping result: ${result['ping_success']}');
      
      // Test health endpoint
      final healthResult = await getBasicHealth();
      result['health_success'] = healthResult['status'] == 'healthy';
      result['health_data'] = healthResult;
      print('DEBUG: Health result: ${result['health_success']}, status: ${healthResult['status']}');
      
      // Test AI endpoint
      final aiResult = await getAiHealth();
      result['ai_success'] = aiResult['status'] == 'healthy' || aiResult['status'] == 'initializing';
      result['ai_data'] = aiResult;
      print('DEBUG: AI result: ${result['ai_success']}, status: ${aiResult['status']}');
      
      // Determine overall status
      if (result['ping_success'] && result['health_success'] && result['ai_success']) {
        result['overall_status'] = 'fully_connected';
      } else if (result['ping_success'] && result['health_success']) {
        result['overall_status'] = 'partially_connected';
      } else if (result['ping_success']) {
        result['overall_status'] = 'basic_connection';
      } else {
        result['overall_status'] = 'disconnected';
      }
      
      print('DEBUG: Overall status: ${result['overall_status']}');
      
    } catch (e) {
      result['error'] = e.toString();
      print('DEBUG: Health check error: $e');
    }
    
    return result;
  }
}
