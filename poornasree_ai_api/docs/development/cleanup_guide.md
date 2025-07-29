# 🧹 Database Cleanup Guide

## Overview

This guide provides instructions for cleaning all trained data from your Poornasree AI system. There are two cleanup options available:

---

## 🚀 Quick Cleanup (Database Only)

**Best for**: Quick database reset while keeping uploaded files

```bash
cd poornasree_ai_api
python quick_cleanup.py
```

**What it does:**
- ✅ Clears all database tables
- ✅ Removes all user data and chat history
- ✅ Deletes all document metadata
- ✅ Resets auto-increment counters
- ❌ Keeps uploaded files on disk

**Time**: ~30 seconds

---

## 🔥 Complete Cleanup (Everything)

**Best for**: Complete system reset to factory state

```bash
cd poornasree_ai_api
python complete_cleanup.py
```

**What it does:**
- ✅ Clears all database tables
- ✅ Removes all uploaded files
- ✅ Deletes vector embeddings and knowledge base
- ✅ Cleans AI model cache
- ✅ Removes log files
- ✅ Frees disk space

**Time**: ~2-5 minutes

---

## 🔍 What Gets Cleaned

### Database Tables
| Table | Content |
|-------|---------|
| `users` | User accounts and profiles |
| `documents` | Document metadata and processing info |
| `chat_sessions` | Chat conversation sessions |
| `chat_messages` | Individual chat messages and AI responses |
| `document_chunks` | Text chunks and embeddings |
| `api_usage` | API usage statistics |
| `system_health` | System monitoring data |

### File Directories
| Directory | Content |
|-----------|---------|
| `data/uploads/` | All uploaded documents (PDF, DOCX, etc.) |
| `data/knowledge_base/` | Vector embeddings and AI knowledge |
| `data/models/` | Cached AI models |
| `data/logs/` | Application log files |
| `*.pkl` files | Pickle files containing trained data |

---

## 🛡️ Safety Features

### Confirmation Required
- Both scripts require typing **"YES"** to proceed
- No accidental deletions possible

### Detailed Logging
- Complete cleanup creates `cleanup.log` with full details
- Track exactly what was deleted

### Statistics Report
- Shows number of records/files deleted
- Reports disk space freed
- Provides completion summary

---

## 🔄 After Cleanup

### 1. Restart the System
```bash
python startup.py
```

### 2. Verify Clean State
- Check `/health` endpoint shows clean system
- Database tables should be empty
- Upload directories should be clean

### 3. Start Fresh
- Upload new documents
- Begin new chat conversations  
- Train with fresh data

---

## 🚨 Important Warnings

### ⚠️ **Data Loss Warning**
- **ALL DATA WILL BE PERMANENTLY DELETED**
- No recovery possible after cleanup
- Export any important data before cleanup

### ⚠️ **Backup Recommendations**
Before cleanup, consider backing up:
- Important uploaded documents
- Chat conversation exports
- Database dumps if needed

### ⚠️ **System State**
- Stop the API server before running cleanup
- Ensure no active uploads or processing
- Close any database connections

---

## 🔧 Troubleshooting

### Database Connection Issues
```bash
# Check database connectivity first
python -c "from app.database import test_database_connection; import asyncio; print(asyncio.run(test_database_connection()))"
```

### Permission Issues
```bash
# Run with appropriate permissions
# Windows PowerShell:
python complete_cleanup.py

# Linux/Mac:
sudo python complete_cleanup.py
```

### Partial Cleanup Failures
- Check `cleanup.log` for detailed error information
- Run the script again - it's safe to re-run
- Manual table cleanup if needed

---

## 📊 Example Output

### Quick Cleanup Output
```
🧹 Quick Database Cleanup
==============================
This will delete ALL data from the database:
  • All users and their data
  • All uploaded documents
  • All chat history
  • All trained knowledge

Type 'YES' to proceed: YES

🚀 Starting cleanup...
  ✅ api_usage: 1,234 records deleted
  ✅ system_health: 456 records deleted
  ✅ document_chunks: 5,678 records deleted
  ✅ chat_messages: 2,345 records deleted
  ✅ chat_sessions: 123 records deleted
  ✅ documents: 45 records deleted
  ✅ users: 12 records deleted

✅ Cleanup completed!
📊 Total records deleted: 9,893
```

### Complete Cleanup Output
```
📊 CLEANUP COMPLETED - SUMMARY REPORT
====================================

🗄️ Database Records Deleted:
   • Users: 12
   • Documents: 45
   • Chat Sessions: 123
   • Chat Messages: 2,345
   • Document Chunks: 5,678
   • API Usage Records: 1,234
   • System Health Records: 456

📁 Files and Storage:
   • Files Deleted: 67
   • Storage Freed: 234.56 MB

✅ Total Impact:
   • Database Records: 9,893
   • Files Removed: 67
   • Disk Space Freed: 234.56 MB

🎉 System Reset Complete!
```

---

## 💡 Best Practices

### Before Cleanup
1. **Stop the API server**
2. **Export important data** if needed
3. **Verify backup strategy**
4. **Ensure database connectivity**

### During Cleanup
1. **Don't interrupt the process**
2. **Monitor for any errors**
3. **Check log files if issues occur**

### After Cleanup
1. **Restart with `python startup.py`**
2. **Verify clean state**
3. **Begin fresh training**
4. **Monitor system health**

---

## 🆘 Recovery Options

### If Cleanup Fails
1. Check `cleanup.log` for specific errors
2. Run the script again (safe to re-run)
3. Use quick cleanup if complete cleanup fails
4. Manual database cleanup as last resort

### If System Won't Start After Cleanup
1. Run `python startup.py` for fresh initialization
2. Check database connectivity
3. Verify file permissions
4. Review startup logs

---

**🎯 Remember: Cleanup gives you a fresh start for better AI training and performance!**
