from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from expense_tracker.config import Config
from expense_tracker.db.db_init import init_db
from expense_tracker.models import Account, Budget, Category, Transaction
from expense_tracker.routes.account_routes import account_bp
from expense_tracker.routes.budget_routes import budget_bp
from expense_tracker.routes.category_routes import category_bp
from expense_tracker.routes.transaction_routes import transaction_bp

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Register blueprints
app.register_blueprint(account_bp, url_prefix='/accounts')
app.register_blueprint(budget_bp, url_prefix='/budgets')
app.register_blueprint(category_bp, url_prefix='/categories')
app.register_blueprint(transaction_bp, url_prefix='/transactions')


if __name__ == '__main__':
    with app.app_context():
        init_db()
        app.run(debug=True)
