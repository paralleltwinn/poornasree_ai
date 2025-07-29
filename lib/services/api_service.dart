import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:typed_data';
import '../models/document.dart';
import '../models/chat_message.dart';
import '../utils/constants.dart';
import '../utils/time_utils.dart';
import 'document_service.dart';

// For web
import 'dart:html' as html;

class ApiService {
  static String get apiBaseUrl => AppConstants.apiBaseUrl;

  /// Send chat message to API with enhanced Gemini integration
  static Future<ChatMessage> sendMessage(String message, {String userId = 'flutter_user'}) async {
    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/api/v1/chat'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'message': message,
          'user_id': userId,
          'session_id': 'flutter_session_${DateTime.now().millisecondsSinceEpoch}',
        }),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        // Parse the timestamp with timezone support (IST from API)
        DateTime timestamp;
        try {
          timestamp = TimeUtils.parseApiTimestamp(data['timestamp']) ?? DateTime.now();
        } catch (e) {
          timestamp = DateTime.now();
        }
        
        return ChatMessage(
          text: data['response'] ?? 'No response received',
          isUser: false,
          timestamp: timestamp,
          confidence: data['confidence']?.toDouble(),
          userId: userId,
          metadata: {
            'ai_used': data['ai_used'] ?? 'Google Gemini 2.5 Flash-Lite',
            'processing_time': data['processing_time']?.toDouble() ?? 0.0,
            'model_used': data['model_used'] ?? 'Gemini 2.5 Flash-Lite',
            'gemini_status': data['gemini_status'] ?? 'active',
            'gemini_powered': data['ai_used']?.toString().contains('Gemini') ?? true,
            'documents_searched': data['documents_searched'] ?? 0,
            'chunks_analyzed': data['chunks_analyzed'] ?? 0,
            'source_count': (data['source_documents'] as List?)?.length ?? 0,
          },
        );
      } else {
        final errorData = json.decode(response.body);
        throw Exception('API Error: ${errorData['detail'] ?? 'Unknown error'}');
      }
    } catch (e) {
      if (e.toString().contains('Connection refused') || 
          e.toString().contains('Failed host lookup')) {
        throw Exception('Cannot connect to server. Please ensure the API is running on $apiBaseUrl');
      }
      rethrow;
    }
  }

  /// Upload document file to the API
  static Future<UploadResult> uploadDocument(html.File file, {String? description}) async {
    print('🔄 Starting upload for file: ${file.name}');
    print('📂 File size: ${file.size} bytes');
    print('📝 Description: ${description ?? "No description"}');
    
    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$apiBaseUrl/api/v1/documents/upload'),
      );

      print('🌐 Upload URL: $apiBaseUrl/api/v1/documents/upload');

      // Read file as bytes
      final bytes = await _readFileAsBytes(file);
      print('✅ File read successfully: ${bytes.length} bytes');
      
      // Add file to request
      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          bytes,
          filename: file.name,
        ),
      );

      // Add description if provided
      if (description != null && description.isNotEmpty) {
        request.fields['description'] = description;
      }

      // Add user ID
      request.fields['user_id'] = 'flutter_user';

      print('📤 Sending request...');
      // Send request with timeout
      final streamedResponse = await request.send().timeout(const Duration(minutes: 5));
      final response = await http.Response.fromStream(streamedResponse);

      print('📨 Response status: ${response.statusCode}');
      print('📋 Response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('✅ Upload successful!');
        return UploadResult(
          success: true,
          message: data['message'] ?? 'Document uploaded successfully',
          documentId: data['document_id'],
          filename: data['filename'] ?? file.name,
          fileSize: data['file_size'] ?? bytes.length,
          processingTime: data['processing_time']?.toDouble(),
          processedChunks: data['chunk_count'],
        );
      } else {
        final errorData = json.decode(response.body);
        return UploadResult(
          success: false,
          message: errorData['detail'] ?? 'Upload failed',
        );
      }
    } catch (e) {
      return UploadResult(
        success: false,
        message: 'Upload error: ${e.toString()}',
      );
    }
  }

  static Future<List<String>> getSupportedFormats() async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/api/v1/documents/supported-formats'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<String>.from(data['formats'] ?? AppConstants.supportedFileTypes);
      } else {
        return AppConstants.supportedFileTypes;
      }
    } catch (e) {
      return AppConstants.supportedFileTypes;
    }
  }

  static Future<Map<String, dynamic>> getUploadStats() async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/api/v1/documents/stats'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {
          'total_documents': data['total_documents'] ?? 0,
          'total_size': data['total_size'] ?? 0,
          'total_size_mb': ((data['total_size'] ?? 0) / (1024 * 1024)).toStringAsFixed(2),
          'recent_uploads': data['recent_uploads'] ?? [],
          'last_upload': data['last_upload'],
        };
      } else {
        return {
          'total_documents': 0,
          'total_size': 0,
          'total_size_mb': '0.00',
          'recent_uploads': [],
          'last_upload': null,
        };
      }
    } catch (e) {
      return {
        'total_documents': 0,
        'total_size': 0,
        'total_size_mb': '0.00',
        'recent_uploads': [],
        'last_upload': null,
        'error': e.toString(),
      };
    }
  }

  static Future<List<Map<String, dynamic>>> searchDocuments(String query) async {
    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/api/v1/documents/search'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'query': query}),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['results'] ?? []);
      } else {
        return [];
      }
    } catch (e) {
      return [];
    }
  }

  static Future<Map<String, dynamic>> getHealthStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/health/detailed'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        // Parse timestamp for display
        if (data['timestamp'] != null) {
          try {
            data['timestamp_parsed'] = TimeUtils.parseApiTimestamp(data['timestamp']);
          } catch (e) {
            data['timestamp_parsed'] = DateTime.now();
          }
        }
        
        return data;
      } else {
        return {
          'status': 'unhealthy',
          'api_accessible': false,
          'timestamp_parsed': DateTime.now(),
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

  static Future<List<Map<String, dynamic>>> getChatExamples() async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/api/v1/chat/examples'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['examples'] ?? []);
      } else {
        return _getDefaultExamples();
      }
    } catch (e) {
      return _getDefaultExamples();
    }
  }

  /// Train documents manually (trigger reprocessing)
  static Future<Map<String, dynamic>> trainDocuments() async {
    try {
      print('DEBUG: Making POST request to $apiBaseUrl/api/v1/documents/train');
      final response = await http.post(
        Uri.parse('$apiBaseUrl/api/v1/documents/train'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'user_id': 'flutter_user'}),
      ).timeout(const Duration(minutes: 10));

      print('DEBUG: trainDocuments response status: ${response.statusCode}');
      print('DEBUG: trainDocuments response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final result = {
          'success': true,
          'message': data['message'] ?? 'Training completed successfully',
          'processed_documents': data['processed_documents'] ?? 0,
          'training_time': data['training_time']?.toDouble(),
        };
        print('DEBUG: trainDocuments success result: $result');
        return result;
      } else {
        final errorData = json.decode(response.body);
        final result = {
          'success': false,
          'message': errorData['detail'] ?? 'Training failed',
        };
        print('DEBUG: trainDocuments error result: $result');
        return result;
      }
    } catch (e) {
      final result = {
        'success': false,
        'message': 'Training error: ${e.toString()}',
      };
      print('DEBUG: trainDocuments exception result: $result');
      return result;
    }
  }

  /// Delete a document by ID
  static Future<Map<String, dynamic>> deleteDocument(String documentId) async {
    try {
      print('DEBUG: Making DELETE request to $apiBaseUrl/api/v1/documents/$documentId');
      final response = await http.delete(
        Uri.parse('$apiBaseUrl/api/v1/documents/$documentId'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 30));

      print('DEBUG: deleteDocument response status: ${response.statusCode}');
      print('DEBUG: deleteDocument response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final result = {
          'success': true,
          'message': data['message'] ?? 'Document deleted successfully',
          'document_id': documentId,
        };
        print('DEBUG: deleteDocument success result: $result');
        return result;
      } else {
        final errorData = json.decode(response.body);
        final result = {
          'success': false,
          'message': errorData['detail'] ?? 'Failed to delete document',
        };
        print('DEBUG: deleteDocument error result: $result');
        return result;
      }
    } catch (e) {
      final result = {
        'success': false,
        'message': 'Delete error: ${e.toString()}',
      };
      print('DEBUG: deleteDocument exception result: $result');
      return result;
    }
  }

  /// Get list of uploaded documents
  static Future<List<Map<String, dynamic>>> getDocuments() async {
    try {
      print('DEBUG: Making GET request to $apiBaseUrl/api/v1/documents');
      final response = await http.get(
        Uri.parse('$apiBaseUrl/api/v1/documents'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 15));

      print('DEBUG: getDocuments response status: ${response.statusCode}');
      print('DEBUG: getDocuments response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final documents = List<Map<String, dynamic>>.from(data['documents'] ?? []);
        print('DEBUG: Parsed ${documents.length} documents');
        return documents;
      } else {
        print('DEBUG: getDocuments failed with status ${response.statusCode}');
        return [];
      }
    } catch (e) {
      print('DEBUG: getDocuments error: $e');
      return [];
    }
  }

  /// Helper method to read file as bytes (web-specific)
  static Future<Uint8List> _readFileAsBytes(html.File file) async {
    final reader = html.FileReader();
    reader.readAsArrayBuffer(file);
    await reader.onLoad.first;
    return reader.result as Uint8List;
  }

  /// Default chat examples if API is not available
  static List<Map<String, dynamic>> _getDefaultExamples() {
    return [
      {'text': 'How do I start the CNC machine?', 'category': 'operation'},
      {'text': 'What safety precautions should I take?', 'category': 'safety'},
      {'text': 'How do I maintain my machine?', 'category': 'maintenance'},
      {'text': 'What should I do if the machine stops?', 'category': 'troubleshooting'},
      {'text': 'How often should I clean the equipment?', 'category': 'maintenance'},
    ];
  }

  /// Clear all training data (documents and AI knowledge)
  static Future<Map<String, dynamic>> clearAllTrainingData() async {
    try {
      print('DEBUG: Making DELETE request to $apiBaseUrl/api/v1/documents/clear?confirm=true&user_id=flutter_user');
      final response = await http.delete(
        Uri.parse('$apiBaseUrl/api/v1/documents/clear?confirm=true&user_id=flutter_user'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 30));

      print('DEBUG: clearAllTrainingData response status: ${response.statusCode}');
      print('DEBUG: clearAllTrainingData response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final result = {
          'success': true,
          'message': data['message'] ?? 'All training data cleared successfully',
          'deleted_count': data['database']?['deleted_count'] ?? 0,
          'ai_cleared': data['ai_service']?['cleared_documents'] ?? 0,
        };
        print('DEBUG: clearAllTrainingData success result: $result');
        return result;
      } else {
        final errorData = json.decode(response.body);
        final result = {
          'success': false,
          'message': errorData['detail'] ?? 'Failed to clear training data',
        };
        print('DEBUG: clearAllTrainingData error result: $result');
        return result;
      }
    } catch (e) {
      final result = {
        'success': false,
        'message': 'Clear operation error: ${e.toString()}',
      };
      print('DEBUG: clearAllTrainingData exception result: $result');
      return result;
    }
  }

  // ===============================
  // ENHANCED DOCUMENT METHODS
  // ===============================
  
  /// Upload document with enhanced processing capabilities
  /// 
  /// This method leverages the enhanced backend PDF processing system that includes:
  /// - Multi-library PDF extraction (pdfplumber, pypdf, PyPDF2)
  /// - Semantic content tagging and structuring  
  /// - Document boundary detection and identification
  /// - Advanced error handling and recovery
  static Future<UploadResultEnhanced> uploadDocumentEnhanced(
    html.File file, {
    String? description,
    String userId = 'flutter_user',
  }) async {
    return await DocumentService.uploadDocumentEnhanced(
      file,
      description: description,
      userId: userId,
    );
  }
  
  /// Get documents with enhanced metadata and processing information
  static Future<List<DocumentInfoEnhanced>> getDocumentsEnhanced({
    String userId = 'flutter_user',
    String? fileType,
    String? status,
    int? limit,
  }) async {
    return await DocumentService.getDocumentsEnhanced(
      userId: userId,
      fileType: fileType,
      status: status,
      limit: limit,
    );
  }
  
  /// Train model with enhanced document processing and semantic analysis
  static Future<Map<String, dynamic>> trainModelEnhanced({
    String userId = 'flutter_user',
    List<String>? documentIds,
    bool enableAdvancedFeatures = true,
  }) async {
    return await DocumentService.trainModelEnhanced(
      userId: userId,
      documentIds: documentIds,
      enableAdvancedFeatures: enableAdvancedFeatures,
    );
  }
  
  /// Search documents with enhanced filtering and metadata support
  static Future<List<DocumentInfoEnhanced>> searchDocumentsEnhanced(
    String query, {
    String userId = 'flutter_user',
    List<String>? fileTypes,
    List<String>? tags,
    Map<String, dynamic>? metadataFilters,
    int limit = 20,
  }) async {
    return await DocumentService.searchDocumentsEnhanced(
      query,
      userId: userId,
      fileTypes: fileTypes,
      tags: tags,
      metadataFilters: metadataFilters,
      limit: limit,
    );
  }
  
  /// Validate document format and content with enhanced capabilities
  static Future<Map<String, dynamic>> validateDocumentEnhanced(html.File file) async {
    return await DocumentService.validateDocumentEnhanced(file);
  }
  
  /// Get processing status for a document with enhanced details
  static Future<Map<String, dynamic>> getProcessingStatusEnhanced(String documentId) async {
    return await DocumentService.getProcessingStatusEnhanced(documentId);
  }
  
  /// Delete document with enhanced cleanup
  static Future<bool> deleteDocumentEnhanced(String documentId) async {
    return await DocumentService.deleteDocumentEnhanced(documentId);
  }
  
  /// Get supported document formats for enhanced processing
  static List<String> getSupportedFormatsEnhanced() {
    return DocumentService.getSupportedFormats();
  }
  
  /// Get AI service status including Gemini integration
  static Future<Map<String, dynamic>> getAIStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/api/v1/ai/status'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get AI status: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error getting AI status: $e');
    }
  }
  
  /// Get detailed AI model information
  static Future<Map<String, dynamic>> getAIModelInfo() async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/api/v1/ai/model-info'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get AI model info: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error getting AI model info: $e');
    }
  }
  
  /// Test AI connectivity and response quality
  static Future<Map<String, dynamic>> testAIConnection() async {
    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/api/v1/ai/test'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'test_message': 'Hello, this is a connectivity test from Flutter app.',
        }),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('AI test failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error testing AI connection: $e');
    }
  }
  
  /// Get format-specific processing capabilities
  static Map<String, List<String>> getFormatCapabilities() {
    return DocumentService.getFormatCapabilities();
  }

  /// Train Excel file as service guide
  static Future<Map<String, dynamic>> trainServiceGuide(html.File file) async {
    try {
      print('🔄 Training service guide: ${file.name}');
      
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$apiBaseUrl/api/v1/service-guide/train-service-guide'),
      );

      // Read file as bytes
      final bytes = await _readFileAsBytes(file);
      
      // Add file to request
      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          bytes,
          filename: file.name,
        ),
      );

      request.fields['user_id'] = 'flutter_user';
      request.fields['training_type'] = 'service_guide';

      final response = await request.send().timeout(const Duration(minutes: 5));
      final responseString = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return json.decode(responseString);
      } else {
        final errorData = json.decode(responseString);
        throw Exception('Training failed: ${errorData['detail'] ?? 'Unknown error'}');
      }
    } catch (e) {
      throw Exception('Error training service guide: $e');
    }
  }

  /// Get service guide entries
  static Future<List<Map<String, dynamic>>> getServiceGuideEntries({
    String? category,
    String? type,
    String? sheet,
  }) async {
    try {
      final queryParams = <String, String>{};
      if (category != null) queryParams['category'] = category;
      if (type != null) queryParams['type'] = type;
      if (sheet != null) queryParams['sheet'] = sheet;
      
      final uri = Uri.parse('$apiBaseUrl/api/v1/service-guide/entries')
          .replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['entries'] ?? []);
      } else {
        throw Exception('Failed to get service guide entries: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error getting service guide entries: $e');
    }
  }

  /// Search service guide
  static Future<List<Map<String, dynamic>>> searchServiceGuide(String query) async {
    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/api/v1/service-guide/search'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'query': query,
          'limit': 20,
        }),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['results'] ?? []);
      } else {
        throw Exception('Search failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error searching service guide: $e');
    }
  }

  /// Get service guide statistics
  static Future<Map<String, dynamic>> getServiceGuideStats() async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/api/v1/service-guide/stats'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get stats: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error getting service guide stats: $e');
    }
  }
}
