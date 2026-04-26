from sqlalchemy import text

from db import db


MIGRATIONS: list[tuple[str, str]] = [
    (
        "001_unique_users_user_id",
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_users_user_id ON users(user_id);",
    ),
    (
        "002_unique_groups_group_id",
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_groups_group_id ON groups(group_id);",
    ),
    (
        "003_unique_messages_job_name",
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_messages_job_name ON messages(job_name) WHERE job_name IS NOT NULL;",
    ),
    (
        "004_idx_messages_user_id",
        "CREATE INDEX IF NOT EXISTS ix_messages_user_id ON messages(user_id);",
    ),
]


async def run_migrations() -> None:
    await db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """
        )
    )

    rows = await db.execute(text("SELECT name FROM schema_migrations;"))
    applied = {row[0] for row in rows.fetchall()}

    for name, sql in MIGRATIONS:
        if name in applied:
            continue
        await db.execute(text(sql))
        await db.execute(
            text("INSERT INTO schema_migrations(name) VALUES (:name);"),
            {"name": name},
        )
    await db.commit()
