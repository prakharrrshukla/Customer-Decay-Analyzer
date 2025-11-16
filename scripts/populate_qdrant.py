"""
Script to populate Qdrant vector store with churned customers.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from typing import Dict, Any
import pandas as pd
from dotenv import load_dotenv

from models.vector_store import QdrantVectorStore
from utils.data_helpers import load_churned_customers, get_data_dir


# Load environment
load_dotenv()


def estimate_metrics_from_churn(churn_reason: str, decay_pattern: str) -> Dict[str, Any]:
    """
    Estimate behavioral metrics based on churn reason and decay pattern.
    
    Args:
        churn_reason: Why customer churned
        decay_pattern: How they declined (rapid/gradual)
    
    Returns:
        Dict with estimated metrics for vector creation
    """
    # Base metrics (normalized 0-1)
    metrics = {
        "engagement_score": 0.3,
        "login_frequency": 0.3,
        "feature_usage_score": 0.3,
        "email_open_rate": 0.3,
        "support_ticket_trend": 0.5,  # Neutral
        "payment_issues": 0.5,
        "sentiment_score": 0.0,  # Negative
        "login_trend": -1.0,  # Declining
        "engagement_trend": -1.0,  # Declining
        "feature_trend": -1.0,  # Declining
    }
    
    # Adjust based on churn reason
    if churn_reason == "poor_support":
        metrics["support_ticket_trend"] = 0.8  # Many tickets
        metrics["sentiment_score"] = -0.5  # Very negative
        metrics["engagement_score"] = 0.4  # Some engagement
        
    elif churn_reason == "pricing":
        metrics["payment_issues"] = 0.9  # Payment problems
        metrics["feature_usage_score"] = 0.6  # Used features but too expensive
        metrics["engagement_score"] = 0.5
        
    elif churn_reason == "missing_features":
        metrics["feature_usage_score"] = 0.2  # Low usage
        metrics["engagement_score"] = 0.4
        metrics["support_ticket_trend"] = 0.6  # Some feature requests
        
    elif churn_reason == "competitor":
        metrics["engagement_score"] = 0.3
        metrics["login_frequency"] = 0.2  # Stopped logging in
        metrics["feature_usage_score"] = 0.3
        
    elif churn_reason == "business_shutdown":
        metrics["engagement_score"] = 0.1  # Very low
        metrics["login_frequency"] = 0.1
        metrics["feature_usage_score"] = 0.1
        metrics["payment_issues"] = 0.8
    
    # Adjust based on decay pattern
    if decay_pattern == "rapid":
        # Sharp decline
        metrics["login_trend"] = -1.0
        metrics["engagement_trend"] = -1.0
        metrics["engagement_score"] *= 0.5  # Cut in half
        metrics["login_frequency"] *= 0.3
        
    elif decay_pattern == "gradual":
        # Slow decline
        metrics["login_trend"] = -0.5
        metrics["engagement_trend"] = -0.5
        metrics["engagement_score"] *= 0.7
        metrics["login_frequency"] *= 0.6
    
    return metrics


def populate_qdrant():
    """
    Load churned customers and populate Qdrant vector store.
    """
    print("\n" + "="*60)
    print("Populating Qdrant with Churned Customers")
    print("="*60 + "\n")
    
    # Initialize vector store
    print("1. Initializing Qdrant vector store...")
    vector_store = QdrantVectorStore()
    
    # Create collection if needed
    print("2. Creating/verifying collection...")
    vector_store.create_collection()
    
    # Load churned customers
    print("3. Loading churned customers...")
    churned_df = load_churned_customers()
    print(f"   Found {len(churned_df)} churned customers\n")
    
    # Process each churned customer
    print("4. Processing and uploading vectors...")
    success_count = 0
    
    for idx, row in churned_df.iterrows():
        customer_id = row["customer_id"]
        
        # Estimate metrics based on churn info
        metrics = estimate_metrics_from_churn(
            row["churn_reason"],
            row["decay_pattern"]
        )
        
        # Create behavior vector
        behavior_vector = vector_store.create_behavior_vector(metrics)
        
        # Prepare metadata
        metadata = {
            "customer_id": customer_id,
            "churned": True,
            "churn_date": row["churn_date"],
            "churn_reason": row["churn_reason"],
            "decay_pattern": row["decay_pattern"],
            "days_until_churned": int(row["days_until_churned"]),
            "monthly_value": float(row["monthly_value"]),
            "tier": row["tier"],
        }
        
        try:
            # Upload to Qdrant
            vector_store.upload_customer(behavior_vector, metadata)
            success_count += 1
            
            # Progress update every 5 customers
            if success_count % 5 == 0:
                print(f"   Processed {success_count}/{len(churned_df)} customers...")
                
        except Exception as e:
            print(f"   ❌ Error uploading {customer_id}: {e}")
    
    print(f"\n✅ Successfully uploaded {success_count}/{len(churned_df)} customers")
    
    # Get collection info
    print("\n5. Verifying collection...")
    info = vector_store.get_collection_info()
    print(f"   Collection: {info['collection_name']}")
    print(f"   Points: {info['points_count']}")
    print(f"   Vectors: {info['vectors_count']}")
    
    print("\n" + "="*60)
    print("✅ Qdrant population complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        populate_qdrant()
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("   Run scripts/generate_sample_data.py first.\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
