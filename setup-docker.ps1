# AI Web Automation Agent - Docker Setup Script
Write-Host "🐳 Setting up Docker containers for AI Web Automation Agent..." -ForegroundColor Cyan

# Function to check if Docker is running
function Test-DockerRunning {
    try {
        docker version | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Check Docker availability
if (-not (Test-DockerRunning)) {
    Write-Host "❌ Docker is not running!" -ForegroundColor Red
    Write-Host "Please install and start Docker Desktop first." -ForegroundColor Yellow
    Write-Host "Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ Docker is running" -ForegroundColor Green

# Create logs directory
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "📁 Created logs directory" -ForegroundColor Green
}

# Create docker directory if it doesn't exist
if (-not (Test-Path "docker")) {
    New-Item -ItemType Directory -Path "docker" | Out-Null
    Write-Host "📁 Created docker directory" -ForegroundColor Green
}

# Copy environment files from examples
Write-Host "📋 Setting up environment files..." -ForegroundColor Yellow

# Root .env file
if (-not (Test-Path ".env")) {
    Copy-Item "env.example" ".env"
    Write-Host "✅ Created .env from example" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env already exists, not overwriting" -ForegroundColor Yellow
}

# Queue .env file
if (-not (Test-Path "queue\.env")) {
    Copy-Item "queue\queue-env.example" "queue\.env"
    Write-Host "✅ Created queue/.env from example" -ForegroundColor Green
} else {
    Write-Host "⚠️  queue/.env already exists, not overwriting" -ForegroundColor Yellow
}

# Stop existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker stop ai-automation-postgres ai-automation-redis ai-automation-redis-ui ai-automation-pgadmin 2>$null | Out-Null

# Remove existing containers
Write-Host "🗑️  Removing existing containers..." -ForegroundColor Yellow
docker rm ai-automation-postgres ai-automation-redis ai-automation-redis-ui ai-automation-pgadmin 2>$null | Out-Null

# Start Docker containers
Write-Host "🚀 Starting Docker containers..." -ForegroundColor Cyan
docker-compose up -d

# Wait for containers to be ready
Write-Host "⏳ Waiting for containers to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check container health
Write-Host "🔍 Checking container health..." -ForegroundColor Yellow

$containers = @("ai-automation-postgres", "ai-automation-redis")
foreach ($container in $containers) {
    $status = docker inspect --format='{{.State.Health.Status}}' $container 2>$null
    if ($status -eq "healthy" -or $status -eq "") {
        $running = docker inspect --format='{{.State.Running}}' $container 2>$null
        if ($running -eq "true") {
            Write-Host "✅ $container is running" -ForegroundColor Green
        } else {
            Write-Host "❌ $container is not running" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️  $container health: $status" -ForegroundColor Yellow
    }
}

# Test database connection
Write-Host "🔗 Testing database connection..." -ForegroundColor Yellow
$dbTest = docker exec ai-automation-postgres pg_isready -U automation_user -d ai_automation 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostgreSQL is ready" -ForegroundColor Green
} else {
    Write-Host "⚠️  PostgreSQL is still starting up" -ForegroundColor Yellow
}

# Test Redis connection
Write-Host "🔗 Testing Redis connection..." -ForegroundColor Yellow
$redisTest = docker exec ai-automation-redis redis-cli -a redis_password_2024 ping 2>$null
if ($redisTest -eq "PONG") {
    Write-Host "✅ Redis is ready" -ForegroundColor Green
} else {
    Write-Host "⚠️  Redis is still starting up" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Docker setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Available Services:" -ForegroundColor Cyan
Write-Host "  PostgreSQL:     localhost:5432" -ForegroundColor White
Write-Host "  Redis:          localhost:6379" -ForegroundColor White
Write-Host "  PgAdmin:        http://localhost:8080" -ForegroundColor White
Write-Host "  Redis UI:       http://localhost:8081" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Database Credentials:" -ForegroundColor Cyan
Write-Host "  Database: ai_automation" -ForegroundColor White
Write-Host "  User:     automation_user" -ForegroundColor White
Write-Host "  Password: automation_password_2024" -ForegroundColor White
Write-Host ""
Write-Host "🔑 PgAdmin Login:" -ForegroundColor Cyan
Write-Host "  Email:    admin@automation.com" -ForegroundColor White
Write-Host "  Password: admin_password_2024" -ForegroundColor White
Write-Host ""
Write-Host "⚡ Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Update your OpenAI API key in queue/.env" -ForegroundColor White
Write-Host "  2. Run: npm run start-dev" -ForegroundColor White
Write-Host "  3. Access the app at http://localhost:3000" -ForegroundColor White 