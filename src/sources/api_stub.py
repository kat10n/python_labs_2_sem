from src.models import Task


class ApiStubSource:
    """Имитирует получение задач от внешнего API."""

    def get_tasks(self) -> list[Task]:
        return [
            Task(id="api_1", payload={"value": 100}),
            Task(id="api_2", payload={"value": 200}),
        ]