#!/usr/bin/env python3
"""krm_wakun.tsv の japan_knowledge_id が '20020' で始まる和訓のうち、
krm_notes.tsv の remarks に「日国」「未収」「表記」をすべて含み、
hanzi_entry に IDS（U+2FF0-U+2FFF）を含まないものを抽出する（読み取り専用）。

使い方: python3 extract_nikkoku_misshu.py [repo_root] > out.tsv
出力: stdout に TSV（definition_seq_id, hanzi_entry, wakun_elements,
      japan_knowledge_id, remarks）、件数は stderr。
"""
import csv
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/ikeda/Hdic_data/krm")
IDS_RE = re.compile("[⿰-⿿]")
KEYWORDS = ("日国", "未収", "表記")


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        lines = (ln for ln in f if not ln.startswith("#"))
        return list(csv.DictReader(lines, delimiter="\t"))


notes = {r["definition_seq_id"]: r for r in read_tsv(root / "krm_notes.tsv")}

w = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
w.writerow(["definition_seq_id", "hanzi_entry", "wakun_elements",
            "japan_knowledge_id", "remarks"])
n = 0
for r in read_tsv(root / "krm_wakun.tsv"):
    jk = (r.get("japan_knowledge_id") or "").strip()
    if not jk.startswith("20020"):
        continue
    note = notes.get(r["definition_seq_id"])
    if note is None:
        continue
    remarks = note.get("remarks") or ""
    if not all(k in remarks for k in KEYWORDS):
        continue
    if IDS_RE.search(note.get("hanzi_entry") or ""):
        continue
    w.writerow([r["definition_seq_id"], note["hanzi_entry"],
                r["wakun_elements"], jk, remarks])
    n += 1
print(f"{n} 件", file=sys.stderr)
