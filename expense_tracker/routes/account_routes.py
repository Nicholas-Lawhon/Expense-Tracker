from flask import Blueprint, request, jsonify
from expense_tracker.models import Account
from expense_tracker.db.operations import BaseOperations
from expense_tracker.db.connection import get_db_session

account_bp = Blueprint('account', __name__)


@account_bp.route('/', methods=['GET'])
def get_all_accounts():
    """Retrieve all accounts"""
    with get_db_session() as session:
        accounts, total = BaseOperations.get_all(session, Account)
        return jsonify([account.to_dict() for account in accounts]), 200


@account_bp.route('/<int:account_id>', methods=['GET'])
def get_account(account_id):
    """Retrieve a specific account"""
    with get_db_session() as session:
        account = BaseOperations.read(session, Account, account_id)
        if account:
            return jsonify(account.to_dict()), 200
        return jsonify({"error": "Account not found"}), 404


@account_bp.route('/', methods=['POST'])
def create_account():
    """Create a new account"""
    data = request.json
    with get_db_session() as session:
        new_account = BaseOperations.create(session, Account, **data)
        return jsonify(new_account.to_dict()), 201


@account_bp.route('/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    """Update an existing account"""
    data = request.json
    with get_db_session() as session:
        updated_account = BaseOperations.update(session, Account, account_id, **data)
        if updated_account:
            return jsonify(updated_account.to_dict()), 200
        return jsonify({"error": "Account not found"}), 404


@account_bp.route('/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    """Delete an account"""
    with get_db_session() as session:
        if BaseOperations.delete(session, Account, account_id):
            return '', 204
        return jsonify({"error": "Account not found"}), 404
