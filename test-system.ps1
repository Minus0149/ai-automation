# AI Web Automation Agent - System Test
Write-Host "🧪 Testing AI Web Automation Agent System..." -ForegroundColor Cyan

# Test 1: Environment Variables
Write-Host "`n📋 Test 1: Environment Variables" -ForegroundColor Yellow
if (Test-Path "queue\.env") {
    $queueEnv = Get-Content "queue\.env" -Raw
    if ($queueEnv -match 'OPENAI_API_KEY="sk-[^"]+') {
        Write-Host "✅ OpenAI API key found in queue/.env" -ForegroundColor Green
    } else {
        Write-Host "❌ OpenAI API key not found" -ForegroundColor Red
    }
} else {
    Write-Host "❌ queue/.env file missing" -ForegroundColor Red
}

# Test 2: Docker Containers
Write-Host "`n🐳 Test 2: Docker Containers" -ForegroundColor Yellow
try {
    $dockerRunning = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is available" -ForegroundColor Green
        
        # Check PostgreSQL container
        $postgresStatus = docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String "ai-automation-postgres"
        if ($postgresStatus) {
            Write-Host "✅ PostgreSQL container running" -ForegroundColor Green
        } else {
            Write-Host "❌ PostgreSQL container not running" -ForegroundColor Red
        }
        
        # Check Redis container
        $redisStatus = docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String "ai-automation-redis"
        if ($redisStatus) {
            Write-Host "✅ Redis container running" -ForegroundColor Green
        } else {
            Write-Host "❌ Redis container not running" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Docker not available" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Docker not available" -ForegroundColor Red
}

# Test 3: Database Connection
Write-Host "`n🗄️  Test 3: Database Connection" -ForegroundColor Yellow
try {
    $dbTest = docker exec ai-automation-postgres pg_isready -U automation_user -d ai_automation 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL connection successful" -ForegroundColor Green
    } else {
        Write-Host "❌ PostgreSQL connection failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Cannot test PostgreSQL connection" -ForegroundColor Red
}

# Test 4: Redis Connection
Write-Host "`n🔴 Test 4: Redis Connection" -ForegroundColor Yellow
try {
    $redisTest = docker exec ai-automation-redis redis-cli -a redis_password_2024 ping 2>$null
    if ($redisTest -eq "PONG") {
        Write-Host "✅ Redis connection successful" -ForegroundColor Green
    } else {
        Write-Host "❌ Redis connection failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Cannot test Redis connection" -ForegroundColor Red
}

# Test 5: Python Dependencies
Write-Host "`n🐍 Test 5: Python Dependencies" -ForegroundColor Yellow
try {
    $pythonCheck = python -c "import selenium, fastapi, uvicorn; print('OK')" 2>$null
    if ($pythonCheck -eq "OK") {
        Write-Host "✅ Python dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Python dependencies missing" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Python not available" -ForegroundColor Red
}

# Test 6: Node Dependencies
Write-Host "`n📦 Test 6: Node.js Dependencies" -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Write-Host "✅ Root node_modules found" -ForegroundColor Green
} else {
    Write-Host "❌ Root node_modules missing" -ForegroundColor Red
}

if (Test-Path "queue\node_modules") {
    Write-Host "✅ Queue node_modules found" -ForegroundColor Green
} else {
    Write-Host "❌ Queue node_modules missing" -ForegroundColor Red
}

if (Test-Path "frontend\node_modules") {
    Write-Host "✅ Frontend node_modules found" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend node_modules missing" -ForegroundColor Red
}

# Test 7: Port Availability
Write-Host "`n🌐 Test 7: Port Availability" -ForegroundColor Yellow
$ports = @(3000, 5432, 6379, 8000, 8080, 8081)
foreach ($port in $ports) {
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.Connect("localhost", $port)
        Write-Host "✅ Port $port is in use (service running)" -ForegroundColor Green
        $tcpClient.Close()
    } catch {
        Write-Host "⚠️  Port $port is available" -ForegroundColor Yellow
    }
}

Write-Host "`n🎯 Quick Start Commands:" -ForegroundColor Cyan
Write-Host "  npm run setup        # Complete Docker setup" -ForegroundColor White
Write-Host "  npm run start-dev     # Start full system" -ForegroundColor White
Write-Host "  npm run docker:up     # Start containers only" -ForegroundColor White
Write-Host ""
Write-Host "📍 Expected Services:" -ForegroundColor Cyan
Write-Host "  Frontend:      http://localhost:3000" -ForegroundColor White
Write-Host "  Python Worker: http://localhost:8000" -ForegroundColor White
Write-Host "  PostgreSQL:    localhost:5432" -ForegroundColor White
Write-Host "  Redis:         localhost:6379" -ForegroundColor White
Write-Host "  PgAdmin:       http://localhost:8080" -ForegroundColor White
Write-Host "  Redis UI:      http://localhost:8081" -ForegroundColor White 