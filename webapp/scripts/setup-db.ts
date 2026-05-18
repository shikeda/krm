import Database from 'better-sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const KRM_DB = path.join(__dirname, '..', '..', 'krm.db');
const APP_DB = path.join(__dirname, '..', 'data', 'krm_app.db');

// Create data directory
fs.mkdirSync(path.dirname(APP_DB), { recursive: true });

// Remove existing DB and recreate
if (fs.existsSync(APP_DB)) fs.unlinkSync(APP_DB);

const src = new Database(KRM_DB, { readonly: true });
const dst = new Database(APP_DB);
dst.pragma('journal_mode = WAL');

console.log('Copying tables from krm.db...');

// Copy table schemas
const tables = src.prepare("SELECT name, sql FROM sqlite_master WHERE type='table'").all() as { name: string; sql: string }[];
for (const { name, sql } of tables) {
  dst.exec(sql);
  const rows = src.prepare(`SELECT * FROM "${name}"`).all();
  if (rows.length === 0) continue;
  const cols = Object.keys(rows[0] as object);
  const placeholders = cols.map(() => '?').join(',');
  const insert = dst.prepare(`INSERT INTO "${name}" (${cols.map((c) => `"${c}"`).join(',')}) VALUES (${placeholders})`);
  const insertMany = dst.transaction((rs: unknown[]) => {
    for (const row of rs) insert.run(Object.values(row as object));
  });
  insertMany(rows);
  console.log(`  ${name}: ${rows.length} rows`);
}

src.close();

// Create FTS5 virtual table
console.log('Creating FTS5 index...');
dst.exec(`
  CREATE VIRTUAL TABLE IF NOT EXISTS krm_fts USING fts5(
    entry_id UNINDEXED,
    hanzi_entry,
    definition,
    wakun_forms,
    tokenize = 'unicode61'
  );
`);

// Populate FTS5 with krm_main + wakun data
const entries = dst.prepare(`SELECT entry_id, hanzi_entry, definition FROM krm_main`).all() as { entry_id: string; hanzi_entry: string; definition: string }[];

const wakunMap = new Map<string, string[]>();
const wakuns = dst.prepare(`
  SELECT n.entry_id, w.wakun_form FROM krm_wakun w
  JOIN krm_notes n ON w.definition_seq_id = n.definition_seq_id
`).all() as { entry_id: string; wakun_form: string }[];
for (const w of wakuns) {
  if (!wakunMap.has(w.entry_id)) wakunMap.set(w.entry_id, []);
  wakunMap.get(w.entry_id)!.push(w.wakun_form);
}

const insertFts = dst.prepare(`INSERT INTO krm_fts(entry_id, hanzi_entry, definition, wakun_forms) VALUES (?,?,?,?)`);
const insertFtsMany = dst.transaction(() => {
  for (const e of entries) {
    const wForms = (wakunMap.get(e.entry_id) ?? []).join(' ');
    insertFts.run(e.entry_id, e.hanzi_entry, e.definition ?? '', wForms);
  }
});
insertFtsMany();
console.log(`FTS5: ${entries.length} entries indexed`);

// Create indexes
dst.exec(`CREATE INDEX IF NOT EXISTS idx_main_entry_id ON krm_main(entry_id)`);
dst.exec(`CREATE INDEX IF NOT EXISTS idx_notes_entry_id ON krm_notes(entry_id)`);
dst.exec(`CREATE INDEX IF NOT EXISTS idx_notes_def_seq ON krm_notes(definition_seq_id)`);
dst.exec(`CREATE INDEX IF NOT EXISTS idx_wakun_def_seq ON krm_wakun(definition_seq_id)`);

dst.close();
console.log('Done! krm_app.db created at:', APP_DB);
