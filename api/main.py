from fastapi import FastAPI
from pydantic import BaseModel
import sys
sys.path.append("..")
from graph.ontology import OntologyGraph
from nlp.extractor import ClauseExtractor
from portfolio.mapper import Portfolio
import os

app = FastAPI()

class ImpactRequest(BaseModel):
    changed_concept: str
    old_clause: str
    new_clause: str
    old_risk_weight: float
    new_risk_weight: float

@app.post("/impact")
def get_impact(req: ImpactRequest):
    graph = OntologyGraph("bolt://localhost:7687", "neo4j", "test1234")
    impacted_rules = graph.get_impacted_rules(req.changed_concept)
    graph.close()

    extractor = ClauseExtractor(api=os.environ.get("ANTHROPIC_API_KEY"))
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