#!/usr/bin/env python3
"""KRM TSVファイル群のクロステーブル整合性・ID書式・重複を検証する。

検証対象は krm_main.tsv / krm_notes.tsv / krm_wakun.tsv /
krm_pronunciations.tsv / krm_headword_chars.tsv。
このスクリプトはデータを一切変更しない（読み取り専用）。

終了コード:
    0 - エラーなし（警告のみ、または問題なし）
    1 - エラーあり
"""
import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

ENTRY_ID_RE = re.compile(r"^F\d{5}[a-z]?$")
HANZI_ID_RE = re.compile(r"^S\d{5}[a-z]?$")
DEF_SEQ_ID_RE = re.compile(r"^F\d{5}[a-z]?_\d{2}$")
WAKUN_PRON_ID_RE = re.compile(r"^F\d{5}[a-z]?_\d{2}[a-z]*$")
KAZAMA_RE = re.compile(r"^K\d{8}$")
TENRI_RE = re.compile(r"^T[abc]\d{6}$")

# ファイル名 -> {id_patterns: {列名: 正規表現}, pk: 主キー列名}
FILES = {
    "krm_main.tsv": {
        "id_patterns": {
            "entry_id": ENTRY_ID_RE,
            "hanzi_id": HANZI_ID_RE,
            "kazama_location": KAZAMA_RE,
            "tenri_location": TENRI_RE,
        },
        "pk": "entry_id",
    },
    "krm_notes.tsv": {
        "id_patterns": {
            "entry_id": ENTRY_ID_RE,
            "definition_seq_id": DEF_SEQ_ID_RE,
            "kazama_location": KAZAMA_RE,
            "tenri_location": TENRI_RE,
        },
        "pk": "definition_seq_id",
    },
    "krm_wakun.tsv": {
        "id_patterns": {
            "wakun_id": WAKUN_PRON_ID_RE,
            "definition_seq_id": DEF_SEQ_ID_RE,
            "kazama_location": KAZAMA_RE,
        },
        "pk": "wakun_id",
    },
    "krm_pronunciations.tsv": {
        "id_patterns": {
            "pronunciation_id": WAKUN_PRON_ID_RE,
            "definition_seq_id": DEF_SEQ_ID_RE,
        },
        "pk": "pronunciation_id",
    },
    "krm_headword_chars.tsv": {
        "id_patterns": {
            "hanzi_id": HANZI_ID_RE,
            "entry_id": ENTRY_ID_RE,
            "kazama_location_id": KAZAMA_RE,
            "tenri_location_id": TENRI_RE,
        },
        "pk": "hanzi_id",
    },
}

CHECK_NAMES = ["column_count", "id_format", "duplicate_pk", "fk", "type_code"]

MAX_EXAMPLES = 20


class Finding:
    __slots__ = ("severity", "check", "file", "line", "message")

    def __init__(self, severity, check, file, line, message):
        self.severity = severity
        self.check = check
        self.file = file
        self.line = line
        self.message = message

    def to_dict(self):
        return {
            "severity": self.severity,
            "check": self.check,
            "file": self.file,
            "line": self.line,
            "message": self.message,
        }


def load_tsv(path: Path):
    """(header, rows, malformed) を返す。rows は [(record_no, dict), ...]。

    一部の列（remarks等）は値の中に改行やタブを含み、"..." で囲むCSV形式の
    引用が使われているため、単純な行split ではなく csv モジュールで解釈する
    （scripts/update_pronunciation.py の read_tsv() と同じ方式）。
    record_no は元ファイルの行番号ではなく、データ部分での通し番号。
    """
    all_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    data_lines = [line for line in all_lines if not line.startswith("#")]

    reader = csv.reader(data_lines, delimiter="\t")
    try:
        header = next(reader)
    except StopIteration:
        return [], [], []

    rows = []
    malformed = []
    for record_no, fields in enumerate(reader, start=1):
        if not fields or fields == [""]:
            continue
        if len(fields) != len(header):
            malformed.append((record_no, len(fields)))
            continue
        rows.append((record_no, dict(zip(header, fields))))
    return header, rows, malformed


def check_column_count(name, header, malformed, findings):
    for lineno, count in malformed:
        findings.append(Finding(
            "error", "column_count", name, lineno,
            f"列数が {len(header)} 列であるべきところ {count} 列でした",
        ))


def check_id_format(name, rows, id_patterns, findings):
    for lineno, row in rows:
        for column, pattern in id_patterns.items():
            value = row.get(column, "")
            if not pattern.match(value):
                findings.append(Finding(
                    "error", "id_format", name, lineno,
                    f"{column}={value!r} が期待される書式（{pattern.pattern}）に一致しません",
                ))


def check_duplicate_pk(name, rows, pk, findings):
    seen = defaultdict(list)
    for lineno, row in rows:
        seen[row.get(pk, "")].append(lineno)
    for value, linenos in seen.items():
        if len(linenos) > 1:
            findings.append(Finding(
                "error", "duplicate_pk", name, linenos[0],
                f"{pk}={value!r} が {len(linenos)} レコードに重複しています（レコード#: {linenos}）",
            ))


def check_fk(source_name, source_rows, source_column, target_name, target_ids, findings):
    for lineno, row in source_rows:
        value = row.get(source_column, "")
        if value not in target_ids:
            findings.append(Finding(
                "error", "fk", source_name, lineno,
                f"{source_column}={value!r} が {target_name} に存在しません",
            ))


def check_notes_headword_completeness(main_ids, notes_rows, findings):
    headword_entry_ids = {
        row["entry_id"] for _, row in notes_rows
        if row.get("definition_seq_id", "").endswith("_00")
    }
    missing = main_ids - headword_entry_ids
    for entry_id in sorted(missing):
        findings.append(Finding(
            "error", "fk", "krm_notes.tsv", None,
            f"entry_id={entry_id!r} の見出し（_00）行が krm_notes.tsv にありません",
        ))


def check_type_code_consistency(notes_rows, findings):
    code_to_names = defaultdict(set)
    code_first_line = {}
    for lineno, row in notes_rows:
        code = row.get("definition_type_code", "")
        name = row.get("definition_type_name", "")
        if not code:
            continue
        code_to_names[code].add(name)
        code_first_line.setdefault(code, lineno)
    for code, names in sorted(code_to_names.items()):
        if len(names) > 1:
            findings.append(Finding(
                "warning", "type_code", "krm_notes.tsv", code_first_line[code],
                f"definition_type_code={code!r} が複数の definition_type_name に対応しています: {sorted(names)}",
            ))


def run(target_files, only_checks):
    loaded = {}
    for name in FILES:
        path = REPO_ROOT / name
        if not path.exists():
            continue
        header, rows, malformed = load_tsv(path)
        loaded[name] = {"header": header, "rows": rows, "malformed": malformed}

    findings = []

    for name in target_files:
        if name not in loaded:
            continue
        data = loaded[name]
        if "column_count" in only_checks:
            check_column_count(name, data["header"], data["malformed"], findings)
        if "id_format" in only_checks:
            check_id_format(name, data["rows"], FILES[name]["id_patterns"], findings)
        if "duplicate_pk" in only_checks:
            check_duplicate_pk(name, data["rows"], FILES[name]["pk"], findings)

    if "fk" in only_checks:
        main_ids = {row["entry_id"] for _, row in loaded.get("krm_main.tsv", {}).get("rows", [])}
        notes_seq_ids = {row["definition_seq_id"] for _, row in loaded.get("krm_notes.tsv", {}).get("rows", [])}

        if "krm_notes.tsv" in target_files and "krm_notes.tsv" in loaded:
            check_fk("krm_notes.tsv", loaded["krm_notes.tsv"]["rows"], "entry_id",
                      "krm_main.tsv", main_ids, findings)
        if "krm_main.tsv" in target_files and "krm_notes.tsv" in loaded:
            check_notes_headword_completeness(main_ids, loaded["krm_notes.tsv"]["rows"], findings)
        if "krm_wakun.tsv" in target_files and "krm_wakun.tsv" in loaded:
            check_fk("krm_wakun.tsv", loaded["krm_wakun.tsv"]["rows"], "definition_seq_id",
                      "krm_notes.tsv", notes_seq_ids, findings)
        if "krm_pronunciations.tsv" in target_files and "krm_pronunciations.tsv" in loaded:
            check_fk("krm_pronunciations.tsv", loaded["krm_pronunciations.tsv"]["rows"], "definition_seq_id",
                      "krm_notes.tsv", notes_seq_ids, findings)
        if "krm_headword_chars.tsv" in target_files and "krm_headword_chars.tsv" in loaded:
            check_fk("krm_headword_chars.tsv", loaded["krm_headword_chars.tsv"]["rows"], "entry_id",
                      "krm_main.tsv", main_ids, findings)

    if "type_code" in only_checks and "krm_notes.tsv" in target_files and "krm_notes.tsv" in loaded:
        check_type_code_consistency(loaded["krm_notes.tsv"]["rows"], findings)

    return findings


def print_report(findings):
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    def print_group(items, label):
        if not items:
            return
        by_check = defaultdict(list)
        for item in items:
            by_check[item.check].append(item)
        print(f"\n=== {label}: {len(items)}件 ===")
        for check, group in by_check.items():
            print(f"\n[{check}] {len(group)}件")
            for item in group[:MAX_EXAMPLES]:
                loc = f"{item.file} (レコード#{item.line})" if item.line else item.file
                print(f"  {loc}: {item.message}")
            if len(group) > MAX_EXAMPLES:
                print(f"  ...ほか {len(group) - MAX_EXAMPLES} 件")

    print_group(errors, "エラー")
    print_group(warnings, "警告")

    print()
    if not findings:
        print("問題は見つかりませんでした。")
    else:
        print(f"合計: エラー {len(errors)}件 / 警告 {len(warnings)}件")


def main():
    parser = argparse.ArgumentParser(
        description="KRM TSVファイル群のクロステーブル整合性・ID書式・重複を検証する（読み取り専用）。",
    )
    parser.add_argument(
        "--tsv", nargs="+", metavar="FILE",
        help="検証対象のTSVファイル名を絞る（省略時は全ファイル）。FK検証の参照先は常に全ファイルを読み込む。",
    )
    parser.add_argument(
        "--only", nargs="+", choices=CHECK_NAMES, metavar="CHECK",
        help=f"実行するチェックを絞る（{', '.join(CHECK_NAMES)}）。省略時は全チェック。",
    )
    parser.add_argument("--json", action="store_true", help="機械可読なJSON形式で出力する")
    args = parser.parse_args()

    target_files = args.tsv or list(FILES.keys())
    unknown = [f for f in target_files if f not in FILES]
    if unknown:
        print(f"エラー: 未対応のファイルです: {', '.join(unknown)}", file=sys.stderr)
        return 2

    only_checks = args.only or CHECK_NAMES

    findings = run(target_files, only_checks)

    if args.json:
        print(json.dumps([f.to_dict() for f in findings], ensure_ascii=False, indent=2))
    else:
        print_report(findings)

    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # 出力を `head` 等に途中でパイプした場合の標準的な対処
        import os
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(1)
