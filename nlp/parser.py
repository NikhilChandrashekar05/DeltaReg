import pymupdf  #Python library to read PDFS
from sentence_transformers import SentenceTransformer #For convertion to vector for embeddings
from sklearn.metrics.pairwise import cosine_similarity

#Downloads the embedding model 
class RegulatoryParse():
    def __init__(self):
        self.model = SentenceTransformer('all-mpnet-base-v2')

    #opens pdf loops through all pages pulls text and concatenates into 1 big string
    def extract_text(self, pdfpath: str) -> str:
        doc = pymupdf.open(pdfpath)
        fulltext = ""
        for page in doc:
            fulltext += page.get_text()
        return fulltext

    #Splits the full text into individual clauses, filter anything under 50 characters becuz those re just un needed things, like whitespace, page#
    def split_clause(self, text: str) -> list:
        clauses = []
        for line in text.split("\n"):
            temp = line.strip()
            if len(temp) > 50:
                clauses.append(temp)
        return clauses
    
    #Passes the list of clauses into the model and gets back a list of vectors, 1 vector per clause
    def embed(self, clauses: list) -> list:
        return self.model.encode(clauses)
    
    def semantic_diff(self, old_clause, new_clause) -> list:
        oldembedd = self.embed(old_clause)
        newembedd = self.embed(new_clause)

        changed = []
        for i, new_embedd in enumerate(newembedd):
            score = cosine_similarity([new_embedd], oldembedd)[0]
            best = max(score)
            if best < 0.98:
                changed.append({"new_clause": new_clause[i], "similarity_score": round(float(best), 4), "status": "changed" if best > 0.70 else "new"})
        return changed


if __name__ == "__main__":
    parse = RegulatoryParse()

    old = ["Banks must hold 8% capital against risk-weighted assets", 
                "Instiutions must report quarterly to the Federal Reserve", 
                "Leverage ratio must not exceed 3%"]
        
    new = ["Banks must hold 10% capital against risk-weighted assets", 
                "Instiutions must report quarterly to the Federal Reserve",
                "All derivative contracts must be cleared through a CCP"]
        
    changes = parse.semantic_diff(old, new)

    print(f"\n Found {len(changes)} changed statement clauses:\n")
    for c in changes:
        print(f"{c['status'].upper()} score: {c['similarity_score']}")
        print(f"{c['new_clause']}\n")