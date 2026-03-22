import argparse
import hashlib
import hmac
import secrets

from data_models.api_user import ApiUser
from db.db import engine, init_db
from config.config import CONFIG
from sqlmodel import Session


def hash_key(raw_key: str) -> str:
    pepper = CONFIG.api_key_pepper
    return hmac.new(pepper.encode(), raw_key.encode(), hashlib.sha256).hexdigest()


def create_key(name: str, is_internal: bool = False) -> str:
    raw = secrets.token_urlsafe(32)
    digest = hash_key(raw)
    init_db()

    with Session(engine) as session:
        user = ApiUser(name=name, api_key_hash=digest, is_internal=is_internal)
        session.add(user)
        session.commit()
        session.refresh(user)

    return raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("create", nargs='?', help="create a key", default=None)
    parser.add_argument("--name", required=False, default="default")
    parser.add_argument("--internal", action="store_true")
    parser.add_argument("--init-db", action="store_true")
    args = parser.parse_args()

    if args.init_db:
        init_db()
        print("Initialized database (tables created)")
        return

    if args.create is not None:
        raw = create_key(args.name, is_internal=args.internal)
        print("Created API key for '{}'. Save this value now (it will not be stored raw):".format(args.name))
        print(raw)
        return

    parser.print_help()

if __name__ == "__main__":
    main()
