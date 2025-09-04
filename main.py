from src.widget import mask_account_card


def main() -> None:
    """Основная функция для тестирования масок.
    :rtype: None
    """
    test_cases = [
        "Visa Platinum 7000792289606361",
        "Maestro 7000792289606361",
        "Счет 73654108430135874305",
        "MasterCard 7158300734726758",
        "Счет 64686473678894779589",
        "Visa Classic 6831982476737658"
    ]

    for test in test_cases:
        try:
            result = mask_account_card(test)
            print(f"✓ {test} -> {result}")
        except ValueError as e:
            print(f"✗ {test} -> Ошибка: {e}")


if __name__ == "__main__":
    main()
