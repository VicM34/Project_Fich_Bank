import os
import tempfile
from io import StringIO
from unittest.mock import patch

import pytest

from src.decorators import log


class TestLogDecorator:
    """Тесты для декоратора log"""

    def test_log_to_console_success(self) -> None:
        """Тест логирования успешной операции в консоль"""

        @log()
        def sample_add_function(x: int, y: int) -> int:
            return x + y

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = sample_add_function(5, 3)

        output = mock_stdout.getvalue()
        assert result == 8
        assert "sample_add_function - начало выполнения" in output
        assert "sample_add_function - успешно завершена" in output
        assert "результат: 8" in output

    def test_log_to_file_success(self) -> None:
        """Тест логирования успешной операции в файл"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_filename = temp_file.name

        try:

            @log(temp_filename)
            def greeting_function(name: str) -> str:
                return f"Hello, {name}"

            result = greeting_function("Alice")

            with open(temp_filename, "r", encoding="utf-8") as file:
                log_content = file.read()

            assert result == "Hello, Alice"
            assert "greeting_function - начало выполнения" in log_content  # ← ИСПРАВЛЕНО
            assert "greeting_function - успешно завершена" in log_content
            assert "результат: 'Hello, Alice'" in log_content

        finally:
            os.unlink(temp_filename)

    def test_log_error_to_console(self) -> None:
        """Тест логирования ошибки в консоль"""

        @log()
        def error_function() -> None:
            raise ValueError("Test error")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            with pytest.raises(ValueError):
                error_function()

        output = mock_stdout.getvalue()
        assert "error_function - начало выполнения" in output
        assert "error_function - ошибка: ValueError" in output
        assert "Test error" in output

    def test_log_with_arguments(self) -> None:
        """Тест логирования с аргументами"""

        @log()
        def complex_function(a: int, b: int, c: int = 10) -> int:
            return a + b + c

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = complex_function(1, 2, c=3)

        output = mock_stdout.getvalue()
        assert result == 6
        assert "complex_function - начало выполнения" in output
        assert "args: 1, 2" in output
        assert "c=3" in output


def test_function_name_preserved() -> None:
    """Тест что имя функции сохраняется после декорирования"""

    @log()
    def original_function() -> str:
        """Тестовая функция"""
        return "test"

    assert original_function.__name__ == "original_function"
    assert original_function.__doc__ == "Тестовая функция"
