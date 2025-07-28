import 'package:intl/intl.dart';

class TimeUtils {
  /// Format timestamp for Indian Standard Time display
  static String formatIndianTime(DateTime dateTime) {
    // Create a formatter for Indian timezone display
    final formatter = DateFormat('dd/MM/yyyy HH:mm:ss');
    return '${formatter.format(dateTime)} IST';
  }

  /// Format timestamp for chat messages
  static String formatChatTime(DateTime dateTime) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final messageDate = DateTime(dateTime.year, dateTime.month, dateTime.day);
    
    if (messageDate == today) {
      // Same day - show only time
      return DateFormat('HH:mm').format(dateTime);
    } else if (messageDate == today.subtract(const Duration(days: 1))) {
      // Yesterday
      return 'Yesterday ${DateFormat('HH:mm').format(dateTime)}';
    } else {
      // Older - show date and time
      return DateFormat('dd/MM HH:mm').format(dateTime);
    }
  }

  /// Format timestamp for detailed display with IST
  static String formatDetailedTime(DateTime dateTime) {
    return DateFormat('EEEE, MMMM dd, yyyy \'at\' HH:mm:ss').format(dateTime);
  }

  /// Parse API timestamp string to DateTime
  static DateTime? parseApiTimestamp(String? timestamp) {
    if (timestamp == null || timestamp.isEmpty) return null;
    
    try {
      return DateTime.parse(timestamp);
    } catch (e) {
      return null;
    }
  }

  /// Check if timestamp is today
  static bool isToday(DateTime dateTime) {
    final now = DateTime.now();
    return dateTime.year == now.year &&
           dateTime.month == now.month &&
           dateTime.day == now.day;
  }

  /// Get relative time string
  static String getRelativeTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else if (difference.inDays == 1) {
      return 'Yesterday';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return formatChatTime(dateTime);
    }
  }

  /// Create a human-readable uptime string
  static String formatUptime(double uptimeSeconds) {
    final hours = (uptimeSeconds / 3600).floor();
    final minutes = ((uptimeSeconds % 3600) / 60).floor();
    final seconds = (uptimeSeconds % 60).floor();
    
    if (hours > 0) {
      return '${hours}h ${minutes}m ${seconds}s';
    } else if (minutes > 0) {
      return '${minutes}m ${seconds}s';
    } else {
      return '${seconds}s';
    }
  }
}
