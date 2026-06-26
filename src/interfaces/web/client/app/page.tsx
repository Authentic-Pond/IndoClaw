"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Bot, MessageSquare, Users, Settings, Activity, Terminal } from "lucide-react";

export default function Dashboard() {
  const router = useRouter();
  const [agents, setAgents] = useState<{ id: string; name: string; status: "online" | "idle" | "busy" }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch agents from backend
    fetch("/api/agents")
      .then((res) => res.json())
      .then((data) => setAgents(data))
      .catch(() => setAgents([{ id: "default", name: "IndoClaw", status: "idle" }]))
      .finally(() => setLoading(false));
  }, []);

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

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Welcome to IndoClaw - Your Autonomous AI Agent OS
          </p>
        </header>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-secondary p-4 rounded-lg">
            <div className="text-sm text-muted-foreground">Active Agents</div>
            <div className="text-2xl font-bold">{agents.length}</div>
          </div>
          <div className="bg-secondary p-4 rounded-lg">
            <div className="text-sm text-muted-foreground">Total Tasks</div>
            <div className="text-2xl font-bold">0</div>
          </div>
          <div className="bg-secondary p-4 rounded-lg">
            <div className="text-sm text-muted-foreground">Memory Entries</div>
            <div className="text-2xl font-bold">0</div>
          </div>
          <div className="bg-secondary p-4 rounded-lg">
            <div className="text-sm text-muted-foreground">System Status</div>
            <div className="text-green-500 font-bold">Healthy</div>
          </div>
        </div>

        {/* Agents Grid */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Agents</h2>
            <button
              onClick={() => router.push("/agents")}
              className="text-sm text-primary hover:underline"
            >
              Manage All Agents
            </button>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-secondary h-32 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {agents.map((agent) => (
                <div
                  key={agent.id}
                  className="bg-secondary p-4 rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => router.push(`/agents/${agent.id}`)}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <Bot className="w-6 h-6 text-primary" />
                    <h3 className="font-semibold">{agent.name}</h3>
                    <span className={`w-2 h-2 rounded-full ${statusColor(agent.status)}`} />
                  </div>
                  <div className="text-sm text-muted-foreground">
                    ID: {agent.id}
                  </div>
                  <div className="mt-3 flex gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/chat?agent=${agent.id}`);
                      }}
                      className="flex-1 bg-primary text-white py-1 px-3 rounded text-sm hover:bg-primary-hover transition-colors"
                    >
                      Chat
                    </button>
                  </div>
                </div>
              ))}
              {agents.length === 0 && (
                <div className="col-span-3 text-center py-8 text-muted-foreground">
                  No agents configured. Go to Configuration to set up your first agent.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => router.push("/chat")}
            className="bg-secondary p-4 rounded-lg hover:bg-secondary/80 transition-colors flex flex-col items-center gap-2"
          >
            <MessageSquare className="w-8 h-8 text-primary" />
            <span className="font-medium">Start Chat</span>
          </button>

          <button
            onClick={() => router.push("/events")}
            className="bg-secondary p-4 rounded-lg hover:bg-secondary/80 transition-colors flex flex-col items-center gap-2"
          >
            <Activity className="w-8 h-8 text-accent" />
            <span className="font-medium">Events</span>
          </button>

          <button
            onClick={() => router.push("/agents")}
            className="bg-secondary p-4 rounded-lg hover:bg-secondary/80 transition-colors flex flex-col items-center gap-2"
          >
            <Users className="w-8 h-8 text-secondary-foreground" />
            <span className="font-medium">Agents</span>
          </button>

          <button
            onClick={() => router.push("/config")}
            className="bg-secondary p-4 rounded-lg hover:bg-secondary/80 transition-colors flex flex-col items-center gap-2"
          >
            <Settings className="w-8 h-8 text-foreground" />
            <span className="font-medium">Configuration</span>
          </button>
        </div>
      </div>
    </div>
  );
}
