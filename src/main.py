import asyncio
from logging import getLogger, basicConfig, DEBUG
from src.protocols import TaskSource
from src.sources.api_stub import ApiStubSource
from src.sources.file_source import FileSource
from src.sources.generator_source import GeneratorSource
from src.models import Task
from src.task_queue import TaskQueue
from src.executor import (AsyncTaskExecutor, TextPayloadHandler, DictPayloadHandler, FallbackHandler)


logger = getLogger()
format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
basicConfig(filename='shell.log', encoding='utf-8',
            level=DEBUG, format=format, filemode='w')

def create_source(source_class: type, *args, **kwargs) -> TaskSource:
    """Создаёт источник, проверяя контракт через issubclass."""
    if not issubclass(source_class, TaskSource): # работает с классами
        logger.error("%s не реализует протокол TaskSource", source_class.__name__)
        raise TypeError(f"{source_class.__name__} не реализует TaskSource")
    logger.info("Создан источник %s", source_class.__name__)
    return source_class(*args, **kwargs)


def process_tasks(source: TaskSource) -> None:
    """Проверяет источник через isinstance и печатает его задачи."""
    if not isinstance(source, TaskSource): # работает с экземплярами
        logger.error("%s не реализует протокол TaskSource", type(source).__name__)
        raise TypeError(f"{type(source).__name__} не реализует TaskSource")

    tasks = source.get_tasks()
    logger.info("Обработка %d задач из %s", len(tasks), type(source).__name__)
    for task in tasks:
        print(f"  [{task.id}] {task.payload}")


async def main():
    sources = [
        create_source(FileSource, "text_files/tasks.txt"),
        create_source(GeneratorSource, 5),
        create_source(ApiStubSource),
    ]
    print("Лаба 1")
    for src in sources:
        print(f"\n{type(src).__name__}")
        process_tasks(src)
    print("Лаба 2")
    task1 = Task(id="t1", description="djjfjfjfj", priority=9, status="pending")
    task2 = Task(id="t2", description="fjfjfjf", priority=5, status="pending")
    task3 = Task(id="t3", description="woowowowo", priority=3, status="done")
    task4 = Task(id="t4", description="kfkfkfkfkf", priority=7, status="in_progress")
    print(task1)
    print(task2)
    print(task3)
    print(task4)
    for task in [task1, task2, task3, task4]:
        if task.is_ready:
            print(task.id)
    print("Лаба 3")
    queue = TaskQueue(tasks=[task1, task2, task3, task4])
    print(f"Длина очереди: {len(queue)}")
    print("Task у которых status=pending")
    for task in queue.iter_filtered(status="pending"):
        print(task.id)
    print("Task у которых min_priority=5")
    for task in queue.iter_filtered(min_priority=5):
        print(task.id)
    def print_description(task):
        return task.description
    results = list(queue.process(print_description, consume=False, status="pending"))
    print("Описания для task у которых status=pending")
    for r in results:
        print(f"{r}")

    print("Лаба 4")
    t_text = Task(id="lab4_1", description="Текстовая задача", priority=1, status="pending")
    t_text.payload = "Какой-то текст для обработки"

    t_dict = Task(id="lab4_2", description="Словарная задача", priority=2, status="pending")
    t_dict.payload = {"method": "GET", "url": "/api/users"}

    t_fall = Task(id="lab4_3", description="Неизвестный тип", priority=3, status="pending")
    t_fall.payload = 99999

    t_skip = Task(id="lab4_4", description="Пропуск", priority=4, status="done")

    queue4 = TaskQueue(tasks=[t_text, t_dict, t_fall, t_skip])

    handlers = [
        TextPayloadHandler(),
        DictPayloadHandler(),
        FallbackHandler()
    ]

    async with AsyncTaskExecutor(handlers=handlers) as executor:
        await executor.run(queue4)

if __name__ == "__main__":
    asyncio.run(main())