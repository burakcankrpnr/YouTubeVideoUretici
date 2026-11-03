"""SQLite engine and session helpers for Animation Studio."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.studio.models import Base
from app.utils import utils

_ENGINE: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def studio_db_path() -> Path:
    root = Path(utils.storage_dir("studio", create=True))
    return root / "studio.db"


def studio_asset_dir(*parts: str) -> Path:
    path = Path(utils.storage_dir("studio", create=True))
    for part in parts:
        path = path / part
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_engine() -> Engine:
    global _ENGINE, _SessionLocal
    if _ENGINE is None:
        db_path = studio_db_path()
        _ENGINE = create_engine(
            f"sqlite:///{db_path.as_posix()}",
            connect_args={"check_same_thread": False},
            future=True,
        )

        @event.listens_for(_ENGINE, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record):  # noqa: ANN001
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        _SessionLocal = sessionmaker(bind=_ENGINE, autoflush=True, autocommit=False, future=True)
    return _ENGINE


def init_studio_db() -> Path:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    studio_asset_dir("assets")
    studio_asset_dir("renders")
    studio_asset_dir("storyboards")
    studio_asset_dir("characters")
    return studio_db_path()


@contextmanager
def get_session() -> Iterator[Session]:
    get_engine()
    assert _SessionLocal is not None
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
