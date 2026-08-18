# KRM Data Specification

This document gives the full column-level specification for every KRM data file. For a quick orientation (what each file is for, how the files relate to each other, how to read them), see the [top-level README](../README.md) first.

> **Authoritative version/date information**: The version number, publication date, and last-modified date of each file are recorded in that file's own `#`-prefixed comment header (e.g., the first ~20 lines of `krm_main.tsv`). This document does not repeat those numbers, since they change independently of this documentation — check the file header for the current value. See [Version History](../README.md#version-history) in the top README for how this relates to the citable Zenodo release.

## Contents

- [Special Notation Conventions](#special-notation-conventions)
- [ER Diagram](#er-diagram)
- [krm_main](#krm_main)
- [krm_notes](#krm_notes)
- [krm_headword_chars](#krm_headword_chars)
- [krm_wakun](#krm_wakun)
- [krm_pronunciations](#krm_pronunciations)
- [krm_ndl](#krm_ndl)
- [Former krm_definitions file](#former-krm_definitions-file)
- [Appendix: Abbreviations of Cited Works](#appendix-abbreviations-of-cited-works)

## Special Notation Conventions

The following symbols appear across headword and definition fields (`hanzi_entry`, `original_entry`, `definition`, `definition_elements`, `wakun_*`, etc.) in multiple files. This is the v1.2 specification (in effect since the [March 2025 Specification Change](../README.md#march-2025-specification-change)).

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
| `〔抹消〕` | Used in `krm_headword_chars.entry_id` when the character was cancelled/struck through in the original manuscript and has no corresponding `krm_main`/`krm_notes` entry (see [krm_headword_chars](#krm_headword_chars)) |

Hanzi outside Unicode are represented via IDS (Ideographic Description Sequence) or CHISE/GlyphWiki entity references (e.g., `CDP-8C55`, `koseki-00001`).

## ER Diagram

The following ER diagram shows the relationship between the three core tables: `krm_main`, `krm_notes`, and `krm_wakun`. All three are linked by `entry_id`; `krm_notes` and `krm_wakun` further use `definition_seq_id` to identify individual definition elements within an entry.

![ER diagram.](/images/krmer.drawio.png)

In the JSON distribution, `krm_notes` is not a separate flat table — it is nested inside each `krm_main` record under the key `"definitions"`. The following diagram shows this nested structure.

![ER_notes diagram](/images/krm_notes_er.drawio.png)

## krm_main

### Overview and file formats

This section describes the core file of the KRM database (KRM being short for the Kanchi-in manuscript of the *Ruiju Myōgishō*, hereinafter "*Myōgishō*").

Previously, the released file was a TSV file named `KRM.tsv`. It contains information regarding **`Headwords`**, the full content of the **`Definition (Original Glosses)`**, volume, radical, and the locations in the Kazama Shobō edition and the Tenri Central Library/Yōtokusha (Tenri Zenhon Sōsho) edition.

In March 2025, the specifications for column names and the display method for **`Tone marks (*shōten*)`** were updated (see [Notes on the March 2025 Specification Change](../README.md#march-2025-specification-change) in the top README). To clearly indicate that it is the file with these updated specifications, it was renamed `krm_main.tsv`. A JSON version of this file is also available.

### Column name comparison

The correspondence between the old and new column names is as follows:

| New Column Name (v1.2.x) | Old Column Name (v1.1.347) |
|--------------------------|----------------------------|
| entry_id                 | KRID_n                     |
| hanzi_id                 | KRID_sn                    |
| -                        | KR2ID                      |
| kazama_location          | KRID                       |
| tenri_location           | KR_Tenri_p                 |
| volume_name              | KR_vol_name                |
| radical_name             | KR_radical                 |
| volume_radical_index     | KR_vol_radical              |
| hanzi_entry              | Entry                      |
| original_entry           | Entry_original             |
| definition               | Def                        |
| -                        | Remarks                    |

The `KR2ID` column was omitted, and the `kazama_location` column was aligned with the `KRID` column.

The `Remarks` column was omitted; this information is now consolidated in the `krm_notes` file (which contains data for the **`Compiler's Remarks`**).

### Description of each column

| Column Name              | Explanation                 |
| :------------------------ | :------------------------- |
| entry_id                 | A heading **`Entry`** ID consisting of a 5-digit numeric ID starting with 'F'. For some added entry items, a 'b' suffix is appended. |
| hanzi_id                 | A heading **`Hanzi (Chinese character)`** ID consisting of a 5-digit numeric ID starting with 'S'. For some added entry items, a 'b' suffix is appended. |
| kazama_location          | An ID indicating K + Volume (2 digits) + Kazama Edition Page (3 digits) + Line (1 digit) + Segment (1 digit) + Character order (字順, *jijun*) (1 digit). Details of the rules for assigning Character order are defined separately. |
| tenri_location           | An ID indicating T + Volume (a/b/c) + Tenri Edition Page (3 digits) + Line (1 digit) + Segment (1 digit) + Character order (字順, *jijun*) (1 digit). Details of the rules for assigning Character order are defined separately. |
| volume_name              | Name of the volume, consisting of 10 volumes: 仏上, 仏中, 仏下本, 仏下末, 法上, 法中, 法下, 僧上, 僧中, and 僧下. |
| radical_name              | Name of the radical, consisting of 120 radicals ranging from 人 to 雑, used to classify **`Hanzi (Chinese characters)`**. |
| volume_radical_index     | Volume and radical number, ranging from v1#1 (Volume 1, Radical 1) to v10#120 (Volume 10, Radical 120), indicating the location of the **`Entry`** within the text. (Corresponds to 第1帖仏上 to 第10帖僧下). |
| hanzi_entry              | The collated **`Headword`** (校訂漢字) principally uses Kangxi Dictionary form, including Unicode simplified **Chinese characters** (common-use forms, popular variants). For **Chinese characters** not included in Unicode, they are represented by the following methods: if representable by combining **Chinese character** components, input using IDS (Ideographic Description Sequence); for specific characters or components where IDS or standard Unicode is difficult, simplified notations based on the entity reference systems of CHISE and GlyphWiki are used (e.g., `CDP-8C55`, `koseki-00001`). Characters not representable by any of the above methods, or unreadable in the original text (due to damage such as wormholes), are input as '■' (black square). **`Headwords`** consisting of multiple characters are separated by '／' (full-width slash). The abbreviation symbol '｜' is indicated by 'ー' (long vowel mark), and the corresponding character is appended in full-width parentheses（）. |
| original_entry           | **`Headword`** based on the original character form. Typographical errors in the original are preserved. The representation of characters outside Unicode follows the rules for `hanzi_entry`. If the original-form **`Headword`** is not needed, '〇' is used. |
| definition                | The content of this `definition` column represents the **`Definition (Original Glosses)`**. It includes **`Notes on Character Form`**, **`Phonetic Glosses`**, **`Semantic Glosses in Chinese`**, **`Japanese Native Readings (*wakun*)`**, and **Other** relevant information, separated by spaces. As a general rule, character forms included in the "Kangxi Dictionary style" should be used. |

## krm_notes

### Overview and file formats

`krm_notes.tsv`/`krm_notes.json` breaks each entry's `definition` (from `krm_main`) into individually classified, source-annotated elements, incorporating detailed annotation information that was previously spread across `KRM_definitions.tsv` and `KRM.tsv`. It is available in both TSV and JSON formats.

Unlike the other JSON files, which are flat (one object per TSV row), `krm_notes.json` is grouped by `entry_id`, with the entry-level fields (`kazama_location`, `hanzi_entry`, etc.) given once and the definition elements nested underneath as a `"definitions"` array (see [Data structure](#data-structure-er-diagram-and-json-implementation) below). It is generated from `krm_notes.tsv` with the dedicated `scripts/gen_notes_json.py`, not the generic `scripts/tsv_to_json.py` — the latter would either produce a flat list (one object per row, entry-level fields repeated in every row) or, with `--group-by entry_id`, a `{ "F00001": [rows...], ... }` dict where each row still repeats the entry-level fields, which is a different shape from the `"definitions"`-nested format described here.

### Column name comparison

#### Comparison with KRM_definitions.tsv (v1.1.55)

| New Column Name (krm_notes) | Old Column Name (KRM_definitions v1.1.55) |
|--------------------------|----------------------------|
| definition_seq_id        | KRID_no                    |
| kazama_location          | KRID                       |
| hanzi_entry              | Entry                      |
| definition_elements      | Def                        |
| definition_type_code     | Def_code                   |
| definition_type_name     | Def_name                   |
| remarks                  | Remarks                    |

#### Incorporation of KRM.tsv (v1.1.347) content

`krm_notes.tsv` also incorporates information previously stored in `KRM.tsv`:

| New Column Name (krm_notes) | Old Column Name (KRM v1.1.347) |
|--------------------------|----------------------------|
| entry_id                 | KRID_n                     |
| tenri_location           | KR_Tenri_p                 |
| volume_name              | KR_vol_name                |
| radical_name             | KR_radical                 |
| volume_radical_index     | KR_vol_radical              |
| original_entry           | Entry_original             |

### Data structure: ER diagram and JSON implementation

In the ER diagram, `krm_notes` is shown as a child table linked to `krm_main` by `entry_id`, with a one-to-many relationship. In the actual **JSON** distribution, however, this is not a separate flat table — it is implemented as a nested array of objects under the key `"definitions"` within each `krm_main` record.

![ER_notes diagram](/images/krm_notes_er.drawio.png)

Each object inside the `definitions` array corresponds to one definition note and contains the following fields:

- `definition_seq_id`
- `definition_elements`
- `definition_type_code`
- `definition_type_name`
- `remarks`

**Example JSON:**

```json
{
  "entry_id": "F00001",
  "...": "...",
  "definitions": [
    {
      "definition_seq_id": "F00001_01",
      "definition_elements": "音仁（LV）「ニン」",
      "definition_type_code": "215",
      "definition_type_name": "音注声点有_類音注等",
      "remarks": "広韻「如鄰切」..."
    }
  ]
}
```

### Description of each column

| Column Name              | Explanation                 |
| :------------------------ | :------------------------- |
| entry_id                 | A heading **`Entry`** ID consisting of a 5-digit numeric ID starting with 'F'. For some newly added **`Entries`**, a 'b' suffix is appended. |
| definition_seq_id        | An identifier for each component of the **`Definition (Original Glosses)`** or for the **`Headword`** itself within an **`Entry`**. It is formed by appending a sequential suffix (e.g., "_00" for the **`Headword`**/overall **`Entry`** note, "_01", "_02" for subsequent elements in order of appearance) to the 5-digit numeric part of the corresponding `entry_id`. |
| kazama_location          | See [krm_main](#krm_main). |
| tenri_location           | See [krm_main](#krm_main). |
| volume_name              | See [krm_main](#krm_main). |
| radical_name              | See [krm_main](#krm_main). |
| volume_radical_index     | See [krm_main](#krm_main). |
| hanzi_entry              | See [krm_main](#krm_main). |
| original_entry           | See [krm_main](#krm_main). |
| definition_elements      | Extracted individual elements from the full **`Definition (Original Glosses)`**, classified into five types: **`Notes on Character Form`**, **`Phonetic Gloss`**, **`Semantic Gloss in Chinese`**, **`Japanese Native Reading (*wakun*)`**, and **`Other`** information. Each record typically corresponds to one such element. |
| definition_type_code     | A 3-digit numeric code representing the type of element from the **`Definition (Original Glosses)`**. |
| definition_type_name     | Indicates which of the five categories above the element belongs to. |
| remarks                  | **`Compiler's Remarks`**: notes by the database compilers providing additional context, scholarly observations, results of textual collation, or source investigations. See [below](#content-and-significance-of-compilers-remarks). |

### Content and significance of Compiler's Remarks

The `remarks` column stores the **`Compiler's Remarks`** — annotations by the database creators, not part of the *Myōgishō*'s original text. It provides:

- **Additional context**: supplementary background or related information aiding understanding of the entry.
- **Scholarly observations**: philological or linguistic perspectives, including references to previous research.
- **Results of textual collation**: findings from comparison with variant manuscripts, and interpretations based on those comparisons.
- **Source investigations**: findings on the textual sources of an entry, including references to prior studies.

Each remark is associated with either a specific `definition_element` (an individual component of the original glosses, as itemized in `krm_notes`) or the `Headword` itself.

## krm_headword_chars

### Overview and file formats

**`Headwords`** in the *Myōgishō* can consist of a single character or of multiple characters (compounds). `krm_main`, `krm_notes`, and `krm_wakun` are all structured one row per **`Entry`**, so for multi-character headwords, characters after the first cannot be referenced directly from those files.

`krm_headword_chars` provides a complete list of every constituent character of every headword, ordered by entry sequence and then by position within the headword — enabling character-level search, image display, and analysis. It is provided in TSV and JSON formats.

### Description of each column

| Column Name          | Explanation      |
| :------------------- | :------------------------------------------------------ |
| hanzi_id             | A sequential ID assigned to each **`Headword`** (single or multi-character) in the order of its appearance in the *Myōgishō*. A 5-digit numeric ID starting with 'S'. |
| entry_id             | The ID of the **`Entry`** (from `krm_main`) to which the headword containing this character belongs. A 5-digit numeric value starting with 'F'; some added entries have a 'b' suffix. A small number of rows use `〔抹消〕` instead: these document a character that was cancelled/struck through in the original manuscript and therefore has no corresponding `krm_main`/`krm_notes` entry. The row is kept (rather than deleted) so the character sequence on the page is not misread as missing data. |
| constituent_char     | The constituent character itself. Abbreviation marks (ー) and iteration marks (〻) are converted to the actual characters they represent. Collated characters are, in principle, Kangxi Dictionary forms. For detailed collation notes, see `krm_notes`. |
| character_order      | The numerical order of appearance of the character within its headword. |
| kazama_location_id   | K + Volume (2 digits) + Page (3 digits) + Line (1 digit) + Segment (1 digit) + Character Order in Segment (1 digit) — this character's location in the Kazama Edition. |
| tenri_location_id    | T + Volume (a/b/c) + Page (3 digits) + Line (1 digit) + Segment (1 digit) + Character Order in Segment (1 digit) — this character's location in the Tenri Edition. |
| img_file_name        | File name of the cropped image for this character (`.jpg`). 7 digits for Volumes 1–9, 8 digits for Volume 10 (first digit/two digits indicate the volume). The remaining digits follow an internal ordering rule that predates this project and is not separately documented. Null if no image is available. |

## krm_wakun

### Overview and file formats

This file is derived by extracting **`Japanese Native Readings (*wakun*)`** from the *Myōgishō* data, organizing variant forms of *wakun*, and adjusting their correspondence with **`variant characters (*itaiji*)`**.

Collation notes and source investigations for *wakun* are documented in `krm_notes`, so they are omitted here.

Some *wakun* entries carry a second reading written as a small annotation beside the main one — e.g., the *wakun* "マサル" (masaru) is assigned to "倍", with "ス" written in small katakana beside "ル", indicating that "マス" (masu) is also a recorded reading. Support for this side-by-side notation is needed because the JapanKnowledge edition of the *Nihon Kokugo Daijiten* (2nd ed.) is being cross-referenced into this data.

The correspondence with *itaiji* was adjusted because *Myōgishō* headwords sometimes present variant forms together — e.g., the *wakun* "ヤツカレ" appears under the headword "㒒／僕", and is a reading for both "僕" and "㒒". The relationship between standard and variant forms such as "爲"/"為" or "來"/"来" is handled the same way; this mirrors the "Notation" (表記) field of the JapanKnowledge *Nihon Kokugo Daijiten*, which records *Myōgishō* character notations.

### Column name comparison

| New Column Name (v1.2.x) | Old Column Name (v1.1.97) |
|-------------------------|---------------|
| wakun_id                | KRID_wakun_no |
| definition_seq_id       | KRID_no       |
| kazama_location          | KR2ID         |
| hanzi_entry              | Entry         |
| wakun_elements           | Def           |
| wakun_form               | Word_form     |
| wakun_standard_hanzi     | Wakun_Hanzi   |
| wakun_variant_in_hanzi   | Wakun_variant |
| variant_hanzi_for_wakun  | Hanzi_variant |
| japan_knowledge_id       | JK_URL        |
| -                        | Remarks       |

`Remarks` has been omitted, as this information is now consolidated in `krm_notes`.

### Description of each column

| Column Name                | Explanation                                                                                                                                                                                                                                                           |
| :-------------------------- | :-------------------------------------------------- |
| wakun_id                   | An ID for each *wakun*, derived from `definition_seq_id` by extracting only elements whose type is *wakun*. Suffixes 'b', 'c', 'd' are appended for the side-by-side variant readings described above. |
| definition_seq_id          | See [krm_notes](#krm_notes). Links to the corresponding record in `krm_notes`. |
| kazama_location             | ID with location info (Kazama edition: volume, page, line, column); when multiple entries share a column, they are ranked 1, 2, ..., n. |
| hanzi_entry                 | The headword (in Hanzi) to which this *wakun* pertains. |
| wakun_elements              | The extracted *wakun* element(s) from the full definition. |
| wakun_form                  | The lexical (dictionary/citation) form of the *wakun*, excluding particles; the particles "no" and "to" from *Monzen* (文選)-style readings are omitted. |
| wakun_standard_hanzi        | Notation of the *wakun* using standard Hanzi. |
| wakun_variant_in_hanzi      | Notation of a variant form of the *wakun* using standard Hanzi. |
| variant_hanzi_for_wakun     | Notation of the *wakun* using *itaiji* (variant Hanzi forms). |
| japan_knowledge_id          | If this *wakun* exists as a headword in the JapanKnowledge *Nihon Kokugo Daijiten* (2nd ed.), the alphanumeric part of its URL (from "20020" onward); otherwise "null". |

## krm_pronunciations

### Overview and file formats

The **`Phonetic Glosses`** in the *Myōgishō* include **`Fanqie spellings`** (反切), **`Similar sound notes`** (類音注, *ruion-chū*), and **`Kana glosses`** (仮名注, *kana-chū*), often accompanied by **`Tone marks (*shōten*)`**.

This file aligns KRM's phonetic-gloss data with the column specification of the **Database of Historical Sino-Japanese Readings** (DHSJR), developed by Professor Katō Taitsuru and others, to allow cross-referencing between the two databases. `pronunciation_id` is the primary key; `definition_seq_id` (linking to `krm_notes`) is the foreign key. A classification field, `annotation_format`, categorizes the diverse phonetic-gloss formats found in the *Myōgishō*. DHSJR itself uses Japanese column names; HDIC uses English column names for internal processing convenience.

HDIC-original column names (not present in DHSJR) are in **bold** below.

### Column name comparison

| DHSJR (Japanese) | HDIC (English)            | Key         | Explanation                                                                 |
| :--------------- | :------------------------ | :---------- | :--------------------------------------------------------------------------------- |
| ID               | dhsjr_id                  |             | DHSJR unique ID for a single Hanzi character (integrated data only). Currently empty pending finalization of official IDs by the DHSJR project. |
| 音注ID           | **`pronunciation_id`**    | Primary Key | ID for each **`Phonetic Gloss`**, derived from `definition_seq_id` by extracting elements typed as **`Phonetic Gloss`** in `krm_notes`. Suffixes 'b', 'c', 'd' mark variant forms. |
| 注文ID           | **`definition_seq_id`**   | Foreign Key | Links to the corresponding record in `krm_notes`/`krm_main`. |
| 資料番号         | material_id               |             | Material ID. |
| 資料名           | material_name             |             | Name of the material. |
| 資料内漢字番号   | material_character_index  |             | Sequential number of a character's appearance in the material. Numbers 1–27978 follow the manuscript's physical order; numbers ≥30001 are records added after initial encoding (e.g., annotation characters later identified as needing a separate entry) and do not correspond to a physical position. |
| 資料内漢語番号   | material_word_index       |             | Sequential number of a Chinese word's appearance in the material. |
| 単字＿見出し     | character_headword        |             | Headword column for the character bearing the phonetic gloss. |
| 単字＿出現形     | character_form            |             | The character bearing the phonetic gloss. |
| 漢語＿見出し     | word_headword              |             | Headword column of the Chinese word containing that character. |
| 漢語＿出現形     | word_form                 |             | The Chinese word containing that character. |
| 漢語＿alphabet   | word_alpha                |             | Alphabetic representation of the Chinese word, when present. |
| 語種             | word_type                 |             | Word type for mixed-language (e.g. hybrid Sino-Japanese) words. |
| 漢語内位置       | word_position              |             | Position of the character within the Chinese word. |
| 単字長           | character_mora_count       |             | Number of morae for the character. |
| 声点             | tone_marks                 |             | Tone marks for the character: Four Tones (平上去入), Six Tones (平平軽上去入軽入), and voicing (清濁). |
| 声点型           | tone_pattern               |             | Combination of tone marks for the Chinese word; characters without tone marks are represented by ＊. |
| 仮名注           | kana_notes                 |             | Kana gloss for the character, including kana-based fanqie. |
| 仮名型           | kana_pattern                |             | Combination of kana glosses for the word; characters without a kana gloss are represented by ＊. |
| 反切             | fanqie                    |             | Fanqie spelling for the character. |
| 類音             | similar_sound              |             | Similar-sound note for the character. |
| 音注型           | **`annotation_format`**   |             | Pattern of combined phonetic information (kana gloss, fanqie, similar sound, tone marks, etc.). |
| 節博士           | fushi_hakase                |             | Fushi-hakase notation (melodic/intonational marking) for musical materials such as *Shōmyō* chant. |
| その他           | other_phonetic_annotations |             | Other types of phonetic gloss. |
| 出現位置         | material_location           |             | Location of the character/word within the material, in the format K + Volume (2 digits) + Kazama Edition Page (3 digits) + Line (1 digit) + Segment (1 digit) — e.g. `K0201474` = Volume 2, Page 14, Line 7, Segment 4. |
| 備考             | remarks_pronunciation       |             | Notes on this phonetic element. See [docs/remarks_pronunciation_summary.md](remarks_pronunciation_summary.md) for a categorized summary of values used, and [docs/manual_exclusion_list.md](manual_exclusion_list.md) for the manual correction/exclusion log for irregular tone-mark cases. |

## krm_ndl

Links each location in the *Myōgishō* to its corresponding page image in the National Diet Library Digital Collections. Distributed as `krm_ndl.tsv` only (no JSON).

| Column  | Explanation |
|---------|-------------|
| Book    | Volume name (帖名). |
| Radical | Radical character (部首字). |
| Kazama  | Kazama edition page number. |
| Tenri   | Tenri edition page number. |
| NDL_url | URL of the corresponding page image in the National Diet Library Digital Collections. |

Sample:

| Book | Radical | Kazama | Tenri | NDL_url                                       |
|------|---------|--------|-------|-----------------------------------------------|
| 仏上   | 人       | 1      | 23    | https://dl.ndl.go.jp/info:ndljp/pid/2586891/6 |
| 仏上   | 人       | 2      | 24    | https://dl.ndl.go.jp/info:ndljp/pid/2586891/7 |

This file predates the March 2025 specification change and does not yet share a join key (such as `entry_id`) with `krm_main`; matching a location to an entry currently requires comparing `Kazama`/`Tenri` page numbers against `kazama_location`/`tenri_location`.

## Former krm_definitions file

Before the March 2025 specification change, a separate `KRM_definitions.tsv` file provided the individual elements of each entry's definition (character-form notes, phonetic glosses, semantic glosses, etc.), classified by type and ordered by appearance. Its data and functionality have been fully absorbed into `krm_notes` (see the [column comparison](#comparison-with-krm_definitionstsv-v155) above); there is no current `krm_definitions` file, and no separate specification is maintained for it.

## Appendix: Abbreviations of Cited Works

Compiler's Remarks (the `remarks` / `remarks_pronunciation` columns) frequently cite prior scholarship using short abbreviations. These abbreviations are also embedded in the comment headers of `krm_main.tsv`, `krm_notes.tsv`, and `krm_wakun.tsv`; the list below adds English translations.

For each entry, the original Japanese notation is given first, followed by an English translation, with Romanization in parentheses where useful.

- 正宗索引: 正宗敦夫編, 類聚名義抄 仮名索引, 日本古典全集刊行会, 1939-1940
  Masamune Index: Edited by Masamune Atsuo, *Kana Index to the Ruiju Myogisho*, Nihon Koten Zenshu Kankokai, 1939-1940
  (Romanization: Masamune Sakuin: Masamune Atsuo hen, *Ruiju Myōgishō Kana Sakuin*, Nihon Koten Zenshū Kankōkai, 1939-1940)
- 岡田研究: 岡田希雄, 類聚名義抄の研究, 一条書房, 1944
  Okada Research: Okada Mareo, *Research on the Ruiju Myogisho*, Ichijo Shobo, 1944
  (Romanization: Okada Kenkyū: Okada Mareo, *Ruiju Myōgishō no Kenkyū*, Ichijō Shobō, 1944)
- 望月和訓集成: 望月郁子編, 類聚名義抄: 四種声点付和訓集成, 笠間書院, 1974
  Mochizuki Wakun Collection: Edited by Mochizuki Ikuko, *Ruiju Myogisho: Collection of Four Types of Wakun with Tone Marks*, Kasama Shoin, 1974
  (Romanization: Mochizuki Wakun Shūsei: Mochizuki Ikuko hen, *Ruiju Myōgishō: Shishu Shōten-tsuki Wakun Shūsei*, Kasama Shoin, 1974)
- 中村文選: 中村宗彦, 九条本文選古訓集, 風間書房, 1983
  Nakamura Monzen: Nakamura Munehiko, *Old Japanese Readings of the Kujo Text of the Wen Xuan*, Kazama Shobo, 1983
  (Romanization: Nakamura Monzen: Nakamura Munehiko, *Kujō-bon Monzen Kokunshū*, Kazama Shobō, 1983)
- 草川和訓集成: 草川昇編, 五本対照類聚名義抄和訓集成, 汲古書院, 2000
  Kusakawa Wakun Collection: Edited by Kusakawa Noboru, *Comparative Collection of Wakun from Five Texts of the Ruiju Myogisho*, Kyuko Shoin, 2000
  (Romanization: Kusakawa Wakun Shūsei: Kusakawa Noboru hen, *Gohon Taishō Ruiju Myōgishō Wakun Shūsei*, Kyūko Shoin, 2000)
- 西端誤写考察: 西端幸雄, 類聚名義抄における誤写の考察, 訓点語と訓点資料45, 1971
  Nishihata Miscopy Study: Nishihata Yukio, A Study on Miscopies in the *Ruiju Myogisho*, Kunten-go to Kunten Shiryo 45, 1971
  (Romanization: Nishihata Gosha Kōsatsu: Nishihata Yukio, *Ruiju Myōgishō* ni okeru Gosha no Kōsatsu, Kunten-go to Kunten Shiryō 45, 1971)
- 西端誤写諸例: 西端幸雄, 類聚名義抄における誤写の諸例, 訓点語と訓点資料52，1973
  Nishihata Miscopy Examples: Nishihata Yukio, Examples of Miscopies in the *Ruiju Myogisho*, Kunten-go to Kunten Shiryo 52, 1973
  (Romanization: Nishihata Gosha Shorei: Nishihata Yukio, *Ruiju Myōgishō* ni okeru Gosha no Shorei, Kunten-go to Kunten Shiryō 52, 1973)
- 略注: 佐藤喜代治，色葉字類抄略注，明治書院，1995
  Brief Notes: Sato Kiyoji, *Brief Notes on the Iroha Jirui Sho*, Meiji Shoin, 1995
  (Romanization: Ryakuchū: Satō Kiyoji, *Iroha Jirui Shō Ryakuchū*, Meiji Shoin, 1995)
- 群書治要: 小林芳規・原卓志・山本秀人・山本真吾・佐々木勇編, 宮内庁書陵部蔵本群書治要経部語彙索引, 汲古書院, 1996
  Gunsho Chiyo: Edited by Kobayashi Yoshinori, Hara Takushi, Yamamoto Hideto, Yamamoto Shingo, Sasaki Isamu, *Index to the Vocabulary of the Classics Section of the Gunsho Chiyo*, Imperial Household Agency Archives Collection, Kyuko Shoin, 1996
- 毛詩鄭箋: 毛詩鄭箋（一）（二）（三）, 古典研究会叢書漢籍之部１～３, 原本所蔵静嘉堂文庫, 汲古書院, 1992
  Mao Shi Zheng Jian: Mao Shi Zheng Jian (1) (2) (3), Series of the Classical Studies Association, Chinese Classics Section 1-3, Original Texts in the Seikado Bunko, Kyuko Shoin, 1992
