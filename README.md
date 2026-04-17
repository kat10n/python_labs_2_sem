# Платформа обработки задач — лабораторные работы 1–3

**Галанова Екатерина, М8О-102БВ-25**

Три лабораторные работы по курсу Python. Предметная область — платформа обработки задач: приём задач из разных источников, их валидация и хранение, итерация и потоковая обработка.

## Структура проекта

```
src/
  models.py              — модель задачи Task, дескрипторы валидации
  exeptions.py           — специализированные исключения
  protocols.py           — протокол TaskSource
  main.py                — фабрика источников и обработка задач
  simulation.py          — интерактивная демонстрация через меню (лабы 1–3)
  task_queue.py          — очередь задач TaskQueue (лаба 3)
  sources/
    file_source.py       — загрузка задач из текстового файла
    generator_source.py  — программная генерация задач
    api_stub.py          — имитация внешнего API
  text_files/
    tasks.txt            — пример файла с задачами
tests/
  tests.py               — тесты лабораторной 1
  tests_lab2.py          — тесты лабораторной 2
  tests_lab3.py          — тесты лабораторной 3
```

---

## Лабораторная работа 1 — Источники задач и контракты

Подсистема приёма задач. Разные источники не связаны наследованием, но реализуют единый поведенческий контракт через `typing.Protocol`.

### Контракт

```python
@runtime_checkable
class TaskSource(Protocol):
    def get_tasks(self) -> list[Task]: ...
```

Проверка контракта выполняется двумя способами:
- `issubclass(cls, TaskSource)` — в фабрике `create_source`, до создания экземпляра
- `isinstance(source, TaskSource)` — в `process_tasks`, при обработке

### Источники

| Класс | Откуда берёт задачи |
|---|---|
| `FileSource` | Текстовый файл, формат `id;payload` |
| `GeneratorSource` | Генерирует N задач программно |
| `ApiStubSource` | Заглушка внешнего API |

Добавление нового источника не требует изменения существующего кода — достаточно реализовать `get_tasks()`.

---

## Лабораторная работа 2 — Модель задачи: дескрипторы и @property

Класс `Task` с инкапсуляцией и валидацией через дескрипторы.

### Атрибуты

| Атрибут | Тип | Описание |
|---|---|---|
| `id` | `str` | Уникальный идентификатор (непустая строка) |
| `description` | `str` | Описание задачи (непустая строка) |
| `priority` | `int` | Приоритет от 1 до 10 |
| `status` | `str` | `pending` / `in_progress` / `done` / `cancelled` |
| `payload` | `Any` | Произвольные данные задачи |
| `created_at` | `datetime` | Время создания (read-only, через `@property`) |
| `is_ready` | `bool` | Вычисляемое: `status == "pending"` и `priority >= 3` |

### Дескрипторы

Все дескрипторы — **data** (реализуют `__get__` и `__set__`), что означает приоритет над `__dict__` экземпляра.

- `StringValidator` — проверяет, что значение является непустой строкой. Используется для `id` и `description`.
- `PriorityValidator` — проверяет диапазон 1–10, отсекает `bool` и нецелые типы.
- `StatusValidator` — допускает только значения из фиксированного набора.
- `ReadOnlyTimestamp` — non-data дескриптор (только `__get__`): не перехватывает запись, в отличие от data-дескрипторов.

### Исключения

Все наследуются от `TaskValidationError`:

```
TaskValidationError
├── InvalidPriorityError
├── InvalidStatusError
├── InvalidTaskIdError
└── InvalidDescriptionError
```

---

## Лабораторная работа 3 — Очередь задач: итераторы и генераторы

Класс `TaskQueue` на основе `collections.deque`. Поддерживает повторную итерацию, ленивую фильтрацию и потоковую обработку.

### API

```python
q = TaskQueue(tasks)   # инициализация списком
q.enqueue(task)        # добавить задачу
q.dequeue()            # извлечь первую (FIFO)
q.peek()               # посмотреть без извлечения
len(q)                 # количество задач
for t in q: ...        # повторяемая итерация
```

### Ленивые операции

`iter_filtered` — генератор, не создаёт промежуточных копий:

```python
for task in q.iter_filtered(status="pending", min_priority=5):
    ...
```

Доступные параметры фильтра: `status`, `min_priority`, `max_priority`, `predicate`.

`process` — потоковая обработка с применением функции-обработчика:

```python
# consume=False: очередь остаётся нетронутой
results = list(q.process(lambda t: t.id, consume=False))

# consume=True: задачи изымаются из очереди по мере обработки
results = list(q.process(handler, consume=True, status="pending"))
```

`TaskQueue` совместима со стандартными конструкциями Python: `list(q)`, `sum(t.priority for t in q)`, `for t in q`.

---

## Запуск

Интерактивная демонстрация (все три лабораторные):

```bash
python -m src.simulation
```

Тесты:

```bash
# лабораторная 1
python -m pytest tests/tests.py -v

# лабораторная 2
python -m pytest tests/tests_lab2.py -v

# лабораторная 3
python -m pytest tests/tests_lab3.py -v

# все тесты
python -m pytest tests/ -v
```