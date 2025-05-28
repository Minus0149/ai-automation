# AI Web Automation Agent - Docker Setup Guide

This guide shows you how to run the AI Web Automation Agent with persistent Docker containers for Redis and PostgreSQL.

## 🚀 Quick Start

### 1. Prerequisites

- **Docker Desktop** installed and running
- **Node.js** (v18+)
- **Python** (3.8+)
- **OpenAI API Key**

### 2. One-Command Setup

```bash
npm run setup
```

This command will:

- ✅ Set up Docker containers (PostgreSQL + Redis)
- ✅ Create persistent data volumes
- ✅ Copy environment files from examples
- ✅ Test all connections

### 3. Add Your OpenAI API Key

Edit `queue/.env` and replace:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

With your actual key from [OpenAI Platform](https://platform.openai.com/account/api-keys)

### 4. Start the Application

```bash
npm run start-dev
```

## 📊 Docker Services

The setup creates these persistent containers:

| Service             | Port | Purpose                | Credentials                                    |
| ------------------- | ---- | ---------------------- | ---------------------------------------------- |
| **PostgreSQL**      | 5432 | Main database          | `automation_user` / `automation_password_2024` |
| **Redis**           | 6379 | Job queue & caching    | Password: `redis_password_2024`                |
| **PgAdmin**         | 8080 | Database management UI | `admin@automation.com` / `admin_password_2024` |
| **Redis Commander** | 8081 | Redis management UI    | Auto-configured                                |

## 🔧 Docker Commands

```bash
# Setup everything
npm run setup

# Start containers
npm run docker:up

# Stop containers
npm run docker:down

# Restart containers
npm run docker:restart

# View logs
npm run docker:logs

# Clean everything (removes data)
npm run docker:clean
```

## 🎯 Application Commands

```bash
# Start full application with Docker
npm run start-dev

# Start with auto Docker setup
npm run start-with-docker

# Development mode (all services)
npm run dev

# Test system health
npm run test-system
```

## 🗄️ Data Persistence

Your data is persisted in Docker volumes:

- `postgres_data` - All database records
- `redis_data` - Queue state and cache
- `pgadmin_data` - PgAdmin settings

Data survives container restarts but will be lost with `npm run docker:clean`.

## 🔍 Monitoring & Management

### Database (PgAdmin)

1. Go to http://localhost:8080
2. Login: `admin@automation.com` / `admin_password_2024`
3. Add server connection:
   - Host: `ai-automation-postgres`
   - Port: `5432`
   - Database: `ai_automation`
   - Username: `automation_user`
   - Password: `automation_password_2024`

### Redis (Redis Commander)

1. Go to http://localhost:8081
2. Browse Redis data, monitor queues

## 📝 Database Schema

The system automatically creates these tables:

### `automation_tasks`

- Task management and results
- Generated code storage
- Execution history

### `automation_logs`

- Detailed execution logs
- Error tracking
- Performance metrics

## 🔄 Development Workflow

1. **Initial Setup**:

   ```bash
   npm run setup
   # Edit queue/.env with your OpenAI key
   npm run start-dev
   ```

2. **Daily Development**:

   ```bash
   npm run start-dev  # Auto-starts containers if needed
   ```

3. **Reset Everything**:
   ```bash
   npm run docker:clean  # Removes all data
   npm run setup         # Fresh setup
   ```

## 🛠️ Troubleshooting

### Container Issues

```bash
# Check container status
docker ps

# View specific container logs
docker logs ai-automation-postgres
docker logs ai-automation-redis

# Restart specific container
docker restart ai-automation-postgres
```

### Connection Issues

```bash
# Test database connection
docker exec ai-automation-postgres pg_isready -U automation_user -d ai_automation

# Test Redis connection
docker exec ai-automation-redis redis-cli -a redis_password_2024 ping
```

### Environment Issues

```bash
# Validate environment setup
npm run test-system

# Fix common issues
npm run fix-all
```

## 📈 Production Deployment

For production, update the passwords in:

- `docker-compose.yml`
- `env.example`
- `queue/queue-env.example`

Generate secure passwords and update all references consistently.

## 🔐 Security Notes

- Default passwords are for development only
- Change all passwords for production
- Use environment-specific `.env` files
- Never commit actual API keys to version control

## 🎉 Success Indicators

When everything works correctly, you should see:

- ✅ All containers running (`docker ps`)
- ✅ Database ready (PgAdmin accessible)
- ✅ Redis ready (Redis Commander accessible)
- ✅ Frontend at http://localhost:3000
- ✅ Worker at http://localhost:8000
- ✅ Queue processing Redis jobs
