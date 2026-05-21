export interface Entry {
  entry_id: string;
  hanzi_id: string;
  kazama_location: string;
  tenri_location: string;
  volume_name: string;
  radical_name: string;
  volume_radical_index: string;
  hanzi_entry: string;
  original_entry: string;
  definition: string;
  source_id: 'KRM'; // Entry is always KRM
}

export interface Note {
  definition_seq_id: string;
  definition_elements: string;
  definition_type_code: number;
  definition_type_name: string;
  remarks: string | null;
}

export interface Wakun {
  wakun_id: string;
  wakun_elements: string;
  wakun_form: string;
  wakun_standard_hanzi: string;
  wakun_variant_in_hanzi: string;
  japan_knowledge_id: string;
}

export interface SearchResult {
  entry_id: string;
  hanzi_entry: string;
  volume_name: string;
  radical_name: string;
  definition_snippet: string;
  source_id: 'KRM' | 'TSJ';
}

export interface SearchResponse {
  results: SearchResult[];
  total_count: number;
}

export interface EntryDetail extends Entry {
  notes: Note[];
  wakunList: Wakun[];
  ndl_url: string | null;
}

// ===== TSJ-specific types =====

export interface TsjDefinition {
  TSJ2ID: string;
  Entry_word: string | null;
  SJ_def: string | null;
  SJ_remarks: string | null;
  ZhangLei_page: string | null;
}

export interface TsjWakun {
  tsj_id: string;
  sj_w_id: string;
  entry_text: string | null;
  entry_type: string | null;
  def_manyogana: string | null;
  reading_kana_kanji: string | null;
  reading_historical_kana: string | null;
  nikkoku_id: string | null;
}

export interface TsjEntryDetail {
  source_id: 'TSJ';
  entry_id: string;         // SJID
  hanzi_entry: string;      // Entry
  volume_name: string;      // SJ_vol_radical
  radical_name: string;     // SJ_radical
  SJ2ID: string;
  SJ_Rinsen: string | null;
  Entry_original: string | null;
  definitions: TsjDefinition[];
  wakunList: TsjWakun[];
  ndl_url: string | null;
  nijl_url: string | null;
}
