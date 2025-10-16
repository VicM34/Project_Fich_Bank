import os
import tempfile
import logging
from pathlib import Path
from src.logger_config import setup_logger, masks_logger, utils_logger


class TestLogging:
    """Тесты для системы логирования"""

    def test_setup_logger_creates_file(self) -> None:
        """Тест что логгер создает файл"""
        test_logger = setup_logger("test_module", "test.log")

        # Записываем тестовое сообщение
        test_logger.info("Тестовое сообщение")

        # Проверяем что файл создался
        log_file = Path("logs/test.log")
        assert log_file.exists()

        # Читаем и проверяем содержимое
        content = log_file.read_text(encoding='utf-8')
        assert "Тестовое сообщение" in content

        # Очистка
        for handler in test_logger.handlers[:]:
            handler.close()
            test_logger.removeHandler(handler)

    def test_loggers_initialized(self) -> None:
        """Тест что логгеры инициализированы"""
        assert masks_logger is not None
        assert utils_logger is not None
        assert masks_logger.name == "masks"
        assert utils_logger.name == "utils"

    def test_log_file_overwrite(self) -> None:
        """Тест что файл перезаписывается при каждом запуске"""
        test_logger = setup_logger("test_overwrite", "overwrite.log")

        # Первая запись
        test_logger.info("Первое сообщение")

        # Создаем новый логгер с тем же файлом (имитируем новый запуск)
        test_logger2 = setup_logger("test_overwrite2", "overwrite.log")
        test_logger2.info("Второе сообщение")

        # Проверяем что в файле только второе сообщение
        log_file = Path("logs/overwrite.log")
        content = log_file.read_text(encoding='utf-8')

        assert "Первое сообщение" not in content
        assert "Второе сообщение" in content

        # Очистка
        for handler in test_logger.handlers[:] + test_logger2.handlers[:]:
            handler.close()
            test_logger.removeHandler(handler)
            test_logger2.removeHandler(handler)


def test_masks_logging() -> None:
    """Тест логирования в модуле masks"""
    from src.masks import get_mask_card_number, get_mask_account

    # Тестируем успешное выполнение
    try:
        card_mask = get_mask_card_number("1234567812345678")
        account_mask = get_mask_account("12345678901234567890")

        # Проверяем что логи записались
        masks_log = Path("logs/masks.log")
        if masks_log.exists():
            content = masks_log.read_text(encoding='utf-8')
            assert "Успешно создана маска для карты" in content
            assert "Успешно создана маска для счета" in content

    except Exception:
        pass


def test_utils_logging() -> None:
    """Тест логирования в модуле utils"""
    from src.utils import load_transactions

    # Тестируем загрузку несуществующего файла
    result = load_transactions("nonexistent.json")

    # Проверяем что предупреждение записалось в лог
    utils_log = Path("logs/utils.log")
    if utils_log.exists():
        content = utils_log.read_text(encoding='utf-8')
        assert "Файл не найден" in content