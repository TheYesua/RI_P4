"""
Configuración centralizada del sistema de RI.
"""
from pathlib import Path

# Rutas base
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "datos"
EXTRACTED_DIR = DATA_DIR / "extracted"
INDEX_DIR = DATA_DIR / "index"

# Configuración de indexación
BATCH_SIZE = 1000  # Documentos por lote durante indexación
MAX_DOCS = None  # None = todos los documentos, o un número para limitar (útil para pruebas)

# Configuracion de busqueda
DEFAULT_TOP_K = 20
SNIPPET_LENGTH = 300

# Idiomas soportados
SUPPORTED_LANGUAGES = ["es", "ca", "pt"]
DEFAULT_INDEX_LANG = "es"

# Mapeo de codigo de idioma a nombre NLTK
LANGUAGE_MAP = {
    "es": "spanish",
    "ca": "spanish",  # Catalan usa stopwords/stemmer de español
    "pt": "portuguese",
}
