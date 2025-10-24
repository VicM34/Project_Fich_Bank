from typing import Dict, List

from src.file_reader import read_csv_file, read_excel_file
from src.processing import filter_by_state, sort_by_date
from src.search import process_bank_operations, process_bank_search
from src.utils import load_transactions
from src.widget import get_date, mask_account_card


def test_masks() -> None:
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


def get_user_choice(options: List[str], prompt: str) -> str:
    """Получает выбор пользователя из списка вариантов."""
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    while True:
        try:
            choice = input("Ваш выбор: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return options[int(choice) - 1]
            print("Пожалуйста, введите корректный номер.")
        except (ValueError, IndexError):
            print("Пожалуйста, введите корректный номер.")


def get_status_choice() -> str:
    """Получает статус операций от пользователя."""
    available_statuses = ["EXECUTED", "CANCELED", "PENDING"]

    while True:
        print("Введите статус, по которому необходимо выполнить фильтрацию.")
        print(f"Доступные для фильтровки статусы: {', '.join(available_statuses)}")
        status = input("Статус: ").strip().upper()

        if status in available_statuses:
            return status
        else:
            print(f'Статус операции "{status}" недоступен.\n')


def get_yes_no_choice(question: str) -> bool:
    """Получает ответ Да/Нет от пользователя."""
    while True:
        answer = input(f"{question} (Да/Нет): ").strip().lower()
        if answer in ["да", "д", "yes", "y"]:
            return True
        elif answer in ["нет", "н", "no", "n"]:
            return False
        else:
            print("Пожалуйста, ответьте 'Да' или 'Нет'.")


def get_sort_direction() -> bool:
    """Получает направление сортировки от пользователя."""
    while True:
        direction = input("Отсортировать по возрастанию или по убыванию? ").strip().lower()
        if direction in ["по возрастанию", "возрастание", "asc", "ascending"]:
            return False
        elif direction in ["по убыванию", "убывание", "desc", "descending"]:
            return True
        else:
            print("Пожалуйста, укажите 'по возрастанию' или 'по убыванию'.")


def filter_rub_transactions(transactions: List[Dict]) -> List[Dict]:
    """Фильтрует рублевые транзакции."""
    return [
        transaction
        for transaction in transactions
        if transaction.get("operationAmount", {}).get("currency", {}).get("code") == "RUB"
    ]


def format_transaction(transaction: Dict) -> str:
    """Форматирует транзакцию для вывода."""
    date = get_date(transaction.get("date", ""))
    description = transaction.get("description", "")

    from_account = transaction.get("from", "")
    to_account = transaction.get("to", "")

    if from_account:
        from_formatted = mask_account_card(from_account)
    else:
        from_formatted = ""

    if to_account:
        to_formatted = mask_account_card(to_account)
    else:
        to_formatted = ""

    amount_info = transaction.get("operationAmount", {})
    amount = amount_info.get("amount", "0")
    currency = amount_info.get("currency", {}).get("code", "RUB")

    lines = [f"{date} {description}"]

    if from_formatted and to_formatted:
        lines.append(f"{from_formatted} -> {to_formatted}")
    elif from_formatted:
        lines.append(f"{from_formatted}")
    elif to_formatted:
        lines.append(f"-> {to_formatted}")

    lines.append(f"Сумма: {amount} {currency}")

    return "\n".join(lines) + "\n"


def show_statistics(transactions: List[Dict]) -> None:
    """Показывает статистику по операциям."""
    if not transactions:
        print("Нет данных для статистики.")
        return

    # Получаем все уникальные категории из описаний
    categories = set()
    for transaction in transactions:
        description = transaction.get("description", "")
        if description:
            categories.add(description)

    if not categories:
        print("Нет категорий для анализа.")
        return

    # Используем process_bank_operations для подсчета
    stats = process_bank_operations(transactions, list(categories))

    print("\n" + "=" * 50)
    print("СТАТИСТИКА ОПЕРАЦИЙ")
    print("=" * 50)
    print(f"Всего операций в выборке: {len(transactions)}")
    print("\nРаспределение по категориям:")

    # Сортируем по количеству операций (по убыванию)
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)

    for category, count in sorted_stats:
        if count > 0:
            percentage = (count / len(transactions)) * 100
            print(f"  {category}: {count} операций ({percentage:.1f}%)")

    print("=" * 50)


def bank_app() -> None:
    """Основное банковское приложение"""
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")

    file_options = [
        "Получить информацию о транзакциях из JSON-файла",
        "Получить информацию о транзакциях из CSV-файла",
        "Получить информацию о транзакциях из XLSX-файла",
    ]
    file_choice = get_user_choice(file_options, "Выберите необходимый пункт меню:")

    if "JSON" in file_choice:
        file_path = "data/operations.json"
        transactions = load_transactions(file_path)
        print("Для обработки выбран JSON-файл.")
    elif "CSV" in file_choice:
        file_path = "data/transactions.csv"
        transactions = read_csv_file(file_path)
        print("Для обработки выбран CSV-файл.")
    elif "XLSX" in file_choice:
        file_path = "data/transactions_excel.xlsx"
        transactions = read_excel_file(file_path)
        print("Для обработки выбран XLSX-файл.")
    else:
        print("Неизвестный формат файла.")
        return

    if not transactions:
        print("Не удалось загрузить транзакции из файла.")
        return

    status = get_status_choice()
    filtered_transactions = filter_by_state(transactions, status)
    print(f'Операции отфильтрованы по статусу "{status}"')

    if not filtered_transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        return

    # ДОБАВЛЯЕМ СТАТИСТИКУ ДО ФИЛЬТРАЦИИ
    if get_yes_no_choice("Показать статистику по всем операциям?"):
        show_statistics(transactions)

    if get_yes_no_choice("Отсортировать операции по дате?"):
        reverse = get_sort_direction()
        filtered_transactions = sort_by_date(filtered_transactions, reverse=reverse)

    if get_yes_no_choice("Выводить только рублевые транзакции?"):
        filtered_transactions = filter_rub_transactions(filtered_transactions)

    if get_yes_no_choice("Отфильтровать список транзакций по определенному слову в описании?"):
        search_word = input("Введите слово для поиска в описании: ").strip()
        if search_word:
            filtered_transactions = process_bank_search(filtered_transactions, search_word)

    # ДОБАВЛЯЕМ СТАТИСТИКУ ПОСЛЕ ФИЛЬТРАЦИИ
    if get_yes_no_choice("Показать статистику по отфильтрованным операциям?"):
        show_statistics(filtered_transactions)

    print("Распечатываю итоговый список транзакций...")
    print(f"\nВсего банковских операций в выборке: {len(filtered_transactions)}\n")

    if filtered_transactions:
        for transaction in filtered_transactions:
            print(format_transaction(transaction))
    else:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")


def main() -> None:
    """Главная функция с выбором режима"""
    print("=== БАНКОВСКАЯ СИСТЕМА ===")
    print("1. Тестирование масок карт и счетов")
    print("2. Работа с банковскими транзакциями")
    print("3. Выход")

    while True:
        choice = input("\nВыберите режим работы (1-3): ").strip()

        if choice == "1":
            print("\n" + "=" * 50)
            print("ТЕСТИРОВАНИЕ МАСОК")
            print("=" * 50)
            test_masks()
        elif choice == "2":
            print("\n" + "=" * 50)
            print("БАНКОВСКИЕ ТРАНЗАКЦИИ")
            print("=" * 50)
            bank_app()
        elif choice == "3":
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Введите 1, 2 или 3.")


if __name__ == "__main__":
    main()
