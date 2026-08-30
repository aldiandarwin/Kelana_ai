"""Idempotent PostgreSQL migration for Session 8 user ownership.

Run once from backend/ before starting the updated API against a database that
already contains Session 4-7 trips.
"""

from sqlalchemy import text

from database import Base, engine
from models.trip import Trip  # noqa: F401 - registers the table in metadata
from models.user import User  # noqa: F401 - registers the table in metadata

LEGACY_EMAIL = "legacy-import@kelana.local"


def migrate() -> None:
    """Create users, backfill old trips, then enforce the ownership constraint."""

    if engine.dialect.name != "postgresql":
        raise RuntimeError("Session 8 migration is intended for PostgreSQL only.")

    Base.metadata.tables["users"].create(bind=engine, checkfirst=True)

    with engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE trips ADD COLUMN IF NOT EXISTS user_id INTEGER")
        )

        legacy_trip_count = connection.execute(
            text("SELECT COUNT(*) FROM trips WHERE user_id IS NULL")
        ).scalar_one()

        if legacy_trip_count:
            connection.execute(
                text(
                    """
                    INSERT INTO users (name, email, password_hash, created_at)
                    VALUES (
                        'Legacy Import',
                        :email,
                        'disabled-session-8-migration',
                        CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (email) DO NOTHING
                    """
                ),
                {"email": LEGACY_EMAIL},
            )
            legacy_user_id = connection.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": LEGACY_EMAIL},
            ).scalar_one()
            connection.execute(
                text("UPDATE trips SET user_id = :user_id WHERE user_id IS NULL"),
                {"user_id": legacy_user_id},
            )

        connection.execute(
            text("ALTER TABLE trips ALTER COLUMN user_id SET NOT NULL")
        )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS ix_trips_user_id ON trips (user_id)")
        )
        connection.execute(
            text(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_constraint
                        WHERE conname = 'fk_trips_user_id_users'
                    ) THEN
                        ALTER TABLE trips
                        ADD CONSTRAINT fk_trips_user_id_users
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
                    END IF;
                END
                $$
                """
            )
        )

    print(
        "Session 8 migration complete. "
        f"Preserved {legacy_trip_count} pre-auth trip(s)."
    )


if __name__ == "__main__":
    migrate()
