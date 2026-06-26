# IndoClaw Web Interface - Components Documentation

## Layout Components

### Sidebar

The sidebar provides navigation and agent quick access.

**Props:**
- `isOpen: boolean` - Controls sidebar width (64px when open, 16px when closed)
- `setIsOpen: (open: boolean) => void` - Toggle sidebar

**Features:**
- Navigation items (Dashboard, Chat, Agents, Events, Config)
- Agents quick list with status indicators
- Dark/light mode toggle

**Usage:**
```typescript
import { Sidebar } from "@/components/layout/Sidebar"

export function Layout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  
  return (
    <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen}>
      {children}
    </Sidebar>
  )
}
```

### MainLayout

Wrapper component that manages the layout structure.

**Props:**
- `children: React.ReactNode` - Main content to render

**Features:**
- Responsive width based on sidebar state
- Proper spacing and margins

**Usage:**
```typescript
import { MainLayout } from "@/components/layout/MainLayout"

export default function Page() {
  return <MainLayout>Page content</MainLayout>
}
```

## UI Components

### Button

A customizable button component.

**Props:**
- `variant?: "default" | "destructive" | "outline" | "ghost" | "link"`
- `size?: "default" | "sm" | "lg" | "icon"`
- `disabled?: boolean`
- `className?: string`
- `children: React.ReactNode`

**Usage:**
```typescript
import { Button } from "@/components/ui/Button"

<Button variant="primary" onClick={handleClick}>
  Click me
</Button>
```

### Card

A card component for displaying content.

**Props:**
- `title?: string` - Card title
- `description?: string` - Card description
- `className?: string`

**Usage:**
```typescript
import { Card } from "@/components/ui/Card"

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description</CardDescription>
  </CardHeader>
  <CardContent>Card content</CardContent>
</Card>
```

### Input

An input field component.

**Props:**
- `type?: string` - Input type
- `value?: string` - Input value
- `onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void`
- `placeholder?: string`
- `disabled?: boolean`
- `className?: string`

**Usage:**
```typescript
import { Input } from "@/components/ui/Input"

<Input 
  value={value} 
  onChange={handleChange}
  placeholder="Enter text"
/>
```

### Select

A dropdown select component.

**Props:**
- `value?: string` - Selected value
- `onChange?: (e: React.ChangeEvent<HTMLSelectElement>) => void`
- `options: { value: string; label: string }[]`
- `disabled?: boolean`
- `className?: string`

**Usage:**
```typescript
import { Select } from "@/components/ui/Select"

<Select 
  value={value}
  onChange={handleChange}
  options={[
    { value: 'default', label: 'Default Agent' },
    { value: 'agent2', label: 'Agent 2' }
  ]}
/>
```

## Chat Components

### MessageBubble

Displays a chat message.

**Props:**
- `message: Message` - Message object with role, content, timestamp
- `isUser: boolean` - Whether this is a user message

**Usage:**
```typescript
<MessageBubble message={message} isUser={message.role === 'user'} />
```

### ChatInput

Input component for chat messages.

**Props:**
- `value: string` - Input value
- `onChange: (value: string) => void`
- `onSubmit: () => void`
- `disabled?: boolean`

**Usage:**
```typescript
<ChatInput 
  value={input}
  onChange={setInput}
  onSubmit={handleSubmit}
/>
```

## Agent Components

### AgentCard

Displays agent information in a card.

**Props:**
- `agent: Agent` - Agent object with id, name, status
- `onChat: () => void`
- `onDelete: () => void`
- `onView: () => void`

**Usage:**
```typescript
<AgentCard 
  agent={agent}
  onChat={() => router.push(`/chat?agent=${agent.id}`)}
  onDelete={() => handleDelete(agent.id)}
/>
```

### StatusBadge

Displays agent status with color coding.

**Props:**
- `status: "online" | "idle" | "busy"`
- `size?: "sm" | "md" | "lg"`

**Usage:**
```typescript
<StatusBadge status="online" />
```

## Config Components

### ConfigSection

A section in the configuration panel.

**Props:**
- `title: string` - Section title
- `icon: React.ReactNode` - Section icon
- `children: React.ReactNode` - Section content

**Usage:**
```typescript
<ConfigSection title="LLM Settings" icon={<Bot />}>
  {/* Form fields */}
</ConfigSection>
```

### FormInput

A form input with label.

**Props:**
- `label: string` - Input label
- `name: string` - Form field name
- `value: string | number`
- `onChange: (value: string) => void`
- `type?: "text" | "number" | "checkbox"`
- `placeholder?: string`
- `description?: string`

**Usage:**
```typescript
<FormInput
  label="Model Name"
  name="model_name"
  value={config.model_name}
  onChange={(value) => setConfig({ ...config, model_name: value })}
/>
```

## Event Components

### EventLog

Displays event history.

**Props:**
- `events: Event[]` - List of events
- `loading: boolean`
- `onClear: () => void`
- `onRefresh: () => void`

**Usage:**
```typescript
<EventLog 
  events={events}
  loading={loading}
  onClear={handleClear}
  onRefresh={handleRefresh}
/>
```

### EventFilter

Filter dropdown for events.

**Props:**
- `selectedType: string`
- `onTypeChange: (type: string) => void`

**Usage:**
```typescript
<EventFilter 
  selectedType={selectedType}
  onTypeChange={setSelectedType}
/>
```

## Custom Hooks

### useChat

Hook for managing chat state.

```typescript
import { useChat } from "@/lib/hooks/useChat"

export default function ChatPage() {
  const { messages, loading, sendMessage, clearHistory } = useChat()
  
  return (
    // ... JSX
  )
}
```

### useTheme

Hook for managing theme state.

```typescript
import { useTheme } from "next-themes"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  
  return (
    <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      {theme === 'dark' ? '☀️' : '🌙'}
    </button>
  )
}
```

### useAgents

Hook for managing agents.

```typescript
import { useAgents } from "@/lib/hooks/useAgents"

export default function AgentsPage() {
  const { agents, loading, refreshAgents, deleteAgent } = useAgents()
  
  return (
    // ... JSX
  )
}
```
