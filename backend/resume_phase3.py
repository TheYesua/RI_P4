"""
Script para reanudar la construccion del indice desde la Fase 3.

Usa los archivos ya generados:
- doc_metadata.json (para obtener doc_ids)
- idf.json (para calcular TF-IDF)

Uso:
    python resume_phase3.py
"""
import json
import pickle
import re
import time
from collections import Counter, defaultdict
from datetime import datetime
from math import sqrt
from pathlib import Path

from config import INDEX_DIR, SNIPPET_LENGTH

# Directorio de salida para español
OUTPUT_DIR = INDEX_DIR / "es"
from preprocessing import _get_stopwords, _get_stemmer
from wikipedia_loader import iter_wiki_articles

# Regex precompilada para tokenizacion
_TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)

# Directorio de datos
DATA_DIR = Path(__file__).parent.parent / "datos"

# Solo procesar español (CA y PT se indexan con scripts separados)
EXTRACTED_DIRS = {
    "es": DATA_DIR / "extracted_es",
}

# Mapeo de idioma a nombre NLTK
LANGUAGE_MAP = {
    "es": "spanish",
    "ca": "spanish",
    "pt": "portuguese",
}

# Limite de postings por termino (para ahorrar memoria)
MAX_POSTINGS_PER_TERM = 10000

# Total conocido de documentos en español (para mostrar progreso correcto)
TOTAL_DOCS_ES = 3_725_687


def timestamp() -> str:
    """Devuelve marca de tiempo actual."""
    return datetime.now().strftime("%H:%M:%S")


def preprocess_document_fast(text: str, stopwords: frozenset, stemmer) -> list[str]:
    """Pipeline optimizado de preprocesamiento."""
    text_lower = text.lower()
    tokens = _TOKEN_PATTERN.findall(text_lower)
    return [stemmer.stem(t) for t in tokens if t not in stopwords]


def resume_from_phase3() -> None:
    """
    Reanuda la construccion del indice desde la Fase 3.
    Requiere que doc_metadata.json e idf.json existan.
    """
    print("=" * 60)
    print(f"[{timestamp()}] REANUDANDO CONSTRUCCION DEL INDICE (Fase 3)")
    print("=" * 60)

    start_time = time.time()

    # =========================================================================
    # Cargar datos de fases anteriores
    # =========================================================================
    print(f"\n[{timestamp()}] Cargando datos de fases anteriores...")

    # Cargar doc_ids desde metadatos
    metadata_file = OUTPUT_DIR / "doc_metadata.json"
    if not metadata_file.exists():
        print(f"  [ERROR] No se encontro {metadata_file}")
        print("  Ejecuta build_index.py primero para completar Fase 1 y 2")
        return

    print(f"  [{timestamp()}] Cargando doc_metadata.json...")
    with open(metadata_file, "r", encoding="utf-8") as f:
        doc_metadata = json.load(f)
    
    doc_ids = set(doc_metadata.keys())
    doc_count = len(doc_ids)
    print(f"  [{timestamp()}] {doc_count:,} documentos encontrados")
    
    del doc_metadata  # Liberar memoria

    # Cargar IDF
    idf_file = OUTPUT_DIR / "idf.json"
    if not idf_file.exists():
        print(f"  [ERROR] No se encontro {idf_file}")
        return

    print(f"  [{timestamp()}] Cargando idf.json...")
    with open(idf_file, "r", encoding="utf-8") as f:
        idf = json.load(f)
    
    print(f"  [{timestamp()}] {len(idf):,} terminos en vocabulario")

    # =========================================================================
    # FASE 3: Segunda pasada - Construir indice invertido
    # =========================================================================
    print(f"\n[{timestamp()}] [FASE 3] Construyendo indice invertido...")
    print(f"  (Limitando a {MAX_POSTINGS_PER_TERM:,} postings por termino)")

    inverted_index = defaultdict(list)
    doc_norms = {}
    processed = 0

    for lang_code, extracted_dir in EXTRACTED_DIRS.items():
        if not extracted_dir.exists():
            print(f"  [WARN] Directorio no encontrado: {extracted_dir}")
            continue

        language = LANGUAGE_MAP[lang_code]
        print(f"\n  [{timestamp()}] Procesando Wikipedia {lang_code.upper()} ({language})...")
        
        stopwords = _get_stopwords(language)
        stemmer = _get_stemmer(language)

        for article in iter_wiki_articles(extracted_dir, max_docs=None):
            if article.id not in doc_ids:
                continue

            tokens = preprocess_document_fast(article.text, stopwords, stemmer)
            if not tokens:
                continue

            term_counts = Counter(tokens)
            n_tokens = len(tokens)

            # Calcular TF-IDF y norma
            norm_sq = 0.0
            for term, count in term_counts.items():
                if term not in idf:
                    continue
                tfidf = (count / n_tokens) * idf[term]
                norm_sq += tfidf * tfidf
                
                # Solo agregar si no hemos alcanzado el limite
                if len(inverted_index[term]) < MAX_POSTINGS_PER_TERM:
                    inverted_index[term].append((article.id, tfidf))

            doc_norms[article.id] = sqrt(norm_sq)
            processed += 1

            if processed % 10000 == 0:
                elapsed = time.time() - start_time
                rate = processed / elapsed if elapsed > 0 else 0
                pct = (processed / TOTAL_DOCS_ES) * 100
                print(f"  [{timestamp()}] {processed:,}/{TOTAL_DOCS_ES:,} ({pct:.1f}%) | {rate:.0f} docs/s")

    print(f"\n  [{timestamp()}] Indexados: {processed:,} documentos")

    # =========================================================================
    # FASE 4: Ordenar postings
    # =========================================================================
    print(f"\n[{timestamp()}] [FASE 4] Ordenando postings por relevancia...")

    sorted_count = 0
    total_terms = len(inverted_index)
    for term in inverted_index:
        inverted_index[term].sort(key=lambda x: x[1], reverse=True)
        sorted_count += 1
        if sorted_count % 500000 == 0:
            print(f"  [{timestamp()}] {sorted_count:,}/{total_terms:,} terminos ordenados...")

    # =========================================================================
    # FASE 5: Guardar indice final
    # =========================================================================
    print(f"\n[{timestamp()}] [FASE 5] Guardando indice en disco...")

    print(f"  [{timestamp()}] Guardando inverted_index.pkl...")
    with open(OUTPUT_DIR / "inverted_index.pkl", "wb") as f:
        pickle.dump(dict(inverted_index), f)

    print(f"  [{timestamp()}] Guardando doc_norms.json...")
    with open(OUTPUT_DIR / "doc_norms.json", "w", encoding="utf-8") as f:
        json.dump(doc_norms, f)

    elapsed = time.time() - start_time
    stats = {
        "total_documents": doc_count,
        "vocabulary_size": len(inverted_index),
        "build_time_seconds": round(elapsed, 2),
        "languages": list(EXTRACTED_DIRS.keys()),
        "max_postings_per_term": MAX_POSTINGS_PER_TERM,
        "resumed_from_phase3": True,
    }
    with open(OUTPUT_DIR / "stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # =========================================================================
    # Resumen final
    # =========================================================================
    print("\n" + "=" * 60)
    print(f"[{timestamp()}] INDICE CONSTRUIDO EXITOSAMENTE")
    print("=" * 60)
    print(f"  Documentos indexados: {processed:,}")
    print(f"  Terminos en vocabulario: {len(inverted_index):,}")
    print(f"  Tiempo total: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Indice guardado en: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    resume_from_phase3()
