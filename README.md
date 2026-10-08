# streamstats

Анализатор логов. Читает CSV и JSONL построчно, считает статистику, пишет отчёт в JSON.

## Установка

Python 3.10+.

pip install -e ".[dev]"

Ставит пакет в режиме разработки, тащит `pytest` и `ruff`.

## Форматы

### CSV

Первая строка — заголовок. Колонки: timestamp,level,source,message.

timestamp,level,source,message
2026-01-01T12:00:00Z,INFO,app,Server started
2026-01-01T12:05:00Z,ERROR,db,Connection timeout

### JSONL

Каждая строка — JSON. Пустые строки пропускаются.

{"timestamp": "2026-01-01T12:00:00Z", "level": "INFO", "source": "app", "message": "Server started"}
{"timestamp": "2026-01-01T12:05:00Z", "level": "ERROR", "source": "db", "message": "Connection timeout"}


## Событие

Четыре поля, все обязательные:

timestamp — ISO 8601, валидная дата
level — DEBUG, INFO, WARNING, ERROR, CRITICAL
source — непустая строка
message — строка, может быть пустой

Если чего-то нет или не прошло валидацию — событие невалидное.

## Запуск

python -m streamstats analyze INPUT [INPUT ...] --format csv|jsonl --output REPORT.json

INPUT — один или несколько файлов
--format — csv или jsonl (обязательно)
--output — куда сохранить отчёт (обязательно)
--skip-invalid — пропускать битые строки вместо остановки

Примеры:

# один CSV
python -m streamstats analyze events.csv --format csv --output report.json

# несколько JSONL
python -m streamstats analyze app.jsonl db.jsonl --format jsonl --output report.json

# пропускать битые строки
python -m streamstats analyze events.jsonl --format jsonl --skip-invalid --output report.json

## Ошибки

Без --skip-invalid обработка стопает на первой битой строке. В stderr пишется файл, номер строки и поле. Код возврата — 2.

С --skip-invalid битые строки пропускаются, в лог идёт WARNING на каждую. Сколько пропустили — в отчёте, в skipped_invalid. Код возврата — 0.

## Отчёт

{
  "total_events": 2,
  "level_counts": {"INFO": 1, "ERROR": 1},
  "source_counts": {"app": 1, "db": 1},
  "top_error_sources": [{"source": "db", "count": 1}],
  "first_timestamp": "2026-01-01 12:00:00+00:00",
  "last_timestamp": "2026-01-01 12:05:00+00:00",
  "skipped_invalid": 0
}

total_events — сколько событий обработали
level_counts — события по уровням
source_counts — события по источникам
top_error_sources — топ-5 источников с ERROR и CRITICAL
first_timestamp / last_timestamp — первая и последняя метка времени, null если пусто
skipped_invalid — сколько строк пропустили

## Память

Всё стримится через генераторы. События в памяти не копятся, аккумулятор хранит только счётчики. Потребление не зависит от размера файла — 500 МБ переварится с тем же объёмом, что и 5 МБ. read() и readlines() не используются.

## Тесты

python -m pytest

Парсеры, пустой файл, битые строки, несколько файлов, кириллица, CLI.

Проверка:

python -m pytest
ruff check .
python -m streamstats --help

