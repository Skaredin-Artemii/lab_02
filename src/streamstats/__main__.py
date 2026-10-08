"""Точка входа CLI"""

import argparse
import logging
import sys

from.analysis import StatsAccumulator
from .errors import StreamStatsError
from .parsers import stream_events
from .report import build_report, write_json_report

def main():
    """Разбираем аргументы, обрабатывает файлы, пишет отчёт"""

    parser = argparse.ArgumentParser(
        prog = "streastats",
        description = "Потоковый анализатор файлов (CSV и JSONL)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Анализировать файлы")
    analyze.add_argument("inputs", nargs="+", help="Входные файлы")
    analyze.add_argument("--format", choices=["csv", "jsonl"], required=True)
    analyze.add_argument("--output", required=True, help="Куда сохранить отчёт")
    analyze.add_argument("--skip-invalid", action="store_true")

    args = parser.parse_args()

    """Настройка логирования"""

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    """Запуск обработки"""

    try:
        acc= StatsAccumulator()

        for event in stream_events(args.inputs, args.format, args.skip_invalid):
            acc.update(event)

        report = build_report(acc)
        write_json_report(report, args.output)
        logging.info("Отчет записан в %s", args.output)
        return 0
    except StreamStatsError as e:
        logging.error("Ошибка: %s", e)
        return 2

if __name__=="__main__":
    sys.exit(main())   
