from register.db import db


def get_admins():
    if db is None:
        raise RuntimeError("MongoDB connection is not configured.")

    return db["admins"]