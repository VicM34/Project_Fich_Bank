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
