"""
Data helper utilities for loading and processing customer data.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import pandas as pd


def get_data_dir() -> str:
    """Get the data directory path."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "data")


def load_customers() -> pd.DataFrame:
    """
    Load customers CSV file.
    
    Returns:
        DataFrame with customer data
    
    Raises:
        FileNotFoundError: If customers.csv doesn't exist
    """
    data_dir = get_data_dir()
    customers_path = os.path.join(data_dir, "customers.csv")
    
    if not os.path.exists(customers_path):
        raise FileNotFoundError(
            f"customers.csv not found at {customers_path}. "
            "Run scripts/generate_sample_data.py first."
        )
    
    return pd.read_csv(customers_path)


def load_behaviors() -> pd.DataFrame:
    """
    Load behavior events CSV file.
    
    Returns:
        DataFrame with behavior events, event_date converted to datetime
    
    Raises:
        FileNotFoundError: If behavior_events.csv doesn't exist
    """
    data_dir = get_data_dir()
    behaviors_path = os.path.join(data_dir, "behavior_events.csv")
    
    if not os.path.exists(behaviors_path):
        raise FileNotFoundError(
            f"behavior_events.csv not found at {behaviors_path}. "
            "Run scripts/generate_sample_data.py first."
        )
    
    df = pd.read_csv(behaviors_path)
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    return df


def load_churned_customers() -> pd.DataFrame:
    """
    Load churned customers CSV file.
    
    Returns:
        DataFrame with churned customer data
    
    Raises:
        FileNotFoundError: If churned_customers.csv doesn't exist
    """
    data_dir = get_data_dir()
    churned_path = os.path.join(data_dir, "churned_customers.csv")
    
    if not os.path.exists(churned_path):
        raise FileNotFoundError(
            f"churned_customers.csv not found at {churned_path}. "
            "Run scripts/generate_sample_data.py first."
        )
    
    return pd.read_csv(churned_path)


def get_customer_behaviors(
    customer_id: str,
    behaviors_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Filter behaviors for a specific customer.
    
    Args:
        customer_id: Customer ID to filter
        behaviors_df: Full behaviors DataFrame
    
    Returns:
        Filtered DataFrame with only this customer's events
    """
    return behaviors_df[behaviors_df["customer_id"] == customer_id].copy()


def format_currency(amount: float) -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Dollar amount
    
    Returns:
        Formatted string like "$1,234.56"
    """
    return f"${amount:,.2f}"


def calculate_revenue_at_risk(customers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate total revenue at risk by risk level.
    
    Args:
        customers: List of customer risk assessments
    
    Returns:
        Dict with revenue breakdown by risk level
    """
    breakdown = {
        "critical": 0.0,
        "high": 0.0,
        "medium": 0.0,
        "low": 0.0,
        "total": 0.0,
    }
    
    for cust in customers:
        risk_level = cust.get("risk_level", "low")
        revenue = float(cust.get("estimated_revenue_at_risk", 0))
        
        if risk_level in breakdown:
            breakdown[risk_level] += revenue
        breakdown["total"] += revenue
    
    return breakdown


def get_risk_summary_stats(assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate summary statistics from risk assessments.
    
    Args:
        assessments: List of customer risk assessments
    
    Returns:
        Dict with summary stats
    """
    if not assessments:
        return {
            "total_customers": 0,
            "risk_breakdown": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "average_risk_score": 0.0,
            "total_revenue_at_risk": 0.0,
            "customers_needing_intervention": 0,
        }
    
    # Count by risk level
    risk_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    total_score = 0.0
    total_revenue = 0.0
    needing_intervention = 0
    
    for assessment in assessments:
        risk_level = assessment.get("risk_level", "low")
        if risk_level in risk_counts:
            risk_counts[risk_level] += 1
        
        score = float(assessment.get("churn_risk_score", 0))
        total_score += score
        
        revenue = float(assessment.get("estimated_revenue_at_risk", 0))
        total_revenue += revenue
        
        # High/critical need intervention
        if risk_level in ["high", "critical"]:
            needing_intervention += 1
    
    avg_score = total_score / len(assessments) if assessments else 0.0
    
    return {
        "total_customers": len(assessments),
        "risk_breakdown": risk_counts,
        "average_risk_score": round(avg_score, 2),
        "total_revenue_at_risk": round(total_revenue, 2),
        "customers_needing_intervention": needing_intervention,
    }


# Test
if __name__ == "__main__":
    """Test data helpers."""
    print("\nTesting data helpers...\n")
    
    try:
        customers = load_customers()
        print(f"✓ Loaded {len(customers)} customers")
        
        behaviors = load_behaviors()
        print(f"✓ Loaded {len(behaviors)} behavior events")
        
        # Test get_customer_behaviors
        test_id = "CUST001"
        cust_behaviors = get_customer_behaviors(test_id, behaviors)
        print(f"✓ Found {len(cust_behaviors)} events for {test_id}")
        
        # Test format_currency
        formatted = format_currency(1234.56)
        print(f"✓ Currency formatting: {formatted}")
        
        print("\n✅ All data helper tests passed!\n")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("   Run scripts/generate_sample_data.py first.\n")
