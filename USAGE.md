# 📖 Usage Guide

How to use each feature of GeoVision.

---

## 🗺️ Map & Location Selection

### Selecting a Location
1. **Navigate** to the "Map & Location" tab
2. **Click** anywhere on the interactive map
3. **View** coordinates and location name in sidebar
4. Location is automatically saved for other tabs

### Location Information
- **Coordinates:** Latitude and Longitude displayed
- **Location Name:** Automatically resolved (e.g., "New Delhi, India")
- **Validation:** Coordinates must be valid (-90 to 90 lat, -180 to 180 lon)

---

## 🏞️ Land Cover Classification

### Analyzing Land Cover
1. **Select location** on map
2. **Go to** "Land Cover" tab
3. **Click** "Analyze Land Cover"
4. **Wait** 10-20 seconds for satellite data fetch

### Results
- **Classification Map:** Visual representation of land cover types
- **Distribution Chart:** Percentage breakdown of each class
- **Class Legend:** Color-coded land cover types

### Land Cover Classes (EuroSAT)
1. **AnnualCrop** - Cropland harvested annually
2. **Forest** - Dense tree coverage
3. **HerbaceousVegetation** - Grasslands, meadows
4. **Highway** - Major roads and highways
5. **Industrial** - Factories, warehouses
6. **Pasture** - Grazing land
7. **PermanentCrop** - Orchards, vineyards
8. **Residential** - Urban housing
9. **River** - Flowing water bodies
10. **SeaLake** - Standing water bodies

---

## 📊 Change Detection

### Running Change Detection Analysis

#### Step 1: Select Time Period
Choose one of two methods:

**Method A: Date Range**
1. Select "Date Range" input method
2. Choose start date
3. Choose end date
4. Click "Analyze Change Detection"

**Method B: Quick Select**
1. Select "Quick Select" input method
2. Choose preset period:
   - Last 30 Days
   - Last 3 Months
   - Last 6 Months
   - Last 1 Year
   - Last 3 Years
   - Last 5 Years
   - Last 10 Years
3. Click "Analyze Change Detection"

#### Step 2: Wait for Analysis
- **Fetching:** 20-60 seconds (depends on location and date range)
- **Processing:** 5-10 seconds
- **Total:** ~30-70 seconds

#### Step 3: View Results

### Understanding Results

#### Change Metrics
- **Vegetation Change:** NDVI difference (%)
- **Urban Change:** Built-up area difference (%)
- **Moisture Change:** Water content difference (%)

**Interpretation:**
- **Positive %:** Increase (e.g., +15% vegetation = more greenery)
- **Negative %:** Decrease (e.g., -20% vegetation = deforestation)
- **Near 0%:** Little to no change

#### Visual Comparison
- **Historical Image:** Satellite image from start date
- **Current Image:** Satellite image from end date
- **Side-by-side:** Easy visual comparison

#### Change Heatmap
- **Red areas:** Significant decrease
- **Green areas:** Significant increase
- **Yellow/Orange:** Moderate changes
- **Blue:** Little to no change

### Example Scenarios

**Urban Expansion (e.g., New Delhi)**
- Vegetation Change: -15% to -25%
- Urban Change: +20% to +30%
- Moisture Change: -10% to -20%

**Deforestation (e.g., Amazon)**
- Vegetation Change: -30% to -50%
- Urban Change: +5% to +10%
- Moisture Change: -15% to -25%

**Agricultural Development**
- Vegetation Change: +10% to +20% (seasonal)
- Urban Change: +5% to +10%
- Moisture Change: Variable

---

## ⚠️ Risk Assessment

### Generating Risk Assessment
1. **Select location** on map
2. **Go to** "Risk Assessment" tab
3. **View** automatic risk analysis

### Risk Factors
- **Land Cover Vulnerability:** Based on land cover types
- **Weather Conditions:** Current weather impact
- **Environmental Stress:** Combined risk score

### Risk Levels
- **Low (Green):** Minimal environmental risk
- **Medium (Yellow):** Moderate risk, monitor conditions
- **High (Orange):** Elevated risk, take precautions
- **Critical (Red):** Severe risk, immediate attention needed

---

## 🌤️ Weather Data

Weather data is automatically fetched for selected location and displayed in the Risk Assessment tab.

### Weather Information
- **Current Temperature:** Real-time temperature
- **Feels Like:** Apparent temperature
- **Humidity:** Relative humidity percentage
- **Wind Speed:** Current wind speed
- **Precipitation:** Rainfall in last 1h/3h
- **Cloud Cover:** Cloudiness percentage
- **Visibility:** Visibility distance

---

## 💡 Tips & Best Practices

### For Best Results

**Location Selection:**
- Choose areas with clear satellite coverage
- Avoid extreme polar regions (limited data)
- Urban and agricultural areas work best

**Date Range:**
- Minimum: 30 days (for meaningful change)
- Recommended: 1-3 years (clear trends)
- Maximum: 10+ years (long-term analysis)

**Time of Year:**
- Consider seasonal variations
- Compare same seasons (e.g., summer to summer)
- Account for agricultural cycles

### Common Use Cases

**Urban Planning:**
- Monitor city expansion
- Track infrastructure development
- Assess green space changes

**Environmental Monitoring:**
- Deforestation detection
- Wetland changes
- Coastal erosion

**Agriculture:**
- Crop health monitoring
- Irrigation effectiveness
- Land use changes

**Disaster Assessment:**
- Flood extent mapping
- Fire damage assessment
- Post-disaster recovery

---

## 🔄 Workflow Example

### Complete Analysis Workflow

1. **Select Location**
   - Go to Map tab
   - Click on area of interest
   - Verify location name

2. **Land Cover Analysis**
   - Go to Land Cover tab
   - Analyze current land cover
   - Note dominant classes

3. **Change Detection**
   - Go to Change Detection tab
   - Select 3-year period
   - Analyze changes
   - Compare with land cover

4. **Risk Assessment**
   - Go to Risk Assessment tab
   - Review environmental risks
   - Check weather conditions

5. **Export/Document**
   - Take screenshots of results
   - Note key metrics
   - Document findings

---

## 📊 Data Sources

### Satellite Imagery
- **Primary:** Landsat 8/9 Collection 2 Level-2
- **Fallback:** Sentinel-2 Level-2A
- **Resolution:** 10-30 meters
- **Coverage:** Global

### Weather Data
- **Source:** OpenWeather API
- **Update Frequency:** Real-time
- **Coverage:** Global

### Land Cover Model
- **Model:** EfficientNetB3
- **Training Data:** EuroSAT dataset
- **Accuracy:** High (ImageNet pre-trained)

---

## ❓ FAQ

**Q: How often is satellite data updated?**
A: Landsat: every 16 days, Sentinel-2: every 5 days. Combined: near-daily coverage.

**Q: Can I analyze historical data?**
A: Yes! Landsat data available since 2013, Sentinel-2 since 2015.

**Q: Why does analysis take so long?**
A: Downloading and processing real satellite data takes time. Be patient!

**Q: What if no data is available?**
A: Try different dates or location. Some areas/periods have limited coverage due to clouds.

**Q: Can I export results?**
A: Currently, take screenshots. Export feature coming soon!

---

## 🆘 Need Help?

- Check [SETUP.md](SETUP.md) for installation issues
- Check [API_KEYS.md](API_KEYS.md) for API configuration
- Open an issue on GitHub for bugs or feature requests

---

**Happy Analyzing! 🛰️🌍**
