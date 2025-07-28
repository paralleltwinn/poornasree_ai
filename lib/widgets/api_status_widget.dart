import 'package:flutter/material.dart';
import '../services/api_health_service.dart';
import '../utils/time_utils.dart';

class ApiStatusWidget extends StatefulWidget {
  const ApiStatusWidget({super.key});

  @override
  State<ApiStatusWidget> createState() => _ApiStatusWidgetState();
}

class _ApiStatusWidgetState extends State<ApiStatusWidget> {
  Map<String, dynamic>? healthData;
  bool isLoading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    _checkApiStatus();
  }

  Future<void> _checkApiStatus() async {
    try {
      setState(() {
        isLoading = true;
        error = null;
      });

      final result = await ApiHealthService.checkConnection();
      
      setState(() {
        healthData = result;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(),
              SizedBox(width: 16),
              Text('Checking API status...'),
            ],
          ),
        ),
      );
    }

    if (error != null) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.error, color: Colors.red),
                  SizedBox(width: 8),
                  Text('API Connection Error', style: TextStyle(fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 8),
              Text(error!, style: const TextStyle(color: Colors.red)),
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: _checkApiStatus,
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    if (healthData == null) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Text('No data available'),
        ),
      );
    }

    final status = healthData!['overall_status'] ?? 'unknown';
    final healthInfo = healthData!['health_data'] as Map<String, dynamic>?;

    Color statusColor;
    IconData statusIcon;
    String statusText;

    switch (status) {
      case 'fully_connected':
        statusColor = Colors.green;
        statusIcon = Icons.check_circle;
        statusText = 'Fully Connected';
        break;
      case 'partially_connected':
        statusColor = Colors.orange;
        statusIcon = Icons.warning;
        statusText = 'Partially Connected';
        break;
      case 'basic_connection':
        statusColor = Colors.yellow;
        statusIcon = Icons.info;
        statusText = 'Basic Connection';
        break;
      default:
        statusColor = Colors.red;
        statusIcon = Icons.error;
        statusText = 'Disconnected';
    }

    return Card(
      child: Container(
        constraints: const BoxConstraints(
          maxWidth: 300,
          maxHeight: 200,
        ),
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(statusIcon, color: statusColor, size: 16),
                  const SizedBox(width: 8),
                  Flexible(
                    child: Text(
                      'API: $statusText',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: statusColor,
                        fontSize: 12,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    onPressed: _checkApiStatus,
                    icon: const Icon(Icons.refresh, size: 16),
                    tooltip: 'Refresh Status',
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(
                      minWidth: 24,
                      minHeight: 24,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              
              // Connection details
              _buildStatusRow('Ping', healthData!['ping_success'] == true),
              _buildStatusRow('Health', healthData!['health_success'] == true),
              _buildStatusRow('AI Service', healthData!['ai_success'] == true),
              
              if (healthInfo != null) ...[
                const SizedBox(height: 8),
                const Divider(height: 1),
                const SizedBox(height: 4),
                
                // Server information (condensed)
                if (healthInfo['version'] != null)
                  Text(
                    'v${healthInfo['version']}',
                    style: const TextStyle(fontSize: 10, color: Colors.grey),
                  ),
                
                if (healthInfo['uptime'] != null)
                  Text(
                    'Up: ${TimeUtils.formatUptime(healthInfo['uptime'])}',
                    style: const TextStyle(fontSize: 10, color: Colors.grey),
                  ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusRow(String label, bool isSuccess) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 1.0),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isSuccess ? Icons.check : Icons.close,
            color: isSuccess ? Colors.green : Colors.red,
            size: 12,
          ),
          const SizedBox(width: 6),
          Text(
            label,
            style: const TextStyle(fontSize: 10),
          ),
        ],
      ),
    );
  }
}
