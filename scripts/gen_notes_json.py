#!/usr/bin/env python3
"""krm_notes.tsv から krm_notes.json を、entry_id 単位の入れ子構造で再生成する。"""
import csv, json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TSV_PATH  = REPO_ROOT / "krm_notes.tsv"
JSON_PATH = REPO_ROOT / "krm_notes.json"

# entry_id ごとに1回だけ現れる、krm_main由来の項目レベルの列
ENTRY_FIELDS = [
    "entry_id", "kazama_location", "tenri_location", "volume_name",
    "radical_name", "volume_radical_index", "hanzi_entry", "original_entry",
]
# definition_seq_id ごとに異なる、注文要素レベルの列
DEFINITION_FIELDS = [
    "definition_seq_id", "definition_elements", "definition_type_code",
    "definition_type_name", "remarks",
]

all_lines = TSV_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
data_lines = [l for l in all_lines if not l.startswith("#")]

reader = csv.DictReader(data_lines, delimiter="\t")

entries: dict[str, dict] = {}
order: list[str] = []
for row in reader:
    entry_id = row["entry_id"]
    if entry_id not in entries:
        entries[entry_id] = {field: row[field] for field in ENTRY_FIELDS}
        entries[entry_id]["definitions"] = []
        order.append(entry_id)
    entries[entry_id]["definitions"].append(
        {field: row[field] for field in DEFINITION_FIELDS}
    )

records = [entries[eid] for eid in order]

JSON_PATH.write_text(
    json.dumps(records, ensure_ascii=False, indent=4),
    encoding="utf-8",
)
print(f"完了: {len(records):,} 項目（definitions 総数 "
      f"{sum(len(e['definitions']) for e in records):,} 件） → {JSON_PATH}")
