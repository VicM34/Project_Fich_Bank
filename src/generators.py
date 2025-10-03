from typing import Any, Dict, Iterator, List


def filter_by_currency(transactions: List[Dict[str, Any]], currency: str) -> Iterator[Dict[str, Any]]:
    """
    Фильтрует транзакции по заданной валюте.
    """
    for transaction in transactions:
        # Получаем валюту из вложенной структуры operationAmount -> currency -> code
        operation_amount = transaction.get("operationAmount", {})
        currency_info = operation_amount.get("currency", {})
        currency_code = currency_info.get("code")

        if currency_code == currency:
            yield transaction


def transaction_descriptions(transactions: List[Dict[str, Any]]) -> Iterator[str]:
    """
    Генератор, который выдает описание каждой транзакции по очереди.
    """
    for transaction in transactions:
        description = transaction.get("description", "")
        yield description


def card_number_generator(start: int, end: int) -> Iterator[str]:
    """
    Генератор номеров банковских карт в заданном диапазоне.
    """
    # Проверка корректности входных данных
    if start < 1 or end > 9999999999999999:
        raise ValueError("Диапазон должен быть от 1 до 9999999999999999")
    if start > end:
        raise ValueError("Начальное значение не может быть больше конечного")

    for number in range(start, end + 1):
        # Преобразуем число в строку и дополняем нулями до 16 цифр
        card_str = str(number).zfill(16)

        # Форматируем в вид XXXX XXXX XXXX XXXX
        formatted_card: str = f"{card_str[:4]} {card_str[4:8]} {card_str[8:12]} {card_str[12:]}"

        yield formatted_card
