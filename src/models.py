from typing import Any, NamedTuple


class Task(NamedTuple):
    """Задача с идентификатором и произвольными данными."""
    id: str
    payload: Any

a = Task(id=1,payload=34567890)
print(a)
print(hash(a))
b = Task(id=2,payload=34567890)
print(a==b)