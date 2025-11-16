# Customer Decay Analyzer - API Documentation

Complete API reference for the Customer Decay Analyzer backend.

## Base URL

```
http://localhost:5000/api
```

---

## Health & Status Endpoints

### GET /api/health

Comprehensive health check of all services.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T10:30:00",
  "version": "1.0.0",
  "services": {
    "gemini": {
      "status": "connected",
      "message": "Gemini API configured (gemini-2.0-flash)",
      "model": "gemini-2.0-flash"
    },
    "qdrant": {
      "status": "connected",
      "message": "Qdrant connected successfully",
      "collections": ["customer_behaviors"],
      "url": "eu-west-1-0.aws.cloud.qdrant.io:6333"
    },
    "data": {
      "status": "ready",
      "message": "All data files present",
      "files": ["customers.csv", "behavior_events.csv", "churned_customers.csv"]
    }
  }
}
```

**Status Codes:**
- `200`: All services healthy
- `503`: One or more services degraded

---

### GET /api/ping

Simple liveness check.

**Response:**
```json
{
  "message": "pong",
  "status": "alive"
}
```

---

## Customer Endpoints

### GET /api/customers/{customer_id}/analysis

Get comprehensive risk analysis for a specific customer.

**Path Parameters:**
- `customer_id` (string): Customer ID (e.g., "CUST001")

**Response:**
```json
{
  "customer_id": "CUST013",
  "company_name": "TechStart Pro",
  "churn_risk_score": 65.2,
  "risk_level": "high",
  "predicted_churn_date": "2025-03-15",
  "days_until_predicted_churn": 54,
  "confidence_level": "high",
  "intervention_priority": 8,
  "estimated_revenue_at_risk": 3588.0,
  "similar_churned_customers": 5,
  "gemini_analysis": {
    "churn_risk_score": 68,
    "risk_level": "high",
    "primary_concerns": [
      "Declining login frequency (60% drop)",
      "Reduced feature engagement",
      "Negative support ticket sentiment"
    ],
    "recommended_actions": [
      "Schedule executive check-in call",
      "Offer personalized training session",
      "Review pricing and feature needs"
    ],
    "behavioral_metrics": {
      "engagement_score": 0.45,
      "login_frequency": 0.32,
      "feature_usage_score": 0.5,
      "email_open_rate": 0.4,
      "support_ticket_trend": 0.7,
      "payment_issues": 0.2,
      "sentiment_score": -0.3,
      "login_trend": -0.8,
      "engagement_trend": -0.6,
      "feature_trend": -0.4
    }
  },
  "vector_similarity_score": 61.5,
  "similar_patterns": [
    {
      "customer_id": "CHURN007",
      "similarity": 0.89,
      "churn_reason": "poor_support",
      "days_until_churned": 45
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `404`: Customer not found or no behavior data
- `500`: Server error

---

### GET /api/customers/

List all customers with optional filtering.

**Query Parameters:**
- `tier` (optional): Filter by tier (Enterprise/Pro/Basic)
- `limit` (optional): Max results (default: 100)

**Example Request:**
```
GET /api/customers/?tier=Enterprise&limit=10
```

**Response:**
```json
{
  "total": 10,
  "customers": [
    {
      "customer_id": "CUST001",
      "company_name": "Enterprise Corp A",
      "tier": "Enterprise",
      "monthly_value": 999.0,
      "signup_date": "2023-01-15",
      "industry": "Technology"
    }
  ]
}
```

---

### GET /api/customers/at-risk

Get customers at high risk of churning.

**Query Parameters:**
- `min_risk` (optional): Minimum risk score (default: 50)
- `limit` (optional): Max results (default: 20)

**Example Request:**
```
GET /api/customers/at-risk?min_risk=60&limit=10
```

**Response:**
```json
{
  "total_at_risk": 15,
  "returned": 10,
  "min_risk_threshold": 60,
  "summary": {
    "total_customers": 10,
    "risk_breakdown": {
      "critical": 3,
      "high": 5,
      "medium": 2,
      "low": 0
    },
    "average_risk_score": 72.5,
    "total_revenue_at_risk": 45000.0,
    "customers_needing_intervention": 8
  },
  "customers": [
    {
      "customer_id": "CUST025",
      "churn_risk_score": 82.0,
      "risk_level": "critical",
      "intervention_priority": 10,
      "estimated_revenue_at_risk": 11988.0
    }
  ]
}
```

---

### POST /api/customers/analyze-all

Run comprehensive risk assessment on all customers.

**Request Body:**
```json
{
  "save_results": true,
  "min_risk": 0
}
```

**Parameters:**
- `save_results` (boolean, optional): Save to data/analysis_all.json
- `min_risk` (float, optional): Minimum risk score to include (default: 0)

**Response:**
```json
{
  "total_analyzed": 30,
  "returned": 30,
  "min_risk_filter": 0,
  "summary": {
    "total_customers": 30,
    "risk_breakdown": {
      "critical": 5,
      "high": 8,
      "medium": 10,
      "low": 7
    },
    "average_risk_score": 51.3,
    "total_revenue_at_risk": 125000.0,
    "customers_needing_intervention": 13
  },
  "assessments": [...]
}
```

---

## Analytics Endpoints

### GET /api/analytics/stats

Get dashboard statistics.

**Response:**
```json
{
  "total_customers": 30,
  "at_risk_count": 13,
  "critical_count": 5,
  "average_risk_score": 51.3,
  "total_revenue_at_risk": 125000.0,
  "risk_distribution": {
    "critical": 5,
    "high": 8,
    "medium": 10,
    "low": 7
  },
  "tier_breakdown": {
    "Enterprise": {"count": 9, "avg_risk": 62.5},
    "Pro": {"count": 15, "avg_risk": 48.2},
    "Basic": {"count": 6, "avg_risk": 35.1}
  }
}
```

---

## Error Responses

All endpoints may return error responses in this format:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

**Common Status Codes:**
- `400`: Bad request (invalid parameters)
- `404`: Resource not found
- `500`: Internal server error
- `503`: Service unavailable

---

## Rate Limiting

Currently no rate limiting. For production:
- Recommend 100 requests/minute per IP
- Batch endpoints limited to 10 requests/hour

---

## Authentication

Current version: No authentication (development only)

For production:
- Add API key header: `X-API-Key: your-key-here`
- JWT tokens for user sessions
- OAuth 2.0 for third-party integrations

---

## Data Freshness

- Customer data: Loaded from CSV on each request
- Behavior events: Last 90 days analyzed
- Risk scores: Calculated in real-time
- Vector similarity: Based on indexed churned customers

---

## Best Practices

1. **Batch Analysis**: Use `/analyze-all` endpoint during off-peak hours
2. **Caching**: Cache individual analysis results for 1 hour
3. **Webhooks**: Set up webhooks for risk score changes (future feature)
4. **Pagination**: Use `limit` parameter for large result sets

---

## Example Integration

```javascript
// Frontend integration example
const API_BASE = 'http://localhost:5000/api';

// Get at-risk customers
async function getAtRiskCustomers() {
  const response = await fetch(`${API_BASE}/customers/at-risk?min_risk=60`);
  const data = await response.json();
  return data.customers;
}

// Get specific customer analysis
async function analyzeCustomer(customerId) {
  const response = await fetch(`${API_BASE}/customers/${customerId}/analysis`);
  const data = await response.json();
  return data;
}

// Check system health
async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`);
  const data = await response.json();
  return data.status === 'healthy';
}
```

---

## Support

For issues or questions:
- GitHub: [repository-url]
- Email: support@example.com
- Docs: [documentation-url]
