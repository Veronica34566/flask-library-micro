import os
from flask import Flask, jsonify, request, abort
from dotenv import load_dotenv
from models import db, Book

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///library.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")

    db.init_app(app)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    # ---- Endpoints REST ----
    @app.route("/books", methods=["GET"])
    def list_books():
        books = Book.query.order_by(Book.title.asc()).all()
        return jsonify([b.to_dict() for b in books]), 200

    @app.route("/books/<int:book_id>", methods=["GET"])
    def get_book(book_id):
        b = Book.query.get(book_id)
        if not b:
            return jsonify({"error": "not_found", "message": "Book not found"}), 404
        return jsonify(b.to_dict()), 200

    @app.route("/books", methods=["POST"])
    def create_book():
        if not request.is_json:
            return jsonify({"error": "bad_request", "message": "JSON body required"}), 400
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        author = (data.get("author") or "").strip()
        year = data.get("year")
        genre = (data.get("genre") or None)
        if not title or not author:
            return jsonify({"error": "validation_error", "message": "title and author are required"}), 400
        try:
            y = int(year) if year not in (None, "") else None
        except (TypeError, ValueError):
            return jsonify({"error": "validation_error", "message": "year must be integer"}), 400
        b = Book(title=title, author=author, year=y, genre=genre)
        db.session.add(b)
        db.session.commit()
        return jsonify(b.to_dict()), 201

    @app.route("/books/<int:book_id>", methods=["PUT"])
    def update_book(book_id):
        if not request.is_json:
            return jsonify({"error": "bad_request", "message": "JSON body required"}), 400
        b = Book.query.get(book_id)
        if not b:
            return jsonify({"error": "not_found", "message": "Book not found"}), 404
        data = request.get_json(silent=True) or {}
        if "title" in data:
            if not str(data["title"]).strip():
                return jsonify({"error": "validation_error", "message": "title cannot be empty"}), 400
            b.title = str(data["title"]).strip()
        if "author" in data:
            if not str(data["author"]).strip():
                return jsonify({"error": "validation_error", "message": "author cannot be empty"}), 400
            b.author = str(data["author"]).strip()
        if "year" in data:
            try:
                b.year = int(data["year"]) if data["year"] not in (None, "") else None
            except (TypeError, ValueError):
                return jsonify({"error": "validation_error", "message": "year must be integer"}), 400
        if "genre" in data:
            b.genre = str(data["genre"]).strip() or None
        db.session.commit()
        return jsonify(b.to_dict()), 200

    @app.route("/books/<int:book_id>", methods=["DELETE"])
    def delete_book(book_id):
        b = Book.query.get(book_id)
        if not b:
            return jsonify({"error": "not_found", "message": "Book not found"}), 404
        db.session.delete(b)
        db.session.commit()
        return jsonify({"status": "deleted", "id": book_id}), 200

    # ---- Manejadores de error comunes ----
    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"error": "not_found", "message": "Resource not found"}), 404

    @app.errorhandler(400)
    def handle_400(e):
        return jsonify({"error": "bad_request", "message": "Invalid request"}), 400

    @app.errorhandler(Exception)
    def handle_500(e):
        # En producción evita detallar 'e'
        return jsonify({"error": "server_error", "message": "Internal server error"}), 500

    # CLI para inicializar DB con datos demo
    @app.cli.command("init-db")
    def init_db():
        with app.app_context():
            db.drop_all()
            db.create_all()
            demo = [
                Book(title="Cien años de soledad", author="Gabriel García Márquez", year=1967, genre="Realismo mágico"),
                Book(title="El Quijote", author="Miguel de Cervantes", year=1605, genre="Novela"),
                Book(title="Rayuela", author="Julio Cortázar", year=1963, genre="Novela"),
            ]
            db.session.add_all(demo)
            db.session.commit()
            print("DB inicializada con datos de ejemplo.")

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8001"))
    app.run(host=host, port=port, debug=True)
