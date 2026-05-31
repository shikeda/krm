#!/usr/bin/env python3
import argparse
import ast
import csv
import json
import re
import shutil
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
TSV_PATH = REPO_ROOT / "krm_pronunciations.tsv"
DIFF_DIR = REPO_ROOT / "diff"


def extract_brace_blocks(text):
    blocks = []
    start = None
    depth = 0
    quote = None
    escape = False

    for i, ch in enumerate(text):
        if quote:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                quote = None
            continue

        if ch in ("'", '"'):
            quote = ch
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth == 0:
                raise ValueError("対応する { がない } があります")
            depth -= 1
            if depth == 0 and start is not None:
                blocks.append(text[start : i + 1])
                start = None

    if depth != 0:
        raise ValueError("対応する } がない { があります")

    return blocks


def parse_mapping(block):
    try:
        value = json.loads(block)
    except json.JSONDecodeError:
        value = ast.literal_eval(block)

    if not isinstance(value, dict):
        raise ValueError("変更ブロックは dict / JSON object にしてください")
    if not all(isinstance(k, str) for k in value):
        raise ValueError("変更ブロックのキーは文字列にしてください")
    if not all(isinstance(v, str) for v in value.values()):
        raise ValueError("変更ブロックの値は文字列にしてください")
    return value


def resolve_diff_path(path):
    if path.exists():
        return path

    diff_path = DIFF_DIR / path
    if diff_path.exists():
        return diff_path

    raise FileNotFoundError(f"差分ファイルが見つかりません: {path}")


def parse_diff(path):
    text = path.read_text(encoding="utf-8")
    blocks = extract_brace_blocks(text)
    if len(blocks) < 2:
        raise ValueError("差分ファイルには「変更前」と「変更箇所」の2つのブロックが必要です")

    before = parse_mapping(blocks[0])
    fixes = parse_mapping(blocks[-1])

    target = before.get("pronunciation_id")
    if not target:
        match = re.search(r"([A-Z]\d{5}_\d{2}[A-Za-z]?)", path.stem)
        if match:
            target = match.group(1)
    if not target:
        raise ValueError("pronunciation_id を変更前ブロックかファイル名に含めてください")

    fixes.pop("pronunciation_id", None)
    return target, fixes


def read_tsv(path):
    all_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    comment_lines = [line for line in all_lines if line.startswith("#")]
    data_lines = [line for line in all_lines if not line.startswith("#")]

    reader = csv.DictReader(data_lines, delimiter="\t")
    if not reader.fieldnames:
        raise ValueError(f"{path} にヘッダー行がありません")

    return comment_lines, reader.fieldnames, list(reader)


def write_tsv(path, comment_lines, fieldnames, rows):
    backup_path = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup_path)
    try:
        with path.open("w", encoding="utf-8", newline="") as f:
            f.writelines(comment_lines)
            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames,
                delimiter="\t",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
    except Exception:
        shutil.copy2(backup_path, path)
        raise
    else:
        backup_path.unlink()


def update_pronunciation(diff_path, tsv_path):
    diff_path = resolve_diff_path(diff_path)
    target, fixes = parse_diff(diff_path)
    if not fixes:
        raise ValueError("変更箇所が空です")

    comment_lines, fieldnames, rows = read_tsv(tsv_path)

    unknown_fields = sorted(set(fixes) - set(fieldnames))
    if unknown_fields:
        raise ValueError("TSVに存在しない列です: " + ", ".join(unknown_fields))

    matched = 0
    for row in rows:
        if row["pronunciation_id"] == target:
            row.update(fixes)
            matched += 1

    if matched == 0:
        raise ValueError(f"pronunciation_id が見つかりません: {target}")
    if matched > 1:
        raise ValueError(f"pronunciation_id が複数行に存在します: {target}")

    write_tsv(tsv_path, comment_lines, fieldnames, rows)
    return target, fixes


def main():
    parser = argparse.ArgumentParser(
        description="Markdown形式の差分ファイルで krm_pronunciations.tsv を更新します。"
    )
    parser.add_argument("diff_file", type=Path)
    parser.add_argument("--tsv", type=Path, default=TSV_PATH)
    args = parser.parse_args()

    try:
        target, fixes = update_pronunciation(args.diff_file, args.tsv)
    except Exception as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1

    print(f"完了: {args.tsv.name} の {target} を更新しました（{len(fixes)}項目）")
    print("注意: krm_pronunciations.json はまだ更新されていません。")
    print("      必要に応じて別途再生成してください。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
