"""CRUD operations and short-code generation."""

import secrets
import string

from sqlalchemy.orm import Session

from . import models


# Alphabet contains uppercase/lowercase letters and digits.
# A-Z (uppercase), a-z (lowercase), 0-9 = 62 possibilities per character.
ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 7


def generate_short_code() -> str:
    """Generate a random, URL-safe short code.

    Example outputs: "a4Kz9Qw", "x7Kp92", "Zx81Qa".
    Uses the operating system's cryptographic random source,
    so codes cannot be guessed or predicted.
    """
    return "".join(
        secrets.choice(ALPHABET) for _ in range(CODE_LENGTH)
    )


def create_short_url(db: Session, original_url: str) -> models.URL:
    """Create and persist a new URL mapping with a unique short code."""
    # Loop until we find a code that is not already in the database.
    # With 62^7 possible codes, a collision is extremely unlikely,
    # but we still handle it correctly.
    while True:
        code = generate_short_code()

        if (
            db.query(models.URL)
            .filter(models.URL.short_code == code)
            .first()
            is None
        ):
            break

    url_mapping = models.URL(
        original_url=original_url,
        short_code=code,
    )

    db.add(url_mapping)
    db.commit()
    db.refresh(url_mapping)

    return url_mapping


def get_original_url(
    db: Session,
    short_code: str,
) -> str | None:
    """Look up the original URL for a short code.

    Returns None when the code does not exist.
    """
    url_mapping = (
        db.query(models.URL)
        .filter(models.URL.short_code == short_code)
        .first()
    )

    return url_mapping.original_url if url_mapping else None