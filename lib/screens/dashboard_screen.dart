import 'package:flutter/material.dart';
import 'dart:html' as html;
import '../services/api_service.dart';
import '../services/document_service.dart';
import '../widgets/api_status_widget.dart';
import '../widgets/ai_status_widget.dart';
import '../widgets/service_guide_status_widget.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<DocumentInfoEnhanced> _documents = [];
  Map<String, dynamic> _stats = {};
  bool _isLoading = true;
  bool _isUploading = false;
  bool _isTraining = false;
  bool _isClearing = false;
  bool _isDeleting = false;
  List<String> _supportedFormats = [];
  Set<String> _selectedDocuments = <String>{};
  bool _isSelectionMode = false;

  @override
  void initState() {
    super.initState();
    _supportedFormats = DocumentService.getSupportedFormats();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final documents = await ApiService.getDocumentsEnhanced();
      final stats = await ApiService.getUploadStats();
      
      setState(() {
        _documents = documents;
        _stats = stats;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading data: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _uploadFiles() async {
    if (_isUploading) return;

    final input = html.FileUploadInputElement();
    // Set accepted file types based on enhanced service capabilities
    if (_supportedFormats.isNotEmpty) {
      input.accept = _supportedFormats.map((format) => '.$format').join(',');
    } else {
      input.accept = '.pdf,.doc,.docx,.txt,.xlsx,.xls';
    }
    input.multiple = true;
    input.click();

    await input.onChange.first;
    final files = input.files;
    
    if (files == null || files.isEmpty) return;

    setState(() {
      _isUploading = true;
    });

    try {
      for (final file in files) {
        // Validate the file first
        final validation = await ApiService.validateDocumentEnhanced(file);
        
        if (!validation['valid']) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('${file.name}: ${validation['error']}'),
                backgroundColor: Colors.red,
              ),
            );
          }
          continue;
        }

        // Upload with enhanced processing
        final response = await ApiService.uploadDocumentEnhanced(file);
        
        if (response.success) {
          if (mounted) {
            String message = '${file.name} uploaded successfully';
            if (response.processingTime != null) {
              message += ' (${response.processingTime!.toStringAsFixed(1)}s)';
            }
            if (response.processedChunks != null) {
              message += ' - ${response.processedChunks} chunks processed';
            }
            
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(message),
                backgroundColor: Colors.green,
              ),
            );

            // Show enhanced metadata if available
            if (response.metadata != null && response.metadata!.isNotEmpty) {
              _showEnhancedMetadata(file.name, response.metadata!);
            }
          }
        } else {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('${file.name}: ${response.message}'),
                backgroundColor: Colors.red,
              ),
            );
          }
        }
      }
      
      await _loadData();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Upload failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isUploading = false;
      });
    }
  }

  Future<void> _trainAI() async {
    if (_isTraining || _documents.isEmpty) return;

    setState(() {
      _isTraining = true;
    });

    try {
      final response = await ApiService.trainModelEnhanced(enableAdvancedFeatures: true);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['message'] ?? 'Training completed successfully'),
            backgroundColor: Colors.green,
          ),
        );
      }
      
      await _loadData();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Training failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isTraining = false;
      });
    }
  }

  Future<void> _clearAllTrainingData() async {
    if (_isClearing || _documents.isEmpty) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.warning, color: Colors.red),
            SizedBox(width: 8),
            Text('Clear All Training Data'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'This will permanently delete:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text('• ${_documents.length} uploaded documents'),
            Text('• ${_stats['total_chunks'] ?? 0} processed chunks'),
            Text('• All AI training data and embeddings'),
            Text('• All document processing history'),
            const SizedBox(height: 16),
            const Text(
              'Your Gemini AI model will start fresh without any document context. '
              'This action cannot be undone.',
              style: TextStyle(
                color: Colors.red,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Clear All Data'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    setState(() {
      _isClearing = true;
    });

    try {
      final response = await ApiService.clearAllTrainingData();
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.check_circle, color: Colors.white),
                    SizedBox(width: 8),
                    Text(
                      'Training Data Cleared Successfully',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                if (response['deleted_count'] != null)
                  Text('Deleted ${response['deleted_count']} documents'),
                if (response['ai_cleared'] != null)
                  Text('Cleared ${response['ai_cleared']} AI training records'),
              ],
            ),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 4),
          ),
        );
      }
      
      await _loadData();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to clear data: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isClearing = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: _buildAppBar(),
      backgroundColor: Colors.grey[50],
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildBody(),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      title: const Text(
        'Training Data Dashboard',
        style: TextStyle(
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
      backgroundColor: Colors.blue[700],
      elevation: 0,
      actions: [
        Container(
          margin: const EdgeInsets.only(right: 16),
          child: const ApiStatusWidget(),
        ),
      ],
    );
  }

  Widget _buildBody() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildWelcomeSection(),
          const SizedBox(height: 24),
          // AI Status Section
          const AIStatusWidget(),
          const SizedBox(height: 24),
          // Service Guide Status Section
          const ServiceGuideStatusWidget(),
          const SizedBox(height: 32),
          _buildQuickActionsRow(),
          const SizedBox(height: 32),
          _buildStatsDashboard(),
          const SizedBox(height: 32),
          _buildEnhancedCapabilitiesSection(),
          const SizedBox(height: 32),
          _buildDocumentsSection(),
          const SizedBox(height: 32),
          _buildSystemStatus(),
        ],
      ),
    );
  }

  Widget _buildWelcomeSection() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue[600]!, Colors.blue[800]!],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.blue.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.dashboard,
                  color: Colors.white,
                  size: 28,
                ),
              ),
              const SizedBox(width: 16),
              const Expanded(
                child: Text(
                  'Welcome to AI Training Dashboard',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Text(
            'Manage your training documents and optimize your Gemini AI assistant. '
            'Upload manuals, technical documentation, and knowledge bases to enhance AI responses with Google Gemini 2.5 Flash-Lite.',
            style: TextStyle(
              fontSize: 16,
              color: Colors.white,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionsRow() {
    return Row(
      children: [
        Expanded(
          child: _buildActionCard(
            title: 'Upload Documents',
            description: 'Add new training files',
            icon: Icons.upload_file,
            color: Colors.blue,
            isLoading: _isUploading,
            onTap: _uploadFiles,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildActionCard(
            title: 'Train AI Model',
            description: 'Process uploaded documents',
            icon: Icons.psychology,
            color: Colors.orange,
            isLoading: _isTraining,
            isEnabled: _documents.isNotEmpty && !_isTraining,
            onTap: _trainAI,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildActionCard(
            title: 'Clear All Data',
            description: 'Remove all training data',
            icon: Icons.clear_all,
            color: Colors.red,
            isLoading: _isClearing,
            isEnabled: _documents.isNotEmpty && !_isClearing,
            onTap: _clearAllTrainingData,
          ),
        ),
      ],
    );
  }

  Widget _buildActionCard({
    required String title,
    required String description,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
    bool isLoading = false,
    bool isEnabled = true,
  }) {
    return GestureDetector(
      onTap: isEnabled && !isLoading ? onTap : null,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isEnabled ? color.withOpacity(0.2) : Colors.grey.withOpacity(0.2),
            width: 2,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: (isEnabled ? color : Colors.grey).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: isLoading
                  ? SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(color),
                      ),
                    )
                  : Icon(
                      icon,
                      size: 24,
                      color: isEnabled ? color : Colors.grey,
                    ),
            ),
            const SizedBox(height: 16),
            Text(
              title,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: isEnabled ? Colors.black87 : Colors.grey,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              description,
              style: TextStyle(
                fontSize: 12,
                color: isEnabled ? Colors.grey[600] : Colors.grey,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsDashboard() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Statistics Overview',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildStatCard(
                title: 'Total Documents',
                value: '${_stats['total_documents'] ?? 0}',
                icon: Icons.description,
                color: Colors.blue,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildStatCard(
                title: 'Total Size',
                value: _formatFileSize(_stats['total_size'] ?? 0),
                icon: Icons.storage,
                color: Colors.green,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildStatCard(
                title: 'AI Status',
                value: 'Ready',
                icon: Icons.check_circle,
                color: Colors.orange,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: color, size: 24),
              ),
              const Spacer(),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            value,
            style: const TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[600],
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEnhancedCapabilitiesSection() {
    final capabilities = DocumentService.getFormatCapabilities();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Enhanced Processing Capabilities',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.auto_awesome, color: Colors.purple[600], size: 24),
                  const SizedBox(width: 8),
                  Text(
                    'Advanced PDF Processing',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.purple[600],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              const Text(
                'This system now features enhanced document processing with:',
                style: TextStyle(fontSize: 14, color: Colors.black87),
              ),
              const SizedBox(height: 12),
              ...capabilities['pdf']!.take(3).map((capability) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.check_circle, color: Colors.green[600], size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        capability,
                        style: const TextStyle(fontSize: 13, color: Colors.black87),
                      ),
                    ),
                  ],
                ),
              )),
              const SizedBox(height: 16),
              Row(
                children: [
                  const Text(
                    'Supported formats: ',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
                  ),
                  ..._supportedFormats.take(4).map((format) => Container(
                    margin: const EdgeInsets.only(right: 8),
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.blue[100],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      format.toUpperCase(),
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: Colors.blue[700],
                      ),
                    ),
                  )),
                  if (_supportedFormats.length > 4)
                    Text(
                      '+${_supportedFormats.length - 4} more',
                      style: TextStyle(fontSize: 11, color: Colors.grey[600]),
                    ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDocumentsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Text(
              'Recent Documents',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.black87,
              ),
            ),
            const Spacer(),
            if (_documents.isNotEmpty) ...[
              // Selection mode toggle
              TextButton.icon(
                onPressed: _toggleSelectionMode,
                icon: Icon(
                  _isSelectionMode ? Icons.close : Icons.checklist,
                  size: 16,
                ),
                label: Text(_isSelectionMode ? 'Cancel' : 'Select'),
                style: TextButton.styleFrom(
                  foregroundColor: _isSelectionMode ? Colors.red[600] : Colors.blue[600],
                ),
              ),
              const SizedBox(width: 8),
            ],
            TextButton.icon(
              onPressed: () {
                // TODO: Navigate to full documents list
              },
              icon: const Icon(Icons.arrow_forward, size: 16),
              label: const Text('View All'),
              style: TextButton.styleFrom(
                foregroundColor: Colors.blue[600],
              ),
            ),
          ],
        ),
        // Selection controls when in selection mode
        if (_isSelectionMode && _documents.isNotEmpty) ...[
          const SizedBox(height: 8),
          Row(
            children: [
              TextButton.icon(
                onPressed: _selectAllDocuments,
                icon: const Icon(Icons.select_all, size: 16),
                label: Text(_selectedDocuments.length == (_isSelectionMode ? _documents.length : _documents.take(5).length) ? 'Deselect All' : 'Select All'),
                style: TextButton.styleFrom(
                  foregroundColor: Colors.blue[600],
                ),
              ),
              const SizedBox(width: 16),
              if (_selectedDocuments.isNotEmpty) ...[
                Text(
                  '${_selectedDocuments.length} selected',
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 14,
                  ),
                ),
                const SizedBox(width: 16),
                ElevatedButton.icon(
                  onPressed: _isDeleting ? null : _deleteSelectedDocuments,
                  icon: _isDeleting
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.delete, size: 16),
                  label: Text(_isDeleting ? 'Deleting...' : 'Delete Selected'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red[500],
                    foregroundColor: Colors.white,
                  ),
                ),
              ],
            ],
          ),
        ],
        const SizedBox(height: 16),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: _documents.isEmpty
              ? _buildEmptyDocuments()
              : _buildDocumentsList(),
        ),
      ],
    );
  }

  Widget _buildEmptyDocuments() {
    return Padding(
      padding: const EdgeInsets.all(48),
      child: Column(
        children: [
          Icon(
            Icons.description_outlined,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            'No Documents Yet',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Upload your first document to get started with AI training',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildDocumentsList() {
    // Show all documents when in selection mode, otherwise show recent 5
    final docsToShow = _isSelectionMode ? _documents : _documents.take(5).toList();
    
    return Column(
      children: [
        ...docsToShow.asMap().entries.map((entry) {
          final index = entry.key;
          final doc = entry.value;
          return _buildDocumentItem(doc, index == docsToShow.length - 1);
        }).toList(),
        if (!_isSelectionMode && _documents.length > 5)
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              'And ${_documents.length - 5} more documents...',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 12,
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildDocumentItem(DocumentInfoEnhanced doc, bool isLast) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: isLast ? null : Border(
          bottom: BorderSide(color: Colors.grey[100]!, width: 1),
        ),
      ),
      child: Row(
        children: [
          // Selection checkbox
          if (_isSelectionMode)
            Checkbox(
              value: _selectedDocuments.contains(doc.id),
              onChanged: (bool? value) {
                setState(() {
                  if (value == true) {
                    _selectedDocuments.add(doc.id);
                  } else {
                    _selectedDocuments.remove(doc.id);
                  }
                });
              },
            ),
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.blue[50],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              _getFileIcon(doc.filename),
              color: Colors.blue[600],
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  doc.filename,
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  _formatFileSize(doc.fileSize),
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          // Individual delete button when not in selection mode
          if (!_isSelectionMode)
            IconButton(
              icon: Icon(
                Icons.delete_outline,
                color: Colors.red[400],
                size: 20,
              ),
              onPressed: () => _deleteDocument(doc.id, doc.filename),
              tooltip: 'Delete document',
            ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.green[50],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              'Processed',
              style: TextStyle(
                color: Colors.green[700],
                fontSize: 10,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _deleteDocument(String documentId, String filename) async {
    final bool? confirm = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Delete Document'),
          content: Text('Are you sure you want to delete "$filename"?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(true),
              style: TextButton.styleFrom(
                foregroundColor: Colors.red,
              ),
              child: const Text('Delete'),
            ),
          ],
        );
      },
    );

    if (confirm == true) {
      setState(() {
        _isDeleting = true;
      });

      try {
        final result = await ApiService.deleteDocument(documentId);
        if (result['success']) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Document "$filename" deleted successfully'),
                backgroundColor: Colors.green,
              ),
            );
          }
          await _loadData(); // Refresh the list
        } else {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Failed to delete document: ${result['message']}'),
                backgroundColor: Colors.red,
              ),
            );
          }
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error deleting document: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      } finally {
        setState(() {
          _isDeleting = false;
        });
      }
    }
  }

  Future<void> _deleteSelectedDocuments() async {
    if (_selectedDocuments.isEmpty) return;

    final bool? confirm = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Delete Selected Documents'),
          content: Text('Are you sure you want to delete ${_selectedDocuments.length} selected documents?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(true),
              style: TextButton.styleFrom(
                foregroundColor: Colors.red,
              ),
              child: const Text('Delete All'),
            ),
          ],
        );
      },
    );

    if (confirm == true) {
      setState(() {
        _isDeleting = true;
      });

      try {
        int successCount = 0;
        int failCount = 0;

        for (String documentId in _selectedDocuments) {
          try {
            final result = await ApiService.deleteDocument(documentId);
            if (result['success']) {
              successCount++;
            } else {
              failCount++;
            }
          } catch (e) {
            failCount++;
          }
        }

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Deleted $successCount documents successfully${failCount > 0 ? ', $failCount failed' : ''}'),
              backgroundColor: failCount > 0 ? Colors.orange : Colors.green,
            ),
          );
        }

        setState(() {
          _selectedDocuments.clear();
          _isSelectionMode = false;
        });

        await _loadData(); // Refresh the list
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error deleting documents: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      } finally {
        setState(() {
          _isDeleting = false;
        });
      }
    }
  }

  void _toggleSelectionMode() {
    setState(() {
      _isSelectionMode = !_isSelectionMode;
      if (!_isSelectionMode) {
        _selectedDocuments.clear();
      }
    });
  }

  void _selectAllDocuments() {
    final docsToShow = _isSelectionMode ? _documents : _documents.take(5).toList();
    setState(() {
      if (_selectedDocuments.length == docsToShow.length) {
        _selectedDocuments.clear();
      } else {
        _selectedDocuments = docsToShow.map((doc) => doc.id).toSet();
      }
    });
  }

  Widget _buildSystemStatus() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text(
                'System Status',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.green[50],
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: Colors.green[600],
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Online',
                      style: TextStyle(
                        color: Colors.green[700],
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: _buildStatusItem('API Server', true),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildStatusItem('Database', true),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildStatusItem('AI Service', true),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatusItem(String title, bool isOnline) {
    return Row(
      children: [
        Icon(
          isOnline ? Icons.check_circle : Icons.error,
          color: isOnline ? Colors.green[600] : Colors.red[600],
          size: 16,
        ),
        const SizedBox(width: 8),
        Text(
          title,
          style: TextStyle(
            fontSize: 14,
            color: Colors.grey[700],
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  void _showEnhancedMetadata(String filename, Map<String, dynamic> metadata) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Enhanced Processing Results'),
          content: Container(
            width: double.maxFinite,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('File: $filename', style: TextStyle(fontWeight: FontWeight.bold)),
                SizedBox(height: 16),
                if (metadata['extracted_tags'] != null) ...[
                  Text('Extracted Tags:', style: TextStyle(fontWeight: FontWeight.bold)),
                  SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    children: (metadata['extracted_tags'] as List)
                        .map((tag) => Chip(
                              label: Text(tag.toString()),
                              backgroundColor: Colors.blue[100],
                            ))
                        .toList(),
                  ),
                  SizedBox(height: 16),
                ],
                if (metadata['document_type'] != null) ...[
                  Text('Document Type: ${metadata['document_type']}'),
                  SizedBox(height: 8),
                ],
                if (metadata['processing_method'] != null) ...[
                  Text('Processing Method: ${metadata['processing_method']}'),
                  SizedBox(height: 8),
                ],
                if (metadata['content_stats'] != null) ...[
                  Text('Content Statistics:', style: TextStyle(fontWeight: FontWeight.bold)),
                  SizedBox(height: 8),
                  ...((metadata['content_stats'] as Map<String, dynamic>).entries
                      .map((e) => Text('${e.key}: ${e.value}'))
                      .take(5)),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text('Close'),
            ),
          ],
        );
      },
    );
  }

  IconData _getFileIcon(String filename) {
    final ext = filename.toLowerCase().split('.').last;
    switch (ext) {
      case 'pdf':
        return Icons.picture_as_pdf;
      case 'doc':
      case 'docx':
        return Icons.description;
      case 'txt':
        return Icons.text_snippet;
      default:
        return Icons.insert_drive_file;
    }
  }

  String _formatFileSize(int bytes) {
    if (bytes < 1024) return '${bytes}B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)}KB';
    return '${(bytes / (1024 * 1024)).toStringAsFixed(1)}MB';
  }
}
