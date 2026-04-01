import pytest
from datetime import datetime
from src.models import Task
from src.exeptions import (
    InvalidPriorityError,
    InvalidStatusError,
    InvalidTaskIdError,
    InvalidDescriptionError,
)


class TestTaskCreation:
    def test_create_minimal(self):
        t = Task(id="t1", description="Описание")
        assert t.id == "t1"
        assert t.description == "Описание"
        assert t.priority == 5
        assert t.status == "pending"

    def test_create_full(self):
        t = Task(id="t2", description="Полная", payload={"x": 1}, priority=8, status="in_progress")
        assert t.priority == 8
        assert t.status == "in_progress"
        assert t.payload == {"x": 1}

    def test_created_at_is_datetime(self):
        t = Task(id="t3", description="Тест")
        assert isinstance(t.created_at, datetime)


class TestTaskIdValidation:
    def test_empty_id_raises(self):
        with pytest.raises((ValueError, InvalidTaskIdError)):
            Task(id="", description="ok")

    def test_whitespace_id_raises(self):
        with pytest.raises((ValueError, InvalidTaskIdError)):
            Task(id="   ", description="ok")

    def test_non_string_id_raises(self):
        with pytest.raises(TypeError):
            Task(id=123, description="ok")


class TestTaskDescriptionValidation:
    def test_empty_description_raises(self):
        with pytest.raises((ValueError, InvalidDescriptionError)):
            Task(id="t1", description="")

    def test_non_string_description_raises(self):
        with pytest.raises(TypeError):
            Task(id="t1", description=None)


class TestTaskPriorityValidation:
    def test_valid_boundaries(self):
        Task(id="a", description="x", priority=1)
        Task(id="b", description="x", priority=10)

    def test_priority_too_low(self):
        with pytest.raises(InvalidPriorityError):
            Task(id="t", description="x", priority=0)

    def test_priority_too_high(self):
        with pytest.raises(InvalidPriorityError):
            Task(id="t", description="x", priority=11)

    def test_priority_negative(self):
        with pytest.raises(InvalidPriorityError):
            Task(id="t", description="x", priority=-5)

    def test_priority_float_raises(self):
        with pytest.raises(InvalidPriorityError):
            Task(id="t", description="x", priority=5.0)  # type: ignore

    def test_priority_string_raises(self):
        with pytest.raises(InvalidPriorityError):
            Task(id="t", description="x", priority="high")  # type: ignore

    def test_priority_bool_raises(self):
        with pytest.raises(InvalidPriorityError):
            Task(id="t", description="x", priority=True)  # type: ignore


class TestTaskStatusValidation:
    def test_all_valid_statuses(self):
        for status in ("pending", "in_progress", "done", "cancelled"):
            t = Task(id="t", description="x", status=status)
            assert t.status == status

    def test_invalid_status_raises(self):
        with pytest.raises(InvalidStatusError):
            Task(id="t", description="x", status="unknown")

    def test_status_case_sensitive(self):
        with pytest.raises(InvalidStatusError):
            Task(id="t", description="x", status="Pending")

    def test_status_change_valid(self):
        t = Task(id="t", description="x")
        t.status = "done"
        assert t.status == "done"

    def test_status_change_invalid(self):
        t = Task(id="t", description="x")
        with pytest.raises(InvalidStatusError):
            t.status = "broken"


class TestCreatedAt:
    def test_created_at_readonly(self):
        t = Task(id="t", description="x")
        with pytest.raises(AttributeError):
            t.created_at = datetime.now()  # type: ignore

    def test_created_at_stable(self):
        t = Task(id="t", description="x")
        first = t.created_at
        second = t.created_at
        assert first == second


class TestIsReady:
    def test_ready_when_pending_and_high_priority(self):
        t = Task(id="t", description="x", priority=5, status="pending")
        assert t.is_ready is True

    def test_not_ready_when_done(self):
        t = Task(id="t", description="x", status="done")
        assert t.is_ready is False

    def test_not_ready_when_priority_low(self):
        t = Task(id="t", description="x", priority=1, status="pending")
        assert t.is_ready is False

    def test_is_ready_updates_with_status(self):
        t = Task(id="t", description="x", priority=7)
        assert t.is_ready is True
        t.status = "done"
        assert t.is_ready is False

    def test_is_ready_is_not_settable(self):
        t = Task(id="t", description="x")
        with pytest.raises(AttributeError):
            t.is_ready = True  # type: ignore


class TestDescriptorBehavior:
    def test_data_descriptor_blocks_instance_dict(self):
        t = Task(id="t", description="x", priority=5)
        assert t.priority == 5

    def test_priority_updates_correctly(self):
        t = Task(id="t", description="x", priority=3)
        t.priority = 9
        assert t.priority == 9

    def test_two_tasks_dont_share_state(self):
        t1 = Task(id="1", description="a", priority=2)
        t2 = Task(id="2", description="b", priority=8)
        assert t1.priority == 2
        assert t2.priority == 8