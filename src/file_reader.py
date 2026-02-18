"""
Модуль для чтения финансовых операций из CSV и XLSX файлов.
"""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import openpyxl
    from openpyxl.worksheet.worksheet import Worksheet

    HAS_EXCEL_SUPPORT = True
except ImportError:
    HAS_EXCEL_SUPPORT = False

from src.logger_config import utils_logger


def read_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Считывает финансовые операции из CSV файла.

    Args:
        file_path (str): Путь к файлу CSV

    Returns:
        List[Dict[str, Any]]: Список словарей с транзакциями
    """
    utils_logger.info(f"Чтение CSV файла: {file_path}")

    if not Path(file_path).exists():
        utils_logger.warning(f"CSV файл не найден: {file_path}")
        return []

    if Path(file_path).suffix.lower() != ".csv":
        utils_logger.warning(f"Файл не является CSV: {file_path}")
        return []

    transactions = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            # Определяем разделитель
            sample = file.read(1024)
            file.seek(0)

            delimiter = "," if "," in sample else ";"

            reader = csv.DictReader(file, delimiter=delimiter)

            for row_num, row in enumerate(reader, 1):
                try:
                    transaction = _parse_transaction_row(row)
                    if transaction:
                        transactions.append(transaction)
                except Exception as e:
                    utils_logger.warning(f"Ошибка в строке {row_num} CSV файла: {e}")
                    continue

        utils_logger.info(f"Успешно загружено {len(transactions)} транзакций из CSV: {file_path}")
        return transactions

    except Exception as e:
        utils_logger.error(f"Ошибка чтения CSV файла {file_path}: {e}")
        return []


def read_excel_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Считывает финансовые операции из Excel файла.

    Args:
        file_path (str): Путь к файлу Excel

    Returns:
        List[Dict[str, Any]]: Список словарей с транзакциями
    """
    utils_logger.info(f"Чтение Excel файла: {file_path}")

    if not HAS_EXCEL_SUPPORT:
        utils_logger.error("Для работы с Excel файлами установите openpyxl: pip install openpyxl")
        return []

    if not Path(file_path).exists():
        utils_logger.warning(f"Excel файл не найден: {file_path}")
        return []

    file_ext = Path(file_path).suffix.lower()
    if file_ext not in [".xlsx", ".xls"]:
        utils_logger.warning(f"Файл не является Excel: {file_path}")
        return []

    transactions = []

    try:
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        sheet: Optional[Worksheet] = workbook.active

        # Проверяем что sheet существует
        if sheet is None:
            utils_logger.warning(f"Excel файл не содержит активного листа: {file_path}")
            return []

        # Получаем заголовки из первой строки
        headers = []
        first_row = sheet[1]  # type: ignore[index]
        for cell in first_row:
            if cell.value:
                headers.append(str(cell.value).strip())

        if not headers:
            utils_logger.warning(f"Excel файл не содержит заголовков: {file_path}")
            return []

        # Читаем данные построчно
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), 2):  # type: ignore[union-attr]
            if not any(row):  # Пропускаем пустые строки
                continue

            try:
                # Создаем словарь из строки Excel
                row_data = {}
                for i, value in enumerate(row):
                    if i < len(headers) and value is not None:
                        row_data[headers[i]] = str(value) if value is not None else ""

                transaction = _parse_transaction_row(row_data)
                if transaction:
                    transactions.append(transaction)

            except Exception as e:
                utils_logger.warning(f"Ошибка в строке {row_num} Excel файла: {e}")
                continue

        utils_logger.info(f"Успешно загружено {len(transactions)} транзакций из Excel: {file_path}")
        return transactions

    except Exception as e:
        utils_logger.error(f"Ошибка чтения Excel файла {file_path}: {e}")
        return []


def _parse_transaction_row(row_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Парсит строку данных в формат транзакции.
    """
    transaction = {}

    # Маппинг полей на стандартные поля транзакции
    field_mapping = {
        "id": ["id", "ID", "Id", "transaction_id", "№"],
        "state": ["state", "State", "STATUS", "status", "Статус"],
        "date": ["date", "Date", "DATE", "datetime", "Дата"],
        "description": ["description", "Description", "DESCRIPTION", "comment", "Описание"],
        "from": ["from", "From", "FROM", "sender", "payer", "Отправитель"],
        "to": ["to", "To", "TO", "recipient", "receiver", "Получатель"],
    }

    # Применяем маппинг для основных полей
    for standard_field, possible_fields in field_mapping.items():
        for field in possible_fields:
            if field in row_data and row_data[field]:
                transaction[standard_field] = row_data[field]
                break

    # Обработка operationAmount (сумма и валюта)
    amount = None
    currency = "RUB"  # валюта по умолчанию

    # Ищем поле суммы
    amount_fields = ["amount", "Amount", "AMOUNT", "sum", "Sum", "Сумма", "operationAmount.amount"]
    for field in amount_fields:
        if field in row_data and row_data[field]:
            amount = row_data[field]
            break

    # Ищем поле валюты
    currency_fields = ["currency", "Currency", "CURRENCY", "valute", "Валюта", "operationAmount.currency.code"]
    for field in currency_fields:
        if field in row_data and row_data[field]:
            currency = row_data[field]
            break

    # Создаем структуру operationAmount
    if amount is not None:
        transaction["operationAmount"] = {
            "amount": amount,
            "currency": {"code": currency, "name": _get_currency_name(currency)},
        }

    return transaction


def _get_currency_name(currency_code: str) -> str:
    """
    Возвращает название валюты по коду.
    """
    currency_names = {
        "RUB": "Russian Ruble",
        "USD": "US Dollar",
        "EUR": "Euro",
        "GBP": "British Pound",
        "CNY": "Chinese Yuan",
        "JPY": "Japanese Yen",
    }
    return currency_names.get(currency_code, currency_code)
