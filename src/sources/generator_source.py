from logging import getLogger

from src.models import Task

logger = getLogger(__name__)


class GeneratorSource:
    """Программно генерирует задачи в заданном количестве."""

    def __init__(self, count: int) -> None:
        if not isinstance(count, int):
            logger.error('Количество задач не целое число')
            raise TypeError("Количество задач должно быть целым числом")
        if count < 0:
            logger.error('Количество задач отрицательно')
            raise ValueError("Количество задач не может быть отрицательным")
        self.count = count

    def get_tasks(self) -> list[Task]:
        tasks = [Task(id=str(i), description=f"Задача {i}", payload=f"data_{i}") for i in range(self.count)]
        logger.info("Сгенерировано %d задач", len(tasks))
        return tasks