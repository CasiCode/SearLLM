import os
import datetime
import logging

from fastapi import Security, Request, Depends
from fastapi.security import APIKeyHeader

from sqlalchemy.orm import Session

from backend.api.core.exceptions import InvalidKeyException, BlockedIPException
from backend.database.models.blocked_ip import BlockedIP
from backend.api.core.dependencies import get_db
from backend.utils import get_config


config = get_config("api/config.yml")


# TODO: Write the thing completely and read trough it


class SecurityManager:
    def __init__(self, db: Session):
        self.db = db

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

    def record_failed_attempt(self, ip: str):
        self.db.query(BlockedIP).filter(
            BlockedIP.blocked_until <= datetime.datetime.now()
        ).delete()

        blocked_ip = self.db.query(BlockedIP).filter(BlockedIP.ip_address == ip).first()
        if blocked_ip:
            blocked_ip.failed_attemps += 1
            blocked_ip.last_attempt = datetime.datetime.now()

            if blocked_ip.failed_attemps > config.service_key_manager.max_attempts:
                blocked_ip.blocked_until = datetime.datetime.now() + datetime.timedelta(
                    hours=config.service_key_manager.block_hours
                )
        else:
            blocked_ip = BlockedIP(
                ip_address=ip,
                failed_attempts=1,
                blocked_until=datetime.datetime.now(),  # ? might be better to SET NULL
            )
            self.db.add(blocked_ip)

        self.db.commit()


SERVICE_API_KEY = os.getenv("SERVICE_API_KEY")
api_key_header = APIKeyHeader(name="SearXTG-API-key")


logger = logging.getLogger(__name__)


async def verify_service_key(
    request: Request,
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db),
) -> bool:
    client_ip = request.client.host
    manager = SecurityManager()

    if block_time := manager.check_ip(client_ip):
        raise BlockedIPException(
            f"This IP was blocked after too many failed attempts. Try again in {block_time}."
        )

    if api_key != SERVICE_API_KEY:
        manager.record_failed_attempt(client_ip)
        raise InvalidKeyException("Invalid SERVICE_API_KEY used.")
    return True
