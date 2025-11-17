"""
Generate preprocessed risk analysis for all customers WITHOUT calling Gemini API.

This script creates realistic risk assessments based on behavioral patterns,
avoiding API rate limits during demos. All 100 customers get pre-calculated
risk scores, decay signals, and recommendations.

Output: data/preprocessed_analysis.json
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta, date
from typing import Dict, List, Any

import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import message templates
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"))
from sample_concerns_interventions import (
    get_concern_for_signals,
    get_intervention_for_risk,
    DECAY_SIGNALS
)

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def load_data():
    """Load customers, behaviors, and churned customers data."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    customers_df = pd.read_csv(os.path.join(data_dir, "customers.csv"))
    behaviors_df = pd.read_csv(os.path.join(data_dir, "behavior_events.csv"))
    churned_df = pd.read_csv(os.path.join(data_dir, "churned_customers.csv"))
    
    return customers_df, behaviors_df, churned_df


def calculate_behavioral_metrics(customer_id: str, behaviors_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate behavioral metrics from event data.
    
    Args:
        customer_id: Customer ID
        behaviors_df: DataFrame of behavior events
        
    Returns:
        Dict with calculated metrics
    """
    # Filter events for this customer
    customer_events = behaviors_df[behaviors_df["customer_id"] == customer_id].copy()
    
    if customer_events.empty:
        return {}
    
    # Convert dates
    customer_events["event_date"] = pd.to_datetime(customer_events["event_date"])
    today = pd.Timestamp.now()
    
    # Define time windows
    last_30_days = today - pd.Timedelta(days=30)
    last_60_days = today - pd.Timedelta(days=60)
    prev_30_days = today - pd.Timedelta(days=60)  # Days 31-60
    
    # Recent events (last 30 days)
    recent = customer_events[customer_events["event_date"] >= last_30_days]
    
    # Previous period events (days 31-60)
    previous = customer_events[
        (customer_events["event_date"] >= prev_30_days) &
        (customer_events["event_date"] < last_30_days)
    ]
    
    # LOGIN METRICS
    login_count_30d = len(recent[recent["event_type"] == "login"])
    prev_login_count_60d = len(previous[previous["event_type"] == "login"])
    
    if prev_login_count_60d > 0:
        login_change = (login_count_30d - prev_login_count_60d) / prev_login_count_60d
        if login_change < -0.3:
            login_trend = "declining"
        elif login_change > 0.2:
            login_trend = "increasing"
        else:
            login_trend = "stable"
    else:
        login_trend = "stable" if login_count_30d > 5 else "declining"
    
    # SUPPORT TICKET METRICS
    support_tickets_30d = recent[recent["event_type"] == "support_ticket"]
    ticket_count_30d = len(support_tickets_30d)
    
    # Sentiment from notes
    if not support_tickets_30d.empty:
        negative_keywords = ["frustrated", "urgent", "disappointed", "escalation", "issue", "problem"]
        notes = support_tickets_30d["notes"].fillna("").str.lower()
        negative_count = sum(any(kw in note for kw in negative_keywords) for note in notes)
        
        if negative_count > len(support_tickets_30d) * 0.5:
            ticket_sentiment = "negative"
        elif negative_count > 0:
            ticket_sentiment = "mixed"
        else:
            ticket_sentiment = "positive"
    else:
        ticket_sentiment = "neutral"
    
    # FEATURE USAGE METRICS
    feature_recent = recent[recent["event_type"] == "feature_usage"]
    feature_prev = previous[previous["event_type"] == "feature_usage"]
    
    feature_usage_30d = feature_recent["metric_value"].mean() if not feature_recent.empty else 0
    prev_feature_usage_60d = feature_prev["metric_value"].mean() if not feature_prev.empty else 0
    
    # EMAIL RESPONSE TIME METRICS
    email_recent = recent[recent["event_type"] == "email_response_time"]
    email_prev = previous[previous["event_type"] == "email_response_time"]
    
    avg_response_time_30d = email_recent["metric_value"].mean() if not email_recent.empty else 24
    prev_avg_response_time_60d = email_prev["metric_value"].mean() if not email_prev.empty else 24
    
    # PAYMENT DELAY METRICS
    payment_recent = recent[recent["event_type"] == "payment_delay"]
    payment_delay_days_30d = payment_recent["metric_value"].max() if not payment_recent.empty else 0
    
    # ENGAGEMENT TREND
    if login_trend == "declining" and feature_usage_30d < prev_feature_usage_60d:
        engagement_trend = "declining"
    elif login_trend == "increasing" and feature_usage_30d > prev_feature_usage_60d:
        engagement_trend = "increasing"
    else:
        engagement_trend = "stable"
    
    # Calculate months as customer
    signup_date = pd.to_datetime(customer_events["event_date"].min())
    months_as_customer = (today - signup_date).days / 30.0
    
    return {
        "login_count_30d": int(login_count_30d),
        "prev_login_count_60d": int(prev_login_count_60d),
        "login_trend": login_trend,
        "support_ticket_count_30d": int(ticket_count_30d),
        "ticket_sentiment": ticket_sentiment,
        "feature_usage_30d": round(float(feature_usage_30d), 1),
        "prev_feature_usage_60d": round(float(prev_feature_usage_60d), 1),
        "avg_email_response_time_30d": round(float(avg_response_time_30d), 1),
        "prev_avg_email_response_time_60d": round(float(prev_avg_response_time_60d), 1),
        "payment_delay_days_30d": int(payment_delay_days_30d),
        "months_as_customer": round(float(months_as_customer), 1),
        "engagement_trend": engagement_trend
    }


def calculate_risk_score_from_metrics(metrics: Dict[str, Any], customer_pattern: str) -> int:
    """
    Calculate risk score based on behavioral metrics and customer pattern.
    
    Args:
        metrics: Behavioral metrics dict
        customer_pattern: "healthy", "declining", or "critical"
        
    Returns:
        Risk score (0-100)
    """
    # Base score by pattern
    if customer_pattern == "healthy":
        base_score = random.randint(15, 35)
    elif customer_pattern == "declining":
        base_score = random.randint(50, 75)
    else:  # critical
        base_score = random.randint(80, 100)
    
    # Adjust based on metrics
    score_adjustments = 0
    
    # Login trend
    if metrics.get("login_trend") == "declining":
        score_adjustments += 5
    elif metrics.get("login_trend") == "increasing":
        score_adjustments -= 3
    
    # Ticket sentiment
    if metrics.get("ticket_sentiment") == "negative":
        score_adjustments += 8
    elif metrics.get("ticket_sentiment") == "positive":
        score_adjustments -= 2
    
    # Payment delays
    if metrics.get("payment_delay_days_30d", 0) > 10:
        score_adjustments += 10
    elif metrics.get("payment_delay_days_30d", 0) > 0:
        score_adjustments += 5
    
    # Engagement trend
    if metrics.get("engagement_trend") == "declining":
        score_adjustments += 7
    elif metrics.get("engagement_trend") == "increasing":
        score_adjustments -= 4
    
    final_score = base_score + score_adjustments
    return max(0, min(100, final_score))  # Clamp to 0-100


def generate_decay_signals(metrics: Dict[str, Any], risk_score: int) -> List[str]:
    """
    Generate realistic decay signals based on metrics and risk score.
    
    Args:
        metrics: Behavioral metrics
        risk_score: Calculated risk score
        
    Returns:
        List of decay signal strings
    """
    signals = []
    
    # Login frequency
    if metrics.get("login_trend") == "declining":
        if metrics.get("login_count_30d", 0) < 5:
            signals.append(DECAY_SIGNALS["login_decline_severe"])
        else:
            signals.append(DECAY_SIGNALS["login_decline_moderate"])
    
    # Feature usage
    feature_30d = metrics.get("feature_usage_30d", 0)
    feature_60d = metrics.get("prev_feature_usage_60d", 0)
    if feature_60d > 0 and feature_30d < feature_60d * 0.6:
        signals.append(DECAY_SIGNALS["feature_decline_severe"])
    elif feature_60d > 0 and feature_30d < feature_60d * 0.8:
        signals.append(DECAY_SIGNALS["feature_decline"])
    
    # Email response time
    response_30d = metrics.get("avg_email_response_time_30d", 0)
    response_60d = metrics.get("prev_avg_email_response_time_60d", 0)
    if response_30d > response_60d * 2:
        signals.append(DECAY_SIGNALS["response_time_severe"])
    elif response_30d > response_60d * 1.5:
        signals.append(DECAY_SIGNALS["response_time_increase"])
    
    # Payment delays
    payment_delay = metrics.get("payment_delay_days_30d", 0)
    if payment_delay > 15:
        signals.append(DECAY_SIGNALS["payment_delay_severe"])
    elif payment_delay > 0:
        signals.append(DECAY_SIGNALS["payment_delay"])
    
    # Negative sentiment
    if metrics.get("ticket_sentiment") == "negative":
        signals.append(DECAY_SIGNALS["negative_sentiment"])
    
    # Ticket increase
    if metrics.get("support_ticket_count_30d", 0) > 5:
        signals.append(DECAY_SIGNALS["ticket_increase"])
    
    # Overall engagement
    if metrics.get("engagement_trend") == "declining":
        signals.append(DECAY_SIGNALS["engagement_drop"])
    
    # Critical inactivity
    if risk_score >= 85 and metrics.get("login_count_30d", 0) < 3:
        signals.append(DECAY_SIGNALS["critical_inactivity"])
    
    return signals


def get_risk_level(risk_score: int) -> str:
    """Convert risk score to risk level."""
    if risk_score >= 80:
        return "critical"
    elif risk_score >= 60:
        return "high"
    elif risk_score >= 35:
        return "medium"
    else:
        return "low"


def predict_churn_date(risk_score: int) -> str:
    """
    Predict churn date based on risk score.
    
    Args:
        risk_score: Risk score (0-100)
        
    Returns:
        ISO format date string
    """
    today = date.today()
    
    if risk_score >= 85:
        days_until_churn = random.randint(7, 30)
    elif risk_score >= 70:
        days_until_churn = random.randint(30, 90)
    elif risk_score >= 50:
        days_until_churn = random.randint(90, 180)
    else:
        days_until_churn = random.randint(180, 365)
    
    churn_date = today + timedelta(days=days_until_churn)
    return churn_date.isoformat()


def calculate_priority(risk_score: int, monthly_value: float) -> int:
    """
    Calculate intervention priority (1-10).
    
    Args:
        risk_score: Risk score (0-100)
        monthly_value: Monthly contract value
        
    Returns:
        Priority score (1-10, 10 being highest)
    """
    # Normalize monthly value (assuming range $100-$8000)
    value_score = min(10, (monthly_value - 100) / 790)  # 0-10 scale
    
    # Risk component (0-10 scale)
    risk_component = risk_score / 10
    
    # Weighted average: 60% risk, 40% value
    priority = (0.6 * risk_component) + (0.4 * value_score)
    
    return max(1, min(10, round(priority)))


def select_similar_churned(churned_df: pd.DataFrame, count: int = 3) -> List[Dict[str, Any]]:
    """
    Select random churned customers as similar examples.
    
    Args:
        churned_df: DataFrame of churned customers
        count: Number to select
        
    Returns:
        List of similar churned customer dicts
    """
    sample = churned_df.sample(n=min(count, len(churned_df)))
    
    similar = []
    for _, row in sample.iterrows():
        similarity_score = round(random.uniform(0.6, 0.95), 2)
        similar.append({
            "customer_id": row["customer_id"],
            "similarity_score": similarity_score,
            "company_name": row["company_name"],
            "churn_reason": row["churn_reason"],
            "days_until_churned": int(row["days_until_churned"]),
            "decay_pattern": row["decay_pattern"]
        })
    
    return similar


def generate_analysis_for_customer(
    customer: pd.Series,
    behaviors_df: pd.DataFrame,
    churned_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Generate complete risk analysis for a customer.
    
    Args:
        customer: Customer row from DataFrame
        behaviors_df: All behavior events
        churned_df: Churned customers data
        
    Returns:
        Complete analysis dict
    """
    customer_id = customer["customer_id"]
    cust_num = int(customer_id[4:])  # Extract number from CUST001
    
    # Determine pattern
    if 1 <= cust_num <= 40:
        pattern = "healthy"
    elif 41 <= cust_num <= 80:
        pattern = "declining"
    else:
        pattern = "critical"
    
    # Calculate behavioral metrics
    metrics = calculate_behavioral_metrics(customer_id, behaviors_df)
    
    # Calculate risk score
    risk_score = calculate_risk_score_from_metrics(metrics, pattern)
    risk_level = get_risk_level(risk_score)
    
    # Generate decay signals
    decay_signals = generate_decay_signals(metrics, risk_score)
    
    # Generate concern and intervention
    primary_concern = get_concern_for_signals(risk_level, decay_signals)
    recommended_intervention = get_intervention_for_risk(risk_level, decay_signals)
    
    # Predict churn date
    predicted_churn_date = predict_churn_date(risk_score)
    
    # Calculate revenue at risk
    churn_date_obj = datetime.fromisoformat(predicted_churn_date)
    months_until_churn = (churn_date_obj - datetime.now()).days / 30.0
    estimated_revenue_at_risk = int(customer["monthly_value"] * months_until_churn)
    
    # Calculate priority
    priority = calculate_priority(risk_score, customer["monthly_value"])
    
    # Select similar churned customers
    similar_churned = select_similar_churned(churned_df, count=3)
    
    # Determine urgency
    if risk_level == "critical":
        urgency = "critical"
    elif risk_level == "high":
        urgency = "high"
    elif risk_level == "medium":
        urgency = "medium"
    else:
        urgency = "low"
    
    # Confidence level
    if len(decay_signals) >= 4:
        confidence = "high"
    elif len(decay_signals) >= 2:
        confidence = "medium"
    else:
        confidence = "low"
    
    return {
        "customer_id": customer_id,
        "customer_name": customer["company_name"],
        "subscription_tier": customer["subscription_tier"],
        "monthly_value": float(customer["monthly_value"]),
        "churn_risk_score": risk_score,
        "risk_level": risk_level,
        "decay_signals": decay_signals,
        "primary_concern": primary_concern,
        "recommended_intervention": recommended_intervention,
        "urgency": urgency,
        "similar_churned_customers": similar_churned,
        "predicted_churn_date": predicted_churn_date,
        "intervention_priority": priority,
        "estimated_revenue_at_risk": estimated_revenue_at_risk,
        "confidence_level": confidence,
        "behavioral_metrics": metrics,
        "analysis_timestamp": datetime.now().isoformat()
    }


def main():
    """Main execution: generate preprocessed analysis for all customers."""
    print("="*70)
    print("GENERATING PREPROCESSED RISK ANALYSIS")
    print("="*70)
    
    # Load data
    print("\n1. Loading data...")
    customers_df, behaviors_df, churned_df = load_data()
    print(f"   ✓ Loaded {len(customers_df)} customers")
    print(f"   ✓ Loaded {len(behaviors_df)} behavior events")
    print(f"   ✓ Loaded {len(churned_df)} churned customers")
    
    # Generate analysis for each customer
    print("\n2. Generating risk analysis (NO API CALLS)...")
    all_analyses = []
    
    for idx, customer in customers_df.iterrows():
        if (idx + 1) % 20 == 0:
            print(f"   Processing customer {idx + 1}/{len(customers_df)}...")
        
        analysis = generate_analysis_for_customer(customer, behaviors_df, churned_df)
        all_analyses.append(analysis)
    
    print(f"   ✓ Generated {len(all_analyses)} complete analyses")
    
    # Save to file
    print("\n3. Saving results...")
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    output_path = os.path.join(data_dir, "preprocessed_analysis.json")
    
    with open(output_path, "w") as f:
        json.dump(all_analyses, f, indent=2)
    
    print(f"   ✓ Saved to {output_path}")
    
    # Print statistics
    print("\n" + "="*70)
    print("ANALYSIS SUMMARY")
    print("="*70)
    
    risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for analysis in all_analyses:
        risk_counts[analysis["risk_level"]] += 1
    
    print(f"\nRisk Distribution:")
    print(f"  Low Risk:      {risk_counts['low']} customers ({risk_counts['low']/len(all_analyses)*100:.1f}%)")
    print(f"  Medium Risk:   {risk_counts['medium']} customers ({risk_counts['medium']/len(all_analyses)*100:.1f}%)")
    print(f"  High Risk:     {risk_counts['high']} customers ({risk_counts['high']/len(all_analyses)*100:.1f}%)")
    print(f"  Critical Risk: {risk_counts['critical']} customers ({risk_counts['critical']/len(all_analyses)*100:.1f}%)")
    
    # Revenue at risk
    total_revenue_at_risk = sum(a["estimated_revenue_at_risk"] for a in all_analyses)
    high_risk_revenue = sum(
        a["estimated_revenue_at_risk"]
        for a in all_analyses
        if a["risk_level"] in ["high", "critical"]
    )
    
    print(f"\nRevenue Analysis:")
    print(f"  Total Revenue at Risk: ${total_revenue_at_risk:,}")
    print(f"  High/Critical Risk:    ${high_risk_revenue:,}")
    
    print("\n" + "="*70)
    print("✅ PREPROCESSING COMPLETE!")
    print("="*70)
    print("\nYour backend can now serve 100 customers instantly without API calls!")
    print("Start the server: python app.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
