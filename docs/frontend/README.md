# IndoClaw Web Interface - Frontend Documentation

## Overview

The frontend is built with Next.js 14 using the App Router pattern. It's a Single Page Application (SPA) that communicates with the FastAPI backend via REST API and WebSocket.

## Project Structure

```
src/interfaces/web/client/
├── app/                              # Next.js App Router pages
│   ├── layout.tsx                    # Root layout
│   ├── page.tsx                      # Home/Dashboard
│   ├── globals.css                   # Global styles
│   ├── chat/                         # Chat interface
│   │   └── page.tsx
│   ├── agents/                       # Agent management
│   │   └── page.tsx
│   ├── config/                       # Configuration
│   │   └── page.tsx
│   └── events/                       # Event viewer
│       └── page.tsx
├── components/                       # React components
│   └── layout/
│       ├── Sidebar.tsx
│       └── MainLayout.tsx
├── lib/                              # Utility functions
│   └── ws-client.ts                  # WebSocket client
├── public/                           # Static assets
├── next.config.js                    # Next.js configuration
├── package.json                      # Dependencies
├── tailwind.config.js                # Tailwind configuration
├── postcss.config.json               # PostCSS configuration
└── tsconfig.json                     # TypeScript configuration
```

## Pages

### Dashboard (`/`)

The dashboard is the entry point showing:
- Quick stats (agents, tasks, memory)
- Agent grid with status indicators
- Quick navigation cards

```typescript
// Key features:
// - Fetches agents from backend
// - Shows status indicators (online/idle/busy)
// - Quick links to chat, events, agents, config
```

### Chat Interface (`/chat`)

The chat interface handles conversation with agents:
- Message history display
- Agent selection dropdown
- Input with keyboard shortcuts
- Loading states during agent response

```typescript
// Key features:
// - LocalStorage persistence of chat history
// - Real-time response display
// - Agent switching
// - Clear history button
```

### Agents Page (`/agents`)

Agent management interface:
- List of all configured agents
- Status indicators
- Actions (chat, delete)

```typescript
// Key features:
// - Grid layout for agents
// - Status badges (green/yellow/gray)
// - Delete confirmation
```

### Configuration Page (`/config`)

Configuration panel with tabbed interface:
- LLM Settings tab
- Memory Settings tab
- Agent Settings tab

```typescript
// Key features:
// - Tab-based navigation
// - Form validation
// - Save button
```

### Events Page (`/events`)

Event viewer with real-time updates:
- Event history log
- Filter by event type
- Clear history functionality

```typescript
// Key features:
// - Polling for new events (5s interval)
// - Event type filtering
// - Payload and metadata display
```

## Components

### Sidebar

The sidebar provides navigation and agent quick access:

```typescript
// Props:
// - isOpen: boolean - Controls sidebar width
// - setIsOpen: (open: boolean) => void - Toggle sidebar

// Features:
// - Navigation items (Dashboard, Chat, Agents, Events, Config)
// - Agents quick list
// - Dark/light mode toggle
```

### MainLayout

Wrapper component that manages the layout structure:

```typescript
// Renders:
// - Sidebar
// - Main content area
// - Responsive behavior
```

## State Management

### Using Zustand

```typescript
// lib/state.ts
import { create } from 'zustand';

interface ChatState {
  messages: Message[];
  loading: boolean;
  agentId: string;
  
  addMessage: (message: Message) => void;
  setLoading: (loading: boolean) => void;
  setAgentId: (agentId: string) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  loading: false,
  agentId: 'default',
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  
  setLoading: (loading) => set({ loading }),
  setAgentId: (agentId) => set({ agentId })
}));
```

## Routing

### App Router Pattern

```
/app
├── layout.tsx              # Root layout
├── page.tsx                # / (dashboard)
├── chat/
│   ├── layout.tsx          # /chat (if needed)
│   └── page.tsx            # /chat
├── agents/
│   └── page.tsx            # /agents
├── config/
│   └── page.tsx            # /config
└── events/
    └── page.tsx            # /events
```

### Navigation

```typescript
// Client-side navigation
import { useRouter } from 'next/navigation';

const router = useRouter();
router.push('/chat');
router.push(`/chat?agent=${agentId}`);
```

## Styling

### Tailwind CSS

The project uses Tailwind CSS with custom configuration:

```javascript
// tailwind.config.js
module.exports = {
  darkMode: "class",  // Dark mode via class
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        // ... custom colors
      }
    }
  }
}
```

### CSS Variables

```css
:root {
  --background: #ffffff;
  --foreground: #16161a;
  --primary: #6366f1;
  --secondary: #f3f4f6;
  --border: #e4e4e7;
}
```

### Dark Mode

```typescript
// Theme toggle
import { useTheme } from 'next-themes';

const { theme, setTheme } = useTheme();

// In component:
<button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
  {theme === 'dark' ? '☀️' : '🌙'}
</button>
```

## API Integration

### REST Client

```typescript
// lib/api-client.ts
export const apiClient = {
  async get(path: string) {
    return fetch(`/api${path}`).then(res => res.json());
  },
  
  async post(path: string, data: any) {
    return fetch(`/api${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(res => res.json());
  },
  
  async delete(path: string) {
    return fetch(`/api${path}`, { method: 'DELETE' }).then(res => res.json());
  }
};
```

## WebSocket Integration

### Client Setup

```typescript
// lib/ws-client.ts
import { io, Socket } from 'socket.io-client';

export const wsClient = new Client("http://localhost:8000");

// Usage:
wsClient.connect();
wsClient.subscribe(['task_start', 'task_end']);
wsClient.on('event', (data) => console.log(data));
```

## Error Handling

### UI Error States

```typescript
// Loading states
{loading ? (
  <Loader className="animate-spin" />
) : error ? (
  <div className="text-red-500">{error}</div>
) : (
  <div>{data}</div>
)}
```

### Network Errors

```typescript
try {
  const response = await fetch("/api/endpoint");
  if (!response.ok) throw new Error(response.statusText);
  const data = await response.json();
} catch (error) {
  console.error("Network error:", error);
  // Show user-friendly error message
}
```

## Performance Optimization

### Code Splitting

Next.js automatically code-splits pages:
- Each page in `app/` is lazy-loaded
- Dependencies are bundled separately

### Static Generation

```javascript
// next.config.js
module.exports = {
  output: "export",  // Static export for GitHub Pages
  // or use "server" for full SSR
}
```

## Deployment

### Build

```bash
npm run build
```

### Start Production Server

```bash
npm start
```

### Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```
