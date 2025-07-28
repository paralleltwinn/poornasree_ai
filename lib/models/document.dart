class DocumentInfo {
  final String id;
  final String filename;
  final String fileType;
  final DateTime uploadDate;
  final int fileSize;
  final int? chunkCount;
  final String status;

  DocumentInfo({
    required this.id,
    required this.filename,
    required this.fileType,
    required this.uploadDate,
    required this.fileSize,
    this.chunkCount,
    required this.status,
  });

  factory DocumentInfo.fromJson(Map<String, dynamic> json) {
    return DocumentInfo(
      id: json['id'] ?? '',
      filename: json['filename'] ?? '',
      fileType: json['file_type'] ?? '',
      uploadDate: DateTime.parse(json['created_at'] ?? json['upload_date'] ?? DateTime.now().toIso8601String()),
      fileSize: json['file_size'] ?? 0,
      chunkCount: json['chunk_count'],
      status: json['processing_status'] ?? json['status'] ?? 'unknown',
    );
  }

  String get fileSizeFormatted {
    if (fileSize < 1024) return '${fileSize}B';
    if (fileSize < 1024 * 1024) return '${(fileSize / 1024).toStringAsFixed(1)}KB';
    return '${(fileSize / (1024 * 1024)).toStringAsFixed(1)}MB';
  }
}

class UploadResult {
  final bool success;
  final String message;
  final String? filename;
  final String? documentId;
  final int? fileSize;
  final int? processedChunks;
  final double? processingTime;

  UploadResult({
    required this.success,
    required this.message,
    this.filename,
    this.documentId,
    this.fileSize,
    this.processedChunks,
    this.processingTime,
  });

  factory UploadResult.fromJson(Map<String, dynamic> json) {
    return UploadResult(
      success: json['upload_status'] == 'success',
      message: json['upload_status'] ?? 'Unknown',
      filename: json['filename'],
      processedChunks: json['processed_chunks'],
      processingTime: json['processing_time']?.toDouble(),
    );
  }
}
