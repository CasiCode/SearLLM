from backend.security.utils import generate_service_token

print(generate_service_token(prefix="st", length=64))
