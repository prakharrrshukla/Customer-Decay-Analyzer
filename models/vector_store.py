"""
Qdrant vector database interface for customer behavior similarity search.

Stores customer behaviors as 768-dimensional vectors and finds customers
with similar patterns to those who churned historically.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, List, Optional

import numpy as np
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

load_dotenv()


class QdrantVectorStore:
    """
    Manages customer behavior vectors in Qdrant Cloud.
    """
    
    def __init__(self, collection_name: str = "customer_behaviors") -> None:
        """
        Initialize Qdrant connection.
        
        Args:
            collection_name: Name of vector collection
        
        Raises:
            ValueError: If Qdrant credentials missing
        """
        url = os.getenv("QDRANT_URL")
        api_key = os.getenv("QDRANT_API_KEY")
        
        if not url or not api_key:
            raise ValueError(
                "Missing Qdrant credentials: QDRANT_URL and QDRANT_API_KEY required"
            )
        
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
    
    def create_collection(self, dimension: int = 768, recreate: bool = False) -> None:
        """
        Create Qdrant collection if it doesn't exist.
        
        Args:
            dimension: Vector dimension (default 768)
            recreate: If True, delete and recreate collection
        """
        if recreate:
            try:
                self.client.delete_collection(self.collection_name)
                print(f"  Deleted existing collection '{self.collection_name}'")
            except Exception:
                pass
        
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
            )
            print(f"✓ Created collection '{self.collection_name}' ({dimension} dims, COSINE)")
        except Exception as e:
            msg = str(e).lower()
            if "already exists" in msg or "exists" in msg:
                print(f"ℹ Collection '{self.collection_name}' already exists")
            else:
                raise
    
    def normalize_value(self, value: float, min_val: float, max_val: float) -> float:
        """
        Normalize value to 0-1 range.
        
        Args:
            value: Value to normalize
            min_val: Minimum expected value
            max_val: Maximum expected value
        
        Returns:
            Normalized value between 0 and 1
        """
        if max_val == min_val:
            return 0.5
        norm = (float(value) - float(min_val)) / float(max_val - min_val)
        return float(np.clip(norm, 0.0, 1.0))
    
    def create_behavior_vector(self, behavior_metrics: Dict[str, Any]) -> List[float]:
        """
        Convert behavior metrics to 768-dimensional vector.
        
        Args:
            behavior_metrics: Dict with keys:
                - login_frequency: logins per month (0-30)
                - feature_usage: features per week (0-20)
                - support_ticket_count: tickets per month (0-15)
                - email_response_time: hours (0-100)
                - payment_delay_days: days (0-30)
                - session_duration: minutes (0-120)
                - sentiment_score: -1 to 1
                - months_as_customer: months (0-36)
                - login_trend: -1 to 1
                - engagement_score: 0 to 1
        
        Returns:
            768-dimensional vector as list of floats
        """
        # Defaults
        login_frequency = float(behavior_metrics.get("login_frequency", 15))
        feature_usage = float(behavior_metrics.get("feature_usage", 10))
        support_ticket_count = float(behavior_metrics.get("support_ticket_count", 3))
        email_response_time = float(behavior_metrics.get("email_response_time", 24))
        payment_delay_days = float(behavior_metrics.get("payment_delay_days", 0))
        session_duration = float(behavior_metrics.get("session_duration", 30))
        sentiment_score = float(behavior_metrics.get("sentiment_score", 0))  # -1..1
        months_as_customer = float(behavior_metrics.get("months_as_customer", 12))
        login_trend = float(behavior_metrics.get("login_trend", 0))  # -1..1
        engagement_score = float(behavior_metrics.get("engagement_score", 0.5))
        
        vec = [0.0] * 768
        vec[0] = self.normalize_value(login_frequency, 0, 30)
        vec[1] = self.normalize_value(feature_usage, 0, 20)
        vec[2] = self.normalize_value(support_ticket_count, 0, 15)
        vec[3] = self.normalize_value(email_response_time, 0, 100)
        vec[4] = self.normalize_value(payment_delay_days, 0, 30)
        vec[5] = self.normalize_value(session_duration, 0, 120)
        vec[6] = self.normalize_value((sentiment_score + 1.0) / 2.0, 0, 1)
        vec[7] = self.normalize_value(months_as_customer, 0, 36)
        vec[8] = self.normalize_value((login_trend + 1.0) / 2.0, 0, 1)
        vec[9] = float(np.clip(engagement_score, 0.0, 1.0))
        # Dimensions 10-767 remain zero
        
        return vec
    
    def _stable_numeric_id(self, customer_id: str) -> int:
        """Create a stable numeric ID from a string using SHA1."""
        h = hashlib.sha1(customer_id.encode("utf-8")).hexdigest()
        return int(h[:12], 16)
    
    def upload_customer(
        self,
        customer_id: str,
        behavior_vector: List[float],
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Upload customer behavior vector to Qdrant.
        
        Args:
            customer_id: Unique customer ID
            behavior_vector: 768-dimensional vector
            metadata: Customer metadata dict with all relevant fields
        
        Returns:
            True if successful, False otherwise
        """
        try:
            pid = self._stable_numeric_id(customer_id)
            payload = {**metadata, "customer_id": customer_id}
            point = PointStruct(id=pid, vector=behavior_vector, payload=payload)
            self.client.upsert(collection_name=self.collection_name, points=[point])
            return True
        except Exception as e:
            print(f"Failed to upload customer '{customer_id}': {e}")
            return False
    
    def search_similar_customers(
        self,
        query_vector: List[float],
        limit: int = 5,
        filter_churned: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find customers with similar behavior patterns.
        
        Args:
            query_vector: 768-dimensional behavior vector
            limit: Number of results
            filter_churned: If True, only return churned customers
        
        Returns:
            List of dicts with customer info and similarity scores
        """
        qf: Optional[Filter] = None
        if filter_churned:
            qf = Filter(must=[FieldCondition(key="churned", match=MatchValue(value=True))])
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=qf,
        )
        
        output: List[Dict[str, Any]] = []
        for r in results:
            payload = r.payload or {}
            output.append({
                "customer_id": payload.get("customer_id"),
                "similarity_score": round(float(r.score), 4),
                "company_name": payload.get("company_name"),
                "churn_reason": payload.get("churn_reason"),
                "decay_pattern": payload.get("decay_pattern"),
                "days_until_churned": payload.get("days_until_churned"),
                "subscription_tier": payload.get("subscription_tier"),
                "monthly_value": payload.get("monthly_value"),
                "payload": payload,
            })
        
        return output
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Returns:
            Dict with collection metadata
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count if hasattr(info, 'vectors_count') else 0,
                "points_count": info.points_count if hasattr(info, 'points_count') else 0,
                "status": "ready",
            }
        except Exception as e:
            return {
                "name": self.collection_name,
                "status": "error",
                "error": str(e),
            }


# Test script
if __name__ == "__main__":
    """
    Test vector store with sample operations.
    """
    print("\n" + "="*70)
    print("QDRANT VECTOR STORE TEST")
    print("="*70 + "\n")
    
    store = QdrantVectorStore("test_behaviors")
    
    print("Creating collection...")
    store.create_collection(dimension=768, recreate=True)
    
    print("\nCreating sample behavior vector...")
    metrics = {
        "login_frequency": 20,
        "feature_usage": 12,
        "support_ticket_count": 1,
        "email_response_time": 6,
        "payment_delay_days": 0,
        "session_duration": 45,
        "sentiment_score": 0.4,
        "months_as_customer": 18,
        "login_trend": 0.2,
        "engagement_score": 0.8,
    }
    vec = store.create_behavior_vector(metrics)
    print(f"  Vector dimensions: {len(vec)}")
    print(f"  First 10 values: {[round(v, 3) for v in vec[:10]]}")
    
    print("\nUploading test customer...")
    metadata = {
        "company_name": "Test Company",
        "churned": False,
        "subscription_tier": "Pro",
        "monthly_value": 1200,
    }
    success = store.upload_customer("TEST001", vec, metadata)
    print(f"  Upload {'succeeded' if success else 'failed'}")
    
    print("\nGetting collection info...")
    info = store.get_collection_info()
    print(f"  Status: {info['status']}")
    print(f"  Points: {info.get('points_count', 0)}")
    
    print("\n" + "="*70)
    print("✅ Vector store test completed!")
    print("="*70 + "\n")
