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

El frontend usa `/api/v1` desde el navegador y Next.js lo reenvia al backend dentro de Docker. Eso permite abrir la app desde otra computadora usando el host publico, por ejemplo `http://TU-DOMINIO:3000`, sin que el navegador intente llamar a su propio `localhost`.

Para usarla fuera de la LAN tenes que publicar el puerto `3000` del equipo que corre Docker mediante port forwarding, un dominio/reverse proxy, una VPS, o un tunel como Cloudflare Tunnel/ngrok. No hace falta exponer el puerto `8000` si se usa el frontend, porque las llamadas pasan por `/api/v1`.

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

Para peliculas y episodios, se sube un unico archivo en la maxima calidad disponible. El backend usa FFmpeg para detectar la duracion, generar las variantes de calidad y guardarlas juntas en la carpeta propia de esa pelicula o episodio dentro de MinIO.

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
