import pytest

from src.masks import get_mask_account, get_mask_card_number


@pytest.mark.parametrize(
    "card_number, expected",
    [
        ("1234567812345678", "1234 56** **** 5678"),
        ("9876543210987654", "9876 54** **** 7654"),
        ("1111222233334444", "1111 22** **** 4444"),
    ],
)
def test_get_mask_card_number_parametrized(card_number: str, expected: str) -> None:
    """Параметризованный тест маскировки карт."""
    assert get_mask_card_number(card_number) == expected


@pytest.mark.parametrize(
    "account_number, expected",
    [
        ("12345678901234567890", "**7890"),
        ("98765432109876543210", "**3210"),
        ("11111111112222222222", "**2222"),
    ],
)
def test_get_mask_account_parametrized(account_number: str, expected: str) -> None:
    """Параметризованный тест маскировки счетов."""
    assert get_mask_account(account_number) == expected


@pytest.mark.parametrize(
    "invalid_card_number, error_message",
    [
        ("123", "Номер карты должен содержать 16 цифр"),
        ("12345678123456789", "Номер карты должен содержать 16 цифр"),
        ("abcdefghijklmnop", "Номер карты должен содержать 16 цифр"),
        ("", "Номер карты должен содержать 16 цифр"),
    ],
)
def test_get_mask_card_number_invalid_input(invalid_card_number: str, error_message: str) -> None:
    """Тест маскировки карт с невалидными входными данными."""
    with pytest.raises(ValueError, match=error_message):
        get_mask_card_number(invalid_card_number)


@pytest.mark.parametrize(
    "invalid_account_number, error_message",
    [
        ("123", "Номер счета должен содержать ровно 20 цифр"),
        ("123456789012345678901", "Номер счета должен содержать ровно 20 цифр"),
        ("abcdefghijklmnopqrst", "Номер счета должен содержать только цифры"),
        ("", "Номер счета должен содержать ровно 20 цифр"),
        # УБРАН тест с пробелами, так как функция их корректно обрабатывает
    ],
)
def test_get_mask_account_invalid_input(invalid_account_number: str, error_message: str) -> None:
    """Тест маскировки счетов с невалидными входными данными."""
    with pytest.raises(ValueError, match=error_message):
        get_mask_account(invalid_account_number)


def test_get_mask_card_number_with_integer_input() -> None:
    """Тест маскировки карты с числовым входом."""
    result = get_mask_card_number(1234567812345678)
    assert result == "1234 56** **** 5678"


def test_get_mask_account_with_integer_input() -> None:
    """Тест маскировки счета с числовым входом."""
    result = get_mask_account(12345678901234567890)
    assert result == "**7890"


def test_get_mask_card_number_with_spaces() -> None:
    """Тест маскировки карты с пробелами в номере."""
    result = get_mask_card_number("1234 5678 1234 5678")
    assert result == "1234 56** **** 5678"


def test_get_mask_account_with_spaces() -> None:
    """Тест маскировки счета с пробелами в номере."""
    result = get_mask_account("1234 5678 9012 3456 7890")
    assert result == "**7890"
