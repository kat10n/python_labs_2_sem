from pathlib import Path

from src.protocols import TaskSource
from src.sources.file_source import FileSource
from src.sources.generator_source import GeneratorSource
from src.sources.api_stub import ApiStubSource
from src.main import create_source, process_tasks
from logging import getLogger
logger = getLogger(__name__)


def show_menu() -> None:
    print("\nВыберите действие:")
    print("1 Получить задачи из файла (tasks.txt)")
    print("2 Получить задачи через API")
    print("3 Получить задачи из генератора")
    print("4 Проверить контракт")
    print("5 Выйти")


def run() -> None:
    command = 0
    show_menu()
    while command != 5:
        try:
            command = int(input("Введите номер действия: "))
        except ValueError:
            print("Некорректный ввод, попробуйте снова.")
            continue
        try:
            if command == 1:
                print("Задачи из файла")
                file_src = create_source(FileSource, "text_files/tasks.txt")
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

                print(f"  BadSource: {issubclass(BadSource, TaskSource)}")

            elif command == 5:
                print("Выход.")

            else:
                print("Неизвестная команда.")
        except:
            print('Не удалось выполнить действие.')


if __name__ == "__main__":
    run()
