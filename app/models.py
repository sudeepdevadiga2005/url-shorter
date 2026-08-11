"""SQLAlchemy models. Each class maps to one database table."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class URL(Base):
    """Represents a single short URL mapping.

    Table:
        urls
        -------------------------------
        id            integer  (primary key)
        original_url  varchar
        short_code    varchar  (unique)
        created_at    timestamp
        -------------------------------
    """

    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    # short_code is unique, so two different URLs can never share a code.
    # PostgreSQL automatically creates a unique index for this column.
    short_code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:  # helpful when debugging in a shell
        return f"<URL short_code={self.short_code!r} original_url={self.original_url!r}>"
