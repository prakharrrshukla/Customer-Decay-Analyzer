# Railway Deployment Guide

Complete guide to deploy Customer Decay Analyzer backend to Railway.

## 🚂 Quick Deploy (5 Minutes)

### Prerequisites
- GitHub account with your repository pushed
- Railway account (free tier available)
- API keys ready:
  - `GEMINI_API_KEY` from https://makersuite.google.com/app/apikey
  - `QDRANT_URL` and `QDRANT_API_KEY` from https://cloud.qdrant.io

---

## Step 1: Create Railway Project

1. Go to https://railway.app/
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select repository: **`Customer-Decay-Analyzer`**
6. Select the **`customer-decay-backend`** folder (if monorepo)

---

## Step 2: Configure Environment Variables

In Railway project settings, add these environment variables:

### Required Variables

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-production-secret-key-change-this
HOST=0.0.0.0
PORT=5000

# Google Gemini API
GEMINI_API_KEY=AIzaSy...your-actual-key
GEMINI_MODEL=gemini-2.0-flash-exp

# Qdrant Vector Database
QDRANT_URL=https://your-instance.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key

# Optional: AI/ML API Key
AIML_API_KEY=your-aiml-api-key

# Logging
LOG_LEVEL=INFO
```

### How to Add Variables in Railway

1. Click on your deployment
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add each variable one by one
5. Click **"Deploy"** after adding all variables

---

## Step 3: Configure Build Settings

Railway should auto-detect Python and use `nixpacks.toml`.

**Build Command** (automatic):
```bash
pip install -r requirements.txt
python scripts/generate_sample_data.py
python scripts/generate_preprocessed_analysis.py
```

**Start Command** (automatic):
```bash
python app.py
```

If needed, override in Railway settings:
- Settings → Deploy → Start Command: `python app.py`

---

## Step 4: Deploy

1. Railway will automatically deploy on push to main
2. Wait 2-3 minutes for build and deployment
3. Check deployment logs for any errors

**Expected logs:**
```
✓ All blueprints registered successfully
🚀 Customer Decay Prediction Backend
Server: http://0.0.0.0:5000
Health: http://0.0.0.0:5000/health
Debug: False
```

---

## Step 5: Get Your Deployment URL

1. In Railway dashboard, find your service
2. Click **"Settings"** → **"Networking"**
3. Click **"Generate Domain"**
4. Your URL will be: `https://customer-decay-analyzer-production.up.railway.app`

---

## Step 6: Test Deployment

### Health Check
```bash
curl https://your-app.up.railway.app/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T...",
  "services": {
    "gemini": {
      "status": "connected",
      "model": "gemini-2.0-flash-exp"
    },
    "qdrant": {
      "status": "connected"
    },
    "data": {
      "status": "ready",
      "files": ["customers.csv", "behavior_events.csv", "churned_customers.csv"]
    }
  }
}
```

### Get At-Risk Customers
```bash
curl https://your-app.up.railway.app/api/customers/at-risk?min_risk=50
```

### Get Customer Analysis
```bash
curl https://your-app.up.railway.app/api/customers/CUST050/analysis
```

---

## Troubleshooting

### Build Fails

**Error: Missing dependencies**
```bash
# Solution: Ensure requirements.txt is complete
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

**Error: Data files not found**
```bash
# Solution: Ensure build commands run in nixpacks.toml
# Check Railway build logs for script execution
```

### Deployment Fails

**Error: Port binding issues**
- Ensure `PORT` environment variable is set to `5000`
- Ensure `HOST` is set to `0.0.0.0`
- Check app.py uses: `port = int(os.getenv('PORT', 5000))`

**Error: API keys not working**
- Verify all environment variables are set correctly
- No quotes around values in Railway dashboard
- Redeploy after adding variables

### Health Check Fails

**Gemini connection error**
```
"gemini": {"status": "error", "message": "GEMINI_API_KEY not set"}
```
**Solution:** Add `GEMINI_API_KEY` to Railway environment variables

**Qdrant connection error**
```
"qdrant": {"status": "error", "message": "Connection failed"}
```
**Solution:** 
- Verify `QDRANT_URL` and `QDRANT_API_KEY`
- Ensure Qdrant Cloud instance is running
- Check firewall/network settings in Qdrant Cloud

---

## Railway Configuration Files

### `railway.json`
Railway-specific configuration for build and deployment.

### `nixpacks.toml`
Build configuration including:
- Python version
- Package installation
- Data generation scripts
- Start command

### `Procfile`
Process definition for Railway (legacy support).

### `runtime.txt`
Specifies Python version for deployment.

---

## Auto-Deployment

Railway automatically deploys on every push to main branch:

1. Make changes locally
2. Commit and push:
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```
3. Railway detects push and rebuilds
4. New version deployed in ~2-3 minutes

---

## Monitoring

### View Logs
1. Go to Railway dashboard
2. Click on your service
3. Click **"Logs"** tab
4. Monitor real-time application logs

### Metrics
1. Click **"Metrics"** tab
2. View:
   - CPU usage
   - Memory usage
   - Network traffic
   - Request count

---

## Cost Optimization

### Free Tier Limits (Railway)
- $5 free credit per month
- 500 hours of usage
- 512 MB RAM per service
- 1 GB disk storage

### Tips
- Use preprocessed analysis (already implemented!)
- Set `FLASK_DEBUG=False` in production
- Monitor API usage (Gemini: 15 RPM free tier)
- Consider upgrading if traffic increases

---

## Custom Domain (Optional)

1. Go to **Settings** → **Networking**
2. Click **"Add Custom Domain"**
3. Enter your domain: `api.yourdomain.com`
4. Add CNAME record to your DNS:
   - Name: `api`
   - Value: `your-app.up.railway.app`
5. Wait for DNS propagation (5-30 minutes)

---

## Production Checklist

Before going live:

- [ ] All environment variables set
- [ ] `FLASK_DEBUG=False`
- [ ] Strong `SECRET_KEY` configured
- [ ] API keys are valid and active
- [ ] Health check returns "healthy"
- [ ] At least one customer analysis works
- [ ] Preprocessed data generated successfully
- [ ] Qdrant vector store populated
- [ ] CORS configured for your frontend domain
- [ ] Monitoring enabled
- [ ] Custom domain configured (if needed)

---

## Support

**Railway Documentation:** https://docs.railway.app/  
**Railway Discord:** https://discord.gg/railway  
**This Project:** https://github.com/prakharrrshukla/Customer-Decay-Analyzer

---

## Next Steps

1. Deploy frontend to Vercel/Netlify
2. Update frontend API endpoint to Railway URL
3. Configure CORS in app.py for your frontend domain
4. Test full integration
5. Share with your team! 🚀
