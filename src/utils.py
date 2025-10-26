import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.logger_config import utils_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    utils_logger = logging.getLogger("utils")


def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает данные о финансовых транзакциях из JSON-файла
    """
    utils_logger.info(f"Попытка загрузки файла: {file_path}")

    if not os.path.exists(file_path):
        utils_logger.warning(f"Файл не найден: {file_path}")
        return []

    try:
        # Открываем и читаем файл
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()

            if not content:
                utils_logger.warning(f"Файл пустой: {file_path}")
                return []

            data = json.loads(content)

            # Проверяем, что данные - это список
            if isinstance(data, list):
                utils_logger.info(f"Успешно загружено {len(data)} транзакций из {file_path}")
                return data
            else:
                utils_logger.warning(f"Файл не содержит список: {file_path}")
                return []

    except json.JSONDecodeError as e:
        utils_logger.error(f"Ошибка парсинга JSON в файле {file_path}: {e}")
        return []
    except UnicodeDecodeError as e:
        utils_logger.error(f"Ошибка кодировки в файле {file_path}: {e}")
        return []
    except Exception as e:
        utils_logger.error(f"Неожиданная ошибка при загрузке файла {file_path}: {e}")
        return []


def load_transactions_excel(file_path: str = "data/operations.xlsx") -> pd.DataFrame:
    """
    Загружает транзакции из Excel файла для новой функциональности
    """
    try:
        df = pd.read_excel(file_path)
        utils_logger.info(f"Успешно загружено {len(df)} транзакций из {file_path}")
        return df
    except Exception as e:
        utils_logger.error(f"Ошибка загрузки файла {file_path}: {e}")
        return pd.DataFrame()


def load_user_settings(settings_path: str = "user_settings.json") -> Dict[str, List[str]]:
    """
    Загружает пользовательские настройки из JSON файла
    """
    default_settings: Dict[str, List[str]] = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"],
    }

    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings: Dict[str, Any] = json.load(f)

        result: Dict[str, List[str]] = {
            "user_currencies": list(settings.get("user_currencies", default_settings["user_currencies"])),
            "user_stocks": list(settings.get("user_stocks", default_settings["user_stocks"])),
        }

        utils_logger.info(f"Пользовательские настройки загружены из {settings_path}")
        return result

    except FileNotFoundError:
        utils_logger.warning(f"Файл настроек {settings_path} не найден, используются настройки по умолчанию")
        return default_settings.copy()

    except Exception as e:
        utils_logger.error(f"Ошибка загрузки {settings_path}: {e}")
        return default_settings.copy()


def get_greeting_by_time(time_str: str) -> str:
    """
    Определяет приветствие по времени
    """
    try:
        time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").time()

        if 5 <= time_obj.hour < 12:
            return "Доброе утро"
        elif 12 <= time_obj.hour < 18:
            return "Добрый день"
        elif 18 <= time_obj.hour < 23:
            return "Добрый вечер"
        else:
            return "Доброй ночи"
    except ValueError as e:
        utils_logger.error(f"Неверный формат времени: {time_str}, ошибка: {e}")
        return "Добрый день"


def filter_transactions_by_date_range(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Фильтрует транзакции по диапазону дат
    """
    try:
        if "date" not in df.columns:
            utils_logger.error("В DataFrame отсутствует колонка 'date'")
            return df

        df["date"] = pd.to_datetime(df["date"])
        mask = (df["date"] >= start_date) & (df["date"] <= end_date)
        filtered_df = df.loc[mask]
        utils_logger.info(f"Отфильтровано {len(filtered_df)} транзакций с {start_date} по {end_date}")
        return filtered_df
    except Exception as e:
        utils_logger.error(f"Ошибка фильтрации по датам: {e}")
        return df


def convert_json_transactions_to_dataframe(transactions: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Конвертирует JSON транзакции в DataFrame для совместимости
    """
    try:
        df = pd.DataFrame(transactions)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        utils_logger.error(f"Ошибка конвертации транзакций в DataFrame: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    transactions = load_transactions("data/operations.json")
    print(f"Загружено транзакций: {len(transactions)}")

    empty_result = load_transactions("nonexistent.json")
    print(f"Результат для несуществующего файла: {len(empty_result)}")
