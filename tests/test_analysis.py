"""Тесты для аккумулятора статистики"""

from datetime import datetime, timezone

import pytest

from streamstats.analysis import StatsAccumulator
from streamstats.models import Event, Level


def make_event(ts, level, source, message="msg"):
    return Event(
        timestamp=datetime.fromisoformat(ts).replace(tzinfo=timezone.utc),
        level=Level(level),
        source=source,
        message=message,
    )


def test_empty_accumulator():
    acc = StatsAccumulator()

    assert acc.total_events == 0
    assert dict(acc.level_counts) == {}
    assert dict(acc.source_counts) == {}
    assert acc.first_timestamp is None
    assert acc.last_timestamp is None
    assert acc.skipped_invalid == 0


def test_total_events_counts_all():
    acc = StatsAccumulator()
    acc.update(make_event("2026-11-11T10:10:10", "INFO", "app"))
    acc.update(make_event("2026-12-12T11:11:11", "ERROR", "db"))
    acc.update(make_event("2026-01-21T15:15:15", "DEBUG", "app"))

    assert acc.total_events == 3


def test_level_counts():
    acc = StatsAccumulator()
    acc.update(make_event("2026-02-22T01:02:03", "INFO", "app"))
    acc.update(make_event("2026-03-23T04:05:06", "INFO", "db"))
    acc.update(make_event("2026-04-24T07:08:09", "ERROR", "app"))

    assert acc.level_counts[Level.INFO] == 2
    assert acc.level_counts[Level.ERROR] == 1


def test_source_counts():
    acc = StatsAccumulator()
    acc.update(make_event("2026-05-25T10:11:12", "INFO", "app"))
    acc.update(make_event("2026-06-26T13:14:15", "ERROR", "db"))
    acc.update(make_event("2026-07-27T16:17:18", "ERROR", "db"))

    assert acc.source_counts["app"] == 1
    assert acc.source_counts["db"] == 2


def test_error_source_counts_only_errors():
    acc = StatsAccumulator()
    acc.update(make_event("2026-08-28T19:20:21", "INFO", "app"))
    acc.update(make_event("2026-09-29T22:23:24", "ERROR", "db"))
    acc.update(make_event("2026-10-30T01:25:26", "CRITICAL", "db"))
    acc.update(make_event("2026-11-01T02:26:27", "WARNING", "cache"))

    assert acc.error_source_count["db"] == 2
    assert "app" not in acc.error_source_count
    assert "cache" not in acc.error_source_count


def test_top_error_sources_returs_top_n():
    acc = StatsAccumulator()

    for _ in range(3):
        acc.update(make_event("2026-12-02T03:28:29", "ERROR", "db"))
    for _ in range(2):
        acc.update(make_event("2026-01-03T04:30:31", "ERROR", "auth"))
    acc.update(make_event("2026-02-04T05:32:33", "CRITICAL", "cache"))

    top = acc.get_top_error_sources(2)
    assert top == [("db", 3), ("auth", 2)]


@pytest.mark.parametrize("order", [["a", "b"], ["b", "a"]])
def test_top_error_sources_is_deterministic(order):
    acc = StatsAccumulator()
    for src in order:
        acc.update(make_event("2026-03-05T06:34:35", "ERROR", src))

    top = acc.get_top_error_sources(5)

    assert top == [("a", 1), ("b", 1)]


def test_first_and_last_timestamps():
    acc = StatsAccumulator()
    acc.update(make_event("2026-04-09T07:36:37", "INFO", "app"))
    acc.update(make_event("2026-05-10T08:38:39", "INFO", "app"))
    acc.update(make_event("2026-06-11T09:40:41", "INFO", "app"))

    assert acc.first_timestamp.year == 2026
    assert acc.first_timestamp.month == 4
    assert acc.first_timestamp.day == 9
    assert acc.last_timestamp.day == 11


def test_mark_skipped_increments():
    acc = StatsAccumulator()

    acc.mark_skipped()
    acc.mark_skipped()
    acc.mark_skipped()

    assert acc.skipped_invalid == 3