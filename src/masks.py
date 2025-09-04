def get_mask_card_number(card_number: int | str) -> str:
    """Создаем функцию, которая принимает на вход номер карты в виде числа и возвращает маску номера по правилу
    XXXX XX** **** XXXX"""

    card_str = str(card_number).replace(" ", "")
    # преобразуем в строку и удаляем пробелы

    if len(card_str) != 16 or not card_str.isdigit():
        raise ValueError("Номер карты должен содержать 16 цифр")
    # Проверяем длину номера карты (16 цифр)

    return f"{card_str[:4]} {card_str[4:6]}** **** {card_str[12:]}"
    # Форматируем по маске


def get_mask_account(account_number: int | str) -> str:
    """Создаем функцию, которая принимает на вход номер счета в виде числа и возвращает маску номера по правилу
    **XXXX"""

    account_str = str(account_number).replace(" ", "")
    # преобразуем в строку и удаляем пробелы

    if len(account_str) != 20:
        raise ValueError("Номер счета должен содержать ровно 20 цифр")
    if not account_str.isdigit():
        raise ValueError("Номер счета должен содержать только цифры")
    # Проверяем длину номера счета (20 цифр)

    return f"**{account_str[-4:]}"
    # Форматируем по маске


