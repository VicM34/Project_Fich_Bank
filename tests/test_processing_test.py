from datetime import datetime

import pytest

from src.processing import filter_by_state, sort_by_date


@pytest.fixture
def sample_operations() -> list[dict[str, str | int]]:
    """Фикстура с тестовыми операциями."""
    return [
        {"id": 1, "state": "EXECUTED", "date": "2024-01-15T10:30:00.000000"},
        {"id": 2, "state": "EXECUTED", "date": "2024-01-15T10:30:00.000000"},  # Такая же дата
        {"id": 3, "state": "CANCELED", "date": "2023-12-01T14:20:00.000000"},
        {"id": 4, "state": "PENDING", "date": "2023-11-10T09:15:00.000000"},
        {"id": 5, "state": "EXECUTED", "date": "2023-10-05T16:45:00.000000"},
        {"id": 6, "state": "COMPLETED", "date": "2023-09-20T11:00:00.000000"},
        {"id": 7, "state": "EXECUTED"},  # Без даты
        {"id": 8, "state": "FAILED", "date": "invalid-date"},  # Невалидная дата
    ]


@pytest.fixture
def operations_with_same_dates() -> list[dict[str, str | int]]:
    """Фикстура с операциями с одинаковыми датами."""
    return [
        {"id": 1, "state": "EXECUTED", "date": "2024-01-01T12:00:00.000000"},
        {"id": 2, "state": "CANCELED", "date": "2024-01-01T12:00:00.000000"},
        {"id": 3, "state": "EXECUTED", "date": "2024-01-01T12:00:00.000000"},
        {"id": 4, "state": "PENDING", "date": "2023-12-15T09:30:00.000000"},
    ]


@pytest.fixture
def operations_with_invalid_dates() -> list[dict[str, str | int]]:
    """Фикстура с невалидными датами."""
    return [
        {"id": 1, "state": "EXECUTED", "date": "2024-01-01T12:00:00.000000"},
        {"id": 2, "state": "EXECUTED", "date": "invalid-date-format"},
        {"id": 3, "state": "EXECUTED", "date": "2024/01/01 12:00:00"},
        {"id": 4, "state": "EXECUTED", "date": ""},
        {"id": 5, "state": "EXECUTED"},  # Нет даты
    ]


@pytest.mark.parametrize(
    "state, expected_count, expected_ids",
    [
        ("EXECUTED", 4, [1, 2, 5, 7]),  # ← 4 executed (id 1,2,5,7)
        ("CANCELED", 1, [3]),
        ("PENDING", 1, [4]),
        ("COMPLETED", 1, [6]),
        ("FAILED", 1, [8]),
        ("NONEXISTENT", 0, []),
    ],
)
def test_filter_by_state_parametrized(
    sample_operations: list[dict[str, str | int]], state: str, expected_count: int, expected_ids: list[int]
) -> None:
    """Параметризованный тест фильтрации по разным статусам."""
    result = filter_by_state(sample_operations, state)
    assert len(result) == expected_count
    assert all(op["id"] in expected_ids for op in result)
    assert all(op["state"] == state for op in result)


def test_filter_by_state_empty_result() -> None:
    """Тест фильтрации когда нет операций с указанным статусом."""
    operations = [
        {"id": 1, "state": "EXECUTED", "date": "2024-01-01T12:00:00.000000"},
        {"id": 2, "state": "EXECUTED", "date": "2024-01-02T12:00:00.000000"},
    ]

    # Пытаемся найти несуществующий статус
    result = filter_by_state(operations, "CANCELED")
    assert result == []  # Должен вернуть пустой список


def test_filter_by_state_default_parameter() -> None:
    """Тест фильтрации с параметром по умолчанию."""
    operations = [
        {"id": 1, "state": "EXECUTED", "date": "2024-01-01T12:00:00.000000"},
        {"id": 2, "state": "CANCELED", "date": "2024-01-02T12:00:00.000000"},
    ]

    result = filter_by_state(operations)  # По умолчанию EXECUTED
    assert len(result) == 1
    assert result[0]["id"] == 1
    assert result[0]["state"] == "EXECUTED"


@pytest.mark.parametrize(
    "reverse, expected_order",
    [
        (True, [1, 2, 3, 4, 5, 6]),  # По убыванию (новые сначала)
        (False, [6, 5, 4, 3, 1, 2]),  # По возрастанию (старые сначала)
    ],
)
def test_sort_by_date_parametrized(
    sample_operations: list[dict[str, str | int]], reverse: bool, expected_order: list[int]
) -> None:
    """Параметризованный тест сортировки по дате."""
    result = sort_by_date(sample_operations, reverse=reverse)

    # Более строгая фильтрация: только валидные ISO даты
    dated_operations = []
    for op in result:
        if "date" in op:
            try:
                datetime.fromisoformat(op["date"].replace("Z", "+00:00"))
                dated_operations.append(op)
            except (ValueError, AttributeError):
                continue  # Пропускаем невалидные даты

    # Проверяем порядок ID
    result_ids = [op["id"] for op in dated_operations]
    assert result_ids == expected_order


def test_sort_by_date_with_same_dates(operations_with_same_dates: list[dict[str, str | int]]) -> None:
    """Тест сортировки при одинаковых датах."""
    result = sort_by_date(operations_with_same_dates, reverse=True)

    # Операции с одинаковой датой должны сохранить исходный порядок
    same_date_ops = [op for op in result if op["date"] == "2024-01-01T12:00:00.000000"]
    assert [op["id"] for op in same_date_ops] == [1, 2, 3]  # Исходный порядок


def test_sort_by_date_with_invalid_dates(operations_with_invalid_dates: list[dict[str, str | int]]) -> None:
    """Тест сортировки с невалидными датами."""
    result = sort_by_date(operations_with_invalid_dates, reverse=True)

    # Операции с валидными датами должны быть сначала
    valid_date_ops = [op for op in result if op.get("date") == "2024-01-01T12:00:00.000000"]
    invalid_date_ops = [op for op in result if op.get("date") not in [None, "2024-01-01T12:00:00.000000"]]
    no_date_ops = [op for op in result if "date" not in op]

    assert len(valid_date_ops) == 1
    assert valid_date_ops[0]["id"] == 1  # Единственная валидная дата
    assert len(invalid_date_ops) == 3  # 3 операции с невалидными датами
    assert len(no_date_ops) == 1  # 1 операция без даты


def test_sort_by_date_stability() -> None:
    """Тест стабильности сортировки (сохранение порядка при одинаковых датах)."""
    operations = [
        {"id": 1, "state": "EXECUTED", "date": "2024-01-01T12:00:00.000000"},
        {"id": 2, "state": "CANCELED", "date": "2024-01-01T12:00:00.000000"},
        {"id": 3, "state": "PENDING", "date": "2024-01-01T12:00:00.000000"},
    ]

    result = sort_by_date(operations, reverse=True)
    # Порядок должен сохраниться как в исходном списке
    assert [op["id"] for op in result] == [1, 2, 3]


def test_sort_by_date_empty_operations() -> None:
    """Тест сортировки пустого списка."""
    result = sort_by_date([])
    assert result == []


def test_sort_by_date_none_operations() -> None:
    """Тест сортировки None списка."""
    result = sort_by_date([])
    assert result == []


def test_integration_filter_and_sort(sample_operations: list[dict[str, str | int]]) -> None:
    """Интеграционный тест: фильтрация + сортировка."""
    # Фильтруем выполненные операции
    executed_ops = filter_by_state(sample_operations, "EXECUTED")

    # Сортируем по убыванию даты
    sorted_ops = sort_by_date(executed_ops, reverse=True)

    # Проверяем результаты
    assert len(sorted_ops) == 4
    assert all(op["state"] == "EXECUTED" for op in sorted_ops)

    # Проверяем порядок сортировки (новые сначала)
    valid_dated_ops = [op for op in sorted_ops if "date" in op and op["date"] not in ["", "invalid-date-format"]]
    assert [op["id"] for op in valid_dated_ops] == [1, 2, 5]
