import asyncio
import logging

from src.models import Task
from src.protocols import TaskHandler
from src.task_queue import TaskQueue

logger = logging.getLogger(__name__)


class TextPayloadHandler:
    """
    Обрабатывает задачи, у которых payload - строка.
    Например, задачи из FileSource и GeneratorSource.
    """

    def can_handle(self, task: Task) -> bool:
        return isinstance(task.payload, str)

    async def handle(self, task: Task) -> None:
        logger.info(f"Взяли в работу текст (ID: {task.id}), содержимое: {task.payload}")
        await asyncio.sleep(2)
        logger.info(f"Закончили с текстовой задачей {task.id}")


class DictPayloadHandler:
    """
    Обрабатывает задачи, у которых payload - словарь.
    Например, задачи из ApiStubSource.
    """

    def can_handle(self, task: Task) -> bool:
        return isinstance(task.payload, dict)

    async def handle(self, task: Task) -> None:
        keys = list(task.payload.keys())
        logger.info(f"Прилетела задача со словарем (ID: {task.id}). Ключи: {keys}")
        await asyncio.sleep(1)
        logger.info(f"Словарь {task.id} обработан")


class FallbackHandler:
    """Обрабатывает всё остальное"""

    def can_handle(self, task: Task) -> bool:
        return True

    async def handle(self, task: Task) -> None:
        logger.info(f"Непонятный тип данных у задачи {task.id}. Тип: {type(task.payload).__name__}.")
        await asyncio.sleep(3)


class AsyncTaskExecutor:
    """
    Асинхронный исполнитель задач с управлением ресурсами.
    """

    def __init__(self, handlers: list[TaskHandler]) -> None:
        self._handlers = handlers
        self._processed = 0
        self._failed = 0

    async def __aenter__(self) -> "AsyncTaskExecutor":
        """Валидация обработчиков при входе вызывается при async with"""
        if not self._handlers:
            raise ValueError("Список обработчиков не может быть пустым!")
        for h in self._handlers:
            if not isinstance(h, TaskHandler):
                raise TypeError(
                    f"Обработчик {type(h).__name__} не реализует протокол TaskHandler"
                )
        logger.info(f"Начало асинхронной очереди. У нас {len(self._handlers)} обработчик(а/ов).")
        print(f"Начало асинхронной очереди. У нас {len(self._handlers)} обработчик(а/ов).")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Освобождение ресурсов и выход из async with"""
        logger.info(f"Асинхронная очередь завершила работу.")
        print(f"Асинхронная очередь завершила работу.")
        return False # не подавляем ошибку

    async def _process(self, task: Task) -> None:
        """
        Найти подходящий обработчик и выполнить задачу.
        Меняет статус через StatusValidator - невалидный статус будет отклонён.
        """
        handler = next((h for h in self._handlers if h.can_handle(task)), None)

        if handler is None:
            logger.warning(f"Вообще не нашли подходящего обработчика для задачи {task.id}")
            print(f"Вообще не нашли подходящего обработчика для задачи {task.id}")
            task.status = "cancelled"
            self._failed += 1
            return

        task.status = "in_progress"
        try:
            await handler.handle(task)
            task.status = "done"
            self._processed += 1
        except Exception as e:
            task.status = "cancelled"
            self._failed += 1
            logger.error(f"Задача {task.id} упала с ошибкой {type(e).__name__}: {e}")
            print(f"Задача {task.id} упала с ошибкой {type(e).__name__}: {e}")

    async def run(self, queue: TaskQueue) -> None:
        """
        Обрабатывает все задачи со статусом pending из TaskQueue.
        Задачи выполняются параллельно через asyncio.gather.
        """
        async_queue: asyncio.Queue[Task] = asyncio.Queue()

        for task in queue.iter_filtered(status="pending"):
            await async_queue.put(task)

        logger.info(f"Готово к обработке: {async_queue.qsize()} задач в очереди.")
        print(f"Готово к обработке: {async_queue.qsize()} задач в очереди.")

        coroutines = []
        while not async_queue.empty():
            task = await async_queue.get()
            coroutines.append(self._process(task))

        await asyncio.gather(*coroutines)