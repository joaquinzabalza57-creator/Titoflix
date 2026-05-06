from src.app import app

print("Rutas registradas en la app:")
for route in app.routes:
    path = getattr(route, 'path', 'N/A')
    methods = getattr(route, 'methods', 'N/A')
    print(f"  {path} - {methods}")
