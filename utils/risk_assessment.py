from typing import Dict, List, Tuple
from datetime import datetime

class RiskAssessmentSystem:
    def __init__(self):
        self.lulc_classes = {
            'AnnualCrop': 'Annual Crop',
            'Forest': 'Forest',
            'HerbaceousVegetation': 'Herbaceous Vegetation',
            'Highway': 'Highway/Road',
            'Industrial': 'Industrial',
            'Pasture': 'Pasture',
            'PermanentCrop': 'Permanent Crop',
            'Residential': 'Residential',
            'River': 'River/Water Body',
            'SeaLake': 'Sea/Lake'
        }
        
        # Land cover vulnerability scores (base risk)
        self.land_cover_vulnerability = {
            'AnnualCrop': 35,           # Vulnerable to weather
            'Forest': 40,                # Vulnerable to fire/deforestation
            'HerbaceousVegetation': 25,  # Moderate vulnerability
            'Highway': 15,               # Infrastructure, lower environmental risk
            'Industrial': 45,            # High pollution potential
            'Pasture': 30,               # Vulnerable to drought
            'PermanentCrop': 35,         # Vulnerable to seasonal changes
            'Residential': 30,           # Urban heat island, flooding
            'River': 50,                 # Water-related risks
            'SeaLake': 55                # Marine risks
        }

    def assess_risk(self, lulc_class: str, weather_data: Dict, change_stats: Dict = None) -> Dict:
        risk_factors = []
        # Start with base land cover vulnerability
        risk_level = self.land_cover_vulnerability.get(lulc_class, 25)
        recommendations = []

        temp = weather_data.get('temperature', 20)
        feels_like = weather_data.get('feels_like', temp)
        humidity = weather_data.get('humidity', 50)
        wind_speed = weather_data.get('wind_speed', 0)
        wind_gust = weather_data.get('wind_gust', wind_speed)
        rainfall_1h = weather_data.get('rainfall_1h', 0)
        rainfall_3h = weather_data.get('rainfall_3h', 0)
        cloudiness = weather_data.get('cloudiness', 0)
        
        # Temperature-based risks (applies to all)
        if temp > 40:
            risk_factors.append({
                'factor': '🔥 Extreme Heat',
                'severity': 'High',
                'description': f'Dangerous heat levels ({temp}°C) pose severe health and fire risks',
                'value': temp
            })
            risk_level += 35
            if lulc_class in ['Forest', 'HerbaceousVegetation']:
                recommendations.append('CRITICAL: Implement fire prevention measures; monitor forest conditions closely')
            elif lulc_class in ['Residential', 'Industrial']:
                recommendations.append('Issue heat advisory; activate cooling centers; increase water supply')
            else:
                recommendations.append('Prepare for emergency scenarios; maintain alert status')
        elif temp > 35:
            risk_factors.append({
                'factor': '🌡️ High Temperature',
                'severity': 'Medium',
                'description': f'Elevated temperature ({temp}°C) increases environmental stress',
                'value': temp
            })
            risk_level += 18
            if lulc_class in ['Forest', 'HerbaceousVegetation', 'AnnualCrop', 'Pasture']:
                recommendations.append('Monitor vegetation stress; ensure water availability')
            else:
                recommendations.append('Prepare for possible temperature-related incidents')
        elif temp > 32:
            risk_factors.append({
                'factor': '☀️ Warm Temperature',
                'severity': 'Low',
                'description': f'Warm conditions ({temp}°C) may increase risk of some environmental issues',
                'value': temp
            })
            risk_level += 8
        
        if temp < 0:
            risk_factors.append({
                'factor': '❄️ Freezing Temperature',
                'severity': 'High' if temp < -10 else 'Medium',
                'description': f'Freezing conditions ({temp}°C) create infrastructure and agricultural risks',
                'value': abs(temp)
            })
            risk_level += (25 if temp < -10 else 15)
            if lulc_class in ['River', 'SeaLake']:
                recommendations.append('Monitor ice formation; restrict water-based activities')
            elif lulc_class in ['AnnualCrop', 'Pasture', 'PermanentCrop']:
                recommendations.append('Protect crops from frost; provide heat for sensitive plants')
            else:
                recommendations.append('Monitor infrastructure for freeze damage')
        
        # Humidity-based risks
        if humidity < 20:
            risk_factors.append({
                'factor': '🏜️ Extreme Dryness',
                'severity': 'High',
                'description': f'Very low humidity ({humidity}%) creates critical drought conditions',
                'value': (100 - humidity)
            })
            risk_level += 30
            recommendations.append('Implement water conservation; prepare irrigation; monitor for wildfires')
        elif humidity < 35 and temp > 30:
            risk_factors.append({
                'factor': '💨 High Fire Danger',
                'severity': 'High',
                'description': f'Low humidity ({humidity}%) combined with heat creates fire conditions',
                'value': temp + (100 - humidity) / 2
            })
            risk_level += 25
            if lulc_class in ['Forest', 'HerbaceousVegetation', 'Pasture']:
                recommendations.append('ALERT: Extreme fire risk; restrict outdoor activities; pre-position emergency resources')
            else:
                recommendations.append('Prepare for potential fire incidents in adjacent areas')
        elif humidity < 50:
            risk_factors.append({
                'factor': '💧 Low Humidity',
                'severity': 'Medium',
                'description': f'Reduced humidity ({humidity}%) increases evaporation and drought stress',
                'value': (100 - humidity)
            })
            risk_level += 12
            recommendations.append('Increase water monitoring; prepare irrigation schedules')
        
        if humidity > 85:
            risk_factors.append({
                'factor': '☔ High Humidity',
                'severity': 'Medium',
                'description': f'High humidity ({humidity}%) increases disease and flooding risks',
                'value': humidity
            })
            risk_level += 15
            recommendations.append('Prepare for possible heavy rainfall; monitor water drainage')
        
        # Wind-based risks
        if wind_gust > 20:
            risk_factors.append({
                'factor': '💨 Severe Winds',
                'severity': 'High',
                'description': f'Extreme wind gusts ({wind_gust} m/s) pose structural and agricultural dangers',
                'value': wind_gust
            })
            risk_level += 28
            if lulc_class in ['Forest', 'Pasture', 'AnnualCrop']:
                recommendations.append('Secure loose materials; expect tree falls and crop damage; clear emergency routes')
            elif lulc_class in ['Residential', 'Industrial', 'Highway']:
                recommendations.append('Issue wind advisory; secure infrastructure; restrict outdoor operations')
            else:
                recommendations.append('Prepare for weather-related emergencies')
        elif wind_speed > 15:
            risk_factors.append({
                'factor': '🌪️ Strong Winds',
                'severity': 'Medium',
                'description': f'High wind speeds ({wind_speed} m/s) may cause damage',
                'value': wind_speed
            })
            risk_level += 15
            recommendations.append('Monitor for wind damage; secure structures')
        elif wind_speed > 10:
            risk_factors.append({
                'factor': '💨 Windy Conditions',
                'severity': 'Low',
                'description': f'Moderate wind speeds ({wind_speed} m/s) present minor concerns',
                'value': wind_speed
            })
            risk_level += 5
        
        # Rainfall-based risks
        if rainfall_1h > 40:
            risk_factors.append({
                'factor': '🌊 Flash Flood Risk',
                'severity': 'High',
                'description': f'Intense rainfall ({rainfall_1h}mm/h) creates flash flood potential',
                'value': rainfall_1h
            })
            risk_level += 30
            if lulc_class in ['River', 'SeaLake']:
                recommendations.append('ALERT: High flood risk; evacuate flood-prone areas; activate emergency protocols')
            elif lulc_class in ['Residential', 'Industrial', 'Highway']:
                recommendations.append('Prepare evacuations; close low-lying roads; activate drainage systems')
            else:
                recommendations.append('Monitor low-lying areas; prepare for water management')
        elif rainfall_3h > 60:
            risk_factors.append({
                'factor': '🌧️ Heavy Rain',
                'severity': 'High',
                'description': f'Significant rainfall ({rainfall_3h}mm/3h) creates flooding risk',
                'value': rainfall_3h
            })
            risk_level += 25
            recommendations.append('Monitor drainage and flood-prone locations; prepare for flooding')
        elif rainfall_1h > 20:
            risk_factors.append({
                'factor': '🌧️ Moderate Rainfall',
                'severity': 'Medium',
                'description': f'Steady rainfall ({rainfall_1h}mm/h) may cause temporary issues',
                'value': rainfall_1h
            })
            risk_level += 12
            if lulc_class in ['AnnualCrop', 'Pasture', 'PermanentCrop']:
                recommendations.append('Monitor water accumulation; ensure proper drainage; delay field operations')
            else:
                recommendations.append('Monitor water conditions')
        elif rainfall_3h > 0 and humidity > 70:
            risk_factors.append({
                'factor': '🌦️ Wet Conditions',
                'severity': 'Low',
                'description': f'Recent rainfall with high humidity may increase disease risk',
                'value': humidity
            })
            risk_level += 5
            recommendations.append('Monitor crops for fungal/pest issues; maintain vegetation health')
        
        # Vegetation-specific risks (from change detection)
        if change_stats and 'statistics' in change_stats:
            stats = change_stats['statistics']
            
            if lulc_class in ['Forest', 'HerbaceousVegetation', 'Pasture']:
                ndvi_veg_loss = stats.get('ndvi', {}).get('vegetation_loss', 0)
                if ndvi_veg_loss > 25:
                    risk_factors.append({
                        'factor': '🌳 Severe Vegetation Loss',
                        'severity': 'High',
                        'description': f'{ndvi_veg_loss:.1f}% vegetation loss detected - possible deforestation/drought',
                        'value': ndvi_veg_loss
                    })
                    risk_level += 30
                    recommendations.append('URGENT: Investigate vegetation loss; implement reforestation/conservation')
                elif ndvi_veg_loss > 10:
                    risk_factors.append({
                        'factor': '🌱 Vegetation Decline',
                        'severity': 'Medium',
                        'description': f'{ndvi_veg_loss:.1f}% vegetation loss detected',
                        'value': ndvi_veg_loss
                    })
                    risk_level += 15
                    recommendations.append('Monitor vegetation health; assess causes of decline')
            
            if lulc_class in ['AnnualCrop', 'Pasture', 'PermanentCrop', 'HerbaceousVegetation']:
                ndmi_moisture_loss = stats.get('ndmi', {}).get('moisture_loss', 0)
                if ndmi_moisture_loss > 25:
                    risk_factors.append({
                        'factor': '💧 Critical Moisture Loss',
                        'severity': 'High',
                        'description': f'{ndmi_moisture_loss:.1f}% soil moisture loss - potential drought crisis',
                        'value': ndmi_moisture_loss
                    })
                    risk_level += 28
                    recommendations.append('CRITICAL: Increase irrigation immediately; prepare drought contingency plans')
                elif ndmi_moisture_loss > 12:
                    risk_factors.append({
                        'factor': '🏜️ Soil Moisture Decline',
                        'severity': 'Medium',
                        'description': f'{ndmi_moisture_loss:.1f}% soil moisture loss detected',
                        'value': ndmi_moisture_loss
                    })
                    risk_level += 15
                    recommendations.append('Increase irrigation frequency; monitor water management')
            
            if lulc_class in ['Residential', 'Industrial', 'Highway']:
                ndbi_urban_exp = stats.get('ndbi', {}).get('urban_expansion', 0)
                if ndbi_urban_exp > 15:
                    risk_factors.append({
                        'factor': '🏗️ Rapid Urban Expansion',
                        'severity': 'High',
                        'description': f'{ndbi_urban_exp:.1f}% urban expansion - environmental impact concerns',
                        'value': ndbi_urban_exp
                    })
                    risk_level += 18
                    recommendations.append('Assess environmental impact; ensure infrastructure adequacy; plan services')
        
        # Industrial-specific pollution risks
        if lulc_class == 'Industrial':
            # Industrial areas have inherent pollution risk - increase based on weather
            if wind_speed < 5 and cloudiness > 70:  # Stagnant air, traps pollution
                risk_factors.append({
                    'factor': '🏭 Air Quality Risk',
                    'severity': 'High',
                    'description': 'Stagnant air conditions trap industrial emissions',
                    'value': (100 - wind_speed * 10) + cloudiness
                })
                risk_level += 25
                recommendations.append('Monitor air quality; issue pollution warnings; limit emissions')
            elif wind_speed < 3:
                risk_factors.append({
                    'factor': '💨 Poor Air Dispersion',
                    'severity': 'Medium',
                    'description': 'Very light winds limit pollution dispersion',
                    'value': 100 - wind_speed * 20
                })
                risk_level += 15
                recommendations.append('Monitor air quality closely; prepare air quality advisories')
            else:
                risk_factors.append({
                    'factor': '🏭 Industrial Activity',
                    'severity': 'Low',
                    'description': 'Normal industrial risk with adequate wind dispersion',
                    'value': 20
                })
                risk_level += 8
        
        # Agricultural-specific risks
        if lulc_class in ['AnnualCrop', 'PermanentCrop', 'Pasture']:
            if temp > 38 and humidity < 50:
                risk_factors.append({
                    'factor': '🌾 Crop Heat Stress',
                    'severity': 'High',
                    'description': f'Extreme heat ({temp}°C) and dryness stress crops severely',
                    'value': temp + (100 - humidity) / 2
                })
                risk_level += 30
                recommendations.append('Increase irrigation; provide shade protection; consider early harvest')
            elif temp > 35 and humidity < 40:
                risk_factors.append({
                    'factor': '☀️ Crop Stress',
                    'severity': 'Medium',
                    'description': f'Heat and dry conditions stress crops',
                    'value': temp + (100 - humidity) / 3
                })
                risk_level += 18
                recommendations.append('Ensure adequate irrigation; monitor plant health')
        
        # Water body risks
        if lulc_class in ['River', 'SeaLake']:
            if temp < 0 and humidity > 65:
                risk_factors.append({
                    'factor': '🧊 Ice Formation',
                    'severity': 'High',
                    'description': f'Freezing temp ({temp}°C) with moisture risk ice formation',
                    'value': abs(temp)
                })
                risk_level += 20
                recommendations.append('Monitor ice thickness; restrict water access; activate ice response')
            
            if wind_speed > 12:
                risk_factors.append({
                    'factor': '🌊 Roughy Water',
                    'severity': 'High' if wind_speed > 18 else 'Medium',
                    'description': f'Strong winds ({wind_speed} m/s) create hazardous water conditions',
                    'value': wind_speed
                })
                risk_level += (25 if wind_speed > 18 else 15)
                recommendations.append('Issue boating advisory; restrict water activities; warn mariners')
        
        # Ensure at least one risk factor if no major risks
        if not risk_factors:
            risk_factors.append({
                'factor': '✅ Favorable Conditions',
                'severity': 'Low',
                'description': 'Current conditions are stable with minimal environmental risks',
                'value': 0
            })
            recommendations.append('Continue regular monitoring and maintenance protocols')
        
        # Cap risk level at 100
        risk_level = min(100, max(0, risk_level))
        
        # Determine risk category
        if risk_level >= 60:
            risk_category = 'CRITICAL RISK'
            risk_color = '🔴'
        elif risk_level >= 40:
            risk_category = 'HIGH RISK'
            risk_color = '🔴'
        elif risk_level >= 25:
            risk_category = 'MEDIUM RISK'
            risk_color = '🟡'
        elif risk_level >= 12:
            risk_category = 'LOW RISK'
            risk_color = '🟢'
        else:
            risk_category = 'MINIMAL RISK'
            risk_color = '🟢'

        return {
            'risk_level': risk_level,
            'risk_category': risk_category,
            'risk_color': risk_color,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'lulc_type': self.lulc_classes.get(lulc_class, lulc_class)
        }

    def generate_risk_report(self, risk_assessment: Dict) -> str:
        report = f"""
        ### {risk_assessment['risk_color']} Risk Assessment: {risk_assessment['risk_category']}

        **Land Cover Type**: {risk_assessment['lulc_type']}
        **Overall Risk Score**: {risk_assessment['risk_level']}/100

        ---

        #### 🎯 Identified Risk Factors

        """

        for i, factor in enumerate(risk_assessment['risk_factors'], 1):
            severity_emoji = '🔴' if factor['severity'] == 'High' else '🟡' if factor['severity'] == 'Medium' else '🟢'
            report += f"""
        **{i}. {factor['factor']}** {severity_emoji}
        - **Severity**: {factor['severity']}
        - **Description**: {factor['description']}
        - **Risk Value**: {factor['value']:.2f}

        """

        report += """
        ---

        #### 💡 Recommendations

        """

        for i, rec in enumerate(risk_assessment['recommendations'], 1):
            report += f"{i}. {rec}\n\n"

        return report
