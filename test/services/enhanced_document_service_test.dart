import 'package:flutter_test/flutter_test.dart';
import 'package:poornasree_ai/services/document_service.dart';

void main() {
  group('Enhanced Document Service Tests', () {
    
    test('Should provide supported formats', () {
      final formats = DocumentService.getSupportedFormats();
      expect(formats, isNotEmpty);
      expect(formats, contains('pdf'));
      expect(formats, contains('docx'));
      expect(formats, contains('xlsx'));
    });

    test('Should provide format capabilities', () {
      final capabilities = DocumentService.getFormatCapabilities();
      expect(capabilities, isNotEmpty);
      expect(capabilities['pdf'], isNotNull);
      expect(capabilities['pdf'], contains('Multi-library extraction (pdfplumber, pypdf, PyPDF2)'));
      expect(capabilities['pdf'], contains('Semantic content tagging'));
    });

    test('Should provide format capabilities with PDF enhancements', () {
      final capabilities = DocumentService.getFormatCapabilities();
      expect(capabilities, isNotEmpty);
      expect(capabilities['pdf'], isNotNull);
      expect(capabilities['pdf'], contains('Multi-library extraction (pdfplumber, pypdf, PyPDF2)'));
      expect(capabilities['pdf'], contains('Semantic content tagging'));
      expect(capabilities['xlsx'], contains('Multi-sheet processing'));
      expect(capabilities['docx'], contains('Style preservation'));
    });

    test('Enhanced classes should extend base classes properly', () {
      final uploadResult = UploadResultEnhanced(
        success: true,
        message: 'Test upload',
        metadata: {'test': 'data'},
        warnings: ['test warning'],
      );
      
      expect(uploadResult.success, isTrue);
      expect(uploadResult.message, equals('Test upload'));
      expect(uploadResult.metadata, isNotNull);
      expect(uploadResult.warnings, isNotEmpty);
    });

    test('Enhanced document info should extend base properly', () {
      final docInfo = DocumentInfoEnhanced(
        id: 'test-id',
        filename: 'test.pdf',
        fileType: 'pdf',
        uploadDate: DateTime.now(),
        fileSize: 1024,
        status: 'processed',
        metadata: {'pages': 10},
        extractedTags: ['SPECIFICATION', 'ERROR_CODE'],
      );
      
      expect(docInfo.id, equals('test-id'));
      expect(docInfo.filename, equals('test.pdf'));
      expect(docInfo.metadata, isNotNull);
      expect(docInfo.extractedTags, isNotEmpty);
    });
  });
}
