# 🧠 Enhanced Selenium Automation with Multi-Model LangChain

A powerful web automation system that combines Selenium with multi-model LangChain AI for intelligent automation, dynamic page analysis, and complete project generation. Now supports OpenAI, Anthropic, Google, Ollama, and Hugging Face models.

## ✨ Features

### 🎯 Core Capabilities

- **Multi-Model LangChain AI**: Support for OpenAI GPT, Claude, Gemini, Ollama, and Hugging Face models
- **Dynamic Model Switching**: Change AI models on-the-fly through the UI
- **Dynamic Page Analysis**: Real-time page structure understanding and adaptation
- **Complete Project Generation**: Creates full automation projects with code, tests, and documentation
- **StackBlitz-like Interface**: Professional file explorer with syntax highlighting
- **Real-time Code Viewer**: Live code display with copy/download functionality

### 🤖 Supported AI Models

- **OpenAI**: GPT-4, GPT-3.5-turbo, and legacy models
- **Anthropic**: Claude-3 (Opus, Sonnet, Haiku), Claude-2
- **Google**: Gemini Pro, Gemini Pro Vision
- **Ollama**: Local models (Llama2, Mistral, CodeLlama, etc.)
- **Hugging Face**: Various open-source models

### 🔧 Automation Tools

- **Smart Navigation**: Context-aware page navigation
- **Element Interaction**: Click, fill, extract with AI-powered selectors
- **Form Handling**: Intelligent form detection and completion
- **Multi-page Workflows**: Complex automation sequences
- **Error Recovery**: Automatic retry and adaptation mechanisms

### 📁 Project Generation

- **Complete Structures**: Full project scaffolding with proper architecture
- **Multiple Frameworks**: Support for Selenium and SeleniumBase
- **Documentation**: Auto-generated README and code comments
- **Configuration**: Docker, requirements, and setup files
- **Best Practices**: Following industry standards and patterns

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Chrome Browser** (for Selenium)
- **AI API Keys** (at least one of: OpenAI, Anthropic, Google, or local Ollama)

### Installation & Startup

1. **Clone and setup**:

   ```bash
   git clone <repository>
   cd selenium-automation
   ```

2. **Configure environment**:

   Copy `env.example` to `.env` and add your API keys:

   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Start the system**:

   ```bash
   # Windows
   start.bat

   # Linux/Mac
   chmod +x start.sh && ./start.sh
   ```

4. **Access the application**:
   - 🌐 **Frontend**: http://localhost:3000
   - 🔧 **Worker API**: http://localhost:8000
   - 📊 **Health Check**: http://localhost:8000/health

### Configuration

Create a `.env` file with your preferred AI model:

```env
# AI Model Configuration
AI_MODEL_PROVIDER=openai
AI_MODEL_NAME=gpt-3.5-turbo

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google Configuration (optional)
GOOGLE_API_KEY=your_google_api_key_here

# Ollama Configuration (for local models)
OLLAMA_BASE_URL=http://localhost:11434

# Hugging Face Configuration (optional)
HUGGINGFACE_API_TOKEN=your_huggingface_token_here

# LangChain Configuration (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key_here
```

## 🏗️ Simplified Architecture

```
selenium-automation/
├── 📱 frontend/                    # Next.js Frontend
│   ├── app/
│   │   ├── api/
│   │   │   ├── tasks/             # Task execution APIs
│   │   │   └── models/            # Model management API
│   │   └── page.tsx               # Main interface
│   ├── components/
│   │   ├── EnhancedAutomationForm.tsx  # Main form
│   │   ├── ModelSelector.tsx           # AI model selector
│   │   ├── FileExplorer.tsx            # StackBlitz-like explorer
│   │   └── CodeViewer.tsx              # Syntax highlighted viewer
│   └── package.json
│
├── 🐍 worker/                      # Python LangChain Worker
│   ├── main.py                    # FastAPI server with lifespan events
│   ├── enhanced_langchain_executor.py  # Multi-model LangChain executor
│   ├── selenium_executor.py       # Basic Selenium executor
│   ├── dynamic_executor.py        # Dynamic automation executor
│   └── requirements.txt           # Updated with multi-model deps
│
├── env.example                    # Environment configuration template
├── docker-compose.yml             # Simplified Docker setup
├── start.bat                      # Windows startup script
└── README.md
```

## 🎮 Usage Guide

### Model Selection

1. **Choose AI Model**: Use the model selector in the form to pick your preferred AI provider and model
2. **Switch Models**: Change models anytime through the dropdown interface
3. **Model Status**: View current model status and availability

### Basic Automation

1. Select your preferred AI model from the dropdown
2. Enter target URL and automation goal
3. Choose automation framework (Selenium or SeleniumBase)
4. Click "Start Enhanced Automation"
5. Watch real-time progress and results
6. View generated project structure

### Advanced Features

- **Custom Instructions**: Provide specific automation requirements
- **Multi-step Workflows**: Chain multiple automation tasks
- **Code Generation**: Get complete automation projects with AI assistance
- **Error Handling**: Automatic retry and adaptation
- **Model Switching**: Change AI models mid-workflow

### Generated Projects

Projects include:

- 📄 **Main automation script** (AI-generated)
- 🧪 **Test files and test data**
- 📋 **Requirements and dependencies**
- 🐳 **Docker configuration**
- 📖 **Documentation and README**
- ⚙️ **Configuration files**

## 🔧 API Endpoints

### Worker API (Port 8000)

- `POST /execute-enhanced` - Enhanced automation with AI
- `GET /models/available` - Get available AI models
- `POST /models/switch` - Switch AI model
- `GET /status` - Worker and model status
- `GET /health` - Health check

### Frontend API (Port 3000)

- `POST /api/tasks/enhanced` - Enhanced automation proxy
- `GET /api/models` - Model management proxy
- `POST /api/models` - Model switching proxy

## 🛠️ Technology Stack

### Backend

- **FastAPI**: High-performance async API framework with lifespan events
- **LangChain**: Multi-model AI integration and agent orchestration
- **Multi-Model Support**: OpenAI, Anthropic, Google, Ollama, Hugging Face
- **Selenium**: Web automation and browser control

### Frontend

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Lucide Icons**: Modern icon library

### Infrastructure

- **Docker**: Simplified containerization
- **ChromaDB**: Vector database for AI memory (optional)
- **Chrome WebDriver**: Browser automation

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**:

   ```bash
   cd worker
   pip install -r requirements.txt
   ```

2. **Model Issues**:

   - Verify API keys in `.env` file
   - Check model availability in the UI
   - Try switching to a different model

3. **Port Conflicts**:

   - Worker auto-detects available ports (8000-8010)
   - Change frontend port in `package.json` if needed

4. **Chrome Driver Issues**:
   - System will auto-download compatible version
   - Ensure Chrome browser is installed

### Model-Specific Issues

**OpenAI**:

- Check API quota and billing
- Verify API key format

**Anthropic**:

- Ensure you have access to Claude API
- Check rate limits

**Google**:

- Enable Gemini API in Google Cloud Console
- Verify API key permissions

**Ollama**:

- Ensure Ollama is running locally
- Check model availability with `ollama list`

**Hugging Face**:

- Verify HF token permissions
- Check model download requirements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain**: For the powerful AI/ML framework
- **OpenAI**: For GPT-4 and AI capabilities
- **Selenium**: For web automation foundation
- **Next.js**: For the modern frontend framework

---

**🎯 Ready to automate? Start with `start.bat` and experience intelligent web automation!**
