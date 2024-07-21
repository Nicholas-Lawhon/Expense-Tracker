import os
from dotenv import load_dotenv

"""
This module handles configuration settings for the database connection.

It uses environment variables to set up the database path, allowing for
flexible configuration across different environments.
"""

# Load environment variables from .env file
load_dotenv()

# Get the directory of the current file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the database file, using an environment variable
DB_PATH = os.getenv('DB_PATH', os.path.join(CURRENT_DIR, "database.db"))
DB_URL = f"sqlite:///{DB_PATH}"

"""
DB_PATH: The path to the SQLite database file. If not specified in the environment,
         it defaults to a file named 'database.db' in the current directory.
DB_URL: The SQLAlchemy connection string for the database.
"""