import json
import os
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest

from src.utils import (
    convert_json_transactions_to_dataframe,
    filter_transactions_by_date_range,
    get_greeting_by_time,
    load_transactions,
    load_transactions_excel,
    load_user_settings,
)


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


class TestNewUtilsFunctions:
    """Тесты для новых функций в utils.py"""

    @patch("pandas.read_excel")
    def test_load_transactions_excel_success(self, mock_read_excel: MagicMock) -> None:
        """Тест успешной загрузки Excel файла"""
        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_excel.return_value = mock_df

        result = load_transactions_excel("test.xlsx")

        assert len(result) == 2
        mock_read_excel.assert_called_once_with("test.xlsx")

    @patch("pandas.read_excel")
    def test_load_transactions_excel_file_not_found(self, mock_read_excel: MagicMock) -> None:
        """Тест загрузки несуществующего Excel файла"""
        mock_read_excel.side_effect = FileNotFoundError("File not found")

        result = load_transactions_excel("nonexistent.xlsx")

        assert result.empty
        assert len(result) == 0

    @patch(
        "builtins.open", mock_open(read_data='{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "TSLA"]}')
    )
    def test_load_user_settings_success(self) -> None:
        """Тест успешной загрузки пользовательских настроек"""
        settings = load_user_settings()

        assert settings["user_currencies"] == ["USD", "EUR"]
        assert settings["user_stocks"] == ["AAPL", "TSLA"]

    def test_load_user_settings_file_not_found(self) -> None:
        """Тест загрузки настроек при отсутствии файла"""
        settings = load_user_settings("nonexistent_settings.json")

        assert "user_currencies" in settings
        assert "user_stocks" in settings
        assert "USD" in settings["user_currencies"]
        assert "EUR" in settings["user_currencies"]

    @pytest.mark.parametrize(
        "time_str, expected_greeting",
        [
            ("2024-01-01 06:00:00", "Доброе утро"),
            ("2024-01-01 12:00:00", "Добрый день"),
            ("2024-01-01 19:00:00", "Добрый вечер"),
            ("2024-01-01 02:00:00", "Доброй ночи"),
            ("2024-01-01 23:30:00", "Доброй ночи"),
        ],
    )
    def test_get_greeting_by_time_variations(self, time_str: str, expected_greeting: str) -> None:
        """Тест определения приветствия по разному времени"""
        assert get_greeting_by_time(time_str) == expected_greeting

    def test_get_greeting_by_time_invalid_format(self) -> None:
        """Тест обработки неверного формата времени"""
        result = get_greeting_by_time("invalid-time-format")
        assert result == "Добрый день"  # fallback значение

    def test_filter_transactions_by_date_range_success(self) -> None:
        """Тест успешной фильтрации транзакций по дате"""
        df = pd.DataFrame({"date": ["2024-01-01", "2024-01-15", "2024-02-01"], "amount": [100, 200, 300]})

        result = filter_transactions_by_date_range(df, "2024-01-01", "2024-01-31")

        assert len(result) == 2
        assert all(result["date"].dt.strftime("%Y-%m-%d").isin(["2024-01-01", "2024-01-15"]))

    def test_filter_transactions_by_date_range_no_date_column(self) -> None:
        """Тест фильтрации когда нет колонки date"""
        df = pd.DataFrame({"amount": [100, 200, 300]})  # нет колонки date

        result = filter_transactions_by_date_range(df, "2024-01-01", "2024-01-31")

        # Должен вернуть исходный DataFrame без изменений
        assert len(result) == 3

    def test_convert_json_transactions_to_dataframe(self) -> None:
        """Тест конвертации JSON транзакций в DataFrame"""
        transactions = [
            {"date": "2024-01-01", "amount": 100, "category": "food"},
            {"date": "2024-01-02", "amount": 200, "category": "transport"},
        ]

        result = convert_json_transactions_to_dataframe(transactions)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "date" in result.columns
        assert "amount" in result.columns
        assert "category" in result.columns

    def test_convert_json_transactions_to_dataframe_empty(self) -> None:
        """Тест конвертации пустого списка транзакций"""
        result = convert_json_transactions_to_dataframe([])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


# Интеграционный тест с реальным файлом
def test_with_real_data() -> None:
    """Тест с реальным файлом operations.json"""
    if os.path.exists("../data/operations.json"):
        result = load_transactions("../data/operations.json")
        # Проверяем что возвращается список (может быть пустым)
        assert isinstance(result, list)
