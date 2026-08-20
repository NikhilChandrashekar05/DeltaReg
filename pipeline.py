import sys
import os
sys.path.append(".")
from ingestion.fetcher import RegulationsFetch
from nlp.parser import RegulatoryParse
from nlp.extractor import ClauseExtractor
from graph.ontology import OntologyGraph
from dotenv import load_dotenv
load_dotenv()
#import time

class DeltaRegPipeline:
    def __init__(self):
        self.fetcher = RegulationsFetch()
        self.parser = RegulatoryParse()
        self.extractor = ClauseExtractor(api=os.getenv("ANTHROPIC_API_KEY"))
        self.graph = OntologyGraph(
        os.getenv("NEO4J_URI"),
        os.getenv("NEO4J_USER"),
        os.getenv("NEO4J_PASSWORD")
)
    
    def process_document(self, doc: dict):
        print(f"\nProcessing: [{doc['agency']}] {doc['title']}")
        
        extraction = self.extractor.extract_concepts(doc['title'])
        
        for concept in extraction.get("concepts", []):
            self.graph.add_concept(concept["name"], concept["description"])
            print(f"   Concept: {concept['name']}")
        
        for dep in extraction.get("dependencies", []):
            self.graph.add_dependency(dep["from"], dep["to"])
            print(f"   Dependency: {dep['from']} -> {dep['to']}")
        
        self.graph.add_rule(
            rule_id=doc["id"],
            regulator=doc["agency"],
            effective_date=doc["postedDate"],
            text=doc["title"]
        )
        print(f"   Rule: {doc['id']}")
        
        for concept in extraction.get("concepts", []):
            self.graph.add_reference(doc["id"], concept["name"])

    def run(self, days_back: int = 30):
        #start = time.time()
        print("Fetching regulatory documents...")
        raw = self.fetcher.getdocs(daysprev=days_back)
        docs = self.fetcher.parse(raw)
        print(f"Found {len(docs)} documents\n")
        
        for doc in docs:
            try:
                self.process_document(doc)
            except Exception as e:
                print(f"  Failed: {e}")
                continue

        # elapsed = time.time() - start
        # print(f"\nPipeline complete. Processed {len(docs)} documents in {elapsed:.1f}s")
        # print(f"Average: {elapsed/len(docs):.1f}s per document")
        self.graph.close()
        print("\nPipeline complete.")
    
if __name__ == "__main__":
    pipeline = DeltaRegPipeline()
    pipeline.run(days_back=365)