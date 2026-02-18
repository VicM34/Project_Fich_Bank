import os
from datetime import datetime
from typing import Generator
from unittest.mock import patch

import pandas as pd
import pytest

from src.reports import spending_by_category, spending_by_weekday, spending_by_workday


class TestReports:
    """Тесты для модуля reports.py"""

    @pytest.fixture
    def sample_transactions(self) -> pd.DataFrame:
        """Фикстура с тестовыми транзакциями"""
        return pd.DataFrame(
            {
                "date": [
                    "2023-11-05",
                    "2023-11-20",
                    "2023-12-10",
                    "2024-01-05",
                    "2024-01-15",
                    "2024-02-01",
                ],
                "amount": [1000.0, 1500.0, 800.0, 1200.0, 900.0, 1100.0],
                "category": [
                    "Магазин",
                    "Ресторан",
                    "Магазин",
                    "Транспорт",
                    "Магазин",
                    "Магазин",
                ],
            }
        )

    def test_spending_by_category_found(self, sample_transactions: pd.DataFrame) -> None:
        """Тест анализа трат по существующей категории"""
        result = spending_by_category(sample_transactions, "Магазин", "2024-01-20")
        assert not result.empty
        assert len(result) == 3
        assert "year_month" in result.columns
        assert "amount" in result.columns
        assert result["amount"].sum() == 2700.0

    def test_spending_by_category_date_range(self, sample_transactions: pd.DataFrame) -> None:
        """Тест правильности диапазона дат"""
        result = spending_by_category(sample_transactions, "Магазин", "2024-01-31")
        assert len(result) == 3
        assert result["amount"].sum() == 2700.0

    def test_spending_by_category_excludes_future(self, sample_transactions: pd.DataFrame) -> None:
        """Тест, что будущие даты исключаются"""
        result = spending_by_category(sample_transactions, "Магазин", "2024-01-15")
        assert len(result) == 3
        assert result["amount"].sum() == 2700.0

    def test_spending_by_category_not_found(self, sample_transactions: pd.DataFrame) -> None:
        """Тест анализа трат по несуществующей категории"""
        result = spending_by_category(sample_transactions, "Несуществующая", "2024-01-20")
        assert result.empty

    def test_spending_by_category_default_date(self, sample_transactions: pd.DataFrame) -> None:
        """Тест анализа трат с датой по умолчанию"""
        with patch("src.reports.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 20)
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            result = spending_by_category(sample_transactions, "Магазин")
            assert not result.empty
            assert len(result) == 3

    def test_spending_by_category_empty_dataframe(self) -> None:
        """Тест анализа трат с пустым DataFrame"""
        empty_df = pd.DataFrame()
        result = spending_by_category(empty_df, "Магазин", "2024-01-20")
        assert result.empty

    def test_spending_by_category_no_date_column(self) -> None:
        """Тест анализа трат без колонки даты"""
        df_without_date = pd.DataFrame({"amount": [100, 200, 300], "category": ["Магазин", "Магазин", "Ресторан"]})
        result = spending_by_category(df_without_date, "Магазин", "2024-01-20")
        assert result.empty

    def test_spending_by_category_date_format(self, sample_transactions: pd.DataFrame) -> None:
        """Тест корректности формата дат в результате"""
        result = spending_by_category(sample_transactions, "Магазин", "2024-01-20")
        for period in result["year_month"]:
            assert isinstance(period, str)
            assert len(period) == 7
            assert period[4] == "-"

    @pytest.fixture(autouse=True)
    def cleanup_report_files(self) -> Generator[None, None, None]:  # ← ИСПРАВЛЕНО ТИП
        """Фикстура для очистки файлов отчетов после каждого теста"""
        files_before = set(os.listdir("."))
        yield
        files_after = set(os.listdir("."))
        new_files = files_after - files_before
        for file in new_files:
            if file.startswith("report_") and file.endswith(".json"):
                os.remove(file)

    def test_spending_by_weekday(self, sample_transactions: pd.DataFrame) -> None:
        """Тест анализа трат по дням недели"""
        result = spending_by_weekday(sample_transactions)

        assert not result.empty
        assert "weekday_name" in result.columns
        assert "total_amount" in result.columns
        assert len(result) <= 7  # максимум 7 дней недели

    def test_spending_by_workday(self, sample_transactions: pd.DataFrame) -> None:
        """Тест анализа трат в рабочие/выходные дни"""
        result = spending_by_workday(sample_transactions, "Магазин", "2024-01-20")

        assert not result.empty
        assert "day_type" in result.columns
        assert "total_amount" in result.columns
        assert any(result["day_type"].isin(["рабочий", "выходной"]))
