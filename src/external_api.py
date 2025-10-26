import logging
import os
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List, Optional, Union

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

logger = logging.getLogger(__name__)


# === СУЩЕСТВУЮЩИЕ ФУНКЦИИ ===
def get_exchange_rates(api_key: str, base_currency: str = "RUB") -> Optional[Dict[str, Any]]:
    """
    Получает текущие курсы валют от API
    """
    url = f"https://api.apilayer.com/exchangerates_data/latest?base={base_currency}"

    headers = {"apikey": api_key}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("success", False):
            rates = data.get("rates", {})
            return {str(currency): float(rate) for currency, rate in rates.items()}
        else:
            print(f"API error: {data.get('error', {}).get('info', 'Unknown error')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except ValueError as e:
        print(f"JSON parsing error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def convert_to_rubles(amount: float, currency: str, api_key: str) -> Optional[float]:
    """
    Конвертирует сумму в рубли по текущему курсу.
    """
    if currency == "RUB":
        return float(amount)

    rates = get_exchange_rates(api_key, "RUB")

    if not rates or currency not in rates:
        print(f"Exchange rate for {currency} not found")
        return None

    exchange_rate = rates[currency]

    # Конвертируем: amount (в исходной валюте) * курс к рублю
    result = amount * exchange_rate

    # Округляем до 2 знаков после запятой
    result = float(Decimal(str(result)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    return result


def get_transaction_amount_in_rubles(transaction: Dict[str, Any]) -> Optional[float]:
    """
    Возвращает сумму транзакции в рублях.
    """
    try:
        # Получаем API ключ из переменных окружения
        api_key = os.getenv("API_KEY")
        if not api_key:
            print("API key not found in environment variables")
            return None

        # Извлекаем данные о сумме и валюте
        operation_amount = transaction.get("operationAmount", {})
        amount_str = operation_amount.get("amount", "0")
        currency_info = operation_amount.get("currency", {})
        currency_code = currency_info.get("code", "RUB")

        # Преобразуем сумму в float
        try:
            amount = float(amount_str)
        except (ValueError, TypeError):
            print(f"Invalid amount format: {amount_str}")
            return None

        # Конвертируем в рубли если нужно
        if currency_code in ["USD", "EUR"]:
            return convert_to_rubles(amount, currency_code, api_key)
        else:
            # Для RUB и других валют возвращаем как есть
            return amount

    except Exception as e:
        print(f"Error processing transaction: {e}")
        return None


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Union[str, float]]]:
    """
    Получает курсы валют через API для главной страницы
    """
    results: List[Dict[str, Union[str, float]]] = []
    api_key = os.getenv("API_KEY")

    if not api_key:
        logger.error("API_KEY не найден в переменных окружения")
        return results

    try:
        rates = get_exchange_rates(api_key, "RUB")

        if rates:
            for currency in currencies:
                if currency in rates:
                    rate_value = round(rates[currency], 2)
                    results.append({"currency": currency, "rate": rate_value})
    except Exception as e:
        logger.error(f"Ошибка получения курсов валют: {e}")

    return results


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Union[str, float]]]:
    """
    Получает цены акций через API
    """
    results: List[Dict[str, Union[str, float]]] = []

    mock_prices: Dict[str, float] = {
        "AAPL": 150.12,
        "AMZN": 3173.18,
        "GOOGL": 2742.39,
        "MSFT": 296.71,
        "TSLA": 1007.08,
    }

    for stock in stocks:
        price = mock_prices.get(stock)
        if price is not None:
            results.append({"stock": stock, "price": price})  # str  # float

    logger.info(f"Получены цены для {len(results)} акций")
    return results


if __name__ == "__main__":
    # Тестируем новые функции
    print("Тестирование currency rates:")
    currencies = ["USD", "EUR"]
    currency_rates = get_currency_rates(currencies)
    print(f"Курсы валют: {currency_rates}")

    print("\nТестирование stock prices:")
    stocks = ["AAPL", "AMZN", "GOOGL"]
    stock_prices = get_stock_prices(stocks)
    print(f"Цены акций: {stock_prices}")
