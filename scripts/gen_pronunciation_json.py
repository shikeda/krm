#!/usr/bin/env python3
"""krm_pronunciations.tsv から krm_pronunciations.json を再生成する。"""
import csv, json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TSV_PATH  = REPO_ROOT / "krm_pronunciations.tsv"
JSON_PATH = REPO_ROOT / "krm_pronunciations.json"

all_lines = TSV_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
data_lines = [l for l in all_lines if not l.startswith("#")]

reader = csv.DictReader(data_lines, delimiter="\t")
rows = [dict(r) for r in reader]

JSON_PATH.write_text(
    json.dumps(rows, ensure_ascii=False, indent=4),
    encoding="utf-8"
)
print(f"完了: {len(rows):,} 件 → {JSON_PATH}")
