import re
from functools import lru_cache
from typing import Iterable

import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

# Cache global para stopwords y stemmers (evita recrearlos por cada documento)
_STOPWORDS_CACHE: dict[str, frozenset[str]] = {}
_STEMMER_CACHE: dict[str, SnowballStemmer] = {}


def normalize_text(text: str) -> str:
    """Normalización básica: minúsculas y espacios limpios."""
    text = text.lower()
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize_text(text: str) -> list[str]:
    """Tokenización sencilla basada en expresiones regulares."""
    normalized = normalize_text(text)
    # \w incluye letras, números y guion bajo; con UNICODE mantiene acentos.
    tokens = re.findall(r"\w+", normalized, flags=re.UNICODE)
    return tokens


def _normalize_language(language: str) -> str:
    lang = language.lower()
    mapping = {
        "es": "spanish",
        "español": "spanish",
        "spanish": "spanish",
        "en": "english",
        "inglés": "english",
        "english": "english",
        "fr": "french",
        "francés": "french",
        "french": "french",
    }
    return mapping.get(lang, lang)


def _get_stopwords(language: str) -> frozenset[str]:
    """Obtiene stopwords cacheadas para el idioma."""
    lang = _normalize_language(language)
    if lang not in _STOPWORDS_CACHE:
        try:
            _STOPWORDS_CACHE[lang] = frozenset(stopwords.words(lang))
        except LookupError:
            nltk.download("stopwords", quiet=True)
            _STOPWORDS_CACHE[lang] = frozenset(stopwords.words(lang))
    return _STOPWORDS_CACHE[lang]


def remove_stopwords_tokens(tokens: Iterable[str], language: str = "spanish") -> list[str]:
    sw = _get_stopwords(language)
    return [t for t in tokens if t.lower() not in sw]


def _get_stemmer(language: str) -> SnowballStemmer:
    """Obtiene stemmer cacheado para el idioma."""
    lang = _normalize_language(language)
    if lang not in _STEMMER_CACHE:
        try:
            _STEMMER_CACHE[lang] = SnowballStemmer(lang)
        except ValueError:
            _STEMMER_CACHE[lang] = SnowballStemmer("english")
    return _STEMMER_CACHE[lang]


def lemmatize_or_stem_tokens(tokens: Iterable[str], language: str = "spanish") -> list[str]:
    """Aplica stemming (como aproximación a lematización) con SnowballStemmer."""
    stemmer = _get_stemmer(language)
    return [stemmer.stem(t) for t in tokens]
