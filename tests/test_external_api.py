import os
from unittest.mock import MagicMock, patch

from src.external_api import convert_to_rubles, get_exchange_rates, get_transaction_amount_in_rubles


class TestExternalAPI:
    """Тесты для модуля external_api"""

    @patch("src.external_api.requests.get")
    def test_get_exchange_rates_success(self, mock_get: MagicMock) -> None:
        """Тест успешного получения курсов валют"""
        # Мокаем ответ API
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "rates": {"USD": 0.013, "EUR": 0.011, "KZT": 5.5}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_exchange_rates("test_api_key")

        assert result is not None
        assert "USD" in result
        assert result["USD"] == 0.013
        mock_get.assert_called_once()

    @patch("src.external_api.requests.get")
    def test_get_exchange_rates_api_error(self, mock_get: MagicMock) -> None:
        """Тест ошибки API"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": False, "error": {"info": "Invalid API key"}}
        mock_get.return_value = mock_response

        result = get_exchange_rates("invalid_key")

        assert result is None

    @patch("src.external_api.requests.get")
    def test_get_exchange_rates_request_error(self, mock_get: MagicMock) -> None:
        """Тест ошибки сети"""
        mock_get.side_effect = Exception("Network error")

        result = get_exchange_rates("test_key")

        assert result is None

    @patch("src.external_api.get_exchange_rates")
    def test_convert_to_rubles_usd(self, mock_get_rates: MagicMock) -> None:
        """Тест конвертации USD в рубли"""
        mock_get_rates.return_value = {"USD": 0.013, "EUR": 0.011}

        result = convert_to_rubles(100.0, "USD", "test_key")

        assert result == 1.3  # 100 USD * 0.013 = 1.3 RUB
        mock_get_rates.assert_called_once_with("test_key", "RUB")

    @patch("src.external_api.get_exchange_rates")
    def test_convert_to_rubles_eur(self, mock_get_rates: MagicMock) -> None:
        """Тест конвертации EUR в рубли"""
        mock_get_rates.return_value = {"USD": 0.013, "EUR": 0.011}

        result = convert_to_rubles(50.0, "EUR", "test_key")

        assert result == 0.55  # 50 EUR * 0.011 = 0.55 RUB

    def test_convert_to_rubles_rub(self) -> None:
        """Тест конвертации RUB (возвращает ту же сумму)"""
        result = convert_to_rubles(100.0, "RUB", "test_key")

        assert result == 100.0

    @patch("src.external_api.get_exchange_rates")
    def test_convert_to_rubles_currency_not_found(self, mock_get_rates: MagicMock) -> None:
        """Тест когда валюта не найдена в курсах"""
        mock_get_rates.return_value = {"USD": 0.013}

        result = convert_to_rubles(100.0, "EUR", "test_key")

        assert result is None

    @patch.dict(os.environ, {"API_KEY": "test_key"})
    @patch("src.external_api.convert_to_rubles")
    def test_get_transaction_amount_in_rubles_usd(self, mock_convert: MagicMock) -> None:
        """Тест получения суммы USD транзакции в рублях"""
        mock_convert.return_value = 7500.0

        transaction = {"operationAmount": {"amount": "100.00", "currency": {"code": "USD"}}}

        result = get_transaction_amount_in_rubles(transaction)

        assert result == 7500.0
        mock_convert.assert_called_once_with(100.0, "USD", "test_key")

    @patch.dict(os.environ, {"API_KEY": "test_key"})
    def test_get_transaction_amount_in_rubles_rub(self) -> None:
        """Тест получения суммы RUB транзакции"""
        transaction = {"operationAmount": {"amount": "5000.00", "currency": {"code": "RUB"}}}

        result = get_transaction_amount_in_rubles(transaction)

        assert result == 5000.0

    @patch.dict(os.environ, {"API_KEY": "test_key"})
    def test_get_transaction_amount_in_rubles_invalid_amount(self) -> None:
        """Тест с невалидной суммой"""
        transaction = {"operationAmount": {"amount": "invalid", "currency": {"code": "RUB"}}}

        result = get_transaction_amount_in_rubles(transaction)

        assert result is None

    def test_get_transaction_amount_in_rubles_no_api_key(self) -> None:
        """Тест когда API ключ не установлен"""
        # Убедимся что переменной нет
        if "API_KEY" in os.environ:
            del os.environ["API_KEY"]

        transaction = {"operationAmount": {"amount": "100.00", "currency": {"code": "USD"}}}

        result = get_transaction_amount_in_rubles(transaction)

        assert result is None

    @patch.dict(os.environ, {"API_KEY": "test_key"})
    def test_get_transaction_amount_in_rubles_missing_operation_amount(self) -> None:
        """Тест когда нет operationAmount"""
        transaction = {"id": 1, "state": "EXECUTED"}

        result = get_transaction_amount_in_rubles(transaction)

        assert result == 0.0


def test_rounding() -> None:
    """Тест округления результатов"""
    from src.external_api import convert_to_rubles

    with patch("src.external_api.get_exchange_rates") as mock_rates:
        mock_rates.return_value = {"USD": 0.013456}

        result = convert_to_rubles(100.0, "USD", "test_key")

        # Проверяем что результат округлен до 2 знаков
        assert result == 1.35  # 100 * 0.013456 = 1.3456 → округляем до 1.35


class TestEdgeCases:
    """Тесты граничных случаев"""

    @patch("src.external_api.get_exchange_rates")
    def test_convert_to_rubles_zero_amount(self, mock_get_rates: MagicMock) -> None:
        """Тест конвертации нулевой суммы"""
        mock_get_rates.return_value = {"USD": 0.013}

        result = convert_to_rubles(0.0, "USD", "test_key")

        assert result == 0.0

    @patch("src.external_api.get_exchange_rates")
    def test_convert_to_rubles_negative_amount(self, mock_get_rates: MagicMock) -> None:
        """Тест конвертации отрицательной суммы"""
        mock_get_rates.return_value = {"USD": 0.013}

        result = convert_to_rubles(-100.0, "USD", "test_key")

        assert result == -1.3

    @patch.dict(os.environ, {"API_KEY": "test_key"})
    def test_get_transaction_amount_missing_currency_code(self) -> None:
        """Тест когда нет кода валюты"""
        transaction = {"operationAmount": {"amount": "100.00", "currency": {}}}  # Нет code

        result = get_transaction_amount_in_rubles(transaction)

        assert result == 100.0  # По умолчанию RUB

    @patch.dict(os.environ, {"API_KEY": "test_key"})
    def test_get_transaction_amount_missing_currency(self) -> None:
        """Тест когда нет currency"""
        transaction = {
            "operationAmount": {
                "amount": "100.00"
                # Нет currency
            }
        }

        result = get_transaction_amount_in_rubles(transaction)

        assert result == 100.0
