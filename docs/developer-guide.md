# IndoClaw Web Interface - Developer Guide

## Development Setup

### Frontend Development

```bash
# Navigate to the client directory
cd src/interfaces/web/client

# Install dependencies
npm install

# Start development server
npm run dev

# The server runs on http://localhost:3000
```

### Backend Development

```bash
# Navigate to the server directory
cd src/interfaces/web/server

# Install dependencies
pip install -r requirements.txt

# Start development server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Both Together

```bash
# Terminal 1: Start backend
cd src/interfaces/web/server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd src/interfaces/web/client
npm run dev
```

## Development Workflow

### Making Changes to the Frontend

1. Make your changes in `src/interfaces/web/client/`
2. The dev server auto-reloads on file changes
3. Check the browser console for errors
4. Refresh if auto-reload doesn't trigger

### Making Changes to the Backend

1. Make your changes in `src/interfaces/web/server/`
2. The uvicorn server auto-reloads on file changes
3. Check the terminal for errors
4. Test API endpoints with curl or a REST client

## Adding New Features

### Adding a New Page

1. Create a new directory in `app/`:
```bash
mkdir -p src/interfaces/web/client/app/new-feature
touch src/interfaces/web/client/app/new-feature/page.tsx
```

2. Add the page component:
```typescript
// app/new-feature/page.tsx
export default function NewFeaturePage() {
  return <div>New Feature Page</div>
}
```

3. Add navigation link in the Sidebar component:
```typescript
// components/layout/Sidebar.tsx
const navItems = [
  // ... existing items
  { id: "/new-feature", icon: YourIcon, label: "New Feature" },
]
```

### Adding a New API Endpoint

1. Create a route handler:
```python
# routers/new_feature.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/new-feature")
async def get_new_feature():
    return {"message": "Hello from new feature"}

@router.post("/new-feature")
async def create_new_feature(data: dict):
    return {"status": "created"}
```

2. Register the router in main.py:
```python
# main.py
from routers.new_feature import router as new_feature_router

app.include_router(new_feature_router, prefix="/api", tags=["new-feature"])
```

### Adding a New WebSocket Event

1. Define the event in ws_handler.py:
```python
# ws_handler.py
class EventType(Enum):
    NEW_EVENT = "new_event"

async def broadcast_new_event(agent_id: str, payload: dict):
    event = AgentEvent(
        event_type="new_event",
        timestamp=datetime.now().isoformat(),
        agent_id=agent_id,
        payload=payload
    )
    await ws_manager.broadcast(event)
```

2. Emit the event from your code:
```python
# From anywhere in your code
await broadcast_new_event(agent_id, {"data": "value"})
```

3. Listen for the event in the frontend:
```typescript
// In your component
useEffect(() => {
  wsClient.subscribe(['new_event']);
  
  const handler = (data: any) => {
    console.log('New event:', data);
  };
  
  wsClient.on('event', handler);
  
  return () => {
    wsClient.off('event', handler);
    wsClient.unsubscribe(['new_event']);
  };
}, []);
```

## Code Style

### Frontend

- Use TypeScript
- Follow React best practices
- Use functional components with hooks
- Use Tailwind CSS for styling
- Import from `@/lib` using TypeScript path aliases

### Backend

- Use Python 3.10+ features
- Follow PEP 8 style guide
- Use Pydantic for data validation
- Use type hints throughout

## Testing

### Frontend Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage
```

### Backend Testing

```bash
# Run tests
pytest tests/

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=. --cov-report=html tests/
```

## Debugging

### Frontend Debugging

1. Open browser developer tools
2. Check the Console tab for errors
3. Check the Network tab for API calls
4. Use React DevTools for component inspection

### Backend Debugging

1. Use Python logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. Use print statements for quick debugging
3. Use the Python debugger:
```python
import pdb; pdb.set_trace()
```

4. Log to a file:
```python
logging.basicConfig(filename='app.log', level=logging.DEBUG)
```

## Environment Variables

### Frontend

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Backend

```env
# .env
INDOCLAW_CONFIG_PATH=~/.indoclaw/settings.json
LOG_LEVEL=DEBUG
```

## Common Development Tasks

### Adding a New UI Component

1. Create the component file:
```bash
touch src/interfaces/web/client/components/ui/Button.tsx
```

2. Implement the component:
```typescript
// components/ui/Button.tsx
import { cva, type VariantProps } from "class-variance-authority"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

3. Use the component:
```typescript
import { Button } from "@/components/ui/Button"

<Button variant="primary" size="lg">Click me</Button>
```

### Modifying the Sidebar

1. Edit `components/layout/Sidebar.tsx`
2. Add new navigation items to `navItems`
3. Add agent logic as needed

### Updating API Routes

1. Edit the appropriate router file in `routers/`
2. Add new endpoints with proper decorators
3. Ensure proper validation with Pydantic models

## Deployment

### Building for Production

```bash
# Build the frontend
cd src/interfaces/web/client
npm run build

# The frontend is now at src/interfaces/web/client/.next/
```

### Running in Production

```bash
# Start the backend with production settings
cd src/interfaces/web/server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Contributing

1. Create a new branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `pytest tests/ && npm test`
4. Commit your changes: `git commit -m 'Add some feature'`
5. Push to your branch: `git push origin feature/your-feature`
6. Open a Pull Request

## Troubleshooting Development Issues

### Frontend Not Loading

- Check if the backend is running on port 8000
- Check browser console for errors
- Check network tab for failed API calls

### Backend Not Starting

- Check if port 8000 is already in use
- Check Python dependencies are installed
- Review error logs

### WebSocket Not Connecting

- Check backend WebSocket endpoint is running
- Check CORS settings
- Verify WebSocket URL in frontend code

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [React Documentation](https://react.dev/)
