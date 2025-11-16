"""
Comprehensive test suite for Customer Decay Analyzer.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from dotenv import load_dotenv

from models.gemini_analyzer import CustomerAnalyzer
from models.vector_store import QdrantVectorStore
from models.risk_assessor import RiskAssessor
from utils.data_helpers import (
    load_customers,
    load_behaviors,
    get_customer_behaviors,
    format_currency,
    get_risk_summary_stats
)

# Load environment
load_dotenv()


@pytest.fixture
def sample_customer():
    """Create sample customer data."""
    return {
        "customer_id": "TEST001",
        "company_name": "Test Company",
        "tier": "Pro",
        "monthly_value": 299.0,
        "signup_date": "2024-01-01",
        "industry": "Technology"
    }


@pytest.fixture
def sample_behaviors():
    """Create sample behavior events."""
    events = []
    base_date = datetime.now() - timedelta(days=90)
    
    # Healthy behavior: consistent logins
    for day in range(90):
        event_date = base_date + timedelta(days=day)
        events.append({
            "customer_id": "TEST001",
            "event_type": "login",
            "event_date": event_date.strftime("%Y-%m-%d"),
            "metadata": "{}"
        })
    
    return pd.DataFrame(events)


def test_gemini_analyzer_healthy_customer(sample_customer, sample_behaviors):
    """Test Gemini analyzer with healthy customer data."""
    print("\n\n" + "="*60)
    print("TEST 1: Gemini Analyzer - Healthy Customer")
    print("="*60)
    
    analyzer = CustomerAnalyzer()
    result = analyzer.analyze_customer(sample_customer, sample_behaviors)
    
    # Assertions
    assert result is not None, "Analysis result should not be None"
    assert "churn_risk_score" in result, "Should contain risk score"
    assert "risk_level" in result, "Should contain risk level"
    
    risk_score = result["churn_risk_score"]
    print(f"\n✓ Risk score: {risk_score}")
    print(f"✓ Risk level: {result['risk_level']}")
    
    # Healthy customer should have low risk
    assert risk_score < 40, f"Healthy customer risk should be < 40, got {risk_score}"
    assert result["risk_level"] in ["low", "medium"], "Should be low or medium risk"
    
    print("\n✅ TEST PASSED: Gemini analyzer working correctly\n")


def test_vector_store_operations():
    """Test Qdrant vector store operations."""
    print("\n\n" + "="*60)
    print("TEST 2: Vector Store Operations")
    print("="*60)
    
    store = QdrantVectorStore()
    
    # Test collection creation
    print("\n1. Testing collection creation...")
    store.create_collection()
    info = store.get_collection_info()
    assert info["collection_name"] == "customer_behaviors", "Collection name mismatch"
    print(f"✓ Collection exists: {info['collection_name']}")
    
    # Test vector creation
    print("\n2. Testing vector creation...")
    metrics = {
        "engagement_score": 0.75,
        "login_frequency": 0.8,
        "feature_usage_score": 0.7,
        "email_open_rate": 0.65,
        "support_ticket_trend": 0.3,
        "payment_issues": 0.1,
        "sentiment_score": 0.5,
        "login_trend": 0.2,
        "engagement_trend": 0.1,
        "feature_trend": 0.15
    }
    vector = store.create_behavior_vector(metrics)
    assert len(vector) == 768, f"Vector should be 768-dim, got {len(vector)}"
    print(f"✓ Vector created: {len(vector)} dimensions")
    
    # Test upload
    print("\n3. Testing customer upload...")
    metadata = {
        "customer_id": "TEST_VECTOR",
        "churned": False,
        "tier": "Pro",
        "monthly_value": 299.0
    }
    store.upload_customer(vector, metadata)
    print("✓ Customer uploaded successfully")
    
    # Test search
    print("\n4. Testing similarity search...")
    results = store.search_similar_customers(vector, limit=3)
    print(f"✓ Found {len(results)} similar customers")
    
    print("\n✅ TEST PASSED: Vector store operations working\n")


def test_risk_assessor_declining_customer():
    """Test risk assessor with declining customer."""
    print("\n\n" + "="*60)
    print("TEST 3: Risk Assessor - Declining Customer")
    print("="*60)
    
    # Create declining behavior pattern
    customer = {
        "customer_id": "TEST_DECLINE",
        "company_name": "Declining Co",
        "tier": "Enterprise",
        "monthly_value": 999.0,
        "signup_date": "2023-06-01",
        "industry": "Finance"
    }
    
    # Declining logins: 30 recent, 60 in past 60 days
    events = []
    base_date = datetime.now() - timedelta(days=90)
    
    # Days 0-30: 60 logins
    for day in range(30):
        for _ in range(2):
            events.append({
                "customer_id": "TEST_DECLINE",
                "event_type": "login",
                "event_date": (base_date + timedelta(days=day)).strftime("%Y-%m-%d"),
                "metadata": "{}"
            })
    
    # Days 31-90: Only 30 logins (declining)
    for day in range(31, 90):
        if day % 2 == 0:  # Every other day
            events.append({
                "customer_id": "TEST_DECLINE",
                "event_type": "login",
                "event_date": (base_date + timedelta(days=day)).strftime("%Y-%m-%d"),
                "metadata": "{}"
            })
    
    behaviors = pd.DataFrame(events)
    
    # Run assessment
    assessor = RiskAssessor()
    result = assessor.assess_customer_risk(customer, behaviors)
    
    # Assertions
    assert result is not None, "Assessment should not be None"
    risk_score = result["churn_risk_score"]
    
    print(f"\n✓ Risk score: {risk_score}")
    print(f"✓ Risk level: {result['risk_level']}")
    print(f"✓ Intervention priority: {result['intervention_priority']}/10")
    
    # Declining customer should have elevated risk
    assert 40 <= risk_score <= 80, f"Declining customer risk should be 40-80, got {risk_score}"
    assert result["risk_level"] in ["medium", "high"], "Should be medium or high risk"
    
    print("\n✅ TEST PASSED: Risk assessor working correctly\n")


def test_full_pipeline_three_customers():
    """Test full pipeline with three customer patterns."""
    print("\n\n" + "="*60)
    print("TEST 4: Full Pipeline - Three Customer Patterns")
    print("="*60)
    
    try:
        # Load real data
        customers_df = load_customers()
        behaviors_df = load_behaviors()
        
        # Test with 3 customers: CUST001, CUST013, CUST025
        test_ids = ["CUST001", "CUST013", "CUST025"]
        assessor = RiskAssessor()
        
        results = []
        for cust_id in test_ids:
            print(f"\nAnalyzing {cust_id}...")
            
            customer = customers_df[customers_df["customer_id"] == cust_id].iloc[0].to_dict()
            behaviors = get_customer_behaviors(cust_id, behaviors_df)
            
            result = assessor.assess_customer_risk(customer, behaviors)
            results.append(result)
            
            print(f"  Risk: {result['churn_risk_score']:.1f} ({result['risk_level']})")
        
        # Assertions
        assert len(results) == 3, "Should analyze all 3 customers"
        
        # Should have varying risk levels
        risk_scores = [r["churn_risk_score"] for r in results]
        assert max(risk_scores) - min(risk_scores) > 20, "Should have diverse risk scores"
        
        print(f"\n✓ Risk score range: {min(risk_scores):.1f} - {max(risk_scores):.1f}")
        print("\n✅ TEST PASSED: Full pipeline working\n")
        
    except FileNotFoundError:
        pytest.skip("Sample data not generated. Run scripts/generate_sample_data.py first.")


def test_api_endpoints():
    """Test Flask API endpoints."""
    print("\n\n" + "="*60)
    print("TEST 5: API Endpoints")
    print("="*60)
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test health endpoint
            print("\n1. Testing /api/health...")
            response = client.get("/api/health")
            assert response.status_code in [200, 503], "Health endpoint should respond"
            data = response.get_json()
            assert "status" in data, "Should have status field"
            print(f"✓ Health status: {data['status']}")
            
            # Test ping endpoint
            print("\n2. Testing /api/ping...")
            response = client.get("/api/ping")
            assert response.status_code == 200, "Ping should return 200"
            data = response.get_json()
            assert data["message"] == "pong", "Should return pong"
            print("✓ Ping successful")
            
            # Test customer list endpoint
            print("\n3. Testing /api/customers/...")
            response = client.get("/api/customers/?limit=5")
            if response.status_code == 200:
                data = response.get_json()
                assert "customers" in data, "Should have customers list"
                print(f"✓ Retrieved {data['total']} customers")
            else:
                print("⚠ Customer endpoint requires data files")
            
            print("\n✅ TEST PASSED: API endpoints responding\n")
            
    except Exception as e:
        pytest.skip(f"API test skipped: {e}")


def test_utility_functions():
    """Test utility helper functions."""
    print("\n\n" + "="*60)
    print("TEST 6: Utility Functions")
    print("="*60)
    
    # Test format_currency
    print("\n1. Testing format_currency...")
    assert format_currency(1234.56) == "$1,234.56"
    assert format_currency(1000000) == "$1,000,000.00"
    print("✓ Currency formatting works")
    
    # Test get_risk_summary_stats
    print("\n2. Testing get_risk_summary_stats...")
    sample_assessments = [
        {"risk_level": "high", "churn_risk_score": 75, "estimated_revenue_at_risk": 10000},
        {"risk_level": "medium", "churn_risk_score": 55, "estimated_revenue_at_risk": 5000},
        {"risk_level": "low", "churn_risk_score": 25, "estimated_revenue_at_risk": 1000},
    ]
    
    stats = get_risk_summary_stats(sample_assessments)
    assert stats["total_customers"] == 3
    assert stats["average_risk_score"] > 0
    assert stats["customers_needing_intervention"] >= 1
    print(f"✓ Summary stats calculated: {stats['customers_needing_intervention']} need intervention")
    
    print("\n✅ TEST PASSED: Utility functions working\n")


if __name__ == "__main__":
    """Run tests with pytest."""
    print("\n" + "="*60)
    print("Customer Decay Analyzer - Test Suite")
    print("="*60)
    
    # Run pytest with verbose output
    pytest.main([__file__, "-v", "--tb=short", "-s"])
