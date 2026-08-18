#!/usr/bin/env python3
"""krm_*.tsv を編集した後の後始末をまとめて行う。

- 変更されたTSVを git diff から自動検出（引数で明示指定も可）
- 各TSVのコメントヘッダーの Version / Last update（Last modified）を
  git HEAD時点のVersionを基準に patch を +1 して更新する
  （複数回実行しても、コミットするまでは同じ結果に収束する＝二重加算しない）
- 対応する JSON を再生成する（--skip-json で省略可）

このスクリプトは TSV の中身（データ行）は一切変更しない。
データ行の編集は Edit ツール等で先に済ませておくこと。
"""
import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

KNOWN_TSV_FILES = [
    "krm_main.tsv",
    "krm_notes.tsv",
    "krm_wakun.tsv",
    "krm_pronunciations.tsv",
    "krm_headword_chars.tsv",
    "krm_ndl.tsv",
]

# ファイル名 -> JSON再生成コマンド（Noneは対応JSONなし）
JSON_REGEN_COMMANDS = {
    "krm_main.tsv": ["python3", "scripts/tsv_to_json.py", "krm_main.tsv", "--output", "krm_main.json"],
    "krm_wakun.tsv": ["python3", "scripts/tsv_to_json.py", "krm_wakun.tsv", "--output", "krm_wakun.json"],
    "krm_headword_chars.tsv": [
        "python3", "scripts/tsv_to_json.py", "krm_headword_chars.tsv",
        "--output", "krm_headword_chars.json",
    ],
    "krm_pronunciations.tsv": ["python3", "scripts/gen_pronunciation_json.py"],
    "krm_notes.tsv": ["python3", "scripts/gen_notes_json.py"],
    "krm_ndl.tsv": None,
}

VERSION_RE = re.compile(r"^(#\s*)Version:\s*(\d+)\.(\d+)\.(\d+)(.*)$")
DATE_LABEL_RE = re.compile(r"^(#\s*)(Last update\s*:|Last modified\s*:)(.*)$")


def format_today() -> str:
    today = datetime.date.today()
    return f"{today.strftime('%B')} {today.day}, {today.year}"


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失敗: {result.stderr.strip()}")
    return result.stdout


def detect_changed_files() -> list[str]:
    changed = set(run_git(["diff", "--name-only"]).splitlines())
    changed |= set(run_git(["diff", "--name-only", "--cached"]).splitlines())
    return [f for f in KNOWN_TSV_FILES if f in changed]


def get_head_version(rel_path: str) -> tuple[int, int, int, str] | None:
    """git HEADに記録されているVersion（未コミットの変更は無視）を返す。"""
    result = subprocess.run(
        ["git", "show", f"HEAD:{rel_path}"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    for line in result.stdout.split("\n"):
        m = VERSION_RE.match(line)
        if m:
            _, major, minor, patch, suffix = m.groups()
            return int(major), int(minor), int(patch), suffix
    return None


def bump_version_and_date(path: Path, rel_path: str, today: str) -> tuple[str, str]:
    head_version = get_head_version(rel_path)
    if head_version is None:
        raise ValueError(f"{rel_path}: git HEAD側にVersionヘッダーが見つかりません")
    major, minor, patch, suffix = head_version
    old_version = f"{major}.{minor}.{patch}"
    new_version = f"{major}.{minor}.{patch + 1}"

    lines = path.read_text(encoding="utf-8").split("\n")
    version_hit = False
    date_hit = False

    for i, line in enumerate(lines):
        if not version_hit:
            m = VERSION_RE.match(line)
            if m:
                prefix = m.group(1)
                lines[i] = f"{prefix}Version: {new_version}{suffix}"
                version_hit = True
                continue
        if not date_hit:
            m2 = DATE_LABEL_RE.match(line)
            if m2:
                prefix, label = m2.group(1), m2.group(2)
                lines[i] = f"{prefix}{label} {today}"
                date_hit = True

    if not version_hit:
        raise ValueError(f"{rel_path}: 作業ツリー側にVersionヘッダーが見つかりません")
    if not date_hit:
        raise ValueError(f"{rel_path}: 作業ツリー側にLast update/Last modifiedヘッダーが見つかりません")

    path.write_text("\n".join(lines), encoding="utf-8")
    return old_version, new_version


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TSV編集後にVersion/Last update欄を更新し、対応するJSONを再生成する。",
    )
    parser.add_argument(
        "tsv_files", nargs="*",
        help="対象TSVファイル名（省略時は git diff から自動検出）",
    )
    parser.add_argument("--skip-json", action="store_true", help="JSON再生成をスキップする")
    args = parser.parse_args()

    try:
        targets = args.tsv_files or detect_changed_files()
    except RuntimeError as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1

    unknown = [f for f in targets if f not in KNOWN_TSV_FILES]
    if unknown:
        print(f"エラー: 未対応のファイルです: {', '.join(unknown)}", file=sys.stderr)
        return 1

    if not targets:
        print("Versionを更新すべきTSVの変更が見つかりません（git diffで検出できませんでした）。")
        return 0

    today = format_today()

    for name in targets:
        path = REPO_ROOT / name
        try:
            old_v, new_v = bump_version_and_date(path, name, today)
        except ValueError as exc:
            print(f"エラー: {exc}", file=sys.stderr)
            return 1
        print(f"{name}: Version {old_v} -> {new_v} / Last update -> {today}")

        if not args.skip_json:
            cmd = JSON_REGEN_COMMANDS.get(name)
            if cmd:
                print(f"  JSON再生成: {' '.join(cmd)}")
                subprocess.run(cmd, cwd=REPO_ROOT, check=True)

    print()
    print("次のステップ: git diff で内容を確認し、問題なければ git add / git commit してください。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
