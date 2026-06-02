# KRM スクリプト 使い方まとめ

作成日: 2026-06-02

---

## スクリプト一覧と役割

| スクリプト | 役割 |
|---|---|
| `gen_diff_template.py` | 修正用 Markdown 雛形を生成する |
| `update_pronunciation.py` | 差分 Markdown で TSV を更新する |
| `delete_pronunciation.py` | TSV から指定行を削除する |
| `gen_pronunciation_json.py` | TSV から JSON を再生成する |
| `tsv_to_json.py` | 任意の KRM TSV を JSON に変換する |

---

## 作業フローの全体像

```
【修正の場合】
  gen_diff_template.py   →   diff/diff_*.md を編集   →   update_pronunciation.py
        ↓                                                          ↓
  雛形生成（変更前 JSON + 空の変更箇所）            TSV の該当行を更新

【削除の場合】
  delete_pronunciation.py
        ↓
  TSV から指定行を削除 + diff/deleted_pronunciations.tsv にログを記録

【新規追加の場合】
  TSV に手動で行を追加

【JSON の同期】
  修正・削除・追加のたびに gen_pronunciation_json.py で JSON を再生成
```

---

## 1. gen_diff_template.py — 修正用 Markdown 雛形の生成

### 概要

`krm_pronunciations.json` から指定 ID のレコードを読み込み、
修正用の Markdown ファイル（`diff/diff_<ID>.md`）を生成する。

### 使い方

```bash
python3 scripts/gen_diff_template.py --input <pronunciation_id>

# 例
python3 scripts/gen_diff_template.py --input F00566_02b
# → diff/diff_F00566_02b.md を生成
```

### オプション

| オプション | 省略形 | 内容 | 既定値 |
|---|---|---|---|
| `--input` | `-i` | 対象の pronunciation_id（必須） | — |
| `--json` | — | 入力 JSON ファイルのパス | `krm_pronunciations.json` |
| `--output-dir` | `-o` | 出力ディレクトリ | `diff/` |

### 生成される Markdown の形式

```markdown
# 変更前
\```json
{
    "pronunciation_id": "F00566_02b",
    "character_headword": "巨",
    ...
}
\```

# 変更箇所
\```python
{
}
\```
```

`# 変更箇所` の `{}` の中に修正したい列名と値を記入して保存する。

### 記入例

```python
{
    "character_headword": "亮",
    "character_form": "高",
    "word_headword": "亮",
    "word_form": "高",
    "remarks_pronunciation": "「高」は「亮」の誤写と推定。集韻「其亮切」参照"
}
```

---

## 2. update_pronunciation.py — TSV の更新

### 概要

`gen_diff_template.py` で作成し編集した差分 Markdown ファイルを読み込み、
`krm_pronunciations.tsv` の該当行を更新する。
実行前に `.bak` バックアップを自動生成し、失敗時は自動復元する。

### 使い方

```bash
python3 scripts/update_pronunciation.py <diff_file>

# 例
python3 scripts/update_pronunciation.py diff/diff_F00566_02b.md

# diff/ ディレクトリ内のファイルはファイル名だけでも指定可能
python3 scripts/update_pronunciation.py diff_F00566_02b.md
```

### オプション

| オプション | 内容 | 既定値 |
|---|---|---|
| `--tsv` | 対象 TSV ファイルのパス | `krm_pronunciations.tsv` |

### 注意事項

- 差分 Markdown の `# 変更箇所` ブロックが空（`{}`）の場合はエラーで終了する
- `# 変更箇所` は JSON object または Python の dict リテラルとして解釈される
- 変更値は文字列で指定する
- TSV に存在しない列名を指定した場合はエラーで終了する
- 同一 `pronunciation_id` が複数行ある場合はエラーで終了する
- **JSON は自動更新されない**。更新後は `gen_pronunciation_json.py` を実行すること

---

## 3. delete_pronunciation.py — 行の削除

### 概要

`krm_pronunciations.tsv` から指定した `pronunciation_id` の行を削除する。
削除内容を `diff/deleted_pronunciations.tsv` にログとして記録する。

### 使い方

```bash
python3 scripts/delete_pronunciation.py <pronunciation_id> [オプション]

# 例
python3 scripts/delete_pronunciation.py F15006_01b \
    --reason "声点は汚れ（F15006_01 参照）。音注字かつ声点なしのため削除。"

# 実際には削除せず内容だけ確認する（dry-run）
python3 scripts/delete_pronunciation.py F15006_01b --dry-run
```

### オプション

| オプション | 省略形 | 内容 | 既定値 |
|---|---|---|---|
| `--reason` | `-r` | 削除理由（ログに記録される） | 空欄 |
| `--tsv` | — | 対象 TSV ファイルのパス | `krm_pronunciations.tsv` |
| `--log` | — | 削除ログのパス | `diff/deleted_pronunciations.tsv` |
| `--dry-run` | — | 実際には削除せず対象行を表示する | — |

### 削除ログの形式

削除するたびに `diff/deleted_pronunciations.tsv` に1行追記される。

| 列 | 内容 |
|---|---|
| `deleted_at` | 削除日時 |
| `pronunciation_id` | 削除した ID |
| `reason` | 削除理由 |
| `character_headword` | 見出し字 |
| `tone_marks` | 声点 |
| `similar_sound` | 類音注 |
| `annotation_format` | 音注形式 |
| `remarks_pronunciation` | 備考 |

### 注意事項

- 実行前に `.bak` バックアップを自動生成し、書き込み失敗時は復元する
- `pronunciation_id` が存在しない場合、または複数行に存在する場合はエラーで終了する
- **JSON は自動更新されない**。削除後は `gen_pronunciation_json.py` を実行すること

---

## 4. gen_pronunciation_json.py — JSON の再生成

### 概要

`krm_pronunciations.tsv` から `krm_pronunciations.json` を再生成する。
修正・削除・追加のいずれかを行った後に実行して JSON を TSV と同期させる。

このスクリプトは `krm_pronunciations.tsv` 専用の簡易変換器であり、
コマンドラインオプションは持たない。リポジトリ直下の
`krm_pronunciations.tsv` を読み込み、同じくリポジトリ直下の
`krm_pronunciations.json` を上書きする。

### 使い方

```bash
python3 scripts/gen_pronunciation_json.py
```

### 注意事項

- 既存の `krm_pronunciations.json` を上書きする
- コメント行（`#` 始まり）は JSON には出力しない
- 出力はレコード配列のみで、インデント幅は 4
- `--help` などのオプションは実装されていない。引数を付けても無視され、通常どおり再生成される
- 任意の入出力パス、メタ情報付与、厳密な検証が必要な場合は `tsv_to_json.py` を使う

---

## 5. tsv_to_json.py — 汎用 TSV → JSON 変換

### 概要

`krm_main.tsv`・`krm_notes.tsv` など KRM の任意の TSV ファイルを JSON に変換する。
変換前に列数・NULL 値・空値の分布を検証して問題を報告する。

### 使い方

```bash
python3 scripts/tsv_to_json.py <input_tsv> [オプション]

# 基本（リスト形式）
python3 scripts/tsv_to_json.py krm_main.tsv

# entry_id でグループ化した辞書形式
python3 scripts/tsv_to_json.py krm_notes.tsv --group-by entry_id

# コメント行からメタ情報を付ける
python3 scripts/tsv_to_json.py krm_main.tsv --with-meta

# 出力先を指定
python3 scripts/tsv_to_json.py krm_main.tsv --output data/output/krm_main.json

# インデントなし（ファイルサイズ削減）
python3 scripts/tsv_to_json.py krm_main.tsv --no-indent

# 警告があればエラーで終了（厳密モード）
python3 scripts/tsv_to_json.py krm_main.tsv --strict
```

### オプション

| オプション | 省略形 | 内容 | 既定値 |
|---|---|---|---|
| `--output` | `-o` | 出力 JSON のパス | 入力ファイルと同じ場所に `.json` |
| `--group-by` | `-g` | 指定列でグループ化した辞書形式で出力 | なし（リスト形式） |
| `--with-meta` | — | コメント行からメタ情報を `_meta` キーに付与 | なし |
| `--indent` | — | インデント幅 | 4 |
| `--no-indent` | — | インデントなし | — |
| `--strict` | — | 警告時にエラーで終了 | — |

### 出力 JSON の形式

**リスト形式（デフォルト）**:
```json
[ { "entry_id": "F00001", ... }, ... ]
```

**グループ化形式（`--group-by entry_id`）**:
```json
{ "F00001": [ { ... }, ... ], ... }
```

**メタ情報付き（`--with-meta`）**:
```json
{
  "_meta": {
    "source_file": "krm_main.tsv",
    "record_count": 12345,
    "converted_at": "2026-06-02 ...",
    "version": "1.2.12",
    "license": "CC BY-SA 4.0",
    "comments": [ "# HDIC Project", ... ]
  },
  "records": [ ... ]
}
```

### `krm_pronunciations.tsv` への適用

`gen_pronunciation_json.py` の代替として `tsv_to_json.py` も使用可能。
`gen_pronunciation_json.py` と同じレコード配列形式にする場合は
`--with-meta` を付けない。

```bash
python3 scripts/tsv_to_json.py krm_pronunciations.tsv \
    --output krm_pronunciations.json \
    --indent 4
```

メタ情報付き JSON が必要な場合のみ `--with-meta` を付ける。

```bash
python3 scripts/tsv_to_json.py krm_pronunciations.tsv \
    --output krm_pronunciations_with_meta.json \
    --with-meta
```

日常の `krm_pronunciations.json` 同期には、専用の
`gen_pronunciation_json.py` の使用を推奨する。

---

## よくある作業手順

### 既存レコードを修正する

```bash
# 1. 雛形生成
python3 scripts/gen_diff_template.py --input F00566_02b

# 2. diff/diff_F00566_02b.md を編集（変更箇所を記入）

# 3. TSV に適用
python3 scripts/update_pronunciation.py diff/diff_F00566_02b.md

# 4. JSON を再生成
python3 scripts/gen_pronunciation_json.py
```

### 不要なレコードを削除する

```bash
# 1. 削除内容を確認（dry-run）
python3 scripts/delete_pronunciation.py F15006_01b --dry-run

# 2. 実際に削除
python3 scripts/delete_pronunciation.py F15006_01b \
    --reason "声点は汚れ。音注字かつ声点なしのため削除（F15006_01 参照）"

# 3. JSON を再生成
python3 scripts/gen_pronunciation_json.py
```

### 複数件をまとめて修正してから JSON を再生成する

```bash
python3 scripts/update_pronunciation.py diff/diff_F30909_01.md
python3 scripts/update_pronunciation.py diff/diff_F30909_01b.md
python3 scripts/update_pronunciation.py diff/diff_F30909_02.md
# まとめて1回だけ再生成
python3 scripts/gen_pronunciation_json.py
```
