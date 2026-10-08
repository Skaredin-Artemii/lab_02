"""Подсчет статистики"""

from collections import defaultdict

from .models import Level


class StatsAccumulator:
    """Считает статистику, не храня события в памяти"""

    def __init__(self):
        self.total_events = 0
        self.level_counts = defaultdict(int)
        self.source_counts = defaultdict(int)
        self.error_source_count = defaultdict(int)
        self.first_timestamp = None
        self.last_timestamp = None
        self.skipped_invalid = 0

    def update(self, event):
        self.total_events += 1
        self.level_counts[event.level] += 1
        self.source_counts[event.source] += 1

        if event.level in (Level.ERROR, Level.CRITICAL):
            self.error_source_count[event.source] += 1

        ts = event.timestamp
        if self.first_timestamp is None or ts < self.first_timestamp:
            self.first_timestamp = ts
        if self.last_timestamp is None or ts > self.last_timestamp:
            self.last_timestamp = ts

    def mark_skipped(self):
        self.skipped_invalid += 1

    def get_top_error_sources(self, n=5):
        items = sorted(
            self.error_source_count.items(),
            key=lambda pair: (-pair[1], pair[0]),
        )
        return items[:n]