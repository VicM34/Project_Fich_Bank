from datetime import datetime
from typing import Any, Dict, List


def filter_by_state(operations: List[Dict[str, Any]], state: str = "EXECUTED") -> List[Dict[str, Any]]:
    """Функция, которая фильтрует операции по состоянию."""
    if not operations:
        return []
    return [operation for operation in operations if operation.get("state") == state]


def sort_by_date(operations: List[Dict[str, Any]], reverse: bool = True) -> List[Dict[str, Any]]:
    """Функция, которая сортирует список операций по дате. True - по убыванию, False - по возрастанию"""
    if not operations:
        return []

    def get_date_key(operation: Dict[str, Any]) -> datetime:
        """Вспомогательная функция для получения даты из операции."""
        date_str = operation.get("date")
        if not date_str:
            return datetime.min

        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            return datetime.min

    # Сортируем операции по дате
    return sorted(operations, key=get_date_key, reverse=reverse)


operations = [
    {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
    {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
    {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
    {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
]

# Сортировка по убыванию (новые сначала)
newest_first = sort_by_date(operations, reverse=True)
print("Новые операции сначала:")
for op in newest_first:
    print(f"{op['date']} - ID: {op['id']}")

# Сортировка по возрастанию (старые сначала)
oldest_first = sort_by_date(operations, reverse=False)
print("Старые операции сначала:")
for op in oldest_first:
    print(f"{op['date']} - ID: {op['id']}")
