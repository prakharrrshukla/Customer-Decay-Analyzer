"""
Risk Assessor - Combines Gemini AI analysis with Qdrant vector similarity.

Provides comprehensive churn risk assessment by analyzing current behavior
and comparing against historical churned customer patterns.
"""

from __future__ import annotations

import os
import statistics
from datetime import date, datetime, timedelta
from typing import Any, Dict, List

import pandas as pd
from dotenv import load_dotenv

from models.gemini_analyzer import CustomerAnalyzer
from models.vector_store import QdrantVectorStore

load_dotenv()


class RiskAssessor:
    """
    Combines AI analysis with vector similarity for comprehensive risk assessment.
    """
    
    def __init__(self) -> None:
        """Initialize Gemini analyzer and Qdrant vector store."""
        self.analyzer = CustomerAnalyzer()
        collection_name = os.getenv("QDRANT_COLLECTION", "customer_behaviors")
        self.vector_store = QdrantVectorStore(collection_name)
    
    def calculate_combined_risk_score(
        self,
        gemini_score: float,
        similar_customers: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate combined risk score weighted between Gemini and similarity.
        
        Args:
            gemini_score: Risk score from Gemini (0-100)
            similar_customers: List of similar churned customers with scores
        
        Returns:
            Combined risk score (0-100)
        """
        if not similar_customers:
            return float(gemini_score)
        
        # Calculate similarity component
        # Higher similarity to churned customers = higher risk
        # Weight recent churns more heavily
        similarity_scores = []
        for cust in similar_customers:
            sim_score = float(cust.get("similarity_score", 0))
            days_until = int(cust.get("days_until_churned", 90))
            
            # Quick churns (< 60 days) are more concerning
            urgency_multiplier = 1.5 if days_until < 60 else 1.0
            similarity_scores.append(sim_score * urgency_multiplier * 100)
        
        avg_similarity = statistics.mean(similarity_scores) if similarity_scores else 0
        
        # Combine: Gemini 60%, Similarity 40%
        combined = (gemini_score * 0.6) + (avg_similarity * 0.4)
        return round(max(0, min(100, combined)), 2)
    
    def predict_churn_date(
        self,
        similar_customers: List[Dict[str, Any]],
        current_decline_trend: str
    ) -> str:
        """
        Predict likely churn date based on similar customers and current trend.
        
        Args:
            similar_customers: List of similar churned customers
            current_decline_trend: "slow", "moderate", or "rapid"
        
        Returns:
            Predicted churn date as ISO string
        """
        if not similar_customers:
            # Default to 90 days
            pred_date = date.today() + timedelta(days=90)
            return pred_date.isoformat()
        
        # Get median days_until_churned from similar customers
        days_list = [
            int(c.get("days_until_churned", 90))
            for c in similar_customers
            if c.get("days_until_churned")
        ]
        
        if days_list:
            median_days = statistics.median(days_list)
        else:
            median_days = 90
        
        # Adjust by current trend
        if current_decline_trend == "rapid":
            adjusted_days = median_days * 0.5  # Faster churn
        elif current_decline_trend == "slow":
            adjusted_days = median_days * 1.5  # Slower churn
        else:
            adjusted_days = median_days
        
        pred_date = date.today() + timedelta(days=int(adjusted_days))
        return pred_date.isoformat()
    
    def assess_customer_risk(
        self,
        customer_data: Dict[str, Any],
        behavior_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Complete risk assessment pipeline for one customer.
        
        Args:
            customer_data: Customer information dict
            behavior_data: DataFrame with behavior events
        
        Returns:
            Comprehensive risk report with AI analysis, similar customers,
            predictions, and recommendations
        """
        # Step 1: Run Gemini analysis
        gemini_analysis = self.analyzer.analyze_customer(customer_data, behavior_data)
        
        # Step 2: Extract metrics and create behavior vector
        metrics = gemini_analysis["behavioral_metrics"]
        
        # Map metrics to vector format
        vector_metrics = {
            "login_frequency": metrics.get("login_count_30d", 15),
            "feature_usage": metrics.get("feature_usage_30d", 10),
            "support_ticket_count": metrics.get("support_ticket_count_30d", 3),
            "email_response_time": metrics.get("avg_email_response_time_30d", 24),
            "payment_delay_days": metrics.get("payment_delay_days_30d", 0),
            "session_duration": 30,  # Default
            "sentiment_score": -0.3 if metrics.get("ticket_sentiment") == "negative"
                              else (0.3 if metrics.get("ticket_sentiment") == "positive" else 0),
            "months_as_customer": metrics.get("months_as_customer", 12),
            "login_trend": 0.3 if metrics.get("login_trend") == "increasing"
                          else (-0.3 if metrics.get("login_trend") == "declining" else 0),
            "engagement_score": 0.7 if metrics.get("engagement_trend") == "improving"
                               else (0.3 if metrics.get("engagement_trend") == "declining" else 0.5),
        }
        
        behavior_vector = self.vector_store.create_behavior_vector(vector_metrics)
        
        # Step 3: Search for similar churned customers
        try:
            similar_churned = self.vector_store.search_similar_customers(
                behavior_vector,
                limit=5,
                filter_churned=True
            )
        except Exception as e:
            print(f"Warning: Vector search failed: {e}")
            similar_churned = []
        
        # Step 4: Calculate combined risk score
        gemini_score = gemini_analysis["churn_risk_score"]
        combined_score = self.calculate_combined_risk_score(gemini_score, similar_churned)
        
        # Step 5: Determine decline trend
        engagement = metrics.get("engagement_trend", "stable")
        login_trend = metrics.get("login_trend", "stable")
        
        if engagement == "declining" and login_trend == "declining":
            decline_trend = "rapid"
        elif engagement == "declining" or login_trend == "declining":
            decline_trend = "moderate"
        else:
            decline_trend = "slow"
        
        # Step 6: Predict churn date
        predicted_churn = self.predict_churn_date(similar_churned, decline_trend)
        
        # Step 7: Calculate intervention priority (1-10)
        monthly_value = float(customer_data.get("monthly_value", 0))
        # High risk + high value = high priority
        priority = min(10, int((combined_score / 100) * 10 * (1 + min(monthly_value / 5000, 1))))
        
        # Step 8: Estimate revenue at risk
        # Assume average 12 months lifetime value
        estimated_revenue_at_risk = monthly_value * 12
        
        # Step 9: Determine confidence level
        if similar_churned and len(similar_churned) >= 3:
            confidence = "high"
        elif similar_churned:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Determine risk level from combined score
        if combined_score < 30:
            risk_level = "low"
        elif combined_score <= 60:
            risk_level = "medium"
        elif combined_score <= 80:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        # Build comprehensive report
        report = {
            "customer_id": customer_data.get("customer_id"),
            "customer_name": customer_data.get("company_name"),
            "subscription_tier": customer_data.get("subscription_tier"),
            "monthly_value": monthly_value,
            "churn_risk_score": combined_score,
            "risk_level": risk_level,
            "decay_signals": gemini_analysis.get("decay_signals", []),
            "primary_concern": gemini_analysis.get("primary_concern", ""),
            "recommended_intervention": gemini_analysis.get("recommended_intervention", ""),
            "urgency": gemini_analysis.get("urgency", "low"),
            "similar_churned_customers": similar_churned,
            "predicted_churn_date": predicted_churn,
            "intervention_priority": priority,
            "estimated_revenue_at_risk": round(estimated_revenue_at_risk, 2),
            "confidence_level": confidence,
            "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
            "behavioral_metrics": metrics,
        }
        
        return report
    
    def assess_all_customers(
        self,
        customers_df: pd.DataFrame,
        behaviors_df: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """
        Assess risk for all customers.
        
        Args:
            customers_df: DataFrame of all customers
            behaviors_df: DataFrame of all behavior events
        
        Returns:
            List of risk assessments sorted by risk score (descending)
        """
        results: List[Dict[str, Any]] = []
        
        print(f"\nAssessing {len(customers_df)} customers...")
        
        for idx, row in customers_df.iterrows():
            customer_data = row.to_dict()
            customer_id = customer_data.get("customer_id")
            
            # Filter behaviors for this customer
            customer_behaviors = behaviors_df[
                behaviors_df["customer_id"] == customer_id
            ]
            
            try:
                assessment = self.assess_customer_risk(customer_data, customer_behaviors)
                results.append(assessment)
                
                # Progress indicator
                if (idx + 1) % 5 == 0:
                    print(f"  Processed {idx + 1}/{len(customers_df)} customers...")
            except Exception as e:
                print(f"  Error assessing {customer_id}: {e}")
                continue
        
        # Sort by risk score descending
        results.sort(key=lambda x: x.get("churn_risk_score", 0), reverse=True)
        
        return results


# Test script
if __name__ == "__main__":
    """
    Test risk assessor with sample customers.
    """
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, "data")
    customers_path = os.path.join(data_dir, "customers.csv")
    events_path = os.path.join(data_dir, "behavior_events.csv")
    
    if not os.path.exists(customers_path) or not os.path.exists(events_path):
        print("ERROR: Sample data not found. Run scripts/generate_sample_data.py first.")
        sys.exit(1)
    
    customers = pd.read_csv(customers_path)
    events = pd.read_csv(events_path)
    
    assessor = RiskAssessor()
    
    print("\n" + "="*70)
    print("RISK ASSESSOR TEST")
    print("="*70)
    
    # Test with declining customer
    test_id = "CUST013"
    cust_row = customers[customers["customer_id"] == test_id].iloc[0].to_dict()
    beh_df = events[events["customer_id"] == test_id]
    
    print(f"\nAssessing {test_id} ({cust_row['company_name']})...")
    report = assessor.assess_customer_risk(cust_row, beh_df)
    
    print(f"\n{'─'*70}")
    print("COMPREHENSIVE RISK REPORT")
    print(f"{'─'*70}")
    print(f"Customer: {report['customer_name']} ({report['customer_id']})")
    print(f"Tier: {report['subscription_tier']} | Value: ${report['monthly_value']}")
    print(f"\nRisk Score: {report['churn_risk_score']} ({report['risk_level'].upper()})")
    print(f"Confidence: {report['confidence_level'].upper()}")
    print(f"Urgency: {report['urgency'].upper()}")
    print(f"Intervention Priority: {report['intervention_priority']}/10")
    print(f"\nPredicted Churn Date: {report['predicted_churn_date']}")
    print(f"Revenue at Risk: ${report['estimated_revenue_at_risk']:,.2f}")
    print(f"\nDecay Signals: {', '.join(report['decay_signals'])}")
    print(f"\nPrimary Concern:\n  {report['primary_concern']}")
    print(f"\nRecommended Action:\n  {report['recommended_intervention']}")
    print(f"\nSimilar Churned Customers: {len(report['similar_churned_customers'])}")
    
    for sim in report['similar_churned_customers'][:3]:
        print(f"  - {sim['company_name']}: {sim['churn_reason']} "
              f"(similarity: {sim['similarity_score']:.2f})")
    
    print(f"\n{'─'*70}\n")
    print("✅ Risk assessor test completed!")
    print("="*70 + "\n")
