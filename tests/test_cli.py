"""Тесты CLI"""

import json
import subprocess
import sys

import pytest


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "streamstats", *args],
        capture_output=True,
        text=True,
    )


def test_cli_help_works():
    result = run_cli("--help")
    assert result.returncode == 0
    assert "streamstats" in result.stdout


def test_cli_analyze_help_works():
    result = run_cli("analyze", "--help")
    assert result.returncode == 0
    assert "--format" in result.stdout
    assert "--output" in result.stdout


def test_cli_success_jsonl(tmp_path):
    inp = tmp_path / "in.jsonl"
    inp.write_text(
        '{"timestamp":"2026-01-30T13:14:15Z","level":"INFO","source":"app","message":"hi"}\n'
        '{"timestamp":"2026-02-28T16:17:18Z","level":"ERROR","source":"db","message":"fail"}',
        encoding="utf-8",
    )
    out = tmp_path / "report.json"

    result = run_cli("analyze", str(inp), "--format", "jsonl", "--output", str(out))

    assert result.returncode == 0
    assert out.exists()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["total_events"] == 2
    assert data["level_counts"]["INFO"] == 1
    assert data["level_counts"]["ERROR"] == 1
    assert data["source_counts"]["app"] == 1
    assert data["source_counts"]["db"] == 1
    assert data["top_error_sources"] == [{"source": "db", "count": 1}]


def test_cli_strict_mode_fails(tmp_path):
    inp = tmp_path / "bad.jsonl"
    inp.write_text("{bad json}", encoding="utf-8")
    out = tmp_path / "report.json"

    result = run_cli("analyze", str(inp), "--format", "jsonl", "--output", str(out))

    assert result.returncode == 2
    assert not out.exists()


def test_cli_reports_line_number(tmp_path):
    inp = tmp_path / "bad.jsonl"
    inp.write_text(
        '{"timestamp":"2026-05-06T11:22:33Z","level":"INFO","source":"app","message":"ok"}\n'
        "{bad}\n",
        encoding="utf-8",
    )
    out = tmp_path / "report.json"

    result = run_cli("analyze", str(inp), "--format", "jsonl", "--output", str(out))

    assert result.returncode == 2
    assert "строка: 2" in result.stderr


def test_cli_skip_invalid(tmp_path):
    inp = tmp_path / "mixed.jsonl"
    inp.write_text(
        "{bad}\n"
        '{"timestamp":"2026-10-11T13:15:17Z","level":"INFO","source":"app","message":"ok"}',
        encoding="utf-8",
    )
    out = tmp_path / "report.json"

    result = run_cli(
        "analyze", str(inp),
        "--format", "jsonl",
        "--output", str(out),
        "--skip-invalid",
    )

    assert result.returncode == 0
    assert out.exists()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["total_events"] == 1
    assert data["skipped_invalid"] == 1


def test_cli_multiple_files(tmp_path):
    f1 = tmp_path / "a.jsonl"
    f2 = tmp_path / "b.jsonl"
    f1.write_text(
        '{"timestamp":"2026-11-19T17:46:52Z","level":"INFO","source":"app","message":"1"}',
        encoding="utf-8",
    )
    f2.write_text(
        '{"timestamp":"2026-10-20T15:57:51Z","level":"ERROR","source":"db","message":"2"}',
        encoding="utf-8",
    )
    out = tmp_path / "report.json"

    result = run_cli("analyze", str(f1), str(f2), "--format", "jsonl", "--output", str(out))

    assert result.returncode == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["total_events"] == 2


def test_cli_empty_file(tmp_path):
    inp = tmp_path / "empty.jsonl"
    inp.write_text("", encoding="utf-8")
    out = tmp_path / "report.json"

    result = run_cli("analyze", str(inp), "--format", "jsonl", "--output", str(out))

    assert result.returncode == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["total_events"] == 0
    assert data["first_timestamp"] is None
    assert data["last_timestamp"] is None


def test_cli_unicode_in_report(tmp_path):
    inp = tmp_path / "u.jsonl"
    inp.write_text(
        '{"timestamp":"2026-09-07T23:59:59Z","level":"INFO","source":"приложение","message":"Привет"}',
        encoding="utf-8",
    )
    out = tmp_path / "report.json"

    run_cli("analyze", str(inp), "--format", "jsonl", "--output", str(out))

    text = out.read_text(encoding="utf-8")
    assert "приложение" in text
    assert "\\u" not in text


def test_cli_input_file_not_modified(tmp_path):
    inp = tmp_path / "in.jsonl"
    content = '{"timestamp":"2026-05-20T13:17:21Z","level":"INFO","source":"app","message":"ok"}'
    inp.write_text(content, encoding="utf-8")
    out = tmp_path / "report.json"

    run_cli("analyze", str(inp), "--format", "jsonl", "--output", str(out))

    assert inp.read_text(encoding="utf-8") == content


@pytest.mark.parametrize(
    "fmt,content",
    [
        (
            "csv",
            "timestamp,level,source,message\n"
            "2026-11-22T13:12:11Z,INFO,app,hi",
        ),
        (
            "jsonl",
            '{"timestamp":"2026-10-20T12:15:18Z","level":"INFO","source":"app","message":"hi"}',
        ),
    ],
)
def test_cli_equivalent_formats(tmp_path, fmt, content):
    inp = tmp_path / f"in.{fmt}"
    inp.write_text(content, encoding="utf-8")
    out = tmp_path / "report.json"

    result = run_cli("analyze", str(inp), "--format", fmt, "--output", str(out))

    assert result.returncode == 0

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["total_events"] == 1
    assert data["source_counts"] == {"app": 1}