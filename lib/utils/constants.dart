class AppConstants {
  // API Configuration
  static const String localApiUrl = "http://localhost:8000";
  static const String productionApiUrl = "https://your-api-domain.com"; // Update this when deployed
  
  // Use this to switch between environments
  static const bool isProduction = false;
  
  static String get apiBaseUrl => isProduction ? productionApiUrl : localApiUrl;
  
  // App Information
  static const String appName = "Poornasree AI";
  static const String appDescription = "AI-powered assistant for machine manuals with Google Gemini 2.5 Flash-Lite";
  static const String version = "2.0.0";
  static const String aiModel = "Google Gemini 2.5 Flash-Lite";
  
  // UI Constants
  static const double defaultPadding = 16.0;
  static const double defaultBorderRadius = 8.0;
  static const double messageBorderRadius = 18.0;
  
  // File Upload Limits
  static const int maxFileSize = 10 * 1024 * 1024; // 10MB
  static const List<String> supportedFileTypes = ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls'];
  
  // Chat Configuration
  static const int maxMessageLength = 1000;
  static const int maxChatHistory = 100;
  
  // Colors
  static const primaryColor = 0xFF2196F3;
  static const secondaryColor = 0xFF03DAC6;
  static const errorColor = 0xFFB00020;
  static const successColor = 0xFF4CAF50;
  static const geminiColor = 0xFF4285F4; // Google Blue
}
