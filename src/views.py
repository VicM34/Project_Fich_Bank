import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from src.external_api import get_currency_rates, get_stock_prices
from src.utils import (
    filter_transactions_by_date_range,
    get_greeting_by_time,
    load_transactions_excel,
    load_user_settings,
)

logger = logging.getLogger(__name__)


def get_cards_statistics(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Рассчитывает статистику по картам
    """
    cards_data = []

    # Группируем по последним 4 цифрам карты (предполагаем, что есть колонка 'card_number')
    if "card_number" in df.columns:
        for card in df["card_number"].unique():
            card_df = df[df["card_number"] == card]
            total_spent = card_df["amount"].sum()
            cashback = total_spent * 0.01  # 1% кешбэк

            cards_data.append(
                {"last_digits": str(card)[-4:], "total_spent": round(total_spent, 2), "cashback": round(cashback, 2)}
            )

    return cards_data


def get_top_transactions(df: pd.DataFrame, top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Возвращает топ-N транзакций по сумме
    """
    try:
        # Сортируем по абсолютному значению суммы и берем топ-N
        top_df = df.nlargest(top_n, "amount", keep="all")

        top_transactions = []
        for _, row in top_df.iterrows():
            top_transactions.append(
                {
                    "date": row["date"].strftime("%d.%m.%Y"),
                    "amount": round(row["amount"], 2),
                    "category": row.get("category", "Не указана"),
                    "description": row.get("description", ""),
                }
            )

        return top_transactions
    except Exception as e:
        logger.error(f"Ошибка получения топ транзакций: {e}")
        return []


def main_page_data(date_time: str) -> Dict[str, Any]:
    """
    Главная функция для страницы 'Главная'
    """
    logger.info(f"Формирование данных для главной страницы на дату: {date_time}")

    try:
        df = load_transactions_excel("data/operations.xlsx")  # Добавляем file_path

        settings = load_user_settings()

        # Определяем диапазон дат
        date_obj = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        start_of_month = date_obj.replace(day=1)

        filtered_df = filter_transactions_by_date_range(
            df, start_of_month.strftime("%Y-%m-%d"), date_obj.strftime("%Y-%m-%d")
        )

        # Формируем ответ
        response = {
            "greeting": get_greeting_by_time(date_time),
            "cards": get_cards_statistics(filtered_df),
            "top_transactions": get_top_transactions(filtered_df),
            "currency_rates": get_currency_rates(settings.get("user_currencies", [])),
            "stock_prices": get_stock_prices(settings.get("user_stocks", [])),
        }

        logger.info("Данные для главной страницы успешно сформированы")
        return response

    except Exception as e:
        logger.error(f"Ошибка формирования данных главной страницы: {e}")
        return {"error": str(e)}


def events_page_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Функция для страницы 'События'
    Принимает DataFrame и возвращает данные для отображения событий
    """
    logger.info("Формирование данных для страницы 'События'")

    try:
        # Анализ событий по категориям
        events_by_category = []
        if "category" in df.columns:
            category_stats = df.groupby("category").agg({"amount": ["sum", "count"], "date": ["min", "max"]}).round(2)

            for category, stats in category_stats.iterrows():
                events_by_category.append(
                    {
                        "category": category,
                        "total_amount": stats[("amount", "sum")],
                        "transactions_count": stats[("amount", "count")],
                        "first_date": stats[("date", "min")].strftime("%Y-%m-%d"),
                        "last_date": stats[("date", "max")].strftime("%Y-%m-%d"),
                    }
                )

        # Последние события
        recent_events = []
        if not df.empty:
            recent_df = df.nlargest(10, "date")
            for _, row in recent_df.iterrows():
                recent_events.append(
                    {
                        "date": row["date"].strftime("%d.%m.%Y %H:%M"),
                        "amount": round(row["amount"], 2),
                        "category": row.get("category", "Не указана"),
                        "description": row.get("description", ""),
                    }
                )

        response = {
            "events_by_category": events_by_category,
            "recent_events": recent_events,
            "total_events": len(df),
            "period_events": (
                f"{df['date'].min().strftime('%d.%m.%Y')} - {df['date'].max().strftime('%d.%m.%Y')}"
                if not df.empty
                else "Нет данных"
            ),
        }

        logger.info("Данные для страницы 'События' успешно сформированы")
        return response

    except Exception as e:
        logger.error(f"Ошибка формирования данных страницы 'События': {e}")
        return {"error": str(e)}
