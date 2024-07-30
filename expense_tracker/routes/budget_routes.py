from flask import Blueprint, request, jsonify
from expense_tracker.models import Budget
from expense_tracker.db.operations import BaseOperations
from expense_tracker.db.connection import get_db_session

budget_bp = Blueprint('budget', __name__)


@budget_bp.route('/', methods=['GET'])
def get_all_budgets():
    """Retrieve all budgets"""
    with get_db_session() as session:
        budgets, total = BaseOperations.get_all(session, Budget)
        return jsonify([budget.to_dict() for budget in budgets]), 200


@budget_bp.route('/<int:budget_id>', methods=['GET'])
def get_budget(budget_id):
    """Retrieve a specific budget"""
    with get_db_session() as session:
        budget = BaseOperations.read(session, Budget, budget_id)
        if budget:
            return jsonify(budget.to_dict()), 200
        return jsonify({"error": "Budget not found"}), 404


@budget_bp.route('/', methods=['POST'])
def create_budget():
    """Create a new budget"""
    data = request.json
    with get_db_session() as session:
        new_budget = BaseOperations.create(session, Budget, **data)
        return jsonify(new_budget.to_dict()), 201


@budget_bp.route('/<int:budget_id>', methods=['PUT'])
def update_budget(budget_id):
    """Update an existing budget"""
    data = request.json
    with get_db_session() as session:
        updated_budget = BaseOperations.update(session, Budget, budget_id, **data)
        if updated_budget:
            return jsonify(updated_budget.to_dict()), 200
        return jsonify({"error": "Budget not found"}), 404


@budget_bp.route('/<int:budget_id>', methods=['DELETE'])
def delete_budget(budget_id):
    """Delete a budget"""
    with get_db_session() as session:
        if BaseOperations.delete(session, Budget, budget_id):
            return '', 204
        return jsonify({"error": "Budget not found"}), 404
