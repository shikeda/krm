#!/usr/bin/env python3
"""部首（120部）ごとの掲出項目数・掲出字数を krm_main.tsv と
krm_headword_chars.tsv から自動集計する。

- 項目数      : 部首ごとの krm_main.tsv 行数
- 1字〜6字以上 : 項目を構成字数で分類したヒストグラム
                 （6字以上のバケットに入れるが、字数には実字数を加算する）
- 字数        : 部首ごとの構成字数（krm_headword_chars.tsv の行数）の総和

部首番号は krm_main.tsv の volume_radical_index（vN#M の M）から取る。
krm_headword_chars.tsv の entry_id が「〔抹消〕」の行は集計から除外する
（原本上で抹消された文字。対応する krm_main 項目が存在しない）。

このスクリプトはデータを一切変更しない（読み取り専用）。

--against を渡すと、content/docs/krm/05-annotation-policy/
05-02b-headword-count-by-fascicle.ja.md の「部首毎の掲出項目数と
掲出字数のまとめ」表を読み取り、集計結果と突き合わせて差分を表示する。

終了コード:
    0 - まとめ表と一致（--against 未指定時は常に 0）
    1 - まとめ表と差分あり
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

MAIN_TSV = REPO_ROOT / "krm_main.tsv"
CHARS_TSV = REPO_ROOT / "krm_headword_chars.tsv"

# krm_headword_chars.entry_id の正規プレースホルダ（抹消文字）。集計から除外する。
CANCELLED_ENTRY_MARKER = "〔抹消〕"

# まとめ表の既定の場所（krm リポジトリの隣に site リポジトリがある想定）。
DEFAULT_MD = (
    REPO_ROOT.parent
    / "shikeda.github.io"
    / "content/docs/krm/05-annotation-policy"
    / "05-02b-headword-count-by-fascicle.ja.md"
)

COLS = ["1字", "2字", "3字", "4字", "5字", "6字以上", "項目数", "字数"]


def read_tsv(path):
    lines = [l for l in path.read_text(encoding="utf-8").splitlines(keepends=True)
             if not l.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))


def aggregate():
    """部首番号 -> {'name', 'row': [1字..字数], 'nodata': int} を返す。"""
    chars_per_entry = Counter()
    for row in read_tsv(CHARS_TSV):
        if row["entry_id"] == CANCELLED_ENTRY_MARKER:
            continue
        chars_per_entry[row["entry_id"]] += 1

    data = defaultdict(lambda: {"name": "", "buckets": Counter(), "items": 0,
                                "chars": 0, "nodata": 0})
    for row in read_tsv(MAIN_TSV):
        rad_no = int(row["volume_radical_index"].split("#")[1])
        d = data[rad_no]
        d["name"] = row["radical_name"]
        d["items"] += 1
        n = chars_per_entry.get(row["entry_id"], 0)
        if n == 0:
            d["nodata"] += 1
            continue
        d["chars"] += n
        d["buckets"][min(n, 6)] += 1

    result = {}
    for rad_no, d in data.items():
        b = d["buckets"]
        result[rad_no] = {
            "name": d["name"],
            "row": [b[1], b[2], b[3], b[4], b[5], b[6], d["items"], d["chars"]],
            "nodata": d["nodata"],
        }
    return result


def parse_summary_table(md_path):
    """まとめ表を 部首番号 -> [1字..字数] で返す。"""
    text = md_path.read_text(encoding="utf-8")
    if "## 部首毎の掲出項目数と掲出字数のまとめ" not in text:
        raise SystemExit(f"まとめ表の見出しが見つかりません: {md_path}")
    section = text.split("## 部首毎の掲出項目数と掲出字数のまとめ", 1)[1]
    out = {}
    for line in section.splitlines():
        m = re.match(r"\|\s*(\d{3})\s*\|\s*\S+\s*\|(.+)\|", line)
        if not m:
            continue
        nums = [int(x.replace(",", "").replace("*", "").strip())
                for x in m.group(2).split("|") if x.strip()]
        if len(nums) == 8:
            out[int(m.group(1))] = nums
    return out


def fmt(row):
    return " ".join(f"{v:>7,}" for v in row)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--against", nargs="?", const=str(DEFAULT_MD), default=None,
                    metavar="MD_PATH",
                    help="05-02b の .md と突き合わせて差分表示（省略時は既定パス）")
    ap.add_argument("--all", action="store_true",
                    help="差分のない部首も含めて全 120 部を表示する")
    args = ap.parse_args(argv)

    agg = aggregate()
    summary = parse_summary_table(Path(args.against)) if args.against else None

    header = f"{'No':>3} {'部':<3} | " + " ".join(f"{c:>7}" for c in COLS)
    print(header)
    print("-" * len(header))

    total_c = [0] * 8
    total_s = [0] * 8
    n_diff = 0
    for rad_no in range(1, 121):
        a = agg.get(rad_no)
        if a is None:
            print(f"{rad_no:>3} {'?':<3} | (krm_main に該当行なし)")
            continue
        comp = a["row"]
        for i in range(8):
            total_c[i] += comp[i]
        if summary is None:
            if args.all:
                print(f"{rad_no:>3} {a['name']:<3} | {fmt(comp)}")
            continue
        s = summary.get(rad_no, [0] * 8)
        for i in range(8):
            total_s[i] += s[i]
        diff = [comp[i] - s[i] for i in range(8)]
        if any(diff):
            n_diff += 1
        if any(diff) or args.all:
            mark = "  <<<" if any(diff) else ""
            print(f"{rad_no:>3} {a['name']:<3} | {fmt(comp)}   集計{mark}")
            print(f"{'':>3} {'':<3} | {fmt(s)}   まとめ")
            print(f"{'':>3} {'':<3} | {fmt(diff)}   差分")

    print("-" * len(header))
    print(f"{'':>3} {'合計':<3} | {fmt(total_c)}   集計")
    if summary is not None:
        print(f"{'':>3} {'':<3} | {fmt(total_s)}   まとめ")
        print(f"{'':>3} {'':<3} | {fmt([total_c[i] - total_s[i] for i in range(8)])}   差分")

    nodata = sum(a["nodata"] for a in agg.values())
    if nodata:
        print(f"\n注意: krm_headword_chars.tsv に構成字の行がない krm_main 項目が "
              f"{nodata} 件あります（字数・バケットに未計上）。")

    if summary is not None:
        print(f"\n差分のある部首: {n_diff}/120")
        return 1 if n_diff else 0
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # 出力を `head` 等で打ち切った場合。
        sys.exit(0)
