"""
Auto-approval provider for IndoClaw.
Auto-approves low-risk tools based on confidence threshold.
"""

from typing import Dict, Any, List
from .base import ApprovalProvider, ApprovalRequest, ApprovalResult, ApprovalDecision


class AutoApprovalProvider(ApprovalProvider):
    """
    Auto-approval provider that approves low-risk actions based on confidence threshold.
    """

    def __init__(self, confidence_threshold: float = 0.8):
        """
        Initialize the auto-approval provider.

        Args:
            confidence_threshold: Minimum confidence for auto-approval (0.0 to 1.0)
        """
        self.confidence_threshold = confidence_threshold
        self._approved_count = 0
        self._rejected_count = 0

    def request_approval(self, request: ApprovalRequest) -> ApprovalResult:
        """
        Request approval - auto-approves if confidence is above threshold.

        Args:
            request: The approval request with details about the action

        Returns:
            ApprovalResult with decision
        """
        if self.is_auto_approve(request):
            self._approved_count += 1
            return ApprovalResult(
                decision=ApprovalDecision.APPROVED,
                approved=True,
                user_id=request.user_id
            )
        else:
            self._rejected_count += 1
            return ApprovalResult(
                decision=ApprovalDecision.PENDING,
                approved=False,
                rejection_reason="Manual approval required - confidence below threshold"
            )

    def approve(self, request_id: str, modified_input: Dict[str, Any] = None) -> ApprovalResult:
        """
        Manually approve a request (stub implementation).

        Args:
            request_id: The ID of the request to approve
            modified_input: Optional modified input data

        Returns:
            ApprovalResult with APPROVED decision
        """
        self._approved_count += 1
        return ApprovalResult(
            decision=ApprovalDecision.APPROVED,
            approved=True,
            modified_input=modified_input,
            user_id="system"
        )

    def reject(self, request_id: str, reason: str) -> ApprovalResult:
        """
        Manually reject a request (stub implementation).

        Args:
            request_id: The ID of the request to reject
            reason: The reason for rejection

        Returns:
            ApprovalResult with REJECTED decision
        """
        self._rejected_count += 1
        return ApprovalResult(
            decision=ApprovalDecision.REJECTED,
            approved=False,
            rejection_reason=reason,
            user_id="system"
        )

    def is_auto_approve(self, request: ApprovalRequest) -> bool:
        """
        Check if a request should be auto-approved.

        Args:
            request: The approval request to check

        Returns:
            True if confidence >= threshold, False otherwise
        """
        return request.confidence >= self.confidence_threshold

    def get_stats(self) -> Dict[str, int]:
        """
        Get approval statistics.

        Returns:
            Dict with approved and rejected counts
        """
        return {
            "approved": self._approved_count,
            "rejected": self._rejected_count
        }
