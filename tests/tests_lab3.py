import pytest

from src.models import Task
from src.task_queue import TaskQueue


class TestTaskQueueIteration:
    def test_iter_is_repeatable(self):
        q = TaskQueue(
            [
                Task(id="1", description="a", priority=3, status="pending"),
                Task(id="2", description="b", priority=8, status="done"),
            ]
        )

        first = [t.id for t in q]
        second = [t.id for t in q]
        assert first == ["1", "2"]
        assert second == ["1", "2"]

    def test_list_constructor_works(self):
        q = TaskQueue([Task(id="1", description="a")])
        assert [t.id for t in list(q)] == ["1"]


class TestTaskQueueBasics:
    def test_enqueue_dequeue(self):
        q = TaskQueue()
        q.enqueue(Task(id="1", description="a"))
        q.enqueue(Task(id="2", description="b"))

        assert q.peek().id == "1"
        assert q.dequeue().id == "1"
        assert q.dequeue().id == "2"
        assert len(q) == 0

    def test_dequeue_empty_raises(self):
        q = TaskQueue()
        with pytest.raises(IndexError):
            q.dequeue()

    def test_enqueue_type_check(self):
        q = TaskQueue()
        with pytest.raises(TypeError):
            q.enqueue("not a task")  # type: ignore[arg-type]


class TestTaskQueueFilters:
    def _queue(self) -> TaskQueue:
        return TaskQueue(
            [
                Task(id="1", description="a", priority=2, status="pending"),
                Task(id="2", description="b", priority=5, status="pending"),
                Task(id="3", description="c", priority=9, status="in_progress"),
                Task(id="4", description="d", priority=1, status="done"),
            ]
        )

    def test_filter_by_status(self):
        q = self._queue()
        ids = [t.id for t in q.iter_filtered(status="pending")]
        assert ids == ["1", "2"]

    def test_filter_by_priority_range(self):
        q = self._queue()
        ids = [t.id for t in q.iter_filtered(min_priority=5, max_priority=9)]
        assert ids == ["2", "3"]

    def test_filter_by_predicate(self):
        q = self._queue()
        ids = [t.id for t in q.iter_filtered(predicate=lambda t: t.id in {"1", "4"})]
        assert ids == ["1", "4"]


class TestTaskQueueProcessing:
    def test_process_consume_true_drains_queue(self):
        q = TaskQueue(
            [
                Task(id="1", description="a", priority=2, status="pending"),
                Task(id="2", description="b", priority=6, status="pending"),
                Task(id="3", description="c", priority=9, status="done"),
            ]
        )

        got = list(q.process(lambda t: t.id, consume=True, status="pending", min_priority=5))
        assert got == ["2"]
        assert len(q) == 0  # consume=True: очередь опустела

    def test_process_consume_false_keeps_queue(self):
        q = TaskQueue(
            [
                Task(id="1", description="a", priority=2, status="pending"),
                Task(id="2", description="b", priority=6, status="pending"),
            ]
        )

        got = list(q.process(lambda t: t.priority, consume=False))
        assert got == [2, 6]
        assert len(q) == 2
