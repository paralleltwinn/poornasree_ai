# Test script for Poornasree AI API endpoints verification
Write-Host "🚀 Starting Poornasree AI API Verification Tests" -ForegroundColor Green
Write-Host "=" * 60

$baseUrl = "http://localhost:8000"
$apiUrl = "$baseUrl/api/v1"

# Test 1: Health Check
Write-Host "1. Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✅ Health Check: $($health.status)" -ForegroundColor Green
    Write-Host "   Version: $($health.version)" -ForegroundColor Cyan
    Write-Host "   AI Model Status: $($health.ai_model_status)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Documents List
Write-Host "`n2. Testing Documents List Endpoint..." -ForegroundColor Yellow
try {
    $docs = Invoke-RestMethod -Uri "$apiUrl/documents" -Method GET
    Write-Host "✅ Documents Retrieved: $($docs.documents.Count) documents found" -ForegroundColor Green
    foreach ($doc in $docs.documents[0..2]) {  # Show first 3 docs
        Write-Host "   - $($doc.filename) ($($doc.file_type))" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Documents List Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Supported Formats
Write-Host "`n3. Testing Supported Formats Endpoint..." -ForegroundColor Yellow
try {
    $formats = Invoke-RestMethod -Uri "$apiUrl/documents/supported-formats" -Method GET
    Write-Host "✅ Supported Formats Retrieved" -ForegroundColor Green
    Write-Host "   Formats: $($formats.formats -join ', ')" -ForegroundColor Cyan
    Write-Host "   Max Size: $($formats.max_file_size_mb)MB" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Supported Formats Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Chat Status
Write-Host "`n4. Testing Chat Status Endpoint..." -ForegroundColor Yellow
try {
    $chatStatus = Invoke-RestMethod -Uri "$apiUrl/chat/status" -Method GET
    Write-Host "✅ Chat Status: $($chatStatus.status)" -ForegroundColor Green
    Write-Host "   Model: $($chatStatus.model_name)" -ForegroundColor Cyan
    Write-Host "   Documents: $($chatStatus.document_count) loaded" -ForegroundColor Cyan
    Write-Host "   Chunks: $($chatStatus.total_chunks) processed" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Chat Status Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Chat Message
Write-Host "`n5. Testing Chat Message Endpoint..." -ForegroundColor Yellow
try {
    $chatBody = @{
        message = "What is CNC machine maintenance?"
        user_id = "test_verification"
    } | ConvertTo-Json

    $chatResponse = Invoke-RestMethod -Uri "$apiUrl/chat" -Method POST -Body $chatBody -ContentType "application/json"
    Write-Host "✅ Chat Response Received" -ForegroundColor Green
    $response = $chatResponse.response
    if ($response.Length -gt 100) {
        Write-Host "   Response: $($response.Substring(0, 100))..." -ForegroundColor Cyan
    } else {
        Write-Host "   Response: $response" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Chat Message Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Document Stats
Write-Host "`n6. Testing Document Stats Endpoint..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "$apiUrl/documents/stats" -Method GET
    Write-Host "✅ Document Stats Retrieved" -ForegroundColor Green
    Write-Host "   Total Documents: $($stats.total_documents)" -ForegroundColor Cyan
    Write-Host "   Total Size: $($stats.total_size_mb)MB" -ForegroundColor Cyan
    Write-Host "   Most Common Format: $($stats.format_breakdown.Keys[0])" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Document Stats Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" + "=" * 60
Write-Host "🏁 API Verification Tests Complete!" -ForegroundColor Green
Write-Host "📱 Flutter App URL: http://localhost:53346" -ForegroundColor Magenta
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Magenta
