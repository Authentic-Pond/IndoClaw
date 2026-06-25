# 🚀 IndoClaw - Autonomous AI Agent OS (Under Development)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Status](https://img.shields.io/badge/Status-Active%20Development-orange.svg)](https://github.com/Authentic-Pond/IndoClaw)

> **ACTIVE DEVELOPMENT** - IndoClaw is under active development. Features may change and new versions are released frequently.

---

IndoClaw is an open-source autonomous AI agent framework designed for:

- Multi-agent orchestration
- Tool execution
- Memory management
- Agent-to-agent communication
- Human-in-the-loop workflows
- Local-first deployment
- Cloud-native deployment
- Model-agnostic operation

---

## Features

- **Model Agnostic** - OpenAI, Ollama, vLLM, SGLang via adapter pattern
- **Multi-Agent Network** - Collaborating agents with structured messaging
- **Tool Registry** - Pluggable tools with Pydantic validation
- **Memory Systems** - Short-term (conversation) and long-term (vector embeddings)
- **Observability** - Thought tracing for debugging agent behavior
- **CLI Interface** - Rich terminal interface with prompt support
- **Workspace Management** - Multi-agent workspaces with persistent configurations
- **Agent Onboarding** - First-time setup wizard for easy configuration

---

## Architecture

IndoClaw follows a layered architecture:

### Layer 1: Core Runtime
- Agent lifecycle management
- Task execution
- Context management
- Event management

### Layer 2: Agent Engine
- Planning
- Reasoning
- Reflection
- Self-correction

### Layer 3: Memory System
- Short-term memory
- Long-term memory (ChromaDB)
- Episodic memory
- Semantic memory

### Layer 4: Tool System
- Tool registration
- Tool execution
- Permission checks
- Result validation

### Layer 5: Multi-Agent Network
- Agent communication
- Task delegation
- Collaboration
- Conflict resolution

### Layer 6: User Interfaces
- CLI
- REST API (future)
- Web UI (future)
- SDK (future)

---

## Installation

### Option 1: Install from PyPI (recommended)

```bash
pip install indoclaw
```

### Option 2: Install from source

```bash
# Clone the repository
git clone https://github.com/Authentic-Pond/IndoClaw.git
cd IndoClaw

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install IndoClaw
pip install -e .
```

### Option 3: Auto-Install (Recommended for development)

Run the auto-install script:

```bash
./install.sh
```

This script will:
- Create a virtual environment
- Install all dependencies
- Show you how to add IndoClaw to your PATH

### Adding `indoclaw` to PATH (Windows)

After installation, add the venv Scripts directory to your PATH:

```cmd
set PATH="%PATH%;C:\path\to\IndoClaw\venv\Scripts"
```

---

## Usage

### Command Line Interface (after installation)

```bash
# Interactive chat mode
indoclaw
indoclaw chat

# Single prompt with default agent
indoclaw "What is 25 * 17?"

# With specific agent
indoclaw agent "agent_name" "Hello how are you?"

# With agent and subcommand
indoclaw agent Serene research "Quantum computing"
indoclaw agent Writer write "AI trends" --format markdown

# Direct commands
indoclaw research "Latest AI developments"
indoclaw write "The future of technology" --format article

# Verbose mode
indoclaw -v

# List registered tools
indoclaw list-tools

# List registered agents
indoclaw list-agents

# View thought traces
indoclaw --trace
```

### Agent Management Commands

```bash
# First-time setup (onboard)
indoclaw onboard

# Setup agent
indoclaw setup [agent_name]

# Reset configuration
indoclaw reset

# Uninstall (remove configurations)
indoclaw uninstall
indoclaw uninstall --full

# Uninstall full installation (removes ~/.indoclaw)
indoclaw uninstall --full
```

### Examples

```bash
# Basic conversation with default agent
indoclaw "How can I improve my Python skills?"

# With specific agent
indoclaw agent "agent_name" "Hello how are you?"

# Research with web search
indoclaw research "Latest breakthroughs in quantum computing"

# Write an article
indoclaw write "The impact of AI on healthcare" --format article

# List available tools
indoclaw list-tools

# List registered agents
indoclaw list-agents

# Verbose mode with prompt
indoclaw -v "What is 25 * 17?"
```

### Programmatic Usage

```python
from src.core import (
    create_agent,
    tool_registry,
    get_agent_registry,
    get_tracer,
    ResearcherAgent,
    WriterAgent,
)

# Set up tracing
get_tracer().enabled = True

# Access tool registry
print(tool_registry.list_tools())

# Use a specialized agent
researcher = ResearcherAgent(verbose=True)
result = researcher.research("Quantum computing advances")
print(result.summary)

# Use writer
writer = WriterAgent(verbose=True)
result = writer.write("AI trends", format="article")
print(result.content)
```

---

## Configuration

Create a `.env` file in `src/config/`:

```env
# LLM Provider (choose one)
OPENAI_API_KEY=sk-...
# or
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434/v1

# Memory
SHORT_TERM_CAPACITY=10
LONG_TERM_TOP_K=5
VECTOR_DB_PATH=./data/chroma

# Tool Configuration
MAX_SEARCH_RESULTS=5

# Agent
MAX_ITERATIONS=10
VERBOSE=true
```

---

## Available Tools

| Tool | Description |
|------|-------------|
| `duckduckgo_search` | Web search using DuckDuckGo |
| `web_search` | Web search using Tavily API |
| `file_ops` | Read, write, list directories |
| `calculator` | Safe mathematical expressions |
| `llm_call` | LLM inference |

---

## Agent Types

### General Agent
- Reasoning → Action loop
- Tool selection
- Memory-aware

### Researcher Agent
- Deep web search
- Information synthesis
- Source tracking

### Writer Agent
- Content generation
- Format control
- Editing

---

## Memory System

### Short-Term Memory
- Current session context
- Recent interactions
- Active tasks

### Long-Term Memory
- Historical patterns
- Learned behaviors
- Key insights (via ChromaDB vector embeddings)

---

## Requirements

- Python 3.10+
- LangChain, LangGraph
- Pydantic
- ChromaDB (optional, for vector memory)

---

## Development

### Running Tests

All tests pass (62/62):

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_tools.py
pytest tests/test_messaging.py
pytest tests/test_memory.py
pytest tests/test_observation.py
```

### Project Structure

```
src/
├── agents/              # Agent implementations
├── core/               # Core framework
│   ├── adapters/       # LLM provider adapters
│   ├── memory/         # Memory providers
│   ├── messaging/      # Agent communication
│   ├── tools/          # Tool implementations
│   └── workspace/      # Agent workspace management
├── interfaces/         # CLI and other interfaces
└── models/             # Data models
```

---

## 🚧 Development Status

**MVP Complete** - All core features implemented:

1. ✅ Model Agnosticism (adapters for OpenAI/Ollama/vLLM)
2. ✅ Tool Registry (pluggable tools with auto-registration)
3. ✅ Agent Communication (AgentMessage, AgentRegistry, DelegationTool)
4. ✅ Persistence & Observability (BaseMemoryProvider, ThoughtTracer)

**Tests: 62 passing**

---

## Contributing

We welcome contributions! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/Authentic-Pond/IndoClaw.git
cd IndoClaw
./install.sh
# Or run: indoclaw --install

# Add to PATH (after installation):
export PATH="$PATH:$HOME/.indoclaw/venv/bin"
source ~/.bashrc   # or ~/.zshrc
```

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

### Apache License 2.0 Summary

- Free to use, modify, and distribute
- Must include original copyright notice
- Modifications must be documented
- Provider liability protection

---

## Acknowledgments

- Inspired by OpenClaw's architecture
- Built with LangChain framework
- Uses LangGraph for state management
- Powered by OpenAI, Ollama, and other LLM providers

---

## Contact

**Project:** [https://github.com/Authentic-Pond/IndoClaw](https://github.com/Authentic-Pond/IndoClaw)

**Support:** admin@indoclaw.in
