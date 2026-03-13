"""Тесты подсистемы приёма задач."""

import pytest
from unittest.mock import patch

from src.models import Task
from src.protocols import TaskSource
from src.sources.file_source import FileSource
from src.sources.generator_source import GeneratorSource
from src.sources.api_stub import ApiStubSource
from src.main import create_source, process_tasks


class TestTask:
    def test_create(self):
        task = Task(id="1", payload="data")
        assert task.id == "1"
        assert task.payload == "data"

    def test_equality(self):
        assert Task(id="1", payload="x") == Task(id="1", payload="x")

    def test_inequality_id(self):
        assert Task(id="1", payload="x") != Task(id="2", payload="x")

    def test_inequality_payload(self):
        assert Task(id="1", payload="a") != Task(id="1", payload="b")

    def test_unpack(self):
        tid, payload = Task(id="a", payload="b")
        assert tid == "a"
        assert payload == "b"

    def test_dict_payload(self):
        task = Task(id="1", payload={"key": "value"})
        assert task.payload == {"key": "value"}


class TestTaskSourceProtocol:
    def test_file_source_is_subclass(self):
        assert issubclass(FileSource, TaskSource)

    def test_generator_source_is_subclass(self):
        assert issubclass(GeneratorSource, TaskSource)

    def test_api_stub_is_subclass(self):
        assert issubclass(ApiStubSource, TaskSource)

    def test_bad_class_not_subclass(self):
        class Bad:
            pass
        assert not issubclass(Bad, TaskSource)

    def test_isinstance_positive(self):
        assert isinstance(ApiStubSource(), TaskSource)
        assert isinstance(GeneratorSource(1), TaskSource)

    def test_isinstance_negative(self):
        class Bad:
            pass
        assert not isinstance(Bad(), TaskSource)


class TestFileSource:
    def test_get_tasks(self, tmp_path):
        f = tmp_path / "t.txt"
        f.write_text("id1;payload1\nid2;payload2\n", encoding="utf-8")
        tasks = FileSource(str(f)).get_tasks()
        assert tasks == [Task("id1", "payload1"), Task("id2", "payload2")]

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")
        assert FileSource(str(f)).get_tasks() == []

    def test_blank_lines_skipped(self, tmp_path):
        f = tmp_path / "t.txt"
        f.write_text("1;a\n\n\n2;b\n", encoding="utf-8")
        assert len(FileSource(str(f)).get_tasks()) == 2

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            FileSource("no_such_file.txt").get_tasks()

    def test_semicolon_in_payload(self, tmp_path):
        f = tmp_path / "t.txt"
        f.write_text("1;data;extra\n", encoding="utf-8")
        tasks = FileSource(str(f)).get_tasks()
        assert tasks[0].payload == "data;extra"

    def test_not_string_filename(self):
        with pytest.raises(TypeError, match="строкой"):
            FileSource(123)

    def test_empty_filename(self):
        with pytest.raises(ValueError, match="пустым"):
            FileSource("")

    def test_wrong_extension(self):
        with pytest.raises(ValueError, match=".txt"):
            FileSource("tasks.csv")


class TestGeneratorSource:
    def test_count(self):
        assert len(GeneratorSource(5).get_tasks()) == 5

    def test_zero(self):
        assert GeneratorSource(0).get_tasks() == []

    def test_content(self):
        tasks = GeneratorSource(3).get_tasks()
        assert tasks[0] == Task("0", "data_0")
        assert tasks[2] == Task("2", "data_2")

    def test_returns_task_instances(self):
        for t in GeneratorSource(3).get_tasks():
            assert isinstance(t, Task)

    def test_negative_count_raises(self):
        with pytest.raises(ValueError, match="отрицательным"):
            GeneratorSource(-1)

    def test_non_integer_count_raises(self):
        with pytest.raises(TypeError, match="целым числом"):
            GeneratorSource(1.5)


class TestApiStubSource:
    def test_get_tasks_count(self):
        assert len(ApiStubSource().get_tasks()) == 2

    def test_task_content(self):
        tasks = ApiStubSource().get_tasks()
        assert tasks[0] == Task("api_1", {"value": 100})
        assert tasks[1] == Task("api_2", {"value": 200})

    def test_returns_task_instances(self):
        for t in ApiStubSource().get_tasks():
            assert isinstance(t, Task)


class TestCreateSource:
    def test_valid_generator(self):
        src = create_source(GeneratorSource, 2)
        assert isinstance(src, GeneratorSource)

    def test_valid_api(self):
        src = create_source(ApiStubSource)
        assert isinstance(src, ApiStubSource)

    def test_valid_file(self, tmp_path):
        f = tmp_path / "t.txt"
        f.write_text("1;x\n", encoding="utf-8")
        src = create_source(FileSource, str(f))
        assert isinstance(src, FileSource)

    def test_invalid_source_raises(self):
        class Bad:
            pass
        with pytest.raises(TypeError, match="не реализует TaskSource"):
            create_source(Bad)


class TestProcessTasks:
    def test_prints_tasks(self, capsys):
        process_tasks(GeneratorSource(2))
        out = capsys.readouterr().out
        assert "[0] data_0" in out
        assert "[1] data_1" in out

    def test_api_tasks_printed(self, capsys):
        process_tasks(ApiStubSource())
        out = capsys.readouterr().out
        assert "[api_1]" in out
        assert "[api_2]" in out

    def test_invalid_source_raises(self):
        class Bad:
            pass
        with pytest.raises(TypeError, match="не реализует TaskSource"):
            process_tasks(Bad())


class TestSimulation:
    @patch("builtins.input", side_effect=["5"])
    def test_exit(self, mock_input, capsys):
        from src.simulation import run
        run()
        assert "Выход" in capsys.readouterr().out

    @patch("builtins.input", side_effect=["1", "5"])
    def test_file_menu(self, mock_input, capsys):
        from src.simulation import run
        run()
        assert "Задачи из файла" in capsys.readouterr().out

    @patch("builtins.input", side_effect=["2", "5"])
    def test_api_menu(self, mock_input, capsys):
        from src.simulation import run
        run()
        assert "Задачи из API" in capsys.readouterr().out

    @patch("builtins.input", side_effect=["3", "5"])
    def test_generator_menu(self, mock_input, capsys):
        from src.simulation import run
        run()
        assert "Задачи из генератора" in capsys.readouterr().out

    @patch("builtins.input", side_effect=["4", "5"])
    def test_contract_check(self, mock_input, capsys):
        from src.simulation import run
        run()
        out = capsys.readouterr().out
        assert "Проверка контракта" in out
        assert "BadSource: False" in out

    @patch("builtins.input", side_effect=["abc", "5"])
    def test_invalid_input(self, mock_input, capsys):
        from src.simulation import run
        run()
        assert "Некорректный ввод" in capsys.readouterr().out

    @patch("builtins.input", side_effect=["9", "5"])
    def test_unknown_command(self, mock_input, capsys):
        from src.simulation import run
        run()
        assert "Неизвестная команда" in capsys.readouterr().out