# KRM データ仕様書

本書は、KRMの各データファイルのカラムレベルの詳細仕様を記す。全体像（各ファイルの用途、ファイル間の関係、読み方の最低限の注意）は、まず[トップREADME](../README_jp.md)を参照されたい。

> **バージョン・日付の正典について**: 各ファイルのバージョン番号・公開日・最終更新日は、そのファイル自身の `#` で始まるコメントヘッダー（例: `krm_main.tsv` 冒頭の約20行）に記載されている。本書ではこれらの数値を転記しない。ドキュメントとは独立に更新されるため、最新の値は各ファイルのヘッダーを確認すること。Zenodoの引用可能なリリースとの関係は、トップREADMEの[バージョン履歴](../README_jp.md#バージョン履歴)を参照。

## 目次

- [ER図](#er図)
- [krm_main](#krm_main)
- [krm_notes](#krm_notes)
- [krm_headword_chars](#krm_headword_chars)
- [krm_wakun](#krm_wakun)
- [krm_pronunciations](#krm_pronunciations)
- [krm_ndl](#krm_ndl)
- [旧krm_definitionsファイルについて](#旧krm_definitionsファイルについて)
- [付録：引用書の略称一覧](#付録引用書の略称一覧)

## ER図

`krm_main`・`krm_notes`・`krm_wakun`の三つのテーブルの関係を図示すれば次のようになる。三者はいずれも`entry_id`で連結され、`krm_notes`と`krm_wakun`はさらに`definition_seq_id`で項目内の各注文要素を特定する。

![ER図](/images/krmer.drawio.png)

JSON形式では、`krm_notes`は独立した平坦なテーブルではなく、各`krm_main`レコード内の`"definitions"`キーの下に入れ子構造で格納される。次の図はこの入れ子構造を示す。

![ER_notes図](/images/krm_notes_er.drawio.png)

## krm_main

### 概要とファイル形式

観智院本類聚名義抄（以下、名義抄）データベースの中核となるファイルを解説する。従来公開していたのは、`KRM.tsv`という名称のTSVファイルである。掲出字、注文、巻、部首、風間書房版と天理善本叢書版の所在などに関する情報を収録する。

2025年3月に、カラム名、声点の表示法の仕様を変更した（詳細は[トップREADMEの「2025年3月仕様変更」](../README_jp.md#2025年3月仕様変更)を参照）。仕様変更後のファイルであることを明示するために、`krm_main.tsv`という名称にした。JSON形式も用意している。

### カラム名対照

| 新カラム名 (v1.2.x) | 旧カラム名 (v1.1.347) |
|--------------------------|----------------------------|
| entry_id                 | KRID_n                     |
| hanzi_id                 | KRID_sn                    |
| -                        | KR2ID                      |
| kazama_location          | KRID                       |
| tenri_location           | KR_Tenri_p                 |
| volume_name              | KR_vol_name                |
| radical_name              | KR_radical                 |
| volume_radical_index     | KR_vol_radical              |
| hanzi_entry              | Entry                      |
| original_entry           | Entry_original             |
| definition                | Def                        |
| -                        | Remarks                    |

`KR2ID`は省略し、`kazama_location`を`KRID`に対応させた。

`Remarks`は`krm_notes`にまとめることとして、省略した。

### 各カラムの説明

| カラム名 | 説明 |
|--------------------------|-------------------------------------------|
| entry_id                 | Fで始まる5桁の数値からなる見出し項目ID。一部、追加した掲出項目にはb番号を付す。 |
| hanzi_id                 | Sで始まる5桁の数値からなる見出し漢字ID。一部、追加した掲出項目にはb番号を付す。 |
| kazama_location    | K・巻数（2桁）・風間版頁数（3桁）・行数（1桁）、段数（1桁）、字順（1桁）を示すID。字順付与のルールの詳細は別に定める。 |
| tenri_location           | T・巻数（a/b/c）・天理版頁数（3桁）・行数（1桁）・段数（1桁）・字順（1桁）を示す。字順付与のルールの詳細は別に定める。 |
| volume_name              | 巻名。「仏上」「仏中」「仏下本」「仏下末」「法上」「法中」「法下」「僧上」「僧中」「僧下」の10巻を示す。 |
| radical_name              | 部首名。「人、彳、辵」から「風、酉、雑」までの120部を示す。 |
| volume_radical_index     | 巻。v・巻数（1-10）#・部首番号（1-120）を示す。v1#1(第1帖第1)〜v10#120(第10帖第120)。第1帖(仏上)〜第10帖(僧下)。 |
| hanzi_entry              | 校訂漢字は原則、康熙字典体（Unicodeの新字体（通用字体・俗字体）を含む）を用いる。Unicodeに収録されていない漢字については、以下の方法で表現する。漢字の部品の組み合わせで表現可能な場合は、IDS（漢字構成記述文字列）で入力する。特定の漢字やその部品で、IDSまたは標準Unicodeで表現が困難な場合は、CHISEおよびGlyphWikiの実体参照方式に基づいた簡略表記（例：CDP-8C55, koseki-00001）を用いる。上記のいずれの方法でも表現できない文字や、原典で判読不能な文字（虫損等）は、「■」（黒い四角）で入力する。複数漢字の見出しは「／」（全角スラッシュ）で区切る。省略符号「｜」は「ー」（長音符）で示し、全角括弧（）内に該当字を付記する。 |
| original_entry           | 原字形に準拠した見出し字。誤字はそのまま。Unicode外の漢字の表現はhanzi_entryに準じる。原字形の掲出字が不要なら「〇」。 |
| definition                | 注文は、字体注、音注、義注、和訓、その他からなる。これらをスペース区切りで入力。原則として「康熙字典体」に含まれる字形を入力。 |

## krm_notes

### 概要とファイル形式

`krm_notes.tsv`/`krm_notes.json`は、各項目の注文（`krm_main`の`definition`）を種類ごとに分類し出典を付した要素へと分解したファイルであり、従来`KRM_definitions.tsv`と`KRM.tsv`に分散していた詳細な注釈情報を統合している。TSV形式とJSON形式で提供する。

他のJSONファイルがすべて（TSVの1行につき1オブジェクトの）フラットな配列であるのに対し、`krm_notes.json`のみ`entry_id`ごとにまとめ、項目レベルの列（`kazama_location`、`hanzi_entry`など）は1回だけ持たせ、注文の各要素を`"definitions"`配列としてその下に入れ子で格納する（詳細は[データ構造](#データ構造er図とjsonにおける実装)を参照）。生成には汎用の`scripts/tsv_to_json.py`ではなく、専用の`scripts/gen_notes_json.py`を用いる。`tsv_to_json.py`では、フラットな配列（項目レベルの列が全行で重複）か、`--group-by entry_id`指定時でも`{ "F00001": [各行...], ... }`という辞書形式（この場合も各行に項目レベルの列が重複）になり、ここで説明した`"definitions"`入れ子形式とは異なる。

### カラム名対照

#### KRM_definitions.tsv (v1.1.55) との対照

| 新カラム名 (krm_notes) | 旧カラム名 (KRM_definitions v1.1.55) |
|--------------------------|----------------------------|
| definition_seq_id        | KRID_no                    |
| kazama_location          | KRID                       |
| hanzi_entry              | Entry                      |
| definition_elements      | Def                        |
| definition_type_code     | Def_code                   |
| definition_type_name     | Def_name                   |
| remarks                  | Remarks                    |

#### KRM.tsv (v1.1.347) の内容の取り込み

`krm_notes.tsv`は`KRM.tsv`の内容も取り込んでいる。

| 新カラム名 (krm_notes) | 旧カラム名 (KRM v1.1.347) |
|--------------------------|----------------------------|
| entry_id                 | KRID_n                     |
| tenri_location           | KR_Tenri_p                 |
| volume_name              | KR_vol_name                |
| radical_name              | KR_radical                 |
| volume_radical_index     | KR_vol_radical              |
| original_entry           | Entry_original             |

### データ構造：ER図とJSONにおける実装

ER図においては、`krm_notes`テーブルは`krm_main`テーブルと`entry_id`によって関連づけられた子テーブル（一対多）として表現されている。一方、実際のJSONデータでは、この`krm_notes`に相当する情報は平坦なテーブル構造ではなく、各`krm_main`オブジェクト内に`"definitions"`というキーでまとめられた入れ子の配列として実装されている。

![ER_notes図](/images/krm_notes_er.drawio.png)

`"definitions"`配列には、以下のフィールドをもつ定義オブジェクトが複数格納されている。

- definition_seq_id
- definition_elements
- definition_type_code
- definition_type_name
- remarks

**JSONデータ構造の例：**

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

### 各カラムの説明

| カラム名 | 説明 |
|--------------------------|---------------------------------------------------------------------------|
| entry_id                 | Fで始まる5桁の数値からなる見出し項目ID。一部、追加した掲出項目にはb番号を付す。 |
| definition_seq_id        | 連番で与えられるFで始まる5桁の見出しの数値IDに加えて、見出しの下に記される注文の各要素を出現順に区分し、出現の順番に_01、_02のように追加したもの。見出しには_00を追加する。 |
| kazama_location          | [krm_main](#krm_main) を参照。 |
| tenri_location           | [krm_main](#krm_main) を参照。 |
| volume_name              | [krm_main](#krm_main) を参照。 |
| radical_name              | [krm_main](#krm_main) を参照。 |
| volume_radical_index     | [krm_main](#krm_main) を参照。 |
| hanzi_entry              | [krm_main](#krm_main) を参照。 |
| original_entry           | [krm_main](#krm_main) を参照。 |
| definition_elements      | 注文の全文から、字体注、音注、意義注、和訓、その他の5種に区分し、それぞれの要素を一つずつ抜き出したもの。 |
| definition_type_code     | 注文の種類を分類した3桁の数値。 |
| definition_type_name     | 注文の種類を字体注、音注、意義注、和訓、その他の5種に区分して、そのいずれに該当するかを示したもの。 |
| remarks                  | 編集者による注記（Compiler's Remarks）。詳細は[次節](#compilers-remarksremarksカラムの内容と意義)を参照。 |

### Compiler's Remarks（remarksカラム）の内容と意義

`remarks`カラムには、名義抄本文そのものではなく、データベース作成者による注釈（Compiler's Remarks）が格納される。

- **追加的な文脈**: 名義抄の記述を理解する上で助けとなるような、補足的な背景情報や関連情報。
- **学術的な考察**: 特定の記述に対する、文献学的、言語学的などの専門的観点からの考察や見解。先行研究の紹介を含む。
- **本文校勘の結果**: 異本や関連資料との比較検討（校勘）を行った結果判明したことや、それに基づく本文解釈など。
- **出典調査**: 名義抄の記述が、どのような文献を典拠としているかの調査結果や、その考察。先行研究での指摘も紹介。

これらの注釈は、それぞれ`krm_notes`内の特定の`definition_element`（注文の個別要素）、または`Headword`（掲出字）に関連付けられている。

## krm_headword_chars

### 概要とファイル形式

名義抄の掲出字は、単字からなるものと、複字（多字）からなるものがある。`krm_main`・`krm_notes`・`krm_wakun`はいずれも項目単位のデータであるため、複数の文字で構成される掲出字の2字目以降の文字はこれらのデータから直接参照できない。

`krm_headword_chars`は、名義抄のすべての掲出字を構成する文字を、項目順および項目内の出現順に一覧したデータであり、文字単位の検索・画像表示・分析を可能にする。TSV形式とJSON形式で提供する。

### 各カラムの説明

| カラム名 | 説明 |
|----------------------|-----------------------------------------------|
| hanzi_id                | 単字、複字を問わず、名義抄の出現順に与えられたSで始まる5桁の数値からなる掲出字の通しID。 |
| entry_id               | この文字が属する掲出字（見出し語）の項目（krm_mainにおける項目）のID（Fで始まる5桁の数値）。一部、追加した掲出項目にはb番号を付す。 |
| constituent_char              | 見出しを構成する文字そのもの。省略符号（ー）と踊り字（〻）は当該の文字に改める。校訂漢字は原則、康熙字典体。詳細な校訂注記はkrm_notes参照。 |
| character_order              | それが属する掲出字（見出し語）内で何字目に出現するかを数値で示す。 |
| kazama_location_id            | K・巻数（2桁）・風間版頁数（3桁）・行数（1桁）、段数（1桁）、字順（1桁）で構成される、この文字の風間版における所在ID。 |
| tenri_location_id              | T・巻数（a/b/c）・天理版頁数（3桁）・行数（1桁）・段数（1桁）、字順（1桁）で構成される、この文字の天理版における所在ID。 |
| img_file_name       | 掲出字の画像ファイル名（拡張子.jpgを含む）。ファイル名の本体は、巻1から巻9の画像では7桁の数値、巻10の画像では8桁の数値となる。7桁の場合、最初の1桁が巻数を、8桁の場合、最初の2桁が巻10を示す。下6桁の数値は出現順に基づいているが、その割り当ては独自の規則による。20年以上前の作業のため、詳細な命名規則に関するドキュメントは現存しない。画像がない場合はnull。 |

## krm_wakun

### 概要とファイル形式

名義抄データから和訓を抜き出して、和訓の異形を整理し、異体字との対応を調整したデータである。和訓に関する校勘と出典考証は`krm_notes`に記載したので省略している。

和訓には、異なる読み方を傍書して併記する場合がある。たとえば「倍」に「マサル」という和訓を付すが、「ル」の右に小さい片仮名で「ス」を傍書する。これは「マサル」に加えて「マス」という和訓を注記したものである。この併記への対応が必要なのは、和訓にジャパンナレッジ版『日本国語大辞典第二版』の情報を追加するためである。

異体字との対応は、掲出字に異体字を示すことがあり、これを調整したものである。たとえば、「ヤツカレ」という和訓は、掲出字「㒒／僕」の注文に見える。和訓「ヤツカレ」は、「僕」に対する和訓であると同時に「㒒」に対する和訓となっている。「爲」と「為」、「來」と「来」との関係も同様である。ジャパンナレッジ版『日本国語大辞典第二版』には「表記」欄があり、名義抄の漢字表記を収録しているので、これとの対応をとるための措置である。

### カラム名対照

| 新カラム名 (v1.2.x) | 旧カラム名 (v1.1.97) |
|-------------------------|---------------|
| wakun_id                | KRID_wakun_no |
| definition_seq_id       | KRID_no       |
| kazama_location   | KR2ID         |
| hanzi_entry             | Entry         |
| wakun_elements          | Def           |
| wakun_form              | Word_form     |
| wakun_standard_hanzi    | Wakun_Hanzi   |
| wakun_variant_in_hanzi  | Wakun_variant |
| variant_hanzi_for_wakun | Hanzi_variant |
| japan_knowledge_id      | JK_URL        |
| -           | Remarks       |

`Remarks`は`krm_notes`にまとめることとして、省略した。

### 各カラムの説明

| カラム名 | 説明 |
|-------------------------|-------------|
| wakun_id                | 和訓ID。definition_seq_idから、注文の種類が和訓のものだけを取り出したもの。傍書による併記形には末尾にb, c, dを付した。 |
| definition_seq_id        | [krm_notes](#krm_notes) を参照。`krm_notes`内の該当レコードと連結する。 |
| kazama_location   | 位置情報（風間版：K、冊子（巻）、ページ（xxx）、行（y）、列（zz））を含むID。列に複数のエントリがある場合は、1、2、...、n の順位になる。 |
| hanzi_entry                | この和訓が対応する掲出字（漢字）。 |
| wakun_elements          | 注文の全文から、和訓の要素を一つずつ抜き出したもの。 |
| wakun_form           | 和訓の語形。活用のあるものは、助詞助動詞を除いて終止形とする。文選読みの「の」「と」は省略する。 |
| wakun_standard_hanzi         | 標準的な漢字による和訓表記。 |
| wakun_variant_in_hanzi | 標準的な漢字による和訓の異形の表記。 |
| variant_hanzi_for_wakun    | 異体字による和訓の表記。 |
| japan_knowledge_id      | ジャパンナレッジ版『日本国語大辞典第二版』にこの和訓が見出しとして存在する場合に、そのURLの後半、20020から末尾までの英数字を記載する。見出しとして存在しない場合はnullと入力する。 |

## krm_pronunciations

### 概要とファイル形式

名義抄の音注は、反切、類音注、仮名注があり、それらに声点が施されることも多い。本ファイルは、加藤大鶴氏らによる「資料横断的な漢字音・漢語音データベース」（DHSJR）のカラム仕様にKRMの音注データを合わせ、両データベース間の連携を可能にするものである。`pronunciation_id`を主キー、`definition_seq_id`（`krm_notes`と連結）を外部キーとする。名義抄の音注には多様な形式があるため、それらを分類する`annotation_format`カラムを設けている。DHSJR自体は日本語カラム名を用いるが、HDIC内部の処理の都合上、英語カラム名を採用している。

以下の表で、HDIC独自のカラム名（DHSJRに存在しないもの）は**太字**で示す。

### カラム名対照

| DHSJR（日本語） | HDIC（英語）            | キー         | 説明                                                                 |
| :--------------- | :------------------------ | :---------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ID               | dhsjr_id                  |             | 単字ごとのDHSJRユニークID（統合データのみ）。DHSJR側の公式ID確定まで現在は空欄。 |
| 音注ID           | **`pronunciation_id`**    | 主キー | 音注ID。`definition_seq_id`から、`krm_notes`で音注に分類される要素のみを取り出したもの。異形にはb, c, dの接尾辞を付す。 |
| 注文ID           | **`definition_seq_id`**   | 外部キー | `krm_notes`・`krm_main`の該当レコードと連結する。 |
| 資料番号         | material_id               |             | 資料ID。 |
| 資料名           | material_name             |             | 資料の名称。 |
| 資料内漢字番号   | material_character_index  |             | 漢字の資料内出現順の通し番号。1〜27978は原本の物理的な出現順に対応する。30001以上は初期入力後に追加されたレコード（例：別レコードとして扱う必要が判明した注音字など）であり、原本上の物理的位置には対応しない。 |
| 資料内漢語番号   | material_word_index       |             | 漢語の資料内出現順の通し番号。 |
| 単字＿見出し      | character_headword        |             | 音注が付された漢字の見出し列。 |
| 単字＿出現形      | character_form            |             | 音注が付された漢字。 |
| 漢語＿見出し      | word_headword             |             | 音注が付された漢字を含む漢語の見出し列。 |
| 漢語＿出現形      | word_form                 |             | 音注が付された漢字を含む漢語。 |
| 漢語＿alphabet  | word_alpha                |             | 欧文による漢語の表記がある場合に入力されている。 |
| 語種             | word_type                 |             | 混種語がある場合に、語種を示す。 |
| 漢語内位置       | word_position             |             | 漢語内での単字の位置。 |
| 単字長           | character_mora_count      |             | 単字の拍数。 |
| 声点             | tone_marks                |             | 単字に対する四声（平上去入）、六声（平平軽上去入軽入）及び清濁。 |
| 声点型           | tone_pattern              |             | 漢語に対する声点の組合せ。声点がない単字については＊で表す。 |
| 仮名注           | kana_notes                |             | 仮名表記による字音注（仮名反切を含む）。 |
| 仮名型           | kana_pattern              |             | 漢語に対する仮名注の組合せ。仮名注がない単字については＊で表す。 |
| 反切             | fanqie                    |             | 単字に対する反切注。 |
| 類音             | similar_sound             |             | 単字に対する類音注。 |
| 音注型           | **`annotation_format`**   |             | 仮名注、反切、類音、声点などの複数の音注が組み合わさった形式のパターン。 |
| 節博士           | fushi_hakase               |             | 声明等音楽資料に付される博士譜など。 |
| その他           | other_phonetic_annotations|             | その他の音注。 |
| 出現位置         | material_location          |             | 資料内の単字・漢語の所在。K・巻数（2桁）・風間版頁数（3桁）・行数（1桁）・段数（1桁）の形式。例：`K0201474`は巻2・14頁・7行目・4段目を示す。 |
| 備考             | remarks_pronunciation      |             | 注記すべき事柄。値の分類は[docs/remarks_pronunciation_summary.md](remarks_pronunciation_summary.md)、上声全濁字の異例に関する手動補正・除外の記録は[docs/manual_exclusion_list.md](manual_exclusion_list.md)を参照。 |

## krm_ndl

観智院本類聚名義抄の所在と、国会図書館デジタルコレクションの該当画像URLとを対照させたデータである。`krm_ndl.tsv`のみで提供する（JSON形式なし）。

| カラム | 説明 |
|--------|------|
| Book    | 巻名（帖名）。 |
| Radical | 部首字。 |
| Kazama  | 風間版頁数。 |
| Tenri   | 天理版頁数。 |
| NDL_url | 国会図書館デジタルコレクションの該当画像URL。 |

サンプル：

| Book | Radical | Kazama | Tenri | NDL_url                                       |
|------|---------|--------|-------|-----------------------------------------------|
| 仏上   | 人       | 1      | 23    | https://dl.ndl.go.jp/info:ndljp/pid/2586891/6 |
| 仏上   | 人       | 2      | 24    | https://dl.ndl.go.jp/info:ndljp/pid/2586891/7 |

このファイルは2025年3月の仕様変更以前から公開されており、`krm_main`と共通の連結キー（`entry_id`など）をまだ持たない。所在とエントリの対応づけには、`Kazama`/`Tenri`の頁数と`kazama_location`/`tenri_location`を照合する必要がある。

## 旧krm_definitionsファイルについて

2025年3月の仕様変更以前は、注文の各要素（字体注、音注、意義注など）を種類ごとに分類し出現順に並べた`KRM_definitions.tsv`という独立ファイルを公開していた。そのデータと機能は[上記のカラム対照](#krm_definitionstsv-v155-との対照)のとおり`krm_notes`に完全に統合されており、現在`krm_definitions`という独立ファイルは存在せず、別途の仕様書も維持していない。

## 付録：引用書の略称一覧

Compiler's Remarks（`remarks`・`remarks_pronunciation`カラム）では、先行研究を略称で引用することが多い。これらの略称は`krm_main.tsv`・`krm_notes.tsv`・`krm_wakun.tsv`のコメントヘッダーにも記載されているが、以下では英訳を付して一覧化する。

- 正宗索引: 正宗敦夫編, 類聚名義抄 仮名索引, 日本古典全集刊行会, 1939-1940
- 岡田研究: 岡田希雄, 類聚名義抄の研究, 一条書房, 1944
- 望月和訓集成: 望月郁子編, 類聚名義抄: 四種声点付和訓集成, 笠間書院, 1974
- 中村文選: 中村宗彦, 九条本文選古訓集, 風間書房, 1983
- 草川和訓集成: 草川昇編, 五本対照類聚名義抄和訓集成, 汲古書院, 2000
- 西端誤写考察: 西端幸雄, 類聚名義抄における誤写の考察, 訓点語と訓点資料45, 1971
- 西端誤写諸例: 西端幸雄, 類聚名義抄における誤写の諸例, 訓点語と訓点資料52，1973
- 略注: 佐藤喜代治，色葉字類抄略注，明治書院，1995
- 群書治要: 小林芳規・原卓志・山本秀人・山本真吾・佐々木勇編, 宮内庁書陵部蔵本群書治要経部語彙索引, 汲古書院, 1996
- 毛詩鄭箋: 毛詩鄭箋（一）（二）（三）, 古典研究会叢書漢籍之部１～３, 原本所蔵静嘉堂文庫, 汲古書院, 1992

英訳を含む詳細版は[docs/data_specification.md](data_specification.md#appendix-abbreviations-of-cited-works)（英語）を参照。
