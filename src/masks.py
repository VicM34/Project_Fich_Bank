import os
import sys

from src.logger_config import masks_logger

# Добавляем путь к корню проекта для импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_mask_card_number(card_number: int | str) -> str:
    """
    Создаем функцию, которая принимает на вход номер карты в виде числа и возвращает маску номера по правилу
    XXXX XX** **** XXXX
    """
    card_str = str(card_number).replace(" ", "")
    # преобразуем в строку и удаляем пробелы

    if len(card_str) != 16 or not card_str.isdigit():
        masks_logger.error(f"Неверный номер карты: {card_number}. Должно быть 16 цифр")
        raise ValueError("Номер карты должен содержать 16 цифр")
    # Проверяем длину номера карты (16 цифр)

    masks_logger.info(f"Успешно создана маска для карты: {card_number}")
    return f"{card_str[:4]} {card_str[4:6]}** **** {card_str[12:]}"
    # Форматируем по маске


def get_mask_account(account_number: int | str) -> str:
    """
    Создаем функцию, которая принимает на вход номер счета в виде числа и возвращает маску номера по правилу
    **XXXX
    """
    account_str = str(account_number).replace(" ", "")
    # преобразуем в строку и удаляем пробелы

    if len(account_str) != 20:
        masks_logger.error(f"Неверная длина номера счета: {account_number}. Должно быть 20 цифр")
        raise ValueError("Номер счета должен содержать ровно 20 цифр")
    if not account_str.isdigit():
        masks_logger.error(f"Номер счета содержит не только цифры: {account_number}")
        raise ValueError("Номер счета должен содержать только цифры")
    # Проверяем длину номера счета (20 цифр)

    masks_logger.info(f"Успешно создана маска для счета: {account_number}")
    return f"**{account_str[-4:]}"
    # Форматируем по маске


# Пример использования
if __name__ == "__main__":
    try:
        # Тестирование успешных случаев
        card_mask = get_mask_card_number("1234567812345678")
        print(f"Маска карты: {card_mask}")

        account_mask = get_mask_account("12345678901234567890")
        print(f"Маска счета: {account_mask}")

        # Тестирование ошибок
        # get_mask_card_number("123")  # Вызовет ошибку
        # get_mask_account("123abc")   # Вызовет ошибку

    except Exception as e:
        masks_logger.error(f"Ошибка при выполнении: {e}")
