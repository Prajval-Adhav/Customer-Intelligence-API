from neo4j import GraphDatabase
import os

driver = GraphDatabase.driver(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")))

def search_nodes(label: str, name: str):
    query = f"""
    MATCH (n:{label})
    WHERE toLower(n.name) CONTAINS toLower($name)
    RETURN n
    """
    with driver.session() as session:
        results = session.run(query, name=name)
        return [record["n"] for record in results]