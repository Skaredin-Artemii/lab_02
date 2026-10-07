"""Модель события и валидация"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from .errors import InvalidEventError, InvalidTimestampError


class Level(str, Enum):
    """Уровни события"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class Event:
    """Одно событие из лога"""

    timestamp: datetime
    level: Level
    source: str
    message: str

def create_event(raw: dict, file=None, line=None) -> Event:
    """Проверяет словарь и возвращает Event или ошибку"""

    for field in ["timestamp", "level", "source", "message"]:
        if field not in raw:
            raise InvalidEventError(
                f"Отсутствует поле '{field}'", file=file, line=line, field=field
            )

    ts = raw["timestamp"]
    if not isinstance(ts, str) or not ts.strip():
        raise InvalidTimestampError(
            "Timestamp должен быть непустой строкой", file=file, line=line
        )    
    try:
        ts_clean = ts.strip().replace("Z", "+00:00")
        parsed_ts = datetime.fromisoformat(ts_clean)
    except ValueError:
        raise InvalidEventError(
            "Неверный формат даты", file=file, line=line
        )
    if parsed_ts.tzinfo is None:
        parsed_ts = parsed_ts.replace(tzinfo=timezone.utc)

    lvl = raw["level"]
    try:
        parsed_level =Level(lvl)
    except (ValueError, TypeError):
        raise InvalidEventError(
            "Недопустимый level", file=file, line=line, field="level"
        )

    src = raw["source"]
    if not isinstance(src, str) or not src.strip():
        raise InvalidEventError(
            "Source должен быть непустой строкой", file=file, line=line, field="source"
        )    

    msg =raw["message"]
    if not isinstance(msg,str):
        raise InvalidEventError(
            "Message должен быть строкой", file=file, line=line, field="message"
        )

    return Event(parsed_ts, parsed_level, src.strip(), msg)
    



