# Library Client (Flask)

Aplicación Flask **cliente** que consume la API REST vía HTTP (biblioteca). Renderiza vistas Jinja2 con datos del backend.

## Configuración
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# en .env ajusta API_BASE_URL (por defecto http://127.0.0.1:8001)
```

## Ejecutar
```bash
python app.py
# o producción:
gunicorn -w 2 -b 0.0.0.0:8000 'app:create_app()'
```

## Operaciones
- Listar libros (`GET /books` de la API)
- Crear (`POST /books`)
- Editar (`PUT /books/<id>`)
- Eliminar (`DELETE /books/<id>`)

## Manejo de errores
- Timeouts y fallos de red → `flash()` con mensajes de error.
- Errores HTTP de la API se muestran al usuario.
