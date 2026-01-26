"""
Database connection and query execution utilities
Handles PostgreSQL connection via psycopg2
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from config import config


def get_db_connection():
    """
    Create and return a database connection

    Returns:
        connection: psycopg2 connection object with RealDictCursor

    Raises:
        Exception: If connection fails
    """
    try:
        connection = psycopg2.connect(
            config.DATABASE_URL,
            cursor_factory=RealDictCursor  # Returns rows as dictionaries
        )
        return connection
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a database query with automatic connection management

    Args:
        query (str): SQL query string with %s placeholders
        params (tuple/list): Query parameters to prevent SQL injection
        fetch_one (bool): Return single row
        fetch_all (bool): Return all rows

    Returns:
        Result of query (dict, list of dicts, or None)

    Example:
        # Fetch one user
        user = execute_query(
            "SELECT * FROM users WHERE userid = %s",
            ('student1',),
            fetch_one=True
        )

        # Fetch all profiles
        profiles = execute_query(
            "SELECT * FROM profile",
            fetch_all=True
        )

        # Insert application
        execute_query(
            "INSERT INTO application (profile_code, entry_number, status) VALUES (%s, %s, %s)",
            (1001, 'student1', 'Applied')
        )
    """
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Execute query with parameters (prevents SQL injection)
        cursor.execute(query, params or ())

        # Fetch results if requested
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = None

        # Commit changes for INSERT/UPDATE/DELETE
        connection.commit()

        return result

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"❌ Query execution error: {e}")
        print(f"Query: {query}")
        print(f"Params: {params}")
        raise

    finally:
        # Always close cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def test_connection():
    """Test database connection"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False