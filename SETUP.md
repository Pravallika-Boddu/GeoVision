# 🔧 Setup Guide

Complete installation and configuration guide for GeoVision.

---

## 📋 Prerequisites

### System Requirements
- **Python:** 3.8 or higher
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 2GB for dependencies
- **Internet:** Required for satellite data and weather API

### Accounts Needed
1. **Google Account** - For Google Earth Engine
2. **OpenWeather Account** - For weather data (free tier available)

---

## 🚀 Installation Steps

### 1. Clone or Download Project
```bash
cd GeoVision
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `streamlit` - Web framework
- `earthengine-api` - Google Earth Engine
- `tensorflow` - Machine learning
- `rasterio` - Geospatial data
- `folium` - Interactive maps
- `plotly` - Visualizations

### 4. Authenticate Google Earth Engine

#### Create GEE Account
1. Go to [Google Earth Engine](https://earthengine.google.com/)
2. Click "Sign Up"
3. Use your Google account
4. Wait for approval (usually instant for non-commercial use)

#### Authenticate
```bash
earthengine authenticate
```

This will:
1. Open your browser
2. Ask you to sign in with Google
3. Generate authentication token
4. Save credentials locally

**Verify Authentication:**
```bash
python -c "import ee; ee.Initialize(project='ee-boddupravallika04'); print('✅ GEE Ready!')"
```

### 5. Configure API Keys

#### Get OpenWeather API Key
1. Go to [OpenWeather](https://openweathermap.org/api)
2. Sign up for free account
3. Go to "API keys" section
4. Copy your API key

#### Create .env File
Create a file named `.env` in the project root:

```env
OPENWEATHER_API_KEY=your_api_key_here
```

**Example:**
```env
OPENWEATHER_API_KEY=abc123def456ghi789jkl012mno345pq
```

### 6. Verify Installation

Run verification script:
```bash
python -c "from utils.gee_fetcher import get_gee_fetcher; gee = get_gee_fetcher(); print('GEE Available:', gee.is_available())"
```

**Expected Output:**
```
✅ Google Earth Engine initialized successfully with project: ee-boddupravallika04
GEE Available: True
```

---

## 🏃 Running the Application

### Start Streamlit
```bash
streamlit run app.py
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### Access Application
Open your browser and go to: `http://localhost:8501`

---

## 🔍 Troubleshooting

### GEE Not Available
**Error:** `❌ GEE Not Available`

**Solutions:**
1. Run `earthengine authenticate`
2. Check internet connection
3. Verify Google account has GEE access
4. Restart terminal/IDE

### Weather Data Not Loading
**Error:** `⚠️ Could not fetch weather data`

**Solutions:**
1. Check `.env` file exists
2. Verify API key is correct
3. Check OpenWeather API quota (60 calls/min free tier)
4. Test API key: `curl "https://api.openweathermap.org/data/2.5/weather?lat=28.7&lon=77.1&appid=YOUR_KEY"`

### Module Not Found
**Error:** `ModuleNotFoundError: No module named 'X'`

**Solutions:**
1. Activate virtual environment
2. Run `pip install -r requirements.txt`
3. Check Python version (3.8+)

### Satellite Data Fetch Failed
**Error:** `❌ Failed to fetch satellite imagery`

**Solutions:**
1. Try different date range (some periods have no data)
2. Try different location
3. Check GEE authentication
4. Wait a moment and retry (GEE rate limits)

---

## 📦 Dependencies List

**Core:**
- streamlit
- python-dotenv

**Geospatial:**
- earthengine-api
- geemap
- rasterio
- geopandas
- folium
- streamlit-folium

**Machine Learning:**
- tensorflow
- keras
- numpy
- opencv-python

**Data & Visualization:**
- pandas
- plotly
- matplotlib
- seaborn

**APIs:**
- requests

---

## 🔄 Updating

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Update Earth Engine
```bash
pip install --upgrade earthengine-api
```

---

## 🌐 Network Configuration

### Firewall
Allow outbound connections to:
- `earthengine.googleapis.com` (port 443)
- `api.openweathermap.org` (port 80/443)

### Proxy
If behind proxy, set environment variables:
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=https://proxy.example.com:8080
```

---

## ✅ Installation Complete!

You're ready to use GeoVision! See [USAGE.md](USAGE.md) for how to use the application.
