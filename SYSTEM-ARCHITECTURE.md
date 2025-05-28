# AI Web Automation Agent - System Architecture

## 🏗️ System Overview

The AI Web Automation Agent is a distributed system that uses AI to generate and execute web automation tasks. It consists of multiple services working together to provide a complete automation solution.

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AI Web Automation Agent                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐             │
│  │   Frontend      │    │  Queue          │    │  Python Worker │             │
│  │   (Next.js)     │    │  Processor      │    │  (FastAPI)      │             │
│  │   Port: 3000    │    │  (Node.js)      │    │  Port: 8000     │             │
│  │                 │    │  Port: 3002     │    │                 │             │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘             │
│           │                       │                       │                     │
│           │                       │                       │                     │
│           └───────────────────────┼───────────────────────┘                     │
│                                   │                                             │
│  ┌─────────────────────────────────┼─────────────────────────────────────────┐   │
│  │                    Data Layer   │                                         │   │
│  │                                 │                                         │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐       │   │
│  │  │   PostgreSQL    │    │     Redis       │    │   File System   │       │   │
│  │  │   Database      │    │     Queue       │    │   Screenshots   │       │   │
│  │  │   Port: 5432    │    │   Port: 6379    │    │   Logs & Temp   │       │   │
│  │  │                 │    │                 │    │                 │       │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        Management UIs                                   │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐              ┌─────────────────┐                   │   │
│  │  │    PgAdmin      │              │ Redis Commander │                   │   │
│  │  │   Port: 8080    │              │   Port: 8081    │                   │   │
│  │  │                 │              │                 │                   │   │
│  │  └─────────────────┘              └─────────────────┘                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        External Services                                │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐              ┌─────────────────┐                   │   │
│  │  │   OpenAI API    │              │   Chrome/       │                   │   │
│  │  │   GPT-4 Model   │              │   ChromeDriver  │                   │   │
│  │  │                 │              │                 │                   │   │
│  │  └─────────────────┘              └─────────────────┘                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Diagram

```
User Request → Frontend → Queue Processor → OpenAI → Python Worker → Results
     ↓             ↓            ↓             ↓           ↓            ↓
     │             │            │             │           │            │
     │             │            ├─ Database ──┤           │            │
     │             │            │             │           │            │
     │             │            ├─── Redis ───┤           │            │
     │             │            │             │           │            │
     │             │            │             │           ├─ Chrome ───┤
     │             │            │             │           │            │
     │             │            │             │           ├─ Screenshots
     │             │            │             │           │            │
     └─────────────┴────────────┴─────────────┴───────────┴────────────┘
                                    Results & Status Updates
```

## 🧩 Component Details

### 1. Frontend (Next.js) - Port 3000

**Purpose**: User interface for creating and monitoring automation tasks

**Technologies**:

- Next.js 15.3.2
- React with TypeScript
- Tailwind CSS for styling
- Server-side rendering

**Key Features**:

- Task creation form
- Real-time status monitoring
- Results visualization
- Screenshot gallery
- Task history

**Environment Variables**:

```bash
NEXT_PUBLIC_API_URL=http://localhost:3000
DATABASE_URL="postgresql://automation_user:automation_password_2024@localhost:5432/ai_automation"
REDIS_URL="redis://:redis_password_2024@localhost:6379"
```

### 2. Queue Processor (Node.js) - Port 3002

**Purpose**: Orchestrates job processing and manages the automation workflow

**Technologies**:

- Node.js with TypeScript
- BullMQ for Redis-based job queues
- Express.js for API endpoints
- PostgreSQL client (pg)

**Key Features**:

- Job queue management
- OpenAI integration
- Database operations
- Error handling and retries
- Logging and monitoring

**Environment Variables**:

```bash
OPENAI_API_KEY="your-openai-api-key"
DATABASE_URL="postgresql://automation_user:automation_password_2024@localhost:5432/ai_automation"
REDIS_URL="redis://:redis_password_2024@localhost:6379"
WORKER_URL=http://localhost:8000
```

### 3. Python Worker (FastAPI) - Port 8000

**Purpose**: Executes Selenium automation scripts in a sandboxed environment

**Technologies**:

- Python 3.8+
- FastAPI for REST API
- Selenium WebDriver
- Chrome/ChromeDriver
- Uvicorn ASGI server

**Key Features**:

- Selenium script execution
- Chrome browser automation
- Screenshot capture
- Error handling and timeouts
- Resource management

**Environment Variables**:

```bash
HOST=0.0.0.0
PORT=8000
HEADLESS=true
SCREENSHOT_DIR=./screenshots
MAX_EXECUTION_TIME=300
```

### 4. PostgreSQL Database - Port 5432

**Purpose**: Persistent storage for tasks, results, and logs

**Database Schema**:

```sql
-- Main tasks table
automation_tasks (
  id SERIAL PRIMARY KEY,
  task_id VARCHAR(255) UNIQUE,
  prompt TEXT,
  website_url VARCHAR(2048),
  status VARCHAR(50),
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  completed_at TIMESTAMP,
  generated_code TEXT,
  execution_result JSONB,
  error_message TEXT,
  screenshots JSONB,
  attempt_count INTEGER,
  max_attempts INTEGER,
  execution_time_ms INTEGER,
  user_id VARCHAR(255),
  session_id VARCHAR(255)
);

-- Logs table
automation_logs (
  id SERIAL PRIMARY KEY,
  task_id VARCHAR(255),
  level VARCHAR(20),
  message TEXT,
  timestamp TIMESTAMP,
  source VARCHAR(100)
);
```

**Credentials**:

- Database: `ai_automation`
- User: `automation_user`
- Password: `automation_password_2024`

### 5. Redis Cache/Queue - Port 6379

**Purpose**: Job queue management and caching

**Features**:

- BullMQ job queues
- Task status caching
- Session management
- Real-time updates

**Configuration**:

- Password: `redis_password_2024`
- Persistence: AOF enabled
- Memory optimization

### 6. Management UIs

#### PgAdmin - Port 8080

- Database administration
- Query execution
- Schema management
- Performance monitoring

**Login**:

- Email: `admin@automation.com`
- Password: `admin_password_2024`

#### Redis Commander - Port 8081

- Redis data browser
- Queue monitoring
- Cache management
- Real-time statistics

## 🔄 Workflow Process

### 1. Task Creation

```
User → Frontend → API → Queue Processor → Database
                                      ↓
                                   Redis Queue
```

### 2. Task Processing

```
Redis Queue → Queue Processor → OpenAI API → Generated Code
                    ↓                            ↓
                Database                   Python Worker
                    ↓                            ↓
              Status Updates              Selenium Execution
                    ↓                            ↓
                Frontend ← Results ← Screenshots ← Chrome
```

### 3. Result Storage

```
Python Worker → Queue Processor → Database → Frontend
      ↓               ↓              ↓          ↓
  Screenshots    Status Update   Persistence  Display
```

## 🚀 How to Run the System

### Prerequisites

```bash
# Required software
- Docker Desktop
- Node.js 18+
- Python 3.8+
- Git
```

### Quick Start

```bash
# 1. Clone and setup
git clone <repository>
cd selenium-automation

# 2. Setup Docker containers and environment
npm run setup

# 3. Add your OpenAI API key
# Edit queue/.env and add: OPENAI_API_KEY=sk-your-key-here

# 4. Start the system
npm run start-dev
```

### Manual Setup

```bash
# 1. Install dependencies
npm run install:all

# 2. Start Docker containers
npm run docker:up

# 3. Start services individually
npm run dev:frontend    # Port 3000
npm run dev:queue      # Port 3002
npm run dev:worker     # Port 8000
```

### Verification

```bash
# Test system health
npm run test-system

# Check container status
docker ps

# View logs
npm run docker:logs
```

## 📊 Service URLs

| Service        | URL                   | Purpose                |
| -------------- | --------------------- | ---------------------- |
| **Frontend**   | http://localhost:3000 | Main application UI    |
| **Queue API**  | http://localhost:3002 | Job management API     |
| **Worker API** | http://localhost:8000 | Selenium execution API |
| **PgAdmin**    | http://localhost:8080 | Database management    |
| **Redis UI**   | http://localhost:8081 | Redis monitoring       |

## 🔧 Configuration Files

### Docker Configuration

- `docker-compose.yml` - Container orchestration
- `docker/init.sql` - Database initialization

### Environment Files

- `.env` - Root configuration
- `queue/.env` - Queue processor settings
- `frontend/.env.local` - Frontend settings
- `worker/.env` - Python worker settings

### Package Management

- `package.json` - Root scripts and dependencies
- `queue/package.json` - Queue processor dependencies
- `frontend/package.json` - Frontend dependencies
- `worker/requirements.txt` - Python dependencies

## 🛠️ Development Commands

```bash
# Setup and Installation
npm run setup              # Complete setup
npm run install:all        # Install all dependencies

# Docker Management
npm run docker:up          # Start containers
npm run docker:down        # Stop containers
npm run docker:restart     # Restart containers
npm run docker:logs        # View logs
npm run docker:clean       # Clean everything

# Development
npm run start-dev          # Start with Docker check
npm run dev               # Start all services
npm run dev:frontend      # Frontend only
npm run dev:queue         # Queue only
npm run dev:worker        # Worker only

# Testing and Monitoring
npm run test-system       # System health check
npm run validate          # Environment validation
```

## 🔍 Monitoring and Debugging

### Logs Location

- **Queue Processor**: Console output + Database logs
- **Python Worker**: `./logs/worker.log`
- **Frontend**: Next.js console
- **Docker**: `docker logs <container-name>`

### Health Checks

```bash
# Database
docker exec ai-automation-postgres pg_isready -U automation_user -d ai_automation

# Redis
docker exec ai-automation-redis redis-cli -a redis_password_2024 ping

# Worker API
curl http://localhost:8000/health

# Queue API
curl http://localhost:3002/tasks
```

### Common Issues

1. **Port conflicts**: Check with `netstat -an | findstr :3000`
2. **Docker not running**: Start Docker Desktop
3. **Environment variables**: Run `npm run test-system`
4. **Database connection**: Check PgAdmin at localhost:8080

## 🔐 Security Considerations

### Development

- Default passwords for local development
- No SSL/TLS required
- CORS enabled for localhost

### Production

- Change all default passwords
- Enable SSL/TLS
- Restrict CORS origins
- Use environment-specific secrets
- Enable database SSL
- Use Redis AUTH

## 📈 Performance Optimization

### Scaling Options

- **Horizontal**: Multiple worker instances
- **Vertical**: Increase container resources
- **Database**: Connection pooling, read replicas
- **Redis**: Clustering, persistence tuning

### Resource Limits

- **Worker**: 512MB RAM, 80% CPU
- **Database**: Configurable connection pool
- **Redis**: Memory optimization enabled
- **Screenshots**: Automatic cleanup after 7 days

This architecture provides a robust, scalable foundation for AI-powered web automation with full data persistence and comprehensive monitoring capabilities.
