# IndoClaw Web Interface - Getting Started Guide

## Prerequisites

Before starting, ensure you have:
- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn

## Installation

### Option 1: Using pip

```bash
# Clone the repository
git clone https://github.com/Authentic-Pond/IndoClaw.git
cd IndoClaw

# Install IndoClaw with web interface
pip install -e .
```

### Option 2: Using Auto-Install

```bash
# Run the auto-install script
./install.sh
# or
indoclaw --install
```

### Option 3: Manual Installation

```bash
# Install Python dependencies
pip install fastapi uvicorn python-multipart websockets

# Install frontend dependencies
cd src/interfaces/web/client
npm install
```

## First-Time Setup

1. **Configure IndoClaw**

```bash
# Run the setup wizard
indoclaw onboard

# Or configure an agent directly
indoclaw setup
```

2. **Start the Web Interface**

```bash
# Start the web interface server
indoclaw web start

# Or specify a custom port
indoclaw web start --port 3000
```

3. **Access the Web Interface**

Open your browser and navigate to:
```
http://localhost:8000
```

## Usage

### Dashboard

The dashboard shows:
- Quick stats overview
- Agent grid with status
- Quick navigation cards

### Chat

1. Click "Chat" in the sidebar
2. Type your message in the input box
3. Press Enter or click Send
4. View the agent's response

### Agent Management

1. Click "Agents" in the sidebar
2. View all configured agents
3. Click an agent to start a chat
4. Click the settings icon for agent details
5. Click the trash icon to delete an agent

### Configuration

1. Click "Configuration" in the sidebar
2. Navigate to the tab you want to modify
3. Make your changes
4. Click "Save Changes"

### Event Viewer

1. Click "Events" in the sidebar
2. View real-time events
3. Use the dropdown to filter by event type
4. Click the refresh icon to update
5. Click the trash icon to clear history

## Common Tasks

### Start the Web Interface on a Different Port

```bash
indoclaw web start --port 8080
```

### Stop the Web Interface

```bash
indoclaw web stop
```

### Reinstall Dependencies

```bash
indoclaw web install
```

### View Logs

```bash
# Check backend logs
tail -f ~/.indoclaw/web_logs/backend.log
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
# Use a different port
indoclaw web start --port 8080

# Or kill the process using the port
lsof -ti:8000 | xargs kill -9
```

### Dependency Errors

```bash
# Reinstall Python dependencies
pip install -e .

# Reinstall frontend dependencies
cd src/interfaces/web/client
npm install
```

### Connection Refused

Make sure the backend is running:

```bash
# Check if port 8000 is listening
netstat -tulpn | grep 8000

# Start the backend manually
indoclaw web start
```

### Agent Not Responding

1. Check that IndoClaw is configured:
```bash
indoclaw list-agents
```

2. Check configuration:
```bash
# Verify settings
cat ~/.indoclaw/settings.json
```

3. Check LLM provider is accessible:
```bash
# Test Ollama
curl http://localhost:11434/v1/models
```

## Next Steps

1. **Customize Configuration**: Modify agent settings in the Configuration panel
2. **Add More Agents**: Use the Agents page to create additional agents
3. **Explore Events**: Monitor agent activity in the Events viewer
4. **Read Documentation**: See [architecture.md](../architecture.md) for deeper understanding

## Getting Help

- Check the logs: `~/.indoclaw/logs/`
- Review the documentation in the `docs/` folder
- Open an issue on GitHub if you encounter bugs
