# Testing Guide - Customer Decay Analyzer

Step-by-step instructions for testing the complete system.

---

## Prerequisites

1. **Python Environment**
   ```powershell
   # Verify Python installation
   python --version  # Should be 3.9+
   
   # Activate virtual environment
   .\venv\Scripts\Activate.ps1
   ```

2. **Environment Variables**
   - Ensure `.env` file exists with:
     - `GEMINI_API_KEY`
     - `QDRANT_URL`
     - `QDRANT_API_KEY`

3. **Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

---

## Phase 1: Generate Sample Data

**Purpose**: Create realistic customer and behavior data for testing.

```powershell
# Run data generation script
python scripts/generate_sample_data.py
```

**Expected Output**:
```
Generating Sample Data for Customer Decay Analyzer
====================================================

Step 1: Generating 30 customers...
   ✓ Created 9 Enterprise, 15 Pro, 6 Basic tier customers

Step 2: Generating behavior events for 90 days...
   [Progress updates every 5 customers]
   ✓ Generated 2544 events across 30 customers

Step 3: Generating 20 churned customers...
   ✓ Created 20 churned customers with realistic patterns

✅ Sample data generation complete!
```

**Verify Files Created**:
```powershell
ls data/*.csv
```
Should show:
- `customers.csv` (30 rows)
- `behavior_events.csv` (~2500 rows)
- `churned_customers.csv` (20 rows)

---

## Phase 2: Test API Connections

**Purpose**: Verify Gemini and Qdrant connectivity.

```powershell
# Run connection tests
python scripts/test_connections.py
```

**Expected Output**:
```
Testing API Connections
=======================

1. Testing Gemini API...
   Model: gemini-2.0-flash
   ✓ Gemini API connection successful!

2. Testing Qdrant...
   URL: https://[your-instance].aws.cloud.qdrant.io:6333
   ✓ Qdrant connection successful!

3. Testing AIML API...
   ✓ AIML API connection successful!

✅ All connections successful!
```

**Troubleshooting**:
- ❌ Gemini fails: Check `GEMINI_API_KEY` in `.env`
- ❌ Qdrant fails: Verify `QDRANT_URL` and `QDRANT_API_KEY`
- ❌ Network errors: Check firewall/proxy settings

---

## Phase 3: Populate Qdrant Vector Store

**Purpose**: Index churned customers for similarity search.

```powershell
# Populate Qdrant with churned customer vectors
python scripts/populate_qdrant.py
```

**Expected Output**:
```
Populating Qdrant with Churned Customers
=========================================

1. Initializing Qdrant vector store...
2. Creating/verifying collection...
3. Loading churned customers...
   Found 20 churned customers

4. Processing and uploading vectors...
   Processed 5/20 customers...
   Processed 10/20 customers...
   Processed 15/20 customers...
   Processed 20/20 customers...

✅ Successfully uploaded 20/20 customers

5. Verifying collection...
   Collection: customer_behaviors
   Points: 20
   Vectors: 20

✅ Qdrant population complete!
```

**Verify in Qdrant Cloud Console**:
1. Log into Qdrant Cloud
2. Select your cluster
3. Check collection `customer_behaviors`
4. Should show 20+ points

---

## Phase 4: Test Individual Components

### 4.1 Test Gemini Analyzer

```powershell
# Run Gemini analyzer test
python models/gemini_analyzer.py
```

**Expected Output**:
```
Testing CustomerAnalyzer with 3 sample customers
=================================================

Customer: CUST001 (Healthy Enterprise)
---------------------------------------
Risk Score: 25/100 (low)
Primary Concerns:
  - Consistent engagement patterns
  - Stable login frequency
Recommended Actions:
  - Continue monitoring
  - Upsell opportunities

[Similar output for CUST013 and CUST025]
```

### 4.2 Test Vector Store

```powershell
# Run vector store test
python models/vector_store.py
```

**Expected Output**:
```
Testing QdrantVectorStore
=========================

1. Creating collection...
   ✓ Collection created/verified

2. Creating behavior vector...
   ✓ Vector dimensions: 768

3. Uploading test customer...
   ✓ Upload successful

4. Searching similar customers...
   ✓ Found 3 similar customers
```

### 4.3 Test Risk Assessor

```powershell
# Run risk assessor test
python models/risk_assessor.py
```

**Expected Output**:
```
Testing RiskAssessor with declining customer
=============================================

Customer: CUST013
------------------
Risk Score: 65.2/100 (high)
Predicted Churn: 2025-03-15 (54 days)
Intervention Priority: 8/10
Revenue at Risk: $3,588.00
Confidence: high (5 similar patterns)

Similar Churned Customers:
  1. CHURN007 (89% similar, churned after 45 days)
  2. CHURN012 (85% similar, churned after 52 days)
```

---

## Phase 5: Run Flask API

**Purpose**: Start the backend server for API testing.

```powershell
# Start Flask development server
python app.py
```

**Expected Output**:
```
==================================================
🚀 Customer Decay Prediction Backend
==================================================
   Server: http://0.0.0.0:5000
   Health: http://0.0.0.0:5000/health
   Debug:  True
==================================================

✓ All blueprints registered successfully

 * Running on http://0.0.0.0:5000
```

**Keep this terminal open** - server must be running for API tests.

---

## Phase 6: Test API Endpoints

Open a **new PowerShell terminal** and run these tests:

### 6.1 Health Check

```powershell
# Test health endpoint
Invoke-RestMethod -Uri http://localhost:5000/api/health -Method GET | ConvertTo-Json
```

**Expected**: Status "healthy" with all services "connected"

### 6.2 Ping

```powershell
# Test ping endpoint
Invoke-RestMethod -Uri http://localhost:5000/api/ping -Method GET
```

**Expected**: `{"message": "pong", "status": "alive"}`

### 6.3 Customer Analysis

```powershell
# Analyze specific customer
Invoke-RestMethod -Uri http://localhost:5000/api/customers/CUST013/analysis -Method GET | ConvertTo-Json -Depth 5
```

**Expected**: Full risk assessment with score, predictions, recommendations

### 6.4 At-Risk Customers

```powershell
# Get high-risk customers
Invoke-RestMethod -Uri "http://localhost:5000/api/customers/at-risk?min_risk=60&limit=5" -Method GET | ConvertTo-Json -Depth 3
```

**Expected**: List of 5 customers with risk ≥ 60

### 6.5 Batch Analysis

```powershell
# Analyze all customers
$body = @{
    save_results = $true
    min_risk = 0
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5000/api/customers/analyze-all -Method POST -Body $body -ContentType "application/json" | ConvertTo-Json
```

**Expected**: Summary stats + full analysis for all 30 customers

### 6.6 Analytics Stats

```powershell
# Get dashboard stats
Invoke-RestMethod -Uri http://localhost:5000/api/analytics/stats -Method GET | ConvertTo-Json
```

**Expected**: Aggregate statistics with risk distribution

---

## Phase 7: Run Automated Test Suite

**Purpose**: Run comprehensive pytest suite.

```powershell
# Run all tests
python tests/test_pipeline.py
```

**Expected Output**:
```
Customer Decay Analyzer - Test Suite
=====================================

TEST 1: Gemini Analyzer - Healthy Customer
✓ Risk score: 28
✓ Risk level: low
✅ TEST PASSED

TEST 2: Vector Store Operations
✓ Collection exists: customer_behaviors
✓ Vector created: 768 dimensions
✅ TEST PASSED

TEST 3: Risk Assessor - Declining Customer
✓ Risk score: 65
✓ Risk level: high
✅ TEST PASSED

TEST 4: Full Pipeline - Three Customer Patterns
✓ Risk score range: 25.0 - 82.0
✅ TEST PASSED

TEST 5: API Endpoints
✓ Health status: healthy
✓ Ping successful
✅ TEST PASSED

TEST 6: Utility Functions
✓ Currency formatting works
✓ Summary stats calculated
✅ TEST PASSED

==================== 6 passed in 45.23s ====================
```

**Alternative**: Run with pytest directly
```powershell
pytest tests/test_pipeline.py -v
```

---

## Phase 8: Manual Testing Scenarios

### Scenario 1: Healthy Customer
```powershell
# Should show low risk (< 40)
Invoke-RestMethod -Uri http://localhost:5000/api/customers/CUST001/analysis -Method GET | Select-Object customer_id, churn_risk_score, risk_level
```

### Scenario 2: Declining Customer
```powershell
# Should show medium/high risk (50-70)
Invoke-RestMethod -Uri http://localhost:5000/api/customers/CUST013/analysis -Method GET | Select-Object customer_id, churn_risk_score, predicted_churn_date
```

### Scenario 3: Critical Customer
```powershell
# Should show critical risk (> 75)
Invoke-RestMethod -Uri http://localhost:5000/api/customers/CUST025/analysis -Method GET | Select-Object customer_id, churn_risk_score, intervention_priority
```

---

## Troubleshooting

### Problem: "Module not found" errors
**Solution**: 
```powershell
pip install -r requirements.txt
```

### Problem: Gemini API quota exceeded
**Solution**:
- Wait 1 minute (free tier: 15 RPM limit)
- Or use rule-based fallback (automatic in code)

### Problem: Qdrant connection timeout
**Solution**:
- Check internet connection
- Verify QDRANT_URL includes port :6333
- Check Qdrant Cloud console for cluster status

### Problem: Flask port already in use
**Solution**:
```powershell
# Find process on port 5000
netstat -ano | findstr :5000

# Kill process (replace <PID> with actual process ID)
taskkill /PID <PID> /F
```

### Problem: No behavior data for customer
**Solution**:
- Re-run `python scripts/generate_sample_data.py`
- Verify `data/behavior_events.csv` exists and has data

---

## Performance Benchmarks

**Expected Timings** (on standard hardware):

| Operation | Time |
|-----------|------|
| Gemini analysis (1 customer) | 2-5 seconds |
| Vector search (top 5) | < 1 second |
| Full risk assessment (1 customer) | 3-7 seconds |
| Batch analysis (30 customers) | 2-4 minutes |
| API health check | < 0.5 seconds |

---

## Success Criteria

✅ **All tests passing**:
- Data generation: 3 CSV files created
- API connections: All services "connected"
- Qdrant: 20+ vectors indexed
- Component tests: All 6 pytest tests pass
- API tests: All endpoints return 200

✅ **Expected Risk Distribution**:
- Low risk (0-40): ~30% of customers
- Medium risk (41-60): ~35% of customers
- High risk (61-75): ~25% of customers
- Critical risk (76-100): ~10% of customers

✅ **Data Quality**:
- Risk scores vary across customer base
- Declining customers have higher risk than healthy
- Intervention priority correlates with value
- Similar churned patterns found for high-risk customers

---

## Next Steps

After all tests pass:
1. **Demo Preparation**: Run batch analysis, save results
2. **Frontend Integration**: Use API_DOCS.md for endpoint specs
3. **Production Deployment**: Add authentication, rate limiting
4. **Monitoring**: Set up alerts for critical risk customers

---

## Quick Test Command Reference

```powershell
# Full test sequence (run in order)
python scripts/generate_sample_data.py
python scripts/test_connections.py
python scripts/populate_qdrant.py
python app.py  # In separate terminal
python tests/test_pipeline.py
```

---

## Support

For issues during testing:
1. Check error messages in terminal output
2. Review troubleshooting section above
3. Verify `.env` file has all required keys
4. Check `data/` directory for CSV files
5. Test internet connectivity (Gemini + Qdrant are cloud services)
