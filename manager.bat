@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

:menu
cls
echo Titoflix Docker Manager
echo =======================
echo.
echo 1. Iniciar servicios
echo 2. Ver estado
echo 3. Ver consola del frontend
echo 4. Ver consola del backend
echo 5. Ver consola de postgres
echo 6. Ver consola de MinIO
echo 7. Detener servicios
echo 8. Reconstruir e iniciar
echo 9. Resetear tablas de Postgres y buckets de MinIO
echo 10. Iniciar tunel publico
echo 11. Ver URL del tunel publico
echo 12. Detener tunel publico
echo 0. Salir
echo.
set /p option=Elegi una opcion: 

if "%option%"=="1" goto start
if "%option%"=="2" goto status
if "%option%"=="3" goto logs_frontend
if "%option%"=="4" goto logs_backend
if "%option%"=="5" goto logs_postgres
if "%option%"=="6" goto logs_minio
if "%option%"=="7" goto stop
if "%option%"=="8" goto rebuild
if "%option%"=="9" goto reset_db
if "%option%"=="10" goto start_tunnel
if "%option%"=="11" goto tunnel_logs
if "%option%"=="12" goto stop_tunnel
if "%option%"=="0" goto end
goto menu

:start
call :write_host_ip
docker compose up -d
pause
goto menu

:status
docker compose ps
pause
goto menu

:logs_frontend
docker compose logs -f frontend
goto menu

:logs_backend
docker compose logs -f backend
goto menu

:logs_postgres
docker compose logs -f postgres
goto menu

:logs_minio
docker compose logs -f minio
goto menu

:stop
docker compose down
pause
goto menu

:rebuild
call :write_host_ip
docker compose down --remove-orphans
docker compose build --no-cache frontend backend
if errorlevel 1 (
    echo.
    echo La reconstruccion fallo. No se iniciaron los contenedores para evitar usar una imagen anterior.
    pause
    goto menu
)
docker compose up -d --force-recreate
pause
goto menu

:reset_db
echo.
echo Esto elimina y vuelve a crear todas las tablas de Postgres.
echo Tambien elimina y recrea el bucket titoflix-media de MinIO.
set /p confirm=Escribi RESET para confirmar: 
if not "%confirm%"=="RESET" goto menu
docker compose exec backend python -c "from src.db import reset_database; reset_database()"
docker compose run --rm --entrypoint /bin/sh minio-init -c "until mc alias set local http://minio:9000 titoflix titoflix-secret; do sleep 2; done && mc rb --force local/titoflix-media || true && mc mb --ignore-existing local/titoflix-media"
pause
goto menu

:start_tunnel
docker rm -f titoflix-cloudflared-tunnel >nul 2>nul
docker run -d --name titoflix-cloudflared-tunnel cloudflare/cloudflared:latest tunnel --url http://host.docker.internal:3000
echo.
echo Espera unos segundos. La URL aparece abajo como https://...trycloudflare.com
timeout /t 6 /nobreak >nul
docker logs titoflix-cloudflared-tunnel
pause
goto menu

:tunnel_logs
docker logs titoflix-cloudflared-tunnel
pause
goto menu

:stop_tunnel
docker rm -f titoflix-cloudflared-tunnel
pause
goto menu

:write_host_ip
set "HOST_IP=127.0.0.1"
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch '^(127\.0\.0\.1|169\.254\.)' -and $_.InterfaceOperationalStatus -eq 'Up' } | Select-Object -ExpandProperty IPAddress -First 1"`) do set "HOST_IP=%%I"
powershell -NoProfile -Command "if (Test-Path '.env') { $c=Get-Content '.env'; if ($c -match '^HOST_IP=') { $c = $c -replace '^HOST_IP=.*','HOST_IP=%HOST_IP%'; $c | Set-Content '.env' } else { Add-Content '.env' 'HOST_IP=%HOST_IP%' } } else { Set-Content '.env' 'HOST_IP=%HOST_IP%' }"
goto :eof

:end
endlocal
