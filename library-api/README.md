# Library API (REST)

API RESTful para gestionar libros. Responde en **JSON** y usa códigos HTTP correctos.

## Endpoints
- `GET /books` — lista de libros
- `GET /books/<id>` — libro por id
- `POST /books` — crear (JSON: title, author, year?, genre?)
- `PUT /books/<id>` — actualizar campos
- `DELETE /books/<id>` — eliminar

## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
flask --app app.py init-db
python app.py  # o: gunicorn -w 2 -b 0.0.0.0:8001 'app:create_app()'
```
