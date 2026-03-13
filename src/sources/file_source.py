import os
from logging import getLogger

from src.models import Task

logger = getLogger(__name__)


class FileSource:
    """Загружает задачи из txt-файла."""

    def __init__(self, filename: str) -> None:
        if not isinstance(filename, str):
            raise TypeError("Имя файла должно быть строкой")
        if not filename:
            raise ValueError("Имя файла не должно быть пустым")
        if not filename.lower().endswith(".txt"):
            raise ValueError("Файл должен иметь расширение .txt")
        self.filename = filename

    def get_tasks(self) -> list[Task]:
        if not os.path.isfile(self.filename):
            logger.error("Файл %s не найден", self.filename)
            raise FileNotFoundError(f"Файл {self.filename} не найден")
        tasks: list[Task] = []
        with open(self.filename, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                task_id, payload = line.split(";", maxsplit=1)
                tasks.append(Task(id=task_id, payload=payload))
        logger.info("Загружено %d задач из %s", len(tasks), self.filename)
        return tasks