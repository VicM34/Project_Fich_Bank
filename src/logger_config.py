import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str, log_file: str, level: str = "INFO") -> logging.Logger:
    """
    Настраивает и возвращает логгер для модуля.
    """
    # Создаем папку logs если ее нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Полный путь к файлу лога
    log_path = log_dir / log_file

    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Форматтер для логов
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Обработчик для файла (перезаписывает файл при каждом запуске)
    file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(file_handler)

    # Отключаем propagation чтобы избежать дублирования
    logger.propagate = False

    return logger


# Создаем логгеры для каждого модуля
masks_logger = setup_logger("masks", "masks.log")
utils_logger = setup_logger("utils", "utils.log")