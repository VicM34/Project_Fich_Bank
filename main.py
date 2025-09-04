from src.masks import get_mask_account, get_mask_card_number


def main() -> None:
    """Основная функция для тестирования масок."""
    print("Тест маскировки карты:")
    print(get_mask_card_number(1234567812345678))

    print("Тест маскировки счета:")
    print(get_mask_account("12345678912345678912"))


if __name__ == "__main__":
    main()
