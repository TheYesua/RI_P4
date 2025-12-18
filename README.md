# WikiSearch - Sistema de Recuperación de Información

Sistema completo de Recuperación de Información sobre Wikipedia, desarrollado como Práctica 4 de la asignatura de Recuperación de Información.

## Descripción

Buscador semántico sobre artículos de Wikipedia en múltiples idiomas (español, catalán y portugués) utilizando el modelo vectorial TF-IDF con similitud coseno.

### Características

- **Backend**: API REST con FastAPI
- **Frontend**: Interfaz web con React + TypeScript + TailwindCSS
- **Modelo de RI**: TF-IDF con similitud coseno
- **Corpus**: +10 GB de artículos de Wikipedia (ES, CA, PT)

## Estructura del proyecto

```
P4_RI/
├── backend/                 # API FastAPI
│   ├── main.py              # Punto de entrada de la API
│   ├── config.py            # Configuracion centralizada
│   ├── preprocessing.py     # Tokenizacion, stopwords, stemming
│   ├── indexing.py          # Calculo TF-IDF, indice invertido
│   ├── build_index.py       # Indexacion de castellano
│   ├── build_index_ca.py    # Indexacion de catalan
│   ├── build_index_pt.py    # Indexacion de portugues
│   ├── merge_indexes.py     # Fusion de indices por idioma
│   ├── resume_phase3.py     # Reanudar indexacion desde fase 3
│   ├── wikipedia_loader.py  # Carga de articulos de Wikipedia
│   ├── persistent_index.py  # Indice persistente en disco
│   └── requirements.txt
├── frontend/                # Interfaz React
│   ├── src/
│   │   ├── App.tsx          # Componente principal
│   │   ├── api.ts           # Cliente API
│   │   └── types.ts         # Tipos TypeScript
│   ├── package.json
│   └── README.md
├── datos/                   # Corpus de Wikipedia
│   ├── extracted_es/        # Articulos en castellano (~5.8 GB)
│   ├── extracted_ca/        # Articulos en catalan (~1.9 GB)
│   ├── extracted_pt/        # Articulos en portugues (~4 GB)
│   └── index/               # Indices generados
│       ├── es/              # Indice castellano
│       ├── ca/              # Indice catalan
│       └── pt/              # Indice portugues
├── doc_practica4/           # Documentacion y memoria
└── esquema_practica4_RI.md  # Esquema detallado del proyecto
```

## Requisitos

### Backend
- Python 3.11+
- Anaconda (recomendado)

### Frontend
- Node.js 18+
- npm

## Instalación

### Opción A: Instalación automática (recomendada)
```bash
conda create -n P4_Final_RI python=3.11
conda activate P4_Final_RI
python setup.py
```

### Opción B: Instalación manual

#### 1. Clonar el repositorio
```bash
git clone <url-repositorio>
cd P4_RI
```

#### 2. Configurar el entorno Python
```bash
conda create -n P4_Final_RI python=3.11
conda activate P4_Final_RI
pip install -r backend/requirements.txt
```

#### 3. Descargar recursos de NLTK
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
```

#### 4. Instalar dependencias del frontend
```bash
cd frontend
npm install
```

#### 5. Construir el indice

La indexacion se realiza por idiomas separados para evitar problemas de memoria:

```bash
cd backend

# Indexar castellano (~1.9M docs, ~3 horas)
python build_index.py

# Indexar catalan (~744K docs, ~41 min)
python build_index_ca.py

# Indexar portugues (~1M docs, ~48 min)
python build_index_pt.py
```

**Nota**: Los indices se mantienen separados por idioma. El frontend permite seleccionar en que Wikipedia buscar.

## Ejecución

### Backend
```bash
cd backend
uvicorn main:app --reload
```
API disponible en: http://localhost:8000

### Frontend
```bash
cd frontend
npm run dev
```
Interfaz disponible en: http://localhost:3000

## Endpoints de la API

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

## Corpus

| Idioma | Articulos indexados | Terminos unicos | Tiempo |
|--------|---------------------|------------------|--------|
| Castellano (es) | 1,924,610 | 2,657,342 | 188.6 min |
| Catalan (ca) | 743,723 | 1,574,860 | 41.1 min |
| Portugues (pt) | 1,057,354 | 1,603,916 | 47.6 min |
| **Total** | **3,725,687** | - | **~4.6 horas** |

Fuente: [Wikimedia Dumps](https://dumps.wikimedia.org/)

## Problemas conocidos y soluciones

### MemoryError durante la indexacion
**Problema**: Con corpus grandes (+3M docs), el script original fallaba por falta de memoria RAM.

**Solucion**: Se dividio la indexacion en scripts separados por idioma, cada uno guardando en su propio directorio (`index/es/`, `index/ca/`, `index/pt/`). Los indices se mantienen separados.

### Alto consumo de RAM al cargar indices
**Problema**: Cargar el indice de castellano consume ~18GB de RAM en pico.

**Solucion**: Los indices se cargan bajo demanda (no al iniciar el servidor). Docker funciona con CA y PT; para ES se recomienda ejecucion local con 24GB+ RAM.

### Mezcla de idiomas en resultados (RESUELTO)
**Problema**: Busquedas en castellano devolvian resultados en portugues y catalan.

**Causa**: El indice original fue construido antes de separar los scripts por idioma.

**Solucion**: Reconstruir el indice de ES usando solo `extracted_es`.

### Indexacion interrumpida
**Problema**: Si el proceso se interrumpe, hay que empezar de cero.

**Solucion**: Se creo `resume_phase3.py` que permite reanudar desde la fase 3 si las fases 1 y 2 ya completaron.

## Ejecucion con Docker

Para ejecutar el sistema completo con Docker:

```bash
docker compose up
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

**Nota**: Docker tiene limite de 16GB RAM por defecto. El indice de ES requiere ~18GB, por lo que se recomienda usar CA o PT en Docker, o aumentar el limite de RAM en Docker Desktop.

## Autor

Jesus J. Cantero - Ceuta - 2024/25

## Licencia

Proyecto academico - Recuperacion de Informacion
