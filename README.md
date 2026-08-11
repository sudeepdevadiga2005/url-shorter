# URL Shortener API

## 1. Project Overview

A minimal REST API that shortens long URLs. You submit a long URL, the API stores it in a PostgreSQL database and returns a short URL such as `http://localhost:8000/a4Kz9Qw`. Opening the short URL redirects you to the original page.

The project is built as a Python Development Internship assessment for VISMA. It deliberately stays small and readable: one file per responsibility, no framework magic, and no unrelated features.

## 2. Features

- `POST /shorten` – accepts a long URL, generates a unique short code, saves it to PostgreSQL, and returns the short URL.
- `GET /{short_code}` – looks up a short code and redirects (HTTP 302) to the original URL. Returns `404` when the code is unknown.
- URL validation with Pydantic `HttpUrl` – invalid input such as `"hello"` is rejected with HTTP 422 before any database work.
- Random, URL-safe short codes (7 characters from A-Z, a-z, 0-9) generated with Python's `secrets` module, with collision handling.
- Automatic API documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc).
- Environment configuration through a `.env` file, with no credentials committed to the repository.

## 3. Technology Stack

| Layer      | Technology                                  |
| ---------- | ------------------------------------------- |
| Language   | Python 3.10+                                |
| Framework  | FastAPI                                     |
| Server     | Uvicorn                                     |
| Database   | PostgreSQL                                  |
| ORM        | SQLAlchemy 2.x                              |
| Validation | Pydantic 2.x                                |
| Config     | python-dotenv                               |
| Testing    | pytest + FastAPI TestClient (integration)   |

## 4. Project Structure

```
url-shortener/
│
├── app/
│   ├── __init__.py     # Marks app/ as a Python package
│   ├── main.py         # FastAPI application and routes
│   ├── database.py     # Engine, session factory, Base, get_db dependency
│   ├── models.py       # SQLAlchemy model (the "urls" table)
│   ├── schemas.py      # Pydantic request/response models
│   └── crud.py         # Short-code generation and DB operations
│
├── tests/
│   └── test_main.py    # Integration tests (run against the real database)
│
├── requirements.txt    # Python dependencies
├── .env.example        # Template for the local .env file
├── .gitignore          # Files that must not be committed
├── README.md           # This document
└── SUBMISSION.md       # Hand-in summary for the assessment
```

## 5. Prerequisites

- Python 3.10 or newer (the project uses modern type hints such as `Mapped`).
- PostgreSQL 12 or newer.
- Windows (commands below use PowerShell/cmd; Linux/macOS equivalents are shown where useful).

## 6. PostgreSQL Setup

### Windows

1. Download PostgreSQL from <https://www.postgresql.org/download/windows/> and install it.
2. During installation you choose a password for the `postgres` superuser. Remember it — it goes into `.env`.
3. During installation you can also install **pgAdmin** (the graphical tool). It is optional.

### Create the database

Open a terminal and connect to PostgreSQL:

```
psql -U postgres
```

You will be prompted for the `postgres` password you set at install time.

Then create the database:

```sql
CREATE DATABASE url_shortener;
```

Verify the database exists:

```
\l
```

Look for a row named `url_shortener` in the list. Type `\q` to exit.

The application creates its `urls` table automatically on startup (see section 9), so you only need to create the empty database by hand.

## 7. Environment Configuration

Copy the example file and fill in your real password:

```
copy .env.example .env
```

then edit `.env`:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/url_shortener
BASE_URL=http://localhost:8000
```

Replace `YOUR_PASSWORD` with the password you set for the `postgres` user. Leave `BASE_URL` as `http://localhost:8000` for local development.

The `.env` file contains a real password and must never be committed. It is already listed in `.gitignore`.

## 8. Installation

Open a terminal in the project root (`url-shortener/`).

**Windows:**

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/macOS:**

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To confirm the virtual environment is active, the terminal prompt should show `(venv)` before the path.

## 9. Running the Application

Make sure PostgreSQL is running and the `.env` file is in place, then start the API:

```
uvicorn app.main:app --reload
```

This command means:

- `uvicorn` – the ASGI server that runs the application.
- `app.main:app` – import the `app` object from the module `app/main.py` (module `app.main`, attribute `app`).
- `--reload` – automatically restart the server when code files change (development convenience).

The server starts at:

- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

On first startup the application creates the `urls` table (via `Base.metadata.create_all`) if it does not exist yet.

## 10. Swagger Documentation

FastAPI generates interactive documentation automatically from the route and Pydantic definitions:

- **Swagger UI** – `http://localhost:8000/docs` – lets you try endpoints with "Try it out".
- **ReDoc** – `http://localhost:8000/redoc` – a more reading-oriented view of the same docs.

## 11. API Endpoints

### POST /shorten

Creates a short URL.

Request body:

```json
{
  "url": "https://www.example.com/some/very/long/url"
}
```

Response `201 Created`:

```json
{
  "short_url": "http://localhost:8000/a4Kz9Qw"
}
```

If the URL is invalid (for example `"hello"`), the API responds `422 Unprocessable Entity`.

### GET /{short_code}

Redirects to the original URL.

Example: open `http://localhost:8000/a4Kz9Qw` in a browser → you land on the original page.

- Response: `302 Found`, `Location` header set to the original URL.
- If the short code does not exist: `404 Not Found` with:

```json
{
  "detail": "Short URL not found"
}
```

## 12. Testing

```
pytest -v
```

The tests in `tests/test_main.py` cover:

1. Successful URL shortening (returns 201 and a short_url).
2. Invalid URL rejected with 422.
3. Missing short code returns 404.
4. Valid short code redirects (302, correct Location header).

Note: the tests are integration tests and run against the real `url_shortener` database, because that keeps the assessment setup minimal. Each test deletes the rows it created, so the database is left clean and the tests can be re-run safely. The URL `https://www.example.com` is a reserved example domain and will never perform a real download.

## 13. Error Handling

- **422 Unprocessable Entity** – request body fails Pydantic validation (missing field or invalid URL).
- **404 Not Found** – `GET /{short_code}` receives an unknown code.
- Database errors are not exposed to the client. The application logs a general error; it never returns connection strings, credentials, or stack traces to the caller.

## 14. Design Decisions

- **File-per-responsibility structure.** `database.py` (connection), `models.py` (tables), `schemas.py` (validation), `crud.py` (queries + code generation), `main.py` (routes). Each file is small and easy to explain in an interview.
- **Short codes of 7 characters from 62 symbols.** With `62^7 ≈ 3.5 trillion` possibilities collisions are extremely unlikely, and the collision loop handles the (virtual) case where one happens anyway by simply generating a new code.
- **`secrets` instead of `random`.** `secrets.choice` is cryptographically strong, so short codes cannot be predicted and one short URL cannot be guessed from another.
- **The database does the uniqueness enforcement.** `short_code` has a `unique=True` constraint in the model, so a duplicate can never be inserted even if two requests collided at the same moment.
- **SQLAlchemy 2.x style.** Modern `Mapped[...]` / `mapped_column()` syntax, which is the current recommended API.
- **HTTP 302 for redirects.** Temporary redirect is the standard choice for shorteners that may change or expire later.
- **`Base.metadata.create_all` at startup.** Simple and appropriate for this assessment. A real production codebase would use migration tooling such as Alembic.
- **Full short URL via `BASE_URL`.** The response contains a ready-to-paste short URL, built from the base URL configured in `.env`.

## 15. Future Improvements

Ideas that would be natural next steps, but which were intentionally left out of the assessment scope:

- A click counter to track how often each short URL is used.
- Expiration or deletion of short links.
- Custom aliases chosen by the user (e.g. `my-link`) instead of random codes.
- Alembic migrations instead of `create_all`.
- A local cache (e.g. Redis) to serve popular short codes without hitting PostgreSQL.
- Rate limiting and authentication if the API is exposed publicly.
- Paged listing of existing short URLs.