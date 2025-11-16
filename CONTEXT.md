# Customer Decay Analyzer - Technical Context Document

## Project Overview

**Purpose**: Churn prediction system that detects customer decay 90 days in advance using AI-powered behavioral analysis and vector similarity search.

**Core Value Proposition**: Identify at-risk customers before they churn by analyzing engagement patterns against historical churn data, enabling proactive intervention.

## Business Problem

Traditional churn detection reacts to cancellations. This system **predicts** decay by:
1. Analyzing current customer behavior patterns
2. Finding similar patterns in historical churned customers
3. Using AI to interpret complex behavioral signals
4. Providing actionable intervention recommendations

## Technology Stack

### Backend Framework
- **Flask 3.0.0**: REST API server
- **flask-cors 4.0.0**: Cross-origin request handling

### AI & Machine Learning
- **google-generativeai 0.3.1**: Gemini API client
- **Model**: `gemini-2.0-flash` (free tier optimized, production-ready)
- **scikit-learn 1.3.0**: Data preprocessing and normalization

### Vector Database
- **qdrant-client 1.7.0**: Vector similarity search
- **Instance**: Qdrant Cloud (eu-west-1-0)
- **Vector Dimensions**: 768 (behavioral feature space)

### Data Processing
- **pandas 2.1.0**: CSV processing and data manipulation
- **numpy 1.24.0**: Numerical computations

### Development Tools
- **python-dotenv 1.0.0**: Environment configuration
- **pytest 7.4.0**: Unit testing
- **pytest-cov 4.1.0**: Code coverage

## Data Schemas

### 1. Customer CSV (`data/customers.csv`)
```csv
customer_id, company_name, signup_date, subscription_tier, monthly_value
```

**Fields**:
- `customer_id`: Unique identifier (e.g., CUST001)
- `company_name`: Customer company name
- `signup_date`: ISO date format (YYYY-MM-DD)
- `subscription_tier`: Enum [Starter, Professional, Enterprise]
- `monthly_value`: USD monthly revenue (float)

**Example**:
```csv
CUST001, Acme Corp, 2023-01-15, Enterprise, 5000
CUST002, TechStart Inc, 2023-03-20, Professional, 1500
```

### 2. Behavior Events CSV (`data/behavior_events.csv`)
```csv
customer_id, event_date, event_type, metric_value, notes
```

**Event Types**:
- `login`: Daily login count
- `support_ticket`: Ticket opened (1 per event)
- `email_response_time`: Hours to respond to emails
- `feature_usage`: Number of features used per day
- `payment_delay`: Days past due on invoice

**Example**:
```csv
CUST001, 2024-10-01, login, 15, "Active usage"
CUST001, 2024-10-15, support_ticket, 1, "Billing question"
CUST001, 2024-10-20, payment_delay, 5, "Invoice 30 days late"
```

### 3. Churned Customers CSV (`data/churned_customers.csv`)
All customer fields plus:
- `churn_date`: Date customer cancelled (ISO format)
- `churn_reason`: Free text reason
- `days_until_churned`: Days from signup to churn
- `decay_pattern`: JSON string of behavioral signals

**Example**:
```csv
CUST099, Former Corp, 2023-01-10, Enterprise, 4500, 2024-03-15, "Product not meeting needs", 430, "decreased_logins,slow_email_responses"
```

### 4. Risk Assessment Output JSON
```json
{
  "customer_id": "CUST001",
  "customer_name": "Acme Corp",
  "subscription_tier": "Enterprise",
  "monthly_value": 5000,
  "churn_risk_score": 85,
  "risk_level": "critical",
  "decay_signals": [
    "decreased_logins",
    "payment_delays",
    "slow_email_responses"
  ],
  "primary_concern": "Customer showing significant disengagement pattern",
  "recommended_intervention": "Immediate CSM outreach with product review",
  "urgency": "critical",
  "similar_churned_customers": [
    {
      "customer_id": "CUST099",
      "similarity_score": 0.92,
      "days_until_churned": 45,
      "churn_reason": "Product not meeting needs"
    }
  ],
  "predicted_churn_date": "2025-02-15",
  "confidence_level": "high",
  "analysis_timestamp": "2025-01-15T10:30:00Z"
}
```

**Risk Levels**:
- `low`: 0-25 (routine monitoring)
- `medium`: 26-50 (increased attention)
- `high`: 51-75 (proactive outreach)
- `critical`: 76-100 (immediate intervention)

## Vector Embedding Structure

### 768-Dimensional Behavioral Fingerprint
**Dimensions 0-9**: Core behavioral metrics (normalized 0-1)

| Dim | Feature | Range | Normalization |
|-----|---------|-------|---------------|
| 0 | login_frequency | 0-30 logins/month | x / 30 |
| 1 | feature_usage | 0-20 features/day | x / 20 |
| 2 | support_ticket_count | 0-15 tickets/month | x / 15 |
| 3 | email_response_time | 0-100 hours | x / 100 |
| 4 | payment_delay_days | 0-30 days | x / 30 |
| 5 | session_duration | 0-120 minutes/session | x / 120 |
| 6 | sentiment_score | -1 to 1 | (x + 1) / 2 |
| 7 | months_as_customer | 0-36 months | x / 36 |
| 8 | login_trend | -1 to 1 (decreasing/increasing) | (x + 1) / 2 |
| 9 | engagement_score | 0-1 (composite) | direct |

**Dimensions 10-767**: Zero-padded for future feature expansion

**Vector Generation Logic**:
```python
def create_behavior_vector(customer_data: dict) -> List[float]:
    """
    Generate 768-dim vector from customer behavior metrics.
    
    Args:
        customer_data: Dict with behavior metrics
        
    Returns:
        List of 768 floats normalized to [0, 1]
    """
    vector = [0.0] * 768
    vector[0] = min(customer_data['login_count'] / 30, 1.0)
    vector[1] = min(customer_data['feature_usage'] / 20, 1.0)
    # ... additional dimensions
    return vector
```

## API Endpoints

### Health & Status
```
GET /api/health
Response: {
  "status": "healthy",
  "services": {
    "gemini": "connected",
    "qdrant": "connected"
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Customer Management
```
GET /api/customers
Query Params: ?status=active&tier=Enterprise&min_risk=50
Response: [
  {
    "customer_id": "CUST001",
    "company_name": "Acme Corp",
    "subscription_tier": "Enterprise",
    "monthly_value": 5000,
    "current_risk_score": 85,
    "risk_level": "critical"
  }
]
```

```
GET /api/customers/at-risk
Query Params: ?threshold=50&limit=20
Response: Array of customers with risk_score >= threshold
```

### Risk Analysis
```
GET /api/customers/<customer_id>/analysis
Response: Full risk assessment JSON (see Data Schemas section)
```

```
POST /api/analyze-all
Triggers batch analysis of all active customers
Response: {
  "status": "processing",
  "customers_queued": 150,
  "estimated_completion": "2025-01-15T10:45:00Z"
}
```

### Analytics Dashboard
```
GET /api/dashboard/stats
Response: {
  "total_customers": 200,
  "active_customers": 180,
  "at_risk_count": 35,
  "critical_count": 8,
  "avg_risk_score": 32.5,
  "churn_rate_30d": 2.5,
  "intervention_success_rate": 78.3
}
```

## Gemini AI Integration

### Prompt Strategy
**Goal**: Extract structured risk assessments from behavioral data using natural language understanding.

**Prompt Template**:
```python
ANALYSIS_PROMPT = """
You are a customer success AI analyzing churn risk. Return ONLY valid JSON.

Customer Context:
- ID: {customer_id}
- Company: {company_name}
- Tier: {subscription_tier}
- Monthly Value: ${monthly_value}
- Tenure: {months_as_customer} months

Behavior Metrics (last 30 days):
- Logins: {login_count} (previous: {prev_login_count})
- Support Tickets: {ticket_count}
- Email Response Time: {email_response_hours}h avg
- Payment Status: {payment_delay_days} days delayed
- Feature Usage: {feature_usage_count} features

Similar Churned Customers:
{similar_customers_json}

Analyze decay patterns and return JSON:
{{
  "churn_risk_score": <0-100>,
  "risk_level": "<low|medium|high|critical>",
  "decay_signals": ["signal1", "signal2"],
  "primary_concern": "<one sentence>",
  "recommended_intervention": "<specific action>",
  "urgency": "<low|medium|high|critical>",
  "predicted_churn_date": "YYYY-MM-DD",
  "confidence_level": "<low|medium|high>"
}}
"""
```

**Response Validation**:
- Ensure JSON-only output (no markdown, no explanations)
- Validate all required fields present
- Verify score ranges (0-100)
- Check enum values match expected values

**Error Handling**:
```python
try:
    response = model.generate_content(prompt)
    data = json.loads(response.text)
    validate_risk_assessment(data)
except json.JSONDecodeError:
    # Fallback to rule-based scoring
    data = calculate_rule_based_score(customer_data)
```

## Qdrant Vector Operations

### Collection Configuration
```python
from qdrant_client.models import Distance, VectorParams

collection_config = {
    "vectors": VectorParams(
        size=768,
        distance=Distance.COSINE  # Best for behavioral similarity
    )
}
```

### Similarity Search
```python
def find_similar_churned_customers(
    customer_vector: List[float],
    limit: int = 5
) -> List[dict]:
    """
    Find churned customers with similar behavioral patterns.
    
    Args:
        customer_vector: 768-dim behavior vector
        limit: Max results to return
        
    Returns:
        List of similar customers with scores
    """
    results = qdrant_client.search(
        collection_name="churned_customers",
        query_vector=customer_vector,
        limit=limit,
        score_threshold=0.7  # Only high similarity
    )
    return results
```

### Indexing Churned Customers
```python
def index_churned_customer(customer_data: dict):
    """Upload churned customer vector to Qdrant."""
    vector = create_behavior_vector(customer_data)
    
    qdrant_client.upsert(
        collection_name="churned_customers",
        points=[{
            "id": customer_data['customer_id'],
            "vector": vector,
            "payload": {
                "company_name": customer_data['company_name'],
                "churn_date": customer_data['churn_date'],
                "churn_reason": customer_data['churn_reason'],
                "days_until_churned": customer_data['days_until_churned']
            }
        }]
    )
```

## Code Style Guidelines

### Type Hints
```python
from typing import List, Dict, Optional, Tuple

def analyze_customer(
    customer_id: str,
    behavior_window_days: int = 30
) -> Dict[str, Any]:
    """
    Analyze customer churn risk.
    
    Args:
        customer_id: Unique customer identifier
        behavior_window_days: Days of behavior data to analyze
        
    Returns:
        Risk assessment dictionary with scores and recommendations
        
    Raises:
        CustomerNotFoundError: If customer_id doesn't exist
        APIConnectionError: If Gemini/Qdrant unavailable
    """
    pass
```

### Error Handling Pattern
```python
from flask import jsonify

@app.errorhandler(Exception)
def handle_error(error: Exception):
    """Centralized error handler."""
    app.logger.error(f"Error: {str(error)}", exc_info=True)
    
    return jsonify({
        "error": error.__class__.__name__,
        "message": str(error),
        "timestamp": datetime.utcnow().isoformat()
    }), 500
```

### JSON Response Structure
```python
def success_response(data: Any, message: str = "Success") -> Tuple[dict, int]:
    """Standard success response."""
    return jsonify({
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }), 200

def error_response(message: str, code: int = 400) -> Tuple[dict, int]:
    """Standard error response."""
    return jsonify({
        "success": False,
        "error": message,
        "timestamp": datetime.utcnow().isoformat()
    }), code
```

## Environment Configuration

### Required Variables (.env)
```bash
# AI Services
GEMINI_API_KEY=AIzaSyCsAzRnw-CpDvYDOvgyqpK_vEXOTs67-uk
GEMINI_MODEL=gemini-2.0-flash  # Free tier optimized

# Vector Database
QDRANT_URL=https://dce5ab33-47c7-463c-b630-c35e90f32c43.eu-west-1-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
QDRANT_COLLECTION=churned_customers

# Additional AI (if needed)
AIML_API_KEY=_8f192dfd9cb641beb7bd2ecc21835e31d8cf58539a0a91c73227adc5b28e575abea32e5daa8edca76d6932306e303774

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
DATA_DIR=./data
```

### Loading Configuration
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
    QDRANT_URL = os.getenv('QDRANT_URL')
    QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
    DATA_DIR = os.getenv('DATA_DIR', './data')
```

## Implementation Phases

### Phase 1: Core Infrastructure ✅ COMPLETE
- [x] Flask app setup (app.py)
- [x] Environment configuration (.env)
- [x] Connection testing (scripts/test_connections.py)
- [x] Health check endpoints
- [x] Error handling middleware

### Phase 2: Data Pipeline (NEXT)
- [ ] CSV import utilities (utils/data_loader.py)
- [ ] Vector generation (utils/vector_builder.py)
- [ ] Qdrant collection management (utils/qdrant_client.py)
- [ ] Data validation schemas

### Phase 3: AI Integration
- [ ] Gemini client wrapper (utils/gemini_client.py)
- [ ] Prompt templates (utils/prompts.py)
- [ ] Risk scoring engine (pipeline/risk_scorer.py)
- [ ] Response parsing and validation

### Phase 4: API Development
- [ ] Customer routes (routes/customers.py)
- [ ] Analytics routes (routes/analytics.py)
- [ ] AI analysis routes (routes/ai.py)
- [ ] Batch processing endpoints

### Phase 5: Testing & Polish
- [ ] Unit tests (tests/test_*.py)
- [ ] Integration tests
- [ ] Performance profiling
- [ ] Documentation updates

## Security Considerations

### API Key Protection
- Never commit .env to version control
- Use .gitignore for sensitive files
- Rotate keys quarterly
- Use environment-specific keys (dev/prod)

### Input Validation
- Sanitize all user inputs
- Validate CSV uploads
- Check customer_id format
- Limit query parameter ranges

### Rate Limiting
- Gemini API: Max 60 requests/minute (free tier)
- Implement exponential backoff on failures
- Cache frequent queries
- Queue batch operations

### Data Privacy
- Encrypt customer data at rest
- Use HTTPS for all API calls
- Implement audit logging
- GDPR compliance for EU customers

## Success Metrics

### Technical Metrics
- API response time < 500ms (p95)
- Vector search latency < 100ms
- Gemini API success rate > 95%
- System uptime > 99.5%

### Business Metrics
- Churn prediction accuracy > 80%
- False positive rate < 15%
- Intervention success rate (target: 70%)
- Average days of advance warning (target: 90+ days)

---

**Last Updated**: November 16, 2025  
**Version**: 2.0.0  
**Status**: Development - Phase 1 Complete
