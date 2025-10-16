import json
import os
from typing import Any, Dict, List


def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает данные о финансовых транзакциях из JSON-файла
    """
    # Проверяем существование файла
    if not os.path.exists(file_path):
        return []

    try:
        # Открываем и читаем файл
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()

            # Если файл пустой
            if not content:
                return []

            # Парсим JSON
            data = json.loads(content)

            # Проверяем, что данные - это список
            if isinstance(data, list):
                return data
            else:
                return []

    except (json.JSONDecodeError, UnicodeDecodeError):
        # Если ошибка парсинга JSON или кодировки
        return []
