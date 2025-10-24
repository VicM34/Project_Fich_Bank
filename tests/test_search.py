"""
Тесты для модуля search.py
"""

from collections import Counter
from unittest.mock import MagicMock, patch

import pytest

from src.search import process_bank_operations, process_bank_search


class TestBankSearch:
    """Тесты для функции поиска операций"""

    def test_process_bank_search_basic(self) -> None:
        """Тест базового поиска операций"""
        data = [
            {"description": "Перевод организации", "amount": 100},
            {"description": "Оплата услуг", "amount": 200},
            {"description": "Перевод между счетами", "amount": 300},
        ]

        result = process_bank_search(data, "перевод")

        assert len(result) == 2
        assert all("перевод" in item["description"].lower() for item in result)

    def test_process_bank_search_case_insensitive(self) -> None:
        """Тест case-insensitive поиска"""
        data = [
            {"description": "Перевод организации", "amount": 100},
            {"description": "ПЕРЕВОД МЕЖДУ СЧЕТАМИ", "amount": 200},
        ]

        result = process_bank_search(data, "перевод")

        assert len(result) == 2

    def test_process_bank_search_no_matches(self) -> None:
        """Тест поиска без совпадений"""
        data = [{"description": "Оплата услуг", "amount": 100}, {"description": "Пополнение счета", "amount": 200}]

        result = process_bank_search(data, "перевод")

        assert len(result) == 0

    def test_process_bank_search_empty_data(self) -> None:
        """Тест поиска с пустыми данными"""
        result = process_bank_search([], "перевод")
        assert result == []

    def test_process_bank_search_uses_regex(self) -> None:
        """Тест что используется библиотека re"""
        with patch("re.compile") as mock_compile:
            with patch("re.escape") as mock_escape:
                mock_escape.return_value = "test"
                mock_pattern = MagicMock()
                mock_compile.return_value = mock_pattern
                mock_pattern.search.return_value = True

                data = [{"description": "test transaction"}]
                process_bank_search(data, "test")

                mock_compile.assert_called_once()
                mock_pattern.search.assert_called_once()


class TestBankOperations:
    """Тесты для функции подсчета операций"""

    def test_process_bank_operations_basic(self) -> None:
        """Тест базового подсчета операций"""
        data = [
            {"description": "Перевод"},
            {"description": "Оплата"},
            {"description": "Перевод"},
            {"description": "Пополнение"},
        ]

        categories = ["Перевод", "Оплата"]
        result = process_bank_operations(data, categories)

        assert result == {"перевод": 2, "оплата": 1}

    def test_process_bank_operations_case_insensitive(self) -> None:
        """Тест case-insensitive подсчета"""
        data = [{"description": "ПЕРЕВОД"}, {"description": "перевод"}, {"description": "Перевод"}]

        categories = ["перевод"]
        result = process_bank_operations(data, categories)

        assert result == {"перевод": 3}

    def test_process_bank_operations_no_matches(self) -> None:
        """Тест подсчета без совпадений"""
        data = [{"description": "Перевод"}, {"description": "Оплата"}]

        categories = ["Пополнение"]
        result = process_bank_operations(data, categories)

        assert result == {"пополнение": 0}

    def test_process_bank_operations_uses_counter(self) -> None:
        """Тест что используется Counter"""
        with patch("src.search.Counter") as mock_counter:
            mock_counter.return_value = Counter({"перевод": 2})

            data = [{"description": "Перевод"}, {"description": "Перевод"}]
            categories = ["Перевод"]

            process_bank_operations(data, categories)

            mock_counter.assert_called_once()

    def test_process_bank_operations_empty_data(self) -> None:
        """Тест подсчета с пустыми данными"""
        result = process_bank_operations([], ["Перевод"])
        assert result == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
