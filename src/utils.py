import json
import os
import sys
from typing import Any, Dict, List

from src.logger_config import utils_logger

# Добавляем путь к корню проекта для импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает данные о финансовых транзакциях из JSON-файла
    """
    utils_logger.info(f"Попытка загрузки файла: {file_path}")

    # Проверяем существование файла
    if not os.path.exists(file_path):
        utils_logger.warning(f"Файл не найден: {file_path}")
        return []

    try:
        # Открываем и читаем файл
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()

            # Если файл пустой
            if not content:
                utils_logger.warning(f"Файл пустой: {file_path}")
                return []

            # Парсим JSON
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


# Пример использования
if __name__ == "__main__":
    # Тестирование успешной загрузки
    transactions = load_transactions("data/operations.json")
    print(f"Загружено транзакций: {len(transactions)}")

    # Тестирование ошибок
    empty_result = load_transactions("nonexistent.json")
    print(f"Результат для несуществующего файла: {len(empty_result)}")
