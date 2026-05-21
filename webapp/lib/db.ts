import Database from 'better-sqlite3';
import path from 'path';
import type { SearchResult, EntryDetail, Entry, Note, Wakun,
              TsjEntryDetail, TsjDefinition, TsjWakun } from './types';

const APP_DB_PATH = path.join(process.cwd(), 'data', 'krm_app.db');

let _db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!_db) {
    _db = new Database(APP_DB_PATH, { readonly: false });
    _db.pragma('journal_mode = WAL');
    _db.pragma('foreign_keys = ON');
  }
  return _db;
}

export function searchEntries(query: string, limit = 50, offset = 0): SearchResult[] {
  const db = getDb();
  // FTS5 search
  const stmt = db.prepare(`
    SELECT m.entry_id, m.hanzi_entry, m.volume_name, m.radical_name,
           substr(m.definition, 1, 80) as definition_snippet,
           'KRM' as source_id
    FROM krm_fts f
    JOIN krm_main m ON f.entry_id = m.entry_id
    WHERE krm_fts MATCH ?
    ORDER BY rank
    LIMIT ? OFFSET ?
  `);
  return stmt.all(query, limit, offset) as SearchResult[];
}

// expandedTerms が非 null のとき各文字を OR 結合した FTS5 クエリを生成する
// null のときは ftsQuery をそのまま使う（フレーズ検索・前方一致フォールバック共通）
function resolveTsjFtsQuery(ftsQuery: string, expandedTerms: string[] | null): string {
  if (expandedTerms) {
    return expandedTerms.map(t => `"${t.replace(/"/g, '""')}"`).join(' OR ');
  }
  return ftsQuery;
}

export function searchTSJ(
  ftsQuery: string,
  expandedTerms: string[] | null,
  limit = 50,
  offset = 0
): SearchResult[] {
  const db = getDb();
  const q = resolveTsjFtsQuery(ftsQuery, expandedTerms);
  const stmt = db.prepare(`
    SELECT
      e.SJID            AS entry_id,
      e.Entry           AS hanzi_entry,
      e.SJ_vol_radical  AS volume_name,
      e.SJ_radical      AS radical_name,
      (SELECT substr(SJ_def, 1, 80) FROM tsj_definitions WHERE TSJ2ID = e.SJ2ID LIMIT 1)
                        AS definition_snippet,
      'TSJ'             AS source_id
    FROM tsj_fts f
    JOIN tsj_entries e ON f.sjid = e.SJID
    WHERE tsj_fts MATCH ?
    ORDER BY rank
    LIMIT ? OFFSET ?
  `);
  return stmt.all(q, limit, offset) as SearchResult[];
}

export function countTSJ(ftsQuery: string, expandedTerms: string[] | null): number {
  const db = getDb();
  const q = resolveTsjFtsQuery(ftsQuery, expandedTerms);
  const row = db.prepare(
    `SELECT COUNT(*) as cnt FROM tsj_fts WHERE tsj_fts MATCH ?`
  ).get(q) as { cnt: number };
  return row.cnt;
}

export function countEntries(query: string): number {
  const db = getDb();
  const row = db.prepare(
    `SELECT COUNT(*) as cnt FROM krm_fts WHERE krm_fts MATCH ?`
  ).get(query) as { cnt: number };
  return row.cnt;
}

export function getEntry(entryId: string): EntryDetail | null {
  const db = getDb();
  const entry = db.prepare(`
    SELECT *, 'KRM' as source_id FROM krm_main WHERE entry_id = ?
  `).get(entryId) as Entry | undefined;
  if (!entry) return null;

  const notes = db.prepare(`
    SELECT definition_seq_id, definition_elements, definition_type_code,
           definition_type_name, remarks
    FROM krm_notes WHERE entry_id = ? ORDER BY definition_seq_id
  `).all(entryId) as Note[];

  const wakunList = db.prepare(`
    SELECT w.wakun_id, w.wakun_elements, w.wakun_form, w.wakun_standard_hanzi,
           w.wakun_variant_in_hanzi, w.japan_knowledge_id
    FROM krm_wakun w
    JOIN krm_notes n ON w.definition_seq_id = n.definition_seq_id
    WHERE n.entry_id = ?
  `).all(entryId) as Wakun[];

  // NDL: look up by volume name and kazama page number
  // kazama_location format: K + vol(2) + page(3) + ...
  const kLoc = entry.kazama_location; // e.g. K01001310
  let ndl_url: string | null = null;
  if (kLoc && kLoc.length >= 6) {
    const page = parseInt(kLoc.substring(3, 6), 10);
    const ndlRow = db.prepare(`
      SELECT NDL_url FROM krm_ndl WHERE Book = ? AND Kazama = ?
    `).get(entry.volume_name, page) as { NDL_url: string } | undefined;
    ndl_url = ndlRow?.NDL_url ?? null;
  }

  return { ...entry, notes, wakunList, ndl_url };
}

export function getTSJEntry(sjid: string): TsjEntryDetail | null {
  const db = getDb();

  const entry = db.prepare(`
    SELECT SJID, SJ2ID, SJ_Rinsen, SJ_vol_radical, SJ_radical, Entry, Entry_original
    FROM tsj_entries WHERE SJID = ?
  `).get(sjid) as {
    SJID: string; SJ2ID: string; SJ_Rinsen: string | null;
    SJ_vol_radical: string; SJ_radical: string;
    Entry: string | null; Entry_original: string | null;
  } | undefined;
  if (!entry) return null;

  const definitions = db.prepare(`
    SELECT TSJ2ID, Entry_word, SJ_def, SJ_remarks, ZhangLei_page
    FROM tsj_definitions WHERE TSJ2ID = ? ORDER BY rowid
  `).all(entry.SJ2ID) as TsjDefinition[];

  const wakunList = db.prepare(`
    SELECT tsj_id, sj_w_id, entry_text, entry_type, def_manyogana,
           reading_kana_kanji, reading_historical_kana, nikkoku_id
    FROM tsj_wakun WHERE tsj_id = ? ORDER BY sj_w_id
  `).all(sjid) as TsjWakun[];

  // SJIDの先頭6文字（例: s0104a）がNDLテーブルの葉IDに対応する
  const leaf = sjid.slice(0, 6);
  const ndlRow = db.prepare(`
    SELECT "NDL_URL_813.2-Sy968s_1916" as ndl_url, NIJL_Shoryobu_micro as nijl_url
    FROM tsj_ndl WHERE SJ_vol_leaf = ? LIMIT 1
  `).get(leaf) as { ndl_url: string | null; nijl_url: string | null } | undefined;

  return {
    source_id: 'TSJ',
    entry_id: entry.SJID,
    hanzi_entry: entry.Entry ?? '',
    volume_name: entry.SJ_vol_radical ?? '',
    radical_name: entry.SJ_radical ?? '',
    SJ2ID: entry.SJ2ID,
    SJ_Rinsen: entry.SJ_Rinsen ?? null,
    Entry_original: entry.Entry_original ?? null,
    definitions,
    wakunList,
    ndl_url: ndlRow?.ndl_url ?? null,
    nijl_url: ndlRow?.nijl_url ?? null,
  };
}
