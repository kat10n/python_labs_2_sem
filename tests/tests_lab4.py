import pytest
from unittest.mock import MagicMock, AsyncMock

from src.executor import TextPayloadHandler, DictPayloadHandler, FallbackHandler, AsyncTaskExecutor
from src.protocols import TaskHandler


@pytest.fixture
def mock_task():
    return MagicMock(id="123", status="pending", is_ready=True)


@pytest.mark.asyncio
async def test_handlers(mock_task):
    text_h, dict_h, fall_h = TextPayloadHandler(), DictPayloadHandler(), FallbackHandler()

    mock_task.payload = "Текст"
    assert text_h.can_handle(mock_task) is True
    assert dict_h.can_handle(mock_task) is False

    mock_task.payload = {"key": "value"}
    assert dict_h.can_handle(mock_task) is True
    assert text_h.can_handle(mock_task) is False

    assert fall_h.can_handle(mock_task) is True


@pytest.mark.asyncio
async def test_executor_validation():
    with pytest.raises(ValueError):
        async with AsyncTaskExecutor(handlers=[]): pass

    with pytest.raises(TypeError):
        async with AsyncTaskExecutor(handlers=[MagicMock()]): pass


@pytest.mark.asyncio
async def test_executor_process(mock_task):
    handler = MagicMock(spec=TaskHandler)
    executor = AsyncTaskExecutor(handlers=[handler])

    handler.can_handle.return_value = True
    handler.handle = AsyncMock()
    await executor._process(mock_task)
    assert mock_task.status == "done"
    assert executor._processed == 1

    handler.can_handle.return_value = False
    await executor._process(mock_task)
    assert mock_task.status == "cancelled"
    assert executor._failed == 1

    handler.can_handle.return_value = True
    handler.handle = AsyncMock(side_effect=Exception("Упс"))
    await executor._process(mock_task)
    assert executor._failed == 2


@pytest.mark.asyncio
async def test_executor_run():
    t_ready = MagicMock(status="pending", is_ready=True)
    t_skip = MagicMock(status="pending", is_ready=False)

    queue = MagicMock()
    queue.iter_filtered.return_value = [t_ready, t_skip]

    handler = MagicMock(spec=TaskHandler)
    handler.can_handle.return_value = True
    handler.handle = AsyncMock()

    executor = AsyncTaskExecutor(handlers=[handler])
    await executor.run(queue)

    assert handler.handle.call_count == 1
    assert executor._processed == 1