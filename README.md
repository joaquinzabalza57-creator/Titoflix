# Titoflix

Titoflix es una aplicacion de streaming full stack con frontend Next.js, backend FastAPI, PostgreSQL para datos relacionales y MinIO/S3 para videos e imagenes. Permite registrar cuentas, crear perfiles, explorar catalogo, reproducir peliculas y episodios, guardar progreso, administrar "Mi lista" y cargar contenido desde una consola admin.

## Objetivo

El objetivo del sistema es separar claramente la experiencia de usuario, la API de negocio y la persistencia de datos/archivos para facilitar mantenimiento, despliegue con Docker y futuras extensiones.

| Area       | Responsabilidad                                                                              |
|------------|--------------------------------------------------------------------------------------------- |
| Frontend   | UI de login, perfiles, catalogo, detalle, reproduccion y administracion.                     |
| Backend    | API REST, autenticacion JWT, reglas de negocio, procesamiento de video y streaming.          |
| PostgreSQL | Persistencia de cuentas, perfiles, catalogo, temporadas, episodios, vistas y calificaciones. |
| MinIO/S3   | Almacenamiento de videos, variantes generadas, portadas, thumbnails y avatares.              |
| Docker     | Orquestacion local de servicios y volumenes persistentes.                                    |

## Tecnologias

| Capa          | Tecnologias                                                                      |
|---------------|----------------------------------------------------------------------------------|
| Frontend      | Next.js 16, React 19, TypeScript, Tailwind CSS 4, lucide-react                   |
| Backend       | Python 3.12, FastAPI, Uvicorn, SQLAlchemy, Pydantic, python-jose, passlib/bcrypt |
| Base de datos | PostgreSQL 16                                                                    |
| Storage       | MinIO compatible con S3, boto3                                                   |
| Media         | FFmpeg/ffprobe                                                                   |
| Contenedores  | Docker, Docker Compose v2                                                        |

## Estructura

```text
.
|-- README.md
|-- DOCKER.md
|-- docker-compose.yml
|-- manager.bat
|-- backend/
|   |-- README.md
|   |-- Dockerfile
|   |-- requirements.txt
|   `-- src/
`-- frontend/
    |-- README.md
    |-- Dockerfile
    |-- package.json
    |-- app/
    |-- components/
    `-- lib/
```

## Arquitectura

```mermaid
flowchart LR
    Browser[Navegador] --> Next[Frontend Next.js]
    Next -->|/api/v1 via rewrites| API[Backend FastAPI]
    API --> DB[(PostgreSQL)]
    API --> S3[(MinIO / S3)]
    API --> FFmpeg[FFmpeg / ffprobe]
    FFmpeg --> S3
```

```mermaid
flowchart TB
    UI[Frontend: paginas y componentes]
    Client[lib/api.ts y AuthContext]
    Routers[Backend: routers FastAPI]
    Services[Services: reglas de negocio]
    Repos[Repositories: consultas SQLAlchemy]
    Models[Models: tablas relacionales]
    Storage[StorageService: S3/MinIO]

    UI --> Client
    Client --> Routers
    Routers --> Services
    Services --> Repos
    Repos --> Models
    Services --> Storage
```

## Flujo de ejecucion

1. El usuario abre `http://localhost:3000`.
2. Next.js renderiza la UI y envia requests a rutas relativas `/api/v1/...`.
3. `frontend/next.config.ts` reenvia esas requests al backend interno (`INTERNAL_BACKEND_URL`).
4. FastAPI valida payloads con schemas Pydantic, resuelve autenticacion JWT y ejecuta servicios.
5. Los servicios consultan PostgreSQL mediante repositories y guardan/leen archivos desde MinIO.
6. Para videos cargados por admin, el backend usa FFmpeg para crear variantes `FHD`, `QHD` y `4K` hasta la calidad maxima del archivo fuente.
7. El playback devuelve una `stream_url` temporal y el video se sirve desde el backend con soporte de header `Range`.

## Documentacion por modulo

| Documento                      | Contenido                                       |
|--------------------------------|-------------------------------------------------|
| [Backend](backend/README.md)   | API, modelos, servicios, endpoints y variables. |
| [Frontend](frontend/README.md) | UI, rutas, cliente API, auth y playback.        |
| [Docker](DOCKER.md)            | Compose, servicios, volumenes, debug y reset.   |

## Instalacion rapida con Docker

Crear un archivo `.env` en la raiz. Puede partir de `.env.example`; este ejemplo es suficiente para desarrollo local:

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

Levantar el stack:

```powershell
docker compose up -d --build
```

Tambien se puede usar el menu de Windows:

```powershell
.\manager.bat
```

## URLs principales

| Servicio      | URL                            |
|---------------|--------------------------------|
| Frontend      | `http://localhost:3000`        |
| Backend       | `http://localhost:8000`        |
| Swagger       | `http://localhost:8000/docs`   |
| Healthcheck   | `http://localhost:8000/health` |
| MinIO API     | `http://localhost:9000`        |
| MinIO Console | `http://localhost:9001`        |

## Cuenta admin

El backend crea o actualiza automaticamente una cuenta admin al iniciar.

| Campo      | Valor por defecto |
|------------|-------------------|
| Usuario    | `titoflix-admin`  |
| Contrasena | `admin1234`       |

Endpoint usado:

```http
POST /api/v1/auth/admin-login
```

Payload valido:

```json
{
  "username": "titoflix-admin",
  "password": "admin1234"
}
```

La consola admin permite administrar generos, peliculas, series, temporadas, episodios, portadas, videos y pruebas de playback.

## Endpoints principales

Todos los endpoints de API usan el prefijo `/api/v1`, excepto `/health`.

| Dominio   | Endpoints                                                                                                                    |
|-----------|------------------------------------------------------------------------------------------------------------------------------|
| Auth      | `POST /auth/login`, `POST /auth/admin-login`, `GET /auth/me`, `POST /auth/perfiles/{perfil_id}`                              |
| Cuentas   | `POST /cuentas`, `GET /cuentas`, `GET/PUT/DELETE /cuentas/{user_id}`                                                         |
| Perfiles  | `POST /cuentas/perfiles`, `GET/PUT/DELETE /cuentas/perfiles/{profile_id}`, `GET /cuentas/{user_id}/perfiles`                 |
| Catalogo  | `GET/POST /contenidos`, `GET /contenidos/top`, `GET/PUT/DELETE /contenidos/{contenido_id}`                                   |
| Generos   | `GET/POST /generos`, `DELETE /generos/{genero_id}`                                                                           |
| Series    | `POST /temporadas`, `GET /contenidos/{contenido_id}/temporadas`, `PUT/DELETE /temporadas/{temporada_id}`                     |
| Episodios | `POST /episodios`, `GET /temporadas/{temporada_id}/episodios`, `PUT/DELETE /episodios/{episodio_id}`                         |
| Playback  | `GET /contenidos/{id}/playback`, `GET /contenidos/{id}/stream`, `GET /episodios/{id}/playback`, `GET /episodios/{id}/stream` |
| Usuario   | `GET/POST/PUT/DELETE /perfiles/{perfil_id}/vistas`, `GET/POST/DELETE /perfiles/{perfil_id}/mi-lista`, calificaciones         |
| Assets    | `GET /assets/{asset_path}`                                                                                                   |

## Flujos clave

### Login

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant B as Backend
    participant DB as PostgreSQL

    U->>F: Ingresa email/password
    F->>B: POST /api/v1/auth/login
    B->>DB: Busca cuenta y verifica hash
    B-->>F: JWT + datos de cuenta
    F->>B: GET /api/v1/auth/me
    F-->>U: Selector de perfiles o home
```

### Carga y reproduccion

```mermaid
sequenceDiagram
    participant A as Admin
    participant F as Frontend
    participant B as Backend
    participant M as MinIO
    participant V as FFmpeg

    A->>F: Sube pelicula o episodio
    F->>B: multipart/form-data
    B->>V: ffprobe + ffmpeg
    V-->>B: Metadata, variantes y thumbnail
    B->>M: Guarda variantes/assets
    B-->>F: Recurso creado
    F->>B: GET /playback?quality=...
    B-->>F: stream_url temporal
    F->>B: GET /stream con Range
    B->>M: Lee objeto S3
    B-->>F: Video parcial o completo
```

## Comandos relevantes

| Comando                           | Uso                                                               |
|-----------------------------------|-------------------------------------------------------------------|
| `docker compose up -d --build`    | Construye y levanta todo el stack.                                |
| `docker compose ps`               | Verifica estado de contenedores.                                  |
| `docker compose logs -f backend`  | Sigue logs del backend.                                           |
| `docker compose logs -f frontend` | Sigue logs del frontend.                                          |
| `docker compose down`             | Detiene servicios sin borrar volumenes.                           |
| `docker compose down -v`          | Detiene servicios y borra datos locales.                          |
| `.\manager.bat`                   | Menu Windows para iniciar, reconstruir, resetear y exponer tunel. |

## Mantenimiento y extension

| Cambio deseado            | Lugar principal                                                          |
|---------------------------|--------------------------------------------------------------------------|
| Nueva pantalla            | `frontend/app` y `frontend/components`                                   |
| Nuevo endpoint            | Router, service, repository, schema y DTO en `backend/src`               |
| Nueva entidad             | Modelo SQLAlchemy, repository, service, mapper y schema/DTO              |
| Nueva regla de catalogo   | `ContenidoService`, `EpisodioService`, `VistaService` o `MiListaService` |
| Cambios de storage        | `StorageService`                                                         |
| Cambios de calidad/video  | `QUALITY_HEIGHTS`, `QUALITY_PRIORITY` y `VideoProcessingService`         |
| Cambios de despliegue     | `docker-compose.yml`, `DOCKER.md`, `.env.example` y variables de entorno |

Reglas de arquitectura observadas:

- Los routers no acceden directamente a la base de datos salvo para recibir la sesion por dependency injection.
- Los services concentran validaciones de negocio.
- Los repositories encapsulan consultas y mutaciones SQLAlchemy.
- Los DTOs/schemas separan transporte HTTP, respuesta y dominio interno.
- Los assets y videos se guardan en MinIO; la base de datos guarda referencias y metadata.
