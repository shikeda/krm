import type Database from 'better-sqlite3';

/**
 * itaiji_groups テーブルから、指定した1文字と同グループの全文字リストを返す。
 * グループ未登録の場合は [char] をそのまま返す。
 */
export function getItaijiGroup(db: Database.Database, char: string): string[] {
  const row = db.prepare(
    `SELECT group_id FROM itaiji_groups WHERE char = ? LIMIT 1`
  ).get(char) as { group_id: string } | undefined;
  if (!row) return [char];

  const members = db.prepare(
    `SELECT char FROM itaiji_groups WHERE group_id = ?`
  ).all(row.group_id) as { char: string }[];

  // Deduplicate while preserving order (input char first)
  const seen = new Set<string>([char]);
  const result = [char];
  for (const m of members) {
    if (!seen.has(m.char)) {
      seen.add(m.char);
      result.push(m.char);
    }
  }
  return result;
}

/**
 * クエリ文字列中の各文字を異体字グループに展開し、FTS5 OR 検索用の文字列リストを返す。
 *
 * 設計判断: 文字ごとに展開して OR 結合する方式を採用する。
 * 理由: KRM の検索は主に1文字の見出し字引きで使われる。複数文字のクエリに対して
 * 全置換パターン（例: 「人体」→「人体」「人體」）を生成すると文字数に対して指数的に
 * 増加するため FTS5 クエリが肥大化する。文字単位の OR 展開は多少広くなるが、
 * 古典籍の異体字検索では許容範囲であり、実用的なトレードオフと判断した。
 *
 * 例: "亜"  → ["亜", "亞", "亚"]
 * 例: "人体" → ["人", "体", "體"]  (人はグループ未登録)
 */
export function expandQueryWithItaiji(db: Database.Database, query: string): string[] {
  const seen = new Set<string>();
  const result: string[] = [];

  for (const char of query) {
    for (const variant of getItaijiGroup(db, char)) {
      if (!seen.has(variant)) {
        seen.add(variant);
        result.push(variant);
      }
    }
  }

  return result;
}
