# Ejecucion con Docker

Esta guia explica como ejecutar el sistema WikiSearch usando Docker para el **backend y frontend**.

**NOTA**: La indexacion se realiza localmente (sin Docker) debido a los requisitos de memoria.

## Requisitos

- Docker 20+
- Docker Compose 2+
- Indice ya construido en `datos/index/` (ver seccion de indexacion)

## Estructura de volumenes

Docker monta el directorio `datos/` del host:

```
Host (Windows/Linux)          Container
---------------------         ---------
./datos/index/es/        ->   /app/datos/index/es/
./datos/index/ca/        ->   /app/datos/index/ca/
./datos/index/pt/        ->   /app/datos/index/pt/
./backend/               ->   /app/backend/
```

## Indexacion (local, sin Docker)

La indexacion debe realizarse localmente para evitar problemas de memoria:

```bash
cd backend

# Indexar cada idioma por separado
python build_index.py       # Castellano (~1.9M docs, ~3h)
python build_index_ca.py    # Catalan (~744K docs, ~41 min)
python build_index_pt.py    # Portugues (~1M docs, ~48 min)
```

**Nota**: Los indices se mantienen separados por idioma. No se fusionan.

## Comandos Docker

### 1. Construir la imagen

```bash
docker-compose build
```

### 2. Ejecutar el backend

```bash
docker-compose up backend
```

API disponible en: http://localhost:8000

### 3. Ejecutar todo (backend + frontend)

```bash
docker-compose up
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

**Nota sobre RAM**: Docker tiene limite de 16GB por defecto. El indice de ES requiere ~18GB en pico. Para ES, usar ejecucion local o aumentar RAM en Docker Desktop > Settings > Resources.

### 4. Detener servicios

```bash
docker-compose down
```

## Ejecucion en servidor remoto

### Copiar indice al servidor

```bash
# Copiar solo el indice (no los datos crudos)
scp -r datos/index/ usuario@servidor:/ruta/proyecto/datos/

# O usar rsync
rsync -avz --progress datos/index/ usuario@servidor:/ruta/proyecto/datos/index/
```

### Ejecutar en servidor

```bash
git clone <repo> wikisearch
cd wikisearch

docker-compose build
docker-compose up -d
```

## Solucion de problemas

### Error: "No such file or directory: datos/index"

El indice no esta construido. Construirlo localmente primero:
```bash
cd backend
python build_index.py
python build_index_ca.py
python build_index_pt.py
```

### Backend no responde o se queda cargando

El indice de castellano requiere ~18GB de RAM. Si Docker tiene limite de 16GB:
- Usar indices de CA o PT (mas ligeros)
- Aumentar RAM en Docker Desktop
- Ejecutar backend localmente sin Docker

### Ver logs en tiempo real

```bash
docker-compose logs -f backend
```
