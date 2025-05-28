#!/usr/bin/env pwsh

Write-Host "🚀 Starting AI Web Automation Agent with Multi-Model Support" -ForegroundColor Green
Write-Host "===============================================================" -ForegroundColor Cyan

# Check for environment files
$queueEnvPath = "queue\.env"
$frontendEnvPath = "frontend\.env"

if (-not (Test-Path $queueEnvPath)) {
    Write-Host "⚙️  Creating queue environment file..." -ForegroundColor Yellow
    Copy-Item "queue\queue-env.example" $queueEnvPath
}

if (-not (Test-Path $frontendEnvPath)) {
    Write-Host "⚙️  Creating frontend environment file..." -ForegroundColor Yellow
    Copy-Item "frontend\.env.example" $frontendEnvPath
}

# Load environment variables to check API keys
$envContent = Get-Content $queueEnvPath -ErrorAction SilentlyContinue
$geminiKey = ($envContent | Where-Object { $_ -match "^GEMINI_API_KEY=" }) -replace "GEMINI_API_KEY=", ""
$openaiKey = ($envContent | Where-Object { $_ -match "^OPENAI_API_KEY=" }) -replace "OPENAI_API_KEY=", ""

Write-Host ""
Write-Host "🔍 AI Model Configuration Status:" -ForegroundColor Cyan

$hasGemini = $geminiKey -and $geminiKey -ne "your-gemini-api-key-here" -and $geminiKey.Length -gt 10
$hasOpenAI = $openaiKey -and $openaiKey -ne "your-openai-api-key-here" -and $openaiKey.Length -gt 10

if ($hasGemini) {
    Write-Host "   ✅ Gemini 2.0 Flash: Configured (${geminiKey.Substring(0,8)}...)" -ForegroundColor Green
} else {
    Write-Host "   ❌ Gemini 2.0 Flash: Not configured" -ForegroundColor Red
    Write-Host "      Get API key: https://aistudio.google.com/app/apikey" -ForegroundColor Yellow
}

if ($hasOpenAI) {
    Write-Host "   ✅ OpenAI GPT: Configured (${openaiKey.Substring(0,8)}...)" -ForegroundColor Green
} else {
    Write-Host "   ❌ OpenAI GPT: Not configured" -ForegroundColor Red
    Write-Host "      Get API key: https://platform.openai.com/api-keys" -ForegroundColor Yellow
}

if (-not $hasGemini -and -not $hasOpenAI) {
    Write-Host ""
    Write-Host "⚠️  Warning: No AI models configured!" -ForegroundColor Red
    Write-Host "   Please edit 'queue\.env' and add at least one API key." -ForegroundColor Yellow
    Write-Host "   The system needs either GEMINI_API_KEY or OPENAI_API_KEY to function." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to continue anyway, or Ctrl+C to exit and configure API keys"
}

Write-Host ""
Write-Host "🌟 New Features in this version:" -ForegroundColor Cyan
Write-Host "   • Multi-Model Support: Choose between Gemini 2.0 Flash and OpenAI GPT" -ForegroundColor White
Write-Host "   • Intelligent Chat: Debug failed automations with AI assistance" -ForegroundColor White
Write-Host "   • Auto-Fallback: Seamlessly switch between AI models if one fails" -ForegroundColor White
Write-Host "   • Context Caching: Faster response times with Gemini" -ForegroundColor White
Write-Host "   • Enhanced Analysis: Better website understanding and element selection" -ForegroundColor White

Write-Host ""
Write-Host "🌟 Available AI Models:" -ForegroundColor Cyan
Write-Host "   • Gemini 2.0 Flash: Enhanced website analysis with context caching" -ForegroundColor White
Write-Host "   • Gemini 2.5 Preview: Latest experimental model with advanced reasoning" -ForegroundColor White
Write-Host "   • GPT-4o Mini: Reliable and fast model (set as default)" -ForegroundColor White
Write-Host "   • Auto-Fallback: Seamlessly switch between models if one fails" -ForegroundColor White
Write-Host "   • Context Caching: Faster response times with Gemini 2.0 Flash" -ForegroundColor White

Write-Host ""
Write-Host "🔗 Service URLs (will be available after startup):" -ForegroundColor Cyan
Write-Host "   • Frontend:        http://localhost:3001" -ForegroundColor White
Write-Host "   • Queue Processor: http://localhost:3002+" -ForegroundColor White
Write-Host "   • Worker:          http://localhost:8000" -ForegroundColor White

Write-Host ""
Write-Host "📖 Quick Usage Guide:" -ForegroundColor Cyan
Write-Host "   1. Select your preferred AI model (Gemini 2.0/2.5 or GPT-4o Mini)" -ForegroundColor White
Write-Host "   2. Enter a website URL and describe your automation" -ForegroundColor White
Write-Host "   3. If automation fails 3 times, chat with AI for debugging help" -ForegroundColor White
Write-Host "   4. Apply AI suggestions and retry with improved automation" -ForegroundColor White

Write-Host ""
Write-Host "🚀 Starting all services..." -ForegroundColor Green

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start all services
npm run dev 