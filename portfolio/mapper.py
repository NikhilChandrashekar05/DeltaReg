import json, psycopg2

#Opens connection to the PostgreSQL DB and creates cursor to run SQL queries
class Portfolio:
    def __init__(self):
        self.conn = psycopg2.connect(host="localhost", port=5432, database="deltareg", user="deltareg", password="deltareg123")
        self.cursor = self.conn.cursor()

    #Creates positions table if not there, each row would be 1 trading position a bank hold.
    def createtable(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS positions (
                            position_id      SERIAL PRIMARY KEY,
                            instrument_type  VARCHAR(50),
                            jurisdiction     VARCHAR(10),
                            notional         DECIMAL(20,2),
                            business_line    VARCHAR(100),
                            current_rwa      DECIMAL(20,2),
                            current_capital  DECIMAL(20,2))""")
        self.conn.commit()

    #Seeds fake position data for testing
    def positions(self):
        position = [
            ("equity_derivative", "US", 50000000, "rates_trading", 4000000, 320000),
            ("sovereign_bond", "EU", 120000000, "fixed_income", 6000000, 480000),
            ("uncleared_swap", "US", 80000000, "rates_trading", 8000000, 640000),
            ("equity_derivative", "EU", 30000000, "prime_brokerage", 2400000, 192000),
            ("mortgage_backed_security", "US", 200000000, "structured_products", 16000000, 1280000),
            ("corporate_bond", "US", 60000000, "fixed_income", 4800000, 384000),
            ("sovereign_bond", "US", 90000000, "rates_trading", 4500000, 360000),
            ("uncleared_swap", "EU", 45000000, "prime_brokerage", 4500000, 360000)
        ]
        self.cursor.executemany("""
            INSERT INTO positions 
            (instrument_type, jurisdiction, notional, business_line, current_rwa, current_capital)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, position)
        self.conn.commit()

    def get_impacted_positions(self, affected_instruments: list) -> list:
        self.cursor.execute(""" SELECT 
                position_id,
                instrument_type,
                jurisdiction,
                notional,
                business_line,
                current_rwa,
                current_capital
            FROM positions
            WHERE instrument_type = ANY(%s) """, (affected_instruments,))
        rows = self.cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                "position_id": row[0],
                "instrument_type": row[1],
                "jurisdiction": row[2],
                "notional": row[3],
                "business_line": row[4],
                "current_rwa": row[5],
                "current_capital": row[6]
            })
        return results
    
    def calc_capitaldelta(self,position: dict, old_risk: float, new_risk:float):
        oldRWA = float(position["notional"]) * old_risk
        newRWA = float(position["notional"]) * new_risk
        diff = newRWA - oldRWA
        capital_delta = diff * 0.08
        return  { "position_id": position["position_id"], "instrument_type": position["instrument_type"], "business_line": position["business_line"], 
            "notional": float(position["notional"]),
            "old_rwa": oldRWA, "new_rwa": newRWA, "rwa_delta": diff, "additional_capital_required": capital_delta,
            "materiality": "high" if capital_delta > 1000000 else "medium"}

if __name__ == "__main__":
    mapper = Portfolio()
    mapper.createtable()
    mapper.positions()

    affected = ["equity_derivative", "uncleared_swap"]
    pos = mapper.get_impacted_positions(affected)

    print(f"\nFound {len(pos)} affected positions\n")
    for p in pos:
        delta = mapper.calc_capitaldelta(p, old_risk=0.08, new_risk=0.10)
        print(f"  [{delta['business_line']}] {delta['instrument_type']}")
        print(f"  Notional: ${delta['notional']:,.0f}")
        print(f"  Additional capital required: ${delta['additional_capital_required']:,.0f}")
        print(f"  Materiality: {delta['materiality']}\n")
    
    mapper.cursor.close()
    mapper.conn.close()
