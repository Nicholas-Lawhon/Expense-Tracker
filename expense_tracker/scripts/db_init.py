from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import os
from dotenv import load_dotenv
from expense_tracker.models import Base, Account, Budget, Category, Transaction
from expense_tracker.utils.crypto import decrypt_value

load_dotenv()

app = Flask(__name__)

encryption_key = os.getenv('ENCRYPTION_KEY').encode()
db_password = decrypt_value(encryption_key, os.getenv('DB_PASSWORD'))

app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{db_password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


def init_db():
    inspector = inspect(db.engine)
    existing_tables = inspector.get_table_names()

    model_tables = {Account.__tablename__, Budget.__tablename__, Category.__tablename__, Transaction.__tablename__}

    if not model_tables.issubset(existing_tables):
        print("Creating missing tables...")
        Base.metadata.create_all(db.engine)
        print("Tables created successfully.")
    else:
        print("All tables already exist.")


if __name__ == "__main__":
    with app.app_context():
        init_db()