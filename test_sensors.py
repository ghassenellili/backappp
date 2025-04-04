import requests
import time
from datetime import datetime
import json
import unittest

BASE_URL = "http://localhost:5000/api"  # Added /api to match the blueprint prefix

def validate_reading(reading_type, value):
    """Validate sensor readings before sending"""
    limits = {
        "temperature": (-10, 50),  # °C
        "ph": (0, 14),            # pH scale
        "oxygen": (0, 20)         # mg/L
    }
    
    if reading_type not in limits:
        raise ValueError(f"Invalid reading type: {reading_type}")
    
    min_val, max_val = limits[reading_type]
    if not min_val <= value <= max_val:
        raise ValueError(f"Value {value} for {reading_type} is outside valid range ({min_val}, {max_val})")

def send_sensor_reading(site_id, section_name, reading_type, value):
    # Validate reading before sending
    try:
        validate_reading(reading_type, value)
    except ValueError as e:
        print(f"Validation error: {str(e)}")
        return None

    url = f"{BASE_URL}/readings"
    data = {
        "site_id": site_id,
        "section_name": section_name,
        "reading_type": reading_type,
        "value": value
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Envoi {reading_type}: {value} - Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            # Verify response structure
            assert 'id' in response_data, "Response missing 'id' field"
            assert 'timestamp' in response_data, "Response missing 'timestamp' field"
            assert 'value' in response_data, "Response missing 'value' field"
            
            # Verify value matches
            assert float(response_data['value']) == float(value), f"Value mismatch: sent {value}, received {response_data['value']}"
            
            # Verify timestamp format
            try:
                datetime.fromisoformat(response_data['timestamp'])
            except ValueError:
                raise AssertionError("Invalid timestamp format")
                
            print(f"Validation réussie pour {reading_type}")
            return response_data
        else:
            print(f"Erreur: {response.status_code}")
            try:
                print(response.json())
            except:
                print("Réponse non-JSON:", response.text)
            return None
            
    except Exception as e:
        print(f"Erreur lors de l'envoi: {str(e)}")
        raise

def test_sensors():
    # D'abord, créer un utilisateur de test si nécessaire
    register_user()
    
    # Test pour le site 1, section A1
    site_id = 1
    section_name = "A1"
    
    readings = [
        ("temperature", 3.5),  # Fixed temperature value
        ("ph", 12.2),           # Fixed pH value
        ("oxygen", 2.5)
    ]
  
    
   
    for reading_type, value in readings:
        send_sensor_reading(site_id, section_name, reading_type, value)
        time.sleep(1)

def register_user():
    url = f"{BASE_URL}/register"
    data = {
        "email": "test@example.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(url, json=data)
        print("Enregistrement utilisateur:", response.status_code)
        if response.status_code == 201:
            print("Utilisateur créé avec succès")
        elif response.status_code == 400:
            print("Utilisateur existe déjà")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement: {str(e)}")

def test_get_latest_readings():
    url = f"{BASE_URL}/readings/latest"  # Changed endpoint URL
    try:
        params = {"site_id": 1, "section_name": "A1"}  # Add query parameters
        response = requests.get(url, params=params)
        print(f"\nTest get latest readings - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Latest readings:", response.json())
        else:
            print(f"Erreur: {response.status_code}")
            try:
                print(response.json())
            except:
                print("Réponse non-JSON:", response.text)
                
    except Exception as e:
        print(f"Erreur lors de la récupération: {str(e)}")

if __name__ == "__main__":
    print(f"Début des tests: {datetime.now()}")
    test_sensors()
    test_get_latest_readings()  # Add this line to run the new test
    print(f"Fin des tests: {datetime.now()}")
