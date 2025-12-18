# Datos - Corpus de Wikipedia

Este directorio contiene el corpus documental del sistema de Recuperación de Información, compuesto por artículos de Wikipedia en español, catalán y portugués.

## Contenido

```
datos/
├── extracted_es/     # Articulos castellano (JSON, ~5.8 GB)
├── extracted_ca/     # Articulos catalan (JSON, ~1.9 GB)
├── extracted_pt/     # Articulos portugues (JSON, ~4 GB)
└── index/            # Indices generados
    ├── es/           # Indice castellano
    ├── ca/           # Indice catalan
    └── pt/           # Indice portugues
```

## Estadísticas del corpus

| Idioma | Artículos | Tamaño extraído | Dump comprimido |
|--------|-----------|-----------------|-----------------|
| Español | 4,027,640 | ~5.8 GB | 4.63 GB |
| Catalán | 1,284,033 | ~1.9 GB | ~1.2 GB |
| Portugués | ~1,100,000 | ~4 GB | ~2.5 GB |
| **Total** | **~6,400,000** | **~11.7 GB** | - |

## Resultados de indexacion

| Idioma | Documentos indexados | Terminos unicos | Tiempo |
|--------|----------------------|-----------------|--------|
| Castellano (es) | 1,924,610 | 2,657,342 | 188.6 min |
| Catalan (ca) | 743,723 | 1,574,860 | 41.1 min |
| Portugues (pt) | 1,057,354 | 1,603,916 | 47.6 min |
| **Total** | **3,725,687** | - | **~4.6 horas** |

## Construccion del indice

La indexacion se realiza por idiomas separados desde el directorio `backend/`:

```bash
cd backend

# Indexar cada idioma por separado
python build_index.py       # Castellano (~3h)
python build_index_ca.py    # Catalan (~45min)
python build_index_pt.py    # Portugues (~50min)
```

**Nota**: Los indices se mantienen separados por idioma. El frontend permite seleccionar en que Wikipedia buscar.

## Archivos del indice

Cada idioma genera los siguientes archivos en su directorio:

| Archivo | Descripcion |
|---------|-------------|
| `inverted_index.pkl` | Indice invertido (pickle) |
| `idf.json` | IDF de terminos |
| `doc_norms.json` | Normas de documentos |
| `doc_metadata.json` | Metadatos (titulo, URL, snippet) |
| `stats.json` | Estadisticas de construccion |

## Formato de los articulos extraidos

WikiExtractor genera archivos JSON con una linea por articulo:

```json
{"id": "12", "url": "https://es.wikipedia.org/wiki/...", "title": "Titulo", "text": "Contenido del articulo..."}
```

Los archivos se organizan en subdirectorios (AA, AB, AC, ...) con archivos `wiki_00`, `wiki_01`, etc.

## Problemas conocidos

### Alto consumo de RAM
- Cargar el indice de castellano requiere ~18GB de RAM en pico
- Requiere maquina con 24GB+ RAM para el indice de ES
- Los indices de CA y PT son mas ligeros (~4-6GB cada uno)
- Docker tiene limite de 16GB por defecto, insuficiente para ES

### Documentos en otros idiomas
- El corpus de Wikipedia en espanol contiene algunos articulos con texto en portugues o catalan
- Esto es inherente al dump original de Wikipedia
- Solucion potencial: filtrar con libreria de deteccion de idioma (langdetect)

## Fuentes

- Wikipedia en castellano: https://dumps.wikimedia.org/eswiki/
- Wikipedia en catalan: https://dumps.wikimedia.org/cawiki/
- Wikipedia en portugues: https://dumps.wikimedia.org/ptwiki/

Licencia de los datos: [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)
