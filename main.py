from src.widget import mask_account_card


def main() -> None:
    """Функция для тестирования масок"""

    test_cases = [
        "Visa Platinum 7000792289606361",
        "Maestro 7000792289606361",
        "Счет 73654108430135874305",
        "MasterCard 7158300734726758",
        "Счет 64686473678894779589",
        "Visa Classic 6831982476737658",
    ]

    cards = []
    accounts = []
    errors = []

    for test in test_cases:
        try:
            result = mask_account_card(test)
            if "Счет" in test:
                accounts.append((test, result))
            else:
                cards.append((test, result))
        except ValueError as e:
            errors.append((test, str(e)))

    # Вывод карт
    for original, masked in cards:
        print(masked)

    for original, masked in accounts:
        print(masked)


if __name__ == "__main__":
    main()

