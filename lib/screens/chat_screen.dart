import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/chat_message.dart';
import '../widgets/message_bubble.dart';
import '../widgets/chat_input.dart';
import '../widgets/example_questions.dart';
import '../widgets/ai_status_widget.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<ChatMessage> _messages = [];
  final ScrollController _scrollController = ScrollController();
  bool _isLoading = false;
  bool _showExamples = true;
  bool _showAIStatus = false;

  @override
  void initState() {
    super.initState();
    _addWelcomeMessage();
  }

  void _addWelcomeMessage() {
    setState(() {
      _messages.add(ChatMessage(
        text: "Hello! I'm your AI assistant powered **entirely** by **Google Gemini 2.5 Flash-Lite**. I can help you with:\n\n"
            "🔧 Machine operation procedures\n"
            "🛠️ Troubleshooting and diagnostics\n"
            "📋 Maintenance schedules\n"
            "⚠️ Safety guidelines\n"
            "📚 Document analysis and answers\n"
            "🤖 Advanced AI-powered technical support\n"
            "🚀 Complete Gemini 2.5 Flash-Lite integration\n\n"
            "**Every response is powered by Gemini 2.5 Flash-Lite** for the most accurate, comprehensive, and contextual technical guidance!\n\n"
            "Upload your manuals in the Dashboard and ask me anything for detailed, AI-enhanced guidance!",
        isUser: false,
        timestamp: DateTime.now(),
        metadata: {
          'ai_used': 'Google Gemini 2.5 Flash-Lite',
          'model_used': 'Gemini 2.5 Flash-Lite',
          'gemini_powered': true,
        },
      ));
    });
  }

  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    // Hide examples when user starts chatting
    if (_showExamples) {
      setState(() {
        _showExamples = false;
      });
    }

    // Add user message
    setState(() {
      _messages.add(ChatMessage(
        text: text,
        isUser: true,
        timestamp: DateTime.now(),
      ));
      _isLoading = true;
    });

    _scrollToBottom();

    try {
      // Call API
      final response = await ApiService.sendMessage(text);
      
      setState(() {
        _messages.add(response);
      });
    } catch (e) {
      _addErrorMessage('Sorry, I encountered an error. Please make sure the API is running and try again.');
    } finally {
      setState(() {
        _isLoading = false;
      });
      _scrollToBottom();
    }
  }

  void _addErrorMessage(String error) {
    setState(() {
      _messages.add(ChatMessage(
        text: error,
        isUser: false,
        timestamp: DateTime.now(),
      ));
    });
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _clearChat() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear Chat'),
        content: const Text('Are you sure you want to clear all messages?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              setState(() {
                _messages.clear();
                _showExamples = true;
              });
              _addWelcomeMessage();
              Navigator.pop(context);
            },
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }

  void _showApiStatus() async {
    final isOnline = await ApiService.pingApi();
    final status = await ApiService.getHealthStatus();
    
    if (mounted) {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('API Status'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    isOnline ? Icons.check_circle : Icons.error,
                    color: isOnline ? Colors.green : Colors.red,
                  ),
                  const SizedBox(width: 8),
                  Text(isOnline ? 'Online' : 'Offline'),
                ],
              ),
              const SizedBox(height: 8),
              if (status.isNotEmpty) ...[
                Text('Status: ${status['status'] ?? 'Unknown'}'),
                if (status['ai_model_status'] != null)
                  Text('AI Model: ${status['ai_model_status']}'),
                if (status['uptime_formatted'] != null)
                  Text('Uptime: ${status['uptime_formatted']}'),
              ],
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Close'),
            ),
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Assistant'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.smart_toy),
            onPressed: () {
              setState(() {
                _showAIStatus = !_showAIStatus;
              });
            },
            tooltip: 'AI Status',
          ),
          IconButton(
            icon: const Icon(Icons.info_outline),
            onPressed: _showApiStatus,
            tooltip: 'API Status',
          ),
          IconButton(
            icon: const Icon(Icons.clear_all),
            onPressed: _clearChat,
            tooltip: 'Clear Chat',
          ),
        ],
      ),
      body: Column(
        children: [
          // AI Status Widget (optional)
          if (_showAIStatus)
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: AIStatusWidget(),
            ),
          
          // Chat messages
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16.0),
              itemCount: _messages.length + (_showExamples ? 1 : 0),
              itemBuilder: (context, index) {
                if (_showExamples && index == _messages.length) {
                  return ExampleQuestions(
                    onQuestionTap: _sendMessage,
                  );
                }
                return MessageBubble(
                  message: _messages[index],
                );
              },
            ),
          ),
          
          // Loading indicator
          if (_isLoading)
            Container(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(
                        Theme.of(context).primaryColor,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    'Gemini AI is thinking...',
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
          
          // Input field
          ChatInput(
            onSendMessage: _sendMessage,
            enabled: !_isLoading,
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }
}
