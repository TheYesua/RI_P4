"""
Índice invertido persistente para el sistema de RI.

Soporta índices separados por idioma:
- index/es/ - Índice castellano
- index/ca/ - Índice catalán
- index/pt/ - Índice portugués

Cada índice contiene:
- inverted_index.pkl - Índice invertido
- idf.json - IDF de términos
- doc_norms.json - Normas de documentos
- doc_metadata.json - Metadatos (título, URL, snippet)
- stats.json - Estadísticas
"""
import json
import pickle
from pathlib import Path
from typing import Any
from config import INDEX_DIR, SUPPORTED_LANGUAGES, DEFAULT_INDEX_LANG


class PersistentIndex:
    """
    Índice invertido con persistencia en disco.
    Soporta múltiples idiomas con índices separados.
    
    Estructura de archivos:
    index/
    ├── es/
    │   ├── inverted_index.pkl
    │   ├── idf.json
    │   ├── doc_norms.json
    │   ├── doc_metadata.json
    │   └── stats.json
    ├── ca/
    └── pt/
    """
    
    def __init__(self, base_dir: Path = INDEX_DIR):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Idioma actualmente cargado
        self._current_lang: str | None = None
        
        # Datos en memoria (se cargan bajo demanda)
        self._inverted_index: dict[str, list[tuple[str, float]]] | None = None
        self._idf: dict[str, float] | None = None
        self._doc_norms: dict[str, float] | None = None
        self._doc_metadata: dict[str, dict[str, str]] | None = None
        self._stats: dict[str, Any] | None = None
    
    def _get_lang_dir(self, lang: str) -> Path:
        """Obtiene el directorio del índice para un idioma."""
        return self.base_dir / lang
    
    def _get_paths(self, lang: str) -> dict[str, Path]:
        """Obtiene las rutas de archivos para un idioma."""
        lang_dir = self._get_lang_dir(lang)
        return {
            "inverted_index": lang_dir / "inverted_index.pkl",
            "idf": lang_dir / "idf.json",
            "doc_norms": lang_dir / "doc_norms.json",
            "doc_metadata": lang_dir / "doc_metadata.json",
            "stats": lang_dir / "stats.json",
        }
    
    @property
    def current_lang(self) -> str | None:
        """Idioma actualmente cargado."""
        return self._current_lang
    
    def available_languages(self) -> list[str]:
        """Lista de idiomas con índice disponible."""
        available = []
        for lang in SUPPORTED_LANGUAGES:
            if self.exists(lang):
                available.append(lang)
        return available
    
    def exists(self, lang: str | None = None) -> bool:
        """Verifica si el índice existe en disco para un idioma."""
        if lang is None:
            lang = self._current_lang or DEFAULT_INDEX_LANG
        paths = self._get_paths(lang)
        return (
            paths["inverted_index"].exists() and
            paths["idf"].exists() and
            paths["doc_norms"].exists() and
            paths["doc_metadata"].exists()
        )
    
    def load(self, lang: str | None = None) -> bool:
        """Carga el índice de un idioma desde disco a memoria."""
        if lang is None:
            lang = DEFAULT_INDEX_LANG
        
        # Si ya está cargado este idioma, no recargar
        if self._current_lang == lang and self._inverted_index is not None:
            return True
        
        if not self.exists(lang):
            return False
        
        paths = self._get_paths(lang)
        print(f"Cargando índice [{lang}] desde disco...")
        
        # Cargar índice invertido
        with open(paths["inverted_index"], "rb") as f:
            self._inverted_index = pickle.load(f)
        
        # Cargar IDF
        with open(paths["idf"], "r", encoding="utf-8") as f:
            self._idf = json.load(f)
        
        # Cargar normas de documentos
        with open(paths["doc_norms"], "r", encoding="utf-8") as f:
            self._doc_norms = json.load(f)
        
        # Cargar metadatos
        with open(paths["doc_metadata"], "r", encoding="utf-8") as f:
            self._doc_metadata = json.load(f)
        
        # Cargar estadísticas si existen
        if paths["stats"].exists():
            with open(paths["stats"], "r", encoding="utf-8") as f:
                self._stats = json.load(f)
        else:
            self._stats = {}
        
        self._current_lang = lang
        print(f"Índice [{lang}] cargado: {len(self._doc_metadata)} documentos, {len(self._inverted_index)} términos")
        return True
    
    def save(
        self,
        inverted_index: dict[str, list[tuple[str, float]]],
        idf: dict[str, float],
        doc_norms: dict[str, float],
        doc_metadata: dict[str, dict[str, str]],
        stats: dict[str, Any] | None = None,
        lang: str = DEFAULT_INDEX_LANG,
    ) -> None:
        """Guarda el índice en disco para un idioma."""
        lang_dir = self._get_lang_dir(lang)
        lang_dir.mkdir(parents=True, exist_ok=True)
        paths = self._get_paths(lang)
        
        print(f"Guardando índice [{lang}] en disco...")
        
        # Guardar índice invertido
        with open(paths["inverted_index"], "wb") as f:
            pickle.dump(inverted_index, f)
        
        # Guardar IDF
        with open(paths["idf"], "w", encoding="utf-8") as f:
            json.dump(idf, f)
        
        # Guardar normas
        with open(paths["doc_norms"], "w", encoding="utf-8") as f:
            json.dump(doc_norms, f)
        
        # Guardar metadatos
        with open(paths["doc_metadata"], "w", encoding="utf-8") as f:
            json.dump(doc_metadata, f)
        
        # Guardar estadísticas
        if stats:
            with open(paths["stats"], "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2)
        
        # Actualizar cache en memoria
        self._inverted_index = inverted_index
        self._idf = idf
        self._doc_norms = doc_norms
        self._doc_metadata = doc_metadata
        self._stats = stats
        self._current_lang = lang
        
        print(f"Índice [{lang}] guardado: {len(doc_metadata)} documentos, {len(inverted_index)} términos")
    
    @property
    def inverted_index(self) -> dict[str, list[tuple[str, float]]]:
        if self._inverted_index is None:
            self.load(DEFAULT_INDEX_LANG)
        return self._inverted_index or {}
    
    @property
    def idf(self) -> dict[str, float]:
        if self._idf is None:
            self.load(DEFAULT_INDEX_LANG)
        return self._idf or {}
    
    @property
    def doc_norms(self) -> dict[str, float]:
        if self._doc_norms is None:
            self.load(DEFAULT_INDEX_LANG)
        return self._doc_norms or {}
    
    @property
    def doc_metadata(self) -> dict[str, dict[str, str]]:
        if self._doc_metadata is None:
            self.load(DEFAULT_INDEX_LANG)
        return self._doc_metadata or {}
    
    @property
    def stats(self) -> dict[str, Any]:
        if self._stats is None:
            self._stats = {}
        return self._stats
    
    def get_document(self, doc_id: str) -> dict[str, str] | None:
        """Obtiene los metadatos de un documento por su ID."""
        return self.doc_metadata.get(doc_id)
    
    def clear(self, lang: str | None = None) -> None:
        """Elimina el índice de disco y memoria para un idioma."""
        if lang is None:
            lang = self._current_lang or DEFAULT_INDEX_LANG
        
        paths = self._get_paths(lang)
        for path in paths.values():
            if path.exists():
                path.unlink()
        
        if self._current_lang == lang:
            self._inverted_index = None
            self._idf = None
            self._doc_norms = None
            self._doc_metadata = None
            self._stats = None
            self._current_lang = None
    
    def unload(self) -> None:
        """Descarga el índice de memoria sin eliminarlo de disco."""
        self._inverted_index = None
        self._idf = None
        self._doc_norms = None
        self._doc_metadata = None
        self._stats = None
        self._current_lang = None
