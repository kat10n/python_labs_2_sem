from collections import deque
from src.models import Task


class TaskQueue:
    """Простая очередь задач + итерация и генераторы."""

    def __init__(self, tasks=None):
        self._dq = deque()
        if tasks:
            self.extend(tasks)

    def __len__(self):
        return len(self._dq)

    def __iter__(self):
        # каждый раз новый итератор -> можно обходить очередь повторно
        return iter(self._dq)

    def __repr__(self):
        return f"TaskQueue(size={len(self._dq)})"

    def enqueue(self, task):
        if not isinstance(task, Task):
            raise TypeError("task должен быть Task")
        self._dq.append(task)

    def extend(self, tasks):
        for t in tasks:
            self.enqueue(t)

    def dequeue(self):
        if not self._dq:
            raise IndexError("Очередь пуста")
        return self._dq.popleft()

    def peek(self):
        if not self._dq:
            raise IndexError("Очередь пуста")
        return self._dq[0]

    def clear(self):
        self._dq.clear()

    def iter_filtered(self, status=None, min_priority=None, max_priority=None, predicate=None):
        """Ленивый фильтр, ничего не копирует."""
        for task in self._dq:
            if status is not None and task.status != status:
                continue
            if min_priority is not None and task.priority < min_priority:
                continue
            if max_priority is not None and task.priority > max_priority:
                continue
            if predicate is not None and not predicate(task):
                continue
            yield task

    def process(self, handler, consume=True, status=None, min_priority=None, max_priority=None, predicate=None):
        """Потоковая обработка, consume=True -> достаём из очереди."""
        if consume:
            while self._dq:
                task = self._dq.popleft()
                if status is not None and task.status != status:
                    continue
                if min_priority is not None and task.priority < min_priority:
                    continue
                if max_priority is not None and task.priority > max_priority:
                    continue
                if predicate is not None and not predicate(task):
                    continue
                yield handler(task)
        else:
            for task in self.iter_filtered(status, min_priority, max_priority, predicate):
                yield handler(task)
