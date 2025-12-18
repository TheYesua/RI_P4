"""
Script para construir el indice de Wikipedia en CATALAN.

Este script genera archivos separados que luego se pueden fusionar
con el indice principal usando merge_indexes.py

Uso:
    python build_index_ca.py
"""
import json
import pickle
import re
import time
from collections import Counter, defaultdict
from datetime import datetime
from math import log, sqrt
from pathlib import Path

from config import INDEX_DIR, SNIPPET_LENGTH
from preprocessing import _get_stopwords, _get_stemmer
from wikipedia_loader import iter_wiki_articles

# Regex precompilada para tokenizacion
_TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)

# Directorio de datos
DATA_DIR = Path(__file__).parent.parent / "datos"

# Directorio de salida para este idioma
OUTPUT_DIR = INDEX_DIR / "ca"

# Directorio de articulos extraidos
EXTRACTED_DIR = DATA_DIR / "extracted_ca"

# Configuracion de idioma
LANG_CODE = "ca"
LANGUAGE = "spanish"  # Catalan usa stopwords español (similar)

# Limite de postings por termino
MAX_POSTINGS_PER_TERM = 10000


def timestamp() -> str:
    """Devuelve marca de tiempo actual."""
    return datetime.now().strftime("%H:%M:%S")


def preprocess_document_fast(text: str, stopwords: frozenset, stemmer) -> list[str]:
    """Pipeline optimizado de preprocesamiento."""
    text_lower = text.lower()
    tokens = _TOKEN_PATTERN.findall(text_lower)
    return [stemmer.stem(t) for t in tokens if t not in stopwords]


def build_index_ca() -> None:
    """Construye el indice para Wikipedia en catalan."""
    print("=" * 60)
    print(f"[{timestamp()}] INDEXACION DE WIKIPEDIA CATALAN")
    print("=" * 60)

    if not EXTRACTED_DIR.exists():
        print(f"[ERROR] Directorio no encontrado: {EXTRACTED_DIR}")
        return

    start_time = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # FASE 1: Procesar documentos y calcular DF
    # =========================================================================
    print(f"\n[{timestamp()}] [FASE 1] Procesando documentos...")

    df = Counter()
    doc_metadata = {}
    doc_tf = {}
    doc_count = 0

    stopwords = _get_stopwords(LANGUAGE)
    stemmer = _get_stemmer(LANGUAGE)

    for article in iter_wiki_articles(EXTRACTED_DIR, max_docs=None):
        tokens = preprocess_document_fast(article.text, stopwords, stemmer)
        if not tokens:
            continue

        term_counts = Counter(tokens)
        n_tokens = len(tokens)

        # Guardar TF
        doc_tf[article.id] = {
            "counts": dict(term_counts),
            "n_tokens": n_tokens,
        }

        # Actualizar DF
        df.update(term_counts.keys())

        # Guardar metadatos
        doc_metadata[article.id] = {
            "title": article.title,
            "url": article.url,
            "snippet": article.text[:SNIPPET_LENGTH].replace("\n", " "),
            "lang": LANG_CODE,
        }

        doc_count += 1

        if doc_count % 10000 == 0:
            elapsed = time.time() - start_time
            rate = doc_count / elapsed if elapsed > 0 else 0
            print(f"  [{timestamp()}] {doc_count:,} docs | {len(df):,} terminos | {rate:.0f} docs/s")

    print(f"\n  [{timestamp()}] Total: {doc_count:,} documentos, {len(df):,} terminos unicos")

    # Guardar metadatos
    print(f"\n  [{timestamp()}] Guardando metadatos...")
    with open(OUTPUT_DIR / "doc_metadata.json", "w", encoding="utf-8") as f:
        json.dump(doc_metadata, f, ensure_ascii=False)

    # =========================================================================
    # FASE 2: Calcular IDF
    # =========================================================================
    print(f"\n[{timestamp()}] [FASE 2] Calculando IDF...")

    idf = {}
    for term, df_t in df.items():
        idf[term] = log((doc_count + 1) / (df_t + 1)) + 1.0

    print(f"  [{timestamp()}] IDF calculado para {len(idf):,} terminos")

    with open(OUTPUT_DIR / "idf.json", "w", encoding="utf-8") as f:
        json.dump(idf, f)

    # =========================================================================
    # FASE 3: Construir indice invertido
    # =========================================================================
    print(f"\n[{timestamp()}] [FASE 3] Construyendo indice invertido...")

    inverted_index = defaultdict(list)
    doc_norms = {}

    processed = 0
    for doc_id, tf_data in doc_tf.items():
        term_counts = tf_data["counts"]
        n_tokens = tf_data["n_tokens"]

        norm_sq = 0.0
        for term, count in term_counts.items():
            tfidf = (count / n_tokens) * idf[term]
            norm_sq += tfidf * tfidf

            if len(inverted_index[term]) < MAX_POSTINGS_PER_TERM:
                inverted_index[term].append((doc_id, tfidf))

        doc_norms[doc_id] = sqrt(norm_sq)
        processed += 1

        if processed % 50000 == 0:
            print(f"  [{timestamp()}] {processed:,}/{doc_count:,} documentos indexados...")

    # =========================================================================
    # FASE 4: Ordenar postings
    # =========================================================================
    print(f"\n[{timestamp()}] [FASE 4] Ordenando postings...")

    for term in inverted_index:
        inverted_index[term].sort(key=lambda x: x[1], reverse=True)

    # =========================================================================
    # FASE 5: Guardar indice
    # =========================================================================
    print(f"\n[{timestamp()}] [FASE 5] Guardando indice...")

    with open(OUTPUT_DIR / "inverted_index.pkl", "wb") as f:
        pickle.dump(dict(inverted_index), f)

    with open(OUTPUT_DIR / "doc_norms.json", "w", encoding="utf-8") as f:
        json.dump(doc_norms, f)

    elapsed = time.time() - start_time
    stats = {
        "total_documents": doc_count,
        "vocabulary_size": len(inverted_index),
        "build_time_seconds": round(elapsed, 2),
        "language": LANG_CODE,
    }
    with open(OUTPUT_DIR / "stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # =========================================================================
    # Resumen
    # =========================================================================
    print("\n" + "=" * 60)
    print(f"[{timestamp()}] INDICE CATALAN CONSTRUIDO")
    print("=" * 60)
    print(f"  Documentos: {doc_count:,}")
    print(f"  Terminos: {len(inverted_index):,}")
    print(f"  Tiempo: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Guardado en: {OUTPUT_DIR}")
    print("=" * 60)
    print("\nEjecuta merge_indexes.py para fusionar con el indice principal")


if __name__ == "__main__":
    build_index_ca()
