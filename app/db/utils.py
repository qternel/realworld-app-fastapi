from datetime import datetime, timedelta, timezone

from jose import jwt

from .database import Session


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
