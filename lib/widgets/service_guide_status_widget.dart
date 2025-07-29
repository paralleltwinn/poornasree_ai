import 'package:flutter/material.dart';
import '../models/service_guide.dart';
import '../services/api_service.dart';

class ServiceGuideStatusWidget extends StatefulWidget {
  const ServiceGuideStatusWidget({super.key});

  @override
  State<ServiceGuideStatusWidget> createState() => _ServiceGuideStatusWidgetState();
}

class _ServiceGuideStatusWidgetState extends State<ServiceGuideStatusWidget> {
  ServiceGuideStats? _stats;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  Future<void> _loadStats() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final statsData = await ApiService.getServiceGuideStats();
      setState(() {
        _stats = ServiceGuideStats.fromJson(statsData);
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.description, color: Colors.blue),
                const SizedBox(width: 8),
                Text(
                  'Service Guide Status',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                IconButton(
                  onPressed: _loadStats,
                  icon: const Icon(Icons.refresh),
                  tooltip: 'Refresh',
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (_isLoading)
              const Center(child: CircularProgressIndicator())
            else if (_error != null)
              Column(
                children: [
                  const Icon(Icons.error_outline, color: Colors.red, size: 32),
                  const SizedBox(height: 8),
                  Text(
                    'Failed to load service guide stats',
                    style: TextStyle(color: Colors.red[700]),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _error!,
                    style: Theme.of(context).textTheme.bodySmall,
                    textAlign: TextAlign.center,
                  ),
                ],
              )
            else if (_stats != null)
              _buildStatsContent()
            else
              const Text('No service guide data available'),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsContent() {
    return Column(
      children: [
        // Total entries
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.primaryContainer,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            children: [
              const Icon(Icons.format_list_numbered, size: 32),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Total Entries',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  Text(
                    _stats!.totalEntries.toString(),
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        
        // Categories breakdown
        if (_stats!.byCategory.isNotEmpty) ...[
          Text(
            'By Category',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          ..._stats!.byCategory.entries.take(5).map((entry) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  _getCategoryIcon(entry.key) + ' ' + entry.key,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.secondaryContainer,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    entry.value.toString(),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          )),
          const SizedBox(height: 16),
        ],
        
        // Types breakdown
        if (_stats!.byType.isNotEmpty) ...[
          Text(
            'By Type',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          ..._stats!.byType.entries.take(4).map((entry) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  _getTypeIcon(entry.key) + ' ' + entry.key,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.tertiaryContainer,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    entry.value.toString(),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          )),
        ],
        
        // Last updated
        if (_stats!.lastUpdated != null) ...[
          const SizedBox(height: 16),
          Row(
            children: [
              const Icon(Icons.update, size: 16, color: Colors.grey),
              const SizedBox(width: 4),
              Text(
                'Updated: ${_formatDateTime(_stats!.lastUpdated!)}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }

  String _getCategoryIcon(String category) {
    switch (category.toLowerCase()) {
      case 'specification':
        return '📐';
      case 'maintenance':
        return '🔧';
      case 'operation':
        return '▶️';
      case 'safety':
        return '🛡️';
      case 'troubleshooting':
        return '🔍';
      default:
        return '📄';
    }
  }

  String _getTypeIcon(String type) {
    switch (type.toLowerCase()) {
      case 'specification':
        return '📊';
      case 'maintenance':
        return '🔧';
      case 'tool':
        return '🛠️';
      case 'troubleshooting':
        return '🔍';
      case 'safety':
        return '⚠️';
      default:
        return '📋';
    }
  }

  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }
}
