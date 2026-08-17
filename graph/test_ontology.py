from ontology import OntologyGragh

graph = OntologyGragh(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="test1234"
)

results = graph.get_impacted("CET1")

print(f"\nRules impacted by a change to CET1:\n")
for each in results:
    print(f"  Rule: {each['rule_id']} | Regulator: {each['regulator']} | Via: {each['downstream_concept']}")

graph.close()
