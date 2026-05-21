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

// Build itaiji_groups table from NIHU 異体漢字対応テーブル (CC-BY 4.0)
const ITAIJI_TSV = path.join(__dirname, '..', '..', '異体漢字対応テーブル111220版_TSV221111.txt');
if (fs.existsSync(ITAIJI_TSV)) {
  console.log('Building itaiji_groups table...');
  dst.exec(`DROP TABLE IF EXISTS itaiji_groups`);
  dst.exec(`DROP INDEX IF EXISTS idx_itaiji_char`);
  dst.exec(`
    CREATE TABLE IF NOT EXISTS itaiji_groups (
      group_id    TEXT NOT NULL,
      char        TEXT NOT NULL,
      unicode_hex TEXT NOT NULL
    )
  `);

  const lines = fs.readFileSync(ITAIJI_TSV, 'utf-8').split('\n');
  const insertItaiji = dst.prepare(
    `INSERT INTO itaiji_groups (group_id, char, unicode_hex) VALUES (?, ?, ?)`
  );
  const insertAll = dst.transaction(() => {
    let count = 0;
    for (const line of lines) {
      const cols = line.split('\t');
      if (cols.length < 2) continue;
      const groupId = cols[0].trim();
      // Skip header row
      if (groupId === '整理番号') continue;
      if (!groupId) continue;
      // Columns: [group_id, char1, unicode1, char2, unicode2, char3, unicode3, char4, unicode4]
      for (let i = 0; i < 4; i++) {
        const charVal = (cols[1 + i * 2] ?? '').trim();
        const hexVal  = (cols[2 + i * 2] ?? '').trim();
        if (charVal) {
          insertItaiji.run(groupId, charVal, hexVal);
          count++;
        }
      }
    }
    return count;
  });
  const inserted = insertAll();
  dst.exec(`CREATE INDEX IF NOT EXISTS idx_itaiji_char ON itaiji_groups(char)`);
  console.log(`  itaiji_groups: ${inserted} chars inserted`);
} else {
  console.warn(`  NIHU itaiji TSV not found, skipping: ${ITAIJI_TSV}`);
}

// ===== TSJ Tables =====
const HDIC_DIR = path.join(__dirname, '..', '..', '..', 'HDIC');

function parseTsvFile(filePath: string): { headers: string[]; rows: string[][] } {
  const lines = fs.readFileSync(filePath, 'utf-8').split('\n');
  const nonComment = lines.filter(l => !l.startsWith('#'));
  if (nonComment.length === 0) return { headers: [], rows: [] };
  const headers = nonComment[0].split('\t').map(h => h.trim());
  const rows = nonComment.slice(1).filter(l => l.trim()).map(l => l.split('\t'));
  return { headers, rows };
}

function loadTsvToTable(db: Database.Database, tableName: string, filePath: string): number {
  const { headers, rows } = parseTsvFile(filePath);
  db.exec(`DROP TABLE IF EXISTS "${tableName}"`);
  const colDefs = headers.map(h => `"${h}" TEXT`).join(', ');
  db.exec(`CREATE TABLE "${tableName}" (${colDefs})`);
  if (rows.length === 0) return 0;
  const colNames = headers.map(h => `"${h}"`).join(', ');
  const placeholders = headers.map(() => '?').join(', ');
  const insert = db.prepare(`INSERT INTO "${tableName}" (${colNames}) VALUES (${placeholders})`);
  const insertAll = db.transaction(() => {
    for (const row of rows) {
      const vals = headers.map((_, i) => (row[i] ?? '').trim() || null);
      insert.run(vals);
    }
  });
  insertAll();
  return rows.length;
}

console.log('\nLoading TSJ tables...');

const tsjFiles: { file: string; table: string }[] = [
  { file: 'TSJ_entries.tsv',     table: 'tsj_entries' },
  { file: 'TSJ_definitions.tsv', table: 'tsj_definitions' },
  { file: 'TSJ_wakun.tsv',       table: 'tsj_wakun' },
  { file: 'TSJ_ndl.tsv',         table: 'tsj_ndl' },
];

for (const { file, table } of tsjFiles) {
  const count = loadTsvToTable(dst, table, path.join(HDIC_DIR, file));
  console.log(`  TSJ: ${count} rows → ${table}`);
}

dst.exec(`CREATE INDEX IF NOT EXISTS idx_tsj_entries_sjid  ON tsj_entries(SJID)`);
dst.exec(`CREATE INDEX IF NOT EXISTS idx_tsj_entries_sj2id ON tsj_entries(SJ2ID)`);
dst.exec(`CREATE INDEX IF NOT EXISTS idx_tsj_def_tsj2id    ON tsj_definitions(TSJ2ID)`);
dst.exec(`CREATE INDEX IF NOT EXISTS idx_tsj_wakun_tsj_id  ON tsj_wakun(tsj_id)`);

// Build TSJ FTS5 (Entry + SJ_def + reading_historical_kana)
console.log('Building TSJ FTS5 index...');
dst.exec(`DROP TABLE IF EXISTS tsj_fts`);
dst.exec(`
  CREATE VIRTUAL TABLE tsj_fts USING fts5(
    sjid       UNINDEXED,
    entry,
    definition,
    wakun,
    tokenize = 'unicode61'
  )
`);

const tsjEntries = dst.prepare(
  `SELECT SJID, SJ2ID, Entry FROM tsj_entries`
).all() as { SJID: string; SJ2ID: string; Entry: string | null }[];

// SJ2ID → aggregated SJ_def  (tsj_definitions.TSJ2ID = tsj_entries.SJ2ID)
const tsjDefMap = new Map<string, string[]>();
(dst.prepare(
  `SELECT TSJ2ID, SJ_def FROM tsj_definitions WHERE SJ_def IS NOT NULL`
).all() as { TSJ2ID: string; SJ_def: string }[]).forEach(d => {
  if (!tsjDefMap.has(d.TSJ2ID)) tsjDefMap.set(d.TSJ2ID, []);
  tsjDefMap.get(d.TSJ2ID)!.push(d.SJ_def);
});

// SJID → aggregated reading_historical_kana  (tsj_wakun.tsj_id = tsj_entries.SJID)
const tsjWakunMap = new Map<string, string[]>();
(dst.prepare(
  `SELECT tsj_id, reading_historical_kana FROM tsj_wakun WHERE reading_historical_kana IS NOT NULL`
).all() as { tsj_id: string; reading_historical_kana: string }[]).forEach(w => {
  if (!tsjWakunMap.has(w.tsj_id)) tsjWakunMap.set(w.tsj_id, []);
  tsjWakunMap.get(w.tsj_id)!.push(w.reading_historical_kana);
});

const insertTsjFts = dst.prepare(
  `INSERT INTO tsj_fts(sjid, entry, definition, wakun) VALUES (?, ?, ?, ?)`
);
dst.transaction(() => {
  for (const e of tsjEntries) {
    const defs  = (tsjDefMap.get(e.SJ2ID)   ?? []).join(' ');
    const wakun = (tsjWakunMap.get(e.SJID)   ?? []).join(' ');
    insertTsjFts.run(e.SJID, e.Entry ?? '', defs, wakun);
  }
})();
console.log(`  tsj_fts: ${tsjEntries.length} entries indexed`);

dst.close();
console.log('Done! krm_app.db created at:', APP_DB);
