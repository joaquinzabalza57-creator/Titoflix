# Docker Titoflix

Guia para ejecutar Titoflix con Docker Compose. El stack levanta frontend, backend, PostgreSQL, MinIO y un contenedor de inicializacion de bucket.

## Servicios

| Servicio     | Contenedor            | Imagen/base                                        | Puerto host    | Responsabilidad                       |
|--------------|-----------------------|----------------------------------------------------|----------------|----------------------------------------|
| `frontend`   | `titoflix-frontend`   | Build de `frontend/Dockerfile` (`node:24-alpine`)  | `3000`         | Next.js en produccion.                |
| `backend`    | `titoflix-backend`    | Build de `backend/Dockerfile` (`python:3.12-slim`) | `8000`         | API FastAPI y procesamiento de media. |
| `postgres`   | `titoflix-postgres`   | `postgres:16-alpine`                               | `5432`         | Base de datos relacional.             |
| `minio`      | `titoflix-minio`      | `minio/minio:latest`                               | `9000`, `9001` | Storage compatible S3.                |
| `minio-init` | `titoflix-minio-init` | `minio/mc:latest`                                  | No expone      | Crea bucket S3 si no existe.          |

## Arquitectura de contenedores

```mermaid
flowchart LR
    Browser[Navegador]
    Front[frontend:3000]
    Back[backend:8000]
    Postgres[(postgres:5432)]
    Minio[(minio:9000)]
    Console[MinIO Console:9001]
    Init[minio-init]

    Browser --> Front
    Front -->|INTERNAL_BACKEND_URL| Back
    Back --> Postgres
    Back --> Minio
    Init --> Minio
    Browser -. gestion .-> Console
```

## Flujo de arranque

```mermaid
sequenceDiagram
    participant Compose as Docker Compose
    participant PG as postgres
    participant M as minio
    participant Init as minio-init
    participant B as backend
    participant F as frontend

    Compose->>PG: Inicia DB
    PG-->>Compose: healthcheck OK
    Compose->>M: Inicia MinIO
    Compose->>Init: Configura alias y bucket
    Init-->>Compose: service_completed_successfully
    Compose->>B: Inicia FastAPI
    B->>PG: create_tables + cuenta admin
    Compose->>F: Inicia Next.js
```

## Requisitos

| Requisito | Detalle |
|-----------|---------|
| Docker | Docker Desktop o Docker Engine. |
| Compose | Docker Compose v2. |
| Puertos libres | `3000`, `8000`, `5432`, `9000`, `9001`. |
| Archivo `.env` | Debe existir en la raiz para credenciales y URLs. |

## Variables de entorno

`docker-compose.yml` toma valores desde un `.env` en la raiz. Algunas variables tienen default en Compose o en el codigo, pero para un arranque reproducible se recomienda definirlas explicitamente.

```env
APP_NAME=Titoflix API
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
HOST_IP=127.0.0.1

POSTGRES_DB=titoflix
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/titoflix

JWT_SECRET=cambiame-en-produccion
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ADMIN_USERNAME=titoflix-admin
ADMIN_PASSWORD=admin1234

MINIO_ROOT_USER=titoflix
MINIO_ROOT_PASSWORD=titoflix-secret
S3_ENDPOINT_URL=http://minio:9000
S3_PUBLIC_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=titoflix
S3_SECRET_KEY=titoflix-secret
S3_BUCKET_NAME=titoflix-media
S3_REGION=us-east-1
S3_MEDIA_PREFIX=media
S3_ASSETS_PREFIX=assets

CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

INTERNAL_BACKEND_URL=http://backend:8000
NEXT_PUBLIC_API_URL=/api/v1
NEXT_PUBLIC_DIRECT_API_URL=/api/v1
NEXT_PUBLIC_BACKEND_URL=
NEXT_PUBLIC_MAX_UPLOAD_SIZE=10485760
```

| Variable                                            | Servicio            | Uso                                                       |
|-----------------------------------------------------|---------------------|-----------------------------------------------------------|
| `APP_NAME`                                          | backend             | Nombre logico de la API.                                 |
| `ENVIRONMENT`                                       | backend             | Entorno de ejecucion.                                    |
| `HOST`, `PORT`, `HOST_IP`                           | backend             | Host/puerto y CORS extra para LAN.                       |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | postgres            | Inicializacion de PostgreSQL.                            |
| `DATABASE_URL`                                      | backend             | Conexion a PostgreSQL desde FastAPI.                     |
| `JWT_SECRET`, `JWT_ALGORITHM`                       | backend             | Firma y algoritmo de tokens JWT.                         |
| `ACCESS_TOKEN_EXPIRE_MINUTES`                       | backend             | Duracion default de tokens de cuenta.                    |
| `ADMIN_USERNAME`, `ADMIN_PASSWORD`                  | backend             | Admin creado/actualizado en startup.                     |
| `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`            | minio, minio-init   | Credenciales root de MinIO.                              |
| `S3_ENDPOINT_URL`                                   | backend             | Endpoint S3 interno (`http://minio:9000`).                |
| `S3_PUBLIC_ENDPOINT_URL`                            | backend             | Endpoint publico configurado.                            |
| `S3_ACCESS_KEY`, `S3_SECRET_KEY`                    | backend, minio-init | Credenciales S3.                                         |
| `S3_BUCKET_NAME`                                    | backend, minio-init | Bucket de media.                                         |
| `S3_REGION`                                         | backend             | Region del cliente S3.                                   |
| `S3_MEDIA_PREFIX`                                   | backend             | Prefijo de videos.                                       |
| `S3_ASSETS_PREFIX`                                  | backend             | Prefijo de imagenes; el codigo usa `assets` por defecto. |
| `CORS_ORIGINS`                                      | backend             | Origenes permitidos.                                     |
| `INTERNAL_BACKEND_URL`                              | frontend            | Destino de rewrites de Next.js.                          |
| `NEXT_PUBLIC_API_URL`                               | frontend            | Base API del navegador.                                  |
| `NEXT_PUBLIC_DIRECT_API_URL`                        | frontend            | Base directa alternativa.                                |
| `NEXT_PUBLIC_BACKEND_URL`                           | frontend            | Prefijo opcional para streams.                           |
| `NEXT_PUBLIC_MAX_UPLOAD_SIZE`                       | frontend            | Limite cliente de uploads.                               |

Nota: si queres que `S3_ASSETS_PREFIX` sea configurable desde Compose, agregalo tambien en `services.backend.environment`; hoy el backend usa su default `assets` si Compose no lo pasa.

## Uso rapido

Desde la raiz:

```bash
docker compose up -d --build
```

| Accion | Comando |
|--------|---------|
| Ver estado | `docker compose ps` |
| Logs backend | `docker compose logs -f backend` |
| Logs frontend | `docker compose logs -f frontend` |
| Logs PostgreSQL | `docker compose logs -f postgres` |
| Logs MinIO | `docker compose logs -f minio` |
| Apagar sin borrar datos | `docker compose down` |
| Apagar y borrar datos | `docker compose down -v` |

## URLs

| Recurso       | URL                            |
|---------------|--------------------------------|
| Frontend      | `http://localhost:3000`        |
| Backend       | `http://localhost:8000`        |
| Swagger       | `http://localhost:8000/docs`   |
| Healthcheck   | `http://localhost:8000/health` |
| MinIO API S3  | `http://localhost:9000`        |
| MinIO Console | `http://localhost:9001`        |

Credenciales de MinIO segun `.env` sugerido:

| Campo    | Valor             |
|----------|-------------------|
| Usuario  | `titoflix`        |
| Password | `titoflix-secret` |
| Bucket   | `titoflix-media`  |

## Dockerfiles

| Dockerfile | Base | Detalles |
|------------|------|----------|
| `backend/Dockerfile` | `python:3.12-slim` | Instala FFmpeg, dependencias Python, copia `src/`, expone `8000` y ejecuta Uvicorn. |
| `frontend/Dockerfile` | `node:24-alpine` | Activa Corepack, usa `pnpm@9.15.9`, instala dependencias, recibe args/env y ejecuta build/start. |

## Volumenes

```mermaid
flowchart TB
    PG[postgres] --> PGVol[(postgres_data)]
    Minio[minio] --> MinioVol[(minio_data)]
```

| Volumen         | Uso                               |
|-----------------|-----------------------------------|
| `postgres_data` | Datos persistentes de PostgreSQL. |
| `minio_data`    | Objetos guardados en MinIO.       |

`docker compose down` conserva volumenes. `docker compose down -v` los elimina.

## Storage y media

El backend guarda videos bajo `S3_MEDIA_PREFIX` y assets bajo `S3_ASSETS_PREFIX`.

| Paso | Descripcion |
|------|-------------|
| 1 | El admin sube el archivo fuente. |
| 2 | FastAPI guarda temporalmente el archivo. |
| 3 | `ffprobe` detecta altura y duracion. |
| 4 | `ffmpeg` genera variantes permitidas: `FHD`, `QHD`, `4K`. |
| 5 | Las variantes y thumbnails/portadas se suben a MinIO. |
| 6 | PostgreSQL guarda referencias como `video_storage_key`, `thumbnail_url`, `portada_url`. |

## Manager Windows

`manager.bat` ofrece un menu interactivo.

| Opcion | Accion                                                         |
|--------|----------------------------------------------------------------|
| 1      | Iniciar servicios (`docker compose up -d`).                    |
| 2      | Ver estado (`docker compose ps`).                              |
| 3      | Ver logs de frontend.                                          |
| 4      | Ver logs de backend.                                           |
| 5      | Ver logs de PostgreSQL.                                        |
| 6      | Ver logs de MinIO.                                             |
| 7      | Detener servicios (`docker compose down`).                     |
| 8      | Reconstruir frontend/backend sin cache y recrear contenedores. |
| 9      | Resetear tablas de PostgreSQL y recrear bucket MinIO.          |
| 10     | Iniciar tunel publico con `cloudflare/cloudflared`.            |
| 11     | Ver URL/logs del tunel publico.                                |
| 12     | Detener tunel publico.                                         |

El script actualiza `HOST_IP` en `.env` antes de iniciar/reconstruir para facilitar acceso desde la red local.

## Reset de datos

| Reset | Comando | Borra MinIO |
|-------|---------|-------------|
| Solo tablas | `docker compose exec backend python -c "from src.db import reset_database; reset_database()"` | No |
| Volumenes completos | `docker compose down -v` | Si |
| Manager opcion 9 | `.\manager.bat` y elegir `9` | Si, recrea bucket |

## Acceso desde otra maquina

El navegador llama a `/api/v1` sobre el mismo host del frontend. Next.js reenvia internamente al backend, por lo que para uso normal basta con publicar el puerto `3000`.

| Opcion | Comentario |
|--------|------------|
| Port forwarding de `3000` | Suficiente para LAN si firewall lo permite. |
| Reverse proxy con dominio | Recomendado para despliegue estable. |
| VPS | Requiere configurar variables publicas y certificados. |
| Cloudflare Tunnel | Disponible desde `manager.bat`. |

No hace falta exponer `8000` si los usuarios acceden a traves del frontend.

## Debugging

| Sintoma                 | Revision sugerida                                                                   |
|-------------------------|--------------------------------------------------------------------------------------|
| Frontend no carga       | `docker compose logs -f frontend`, puerto `3000`, build de Next.                    |
| API no responde         | `docker compose logs -f backend`, `http://localhost:8000/health`.                   |
| Backend no conecta a DB | Validar `DATABASE_URL`, healthcheck de postgres y logs.                             |
| Upload falla            | Revisar logs backend, disponibilidad de FFmpeg y credenciales S3.                   |
| Videos no reproducen    | Revisar `/playback`, `/stream`, token temporal, objetos en MinIO y headers `Range`. |
| MinIO no crea bucket    | Revisar `minio-init`, `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `S3_BUCKET_NAME`.   |

Comandos utiles:

```bash
docker compose logs -f backend
docker compose logs -f minio-init
docker compose exec backend python -c "from src.config import settings; print(settings.DATABASE_URL)"
docker compose exec backend python -c "from src.db import create_tables; create_tables()"
```

## Mantenimiento

| Cambio | Archivos a revisar |
|--------|--------------------|
| Variables de entorno | `.env.example`, `docker-compose.yml`, `README.md`, `backend/README.md`, `frontend/README.md`, `DOCKER.md` |
| Puertos o nombres de servicio | `docker-compose.yml`, rewrites de Next y CORS |
| Storage | `S3_*`, `StorageService`, `minio-init` |
| Procesamiento de video | `backend/Dockerfile`, FFmpeg y `VideoProcessingService` |
| Dependencias frontend | `package.json`, lockfile usado por Docker y `frontend/Dockerfile` |
