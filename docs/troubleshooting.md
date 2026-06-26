# IndoClaw Web Interface - Troubleshooting Guide

## Common Issues

### 1. Web Interface Won't Start

**Symptoms:**
- Command fails immediately
- Error message about missing dependencies

**Solutions:**
```bash
# Reinstall dependencies
indoclaw web install

# Or manually
pip install fastapi uvicorn python-multipart websockets

# Check Python version
python --version
# Should be 3.10 or higher
```

### 2. Port Already in Use

**Symptoms:**
```
OSError: [Errno 98] Address already in use
```

**Solutions:**
```bash
# Use a different port
indoclaw web start --port 8080

# Or kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Check what's using the port
netstat -tulpn | grep 8000
```

### 3. Frontend Can't Connect to Backend

**Symptoms:**
- Frontend shows "Connection refused"
- Browser console shows CORS errors

**Solutions:**
```bash
# Ensure backend is running
indoclaw web start

# Check backend is listening
curl http://localhost:8000/api/health

# Check firewall settings
# Allow port 8000 through firewall
```

### 4. WebSocket Connection Fails

**Symptoms:**
- Frontend can't connect to WebSocket
- Repeated connection attempts

**Solutions:**
```bash
# Verify WebSocket endpoint
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: test" \
  http://localhost:8000/ws

# Check backend logs
# WebSocket route should be registered in main.py
```

### 5. Agent Not Responding

**Symptoms:**
- Chat messages sent but no response
- Agent appears idle

**Solutions:**
```bash
# Check IndoClaw configuration
cat ~/.indoclaw/settings.json

# Verify LLM provider is accessible
curl http://localhost:11434/v1/models

# Check agent is registered
indoclaw list-agents

# Check IndoClaw logs
tail -f ~/.indoclaw/logs/agent.log
```

### 6. Frontend Shows Empty Page

**Symptoms:**
- Page loads but content is missing
- No error messages in browser console

**Solutions:**
```bash
# Clear browser cache
# Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

# Check if frontend is running
curl http://localhost:3000

# Rebuild frontend
cd src/interfaces/web/client
npm run build
```

### 7. Configuration Changes Not Applied

**Symptoms:**
- Changes saved but not reflected
- Old configuration persists

**Solutions:**
```bash
# Restart backend
indoclaw web stop
indoclaw web start

# Or reload the page (Ctrl+R)

# Check configuration file
cat ~/.indoclaw/settings.json
```

### 8. Events Not Showing in Event Viewer

**Symptoms:**
- Event viewer shows no events
- Agent appears to be running

**Solutions:**
```bash
# Check event publisher is enabled
# Verify in src/core/events/publisher.py

# Check agent has event publisher configured
# Should be in agent initialization

# Verify WebSocket subscription
# Frontend should subscribe to events on connect
```

## Debugging

### Enabling Verbose Logging

```bash
# Backend with verbose logging
uvicorn main:app --reload --log-level debug

# Frontend with verbose logging
# Add to lib/ws-client.ts
console.log('WebSocket event:', data);
```

### Checking Logs

```bash
# Backend logs
tail -f ~/.indoclaw/web_logs/backend.log

# Frontend logs (browser console)
# Open developer tools in browser
```

## Performance Issues

### Slow Page Load

**Symptoms:**
- Pages take too long to load
- High latency in chat responses

**Solutions:**
```bash
# Clear browser cache
# Optimize images
# Use lazy loading for components
```

### High Memory Usage

**Symptoms:**
- System becomes slow
- Memory usage is high

**Solutions:**
```bash
# Limit event history
# Reduce WebSocket reconnection attempts
# Clear chat history periodically
```

## Development Issues

### Hot Reload Not Working

**Solutions:**
```bash
# Frontend
npm run dev

# Backend
uvicorn main:app --reload

# Ensure file watcher is enabled
```

### TypeScript Errors

**Solutions:**
```bash
# Install TypeScript
npm install --save-dev typescript

# Check tsconfig.json
# Run: npm run build to check for errors
```

### Python Import Errors

**Solutions:**
```bash
# Verify Python path
python -c "import sys; print(sys.path)"

# Install missing dependencies
pip install -e .
```

## Getting Help

### Check Documentation

- [README.md](README.md)
- [architecture.md](architecture.md)
- [getting-started.md](getting-started.md)

### Report Issues

When reporting issues, include:
- Operating system
- Python version
- Node.js version
- Steps to reproduce
- Error messages
- Logs
