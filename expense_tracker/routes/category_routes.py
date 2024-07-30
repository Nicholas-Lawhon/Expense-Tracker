from flask import Blueprint, request, jsonify
from expense_tracker.models import Category
from expense_tracker.db.operations import BaseOperations
from expense_tracker.db.connection import get_db_session

category_bp = Blueprint('category', __name__)


@category_bp.route('/', methods=['GET'])
def get_all_categories():
    """Retrieve all categories"""
    with get_db_session() as session:
        categories, total = BaseOperations.get_all(session, Category)
        return jsonify([category.to_dict() for category in categories]), 200


@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Retrieve a specific category"""
    with get_db_session() as session:
        category = BaseOperations.read(session, Category, category_id)
        if category:
            return jsonify(category.to_dict()), 200
        return jsonify({"error": "Category not found"}), 404


@category_bp.route('/', methods=['POST'])
def create_category():
    """Create a new category"""
    data = request.json
    with get_db_session() as session:
        new_category = BaseOperations.create(session, Category, **data)
        return jsonify(new_category.to_dict()), 201


@category_bp.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """Update an existing category"""
    data = request.json
    with get_db_session() as session:
        updated_category = BaseOperations.update(session, Category, category_id, **data)
        if updated_category:
            return jsonify(updated_category.to_dict()), 200
        return jsonify({"error": "Category not found"}), 404


@category_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category"""
    with get_db_session() as session:
        if BaseOperations.delete(session, Category, category_id):
            return '', 204
        return jsonify({"error": "Category not found"}), 404
