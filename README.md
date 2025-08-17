# Biblioteca — Arquitectura desacoplada (API + Cliente)

Este repositorio contiene **dos proyectos** separados:
- `library-api/` → API RESTful (proveedor de datos)
- `library-client/` → Cliente Flask (consume la API con `requests` y renderiza Jinja2)

## Puesta en marcha rápida (local)
1) **API**
```bash
cd library-api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app app.py init-db
python app.py  # o gunicorn -w 2 -b 0.0.0.0:8001 'app:create_app()'
```
2) **Cliente**
```bash
cd ../library-client
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # verifica API_BASE_URL apunta a la API
python app.py  # o gunicorn -w 2 -b 0.0.0.0:8000 'app:create_app()'
```
- Cliente en `http://127.0.0.1:8000` (si usas Gunicorn) o `:5000` (python app.py).
- API en `http://127.0.0.1:8001`.

## Producción (esquema)
- **Nginx** delante con dos `upstream`:
  - `/api/` → Gunicorn (library-api).
  - `/` → Gunicorn (library-client).
- Variables en `.env` para credenciales/URLs.
