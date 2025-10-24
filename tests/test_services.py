from typing import Any
from unittest.mock import patch

import pandas as pd
import pytest

from src.services import (
    investment_piggy_bank,
    profitable_cashback_categories,
    search_by_phone_numbers,
    search_individual_transfers,
    simple_search,
)


class TestServices:
    """Тесты для модуля services.py"""

    @pytest.fixture
    def sample_transactions(self) -> pd.DataFrame:
        """Фикстура с тестовыми транзакциями"""
        return pd.DataFrame(
            {
                "date": ["2024-01-15", "2024-01-16", "2024-01-17"],
                "amount": [1000.0, 500.0, 200.0],
                "category": ["Магазин", "Ресторан", "Транспорт"],
                "description": ["Покупка в супермаркете", "Ужин в кафе", "Такси до магазина"],
                "card_number": ["1234567812345678", "8765432187654321", "1234567812345678"],
            }
        )

    @patch("src.services.load_transactions_excel")
    def test_simple_search_found(self, mock_load_transactions: Any, sample_transactions: pd.DataFrame) -> None:
        """Тест успешного поиска транзакций"""
        mock_load_transactions.return_value = sample_transactions

        result = simple_search("магазин")

        assert len(result) == 2
        assert any("магазин" in item["description"].lower() for item in result)
        assert any("Магазин" in item["category"] for item in result)

    @patch("src.services.load_transactions_excel")
    def test_simple_search_not_found(self, mock_load_transactions: Any, sample_transactions: pd.DataFrame) -> None:
        """Тест поиска когда ничего не найдено"""
        mock_load_transactions.return_value = sample_transactions

        result = simple_search("несуществующийзапрос")

        assert result == []

    @patch("src.services.load_transactions_excel")
    def test_simple_search_case_insensitive(
        self, mock_load_transactions: Any, sample_transactions: pd.DataFrame
    ) -> None:
        """Тест поиска без учета регистра"""
        mock_load_transactions.return_value = sample_transactions

        result_lower = simple_search("магазин")
        result_upper = simple_search("МАГАЗИН")

        assert len(result_lower) == len(result_upper)

    @patch("src.services.load_transactions_excel")
    def test_simple_search_empty_dataframe(self, mock_load_transactions: Any) -> None:
        """Тест поиска при пустом DataFrame"""
        mock_load_transactions.return_value = pd.DataFrame()

        result = simple_search("запрос")

        assert result == []

    def test_simple_search_empty_query(self) -> None:
        """Тест поиска с пустым запросом"""
        result = simple_search("")
        assert isinstance(result, list)

    @patch("src.services.load_transactions_excel")
    def test_simple_search_description_only(self, mock_load_transactions: Any) -> None:
        """Тест поиска только в описании"""
        df = pd.DataFrame(
            {
                "date": ["2024-01-15"],
                "amount": [1000.0],
                "category": ["Другое"],
                "description": ["Покупка в магазине"],
                "card_number": ["1234567812345678"],
            }
        )
        mock_load_transactions.return_value = df

        result = simple_search("магазин")

        assert len(result) == 1
        assert "магазин" in result[0]["description"].lower()

    @patch("src.services.load_transactions_excel")
    def test_simple_search_category_only(self, mock_load_transactions: Any) -> None:
        """Тест поиска только в категории"""
        df = pd.DataFrame(
            {
                "date": ["2024-01-15"],
                "amount": [1000.0],
                "category": ["Магазин"],
                "description": ["Покупка продуктов"],
                "card_number": ["1234567812345678"],
            }
        )
        mock_load_transactions.return_value = df

        result = simple_search("магазин")

        assert len(result) == 1
        assert "Магазин" in result[0]["category"]

    def test_profitable_cashback_categories(self) -> None:
        """Тест сервиса выгодных категорий кешбэка"""
        transactions = [
            {"date": "2024-01-15", "amount": 1000.0, "category": "Магазин"},
            {"date": "2024-01-16", "amount": 500.0, "category": "Ресторан"},
            {"date": "2024-01-17", "amount": 300.0, "category": "Магазин"},
        ]

        result = profitable_cashback_categories(2024, 1, transactions)

        assert "cashback_categories" in result
        assert "Магазин" in result["cashback_categories"]
        assert result["cashback_categories"]["Магазин"] == 65.0  # (1000+300)*0.05

    def test_investment_piggy_bank(self) -> None:
        """Тест сервиса инвесткопилки"""
        transactions = [
            {"amount": "47.50", "description": "Кофе"},
            {"amount": "123.30", "description": "Обед"},
            {"amount": "89.90", "description": "Книга"},
        ]

        result = investment_piggy_bank("2024-01", transactions, 10.0)

        assert "total_savings" in result
        assert "rounded_transactions" in result
        assert result["total_savings"] > 0

    def test_search_by_phone_numbers(self) -> None:
        """Тест поиска по телефонным номерам"""
        transactions = [
            {"description": "Перевод +7 (999) 123-45-67"},
            {"description": "Оплата услуг 89991234567"},
            {"description": "Покупка в магазине"},
        ]

        result = search_by_phone_numbers(transactions)

        assert result["found_transactions"] == 2
        assert any("+7" in str(phone) for t in result["transactions"] for phone in t["phones_found"])

    def test_search_individual_transfers(self) -> None:
        """Тест поиска переводов физлицам"""
        transactions = [
            {"description": "Перевод физлицу Сбербанк"},
            {"description": "Оплата Тинькофф"},
            {"description": "Покупка в магазине"},
        ]

        result = search_individual_transfers(transactions)

        assert result["found_transactions"] == 2
        assert any("физлицу" in t["description"] for t in result["transactions"])
