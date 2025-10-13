import json
import os
import tempfile

from src.utils import load_transactions


class TestLoadTransactions:
    """Тесты для функции load_transactions"""

    def test_load_valid_json(self) -> None:
        """Тест загрузки корректного JSON файла"""
        # Создаем временный файл с валидными данными
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            json_data = [{"id": 1, "amount": 100, "currency": "USD"}, {"id": 2, "amount": 200, "currency": "EUR"}]
            temp_file.write(json.dumps(json_data))
            temp_filename = temp_file.name

        try:
            result = load_transactions(temp_filename)
            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[1]["currency"] == "EUR"
        finally:
            os.unlink(temp_filename)

    def test_file_not_found(self) -> None:
        """Тест когда файл не существует"""
        result = load_transactions("nonexistent_file.json")
        assert result == []

    def test_empty_file(self) -> None:
        """Тест пустого файла"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            result = load_transactions(temp_filename)
            assert result == []
        finally:
            os.unlink(temp_filename)

    def test_invalid_json(self) -> None:
        """Тест файла с невалидным JSON"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            temp_file.write("invalid json content")
            temp_filename = temp_file.name

        try:
            result = load_transactions(temp_filename)
            assert result == []
        finally:
            os.unlink(temp_filename)

    def test_json_not_list(self) -> None:
        """Тест когда JSON не является списком"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            json_data = {"id": 1, "amount": 100}  # словарь, не список
            temp_file.write(json.dumps(json_data))
            temp_filename = temp_file.name

        try:
            result = load_transactions(temp_filename)
            assert result == []
        finally:
            os.unlink(temp_filename)


# Интеграционный тест с реальным файлом
def test_with_real_data() -> None:
    """Тест с реальным файлом operations.json"""
    if os.path.exists("../data/operations.json"):
        result = load_transactions("../data/operations.json")
        # Проверяем что возвращается список (может быть пустым)
        assert isinstance(result, list)
