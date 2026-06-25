"""
Tests for the plan generation and execution system.
"""

import pytest
from datetime import datetime

from src.core.plan.base import Plan, PlanStep, PlanStatus, PlanReview


class TestPlanStep:
    """Tests for PlanStep dataclass."""

    def test_plan_step_creation(self):
        """Test creating a PlanStep."""
        step = PlanStep(
            step_number=1,
            description="Search for information",
            tool_name="web_search",
            input_data={"query": "test"},
            expected_output="Search results",
            confidence=0.9
        )
        assert step.step_number == 1
        assert step.description == "Search for information"
        assert step.tool_name == "web_search"
        assert step.input_data == {"query": "test"}
        assert step.expected_output == "Search results"
        assert step.confidence == 0.9

    def test_plan_step_to_dict(self):
        """Test converting PlanStep to dictionary."""
        step = PlanStep(
            step_number=1,
            description="Test step",
            tool_name="calculator",
            input_data={"expression": "2+2"},
            expected_output="4",
            confidence=0.8
        )
        result = step.to_dict()
        assert result["step_number"] == 1
        assert result["description"] == "Test step"
        assert result["tool_name"] == "calculator"
        assert result["input_data"] == {"expression": "2+2"}
        assert result["expected_output"] == "4"
        assert result["confidence"] == 0.8


class TestPlan:
    """Tests for Plan dataclass."""

    def test_plan_creation(self):
        """Test creating a Plan."""
        plan = Plan(
            task="Calculate 5 * 10",
            steps=[],
            status=PlanStatus.DRAFT
        )
        assert plan.task == "Calculate 5 * 10"
        assert plan.status == PlanStatus.DRAFT
        assert len(plan.steps) == 0

    def test_plan_with_steps(self):
        """Test creating a Plan with steps."""
        step1 = PlanStep(
            step_number=1,
            description="First step",
            tool_name="calculator",
            input_data={"expression": "5 * 10"}
        )
        plan = Plan(
            task="Calculate 5 * 10",
            steps=[step1],
            status=PlanStatus.APPROVED
        )
        assert len(plan.steps) == 1
        assert plan.status == PlanStatus.APPROVED

    def test_plan_to_dict(self):
        """Test converting Plan to dictionary."""
        step = PlanStep(
            step_number=1,
            description="Test step",
            tool_name="web_search",
            input_data={"query": "test"}
        )
        plan = Plan(
            task="Test task",
            steps=[step],
            status=PlanStatus.REVIEWING
        )
        result = plan.to_dict()
        assert result["task"] == "Test task"
        assert result["status"] == "reviewing"
        assert len(result["steps"]) == 1

    def test_plan_to_json(self):
        """Test converting Plan to JSON."""
        step = PlanStep(
            step_number=1,
            description="Test step",
            tool_name="calculator",
            input_data={"expression": "1+1"}
        )
        plan = Plan(
            task="Test task",
            steps=[step],
            status=PlanStatus.DRAFT
        )
        json_str = plan.to_json()
        assert '"task": "Test task"' in json_str
        assert '"status": "draft"' in json_str
        assert '"step_number": 1' in json_str

    def test_plan_timestamps(self):
        """Test that plan has creation timestamp."""
        plan = Plan(
            task="Test task",
            steps=[]
        )
        assert plan.created_at is not None
        assert isinstance(plan.created_at, datetime)


class TestPlanStatus:
    """Tests for PlanStatus enum."""

    def test_all_statuses(self):
        """Test all plan statuses."""
        statuses = [
            PlanStatus.DRAFT,
            PlanStatus.REVIEWING,
            PlanStatus.APPROVED,
            PlanStatus.REJECTED,
            PlanStatus.EXECUTING,
            PlanStatus.COMPLETED,
            PlanStatus.FAILED
        ]
        for status in statuses:
            assert status.value is not None
            assert isinstance(status.value, str)

    def test_status_values(self):
        """Test status enum values."""
        assert PlanStatus.DRAFT.value == "draft"
        assert PlanStatus.APPROVED.value == "approved"
        assert PlanStatus.COMPLETED.value == "completed"


class TestPlanReview:
    """Tests for PlanReview dataclass."""

    def test_plan_review_creation(self):
        """Test creating a PlanReview."""
        plan = Plan(
            task="Test task",
            steps=[]
        )
        review = PlanReview(plan=plan)
        assert review.plan == plan
        assert review.approval_required is True
        assert review.can_modify is True

    def test_plan_review_to_dict(self):
        """Test converting PlanReview to dictionary."""
        plan = Plan(
            task="Test task",
            steps=[]
        )
        review = PlanReview(
            plan=plan,
            user_instructions="Please review carefully",
            approval_required=True,
            can_modify=False
        )
        result = review.to_dict()
        assert result["user_instructions"] == "Please review carefully"
        assert result["approval_required"] is True
        assert result["can_modify"] is False
