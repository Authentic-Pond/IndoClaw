"""
Approval provider interface for IndoClaw Human-in-the-Loop features.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ApprovalDecision(Enum):
    """Approval decision types."""
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    MODIFIED = "modified"


@dataclass
class ApprovalRequest:
    """A request for approval from a user."""
    tool_name: str
    action: str
    input_data: Dict[str, Any]
    reason: str
    confidence: float
    user_id: str = "default"
    timestamp: Optional[str] = None


@dataclass
class ApprovalResult:
    """Result of an approval request."""
    decision: ApprovalDecision
    approved: bool
    modified_input: Optional[Dict[str, Any]] = None
    rejection_reason: Optional[str] = None
    user_id: Optional[str] = None


class ApprovalProvider(ABC):
    """
    Abstract base class for approval providers.
    Defines the interface for requesting and recording approval decisions.
    """

    @abstractmethod
    def request_approval(self, request: ApprovalRequest) -> ApprovalResult:
        """
        Request approval for an action.

        Args:
            request: The approval request with details about the action

        Returns:
            ApprovalResult with the decision and any modifications
        """
        pass

    @abstractmethod
    def approve(self, request_id: str, modified_input: Dict[str, Any] = None) -> ApprovalResult:
        """
        Manually approve a pending request.

        Args:
            request_id: The ID of the request to approve
            modified_input: Optional modified input data

        Returns:
            ApprovalResult with APPROVED decision
        """
        pass

    @abstractmethod
    def reject(self, request_id: str, reason: str) -> ApprovalResult:
        """
        Manually reject a pending request.

        Args:
            request_id: The ID of the request to reject
            reason: The reason for rejection

        Returns:
            ApprovalResult with REJECTED decision
        """
        pass

    @abstractmethod
    def is_auto_approve(self, request: ApprovalRequest) -> bool:
        """
        Check if a request should be auto-approved.

        Args:
            request: The approval request to check

        Returns:
            True if auto-approve, False otherwise
        """
        pass
