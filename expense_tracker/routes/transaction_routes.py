from flask import Blueprint, request, jsonify
from expense_tracker.models import Transaction
from expense_tracker.db.operations import BaseOperations
from expense_tracker.db.connection import get_db_session

transaction_bp = Blueprint('transaction', __name__)


@transaction_bp.route('/', methods=['GET'])
def get_all_transactions():
    """Retrieve all transactions"""
    with get_db_session() as session:
        transactions, total = BaseOperations.get_all(session, Transaction)
        return jsonify([transaction.to_dict() for transaction in transactions]), 200


@transaction_bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Retrieve a specific transaction"""
    with get_db_session() as session:
        transaction = BaseOperations.read(session, Transaction, transaction_id)
        if transaction:
            return jsonify(transaction.to_dict()), 200
        return jsonify({"error": "Transaction not found"}), 404


@transaction_bp.route('/', methods=['POST'])
def create_transaction():
    """Create a new transaction"""
    data = request.json
    with get_db_session() as session:
        new_transaction = BaseOperations.create(session, Transaction, **data)
        return jsonify(new_transaction.to_dict()), 201


@transaction_bp.route('/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """Update an existing transaction"""
    data = request.json
    with get_db_session() as session:
        updated_transaction = BaseOperations.update(session, Transaction, transaction_id, **data)
        if updated_transaction:
            return jsonify(updated_transaction.to_dict()), 200
        return jsonify({"error": "Transaction not found"}), 404


@transaction_bp.route('/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Delete a transaction"""
    with get_db_session() as session:
        if BaseOperations.delete(session, Transaction, transaction_id):
            return '', 204
        return jsonify({"error": "Transaction not found"}), 404
