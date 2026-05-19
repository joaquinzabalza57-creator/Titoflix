# Backend Titoflix

Backend REST de Titoflix construido con FastAPI, SQLAlchemy y Pydantic. Expone la API usada por el frontend, administra autenticacion JWT, cuentas, perfiles, catalogo, progreso de reproduccion, calificaciones, carga de media, procesamiento de video con FFmpeg y streaming desde MinIO/S3.

## Responsabilidades

| Responsabilidad | Detalle                                                                      |
|-----------------|------------------------------------------------------------------------------|
| API REST        | Expone endpoints bajo `/api/v1` y documentacion Swagger en `/docs`.          |
| Validacion      | Valida entradas HTTP con schemas Pydantic.                                   |
| Negocio         | Ejecuta reglas en servicios, separadas de routers y repositories.            |
| Persistencia    | Usa PostgreSQL mediante SQLAlchemy.                                          |
| Storage         | Guarda videos, portadas, miniaturas y avatares en MinIO/S3.                  |
| Video           | Usa FFmpeg/ffprobe para duracion, thumbnails y variantes `FHD`, `QHD`, `4K`. |
| Seguridad       | Firma JWT de cuenta y tokens temporales de media.                            |
| Bootstrap       | Crea tablas, aplica migraciones livianas y asegura cuenta admin por defecto. |

## Dependencias

| Dependencia                     | Uso                                        |
|---------------------------------|--------------------------------------------|
| `fastapi`                       | API HTTP y dependency injection.           |
| `uvicorn[standard]`             | Servidor ASGI.                             |
| `sqlalchemy`                    | ORM y sesiones de base de datos.           |
| `pydantic`, `pydantic-settings` | Schemas, DTOs y configuracion por entorno. |
| `python-jose[cryptography]`     | Creacion y validacion de JWT.              |
| `passlib[bcrypt]`, `bcrypt`     | Hash y verificacion de passwords/PIN.      |
| `psycopg2-binary`               | Driver PostgreSQL.                         |
| `python-multipart`              | Uploads `multipart/form-data`.             |
| `boto3`                         | Cliente S3/MinIO.                          |
| `ffmpeg`, `ffprobe`             | Procesamiento de videos en Docker/local.   |

## Estructura

```text
backend/
|-- Dockerfile
|-- README.md
|-- requirements.txt
`-- src/
    |-- app.py                  # FastAPI, CORS, routers, startup
    |-- main.py                 # Entry point local con uvicorn
    |-- config/
    |   `-- env.py              # Settings por variables de entorno
    |-- db/
    |   |-- connection.py       # Engine, SessionLocal, create_tables/reset
    |   `-- models/             # Modelos SQLAlchemy
    |-- routers/                # Endpoints HTTP
    |-- services/               # Reglas de negocio
    |-- repositories/           # Consultas y mutaciones SQLAlchemy
    |-- schemas/                # Validacion HTTP
    |-- dtos/                   # Transporte entre capas y respuestas
    |-- mappers/                # Conversion ORM -> DTO
    |-- middlewares/            # Auth y manejo de errores
    `-- utils/                  # JWT, hash y errores de dominio
```

## Arquitectura por capas

```mermaid
flowchart TB
    Request[Request HTTP]
    Router[routers/*_router.py]
    Schema[schemas/*.py]
    Service[services/*.py]
    Repository[repositories/*.py]
    Model[db/models/*.py]
    DB[(PostgreSQL)]
    Storage[StorageService]
    S3[(MinIO/S3)]
    FFmpeg[VideoProcessingService + FFmpeg]

    Request --> Router
    Router --> Schema
    Router --> Service
    Service --> Repository
    Repository --> Model
    Model --> DB
    Service --> Storage
    Storage --> S3
    Service --> FFmpeg
    FFmpeg --> Storage
```

| Capa         | Responsabilidad                                                             |
|--------------|-----------------------------------------------------------------------------|
| Routers      | Definen rutas, dependencies, auth requerida, forms/files y response models. |
| Schemas      | Validan payloads HTTP de entrada.                                           |
| DTOs         | Transportan datos entre capas y respuestas tipadas.                         |
| Services     | Reglas de negocio, validaciones y coordinacion con storage/video.           |
| Repositories | Acceso a datos y operaciones SQLAlchemy.                                    |
| Models       | Tablas, relaciones, constraints y metadata relacional.                      |
| Mappers      | Conversion de modelos ORM a DTOs.                                           |

## Startup y base de datos

En `src/app.py`, el evento `startup` ejecuta `create_tables()` con reintentos para esperar a PostgreSQL cuando Docker aun esta levantando servicios. `create_tables()`:

1. Crea tablas con `Base.metadata.create_all`.
2. Agrega columnas nuevas si una base local ya existia.
3. Ajusta tipos de duracion a `DOUBLE PRECISION`.
4. Normaliza valores de calidades de video.
5. Crea o actualiza la cuenta admin fija con ID `1`.

Estas funciones son migraciones livianas para desarrollo. En produccion real convendria reemplazarlas por Alembic.

## Variables de entorno

| Variable                      | Default en codigo                                        | Uso                                          |
|-------------------------------|----------------------------------------------------------|----------------------------------------------|
| `APP_NAME`                    | `Titoflix API`                                           | Nombre logico de la app.                     |
| `ENVIRONMENT`                 | `development`                                            | CORS amplio y reload local.                  |
| `DATABASE_URL`                | `postgresql://postgres:postgres@localhost:5432/titoflix` | Conexion SQLAlchemy.                         |
| `HOST`                        | `127.0.0.1`                                              | Host para `src/main.py`.                     |
| `PORT`                        | `8000`                                                   | Puerto para `src/main.py`.                   |
| `HOST_IP`                     | `127.0.0.1`                                              | Origen CORS adicional para LAN.              |
| `JWT_SECRET`                  | `cambiame-en-produccion`                                 | Firma de tokens JWT.                         |
| `JWT_ALGORITHM`               | `HS256`                                                  | Algoritmo JWT.                               |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                                                     | Expiracion de tokens de cuenta.              |
| `S3_ENDPOINT_URL`             | `http://localhost:9000`                                  | Endpoint interno S3.                         |
| `S3_PUBLIC_ENDPOINT_URL`      | `http://localhost:9000`                                  | Endpoint publico configurado.                |
| `S3_ACCESS_KEY`               | `titoflix`                                               | Access key S3.                               |
| `S3_SECRET_KEY`               | `titoflix-secret`                                        | Secret key S3.                               |
| `S3_BUCKET_NAME`              | `titoflix-media`                                         | Bucket de media.                             |
| `S3_REGION`                   | `us-east-1`                                              | Region S3.                                   |
| `S3_MEDIA_PREFIX`             | `media`                                                  | Prefijo para videos.                         |
| `S3_ASSETS_PREFIX`            | `assets`                                                 | Prefijo para portadas, thumbnails y avatars. |
| `CORS_ORIGINS`                | `http://localhost:3000,http://127.0.0.1:3000`            | Origenes permitidos.                         |
| `ADMIN_USERNAME`              | `titoflix-admin`                                         | Cuenta admin por defecto.                    |
| `ADMIN_PASSWORD`              | `admin1234`                                              | Password admin por defecto.                  |

## Modelos principales

```mermaid
erDiagram
    Cuenta ||--o{ Perfil : tiene
    Perfil ||--o{ Vista : registra
    Perfil ||--o{ Calificacion : califica
    Perfil }o--o{ Contenido : mi_lista
    Contenido }o--o{ Genero : contenido_generos
    Contenido ||--o{ Temporada : contiene
    Temporada ||--o{ Episodio : contiene
    Contenido ||--o{ VideoVariant : variantes
    Episodio ||--o{ VideoVariant : variantes
    Contenido ||--o{ Vista : progreso_pelicula
    Episodio ||--o{ Vista : progreso_episodio
    Contenido ||--o{ Calificacion : recibe
```

| Modelo         | Tabla               | Campos destacados                                                           |
|----------------|---------------------|-----------------------------------------------------------------------------|
| `Cuenta`       | `cuentas`           | `email`, `password_hash`, `plan`, `is_admin`, `fecha_alta`                  |
| `Perfil`       | `perfiles`          | `cuenta_id`, `nombre`, `pin`, `es_infantil`, `avatar`                       |
| `Genero`       | `generos`           | `nombre`                                                                    |
| `Contenido`    | `contenidos`        | `titulo`, `tipo`, `anio`, `duracion_min`, `portada_url`, metadata de video  |
| `Temporada`    | `temporadas`        | `contenido_id`, `numero`, `anio`, `storage_folder_id`                       |
| `Episodio`     | `episodios`         | `temporada_id`, `numero`, `titulo`, `thumbnail_url`, metadata de video      |
| `VideoVariant` | `video_variants`    | `quality`, `video_storage_key`, `video_mime`, `video_size`                  |
| `Vista`        | `vistas`            | `perfil_id`, `contenido_id` o `episodio_id`, `segundos_vistos`, `terminado` |
| `Calificacion` | `calificaciones`    | `perfil_id`, `contenido_id`, `puntaje`                                      |

## Servicios principales

| Servicio                 | Responsabilidad                                                                |
|--------------------------|--------------------------------------------------------------------------------|
| `AuthService`            | Login, admin login, cuenta actual y autorizacion de perfil con PIN.            |
| `CuentaService`          | CRUD de cuentas, hashing de password, validacion de plan y limpieza de assets. |
| `PerfilService`          | CRUD de perfiles, limite por plan, PIN, avatar base64 y limpieza de assets.    |
| `GeneroService`          | CRUD basico de generos.                                                        |
| `ContenidoService`       | Crear/buscar/actualizar/eliminar contenido, portadas, variantes y playback.    |
| `TemporadaService`       | Crear/listar/actualizar/eliminar temporadas.                                   |
| `EpisodioService`        | Crear/listar/actualizar/eliminar episodios, thumbnails y playback.             |
| `VistaService`           | Upsert de progreso, validacion infantil y calculo de "continuar viendo".       |
| `MiListaService`         | Agregar, quitar y listar contenidos por perfil.                                |
| `CalificacionService`    | Upsert y eliminacion de calificaciones.                                        |
| `StorageService`         | Upload, stream con `Range`, delete object/prefix y creacion de bucket S3.      |
| `VideoProcessingService` | ffprobe, transcodificacion, thumbnails y seleccion de calidades.               |

| Constante                 | Archivo                                 | Uso                                             |
|---------------------------|-----------------------------------------|-------------------------------------------------|
| `API_PREFIX`              | `src/app.py`                            | Prefijo `/api/v1`.                              |
| `PLAN_LIMITS`             | `services/user_service.py`              | `basico=1`, `estandar=2`, `premium=5` perfiles. |
| `QUALITY_HEIGHTS`         | `services/video_processing_service.py`  | `FHD=1080`, `QHD=1440`, `4K=2160`.              |
| `QUALITY_PRIORITY`        | `services/video_processing_service.py`  | Orden de seleccion de calidad.                  |
| `MEDIA_TOKEN_TTL_MINUTES` | `routers/product_router.py`             | 10 minutos para tokens de stream.               |

## Endpoints

Todos usan `/api/v1` como prefijo.

### Auth

| Metodo | Ruta                         | Auth   | Descripcion                                   |
|--------|------------------------------|--------|-----------------------------------------------|
| `POST` | `/auth/login`                | No     | Login por email/password.                     |
| `POST` | `/auth/admin-login`          | No     | Login admin por username/password o password. |
| `GET`  | `/auth/me`                   | Cuenta | Devuelve cuenta autenticada.                  |
| `POST` | `/auth/perfiles/{perfil_id}` | Cuenta | Autoriza perfil y valida PIN si existe.       |

### Cuentas y perfiles

| Metodo   | Ruta                                  | Auth                | Descripcion                                             |
|----------|---------------------------------------|---------------------|---------------------------------------------------------|
| `POST`   | `/cuentas`                            | Opcional            | Crea cuenta; crear admin requiere admin.                |
| `GET`    | `/cuentas`                            | Admin               | Lista cuentas.                                          |
| `GET`    | `/cuentas/{user_id}`                  | Cuenta propia/Admin | Obtiene cuenta.                                         |
| `PUT`    | `/cuentas/{user_id}`                  | Cuenta propia/Admin | Actualiza email, password, plan o admin si corresponde. |
| `DELETE` | `/cuentas/{user_id}`                  | Cuenta propia/Admin | Elimina cuenta y assets asociados.                      |
| `POST`   | `/cuentas/perfiles`                   | Cuenta              | Crea perfil.                                            |
| `GET`    | `/cuentas/{user_id}/perfiles`         | Cuenta propia/Admin | Lista perfiles de cuenta.                               |
| `GET`    | `/cuentas/perfiles/{profile_id}`      | Cuenta propia/Admin | Obtiene perfil.                                         |
| `PUT`    | `/cuentas/perfiles/{profile_id}`      | Cuenta propia/Admin | Actualiza perfil, PIN o avatar.                         |
| `DELETE` | `/cuentas/perfiles/{profile_id}`      | Cuenta propia/Admin | Elimina perfil y assets.                                |

### Catalogo y media

| Metodo   | Ruta                                  | Auth        | Descripcion                                                                      |
|----------|---------------------------------------|-------------|----------------------------------------------------------------------------------|
| `GET`    | `/generos`                            | No          | Lista generos.                                                                   |
| `POST`   | `/generos?nombre=...`                 | Admin       | Crea genero.                                                                     |
| `DELETE` | `/generos/{genero_id}`                | Admin       | Elimina genero.                                                                  |
| `GET`    | `/contenidos`                         | No          | Busca contenidos por `q`, `tipo`, `genero_id`, `genero`, `perfil_id`, `ordenar`. |
| `POST`   | `/contenidos`                         | Admin       | Crea pelicula o serie con form-data, portada y video segun tipo.                 |
| `GET`    | `/contenidos/top`                     | No          | Lista top, opcionalmente por genero.                                             |
| `GET`    | `/contenidos/{contenido_id}`          | No          | Detalle de contenido.                                                            |
| `PUT`    | `/contenidos/{contenido_id}`          | Admin       | Actualiza contenido, portada y video.                                            |
| `DELETE` | `/contenidos/{contenido_id}`          | Admin       | Elimina contenido y media asociada.                                              |
| `GET`    | `/contenidos/{contenido_id}/playback` | Cuenta      | Devuelve `stream_url` y `mime_type`.                                             |
| `GET`    | `/contenidos/{contenido_id}/stream`   | Token media | Stream con soporte `Range`.                                                      |
| `GET`    | `/contenidos/{contenido_id}/download` | Cuenta      | Descarga archivo de video.                                                       |
| `GET`    | `/assets/{asset_path}`                | No          | Sirve assets desde MinIO.                                                        |

### Series, progreso y engagement

| Metodo     | Ruta                                             | Auth                | Descripcion                              |
|------------|--------------------------------------------------|---------------------|------------------------------------------|
| `POST`     | `/temporadas`                                    | Admin               | Crea temporada.                          |
| `GET`      | `/contenidos/{contenido_id}/temporadas`          | No                  | Lista temporadas.                        |
| `PUT`      | `/temporadas/{temporada_id}`                     | Admin               | Actualiza temporada.                     |
| `DELETE`   | `/temporadas/{temporada_id}`                     | Admin               | Elimina temporada.                       |
| `POST`     | `/episodios`                                     | Admin               | Crea episodio con video.                 |
| `GET`      | `/temporadas/{temporada_id}/episodios`           | No                  | Lista episodios.                         |
| `PUT`      | `/episodios/{episodio_id}`                       | Admin               | Actualiza episodio y video.              |
| `DELETE`   | `/episodios/{episodio_id}`                       | Admin               | Elimina episodio.                        |
| `GET`      | `/episodios/{episodio_id}/playback`              | Cuenta              | Devuelve stream de episodio.             |
| `GET`      | `/episodios/{episodio_id}/stream`                | Token media         | Stream de episodio.                      |
| `GET`      | `/episodios/{episodio_id}/download`              | Cuenta              | Descarga episodio.                       |
| `POST/PUT` | `/perfiles/{perfil_id}/vistas`                   | Perfil propio/Admin | Crea o actualiza progreso.               |
| `DELETE`   | `/perfiles/{perfil_id}/vistas`                   | Perfil propio/Admin | Elimina progreso por contenido/episodio. |
| `GET`      | `/perfiles/{perfil_id}/continuar`                | Perfil propio/Admin | Lista continuar viendo.                  |
| `POST/GET` | `/perfiles/{perfil_id}/mi-lista`                 | Perfil propio/Admin | Agrega/lista Mi lista.                   |
| `DELETE`   | `/perfiles/{perfil_id}/mi-lista/{contenido_id}`  | Perfil propio/Admin | Quita de Mi lista.                       |
| `POST/PUT` | `/perfiles/{perfil_id}/calificaciones/{id}`      | Perfil propio/Admin | Upsert de calificacion por contenido.    |
| `DELETE`   | `/perfiles/{perfil_id}/calificaciones/{id}`      | Perfil propio/Admin | Elimina calificacion.                    |

## Procesamiento de video

```mermaid
flowchart TB
    Upload[UploadFile recibido]
    Temp[Archivo temporal]
    Probe[ffprobe: altura y duracion]
    Quality[Detecta calidad fuente]
    Transcode[ffmpeg genera variantes permitidas]
    Thumb[ffmpeg extrae thumbnail]
    S3[StorageService sube a MinIO]
    DB[Service registra metadata y variants]

    Upload --> Temp --> Probe --> Quality --> Transcode --> S3 --> DB
    Quality --> Thumb --> S3
```

| Regla       | Detalle                                                                            |
|-------------|------------------------------------------------------------------------------------|
| Sin upscale | Si el video fuente no alcanza una calidad superior, no se crea una variante mayor. |
| Calidades   | Las calidades disponibles son `FHD`, `QHD` y `4K`.                                 |
| Peliculas   | Guardan variantes asociadas a `Contenido`.                                         |
| Episodios   | Guardan variantes asociadas a `Episodio` y thumbnail generado.                     |
| Playback    | `/playback` genera token temporal; `/stream` valida token y responde con `Range`.  |

## Instalacion local sin Docker

Requisitos: Python 3.12, PostgreSQL, MinIO compatible S3 y FFmpeg disponible en `PATH`.

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.app:app --reload
```

En Windows PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn src.app:app --reload
```

Swagger queda disponible en `http://localhost:8000/docs`.

## Ejemplos basicos

Login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@example.com","password":"password123"}'
```

Crear cuenta:

```bash
curl -X POST http://localhost:8000/api/v1/cuentas \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@example.com","password":"password123","plan":"estandar"}'
```

Buscar contenidos:

```bash
curl "http://localhost:8000/api/v1/contenidos?tipo=pelicula&ordenar=anio_desc"
```

Healthcheck:

```bash
curl http://localhost:8000/health
```

## Mantenimiento

| Tarea                   | Comando o archivo                                                                             |
|-------------------------|-----------------------------------------------------------------------------------------------|
| Ver logs backend        | `docker compose logs -f backend`                                                              |
| Resetear tablas         | `docker compose exec backend python -c "from src.db import reset_database; reset_database()"` |
| Cambiar limites de plan | `backend/src/services/user_service.py`                                                        |
| Cambiar calidades       | `backend/src/services/video_processing_service.py` y constraint de `VideoVariant`             |
| Cambiar storage         | `backend/src/services/storage_service.py`                                                     |
| Agregar dominio nuevo   | Crear `model`, `schema`, `dto`, `mapper`, `repository`, `service` y `router`                  |
