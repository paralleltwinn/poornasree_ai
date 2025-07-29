# ================================================================
# 🚀 POORNASREE AI - POWERSHELL QUICK STARTUP
# ================================================================

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🚀 POORNASREE AI - QUICK STARTUP" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "This script will run all tests and start the API server" -ForegroundColor Yellow
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11 or higher." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the comprehensive startup script
Write-Host "🔄 Running comprehensive startup script..." -ForegroundColor Yellow
Write-Host ""

try {
    python startup.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Startup completed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Startup failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        Read-Host "Press Enter to exit"
    }
} catch {
    Write-Host "❌ Failed to run startup script: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
