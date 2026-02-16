import tensorflow as tf
import numpy as np
from typing import Dict, Tuple
import os

class LULCClassifier:
    def __init__(self, model_path='model/eurosat_model.h5'):
        self.model_path = model_path
        self.class_names = [
            'AnnualCrop',
            'Forest',
            'HerbaceousVegetation',
            'Highway',
            'Industrial',
            'Pasture',
            'PermanentCrop',
            'Residential',
            'River',
            'SeaLake'
        ]

        self.class_descriptions = {
            'AnnualCrop': 'Annual Crop - Agricultural land with seasonal crops',
            'Forest': 'Forest - Dense tree coverage and woodland areas',
            'HerbaceousVegetation': 'Herbaceous Vegetation - Grasslands and natural vegetation',
            'Highway': 'Highway/Road - Major transportation infrastructure',
            'Industrial': 'Industrial - Manufacturing and industrial facilities',
            'Pasture': 'Pasture - Grazing land for livestock',
            'PermanentCrop': 'Permanent Crop - Orchards, vineyards, and perennial crops',
            'Residential': 'Residential - Housing and residential areas',
            'River': 'River - Water bodies including rivers and streams',
            'SeaLake': 'Sea/Lake - Large water bodies including seas and lakes'
        }

        self.class_colors = {
            'AnnualCrop': '#FFD700',
            'Forest': '#228B22',
            'HerbaceousVegetation': '#90EE90',
            'Highway': '#808080',
            'Industrial': '#8B4513',
            'Pasture': '#ADFF2F',
            'PermanentCrop': '#FF8C00',
            'Residential': '#FF6347',
            'River': '#4682B4',
            'SeaLake': '#0000FF'
        }

        self.model = None
        self.load_model()

    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
                print(f"Model loaded from {self.model_path}")
            else:
                print(f"Model file not found at {self.model_path}")
                print("Creating a new model...")
                from model.train_model import EuroSATModelTrainer
                trainer = EuroSATModelTrainer()
                self.model = trainer.create_pretrained_model(self.model_path)
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Creating a new model...")
            from model.train_model import EuroSATModelTrainer
            trainer = EuroSATModelTrainer()
            self.model = trainer.create_pretrained_model(self.model_path)

    def classify(self, image: np.ndarray) -> Dict:
        if self.model is None:
            return {
                'predicted_class': 'Unknown',
                'confidence': 0.0,
                'all_probabilities': {},
                'top_3_predictions': []
            }

        if len(image.shape) == 3:
            image_batch = np.expand_dims(image, axis=0)
        else:
            image_batch = image

        predictions = self.model.predict(image_batch, verbose=0)
        probabilities = predictions[0]

        predicted_idx = np.argmax(probabilities)
        predicted_class = self.class_names[predicted_idx]
        confidence = float(probabilities[predicted_idx])

        all_probs = {
            self.class_names[i]: float(probabilities[i])
            for i in range(len(self.class_names))
        }

        top_3_idx = np.argsort(probabilities)[-3:][::-1]
        top_3_predictions = [
            {
                'class': self.class_names[idx],
                'confidence': float(probabilities[idx]),
                'description': self.class_descriptions[self.class_names[idx]]
            }
            for idx in top_3_idx
        ]

        return {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'description': self.class_descriptions[predicted_class],
            'color': self.class_colors[predicted_class],
            'all_probabilities': all_probs,
            'top_3_predictions': top_3_predictions
        }

    def get_class_info(self, class_name: str) -> Dict:
        return {
            'name': class_name,
            'description': self.class_descriptions.get(class_name, 'Unknown'),
            'color': self.class_colors.get(class_name, '#CCCCCC')
        }
