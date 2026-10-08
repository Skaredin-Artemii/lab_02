"""Формирование JSON-отчёта"""

import json


def build_report(acc):
    """Собираем отчет"""

    level_counts = {}
    for level in acc.level_counts:
        level_counts[level.value] = acc.level_counts[level]

    """Топ источников ошибок"""

    top = []
    for src, count in acc.get_top_error_sources(5):
        top.append({"source": src, "count": count})

    return {
        "total_events": acc.total_events,
        "level_counts": level_counts,
        "source_counts": dict(acc.source_counts),
        "top_error_sources": top,
        "first_timestamp": str(acc.first_timestamp) if acc.first_timestamp else None,
        "last_timestamp": str(acc.last_timestamp) if acc.last_timestamp else None,
        "skipped_invalid": acc.skipped_invalid,
    }


def write_json_report(report, output_path):
    """Записывает словарь в JSON-файл"""

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


