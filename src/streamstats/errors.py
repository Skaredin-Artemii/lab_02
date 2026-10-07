"""Ошибки пакета streamstats"""

from dataclasses import dataclass
from enum import Enum

class ErrorCode (str, Enum):
    """Коды ошибок"""

    CLI_CONFIG = "CLI_CONFIG"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    INVALID_EVENT = "INVALID_EVENT"
    INVALID_TIMESTAMP = "INVALID_TIMESTAMP"


@dataclass 
class ErrorContext:
    """Где именно произошла ошибка"""

    file: str | None = None
    line: int | None = None
    field: str | None = None

def __str__(self) -> str:
    """Собираем контекст в строку для сообщения ошибки"""
    parts = []
    if self.file:
        parts.append(f"файл: {self.file}")
    if self.line is not None:
        parts.append(f"строка: {self.line}")
    if self.field:
        parts.append(f"поле: '{self.field}'")
    return ", ".join(parts)


class StreamStatsError(Exception):
    """Общая ошибка пакета"""


    def __init__(
            self,
            code: ErrorCode,
            message: str,
            context: ErrorContext | None = None,
    ) -> None:
        self.code = code 
        self.message = message
        self.context = context
        super().__init__(message)

    def __str__(self) -> str:
        """Красивое представление ошибки: код и контекст"""
        base = f"[{self.code.value}] {self.message}"
        if self.context:
            return f"{base} ({self.context})"
        return base

    
def cli_config(message: str) -> StreamStatsError:
    """Создать ошибку неправильных аргументов CLI"""
    return StreamStatsError(ErrorCode.CLI_CONFIG, message)


def unsupported_format(fmt: str) -> StreamStatsError:
    """Ошибка неподдерживаемого формата файла"""
    return StreamStatsError(
        ErrorCode.UNSUPPORTED_FORMAT,
        f"Формат '{fmt}' не поддерживается",
    )


def invalid_event(
        message: str,
        *,
        file: str | None = None,
        line: int | None = None,
        field: str | None = None,
) -> StreamStatsError:
    """Ошибка неверного события"""
    return StreamStatsError(
        ErrorCode.INVALID_EVENT,
        message,
        ErrorContext(file=file, line=line, field=field)
    )


def invalid_timestamp(
        message: str,
        *,
        file: str | None = None,
        line: int | None = None,
) -> StreamStatsError:
    """Ошибка неправильной даты"""
    return StreamStatsError(
        ErrorCode.INVALID_TIMESTAMP,
        message,
        ErrorContext(file=file,line=line,field="timestamp"),
    )

    
    

