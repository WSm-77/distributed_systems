from fastapi import Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from sqlmodel import select
import hmac
import hashlib

from db.db import SessionDep
from data_models.api_user import ApiUser
from config.config import CONFIG

api_key = APIKeyHeader(name="x-api-key")

internal_routes = [
    '/users'
]

async def handle_api_key(req: Request, db: SessionDep, key: str = Security(api_key)):
    # Hash the incoming key with the pepper
    pepper = CONFIG.api_key_pepper
    key_hash = hmac.new(pepper.encode(), key.encode(), hashlib.sha256).hexdigest()

    res = db.exec(
        select(ApiUser).where(ApiUser.api_key_hash == key_hash).where(ApiUser.active == True)
    )

    api_key_data = res.first()

    # No active API key found
    if not api_key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key"
        )

    # Check if the user is trying to access an internal route
    for path in internal_routes:
        if path in req.url.path and not api_key_data.is_internal:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this route"
            )

    # Check if the user has any credits left
    if api_key_data.curr_credits <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="You have no credits left for the month"
        )

    yield api_key_data

    # If successful, decrement the user's credits
    api_key_data.curr_credits -= 1
    db.commit()
    db.refresh(api_key_data)
