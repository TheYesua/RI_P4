# WikiSearch Frontend

Frontend React para el Sistema de Recuperación de Información sobre Wikipedia.

## Stack tecnológico

- **Vite** - Bundler moderno y rápido
- **React 18** - Framework UI
- **TypeScript** - Tipado estático
- **TailwindCSS** - Framework CSS utility-first
- **Lucide React** - Iconos

## Estructura

```
src/
├── main.tsx      # Punto de entrada
├── App.tsx       # Componente principal (buscador + resultados)
├── api.ts        # Cliente API para comunicación con backend
├── types.ts      # Tipos TypeScript (SearchResult, IndexStats, etc.)
└── index.css     # Estilos con Tailwind
```

## Requisitos

- Node.js 18+
- npm

## Instalación

```bash
# Desde el directorio frontend/
npm install
```

**Nota**: Si npm no está disponible en el entorno Anaconda:
```bash
conda install nodejs -c conda-forge
```

## Desarrollo

```bash
npm run dev
```

El frontend estará disponible en http://localhost:3000

## Producción

```bash
npm run build
npm run preview
```

## Conexión con el Backend

El frontend se conecta al backend FastAPI en `http://localhost:8000`.

Asegúrate de que el backend esté ejecutándose:

```bash
cd ../backend
conda activate P4_Final_RI
uvicorn main:app --reload
```

## Características

- **Barra de búsqueda** con indicador de carga
- **Estadísticas del índice** (documentos, vocabulario, estado)
- **Lista de resultados** con:
  - Posición en ranking
  - Título del artículo
  - Score de relevancia (similitud coseno)
  - Snippet del contenido
  - Enlace a Wikipedia original
- **Gestión de estados**: cargando, error, sin resultados, backend offline
- **Interfaz responsive** con TailwindCSS

## Capturas de pantalla

(Pendiente de añadir tras pruebas de integración)
