import 'package:flutter/material.dart';

class ChatInput extends StatefulWidget {
  final Function(String) onSendMessage;
  final bool enabled;

  const ChatInput({
    super.key,
    required this.onSendMessage,
    this.enabled = true,
  });

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();

  void _sendMessage() {
    final text = _controller.text.trim();
    if (text.isNotEmpty && widget.enabled) {
      widget.onSendMessage(text);
      _controller.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            spreadRadius: 1,
            blurRadius: 3,
            offset: const Offset(0, -1),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _controller,
                focusNode: _focusNode,
                decoration: InputDecoration(
                  hintText: widget.enabled 
                      ? 'Ask about your machine manual...' 
                      : 'Please wait...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(25),
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 20.0,
                    vertical: 12.0,
                  ),
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.emoji_emotions_outlined),
                    onPressed: () {
                      // You can add emoji picker here if needed
                    },
                  ),
                ),
                onSubmitted: widget.enabled ? (_) => _sendMessage() : null,
                enabled: widget.enabled,
                maxLines: null,
                textCapitalization: TextCapitalization.sentences,
                keyboardType: TextInputType.multiline,
                textInputAction: TextInputAction.send,
              ),
            ),
            const SizedBox(width: 8),
            FloatingActionButton(
              onPressed: widget.enabled ? _sendMessage : null,
              mini: true,
              backgroundColor: widget.enabled 
                  ? Theme.of(context).primaryColor 
                  : Colors.grey,
              child: Icon(
                Icons.send,
                color: Colors.white,
                size: 20,
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }
}
