@AGENTS.md

## このアプリの概要

KRM（観智院本類聚名義抄）データベースの検索・閲覧Webアプリ。
見出し字・定義文・和訓をFTS5全文検索する。

## 重要な設定・注意事項

### better-sqlite3について
- `next.config.ts`に`serverExternalPackages: ['better-sqlite3']`が必要
- `turbopack`は削除済み（better-sqlite3との権限エラーのため）
- この設定を変更・削除しないこと

### DBファイルの構成
- `../../krm.db` — 元データ（読み取り専用・変更禁止）
- `./data/krm_app.db` — FTS5インデックス付きアプリ用DB（`npm run setup-db`で再生成）

### ファイル構成
- `app/api/search/route.ts` — 全文検索API
- `app/api/entry/[id]/route.ts` — エントリ詳細API
- `lib/db.ts` — DB接続
- `lib/types.ts` — 型定義（`source_id = "KRM"`で将来の他辞書追加に対応）

## してはいけないこと

- `krm.db`を直接編集・上書きしない
- `turbopack`を`next.config.ts`に追加しない
- `data/`フォルダをGitにコミットしない