import pytest
from datetime import datetime
from src.processing import filter_by_state, sort_by_date


@pytest.fixture
def sample_operations():
    return [
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
        {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
        {"id": 1, "state": "EXECUTED", "date": "2020-01-01T00:00:00.000000"},
        {"id": 2, "state": "PENDING", "date": "2017-05-15T12:00:00.000000"},
        {"id": 3, "state": "EXECUTED"}
    ]


def test_filter_by_state_executed(sample_operations):
    """Тест фильтрации выполненных операций."""
    result = filter_by_state(sample_operations, "EXECUTED")

    assert len(result) == 4
    assert all(op["state"] == "EXECUTED" for op in result)
    assert all(op["id"] in [41428829, 939719570, 1, 3] for op in result)


def test_filter_by_state_default(sample_operations):
    """Тест фильтрации с параметром по умолчанию (EXECUTED)."""
    result = filter_by_state(sample_operations)

    assert len(result) == 4
    assert all(op["state"] == "EXECUTED" for op in result)


def test_sort_by_date_descending(sample_operations):
    """Тест сортировки по убыванию даты (новые сначала)."""
    result = sort_by_date(sample_operations, reverse=True)

    # Проверяем порядок (от новых к старым)
    dates = [op["date"] for op in result if "date" in op]
    assert dates == [
        "2020-01-01T00:00:00.000000",
        "2019-07-03T18:35:29.512364",
        "2018-10-14T08:21:33.419441",
        "2018-09-12T21:27:25.241689",
        "2018-06-30T02:08:58.425572",
        "2017-05-15T12:00:00.000000",
    ]


def test_sort_by_date_ascending(sample_operations):
    """Тест сортировки по возрастанию даты (старые сначала)."""
    result = sort_by_date(sample_operations, reverse=False)

    # Проверяем порядок (от старых к новым)
    dates = [op["date"] for op in result if "date" in op]
    assert dates == [
        "2017-05-15T12:00:00.000000",
        "2018-06-30T02:08:58.425572",
        "2018-09-12T21:27:25.241689",
        "2018-10-14T08:21:33.419441",
        "2019-07-03T18:35:29.512364",
        "2020-01-01T00:00:00.000000",
    ]


def test_sort_by_date_empty_list():
    """Тест сортировки пустого списка."""
    result = sort_by_date([])
    assert result == []


def test_sort_by_date_none_list():
    """Тест сортировки None списка."""
    result = sort_by_date(None)
    assert result == []


def test_filter_by_state_invalid_input():
    """Тест обработки неверного ввода."""
    # Тест для None
    result = filter_by_state(None, "EXECUTED")
    assert result == []

    # Тест для пустого списка
    result = filter_by_state([], "EXECUTED")
    assert result == []