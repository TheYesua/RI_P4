"""
Script para fusionar indices de diferentes idiomas en un indice unificado.

Fusiona los indices de:
- datos/index/ (español - indice principal)
- datos/index/ca/ (catalan)
- datos/index/pt/ (portugues)

Uso:
    python merge_indexes.py
"""
import json
import pickle
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from config import INDEX_DIR

# Limite de postings por termino en el indice final
MAX_POSTINGS_PER_TERM = 10000


def timestamp() -> str:
    """Devuelve marca de tiempo actual."""
    return datetime.now().strftime("%H:%M:%S")


def merge_indexes() -> None:
    """Fusiona los indices de todos los idiomas."""
    print("=" * 60)
    print(f"[{timestamp()}] FUSION DE INDICES")
    print("=" * 60)

    start_time = time.time()

    # Directorios de indices por idioma
    index_dirs = {
        "es": INDEX_DIR / "es",
        "ca": INDEX_DIR / "ca",
        "pt": INDEX_DIR / "pt",
    }

    # =========================================================================
    # Cargar y fusionar metadatos
    # =========================================================================
    print(f"\n[{timestamp()}] Fusionando metadatos...")

    merged_metadata = {}
    for lang, idx_dir in index_dirs.items():
        metadata_file = idx_dir / "doc_metadata.json"
        if not metadata_file.exists():
            print(f"  [WARN] No encontrado: {metadata_file}")
            continue

        print(f"  [{timestamp()}] Cargando {lang}...")
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        # Prefijo para evitar colisiones de IDs entre idiomas
        for doc_id, doc_data in metadata.items():
            merged_id = f"{lang}_{doc_id}"
            merged_metadata[merged_id] = doc_data
        
        print(f"    {len(metadata):,} documentos")
        del metadata

    print(f"\n  [{timestamp()}] Total: {len(merged_metadata):,} documentos")

    # =========================================================================
    # Fusionar indices invertidos
    # =========================================================================
    print(f"\n[{timestamp()}] Fusionando indices invertidos...")

    merged_index = defaultdict(list)
    
    for lang, idx_dir in index_dirs.items():
        index_file = idx_dir / "inverted_index.pkl"
        if not index_file.exists():
            print(f"  [WARN] No encontrado: {index_file}")
            continue

        print(f"  [{timestamp()}] Cargando {lang}...")
        with open(index_file, "rb") as f:
            index = pickle.load(f)
        
        print(f"    {len(index):,} terminos")
        
        # Fusionar postings con prefijo de idioma
        for term, postings in index.items():
            for doc_id, tfidf in postings:
                merged_id = f"{lang}_{doc_id}"
                merged_index[term].append((merged_id, tfidf))
        
        del index

    print(f"\n  [{timestamp()}] Total: {len(merged_index):,} terminos unicos")

    # =========================================================================
    # Fusionar normas de documentos
    # =========================================================================
    print(f"\n[{timestamp()}] Fusionando normas de documentos...")

    merged_norms = {}
    
    for lang, idx_dir in index_dirs.items():
        norms_file = idx_dir / "doc_norms.json"
        if not norms_file.exists():
            print(f"  [WARN] No encontrado: {norms_file}")
            continue

        print(f"  [{timestamp()}] Cargando {lang}...")
        with open(norms_file, "r", encoding="utf-8") as f:
            norms = json.load(f)
        
        for doc_id, norm in norms.items():
            merged_id = f"{lang}_{doc_id}"
            merged_norms[merged_id] = norm
        
        print(f"    {len(norms):,} documentos")
        del norms

    # =========================================================================
    # Fusionar IDF (usar el maximo para cada termino)
    # =========================================================================
    print(f"\n[{timestamp()}] Fusionando IDF...")

    merged_idf = {}
    
    for lang, idx_dir in index_dirs.items():
        idf_file = idx_dir / "idf.json"
        if not idf_file.exists():
            continue

        print(f"  [{timestamp()}] Cargando {lang}...")
        with open(idf_file, "r", encoding="utf-8") as f:
            idf = json.load(f)
        
        for term, value in idf.items():
            if term not in merged_idf or value > merged_idf[term]:
                merged_idf[term] = value
        
        del idf

    print(f"\n  [{timestamp()}] Total: {len(merged_idf):,} terminos")

    # =========================================================================
    # Ordenar y limitar postings
    # =========================================================================
    print(f"\n[{timestamp()}] Ordenando y limitando postings...")

    for term in merged_index:
        # Ordenar por TF-IDF descendente
        merged_index[term].sort(key=lambda x: x[1], reverse=True)
        # Limitar a MAX_POSTINGS_PER_TERM
        if len(merged_index[term]) > MAX_POSTINGS_PER_TERM:
            merged_index[term] = merged_index[term][:MAX_POSTINGS_PER_TERM]

    # =========================================================================
    # Guardar indice fusionado
    # =========================================================================
    print(f"\n[{timestamp()}] Guardando indice fusionado...")

    # Backup del indice original
    backup_dir = INDEX_DIR / "backup_es"
    if not backup_dir.exists():
        backup_dir.mkdir(parents=True)
        for f in ["inverted_index.pkl", "doc_metadata.json", "doc_norms.json", "idf.json"]:
            src = INDEX_DIR / f
            if src.exists():
                import shutil
                shutil.copy(src, backup_dir / f)
        print(f"  [{timestamp()}] Backup creado en {backup_dir}")

    # Guardar archivos fusionados
    print(f"  [{timestamp()}] Guardando inverted_index.pkl...")
    with open(INDEX_DIR / "inverted_index.pkl", "wb") as f:
        pickle.dump(dict(merged_index), f)

    print(f"  [{timestamp()}] Guardando doc_metadata.json...")
    with open(INDEX_DIR / "doc_metadata.json", "w", encoding="utf-8") as f:
        json.dump(merged_metadata, f, ensure_ascii=False)

    print(f"  [{timestamp()}] Guardando doc_norms.json...")
    with open(INDEX_DIR / "doc_norms.json", "w", encoding="utf-8") as f:
        json.dump(merged_norms, f)

    print(f"  [{timestamp()}] Guardando idf.json...")
    with open(INDEX_DIR / "idf.json", "w", encoding="utf-8") as f:
        json.dump(merged_idf, f)

    # Estadisticas
    elapsed = time.time() - start_time
    stats = {
        "total_documents": len(merged_metadata),
        "vocabulary_size": len(merged_index),
        "merge_time_seconds": round(elapsed, 2),
        "languages": ["es", "ca", "pt"],
        "max_postings_per_term": MAX_POSTINGS_PER_TERM,
    }
    with open(INDEX_DIR / "stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # =========================================================================
    # Resumen
    # =========================================================================
    print("\n" + "=" * 60)
    print(f"[{timestamp()}] INDICES FUSIONADOS EXITOSAMENTE")
    print("=" * 60)
    print(f"  Documentos totales: {len(merged_metadata):,}")
    print(f"  Terminos totales: {len(merged_index):,}")
    print(f"  Tiempo: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Indice guardado en: {INDEX_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    merge_indexes()
