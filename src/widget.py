from datetime import datetime

from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(account_card_info: str) -> str:
    """Функция, которая принимает на вход номер счета или карты и возвращает маску"""

    parts = account_card_info.split()
    # Разделяем строку на слова

    if len(parts) < 2:
        raise ValueError("Строка должна содержать тип и номер")

    number_str = parts[-1].replace(" ", "")
    # Извлекаем номер

    type_str = " ".join(parts[:-1])
    # Определяем тип по первому слову

    # Проверяем, является ли номер картой (16 цифр)
    if number_str.isdigit() and len(number_str) == 16:
        # Проверяем, является ли номер картой (16 цифр)
        masked_number = get_mask_card_number(number_str)
        # Используем существующую функцию для карт
        return f"{type_str} {masked_number}"

    elif number_str.isdigit() and len(number_str) == 20:
        # Проверяем, является ли номер счетом (20 цифр)
        masked_number = get_mask_account(number_str)
        # Используем существующую функцию для счетов
        return f"{type_str} {masked_number}"

    else:
        raise ValueError("Неверный формат номера. Должно быть 16 цифр для карты или 20 цифр для счета")


def get_date(date_string: str) -> str:
    """Функция, которая преобразует формат даты из
    '2024-03-11T02:26:18.671407' в 'ДД.ММ.ГГГГ'"""
    try:

        if "." in date_string:
            date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")
            # Вводим формат даты с миллисекундами

        else:
            date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
            # Вводим формат даты без миллисекунд

        return date_obj.strftime("%d.%m.%Y")
        # Возвращаем нужный нам формат(ДД.ММ.ГГГГ)

    except ValueError:
        raise ValueError("Неверный формат даты. Ожидается: 'YYYY-MM-DDTHH:MM:SS.microseconds'")
        # Прописываем конструкцию для обработки вызова ошибки
