# WikiSearch Backend

Backend FastAPI para el Sistema de Recuperación de Información sobre Wikipedia.

## Stack tecnológico

- **FastAPI** - Framework web asíncrono
- **NLTK** - Procesamiento de lenguaje natural (stopwords, stemming)
- **Pydantic** - Validación de datos
- **Pickle/JSON** - Persistencia del índice

## Estructura

```
backend/
├── main.py              # API FastAPI con endpoints
├── config.py            # Configuracion centralizada
├── preprocessing.py     # Tokenizacion, stopwords, stemming
├── indexing.py          # Calculo TF-IDF, indice invertido
├── build_index.py       # Indexacion de castellano
├── build_index_ca.py    # Indexacion de catalan
├── build_index_pt.py    # Indexacion de portugues
├── merge_indexes.py     # Fusion de indices por idioma
├── resume_phase3.py     # Reanudar indexacion interrumpida
├── wikipedia_loader.py  # Carga de articulos JSON de Wikipedia
├── persistent_index.py  # Indice persistente en disco
└── requirements.txt     # Dependencias Python
```

## Requisitos

- Python 3.11+
- Entorno Anaconda `P4_Final_RI` (recomendado)

## Instalación

```bash
# Activar entorno
conda activate P4_Final_RI

# Instalar dependencias
pip install -r requirements.txt

# Descargar recursos NLTK (primera vez)
python -c "import nltk; nltk.download('stopwords')"
```

## Uso

### 1. Construir el indice

La indexacion se realiza por idiomas separados para evitar problemas de memoria:

```bash
# Prueba rapida con 10,000 articulos
python build_index.py --max-docs 10000

# Indexacion completa por idiomas
python build_index.py       # Castellano (~3.7M docs, ~3h)
python build_index_ca.py    # Catalan (~1.2M docs, ~1h)
python build_index_pt.py    # Portugues (~1.1M docs, ~1h)

# Fusionar todos los indices
python merge_indexes.py
```

**Si la indexacion se interrumpe** en la fase 3, usar:
```bash
python resume_phase3.py
```

### 2. Ejecutar el servidor

```bash
uvicorn main:app --reload
```

API disponible en: http://localhost:8000

Documentación interactiva: http://localhost:8000/docs

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información de la API |
| GET | `/stats` | Estadísticas del índice |
| GET | `/search?q=<query>` | Búsqueda de documentos |
| GET | `/document/{doc_id}` | Obtener documento por ID |
| POST | `/analyze_query` | Analizar pipeline de una consulta |
| POST | `/lexical_analysis` | Normalización de texto |
| POST | `/tokenize` | Tokenización |
| POST | `/remove_stopwords` | Eliminación de stopwords |
| POST | `/lemmatize` | Stemming/Lematización |
| POST | `/weight_terms` | Cálculo de pesos TF |

## Pipeline de indexación

1. **Carga de documentos**: Lee archivos JSON de WikiExtractor
2. **Preprocesamiento**: 
   - Normalización (minúsculas, limpieza)
   - Tokenización (regex `\w+`)
   - Eliminación de stopwords (NLTK)
   - Stemming (SnowballStemmer)
3. **Ponderación**: Cálculo de TF-IDF
4. **Indexación**: Construcción de índice invertido
5. **Persistencia**: Guardado en disco (pickle + JSON)

## Pipeline de búsqueda

1. **Preprocesamiento de consulta**: Mismo pipeline que documentos
2. **Vectorización**: Cálculo de vector TF-IDF de la consulta
3. **Ranking**: Similitud coseno con documentos del índice
4. **Resultados**: Top-k documentos ordenados por score

## Archivos del indice

Cada idioma tiene su propio directorio en `datos/index/`:

```
index/
├── es/                  # Indice castellano
│   ├── inverted_index.pkl
│   ├── idf.json
│   ├── doc_norms.json
│   ├── doc_metadata.json
│   └── stats.json
├── ca/                  # Indice catalan
└── pt/                  # Indice portugues
```

Despues de ejecutar `merge_indexes.py`, se genera un indice unificado en `index/`.

## Configuración

Editar `config.py` para ajustar:

- `BATCH_SIZE`: Documentos por lote durante indexación
- `MAX_DOCS`: Límite de documentos (None = todos)
- `DEFAULT_TOP_K`: Resultados por defecto en búsqueda
- `SNIPPET_LENGTH`: Longitud del snippet en resultados
