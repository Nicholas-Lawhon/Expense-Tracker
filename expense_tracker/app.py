from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import os
from dotenv import load_dotenv
from expense_tracker.models import Account, Budget, Category, Transaction
from expense_tracker.utils.crypto import decrypt_value


load_dotenv()

app = Flask(__name__)

encryption_key = os.getenv('ENCRYPTION_KEY').encode()
db_password = decrypt_value(encryption_key, os.getenv('DB_PASSWORD'))

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{db_password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
