# Esquema de realización de la Práctica 4 – Sistema de Recuperación de Información

## 0. Objetivo general
- Desarrollar un sistema completo de Recuperación de Información (RI) compuesto por:
  - Backend en FastAPI para procesar documentos, construir el índice e implementar la búsqueda.
  - Frontend en ReactJS para enviar consultas y mostrar resultados.
  - Colección documental real (> 10 GB) y justificada.
- Entregar memoria, código completo (backend + frontend) y repositorio GitHub con documentación e instrucciones.

---

## 1. Preparación del entorno [DONE]

### 1.1. Entorno Python / Backend
- **Entorno Anaconda**: `P4_Final_RI` con Python 3.11
- **Dependencias instaladas**:
  ```bash
  pip install fastapi uvicorn nltk pydantic requests tqdm wikiextractor
  ```

### 1.2. Entorno JavaScript / Frontend
- **Proyecto creado con Vite** (más moderno que create-react-app)
- **Stack**: React 18 + TypeScript + TailwindCSS + Lucide Icons
- **Instalación**:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

### 1.3. Control de versiones
- Repositorio Git local configurado
- Estructura del proyecto:
  ```
  P4_RI/
  ├── backend/       # API FastAPI
  ├── frontend/      # React + Vite
  ├── datos/         # Corpus Wikipedia
  └── doc_practica4/ # Memoria LaTeX
  ```

### 1.4. Problemas encontrados y soluciones
- **npm no disponible**: Node.js no estaba en el entorno conda. Solución: `conda install nodejs -c conda-forge`

---

## 2. Diseño de la arquitectura del sistema
- **2.1. Visión general**
  - Cliente web (React) → API REST (FastAPI) → Módulos de RI → Almacenamiento del índice y del corpus.
- **2.2. Módulos principales**
  - Módulo de ingestión / crawling (opcional, pero valorable).
  - Módulo de preprocesamiento (análisis léxico, tokenización, stopwords, lematización/stemming).
  - Módulo de ponderación de términos (TF, IDF, TF-IDF u otros).
  - Módulo de indexación (índice invertido, estructuras de datos, almacenamiento en disco/BD).
  - Módulo de búsqueda (procesamiento de la consulta, cálculo de similitud / ranking, recuperación de documentos).
- **2.3. Flujo de datos**
  - Colección documental → pipeline de preprocesado → términos ponderados → selección de términos → índice invertido → consultas → resultados ordenados.

---

## 3. Backend con FastAPI [DONE]

### 3.1. Estructura del proyecto backend
```
backend/
├── main.py              # API FastAPI con todos los endpoints
├── config.py            # Configuracion centralizada (rutas, parametros)
├── preprocessing.py     # Tokenizacion, stopwords, stemming
├── indexing.py          # Calculo TF-IDF, construccion indice invertido
├── build_index.py       # Indexacion de castellano
├── build_index_ca.py    # Indexacion de catalan
├── build_index_pt.py    # Indexacion de portugues
├── merge_indexes.py     # Fusion de indices por idioma
├── resume_phase3.py     # Reanudar indexacion interrumpida
├── wikipedia_loader.py  # Carga de articulos JSON de Wikipedia
├── persistent_index.py  # Indice persistente en disco (pickle/JSON)
└── requirements.txt     # Dependencias Python
```

### 3.2. Implementación de endpoints básicos (según cabeceras propuestas)
- **`POST /crawl` (opcional)**
  - Entrada: `url: str`, `depth: int`.
  - Salida (esquema): resumen del número de documentos obtenidos / rutas de los ficheros.
  - Tareas: implementar o simular un crawler; almacenar documentos en disco.
- **`POST /lexical_analysis`**
  - Entrada: documento o identificador de documento.
  - Salida: texto normalizado (codificación, limpieza básica, etc.).
- **`POST /tokenize`**
  - Entrada: texto.
  - Salida: lista de tokens.
- **`POST /remove_stopwords`**
  - Entrada: lista de tokens.
  - Salida: lista de tokens sin palabras vacías.
- **`POST /lemmatize`**
  - Entrada: lista de tokens.
  - Salida: lista de lemas o raíces morfológicas.
- **`POST /weight_terms`**
  - Entrada: términos / documentos.
  - Salida: términos ponderados (TF, IDF, TF-IDF, etc.).
- **`POST /select_terms`**
  - Entrada: términos ponderados.
  - Salida: subconjunto de términos relevantes (términos de indexación).
- **`POST /index`**
  - Entrada: términos de indexación por documento.
  - Salida: creación / actualización del índice invertido persistente.
- **`GET /search`**
  - Entrada: `query: str`.
  - Salida: lista de documentos relevantes ordenados por puntuación, con metadatos mínimos para mostrarlos en el frontend.

### 3.3. Proceso de indexación (offline o batch)
- Definir un script / proceso en el backend que:
  - Recorra todos los documentos de la colección.
  - Aplique secuencialmente: análisis léxico → tokenización → stopwords → lematización/stemming.
  - Calcule ponderaciones (TF, IDF, TF-IDF, etc.).
  - Seleccione términos de indexación.
  - Construya el índice invertido (estructura adecuada para búsquedas rápidas).
  - Guarde el índice en disco (formato propio, JSON, pickle, base de datos ligera, etc.).

### 3.4. Proceso de búsqueda (online)
- Pasos para cada consulta recibida por `GET /search`:
  - Preprocesar la consulta de forma análoga a los documentos (tokenización, stopwords, lematización, ponderación).
  - Consultar el índice invertido.
  - Calcular la similitud / ranking (por ejemplo, modelo vectorial con TF-IDF y coseno).
  - Devolver una lista de resultados con título, snippet/resumen y algún identificador de documento.

---

## 4. Frontend con ReactJS [DONE]

### 4.1. Estructura del proyecto frontend
```
frontend/
├── index.html           # HTML principal
├── package.json         # Dependencias npm
├── vite.config.ts       # Configuración Vite
├── tailwind.config.js   # Configuración TailwindCSS
├── tsconfig.json        # Configuración TypeScript
├── public/
│   └── wikipedia.svg    # Favicon
└── src/
    ├── main.tsx         # Punto de entrada React
    ├── App.tsx          # Componente principal (buscador)
    ├── api.ts           # Cliente API para el backend
    ├── types.ts         # Tipos TypeScript
    └── index.css        # Estilos con Tailwind
```

### 4.2. Stack tecnológico
- **Vite**: Bundler moderno (más rápido que create-react-app)
- **React 18**: Framework UI
- **TypeScript**: Tipado estático
- **TailwindCSS**: Framework CSS utility-first
- **Lucide React**: Iconos

### 4.2. Pantallas y componentes mínimos
- **Página principal de búsqueda**
  - Campo de texto para la consulta.
  - Botón de enviar.
  - Lista de resultados.
- **Componentes clave**
  - Componente de formulario de búsqueda.
  - Componente de resultados (lista de documentos).
  - Componente de resultado individual (título, snippet, enlace / identificador).
  - Gestión de estados: cargando, error, sin resultados, etc.

### 4.3. Comunicación con el backend
- Implementar función de búsqueda que haga:
  - `fetch("http://localhost:8000/search?query=" + consulta)` (o equivalente con librería HTTP elegida).
  - Parseo de la respuesta JSON.
  - Actualización del estado en React para mostrar los resultados.
- Manejo básico de errores (timeout, servidor caído, etc.).

### 4.4. Estilo y usabilidad
- Añadir un estilo sencillo pero claro (CSS o framework ligero).
- Asegurar que la interfaz es usable: mensajes de ayuda, indicación de carga, etc.

---

## 5. Selección y preparación de la colección documental (> 10 GB) [DONE]

### 5.1. Elección de la fuente
- **Fuente elegida**: Dumps de Wikipedia (Wikimedia)
- **Idiomas**: Español, Catalán y Portugués
- **Justificación**:
  - Wikipedia ofrece variedad temática (ciencia, historia, cultura, etc.)
  - Experiencia de búsqueda realista para el usuario
  - Metadatos ricos (título, URL, categorías)
  - Licencia libre (CC BY-SA)
  - Descarga sencilla (un archivo por idioma)

### 5.2. Obtención de los datos
- **Método**: Descarga de dumps oficiales de Wikimedia
- **URLs**:
  - https://dumps.wikimedia.org/eswiki/latest/
  - https://dumps.wikimedia.org/cawiki/latest/
  - https://dumps.wikimedia.org/ptwiki/latest/
- **Extracción**: WikiExtractor (convierte XML a JSON)

### 5.3. Estadísticas del corpus

| Idioma | Articulos indexados | Terminos unicos | Tiempo indexacion |
|--------|---------------------|-----------------|-------------------|
| Castellano | 3,725,687 | 4,099,301 | ~3 horas |
| Catalan | ~1,200,000 | ~1,500,000 | ~1 hora |
| Portugues | ~1,100,000 | ~1,400,000 | ~1 hora |
| **Total** | **~6,000,000** | - | ~5 horas |

### 5.4. Problemas encontrados y soluciones

#### Error de multiprocessing en Windows (extraccion)
- **Error**: `ValueError: cannot find context for 'fork'`
- **Causa**: WikiExtractor usa `fork` que solo existe en Linux/Mac
- **Solucion**: Usar WSL (Windows Subsystem for Linux) para la extraccion con 4 procesos paralelos

#### Corpus insuficiente
- **Problema**: Wikipedia castellano solo (~6 GB) no llegaba a 10 GB
- **Solucion**: Anadir Wikipedia en catalan y portugues

#### MemoryError durante indexacion
- **Error**: `MemoryError` al construir el indice invertido con +3M documentos
- **Causa**: El indice invertido completo no cabe en RAM (~20-40 GB necesarios)
- **Solucion**: Dividir la indexacion en scripts separados por idioma, cada uno guardando en su propio directorio (`index/es/`, `index/ca/`, `index/pt/`). Luego fusionar con `merge_indexes.py`.

#### Checkpoint corrupto
- **Error**: `EOFError: Ran out of input` al reanudar indexacion
- **Causa**: Archivo checkpoint.pkl corrupto por interrupcion durante escritura
- **Solucion**: Eliminar sistema de checkpoints y crear `resume_phase3.py` que reanuda desde la fase 3 usando los archivos intermedios (`doc_metadata.json`, `idf.json`).

#### Porcentaje de progreso incorrecto
- **Problema**: El contador mostraba >100% durante la indexacion
- **Causa**: El total estimado de documentos no coincidia con el real despues del filtrado
- **Solucion**: Actualizar el total conocido de documentos (3,725,687 para castellano) en los scripts.

#### Alto consumo de RAM al cargar indices
- **Problema**: Cargar el indice de castellano consume ~18GB de RAM en pico
- **Causa**: El indice invertido en pickle contiene ~2.6M terminos con millones de postings
- **Impacto**: Requiere maquina con 24GB+ RAM para cargar el indice de ES
- **Mitigacion**: Los indices se cargan bajo demanda, no al iniciar el servidor
- **Docker**: Limite de 16GB por defecto es insuficiente para ES; CA y PT funcionan correctamente
- **Alternativas futuras**: Usar base de datos (SQLite, Redis) en lugar de cargar todo en memoria

#### Documentos en otros idiomas dentro del corpus (RESUELTO)
- **Problema**: Busquedas en castellano devolvian resultados en portugues y catalan
- **Causa**: El indice original fue construido antes de separar los scripts por idioma, mezclando documentos de ES, CA y PT
- **Solucion**: Reconstruir el indice de ES usando solo `extracted_es` (de 3.7M a 1.9M docs)
- **Estado**: Resuelto - los resultados ahora son correctos en cada idioma

### 5.5. Scripts de indexacion
- `build_index.py` - Indexacion de castellano (guarda en `index/es/`)
- `build_index_ca.py` - Indexacion de catalan (guarda en `index/ca/`)
- `build_index_pt.py` - Indexacion de portugues (guarda en `index/pt/`)
- `resume_phase3.py` - Reanudar indexacion interrumpida desde fase 3

**Nota**: Los indices se mantienen separados por idioma. El sistema carga dinamicamente el indice segun el idioma seleccionado en el frontend.

### 5.6. Organizacion del corpus e indices
```
datos/
├── extracted_es/     # Articulos castellano (JSON, ~5.8 GB)
│   ├── AA/
│   │   ├── wiki_00   # Lineas JSON: {"id", "title", "url", "text"}
│   │   └── ...
│   └── ...
├── extracted_ca/     # Articulos catalan (JSON, ~1.9 GB)
├── extracted_pt/     # Articulos portugues (JSON, ~4 GB)
└── index/            # Indices generados
    ├── es/           # Indice castellano
    │   ├── inverted_index.pkl
    │   ├── idf.json
    │   ├── doc_norms.json
    │   ├── doc_metadata.json
    │   └── stats.json
    ├── ca/           # Indice catalan
    └── pt/           # Indice portugues
```

---

## 6. Evaluación del sistema y experimentos
- Definir un conjunto de consultas de prueba representativas.
- Ejecutar búsquedas y analizar:
  - Relevancia cualitativa de los resultados.
  - Ejemplos de documentos recuperados.
- (Opcional) Medir métricas simples (precisión en el top-k, cobertura, etc.) si se dispone de juicios de relevancia.
- Guardar capturas de pantalla del frontend con ejemplos de consultas y resultados.

---

## 7. Memoria y entrega final

### 7.1. Estructura sugerida de la memoria
- Introducción y objetivos.
- Descripción de la colección documental.
- Arquitectura del sistema (diagramas, componentes backend y frontend).
- Detalle del pipeline de RI:
  - Análisis léxico, tokenización, stopwords, lematización/stemming.
  - Ponderación, selección de términos e indexación.
  - Modelo de búsqueda y ranking.
- Descripción del frontend y de la interacción usuario-sistema.
- Experimentos y resultados de búsqueda (consultas de ejemplo, capturas de pantalla).
- Problemas encontrados, decisiones de diseño y posibles mejoras futuras.
- Conclusiones.

### 7.2. Contenido del repositorio GitHub
- Código completo del backend y del frontend.
- Carpeta `docs/` con la memoria (PDF) y recursos adicionales.
- Ejemplos de corpus o instrucciones para descargarlo.
- `README.md` con:
  - Requisitos.
  - Instrucciones de instalación y ejecución (backend y frontend).
  - Ejemplos mínimos de uso.

---

## 8. Plan de trabajo y progreso

### Fase 1: Preparación del entorno [DONE]
- [x] Crear entorno Anaconda `P4_Final_RI`
- [x] Instalar dependencias Python (fastapi, uvicorn, nltk, etc.)
- [x] Crear proyecto frontend con Vite + React + TypeScript
- [x] Instalar dependencias npm

### Fase 2: Obtención del corpus [DONE]
- [x] Descargar dump Wikipedia español (4.63 GB comprimido)
- [x] Descargar dump Wikipedia catalán (~1.2 GB comprimido)
- [x] Descargar dump Wikipedia portugués (~2.5 GB comprimido)
- [x] Extraer artículos con WikiExtractor (usando WSL)
- [x] Verificar tamaño total > 10 GB

### Fase 3: Implementación del backend [DONE]
- [x] Módulo de preprocesamiento (preprocessing.py)
- [x] Módulo de indexación (indexing.py)
- [x] Cargador de Wikipedia (wikipedia_loader.py)
- [x] Índice persistente (persistent_index.py)
- [x] Script de indexación batch (build_index.py)
- [x] API FastAPI con endpoints (main.py)

### Fase 4: Implementación del frontend [DONE]
- [x] Estructura del proyecto Vite
- [x] Componente de búsqueda (App.tsx)
- [x] Cliente API (api.ts)
- [x] Estilos con TailwindCSS

### Fase 5: Integracion y pruebas [DONE]
- [x] Construir indice castellano (1,924,610 articulos, 188.6 min)
- [x] Construir indice catalan (743,723 articulos, 41.1 min)
- [x] Construir indice portugues (1,057,354 articulos, 47.6 min)
- [x] Adaptar backend para indices separados por idioma
- [x] Adaptar frontend con selector de idioma
- [x] Probar busquedas end-to-end (funciona en local y Docker)
- [x] Corregir mezcla de idiomas en indice ES
- [ ] Capturas de pantalla para memoria

### Fase 6: Documentacion [IN PROGRESS]
- [x] Actualizar README con instrucciones de indexacion por idiomas
- [x] Actualizar DOCKER.md (eliminar indexer obsoleto)
- [x] Documentar problemas y soluciones encontrados
- [x] Frontend con info academica (Jesus J. Cantero, Ceuta, 2024/25)
- [ ] Completar memoria LaTeX
- [ ] Capturas de pantalla
- [ ] Preparar repositorio GitHub
