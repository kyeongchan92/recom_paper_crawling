from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()


class Neo4jClient:
    def __init__(self):
        self._driver = GraphDatabase.driver(
            uri=os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
        )

    def close(self):
        self._driver.close()

    def add_paper(self, title, authors):
        """주어진 논문을 Neo4j에 추가 (중복 방지)"""
        with self._driver.session() as session:
            result = session.execute_write(
                self._create_paper_if_not_exists, title, authors
            )
            return result

    def add_reference(self, citing_title, referenced_title):
        """논문 간 'REFERENCES' 관계 추가 (중복 방지)"""
        with self._driver.session() as session:
            session.execute_write(
                self._create_reference_if_not_exists, citing_title, referenced_title
            )

    @staticmethod
    def _create_paper_if_not_exists(tx, title, authors):
        query = """
        MERGE (p:Paper {title: $title})
        ON CREATE SET p.authors = $authors
        RETURN p.title, p.authors
        """
        result = tx.run(query, title=title, authors=authors)
        record = result.single()
        print(f"record : {record}")
        if record:
            return {"title": record["p.title"], "authors": record["p.authors"]}
        return None

    @staticmethod
    def _create_reference_if_not_exists(tx, citing_title, referenced_title):
        query = """
        MATCH (citing:Paper {title: $citing_title})
        MATCH (referenced:Paper {title: $referenced_title})
        MERGE (citing)-[:REFERENCES]->(referenced)
        """
        tx.run(query, citing_title=citing_title, referenced_title=referenced_title)


# 🔹 Neo4jClient 인스턴스 생성
neo4j_client = Neo4jClient()
