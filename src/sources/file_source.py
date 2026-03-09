from src.models import Task


class FileSource:
    """Загружает задачи из txt-файла"""

    def __init__(self, filename: str) -> None:
        self.filename = filename

    def get_tasks(self) -> list[Task]:
        tasks: list[Task] = []
        with open(self.filename, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                task_id, payload = line.split(";", maxsplit=1)
                tasks.append(Task(id=task_id, payload=payload))
        return tasks