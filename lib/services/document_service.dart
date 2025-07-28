import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:typed_data';
import '../models/document.dart';
import '../utils/constants.dart';

// For web
import 'dart:html' as html;

/// Upload result with additional metadata
class UploadResultEnhanced extends UploadResult {
  final Map<String, dynamic>? metadata;
  final List<String>? warnings;
  final Map<String, dynamic>? processingStats;

  UploadResultEnhanced({
    required bool success,
    required String message,
    String? filename,
    String? documentId,
    int? fileSize,
    int? processedChunks,
    double? processingTime,
    this.metadata,
    this.warnings,
    this.processingStats,
  }) : super(
          success: success,
          message: message,
          filename: filename,
          documentId: documentId,
          fileSize: fileSize,
          processedChunks: processedChunks,
          processingTime: processingTime,
        );

  factory UploadResultEnhanced.fromJson(Map<String, dynamic> json) {
    return UploadResultEnhanced(
      success: json['upload_status'] == 'success' || json['success'] == true,
      message: json['message'] ?? json['upload_status'] ?? 'Unknown',
      filename: json['filename'],
      documentId: json['document_id'],
      fileSize: json['file_size'],
      processedChunks: json['processed_chunks'],
      processingTime: json['processing_time']?.toDouble(),
      metadata: json['metadata'],
      warnings: json['warnings'] != null ? List<String>.from(json['warnings']) : null,
      processingStats: json['processing_stats'],
    );
  }
}

/// Document info with enhanced metadata
class DocumentInfoEnhanced extends DocumentInfo {
  final Map<String, dynamic>? metadata;
  final double? processingTime;
  final List<String>? extractedTags;
  final Map<String, dynamic>? contentStats;

  DocumentInfoEnhanced({
    required String id,
    required String filename,
    required String fileType,
    required DateTime uploadDate,
    required int fileSize,
    int? chunkCount,
    required String status,
    this.metadata,
    this.processingTime,
    this.extractedTags,
    this.contentStats,
  }) : super(
          id: id,
          filename: filename,
          fileType: fileType,
          uploadDate: uploadDate,
          fileSize: fileSize,
          chunkCount: chunkCount,
          status: status,
        );

  factory DocumentInfoEnhanced.fromJson(Map<String, dynamic> json) {
    return DocumentInfoEnhanced(
      id: json['id'] ?? '',
      filename: json['filename'] ?? '',
      fileType: json['file_type'] ?? '',
      uploadDate: DateTime.parse(json['created_at'] ?? json['upload_date'] ?? DateTime.now().toIso8601String()),
      fileSize: json['file_size'] ?? 0,
      chunkCount: json['chunk_count'],
      status: json['processing_status'] ?? json['status'] ?? 'unknown',
      metadata: json['metadata'],
      processingTime: json['processing_time']?.toDouble(),
      extractedTags: json['extracted_tags'] != null ? List<String>.from(json['extracted_tags']) : null,
      contentStats: json['content_stats'],
    );
  }
}

/// Document Service for Flutter
/// 
/// Provides comprehensive document processing capabilities that integrate
/// with the enhanced backend PDF processing system featuring:
/// - Multi-library PDF extraction (pdfplumber, pypdf, PyPDF2)
/// - Semantic content tagging and structuring
/// - Document boundary detection and identification
/// - Advanced error handling and recovery
class DocumentService {
  static String get apiBaseUrl => AppConstants.apiBaseUrl;

  /// Upload document with enhanced processing capabilities
  /// 
  /// Features:
  /// - Multi-library PDF extraction (pdfplumber, pypdf, PyPDF2)
  /// - Excel multi-sheet processing (openpyxl, pandas, xlrd)
  /// - Enhanced text structuring with semantic tagging
  /// - Document identification and boundary markers
  /// - Comprehensive metadata extraction
  static Future<UploadResultEnhanced> uploadDocumentEnhanced(
    html.File file, {
    String? description,
    String userId = 'flutter_user',
  }) async {
    print('🚀 Enhanced document upload starting...');
    print('📄 File: ${file.name} (${file.size} bytes)');
    print('🏷️ Description: ${description ?? "No description"}');
    
    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$apiBaseUrl/api/v1/documents/upload'),
      );

      // Read file as bytes
      final bytes = await _readFileAsBytes(file);
      print('✅ File read: ${bytes.length} bytes');
      
      // Add file to request
      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          bytes,
          filename: file.name,
        ),
      );

      // Add enhanced parameters
      request.fields['user_id'] = userId;
      request.fields['enhanced_processing'] = 'true';
      request.fields['enable_semantic_tagging'] = 'true';
      request.fields['enable_document_identification'] = 'true';
      
      if (description != null) {
        request.fields['description'] = description;
      }

      print('📡 Sending enhanced upload request...');
      final response = await request.send();
      final responseBody = await response.stream.bytesToString();
      
      print('📊 Upload response status: ${response.statusCode}');
      print('📋 Response body preview: ${responseBody.substring(0, responseBody.length > 200 ? 200 : responseBody.length)}...');
      
      if (response.statusCode == 200) {
        final responseData = jsonDecode(responseBody);
        print('✅ Enhanced upload successful!');
        
        if (responseData['metadata'] != null) {
          print('🏷️ Extracted metadata: ${responseData['metadata']}');
        }
        
        if (responseData['processing_stats'] != null) {
          print('📊 Processing stats: ${responseData['processing_stats']}');
        }
        
        return UploadResultEnhanced.fromJson(responseData);
      } else {
        print('❌ Enhanced upload failed with status: ${response.statusCode}');
        return UploadResultEnhanced(
          success: false,
          message: 'Enhanced upload failed: ${response.statusCode}',
        );
      }
    } catch (e, stackTrace) {
      print('💥 Enhanced upload error: $e');
      print('📜 Stack trace: $stackTrace');
      return UploadResultEnhanced(
        success: false,
        message: 'Enhanced upload error: $e',
      );
    }
  }

  /// Get documents with enhanced metadata
  static Future<List<DocumentInfoEnhanced>> getDocumentsEnhanced({
    String userId = 'flutter_user',
    String? fileType,
    String? status,
    int? limit,
  }) async {
    try {
      final queryParams = <String, String>{
        'user_id': userId,
        'include_metadata': 'true',
        'include_stats': 'true',
      };
      
      if (fileType != null) queryParams['file_type'] = fileType;
      if (status != null) queryParams['status'] = status;
      if (limit != null) queryParams['limit'] = limit.toString();

      final uri = Uri.parse('$apiBaseUrl/api/v1/documents').replace(
        queryParameters: queryParams,
      );

      print('📡 Fetching enhanced documents from: $uri');
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        final documents = responseData['documents'] as List;
        
        return documents.map((doc) => DocumentInfoEnhanced.fromJson(doc)).toList();
      } else {
        print('❌ Failed to fetch enhanced documents: ${response.statusCode}');
        throw Exception('Failed to fetch enhanced documents: ${response.statusCode}');
      }
    } catch (e) {
      print('💥 Error fetching enhanced documents: $e');
      throw Exception('Error fetching enhanced documents: $e');
    }
  }

  /// Train model with enhanced document processing
  static Future<Map<String, dynamic>> trainModelEnhanced({
    String userId = 'flutter_user',
    List<String>? documentIds,
    bool enableAdvancedFeatures = true,
  }) async {
    try {
      final requestData = {
        'user_id': userId,
        'enhanced_training': true,
        'enable_semantic_analysis': enableAdvancedFeatures,
        'enable_document_classification': enableAdvancedFeatures,
        'enable_metadata_extraction': enableAdvancedFeatures,
      };

      if (documentIds != null && documentIds.isNotEmpty) {
        requestData['document_ids'] = documentIds;
      }

      print('🧠 Starting enhanced model training...');
      print('📊 Training parameters: $requestData');

      final response = await http.post(
        Uri.parse('$apiBaseUrl/api/v1/documents/train'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestData),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        print('✅ Enhanced training completed successfully!');
        
        if (responseData['training_metrics'] != null) {
          print('📊 Training metrics: ${responseData['training_metrics']}');
        }
        
        return responseData;
      } else {
        print('❌ Enhanced training failed: ${response.statusCode}');
        throw Exception('Enhanced training failed: ${response.statusCode}');
      }
    } catch (e) {
      print('💥 Enhanced training error: $e');
      throw Exception('Enhanced training error: $e');
    }
  }

  /// Search documents with enhanced filtering
  static Future<List<DocumentInfoEnhanced>> searchDocumentsEnhanced(
    String query, {
    String userId = 'flutter_user',
    List<String>? fileTypes,
    List<String>? tags,
    Map<String, dynamic>? metadataFilters,
    int limit = 20,
  }) async {
    try {
      final requestData = {
        'query': query,
        'user_id': userId,
        'limit': limit,
        'include_metadata': true,
        'include_stats': true,
        'enhanced_search': true,
      };

      if (fileTypes != null && fileTypes.isNotEmpty) {
        requestData['file_types'] = fileTypes;
      }
      
      if (tags != null && tags.isNotEmpty) {
        requestData['tags'] = tags;
      }
      
      if (metadataFilters != null && metadataFilters.isNotEmpty) {
        requestData['metadata_filters'] = metadataFilters;
      }

      print('🔍 Enhanced document search: $query');
      print('📊 Search parameters: $requestData');

      final response = await http.post(
        Uri.parse('$apiBaseUrl/api/v1/documents/search'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestData),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        final documents = responseData['documents'] as List;
        
        print('✅ Found ${documents.length} enhanced documents');
        return documents.map((doc) => DocumentInfoEnhanced.fromJson(doc)).toList();
      } else {
        print('❌ Enhanced search failed: ${response.statusCode}');
        throw Exception('Enhanced search failed: ${response.statusCode}');
      }
    } catch (e) {
      print('💥 Enhanced search error: $e');
      throw Exception('Enhanced search error: $e');
    }
  }

  /// Validate document format and content
  static Future<Map<String, dynamic>> validateDocumentEnhanced(html.File file) async {
    try {
      final fileExtension = file.name.split('.').last.toLowerCase();
      final supportedFormats = ['pdf', 'docx', 'txt', 'xlsx', 'xls', 'doc'];
      
      if (!supportedFormats.contains(fileExtension)) {
        return {
          'valid': false,
          'error': 'Unsupported file format: $fileExtension',
          'supported_formats': supportedFormats,
        };
      }

      // Additional validation for file size
      const maxFileSize = 50 * 1024 * 1024; // 50MB
      if (file.size > maxFileSize) {
        return {
          'valid': false,
          'error': 'File too large: ${(file.size / (1024 * 1024)).toStringAsFixed(1)}MB (max: 50MB)',
          'file_size': file.size,
          'max_size': maxFileSize,
        };
      }

      return {
        'valid': true,
        'file_type': fileExtension,
        'file_size': file.size,
        'file_name': file.name,
        'estimated_processing_time': _estimateProcessingTime(file.size, fileExtension),
      };
    } catch (e) {
      return {
        'valid': false,
        'error': 'Validation error: $e',
      };
    }
  }

  /// Get processing status for a document
  static Future<Map<String, dynamic>> getProcessingStatusEnhanced(String documentId) async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/api/v1/documents/$documentId/status?enhanced=true'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get processing status: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error getting processing status: $e');
    }
  }

  /// Delete document with enhanced cleanup
  static Future<bool> deleteDocumentEnhanced(String documentId) async {
    try {
      final response = await http.delete(
        Uri.parse('$apiBaseUrl/api/v1/documents/$documentId?enhanced_cleanup=true'),
      );

      return response.statusCode == 200;
    } catch (e) {
      print('💥 Error deleting document: $e');
      return false;
    }
  }

  // Helper methods
  static Future<Uint8List> _readFileAsBytes(html.File file) async {
    final reader = html.FileReader();
    reader.readAsArrayBuffer(file);
    await reader.onLoad.first;
    return Uint8List.fromList((reader.result as List<int>));
  }

  static double _estimateProcessingTime(int fileSize, String fileType) {
    // Estimate processing time based on file size and type
    double baseTime = fileSize / (1024 * 1024); // MB
    
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return baseTime * 2.0; // PDFs take longer due to complex processing
      case 'xlsx':
      case 'xls':
        return baseTime * 1.5; // Excel files with multiple sheets
      case 'docx':
      case 'doc':
        return baseTime * 1.2; // Word documents
      default:
        return baseTime;
    }
  }

  /// Get supported document formats
  static List<String> getSupportedFormats() {
    return ['pdf', 'docx', 'doc', 'txt', 'xlsx', 'xls'];
  }

  /// Get format-specific processing capabilities
  static Map<String, List<String>> getFormatCapabilities() {
    return {
      'pdf': [
        'Multi-library extraction (pdfplumber, pypdf, PyPDF2)',
        'Semantic content tagging',
        'Document boundary detection',
        'Metadata extraction',
        'Text structuring'
      ],
      'xlsx': [
        'Multi-sheet processing',
        'Cell formatting preservation',
        'Formula evaluation',
        'Chart and image extraction'
      ],
      'docx': [
        'Style preservation',
        'Table extraction',
        'Image and shape extraction',
        'Header/footer processing'
      ],
      'txt': [
        'Encoding detection',
        'Line-by-line processing',
        'Paragraph detection'
      ],
    };
  }
}
