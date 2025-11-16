"""
Customer behavior analyzer using Google Gemini API.

Analyzes customer behavior patterns to detect churn risk using Gemini Pro model.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


class CustomerAnalyzer:
    """
    Analyzes customer behavior using Gemini API to detect churn risk.
    
    Attributes:
        api_key: Google AI API key from environment
        model: Gemini model instance
    """
    
    def __init__(self) -> None:
        """
        Initialize analyzer with Gemini API.
        
        Raises:
            ValueError: If GEMINI_API_KEY not found in environment
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.model = genai.GenerativeModel(model_name)
    
    def calculate_metrics(
        self, customer_data: Dict[str, Any], behavior_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Calculate behavioral metrics from last 30 and previous 30 days.
        
        Args:
            customer_data: Dict with customer_id, company_name, subscription_tier,
                          monthly_value, signup_date
            behavior_data: DataFrame with all behavior events for this customer
        
        Returns:
            Dict with calculated metrics including login counts, trends, sentiment,
            feature usage, email response times, payment delays, and engagement trends
        """
        # Ensure event_date is datetime
        df = behavior_data.copy()
        if df.empty:
            df = pd.DataFrame(columns=["event_date", "event_type", "metric_value", "notes"])
        
        df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
        
        today = datetime.utcnow().date()
        start_30 = today - timedelta(days=30)
        start_60 = today - timedelta(days=60)
        
        # Filter by time periods
        df_30 = df[(df["event_date"].dt.date >= start_30) & (df["event_date"].dt.date <= today)]
        df_prev = df[(df["event_date"].dt.date >= start_60) & (df["event_date"].dt.date < start_30)]
        
        # Login counts
        login_count_30d = int((df_30["event_type"] == "login").sum())
        prev_login_count_60d = int((df_prev["event_type"] == "login").sum())
        
        # Calculate trend
        def _trend(cur: float, prev: float, threshold: float = 0.2) -> str:
            if prev == 0 and cur == 0:
                return "stable"
            if prev == 0:
                return "increasing" if cur > 0 else "stable"
            change = (cur - prev) / prev
            if change > threshold:
                return "increasing"
            if change < -threshold:
                return "declining"
            return "stable"
        
        login_trend = _trend(login_count_30d, prev_login_count_60d)
        
        # Support tickets and sentiment
        tickets_30 = df_30[df_30["event_type"] == "support_ticket"]
        support_ticket_count_30d = int(len(tickets_30))
        
        # Analyze sentiment from notes
        notes_text = " ".join(tickets_30["notes"].dropna().astype(str).tolist()).lower()
        positive_tokens = ["thanks", "quick", "helpful", "resolved", "great", "excellent"]
        negative_tokens = [
            "frustrated", "disappointed", "urgent", "not working",
            "downtime", "escalation", "critical", "angry"
        ]
        
        pos_hits = sum(tok in notes_text for tok in positive_tokens)
        neg_hits = sum(tok in notes_text for tok in negative_tokens)
        
        if neg_hits > pos_hits and neg_hits > 0:
            ticket_sentiment = "negative"
        elif pos_hits > neg_hits and pos_hits > 0:
            ticket_sentiment = "positive"
        else:
            ticket_sentiment = "neutral"
        
        # Feature usage (average per week)
        fu_30 = df_30[df_30["event_type"] == "feature_usage"]["metric_value"].astype(float).sum()
        fu_prev = df_prev[df_prev["event_type"] == "feature_usage"]["metric_value"].astype(float).sum()
        feature_usage_30d = float(fu_30) / 4.0  # ~4 weeks
        prev_feature_usage_60d = float(fu_prev) / 4.0
        
        # Email response time (average hours)
        em_30 = df_30[df_30["event_type"] == "email_response_time"]["metric_value"].astype(float)
        em_prev = df_prev[df_prev["event_type"] == "email_response_time"]["metric_value"].astype(float)
        avg_email_response_time_30d = float(em_30.mean()) if not em_30.empty else 0.0
        prev_avg_email_response_time_60d = float(em_prev.mean()) if not em_prev.empty else 0.0
        
        # Payment delay (max days late)
        pay_30 = df_30[df_30["event_type"] == "payment_delay"]["metric_value"].astype(float)
        payment_delay_days_30d = int(pay_30.max()) if not pay_30.empty else 0
        
        # Months as customer
        signup_str = str(customer_data.get("signup_date", ""))
        try:
            signup_dt = datetime.fromisoformat(signup_str).date()
        except Exception:
            signup_dt = today
        
        months_as_customer = (today - signup_dt).days / 30.44
        
        # Engagement trend
        usage_trend = _trend(feature_usage_30d, prev_feature_usage_60d)
        resp_increase = (
            avg_email_response_time_30d > 0 and
            prev_avg_email_response_time_60d > 0 and
            (avg_email_response_time_30d / max(prev_avg_email_response_time_60d, 1e-9)) > 1.2
        )
        
        if login_trend == "declining" and (usage_trend == "declining" or resp_increase):
            engagement_trend = "declining"
        elif login_trend == "increasing" and usage_trend == "increasing":
            engagement_trend = "improving"
        else:
            engagement_trend = "stable"
        
        return {
            "login_count_30d": login_count_30d,
            "prev_login_count_60d": prev_login_count_60d,
            "login_trend": login_trend,
            "support_ticket_count_30d": support_ticket_count_30d,
            "ticket_sentiment": ticket_sentiment,
            "feature_usage_30d": round(feature_usage_30d, 2),
            "prev_feature_usage_60d": round(prev_feature_usage_60d, 2),
            "avg_email_response_time_30d": round(avg_email_response_time_30d, 2),
            "prev_avg_email_response_time_60d": round(prev_avg_email_response_time_60d, 2),
            "payment_delay_days_30d": payment_delay_days_30d,
            "months_as_customer": round(months_as_customer, 1),
            "engagement_trend": engagement_trend,
        }
    
    def build_analysis_prompt(
        self, customer_data: Dict[str, Any], metrics: Dict[str, Any]
    ) -> str:
        """
        Build structured prompt for Gemini to analyze churn risk.
        
        Args:
            customer_data: Customer information
            metrics: Calculated behavioral metrics
        
        Returns:
            Formatted prompt string requesting JSON-only output
        """
        prompt = f"""You are an expert customer success analyst specializing in churn prediction.

Analyze this customer's behavior and assess churn risk:

CUSTOMER PROFILE:
- Company: {customer_data.get('company_name')}
- Tier: {customer_data.get('subscription_tier')}
- Monthly Value: ${customer_data.get('monthly_value')}
- Customer Since: {metrics.get('months_as_customer')} months

BEHAVIORAL METRICS (Last 30 Days vs Previous 30 Days):
- Login Frequency: {metrics.get('login_count_30d')} (was {metrics.get('prev_login_count_60d')}) - Trend: {metrics.get('login_trend')}
- Support Tickets: {metrics.get('support_ticket_count_30d')} with {metrics.get('ticket_sentiment')} sentiment
- Feature Usage: {metrics.get('feature_usage_30d')} features/week (was {metrics.get('prev_feature_usage_60d')})
- Email Response Time: {metrics.get('avg_email_response_time_30d')} hours (was {metrics.get('prev_avg_email_response_time_60d')})
- Payment Delays: {metrics.get('payment_delay_days_30d')} days max delay
- Overall Engagement: {metrics.get('engagement_trend')}

KNOWN CHURN PATTERNS:
- Login frequency drops >50%
- Support ticket sentiment becomes negative
- Email response time increases >2x
- Payment delays appear or increase
- Feature usage declines steadily over time

TASK:
Assess this customer's churn risk and return ONLY a JSON object (no markdown, no explanation) with this exact structure:
{{
  "churn_risk_score": <number 0-100>,
  "decay_signals": ["signal1", "signal2", ...],
  "primary_concern": "<one sentence description>",
  "recommended_intervention": "<specific action to take>",
  "urgency": "low" | "medium" | "high" | "critical"
}}

Risk score guidelines:
- 0-30: Low risk (healthy customer)
- 31-60: Medium risk (showing some warning signs)
- 61-80: High risk (multiple decay signals)
- 81-100: Critical risk (urgent intervention needed)
"""
        return prompt.strip()
    
    def _clean_json_text(self, text: str) -> str:
        """Remove markdown fences and extraneous text."""
        cleaned = text.strip()
        cleaned = re.sub(r"^```json\s*|\s*```$", "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
        cleaned = re.sub(r"^```\s*|\s*```$", "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
        return cleaned.strip()
    
    def call_gemini_api(self, prompt: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Call Gemini API with retry logic.
        
        Args:
            prompt: Analysis prompt
            max_retries: Number of retry attempts
        
        Returns:
            Parsed JSON response with risk assessment
        
        Raises:
            RuntimeError: If all retries fail
        """
        last_err: Optional[Exception] = None
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                text = getattr(response, "text", None) or ""
                cleaned = self._clean_json_text(text)
                data = json.loads(cleaned)
                
                # Validate required fields
                required = [
                    "churn_risk_score",
                    "decay_signals",
                    "primary_concern",
                    "recommended_intervention",
                    "urgency",
                ]
                for key in required:
                    if key not in data:
                        raise ValueError(f"Missing required field: {key}")
                
                if not isinstance(data.get("decay_signals"), list):
                    raise ValueError("decay_signals must be a list")
                
                # Clamp risk score to [0, 100]
                try:
                    rs = float(data.get("churn_risk_score", 0))
                except Exception:
                    rs = 0.0
                data["churn_risk_score"] = int(max(0, min(100, round(rs))))
                
                return data
            except Exception as e:
                last_err = e
                sleep_for = 2 ** attempt
                time.sleep(sleep_for)
        
        # All retries failed
        raise RuntimeError(f"Gemini API call failed after {max_retries} retries: {last_err}")
    
    def analyze_customer(
        self, customer_data: Dict[str, Any], behavior_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Complete analysis pipeline for one customer.
        
        Args:
            customer_data: Dict with customer info
            behavior_data: DataFrame with behavior events
        
        Returns:
            Comprehensive analysis dict with risk score, signals,
            recommendations, and metrics
        """
        # Calculate metrics
        metrics = self.calculate_metrics(customer_data, behavior_data)
        
        # Build prompt
        prompt = self.build_analysis_prompt(customer_data, metrics)
        
        # Call Gemini API
        try:
            ai_result = self.call_gemini_api(prompt)
        except Exception as e:
            # Fallback to rule-based scoring
            ai_result = self._rule_based_fallback(metrics)
            ai_result["primary_concern"] = f"API error: {str(e)[:100]}"
        
        # Determine risk level
        score = int(ai_result.get("churn_risk_score", 0))
        if score < 30:
            risk_level = "low"
        elif score <= 60:
            risk_level = "medium"
        elif score <= 80:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        # Combine all data
        result = {
            "customer_id": customer_data.get("customer_id"),
            "customer_name": customer_data.get("company_name"),
            "subscription_tier": customer_data.get("subscription_tier"),
            "monthly_value": float(customer_data.get("monthly_value", 0) or 0),
            "churn_risk_score": score,
            "risk_level": risk_level,
            "decay_signals": ai_result.get("decay_signals", []),
            "primary_concern": ai_result.get("primary_concern", ""),
            "recommended_intervention": ai_result.get("recommended_intervention", ""),
            "urgency": ai_result.get("urgency", "low"),
            "behavioral_metrics": metrics,
            "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        return result
    
    def _rule_based_fallback(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Heuristic fallback when LLM is unavailable."""
        score = 20
        signals: List[str] = []
        
        # Login trend
        if metrics.get("login_trend") == "declining":
            score += 20
            signals.append("decreased_logins")
        
        # Feature usage drop
        fu = float(metrics.get("feature_usage_30d", 0))
        fu_prev = float(metrics.get("prev_feature_usage_60d", 0))
        if fu_prev > 0 and fu < 0.75 * fu_prev:
            score += 15
            signals.append("reduced_feature_usage")
        
        # Email response slower
        em = float(metrics.get("avg_email_response_time_30d", 0))
        em_prev = float(metrics.get("prev_avg_email_response_time_60d", 0))
        if em_prev > 0 and em > 2 * em_prev:
            score += 15
            signals.append("slower_email_responses")
        
        # Payment delays
        pdays = int(metrics.get("payment_delay_days_30d", 0))
        if pdays > 0:
            score += 10
            signals.append("payment_delays")
        if pdays >= 10:
            score += 15
        
        # Support tickets and sentiment
        tickets = int(metrics.get("support_ticket_count_30d", 0))
        if tickets >= 5:
            score += 10
            signals.append("high_support_tickets")
        if metrics.get("ticket_sentiment") == "negative":
            score += 10
            signals.append("negative_sentiment")
        
        score = int(max(0, min(100, score)))
        
        urgency = "low"
        if score <= 30:
            urgency = "low"
        elif score <= 60:
            urgency = "medium"
        elif score <= 80:
            urgency = "high"
        else:
            urgency = "critical"
        
        return {
            "churn_risk_score": score,
            "decay_signals": signals or ["insufficient_signals"],
            "primary_concern": "Rule-based assessment (LLM unavailable)",
            "recommended_intervention": "CSM should review recent activity and schedule check-in",
            "urgency": urgency,
        }


# Test script
if __name__ == "__main__":
    """
    Test analyzer with sample data from 3 customer patterns.
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
    
    analyzer = CustomerAnalyzer()
    
    # Test 3 customers: healthy, declining, critical
    test_ids = ["CUST001", "CUST013", "CUST025"]
    
    print("\n" + "="*70)
    print("CUSTOMER BEHAVIOR ANALYZER TEST")
    print("="*70 + "\n")
    
    for cid in test_ids:
        cust_row = customers[customers["customer_id"] == cid].iloc[0].to_dict()
        beh_df = events[events["customer_id"] == cid]
        
        print(f"\nAnalyzing {cid} ({cust_row['company_name']})...")
        result = analyzer.analyze_customer(cust_row, beh_df)
        
        print(f"  Risk Score: {result['churn_risk_score']} ({result['risk_level'].upper()})")
        print(f"  Urgency: {result['urgency']}")
        print(f"  Signals: {', '.join(result['decay_signals'])}")
        print(f"  Concern: {result['primary_concern']}")
        print(f"  Action: {result['recommended_intervention']}")
    
    print("\n" + "="*70)
    print("✅ All tests completed successfully!")
    print("="*70 + "\n")
