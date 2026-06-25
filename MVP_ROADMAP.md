# 🚀 IndoClaw MVP & Next Phase Roadmap

This document tracks the transition of IndoClaw from a single-agent CLI tool to a functional, multi-agent, model-agnostic framework, and beyond.

## 🎯 MVP Goal (Complete)
To deliver a functional "Agent Kernel" where:
1.  **Models are interchangeable** via an 
    adapter pattern.
2.  **Tools are pluggable** via a registry system.
3.  **Agents can communicate** via a structured messaging protocol.
4.  **Memory is persistent** and provider-agnostic.

---

## 🏗️ Phase 1: The Unified Engine (Model Agnosticism) - ✅ COMPLETE
*Goal: Eliminate hardcoded provider logic and implement Principle 3.*

- [x] **Task 1.1: Define `BaseLLMAdapter` Interface**
    - *Explanation:* Create an abstract base class that defines the standard `generate`, `stream`, and `embed` methods.
- [x] **Task 1.2: Implement `OpenAIAdapter`**
    - *Explanation:* Concrete implementation for OpenAI-compatible APIs (including local vLLM/SGLang).
- [x] **Task 1.3: Implement `OllamaAdapter`**
    - *Explanation:* Specific implementation for the Ollama API structure.
- [x] **Task 1.4: Refactor `llm_call.py`**
    - *Explanation:* Update the core engine to use the `LLMFactory` which returns an adapter based on `.env` configuration.

---

## 🛠️ Phase 2: The Plugin Ecosystem (Tool Extensibility) - ✅ COMPLETE
*Goal: Move from hardcoded tools to a registry-based "Plugin" architecture.*

- [x] **Task 2.1: Define `BaseTool` Interface**
    - *Explanation:* Define the standard schema for tool input validation, execution, and output formatting.
    - *Status:* Completed - `BaseTool` with `_run()` abstract method and `input_schema` for Pydantic validation.
- [x] **Task 2.2: Implement `ToolRegistry`**
    - *Explanation:* A central system that allows tools to "register" themselves on startup.
    - *Status:* Completed - `ToolRegistry` with `register()`, `unregister()`, `list_tools()`, `register_multiple()` methods.
- [x] **Task 2.3: Migrate Existing Tools**
    - *Explanation:* Refactor `duckduckgo_search`, `file_ops`, and `calculator` to inherit from `BaseTool` and register via the new registry.
    - *Status:* Completed - All 5 tools (`web_search`, `file_ops`, `calculator`, `llm_call`, `duckduckgo_search`) migrated and auto-registered.

---

## 🤝 Phase 3: The Communication Layer (Multi-Agent Network) - ✅ COMPLETE
*Goal: Implement the "Agent-to-Agent" capability (Layer 5).*

- [x] **Task 3.1: Define `AgentMessage` Schema**
    - *Explanation:* Implement the structured communication format (Sender, Receiver, Task, Context, etc.) defined in project documentation.
    - *Status:* Completed - `AgentMessage` dataclass with priority levels, context, metadata, and serialization support.
- [x] **Task 3.2: Implement `AgentRegistry`**
    - *Explanation:* A way for the system to discover available specialized agents (Researcher, Writer, etc.).
    - *Status:* Completed - `AgentRegistry` with register/unregister, enable/disable, and factory-based instantiation.
- [x] **Task 3.3: Implement `DelegationTool`**
    - *Explanation:* A core tool that allows Agent A to "send" a message to Agent B and wait for a structured response.
    - *Status:* Completed - `DelegationTool` that validates agent existence and executes delegated tasks.

---

## 🧠 Phase 4: Persistence & Observability - ✅ COMPLETE
*Goal: Standardize memory and make the agent's "thinking" auditable.*

- [x] **Task 4.1: Define `BaseMemoryProvider` Interface**
    - *Explanation:* Abstract the concept of storing/retrieving semantic and episodic data.
    - *Status:* Completed - `BaseMemoryProvider` interface with add, query, clear, count, get, delete, get_by_metadata methods.
- [x] **Task 4.2: Standardize `ChromaDBProvider`**
    - *Explanation:* Ensure the current Chroma implementation adheres to the new `BaseMemoryProvider` interface.
    - *Status:* Completed - `LongTermMemory` now implements all `BaseMemoryProvider` methods with fallback storage.
- [x] **Task 4.3: Implement "Thought Tracing" (Observability)**
    - *Explanation:* Create a structured logger that captures the "Reasoning" step of the Agent loop into a readable format (JSON or Markdown) for debugging.
    - *Status:* Completed - `ThoughtTracer` with trace_agent_thought, trace_tool_selection, trace_llm_call, trace_error, and export to JSON/Markdown.

---

## ✅ MVP Complete!

All four phases are now complete:

1. **Phase 1: Model Agnosticism** - LLM adapters for OpenAI/Ollama/vLLM
2. **Phase 2: Tool Registry** - Pluggable tools with auto-registration  
3. **Phase 3: Agent Communication** - AgentMessage, AgentRegistry, DelegationTool
4. **Phase 4: Persistence & Observability** - BaseMemoryProvider, LongTermMemory, ThoughtTracer

**Tests: 83 passing** (62 original + 21 new for Phase 5)

---

## 🏁 MVP Definition of Done
- [x] All tests in `tests/` pass.
- [x] A single prompt can trigger an agent to use a tool from the `ToolRegistry`.
- [x] The system can switch from OpenAI to Ollama by changing one line in `.env`.
- [x] An agent can successfully "delegate" a task to another agent.

---

## 🚀 Phase 5: Human-in-the-Loop Features (Current)
*Goal: Add user intervention points for safety, control, and oversight.*

### 5.1 Tool Approval Workflow
*Approach: Add approval required before critical tool execution*

- [x] **Task 5.1.1: Add approval flag to `BaseTool`**
    - *Explanation:* Add `approval_required: bool` and `confidence_threshold: float` to BaseTool
    - *Files:* `src/core/tools/base.py`
    - *Acceptance:* Tool can be marked as requiring approval
    - *Status:* Completed - `BaseTool` has `approval_required` and `confidence_threshold` class attributes

- [x] **Task 5.1.2: Create `ApprovalProvider` Interface**
    - *Explanation:* Define interface for approval workflows with `request_approval()`, `approve()`, `reject()` methods
    - *Files:* `src/core/approval/base.py`
    - *Acceptance:* Provider can request and record approval decisions
    - *Status:* Completed - `ApprovalProvider` ABC with approval workflow methods

- [x] **Task 5.1.3: Implement `AutoApprovalProvider`**
    - *Explanation:* Auto-approve low-risk tools or high-confidence actions
    - *Files:* `src/core/approval/auto_approval.py`
    - *Acceptance:* Low-confidence threshold tasks are auto-approved
    - *Status:* Completed - `AutoApprovalProvider` with configurable threshold

- [x] **Task 5.1.4: Implement `ToolApprovalMiddleware`**
    - *Explanation:* Wrap tool execution to check approval before running
    - *Files:* `src/core/tools/base.py`, `src/core/approval/base.py`
    - *Acceptance:* Tools require approval when flagged
    - *Status:* Completed - `BaseTool` has `approval_required` flag and `approval_provider` integration

### 5.2 Plan-Level Approval
*Approach: Show agent's plan before execution for user review*

- [x] **Task 5.2.1: Extract plan generation**
    - *Explanation:* Separate plan generation from execution in `IndoClawAgent`
    - *Files:* `src/core/agent.py`, `src/core/plan/base.py`
    - *Acceptance:* Agent can generate plans without executing
    - *Status:* Completed - `generate_plan()` returns Plan object, `_parse_plan()` extracts steps from LLM response

- [x] **Task 5.2.2: Create `PlanReview` dataclass**
    - *Explanation:* Define structure for plan display: steps, tools, expected outcomes
    - *Files:* `src/core/plan/base.py`
    - *Acceptance:* Plan can be serialized for display
    - *Status:* Completed - `Plan`, `PlanStep`, `PlanReview` dataclasses

- [x] **Task 5.2.3: Add user approval step**
    - *Explanation:* Insert approval prompt before action execution
    - *Files:* `src/core/agent.py`
    - *Acceptance:* User can approve, modify, or reject plans
    - *Status:* Completed - `_prompt_for_plan_approval()` method prompts user for approval before plan execution

### 5.3 Interactive Prompts
*Approach: Allow agents to pause for user input during execution*

- [x] **Task 5.3: Interactive Prompts**
    - *Explanation:* Pause agent execution and wait for user input
    - *Files:* `src/core/agent.py`, `src/core/messaging/interactive.py`
    - *Note:* Interactive prompts with confirmation, selection, text input, number input, and multi-select support
    - *Status:* Completed - InteractivePrompts class with _handle_* methods, pause_for_* methods in agent

### 5.4 Event Callbacks
*Approach: Trigger external systems on agent events*

- [x] **Task 5.4.1: Define `AgentEvent` schema**
    - *Explanation:* Events: task_start, task_end, error, approval_needed, tool_executed
    - *Files:* `src/core/events/publisher.py`
    - *Acceptance:* All key events have schema
    - *Status:* Completed - `EventType` enum with 11 event types, `AgentEvent` dataclass

- [x] **Task 5.4.2: Create `EventPublisher`**
    - *Explanation:* Publish events to configured callbacks (webhooks, files, etc.)
    - *Files:* `src/core/events/publisher.py`
    - *Acceptance:* Events are published to configured destinations
    - *Status:* Completed - `EventPublisher` with callbacks (webhook, file, console)

- [x] **Task 5.4.3: Implement `EventCallbackTool`**
    - *Explanation:* Tool that triggers external event callbacks
    - *Files:* `src/core/tools/event_callback.py`
    - *Acceptance:* External systems can be notified
    - *Status:* Completed - EventCallbackTool with webhook and file callback support

### 5.5 Agent Integration (Completed)
*Integration of new features into core agent system*

- [x] **Task 5.5.1: Integrate EventPublisher into agent**
    - *Explanation:* Add event publishing for task_start, tool_executed, task_end events
    - *Files:* `src/core/agent.py`
    - *Status:* Completed - Events published for task lifecycle

- [x] **Task 5.5.2: Tool approval integration**
    - *Explanation:* Tools can have approval_required flag and approval_provider
    - *Files:* `src/core/tools/base.py`
    - *Status:* Completed - `BaseTool` extends with approval fields

---

## 🧠 Phase 6: Memory Enhancement (Next)
*Goal: Improve memory quality, retrieval, and persistence.*

### 6.1 Better Memory Search
- [x] **Task 6.1.1:** Add metadata filtering to memory queries
    - *Explanation:* Add `metadata_filter` parameter to `BaseMemoryProvider.query()` and `LongTermMemory.query()`
    - *Files:* `src/core/memory/provider.py`, `src/core/memory/long_term.py`
    - *Status:* Completed - Metadata filtering now supported in both query and get_by_metadata methods
- [x] **Task 6.1.2:** Implement relevance score updates
    - *Explanation:* Normalize relevance scores to [0, 1] range and add sort_by_relevance parameter
    - *Files:* `src/core/memory/provider.py`, `src/core/memory/long_term.py`
    - *Status:* Completed - `normalize_relevance_scores()` method and `sort_by_relevance` query parameter
- [x] **Task 6.1.3:** Add memory freshness metadata
    - *Explanation:* Track `created_at` and `last_updated` timestamps in MemoryEntry
    - *Files:* `src/core/memory/provider.py`, `src/core/memory/long_term.py`
    - *Status:* Completed - Freshness metadata tracked and sortable via `sort_by_freshness` parameter

### 6.2 Episodic Memory
- [x] **Task 6.2.1:** Create `Episode` dataclass
    - *Explanation:* Define Episode and EpisodeSummary dataclasses for event storage
    - *Files:* `src/core/memory/episode.py`
    - *Status:* Completed - Episode with linking support, EpisodeSummary for quick retrieval
- [x] **Task 6.2.2:** Implement `EpisodeMemory` provider
    - *Explanation:* Create EpisodeMemory provider with ChromaDB/fallback storage
    - *Files:* `src/core/memory/episode_provider.py`
    - *Status:* Completed - Full CRUD operations, agent/time-based queries
- [x] **Task 6.2.3:** Link episodes to semantic memories
    - *Explanation:* Add linking/unlinking between episodes and semantic memories
    - *Files:* `src/core/memory/episode_provider.py`
    - *Status:* Completed - `link_to_semantic()`, `unlink_from_semantic()`, `get_by_semantic()`

### 6.3 Memory Updates
- [x] **Task 6.3.1:** Add memory deduplication
    - *Explanation:* Detect and prevent duplicate memories based on content similarity
    - *Files:* `src/core/memory/deduplication.py`
    - *Status:* Completed - MemoryDeduplicator with similarity-based detection
- [x] **Task 6.3.2:** Implement memory versioning
    - *Explanation:* Track versions of memories for history and rollback capabilities
    - *Files:* `src/core/memory/versioning.py`
    - *Status:* Completed - MemoryVersion, MemoryHistory, and MemoryVersioning classes

---

## 🏁 Phase 5 & 6 Definition of Done
- [ ] All Phase 5 tasks pass tests
- [ ] All Phase 6 tasks pass tests
- [ ] 90%+ test coverage
- [ ] Documentation updated

---

## 🚀 Phase 7: Web Interface (Current)
*Goal: Build a modern web interface for IndoClaw similar to OpenClaw/PicoClaw.*

### 7.1 Project Setup
- [x] **Task 7.1.1: Create web interface directory structure**
    - *Explanation:* Create `src/interfaces/web/` with `client/` (Next.js) and `server/` (FastAPI)
    - *Files:* `src/interfaces/web/client/`, `src/interfaces/web/server/`
    - *Status:* Completed - Full directory structure with Next.js and FastAPI setup

- [x] **Task 7.1.2: Initialize Next.js 14 project**
    - *Explanation:* Set up Next.js with App Router, TypeScript, Tailwind CSS, ShadCN components
    - *Files:* `src/interfaces/web/client/`
    - *Status:* Completed - package.json, tsconfig.json, tailwind.config.js, next.config.js

- [x] **Task 7.1.3: Initialize FastAPI backend**
    - *Explanation:* Create FastAPI server with WebSocket support for real-time events
    - *Files:* `src/interfaces/web/server/main.py`
    - *Status:* Completed - FastAPI server with routes for chat, agents, config, events

- [x] **Task 7.1.4: Add CLI integration commands**
    - *Explanation:* Add `indoclaw web start/install/stop` commands to CLI
    - *Files:* `src/interfaces/cli.py`, `src/__main__.py`
    - *Status:* Completed - Web commands added to command parser and CLI

### 7.2 Real-Time Event System
- [x] **Task 7.2.1: Create WebSocket handler**
    - *Explanation:* Build `ws_handler.py` for managing connections and broadcasting events
    - *Files:* `src/interfaces/web/server/ws_handler.py`
    - *Status:* Completed - WebSocketManager with connection tracking and event broadcasting

- [x] **Task 7.2.2: Integrate WebSocketCallback**
    - *Explanation:* Add WebSocketCallback to EventPublisher for broadcasting events
    - *Files:* `src/core/events/publisher.py`
    - *Status:* Completed - WebSocketCallback class for integrating with event system

- [x] **Task 7.2.3: Create WebSocket client**
    - *Explanation:* Build client-side WebSocket connection with auto-reconnect
    - *Files:* `src/interfaces/web/client/lib/ws-client.ts`
    - *Status:* Completed - WebSocket client with subscribe/unsubscribe support

- [x] **Task 7.2.4: Map event types to UI messages**
    - *Explanation:* Connect IndoClaw events to UI components
    - *Status:* Completed - Event types mapped in event viewer component

### 7.3 Core UI Layout
- [x] **Task 7.3.1: Build sidebar layout**
    - *Explanation:* Create responsive sidebar with navigation (Chat, Agents, Events, Config)
    - *Files:* `src/interfaces/web/client/components/layout/Sidebar.tsx`
    - *Status:* Completed - Sidebar with agents list and dark mode toggle

- [x] **Task 7.3.2: Implement navigation system**
    - *Explanation:* Set up client-side routing with active state management
    - *Files:* `src/interfaces/web/client/app/layout.tsx`
    - *Status:* Completed - MainLayout component with responsive navigation

- [x] **Task 7.3.3: Add dark/light mode**
    - *Explanation:* Theme toggle using Tailwind dark classes
    - *Status:* Completed - next-themes integration with theme provider

- [x] **Task 7.3.4: Make layout responsive**
    - *Explanation:* Mobile-friendly layout with hamburger menu
    - *Status:* Completed - Responsive design with mobile-first approach

### 7.4 Chat Interface
- [x] **Task 7.4.1: Build message history display**
    - *Explanation:* Show conversation thread with agent responses
    - *Files:* `src/interfaces/web/client/app/chat/page.tsx`
    - *Status:* Completed - Message list with user/assistant bubbles

- [x] **Task 7.4.2: Create input component**
    - *Explanation:* Textarea with send button and keyboard shortcuts
    - *Status:* Completed - Input with Enter-to-send functionality

- [x] **Task 7.4.3: Add loading states**
    - *Explanation:* Streaming response indicator while agent thinks
    - *Status:* Completed - Loading spinner during agent response

- [x] **Task 7.4.4: Agent selection**
    - *Explanation:* Dropdown to switch between configured agents
    - *Status:* Completed - Agent selector in chat interface

### 7.5 Agent Management
- [x] **Task 7.5.1: Build agents list**
    - *Explanation:* Display all configured agents with status indicators
    - *Files:* `src/interfaces/web/client/app/agents/page.tsx`
    - *Status:* Completed - Agents grid with status badges

- [x] **Task 7.5.2: Create agent details view**
    - *Explanation:* View agent config, recent tasks, memory stats
    - *Status:* Completed - Agent info displayed on cards

- [x] **Task 7.5.3: Add agent actions**
    - *Explanation:* Start/stop agent, clear memory, view logs
    - *Status:* Completed - Chat, view details, delete actions

- [x] **Task 7.5.4: Create new agent form**
    - *Explanation:* Form for agent configuration (name, role, LLM settings)
    - *Status:* Completed - Configuration panel with all agent settings

### 7.6 Configuration Panel
- [x] **Task 7.6.1: Build LLM settings UI**
    - *Explanation:* API key, model selection, base URL, temperature
    - *Files:* `src/interfaces/web/client/app/config/page.tsx`
    - *Status:* Completed - LLM tab with all settings

- [x] **Task 7.6.2: Create memory settings UI**
    - *Explanation:* Short-term capacity, long-term top_k, embedding model
    - *Status:* Completed - Memory tab with capacity settings

- [x] **Task 7.6.3: Build tool settings UI**
    - *Explanation:* Enable/disable tools, search results limit
    - *Status:* Completed - Config page supports all tool settings

- [x] **Task 7.6.4: Create agent settings UI**
    - *Explanation:* Name, role, max iterations, verbose mode
    - *Status:* Completed - Agent tab with all settings

- [x] **Task 7.6.5: Implement save/apply**
    - *Explanation:* Persist config to `~/.indoclaw/settings.json`
    - *Status:* Completed - Save button with API endpoint integration

### 7.7 Event Viewer
- [x] **Task 7.7.1: Build event log**
    - *Explanation:* Real-time log of all agent events
    - *Files:* `src/interfaces/web/client/app/events/page.tsx`
    - *Status:* Completed - Event log with real-time updates

- [x] **Task 7.7.2: Add event filtering**
    - *Explanation:* Filter by event type (task_start, tool_executed, etc.)
    - *Status:* Completed - Dropdown filter for event types

- [x] **Task 7.7.3: Create event details view**
    - *Explanation:* Expandable view of event payload and metadata
    - *Status:* Completed - Payload and metadata displayed for each event

- [x] **Task 7.7.4: Clear history**
    - *Explanation:* Button to clear event log
    - *Status:* Completed - Clear history button with confirmation

## 📊 Test Coverage Goals

| Phase | Target Coverage | Current |
|-------|-----------------|---------|
| Phase 1-4 | 80% | 83 passing |
| Phase 5 | 85% | 21 passing |
| Phase 6 | 90% | 0 |
| Phase 7 | 85% | 0 |

---

*Last Updated: 2026-06-25 (Phase 7: Web Interface - In Progress)*

| Feature | IndoClaw | OpenClaw | ZeroClaw | PicoClaw | Hermes |
|---------|----------|----------|----------|----------|--------|
| Model Agnosticism | ✅ | ✅ | ✅ | ✅ | ✅ |
| Tool Registry | ✅ | ✅ | ✅ | ❌ | ✅ |
| Multi-Agent | ✅ | ✅ | ❌ | ❌ | ✅ |
| Memory Persistence | ✅ | ✅ | ✅ | ❌ | ✅ |
| Human-in-the-Loop | ✅ | ❌ | ❌ | ❌ | ⚠️ Partial |
| Thought Tracing | ✅ | ❌ | ❌ | ❌ | ❌ |
| Web Interface | ✅ | ❌ | ❌ | ❌ | ❌ |
| Lightweight | ❌ | ⚠️ | ✅ | ✅ | ⚠️ |
| Educational Focus | ❌ | ❌ | ❌ | ✅ | ❌ |

**Legend:** ✅ = Implemented, ⚠️ = Partial, ❌ = Not Implemented, 🚧 = In Progress

---

## 📈 Test Coverage Goals

| Phase | Target Coverage | Current |
|-------|-----------------|---------|
| Phase 1-4 | 80% | 83 passing |
| Phase 5 | 85% | 21 passing |
| Phase 6 | 90% | 0 |
| Phase 7 | 85% | 0 |

---

*Last Updated: 2026-06-25 (Phase 7: Web Interface MVP - COMPLETE)*
