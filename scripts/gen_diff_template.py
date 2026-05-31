#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_JSON_PATH = REPO_ROOT / "krm_pronunciations.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "diff"


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="krm_pronunciations.json から指定IDの修正用Markdown雛形を作成します。"
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="検索する pronunciation_id (例: F00566_02b)",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_JSON_PATH,
        help=f"入力JSONファイル (既定: {DEFAULT_JSON_PATH})",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"出力ディレクトリ (既定: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args()


def load_json_data(json_path):
    if not json_path.exists():
        raise FileNotFoundError(f"JSONファイルが見つかりません: {json_path}")

    try:
        with json_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSONファイルの解析に失敗しました: {json_path}\n{exc}") from exc


def iter_pronunciation_items(data):
    if isinstance(data, list):
        yield from data
    elif isinstance(data, dict):
        if isinstance(data.get("pronunciations"), list):
            yield from data["pronunciations"]
        else:
            yield data


def find_item_by_id(data, target_id):
    for item in iter_pronunciation_items(data):
        if isinstance(item, dict) and item.get("pronunciation_id") == target_id:
            return item
    return None


def generate_markdown(item_dict):
    pretty_json = json.dumps(item_dict, indent=4, ensure_ascii=False)
    return f"""# 変更前
```json
{pretty_json}
```

# 変更箇所
```python
{{
}}
```
"""


def write_template(target_id, item_dict, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"diff_{target_id}.md"
    output_path.write_text(generate_markdown(item_dict), encoding="utf-8")
    return output_path


def main():
    args = parse_arguments()

    try:
        data = load_json_data(args.json)
        item = find_item_by_id(data, args.input)
        if item is None:
            raise ValueError(f"pronunciation_id が見つかりません: {args.input}")
        output_path = write_template(args.input, item, args.output_dir)
    except Exception as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1

    print(f"作成しました: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
