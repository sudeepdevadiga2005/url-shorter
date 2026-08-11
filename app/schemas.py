"""Pydantic schemas: request and response validation."""

from pydantic import BaseModel, HttpUrl


class URLRequest(BaseModel):
    """Body of the POST /shorten request.

    Pydantic validates that "url" is a real URL. If it is not,
    FastAPI rejects the request with HTTP 422 before any database
    work happens.

    Example:
        {"url": "https://www.example.com/some/very/long/url"}
    """

    url: HttpUrl


class URLResponse(BaseModel):
    """Body of the POST /shorten response.

    Example:
        {"short_url": "http://localhost:8000/abc123"}
    """

    short_url: str
