import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import '../utils/time_utils.dart';

class MessageBubble extends StatelessWidget {
  final ChatMessage message;

  const MessageBubble({
    super.key,
    required this.message,
  });

  @override
  Widget build(BuildContext context) {
    // Enhanced Gemini detection from multiple metadata sources
    final isGeminiPowered = _isGeminiPowered();
        
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Column(
        crossAxisAlignment: message.isUser 
            ? CrossAxisAlignment.end 
            : CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: message.isUser 
                ? MainAxisAlignment.end 
                : MainAxisAlignment.start,
            children: [
              // AI Avatar for non-user messages
              if (!message.isUser) ...[
                CircleAvatar(
                  backgroundColor: isGeminiPowered
                      ? const Color(0xFF9C27B0) // Gemini purple
                      : Theme.of(context).primaryColor,
                  radius: 16,
                  child: Icon(
                    isGeminiPowered
                        ? Icons.auto_awesome // Sparkle for Gemini 2.5 Flash-Lite
                        : Icons.smart_toy, 
                    size: 18, 
                    color: Colors.white
                  ),
                ),
                const SizedBox(width: 8),
              ],
              
              // Message bubble
              Flexible(
                child: Container(
                  constraints: BoxConstraints(
                    maxWidth: MediaQuery.of(context).size.width * 0.75,
                  ),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16.0,
                    vertical: 12.0,
                  ),
                  decoration: BoxDecoration(
                    color: message.isUser
                        ? Theme.of(context).primaryColor
                        : Theme.of(context).cardColor,
                    borderRadius: BorderRadius.circular(20.0),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Message text
                      Text(
                        message.text,
                        style: TextStyle(
                          color: message.isUser 
                              ? Colors.white 
                              : Theme.of(context).textTheme.bodyLarge?.color,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 8),
                      
                      // Metadata row
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          // Timestamp
                          Text(
                            _formatTime(message.timestamp),
                            style: TextStyle(
                              color: message.isUser 
                                  ? Colors.white70 
                                  : Theme.of(context).textTheme.bodySmall?.color,
                              fontSize: 12,
                            ),
                          ),
                          
                          // AI model indicator for AI responses
                          if (!message.isUser) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: isGeminiPowered
                                    ? const Color(0xFF9C27B0)
                                    : Colors.blue.withOpacity(0.7),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    isGeminiPowered
                                        ? Icons.auto_awesome
                                        : Icons.memory,
                                    size: 10,
                                    color: Colors.white,
                                  ),
                                  const SizedBox(width: 2),
                                  Text(
                                    isGeminiPowered
                                        ? 'Gemini 2.5 Flash-Lite' 
                                        : 'AI',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 9,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                          
                          // Confidence indicator
                          if (!message.isUser && message.confidence != null) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: _getConfidenceColor(message.confidence!),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Text(
                                '${(message.confidence! * 100).toInt()}%',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                          
                          // Processing time indicator
                          if (!message.isUser && 
                              message.metadata != null && 
                              message.metadata!['processing_time'] != null) ...[
                            const SizedBox(width: 4),
                            Tooltip(
                              message: 'Processing time: ${message.metadata!['processing_time']}s',
                              child: Icon(
                                Icons.timer_outlined,
                                size: 12,
                                color: message.isUser 
                                    ? Colors.white70 
                                    : Theme.of(context).textTheme.bodySmall?.color,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              
              // User avatar
              if (message.isUser) ...[
                const SizedBox(width: 8),
                CircleAvatar(
                  backgroundColor: Colors.grey[300],
                  radius: 16,
                  child: const Icon(Icons.person, size: 18, color: Colors.grey),
                ),
              ],
            ],
          ),
          
          // Gemini 2.5 Flash-Lite branding footer for AI messages
          if (!message.isUser && isGeminiPowered) ...[
            const SizedBox(height: 4),
            Padding(
              padding: EdgeInsets.only(
                left: message.isUser ? 0 : 40, // Align with message bubble
                right: message.isUser ? 40 : 0,
              ),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: const Color(0xFF9C27B0).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: const Color(0xFF9C27B0).withOpacity(0.3),
                    width: 1,
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.auto_awesome,
                      size: 11,
                      color: const Color(0xFF9C27B0),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Powered by Google Gemini 2.5 Flash-Lite',
                      style: TextStyle(
                        fontSize: 9,
                        color: const Color(0xFF9C27B0),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  /// Enhanced Gemini detection from multiple metadata sources
  bool _isGeminiPowered() {
    if (message.metadata == null) return false;
    
    // Check various metadata fields for Gemini indicators
    final metadata = message.metadata!;
    
    // Check explicit gemini_powered flag
    if (metadata['gemini_powered'] == true) return true;
    
    // Check ai_used field
    final aiUsed = metadata['ai_used']?.toString().toLowerCase() ?? '';
    if (aiUsed.contains('gemini')) return true;
    
    // Check model_used field
    final modelUsed = metadata['model_used']?.toString().toLowerCase() ?? '';
    if (modelUsed.contains('gemini')) return true;
    
    // Check gemini_status field
    final geminiStatus = metadata['gemini_status']?.toString().toLowerCase() ?? '';
    if (geminiStatus == 'active' || geminiStatus == 'success') return true;
    
    return false;
  }

  String _formatTime(DateTime dateTime) {
    return TimeUtils.formatChatTime(dateTime);
  }

  Color _getConfidenceColor(double confidence) {
    if (confidence >= 0.8) return Colors.green;
    if (confidence >= 0.6) return Colors.orange;
    return Colors.red;
  }
}
