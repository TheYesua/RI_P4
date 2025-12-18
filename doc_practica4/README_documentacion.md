# Documentación final Práctica 4

Este directorio (`doc_practica4/`) contiene la **memoria y documentación final** de la Práctica 4 de Recuperación de Información.

## Contenido

- `P4_Final_RI_JesusJCantero.tex` - Memoria en LaTeX
- `P4_Final_RI_JesusJCantero.pdf` - Memoria compilada
- Archivos auxiliares de compilación LaTeX (.aux, .log, .toc, etc.)

## Compilación

Para compilar la memoria:

```bash
pdflatex P4_Final_RI_JesusJCantero.tex
```

O usar un editor LaTeX como TeXstudio, Overleaf, etc.

## Estructura de la memoria

1. **Introducción** - Objetivos y descripción general del sistema
2. **Entorno de trabajo** - Python, Node.js, Docker
3. **Estructura del proyecto** - Archivos y directorios
4. **Colección Documental** - Wikipedia ES, CA, PT (+10 GB)
5. **Pipeline de Preprocesamiento** - Tokenización, stopwords, stemming
6. **Modelo de Recuperación** - TF-IDF, similitud coseno, índice invertido
7. **API REST (Backend)** - Endpoints de FastAPI
8. **Interfaz de Usuario (Frontend)** - React + TypeScript
9. **Problemas Encontrados y Soluciones** - MemoryError, multiprocessing, etc.
10. **Conclusiones** - Logros, lecciones aprendidas, mejoras futuras
11. **Referencias**

## Estado

- [x] Memoria actualizada para la Práctica 4
- [x] Capturas de pantalla añadidas (7 imágenes en `capturas/`)
- [ ] Compilar PDF final

## Capturas incluidas

1. `01_interfaz_principal.png` - Interfaz principal
2. `02_busqueda_castellano.png` - Búsqueda en castellano
3. `03_busqueda_catalan.png` - Búsqueda en catalán
4. `04_busqueda_portugues.png` - Búsqueda en portugués
5. `05_consola_backend.png` - Backend FastAPI
6. `06_consola_frontend.png` - Frontend Vite
7. `07_docker_consola.png` - Docker Compose
