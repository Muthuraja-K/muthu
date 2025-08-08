# Stock Prediction API Development Server
# PowerShell script to start the server with auto-reload

Write-Host "🚀 Starting Stock Prediction API Development Server..." -ForegroundColor Green
Write-Host "📁 Auto-reload enabled - watching for file changes" -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔄 Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

try {
    python dev_server.py
}
catch {
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
