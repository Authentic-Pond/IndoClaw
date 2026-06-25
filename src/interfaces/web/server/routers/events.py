"""
Events API routes for IndoClaw Web Interface.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()


class Event(BaseModel):
    event_type: str
    timestamp: str
    agent_id: str
    payload: dict
    metadata: dict


# Event history
event_history: List[Event] = []


@router.get("/events")
async def get_events(
    event_type: Optional[str] = None,
    limit: int = 100
):
    """Get event history."""
    try:
        from src.core.events.publisher import EventPublisher, EventType

        # Get event publisher from agent
        publisher = EventPublisher()
        history = publisher.get_history()

        events = []
        for event in history[-limit:]:
            events.append(Event(
                event_type=event.event_type.value,
                timestamp=event.timestamp,
                agent_id=event.agent_id,
                payload=event.payload,
                metadata=event.metadata
            ))

        # Filter by event type if specified
        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return {"events": events}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/types")
async def get_event_types():
    """Get available event types."""
    try:
        from src.core.events.publisher import EventType

        return {
            "types": [e.value for e in EventType]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/events")
async def clear_events():
    """Clear event history."""
    event_history.clear()
    return {"status": "cleared"}
