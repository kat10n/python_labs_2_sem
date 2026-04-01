from datetime import datetime
from typing import Any

from src.exeptions import (
    InvalidPriorityError,
    InvalidStatusError,
)

class StringValidator:
    """
    DATA-дескриптор: хранит строку в __set_name__-имени на экземпляре.
    Проверяет, что значение — непустая строка.
    """

    def __set_name__(self, owner: type, name: str) -> None:
        # приватное имя для хранения значения на экземпляре
        self._attr = f"_sv_{name}"
        self._name = name

    def __get__(self, obj: Any, objtype: type | None = None) -> str:
        if obj is None:
            return self
        return getattr(obj, self._attr, "")

    def __set__(self, obj: Any, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{self._name} должен быть строкой, получен {type(value).__name__}")
        if not value.strip():
            raise ValueError(f"{self._name} не может быть пустым")
        setattr(obj, self._attr, value)


class PriorityValidator:
    """
    DATA-дескриптор: проверяет, что приоритет — целое число от 1 до 10.
    """

    MIN = 1
    MAX = 10

    def __set_name__(self, owner: type, name: str) -> None:
        self._attr = f"_pv_{name}"

    def __get__(self, obj: Any, objtype: type | None = None) -> int:
        if obj is None:
            return self          # type: ignore[return-value]
        return getattr(obj, self._attr, self.MIN)

    def __set__(self, obj: Any, value: Any) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise InvalidPriorityError(
                f"Приоритет должен быть int, получен {type(value).__name__}"
            )
        if not (self.MIN <= value <= self.MAX):
            raise InvalidPriorityError(
                f"Приоритет должен быть от {self.MIN} до {self.MAX}, получен {value}"
            )
        setattr(obj, self._attr, value)


class StatusValidator:
    """
    DATA-дескриптор: принимает только допустимые статусы задачи.
    """

    ALLOWED: frozenset[str] = frozenset({"pending", "in_progress", "done", "cancelled"})

    def __set_name__(self, owner: type, name: str) -> None:
        self._attr = f"_stv_{name}"

    def __get__(self, obj: Any, objtype: type | None = None) -> str:
        if obj is None:
            return self
        return getattr(obj, self._attr, "pending")

    def __set__(self, obj: Any, value: Any) -> None:
        if not isinstance(value, str):
            raise InvalidStatusError(f"Статус должен быть строкой, получен {type(value).__name__}")
        if value not in self.ALLOWED:
            raise InvalidStatusError(
                f"Недопустимый статус '{value}'. Допустимые: {sorted(self.ALLOWED)}"
            )
        setattr(obj, self._attr, value)


class ReadOnlyTimestamp:
    def __set_name__(self, owner: type, name: str) -> None:
        self._attr = f"_rots_{name}"

    def __get__(self, obj: Any, objtype: type | None = None) -> datetime | None:
        if obj is None:
            return self
        return obj.__dict__.get(self._attr)


class Task:
    """
    Модель задачи с корректной инкапсуляцией и валидацией состояния.
    """
    id: str = StringValidator()
    description: str = StringValidator()
    priority: int = PriorityValidator()
    status: str = StatusValidator()

    def __init__(
        self,
        id: str,
        description: str,
        payload: Any = None,
        priority: int = 5,
        status: str = "pending",
    ) -> None:
        self.id = id
        self.description = description
        self.priority = priority
        self.status = status
        self.payload = payload
        self.__dict__["_created_at"] = datetime.now()

    @property
    def created_at(self) -> datetime:
        """
        Время создания задачи. Read-only — изменить нельзя.
        """
        return self.__dict__["_created_at"]

    @created_at.setter
    def created_at(self, value: Any) -> None:
        raise AttributeError("Время создания задачи изменить нельзя")

    @property
    def is_ready(self) -> bool:
        """
        Вычисляемое свойство.
        """
        return self.status == "pending" and self.priority >= 3

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id!r}, description={self.description!r}, "
            f"priority={self.priority}, status={self.status!r}, "
            f"is_ready={self.is_ready})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        return self.id == other.id