# chaosnexus-tuned/tests/unit/test_pipeline_utils.py
"""Unit tests for pure pipeline helpers (no GPU / torch)."""

from __future__ import annotations

import json
from pathlib import Path

from pipeline import config, utils


def test_read_write_jsonl_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    rows = [{"a": 1}, {"b": "two"}]
    utils.write_jsonl(str(path), rows)
    assert utils.read_jsonl(str(path)) == rows


def test_read_jsonl_missing_returns_empty(tmp_path: Path) -> None:
    assert utils.read_jsonl(str(tmp_path / "missing.jsonl")) == []


def test_read_write_json_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "obj.json"
    data = {"ok": True, "n": 3}
    utils.write_json(str(path), data)
    assert utils.read_json(str(path)) == data


def test_read_json_missing_returns_none(tmp_path: Path) -> None:
    assert utils.read_json(str(tmp_path / "nope.json")) is None


def test_get_files_globs_across_dirs(tmp_path: Path) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    (a / "one.jsonl").write_text("{}\n", encoding="utf-8")
    (b / "two.jsonl").write_text("{}\n", encoding="utf-8")
    (a / "skip.txt").write_text("x", encoding="utf-8")
    found = sorted(Path(p).name for p in utils.get_files([str(a), str(b)], "*.jsonl"))
    assert found == ["one.jsonl", "two.jsonl"]


def test_parse_diff_metadata_create_and_filters() -> None:
    action, path, valid = config.parse_diff_metadata(
        {"change_type": "A", "a_path": None, "b_path": "src/main.rs"}
    )
    assert action == "CREATE"
    assert path == "src/main.rs"
    assert valid is True

    action, path, valid = config.parse_diff_metadata(
        {"change_type": "M", "a_path": "pnpm-lock.yaml", "b_path": "pnpm-lock.yaml"}
    )
    assert action == "MODIFY"
    assert valid is False

    action, path, valid = config.parse_diff_metadata(
        {
            "change_type": "D",
            "a_path": "node_modules/pkg/index.js",
            "b_path": None,
        }
    )
    assert action == "DELETE"
    assert valid is False


def test_fix_concatenated_jsonl_objects(tmp_path: Path) -> None:
    """Inline the fix_jsonl transform without importing the module (it runs on import)."""
    path = tmp_path / "broken.jsonl"
    path.write_text(
        '{"messages":[{"role":"user","content":"a"}]}\\n{"messages":[{"role":"user","content":"b"}]}\\n',
        encoding="utf-8",
    )
    content = path.read_text(encoding="utf-8")
    fixed = content.replace('}\\n{"messages"', '}\n{"messages"')
    if fixed.endswith("\\n"):
        fixed = fixed[:-2] + "\n"
    path.write_text(fixed, encoding="utf-8")
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 2
    assert json.loads(lines[0])["messages"][0]["content"] == "a"
    assert json.loads(lines[1])["messages"][0]["content"] == "b"
