"""
Batch analysis script - Analyzes all customers using RiskAssessor.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from models.risk_assessor import RiskAssessor
from utils.data_helpers import load_customers, load_behaviors


def main() -> None:
    """Run batch analysis on all customers."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "data")
    out_json = os.path.join(data_dir, "analysis_all.json")
    out_csv = os.path.join(data_dir, "analysis_all.csv")

    print("\n" + "="*60)
    print("Batch Customer Risk Analysis")
    print("="*60 + "\n")

    # Load data
    print("Loading customer data...")
    customers_df = load_customers()
    behaviors_df = load_behaviors()
    print(f"✓ Loaded {len(customers_df)} customers\n")

    # Initialize risk assessor
    print("Initializing risk assessor...")
    assessor = RiskAssessor()
    print("✓ Ready\n")

    # Analyze all customers
    print(f"Analyzing {len(customers_df)} customers...")
    results = assessor.assess_all_customers(customers_df, behaviors_df)

    # Save JSON
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Saved JSON: {out_json}")

    # Save CSV with flattened fields
    csv_rows = []
    for r in results:
        csv_rows.append({
            "customer_id": r["customer_id"],
            "company_name": r["company_name"],
            "tier": r.get("tier", ""),
            "monthly_value": r.get("monthly_value", 0),
            "churn_risk_score": r["churn_risk_score"],
            "risk_level": r["risk_level"],
            "intervention_priority": r["intervention_priority"],
            "predicted_churn_date": r.get("predicted_churn_date", ""),
            "estimated_revenue_at_risk": r["estimated_revenue_at_risk"],
            "confidence_level": r["confidence_level"],
        })
    pd.DataFrame(csv_rows).to_csv(out_csv, index=False)
    print(f"✓ Saved CSV: {out_csv}")

    print("\n" + "="*60)
    print("✅ Batch analysis complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
