import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ExampleQuestions extends StatefulWidget {
  final Function(String) onQuestionTap;

  const ExampleQuestions({
    super.key,
    required this.onQuestionTap,
  });

  @override
  State<ExampleQuestions> createState() => _ExampleQuestionsState();
}

class _ExampleQuestionsState extends State<ExampleQuestions> {
  List<Map<String, dynamic>> _examples = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadExamples();
  }

  Future<void> _loadExamples() async {
    try {
      final examples = await ApiService.getChatExamples();
      setState(() {
        _examples = examples;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _examples = _getDefaultExamples();
        _isLoading = false;
      });
    }
  }

  List<Map<String, dynamic>> _getDefaultExamples() {
    return [
      {
        "category": "Machine Operation",
        "questions": [
          "How do I start the machine?",
          "What is the proper startup sequence?",
          "How do I shut down the machine safely?",
          "What are the daily operation checks?"
        ]
      },
      {
        "category": "Troubleshooting",
        "questions": [
          "The machine won't start, what should I check?",
          "What does error code E001 mean?",
          "The machine is making unusual noises",
          "How do I reset the system after an error?"
        ]
      },
      {
        "category": "Maintenance",
        "questions": [
          "When should I perform routine maintenance?",
          "How do I clean the machine properly?",
          "What lubricants should I use?",
          "How often should I replace filters?"
        ]
      },
    ];
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Padding(
        padding: EdgeInsets.all(16.0),
        child: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.help_outline,
                  color: Theme.of(context).primaryColor,
                ),
                const SizedBox(width: 8),
                const Text(
                  'Example Questions',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Text(
              'Tap any question to get started:',
              style: TextStyle(
                color: Colors.grey,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 16),
            
            // Categories
            ...(_examples.take(3).map((category) => _buildCategorySection(category))),
            
            // Tip
            Container(
              margin: const EdgeInsets.only(top: 16),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: const Row(
                children: [
                  Icon(Icons.lightbulb_outline, color: Colors.blue),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Tip: Upload your machine manuals in the Dashboard for more specific answers!',
                      style: TextStyle(fontSize: 14),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCategorySection(Map<String, dynamic> category) {
    final questions = List<String>.from(category['questions'] ?? []);
    
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            category['category'] ?? '',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: Theme.of(context).primaryColor,
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8.0,
            runSpacing: 8.0,
            children: questions.take(4).map((question) => _buildQuestionChip(question)).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildQuestionChip(String question) {
    return ActionChip(
      label: Text(
        question,
        style: const TextStyle(fontSize: 13),
      ),
      onPressed: () => widget.onQuestionTap(question),
      backgroundColor: Theme.of(context).primaryColor.withOpacity(0.1),
      side: BorderSide(color: Theme.of(context).primaryColor.withOpacity(0.3)),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
    );
  }
}
