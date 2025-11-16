"""
Updated customer routes using RiskAssessor for comprehensive analysis.
"""

from flask import Blueprint, request, jsonify
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.risk_assessor import RiskAssessor
from utils.data_helpers import (
    load_customers,
    load_behaviors,
    get_customer_behaviors,
    get_risk_summary_stats
)

customer_bp = Blueprint("customers", __name__)

# Initialize risk assessor (lazy loading)
_risk_assessor = None


def get_risk_assessor() -> RiskAssessor:
    """Get or create risk assessor instance."""
    global _risk_assessor
    if _risk_assessor is None:
        _risk_assessor = RiskAssessor()
    return _risk_assessor


@customer_bp.route("/<customer_id>/analysis", methods=["GET"])
def get_customer_analysis(customer_id: str):
    """
    Get comprehensive risk analysis for a customer.
    
    Args:
        customer_id: Customer ID to analyze
    
    Returns:
        JSON with full risk assessment
    """
    try:
        # Load data
        customers_df = load_customers()
        behaviors_df = load_behaviors()
        
        # Find customer
        customer_row = customers_df[customers_df["customer_id"] == customer_id]
        if customer_row.empty:
            return jsonify({"error": f"Customer {customer_id} not found"}), 404
        
        # Get customer data and behaviors
        customer_data = customer_row.iloc[0].to_dict()
        customer_behaviors = get_customer_behaviors(customer_id, behaviors_df)
        
        if customer_behaviors.empty:
            return jsonify({
                "error": f"No behavior data found for {customer_id}"
            }), 404
        
        # Get risk assessor
        assessor = get_risk_assessor()
        
        # Run comprehensive assessment
        assessment = assessor.assess_customer_risk(
            customer_data,
            customer_behaviors
        )
        
        return jsonify(assessment), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customer_bp.route("/", methods=["GET"])
def list_customers():
    """
    List all customers with optional filtering.
    
    Query params:
        tier: Filter by tier (Enterprise/Pro/Basic)
        limit: Max results (default 100)
    
    Returns:
        JSON with customer list
    """
    try:
        customers_df = load_customers()
        
        # Apply tier filter if provided
        tier = request.args.get("tier")
        if tier:
            customers_df = customers_df[customers_df["tier"] == tier]
        
        # Apply limit
        limit = int(request.args.get("limit", 100))
        customers_df = customers_df.head(limit)
        
        # Convert to list of dicts
        customers = customers_df.to_dict("records")
        
        return jsonify({
            "total": len(customers),
            "customers": customers
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customer_bp.route("/at-risk", methods=["GET"])
def get_at_risk_customers():
    """
    Get customers at risk of churning.
    
    Query params:
        min_risk: Minimum risk score (default 50)
        limit: Max results (default 20)
    
    Returns:
        JSON with at-risk customers sorted by risk score
    """
    try:
        # Load customers and behaviors
        customers_df = load_customers()
        behaviors_df = load_behaviors()
        
        # Get risk assessor
        assessor = get_risk_assessor()
        
        # Get min_risk threshold
        min_risk = float(request.args.get("min_risk", 50))
        limit = int(request.args.get("limit", 20))
        
        # Assess all customers
        print(f"Assessing {len(customers_df)} customers for risk...")
        assessments = assessor.assess_all_customers(customers_df, behaviors_df)
        
        # Filter by risk threshold
        at_risk = [
            a for a in assessments
            if a["churn_risk_score"] >= min_risk
        ]
        
        # Sort by risk descending and limit
        at_risk_sorted = sorted(
            at_risk,
            key=lambda x: x["churn_risk_score"],
            reverse=True
        )[:limit]
        
        # Get summary stats
        summary = get_risk_summary_stats(at_risk_sorted)
        
        return jsonify({
            "total_at_risk": len(at_risk),
            "returned": len(at_risk_sorted),
            "min_risk_threshold": min_risk,
            "summary": summary,
            "customers": at_risk_sorted
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customer_bp.route("/analyze-all", methods=["POST"])
def analyze_all_customers():
    """
    Run comprehensive risk assessment on all customers.
    
    Request body (optional):
        {
            "save_results": true,  // Save to data/analysis_all.json
            "min_risk": 0          // Include all customers
        }
    
    Returns:
        JSON with all assessments and summary stats
    """
    try:
        # Load data
        customers_df = load_customers()
        behaviors_df = load_behaviors()
        
        # Get risk assessor
        assessor = get_risk_assessor()
        
        # Run assessment on all customers
        print(f"Running comprehensive assessment on {len(customers_df)} customers...")
        assessments = assessor.assess_all_customers(customers_df, behaviors_df)
        
        # Apply min_risk filter if provided
        request_data = request.get_json() or {}
        min_risk = float(request_data.get("min_risk", 0))
        
        if min_risk > 0:
            filtered = [a for a in assessments if a["churn_risk_score"] >= min_risk]
        else:
            filtered = assessments
        
        # Get summary stats
        summary = get_risk_summary_stats(filtered)
        
        # Save results if requested
        if request_data.get("save_results", False):
            import json
            import pandas as pd
            
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data"
            )
            
            # Save JSON
            json_path = os.path.join(data_dir, "analysis_all.json")
            with open(json_path, "w") as f:
                json.dump(assessments, f, indent=2)
            
            # Save CSV
            csv_path = os.path.join(data_dir, "analysis_all.csv")
            df = pd.DataFrame(assessments)
            df.to_csv(csv_path, index=False)
            
            print(f"✓ Saved results to {json_path} and {csv_path}")
        
        return jsonify({
            "total_analyzed": len(assessments),
            "returned": len(filtered),
            "min_risk_filter": min_risk,
            "summary": summary,
            "assessments": filtered
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
