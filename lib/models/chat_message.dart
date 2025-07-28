class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final String? source;
  final double? confidence;
  final String? userId;

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.source,
    this.confidence,
    this.userId,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      text: json['text'] ?? '',
      isUser: json['isUser'] ?? false,
      timestamp: DateTime.parse(json['timestamp']),
      source: json['source'],
      confidence: json['confidence']?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'text': text,
      'isUser': isUser,
      'timestamp': timestamp.toIso8601String(),
      'source': source,
      'confidence': confidence,
    };
  }
}
