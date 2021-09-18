from passlib.context import CryptContext

hash_helper = CryptContext(schemes=["bcrypt"])


def encrypt_password(password):
    return hash_helper.encrypt(password)


def verify_password(attempted_password, existing_password):
    return hash_helper.verify(attempted_password, existing_password)
