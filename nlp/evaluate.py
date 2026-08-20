import sys
sys.path.append("..")
from nlp.parser import RegulatoryParse
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
from sklearn.metrics.pairwise import cosine_similarity

VALIDATION_SET = [
    ("Banks must hold 8% capital against risk-weighted assets",
     "Banks must hold 10% capital against risk-weighted assets", 1),

    ("Institutions must report quarterly to the Federal Reserve",
     "Institutions must report quarterly to the Federal Reserve", 0),

    ("Leverage ratio must not exceed 3%",
     "Leverage ratio must not exceed 5%", 1),

    ("Swap dealers must post initial margin of 4% of notional",
     "Swap dealers must post initial margin of 4% of notional value", 0),

    ("All derivative contracts must be cleared through a CCP",
     "All derivative contracts must be cleared through a central counterparty", 0),

    ("Firms shall maintain records for 5 years",
     "Firms shall maintain records for 7 years", 1),

    ("The minimum liquidity coverage ratio is 100%",
     "The minimum liquidity coverage ratio is 100 percent", 0),

    ("Reporting entities must file Form X-17A-5 annually",
     "Reporting entities must file Form X-17A-5 quarterly", 1),

    ("Capital buffers apply to global systemically important banks",
     "Capital buffers apply to G-SIBs", 0),

    ("Position limits are set at 25000 contracts",
     "Position limits are set at 50000 contracts", 1),

    ("Institutions shall disclose counterparty exposures",
     "Institutions shall disclose all counterparty exposures", 0),

    ("Trading book positions require daily mark-to-market",
     "Trading book positions require intraday mark-to-market", 1),

    ("Eligible collateral includes sovereign bonds",
     "Eligible collateral includes government bonds", 0),

    ("The risk weight for corporate exposures is 100%",
     "The risk weight for corporate exposures is 150%", 1),

    ("Firms must appoint a chief compliance officer",
     "Firms must appoint a chief compliance officer", 0),

    ("Margin requirements apply to uncleared swaps",
     "Margin requirements apply to both cleared and uncleared swaps", 1),

    ("Banks shall submit stress test results by March 31",
     "Banks shall submit stress test results by June 30", 1),

    ("Disclosure must occur within 4 business days",
     "Disclosure must occur within four business days", 0),

    ("Tier 1 capital consists of common equity and retained earnings",
     "Tier 1 capital consists of common equity, retained earnings, and disclosed reserves", 1),

    ("Swap execution facilities must register with the Commission",
     "Swap execution facilities must register with the CFTC", 0)
]

HELDOUT_SET = [
    ("Firms must retain transaction records for a minimum of three years",
     "Firms must retain transaction records for a minimum of six years", 1),

    ("Clearing members shall post variation margin daily",
     "Clearing members shall post variation margin on a daily basis", 0),

    ("The countercyclical capital buffer is set at 0%",
     "The countercyclical capital buffer is set at 2.5%", 1),

    ("Registrants must disclose material weaknesses in internal controls",
     "Registrants must disclose material weaknesses in internal control over financial reporting", 0),

    ("This rule applies to entities with assets exceeding $50 billion",
     "This rule applies to entities with assets exceeding $250 billion", 1),

    ("Broker-dealers shall maintain net capital of at least $250,000",
     "Broker-dealers shall maintain minimum net capital of $250,000", 0),

    ("Reporting is required on a T+2 basis",
     "Reporting is required on a T+1 basis", 1),

    ("Foreign private issuers are exempt from this requirement",
     "Foreign private issuers are subject to this requirement", 1),

    ("Institutions shall conduct annual stress testing",
     "Institutions shall conduct stress testing on an annual basis", 0),

    ("The exemption expires on December 31, 2026",
     "The exemption expires on December 31, 2028", 1),

    ("Swap dealers must verify counterparty eligibility prior to execution",
     "Swap dealers must verify counterparty eligibility before executing a transaction", 0),

    ("Applicable to national banks and federal savings associations",
     "Applicable to national banks, federal savings associations, and state member banks", 1),

    ("Firms shall file reports electronically through EDGAR",
     "Firms shall submit reports electronically via the EDGAR system", 0),

    ("The haircut applied to sovereign debt collateral is 2%",
     "The haircut applied to sovereign debt collateral is 8%", 1),

    ("Compliance officers must be independent of the trading desk",
     "Compliance officers must maintain independence from the trading desk", 0),

    ("This provision takes effect immediately upon publication",
     "This provision takes effect 180 days after publication", 1),

    ("Covered funds may not engage in proprietary trading",
     "Covered funds may engage in proprietary trading subject to Commission approval", 1),

    ("Notification must be provided to the Commission in writing",
     "Written notification must be provided to the Commission", 0),

    ("The threshold for aggregate position reporting is 25 contracts",
     "The threshold for aggregate position reporting is 250 contracts", 1),

    ("Auditors shall rotate every five years",
     "Lead audit partners shall rotate every five years", 0)
]


def evaluate(dataset, threshold=0.92):
    parser = RegulatoryParse()

    y_true = []
    y_pred = []
    scores = []

    for old, new, label in dataset:
        old_emb = parser.embed([old])
        new_emb = parser.embed([new])
        score = cosine_similarity(new_emb, old_emb)[0][0]

        prediction = 1 if score < threshold else 0

        y_true.append(label)
        y_pred.append(prediction)
        scores.append(score)

    accuracy = sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true)

    return {
        "threshold": threshold,
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 3),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 3),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 3),
        "accuracy": round(accuracy, 3),
        "y_true": y_true,
        "y_pred": y_pred,
        "scores": scores
    }


if __name__ == "__main__":
    print("\n=== Threshold tuning on validation set ===\n")
    print(f"{'Threshold':<12}{'Precision':<12}{'Recall':<12}{'F1':<12}")

    best_f1 = 0
    best_threshold = 0
    for t in [0.90, 0.92, 0.94, 0.96, 0.98, 0.985, 0.99, 0.995]:
        r = evaluate(VALIDATION_SET, threshold=t)
        print(f"{t:<12}{r['precision']:<12}{r['recall']:<12}{r['f1']:<12}")
        if r['f1'] > best_f1:
            best_f1 = r['f1']
            best_threshold = t

    print(f"\nSelected threshold: {best_threshold} (validation F1 = {best_f1})")

    print("\n=== Held-out test set evaluation ===\n")
    held = evaluate(HELDOUT_SET, threshold=best_threshold)

    print(f"Threshold: {held['threshold']}")
    print(f"Precision: {held['precision']}")
    print(f"Recall:    {held['recall']}")
    print(f"F1 Score:  {held['f1']}")
    print(f"Accuracy:  {held['accuracy']}")

    tn, fp, fn, tp = confusion_matrix(held['y_true'], held['y_pred']).ravel()
    print(f"\nConfusion Matrix:")
    print(f"  True Positives:  {tp}  (correctly flagged as changed)")
    print(f"  True Negatives:  {tn}  (correctly flagged as unchanged)")
    print(f"  False Positives: {fp}  (flagged as changed, actually unchanged)")
    print(f"  False Negatives: {fn}  (missed real changes)")