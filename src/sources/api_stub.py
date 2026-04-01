from logging import getLogger

from src.models import Task

logger = getLogger(__name__)


class ApiStubSource:
    """Имитирует получение задач от внешнего API."""

    def get_tasks(self) -> list[Task]:
        tasks = [
            Task(id="api_1", description="Запрос к серверу", payload={"value": 100}),
            Task(id="api_2", description="Обработка ответа", payload={"value": 200}),
        ]
        logger.info("Получено %d задач из API-заглушки", len(tasks))
        return tasks