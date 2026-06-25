"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Bot, User, MessageSquare, Trash2, Settings, Plus, RefreshCw } from "lucide-react";

interface Agent {
  id: string;
  name: string;
  status: "online" | "idle" | "busy";
  role?: string;
}

export default function AgentsPage() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch("/api/agents");
      const data = await response.json();
      setAgents(data.agents || []);
    } catch (error) {
      console.error("Failed to fetch agents:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAgent = async (agentId: string) => {
    if (!confirm(`Are you sure you want to delete agent "${agentId}"?`)) return;

    try {
      await fetch(`/api/agents/${agentId}`, { method: "DELETE" });
      setAgents((prev) => prev.filter((a) => a.id !== agentId));
    } catch (error) {
      console.error("Failed to delete agent:", error);
    }
  };

  const statusColor = (status: string) => {
    switch (status) {
      case "online":
        return "bg-green-500";
      case "busy":
        return "bg-yellow-500";
      default:
        return "bg-gray-500";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Agents</h1>
          <p className="text-muted-foreground mt-1">Manage your AI agents</p>
        </div>
        <button
          onClick={() => router.push("/agents/new")}
          className="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:bg-primary-hover flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          <span>New Agent</span>
        </button>
      </div>

      {agents.length === 0 ? (
        <div className="text-center py-16 bg-secondary/50 rounded-lg border border-dashed border-border">
          <Bot className="w-16 h-16 mx-auto mb-4 opacity-20" />
          <h3 className="text-lg font-medium mb-2">No agents configured</h3>
          <p className="text-muted-foreground mb-6">Get started by creating your first agent.</p>
          <button
            onClick={() => router.push("/agents/new")}
            className="text-primary hover:underline"
          >
            Create your first agent
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <div key={agent.id} className="bg-secondary p-5 rounded-lg hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center">
                    <Bot className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{agent.name}</h3>
                    <p className="text-xs text-muted-foreground">ID: {agent.id}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => router.push(`/agents/${agent.id}`)}
                    className="p-2 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded-lg transition-colors"
                    title="View details"
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteAgent(agent.id)}
                    className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-colors"
                    title="Delete agent"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-2 mb-4">
                <span
                  className={`w-2 h-2 rounded-full ${statusColor(agent.status)}`}
                />
                <span className="text-sm capitalize text-muted-foreground">{agent.status}</span>
              </div>

              <button
                onClick={() => router.push(`/chat?agent=${agent.id}`)}
                className="w-full bg-primary/10 text-primary py-2 rounded-lg hover:bg-primary/20 transition-colors flex items-center justify-center gap-2"
              >
                <MessageSquare className="w-4 h-4" />
                <span>Start Chat</span>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
