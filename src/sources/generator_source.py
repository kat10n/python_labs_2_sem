from src.models import Task


class GeneratorSource:
    """Программно генерирует задачи в заданном количестве."""

    def __init__(self, count: int) -> None:
        self.count = count

    def get_tasks(self) -> list[Task]:
        return [Task(id=str(i), payload=f"data_{i}") for i in range(self.count)]