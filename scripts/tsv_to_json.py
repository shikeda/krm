#!/usr/bin/env python3
"""
tsv_to_json.py
────────────────────────────────────────────────────────────────────
KRM の TSV ファイル（krm_main.tsv / krm_notes.tsv 等）を
JSON 形式に安全に変換する。

特徴:
  - コメント行（# 始まり）を読み飛ばして変換
  - コメント行からバージョン・ライセンス等のメタ情報を抽出して
    JSON のヘッダに付与する（オプション）
  - 変換前に行数・列数・空値の分布を検証して問題を報告
  - 出力形式はレコードのリスト、またはキー列でグループ化した辞書

使用方法:
    # 基本（レコードのリスト形式）
    python3 scripts/tsv_to_json.py krm_main.tsv

    # グループ化（entry_id をキーにした辞書形式）
    python3 scripts/tsv_to_json.py krm_notes.tsv --group-by entry_id

    # メタ情報をヘッダに付与
    python3 scripts/tsv_to_json.py krm_main.tsv --with-meta

    # 出力先を指定
    python3 scripts/tsv_to_json.py krm_main.tsv --output krm_main.json

出力 JSON の形式:

  リスト形式（デフォルト）:
    [ { "entry_id": "F00001", ... }, ... ]

  グループ化形式（--group-by entry_id）:
    { "F00001": [ { ... }, ... ], ... }

  メタ情報付き（--with-meta）:
    {
      "_meta": {
        "source_file": "krm_main.tsv",
        "record_count": 12345,
        "converted_at": "2026-06-02 ...",
        "version": "1.2.12",
        "license": "CC BY-SA 4.0",
        "comments": [ "# HDIC Project", ... ]
      },
      "records": [ ... ] または "records": { ... }
    }
"""

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT  = SCRIPT_DIR.parent


# ──────────────────────────────────────────────────────────────────
# コメント行のパース
# ──────────────────────────────────────────────────────────────────

def parse_comments(comment_lines: list[str]) -> dict:
    """
    コメント行からメタ情報を抽出する。

    抽出対象:
        Version:     バージョン番号
        Date:        作成日
        Last update: 最終更新日
        License:     ライセンス
    """
    meta = {
        "version":     "",
        "date":        "",
        "last_update": "",
        "license":     "",
        "comments":    [l.rstrip() for l in comment_lines],
    }
    for line in comment_lines:
        line = line.lstrip("#").strip()
        if m := re.match(r"Version\s*:\s*(.+)", line):
            meta["version"] = m.group(1).strip()
        elif m := re.match(r"Date\s*:\s*(.+)", line):
            meta["date"] = m.group(1).strip()
        elif m := re.match(r"Last update\s*:\s*(.+)", line, re.IGNORECASE):
            meta["last_update"] = m.group(1).strip()
        elif m := re.match(r"License\s*:\s*(.+)", line):
            meta["license"] = m.group(1).strip()
    return meta


# ──────────────────────────────────────────────────────────────────
# TSV 読み込み
# ──────────────────────────────────────────────────────────────────

def read_tsv(path: Path) -> tuple[list[str], list[str], list[dict]]:
    """
    TSV を読み込み（comment_lines, fieldnames, rows）を返す。

    コメント行（# 始まり）を分離し、残りを CSV として解析する。
    """
    all_lines     = path.read_text(encoding="utf-8").splitlines(keepends=True)
    comment_lines = [l for l in all_lines if l.startswith("#")]
    data_lines    = [l for l in all_lines if not l.startswith("#")]

    if not data_lines:
        raise ValueError(f"{path.name}: データ行が存在しません")

    reader = csv.DictReader(data_lines, delimiter="\t")
    if not reader.fieldnames:
        raise ValueError(f"{path.name}: ヘッダー行が存在しません")

    rows = list(reader)
    return comment_lines, list(reader.fieldnames), rows


# ──────────────────────────────────────────────────────────────────
# 検証
# ──────────────────────────────────────────────────────────────────

def validate(fieldnames: list[str], rows: list[dict], path_name: str) -> list[str]:
    """
    変換前の検証を行い、警告メッセージのリストを返す。
    エラーがあれば ValueError を送出する。
    """
    warnings = []

    # 列数の不一致チェック
    n_expected = len(fieldnames)
    for i, row in enumerate(rows, 2):  # ヘッダが1行目なので2から
        if len(row) != n_expected:
            warnings.append(
                f"行 {i}: 列数が不一致 (期待={n_expected}, 実際={len(row)})"
            )

    # None 値（列数超過で生じる）の検出
    none_cols = Counter()
    for row in rows:
        for k, v in row.items():
            if v is None:
                none_cols[k] += 1
    for col, cnt in none_cols.items():
        warnings.append(f"列 '{col}' に None 値 {cnt} 件（列数超過の可能性）")

    # 空値の分布レポート（警告ではなく情報として返す）
    empty_cols = Counter()
    for row in rows:
        for k, v in row.items():
            if v is not None and v.strip() == "":
                empty_cols[k] += 1

    return warnings, empty_cols


# ──────────────────────────────────────────────────────────────────
# グループ化
# ──────────────────────────────────────────────────────────────────

def group_by(rows: list[dict], key: str) -> dict:
    """
    rows を key の値でグループ化した辞書を返す。
    key が存在しない行は "_unknown" にまとめる。
    """
    result = defaultdict(list)
    for row in rows:
        k = row.get(key, "_unknown") or "_unknown"
        result[k].append(row)
    return dict(result)


# ──────────────────────────────────────────────────────────────────
# 出力
# ──────────────────────────────────────────────────────────────────

def build_output(records, meta: dict | None,
                 source_file: str, record_count: int) -> dict | list:
    """出力 JSON を組み立てる。"""
    if meta is None:
        return records  # メタなし: records そのものを返す

    return {
        "_meta": {
            "source_file":   source_file,
            "record_count":  record_count,
            "converted_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version":       meta.get("version", ""),
            "date":          meta.get("date", ""),
            "last_update":   meta.get("last_update", ""),
            "license":       meta.get("license", ""),
            "comments":      meta.get("comments", []),
        },
        "records": records,
    }


# ──────────────────────────────────────────────────────────────────
# メイン
# ──────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="KRM TSV ファイルを JSON に変換する"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="入力 TSV ファイルのパス"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="出力 JSON ファイルのパス（省略時は入力ファイルと同じ場所に .json で保存）"
    )
    parser.add_argument(
        "--group-by", "-g",
        default=None,
        metavar="COLUMN",
        help="指定列の値でレコードをグループ化した辞書形式で出力（例: entry_id）"
    )
    parser.add_argument(
        "--with-meta",
        action="store_true",
        help="コメント行からメタ情報を抽出して _meta キーに付与する"
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=4,
        help="JSON のインデント幅（デフォルト: 4）"
    )
    parser.add_argument(
        "--no-indent",
        action="store_true",
        help="インデントなしで出力（ファイルサイズ削減）"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="検証で警告が出た場合にエラーで終了する"
    )
    args = parser.parse_args()

    # 入力ファイルの確認
    input_path = args.input
    if not input_path.is_absolute():
        # スクリプトの場所から REPO_ROOT 経由で解決を試みる
        if not input_path.exists():
            candidate = REPO_ROOT / input_path
            if candidate.exists():
                input_path = candidate
    if not input_path.exists():
        print(f"エラー: ファイルが見つかりません: {input_path}", file=sys.stderr)
        return 1

    # 出力パスの決定
    output_path = args.output or input_path.with_suffix(".json")

    print(f"[1/4] 読み込み中: {input_path}")
    try:
        comment_lines, fieldnames, rows = read_tsv(input_path)
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1

    print(f"      コメント行: {len(comment_lines)} 行")
    print(f"      データ行:   {len(rows):,} 行  列数: {len(fieldnames)}")

    # 検証
    print("[2/4] 検証中 …")
    try:
        warnings, empty_cols = validate(fieldnames, rows, input_path.name)
    except ValueError as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1

    if warnings:
        for w in warnings:
            print(f"  警告: {w}")
        if args.strict:
            print("エラー: --strict モードのため警告を検出した時点で終了します",
                  file=sys.stderr)
            return 1
    else:
        print("      問題なし")

    # 空値の多い列を報告（全行の10%以上が空の列）
    threshold = len(rows) * 0.1
    heavy_empty = {k: v for k, v in empty_cols.items() if v > threshold}
    if heavy_empty:
        print("      空値が多い列（行数の10%超）:")
        for col, cnt in sorted(heavy_empty.items(), key=lambda x: -x[1]):
            print(f"        {col}: {cnt:,} 件 ({cnt/len(rows)*100:.1f}%)")

    # グループ化
    print("[3/4] 変換中 …")
    if args.group_by:
        if args.group_by not in fieldnames:
            print(f"エラー: --group-by に指定した列 '{args.group_by}' が存在しません",
                  file=sys.stderr)
            print(f"  利用可能な列: {', '.join(fieldnames)}", file=sys.stderr)
            return 1
        records = group_by(rows, args.group_by)
        print(f"      グループ化: {args.group_by} = {len(records):,} グループ")
    else:
        records = rows

    # メタ情報
    meta = parse_comments(comment_lines) if args.with_meta else None

    output = build_output(
        records     = records,
        meta        = meta,
        source_file = input_path.name,
        record_count = len(rows),
    )

    # 書き出し
    print(f"[4/4] 書き出し中: {output_path}")
    indent = None if args.no_indent else args.indent
    output_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=indent),
        encoding="utf-8",
    )

    size_kb = output_path.stat().st_size / 1024
    print()
    print("=" * 50)
    print("  完了")
    print("=" * 50)
    print(f"  入力行数    : {len(rows):,} 行")
    print(f"  列数        : {len(fieldnames)}")
    if args.group_by:
        print(f"  グループ数  : {len(records):,}")
    print(f"  出力        : {output_path}")
    print(f"  サイズ      : {size_kb:.1f} KB")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
