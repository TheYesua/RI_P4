// Tipos para la API de búsqueda

export interface SearchResult {
  doc_id: string;
  title: string;
  url: string;
  snippet: string;
  score: number;
}

export interface SearchResponse {
  query: string;
  total_results: number;
  results: SearchResult[];
  processing_time_ms: number;
}

export interface IndexStats {
  total_documents: number;
  vocabulary_size: number;
  index_loaded: boolean;
  current_language: string | null;
  available_languages: string[];
  build_time_seconds: number | null;
}

export interface LanguageInfo {
  code: string;
  name: string;
  documents: number;
  terms: number;
}

export interface PipelineAnalysis {
  query: string;
  pipeline: {
    "1_normalized": string;
    "2_tokens": string[];
    "3_without_stopwords": string[];
    "4_stems": string[];
    "5_tf_weights": Record<string, number>;
    "6_tfidf_weights": Record<string, number> | string;
  };
}
