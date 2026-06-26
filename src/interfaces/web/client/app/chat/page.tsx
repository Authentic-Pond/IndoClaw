"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Send, Bot, User, Loader, StopCircle, Settings } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  agentId?: string;
}

export default function ChatPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [agentId, setAgentId] = useState("default");
  const [agents, setAgents] = useState<{ id: string; name: string }[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load agents on mount
  useEffect(() => {
    fetch("/api/agents")
      .then((res) => res.json())
      .then((data) => setAgents(data.agents || []))
      .catch(() => setAgents([{ id: "default", name: "IndoClaw" }]));
  }, []);

  // Load chat history
  useEffect(() => {
    const savedMessages = localStorage.getItem(`chat_${agentId}`);
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    }
  }, [agentId]);

  // Scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: input.trim(),
      timestamp: new Date().toISOString(),
      agentId,
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    localStorage.setItem(`chat_${agentId}`, JSON.stringify(updatedMessages));
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input.trim(),
          agent_id: agentId,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        const assistantMessage: Message = {
          role: "assistant",
          content: data.response,
          timestamp: new Date().toISOString(),
          agentId,
        };
        setMessages((prev) => [...prev, assistantMessage]);
        localStorage.setItem(`chat_${agentId}`, JSON.stringify([...updatedMessages, assistantMessage]));
      } else {
        const errorMessage: Message = {
          role: "assistant",
          content: `Error: ${data.detail || "Failed to get response"}`,
          timestamp: new Date().toISOString(),
          agentId,
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage: Message = {
        role: "assistant",
        content: `Connection error. Make sure the server is running.`,
        timestamp: new Date().toISOString(),
        agentId,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleAgentChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newAgentId = e.target.value;
    setAgentId(newAgentId);
    const savedMessages = localStorage.getItem(`chat_${newAgentId}`);
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    } else {
      setMessages([]);
    }
  };

  const handleClearHistory = () => {
    setMessages([]);
    localStorage.removeItem(`chat_${agentId}`);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-2rem)]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 pb-4 border-b">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold">Chat</h1>
          <select
            value={agentId}
            onChange={handleAgentChange}
            className="bg-secondary px-3 py-1 rounded text-sm border border-border"
          >
            {agents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={handleClearHistory}
          className="p-2 text-muted-foreground hover:text-destructive transition-colors"
          title="Clear chat history"
        >
          <StopCircle className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto mb-4 p-4 space-y-4 bg-secondary/50 rounded-lg">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
            <Bot className="w-16 h-16 mb-4 opacity-20" />
            <p className="text-lg">Start a conversation with your agent</p>
            <p className="text-sm mt-2">
              Ask anything - the agent will respond using its configured tools
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 ${
              msg.role === "user" ? "flex-row-reverse" : ""
            }`}
          >
            <div
              className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                msg.role === "user" ? "bg-primary text-white" : "bg-green-500 text-white"
              }`}
            >
              {msg.role === "user" ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
            </div>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-background border border-border"
              }`}
            >
              <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
              <p className="text-xs mt-1 opacity-60 text-right">
                {new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center">
              <Bot className="w-5 h-5" />
            </div>
            <div className="bg-background border border-border rounded-2xl px-4 py-3 flex items-center gap-2">
              <Loader className="w-4 h-4 animate-spin" />
              <span className="text-sm text-muted-foreground">Agent is thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && handleSendMessage()}
          placeholder="Type your message..."
          disabled={loading}
          className="flex-1 bg-background border border-border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
        />
        <button
          onClick={handleSendMessage}
          disabled={loading || !input.trim()}
          className="bg-primary text-primary-foreground px-6 py-3 rounded-lg hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <Send className="w-5 h-5" />
          <span>Send</span>
        </button>
      </div>
    </div>
  );
}
