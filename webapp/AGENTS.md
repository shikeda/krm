## 辞書（source）追加時の注意

`app/page.tsx` には、辞書ごとの機能制御に関して **必ずセットで変更すべき2箇所** がある：

1. **`runSearch()` 内の `params.set('itaiji', '1')`**  
   APIリクエストに `itaiji=1` を付与する条件
2. **`pushUrl()` 内の同条件**  
   URLパラメータに `itaiji=1` を書き込む条件

現在（KRM・TSJ）はどちらも `if (useItaiji)` で全辞書共通に適用している。  
新しい辞書 source（例: KTB）を追加する際、itaiji を特定辞書にのみ制限したい場合は、  
この2箇所を **同時に** 修正すること。

**やってはいけない** — 片方だけ変更すると次のような不整合が生じる：
- `runSearch` だけ修正 → チェックボックスは表示されるが `itaiji=1` がAPIに届かない（UIにフィードバックなし）
- `pushUrl` だけ修正 → URLには `itaiji=1` が入るが実際の検索リクエストには含まれない

また、チェックボックスの **表示条件** を変更する場合（例: `{source === 'KRM' && <label>…`）も  
上記2箇所と整合を確認すること。

<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->
