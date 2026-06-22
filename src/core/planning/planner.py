"""
Planner module for IndoClaw.
Handles task decomposition and planning.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

try:
    from langchain_openai import ChatOpenAI
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
    except ImportError:
        from langchain.schema import HumanMessage, SystemMessage
    try:
        from langchain_core.prompts import PromptTemplate
    except ImportError:
        from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


@dataclass
class Task:
    """Represents a task in the plan."""
    id: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    result: Any = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class Plan:
    """Represents a plan with multiple tasks."""
    task_id: str
    description: str
    tasks: List[Task] = field(default_factory=list)
    status: str = "pending"
    current_task_index: int = 0
    
    def get_next_task(self) -> Optional[Task]:
        """Get the next pending task."""
        for i, task in enumerate(self.tasks):
            if task.status == "pending" and all(
                self.tasks[j].status == "completed" 
                for j in task.dependencies
            ):
                return task
        return None
    
    def mark_task_completed(self, task_id: str, result: Any = None) -> bool:
        """Mark a task as completed."""
        for task in self.tasks:
            if task.id == task_id:
                task.status = "completed"
                task.result = result
                task.completed_at = datetime.now()
                return True
        return False
    
    def mark_task_failed(self, task_id: str, error: str = None) -> bool:
        """Mark a task as failed."""
        for task in self.tasks:
            if task.id == task_id:
                task.status = "failed"
                task.result = error
                return True
        return False
    
    def is_complete(self) -> bool:
        """Check if all tasks are completed."""
        return all(task.status == "completed" for task in self.tasks)
    
    def get_status(self) -> Dict[str, Any]:
        """Get plan status."""
        return {
            "total_tasks": len(self.tasks),
            "completed": sum(1 for t in self.tasks if t.status == "completed"),
            "pending": sum(1 for t in self.tasks if t.status == "pending"),
            "failed": sum(1 for t in self.tasks if t.status == "failed"),
            "current_task": self.tasks[self.current_task_index].id if self.tasks else None
        }


class Planner:
    """Task planner for decomposing and managing tasks."""
    
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        api_key: Optional[str] = None
    ):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("langchain-openai is required for Planner")
        
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0.7,
            openai_api_key=api_key
        )
        self.plans: Dict[str, Plan] = {}
    
    def create_plan(self, task_description: str, plan_id: str = None) -> Plan:
        """Create a plan for a task description."""
        prompt = PromptTemplate.from_template("""
        Create a step-by-step plan to accomplish the following task:
        
        Task: {task_description}
        
        Return a JSON array of steps with 'id' and 'description' fields.
        Example: [
            {"id": "step1", "description": "First step"},
            {"id": "step2", "description": "Second step"}
        ]
        """)
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt.format(task_description=task_description))])
            
            # Parse response (simple JSON extraction)
            import json
            import re
            
            # Try to extract JSON array from response
            json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
            if json_match:
                steps = json.loads(json_match.group())
            else:
                # Fallback: split by line and create steps
                steps = [
                    {"id": f"step{i+1}", "description": line.strip().strip('- ')}
                    for i, line in enumerate(response.content.split('\n')[:5])
                    if line.strip()
                ]
            
            tasks = [
                Task(id=step['id'], description=step['description'])
                for step in steps
            ]
            
            plan = Plan(
                task_id=plan_id or task_description[:20].replace(' ', '_'),
                description=task_description,
                tasks=tasks
            )
            
            self.plans[plan.task_id] = plan
            return plan
        
        except Exception as e:
            # Fallback: create a simple single-step plan
            plan = Plan(
                task_id=plan_id or "fallback_plan",
                description=task_description,
                tasks=[Task(id="step1", description=task_description)]
            )
            self.plans[plan.task_id] = plan
            return plan
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get a plan by ID."""
        return self.plans.get(plan_id)
    
    def get_next_task(self, plan_id: str) -> Optional[Task]:
        """Get the next task for a plan."""
        plan = self.plans.get(plan_id)
        if plan:
            return plan.get_next_task()
        return None


# Example usage
if __name__ == "__main__":
    try:
        planner = Planner()
        plan = planner.create_plan("Write a Python script to analyze a CSV file")
        print(f"Plan created: {plan.task_id}")
        for task in plan.tasks:
            print(f"  - {task.id}: {task.description}")
    except Exception as e:
        print(f"Planner initialization error (API key may be missing): {e}")