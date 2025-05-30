#!/usr/bin/env pwsh

Write-Host "Starting AI Web Automation Agent with Multi-Model LangChain Support" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Cyan

# Check for environment file
$envPath = ".env"

if (!(Test-Path $envPath)) {
    Write-Host "Creating environment file..." -ForegroundColor Yellow
    Copy-Item "env.example" $envPath
    Write-Host "Please edit .env file with your API keys before continuing." -ForegroundColor Yellow
    Write-Host ""
}

# Load environment variables to check API keys
$envContent = Get-Content $envPath -ErrorAction SilentlyContinue
$openaiKey = ""
$anthropicKey = ""
$googleKey = ""
$hfToken = ""

foreach ($line in $envContent) {
    if ($line -match "^OPENAI_API_KEY=(.*)") {
        $openaiKey = $matches[1]
    }
    if ($line -match "^ANTHROPIC_API_KEY=(.*)") {
        $anthropicKey = $matches[1]
    }
    if ($line -match "^GOOGLE_API_KEY=(.*)") {
        $googleKey = $matches[1]
    }
    if ($line -match "^HUGGINGFACE_API_TOKEN=(.*)") {
        $hfToken = $matches[1]
    }
}

Write-Host ""
Write-Host "AI Model Configuration Status:" -ForegroundColor Cyan

$hasOpenAI = $false
$hasAnthropic = $false
$hasGoogle = $false
$hasHF = $false

if ($openaiKey -and $openaiKey -ne "your_openai_api_key_here" -and $openaiKey.Length -gt 10) {
    $hasOpenAI = $true
    $shortKey = $openaiKey.Substring(0, [Math]::Min(8, $openaiKey.Length))
    Write-Host "   [OK] OpenAI GPT: Configured ($shortKey...)" -ForegroundColor Green
} else {
    Write-Host "   [X] OpenAI GPT: Not configured" -ForegroundColor Red
    Write-Host "      Get API key: https://platform.openai.com/api-keys" -ForegroundColor Yellow
}

if ($anthropicKey -and $anthropicKey -ne "your_anthropic_api_key_here" -and $anthropicKey.Length -gt 10) {
    $hasAnthropic = $true
    $shortKey = $anthropicKey.Substring(0, [Math]::Min(8, $anthropicKey.Length))
    Write-Host "   [OK] Anthropic Claude: Configured ($shortKey...)" -ForegroundColor Green
} else {
    Write-Host "   [X] Anthropic Claude: Not configured" -ForegroundColor Red
    Write-Host "      Get API key: https://console.anthropic.com/" -ForegroundColor Yellow
}

if ($googleKey -and $googleKey -ne "your_google_api_key_here" -and $googleKey.Length -gt 10) {
    $hasGoogle = $true
    $shortKey = $googleKey.Substring(0, [Math]::Min(8, $googleKey.Length))
    Write-Host "   [OK] Google Gemini: Configured ($shortKey...)" -ForegroundColor Green
} else {
    Write-Host "   [X] Google Gemini: Not configured" -ForegroundColor Red
    Write-Host "      Get API key: https://aistudio.google.com/app/apikey" -ForegroundColor Yellow
}

if ($hfToken -and $hfToken -ne "your_huggingface_token_here" -and $hfToken.Length -gt 10) {
    $hasHF = $true
    $shortKey = $hfToken.Substring(0, [Math]::Min(8, $hfToken.Length))
    Write-Host "   [OK] Hugging Face: Configured ($shortKey...)" -ForegroundColor Green
} else {
    Write-Host "   [X] Hugging Face: Not configured" -ForegroundColor Red
    Write-Host "      Get token: https://huggingface.co/settings/tokens" -ForegroundColor Yellow
}

# Check for Ollama
$ollamaRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $ollamaRunning = $true
        Write-Host "   [OK] Ollama: Running locally" -ForegroundColor Green
    }
} catch {
    Write-Host "   [X] Ollama: Not running" -ForegroundColor Red
    Write-Host "      Install: https://ollama.ai/" -ForegroundColor Yellow
}

$totalModels = $hasOpenAI + $hasAnthropic + $hasGoogle + $hasHF + $ollamaRunning

if ($totalModels -eq 0) {
    Write-Host ""
    Write-Host "Warning: No AI models configured!" -ForegroundColor Red
    Write-Host "   Please edit '.env' and add at least one API key." -ForegroundColor Yellow
    Write-Host "   Or install Ollama for local models." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to continue anyway, or Ctrl+C to exit and configure API keys"
} else {
    Write-Host ""
    Write-Host "✅ $totalModels AI model(s) available" -ForegroundColor Green
}

Write-Host ""
Write-Host "New Multi-Model Features:" -ForegroundColor Cyan
Write-Host "   🤖 Multiple AI Providers: OpenAI, Anthropic, Google, Ollama, Hugging Face" -ForegroundColor White
Write-Host "   🔄 Dynamic Model Switching: Change models through the UI" -ForegroundColor White
Write-Host "   🎯 Simplified Architecture: Direct API calls, no queue system" -ForegroundColor White
Write-Host "   📁 Project Generation: Complete automation projects with AI" -ForegroundColor White
Write-Host "   🔧 Enhanced Tools: LangChain function calling and memory" -ForegroundColor White

Write-Host ""
Write-Host "Available AI Models:" -ForegroundColor Cyan
Write-Host "   OpenAI: GPT-4, GPT-3.5-turbo, and legacy models" -ForegroundColor White
Write-Host "   Anthropic: Claude-3 (Opus, Sonnet, Haiku), Claude-2" -ForegroundColor White
Write-Host "   Google: Gemini Pro, Gemini Pro Vision" -ForegroundColor White
Write-Host "   Ollama: Local models (Llama2, Mistral, CodeLlama, etc.)" -ForegroundColor White
Write-Host "   Hugging Face: Various open-source models" -ForegroundColor White

Write-Host ""
Write-Host "Service URLs (will be available after startup):" -ForegroundColor Cyan
Write-Host "   Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "   Worker API:  http://localhost:8000" -ForegroundColor White
Write-Host "   Health:      http://localhost:8000/health" -ForegroundColor White

Write-Host ""
Write-Host "Quick Usage Guide:" -ForegroundColor Cyan
Write-Host "   1. Select your preferred AI model from the dropdown" -ForegroundColor White
Write-Host "   2. Enter a website URL and describe your automation task" -ForegroundColor White
Write-Host "   3. Choose automation framework (Selenium or SeleniumBase)" -ForegroundColor White
Write-Host "   4. Watch as AI generates a complete automation project" -ForegroundColor White
Write-Host "   5. Switch models anytime for different capabilities" -ForegroundColor White

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
Set-Location worker
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    Read-Host "Press Enter to continue anyway"
}

# Install Node.js dependencies
Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
Set-Location ..\frontend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Node.js dependencies" -ForegroundColor Red
    Read-Host "Press Enter to continue anyway"
}

Set-Location ..

Write-Host ""
Write-Host "🚀 Starting services..." -ForegroundColor Green

# Start Python worker
Write-Host "🐍 Starting Python Worker (Multi-Model LangChain Agent)..." -ForegroundColor Yellow
Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$PWD\worker'; python main.py" -WindowStyle Normal

# Wait for worker to start
Write-Host "⏳ Waiting for worker to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend
Write-Host "🌐 Starting Next.js Frontend..." -ForegroundColor Yellow
Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$PWD\frontend'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "✅ System Started!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Worker API: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
Read-Host 