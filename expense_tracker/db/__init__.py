from .connection import get_db_engine, create_tables, drop_tables
from .models import Transaction

"""
This module initializes the database package.

It imports and makes available key functions and classes from the database package:
- get_db_engine and create_tables from the connection module
- Transaction model from the models module

This allows users of the package to import these items directly from the db package,
rather than having to import from individual modules.
"""