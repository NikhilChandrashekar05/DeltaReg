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

    def add_concept(self, name: str, description: str):
        query = """
        MERGE (c:Concept {name: $name})
        SET c.description = $description
        """
        with self.driver.session() as session:
            session.run(query, name=name, description=description)

    def add_rule(self, rule_id: str, regulator: str, effective_date: str, text: str):
        query = """
        MERGE (r:Rule {id: $rule_id})
        SET r.regulator = $regulator,
            r.effective_date = $effective_date,
            r.text = $text
        """
        with self.driver.session() as session:
            session.run(query, rule_id=rule_id, regulator=regulator,
                       effective_date=effective_date, text=text)

    def add_dependency(self, from_concept: str, to_concept: str):
        query = """
        MATCH (a:Concept {name: $from_concept})
        MATCH (b:Concept {name: $to_concept})
        MERGE (a)-[:DEPENDS_ON]->(b)
        """
        with self.driver.session() as session:
            session.run(query, from_concept=from_concept, to_concept=to_concept)

    def add_reference(self, rule_id: str, concept_name: str):
        query = """
        MATCH (r:Rule {id: $rule_id})
        MATCH (c:Concept {name: $concept_name})
        MERGE (r)-[:REFERENCES]->(c)
        """
        with self.driver.session() as session:
            session.run(query, rule_id=rule_id, concept_name=concept_name)