# AI Web Automation Agent with Multi-Model Support & Chat

A powerful web automation tool that uses **Gemini 2.0 Flash** and **OpenAI GPT** models to generate and execute Selenium WebDriver scripts for any website, with intelligent chat assistance for debugging failed automations.

## 🌟 Key Features

### Multi-Model AI Support

- **Gemini 2.0 Flash**: Primary AI with enhanced website analysis and context caching
- **OpenAI GPT-4o Mini**: Backup AI with reliable code generation
- **Auto-fallback**: Seamlessly switches between models if one fails
- **Model Selection**: Choose your preferred AI model for each task

### Intelligent Chat Assistance

- **Post-failure Chat**: After 3 failed attempts, engage with AI to debug issues
- **Context-aware Responses**: AI understands your task, website, and failure reasons
- **Guided Refinement**: Get specific suggestions to improve automation
- **Continue with Fixes**: Apply AI suggestions and retry automation

### Advanced Automation

- **Smart Website Analysis**: Extracts forms, buttons, links, and interactive elements
- **Reliable Selectors**: Prioritizes ID > Name > Class > Tag for element selection
- **Error Handling**: Comprehensive try-catch blocks and graceful degradation
- **Screenshot Capture**: Automatic screenshots on failures for debugging
- **Retry Logic**: Exponential backoff with up to 3 attempts per task

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- PostgreSQL database
- Chrome browser (for Selenium)

### Installation

1. **Clone and setup:**

```bash
git clone <repository-url>
cd selenium-automation
npm install
```

2. **Configure environment:**

```bash
# Copy and configure environment files
cp queue/queue-env.example queue/.env
cp frontend/.env.example frontend/.env

# Add your AI API keys
nano queue/.env  # Add GEMINI_API_KEY and/or OPENAI_API_KEY
```

3. **Setup database:**

```bash
# Create PostgreSQL database and run migrations
npm run db:setup
```

4. **Start all services:**

```bash
npm run dev  # Starts frontend, queue processor, and worker
```

## 🔧 Configuration

### AI Model Configuration

**Gemini 2.0 Flash (Enhanced Performance)**

```env
GEMINI_API_KEY=your-api-key-from-google-ai-studio
GEMINI_2_0_MODEL=gemini-2.0-flash-exp
GEMINI_2_0_USE_CONTEXT_CACHING=true
```

**Gemini 2.5 Preview (Latest Experimental)**

```env
GEMINI_API_KEY=your-api-key-from-google-ai-studio
GEMINI_2_5_MODEL=gemini-2.5-flash-exp
GEMINI_2_5_USE_CONTEXT_CACHING=false
```

**GPT-4o Mini (Default & Reliable)**

```env
OPENAI_API_KEY=your-api-key-from-openai
OPENAI_MODEL=gpt-4o-mini
DEFAULT_MODEL=gpt-4o-mini
```

### Service Configuration

```env
QUEUE_PORT=3002          # Queue processor port
WORKER_URL=http://localhost:8000
DB_HOST=localhost
```

## 📖 Usage Guide

### 1. Creating Automation Tasks

1. **Select AI Model**: Choose between Gemini or OpenAI
2. **Enter Website URL**: Any publicly accessible website
3. **Describe Task**: Natural language description of what to automate
4. **Submit**: Task will be queued and processed automatically

**Example Tasks:**

- "Fill out the contact form with test data and submit"
- "Search for 'selenium automation' and click the first result"
- "Navigate to the pricing page and click the 'Get Started' button"
- "Find and click all social media links"

### 2. Monitoring Task Progress

- **Real-time Status**: See current attempt number and progress
- **Live Updates**: Task status updates every 2 seconds
- **Attempt Details**: View generated code, execution results, and errors
- **Screenshots**: Automatic capture on failures for debugging

### 3. Chat-Assisted Debugging

When a task fails after 3 attempts:

1. **Chat Interface Activates**: Ask AI for help debugging the automation
2. **Contextual Assistance**: AI knows your task details, website, and error messages
3. **Get Suggestions**: Receive specific advice to fix the automation
4. **Apply Fixes**: Use "Continue with AI Suggestions" to retry with improvements

**Chat Examples:**

- "Why did the form submission fail?"
- "How can I make the element selection more reliable?"
- "The button click isn't working, what should I try?"

### 4. Advanced Features

**Model Comparison**

- Try the same task with different AI models
- Compare code quality and success rates
- Use chat with either Gemini or OpenAI

**Error Recovery**

- Automatic retry with exponential backoff
- Intelligent error analysis and suggestions
- Progressive refinement through chat interaction

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Queue          │    │  Worker         │
│   (Next.js)     │────│  Processor      │────│  (Python)       │
│   Port 3001     │    │  Port 3002      │    │  Port 8000      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                        ┌─────────────────┐
                        │   PostgreSQL    │
                        │   Database      │
                        └─────────────────┘
```

## 🤖 AI Model Comparison

| Feature              | Gemini 2.0 Flash     | Gemini 2.5 Preview      | GPT-4o Mini             |
| -------------------- | -------------------- | ----------------------- | ----------------------- |
| **Website Analysis** | ⭐⭐⭐⭐⭐ Enhanced  | ⭐⭐⭐⭐⭐ Advanced     | ⭐⭐⭐⭐ Good           |
| **Context Caching**  | ✅ Yes               | ❌ No                   | ❌ No                   |
| **Speed**            | ⚡ Very Fast         | ⚡ Fast                 | ⚡ Very Fast            |
| **Cost**             | 💰 Lower             | 💰 Moderate             | 💰 Low                  |
| **Code Quality**     | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Cutting-edge | ⭐⭐⭐⭐ Very Good      |
| **Reliability**      | ⭐⭐⭐⭐ High        | ⭐⭐⭐ Experimental     | ⭐⭐⭐⭐⭐ Very High    |
| **Chat Quality**     | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Advanced     | ⭐⭐⭐⭐⭐ Excellent    |
| **Best For**         | Production use       | Experimental features   | Default reliable choice |

## 🔍 Troubleshooting

**Common Issues:**

1. **Port Conflicts**

   - Queue processor auto-selects available ports
   - Check `QUEUE_PORT` environment variable

2. **AI Model Errors**

   - Verify API keys are correctly set
   - Check API quotas and billing
   - System will auto-fallback to available model

3. **Database Connection**

   - Ensure PostgreSQL is running
   - Verify database credentials in `.env`

4. **Chrome/Selenium Issues**
   - Install Chrome browser
   - Worker auto-manages ChromeDriver

**Enable Debug Logging:**

```env
LOG_LEVEL=debug
NODE_ENV=development
```

## 🚀 Production Deployment

### Environment Configuration

```env
NODE_ENV=production
CORS_ORIGINS=https://yourdomain.com
DB_HOST=your-production-db-host
LOG_LEVEL=info
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Monitoring

- Health check endpoints: `/health`
- Queue status: `/queue/status`
- Model availability: `/models`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini 2.0 Flash** for advanced AI capabilities
- **OpenAI** for reliable language model support
- **Selenium WebDriver** for web automation
- **Next.js** for the modern frontend framework

---

🌟 **Ready to automate the web with AI?** Get started by configuring your API keys and creating your first automation task!
