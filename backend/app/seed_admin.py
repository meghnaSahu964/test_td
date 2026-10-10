"""Provision a local admin explicitly with ADMIN_EMAIL and ADMIN_PASSWORD."""

import os

from sqlalchemy.dialects.postgresql import insert

from .core.database import SessionLocal
from .core.security import hash_password
from .models import AdminUser


def main() -> None:
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")
    if not email or not password:
        raise SystemExit(
            "Set ADMIN_EMAIL and ADMIN_PASSWORD before provisioning an admin."
        )

    statement = (
        insert(AdminUser)
        .values(
            email=email,
            password_hash=hash_password(password),
            is_active=True,
        )
        .on_conflict_do_nothing(index_elements=[AdminUser.email])
    )

    with SessionLocal.begin() as db:
        result = db.execute(statement)

    if result.rowcount:
        print("Development admin created.")
    else:
        print("Admin email already exists; no changes made.")


if __name__ == "__main__":
    main()
