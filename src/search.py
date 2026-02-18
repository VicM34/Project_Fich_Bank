"""
Модуль для поиска и анализа банковских операций.
"""

import re
from collections import Counter
from typing import Dict, List


def process_bank_search(data: List[Dict], search: str) -> List[Dict]:
    """
    Ищет операции по заданной строке в описании с использованием регулярных выражений.

    Args:
        data: Список словарей с транзакциями
        search: Строка для поиска в описании

    Returns:
        Список словарей с операциями, у которых в описании есть искомая строка
    """
    if not data or not search:
        return []

    result = []
    pattern = re.compile(re.escape(search), re.IGNORECASE)

    for operation in data:
        description = operation.get("description", "")
        if pattern.search(description):
            result.append(operation)

    return result


def process_bank_operations(data: List[Dict], categories: List[str]) -> Dict[str, int]:
    """
    Подсчитывает количество операций по категориям.

    Args:
        data: Список словарей с транзакциями
        categories: Список категорий для подсчета

    Returns:
        Словарь с количеством операций по каждой категории
    """
    if not data or not categories:
        return {}

    # Приводим категории к нижнему регистру для case-insensitive сравнения
    categories_lower = [cat.lower() for cat in categories]

    # Собираем все описания
    descriptions = []
    for operation in data:
        description = operation.get("description", "").lower()
        if description:
            descriptions.append(description)

    # Используем Counter для подсчета
    description_counter = Counter(descriptions)

    # Фильтруем только нужные категории
    result = {}
    for category in categories_lower:
        result[category] = description_counter.get(category, 0)

    return result
