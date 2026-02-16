# 🛰️ GeoVision

**Advanced Geospatial Analysis Platform** - Real-time satellite imagery analysis, land cover classification, and environmental monitoring using Google Earth Engine and Machine Learning.

---

## 🌟 Features

### 📡 Real Satellite Data
- **Landsat 8/9** Collection 2 Level-2 (Surface Reflectance)
- **Sentinel-2** Level-2A (Surface Reflectance)
- **Global Coverage** - Any location on Earth
- **Automatic Fallback** - Switches to Sentinel-2 if Landsat unavailable

### 🗺️ Interactive Mapping
- Click anywhere on the map to select a location
- Real-time location name resolution
- Coordinate display and validation

### 🏞️ Land Cover Classification
- **EfficientNetB3** model trained on **EuroSAT dataset**
- 10 land cover classes (Annual Crop, Forest, Urban, etc.)
- Pre-trained ImageNet weights for high accuracy

### 📊 Change Detection
- Multi-temporal analysis (30 days to 10+ years)
- Real multispectral band analysis (NIR, Red, SWIR)
- Vegetation, urban, and moisture change metrics
- Publication-ready results

### ⚠️ Risk Assessment
- Environmental risk scoring
- Weather-based analysis
- Land cover vulnerability assessment

### 🌤️ Real-Time Weather
- **OpenWeather API** integration
- Current conditions for any location
- Temperature, humidity, wind, precipitation

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Earth Engine account
- OpenWeather API key

### Installation
```bash
# Clone repository
cd GeoVision

# Install dependencies
pip install -r requirements.txt

# Authenticate Google Earth Engine
earthengine authenticate

# Configure API keys
# Create .env file with your OpenWeather API key
```

### Run Application
```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

---

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Detailed installation and configuration guide
- **[USAGE.md](USAGE.md)** - How to use each feature
- **[API_KEYS.md](API_KEYS.md)** - API key setup instructions

---

## 🛠️ Technology Stack

### Core
- **Streamlit** - Web application framework
- **Google Earth Engine** - Satellite imagery
- **TensorFlow/Keras** - Machine learning

### Geospatial
- **Folium** - Interactive maps
- **Rasterio** - Geospatial data processing
- **GeoPandas** - Geographic data structures

### Data Science
- **NumPy** - Numerical computing
- **Pandas** - Data analysis
- **Plotly** - Interactive visualizations

---

## 📊 Model Details

### EfficientNetB3 on EuroSAT
- **Architecture:** EfficientNetB3
- **Dataset:** EuroSAT (10 land cover classes)
- **Input Size:** 64x64 pixels
- **Weights:** Pre-trained on ImageNet
- **Classes:** AnnualCrop, Forest, HerbaceousVegetation, Highway, Industrial, Pasture, PermanentCrop, Residential, River, SeaLake

---

## 🌍 Global Coverage

**Satellite Data:**
- Landsat 8: Launched 2013, 16-day revisit, 30m resolution
- Landsat 9: Launched 2021, 16-day revisit, 30m resolution
- Sentinel-2A: Launched 2015, 5-day revisit, 10m resolution
- Sentinel-2B: Launched 2017, 5-day revisit, 10m resolution

**Combined:** Near-daily global coverage since 2015!

---

## 📝 License

This project is for educational and research purposes.

---

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Google Earth Engine, TensorFlow, and Streamlit**
