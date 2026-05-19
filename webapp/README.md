# KRM 検索Webアプリ

観智院本類聚名義抄データベース（KRM）の検索・閲覧Webアプリです。
見出し字・定義文・和訓をFTS5全文検索できます。

**技術構成：** Next.js 16 + TypeScript + Tailwind CSS + better-sqlite3 + SQLite FTS5

---

## 環境構築（初回セットアップ）

### 前提条件

- Node.js 20以上
- Python 3.x + pip（krm.db生成に使用）

### 手順

**1. リポジトリをclone**

```bash
git clone -b webapp https://github.com/shikeda/krm.git
cd krm
```

**2. krm.dbを生成**

TSVファイルからSQLiteデータベースを作成します。

```bash
pip install sqlite-utils

for f in krm_main krm_notes krm_wakun krm_pronunciations krm_ndl; do
  echo "Loading $f..."
  grep -v '^#' ${f}.tsv | sqlite-utils insert krm.db $f - --tsv --detect-types
done
```

Windowsの場合（PowerShell）：

```powershell
pip install sqlite-utils

foreach ($f in @("krm_main","krm_notes","krm_wakun","krm_pronunciations","krm_ndl")) {
  Write-Host "Loading $f..."
  Get-Content "${f}.tsv" | Where-Object { $_ -notmatch '^#' } |
    sqlite-utils insert krm.db $f - --tsv --detect-types
}
```

**3. webappの依存パッケージをインストール**

```bash
cd webapp
npm install
```

**4. 異体字テーブルを配置（任意・推奨）**

異体字曖昧検索を使うには、NIHU の異体漢字対応テーブルを `krm/` リポジトリルートに配置してください。

- 入手先: <https://www.bridge.nihu.jp/researchdata/file/20221125_ITOBYb>
- ファイル名: `異体漢字対応テーブル111220版_TSV221111.txt`
- 配置先: `krm/` ディレクトリ直下（`krm.db` と同じ階層）
- ライセンス: CC-BY 4.0（人間文化研究機構）— `.gitignore` 済みのため手動配置が必要

ファイルがない場合は `setup-db` 実行時に警告を出してスキップします（異体字検索は無効になります）。

**6. アプリ用DBを生成（FTS5インデックス付き）**

```bash
npm run setup-db
```

正常終了すると以下が表示されます（異体字テーブルあり）：

```
Copying tables from krm.db...
  krm_main: 32607 rows
  krm_notes: 119400 rows
  ...
FTS5: 32607 entries indexed
Building itaiji_groups table...
  itaiji_groups: 4902 chars inserted
Done! krm_app.db created at: .../webapp/data/krm_app.db
```

**7. 開発サーバーを起動**

```bash
npm run dev
```

ブラウザで [http://localhost:3000](http://localhost:3000) を開きます。

---

## 起動・停止

```bash
# 起動
npm run dev

# 停止
Ctrl+C
```

---

## 機能

| 機能 | 説明 |
|---|---|
| 全文検索 | 見出し字・定義文・和訓をFTS5で横断検索 |
| 異体字曖昧検索 | 入力文字を異体字グループに展開してOR検索（後述） |
| 詳細表示 | krm_main・krm_notes・krm_wakunを統合表示 |
| NDLリンク | 国立国会図書館デジタルコレクションへのリンク |
| JKリンク | JapanKnowledge版日本国語大辞典へのリンク（北大プロキシ経由） |

### 検索対象

- 見出し字（hanzi_entry）
- 定義文（definition_elements）
- 和訓（wakun_elements）

※ `remarks`（編者注記）は現バージョンでは検索対象外です。

---

## 異体字曖昧検索

### 概要

検索フォームの「異体字を含めて検索」チェックボックスを有効にすると、
入力文字の異体字グループを展開してOR検索します（案A：クエリ展開方式）。

**例：** 「亜」で検索 → FTS5クエリ `"亜" OR "亞" OR "亚"` を実行  
**例：** 「体」で検索 → FTS5クエリ `"体" OR "體"` を実行

チェック状態はURLパラメータ（`?q=亜&itaiji=1`）に反映され、
ページリロード後も維持されます。

### 実装ファイル

| ファイル | 役割 |
|---|---|
| `lib/itaiji.ts` | `getItaijiGroup` / `expandQueryWithItaiji` — 異体字展開ロジック |
| `app/api/search/route.ts` | `itaiji=1` パラメータ受信、FTS5クエリ構築 |
| `scripts/setup-db.ts` | NIHUデータを `itaiji_groups` テーブルとしてDBに投入 |

### 複数文字クエリの展開方針

複数文字のクエリ（例：「人体」）は、**文字ごとに展開してOR結合**する。
フレーズ置換パターンの全列挙（例：「人体」「人體」の2パターン）は
文字数に対して指数的に増加するため採用しない。
この方針は `lib/itaiji.ts` の `expandQueryWithItaiji` 関数コメントに記載している。

### 異体字データとライセンス

| 項目 | 内容 |
|---|---|
| データ名 | 異体漢字対応テーブル |
| 提供者 | 人間文化研究機構（NIHU） |
| ライセンス | **CC-BY 4.0**（クレジット表記必須） |
| URL | https://www.bridge.nihu.jp/researchdata/file/20221125_ITOBYb |
| 元ファイル | `../異体漢字対応テーブル111220版_TSV221111.txt` |
| DB格納テーブル | `itaiji_groups`（`group_id`, `char`, `unicode_hex`） |
| 収録規模 | 2,368グループ、4,902字 |

フッターに以下のクレジットを表示している：  
「異体字データ：人間文化研究機構 異体漢字対応テーブル（CC-BY 4.0）」

### カバレッジの限界

NIHUデータがカバーできるKRM見出し字は**約10%**にとどまる（18,203ユニーク字種中 約1,866字）。

主な理由：
- NIHUデータの対象は現代規格字（常用漢字・JIS X 0213・中国簡化字）が中心
- KRM見出しの約30%が補助漢字面（U+10000以上）の非BMP文字で、NIHUに未収録
- IDS（表意文字記述列）・`■`（未符号字）表記の文字はコード比較による照合が根本的に不可能

対象外の文字（漢籍・仏典由来の俗字・略字等）については、
将来的にGlyphWiki・CHISE IDS DB等との連携が必要になる。
詳しい分析は `~/claude/itaiji/README.md` を参照。

---

## ファイル構成

```
webapp/
├── app/
│   ├── api/
│   │   ├── search/route.ts      ← 全文検索API（itaiji=1 対応）
│   │   └── entry/[id]/route.ts  ← エントリ詳細API
│   ├── entry/[id]/page.tsx      ← 詳細ページ
│   └── page.tsx                 ← 検索トップページ（異体字チェックボックス）
├── lib/
│   ├── db.ts                    ← DB接続
│   ├── itaiji.ts                ← 異体字展開ロジック
│   └── types.ts                 ← 型定義
├── scripts/
│   └── setup-db.ts              ← DB生成スクリプト（itaiji_groups テーブル含む）
└── data/                        ← krm_app.db（.gitignore対象）
```

---

## データについて

- データの詳細は上位フォルダの [README_jp.md](../README_jp.md) を参照
- `krm.db`（元データ）は読み取り専用で参照し、一切変更しません
- `data/krm_app.db`はFTS5インデックス付きのアプリ専用DBで、`setup-db`で再生成できます

---

## トラブルシューティング

**`unable to open database file`エラー**

`krm.db`が`webapp/`の2つ上のフォルダに存在するか確認してください。

```bash
ls ../krm.db   # webappフォルダ内から実行
```

**`Unexpected token '<'`エラー（ブラウザ）**

開発サーバーが起動していないか、ポートが競合しています。

```bash
# 起動確認
curl "http://localhost:3000/api/search?q=人"
```

**ポート競合**

```bash
# 別ポートで起動
npm run dev -- --port 3001
```

**`node_modules`関連エラー**

```bash
rm -rf node_modules .next
npm install
npm run dev
```

---

## 開発メモ

- `next.config.ts`の`turbopack`は削除済み（better-sqlite3との相性問題のため）
- `serverExternalPackages: ['better-sqlite3']`でwebpackがネイティブモジュールを正しく処理
- `source_id = "KRM"`フィールドを型定義に持たせており、将来の他HDIC辞書追加に対応できる構造

---

## 参考リンク

- [KRMデータベース](https://github.com/shikeda/krm)
- [HDICプロジェクト](https://viewer.hdic.jp/)
- [Next.js Documentation](https://nextjs.org/docs)
