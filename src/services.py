import logging
import math
import re
from typing import Any, Dict, List

import pandas as pd

from src.utils import load_transactions_excel

logger = logging.getLogger(__name__)


def simple_search(search_query: str) -> List[Dict[str, Any]]:
    """
    Простой поиск транзакций по запросу
    """
    logger.info(f"Выполнение поиска по запросу: '{search_query}'")

    try:
        df = load_transactions_excel()

        if df.empty or not search_query:
            return []

        mask = pd.Series(False, index=df.index)

        if "description" in df.columns:
            description_mask = df["description"].fillna("").str.contains(search_query, case=False, na=False)
            mask = mask | description_mask

        if "category" in df.columns:
            category_mask = df["category"].fillna("").str.contains(search_query, case=False, na=False)
            mask = mask | category_mask

        results_df = df[mask]

        # Форматируем результат
        results = []
        for _, row in results_df.iterrows():
            result_item = {
                "date": row.get("date", ""),
                "amount": 0.0,
                "category": row.get("category", ""),
                "description": row.get("description", ""),
                "card_number": "",
            }

            # Обрабатываем дату
            if pd.notna(row.get("date")):
                try:
                    if isinstance(row["date"], pd.Timestamp):
                        result_item["date"] = row["date"].strftime("%d.%m.%Y")
                    else:
                        result_item["date"] = str(row["date"])
                except Exception:
                    result_item["date"] = str(row.get("date", ""))

            # Обрабатываем сумму
            if pd.notna(row.get("amount")):
                try:
                    result_item["amount"] = round(float(row["amount"]), 2)
                except Exception:
                    result_item["amount"] = 0.0

            # Обрабатываем номер карты
            if pd.notna(row.get("card_number")):
                card_str = str(row["card_number"])
                result_item["card_number"] = card_str[-4:] if len(card_str) >= 4 else card_str

            results.append(result_item)

        logger.info(f"Найдено {len(results)} транзакций по запросу '{search_query}'")
        return results

    except Exception as e:
        logger.error(f"Ошибка при поиске '{search_query}': {e}")
        return []


def profitable_cashback_categories(year: int, month: int, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Сервис: Выгодные категории повышенного кешбэка
    """
    logger.info(f"Расчет выгодных категорий кешбэка за {month}.{year}")

    try:
        df = pd.DataFrame(transactions)

        # Фильтруем по дате
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df[(df["date"].dt.year == year) & (df["date"].dt.month == month)]

        # Группируем по категориям и считаем кешбэк
        cashback_by_category = {}
        if "category" in df.columns and "amount" in df.columns:
            category_totals = df.groupby("category")["amount"].sum()

            for category, total in category_totals.items():
                cashback = total * 0.05  # 5% кешбэк для примера
                cashback_by_category[str(category)] = round(float(cashback), 2)

        # Сортируем по убыванию кешбэка
        sorted_cashback = dict(sorted(cashback_by_category.items(), key=lambda x: x[1], reverse=True))

        response = {
            "period": f"{month}.{year}",
            "cashback_categories": sorted_cashback,
            "total_cashback": round(sum(sorted_cashback.values()), 2),
        }

        logger.info(f"Рассчитан кешбэк для {len(sorted_cashback)} категорий")
        return response

    except Exception as e:
        logger.error(f"Ошибка расчета кешбэка: {e}")
        return {"error": str(e)}


def investment_piggy_bank(month: str, transactions: List[Dict[str, Any]], round_limit: float = 10.0) -> Dict[str, Any]:
    """
    Сервис: Инвесткопилка - округление трат и накопление
    """
    logger.info(f"Расчет инвесткопилки за {month}")

    try:
        total_savings = 0.0
        rounded_transactions = []

        for transaction in transactions:
            amount = float(transaction.get("amount", 0))
            if amount > 0:  # Только траты (положительные суммы)
                rounded_up = math.ceil(amount / round_limit) * round_limit
                savings = rounded_up - amount

                if savings > 0:
                    total_savings += savings
                    rounded_transactions.append(
                        {
                            "original_amount": round(amount, 2),
                            "rounded_amount": round(rounded_up, 2),
                            "savings": round(savings, 2),
                            "description": transaction.get("description", ""),
                        }
                    )

        response = {
            "month": month,
            "total_savings": round(total_savings, 2),
            "rounded_transactions": rounded_transactions,
            "round_limit": round_limit,
        }

        logger.info(f"Накоплено в инвесткопилке: {total_savings}")
        return response

    except Exception as e:
        logger.error(f"Ошибка расчета инвесткопилки: {e}")
        return {"error": str(e)}


def search_by_phone_numbers(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Сервис: Поиск операций по телефонным номерам
    """
    logger.info("Поиск операций с телефонными номерами")

    try:
        phone_pattern = r"(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}"
        phone_transactions = []

        for transaction in transactions:
            description = transaction.get("description", "")
            # Ищем телефонные номера в описании
            phones_found = re.findall(phone_pattern, description)
            if phones_found:
                phone_transactions.append(
                    {"transaction": transaction, "phones_found": phones_found, "description": description}
                )

        response = {
            "found_transactions": len(phone_transactions),
            "transactions": phone_transactions,
            "search_pattern": "телефонные номера",
        }

        logger.info(f"Найдено транзакций с телефонами: {len(phone_transactions)}")
        return response

    except Exception as e:
        logger.error(f"Ошибка поиска по телефонным номерам: {e}")
        return {"error": str(e)}


def search_individual_transfers(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Сервис: Поиск переводов физическим лицам
    """
    logger.info("Поиск переводов физическим лицам")

    try:
        individual_keywords = ["физлицо", "перевод", "сбербанк онлайн", "тк", "тинькофф", "частное лицо"]
        individual_transactions = []

        for transaction in transactions:
            description = transaction.get("description", "").lower()
            # Ищем ключевые слова, указывающие на перевод физлицу
            if any(keyword in description for keyword in individual_keywords):
                individual_transactions.append(
                    {
                        "transaction": transaction,
                        "matched_keywords": [kw for kw in individual_keywords if kw in description],
                        "description": description,
                    }
                )

        response = {
            "found_transactions": len(individual_transactions),
            "transactions": individual_transactions,
            "search_keywords": individual_keywords,
        }

        logger.info(f"Найдено переводов физлицам: {len(individual_transactions)}")
        return response

    except Exception as e:
        logger.error(f"Ошибка поиска переводов физлицам: {e}")
        return {"error": str(e)}
