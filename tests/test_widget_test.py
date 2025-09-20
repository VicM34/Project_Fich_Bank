from src.widget import mask_account_card


def test_mask_account_card_debit_card() -> None:
    """Тест маскировки номера дебетовой карты."""
    result = mask_account_card("MasterCard 9876543210987654")
    assert result == "MasterCard 9876 54** **** 7654"


def test_mask_account_card_account() -> None:
    """Тест маскировки номера счета."""
    result = mask_account_card("Счет 12345678901234567890")
    assert result == "Счет **7890"


def test_mask_account_card_credit_card() -> None:
    """Тест маскировки номера кредитной карты."""
    result = mask_account_card("Visa Platinum 1234567812345678")
    assert result == "Visa Platinum 1234 56** **** 5678"
