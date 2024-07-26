from cryptography.fernet import Fernet


def generate_key():
    return Fernet.generate_key()


def encrypt_value(key, value):
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()


def decrypt_value(key, encrypted_value):
    f = Fernet(key)
    return f.decrypt(encrypted_value.encode()).decode()
