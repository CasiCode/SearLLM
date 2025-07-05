import os
import datetime
import logging

from fastapi import Security, Request
from fastapi.security import APIKeyHeader

from sqlalchemy.orm import Session

from backend.api.core.exceptions import InvalidKeyException
from backend.database.models.blocked_ip import BlockedIP


class ServiceKeyManager:
    def __init__(self, db: Session):
        self.db = db
        self.WINDOW_MINUTES = 15  # ! MOVE TO CONFIG
        self.MAX_ATTEMPTS = 5  # ! MOVE TO CONFIG
        self.BLOCK_HOURS = 24  # ! MOVE TO CONFIG

    def check_ip(self, ip: str):
        blocked = (
            self.db.query(BlockedIP)
            .filter(
                BlockedIP.ip_address == ip,
                BlockedIP.blocked_until >= datetime.datetime.now(),
            )
            .first()
        )

        if blocked:
            return blocked.blocked_until - datetime.datetime.now()
        else:
            return None

    def record_failed_attempt(self, ip: str, user_id: None):
        self.db.query(BlockedIP).filter(
            BlockedIP.blocked_until <= datetime.datetime.now()
        ).delete()

        blocked_ip = self.db.query(BlockedIP).filter(BlockedIP.ip_address == ip).first()
        if blocked_ip:
            blocked_ip.failed_attemps += 1
            blocked_ip.last_attempt = datetime.datetime.now()

            if blocked_ip.failed_attemps > self.MAX_ATTEMPTS:
                blocked_ip.blocked_until = datetime.datetime.now() + datetime.timedelta(
                    hours=self.BLOCK_HOURS
                )
        else:
            blocked_ip = BlockedIP(
                ip_address=ip,
                failed_attempts=1,
                user_id=user_id or None,
                blocked_until=datetime.datetime.now(),  # ? might be better to SET NULL
            )
            self.db.add(blocked_ip)

        self.db.commit()


SERVICE_API_KEY = os.getenv("SERVICE_API_KEY")
api_key_header = APIKeyHeader(name="SearXTG-API-key")


logger = logging.getLogger(__name__)


async def verify_service_key(
    request: Request, api_key: str = Security(api_key_header)
) -> bool:
    client_ip = request.client.host
    if api_key != SERVICE_API_KEY:
        raise InvalidKeyException("Invalid SERVICE_API_KEY used.")
    return True
