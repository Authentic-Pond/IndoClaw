"""
Calculator tool for IndoClaw.
"""

import ast
import operator
from typing import Any, Dict, Optional

from .base import BaseTool, ToolResult


class CalculatorTool(BaseTool):
    """Calculator tool for mathematical expressions."""
    
    name: str = "calculator"
    description: str = "Calculate mathematical expressions safely"
    
    # Safe operators for AST evaluation
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
    }
    
    def execute(self, expression: str, **kwargs) -> ToolResult:
        """Execute a mathematical expression."""
        try:
            result = self._evaluate(expression)
            return ToolResult(
                success=True,
                content={
                    "expression": expression,
                    "result": result
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    def _evaluate(self, expression: str) -> Any:
        """Safely evaluate a mathematical expression."""
        # Clean the expression
        expression = self._clean_expression(expression)
        
        # Parse to AST
        tree = ast.parse(expression, mode='eval')
        
        return self._eval_node(tree.body)
    
    def _clean_expression(self, expression: str) -> str:
        """Clean and validate the expression."""
        # Remove common prefixes
        expression = expression.strip()
        for prefix in ['calculate ', 'calc ', '= ', '=', '']:
            if expression.startswith(prefix):
                expression = expression[len(prefix):].strip()
                break
        
        # Remove any non-math characters (keep numbers, operators, parens, etc.)
        allowed_chars = set('0123456789+-*/()., ')
        for char in expression:
            if char not in allowed_chars:
                raise ValueError(f"Invalid character in expression: {char}")
        
        return expression
    
    def _eval_node(self, node: ast.AST) -> Any:
        """Recursively evaluate an AST node."""
        if isinstance(node, ast.Num):  # Number
            return node.n
        
        if isinstance(node, ast.BinOp):  # Binary operation
            op_type = type(node.op)
            if op_type not in self.SAFE_OPERATORS:
                raise ValueError(f"Unsupported operator: {op_type}")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.SAFE_OPERATORS[op_type](left, right)
        
        if isinstance(node, ast.UnaryOp):  # Unary operation
            op_type = type(node.op)
            if op_type not in self.SAFE_OPERATORS:
                raise ValueError(f"Unsupported unary operator: {op_type}")
            operand = self._eval_node(node.operand)
            return self.SAFE_OPERATORS[op_type](operand)
        
        if isinstance(node, ast.Expression):  # Expression wrapper
            return self._eval_node(node.body)
        
        raise ValueError(f"Unsupported expression type: {type(node)}")


# Example usage
if __name__ == "__main__":
    tool = CalculatorTool()
    print(tool.get_info())
    print(tool.execute("2 + 2 * 3"))