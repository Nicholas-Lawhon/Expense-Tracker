import os
from dotenv import load_dotenv
from expense_tracker.utils.crypto import decrypt_value

load_dotenv()

encryption_key = os.getenv('ENCRYPTION_KEY').encode()
db_password = decrypt_value(encryption_key, os.getenv('DB_PASSWORD'))

DB_URL = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{db_password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}"