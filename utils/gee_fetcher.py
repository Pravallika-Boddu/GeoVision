"""
Google Earth Engine Satellite Data Fetcher
Fetches real Landsat 8/9 and Sentinel-2 imagery for change detection
"""

try:
    import ee
    EE_AVAILABLE = True
except ImportError:
    EE_AVAILABLE = False
    print("⚠️ earthengine-api not installed. Real satellite data will not be available.")
    print("💡 Install with: pip install earthengine-api")

import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict
import requests
from io import BytesIO
from PIL import Image

class GEEDataFetcher:
    """Fetch real satellite imagery from Google Earth Engine"""
    
    def __init__(self):
        """Initialize Google Earth Engine"""
        self.initialized = False
        self.use_landsat = True  # Primary: Landsat 8/9
        self.use_sentinel = False  # Fallback: Sentinel-2
        
        if not EE_AVAILABLE:
            print("⚠️ Google Earth Engine not available (ee module not installed)")
            self.initialized = False
            return
        
        try:
            # Initialize with user's GEE project
            ee.Initialize(project='ee-boddupravallika04')
            self.initialized = True
            print("✅ Google Earth Engine initialized successfully with project: ee-boddupravallika04")
        except Exception as e:
            # Try legacy initialization as fallback
            try:
                ee.Initialize()
                self.initialized = True
                print("✅ Google Earth Engine initialized successfully (legacy mode)")
            except Exception as e2:
                print(f"⚠️ GEE initialization failed: {e2}")
                print("💡 Run: earthengine authenticate")
                self.initialized = False
    
    def is_available(self) -> bool:
        """Check if GEE is available"""
        return self.initialized
    
    def fetch_temporal_pair(
        self, 
        lat: float, 
        lon: float, 
        start_date: str, 
        end_date: str,
        buffer_days: int = 30,
        image_size: int = 256
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Dict]:
        """
        Fetch real satellite imagery for two time periods
        
        Args:
            lat, lon: Location coordinates
            start_date: Historical date (e.g., '2015-01-01')
            end_date: Recent date (e.g., '2026-01-01')
            buffer_days: Days to composite around each date
            image_size: Output image size in pixels
        
        Returns:
            (historical_image, current_image, metadata)
        """
        if not self.initialized:
            return None, None, {'error': 'GEE not initialized'}
        
        try:
            # Create region of interest (5km buffer around point)
            point = ee.Geometry.Point([lon, lat])
            region = point.buffer(2500).bounds()  # 5km x 5km area
            
            # Fetch historical image
            print(f"📡 Fetching historical imagery around {start_date}...")
            img1, meta1 = self._get_composite(
                region, start_date, buffer_days, image_size
            )
            
            # Fetch current image
            print(f"📡 Fetching current imagery around {end_date}...")
            img2, meta2 = self._get_composite(
                region, end_date, buffer_days, image_size
            )
            
            metadata = {
                'historical': meta1,
                'current': meta2,
                'location': {'lat': lat, 'lon': lon},
                'data_source': 'Landsat 8/9' if self.use_landsat else 'Sentinel-2'
            }
            
            return img1, img2, metadata
            
        except Exception as e:
            print(f"❌ Error fetching satellite data: {e}")
            return None, None, {'error': str(e)}
    
    def _get_composite(
        self, 
        region: ee.Geometry, 
        center_date: str, 
        buffer_days: int,
        image_size: int
    ) -> Tuple[np.ndarray, Dict]:
        """
        Get cloud-free composite for a time period
        
        Returns:
            (image_array, metadata)
        """
        # Calculate date range
        center = datetime.strptime(center_date, '%Y-%m-%d')
        start = (center - timedelta(days=buffer_days)).strftime('%Y-%m-%d')
        end = (center + timedelta(days=buffer_days)).strftime('%Y-%m-%d')
        
        # Try Landsat first
        if self.use_landsat:
            try:
                composite, metadata = self._get_landsat_composite(
                    region, start, end, image_size
                )
                return composite, metadata
            except Exception as e:
                print(f"⚠️ Landsat failed, trying Sentinel-2: {e}")
                self.use_sentinel = True
                self.use_landsat = False
        
        # Use Sentinel-2 (fallback or by choice)
        composite, metadata = self._get_sentinel_composite(
            region, start, end, image_size
        )
        return composite, metadata
    
    def _get_landsat_composite(
        self, 
        region: ee.Geometry, 
        start_date: str, 
        end_date: str,
        image_size: int
    ) -> Tuple[np.ndarray, Dict]:
        """
        Get Landsat 8/9 Surface Reflectance composite
        
        Uses Collection 2 Level-2 (atmospherically corrected)
        """
        try:
            # Landsat 8 Collection 2 Level-2 (Surface Reflectance)
            collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
                .filterBounds(region) \
                .filterDate(start_date, end_date) \
                .filter(ee.Filter.lt('CLOUD_COVER', 50))  # Relaxed from 30% to 50%
            
            # Check if we have any images
            count = collection.size().getInfo()
            
            if count == 0:
                # Try with even more relaxed cloud cover
                collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
                    .filterBounds(region) \
                    .filterDate(start_date, end_date) \
                    .filter(ee.Filter.lt('CLOUD_COVER', 80))
                
                count = collection.size().getInfo()
                
                if count == 0:
                    raise Exception(f"No Landsat images found for {start_date} to {end_date}. Try Sentinel-2 or different dates.")
            
            # Apply cloud masking
            collection = collection.map(self._mask_landsat_clouds)
            
            # Get composite (median to remove remaining clouds)
            composite = collection.median()
            
            # Select and scale bands
            # Landsat 8 bands: SR_B4 (Red), SR_B5 (NIR), SR_B6 (SWIR1)
            composite = composite.select(['SR_B4', 'SR_B5', 'SR_B6', 'SR_B3', 'SR_B2']) \
                .multiply(0.0000275).add(-0.2)  # Scale factors for Collection 2
            
            # Clip to region
            composite = composite.clip(region)
            
            # Download as numpy array
            image_array = self._ee_to_numpy(composite, region, image_size)
            
            metadata = {
                'sensor': 'Landsat 8',
                'date_range': f"{start_date} to {end_date}",
                'image_count': count,
                'cloud_masked': True,
                'atmospheric_correction': 'Surface Reflectance (Collection 2 Level-2)'
            }
            
            return image_array, metadata
            
        except Exception as e:
            print(f"⚠️ Landsat fetch failed: {e}")
            raise
    
    def _get_sentinel_composite(
        self, 
        region: ee.Geometry, 
        start_date: str, 
        end_date: str,
        image_size: int
    ) -> Tuple[np.ndarray, Dict]:
        """
        Get Sentinel-2 Surface Reflectance composite
        
        Fallback option if Landsat not available
        """
        # Sentinel-2 Level-2A (Surface Reflectance)
        collection = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filterBounds(region) \
            .filterDate(start_date, end_date) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
        
        # Apply cloud masking
        collection = collection.map(self._mask_sentinel_clouds)
        
        # Get composite
        composite = collection.median()
        
        # Select bands: B4 (Red), B8 (NIR), B11 (SWIR1)
        composite = composite.select(['B4', 'B8', 'B11', 'B3', 'B2']) \
            .divide(10000)  # Scale to reflectance
        
        composite = composite.clip(region)
        
        count = collection.size().getInfo()
        
        image_array = self._ee_to_numpy(composite, region, image_size)
        
        metadata = {
            'sensor': 'Sentinel-2',
            'date_range': f"{start_date} to {end_date}",
            'image_count': count,
            'cloud_masked': True,
            'atmospheric_correction': 'Surface Reflectance (Level-2A)'
        }
        
        return image_array, metadata
    
    def _mask_landsat_clouds(self, image: ee.Image) -> ee.Image:
        """
        Mask clouds in Landsat 8 using QA_PIXEL band
        """
        qa = image.select('QA_PIXEL')
        
        # Bits 3 and 4 are cloud and cloud shadow
        cloud_bit = 1 << 3
        shadow_bit = 1 << 4
        
        # Create mask
        mask = qa.bitwiseAnd(cloud_bit).eq(0) \
            .And(qa.bitwiseAnd(shadow_bit).eq(0))
        
        return image.updateMask(mask)
    
    def _mask_sentinel_clouds(self, image: ee.Image) -> ee.Image:
        """
        Mask clouds in Sentinel-2 using QA60 band
        """
        qa = image.select('QA60')
        
        # Bits 10 and 11 are clouds and cirrus
        cloud_mask = qa.bitwiseAnd(1 << 10).eq(0) \
            .And(qa.bitwiseAnd(1 << 11).eq(0))
        
        return image.updateMask(cloud_mask)
    
    def _ee_to_numpy(
        self, 
        image: ee.Image, 
        region: ee.Geometry, 
        size: int
    ) -> np.ndarray:
        """
        Convert Earth Engine image to numpy array
        
        Uses GeoTIFF format to handle floating-point data properly
        """
        try:
            # Download as GeoTIFF (handles floating-point data)
            url = image.getDownloadURL({
                'region': region,
                'dimensions': [size, size],
                'format': 'GEO_TIFF',
                'crs': 'EPSG:4326'
            })
            
            # Download and read with rasterio
            import rasterio
            from io import BytesIO
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Read GeoTIFF from memory
            with rasterio.open(BytesIO(response.content)) as dataset:
                bands = []
                for i in range(1, min(dataset.count + 1, 6)):  # Max 5 bands
                    band = dataset.read(i)
                    bands.append(band)
                
                if len(bands) == 0:
                    raise Exception("No bands in downloaded image")
                
                image_array = np.stack(bands, axis=-1)
            
            # Normalize and convert to uint8 for visualization
            image_array = np.clip(image_array, 0, 1)
            image_array = (image_array * 255).astype(np.uint8)
            
            # Create RGB visualization (use first 3 bands or NIR/Red/Green)
            if image_array.shape[-1] >= 3:
                # Use bands 3,2,1 for natural color (or 4,3,2 for false color)
                rgb = image_array[:, :, :3]
            else:
                # Grayscale to RGB
                rgb = np.repeat(image_array[:, :, 0:1], 3, axis=-1)
            
            return rgb
            
        except Exception as e:
            print(f"❌ Error downloading image: {e}")
            # Return blank image as fallback
            return np.zeros((size, size, 3), dtype=np.uint8)
    
    def get_real_bands(
        self,
        lat: float,
        lon: float,
        date: str,
        buffer_days: int = 30
    ) -> Optional[Dict[str, np.ndarray]]:
        """
        Get real multispectral bands (NIR, Red, SWIR) for change detection
        
        Returns:
            Dictionary with 'nir', 'red', 'swir' bands as numpy arrays
        """
        if not self.initialized:
            return None
        
        try:
            point = ee.Geometry.Point([lon, lat])
            region = point.buffer(2500).bounds()
            
            center = datetime.strptime(date, '%Y-%m-%d')
            start = (center - timedelta(days=buffer_days)).strftime('%Y-%m-%d')
            end = (center + timedelta(days=buffer_days)).strftime('%Y-%m-%d')
            
            # Get Landsat composite
            collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
                .filterBounds(region) \
                .filterDate(start, end) \
                .filter(ee.Filter.lt('CLOUD_COVER', 30)) \
                .map(self._mask_landsat_clouds)
            
            composite = collection.median().clip(region)
            
            # Get individual bands
            red = composite.select('SR_B4').multiply(0.0000275).add(-0.2)
            nir = composite.select('SR_B5').multiply(0.0000275).add(-0.2)
            swir = composite.select('SR_B6').multiply(0.0000275).add(-0.2)
            
            # Download bands
            bands = {}
            for band_name, band_image in [('red', red), ('nir', nir), ('swir', swir)]:
                url = band_image.getThumbURL({
                    'region': region,
                    'dimensions': '256x256',
                    'format': 'png',
                    'min': 0,
                    'max': 0.3  # Reflectance values typically 0-0.3
                })
                response = requests.get(url, timeout=30)
                img = Image.open(BytesIO(response.content)).convert('L')  # Grayscale
                bands[band_name] = np.array(img)
            
            return bands
            
        except Exception as e:
            print(f"❌ Error fetching bands: {e}")
            return None


# Singleton instance
_gee_fetcher = None

def get_gee_fetcher() -> GEEDataFetcher:
    """Get or create GEE fetcher singleton"""
    global _gee_fetcher
    if _gee_fetcher is None:
        _gee_fetcher = GEEDataFetcher()
    return _gee_fetcher
