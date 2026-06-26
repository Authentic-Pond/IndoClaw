import { LayoutDashboard, MessageSquare, Users, Settings, Activity, Bot, Menu, X, Moon, Sun, Plus } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useTheme } from "next-themes";

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

export function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const [agents, setAgents] = useState<{ id: string; name: string; status: "online" | "idle" }[]>([]);

  useEffect(() => {
    // Fetch agents from backend
    fetch("/api/agents")
      .then((res) => res.json())
      .then(setAgents)
      .catch(() => setAgents([{ id: "default", name: "IndoClaw", status: "idle" }]));
  }, []);

  const navItems = [
    { id: "/", icon: LayoutDashboard, label: "Dashboard" },
    { id: "/chat", icon: MessageSquare, label: "Chat" },
    { id: "/agents", icon: Users, label: "Agents" },
    { id: "/events", icon: Activity, label: "Events" },
    { id: "/config", icon: Settings, label: "Configuration" },
  ];

  const isActive = (path: string) => {
    if (path === "/") return pathname === "/";
    return pathname.startsWith(path);
  };

  return (
    <aside
      className={`fixed left-0 top-0 h-full bg-background border-r border-border transition-all duration-300 z-50 ${
        isOpen ? "w-64" : "w-16"
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        {isOpen ? (
          <div className="flex items-center gap-2">
            <Bot className="w-6 h-6 text-primary" />
            <span className="font-bold text-foreground">IndoClaw</span>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-1">
            <Bot className="w-6 h-6 text-primary" />
          </div>
        )}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-1 rounded hover:bg-muted text-muted-foreground transition-colors"
        >
          {isOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="p-2 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => router.push(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-all ${
              isActive(item.id)
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            }`}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {isOpen && <span className="text-sm font-medium">{item.label}</span>}
          </button>
        ))}
      </nav>

      {/* Agents List */}
      {isOpen && (
        <div className="mt-4 px-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-muted-foreground uppercase">Agents</span>
            <button onClick={() => router.push("/agents")} className="text-xs text-primary hover:underline">
              Manage
            </button>
          </div>
          <div className="space-y-1">
            {agents.map((agent) => (
              <div
                key={agent.id}
                className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-muted cursor-pointer transition-colors"
                onClick={() => router.push(`/chat?agent=${agent.id}`)}
              >
                <span
                  className={`w-2 h-2 rounded-full flex-shrink-0 ${
                    agent.status === "online" ? "bg-green-500" : "bg-gray-400"
                  }`}
                />
                <span className="text-sm text-foreground truncate flex-1">{agent.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Theme Toggle */}
      <div className="absolute bottom-4 left-0 right-0 px-4">
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg hover:bg-muted transition-colors"
        >
          {theme === "dark" ? (
            <Sun className="w-4 h-4 text-yellow-400" />
          ) : (
            <Moon className="w-4 h-4 text-slate-600" />
          )}
          {isOpen && <span className="text-sm text-foreground">
            {theme === "dark" ? "Light Mode" : "Dark Mode"}
          </span>}
        </button>
      </div>
    </aside>
  );
}
