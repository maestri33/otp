"""
Tortoise ORM configuration.

- TORTOISE_ORM is the config dict used by both the app lifespan
  and Aerich (migrations). Do NOT rename it.
- Model discovery is by convention: everything under `app.models`
  plus Aerich internal tables.
"""

from pathlib import Path

from tortoise import Tortoise

from app.config import get_settings

settings = get_settings()


def _ensure_sqlite_dir(url: str) -> None:
    """
    Create the SQLite file directory if it doesn't exist.

    Tortoise accepts:
    - `sqlite://data/app.db`           (relative path, 2 slashes)
    - `sqlite:///abs/path/app.db`      (absolute path, 3 slashes)
    - `sqlite://:memory:`              (in-memory)
    """
    if not url.startswith("sqlite"):
        return
    after = url.split("://", 1)[1]
    if after in (":memory:", "") or after.startswith(":memory:"):
        return
    # 3 slashes become absolute path: sqlite:///x -> /x
    path_part = "/" + after.lstrip("/") if url.startswith("sqlite:///") else after
    Path(path_part).parent.mkdir(parents=True, exist_ok=True)


TORTOISE_ORM = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}


async def init_db() -> None:
    """Initialize connections and (in dev/sqlite) create tables if missing."""
    _ensure_sqlite_dir(settings.database_url)
    await Tortoise.init(config=TORTOISE_ORM)
    if settings.env == "dev" and settings.database_url.startswith("sqlite"):
        # In dev with sqlite it's convenient to auto-create; in prod use aerich.
        await Tortoise.generate_schemas(safe=True)


async def close_db() -> None:
    """Close connections — called on FastAPI shutdown."""
    await Tortoise.close_connections()
