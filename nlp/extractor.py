import anthropic, json

class ClauseExtractor:
    def __init__(self, api):
        self.client = anthropic.Anthropic(api_key=api)

    def extract(self, old, new) -> dict:
        prompt = f"""You are analyzing two versions of a financial regualtion clause. 
                    OLD Version: {old}
                    NEW Version: {new}
                    Return only correct JSON with these field:
                    {{
                        "change_type": "capital_requirement|reporting_obligation|product_restriction|definition_change|timeline_change|threshold_change",
                        "what_changed": "one sentence describing the specific change",
                        "direction": "more_restrictive|less_restrictive|neutral",
                        "affected_instruments": ["list of instrument types affected"],
                        "effective_date": "YYYY-MM-DD or null",
                        "magnitude": "high|medium|low"
                    }}
                    """
        res = self.client.messages.create(model = "claude-sonnet-4-6", max_tokens= 1000, messages=[{"role": "user", "content": prompt}])
        raw = res.content[0].text
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
                

if __name__ == "__main__":
    import os
    extract_claude = ClauseExtractor(os.environ.get("ANTHROPIC_API_KEY"))

    res = extract_claude.extract(old= "Banks must hold 8% capital against risk-weighted assets", new= "Banks must hold 10% capital against risk-weighted assets")
    print(json.dumps(res, indent=2))