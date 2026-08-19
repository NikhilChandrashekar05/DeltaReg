from neo4j import GraphDatabase

class OntologyGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri,auth=(user,password))

    def close(self):
        self.driver.close()

    def get_impacted_rules(self, changedconcepts):
        query="""
        MATCH (changed:Concept {name: $concept})<-[:DEPENDS_ON*0..5]-(downstream:Concept)<-[:REFERENCES]-(rule:Rule)
        RETURN DISTINCT
            changed.name AS changed_concept,
            downstream.name AS downstream_concept,
            rule.id AS rule_id,
            rule.regulator AS regulator
        """
        with self.driver.session() as session:
            result = session.run(query, concept= changedconcepts)
            return [dict(record) for record in result]