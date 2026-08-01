# 観智院本類聚名義抄データベース（KRM）

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15638843.svg)](https://doi.org/10.5281/zenodo.15638843)

*[English README (README.md)](README.md)* — このリポジトリの一次的な入口は英語版READMEであり、日本語版はその構成をそのまま反映したものである。

## 概要

このデータベースは、観智院本類聚名義抄（略称KRM）の全文をテキストデータベース化し、所在情報、本文校勘、出典考証などを行ったものであり、平安時代漢字字書総合データベース（略称HDIC）を構成する漢字字書データベースのひとつである。

観智院本類聚名義抄は、十二世紀に成立した漢字の字書であり、真言宗の僧侶によって編纂された。アクセントを示した和訓、詳細な漢字音の注記、異体字の注記を大量に収録することから、日本語史研究の重要資料とされてきた。また、反切、意義注、字体注の漢文注記は、中国語学の資料としても注目されている。

KRMは2022年3月に初版を公開した。2025年3月に、仕様の変更（[バージョン履歴](#バージョン履歴)参照）と、より詳細な説明を施した改訂版を公開した。

### Kanji と Hanzi

平安時代に日本で編纂された漢字字書は、日本語学のみならず中国語学にとっても貴重な資料である。国際的な学術交流を促進するため、本プロジェクトでは "Hanzi" という用語を用いている。日本語研究を専門とする研究者は、この用語を「Kanji」と読み替えても差し支えない。これは、両分野の言語的多様性と学術的伝統を尊重しつつ、より広い学術交流を促すことを意図したものである。

## 現行リリースと引用

Zenodoにアーカイブされている引用可能なリリースは **v1.2.6**（2025年6月12日公開）である。リポジトリ自体はこのスナップショット以降も継続的に更新されている。両者の関係は[バージョン履歴](#バージョン履歴)を参照。

学術目的でKRMを利用する場合は、以下のように引用されたい（Chicago Style）：

> Ikeda, Shōju. (2025). *KRM: Database of the Kanchi-in Manuscript of the Ruiju Myōgishō*. Version v1.2.6. Zenodo. https://doi.org/10.5281/zenodo.15638843

**BibTeX**

```bibtex
@misc{krm2025,
  author    = {Ikeda, Shōju},
  title     = {{KRM: Database of the Kanchi-in Manuscript of the Ruiju Myōgishō}},
  year      = 2025,
  month     = jun,
  version   = {v1.2.6},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.15638843},
  url       = {https://doi.org/10.5281/zenodo.15638843}
}
```

機械可読な引用情報は[CITATION.cff](CITATION.cff)にも用意している。

## リポジトリ構成

```
krm/
├── krm_main.tsv / .json              ← データファイル本体（リポジトリ直下）
├── krm_notes.tsv / .json                （詳細は下記「データファイル一覧」）
├── krm_headword_chars.tsv / .json
├── krm_wakun.tsv / .json
├── krm_pronunciations.tsv / .json
├── krm_ndl.tsv
├── krm.db                            ← TSVから生成した読み取り専用SQLite（直接編集禁止）
├── docs/                             ← 詳細仕様・作業メモ
├── scripts/                          ← データパイプライン用ツール（MIT License）
├── examples/                         ← AIを使ったデータ分析ガイド
├── webapp/                           ← 検索Webアプリ（MIT License）
├── images/                           ← ER図
├── diff/                             ← scripts/による修正ワークフローのログ
├── CITATION.cff, LICENSE, README.md, README_jp.md
└── AGENTS.md, CLAUDE.md              ← AIコーディングアシスタント向けの運用ルール
```

`dataset/`という独立ディレクトリはなく、TSV/JSONデータファイルはリポジトリ直下に置かれている。`output/`・`work/`は`scripts/`が使用するローカルの`.gitignore`対象作業ディレクトリであり、配布データには含まれない。

## データファイル一覧

| ファイル | 説明 | 形式 |
|------|-------------|---------|
| [`krm_main`](docs/data_specification_jp.md#krm_main) | 基本データ。掲出字、注文全文、巻・部首、所在IDを含む。 | TSV, JSON |
| [`krm_notes`](docs/data_specification_jp.md#krm_notes) | 注釈データ。各項目の注文を種類別（字体注・音注・意義注・和訓・その他）の要素に分解し、編者注記を付したもの。 | TSV, JSON |
| [`krm_headword_chars`](docs/data_specification_jp.md#krm_headword_chars) | すべての掲出字を構成する文字ごとのデータ。1文字単位の検索を可能にする。 | TSV, JSON |
| [`krm_wakun`](docs/data_specification_jp.md#krm_wakun) | 和訓データ。異形、および『日本国語大辞典第二版』（ジャパンナレッジ版）へのリンクを含む。 | TSV, JSON |
| [`krm_pronunciations`](docs/data_specification_jp.md#krm_pronunciations) | DHSJRのカラム仕様に合わせた音注データ。 | TSV, JSON |
| [`krm_ndl`](docs/data_specification_jp.md#krm_ndl) | 国立国会図書館デジタルコレクションの画像へのリンク。 | TSVのみ |

`krm_notes.json`は約45MBあり、**このGitリポジトリには含まれていない**（`.gitignore`参照）。Zenodoにアーカイブされたリリースには含まれるほか、`scripts/gen_notes_json.py`でローカルに再生成できる（[ツール・アプリケーション](#ツールアプリケーション)参照）。上記のその他のファイルはすべてGit管理下にある。

各ファイルのカラムレベルの詳細仕様、新旧カラム名対照、ER図は[docs/data_specification_jp.md](docs/data_specification_jp.md)を参照。

## データの使い方

- **TSVファイル**は、ヘッダー行の前に`#`で始まるコメント行（そのファイル自身のバージョン・日付・ライセンス・カラム説明を含む）がある。パース時はこれを読み飛ばすこと。
- **JSONファイル**はTSVと同内容を反映するが、`krm_notes.json`は平坦なテーブルではなく、各`krm_main`エントリの`"definitions"`キー以下に入れ子で格納されている（[データモデル](#データモデル)参照）。
- **`krm.db`**は、TSVファイルから生成した読み取り専用のSQLiteデータベースで、`webapp/`が使用する。ソースデータではないため、直接編集しないこと。
- 掲出字・注文に用いられる**特殊表記**（詳細は[CLAUDE.md](CLAUDE.md)を参照）：

  | 記号 | 意味 |
  |--------|---------|
  | `_` | 声点のない仮名和訓 |
  | `V` | 濁音の声点 |
  | `（）`（全角） | 声点の存在 |
  | `〔〕`（全角） | 誤字の訂正案 |
  | `［］`（全角） | 脱字 |
  | `／`（全角） | 複数漢字の見出しの区切り |
  | `■` | 表現不能・判読不能な文字 |
  | `〇` | `original_entry`で原字形の掲出字が不要な場合に使用 |

  Unicode外の漢字は、IDS（漢字構成記述文字列）またはCHISE/GlyphWikiの実体参照（例：`CDP-8C55`、`koseki-00001`）で表現する。

## データモデル

`krm_main`が起点となるテーブルであり、主キーは`entry_id`（例：`F00001`）である。

- `krm_notes`は`entry_id`で`krm_main`と連結する。その`definition_seq_id`（例：`F00001_01`）は`entry_id`に接尾辞を追加したもの（`_00`＝見出し、`_01`、`_02`…＝注文要素を出現順に並べたもの）である。
- `krm_wakun`・`krm_pronunciations`は`definition_seq_id`で`krm_notes`と連結する。
- `krm_headword_chars`は`entry_id`で`krm_main`と連結し、個々の文字IDには`hanzi_id`（例：`S00001`）を用いる。
- `krm_ndl`はこのキー体系以前に公開されたファイルであり、頁数の照合によって`krm_main`と対応づける（[docs/data_specification_jp.md](docs/data_specification_jp.md#krm_ndl)参照）。

![ER図](/images/krmer.drawio.png)

JSON形式では、`krm_notes`は独立した平坦なテーブルではなく、各`krm_main`レコードの`"definitions"`キー以下に入れ子で格納される。

![ER_notes図](/images/krm_notes_er.drawio.png)

ER図の詳しい説明とJSONレコードの例は[docs/data_specification_jp.md](docs/data_specification_jp.md)を参照。

## ドキュメント

詳細な参考資料は[docs/](docs/)にまとめている。

- [docs/data_specification_jp.md](docs/data_specification_jp.md) — 各データファイルのカラムレベルの詳細仕様、新旧カラム名対照、編者注記で用いる引用書略称一覧。（[English version](docs/data_specification.md)）
- [docs/krm_scripts_usage.md](docs/krm_scripts_usage.md) — `scripts/`内のデータパイプラインツールの使い方。
- [docs/remarks_pronunciation_summary.md](docs/remarks_pronunciation_summary.md) — `krm_pronunciations`の`remarks_pronunciation`カラムの値を分類したまとめ。
- [docs/manual_exclusion_list.md](docs/manual_exclusion_list.md) — 上声全濁字の声点異例に関する手動補正・除外の記録。

## ツール・アプリケーション

データセット本体の上に構築されたツール群。**Utility Scripts**はメンテナ向け（データそのものの生成・修正に使用）、**Web Application**と**Examples**は利用者向け（公開データの検索・分析に使用）である。

### Utility Scripts

[`scripts/`](scripts/)には、`krm_pronunciations`のメンテナンス、`krm_notes.json`の再生成（`gen_notes_json.py`）、任意のKRM TSVをJSONに変換する（`tsv_to_json.py`）ためのデータパイプラインツールが含まれる。[CLAUDE.md](CLAUDE.md)にあるとおり、データへの変更はすべてこのパイプライン経由で行い、手動編集は行わない。[MIT License](scripts/LICENSE)のもとで提供。使い方の詳細は[docs/krm_scripts_usage.md](docs/krm_scripts_usage.md)を参照。

### Web Application

[`webapp/`](webapp/)は、Next.js + SQLite FTS5によるKRMの検索・閲覧Webアプリである（見出し字・定義文・和訓の全文検索に加え、異体字の曖昧検索機能を持つ）。[MIT License](webapp/LICENSE)のもとで提供。セットアップと構成の詳細は[webapp/README.md](webapp/README.md)を参照。

**外部データ**: webappの異体字曖昧検索は、任意でNIHU（人間文化研究機構）の異体漢字対応テーブルを利用する。これはKRMデータセットの一部ではなく、**CC-BY 4.0**の第三者データであり、本リポジトリには同梱していない。[NIHUの研究データページ](https://www.bridge.nihu.jp/researchdata/file/20221125_ITOBYb)から別途入手し、[webapp/README.md](webapp/README.md#4-異体字テーブルを配置任意推奨)の説明に従ってリポジトリ直下に配置する。このデータがなくてもwebappは動作し、異体字検索のみが無効になる。

### Examples

[`examples/README.md`](examples/README.md)は、[Claude Code](https://claude.ai/code)を使い、日本語の自然言語だけでKRMを分析する手引きである。プログラミングの知識は不要。質問例（データ整合性の確認、巻別・部首別の集計、複数テーブルにまたがる照会など）とその実行結果例を示し、繰り返し使う集計をスクリプトとして保存する方法も説明している。

## バージョン履歴

各データファイルの正確なバージョン番号・公開日・最終更新日は、そのファイル自身の`#`で始まるコメントヘッダーに記録されている。現在のバージョン状態については、本READMEではなくそのヘッダーを正典として参照すること。

- **2022年3月**：初版公開（`KRM.tsv`ほか、v1.1.x）。
- **2025年3月**：現行の`krm_*`ファイル群（v1.2.x）への仕様変更（下記参照）。
- **2025年6月12日**：`v1.2.6`をZenodoにアーカイブし、引用可能なDOIを付与（[現行リリースと引用](#現行リリースと引用)参照）。
- それ以降、リポジトリは継続的な修正・追加を重ねている（例：`krm_headword_chars`と`krm_pronunciations`はv1.2初版公開後に追加された）。これらは個別にはZenodoへ再アーカイブしていない。

### 2025年3月仕様変更

従来の公開ファイルは`KRM`を接頭辞としていたが、この変更以降のファイルは`krm`を接頭辞とする。主な変更点：

- 仮名和訓の無声点を示す"@"を"_"に変更。
- 濁音の声点を示す`"`を半角英字"V"に変更。
- 声点の存在を示す半角`()`を全角`（）`に変更。
- 誤字の訂正案を示す半角`()`を全角`〔〕`に変更。
- 脱字を示す半角`[]`を全角`［］`に変更。
- `KRM_definitions.tsv`を廃止し、そのデータと機能を新設の`krm_notes`に統合（[docs/data_specification_jp.md](docs/data_specification_jp.md#旧krm_definitionsファイルについて)参照）。

## ライセンス

- **データおよびドキュメント**（リポジトリ直下の各ファイルおよび`docs/`）：[CC BY-SA 4.0](LICENSE)。
- **`scripts/`**および**`webapp/`**のソースコード：[MIT License](scripts/LICENSE)（[webapp/LICENSE](webapp/LICENSE)）。
- **外部データセット**（webappが使用するNIHU異体字テーブルなど）は、それぞれ個別のライセンス条件に従う — [ツール・アプリケーション](#ツールアプリケーション)参照。

オープンアクセスデータである。

## 作成者および連絡先

HDICプロジェクト
代表者：池田　証寿（北海道大学名誉教授）
Copyright (c) 2022-2026 HDIC project, IKEDA Shoju (Chair, Professor Emeritus, Hokkaido University)

連絡先：ikeda.shoju@gmail.com, liyuansapporo@yahoo.co.jp, toyjack@gmail.com, kleinekuma@gmail.com

## 謝辞

観智院本類聚名義抄の解読テキストの公開について、御許可を賜った天理図書館ならびに八木書店に感謝申し上げる。

この研究は日本学術振興会科学研究費補助金（課題番号16H03422、19H00526、23K17500、25K00466、26K21717）の成果の一部である。記して感謝の意を表す。
