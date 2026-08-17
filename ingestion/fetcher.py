import httpx, json
from datetime import datetime, timedelta

class RegulationsFetch:
    def __init__(self):
        self.url = "https://api.regulations.gov/v4/documents"
        self.agencies =["SEC", "CFTC", "TREAS", "FEDERALRESERVE"]


    #Hits the Fed Register API and asks for any new rules posted with certain days previously, and formats date
    def getdocs(self, daysprev = 1):
        sincetime = (datetime.now() - timedelta(daysprev)).strftime("%Y-%m-%d")
        param = {"filter[documentType]" : "Rule", "filter[postedDate][ge]": sincetime, "filter[agencyId]": ",".join(self.agencies), "sort": "-postedDate", "api_key": "tLLBrFko3AnYigrPbKcGp6FLOrBVrkNeUgjVKKIR"}

        response = httpx.get(self.url, params=param)
        return response.json()

#Takes the json and pulls the fields that are needed as shown: id, title, agency, date and type
    def parse(self, rawres):
        docs= []
        for doc in rawres.get("data", []):
            docs.append({"id": doc["id"], "title": doc["attributes"]["title"], "agency": doc["attributes"]["agencyId"], "postedDate": doc["attributes"]["postedDate"], "documentType": doc["attributes"]["documentType"]})
        return docs

if __name__ == "__main__":
    fetcher = RegulationsFetch()
    raw = fetcher.getdocs(daysprev=90)
    docs = fetcher.parse(raw)

    print(f"\n Found {len(docs)} regulatory documents in last 30 days:\n")
    for doc in docs:
        print(f"[{doc['agency']}] {doc['title']} | {doc['postedDate']}")