import requests
from datetime import datetime
from typing import Dict, Optional

class WeatherDataFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def fetch_weather_data(self, lat: float, lon: float) -> Optional[Dict]:
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            weather_info = {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'temp_min': data['main']['temp_min'],
                'temp_max': data['main']['temp_max'],
                'pressure': data['main']['pressure'],
                'humidity': data['main']['humidity'],
                'sea_level': data['main'].get('sea_level', 'N/A'),
                'ground_level': data['main'].get('grnd_level', 'N/A'),
                'visibility': data.get('visibility', 0) / 1000,
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'wind_gust': data['wind'].get('gust', 0),
                'cloudiness': data['clouds']['all'],
                'weather_main': data['weather'][0]['main'],
                'weather_description': data['weather'][0]['description'],
                'weather_icon': data['weather'][0]['icon'],
                'rainfall_1h': data.get('rain', {}).get('1h', 0),
                'rainfall_3h': data.get('rain', {}).get('3h', 0),
                'snowfall_1h': data.get('snow', {}).get('1h', 0),
                'snowfall_3h': data.get('snow', {}).get('3h', 0),
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S'),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S'),
                'timezone': data['timezone'],
                'location_name': data.get('name', 'Unknown'),
                'country': data['sys'].get('country', 'Unknown'),
                'timestamp': datetime.fromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
            }

            return weather_info

        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing weather data: {e}")
            return None

    def get_weather_summary(self, weather_data: Dict) -> str:
        if not weather_data:
            return "Weather data unavailable"

        summary = f"""
        **Location**: {weather_data['location_name']}, {weather_data['country']}
        **Conditions**: {weather_data['weather_description'].title()}
        **Temperature**: {weather_data['temperature']}°C (Feels like {weather_data['feels_like']}°C)
        **Humidity**: {weather_data['humidity']}%
        **Wind**: {weather_data['wind_speed']} m/s
        **Pressure**: {weather_data['pressure']} hPa
        """

        if weather_data['rainfall_1h'] > 0:
            summary += f"\n**Rainfall (1h)**: {weather_data['rainfall_1h']} mm"

        return summary
