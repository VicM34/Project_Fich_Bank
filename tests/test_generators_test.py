from typing import Any, Dict, List

import pytest

from src.generators import card_number_generator, filter_by_currency, transaction_descriptions


class TestFilterByCurrency:
    """Тесты для функции filter_by_currency"""

    @pytest.fixture
    def sample_transactions(self) -> List[Dict[str, Any]]:
        """Фикстура с тестовыми транзакциями"""
        return [
            {
                "id": 1,
                "state": "EXECUTED",
                "date": "2019-07-03T18:35:29.512364",
                "operationAmount": {"amount": "100.0", "currency": {"name": "US Dollar", "code": "USD"}},
                "description": "Payment for services",
                "from": "Visa Platinum 1234567812345678",
                "to": "Счет 12345678901234567890",
            },
            {
                "id": 2,
                "state": "EXECUTED",
                "date": "2018-06-30T02:08:58.425572",
                "operationAmount": {"amount": "5000.0", "currency": {"name": "Russian Ruble", "code": "RUB"}},
                "description": "Salary",
                "to": "Счет 98765432109876543210",
            },
            {
                "id": 3,
                "state": "CANCELED",
                "date": "2018-09-12T21:27:25.241689",
                "operationAmount": {"amount": "50.0", "currency": {"name": "US Dollar", "code": "USD"}},
                "description": "Online purchase",
                "from": "MasterCard 5678567856785678",
                "to": "Amazon Inc.",
            },
        ]

    def test_filter_usd_transactions(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест фильтрации USD транзакций"""
        usd_transactions = list(filter_by_currency(sample_transactions, "USD"))

        assert len(usd_transactions) == 2
        assert all(txn["operationAmount"]["currency"]["code"] == "USD" for txn in usd_transactions)
        assert usd_transactions[0]["id"] == 1
        assert usd_transactions[1]["id"] == 3

    def test_filter_rub_transactions(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест фильтрации RUB транзакций"""
        rub_transactions = list(filter_by_currency(sample_transactions, "RUB"))

        assert len(rub_transactions) == 1
        assert rub_transactions[0]["id"] == 2
        assert rub_transactions[0]["operationAmount"]["currency"]["code"] == "RUB"

    def test_filter_eur_transactions_empty(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест фильтрации EUR транзакций (отсутствуют)"""
        eur_transactions = list(filter_by_currency(sample_transactions, "EUR"))

        assert len(eur_transactions) == 0

    def test_filter_empty_list(self) -> None:
        """Тест работы с пустым списком транзакций"""
        empty_transactions = list(filter_by_currency([], "USD"))

        assert len(empty_transactions) == 0

    def test_generator_behavior(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест поведения генератора (поэлементная выдача)"""
        usd_generator = filter_by_currency(sample_transactions, "USD")

        # Получаем транзакции по одной
        first_txn = next(usd_generator)
        assert first_txn["id"] == 1

        second_txn = next(usd_generator)
        assert second_txn["id"] == 3

        # Должен вызвать StopIteration
        with pytest.raises(StopIteration):
            next(usd_generator)


class TestTransactionDescriptions:
    """Тесты для функции transaction_descriptions"""

    @pytest.fixture
    def sample_transactions(self) -> List[Dict[str, Any]]:
        """Фикстура с тестовыми транзакциями"""
        return [
            {"id": 1, "description": "Перевод организации", "state": "EXECUTED"},
            {"id": 2, "description": "Перевод со счета на счет", "state": "EXECUTED"},
            {"id": 3, "description": "Оплата услуг", "state": "CANCELED"},
            {"id": 4, "state": "EXECUTED"},  # Транзакция без описания
        ]

    def test_get_all_descriptions(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест получения всех описаний"""
        descriptions = list(transaction_descriptions(sample_transactions))

        expected_descriptions = [
            "Перевод организации",
            "Перевод со счета на счет",
            "Оплата услуг",
            "",  # Пустая строка для транзакции без описания
        ]

        assert descriptions == expected_descriptions

    def test_empty_transactions(self) -> None:
        """Тест работы с пустым списком транзакций"""
        descriptions = list(transaction_descriptions([]))

        assert len(descriptions) == 0

    def test_generator_behavior(self, sample_transactions: List[Dict[str, Any]]) -> None:
        """Тест поведения генератора"""
        desc_generator = transaction_descriptions(sample_transactions)

        assert next(desc_generator) == "Перевод организации"
        assert next(desc_generator) == "Перевод со счета на счет"
        assert next(desc_generator) == "Оплата услуг"
        assert next(desc_generator) == ""

        with pytest.raises(StopIteration):
            next(desc_generator)


class TestCardNumberGenerator:
    """Тесты для генератора card_number_generator"""

    def test_small_range(self) -> None:
        """Тест генерации небольшого диапазона"""
        cards = list(card_number_generator(1, 5))

        expected_cards = [
            "0000 0000 0000 0001",
            "0000 0000 0000 0002",
            "0000 0000 0000 0003",
            "0000 0000 0000 0004",
            "0000 0000 0000 0005",
        ]

        assert cards == expected_cards

    def test_single_card(self) -> None:
        """Тест генерации одной карты"""
        cards = list(card_number_generator(123, 123))

        assert cards == ["0000 0000 0000 0123"]

    def test_large_numbers(self) -> None:
        """Тест генерации больших номеров"""
        cards = list(card_number_generator(9999999999999995, 9999999999999999))

        expected_cards = [
            "9999 9999 9999 9995",
            "9999 9999 9999 9996",
            "9999 9999 9999 9997",
            "9999 9999 9999 9998",
            "9999 9999 9999 9999",
        ]

        assert cards == expected_cards

    def test_format_correctness(self) -> None:
        """Тест корректности форматирования"""
        cards = list(card_number_generator(1234567890123456, 1234567890123456))

        assert len(cards) == 1
        card = cards[0]

        # Проверяем формат
        assert len(card) == 19  # 16 цифр + 3 пробела
        assert card.count(" ") == 3
        assert card.replace(" ", "").isdigit()
        assert card == "1234 5678 9012 3456"

    def test_invalid_range(self) -> None:
        """Тест обработки невалидного диапазона"""
        with pytest.raises(ValueError, match="Диапазон должен быть от 1 до 9999999999999999"):
            list(card_number_generator(0, 5))

        with pytest.raises(ValueError, match="Диапазон должен быть от 1 до 9999999999999999"):
            list(card_number_generator(1, 10000000000000000))

    def test_invalid_start_end(self) -> None:
        """Тест когда start > end"""
        with pytest.raises(ValueError, match="Начальное значение не может быть больше конечного"):
            list(card_number_generator(10, 5))

    def test_generator_behavior(self) -> None:
        """Тест поведения генератора (итерация)"""
        generator = card_number_generator(1, 3)

        assert next(generator) == "0000 0000 0000 0001"
        assert next(generator) == "0000 0000 0000 0002"
        assert next(generator) == "0000 0000 0000 0003"

        with pytest.raises(StopIteration):
            next(generator)


# Дополнительные интеграционные тесты
class TestIntegration:
    """Интеграционные тесты"""

    def test_combined_filters(self) -> None:
        """Тест комбинирования фильтров"""
        transactions = [
            {
                "id": 1,
                "state": "EXECUTED",
                "operationAmount": {"amount": "100.0", "currency": {"code": "USD"}},
                "description": "Test 1",
            },
            {
                "id": 2,
                "state": "EXECUTED",
                "operationAmount": {"amount": "200.0", "currency": {"code": "RUB"}},
                "description": "Test 2",
            },
        ]

        # Фильтруем по валюте и получаем описания
        usd_transactions = filter_by_currency(transactions, "USD")
        descriptions = transaction_descriptions(list(usd_transactions))

        assert list(descriptions) == ["Test 1"]
