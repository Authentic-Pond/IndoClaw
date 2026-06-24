# 🚧 IndoClaw - Autonomous AI Agent OS (Under Development)

> **Note:** IndoClaw is currently under active development. The project is not yet ready for public release. We will announce when it's ready to go!

IndoClaw is an autonomous AI agent operating system inspired by OpenClaw, built with LangChain for powerful AI agent capabilities.

## Features

- **Autonomous Agent Architecture**: Perception → Reasoning → Action loop
- **Memory Systems**: Short-term (conversation history) and long-term (vector embeddings)
- **Tool Ecosystem**: Web search, file operations, calculations, and more
- **Specialized Agents**: Researcher, Writer, and general-purpose agents
- **CLI Interface**: Rich terminal interface with prompt support

## Architecture

```
IndoClaw/
├── src/
│   ├── core/              # Core agent system
│   │   ├── agent.py       # Main agent with perception-reasoning-action loop
│   │   ├── memory/        # Memory management
│   │   ├── planning/      # Task planning
│   │   └── tools/         # Available tools
│   ├── agents/            # Specialized agent implementations
│   │   ├── base.py        # Base agent class
│   │   ├── researcher.py  # Research-focused agent
│   │   └── writer.py      # Writing-focused agent
│   ├── interfaces/        # User interfaces
│   │   └── cli.py         # Command-line interface
│   └── config/            # Configuration management
│       └── settings.py    # Configuration class
├── tests/
├── requirements.txt
└── README.md
```

## Installation

### Option 1: Install from PyPI (recommended)

Once published to PyPI, you can install IndoClaw with:

```bash
pip install indoclaw
```

### Option 2: Install from source

```bash
# Clone the repository
git clone https://github.com/Authentic-Pond/IndoClaw.git
cd IndoClaw

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install as a package (development mode)
pip install -e .

# Copy environment example
cp src/config/.env.example src/config/.env

# Edit .env with your API keys
# OPENAI_API_KEY=your_api_key_here
# TAVILY_API_KEY=your_tavily_key_here (optional)
```

### Adding `indoclaw` to PATH (Windows)

After installation, the `indoclaw.exe` script is installed in Python's Scripts directory.
To run `indoclaw` from any directory, add the Scripts directory to your PATH:

1. Open **Settings** > **System** > **About** > **Advanced system settings**
2. Click **Environment Variables**
3. Under **User variables**, select **Path** and click **Edit**
4. Click **New** and add: `C:\Users\YOUR_USERNAME\AppData\Local\Python\pythonX.X\Scripts`
5. Click **OK** to save

Alternatively, you can run IndoClaw using:
```bash
python -m src
```
or
```bash
python -m src --help
```

## Usage

### Command Line Interface (after installation)

```bash
# Interactive chat mode
indoclaw

# Single prompt
indoclaw "What is 25 * 17?"

# Research mode
indoclaw --research "Latest AI developments"

# Writing mode
indoclaw --write "The future of technology" --format article

# Verbose mode
indoclaw -v

# Run chat mode explicitly
indoclaw --chat
```

### Agent Management Commands

```bash
# Configure first agent (onboarding)
indoclaw onboard

# Run with specific agent
indoclaw agent <agent_name>

# Reset (remove .indoclaw folder and all configurations)
indoclaw reset

# Uninstall (remove agent configurations only)
indoclaw uninstall

# Full uninstall (remove everything including .indoclaw folder)
indoclaw uninstall --full

# Setup wizard for specific agent
indoclaw setup <agent_name>
```

### Examples

```bash
# Configure IndoClaw
indoclaw onboard

# Run with default agent
indoclaw

# Run with "Max" agent
indoclaw agent Max

# Run with "Max" agent (alternative syntax)
indoclaw -a Max

# Run with prompt
indoclaw "What is your name?"

# Reset all configurations
indoclaw reset

# Uninstall agent configurations
indoclaw uninstall

# Full uninstall
indoclaw uninstall --full
```
```

### Programmatic Usage

```python
from src.core.agent import create_agent
from src.agents.researcher import ResearcherAgent
from src.agents.writer import WriterAgent

# Create a general-purpose agent
agent = create_agent(verbose=True)
result = agent.run("Solve this math problem: 123 * 456")
print(result.response)

# Use a specialized researcher agent
researcher = ResearcherAgent(verbose=True)
result = researcher.research("Quantum computing advances")
print(result.summary)

# Use a writer agent
writer = WriterAgent(verbose=True)
result = writer.write("Artificial Intelligence trends", format="article")
print(result.content)
```

### Programmatic Usage

```python
from src.core.agent import create_agent
from src.agents.researcher import ResearcherAgent
from src.agents.writer import WriterAgent

# Create a general-purpose agent
agent = create_agent(verbose=True)
result = agent.run("Solve this math problem: 123 * 456")
print(result.response)

# Use a specialized researcher agent
researcher = ResearcherAgent(verbose=True)
result = researcher.research("Quantum computing advances")
print(result.summary)

# Use a writer agent
writer = WriterAgent(verbose=True)
result = writer.write("Artificial Intelligence trends", format="article")
print(result.content)
```

## Configuration

Create a `.env` file in `src/config/`:

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096

# OpenAI-compatible API Base URL (for OpenAI or other providers)
OPENAI_API_BASE=https://api.openai.com/v1

# Ollama Configuration (uncomment and edit to use Ollama locally)
# OLLAMA_ENABLED=true
# OLLAMA_BASE_URL=http://localhost:11434/v1

# Memory Configuration
SHORT_TERM_CAPACITY=10
LONG_TERM_TOP_K=5
VECTOR_DB_PATH=./data/chroma
EMBEDDING_MODEL=text-embedding-3-small

# Tool Configuration
TAVILY_API_KEY=your_tavily_api_key
MAX_SEARCH_RESULTS=5
FILE_OPERATION_TIMEOUT=30

# Tool Display Configuration (controls CLI output)
SHOW_TOOL_CALLING=true
SHOW_THINKING=true

# Agent Configuration
AGENT_NAME=IndoClaw
AGENT_ROLE=Autonomous AI Assistant
MAX_ITERATIONS=10
VERBOSE=true

# System Configuration
LOG_LEVEL=INFO
DATA_DIR=./data
CACHE_DIR=./data/cache
```

## Available Tools

| Tool | Description |
|------|-------------|
| `duckduckgo_search` | Web search using DuckDuckGo (default) |
| `file_ops` | Read, write, list directories |
| `calculator` | Safe mathematical expression evaluation |
| `llm_call` | LLM inference via LangChain |

## Agent Types

### General Agent
- Perception → Reasoning → Action loop
- Uses multiple tools dynamically
- Memory-aware conversation

### Researcher Agent
- Deep web search and analysis
- Information synthesis
- Source tracking

### Writer Agent
- Content generation (articles, reports)
- Format control (markdown, html, etc.)
- Editing capabilities

## Memory System

### Short-Term Memory
- Conversation history
- Configurable capacity
- Context-aware retrieval

### Long-Term Memory
- Vector embeddings for semantic search
- Persistent storage
- Automatic knowledge retrieval

## Requirements

- Python 3.10+
- OpenAI API Key (or compatible provider)
- Tavily API Key (for web search - optional)

## Development

```bash
# Run tests
pytest tests/

# Lint
flake8 src/

# Type check
mypy src/
```

## 🚧 Development Status

**Status:** Active Development

This project is currently under active development and is not yet ready for public release. We're working hard to bring you a stable and powerful autonomous AI agent operating system.

**Stay Updated:** Follow our repository for updates and announcements when IndoClaw is ready for its first release!

## Contributing

We welcome contributions! Once the project is more stable, please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---
**Apache License 2.0 Summary:**

- Free to use, modify, and distribute
- Must include original copyright notice
- Changes must be documented
- No trademark license granted

## Acknowledgments

- Inspired by OpenClaw's architecture
- Built with LangChain framework
- Uses LangGraph for state management
- Powered by OpenAI models

## Contact

Project Link: [https://github.com/Authentic-Pond/IndoClaw](https://github.com/Authentic-Pond/IndoClaw)

## Contact

For support or inquiries, contact us at: **admin@indoclaw.in**
