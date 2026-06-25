"""
Tests for the approval system in IndoClaw.
"""

import pytest
from src.core.approval.base import (
    ApprovalProvider,
    ApprovalRequest,
    ApprovalResult,
    ApprovalDecision
)
from src.core.approval.auto_approval import AutoApprovalProvider


class TestApprovalRequest:
    """Tests for ApprovalRequest dataclass."""

    def test_approval_request_creation(self):
        """Test creating an approval request."""
        request = ApprovalRequest(
            tool_name="calculator",
            action="multiply",
            input_data={"a": 5, "b": 3},
            reason="Multiplication requires approval",
            confidence=0.9,
            user_id="user1"
        )
        assert request.tool_name == "calculator"
        assert request.confidence == 0.9
        assert request.user_id == "user1"

    def test_approval_request_default_user_id(self):
        """Test approval request with default user_id."""
        request = ApprovalRequest(
            tool_name="calculator",
            action="add",
            input_data={"a": 1, "b": 2},
            reason="Addition",
            confidence=0.8
        )
        assert request.user_id == "default"


class TestApprovalResult:
    """Tests for ApprovalResult dataclass."""

    def test_approval_result_approved(self):
        """Test approved approval result."""
        result = ApprovalResult(
            decision=ApprovalDecision.APPROVED,
            approved=True,
            user_id="user1"
        )
        assert result.approved is True
        assert result.decision == ApprovalDecision.APPROVED

    def test_approval_result_rejected(self):
        """Test rejected approval result."""
        result = ApprovalResult(
            decision=ApprovalDecision.REJECTED,
            approved=False,
            rejection_reason="Confidence below threshold"
        )
        assert result.approved is False
        assert result.rejection_reason == "Confidence below threshold"

    def test_approval_result_modified(self):
        """Test modified approval result."""
        result = ApprovalResult(
            decision=ApprovalDecision.MODIFIED,
            approved=True,
            modified_input={"a": 10, "b": 5}
        )
        assert result.approved is True
        assert result.modified_input == {"a": 10, "b": 5}


class TestAutoApprovalProvider:
    """Tests for AutoApprovalProvider."""

    def test_auto_approve_high_confidence(self):
        """Test auto-approval for high confidence."""
        provider = AutoApprovalProvider(confidence_threshold=0.8)
        request = ApprovalRequest(
            tool_name="calculator",
            action="add",
            input_data={},
            reason="Test",
            confidence=0.9
        )
        result = provider.request_approval(request)
        assert result.approved is True
        assert result.decision == ApprovalDecision.APPROVED

    def test_auto_reject_low_confidence(self):
        """Test rejection for low confidence."""
        provider = AutoApprovalProvider(confidence_threshold=0.8)
        request = ApprovalRequest(
            tool_name="calculator",
            action="delete_file",
            input_data={},
            reason="Test",
            confidence=0.5
        )
        result = provider.request_approval(request)
        assert result.approved is False
        assert result.decision == ApprovalDecision.PENDING

    def test_exact_threshold(self):
        """Test approval at exact threshold."""
        provider = AutoApprovalProvider(confidence_threshold=0.8)
        request = ApprovalRequest(
            tool_name="calculator",
            action="add",
            input_data={},
            reason="Test",
            confidence=0.8
        )
        result = provider.request_approval(request)
        assert result.approved is True

    def test_stats(self):
        """Test approval statistics."""
        provider = AutoApprovalProvider(confidence_threshold=0.8)
        high_conf = ApprovalRequest("tool", "action", {}, "test", 0.9)
        low_conf = ApprovalRequest("tool", "action", {}, "test", 0.5)

        provider.request_approval(high_conf)
        provider.request_approval(low_conf)

        stats = provider.get_stats()
        assert stats["approved"] == 1
        assert stats["rejected"] == 1


class TestManualApproval:
    """Tests for manual approval methods."""

    def test_manual_approve(self):
        """Test manual approval."""
        provider = AutoApprovalProvider()
        result = provider.approve("request123")
        assert result.approved is True
        assert result.decision == ApprovalDecision.APPROVED

    def test_manual_reject(self):
        """Test manual rejection."""
        provider = AutoApprovalProvider()
        result = provider.reject("request123", "User rejected")
        assert result.approved is False
        assert result.rejection_reason == "User rejected"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
