import numpy as np
from PIL import Image
import requests
from io import BytesIO
from typing import Optional, Tuple
import random

class SatelliteImageFetcher:
    def __init__(self):
        self.zoom_level = 13
        self.image_size = 256

    def fetch_satellite_image(self, lat: float, lon: float) -> Optional[np.ndarray]:
        try:
            tile_x, tile_y = self._lat_lon_to_tile(lat, lon, self.zoom_level)

            url = f"https://mt1.google.com/vt/lyrs=s&x={tile_x}&y={tile_y}&z={self.zoom_level}"

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            image = Image.open(BytesIO(response.content))
            image_array = np.array(image)

            if len(image_array.shape) == 2:
                image_array = np.stack([image_array] * 3, axis=-1)

            return image_array

        except Exception as e:
            print(f"Error fetching satellite image: {e}")
            return self._generate_placeholder_image()

    def _lat_lon_to_tile(self, lat: float, lon: float, zoom: int) -> Tuple[int, int]:
        lat_rad = np.radians(lat)
        n = 2.0 ** zoom
        x_tile = int((lon + 180.0) / 360.0 * n)
        y_tile = int((1.0 - np.log(np.tan(lat_rad) + (1 / np.cos(lat_rad))) / np.pi) / 2.0 * n)
        return x_tile, y_tile

    def _generate_placeholder_image(self) -> np.ndarray:
        image = np.random.randint(50, 200, (256, 256, 3), dtype=np.uint8)
        return image

    def simulate_temporal_image(self, base_image: np.ndarray, days_offset: int = 30) -> np.ndarray:
        change_factor = days_offset / 100.0

        modified = base_image.copy().astype(float)

        brightness_change = np.random.uniform(-20, 20) * change_factor
        modified += brightness_change

        random_mask = np.random.random(base_image.shape[:2]) < (0.1 * change_factor)
        modified[random_mask] = modified[random_mask] * np.random.uniform(0.7, 1.3)

        modified = np.clip(modified, 0, 255).astype(np.uint8)

        return modified

    def preprocess_for_model(self, image: np.ndarray, target_size: Tuple[int, int] = (64, 64)) -> np.ndarray:
        """Enhanced preprocessing for satellite imagery with histogram equalization and normalization"""
        from PIL import Image
        import cv2

        if len(image.shape) == 2:
            image = np.stack([image] * 3, axis=-1)

        # Ensure uint8
        if image.dtype != np.uint8:
            image = np.uint8(np.clip(image, 0, 255))

        # Convert to PIL for resizing
        pil_image = Image.fromarray(image)
        pil_image = pil_image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Convert back to numpy
        resized = np.array(pil_image).astype('uint8')
        
        # Enhanced preprocessing for satellite imagery
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) for better feature extraction
        lab = cv2.cvtColor(resized, cv2.COLOR_RGB2LAB)
        l_channel = lab[:,:,0]
        
        # CLAHE on L channel for better detail preservation
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l_channel_clahe = clahe.apply(l_channel)
        
        lab[:,:,0] = l_channel_clahe
        processed = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        # Normalize to [0, 1] range with better scaling
        processed = processed.astype('float32') / 255.0
        
        # Optional: Apply slight sharpening to enhance edges (satellite features)
        # This helps distinguish between different land cover types
        processed_img = Image.fromarray((processed * 255).astype('uint8'))
        
        return processed
