"""FastAPI application: URL shortener with POST /shorten and GET /{short_code}."""

import os

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db

# Public base of the API, used to build full short URLs.
# Override with the BASE_URL variable in .env if you deploy elsewhere.
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

app = FastAPI(
    title="URL Shortener API",
    description=(
        "A minimal URL shortener built with FastAPI and PostgreSQL. "
        "Submit a long URL with POST /shorten and receive a short one. "
        "Then open the short URL to be redirected to the original."
    ),
    version="1.0.0",
)

# Create all database tables that are not yet created.
# For this small assessment this is run automatically at startup.
# In a real project you would use a migration tool such as Alembic.
Base.metadata.create_all(bind=engine)


@app.get("/")
def root() -> dict:
    """Simple welcome message on the API root."""
    return {"message": "Welcome to the URL Shortener API. See /docs for usage."}


@app.post(
    "/shorten",
    response_model=schemas.URLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Shorten a URL",
    description="Validates the URL, generates a unique short code, saves the mapping to PostgreSQL, and returns the short URL.",
    response_description="The shortened URL, ready to be shared.",
)
def shorten_url(
    payload: schemas.URLRequest, db: Session = Depends(get_db)
) -> schemas.URLResponse:
    """Create a short URL for a given long URL."""
    # payload.url is already validated by Pydantic (HttpUrl).
    # HttpUrl is a subtype of str, so str() gives us the plain value.
    original_url = str(payload.url)
    url_mapping = crud.create_short_url(db, original_url)
    short_url = f"{BASE_URL}/{url_mapping.short_code}"
    return schemas.URLResponse(short_url=short_url)


@app.get(
    "/{short_code}",
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
    summary="Redirect a short URL",
    description="Looks up the short code and redirects the client to the original URL with HTTP 302. Returns 404 if the code is unknown.",
    response_description="HTTP 302 redirect to the original URL.",
)
def redirect_short_url(
    short_code: str, db: Session = Depends(get_db)
) -> RedirectResponse:
    """Redirect a short code to its original URL."""
    original_url = crud.get_original_url(db, short_code)
    if original_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found"
        )
    return RedirectResponse(url=original_url, status_code=status.HTTP_302_FOUND)