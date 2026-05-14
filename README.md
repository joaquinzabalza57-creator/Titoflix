# Titoflix

Aplicacion de streaming con frontend Next.js, backend FastAPI, PostgreSQL y MinIO/S3 para archivos de video y assets.

## Correr con Docker

Desde la raiz del proyecto:

```powershell
docker compose up -d --build
```

URLs principales:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- MinIO Console: `http://localhost:9001`

El frontend llama al backend mediante `/api/v1` en el mismo host del frontend. Next.js reenvia esas requests al contenedor `backend`, evitando problemas de CORS o URLs absolutas viejas en el navegador.

Tambien podes usar:

```powershell
.\manager.bat
```

## Cuenta admin

El backend crea/actualiza automaticamente una cuenta admin fija al arrancar:

- Usuario: `titoflix-admin`
- Contrasena: `admin1234`

El frontend tiene un acceso separado en la esquina inferior izquierda de la pantalla de login. Ese formulario solo pide la contrasena; el usuario `titoflix-admin` se envia hardcodeado desde el frontend y la contrasena no se muestra por defecto.

Al iniciar como admin se abre una consola distinta al home de usuarios. Esa consola permite crear y probar:

- Generos
- Contenidos de tipo `pelicula` o `serie`
- Temporadas
- Episodios con video
- Playback de peliculas cargadas

Ese acceso usa:

```http
POST /api/v1/auth/admin-login
```

Payload:

```json
{
  "username": "titoflix-admin",
  "password": "admin1234"
}
```

Esta cuenta queda marcada como `is_admin = true` y puede usar endpoints protegidos por permisos de admin.
