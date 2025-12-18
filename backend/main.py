"""
Backend FastAPI para el Sistema de Recuperación de Información.
Práctica 4 - Recuperación de Información

Este backend proporciona:
- Búsqueda sobre artículos de Wikipedia en español
- Endpoints para cada paso del pipeline de RI
- Índice invertido persistente con TF-IDF
"""
from contextlib import asynccontextmanager
from math import sqrt
from collections import Counter

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import DEFAULT_TOP_K, SNIPPET_LENGTH, SUPPORTED_LANGUAGES, DEFAULT_INDEX_LANG, LANGUAGE_MAP
from preprocessing import (
    normalize_text,
    tokenize_text,
    remove_stopwords_tokens,
    lemmatize_or_stem_tokens,
)
from indexing import compute_tf
from persistent_index import PersistentIndex


# =============================================================================
# Inicialización del índice
# =============================================================================
index = PersistentIndex()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Muestra idiomas disponibles al iniciar el servidor."""
    available = index.available_languages()
    if available:
        print(f"Indices disponibles: {', '.join(available)}")
        print("Los indices se cargan bajo demanda en la primera busqueda.")
    else:
        print("AVISO: No hay indices. Ejecuta los scripts de indexacion primero.")
    yield


# =============================================================================
# Aplicación FastAPI
# =============================================================================
app = FastAPI(
    title="WikiSearch - Sistema de Recuperación de Información",
    description="Buscador de artículos de Wikipedia en español usando TF-IDF",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Modelos Pydantic
# =============================================================================
class Document(BaseModel):
    id: str
    text: str


class IndexRequest(BaseModel):
    documents: list[Document]
    language: str = "spanish"


class SearchResult(BaseModel):
    doc_id: str
    title: str
    url: str
    snippet: str
    score: float


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: list[SearchResult]
    processing_time_ms: float


class IndexStats(BaseModel):
    total_documents: int
    vocabulary_size: int
    index_loaded: bool
    current_language: str | None = None
    available_languages: list[str] = []
    build_time_seconds: float | None = None


# =============================================================================
# Endpoints principales
# =============================================================================
@app.get("/")
async def root():
    """Endpoint de bienvenida."""
    return {
        "message": "WikiSearch API - Sistema de Recuperación de Información",
        "version": "1.0.0",
        "available_languages": index.available_languages(),
        "endpoints": {
            "search": "/search?q=<query>&lang=es|ca|pt",
            "stats": "/stats",
            "languages": "/languages",
            "document": "/document/{doc_id}",
        }
    }


@app.get("/languages")
async def get_languages():
    """Lista los idiomas disponibles con estadisticas (sin cargar indices)."""
    import json
    languages = []
    for lang in index.available_languages():
        # Leer stats.json directamente sin cargar el indice completo
        stats_path = index._get_paths(lang)["stats"]
        docs = 0
        terms = 0
        if stats_path.exists():
            with open(stats_path, "r", encoding="utf-8") as f:
                stats_data = json.load(f)
                docs = stats_data.get("total_documents", 0)
                terms = stats_data.get("vocabulary_size", 0)
        languages.append({
            "code": lang,
            "name": {"es": "Castellano", "ca": "Catalán", "pt": "Portugués"}.get(lang, lang),
            "documents": docs,
            "terms": terms,
        })
    return {"languages": languages}


@app.get("/stats", response_model=IndexStats)
async def get_stats():
    """Obtiene estadisticas del indice actual."""
    stats = index.stats
    return IndexStats(
        total_documents=len(index.doc_metadata) if index.current_lang else 0,
        vocabulary_size=len(index.inverted_index) if index.current_lang else 0,
        index_loaded=index.current_lang is not None,
        current_language=index.current_lang,
        available_languages=index.available_languages(),
        build_time_seconds=stats.get("build_time_seconds"),
    )


@app.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Consulta de busqueda"),
    lang: str = Query(DEFAULT_INDEX_LANG, description="Idioma del indice (es, ca, pt)"),
    top_k: int = Query(DEFAULT_TOP_K, ge=1, le=100, description="Numero de resultados"),
):
    """
    Busca documentos relevantes para la consulta.
    
    Proceso:
    1. Carga el indice del idioma seleccionado
    2. Preprocesa la consulta (tokenizacion, stopwords, stemming)
    3. Calcula vector TF-IDF de la consulta
    4. Calcula similitud coseno con documentos del indice
    5. Devuelve los top-k documentos mas relevantes
    """
    import time
    start = time.time()
    
    # Validar idioma
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Idioma '{lang}' no soportado. Usa: {', '.join(SUPPORTED_LANGUAGES)}"
        )
    
    # Cargar indice del idioma si no esta cargado
    if not index.exists(lang):
        raise HTTPException(
            status_code=503,
            detail=f"Indice para '{lang}' no disponible. Ejecuta el script de indexacion."
        )
    
    # Cambiar de idioma si es necesario
    if index.current_lang != lang:
        print(f"Cambiando indice de [{index.current_lang}] a [{lang}]")
        index.unload()
        index.load(lang)
    
    print(f"Buscando '{q}' en indice [{index.current_lang}] ({len(index.doc_metadata)} docs)")
    
    # Obtener idioma NLTK para preprocesamiento
    nltk_lang = LANGUAGE_MAP.get(lang, "spanish")
    
    # Preprocesar consulta
    tokens = tokenize_text(q)
    tokens = remove_stopwords_tokens(tokens, language=nltk_lang)
    tokens = lemmatize_or_stem_tokens(tokens, language=nltk_lang)
    
    if not tokens:
        return SearchResponse(
            query=q,
            total_results=0,
            results=[],
            processing_time_ms=0,
        )
    
    # Calcular vector TF-IDF de la consulta
    term_counts = Counter(tokens)
    n_tokens = len(tokens)
    query_vec: dict[str, float] = {}
    
    for term, count in term_counts.items():
        if term in index.idf:
            tf = count / n_tokens
            query_vec[term] = tf * index.idf[term]
    
    if not query_vec:
        return SearchResponse(
            query=q,
            total_results=0,
            results=[],
            processing_time_ms=(time.time() - start) * 1000,
        )
    
    # Calcular norma de la consulta
    query_norm = sqrt(sum(w * w for w in query_vec.values()))
    
    # Calcular similitud coseno con documentos
    scores: dict[str, float] = {}
    for term, q_weight in query_vec.items():
        postings = index.inverted_index.get(term, [])
        for doc_id, d_weight in postings:
            if doc_id not in scores:
                scores[doc_id] = 0.0
            scores[doc_id] += q_weight * d_weight
    
    # Normalizar por normas de documentos
    results: list[tuple[str, float]] = []
    for doc_id, dot_product in scores.items():
        doc_norm = index.doc_norms.get(doc_id, 0.0)
        if doc_norm > 0 and query_norm > 0:
            cosine_sim = dot_product / (doc_norm * query_norm)
            results.append((doc_id, cosine_sim))
    
    # Ordenar por score descendente
    results.sort(key=lambda x: x[1], reverse=True)
    results = results[:top_k]
    
    # Construir respuesta
    search_results = []
    for doc_id, score in results:
        metadata = index.doc_metadata.get(doc_id, {})
        search_results.append(SearchResult(
            doc_id=doc_id,
            title=metadata.get("title", "Sin título"),
            url=metadata.get("url", ""),
            snippet=metadata.get("snippet", "")[:SNIPPET_LENGTH],
            score=round(score, 4),
        ))
    
    elapsed_ms = (time.time() - start) * 1000
    
    return SearchResponse(
        query=q,
        total_results=len(scores),
        results=search_results,
        processing_time_ms=round(elapsed_ms, 2),
    )


@app.get("/document/{doc_id}")
async def get_document(doc_id: str):
    """Obtiene los metadatos de un documento específico."""
    metadata = index.doc_metadata.get(doc_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return {
        "doc_id": doc_id,
        **metadata,
    }


# =============================================================================
# Endpoints del pipeline de RI (para demostración/memoria)
# =============================================================================
@app.post("/lexical_analysis")
async def lexical_analysis(document: str):
    """Normalización básica del texto."""
    normalized = normalize_text(document)
    return {"original": document, "normalized": normalized}


@app.post("/tokenize")
async def tokenize(document: str):
    """Tokenización del texto."""
    tokens = tokenize_text(document)
    return {"document": document, "tokens": tokens, "count": len(tokens)}


@app.post("/remove_stopwords")
async def remove_stopwords(tokens: list[str], language: str = "spanish"):
    """Eliminación de palabras vacías."""
    filtered = remove_stopwords_tokens(tokens, language=language)
    removed = len(tokens) - len(filtered)
    return {
        "original_tokens": tokens,
        "filtered_tokens": filtered,
        "removed_count": removed,
    }


@app.post("/lemmatize")
async def lemmatize(tokens: list[str], language: str = "spanish"):
    """Lematización/stemming de tokens."""
    lemmatized = lemmatize_or_stem_tokens(tokens, language=language)
    return {
        "original_tokens": tokens,
        "lemmatized_tokens": lemmatized,
    }


@app.post("/weight_terms")
async def weight_terms(terms: list[str]):
    """Calcula pesos TF de términos."""
    weights = compute_tf(terms)
    return {"terms": terms, "weights": weights}


@app.post("/analyze_query")
async def analyze_query(query: str, language: str = "spanish"):
    """
    Muestra el pipeline completo de análisis de una consulta.
    Útil para la memoria y demostración del sistema.
    """
    # Paso 1: Normalización
    normalized = normalize_text(query)
    
    # Paso 2: Tokenización
    tokens = tokenize_text(query)
    
    # Paso 3: Eliminación de stopwords
    tokens_no_sw = remove_stopwords_tokens(tokens, language=language)
    
    # Paso 4: Stemming
    stems = lemmatize_or_stem_tokens(tokens_no_sw, language=language)
    
    # Paso 5: Pesos TF
    tf_weights = compute_tf(stems)
    
    # Paso 6: Pesos TF-IDF (si hay índice)
    tfidf_weights = {}
    if index.exists():
        for term, tf in tf_weights.items():
            idf_val = index.idf.get(term, 0.0)
            tfidf_weights[term] = round(tf * idf_val, 4)
    
    return {
        "query": query,
        "pipeline": {
            "1_normalized": normalized,
            "2_tokens": tokens,
            "3_without_stopwords": tokens_no_sw,
            "4_stems": stems,
            "5_tf_weights": tf_weights,
            "6_tfidf_weights": tfidf_weights if tfidf_weights else "Índice no cargado",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
