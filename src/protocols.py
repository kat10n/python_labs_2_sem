from typing import Protocol, runtime_checkable

from src.models import Task


@runtime_checkable
class TaskSource(Protocol):
    """Контракт для источников задач."""
    def get_tasks(self) -> list[Task]: ...