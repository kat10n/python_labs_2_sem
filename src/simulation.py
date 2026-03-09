"""Интерактивная симуляция подсистемы приёма задач."""

from src.models import Task
from src.protocols import TaskSource
from src.sources.file_source import FileSource
from src.sources.generator_source import GeneratorSource
from src.sources.api_stub import ApiStubSource
from src.main import create_source, process_tasks


def print_tasks(tasks: list[Task]) -> None:
    if not tasks:
        print("Список пуст.")
        return
    for task in tasks:
        print(f"  [{task.id}] {task.payload}")


def show_menu() -> None:
    print("\nВыберите действие:")
    print("1 Получить задачи из файла (tasks.txt)")
    print("2 Получить задачи через API")
    print("3 Получить задачи из генератора")
    print("4 Проверить контракт")
    print("5 Выйти")


def run() -> None:
    command = 0

    while command != 5:
        show_menu()
        try:
            command = int(input("Введите номер действия: "))
        except ValueError:
            print("Некорректный ввод, попробуйте снова.")
            continue

        if command == 1:
            print("Задачи из файла")
            file_src = create_source(FileSource, "src/text_files/tasks.txt")
            process_tasks(file_src)

        elif command == 2:
            print("Задачи из API")
            api = create_source(ApiStubSource)
            process_tasks(api)

        elif command == 3:
            print("Задачи из генератора")
            gen = create_source(GeneratorSource, 5)
            process_tasks(gen)

        elif command == 4: # Проверка subclass и isinstance
            print("Проверка контракта (issubclass)")
            for cls in [FileSource, GeneratorSource, ApiStubSource]:
                result = issubclass(cls, TaskSource)
                print(f"  {cls.__name__}: {result}")

            class BadSource:
                pass

            print(f"BadSource: {issubclass(BadSource, TaskSource)}")

            print("\nПопытка создать BadSource:")
            try:
                create_source(BadSource)
            except TypeError as e:
                print(f"Ошибка: {e}")

        elif command == 5:
            print("Выход.")

        else:
            print("Неизвестная команда.")


if __name__ == "__main__":
    run()
