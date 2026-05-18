import Database from 'better-sqlite3';
import path from 'path';
import type { SearchResult, EntryDetail, Entry, Note, Wakun } from './types';

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
