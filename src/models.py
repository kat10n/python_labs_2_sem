from typing import Any, NamedTuple


class Task(NamedTuple):
    """Задача с идентификатором и произвольными данными."""
    id: str
    payload: Any