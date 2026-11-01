
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME", "registration_db")

client = None
db = None
users = None

if uri:
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=5000
    )

    db = client[db_name]
    users = db["users"]


def get_users():
    if users is None:
        raise RuntimeError(
            "MongoDB connection is not configured. Check your .env file."
        )

    try:
        client.admin.command("ping")
    except Exception as e:
        raise RuntimeError("MongoDB connection failed.") from e

    return users
