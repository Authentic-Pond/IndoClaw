"""
File operation tools for IndoClaw.
"""

import os
import json
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path

from .base import BaseTool, ToolResult


class FileOperationTool(BaseTool):
    """File operations tool for reading, writing, and managing files."""

    name: str = "file_ops"
    description: str = "Read, write, and manage files and directories"

    def __init__(self, base_dir: str = "."):
        super().__init__()
        self.base_dir = Path(base_dir).resolve()
        self._ensure_base_dir()

    def _ensure_base_dir(self) -> None:
        """Ensure base directory exists."""
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to base directory."""
        full_path = (self.base_dir / path).resolve()
        # Security check: ensure resolved path is within base directory
        if not str(full_path).startswith(str(self.base_dir)):
            raise ValueError(f"Access denied: {path} is outside base directory")
        return full_path

    def _run(self, **kwargs) -> ToolResult:
        """
        Execute file operation based on operation kwarg.
        Operations: read, write, list_dir, create_dir, delete, exists, read_json, write_json
        """
        operation = kwargs.get("operation")
        if not operation:
            return ToolResult(
                success=False,
                error="No operation specified. Available: read, write, list_dir, create_dir, delete, exists, read_json, write_json"
            )

        operations = {
            "read": self._read_file,
            "write": self._write_file,
            "list_dir": self._list_directory,
            "create_dir": self._create_directory,
            "delete": self._delete_path,
            "exists": self._check_exists,
            "read_json": self._read_json,
            "write_json": self._write_json,
        }

        if operation not in operations:
            return ToolResult(
                success=False,
                error=f"Unknown operation: {operation}"
            )

        try:
            return operations[operation](**kwargs)
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )

    def _read_file(self, path: str, **kwargs) -> ToolResult:
        """Read file content."""
        try:
            file_path = self._resolve_path(path)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return ToolResult(
                success=True,
                content={"path": str(file_path), "content": content}
            )
        except FileNotFoundError:
            return ToolResult(
                success=False,
                error=f"File not found: {path}"
            )

    def _write_file(self, path: str, content: str, overwrite: bool = False, **kwargs) -> ToolResult:
        """Write content to file."""
        try:
            file_path = self._resolve_path(path)

            if file_path.exists() and not overwrite:
                return ToolResult(
                    success=False,
                    error=f"File already exists: {path}. Use overwrite=True to replace."
                )

            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return ToolResult(
                success=True,
                content={"path": str(file_path), "size": len(content)}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )

    def _list_directory(self, path: str = ".", pattern: str = "*", **kwargs) -> ToolResult:
        """List directory contents."""
        try:
            dir_path = self._resolve_path(path)
            items = []

            for item in dir_path.glob(pattern):
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(item.relative_to(self.base_dir))
                })

            return ToolResult(
                success=True,
                content={"path": str(dir_path), "items": items}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )

    def _create_directory(self, path: str, **kwargs) -> ToolResult:
        """Create a new directory."""
        try:
            dir_path = self._resolve_path(path)
            dir_path.mkdir(parents=True, exist_ok=True)
            return ToolResult(
                success=True,
                content={"path": str(dir_path), "created": True}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )

    def _delete_path(self, path: str, **kwargs) -> ToolResult:
        """Delete a file or directory."""
        try:
            target_path = self._resolve_path(path)

            if target_path.is_dir():
                import shutil
                shutil.rmtree(target_path)
            else:
                target_path.unlink()

            return ToolResult(
                success=True,
                content={"path": str(target_path), "deleted": True}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )

    def _check_exists(self, path: str, **kwargs) -> ToolResult:
        """Check if path exists."""
        try:
            target_path = self._resolve_path(path)
            exists = target_path.exists()
            return ToolResult(
                success=True,
                content={"path": str(target_path), "exists": exists}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )

    def _read_json(self, path: str, **kwargs) -> ToolResult:
        """Read JSON file."""
        try:
            file_path = self._resolve_path(path)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ToolResult(
                success=True,
                content=data
            )
        except json.JSONDecodeError as e:
            return ToolResult(
                success=False,
                error=f"Invalid JSON: {str(e)}"
            )

    def _write_json(self, path: str, data: Dict, indent: int = 2, **kwargs) -> ToolResult:
        """Write data to JSON file."""
        try:
            file_path = self._resolve_path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent)
            return ToolResult(
                success=True,
                content={"path": str(file_path), "size": len(json.dumps(data))}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


# Example usage
if __name__ == "__main__":
    tool = FileOperationTool()
    print(tool.get_info())
