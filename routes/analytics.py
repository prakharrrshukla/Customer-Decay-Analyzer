from __future__ import annotations

import os
from typing import Any, Dict

import pandas as pd
from flask import Blueprint, jsonify, request


analytics_bp = Blueprint("analytics", __name__)


def _data_dir() -> str:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "data")


@analytics_bp.route("/stats", methods=["GET"])
def stats():
    """
    Dashboard stats based on batch analysis results.

    Query params:
    - threshold: int (default 60) for at-risk count
    """
    threshold = 60
    try:
        threshold = int(request.args.get("threshold", "60"))
    except ValueError:
        pass

    data_dir = _data_dir()
    customers_csv = os.path.join(data_dir, "customers.csv")
    analysis_csv = os.path.join(data_dir, "analysis_all.csv")

    total_customers = 0
    try:
        if os.path.exists(customers_csv):
            total_customers = len(pd.read_csv(customers_csv))
    except Exception:
        total_customers = 0

    if not os.path.exists(analysis_csv):
        # Return minimal stats if analysis not present
        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "total_customers": total_customers,
                        "active_customers": total_customers,
                        "at_risk_count": None,
                        "critical_count": None,
                        "avg_risk_score": None,
                        "churn_rate_30d": None,
                        "intervention_success_rate": None,
                    },
                }
            ),
            200,
        )

    try:
        df = pd.read_csv(analysis_csv)
        at_risk = int((df["churn_risk_score"] >= threshold).sum())
        critical = int((df["churn_risk_score"] >= 81).sum())
        avg_risk = float(df["churn_risk_score"].mean()) if not df.empty else 0.0
        data = {
            "total_customers": total_customers or len(df),
            "active_customers": total_customers or len(df),
            "at_risk_count": at_risk,
            "critical_count": critical,
            "avg_risk_score": round(avg_risk, 2),
            "churn_rate_30d": None,
            "intervention_success_rate": None,
        }
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:  # noqa: BLE001
        return jsonify({"success": False, "error": "analysis_load_error", "message": str(e)}), 500
