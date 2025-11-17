"""
Updated customer routes using preprocessed analysis data for fast demo performance.
Falls back to RiskAssessor for real-time analysis if preprocessed data not available.
"""

from flask import Blueprint, request, jsonify
import sys
import os
import json
import subprocess

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
_preprocessed_cache = None


def get_risk_assessor() -> RiskAssessor:
    """Get or create risk assessor instance."""
    global _risk_assessor
    if _risk_assessor is None:
        _risk_assessor = RiskAssessor()
    return _risk_assessor


def load_preprocessed_analysis():
    """Load preprocessed analysis from JSON file."""
    global _preprocessed_cache
    
    if _preprocessed_cache is not None:
        return _preprocessed_cache
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    preprocessed_path = os.path.join(data_dir, "preprocessed_analysis.json")
    
    if not os.path.exists(preprocessed_path):
        return None
    
    try:
        with open(preprocessed_path, "r") as f:
            _preprocessed_cache = json.load(f)
        return _preprocessed_cache
    except Exception as e:
        print(f"Error loading preprocessed analysis: {e}")
        return None


def find_preprocessed_customer(customer_id: str):
    """Find a customer's analysis in preprocessed data."""
    preprocessed = load_preprocessed_analysis()
    if not preprocessed:
        return None
    
    for analysis in preprocessed:
        if analysis.get("customer_id") == customer_id:
            return analysis
    
    return None


@customer_bp.route("/<customer_id>/analysis", methods=["GET"])
def get_customer_analysis(customer_id: str):
    """
    Get comprehensive risk analysis for a customer.
    
    First tries to load from preprocessed data (fast).
    Falls back to real-time analysis if not available.
    
    Args:
        customer_id: Customer ID to analyze
    
    Returns:
        JSON with full risk assessment
    """
    try:
        # Try to get from preprocessed data first (FAST)
        preprocessed_analysis = find_preprocessed_customer(customer_id)
        if preprocessed_analysis:
            return jsonify(preprocessed_analysis), 200
        
        # Fall back to real-time analysis (SLOW - uses AI API)
        print(f"⚠ Running real-time analysis for {customer_id} (preprocessed data not available)")
        
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
    
    Uses preprocessed analysis data for instant results.
    
    Query params:
        min_risk: Minimum risk score (default 50)
        limit: Max results (default 20)
    
    Returns:
        JSON with at-risk customers sorted by risk score
    """
    try:
        # Get min_risk threshold and limit
        min_risk = float(request.args.get("min_risk", 50))
        limit = int(request.args.get("limit", 20))
        
        # Try to load from preprocessed data first (FAST)
        preprocessed = load_preprocessed_analysis()
        
        if preprocessed:
            # Use preprocessed data (instant)
            at_risk = [
                a for a in preprocessed
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
                "customers": at_risk_sorted,
                "data_source": "preprocessed"
            }), 200
        
        # Fall back to real-time analysis (SLOW - uses AI API)
        print(f"⚠ Running real-time analysis (preprocessed data not available)")
        
        # Load customers and behaviors
        customers_df = load_customers()
        behaviors_df = load_behaviors()
        
        # Get risk assessor
        assessor = get_risk_assessor()
        
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
            "customers": at_risk_sorted,
            "data_source": "realtime"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customer_bp.route("/analyze-all", methods=["POST"])
def analyze_all_customers():
    """
    Run comprehensive risk assessment on all customers.
    
    Now triggers regeneration of preprocessed data instead of real-time analysis.
    
    Request body (optional):
        {
            "min_risk": 0          // Include all customers in response
        }
    
    Returns:
        JSON with all assessments and summary stats
    """
    try:
        request_data = request.get_json() or {}
        
        # Regenerate preprocessed data
        print("Regenerating preprocessed analysis data...")
        script_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
        script_path = os.path.join(script_dir, "generate_preprocessed_analysis.py")
        
        # Run the preprocessing script
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return jsonify({
                "error": "Failed to regenerate preprocessed data",
                "details": result.stderr
            }), 500
        
        # Reload the preprocessed data
        global _preprocessed_cache
        _preprocessed_cache = None  # Clear cache
        assessments = load_preprocessed_analysis()
        
        if not assessments:
            return jsonify({"error": "Failed to load preprocessed data"}), 500
        
        # Apply min_risk filter if provided
        min_risk = float(request_data.get("min_risk", 0))
        
        if min_risk > 0:
            filtered = [a for a in assessments if a["churn_risk_score"] >= min_risk]
        else:
            filtered = assessments
        
        # Get summary stats
        summary = get_risk_summary_stats(filtered)
        
        return jsonify({
            "total_analyzed": len(assessments),
            "returned": len(filtered),
            "min_risk_filter": min_risk,
            "summary": summary,
            "assessments": filtered,
            "data_source": "preprocessed"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customer_bp.route("/refresh-preprocessed-data", methods=["POST"])
def refresh_preprocessed_data():
    """
    Regenerate preprocessed analysis data.
    
    This endpoint triggers the generation of preprocessed_analysis.json
    which contains risk assessments for all customers without using AI API.
    
    Returns:
        JSON with success status and statistics
    """
    try:
        print("🔄 Refreshing preprocessed analysis data...")
        
        script_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
        script_path = os.path.join(script_dir, "generate_preprocessed_analysis.py")
        
        # Run the preprocessing script
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        
        if result.returncode != 0:
            return jsonify({
                "success": False,
                "error": "Failed to regenerate preprocessed data",
                "details": result.stderr
            }), 500
        
        # Clear cache and reload
        global _preprocessed_cache
        _preprocessed_cache = None
        assessments = load_preprocessed_analysis()
        
        if not assessments:
            return jsonify({
                "success": False,
                "error": "Failed to load refreshed data"
            }), 500
        
        # Calculate stats
        risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for analysis in assessments:
            risk_level = analysis.get("risk_level", "low")
            risk_counts[risk_level] += 1
        
        return jsonify({
            "success": True,
            "message": "Preprocessed analysis data refreshed successfully",
            "total_customers": len(assessments),
            "risk_distribution": risk_counts,
            "output": result.stdout
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
