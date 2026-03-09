from src.protocols import TaskSource
from src.sources.api_stub import ApiStubSource
from src.sources.file_source import FileSource
from src.sources.generator_source import GeneratorSource


def create_source(source_class: type, *args, **kwargs) -> TaskSource:
    """Создаёт источник, проверяя контракт через issubclass."""
    if not issubclass(source_class, TaskSource):
        raise TypeError(f"{source_class.__name__} не реализует TaskSource")
    return source_class(*args, **kwargs)


def process_tasks(source: TaskSource) -> None:
    """Проверяет источник через isinstance и печатает его задачи."""
    if not isinstance(source, TaskSource):
        raise TypeError(f"{type(source).__name__} не реализует TaskSource")

    for task in source.get_tasks():
        print(f"  [{task.id}] {task.payload}")


if __name__ == "__main__":
    sources = [
        create_source(FileSource, "tasks.txt"),
        create_source(GeneratorSource, 5),
        create_source(ApiStubSource),
    ]

    for src in sources:
        print(f"\n--- {type(src).__name__} ---")
        process_tasks(src)
