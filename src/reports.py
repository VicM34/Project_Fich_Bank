import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

import pandas as pd

logger = logging.getLogger(__name__)

# Тип для функции, которую мы декорируем
F = TypeVar("F", bound=Callable[..., pd.DataFrame])


def report_decorator(filename: Optional[str] = None) -> Callable[[F], F]:
    """
    Декоратор для сохранения результатов отчетов в файл
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            result = func(*args, **kwargs)

            # Определяем имя файла
            if filename is None:
                report_filename = f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            else:
                report_filename = filename

            # Сохраняем результат
            try:
                result.to_json(report_filename, orient="records", indent=2, force_ascii=False)
                logger.info(f"Отчет сохранен в файл: {report_filename}")
            except Exception as e:
                logger.error(f"Ошибка сохранения отчета в файл {report_filename}: {e}")

            return result

        return wrapper  # type: ignore

    return decorator


@report_decorator()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Анализирует траты по категории за последние 3 месяца
    """
    logger.info(f"Анализ трат по категории '{category}'")

    try:
        # Определяем дату анализа
        if date is None:
            analysis_date = datetime.now()
        else:
            analysis_date = datetime.strptime(date, "%Y-%m-%d")

        # Вычисляем дату 3 месяца назад, но с первого дня месяца
        three_months_ago = (analysis_date.replace(day=1) - timedelta(days=90)).replace(day=1)

        # Конвертируем даты
        transactions["date"] = pd.to_datetime(transactions["date"])

        # Фильтруем по дате и категории
        mask = (
            (transactions["date"] >= three_months_ago)
            & (transactions["date"] <= analysis_date)
            & (transactions["category"] == category)
        )

        filtered_df = transactions[mask]

        if filtered_df.empty:
            logger.warning(f"Нет данных по категории '{category}' за последние 3 месяца")
            return pd.DataFrame()

        # Группируем по месяцам
        filtered_df = filtered_df.copy()
        filtered_df["year_month"] = filtered_df["date"].dt.to_period("M")
        monthly_spending = filtered_df.groupby("year_month")["amount"].sum().reset_index()
        monthly_spending["year_month"] = monthly_spending["year_month"].astype(str)

        logger.info(f"Найдено {len(monthly_spending)} месяцев с тратами по категории '{category}'")
        return monthly_spending

    except Exception as e:
        logger.error(f"Ошибка анализа трат по категории '{category}': {e}")
        return pd.DataFrame()


@report_decorator()
def spending_by_weekday(df: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Анализирует траты по дням недели
    """
    logger.info("Анализ трат по дням недели")

    try:
        if df.empty or "date" not in df.columns:
            return pd.DataFrame()

        # Конвертируем даты
        df["date"] = pd.to_datetime(df["date"])

        # Добавляем день недели (0-понедельник, 6-воскресенье)
        df = df.copy()
        df["weekday"] = df["date"].dt.dayofweek
        df["weekday_name"] = df["date"].dt.day_name()

        # Группируем по дням недели
        weekday_spending = df.groupby(["weekday", "weekday_name"])["amount"].agg(["sum", "count"]).reset_index()
        weekday_spending = weekday_spending.rename(columns={"sum": "total_amount", "count": "transactions_count"})

        # Сортируем по дню недели
        weekday_spending = weekday_spending.sort_values("weekday")

        logger.info(f"Проанализированы траты по {len(weekday_spending)} дням недели")
        return weekday_spending

    except Exception as e:
        logger.error(f"Ошибка анализа трат по дням недели: {e}")
        return pd.DataFrame()


@report_decorator()
def spending_by_workday(df: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Анализирует траты в рабочие/выходные дни по категории
    """
    logger.info(f"Анализ трат по категории '{category}' в рабочие/выходные дни")

    try:
        if df.empty or "date" not in df.columns:
            return pd.DataFrame()

        # Определяем дату анализа
        if date is None:
            analysis_date = datetime.now()
        else:
            analysis_date = datetime.strptime(date, "%Y-%m-%d")

        # Вычисляем дату 3 месяца назад
        three_months_ago = (analysis_date.replace(day=1) - timedelta(days=90)).replace(day=1)

        # Конвертируем даты и фильтруем
        df["date"] = pd.to_datetime(df["date"])
        mask = (df["date"] >= three_months_ago) & (df["date"] <= analysis_date) & (df["category"] == category)

        filtered_df = df[mask]

        if filtered_df.empty:
            logger.warning(f"Нет данных по категории '{category}' за последние 3 месяца")
            return pd.DataFrame()

        # Определяем рабочие/выходные (пн-пт рабочие, сб-вс выходные)
        filtered_df = filtered_df.copy()
        filtered_df["is_weekend"] = filtered_df["date"].dt.dayofweek >= 5
        filtered_df["day_type"] = filtered_df["is_weekend"].map({True: "выходной", False: "рабочий"})

        # Группируем по типу дня
        day_type_spending = filtered_df.groupby("day_type")["amount"].agg(["sum", "count", "mean"]).reset_index()
        day_type_spending = day_type_spending.rename(
            columns={"sum": "total_amount", "count": "transactions_count", "mean": "average_amount"}
        ).round(2)

        logger.info(f"Проанализированы траты по категории '{category}' по типам дней")
        return day_type_spending

    except Exception as e:
        logger.error(f"Ошибка анализа трат по типам дней: {e}")
        return pd.DataFrame()
