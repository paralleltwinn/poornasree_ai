class ServiceGuideEntry {
  final String id;
  final String title;
  final String type;
  final String category;
  final String sheet;
  final int row;
  final String description;
  final String details;
  final List<String> keywords;
  final String searchableContent;
  final Map<String, dynamic> rawData;
  final DateTime? createdAt;

  const ServiceGuideEntry({
    required this.id,
    required this.title,
    required this.type,
    required this.category,
    required this.sheet,
    required this.row,
    required this.description,
    required this.details,
    required this.keywords,
    required this.searchableContent,
    required this.rawData,
    this.createdAt,
  });

  factory ServiceGuideEntry.fromJson(Map<String, dynamic> json) {
    return ServiceGuideEntry(
      id: json['id'] ?? '',
      title: json['title'] ?? 'Untitled',
      type: json['type'] ?? 'general',
      category: json['category'] ?? 'general',
      sheet: json['sheet'] ?? '',
      row: json['row'] ?? 0,
      description: json['description'] ?? '',
      details: json['details'] ?? '',
      keywords: List<String>.from(json['keywords'] ?? []),
      searchableContent: json['searchable_content'] ?? '',
      rawData: Map<String, dynamic>.from(json['raw_data'] ?? {}),
      createdAt: json['created_at'] != null 
          ? DateTime.tryParse(json['created_at']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'type': type,
      'category': category,
      'sheet': sheet,
      'row': row,
      'description': description,
      'details': details,
      'keywords': keywords,
      'searchable_content': searchableContent,
      'raw_data': rawData,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  // Helper getters for UI display
  String get displayTitle => title.isNotEmpty ? title : 'Entry $row';
  
  String get typeIcon {
    switch (type.toLowerCase()) {
      case 'specification':
        return '📊';
      case 'maintenance':
        return '🔧';
      case 'tool':
        return '🛠️';
      case 'troubleshooting':
        return '🔍';
      case 'safety':
        return '⚠️';
      default:
        return '📋';
    }
  }

  String get categoryIcon {
    switch (category.toLowerCase()) {
      case 'specification':
        return '📐';
      case 'maintenance':
        return '🔧';
      case 'operation':
        return '▶️';
      case 'safety':
        return '🛡️';
      case 'troubleshooting':
        return '🔍';
      default:
        return '📄';
    }
  }
}

class ServiceGuideStats {
  final int totalEntries;
  final Map<String, int> byType;
  final Map<String, int> byCategory;
  final Map<String, int> bySheet;
  final DateTime? lastUpdated;

  const ServiceGuideStats({
    required this.totalEntries,
    required this.byType,
    required this.byCategory,
    required this.bySheet,
    this.lastUpdated,
  });

  factory ServiceGuideStats.fromJson(Map<String, dynamic> json) {
    return ServiceGuideStats(
      totalEntries: json['total_entries'] ?? 0,
      byType: Map<String, int>.from(json['by_type'] ?? {}),
      byCategory: Map<String, int>.from(json['by_category'] ?? {}),
      bySheet: Map<String, int>.from(json['by_sheet'] ?? {}),
      lastUpdated: json['last_updated'] != null 
          ? DateTime.tryParse(json['last_updated']) 
          : null,
    );
  }
}

class ServiceGuideTrainingResult {
  final bool success;
  final String? error;
  final int entriesTrained;
  final int knowledgeBaseEntries;
  final String file;
  final Map<String, int>? trainingStats;
  final List<ServiceGuideEntry>? sampleEntries;

  const ServiceGuideTrainingResult({
    required this.success,
    this.error,
    required this.entriesTrained,
    required this.knowledgeBaseEntries,
    required this.file,
    this.trainingStats,
    this.sampleEntries,
  });

  factory ServiceGuideTrainingResult.fromJson(Map<String, dynamic> json) {
    return ServiceGuideTrainingResult(
      success: json['success'] ?? false,
      error: json['error'],
      entriesTrained: json['entries_trained'] ?? 0,
      knowledgeBaseEntries: json['knowledge_base_entries'] ?? 0,
      file: json['file'] ?? '',
      trainingStats: json['training_stats'] != null 
          ? Map<String, int>.from(json['training_stats']) 
          : null,
      sampleEntries: json['sample_entries'] != null 
          ? (json['sample_entries'] as List)
              .map((e) => ServiceGuideEntry.fromJson(e))
              .toList()
          : null,
    );
  }
}
