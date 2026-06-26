"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Save, RefreshCw, Loader, Settings, Database, MessageSquare, Bot } from "lucide-react";

interface Config {
  llm: {
    model_name: string;
    base_url: string;
    temperature: number;
    max_tokens: number;
  };
  memory: {
    short_term_capacity: number;
    long_term_top_k: number;
    embedding_model: string;
  };
  agent: {
    name: string;
    role: string;
    max_iterations: number;
    verbose: boolean;
  };
}

export default function ConfigPage() {
  const router = useRouter();
  const [config, setConfig] = useState<Config | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState("llm");

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await fetch("/api/config");
      const data = await response.json();
      setConfig({
        llm: {
          model_name: data.llm?.model_name || "gemma4:26b",
          base_url: data.llm?.base_url || "http://localhost:11434/v1",
          temperature: data.llm?.temperature || 0.7,
          max_tokens: data.llm?.max_tokens || 4096,
        },
        memory: {
          short_term_capacity: data.memory?.short_term_capacity || 10,
          long_term_top_k: data.memory?.long_term_top_k || 5,
          embedding_model: data.memory?.embedding_model || "text-embedding-3-small",
        },
        agent: {
          name: data.agent?.name || "IndoClaw",
          role: data.agent?.role || "Autonomous AI Assistant",
          max_iterations: data.agent?.max_iterations || 10,
          verbose: data.agent?.verbose ?? true,
        },
      });
    } catch (error) {
      console.error("Failed to fetch config:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!config) return;

    setSaving(true);
    try {
      await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      alert("Configuration saved successfully!");
    } catch (error) {
      alert("Failed to save configuration");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  const tabs = [
    { id: "llm", label: "LLM Settings", icon: Bot },
    { id: "memory", label: "Memory Settings", icon: Database },
    { id: "agent", label: "Agent Settings", icon: MessageSquare },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Configuration</h1>
          <p className="text-muted-foreground mt-1">Configure your agent and system settings</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:bg-primary-hover flex items-center gap-2 disabled:opacity-50"
        >
          {saving ? <Loader className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          <span>Save Changes</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 flex items-center gap-2 rounded-t-lg transition-colors ${
                activeTab === tab.id
                  ? "bg-background border-t border-x text-primary"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="bg-secondary/50 rounded-b-lg p-6 min-h-[400px]">
        {activeTab === "llm" && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold mb-4">LLM Provider Configuration</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Model Name</label>
                <input
                  type="text"
                  value={config!.llm.model_name}
                  onChange={(e) =>
                    setConfig({
                      ...config!,
                      llm: { ...config!.llm, model_name: e.target.value },
                    })
                  }
                  className="w-full bg-background border border-border rounded-lg px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Base URL</label>
                <input
                  type="text"
                  value={config!.llm.base_url}
                  onChange={(e) =>
                    setConfig({
                      ...config!,
                      llm: { ...config!.llm, base_url: e.target.value },
                    })
                  }
                  className="w-full bg-background border border-border rounded-lg px-3 py-2"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Temperature</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    value={config!.llm.temperature}
                    onChange={(e) =>
                      setConfig({
                        ...config!,
                        llm: { ...config!.llm, temperature: parseFloat(e.target.value) },
                      })
                    }
                    className="w-full bg-background border border-border rounded-lg px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Max Tokens</label>
                  <input
                    type="number"
                    value={config!.llm.max_tokens}
                    onChange={(e) =>
                      setConfig({
                        ...config!,
                        llm: { ...config!.llm, max_tokens: parseInt(e.target.value) },
                      })
                    }
                    className="w-full bg-background border border-border rounded-lg px-3 py-2"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "memory" && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold mb-4">Memory Configuration</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Short-term Capacity</label>
                <input
                  type="number"
                  value={config!.memory.short_term_capacity}
                  onChange={(e) =>
                    setConfig({
                      ...config!,
                      memory: { ...config!.memory, short_term_capacity: parseInt(e.target.value) },
                    })
                  }
                  className="w-full bg-background border border-border rounded-lg px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Long-term Top K</label>
                <input
                  type="number"
                  value={config!.memory.long_term_top_k}
                  onChange={(e) =>
                    setConfig({
                      ...config!,
                      memory: { ...config!.memory, long_term_top_k: parseInt(e.target.value) },
                    })
                  }
                  className="w-full bg-background border border-border rounded-lg px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Embedding Model</label>
                <input
                  type="text"
                  value={config!.memory.embedding_model}
                  onChange={(e) =>
                    setConfig({
                      ...config!,
                      memory: { ...config!.memory, embedding_model: e.target.value },
                    })
                  }
                  className="w-full bg-background border border-border rounded-lg px-3 py-2"
                />
              </div>
            </div>
          </div>
        )}

        {activeTab === "agent" && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold mb-4">Agent Configuration</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Agent Name</label>
                <input
                  type="text"
                  value={config!.agent.name}
                  onChange={(e) =>
                    setConfig({
                      ...config!,
                      agent: { ...config!.agent, name: e.target.value },
                    })
                  }
                  className="w-full bg-background border border-border rounded-lg px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Agent Role</label>
                <textarea
                  value={config!.agent.role}
                  onChange={(e) =>
                    setConfig({
                      ...config!,
                      agent: { ...config!.agent, role: e.target.value },
                    })
                  }
                  rows={2}
                  className="w-full bg-background border border-border rounded-lg px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Max Iterations</label>
                <input
                  type="number"
                  value={config!.agent.max_iterations}
                  onChange={(e) =>
                    setConfig({
                      ...config!,
                      agent: { ...config!.agent, max_iterations: parseInt(e.target.value) },
                    })
                  }
                  className="w-full bg-background border border-border rounded-lg px-3 py-2"
                />
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="verbose"
                  checked={config!.agent.verbose}
                  onChange={(e) =>
                    setConfig({
                      ...config!,
                      agent: { ...config!.agent, verbose: e.target.checked },
                    })
                  }
                  className="w-4 h-4"
                />
                <label htmlFor="verbose" className="text-sm font-medium">
                  Verbose Mode
                </label>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
