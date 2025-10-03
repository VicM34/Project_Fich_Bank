import datetime
from functools import wraps
from typing import Any, Callable, Optional


def log(filename: Optional[str] = None) -> Callable:
    """Декоратор для логирования выполнения функций"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Получаем текущее время
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            func_name = func.__name__

            # Формируем информацию о входных параметрах
            args_str = ", ".join([repr(arg) for arg in args])
            kwargs_str = ", ".join([f"{key}={repr(value)}" for key, value in kwargs.items()])
            all_args = ", ".join(filter(None, [args_str, kwargs_str]))

            try:
                # Логируем начало выполнения
                start_message = f"{current_time} - {func_name} - начало выполнения"
                if all_args:
                    start_message += f" - args: {all_args}"

                _write_log(start_message, filename)

                # Выполняем функцию
                result = func(*args, **kwargs)

                # Логируем успешное завершение
                success_message = f"{current_time} - {func_name} - успешно завершена - результат: {repr(result)}"
                _write_log(success_message, filename)

                return result

            except Exception as e:
                # Логируем ошибку
                error_message = (
                    f"{current_time} - {func_name} - ошибка: {type(e).__name__}: {str(e)}" f" - args: {all_args}"
                )
                _write_log(error_message, filename)
                raise

        return wrapper

    return decorator


def _write_log(message: str, filename: Optional[str] = None) -> None:
    """Вспомогательная функция для записи лога в файл или консоль"""
    if filename:
        with open(filename, "a", encoding="utf-8") as file:
            file.write(message + "\n")
    else:
        print(message)
