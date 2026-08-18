---
name: krm-data-edit
description: krm_main.tsv・krm_notes.tsv・krm_wakun.tsv・krm_headword_chars.tsv・krm_ndl.tsvの内容を修正する依頼（旧行→新行の指定、特定entry_id/definition_seq_idの特定列を書き換える依頼など）が来たときに使う。1行単位の直接編集を安全に行い、Version/Last update欄の更新とJSON再生成をscripts/finalize_krm_edit.pyで自動化し、diff確認とコミットメッセージ案の提示まで行う定型フロー。krm_pronunciations.tsvの修正はdiff/雛形方式（gen_diff_template.py等、docs/krm_scripts_usage.md参照）を優先する。
---

# krm-data-edit

`krm_pronunciations.tsv` 以外のKRM TSV（`krm_main.tsv`・`krm_notes.tsv`・`krm_wakun.tsv`・
`krm_headword_chars.tsv`・`krm_ndl.tsv`）を修正する依頼を受けたときの手順。

対象外: `krm_pronunciations.tsv` の修正は `docs/krm_scripts_usage.md` の
`gen_diff_template.py` → `diff/*.md` 編集 → `update_pronunciation.py` パイプラインを使う
（このSkillの対象外）。`krm.db` は読み取り専用・直接編集禁止（CLAUDE.md）。

## 手順

1. **対象行の特定**
   - 依頼が「旧行→新行」の形式（TSVの1行をまるごと貼られた）なら、その旧行をそのまま
     `old_string` に使えばよい。
   - 依頼が「`F00036` の `remarks` 列を〜に変更して」のような列指定なら、まず対象TSVを
     `grep` 等で読み、該当行を確認してから旧行・新行を組み立てる。
   - 変更後の列数が変更前と一致することを確認する（TSVはタブ区切り固定列数）。

2. **Editツールで1行だけ書き換える**
   - `Edit` の `old_string`/`new_string` に行全体を渡す（部分列だけでなく行全体を渡すと、
     同じ値を持つ他の行との誤マッチを避けやすい）。
   - `old_string` が複数行にマッチしてエラーになった場合は、`entry_id` などを含めて
     一意になるまで前後の文脈を広げる。安易に `replace_all` は使わない。
   - 複数箇所（例: `krm_main.tsv` と `krm_notes.tsv` の両方）にまたがる修正なら、
     この手順をファイルごとに繰り返す。

3. **後始末スクリプトを実行する**
   ```bash
   python3 scripts/finalize_krm_edit.py
   ```
   - 引数なしで実行すると、`git diff` から変更されたTSVを自動検出し、それぞれの
     `Version:` をHEAD基準で+1、`Last update`/`Last modified` を実行日に更新し、
     対応するJSONを再生成する（対応表は `docs/krm_scripts_usage.md` 参照）。
   - このスクリプトを複数回実行しても、コミット前なら同じ結果に収束する（安全に再実行可）。

4. **整合性チェックを実行する（任意だが推奨）**
   ```bash
   python3 scripts/validate_integrity.py --tsv <今回変更したTSVファイル名...>
   ```
   - 2026-08時点で、このリポジトリには本Skillとは無関係な既知の不整合が
     約84件（`git log`で未修正のまま残っている過去データの問題）ある。
     終了コード非ゼロ＝今回の変更が原因、とは限らない。
   - 出力の中に、**今回編集した`entry_id`/`definition_seq_id`が新たに含まれていないか**
     を確認する。含まれていれば、今回の編集が原因の可能性が高いのでユーザーに報告する。

5. **diffを提示する**
   - `git diff --stat` と、データ行の変更部分の `git diff` を要約してユーザーに見せる。
   - ヘッダーのVersion/Last update行の変化も一言添える。

6. **コミットメッセージ案を提示し、確認を待つ**
   - 既存の履歴の書式に合わせる（例: `fix: revise remarks for 域 (F16701)`、
     `fix: correct original gloss for 祾 (F19445)`）。件名は英語、変更内容が
     `entry_id`/`definition_seq_id` で特定できるようカッコ書きで添える。
   - **ユーザーの明示的な承認を得るまで `git commit` は実行しない。**
     承認が得られたら、変更されたTSVと対応するJSON（`.gitignore`対象のJSONは除く）を
     `git add` し、`git commit` する。`git push` は別途明示的な指示がない限り行わない。

## 注意

- `finalize_krm_edit.py` はデータ行を一切変更しない。ヘッダー更新とJSON再生成専用。
- 複数のentry_idにまたがる一括修正（数十件規模）は、1件ずつこの手順を回すより、
  すべてのEditを終えてから `finalize_krm_edit.py` を1回だけ実行する方が正しい
  （Versionは「今回の変更全体」に対して1回だけ上がる想定）。
