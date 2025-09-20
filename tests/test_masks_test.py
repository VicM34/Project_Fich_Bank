import pytest
from src.masks import get_mask_card_number, get_mask_account

def test_get_mask_card_number():
    """Тест для функции маскировки карты."""
    assert get_mask_card_number(1234567812345678) == "1234 56** **** 5678"

def test_get_mask_account():
    """Тест для функции маскировки счета."""
    assert get_mask_account("12345678901234567890") == "**7890"