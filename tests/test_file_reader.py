"""
Тесты для модуля file_reader.py с использованием Mock и patch
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

from src.file_reader import _parse_transaction_row, read_csv_file, read_excel_file


class TestCSVReader:
    """Тесты для чтения CSV файлов с использованием Mock"""

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("csv.DictReader")
    def test_read_csv_file_success_with_mock(
        self, mock_dict_reader: MagicMock, mock_file: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Тест успешного чтения CSV файла с использованием Mock"""
        # Настраиваем моки
        mock_exists.return_value = True

        # Мокаем данные CSV
        mock_dict_reader.return_value = [
            {"id": "1", "state": "EXECUTED", "amount": "100.0", "currency": "USD", "description": "Test transaction"}
        ]

        result = read_csv_file("test.csv")

        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert result[0]["state"] == "EXECUTED"
        assert result[0]["operationAmount"]["amount"] == "100.0"
        assert result[0]["operationAmount"]["currency"]["code"] == "USD"

        # Проверяем вызовы
        mock_exists.assert_called_once()
        mock_file.assert_called_once_with("test.csv", "r", encoding="utf-8")

    @patch("pathlib.Path.exists")
    def test_read_csv_file_not_found_with_mock(self, mock_exists: MagicMock) -> None:
        """Тест чтения несуществующего CSV файла с Mock"""
        mock_exists.return_value = False

        result = read_csv_file("nonexistent.csv")

        assert result == []
        mock_exists.assert_called_once()

    @patch("pathlib.Path.exists")
    def test_read_csv_wrong_format_with_mock(self, mock_exists: MagicMock) -> None:
        """Тест чтения файла не CSV формата с Mock"""
        mock_exists.return_value = True

        result = read_csv_file("test.txt")

        assert result == []
        mock_exists.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="id;state;amount\n1;EXECUTED;100.0")
    def test_read_csv_with_semicolon_with_mock(self, mock_file: MagicMock, mock_exists: MagicMock) -> None:
        """Тест чтения CSV с разделителем точка с запятой с Mock"""
        mock_exists.return_value = True

        read_csv_file("test.csv")

        # Проверяем что файл был открыт
        mock_file.assert_called_once_with("test.csv", "r", encoding="utf-8")
        mock_exists.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("builtins.open")
    def test_read_csv_exception_handling_with_mock(self, mock_file: MagicMock, mock_exists: MagicMock) -> None:
        """Тест обработки исключений при чтении CSV с Mock"""
        mock_exists.return_value = True
        mock_file.side_effect = Exception("File error")

        result = read_csv_file("test.csv")

        assert result == []
        mock_exists.assert_called_once()
        mock_file.assert_called_once()


class TestExcelReader:
    """Тесты для чтения Excel файлов с использованием Mock и patch"""

    # В tests/test_file_reader.py обновим моки для Excel:

    @patch("src.file_reader.HAS_EXCEL_SUPPORT", True)
    @patch("pathlib.Path.exists")
    @patch("src.file_reader.openpyxl.load_workbook")
    def test_read_excel_file_success_with_mock(
        self, mock_load_workbook: MagicMock, mock_exists: MagicMock, *args: Any
    ) -> None:
        """Тест успешного чтения Excel файла с использованием Mock"""
        # Настраиваем моки
        mock_exists.return_value = True

        # Мокаем workbook и sheet
        mock_sheet = MagicMock()

        # Мокаем заголовки
        header_cell1 = MagicMock()
        header_cell1.value = "id"
        header_cell2 = MagicMock()
        header_cell2.value = "state"
        header_cell3 = MagicMock()
        header_cell3.value = "amount"

        # Мокаем первую строку для заголовков
        mock_first_row = [header_cell1, header_cell2, header_cell3]
        mock_sheet.__getitem__.return_value = mock_first_row

        # Мокаем данные
        mock_sheet.iter_rows.return_value = [("1", "EXECUTED", "100.0")]

        mock_workbook = MagicMock()
        mock_workbook.active = mock_sheet  # active sheet не None
        mock_load_workbook.return_value = mock_workbook

        result = read_excel_file("test.xlsx")

        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert result[0]["state"] == "EXECUTED"

        # Проверяем вызовы
        mock_exists.assert_called_once()
        mock_load_workbook.assert_called_once_with("test.xlsx", data_only=True)

    @patch("src.file_reader.HAS_EXCEL_SUPPORT", True)
    @patch("pathlib.Path.exists")
    @patch("src.file_reader.openpyxl.load_workbook")
    def test_read_excel_empty_data_with_mock(
        self, mock_load_workbook: MagicMock, mock_exists: MagicMock, *args: Any
    ) -> None:
        """Тест чтения Excel файла с пустыми данными с Mock"""
        mock_exists.return_value = True

        mock_sheet = MagicMock()
        mock_sheet.__getitem__.return_value = []  # Пустые заголовки
        mock_sheet.iter_rows.return_value = []  # Пустые данные

        mock_workbook = MagicMock()
        mock_workbook.active = mock_sheet
        mock_load_workbook.return_value = mock_workbook

        result = read_excel_file("test.xlsx")

        assert result == []
        mock_exists.assert_called_once()

    @patch("src.file_reader.HAS_EXCEL_SUPPORT", False)
    def test_read_excel_no_support_with_mock(self) -> None:
        """Тест чтения Excel без поддержки с Mock"""
        result = read_excel_file("test.xlsx")
        assert result == []

    @patch("src.file_reader.HAS_EXCEL_SUPPORT", True)
    @patch("pathlib.Path.exists")
    def test_read_excel_file_not_found_with_mock(self, mock_exists: MagicMock) -> None:
        """Тест чтения несуществующего Excel файла с Mock"""
        mock_exists.return_value = False

        result = read_excel_file("nonexistent.xlsx")

        assert result == []
        mock_exists.assert_called_once()

    @patch("src.file_reader.HAS_EXCEL_SUPPORT", True)
    @patch("pathlib.Path.exists")
    def test_read_excel_wrong_format_with_mock(self, mock_exists: MagicMock) -> None:
        """Тест чтения файла не Excel формата с Mock"""
        mock_exists.return_value = True

        result = read_excel_file("test.txt")

        assert result == []
        mock_exists.assert_called_once()


class TestTransactionParser:
    """Тесты для парсера транзакций"""

    def test_parse_transaction_row_basic(self) -> None:
        """Тест базового парсинга строки транзакции"""
        row_data = {"id": "1", "state": "EXECUTED", "amount": "100.0", "currency": "USD", "description": "Test"}

        result = _parse_transaction_row(row_data)

        assert result["id"] == "1"
        assert result["state"] == "EXECUTED"
        assert result["operationAmount"]["amount"] == "100.0"
        assert result["operationAmount"]["currency"]["code"] == "USD"

    def test_parse_transaction_row_field_mapping(self) -> None:
        """Тест маппинга различных названий полей"""
        row_data = {"ID": "2", "STATUS": "CANCELED", "Sum": "200.0", "Валюта": "RUB"}

        result = _parse_transaction_row(row_data)

        assert result["id"] == "2"
        assert result["state"] == "CANCELED"
        assert result["operationAmount"]["amount"] == "200.0"
        assert result["operationAmount"]["currency"]["code"] == "RUB"

    def test_parse_transaction_row_missing_fields(self) -> None:
        """Тест парсинга с отсутствующими полями"""
        row_data = {"id": "3", "state": "PENDING"}

        result = _parse_transaction_row(row_data)

        assert result["id"] == "3"
        assert result["state"] == "PENDING"
        assert "operationAmount" not in result


# Интеграционные тесты с реальными файлами
class TestIntegration:
    """Интеграционные тесты с реальными файлами"""

    def test_read_csv_real_file(self) -> None:
        """Тест чтения реального CSV файла"""
        csv_path = "data/transactions.csv"
        if Path(csv_path).exists():
            result = read_csv_file(csv_path)
            assert isinstance(result, list)
            # Проверяем что все элементы - словари
            if result:
                assert all(isinstance(item, dict) for item in result)

    def test_read_excel_real_file(self) -> None:
        """Тест чтения реального Excel файла"""
        excel_path = "data/transactions_excel.xlsx"
        if Path(excel_path).exists():
            result = read_excel_file(excel_path)
            assert isinstance(result, list)
            # Проверяем что все элементы - словари
            if result:
                assert all(isinstance(item, dict) for item in result)
