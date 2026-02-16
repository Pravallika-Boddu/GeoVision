# 🔑 API Keys Configuration

Guide to obtaining and configuring API keys for GeoVision.

---

## 📡 Google Earth Engine

### What is it?
Google Earth Engine provides access to petabytes of satellite imagery and geospatial datasets.

### Why do we need it?
- Real Landsat 8/9 satellite data
- Real Sentinel-2 satellite data
- Global coverage
- Historical data since 2013

### How to Get Access

#### Step 1: Create Google Account
- Use existing Google account or create new one
- Go to [accounts.google.com](https://accounts.google.com)

#### Step 2: Sign Up for Earth Engine
1. Visit [Google Earth Engine](https://earthengine.google.com/)
2. Click "Sign Up"
3. Choose account type:
   - **Non-commercial:** Free (for research/education)
   - **Commercial:** Paid (for business use)
4. Fill out registration form
5. Wait for approval (usually instant for non-commercial)

#### Step 3: Create Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name (e.g., "GeoVision")
4. Click "Create"
5. **Copy the Project ID** (e.g., `ee-username123`)

#### Step 4: Authenticate
```bash
earthengine authenticate
```

This will:
1. Open browser
2. Ask you to sign in
3. Generate authentication token
4. Save credentials to `~/.config/earthengine/credentials`

### Configuration in GeoVision

The project ID is already configured in `utils/gee_fetcher.py`:
```python
ee.Initialize(project='ee-boddupravallika04')
```

**To use your own project:**
1. Open `utils/gee_fetcher.py`
2. Find line ~36: `ee.Initialize(project='ee-boddupravallika04')`
3. Replace with your project ID: `ee.Initialize(project='YOUR-PROJECT-ID')`

### Verify Setup
```bash
python -c "from utils.gee_fetcher import get_gee_fetcher; gee = get_gee_fetcher(); print('GEE Available:', gee.is_available())"
```

**Expected Output:**
```
✅ Google Earth Engine initialized successfully with project: YOUR-PROJECT-ID
GEE Available: True
```

### Quota & Limits
- **Free Tier:** 
  - 250,000 requests/day
  - 10,000 concurrent requests
  - Sufficient for most use cases

### Troubleshooting

**Error: "no project found"**
- Solution: Update project ID in `gee_fetcher.py`

**Error: "not authenticated"**
- Solution: Run `earthengine authenticate`

**Error: "quota exceeded"**
- Solution: Wait 24 hours or upgrade to paid tier

---

## 🌤️ OpenWeather API

### What is it?
OpenWeather provides real-time weather data for any location globally.

### Why do we need it?
- Current weather conditions
- Temperature, humidity, wind data
- Precipitation information
- Risk assessment calculations

### How to Get API Key

#### Step 1: Create Account
1. Go to [OpenWeather](https://openweathermap.org/)
2. Click "Sign Up"
3. Fill out registration form
4. Verify email address

#### Step 2: Get API Key
1. Log in to your account
2. Go to [API Keys](https://home.openweathermap.org/api_keys)
3. Find "Default" API key or create new one
4. **Copy the API key** (e.g., `abc123def456ghi789jkl012mno345pq`)

#### Step 3: Activate API Key
- **Wait 10-15 minutes** for API key to activate
- Test activation: `curl "https://api.openweathermap.org/data/2.5/weather?lat=28.7&lon=77.1&appid=YOUR_KEY"`

### Configuration in GeoVision

#### Create .env File
1. In project root directory, create file named `.env`
2. Add your API key:

```env
OPENWEATHER_API_KEY=your_actual_api_key_here
```

**Example `.env` file:**
```env
OPENWEATHER_API_KEY=abc123def456ghi789jkl012mno345pq
```

**Important:**
- No quotes around the key
- No spaces around `=`
- File must be named exactly `.env`
- File should be in project root (same folder as `app.py`)

### Verify Setup
```bash
python utils/real_weather.py
```

**Expected Output:**
```
✅ Real weather data:
Location: Namburu, IN
Temperature: 32.5°C
Humidity: 65%
Wind: 3.2 m/s
```

### Pricing & Limits

**Free Tier:**
- 60 calls/minute
- 1,000,000 calls/month
- Current weather data
- **Cost:** $0

**Paid Tiers:**
- More calls/minute
- Historical data
- Forecasts
- **Cost:** Starting at $40/month

**For GeoVision:** Free tier is sufficient!

### Troubleshooting

**Error: "API key not found"**
- Check `.env` file exists
- Check file is in correct location
- Check spelling: `OPENWEATHER_API_KEY`

**Error: "Invalid API key"**
- Wait 10-15 minutes after creating key
- Check key is copied correctly
- No extra spaces or quotes

**Error: "API call limit exceeded"**
- Free tier: 60 calls/min
- Wait 1 minute and retry
- Or upgrade to paid tier

---

## 🔒 Security Best Practices

### Protect Your API Keys

**DO:**
- ✅ Keep `.env` file in `.gitignore`
- ✅ Use environment variables
- ✅ Rotate keys periodically
- ✅ Use separate keys for dev/prod

**DON'T:**
- ❌ Commit `.env` to Git
- ❌ Share keys publicly
- ❌ Hardcode keys in source code
- ❌ Use same key across projects

### .gitignore
Make sure `.gitignore` includes:
```
.env
*.env
.env.local
```

### Key Rotation
Rotate API keys every 3-6 months:
1. Generate new key
2. Update `.env` file
3. Test application
4. Delete old key

---

## 📋 Quick Reference

### Required API Keys
| Service | Required | Free Tier | Setup Time |
|---------|----------|-----------|------------|
| Google Earth Engine | ✅ Yes | ✅ Yes | 5-10 min |
| OpenWeather | ✅ Yes | ✅ Yes | 2-5 min |

### Configuration Files
| File | Purpose | Location |
|------|---------|----------|
| `.env` | API keys | Project root |
| `gee_fetcher.py` | GEE project ID | `utils/` |
| `credentials` | GEE auth | `~/.config/earthengine/` |

---

## ✅ Verification Checklist

Before running GeoVision, verify:

- [ ] Google account created
- [ ] GEE account approved
- [ ] GEE cloud project created
- [ ] `earthengine authenticate` completed
- [ ] Project ID configured in `gee_fetcher.py`
- [ ] OpenWeather account created
- [ ] OpenWeather API key obtained
- [ ] `.env` file created with API key
- [ ] API key activated (waited 10-15 min)
- [ ] Both APIs tested and working

---

## 🆘 Need Help?

**GEE Issues:**
- [GEE Documentation](https://developers.google.com/earth-engine)
- [GEE Forum](https://groups.google.com/g/google-earth-engine-developers)

**OpenWeather Issues:**
- [OpenWeather FAQ](https://openweathermap.org/faq)
- [OpenWeather Support](https://home.openweathermap.org/questions)

**GeoVision Issues:**
- Check [SETUP.md](SETUP.md) for installation help
- Open issue on GitHub

---

**All Set! 🎉 Your API keys are configured and ready to use!**
