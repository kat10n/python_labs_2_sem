from logging import getLogger, basicConfig, DEBUG
from src.protocols import TaskSource
from src.sources.api_stub import ApiStubSource
from src.sources.file_source import FileSource
from src.sources.generator_source import GeneratorSource


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


if __name__ == "__main__":
    sources = [
        create_source(FileSource, "text_files/tasks.txt"),
        create_source(GeneratorSource, 5),
        create_source(ApiStubSource),
    ]

    for src in sources:
        print(f"\n{type(src).__name__}")
        process_tasks(src)
