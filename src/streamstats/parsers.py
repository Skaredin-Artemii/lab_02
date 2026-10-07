"""Парсеры для CSV и JSONL"""

from csv import DictReader
from json import JSONDecodeError, loads
from logging import getLogger

from .errors import InvalidEventError, UnsupportedFormatError
from .models import create_event

logger = getLogger(__name__)

def parse_csv(file_path, skip_invalid=False):
    """Считываем файл csv"""

    with open(file_path, "r", encoding="utf-8", newline="") as f:
        reader = DictReader(f)
        for row in reader:
            try:
                event = create_event(row, file=file_path, line=reader.line_num)
                yield event
            except InvalidEventError:
                if skip_invalid:
                    logger.warning(f"Пропущена строка {reader.line_num}")
                    continue
                else:
                    raise

def parse_jsonl(file_path, skip_invalid=False):
    """Считываем файл jsonl"""
    with open(file_path, "r", encoding="utf-8") as f:
        line_num = 0
        for line in f:
            line_num += 1
            if line.strip() == "":
                continue
            try:
                data = loads(line)
                event = create_event(data, file=file_path, line=line_num)
                yield event
            except JSONDecodeError:
                if skip_invalid:
                    logger.warning(f"Строка {line_num}: плохой JSON")
                    continue
                else:
                    raise InvalidEventError("Невалидный JSON", file=file_path, line=line_num)

def stream_events(file_paths, format_type, skip_invalid=False):
    if format_type == "csv":
        parser = parse_csv
    elif format_type == "jsonl":
        parser = parse_jsonl
    else:
        raise UnsupportedFormatError(format_type)
    for path in file_paths:
        for event in parser(path, skip_invalid):
            yield event
    
