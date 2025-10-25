# tests/test_db.py
import pytest
from app.db import test_connection

def test_neo4j_connection():
    message = test_connection()
    assert message == "Neo4j connection successful", f"Connection failed: {message}"
