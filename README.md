# IndoClaw - Autonomous AI Agent OS

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
│   ├── core/               # Core agent system
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

```bash
# Clone the repository
git clone https://github.com/your-username/indoclaw.git
cd indoclaw

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment example
cp src/config/.env.example src/config/.env

# Edit .env with your API keys
# OPENAI_API_KEY=your_api_key_here
# TAVILY_API_KEY=your_tavily_key_here (optional)
```

## Usage

### Command Line Interface

```bash
# Interactive chat mode
python -m src

# Single prompt
python -m src "What is 25 * 17?"

# Research mode
python -m src --research "Latest AI developments"

# Writing mode
python -m src --write "The future of technology" --format article
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
| `web_search` | Search the web using Tavily API |
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by OpenClaw's architecture
- Built with LangChain framework
- Uses LangGraph for state management
- Powered by OpenAI models

## Contact

Project Link: [https://github.com/your-username/indoclaw](https://github.com/your-username/indoclaw)
