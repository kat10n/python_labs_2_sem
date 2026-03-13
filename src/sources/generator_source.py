from logging import getLogger

from src.models import Task

logger = getLogger(__name__)


class GeneratorSource:
    """Программно генерирует задачи в заданном количестве."""

    def __init__(self, count: int) -> None:
        if not isinstance(count, int) or isinstance(count, bool):
            raise TypeError("Количество задач должно быть целым числом")
        if count < 0:
            raise ValueError("Количество задач не может быть отрицательным")
        self.count = count

    def get_tasks(self) -> list[Task]:
        tasks = [Task(id=str(i), payload=f"data_{i}") for i in range(self.count)]
        logger.info("Сгенерировано %d задач", len(tasks))
        return tasks