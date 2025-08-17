import os
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from requests.exceptions import RequestException, Timeout
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")
    app.config["API_BASE_URL"] = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")
    app.config["REQUEST_TIMEOUT"] = float(os.getenv("REQUEST_TIMEOUT", "8"))

    def api_url(path: str) -> str:
        base = app.config["API_BASE_URL"].rstrip("/")
        return f"{base}{path}"

    def api_get(path: str):
        try:
            r = requests.get(api_url(path), timeout=app.config["REQUEST_TIMEOUT"])
            r.raise_for_status()
            return r.json(), None
        except Timeout:
            return None, "Tiempo de espera agotado al consultar la API."
        except RequestException as e:
            try:
                err = r.json().get("message") if r is not None else str(e)
            except Exception:
                err = str(e)
            return None, f"Error de red/API: {err}"

    def api_send(method: str, path: str, json_data=None):
        try:
            r = requests.request(method, api_url(path), json=json_data, timeout=app.config["REQUEST_TIMEOUT"])
            if r.status_code >= 400:
                msg = r.json().get("message", f"HTTP {r.status_code}")
                return None, msg
            return r.json() if r.content else None, None
        except Timeout:
            return None, "Tiempo de espera agotado al enviar datos a la API."
        except RequestException as e:
            return None, f"Error de red/API: {str(e)}"

    @app.route("/")
    def home():
        return redirect(url_for("list_books"))

    @app.route("/books")
    def list_books():
        data, err = api_get("/books")
        if err:
            flash(err, "error")
            data = []
        return render_template("books/list.html", books=data)

    @app.route("/books/new", methods=["GET", "POST"])
    def create_book():
        if request.method == "POST":
            payload = {
                "title": request.form.get("title", "").strip(),
                "author": request.form.get("author", "").strip(),
                "year": request.form.get("year") or None,
                "genre": request.form.get("genre") or None,
            }
            res, err = api_send("POST", "/books", json_data=payload)
            if err:
                flash(f"No se pudo crear el libro: {err}", "error")
                return redirect(url_for("create_book"))
            flash("Libro agregado correctamente.", "success")
            return redirect(url_for("list_books"))
        return render_template("books/form.html", book=None)

    @app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
    def edit_book(book_id):
        if request.method == "POST":
            payload = {
                "title": request.form.get("title", "").strip(),
                "author": request.form.get("author", "").strip(),
                "year": request.form.get("year") or None,
                "genre": request.form.get("genre") or None,
            }
            res, err = api_send("PUT", f"/books/{book_id}", json_data=payload)
            if err:
                flash(f"No se pudo actualizar: {err}", "error")
                return redirect(url_for("edit_book", book_id=book_id))
            flash("Libro actualizado.", "success")
            return redirect(url_for("list_books"))
        # GET
        data, err = api_get(f"/books/{book_id}")
        if err:
            flash(err, "error")
            return redirect(url_for("list_books"))
        return render_template("books/form.html", book=data)

    @app.route("/books/<int:book_id>/delete", methods=["GET", "POST"])
    def delete_book(book_id):
        if request.method == "POST":
            _, err = api_send("DELETE", f"/books/{book_id}")
            if err:
                flash(f"No se pudo eliminar: {err}", "error")
                return redirect(url_for("delete_book", book_id=book_id))
            flash("Libro eliminado.", "success")
            return redirect(url_for("list_books"))
        data, err = api_get(f"/books/{book_id}")
        if err:
            flash(err, "error")
            return redirect(url_for("list_books"))
        return render_template("books/confirm_delete.html", book=data)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
