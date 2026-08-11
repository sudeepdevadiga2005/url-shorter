"""Integration tests for the URL Shortener API.

These tests run against the real PostgreSQL url_shortener database,
the same one the application uses. That keeps the setup simple for an
internship assessment: no separate test database or mocking layer.

Each test creates its own rows and deletes them afterwards, so the
tests do not leave data behind and can be re-run safely.

Run from the project root with:
pytest -v
"""

import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import URL

client = TestClient(app)


def _cleanup_short_code(short_code: str) -> None:
    """Delete a row created during a test, if it still exists."""
    if not short_code:
        return

    db = SessionLocal()
    try:
        row = db.query(URL).filter(URL.short_code == short_code).first()
        if row:
            db.delete(row)
            db.commit()
    finally:
        db.close()


def test_shorten_url_returns_short_url() -> None:
    """POST /shorten with a valid URL returns 201 and a short_url."""
    response = client.post(
        "/shorten",
        json={"url": "https://www.google.com"},
    )
    assert response.status_code == 201

    data = response.json()
    assert "short_url" in data

    # The short URL must contain a short code after the last "/".
    short_code = data["short_url"].rsplit("/", 1)[-1]
    assert len(short_code) == 7  # CODE_LENGTH in app/crud.py

    _cleanup_short_code(short_code)


def test_shorten_url_rejects_invalid_url() -> None:
    """POST /shorten with a non-URL must be rejected with 422."""
    response = client.post(
        "/shorten",
        json={"url": "hello"},
    )
    assert response.status_code == 422


def test_missing_short_code_returns_404() -> None:
    """GET / for an unknown code returns 404."""
    response = client.get("/doesnotexist123")
    assert response.status_code == 404
    assert response.json() == {"detail": "Short URL not found"}


def test_valid_short_code_redirects() -> None:
    """GET / for a known code redirects to the original URL."""
    created = client.post(
        "/shorten",
        json={"url": "https://www.example.com"},
    )
    assert created.status_code == 201

    short_code = created.json()["short_url"].rsplit("/", 1)[-1]

    # follow_redirects=False so we can inspect the 302 response.
    redirected = client.get(
        f"/{short_code}",
        follow_redirects=False,
    )
    assert redirected.status_code == 302
    assert redirected.headers["location"] == "https://www.example.com/"

    _cleanup_short_code(short_code)