# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **pure data repository** — no build system, test suite, or scripts. It contains the KRM (Kanchi-in manuscript of the *Ruiju Myōgishō*) database, a full-text digitization of a 12th-century Hanzi dictionary, part of the HDIC project (Integrated Database of Hanzi Dictionaries in Early Japan). All data is available in TSV and JSON formats. License: CC BY-SA 4.0.

## Data Files

| File | Description |
|------|-------------|
| `krm_main.tsv/.json` | Core data: headwords, full definitions, location IDs |
| `krm_notes.tsv/.json` | Annotation data: definitions broken into typed elements with compiler's remarks |
| `krm_headword_chars.tsv/.json` | Per-character data for all constituent characters of headwords (enables single-character search) |
| `krm_wakun.tsv/.json` | Japanese native readings (*wakun*) with variant forms and JapanKnowledge links |
| `krm_pronunciations.tsv/.json` | Phonetic gloss data aligned with DHSJR specification |
| `krm_ndl.tsv` | Links to National Diet Library Digital Collections images |

## Table Relationships

`krm_main` is the root table. The primary key is `entry_id` (e.g., `F00001`).

- `krm_notes` links to `krm_main` via `entry_id`; its `definition_seq_id` (e.g., `F00001_01`) extends `entry_id` with a suffix (`_00` = headword, `_01`, `_02`, ... = definition elements in order)
- `krm_wakun` links to `krm_notes` via `definition_seq_id`
- `krm_headword_chars` links to `krm_main` via `entry_id` and uses `hanzi_id` (e.g., `S00001`) for individual character IDs
- `krm_pronunciations` links to `krm_notes` via `definition_seq_id`

In `krm_notes.json`, the notes are **nested** inside each `krm_main` record under the key `"definitions"` (array of objects), not stored as a flat table.

## ID and Location Formats

- `entry_id`: `F` + 5-digit number (e.g., `F00001`); some additions use a `b` suffix
- `hanzi_id`: `S` + 5-digit number (e.g., `S00001`)
- `definition_seq_id`: `entry_id` numeric part + `_00`, `_01`, ... (e.g., `F00001_01`)
- `kazama_location`: `K` + volume(2) + page(3) + line(1) + segment(1) + char-order(1) — e.g., `K01001310`
- `tenri_location`: `T` + volume(a/b/c) + page(3) + line(1) + segment(1) + char-order(1) — e.g., `Ta023310`

## Special Character Conventions (v1.2 specification, March 2025)

These conventions apply across all current files (lowercase `krm_` prefix):

| Symbol | Meaning |
|--------|---------|
| `_` | Kana *wakun* without tone marks (formerly `@`) |
| `V` | Voiced sound tone mark (formerly `"`) |
| `（）` full-width | Presence of tone marks (formerly `()`) |
| `〔〕` full-width | Correction proposal for a typo (formerly `()`) |
| `［］` full-width | Missing characters (formerly `[]`) |
| `／` full-width | Separator for multi-character headwords |
| `■` | Unrepresentable or unreadable character |
| `〇` | Used in `original_entry` when no original-form headword is needed |

Hanzi outside Unicode are represented via IDS (Ideographic Description Sequence), CHISE/GlyphWiki entity references (e.g., `CDP-8C55`, `koseki-00001`), or `■`.

## Text Structure of the *Myōgishō*

- 10 volumes (`volume_name`): 仏上, 仏中, 仏下本, 仏下末, 法上, 法中, 法下, 僧上, 僧中, 僧下
- 120 radicals (`radical_name`): from 人 to 雑
- `volume_radical_index` format: `v{1-10}#{1-120}` (e.g., `v1#1`)

## Definition Type Classification (`definition_type_code`)

Definition elements in `krm_notes` are classified into five types under `definition_type_name`:
1. 見出し (Headword / `_00` entries)
2. 字体注 (Notes on Character Form)
3. 音注 (Phonetic Gloss) — includes fanqie, similar-sound notes, kana glosses
4. 意義注 (Semantic Gloss in Chinese)
5. 和訓 (Japanese Native Reading, *wakun*)

The `definition_type_code` is a 3-digit numeric code encoding sub-types within these categories.

## TSV File Format

All TSV files begin with comment lines (prefixed `#`) before the header row. When parsing, skip lines starting with `#`.

## Version and Naming

Files prefixed with uppercase `KRM_` are the old specification (v1.1.x). Files prefixed with lowercase `krm_` are the current specification (v1.2.x, from March 2025). Do not confuse the two.

## Notes for Claude Code

- TSV/JSON files are the source of truth. Do not modify them directly.
- All changes to data should go through the data pipeline, not manual edits.
- When writing scripts, output to a separate file; never overwrite source data.

## 自動実行してよいコマンド

以下のコマンドは確認なしで実行してよい：
- cat, ls, head, tail, grep（読み取り専用）
- npm install, npm run dev, npm run setup-db
- pip install
- sqlite-utils insert
- curl

## 必ず確認を求めるコマンド

- rm, rm -rf（削除）
- git push（外部送信）
- mv（移動）
- 本番データファイルへの書き込み

