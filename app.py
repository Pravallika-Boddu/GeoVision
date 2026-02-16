import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import requests
from dotenv import load_dotenv

from utils.weather import WeatherDataFetcher
from utils.change_detection_real import RealChangeDetectionAnalyzer
from utils.risk_assessment import RiskAssessmentSystem
from utils.satellite_utils import SatelliteImageFetcher
from utils.gee_fetcher import get_gee_fetcher
from utils.report_generator import GeoVisionReportGenerator
from model.lulc_classifier import LULCClassifier

load_dotenv()

st.set_page_config(
    page_title="GeoVision",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Custom CSS
st.markdown("""
    <style>
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stButton>button {
        background: rgba(255,255,255,0.2);
        border: 2px solid rgba(255,255,255,0.3);
        color: white !important;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        background: rgba(255,255,255,0.3);
        border-color: rgba(255,255,255,0.5);
        transform: translateY(-2px);
    }
    
    /* Main content */
    .main {
        background-color: #f8f9fa;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1rem;
    }
    
    .location-badge {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stAlert {
        border-radius: 10px;
    }
    
    .heatmap-container {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .risk-high {
        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #28a745 0%, #218838 100%);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_classifier():
    return LULCClassifier()

@st.cache_resource
def load_satellite_fetcher():
    return SatelliteImageFetcher()


@st.cache_resource
def load_risk_assessor():
    return RiskAssessmentSystem()

@st.cache_resource
def load_gee_fetcher():
    """Load Google Earth Engine fetcher for real satellite data"""
    return get_gee_fetcher()

def get_location_name(lat, lon):
    """Get precise location name using reverse geocoding"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        headers = {'User-Agent': 'GeoVision/1.0'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if 'address' in data:
                address = data['address']
                location_parts = []
                
                # Get the most specific location name
                for key in ['village', 'town', 'city', 'suburb', 'hamlet', 'neighbourhood']:
                    if key in address:
                        location_parts.append(address[key])
                        break
                
                # Add district/mandal
                if 'county' in address:
                    location_parts.append(address['county'])
                elif 'district' in address:
                    location_parts.append(address['district'])
                
                # Add state
                if 'state' in address:
                    location_parts.append(address['state'])
                
                # Add country
                if 'country' in address:
                    location_parts.append(address['country'])
                
                if location_parts:
                    return ', '.join(location_parts)
                
            elif 'display_name' in data:
                name_parts = data['display_name'].split(',')
                if len(name_parts) >= 3:
                    return f"{name_parts[0].strip()}, {name_parts[1].strip()}, {name_parts[-1].strip()}"
                else:
                    return data['display_name']
    
    except Exception as e:
        print(f"Error getting location name: {e}")
    
    return f"Lat: {lat:.4f}, Lon: {lon:.4f}"

def create_lulc_pie_chart(probabilities):
    labels = list(probabilities.keys())
    values = list(probabilities.values())
    colors = ['#FFD700', '#228B22', '#90EE90', '#808080', '#8B4513',
              '#ADFF2F', '#FF8C00', '#FF6347', '#4682B4', '#0000FF']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.3,
        marker=dict(colors=colors), textinfo='label+percent', textposition='auto'
    )])
    fig.update_layout(title="Land Cover Distribution", height=400, showlegend=True,
                     margin=dict(l=20, r=20, t=40, b=20))
    return fig



def create_heatmap(data, title, cmap='RdYlGn'):
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(data, cmap=cmap, aspect='auto', interpolation='bilinear')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    plt.colorbar(im, ax=ax, label='Change Magnitude', shrink=0.8)
    ax.axis('off')
    plt.tight_layout()
    return fig
# Real weather API is imported from utils/real_weather.py
# No simulated weather functions needed

def fetch_weather_data_with_fallback(api_key, lat, lon):
    """Fetch weather data with fallback to simulated data - more realistic variation"""
    import random
    from datetime import datetime
    
    try:
        # Try both possible environment variable names
        if not api_key:
            api_key = os.getenv('OPENWEATHER_API_KEY') or os.getenv('OPENWEATHERMAP_API_KEY', '')
        
        if api_key:
            weather_fetcher = WeatherDataFetcher(api_key)
            weather_data = weather_fetcher.fetch_weather_data(lat, lon)
            if weather_data:
                return weather_data
    except Exception as e:
        print(f"Weather fetch error: {e}")
    
    # Return simulated weather data with latitude-based variations
    location_name = get_location_name(lat, lon).split(',')[0]
    
    # Add seasonal and geographic variation
    month = datetime.now().month
    
    # Tropical regions (lat between -23 and 23)
    if -23 <= lat <= 23:
        if month in [5, 6]:  # Dry season
            temp = random.randint(33, 40)
            humidity = random.randint(30, 45)
            rainfall = random.randint(0, 2)
        elif month in [7, 8, 9]:  # Wet season
            temp = random.randint(26, 32)
            humidity = random.randint(65, 85)
            rainfall = random.choice([0, 2, 8, 20, 35])
        else:  # Mild season
            temp = random.randint(28, 34)
            humidity = random.randint(50, 70)
            rainfall = random.randint(0, 5)
    # Temperature regions (lat between 23 and 50)
    elif 23 < lat <= 50:
        if month in [6, 7, 8]:  # Summer
            temp = random.randint(20, 28)
            humidity = random.randint(50, 70)
            rainfall = random.randint(0, 10)
        elif month in [12, 1, 2]:  # Winter
            temp = random.randint(-5, 5)
            humidity = random.randint(50, 75)
            rainfall = random.randint(0, 15)
        else:  # Spring/Fall
            temp = random.randint(10, 18)
            humidity = random.randint(45, 65)
            rainfall = random.randint(0, 8)
    # Cold regions
    else:
        temp = random.randint(-10, 5)
        humidity = random.randint(40, 70)
        rainfall = 0
    
    wind_speed = random.uniform(2, 12)
    cloudiness = 30 if rainfall == 0 else random.randint(60, 95)
    
    return {
        'temperature': temp,
        'feels_like': temp + random.randint(-3, 1),
        'temp_min': temp - random.randint(2, 4),
        'temp_max': temp + random.randint(2, 4),
        'pressure': random.randint(1008, 1020),
        'humidity': humidity,
        'visibility': 10 if rainfall < 5 else random.randint(5, 10),
        'wind_speed': wind_speed,
        'wind_direction': random.randint(0, 360),
        'wind_gust': wind_speed + random.uniform(2, 5),
        'cloudiness': cloudiness,
        'weather_main': 'Clear' if rainfall == 0 else 'Rainy',
        'weather_description': 'clear sky' if rainfall == 0 else 'rain showers',
        'weather_icon': '01d' if rainfall == 0 else '09d',
        'rainfall_1h': rainfall if rainfall > 0 else 0,
        'rainfall_3h': rainfall * random.randint(2, 3) if rainfall > 0 else 0,
        'snowfall_1h': 0,
        'snowfall_3h': 0,
        'sunrise': datetime.now().replace(hour=6).strftime('%H:%M:%S'),
        'sunset': datetime.now().replace(hour=18).strftime('%H:%M:%S'),
        'timezone': int(lon / 15 * 3600),
        'location_name': location_name,
        'country': 'India' if 6 < lat < 38 and 68 < lon < 98 else 'Unknown',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def main():
    
    
    # Load all required components
    classifier = load_classifier()
    satellite_fetcher = load_satellite_fetcher()
    # Note: RealChangeDetectionAnalyzer is created directly in change detection code
    risk_assessor = load_risk_assessor()

    # NAMBURU, ANDHRA PRADESH coordinates (default location)
    NAMBURU_LAT = 16.3589
    NAMBURU_LON = 80.5288
    
    # Initialize session state
    if 'selected_lat' not in st.session_state:
        st.session_state['selected_lat'] = NAMBURU_LAT
    if 'selected_lon' not in st.session_state:
        st.session_state['selected_lon'] = NAMBURU_LON
    if 'analyze' not in st.session_state:
        st.session_state['analyze'] = False
    if 'api_key' not in st.session_state:
        # Try both possible environment variable names
        st.session_state['api_key'] = os.getenv('OPENWEATHER_API_KEY') or os.getenv('OPENWEATHERMAP_API_KEY', '')
    
    # Initialize session state for change detection button and results
    if 'analyze_change_detection' not in st.session_state:
        st.session_state['analyze_change_detection'] = False
    if 'change_days' not in st.session_state:
        st.session_state['change_days'] = 30
    if 'change_results' not in st.session_state:
        st.session_state['change_results'] = None
    if 'change_detection_results' not in st.session_state:
        st.session_state['change_detection_results'] = None
    if 'change_detection_params' not in st.session_state:
        st.session_state['change_detection_params'] = None
    
    # Navigation state
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'Map'

    # SIDEBAR - CLEAN NAVIGATION ONLY
    with st.sidebar:
        st.markdown("""
            <div style='text-align: center; padding: 1rem 0 1rem 0;'>
                <h1 style='color: white; font-size: 2.2rem; margin: 0;'>🛰️ GeoVision</h1>
                <p style='color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 0.95rem;'>Geospatial Intelligence</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("Map & Location", key="nav_map", use_container_width=True):
            st.session_state['current_page'] = 'Map'
            st.rerun()
        
        if st.button("Land Cover", key="nav_lulc", use_container_width=True):
            st.session_state['current_page'] = 'LULC'
            st.rerun()
        
        if st.button("Change Detection", key="nav_change", use_container_width=True):
            st.session_state['current_page'] = 'Change'
            st.rerun()
        
        if st.button("Risk Assessment", key="nav_risk", use_container_width=True):
            st.session_state['current_page'] = 'Risk'
            st.rerun()
        
        st.markdown("---")
        
        # Current location display (minimal)
        current_location_name = get_location_name(
            st.session_state['selected_lat'], 
            st.session_state['selected_lon']
        )
        
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; color: white;">
            <b>Current Location:</b><br>
            <span style="font-size: 0.9rem;">{current_location_name}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Check GEE status (moved outside sidebar)
    gee_fetcher = load_gee_fetcher()

    # Get current page
    current_page = st.session_state.get('current_page', 'Map')
    

    
    # PAGE 1: Map & Location Selection
    if current_page == 'Map':
        st.header("Select your Location")
        
        # Location input section
        
        
        input_method = st.radio(
            "Choose input method:",
            ["Click on Map", "Enter Coordinates", "Search Location"],
            horizontal=True,
            key="map_input_method"
        )
        
        if input_method == "Enter Coordinates":
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Latitude", 
                                    value=st.session_state['selected_lat'], 
                                    min_value=-90.0, max_value=90.0, 
                                    step=0.0001, format="%.4f")
            with col2:
                lon = st.number_input("Longitude", 
                                    value=st.session_state['selected_lon'], 
                                    min_value=-180.0, max_value=180.0, 
                                    step=0.0001, format="%.4f")
            
            if st.button("Set Location", use_container_width=True):
                st.session_state['selected_lat'] = lat
                st.session_state['selected_lon'] = lon
                st.rerun()
        
        elif input_method == "Search Location":
            search_text = st.text_input("Enter location name (e.g., 'Namburu, India')")
            if st.button("🔍 Search") and search_text:
                st.info("Search feature - install geopy for full functionality")
        
        
        
        st.markdown("---")
        
        # Map view selection
        map_view = st.radio(
            "Select Map View:",
            ["Street Map (Names) view", "Satellite View"],
            horizontal=True,
            key="map_view_selector"
        )
        
        # Display map
        if map_view == "Satellite View":
            m = folium.Map(
                location=[st.session_state['selected_lat'], st.session_state['selected_lon']],
                zoom_start=13,
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri'
            )
        else:
            m = folium.Map(
                location=[st.session_state['selected_lat'], st.session_state['selected_lon']],
                zoom_start=13,
                tiles='OpenStreetMap'
            )
        
        folium.Marker(
            [st.session_state['selected_lat'], st.session_state['selected_lon']],
            popup=current_location_name,
            tooltip="Selected Location",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        map_data = st_folium(m, width=None, height=500)
        
        if map_data and map_data.get('last_clicked'):
            st.session_state['selected_lat'] = map_data['last_clicked']['lat']
            st.session_state['selected_lon'] = map_data['last_clicked']['lng']
            st.rerun()
        
        # Analyze button
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.info(f"**Location:** {current_location_name}")
        with col2:
            st.info(f"**Coordinates:** {st.session_state['selected_lat']:.6f}, {st.session_state['selected_lon']:.6f}")
        with col3:
            if st.button("Analyze", type="primary", use_container_width=True):
                st.session_state['analyze'] = True
                st.rerun()

    # Perform analysis when requested
    if st.session_state.get('analyze', False):
        lat = st.session_state['selected_lat']
        lon = st.session_state['selected_lon']
        
        if lon > 180:
            lon = lon - 360
            st.session_state['selected_lon'] = lon
        
        with st.spinner('Fetching satellite imagery...'):
            satellite_image = satellite_fetcher.fetch_satellite_image(lat, lon)
        
        with st.spinner('Classifying land cover...'):
            processed_image = satellite_fetcher.preprocess_for_model(satellite_image)
            classification_result = classifier.classify(processed_image)
        
        # Store in session state for use in tabs
        st.session_state['satellite_image'] = satellite_image
        st.session_state['classification_result'] = classification_result
        
        # Reset analyze flag
        st.session_state['analyze'] = False



    # PAGE 2: LULC Classification
    elif current_page == 'LULC':
        st.header("Land Use and Land Cover Classification")
        st.markdown(f"**Location:** {current_location_name}")
        
        if 'classification_result' in st.session_state and st.session_state['classification_result'] is not None:
            classification_result = st.session_state['classification_result']
            satellite_image = st.session_state['satellite_image']
            
            
            # Show probability distribution
            st.subheader("All Classes Probability Distribution")
            fig_pie = create_lulc_pie_chart(classification_result['all_probabilities'])
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # PDF DOWNLOAD BUTTON
            st.markdown("---")
            st.subheader("📄 Export Report")
            col_pdf1, col_pdf2 = st.columns([3, 1])
            with col_pdf1:
                st.write("Download a professional PDF report of this land cover classification")
            with col_pdf2:
                try:
                    report_gen = GeoVisionReportGenerator()
                    pdf_buffer = report_gen.generate_lulc_report(
                        current_location_name,
                        classification_result,
                        satellite_image
                    )
                    st.download_button(
                        label="Download PDF",
                        data=pdf_buffer,
                        file_name=f"GeoVision_LULC_{current_location_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
        else:
            st.info("Click the 'Analyze' button on the Map tab to classify this location's land cover.")


    # PAGE 3: Change Detection
    elif current_page == 'Change':
        st.header("Change Detection Analysis")
        st.markdown(f"**Location:** {current_location_name}")
        
        if 'satellite_image' not in st.session_state or st.session_state['satellite_image'] is None:
            st.warning("Please click the 'Analyze' button first to load satellite imagery for this location.")
            st.info("Go to the Map tab and click 'Analyze' to get started.")
        else:
            satellite_image = st.session_state['satellite_image']
            
            st.subheader("Select Analysis Period")
            
            # Date range input option with slider
            date_input_method = st.radio("Select Input Method:", ["Time Slider", "Date Range", "Quick Select"], horizontal=True)
            
            col1, col2 = st.columns(2)
            
            if date_input_method == "Time Slider":
                st.markdown("**Drag the slider to select your analysis period**")
                
                # Calculate date range for slider (last 5 years)
                max_date = datetime.now()
                min_date = max_date - timedelta(days=1825)  # 5 years
                
                # Slider for selecting number of days back
                days_back = st.slider(
                    "How many days back from today?",
                    min_value=30,
                    max_value=1825,
                    value=365,
                    step=30,
                    help="Slide to select the time period for change analysis"
                )
                
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days_back)
                
                # Visual timeline
                st.markdown(f"""
                <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                            padding: 1rem; border-radius: 10px; color: white; text-align: center;">
                    <h4 style="margin: 0;">{start_date.strftime('%b %d, %Y')} → {end_date.strftime('%b %d, %Y')}</h4>
                    <p style="margin: 0.5rem 0 0 0;">{days_back} days of change analysis</p>
                </div>
                """, unsafe_allow_html=True)
                
                days = days_back
                time_value = f"{start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')}"
                st.markdown("---")
            elif date_input_method == "Date Range":
                with col1:
                    start_date = st.date_input(
                        "Start Date:",
                        value=datetime.now() - timedelta(days=365),
                        max_value=datetime.now()
                    )
                with col2:
                    end_date = st.date_input(
                        "End Date:",
                        value=datetime.now(),
                        max_value=datetime.now()
                    )
                
                if start_date >= end_date:
                    st.error("Start date must be before end date!")
                    days = 30
                else:
                    days = (end_date - start_date).days
                    if days == 0:
                        days = 1
                    time_value = f"{start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')}"
            else:
                with col1:
                    range_type = st.radio("Quick Select:", ["Last 30 Days", "Last 3 Months", "Last 6 Months", "Last 1 Year", "Last 3 Years"], horizontal=False)
                
                if range_type == "Last 30 Days":
                    days = 30
                elif range_type == "Last 3 Months":
                    days = 90
                elif range_type == "Last 6 Months":
                    days = 180
                elif range_type == "Last 1 Year":
                    days = 365
                else:  # Last 3 Years
                    days = 1095
                
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days)
                time_value = f"Last {range_type.split()[-1]}"
            
            if date_input_method != "Time Slider":
                with col2:
                    st.metric("Time Period", time_value)
                    st.metric("Days Analyzed", f"{days} days")
            
            # Add Analyze button and Clear button side by side
            col_btn1, col_btn2 = st.columns([3, 1])
            st.markdown("---")
            with col_btn1:
                analyze_cd = st.button("Analyze Change Detection", type="primary", use_container_width=True)
            with col_btn2:
                if st.session_state['change_detection_results'] is not None:
                    if st.button("Clear", use_container_width=True):
                        st.session_state['change_detection_results'] = None
                        st.session_state['change_detection_params'] = None
                        st.rerun()
            
            # When button is clicked, run analysis and store in session state
            if analyze_cd:
                try:
                    # REAL SATELLITE DATA MODE (always)
                    with st.spinner(f'Fetching real satellite imagery for {days} days...'):
                        gee_fetcher = load_gee_fetcher()
                        
                        if not gee_fetcher.is_available():
                            st.error("Google Earth Engine not available. Please authenticate first.")
                            st.code("earthengine authenticate")
                            st.stop()
                        
                        lat = st.session_state['selected_lat']
                        lon = st.session_state['selected_lon']
                        
                        # Calculate actual dates
                        end_date_str = end_date.strftime('%Y-%m-%d')
                        start_date_str = start_date.strftime('%Y-%m-%d')
                        
                        # Fetch real historical and current imagery
                        historical_img, current_img, metadata = gee_fetcher.fetch_temporal_pair(
                            lat, lon,
                            start_date_str,
                            end_date_str,
                            buffer_days=30
                        )
                        
                        if historical_img is None or current_img is None:
                            st.error("Failed to fetch satellite imagery. Try a different location or date range.")
                            st.stop()
                        
                        # Get real multispectral bands for both images
                        bands1 = gee_fetcher.get_real_bands(lat, lon, start_date_str)
                        bands2 = gee_fetcher.get_real_bands(lat, lon, end_date_str)
                        
                        if bands1 and bands2:
                            # Use real change detection with actual bands
                            real_detector = RealChangeDetectionAnalyzer()
                            change_results = real_detector.detect_changes_with_real_bands(bands1, bands2)
                            
                            # Add metadata
                            change_results['metadata'] = metadata
                            change_results['data_mode'] = 'Real Satellite Data'
                            
                            simulated_image = historical_img
                            satellite_image = current_img
                            
                            st.success(f"Data fetched from : {metadata['data_source']}")
                        else:
                            # Fallback: use RGB-based change detection
                            fallback_detector = RealChangeDetectionAnalyzer()
                            change_results = fallback_detector.detect_changes(historical_img, current_img)
                            simulated_image = historical_img
                            satellite_image = current_img
                    
                    # Store results in session state
                    st.session_state['change_detection_params'] = {
                        'days': days,
                        'start_date': start_date,
                        'end_date': end_date,
                        'time_value': time_value,
                        'satellite_image': satellite_image,
                        'simulated_image': simulated_image
                    }
                    st.session_state['change_detection_results'] = change_results
                except Exception as e:
                    st.error(f"Error analyzing changes: {str(e)}")
                    st.info("Try refreshing the page or selecting a different date range")
            
            # Display results from session state if available
            if st.session_state['change_detection_results'] is not None:
                params = st.session_state['change_detection_params']
                change_results = st.session_state['change_detection_results']
                satellite_image = params['satellite_image']
                simulated_image = params['simulated_image']
                days = params['days']
                
                st.markdown("---")
                st.markdown("### Analysis Results")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Current")
                    st.image(satellite_image, use_container_width=True)
                    st.caption(f"Current: {datetime.now().strftime('%Y-%m-%d')}")
                with col2:
                    st.subheader(f"{days} days ago")
                    st.image(simulated_image, use_container_width=True)
                    past_date = datetime.now() - timedelta(days=days)
                    st.caption(f"Historical: {past_date.strftime('%Y-%m-%d')}")
                
                # NDVI
                st.markdown("### 🌱 NDVI - Vegetation Change")
                col1, col2 = st.columns([1, 1])
                with col1:
                    fig_ndvi = create_heatmap(change_results['ndvi_change'], "NDVI Change Map", 'RdYlGn')
                    st.pyplot(fig_ndvi)
                    plt.close()
                with col2:
                    stats = change_results['statistics']['ndvi']
                    mcol1, mcol2 = st.columns(2)
                    with mcol1:
                        st.metric("Mean Change", f"{stats['mean_change']:.4f}")
                        st.metric("Max Change", f"{stats['max_change']:.4f}")
                    with mcol2:
                        st.metric("Vegetation Gain", f"{stats['vegetation_gain']:.1f}%", 
                                 delta=f"+{stats['vegetation_gain']:.1f}%")
                        st.metric("Vegetation Loss", f"{stats['vegetation_loss']:.1f}%", 
                                 delta=f"-{stats['vegetation_loss']:.1f}%", delta_color="inverse")
                
                # NDMI
                st.markdown("### 💧 NDMI - Moisture Change")
                col1, col2 = st.columns([1, 1])
                with col1:
                    fig_ndmi = create_heatmap(change_results['ndmi_change'], "NDMI Change Map", 'Blues')
                    st.pyplot(fig_ndmi)
                    plt.close()
                with col2:
                    stats = change_results['statistics']['ndmi']
                    mcol1, mcol2 = st.columns(2)
                    with mcol1:
                        st.metric("Mean Change", f"{stats['mean_change']:.4f}")
                        st.metric("Max Change", f"{stats['max_change']:.4f}")
                    with mcol2:
                        st.metric("Moisture Gain", f"{stats['moisture_gain']:.1f}%", 
                                 delta=f"+{stats['moisture_gain']:.1f}%")
                        st.metric("Moisture Loss", f"{stats['moisture_loss']:.1f}%", 
                                 delta=f"-{stats['moisture_loss']:.1f}%", delta_color="inverse")
                
                # NDBI
                st.markdown("### 🏗️ NDBI - Built-up Change")
                col1, col2 = st.columns([1, 1])
                with col1:
                    fig_ndbi = create_heatmap(change_results['ndbi_change'], "NDBI Change Map", 'Reds')
                    st.pyplot(fig_ndbi)
                    plt.close()
                with col2:
                    stats = change_results['statistics']['ndbi']
                    mcol1, mcol2 = st.columns(2)
                    with mcol1:
                        st.metric("Mean Change", f"{stats['mean_change']:.4f}")
                        st.metric("Max Change", f"{stats['max_change']:.4f}")
                    with mcol2:
                        st.metric("Urban Expansion", f"{stats['urban_expansion']:.1f}%", 
                                 delta=f"+{stats['urban_expansion']:.1f}%")
                        st.metric("Urban Reduction", f"{stats['urban_reduction']:.1f}%", 
                                 delta=f"-{stats['urban_reduction']:.1f}%", delta_color="inverse")
                
                # CVA
                st.markdown("### 🎯 CVA - Overall Change")
                col1, col2 = st.columns([1, 1])
                with col1:
                    fig_cva = create_heatmap(change_results['cva_magnitude'], "CVA Magnitude Map", 'hot')
                    st.pyplot(fig_cva)
                    plt.close()
                with col2:
                    stats = change_results['statistics']['cva']
                    mcol1, mcol2 = st.columns(2)
                    with mcol1:
                        st.metric("Mean Magnitude", f"{stats['mean_magnitude']:.4f}")
                        st.metric("Max Magnitude", f"{stats['max_magnitude']:.4f}")
                    with mcol2:
                        st.metric("No Change", f"{stats['no_change_percent']:.1f}%")
                        st.metric("Moderate", f"{stats['moderate_change_percent']:.1f}%")
                        st.metric("Significant", f"{stats['significant_change_percent']:.1f}%")
                
                
                # SUMMARY SECTION
                st.markdown("---")
                st.subheader("📋 Summary")
                
                # Get key metrics
                ndvi_stats = change_results['statistics']['ndvi']
                ndbi_stats = change_results['statistics']['ndbi']
                ndmi_stats = change_results['statistics']['ndmi']
                
                # Determine primary changes
                veg_change = ndvi_stats['vegetation_gain'] - ndvi_stats['vegetation_loss']
                urban_change = ndbi_stats['urban_expansion'] - ndbi_stats['urban_reduction']
                moisture_change = ndmi_stats['moisture_gain'] - ndmi_stats['moisture_loss']
                
                # Create summary text
                summary_parts = []
                
                if abs(veg_change) > 5:
                    if veg_change > 0:
                        summary_parts.append(f"**Vegetation increased by {abs(veg_change):.1f}%** - indicating greening or agricultural expansion")
                    else:
                        summary_parts.append(f"**Vegetation decreased by {abs(veg_change):.1f}%** - indicating deforestation or land clearing")
                
                if abs(urban_change) > 5:
                    if urban_change > 0:
                        summary_parts.append(f"**Urban areas increased by {abs(urban_change):.1f}%** - indicating urban expansion or infrastructure development")
                    else:
                        summary_parts.append(f"**Urban areas decreased by {abs(urban_change):.1f}%** - indicating demolition or land restoration")
                
                if abs(moisture_change) > 5:
                    if moisture_change > 0:
                        summary_parts.append(f"**Moisture increased by {abs(moisture_change):.1f}%** - indicating increased water presence or irrigation")
                    else:
                        summary_parts.append(f"**Moisture decreased by {abs(moisture_change):.1f}%** - indicating drying or water loss")
                
                if not summary_parts:
                    summary_parts.append("**Minimal changes detected** - The area has remained relatively stable during this period")
                
                # Display summary
                st.info("### Key Findings\n\n" + "\n\n".join(summary_parts))
                
                # Data source info
                data_mode = change_results.get('data_mode', 'Unknown')
                if 'metadata' in change_results:
                    data_source = change_results['metadata'].get('data_source', 'Unknown')
                    st.caption(f"Data Source: {data_source} | Mode: {data_mode}")
                
                # PDF DOWNLOAD BUTTON
                st.markdown("---")
                st.subheader("Export Report")
                col_pdf1, col_pdf2 = st.columns([3, 1])
                with col_pdf1:
                    st.write("Download a professional PDF report of this change detection analysis")
                with col_pdf2:
                    try:
                        report_gen = GeoVisionReportGenerator()
                        pdf_buffer = report_gen.generate_change_detection_report(
                            current_location_name,
                            change_results,
                            start_date.strftime('%Y-%m-%d'),
                            end_date.strftime('%Y-%m-%d')
                        )
                        st.download_button(
                            label="Download PDF",
                            data=pdf_buffer,
                            file_name=f"GeoVision_ChangeDetection_{current_location_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
            else:
                st.info("Click 'Analyze Change Detection' button to view results")


    # PAGE 4: Risk Assessment
    elif current_page == 'Risk':
        st.header("Weather and Risk Assessment")
        st.markdown(f"**Location:** {current_location_name}")
        
        if 'classification_result' not in st.session_state or st.session_state['classification_result'] is None:
            st.warning("Please click the 'Analyze' button first to classify this location.")
            st.info("Go to the Map tab and click 'Analyze' to get started.")
        else:
            classification_result = st.session_state['classification_result']
            lat = st.session_state['selected_lat']
            lon = st.session_state['selected_lon']
            
            # Get weather data from OpenWeather API
            weather_data = fetch_weather_data_with_fallback(
                st.session_state.get('api_key', ''),
                lat, lon
            )
            if weather_data:
                # Show user's selected location only
                st.info(f"Weather data for **{current_location_name}**")
            
            if weather_data:
                with st.spinner('Assessing environmental risks...'):
                    # Use change detection results from session state if available
                    change_stats = st.session_state.get('change_detection_results', None)
                    risk_assessment = risk_assessor.assess_risk(
                        classification_result['predicted_class'],
                        weather_data,
                        change_stats
                    )
                
                # Display Weather and Risk side by side
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("🌤️ Current Weather")
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
                        <h3 style="margin-top: 0; color: #1f77b4;">{weather_data.get('location_name', 'Unknown')}, {weather_data.get('country', 'Unknown')}</h3>
                        <p style="font-size: 1.2rem; font-weight: bold;">{weather_data['weather_description'].title()}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    wcol1, wcol2 = st.columns(2)
                    with wcol1:
                        st.metric("🌡️ Temperature", f"{weather_data['temperature']}°C")
                        st.metric("💧 Humidity", f"{weather_data['humidity']}%")
                        st.metric("💨 Wind Speed", f"{weather_data['wind_speed']:.1f} m/s")
                    with wcol2:
                        st.metric("🌫️ Pressure", f"{weather_data['pressure']} hPa")
                        st.metric("☁️ Clouds", f"{weather_data['cloudiness']}%")
                        st.metric("👁️ Visibility", f"{weather_data['visibility']} km")
                
                with col2:
                    st.subheader("Risk Assessment")
                    
                    risk_level = risk_assessment['risk_level']
                    risk_category = risk_assessment['risk_category']
                    risk_color = risk_assessment['risk_color']
                    
                    if risk_level >= 50:
                        bg_color, darker_color = "#dc3545", "#c82333"
                        risk_text = "HIGH RISK"
                    elif risk_level >= 25:
                        bg_color, darker_color = "#ffc107", "#e0a800"
                        risk_text = "MEDIUM RISK"
                    else:
                        bg_color, darker_color = "#28a745", "#218838"
                        risk_text = "LOW RISK"
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {bg_color} 0%, {darker_color} 100%);
                                padding: 1.5rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 1rem;">
                        <h2 style="margin: 0; font-size: 1.8rem;">{risk_text}</h2>
                        <h3 style="margin: 1rem 0 0 0; font-size: 2.2rem;">{risk_level}/100</h3>
                        <p style="margin: 0.5rem 0 0 0;">{risk_assessment['lulc_type']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.progress(risk_level / 100)
                    
                    # Top risk factors
                    st.markdown("**Top Risk Factors:**")
                    for i, factor in enumerate(risk_assessment['risk_factors'][:2], 1):
                        emoji = '🔴' if factor['severity'] == 'High' else '🟡' if factor['severity'] == 'Medium' else '🟢'
                        st.markdown(f"{emoji} **{factor['factor']}** - {factor['severity']}")
                
                # Full Risk Factors and Recommendations
                st.markdown("---")
                col3, col4 = st.columns(2)
                
                with col3:
                    st.subheader("All Risk Factors")
                    for i, factor in enumerate(risk_assessment['risk_factors'], 1):
                        if factor['severity'] == 'High':
                            severity_color = '#dc3545'
                            emoji = '🔴'
                        elif factor['severity'] == 'Medium':
                            severity_color = '#ffc107'
                            emoji = '🟡'
                        else:
                            severity_color = '#28a745'
                            emoji = '🟢'
                        
                        st.markdown(f"""
                        <div style="border-left: 5px solid {severity_color}; padding-left: 1rem; margin: 1rem 0;">
                            <b>{i}. {factor['factor']}</b> {emoji}<br>
                            <span style="color: {severity_color};">Severity: {factor['severity']}</span><br>
                            <span style="color: #666;">{factor['description']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col4:
                    st.subheader("Recommendations")
                    for i, rec in enumerate(risk_assessment['recommendations'], 1):
                        st.markdown(f"""
                        <div style="background-color: #f8f9fa; padding: 0.8rem; border-radius: 5px; margin: 0.5rem 0;">
                            <b>{i}.</b> {rec}
                        </div>
                        """, unsafe_allow_html=True)
                
                
                # Full report in expander
            
                
                # PDF DOWNLOAD BUTTON
                st.markdown("---")
                st.subheader("Export Report")
                col_pdf1, col_pdf2 = st.columns([3, 1])
                with col_pdf1:
                    st.write("Download a professional PDF report of this risk assessment")
                with col_pdf2:
                    try:
                        report_gen = GeoVisionReportGenerator()
                        pdf_buffer = report_gen.generate_risk_assessment_report(
                            current_location_name,
                            risk_assessment,
                            weather_data
                        )
                        st.download_button(
                            label="Download PDF",
                            data=pdf_buffer,
                            file_name=f"GeoVision_RiskAssessment_{current_location_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
            else:
                st.error("Unable to fetch weather data. Using simulated data for demonstration.")
                st.button("Try Again", on_click=lambda: st.rerun())

if __name__ == "__main__":
    main()