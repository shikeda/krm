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

**4. アプリ用DBを生成（FTS5インデックス付き）**

```bash
npm run setup-db
```

正常終了すると以下が表示されます：

```
Copying tables from krm.db...
  krm_main: 32607 rows
  krm_notes: 119400 rows
  ...
FTS5: 32607 entries indexed
Done! krm_app.db created at: .../webapp/data/krm_app.db
```

**5. 開発サーバーを起動**

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
| 詳細表示 | krm_main・krm_notes・krm_wakunを統合表示 |
| NDLリンク | 国立国会図書館デジタルコレクションへのリンク |
| JKリンク | JapanKnowledge版日本国語大辞典へのリンク（北大プロキシ経由） |

### 検索対象

- 見出し字（hanzi_entry）
- 定義文（definition_elements）
- 和訓（wakun_elements）

※ `remarks`（編者注記）は現バージョンでは検索対象外です。

---

## ファイル構成

```
webapp/
├── app/
│   ├── api/
│   │   ├── search/route.ts      ← 全文検索API
│   │   └── entry/[id]/route.ts  ← エントリ詳細API
│   ├── entry/[id]/page.tsx      ← 詳細ページ
│   └── page.tsx                 ← 検索トップページ
├── lib/
│   ├── db.ts                    ← DB接続
│   └── types.ts                 ← 型定義
├── scripts/
│   └── setup-db.ts              ← DB生成スクリプト
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
