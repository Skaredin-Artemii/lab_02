"""Ошибки пакета streamstats"""


class StreamStatsError(Exception):
    """Базовая ошибка пакета"""


class CliConfigError(StreamStatsError):
    def __init__(self, message: str) -> None:
        super().__init__(f"Ошибка конфигурации CLI: {message}")


class UnsupportedFormatError(StreamStatsError):
    def __init__(self, fmt: str) -> None:
        self.fmt = fmt
        super().__init__(f"Формат '{fmt}' не поддерживается")


class InvalidEventError(StreamStatsError):
    def __init__(
            self,
            message: str,
            *,
            file: str | None = None,
            line: str | None = None,
            field: str | None = None,
    ) -> None:
        self.file = file
        self.line = line
        self.field = field
        super().__init__(self._with_context(message))

    def _with_context(self, message: str) -> str:
        parts = []
        if self.file:
            parts.append(f"файл: {self.file}")
        if self.line is not None:
            parts.append(f"строка: {self.line}")
        if self.field:
            parts.append(f"поле: '{self.field}'")
        if parts:
            return f"{message} ({', '.join(parts)})"
        return message


class InvalidTimestampError(InvalidEventError):
    def __init__(
            self,
            message: str,
            *,
            file: str | None = None,
            line: str | None = None,
    ) -> None:
        super().__init__(message, file=file, line=line, field="timestamp")