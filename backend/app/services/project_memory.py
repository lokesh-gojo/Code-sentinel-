from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone


class MemoryRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    repo_full_name: str
    memory_type: str  # "convention", "decision", "approved_patch", "framework_pattern"
    title: str
    description: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ProjectMemoryService:
    """
    Persistent project-level knowledge base storing approved architectural decisions,
    coding conventions, and previously verified patches.
    """

    def __init__(self):
        # In-memory store with default conventions
        self._memory_store: Dict[str, List[MemoryRecord]] = {
            "default": [
                MemoryRecord(
                    repo_full_name="default",
                    memory_type="convention",
                    title="Pydantic Response Schemas",
                    description="All API endpoints must return typed Pydantic v2 schemas rather than raw dicts.",
                ),
                MemoryRecord(
                    repo_full_name="default",
                    memory_type="decision",
                    title="Isolated Sandbox Execution",
                    description="Untrusted user code must run inside E2B or restricted subprocesses, never on host.",
                ),
                MemoryRecord(
                    repo_full_name="default",
                    memory_type="convention",
                    title="Defensive Null Validation",
                    description="Always perform explicit null checks on optional parameters before property access.",
                ),
            ]
        }

    def add_record(self, repo: str, memory_type: str, title: str, description: str) -> MemoryRecord:
        record = MemoryRecord(
            repo_full_name=repo,
            memory_type=memory_type,
            title=title,
            description=description,
        )
        if repo not in self._memory_store:
            self._memory_store[repo] = []
        self._memory_store[repo].append(record)
        return record

    def get_records(self, repo: str) -> List[MemoryRecord]:
        records = list(self._memory_store.get(repo, []))
        # Include default conventions
        records.extend(self._memory_store.get("default", []))
        return records

    def format_context_for_prompt(self, repo: str) -> str:
        records = self.get_records(repo)
        if not records:
            return "No prior project conventions recorded."
        lines = [f"- [{r.memory_type.upper()}] {r.title}: {r.description}" for r in records]
        return "\n".join(lines)


project_memory_service = ProjectMemoryService()
