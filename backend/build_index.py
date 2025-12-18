"""
Script para construir el indice invertido de Wikipedia en CASTELLANO.

Caracteristicas:
- Streaming: no carga todos los documentos en memoria
- Bajo consumo de memoria: construye indice en dos pasadas
- Solo procesa castellano (CA y PT usan scripts separados)

Uso:
    python build_index.py [--max-docs N]

Ejemplos:
    python build_index.py                  # Indexar todo el corpus ES
    python build_index.py --max-docs 10000 # Prueba con 10k docs

Para catalan y portugues:
    python build_index_ca.py
    python build_index_pt.py
    python merge_indexes.py  # Fusionar todos
"""
import argparse
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

# Solo procesar castellano (CA y PT usan scripts separados)
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


def timestamp() -> str:
    """Devuelve marca de tiempo actual."""
    return datetime.now().strftime("%H:%M:%S")


def preprocess_document_fast(text: str, stopwords: frozenset, stemmer) -> list[str]:
    """Pipeline optimizado de preprocesamiento."""
    text_lower = text.lower()
    tokens = _TOKEN_PATTERN.findall(text_lower)
    return [stemmer.stem(t) for t in tokens if t not in stopwords]


def build_index(max_docs: int | None = None) -> None:
    """
    Construye el indice invertido con bajo consumo de memoria.
    
    Estrategia:
    - Fase 1: Procesar docs, calcular DF, guardar metadatos
    - Fase 2: Calcular IDF
    - Fase 3: Segunda pasada para construir indice invertido (sin guardar doc_tf)
    """
    print("=" * 60)
    print(f"[{timestamp()}] CONSTRUCCION DEL INDICE DE WIKIPEDIA")
    print("=" * 60)

    start_time = time.time()
    OUTPUT_DIR = INDEX_DIR / "es"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # FASE 1: Primera pasada - Calcular DF y guardar metadatos
    # =========================================================================
    print(f"\n[{timestamp()}] [FASE 1] Primera pasada: calculando DF y guardando metadatos...")
    if max_docs:
        print(f"  Limite: {max_docs:,} documentos")

    df = Counter()
    doc_metadata = {}
    doc_count = 0

    for lang_code, extracted_dir in EXTRACTED_DIRS.items():
        if not extracted_dir.exists():
            print(f"  [WARN] Directorio no encontrado: {extracted_dir}")
            continue

        language = LANGUAGE_MAP[lang_code]
        print(f"\n  [{timestamp()}] Procesando Wikipedia {lang_code.upper()} ({language})...")
        
        stopwords = _get_stopwords(language)
        stemmer = _get_stemmer(language)

        for article in iter_wiki_articles(extracted_dir, max_docs=None):
            if max_docs and doc_count >= max_docs:
                print(f"\n  [WARN] Limite alcanzado: {max_docs} documentos")
                break

            tokens = preprocess_document_fast(article.text, stopwords, stemmer)
            if not tokens:
                continue

            # Solo actualizar DF (terminos unicos del documento)
            unique_terms = set(tokens)
            df.update(unique_terms)

            # Guardar metadatos
            doc_metadata[article.id] = {
                "title": article.title,
                "url": article.url,
                "snippet": article.text[:SNIPPET_LENGTH].replace("\n", " "),
                "lang": lang_code,
            }

            doc_count += 1

            if doc_count % 10000 == 0:
                elapsed = time.time() - start_time
                rate = doc_count / elapsed if elapsed > 0 else 0
                print(f"  [{timestamp()}] {doc_count:,} docs | {len(df):,} terminos | {rate:.0f} docs/s")

        if max_docs and doc_count >= max_docs:
            break

    print(f"\n  [{timestamp()}] Total: {doc_count:,} documentos, {len(df):,} terminos unicos")

    # Guardar metadatos inmediatamente para liberar memoria despues
    print(f"\n  [{timestamp()}] Guardando metadatos...")
    with open(OUTPUT_DIR / "doc_metadata.json", "w", encoding="utf-8") as f:
        json.dump(doc_metadata, f, ensure_ascii=False)
    
    # Guardar lista de doc_ids para la segunda pasada
    doc_ids = set(doc_metadata.keys())
    del doc_metadata  # Liberar memoria

    # =========================================================================
    # FASE 2: Calcular IDF
    # =========================================================================
    print(f"\n[{timestamp()}] [FASE 2] Calculando IDF...")

    idf = {}
    for term, df_t in df.items():
        idf[term] = log((doc_count + 1) / (df_t + 1)) + 1.0

    print(f"  [{timestamp()}] IDF calculado para {len(idf):,} terminos")
    
    # Guardar IDF
    with open(OUTPUT_DIR / "idf.json", "w", encoding="utf-8") as f:
        json.dump(idf, f)
    
    del df  # Liberar memoria

    # =========================================================================
    # FASE 3: Segunda pasada - Construir indice invertido
    # =========================================================================
    print(f"\n[{timestamp()}] [FASE 3] Segunda pasada: construyendo indice invertido...")
    print(f"  (Limitando a {MAX_POSTINGS_PER_TERM:,} postings por termino)")

    inverted_index = defaultdict(list)
    doc_norms = {}
    processed = 0

    for lang_code, extracted_dir in EXTRACTED_DIRS.items():
        if not extracted_dir.exists():
            continue

        language = LANGUAGE_MAP[lang_code]
        stopwords = _get_stopwords(language)
        stemmer = _get_stemmer(language)

        for article in iter_wiki_articles(extracted_dir, max_docs=None):
            if article.id not in doc_ids:
                continue
                
            if max_docs and processed >= max_docs:
                break

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

            if processed % 50000 == 0:
                print(f"  [{timestamp()}] {processed:,}/{doc_count:,} documentos indexados...")

        if max_docs and processed >= max_docs:
            break

    print(f"\n  [{timestamp()}] Indexados: {processed:,} documentos")

    # =========================================================================
    # FASE 4: Ordenar postings
    # =========================================================================
    print(f"\n[{timestamp()}] [FASE 4] Ordenando postings por relevancia...")

    for term in inverted_index:
        inverted_index[term].sort(key=lambda x: x[1], reverse=True)

    # =========================================================================
    # FASE 5: Guardar indice final
    # =========================================================================
    print(f"\n[{timestamp()}] [FASE 5] Guardando indice en disco...")

    with open(OUTPUT_DIR / "inverted_index.pkl", "wb") as f:
        pickle.dump(dict(inverted_index), f)

    with open(OUTPUT_DIR / "doc_norms.json", "w", encoding="utf-8") as f:
        json.dump(doc_norms, f)

    elapsed = time.time() - start_time
    stats = {
        "total_documents": doc_count,
        "vocabulary_size": len(inverted_index),
        "build_time_seconds": round(elapsed, 2),
        "languages": list(EXTRACTED_DIRS.keys()),
        "max_docs_limit": max_docs,
        "max_postings_per_term": MAX_POSTINGS_PER_TERM,
    }
    with open(OUTPUT_DIR / "stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # =========================================================================
    # Resumen final
    # =========================================================================
    print("\n" + "=" * 60)
    print(f"[{timestamp()}] INDICE CONSTRUIDO EXITOSAMENTE")
    print("=" * 60)
    print(f"  Documentos indexados: {doc_count:,}")
    print(f"  Terminos en vocabulario: {len(inverted_index):,}")
    print(f"  Tiempo total: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Indice guardado en: {OUTPUT_DIR}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Construir indice de Wikipedia (v2 - Low Memory)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python build_index.py                  # Indexar todo ES
  python build_index.py --max-docs 10000 # Solo 10k docs (prueba)
        """
    )
    parser.add_argument("--max-docs", type=int, default=None,
                        help="Numero maximo de documentos a indexar")

    args = parser.parse_args()
    build_index(max_docs=args.max_docs)


if __name__ == "__main__":
    main()
