import 'package:flutter/material.dart';
import '../models/service_guide.dart';
import '../services/api_service.dart';
import 'dart:html' as html;

class ServiceGuideScreen extends StatefulWidget {
  const ServiceGuideScreen({super.key});

  @override
  State<ServiceGuideScreen> createState() => _ServiceGuideScreenState();
}

class _ServiceGuideScreenState extends State<ServiceGuideScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  
  List<ServiceGuideEntry> _entries = [];
  ServiceGuideStats? _stats;
  bool _isLoading = false;
  String? _error;
  String _searchQuery = '';
  String? _selectedCategory;
  String? _selectedType;
  String? _selectedSheet;

  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadServiceGuideData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadServiceGuideData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Load stats and entries in parallel
      final futures = await Future.wait([
        ApiService.getServiceGuideStats(),
        ApiService.getServiceGuideEntries(),
      ]);

      final statsData = futures[0] as Map<String, dynamic>;
      final entriesData = futures[1] as List<Map<String, dynamic>>;

      setState(() {
        _stats = ServiceGuideStats.fromJson(statsData);
        _entries = entriesData.map((e) => ServiceGuideEntry.fromJson(e)).toList();
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _searchServiceGuide() async {
    if (_searchQuery.trim().isEmpty) {
      _loadServiceGuideData();
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final results = await ApiService.searchServiceGuide(_searchQuery);
      setState(() {
        _entries = results.map((e) => ServiceGuideEntry.fromJson(e)).toList();
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _uploadServiceGuide() async {
    final input = html.FileUploadInputElement()
      ..accept = '.xlsx,.xls'
      ..multiple = false;
    
    input.click();
    
    input.onChange.listen((e) async {
      final files = input.files;
      if (files != null && files.isNotEmpty) {
        await _trainServiceGuide(files.first);
      }
    });
  }

  Future<void> _trainServiceGuide(html.File file) async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final result = await ApiService.trainServiceGuide(file);
      final trainingResult = ServiceGuideTrainingResult.fromJson(result);

      if (trainingResult.success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              '✅ Training successful! ${trainingResult.entriesTrained} entries processed',
            ),
            backgroundColor: Colors.green,
          ),
        );
        _loadServiceGuideData(); // Reload data
      } else {
        throw Exception(trainingResult.error ?? 'Training failed');
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ Training failed: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Service Guide'),
        actions: [
          IconButton(
            onPressed: _uploadServiceGuide,
            icon: const Icon(Icons.upload_file),
            tooltip: 'Upload Excel Service Guide',
          ),
          IconButton(
            onPressed: _loadServiceGuideData,
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.list), text: 'Entries'),
            Tab(icon: Icon(Icons.search), text: 'Search'),
            Tab(icon: Icon(Icons.analytics), text: 'Statistics'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? _buildErrorWidget()
              : TabBarView(
                  controller: _tabController,
                  children: [
                    _buildEntriesTab(),
                    _buildSearchTab(),
                    _buildStatsTab(),
                  ],
                ),
    );
  }

  Widget _buildErrorWidget() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 64, color: Colors.red),
          const SizedBox(height: 16),
          Text(
            'Error Loading Service Guide',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              _error!,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loadServiceGuideData,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildEntriesTab() {
    if (_entries.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.description_outlined, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('No service guide entries found'),
            SizedBox(height: 8),
            Text('Upload an Excel file to get started'),
          ],
        ),
      );
    }

    return Column(
      children: [
        // Filters
        _buildFilters(),
        // Entries list
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(8),
            itemCount: _entries.length,
            itemBuilder: (context, index) {
              final entry = _entries[index];
              return _buildEntryCard(entry);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildFilters() {
    return Card(
      margin: const EdgeInsets.all(8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _selectedCategory,
                    decoration: const InputDecoration(
                      labelText: 'Category',
                      border: OutlineInputBorder(),
                    ),
                    items: _getUniqueCategories()
                        .map((cat) => DropdownMenuItem(
                              value: cat,
                              child: Text(cat),
                            ))
                        .toList(),
                    onChanged: (value) {
                      setState(() {
                        _selectedCategory = value;
                      });
                      _applyFilters();
                    },
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _selectedType,
                    decoration: const InputDecoration(
                      labelText: 'Type',
                      border: OutlineInputBorder(),
                    ),
                    items: _getUniqueTypes()
                        .map((type) => DropdownMenuItem(
                              value: type,
                              child: Text(type),
                            ))
                        .toList(),
                    onChanged: (value) {
                      setState(() {
                        _selectedType = value;
                      });
                      _applyFilters();
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _selectedSheet,
                    decoration: const InputDecoration(
                      labelText: 'Sheet',
                      border: OutlineInputBorder(),
                    ),
                    items: _getUniqueSheets()
                        .map((sheet) => DropdownMenuItem(
                              value: sheet,
                              child: Text(sheet),
                            ))
                        .toList(),
                    onChanged: (value) {
                      setState(() {
                        _selectedSheet = value;
                      });
                      _applyFilters();
                    },
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _clearFilters,
                  child: const Text('Clear'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSearchTab() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          TextField(
            controller: _searchController,
            decoration: InputDecoration(
              labelText: 'Search Service Guide',
              hintText: 'Enter keywords, procedures, or specifications...',
              border: const OutlineInputBorder(),
              suffixIcon: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    onPressed: () {
                      _searchController.clear();
                      setState(() {
                        _searchQuery = '';
                      });
                      _loadServiceGuideData();
                    },
                    icon: const Icon(Icons.clear),
                  ),
                  IconButton(
                    onPressed: () {
                      setState(() {
                        _searchQuery = _searchController.text;
                      });
                      _searchServiceGuide();
                    },
                    icon: const Icon(Icons.search),
                  ),
                ],
              ),
            ),
            onSubmitted: (value) {
              setState(() {
                _searchQuery = value;
              });
              _searchServiceGuide();
            },
          ),
          const SizedBox(height: 16),
          Expanded(
            child: _entries.isEmpty
                ? const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.search_off, size: 64, color: Colors.grey),
                        SizedBox(height: 16),
                        Text('No search results'),
                        Text('Try different keywords'),
                      ],
                    ),
                  )
                : ListView.builder(
                    itemCount: _entries.length,
                    itemBuilder: (context, index) {
                      return _buildEntryCard(_entries[index]);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsTab() {
    if (_stats == null) {
      return const Center(child: Text('No statistics available'));
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildStatsCard(
            'Total Entries',
            _stats!.totalEntries.toString(),
            Icons.description,
            Colors.blue,
          ),
          const SizedBox(height: 16),
          _buildStatsSection('By Type', _stats!.byType, Icons.category),
          const SizedBox(height: 16),
          _buildStatsSection('By Category', _stats!.byCategory, Icons.label),
          const SizedBox(height: 16),
          _buildStatsSection('By Sheet', _stats!.bySheet, Icons.table_chart),
        ],
      ),
    );
  }

  Widget _buildStatsCard(String title, String value, IconData icon, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(icon, size: 48, color: color),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                Text(
                  value,
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        color: color,
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsSection(String title, Map<String, int> data, IconData icon) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...data.entries.map((entry) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(entry.key),
                      Chip(
                        label: Text(entry.value.toString()),
                        backgroundColor: Theme.of(context).colorScheme.secondaryContainer,
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }

  Widget _buildEntryCard(ServiceGuideEntry entry) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
      child: ExpansionTile(
        leading: CircleAvatar(
          child: Text(entry.typeIcon),
          backgroundColor: Theme.of(context).colorScheme.secondaryContainer,
        ),
        title: Text(
          entry.displayTitle,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('${entry.categoryIcon} ${entry.category} • ${entry.type}'),
            Text('Sheet: ${entry.sheet} • Row: ${entry.row}'),
          ],
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (entry.description.isNotEmpty) ...[
                  Text(
                    'Description',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 4),
                  Text(entry.description),
                  const SizedBox(height: 12),
                ],
                if (entry.details.isNotEmpty) ...[
                  Text(
                    'Details',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 4),
                  Text(entry.details),
                  const SizedBox(height: 12),
                ],
                if (entry.keywords.isNotEmpty) ...[
                  Text(
                    'Keywords',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 4),
                  Wrap(
                    spacing: 4,
                    children: entry.keywords.take(10).map((keyword) => Chip(
                      label: Text(keyword),
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    )).toList(),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  List<String> _getUniqueCategories() {
    final categories = _entries.map((e) => e.category).toSet().toList();
    categories.sort();
    return ['All', ...categories];
  }

  List<String> _getUniqueTypes() {
    final types = _entries.map((e) => e.type).toSet().toList();
    types.sort();
    return ['All', ...types];
  }

  List<String> _getUniqueSheets() {
    final sheets = _entries.map((e) => e.sheet).toSet().toList();
    sheets.sort();
    return ['All', ...sheets];
  }

  void _applyFilters() {
    // This would filter the entries based on selected criteria
    // For now, we'll just reload the data with filters
    // In a real implementation, you'd call the API with filter parameters
    _loadServiceGuideData();
  }

  void _clearFilters() {
    setState(() {
      _selectedCategory = null;
      _selectedType = null;
      _selectedSheet = null;
    });
    _loadServiceGuideData();
  }
}
