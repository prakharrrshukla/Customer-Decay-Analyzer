"""
Generate realistic sample data for Customer Decay Analyzer demo.

Creates three CSV files:
1. data/customers.csv - 100 current customers
2. data/behavior_events.csv - 90 days of behavioral data
3. data/churned_customers.csv - 20 historical churned customers

Customer patterns:
- Healthy (40%): CUST001-CUST040 - High engagement, fast responses, no issues
- Declining (40%): CUST041-CUST080 - Decreasing activity, slower responses, occasional delays
- Critical (20%): CUST081-CUST100 - Very low activity, major delays, negative sentiment
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd


RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ---------------------------
# Utilities
# ---------------------------

def ensure_data_dir(path: str) -> None:
    """Ensure the `data/` directory exists.

    Args:
        path: Directory path to create if missing.
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def rand_date(start: date, end: date) -> date:
    """Return a random date between start and end (inclusive).

    Args:
        start: Start date
        end: End date

    Returns:
        Random date in range [start, end].
    """
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def choice_weighted(options: List[str], weights: List[float]) -> str:
    """Weighted random choice for categorical values.

    Args:
        options: List of labels to choose from
        weights: Corresponding probabilities (sum ~ 1.0)

    Returns:
        Selected option string.
    """
    return random.choices(options, weights=weights, k=1)[0]


# ---------------------------
# Data Generators
# ---------------------------

def generate_customers(num_customers: int = 100) -> pd.DataFrame:
    """
    Generate sample customer data.

    Args:
        num_customers: Number of customers to generate (default 100)

    Returns:
        DataFrame with columns: customer_id, company_name, signup_date,
        subscription_tier, monthly_value, email

    Requirements implemented:
    - customer_id: CUST001 to CUST100 (zero-padded)
    - company_name: 100 unique realistic tech company names
    - signup_date: Random dates between 2023-01-01 and 2024-06-01
    - subscription_tier distribution and monthly_value ranges by tier:
        * Enterprise (30%): $3000-$8000
        * Pro (50%): $800-$2000
        * Basic (20%): $100-$500
    - email: Generated from company name
    """
    adjectives = [
        "TechFlow", "DataSync", "CloudBridge", "InnovateTech", "PixelForge",
        "ByteWise", "NexGen", "StreamLine", "CodeCraft", "QuantumEdge",
        "Skyline", "BluePeak", "ApexLogic", "NovaCore", "BrightWave",
        "EchoGrid", "VectorWorks", "FusionByte", "CobaltCloud", "AuroraSoft",
        "DataVault", "CloudScale", "ByteStream", "SkyBridge", "CodeWave",
        "PixelStream", "TechNova", "DataPeak", "CloudVault", "ByteForge",
        "SkyFlow", "CodeBridge", "PixelWise", "TechEdge", "DataWave",
        "CloudCraft", "BytePeak", "SkyVault", "CodeSync", "PixelLogic",
        "TechBridge", "DataForge", "CloudWise", "ByteEdge", "SkySync",
        "CodeVault", "PixelCraft", "TechWave", "DataEdge", "CloudFlow",
        "ByteBridge", "SkyWise", "CodeForge", "PixelEdge", "TechVault",
        "DataCraft", "CloudSync", "ByteWave", "SkyEdge", "CodeFlow",
        "PixelBridge", "TechCraft", "DataBridge", "CloudEdge", "ByteVault",
        "SkyPeak", "CodeEdge", "PixelFlow", "TechSync", "DataFlow",
        "CloudPeak", "ByteSync", "SkyForge", "CodePeak", "PixelSync",
        "TechForge", "DataFlow", "CloudForge", "ByteFlow", "SkyCraft",
        "CodeWave", "PixelVault", "TechFlow", "DataSync", "CloudBridge",
        "ByteCraft", "SkyBridge", "CodeCraft", "PixelForge", "TechWise",
        "DataWise", "CloudVault", "ByteLogic", "SkyLogic", "CodeLogic",
        "PixelPeak", "TechPeak", "DataPeak", "CloudWave", "ByteWise",
    ]
    nouns = [
        "Solutions", "Corp", "Inc", "Studios", "Systems",
        "Analytics", "Software", "Labs", "Networks", "Dynamics",
        "Technologies", "Partners", "Group", "Enterprises", "Digital",
        "Innovations", "Platforms", "Services", "Media", "Interactive",
        "Ventures", "Cloud", "Data", "Tech", "Consulting",
    ]

    # Build 100 unique company names deterministically
    names: List[str] = []
    i = 0
    while len(names) < num_customers:
        adj_idx = i % len(adjectives)
        noun_idx = (i // len(adjectives)) % len(nouns)
        name = f"{adjectives[adj_idx]} {nouns[noun_idx]}"
        if name not in names:
            names.append(name)
        i += 1

    start_date = date(2023, 1, 1)
    end_date = date(2024, 6, 1)

    tiers = ["Enterprise", "Pro", "Basic"]
    tier_weights = [0.30, 0.50, 0.20]

    records: List[Dict[str, Any]] = []
    for idx in range(1, num_customers + 1):
        customer_id = f"CUST{idx:03d}"
        company_name = names[idx - 1]
        signup = rand_date(start_date, end_date)
        tier = choice_weighted(tiers, tier_weights)

        if tier == "Enterprise":
            monthly_value = random.randint(3000, 8000)
        elif tier == "Pro":
            monthly_value = random.randint(800, 2000)
        else:
            monthly_value = random.randint(100, 500)

        # Generate email from company name
        email_prefix = company_name.lower().replace(" ", "").replace(".", "")[:15]
        email = f"contact@{email_prefix}.com"

        records.append(
            {
                "customer_id": customer_id,
                "company_name": company_name,
                "email": email,
                "signup_date": signup.isoformat(),
                "subscription_tier": tier,
                "monthly_value": float(monthly_value),
            }
        )

    return pd.DataFrame.from_records(records)


def _pick_days_in_range(start_day: date, days: int, count: int) -> List[date]:
    """Pick a given number of distinct days within a window.

    Args:
        start_day: Window start date
        days: Window length in days
        count: Number of unique days to pick

    Returns:
        Sorted list of selected dates.
    """
    count = max(0, min(count, days))
    offsets = sorted(random.sample(range(days), count)) if count > 0 else []
    return [start_day + timedelta(days=o) for o in offsets]


def generate_behavior_events(customers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate 90 days of behavior events for each customer.

    Args:
        customers_df: DataFrame of customers

    Returns:
        DataFrame with columns: customer_id, event_date, event_type,
        metric_value, notes

    Customer behavior patterns are defined for three cohorts:
    - Healthy (CUST001-CUST040): 40% - High engagement, no issues
    - Declining (CUST041-CUST080): 40% - Decreasing metrics over time
    - Critical (CUST081-CUST100): 20% - Severe decline, negative sentiment
    """
    today = date.today()
    start = today - timedelta(days=89)

    # Periods: 3 consecutive 30-day windows
    p1_start = start
    p2_start = start + timedelta(days=30)
    p3_start = start + timedelta(days=60)

    def is_healthy(cid: str) -> bool:
        return 1 <= int(cid[-3:]) <= 40

    def is_declining(cid: str) -> bool:
        n = int(cid[-3:])
        return 41 <= n <= 80

    def is_critical(cid: str) -> bool:
        n = int(cid[-3:])
        return 81 <= n <= 100

    support_notes_healthy = [
        "Quick question about API",
        "Minor UI clarification",
        "Feature request",
    ]
    support_notes_declining = [
        "Billing concern",
        "Integration issue",
        "Confusion about permissions",
        "Need help with setup",
    ]
    support_notes_critical = [
        "Very frustrated with downtime",
        "Urgent: System not working",
        "Disappointed with support response time",
        "Escalation requested",
    ]

    records: List[Dict[str, Any]] = []

    for _, row in customers_df.iterrows():
        cid = str(row["customer_id"])  # e.g., CUST001

        # LOGIN EVENTS (daily Bernoulli with trend)
        for i in range(90):
            d = start + timedelta(days=i)
            # Determine period index 0/1/2
            period = 0 if i < 30 else (1 if i < 60 else 2)

            if is_healthy(cid):
                probs = [0.75, 0.75, 0.70]  # ~21-23 logins/month
            elif is_declining(cid):
                probs = [0.65, 0.45, 0.25]  # 15-20, 10-15, 5-10 per month
            elif is_critical(cid):
                probs = [0.40, 0.15, 0.07]  # 10-15, 4-7, 1-3 per month
            else:
                probs = [0.5, 0.4, 0.3]

            if random.random() < probs[period]:
                records.append(
                    {
                        "customer_id": cid,
                        "event_date": d.isoformat(),
                        "event_type": "login",
                        "metric_value": 1,
                        "notes": "",
                    }
                )

        # SUPPORT TICKETS (monthly counts)
        if is_healthy(cid):
            monthly_counts = [random.randint(0, 2) for _ in range(3)]
            notes_pool = support_notes_healthy
        elif is_declining(cid):
            monthly_counts = [random.randint(3, 5) for _ in range(3)]
            notes_pool = support_notes_declining
        else:  # critical
            monthly_counts = [random.randint(5, 8) for _ in range(3)]
            notes_pool = support_notes_critical

        month_starts = [p1_start, p2_start, p3_start]
        for ms, cnt in zip(month_starts, monthly_counts):
            days_chosen = _pick_days_in_range(ms, 30, cnt)
            for d in days_chosen:
                records.append(
                    {
                        "customer_id": cid,
                        "event_date": d.isoformat(),
                        "event_type": "support_ticket",
                        "metric_value": 1,
                        "notes": random.choice(notes_pool),
                    }
                )

        # EMAIL RESPONSE TIME (weekly event)
        for period_idx, ms in enumerate(month_starts):
            # Approx 4-5 weekly events per month
            weekly_days = _pick_days_in_range(ms, 30, 4)
            for d in weekly_days:
                if is_healthy(cid):
                    hours = random.randint(2, 8)
                elif is_declining(cid):
                    if period_idx == 0:
                        hours = random.randint(4, 8)
                    elif period_idx == 1:
                        hours = random.randint(12, 24)
                    else:
                        hours = random.randint(24, 48)
                else:  # critical
                    if period_idx == 0:
                        hours = random.randint(8, 12)
                    elif period_idx == 1:
                        hours = random.randint(24, 48)
                    else:
                        hours = random.randint(48, 96)

                records.append(
                    {
                        "customer_id": cid,
                        "event_date": d.isoformat(),
                        "event_type": "email_response_time",
                        "metric_value": float(hours),
                        "notes": "",
                    }
                )

        # FEATURE USAGE (weekly event with trend)
        for period_idx, ms in enumerate(month_starts):
            weekly_days = _pick_days_in_range(ms, 30, 4)
            for d in weekly_days:
                if is_healthy(cid):
                    features = random.randint(8, 15)
                elif is_declining(cid):
                    if period_idx == 0:
                        features = random.randint(8, 12)
                    elif period_idx == 1:
                        features = random.randint(5, 8)
                    else:
                        features = random.randint(3, 5)
                else:  # critical
                    if period_idx == 0:
                        features = random.randint(6, 10)
                    elif period_idx == 1:
                        features = random.randint(2, 4)
                    else:
                        features = random.randint(1, 2)

                records.append(
                    {
                        "customer_id": cid,
                        "event_date": d.isoformat(),
                        "event_type": "feature_usage",
                        "metric_value": int(features),
                        "notes": "",
                    }
                )

        # PAYMENT DELAY (monthly, with issues for declining/critical)
        delays = []
        if is_healthy(cid):
            delays = [0, 0, 0]
        elif is_declining(cid):
            delays = [0, random.choice([0, random.randint(2, 7)]), random.choice([0, random.randint(2, 7)])]
        else:  # critical
            delays = [0, random.randint(10, 30), random.randint(10, 30)]

        for d_val, ms in zip(delays, month_starts):
            # place payment events near the end of the month
            d = ms + timedelta(days=random.randint(20, 29))
            records.append(
                {
                    "customer_id": cid,
                    "event_date": d.isoformat(),
                    "event_type": "payment_delay",
                    "metric_value": int(d_val),
                    "notes": "On time" if d_val == 0 else f"Late by {d_val} days",
                }
            )

    return pd.DataFrame.from_records(records)


def generate_churned_customers(num_customers: int = 20) -> pd.DataFrame:
    """
    Generate historical churned customers with decay patterns.

    Args:
        num_customers: Number of churned customers to generate

    Returns:
        DataFrame with columns: customer_id, company_name, signup_date,
        subscription_tier, monthly_value, churn_date, churn_reason,
        days_until_churned, decay_pattern
    """
    alt_adjectives = [
        "Silverline",
        "Vertex",
        "Orbit",
        "Cinder",
        "Helix",
        "Nimbus",
        "Vector",
        "Polar",
        "Radial",
        "Summit",
        "NorthStar",
        "Photon",
        "Crux",
        "Astra",
        "Signal",
        "Cortex",
        "Monarch",
        "Ion",
        "Spectrum",
        "Stratus",
        "Vantage",
        "Pulse",
    ]
    alt_nouns = [
        "Industries",
        "Enterprises",
        "Holdings",
        "Ventures",
        "Collective",
        "Works",
        "Solutions",
        "Group",
        "Dynamics",
        "Networks",
    ]

    names: List[str] = []
    i = 0
    while len(names) < num_customers:
        name = f"{alt_adjectives[i % len(alt_adjectives)]} {alt_nouns[i % len(alt_nouns)]}"
        if name not in names:
            names.append(name)
        i += 1

    tiers = ["Enterprise", "Pro", "Basic"]
    tier_weights = [0.25, 0.50, 0.25]

    reasons = [
        "poor_support_experience",
        "pricing_too_high",
        "missing_features",
        "competitor_switch",
        "company_shutdown",
    ]
    reason_weights = [0.30, 0.25, 0.20, 0.15, 0.10]

    reason_to_pattern = {
        "poor_support_experience": "Negative support ticket sentiment, increasing response time expectations",
        "pricing_too_high": "Payment delays increasing, questioning value, reduced feature usage",
        "missing_features": "Low feature adoption, frequent feature requests, exploring alternatives",
        "competitor_switch": "Sudden drop in login frequency, minimal engagement last 30 days",
        "company_shutdown": "Abrupt cessation of all activity, notification received",
    }

    start_signup = date(2022, 1, 1)
    end_signup = date(2023, 12, 1)

    records: List[Dict[str, Any]] = []
    for idx in range(1, num_customers + 1):
        cid = f"CHURN{idx:03d}"
        company_name = names[idx - 1]
        signup = rand_date(start_signup, end_signup)

        tier = choice_weighted(tiers, tier_weights)
        if tier == "Enterprise":
            monthly_value = random.randint(3000, 8000)
        elif tier == "Pro":
            monthly_value = random.randint(800, 2000)
        else:
            monthly_value = random.randint(100, 500)

        days_until = random.randint(30, 180)
        churn_dt = signup + timedelta(days=days_until)

        reason = choice_weighted(reasons, reason_weights)
        pattern = reason_to_pattern[reason]

        records.append(
            {
                "customer_id": cid,
                "company_name": company_name,
                "signup_date": signup.isoformat(),
                "subscription_tier": tier,
                "monthly_value": float(monthly_value),
                "churn_date": churn_dt.isoformat(),
                "churn_reason": reason,
                "days_until_churned": int(days_until),
                "decay_pattern": pattern,
            }
        )

    return pd.DataFrame.from_records(records)


def main() -> None:
    """Main execution to generate datasets and print summaries.

    Steps:
    1. Ensure `data/` directory exists
    2. Generate customers, behavior events (90 days), churned customers
    3. Save all to CSV files
    4. Print dataset summary statistics
    """
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    ensure_data_dir(data_dir)

    print("Generating customers (100)...")
    customers_df = generate_customers(100)
    customers_path = os.path.join(data_dir, "customers.csv")
    customers_df.to_csv(customers_path, index=False)

    print("Generating 90-day behavior events...")
    events_df = generate_behavior_events(customers_df)
    events_path = os.path.join(data_dir, "behavior_events.csv")
    events_df.to_csv(events_path, index=False)

    print("Generating churned customers (20)...")
    churned_df = generate_churned_customers(20)
    churned_path = os.path.join(data_dir, "churned_customers.csv")
    churned_df.to_csv(churned_path, index=False)

    # Summaries
    print("\nSummary Statistics:")
    print("- Customers by tier:")
    print(customers_df["subscription_tier"].value_counts())

    print("\n- Behavior events by type:")
    print(events_df["event_type"].value_counts())

    print("\n- Churned customers by reason:")
    print(churned_df["churn_reason"].value_counts())

    print("\nFiles written:")
    print(f"  - {customers_path}")
    print(f"  - {events_path}")
    print(f"  - {churned_path}")


if __name__ == "__main__":
    main()
