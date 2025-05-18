from config import ADMIN_PASSWORD

def verify_admin_password(password: str) -> bool:
    return password == ADMIN_PASSWORD
