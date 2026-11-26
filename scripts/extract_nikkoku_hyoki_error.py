#!/usr/bin/env python3
"""krm_notes.tsv の remarks から、日国の表記が誤りであると指摘した例を抽出する（読み取り専用）。

条件: remarks を「。」で文に分け、同一文内に「日国」「表記」を含み、
      「未収」を含まず、かつ誤りを示す語（誤|不審|不適）を含むもの。

使い方: python3 scripts/extract_nikkoku_hyoki_error.py [repo_root] > out.tsv
出力: stdout に TSV（definition_seq_id, hanzi_entry, matched_sentence, remarks）、
      件数は stderr。
"""
import csv
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
ERR_RE = re.compile("誤|不審|不適")

with open(root / "krm_notes.tsv", encoding="utf-8", newline="") as f:
    rows = csv.DictReader((ln for ln in f if not ln.startswith("#")), delimiter="\t")
    w = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    w.writerow(["definition_seq_id", "hanzi_entry", "matched_sentence", "remarks"])
    n = 0
    for r in rows:
        remarks = r.get("remarks") or ""
        for s in remarks.split("。"):
            if "日国" in s and "表記" in s and "未収" not in s and ERR_RE.search(s):
                w.writerow([r["definition_seq_id"], r["hanzi_entry"], s, remarks])
                n += 1
                break
print(f"{n} 件", file=sys.stderr)
