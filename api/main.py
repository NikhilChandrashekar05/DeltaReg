from fastapi import FastAPI
from pydantic import BaseModel
import sys
sys.path.append("..")
from graph.ontology import OntologyGraph
from nlp.extractor import ClauseExtractor
from portfolio.mapper import Portfolio
import os
from fastapi.middleware.cors import CORSMiddleware
from pipeline import DeltaRegPipeline
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)
class ImpactRequest(BaseModel):
    changed_concept: str
    old_clause: str
    new_clause: str
    old_risk_weight: float
    new_risk_weight: float

@app.post("/impact")
def get_impact(req: ImpactRequest):
    graph = OntologyGraph(
    os.getenv("NEO4J_URI"),
    os.getenv("NEO4J_USER"),
    os.getenv("NEO4J_PASSWORD")
    )
    impacted_rules = graph.get_impacted_rules(req.changed_concept)
    graph.close()

    extractor = ClauseExtractor(api=os.getenv("ANTHROPIC_API_KEY"))
    extraction = extractor.extract(req.old_clause, req.new_clause)

    mapper = Portfolio()
    affected_instruments = extraction["affected_instruments"]
    positions = mapper.get_impacted_positions(affected_instruments)

    results = []
    for p in positions:
        delta = mapper.calc_capitaldelta(p, req.old_risk_weight, req.new_risk_weight)
        results.append(delta)

    return {
        "changed_concept": req.changed_concept,
        "impacted_rules": impacted_rules,
        "extraction": extraction,
        "impacted_positions": results,
        "total_additional_capital": sum(r["additional_capital_required"] for r in results)
    }

@app.post("/run-pipeline")
def run_pipeline():
    pipeline = DeltaRegPipeline()
    pipeline.run(days_back=30)
    return {"status": "complete"}

@app.get("/graph-data")
def get_graph_data():
    graph = OntologyGraph(
    os.getenv("NEO4J_URI"),
    os.getenv("NEO4J_USER"),
    os.getenv("NEO4J_PASSWORD")
    )
    query = """
    MATCH (r:Rule)-[:REFERENCES]->(c:Concept)
    RETURN r.id AS rule_id, r.regulator AS regulator,
           collect(c.name) AS concepts
    ORDER BY r.regulator
    """
    with graph.driver.session() as session:
        result = session.run(query)
        rules = [dict(record) for record in result]
    
    query2 = """
    MATCH (a:Concept)-[:DEPENDS_ON]->(b:Concept)
    RETURN a.name AS from_concept, b.name AS to_concept
    """
    with graph.driver.session() as session:
        result = session.run(query2)
        deps = [dict(record) for record in result]
    
    graph.close()
    return {"rules": rules, "dependencies": deps}