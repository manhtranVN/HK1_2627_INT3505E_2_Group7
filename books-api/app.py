import os
import sys
import uuid
import re
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import yaml
from flask import Flask, request, jsonify, make_response, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load OpenAPI specification from openapi.yaml
SPEC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "openapi.yaml")
with open(SPEC_PATH, "r", encoding="utf-8") as f:
    OPENAPI_SPEC = yaml.safe_load(f)

# In-memory database of books
BOOKS_DB = {
    "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11": {
        "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "genre": "Technology",
        "publishedDate": "2008-08-01",
        "price": 42.50,
        "isAvailable": True,
        "createdAt": "2026-10-11T08:00:00Z",
        "updatedAt": "2026-10-11T08:00:00Z"
    },
    "b1ffcd88-8b1a-4fe7-aa5c-5aa8ac270b22": {
        "id": "b1ffcd88-8b1a-4fe7-aa5c-5aa8ac270b22",
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann",
        "isbn": "9781449373320",
        "genre": "Technology",
        "publishedDate": "2017-03-16",
        "price": 49.99,
        "isAvailable": True,
        "createdAt": "2026-10-11T08:15:00Z",
        "updatedAt": "2026-10-11T08:15:00Z"
    },
    "c2eede77-7a2b-4ed6-994b-49979b160c33": {
        "id": "c2eede77-7a2b-4ed6-994b-49979b160c33",
        "title": "Design Patterns: Elements of Reusable Object-Oriented Software",
        "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
        "isbn": "9780201633610",
        "genre": "Technology",
        "publishedDate": "1994-10-21",
        "price": 54.95,
        "isAvailable": False,
        "createdAt": "2026-10-11T08:30:00Z",
        "updatedAt": "2026-10-11T08:30:00Z"
    },
    "d3dddc66-693c-4dc5-883a-38868a050d44": {
        "id": "d3dddc66-693c-4dc5-883a-38868a050d44",
        "title": "Sapiens: A Brief History of Humankind",
        "author": "Yuval Noah Harari",
        "isbn": "9780062316097",
        "genre": "History",
        "publishedDate": "2014-02-10",
        "price": 24.99,
        "isAvailable": True,
        "createdAt": "2026-10-11T08:45:00Z",
        "updatedAt": "2026-10-11T08:45:00Z"
    }
}

VALID_GENRES = ["Fiction", "Non-Fiction", "Technology", "Science", "History", "Literature"]

# Helper: RFC 7807 Problem Details response builder
def problem_details(status: int, title: str, detail: str, error_type: str = None):
    if not error_type:
        type_slug = title.lower().replace(" ", "-")
        error_type = f"https://api.example.com/errors/{type_slug}"
    
    trace_id = str(uuid.uuid4())
    payload = {
        "type": error_type,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path,
        "traceId": trace_id
    }
    response = make_response(jsonify(payload), status)
    response.headers["Content-Type"] = "application/problem+json"
    return response

# Root route - Redirect to interactive documentation
@app.route("/")
def index():
    return redirect("/docs")

# OpenAPI Specification in JSON format (Requirement 3)
@app.route("/openapi.json", methods=["GET"])
def get_openapi_json():
    return jsonify(OPENAPI_SPEC)

# Swagger UI Documentation (Requirement 3)
@app.route("/docs", methods=["GET"])
def swagger_ui():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Books Management API - Swagger UI</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.18.2/swagger-ui.css" />
  <link rel="icon" type="image/png" href="https://swagger.io/favicon-32x32.png" sizes="32x32" />
  <style>
    html {
      box-sizing: border-box;
      overflow: -moz-scrollbars-vertical;
      overflow-y: scroll;
    }
    *, *:before, *:after {
      box-sizing: inherit;
    }
    body {
      margin: 0;
      background: #fafafa;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .topbar {
      display: none !important;
    }
    .swagger-ui .info {
      margin: 25px 0;
    }
    .swagger-ui .info .title {
      color: #1e3a8a;
    }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.18.2/swagger-ui-bundle.js" charset="UTF-8"></script>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.18.2/swagger-ui-standalone-preset.js" charset="UTF-8"></script>
  <script>
    window.onload = function() {
      const ui = SwaggerUIBundle({
        url: "/openapi.json",
        dom_id: "#swagger-ui",
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        plugins: [
          SwaggerUIBundle.plugins.DownloadUrl
        ],
        layout: "StandaloneLayout",
        displayRequestDuration: true,
        docExpansion: "list",
        filter: true,
        showExtensions: true,
        showCommonExtensions: true,
        tryItOutEnabled: true,
        persistAuthorization: true
      });
      window.ui = ui;
    };
  </script>
</body>
</html>"""
    return html_content, 200, {"Content-Type": "text/html; charset=utf-8"}


# -------------------------------------------------------------
# 5 REST API Endpoints (supporting both /v1/books and /books)
# -------------------------------------------------------------

# 1. GET /v1/books: List books with pagination and filters
@app.route("/v1/books", methods=["GET"])
@app.route("/books", methods=["GET"])
def list_books():
    try:
        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return problem_details(400, "Bad Request", "The 'limit' and 'offset' parameters must be valid integers.")

    if limit < 1 or limit > 100:
        return problem_details(400, "Bad Request", "The 'limit' parameter must be between 1 and 100.")
    if offset < 0:
        return problem_details(400, "Bad Request", "The 'offset' parameter must be greater than or equal to 0.")

    genre_param = request.args.get("genre")
    if genre_param and genre_param not in VALID_GENRES:
        return problem_details(400, "Bad Request", f"Invalid genre '{genre_param}'. Allowed values: {', '.join(VALID_GENRES)}")

    is_available_param = request.args.get("isAvailable")
    search_param = request.args.get("search", "").strip().lower()

    # Filter books
    books = list(BOOKS_DB.values())
    if genre_param:
        books = [b for b in books if b.get("genre") == genre_param]
    if is_available_param is not None:
        val = is_available_param.lower() in ["true", "1"]
        books = [b for b in books if b.get("isAvailable") == val]
    if search_param:
        books = [
            b for b in books
            if search_param in b.get("title", "").lower() or search_param in b.get("author", "").lower()
        ]

    total = len(books)
    items = books[offset: offset + limit]

    return jsonify({
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset
    }), 200


# 2. POST /v1/books: Create a new book
@app.route("/v1/books", methods=["POST"])
@app.route("/books", methods=["POST"])
def create_book():
    if not request.is_json:
        return problem_details(400, "Invalid Content-Type", "Request body must have Content-Type: application/json.")

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return problem_details(400, "Malformed JSON", "Malformed JSON body. Expected a JSON object.")

    # Required fields validation
    required_fields = ["title", "author", "isbn", "genre", "price"]
    missing = [f for f in required_fields if f not in data or data[f] is None]
    if missing:
        return problem_details(422, "Validation Error", f"Missing required fields: {', '.join(missing)}")

    title = str(data["title"]).strip()
    author = str(data["author"]).strip()
    isbn = str(data["isbn"]).strip()
    genre = str(data["genre"]).strip()
    
    if len(title) == 0:
        return problem_details(422, "Validation Error", "Field 'title' cannot be empty.")
    if len(author) == 0:
        return problem_details(422, "Validation Error", "Field 'author' cannot be empty.")
    if not re.match(r"^[0-9]{13}$", isbn):
        return problem_details(422, "Validation Error", "Field 'isbn' must be a valid 13-digit ISBN string.")
    if genre not in VALID_GENRES:
        return problem_details(422, "Validation Error", f"Field 'genre' must be one of: {', '.join(VALID_GENRES)}")

    try:
        price = float(data["price"])
        if price < 0:
            return problem_details(422, "Validation Error", "Field 'price' must be a number >= 0.")
    except (ValueError, TypeError):
        return problem_details(422, "Validation Error", "Field 'price' must be a valid number.")

    # Validate publishedDate if present
    pub_date = data.get("publishedDate")
    if pub_date:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(pub_date)):
            return problem_details(422, "Validation Error", "Field 'publishedDate' must be formatted as YYYY-MM-DD (RFC 3339).")

    is_available = bool(data.get("isAvailable", True))

    book_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    new_book = {
        "id": book_id,
        "title": title,
        "author": author,
        "isbn": isbn,
        "genre": genre,
        "publishedDate": pub_date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "price": round(price, 2),
        "isAvailable": is_available,
        "createdAt": now_iso,
        "updatedAt": now_iso
    }

    BOOKS_DB[book_id] = new_book

    response = make_response(jsonify(new_book), 201)
    response.headers["Location"] = f"/v1/books/{book_id}"
    return response


# 3. GET /v1/books/<bookId>: Get book details by ID
@app.route("/v1/books/<book_id>", methods=["GET"])
@app.route("/books/<book_id>", methods=["GET"])
def get_book_by_id(book_id):
    book = BOOKS_DB.get(book_id)
    if not book:
        return problem_details(404, "Book Not Found", f"Book with ID '{book_id}' was not found.")
    return jsonify(book), 200


# 4. PATCH /v1/books/<bookId>: Partially update a book
@app.route("/v1/books/<book_id>", methods=["PATCH"])
@app.route("/books/<book_id>", methods=["PATCH"])
def patch_book(book_id):
    book = BOOKS_DB.get(book_id)
    if not book:
        return problem_details(404, "Book Not Found", f"Book with ID '{book_id}' was not found.")

    if not request.is_json:
        return problem_details(400, "Invalid Content-Type", "Request body must have Content-Type: application/json.")

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return problem_details(400, "Malformed JSON", "Malformed JSON body. Expected a JSON object.")

    if "title" in data:
        t = str(data["title"]).strip()
        if len(t) == 0:
            return problem_details(422, "Validation Error", "Field 'title' cannot be empty.")
        book["title"] = t

    if "author" in data:
        a = str(data["author"]).strip()
        if len(a) == 0:
            return problem_details(422, "Validation Error", "Field 'author' cannot be empty.")
        book["author"] = a

    if "isbn" in data:
        isbn = str(data["isbn"]).strip()
        if not re.match(r"^[0-9]{13}$", isbn):
            return problem_details(422, "Validation Error", "Field 'isbn' must be a valid 13-digit ISBN string.")
        book["isbn"] = isbn

    if "genre" in data:
        g = str(data["genre"]).strip()
        if g not in VALID_GENRES:
            return problem_details(422, "Validation Error", f"Field 'genre' must be one of: {', '.join(VALID_GENRES)}")
        book["genre"] = g

    if "price" in data:
        try:
            p = float(data["price"])
            if p < 0:
                return problem_details(422, "Validation Error", "Field 'price' must be a number >= 0.")
            book["price"] = round(p, 2)
        except (ValueError, TypeError):
            return problem_details(422, "Validation Error", "Field 'price' must be a valid number.")

    if "publishedDate" in data:
        d = str(data["publishedDate"]).strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            return problem_details(422, "Validation Error", "Field 'publishedDate' must be formatted as YYYY-MM-DD.")
        book["publishedDate"] = d

    if "isAvailable" in data:
        book["isAvailable"] = bool(data["isAvailable"])

    book["updatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return jsonify(book), 200


# 5. DELETE /v1/books/<bookId>: Delete a book
@app.route("/v1/books/<book_id>", methods=["DELETE"])
@app.route("/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    if book_id not in BOOKS_DB:
        return problem_details(404, "Book Not Found", f"Book with ID '{book_id}' was not found.")

    del BOOKS_DB[book_id]
    return ("", 204)


# Global Error Handlers (RFC 7807)
@app.errorhandler(404)
def not_found_handler(e):
    return problem_details(404, "Not Found", "The requested endpoint or resource does not exist.")

@app.errorhandler(405)
def method_not_allowed_handler(e):
    return problem_details(405, "Method Not Allowed", f"HTTP method {request.method} is not allowed for this endpoint.")

@app.errorhandler(500)
def internal_server_error_handler(e):
    return problem_details(500, "Internal Server Error", "An unexpected internal server error occurred.")

if __name__ == "__main__":
    print("Starting Books Management API on http://localhost:5000")
    print("OpenAPI Specification JSON: http://localhost:5000/openapi.json")
    print("Swagger UI Documentation:   http://localhost:5000/docs")
    app.run(host="0.0.0.0", port=5000, debug=False)
