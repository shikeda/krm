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
  source_id: string; // "KRM" fixed (for future HDIC expansion)
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
  source_id: string;
}

export interface EntryDetail extends Entry {
  notes: Note[];
  wakunList: Wakun[];
  ndl_url: string | null;
}
