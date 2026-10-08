"""Тесты для парсеров"""

import pytest

from streamstats.parsers import parse_csv, parse_jsonl
from streamstats.errors import InvalidEventError, InvalidTimestampError


def test_parse_csv_valid(tmp_path):
    """Arrange: готовим файл c валидной строкой"""

    file = tmp_path / "test.csv"
    file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-10T08:08:08Z,INFO,app,Hello",
        encoding="utf-8",
    )

    "Act: читаем события"

    events = list(parse_csv(str(file)))

    """Assert: проверка результата"""

    assert len(events) == 1
    assert events[0].level == "INFO"
    assert events[0].source == "app"
    assert events[0].message == "Hello"

def test_parse_csv_empty_file(tmp_path):

    """Arrange"""

    file = tmp_path / "empty.csv"
    file.write_text("", encoding="utf-8")

    """Act"""

    events = list(parse_csv(str(file)))

    """Assert"""

    assert events == []

def test_parse_csv_unicode(tmp_path):
    file = tmp_path / "unicode.csv"
    file.write_text(
        "timstamp,level,source,message\n"
        "2026-09-09T07:07:07Z,INFO,приложение,Привет мир",
        encoding="utf-8",
    )
    events = list(parse_csv(str(file)))
    assert events[0].source == "приложение"
    assert events[0].message == "Привет мир"

def test_parse_jsonl_valid(tmp_path):
    file = tmp_path / "test.jsonl"
    file.write_text(
        '{"timestamp":"2026-08-08T06:06:06Z","level":"INFO","source":"app","message":"Hello"}',
        encoding="utf-8",
    )
    events = list(parse_jsonl(str(file)))
    assert len(events) == 1
    assert events[0].level == "INFO" 
    assert events[0].source == "app"

def test_parse_jsonl_bad_json_reports_line(tmp_path):
    file = tmp_path / "test.jsonl"
    good = '{"timestamp":"2026-07-07T05:05:05Z","level":"INFO","source":"app","message":"ok"}'
    lines = [good] * 6 + ["{bad json}"]
    file.write_text("\n".join(lines), encoding="utf-8")

    with pytest.raises(InvalidEventError) as exc_info:
        list(parse_jsonl(str(file)))

    assert "строка: 7" in str(exc_info.value)

def test_parse_jsonl_invalid_timestamp(tmp_path):
    file = tmp_path / "bad_ts.jsonl"
    file.write_text(
        '{"timestamp":"not-a-date","level":"INFO","source":"app","message":"ok"}',
        encoding="utf-8",
    )
    with pytest.raises(InvalidTimestampError) as exc_info:
        list(parse_jsonl(str(file)))
    assert exc_info.value.field == "timestamp"
    assert exc_info.value.line == 1

@pytest.mark.parametrize(
    "raw",
    [
        '{"level":"INFO","source":"app","message":"ok"}',
        '{"timestamp":"2026-06-06T04:04:04Z","source":"app","message":"ok"}',
        '{"timestamp":"2026-05-05T03:03:03Z","level":"INFO","message":"ok"}',
        '{"timestamp":"2026-04-04T02:02:02Z","level":"INFO","source":"app"}',
        '{"timestamp":"2026-03-03T01:01:01Z","level":"NOPE","source":"app","message":"ok"}',
        '{"timestamp":"2026-02-02T00:00:00Z","level":"INFO","source":"","message":"ok"}',
    ], 
)
def test_parse_jsonl_invalid_rows(tmp_path, raw):
    file = tmp_path / "bad.jsonl"
    file.write_text(raw, encoding="utf-8")
    with pytest.raises(InvalidEventError):
        list(parse_jsonl(str(file)))

def test_skip_invalid_continues(tmp_path, caplog):
    file = tmp_path / "mixed.jsonl"
    file.write_text(
        '{bad json}\n'
        '{"timestamp":"2026-01-01T12:12:12Z","level":"INFO","source":"app","message":"ok"}',
        encoding="utf-8",
    )
    events = list(parse_jsonl(str(file), skip_invalid=True))
    assert len(events) == 1
    assert events[0].source == "app"
    assert any("Пропущена" in r.message for r in caplog.records)
    


