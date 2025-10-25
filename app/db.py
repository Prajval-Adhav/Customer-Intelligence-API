# db.py
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Initialize Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def test_connection():
    """Simple function to test Neo4j connectivity"""
    try:
        with driver.session() as session:
            result = session.run("RETURN 'Neo4j connection successful' AS message")
            message = result.single()["message"]
            return message
    except Exception as e:
        return str(e)
