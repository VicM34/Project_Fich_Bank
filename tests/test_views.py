from typing import Any
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import get_greeting_by_time
from src.views import events_page_data, get_cards_statistics, get_top_transactions, main_page_data


class TestViews:
    """Тесты для модуля views"""

    @pytest.fixture
    def sample_transactions(self) -> pd.DataFrame:
        """Фикстура с тестовыми транзакциями"""
        return pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-15", "2024-01-20", "2024-02-01"]),
                "amount": [1000.0, 500.0, -200.0],
                "category": ["Магазин", "Ресторан", "Возврат"],
                "description": ["Покупка в магазине", "Ужин в ресторане", "Возврат средств"],
                "card_number": ["1234567812345678", "1234567812345678", "8765432187654321"],
            }
        )

    def test_get_greeting_by_time(self) -> None:
        """Тест определения приветствия по времени"""
        assert get_greeting_by_time("2024-01-01 08:00:00") == "Доброе утро"
        assert get_greeting_by_time("2024-01-01 14:00:00") == "Добрый день"
        assert get_greeting_by_time("2024-01-01 20:00:00") == "Добрый вечер"
        assert get_greeting_by_time("2024-01-01 02:00:00") == "Доброй ночи"

    def test_get_cards_statistics(self, sample_transactions: pd.DataFrame) -> None:
        """Тест статистики по картам"""
        result = get_cards_statistics(sample_transactions)

        assert len(result) == 2
        assert result[0]["last_digits"] == "5678"
        assert result[0]["total_spent"] == 1500.0

    def test_get_top_transactions(self, sample_transactions: pd.DataFrame) -> None:
        """Тест получения топ транзакций"""
        result = get_top_transactions(sample_transactions, 2)

        assert len(result) == 2
        assert result[0]["amount"] == 1000.0

    @patch("src.views.load_transactions_excel")
    @patch("src.views.load_user_settings")
    @patch("src.views.get_currency_rates")
    @patch("src.views.get_stock_prices")
    def test_main_page_data(
        self,
        mock_stocks: Any,
        mock_currency: Any,
        mock_settings: Any,
        mock_transactions: Any,
        sample_transactions: pd.DataFrame,
    ) -> None:
        """Тест главной функции страницы"""
        mock_transactions.return_value = sample_transactions
        mock_settings.return_value = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}
        mock_currency.return_value = [{"currency": "USD", "rate": 75.0}]
        mock_stocks.return_value = [{"stock": "AAPL", "price": 150.0}]

        result = main_page_data("2024-01-20 12:00:00")

        assert "greeting" in result
        assert "cards" in result
        assert "top_transactions" in result
        assert "currency_rates" in result
        assert "stock_prices" in result
        assert result["greeting"] == "Добрый день"

    @patch("src.views.load_transactions_excel")
    def test_events_page_data(self, mock_transactions: Any, sample_transactions: pd.DataFrame) -> None:
        """Тест функции для страницы 'События'"""
        mock_transactions.return_value = sample_transactions

        result = events_page_data(sample_transactions)

        assert "events_by_category" in result
        assert "recent_events" in result
        assert "total_events" in result
        assert result["total_events"] == 3
