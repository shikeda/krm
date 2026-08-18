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
| `gen_notes_json.py` | krm_notes.tsv から krm_notes.json を entry_id 単位の入れ子構造で再生成する |
| `tsv_to_json.py` | 任意の KRM TSV を JSON に変換する（フラット形式） |
| `finalize_krm_edit.py` | TSV編集後、Version/Last update欄の更新とJSON再生成をまとめて行う |

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

## 5. gen_notes_json.py — krm_notes.json の再生成（entry_id 単位の入れ子構造）

### 概要

`krm_notes.tsv` から `krm_notes.json` を再生成する。`krm_pronunciations.json` など他の
JSON ファイルと異なり、`krm_notes.json` は `entry_id` ごとにまとめ、`kazama_location` や
`hanzi_entry` などの項目レベルの列は1回だけ持たせ、注文の各要素
（`definition_seq_id`・`definition_elements`・`definition_type_code`・
`definition_type_name`・`remarks`）を `"definitions"` 配列としてその下に格納する
（詳細は [docs/data_specification.md](data_specification.md#krm_notes) を参照）。

このスクリプトは `krm_pronunciations.tsv` 専用の簡易変換器であり、
コマンドラインオプションは持たない。リポジトリ直下の `krm_notes.tsv` を読み込み、
同じくリポジトリ直下の `krm_notes.json` を上書きする。

### 使い方

```bash
python3 scripts/gen_notes_json.py
```

### 出力 JSON の形式

```json
[
  {
    "entry_id": "F00001",
    "kazama_location": "K01001310",
    "tenri_location": "Ta023310",
    "volume_name": "仏上",
    "radical_name": "人",
    "volume_radical_index": "v1#1",
    "hanzi_entry": "人",
    "original_entry": "〇",
    "definitions": [
      { "definition_seq_id": "F00001_00", "definition_elements": "", "definition_type_code": "100", "definition_type_name": "見出し", "remarks": "" },
      { "definition_seq_id": "F00001_01", "definition_elements": "音仁（LV）「ニン」", "definition_type_code": "215", "definition_type_name": "音注声点有_類音注等", "remarks": "広韻「如鄰切」（平声眞韻、仁）。" }
    ]
  }
]
```

### 注意事項

- 既存の `krm_notes.json` を上書きする
- コメント行（`#` 始まり）は JSON には出力しない
- `--group-by entry_id` を指定した `tsv_to_json.py` とは出力形式が異なる。`tsv_to_json.py`
  の `--group-by` は `{ "F00001": [各行...], ... }` という辞書形式になり、項目レベルの列が
  各行に重複したまま残る。`gen_notes_json.py` は項目レベルの列を1回だけ持たせる点が異なる
- `krm_notes.tsv` を修正・削除・追加した後は、このスクリプトを再実行して JSON を同期させること

---

## 6. tsv_to_json.py — 汎用 TSV → JSON 変換

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

## 7. finalize_krm_edit.py — TSV編集後の後始末（Version更新 + JSON再生成）

### 概要

`krm_pronunciations.tsv` 以外（`krm_main.tsv`・`krm_notes.tsv`・`krm_wakun.tsv`・
`krm_headword_chars.tsv`・`krm_ndl.tsv`）は、`diff/` 雛形方式のパイプラインを持たず、
`Edit` 等でデータ行を直接書き換える運用になっている。このスクリプトは、その**後始末**
（コメントヘッダーの `Version:` インクリメントと `Last update`/`Last modified` の日付更新、
対応する JSON の再生成）だけをまとめて行う。**データ行そのものは変更しない。**

### 使い方

```bash
# 1. 先に Edit などで対象TSVのデータ行を直接書き換えておく

# 2. 変更されたTSVを git diff から自動検出して後始末する
python3 scripts/finalize_krm_edit.py

# 対象を明示する場合
python3 scripts/finalize_krm_edit.py krm_main.tsv krm_notes.tsv

# JSON再生成を省略する場合
python3 scripts/finalize_krm_edit.py --skip-json
```

### 挙動

- 引数省略時は `git diff --name-only`（未ステージ＋ステージ済み）から、変更のあった
  KRM TSV を自動検出する。
- `Version:` は **git HEAD時点のバージョン** を基準に patch を +1 する（作業ツリー上の
  現在値ではない）。これにより、コミット前に複数回実行しても二重加算されず、
  常に「HEAD+1」に収束する。
- `Last update`/`Last modified` は実行日（例: `August 18, 2026`）に更新する。
- 対応する JSON は下表のコマンドで再生成する（`krm_ndl.tsv` は対応JSONなし）。

| TSV | JSON再生成 |
|---|---|
| `krm_main.tsv` | `tsv_to_json.py krm_main.tsv --output krm_main.json` |
| `krm_wakun.tsv` | `tsv_to_json.py krm_wakun.tsv --output krm_wakun.json` |
| `krm_headword_chars.tsv` | `tsv_to_json.py krm_headword_chars.tsv --output krm_headword_chars.json` |
| `krm_pronunciations.tsv` | `gen_pronunciation_json.py` |
| `krm_notes.tsv` | `gen_notes_json.py`（`krm_notes.json` は `.gitignore` 対象。ローカル確認用） |

### 注意事項

- Version/Last update の両ヘッダーが見つからない場合はエラーで終了する。
- 未対応のファイル名を渡した場合はエラーで終了する。
- 実行後は `git diff` で内容を確認し、問題なければ `git add` / `git commit` する
  （このスクリプト自身はコミットしない）。

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

### krm_main.tsv / krm_notes.tsv 等を直接修正する

`diff/` 雛形パイプラインを持たないTSVは、Editツール等でデータ行を直接書き換えた後、
`finalize_krm_edit.py` で後始末する。

```bash
# 1. Edit等で krm_main.tsv / krm_notes.tsv のデータ行を直接書き換える
#    （old_stringの一意一致を確認しながら1行単位で置換するのが安全）

# 2. Version/Last update更新 + JSON再生成をまとめて実行
python3 scripts/finalize_krm_edit.py

# 3. 内容を確認してからコミット
git diff
git add krm_main.tsv krm_main.json krm_notes.tsv
git commit -m "fix: revise remarks for ... (F#####)"
```
