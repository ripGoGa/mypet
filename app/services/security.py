from passlib.context import CryptContext


my_cc = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_password_hash(password: str) -> str:
    hash_password = my_cc.hash(password)
    return hash_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    result = my_cc.verify(plain_password, hashed_password)
    return result



