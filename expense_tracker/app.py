from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from expense_tracker.config import Config
from expense_tracker.db.db_init import init_db
from expense_tracker.models import Account, Budget, Category, Transaction

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


if __name__ == '__main__':
    with app.app_context():
        init_db()
        app.run(debug=True)
