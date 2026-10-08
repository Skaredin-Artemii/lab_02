"""Парсеры для CSV и JSONL"""

from csv import DictReader
from json import JSONDecodeError, loads
from logging import getLogger

from .errors import InvalidEventError, UnsupportedFormatError
from .models import create_event

logger = getLogger(__name__)


def parse_csv(file_path, skip_invalid=False, on_skip=None):
    with open(file_path, encoding="utf-8-sig", newline="") as f:
        reader = DictReader(f)
        for row in reader:
            try:
                yield create_event(row, file=file_path, line=reader.line_num)
            except InvalidEventError as e:
                if not skip_invalid:
                    raise
                logger.warning(f"Строка {reader.line_num}: {e}")
                if on_skip:
                    on_skip()


def parse_jsonl(file_path, skip_invalid=False, on_skip=None):
    with open(file_path, encoding="utf-8-sig") as f:
        for line_num, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                data = loads(line)
                yield create_event(data, file=file_path, line=line_num)
            except JSONDecodeError:
                if not skip_invalid:
                    raise InvalidEventError(
                        "Невалидный JSON", file=file_path, line=line_num
                    )
                logger.warning(f"Строка {line_num}: плохой JSON")
                if on_skip:
                    on_skip()
            except InvalidEventError as e:
                if not skip_invalid:
                    raise
                logger.warning(f"Строка {line_num}: {e}")
                if on_skip:
                    on_skip()


def stream_events(file_paths, format_type, skip_invalid=False, on_skip=None):
    if format_type == "csv":
        parser = parse_csv
    elif format_type == "jsonl":
        parser = parse_jsonl
    else:
        raise UnsupportedFormatError(format_type)

    for path in file_paths:
        yield from parser(path, skip_invalid, on_skip)