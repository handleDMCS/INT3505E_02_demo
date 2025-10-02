# Library Management API

A simple Flask REST API for managing library books with CRUD operations and status management.

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- pipenv

### Installation

1. **Install dependencies:**

```bash
pipenv install flask flask-restx
```

2. **Activate the virtual environment:**

```bash
pipenv shell
```

### Setup Database

Generate the SQLite database with sample data:

```bash
python generate_db.py
```

This will create a `library.db` file with a sample collection of books.

### Run the Application

Start the Flask development server:

```bash
python app.py
```

The API will be available at `http://127.0.0.1:5000`

## 📚 API Documentation

Interactive API documentation (Swagger UI) is available at:

**[http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs)**

## 📋 API Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `GET` | `/books/` | List all books | - |
| `POST` | `/books/` | Create a new book | `{"name": "string", "status": "available/borrowed"}` |
| `GET` | `/books/{id}` | Get a specific book by ID | - |
| `PUT` | `/books/{id}` | Update a book | `{"name": "string", "status": "available/borrowed"}` |
| `DELETE` | `/books/{id}` | Delete a book | - |
| `PATCH` | `/books/{id}/status` | Update book status only | `{"status": "available/borrowed"}` |

## 📝 Example Usage

### Create a Book

```bash
curl -X POST http://127.0.0.1:5000/books/ \
  -H "Content-Type: application/json" \
  -d '{"name": "The Hobbit", "status": "available"}'
```

### Get All Books

```bash
curl http://127.0.0.1:5000/books/
```

### Update Book Status

```bash
curl -X PATCH http://127.0.0.1:5000/books/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "borrowed"}'
```

## 🗄️ Database Schema

**Table: books**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key (auto-increment) |
| `name` | TEXT | Book name |
| `status` | TEXT | Book status (`available` or `borrowed`) |

## 🧪 Testing

Use the interactive Swagger UI at `/docs` to test all endpoints directly in your browser. No additional tools required!