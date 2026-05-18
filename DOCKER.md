# Titoflix con Docker

Este proyecto corre con cuatro servicios separados:

- `frontend`: aplicacion Next.js en `http://localhost:3000`
- `backend`: API FastAPI en `http://localhost:8000`
- `postgres`: base de datos PostgreSQL en `localhost:5432`
- `minio`: storage compatible con S3 para videos, miniaturas, avatars y assets

La imagen del backend instala FFmpeg para detectar la resolucion de cada video subido y generar las variantes de calidad.

## Requisitos

- Docker Desktop
- Docker Compose v2

## Uso rapido

En Windows ejecuta:

```bat
manager.bat
```

Opciones principales:

- `Iniciar servicios`: levanta todos los contenedores en segundo plano.
- `Ver consola del frontend/backend/postgres/MinIO`: abre logs en vivo del servicio elegido.
- `Detener servicios`: apaga los contenedores sin borrar volumenes.
- `Reconstruir e iniciar`: reconstruye imagenes y vuelve a levantar el stack.
- `Resetear tablas de Postgres y buckets de MinIO`: elimina y vuelve a crear las tablas desde el backend, y vacia/recrea el bucket de medios.

Tambien podes usar Docker Compose directamente:

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f backend
docker compose down
```

Para resetear solo las tablas de Postgres desde Docker:

```bash
docker compose exec backend python -c "from src.db import reset_database; reset_database()"
```

Ese comando no borra los archivos guardados en MinIO.

La opcion `Resetear tablas de Postgres y buckets de MinIO` de `manager.bat` tambien ejecuta el cliente `mc` para borrar y recrear el bucket `titoflix-media`.

## URLs

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Healthcheck backend: `http://localhost:8000/health`
- MinIO API S3: `http://localhost:9000`
- MinIO Console: `http://localhost:9001`

El frontend llama a `/api/v1/...` desde el navegador. Next.js reenvia esas requests al backend interno `http://backend:8000`, asi que la app tambien puede abrirse desde una computadora externa usando el host publico del frontend, por ejemplo `http://TU-DOMINIO:3000`.

Para acceso fuera de la LAN, publica el puerto `3000` del equipo que corre Docker con port forwarding, un dominio/reverse proxy, una VPS, o un tunel como Cloudflare Tunnel/ngrok. No hace falta exponer `8000` para el uso normal del frontend.

Credenciales de MinIO:

- Usuario: `titoflix`
- Password: `titoflix-secret`
- Bucket: `titoflix-media`

## Variables importantes

El `docker-compose.yml` ya define las variables necesarias para desarrollo local:

```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/titoflix
S3_ENDPOINT_URL=http://minio:9000
S3_PUBLIC_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=titoflix
S3_SECRET_KEY=titoflix-secret
S3_BUCKET_NAME=titoflix-media
S3_REGION=us-east-1
S3_MEDIA_PREFIX=media
INTERNAL_BACKEND_URL=http://backend:8000
NEXT_PUBLIC_API_URL=/api/v1
NEXT_PUBLIC_DIRECT_API_URL=/api/v1
NEXT_PUBLIC_BACKEND_URL=
```

El backend crea las tablas al arrancar. PostgreSQL guarda datos en el volumen `postgres_data` y MinIO guarda archivos en `minio_data`.

## Storage S3/MinIO

Se elimino la integracion con Google Drive. Los videos se suben a MinIO usando la API S3 y se guardan en el bucket `titoflix-media`, bajo el prefijo `media`.

Cada pelicula y cada episodio tienen su propia carpeta en MinIO. Al subir un archivo, el backend lo toma como la calidad maxima disponible, detecta su resolucion y duracion con `ffprobe`, y genera con `ffmpeg` las variantes `FHD`, `QHD` y `4K` sin pedir la calidad ni la duracion en la pantalla de administracion. Si el archivo fuente no llega a una resolucion alta, esa variante se conserva en la maxima resolucion disponible en vez de hacer upscale.

Los endpoints de playback siguen devolviendo `stream_url` y `mime_type`. La transmision del video pasa por el backend, que lee desde MinIO y respeta requests con header `Range` para reproduccion parcial.

## Borrar datos locales

Para apagar todo y borrar la base de datos y los archivos de MinIO:

```bash
docker compose down -v
```

Usalo con cuidado: elimina los volumenes `postgres_data` y `minio_data`.
