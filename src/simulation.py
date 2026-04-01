from src.protocols import TaskSource
from src.sources.file_source import FileSource
from src.sources.generator_source import GeneratorSource
from src.sources.api_stub import ApiStubSource
from src.main import create_source, process_tasks
from src.models import Task
from src.exeptions import InvalidPriorityError, InvalidStatusError
from logging import getLogger
logger = getLogger(__name__)


def show_menu():
    print("\nВыберите действие:")
    print("1 Получить задачи из файла (tasks.txt)")
    print("2 Получить задачи через API")
    print("3 Получить задачи из генератора")
    print("4 Проверить контракт")
    print("5 Создать задачу")
    print("6 Показать валидацию дескрипторов")
    print("7 Показать работу property")
    print("8 Data vs Non-data дескрипторы")
    print("9 Выйти")


def demo_create_task():
    tid = input("ID: ").strip()
    desc = input("Описание: ").strip()
    try:
        prio = int(input("  Приоритет (1-10): "))
    except ValueError:
        print("Приоритет должен быть числом")
        return
    status = input("Статус (pending/in_progress/done/cancelled): ").strip()

    t = Task(id=tid, description=desc, priority=prio, status=status)
    print(f"{t}")
    print(f"created_at = {t.created_at}")
    print(f"is_ready = {t.is_ready}")


def demo_validation():
    print("\nStringValidator (id):")
    try:
        Task(id="", description="тест")
    except ValueError as e:
        print(f"  пустой id: {e}")
    try:
        Task(id=123, description="тест")
    except TypeError as e:
        print(f"  id=123: {e}")

    print("\nPriorityValidator:")
    try:
        Task(id="t1", description="тест", priority=0)
    except InvalidPriorityError as e:
        print(f"priority=0: {e}")
    try:
        Task(id="t1", description="тест", priority=11)
    except InvalidPriorityError as e:
        print(f"priority=11: {e}")
    try:
        Task(id="t1", description="тест", priority="high")
    except InvalidPriorityError as e:
        print(f"priority='high': {e}")

    print("\nStatusValidator:")
    try:
        Task(id="t1", description="тест", status="unknown")
    except InvalidStatusError as e:
        print(f"status='unknown': {e}")
    try:
        Task(id="t1", description="тест", status=42)
    except InvalidStatusError as e:
        print(f"status=42: {e}")


def demo_properties():
    t = Task(id="demo", description="Пример", priority=7, status="pending")
    print(f"{t}")
    print(f"created_at = {t.created_at}")
    print(f"is_ready = {t.is_ready}")

    t.status = "done"
    print(f"после status='done': is_ready = {t.is_ready}")

    try:
        t.created_at = "2026-04-01"
    except AttributeError as e:
        print(f"попытка поменять created_at: {e}")

    try:
        t.is_ready = True
    except AttributeError as e:
        print(f"попытка поменять is_ready: {e}")


def demo_data_vs_nondata():
    # data descriptor — priority (есть __get__ и __set__)
    t = Task(id="t1", description="тест", priority=5)
    print(f"priority = {t.priority}")

    t.__dict__["priority"] = 999
    print(f"__dict__['priority'] = {t.__dict__['priority']}")
    print(f"t.priority = {t.priority}")
    print("data descriptor перехватывает доступ, __dict__ игнорируется")

    # non-data descriptor — __repr__ (только __get__, без __set__)
    print(f"\nrepr через дескриптор: {repr(t)}")
    t.__dict__["__repr__"] = lambda: "подмена"
    print(f"repr после записи в __dict__: {repr(t)}")
    print("non-data тоже не сработал, потому что __repr__ ищется на классе")


def run():
    command = 0
    show_menu()
    while command != 9:
        try:
            command = int(input("\nВведите номер: "))
        except ValueError:
            print("Некорректный ввод")
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

            elif command == 4:
                print("Проверка контракта (issubclass)")
                for cls in [FileSource, GeneratorSource, ApiStubSource]:
                    print(f"  {cls.__name__}: {issubclass(cls, TaskSource)}")

                class BadSource:
                    pass
                print(f"  BadSource: {issubclass(BadSource, TaskSource)}")

            elif command == 5:
                demo_create_task()

            elif command == 6:
                demo_validation()

            elif command == 7:
                demo_properties()

            elif command == 8:
                demo_data_vs_nondata()

            elif command == 9:
                print("Выход")

            else:
                print("Нет такой команды")
                logger.info(f"Неизвестная команда: {command}")
        except Exception as e:
            logger.exception("Ошибка при выполнении команды %s", command)
            print(f"Не удалось выполнить действие: {e}")


if __name__ == "__main__":
    run()
