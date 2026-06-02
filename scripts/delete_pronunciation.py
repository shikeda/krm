#!/usr/bin/env python3
"""
delete_pronunciation.py
────────────────────────────────────────────────────────────────────
krm_pronunciations.tsv から指定した pronunciation_id の行を削除する。

使用方法:
    python3 scripts/delete_pronunciation.py <pronunciation_id> [オプション]

例:
    python3 scripts/delete_pronunciation.py F15006_01b
    python3 scripts/delete_pronunciation.py F15006_01b --reason "声点は汚れのため"
    python3 scripts/delete_pronunciation.py F15006_01b --dry-run

オプション:
    --reason TEXT     削除理由（ログに記録される）
    --tsv PATH        対象TSVファイルのパス（省略時はスクリプトの親ディレクトリの krm_pronunciations.tsv）
    --log PATH        削除ログのパス（省略時は diff/deleted_pronunciations.tsv）
    --dry-run         実際には削除せず、対象行の内容だけ表示する

注意:
    - 実行前に .bak ファイルへのバックアップを自動生成する
    - 削除した行の内容と理由を deleted_pronunciations.tsv にログとして記録する
    - pronunciation_id が存在しない場合はエラーで終了する
    - pronunciation_id が複数行に存在する場合もエラーで終了する（想定外のデータ）
"""

import argparse
import csv
import shutil
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT   = SCRIPT_DIR.parent
TSV_PATH    = REPO_ROOT / "krm_pronunciations.tsv"
LOG_PATH    = REPO_ROOT / "diff" / "deleted_pronunciations.tsv"

# ログTSVの列構成
LOG_FIELDS = [
    "deleted_at",
    "pronunciation_id",
    "reason",
    "character_headword",
    "tone_marks",
    "similar_sound",
    "annotation_format",
    "remarks_pronunciation",
]


# ──────────────────────────────────────────────────────────────────
# TSV 読み書き
# ──────────────────────────────────────────────────────────────────

def read_tsv(path: Path) -> tuple[list[str], list[str], list[dict]]:
    """TSVを読み込む。コメント行・フィールド名・データ行を返す。"""
    all_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    comment_lines = [l for l in all_lines if l.startswith("#")]
    data_lines    = [l for l in all_lines if not l.startswith("#")]

    reader = csv.DictReader(data_lines, delimiter="\t")
    if not reader.fieldnames:
        raise ValueError(f"{path} にヘッダー行がありません")

    return comment_lines, list(reader.fieldnames), list(reader)


def write_tsv(path: Path, comment_lines: list[str],
              fieldnames: list[str], rows: list[dict]) -> None:
    """バックアップを作成してから TSV を書き込む。失敗時はバックアップから復元する。"""
    backup = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup)
    try:
        with path.open("w", encoding="utf-8", newline="") as f:
            f.writelines(comment_lines)
            writer = csv.DictWriter(
                f, fieldnames=fieldnames, delimiter="\t", lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(rows)
    except Exception:
        shutil.copy2(backup, path)
        raise
    else:
        backup.unlink()


# ──────────────────────────────────────────────────────────────────
# 削除ログ
# ──────────────────────────────────────────────────────────────────

def append_log(log_path: Path, row: dict, reason: str) -> None:
    """削除したレコードの概要を削除ログに追記する。"""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not log_path.exists()

    with log_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=LOG_FIELDS, delimiter="\t",
            lineterminator="\n", extrasaction="ignore"
        )
        if write_header:
            writer.writeheader()
        writer.writerow({
            "deleted_at":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pronunciation_id":    row.get("pronunciation_id", ""),
            "reason":              reason,
            "character_headword":  row.get("character_headword", ""),
            "tone_marks":          row.get("tone_marks", ""),
            "similar_sound":       row.get("similar_sound", ""),
            "annotation_format":   row.get("annotation_format", ""),
            "remarks_pronunciation": row.get("remarks_pronunciation", ""),
        })


# ──────────────────────────────────────────────────────────────────
# メイン処理
# ──────────────────────────────────────────────────────────────────

def delete_pronunciation(target_id: str, tsv_path: Path, log_path: Path,
                         reason: str, dry_run: bool) -> dict:
    """
    TSV から target_id の行を削除する。

    Returns
    -------
    削除した行の dict
    """
    comment_lines, fieldnames, rows = read_tsv(tsv_path)

    # 対象行を検索
    matched = [r for r in rows if r.get("pronunciation_id") == target_id]

    if len(matched) == 0:
        raise ValueError(f"pronunciation_id が見つかりません: {target_id}")
    if len(matched) > 1:
        raise ValueError(
            f"pronunciation_id が複数行に存在します（{len(matched)}件）: {target_id}"
        )

    target_row = matched[0]

    # dry-run: 削除対象を表示して終了
    if dry_run:
        print("【dry-run】以下の行を削除します（実際には変更しません）:")
        for k, v in target_row.items():
            if v:
                print(f"  {k}: {v}")
        if reason:
            print(f"  削除理由: {reason}")
        return target_row

    # 実際に削除
    new_rows = [r for r in rows if r.get("pronunciation_id") != target_id]
    write_tsv(tsv_path, comment_lines, fieldnames, new_rows)

    # ログに記録
    append_log(log_path, target_row, reason)

    return target_row


# ──────────────────────────────────────────────────────────────────
# エントリーポイント
# ──────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="krm_pronunciations.tsv から指定行を削除する"
    )
    parser.add_argument(
        "pronunciation_id",
        help="削除する pronunciation_id（例: F15006_01b）"
    )
    parser.add_argument(
        "--reason", "-r",
        default="",
        help="削除理由（ログに記録される）"
    )
    parser.add_argument(
        "--tsv",
        type=Path,
        default=TSV_PATH,
        help=f"対象TSVファイル（既定: {TSV_PATH}）"
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=LOG_PATH,
        help=f"削除ログファイル（既定: {LOG_PATH}）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="実際には削除せず、対象行の内容だけ表示する"
    )
    args = parser.parse_args()

    if not args.tsv.exists():
        print(f"エラー: TSVファイルが見つかりません: {args.tsv}", file=sys.stderr)
        return 1

    try:
        row = delete_pronunciation(
            target_id = args.pronunciation_id,
            tsv_path  = args.tsv,
            log_path  = args.log,
            reason    = args.reason,
            dry_run   = args.dry_run,
        )
    except Exception as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1

    if not args.dry_run:
        print(f"完了: {args.tsv} から {args.pronunciation_id} を削除しました")
        print(f"  character_headword : {row.get('character_headword', '')}")
        print(f"  tone_marks         : {row.get('tone_marks', '')}")
        print(f"  similar_sound      : {row.get('similar_sound', '')}")
        if args.reason:
            print(f"  削除理由           : {args.reason}")
        print(f"  ログ               : {args.log}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
