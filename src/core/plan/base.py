"""
Plan data structures for IndoClaw Human-in-the-Loop features.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime


class PlanStatus(Enum):
    """Status of a plan."""
    DRAFT = "draft"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PlanStep:
    """A single step in a plan."""
    step_number: int
    description: str
    tool_name: str
    input_data: Dict[str, Any]
    expected_output: Optional[str] = None
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_number": self.step_number,
            "description": self.description,
            "tool_name": self.tool_name,
            "input_data": self.input_data,
            "expected_output": self.expected_output,
            "confidence": self.confidence
        }


@dataclass
class Plan:
    """A plan for task execution."""
    task: str
    steps: List[PlanStep] = field(default_factory=list)
    status: PlanStatus = PlanStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    user_id: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task": self.task,
            "steps": [step.to_dict() for step in self.steps],
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "user_id": self.user_id,
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        import json
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class PlanReview:
    """A plan review request."""
    plan: Plan
    user_instructions: Optional[str] = None
    approval_required: bool = True
    can_modify: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plan": self.plan.to_dict(),
            "user_instructions": self.user_instructions,
            "approval_required": self.approval_required,
            "can_modify": self.can_modify
        }
