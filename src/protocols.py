from typing import Protocol, runtime_checkable

from src.models import Task


@runtime_checkable
class TaskSource(Protocol):
    """Протокол для источников задач."""
    def get_tasks(self) -> list[Task]: ...


@runtime_checkable
class TaskHandler(Protocol):
    """Протокол для обработчиков задач."""
    def can_handle(self, task: Task) -> bool: ...
    async def handle(self, task: Task) -> None: ...