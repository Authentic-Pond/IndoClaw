"use client";

import { useState, useEffect, useCallback } from "react";
import { Activity, Filter, X, RefreshCw, Clock, Trash2 } from "lucide-react";

interface Event {
  event_type: string;
  timestamp: string;
  agent_id: string;
  payload: Record<string, any>;
  metadata: Record<string, string>;
}

const EVENT_TYPES = [
  "task_start",
  "task_end",
  "tool_executed",
  "tool_approval_needed",
  "error",
  "plan_created",
  "plan_approved",
  "input_requested",
  "input_received",
  "agent_thought",
  "memory_updated",
];

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedType, setSelectedType] = useState<string>("all");
  const [loading, setLoading] = useState(false);

  const fetchEvents = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/events");
      const data = await response.json();
      setEvents(data.events || []);
    } catch (error) {
      console.error("Failed to fetch events:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEvents();
    // Set up polling for new events
    const interval = setInterval(fetchEvents, 5000);
    return () => clearInterval(interval);
  }, [fetchEvents]);

  const handleClearEvents = async () => {
    if (!confirm("Are you sure you want to clear all events?")) return;

    try {
      await fetch("/api/events", { method: "DELETE" });
      setEvents([]);
    } catch (error) {
      console.error("Failed to clear events:", error);
    }
  };

  const filteredEvents =
    selectedType === "all"
      ? events
      : events.filter((e) => e.event_type === selectedType);

  const getTypeColor = (type: string) => {
    switch (type) {
      case "task_start":
        return "bg-blue-500";
      case "task_end":
        return "bg-green-500";
      case "tool_executed":
        return "bg-purple-500";
      case "error":
        return "bg-red-500";
      case "plan_created":
        return "bg-orange-500";
      default:
        return "bg-gray-500";
    }
  };

  const formatPayload = (payload: Record<string, any>) => {
    return JSON.stringify(payload, null, 2);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Event Log</h1>
          <p className="text-muted-foreground mt-1">
            Real-time events from your agents
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchEvents}
            disabled={loading}
            className="p-2 text-muted-foreground hover:text-foreground rounded-lg transition-colors"
            title="Refresh events"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={handleClearEvents}
            className="p-2 text-muted-foreground hover:text-destructive rounded-lg transition-colors"
            title="Clear events"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-2 bg-secondary p-2 rounded-lg">
        <Filter className="w-4 h-4 text-muted-foreground" />
        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="bg-transparent border-none focus:ring-0 text-sm text-foreground w-full"
        >
          <option value="all">All Event Types</option>
          {EVENT_TYPES.map((type) => (
            <option key={type} value={type}>
              {type.replace("_", " ")}
            </option>
          ))}
        </select>
      </div>

      {/* Event Count */}
      <div className="flex items-center gap-4 text-sm text-muted-foreground">
        <span>Total events: {events.length}</span>
        <span>Showing: {filteredEvents.length}</span>
      </div>

      {/* Events List */}
      <div className="space-y-3">
        {filteredEvents.length === 0 ? (
          <div className="text-center py-16 bg-secondary/50 rounded-lg">
            <Activity className="w-16 h-16 mx-auto mb-4 opacity-20" />
            <p className="text-muted-foreground">No events yet</p>
          </div>
        ) : (
          filteredEvents.map((event, idx) => (
            <div
              key={idx}
              className="bg-secondary rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${getTypeColor(event.event_type)}`} />
                  <span className="font-medium capitalize">{event.event_type.replace("_", " ")}</span>
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(event.timestamp).toLocaleString()}
                  </span>
                </div>
                <span className="text-xs bg-muted px-2 py-1 rounded text-muted-foreground">
                  {event.agent_id}
                </span>
              </div>

              <div className="bg-background rounded p-3">
                {event.payload && Object.keys(event.payload).length > 0 ? (
                  <pre className="text-xs text-muted-foreground whitespace-pre-wrap font-mono">
                    {formatPayload(event.payload)}
                  </pre>
                ) : (
                  <p className="text-sm text-muted-foreground italic">
                    No payload data
                  </p>
                )}
              </div>

              {event.metadata && Object.keys(event.metadata).length > 0 && (
                <div className="mt-2 text-xs text-muted-foreground">
                  <p className="font-medium mb-1">Metadata:</p>
                  <pre className="whitespace-pre-wrap font-mono">
                    {JSON.stringify(event.metadata, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
