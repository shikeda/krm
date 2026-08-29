
# KRM: Database of the Kanchi-in Manuscript of *Ruiju Myōgishō*

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22164768.svg)](https://doi.org/10.5281/zenodo.22164768)

*[日本語版はこちら (README_jp.md)](README_jp.md)* — this English README is the primary entry point to the repository; the Japanese version mirrors its structure.

## Overview

This database is a full-text digitization of the Kanchi-in manuscript of the *Ruiju Myōgishō* (abbreviated as KRM), incorporating location information, textual collation, source studies, and more. It is one of the **Hanzi** dictionary databases comprising the **Integrated Database of Hanzi Dictionaries in Early Japan** (abbreviated as HDIC).

The Kanchi-in manuscript of the *Ruiju Myōgishō* is a **Hanzi** dictionary compiled in the twelfth century by a Shingon Buddhist monk. It has been regarded as an important resource for Japanese historical linguistics research due to its extensive collection of *wakun* indicating accent, detailed annotations on Hanzi pronunciations, and annotations on variant characters. Its Chinese annotations on **fanqie**, meanings, and glyph forms have also garnered attention as materials for Chinese linguistics.

KRM was first published in March 2022. In March 2025, a revised edition with a specification change (see [Version History](#version-history)) and more detailed documentation was released.

### Kanji and Hanzi

Dictionaries of Chinese characters compiled in Japan during the Heian period are invaluable resources not only for Japanese linguistics but also for Chinese linguistics. To promote international accessibility, this project uses the term "Hanzi." Researchers specializing in Japanese studies may, without any issue, read this term as "Kanji." This is meant to respect the linguistic diversity and academic traditions of both fields while encouraging broader scholarly exchange.

## Current Release and Citation

| | |
|---|---|
| **Latest archived release** | v1.2.7 (2026-08-29) — DOI-assigned on Zenodo. Cite this version for academic work. |
| **Current repository state (GitHub)** | unreleased — this repository has received incremental corrections and additions since v1.2.7 (see [Version History](#version-history)) that are not yet reflected in any archived Zenodo snapshot. |

If you use KRM for academic purposes, please cite the archived release (Chicago style):

> Ikeda, Shōju. (2026). *KRM: Database of the Kanchi-in Manuscript of the Ruiju Myōgishō*. Version v1.2.7. Zenodo. https://doi.org/10.5281/zenodo.22164768

**BibTeX**

```bibtex
@misc{krm2026,
  author    = {Ikeda, Shōju},
  title     = {{KRM: Database of the Kanchi-in Manuscript of the Ruiju Myōgishō}},
  year      = 2026,
  month     = aug,
  version   = {v1.2.7},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.22164768},
  url       = {https://doi.org/10.5281/zenodo.22164768}
}
```

A machine-readable citation is also available in [CITATION.cff](CITATION.cff).

## Repository Structure

```
krm/
├── krm_main.tsv / .json              ← dataset files (repository root)
├── krm_notes.tsv / .json                (see Dataset Files below)
├── krm_headword_chars.tsv / .json
├── krm_wakun.tsv / .json
├── krm_pronunciations.tsv / .json
├── krm_ndl.tsv
├── krm.db                            ← read-only SQLite build of the TSVs (do not edit)
├── docs/                             ← detailed specifications and working notes
├── scripts/                          ← data-pipeline maintenance tools (MIT License)
├── examples/                         ← AI-assisted data analysis guide
├── webapp/                           ← search web application (MIT License)
├── images/                           ← ER diagrams
├── diff/                             ← correction-workflow logs produced by scripts/
├── CITATION.cff, LICENSE, README.md, README_jp.md
└── AGENTS.md, CLAUDE.md              ← guidance for AI coding assistants working in this repo
```

There is no separate `dataset/` directory: the TSV/JSON data files live directly at the repository root. `output/` and `work/` are local, `.gitignore`d working directories used by `scripts/` and are not part of the distributed dataset.

## Dataset Files

| File | Description | Formats |
|------|-------------|---------|
| [`krm_main`](docs/data_specification.md#krm_main) | Core data: headwords, full definitions, volume/radical, and location IDs. | TSV, JSON |
| [`krm_notes`](docs/data_specification.md#krm_notes) | Annotation data: each entry's definition broken into typed elements (character-form notes, phonetic glosses, semantic glosses, *wakun*, other), with compiler's remarks. | TSV, JSON |
| [`krm_headword_chars`](docs/data_specification.md#krm_headword_chars) | Per-character data for every constituent character of every headword, enabling single-character search. | TSV, JSON |
| [`krm_wakun`](docs/data_specification.md#krm_wakun) | Japanese native readings (*wakun*), with variant forms and links to the JapanKnowledge edition of the *Nihon Kokugo Daijiten*. | TSV, JSON |
| [`krm_pronunciations`](docs/data_specification.md#krm_pronunciations) | Phonetic gloss data aligned with the DHSJR column specification. | TSV, JSON |
| [`krm_ndl`](docs/data_specification.md#krm_ndl) | Links to National Diet Library Digital Collections page images. | TSV only |

`krm_notes.json` is large (~45 MB) and is **not tracked in this Git repository** (see `.gitignore`); it ships with the archived Zenodo release, or can be regenerated locally with `scripts/gen_notes_json.py` (see [Tools and Applications](#tools-and-applications)). All other files listed above are tracked in Git.

Full column-by-column specifications, old/new column-name mappings, and the ER diagrams live in [docs/data_specification.md](docs/data_specification.md).

## How to Use the Data

- **TSV files are the authoritative source** for all data in this repository. They begin with `#`-prefixed comment lines (containing the file's own version, dates, license, and column descriptions) before the header row — skip these when parsing.
- **JSON files are generated from the TSV files** (see `scripts/`, e.g. `tsv_to_json.py`, `gen_notes_json.py`) and are not edited by hand. They mirror the TSV data field-for-field, except `krm_notes.json`, which nests its records under each `krm_main` entry's `"definitions"` key rather than being a flat table (see [Data Model](#data-model)).
- **`krm.db`** is also generated from the TSV files (not from the JSON) — a read-only SQLite build used by `webapp/`. Do not edit it directly; it is a derivative, not source data.
- **Special notation** used across headword and definition fields (see [docs/data_specification.md](docs/data_specification.md#special-notation-conventions) for the full specification):

  | Symbol | Meaning |
  |--------|---------|
  | `_` | Kana *wakun* without tone marks |
  | `V` | Voiced-sound tone mark |
  | `（）` (full-width) | Presence of tone marks |
  | `〔〕` (full-width) | Correction proposal for a typo |
  | `［］` (full-width) | Missing characters |
  | `／` (full-width) | Separator for multi-character headwords |
  | `■` | Unrepresentable or unreadable character |
  | `〇` | Used in `original_entry` when no original-form headword is needed |

  Hanzi outside Unicode are represented via IDS (Ideographic Description Sequence) or CHISE/GlyphWiki entity references (e.g., `CDP-8C55`, `koseki-00001`).

## Data Model

`krm_main` is the root table; its primary key is `entry_id` (e.g., `F00001`).

- `krm_notes` links to `krm_main` via `entry_id`; its `definition_seq_id` (e.g., `F00001_01`) extends `entry_id` with a suffix (`_00` = headword, `_01`, `_02`, ... = definition elements in order).
- `krm_wakun` and `krm_pronunciations` link to `krm_notes` via `definition_seq_id`.
- `krm_headword_chars` links to `krm_main` via `entry_id` and uses `hanzi_id` (e.g., `S00001`) for individual character IDs.
- `krm_ndl` predates this key scheme and is matched to `krm_main` by comparing page numbers (see [docs/data_specification.md](docs/data_specification.md#krm_ndl)).

![ER diagram.](/images/krmer.drawio.png)

In the JSON distribution, `krm_notes` is nested inside each `krm_main` record under a `"definitions"` key rather than being a separate flat table:

![ER_notes diagram](/images/krm_notes_er.drawio.png)

See [docs/data_specification.md](docs/data_specification.md) for the full ER diagram walkthrough and a sample JSON record.

## Documentation

Detailed reference material lives in [docs/](docs/):

- [docs/data_specification.md](docs/data_specification.md) — full column-level specification for every dataset file, old/new column-name mappings, and the citation-abbreviation list used in compiler's remarks. ([Japanese version](docs/data_specification_jp.md))
- [docs/krm_scripts_usage.md](docs/krm_scripts_usage.md) — usage guide for the data-pipeline scripts in `scripts/` (Japanese).
- [docs/remarks_pronunciation_summary.md](docs/remarks_pronunciation_summary.md) — categorized summary of `remarks_pronunciation` values in `krm_pronunciations` (Japanese).
- [docs/manual_exclusion_list.md](docs/manual_exclusion_list.md) — log of manual corrections/exclusions for irregular tone-mark cases (Japanese).

## Tools and Applications

Built on top of the core dataset. **Utility Scripts** are maintainer-facing (used to produce and correct the data itself); **Web Application** and **Examples** are consumer-facing (used to search or analyze the published data).

### Utility Scripts

[`scripts/`](scripts/) contains the data-pipeline tools used to maintain `krm_pronunciations`, regenerate `krm_notes.json` (`gen_notes_json.py`), and convert any KRM TSV to JSON (`tsv_to_json.py`). Per [CLAUDE.md](CLAUDE.md), all changes to the dataset go through this pipeline rather than manual edits. Provided under the [MIT License](scripts/LICENSE). See [docs/krm_scripts_usage.md](docs/krm_scripts_usage.md) for full usage.

### Web Application

[`webapp/`](webapp/) is a Next.js + SQLite FTS5 search and browsing application for KRM (full-text search over headwords, definitions, and *wakun*, plus an approximate *itaiji* (variant-character) search). Provided under the [MIT License](webapp/LICENSE); see [webapp/README.md](webapp/README.md) for setup and architecture.

**External data**: the webapp's *itaiji* fuzzy search optionally uses the NIHU (National Institutes for the Humanities) 異体漢字対応テーブル (Itaiji Correspondence Table), a third-party dataset under **CC-BY 4.0**. It is not part of the KRM dataset and is not bundled in this repository — download it separately from [the NIHU research-data page](https://www.bridge.nihu.jp/researchdata/file/20221125_ITOBYb) and place it at the repository root as described in [webapp/README.md](webapp/README.md#4-異体字テーブルを配置任意推奨). Without it, the webapp still works; *itaiji* search is simply disabled.

### Examples

[`examples/README.md`](examples/README.md) is a guide to analyzing KRM using [Claude Code](https://claude.ai/code) in natural language — no programming knowledge required. It walks through sample questions (data-integrity checks, per-volume/per-radical aggregation, cross-table lookups) and their expected output, and shows how to save a recurring analysis as a reusable script.

## Version History

Each data file's exact version number, publication date, and last-modified date are recorded in that file's own `#`-prefixed comment header — treat those headers, not this README, as authoritative for current version state.

- **March 2022**: initial public release (`KRM.tsv` and related files, v1.1.x).
- **March 2025**: specification change to the current `krm_*` file set (v1.2.x) — see below.
- **2025-06-12**: `v1.2.6` archived on Zenodo.
- **2026-08-29**: `v1.2.7` archived on Zenodo and assigned the current citable DOI (see [Current Release and Citation](#current-release-and-citation)).
- Since then, the repository has continued with incremental corrections and additions (e.g., `krm_headword_chars` and `krm_pronunciations` were added after the initial v1.2 release); these are not individually re-archived on Zenodo.

### March 2025 Specification Change

Previously, published files were prefixed `KRM`; files following this change are prefixed `krm`. Key points:

- The at-mark `@`, indicating kana *wakun* without tone marks, was changed to underscore `_`.
- The double-quotation mark `"`, indicating a voiced-sound tone mark, was changed to the half-width letter `V`.
- Half-width parentheses `()`, indicating the presence of tone marks, were changed to full-width parentheses `（）`.
- Half-width parentheses `()` indicating a correction proposal for a typo were changed to full-width brackets `〔〕`.
- Half-width brackets `[]`, indicating missing characters, were changed to full-width brackets `［］`.
- `KRM_definitions.tsv` was retired; its data and functionality were absorbed into the new `krm_notes` (see [docs/data_specification.md](docs/data_specification.md#former-krm_definitions-file)).

## License

- **Data and documentation** (all files at the repository root, and `docs/`): [CC BY-SA 4.0](LICENSE).
- **`scripts/`** and **`webapp/`** source code: [MIT License](scripts/LICENSE) ([webapp/LICENSE](webapp/LICENSE)).
- **External datasets** (e.g., the NIHU *itaiji* table used by the webapp) retain their own license terms — see [Tools and Applications](#tools-and-applications).

This is open access data.

## Authors and Contact

HDIC Project
Representative: Shoju Ikeda (Professor Emeritus, Hokkaido University)
Copyright (c) 2022-2026 HDIC project, IKEDA Shoju (Chair, Professor Emeritus, Hokkaido University)

Contact: ikeda.shoju@gmail.com, liyuansapporo@yahoo.co.jp, toyjack@gmail.com, kleinekuma@gmail.com

## Acknowledgments

We would like to express our gratitude to Tenri Central Library and Yagi Bookstore for granting permission to publish the decipherment text of the Kanchi-in manuscript of the *Ruiju Myōgishō*.

This research is partly supported by JSPS KAKENHI Grant Numbers 16H03422, 19H00526, 23K17500, 25K00466, and 26K21717. We gratefully acknowledge this support.
