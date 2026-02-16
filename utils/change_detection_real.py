"""
Real Change Detection using actual satellite multispectral bands
Replaces RGB band simulation with real NIR, Red, SWIR data
"""

import numpy as np
from typing import Dict, Tuple, Optional
import cv2

class RealChangeDetectionAnalyzer:
    """Change detection using real multispectral satellite bands"""
    
    def __init__(self):
        self.algorithms = ['NDVI', 'NDMI', 'NDBI', 'CVA']
        self.use_real_bands = True  # Flag to use real vs simulated bands
    
    def calculate_ndvi(self, nir: np.ndarray, red: np.ndarray) -> np.ndarray:
        """Calculate NDVI from real NIR and Red bands"""
        with np.errstate(divide='ignore', invalid='ignore'):
            ndvi = (nir.astype(float) - red.astype(float)) / (nir.astype(float) + red.astype(float))
            ndvi = np.nan_to_num(ndvi, nan=0.0, posinf=0.0, neginf=0.0)
        return ndvi
    
    def calculate_ndmi(self, nir: np.ndarray, swir: np.ndarray) -> np.ndarray:
        """Calculate NDMI from real NIR and SWIR bands"""
        with np.errstate(divide='ignore', invalid='ignore'):
            ndmi = (nir.astype(float) - swir.astype(float)) / (nir.astype(float) + swir.astype(float))
            ndmi = np.nan_to_num(ndmi, nan=0.0, posinf=0.0, neginf=0.0)
        return ndmi
    
    def calculate_ndbi(self, swir: np.ndarray, nir: np.ndarray) -> np.ndarray:
        """Calculate NDBI from real SWIR and NIR bands"""
        with np.errstate(divide='ignore', invalid='ignore'):
            ndbi = (swir.astype(float) - nir.astype(float)) / (swir.astype(float) + nir.astype(float))
            ndbi = np.nan_to_num(ndbi, nan=0.0, posinf=0.0, neginf=0.0)
        return ndbi
    
    def detect_changes_with_real_bands(
        self,
        bands1: Dict[str, np.ndarray],
        bands2: Dict[str, np.ndarray]
    ) -> Dict[str, any]:
        """
        Detect changes using REAL multispectral bands
        
        Args:
            bands1: {'nir': array, 'red': array, 'swir': array} for time 1
            bands2: {'nir': array, 'red': array, 'swir': array} for time 2
        
        Returns:
            Change detection results with statistics
        """
        # Ensure same size
        if bands1['nir'].shape != bands2['nir'].shape:
            for key in bands2:
                bands2[key] = cv2.resize(
                    bands2[key], 
                    (bands1['nir'].shape[1], bands1['nir'].shape[0])
                )
        
        # Calculate indices for both time periods
        ndvi1 = self.calculate_ndvi(bands1['nir'], bands1['red'])
        ndvi2 = self.calculate_ndvi(bands2['nir'], bands2['red'])
        ndvi_change = ndvi2 - ndvi1
        
        ndmi1 = self.calculate_ndmi(bands1['nir'], bands1['swir'])
        ndmi2 = self.calculate_ndmi(bands2['nir'], bands2['swir'])
        ndmi_change = ndmi2 - ndmi1
        
        ndbi1 = self.calculate_ndbi(bands1['swir'], bands1['nir'])
        ndbi2 = self.calculate_ndbi(bands2['swir'], bands2['nir'])
        ndbi_change = ndbi2 - ndbi1
        
        # Calculate CVA magnitude
        cva_magnitude = np.sqrt(ndvi_change**2 + ndmi_change**2 + ndbi_change**2)
        cva_normalized = (cva_magnitude - cva_magnitude.min()) / (cva_magnitude.max() - cva_magnitude.min() + 1e-8)
        
        # Change classification
        no_change = np.sum(cva_normalized < 0.2)
        moderate_change = np.sum((cva_normalized >= 0.2) & (cva_normalized < 0.5))
        significant_change = np.sum(cva_normalized >= 0.5)
        total_pixels = cva_normalized.size
        
        results = {
            'ndvi_change': ndvi_change,
            'ndmi_change': ndmi_change,
            'ndbi_change': ndbi_change,
            'cva_magnitude': cva_normalized,
            'statistics': {
                'ndvi': {
                    'mean_change': float(np.mean(ndvi_change)),
                    'max_change': float(np.max(ndvi_change)),
                    'min_change': float(np.min(ndvi_change)),
                    'std_change': float(np.std(ndvi_change)),
                    'vegetation_gain': float(np.sum(ndvi_change > 0.1) / total_pixels * 100),
                    'vegetation_loss': float(np.sum(ndvi_change < -0.1) / total_pixels * 100)
                },
                'ndmi': {
                    'mean_change': float(np.mean(ndmi_change)),
                    'max_change': float(np.max(ndmi_change)),
                    'min_change': float(np.min(ndmi_change)),
                    'std_change': float(np.std(ndmi_change)),
                    'moisture_gain': float(np.sum(ndmi_change > 0.1) / total_pixels * 100),
                    'moisture_loss': float(np.sum(ndmi_change < -0.1) / total_pixels * 100)
                },
                'ndbi': {
                    'mean_change': float(np.mean(ndbi_change)),
                    'max_change': float(np.max(ndbi_change)),
                    'min_change': float(np.min(ndbi_change)),
                    'std_change': float(np.std(ndbi_change)),
                    'urban_expansion': float(np.sum(ndbi_change > 0.1) / total_pixels * 100),
                    'urban_reduction': float(np.sum(ndbi_change < -0.1) / total_pixels * 100)
                },
                'cva': {
                    'no_change_percent': float(no_change / total_pixels * 100),
                    'moderate_change_percent': float(moderate_change / total_pixels * 100),
                    'significant_change_percent': float(significant_change / total_pixels * 100),
                    'mean_magnitude': float(np.mean(cva_normalized)),
                    'max_magnitude': float(np.max(cva_normalized))
                }
            },
            'data_source': 'Real Satellite Bands (Landsat/Sentinel)',
            'bands_used': 'NIR, Red, SWIR (multispectral)'
        }
        
        return results
    
    def simulate_bands_from_rgb(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        LEGACY: Simulate bands from RGB (for demo mode only)
        ⚠️ NOT scientifically accurate - use real bands instead!
        """
        if len(image.shape) == 2:
            gray = image
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        red = image[:, :, 0] if len(image.shape) == 3 else gray
        green = image[:, :, 1] if len(image.shape) == 3 else gray
        blue = image[:, :, 2] if len(image.shape) == 3 else gray
        
        # Simulated bands (NOT REAL!)
        nir = np.clip(green * 1.2 + 20, 0, 255).astype(np.uint8)
        swir = np.clip(red * 0.8 + blue * 0.3, 0, 255).astype(np.uint8)
        
        return {
            'red': red,
            'green': green,
            'blue': blue,
            'nir': nir,
            'swir': swir
        }
    
    def detect_changes(self, image1: np.ndarray, image2: np.ndarray) -> Dict[str, any]:
        """
        LEGACY: Detect changes from RGB images (demo mode)
        
        For publication-ready results, use detect_changes_with_real_bands() instead
        """
        if image1.shape != image2.shape:
            image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
        
        # Simulate bands from RGB (not accurate!)
        bands1 = self.simulate_bands_from_rgb(image1)
        bands2 = self.simulate_bands_from_rgb(image2)
        
        # Run change detection
        results = self.detect_changes_with_real_bands(bands1, bands2)
        
        # Mark as simulated
        results['data_source'] = 'Simulated Bands (Demo Mode - NOT ACCURATE)'
        results['bands_used'] = 'RGB-derived (not real multispectral)'
        results['warning'] = '⚠️ Results use simulated bands and may not be scientifically accurate'
        
        return results
    
    def get_change_interpretation(self, results: Dict) -> str:
        """Generate human-readable interpretation of changes"""
        stats = results['statistics']
        
        interpretation = []
        
        # Add data source warning if simulated
        if 'warning' in results:
            interpretation.append(f"⚠️ **{results['warning']}**")
            interpretation.append("")
        
        # Vegetation changes
        if stats['ndvi']['vegetation_loss'] > 10:
            interpretation.append(
                f"⚠️ **Significant Vegetation Loss**: {stats['ndvi']['vegetation_loss']:.2f}% "
                f"of area shows vegetation decline"
            )
        elif stats['ndvi']['vegetation_gain'] > 10:
            interpretation.append(
                f"✅ **Vegetation Growth**: {stats['ndvi']['vegetation_gain']:.2f}% "
                f"of area shows vegetation increase"
            )
        
        # Urban changes
        if stats['ndbi']['urban_expansion'] > 5:
            interpretation.append(
                f"🏗️ **Urban Expansion Detected**: {stats['ndbi']['urban_expansion']:.2f}% "
                f"of area shows urban development"
            )
        
        # Moisture changes
        if stats['ndmi']['moisture_loss'] > 15:
            interpretation.append(
                f"💧 **Moisture Depletion**: {stats['ndmi']['moisture_loss']:.2f}% "
                f"of area shows moisture loss (possible drought)"
            )
        elif stats['ndmi']['moisture_gain'] > 15:
            interpretation.append(
                f"💧 **Moisture Increase**: {stats['ndmi']['moisture_gain']:.2f}% "
                f"of area shows moisture gain"
            )
        
        # Overall change
        if stats['cva']['significant_change_percent'] > 20:
            interpretation.append(
                f"🔴 **Major Environmental Change**: {stats['cva']['significant_change_percent']:.2f}% "
                f"of area experienced significant transformation"
            )
        elif stats['cva']['moderate_change_percent'] > 30:
            interpretation.append(
                f"🟡 **Moderate Environmental Change**: {stats['cva']['moderate_change_percent']:.2f}% "
                f"of area shows moderate changes"
            )
        else:
            interpretation.append(
                f"🟢 **Stable Environment**: {stats['cva']['no_change_percent']:.2f}% "
                f"of area remains unchanged"
            )
        
        return "\n\n".join(interpretation) if interpretation else "No significant changes detected"


# For backward compatibility
class ChangeDetectionAnalyzer(RealChangeDetectionAnalyzer):
    """Alias for backward compatibility"""
    pass
