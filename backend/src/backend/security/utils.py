import secrets
import base64


def generate_service_token(prefix: str = "") -> str:
    random_bytes = secrets.token_bytes(64)

    service_token = base64.urlsafe_b64encode(random_bytes).decode("utf-8")
    service_token = f"{prefix}_{service_token}"

    return service_token
