import os
from dotenv import load_dotenv
from expense_tracker.utils.crypto import decrypt_value


load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def get_database_url():
        encryption_key = os.getenv('ENCRYPTION_KEY').encode()
        db_password = decrypt_value(encryption_key, os.getenv('DB_PASSWORD'))
        return f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{db_password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}"

    # Database URL to be used by Flask and SQLAlchemy
    SQLALCHEMY_DATABASE_URI = get_database_url.__func__()

    DB_URL = SQLALCHEMY_DATABASE_URI
