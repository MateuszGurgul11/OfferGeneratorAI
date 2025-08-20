import requests
import math
from typing import Optional, Tuple

base_prices = {
    "Ankel Mini 1,8m": 10800,
    "Ankel Medium Open 2,4m": 11580,
    "Ankel Medium Close 2,4m": 13160,
    "Ankel Large 3,0m": 13800,
    "Ankel XL 3,6m": 14480,
    "Toone Mini 1,8m":  9180,
    "Toone 2,4 Open": 9900,
    "Toone 2,4 Close": 11500,
    "Toone 3,0 Close": 12200,
    "Toone 3,6 Close": 12900,
    "Toone 3,6 Open": 12900,
}

base_paint_prices = {
    "Ankel Mini 1,8m": 750,
    "Ankel Medium Open 2,4m": 800,
    "Ankel Medium Close 2,4m": 800,
    "Ankel Large 3,0m": 850,
    "Ankel XL 3,6m": 900,
    "Toone Mini 1,8m":  750,
    "Toone 2,4 Open": 800,
    "Toone 2,4 Close": 800,
    "Toone 3,0 Close": 850,
    "Toone 3,6 Close": 900,
    "Toone 3,6 Open": 900,
}

furnace_prices = {
    "Piec Harvia z kominem i kamieniami. Spalinowy, ładowany od wewnątrz": 3850,
    "Piec do sauny opalany drewnem - STOVEMAN 13-LS z kominem i kamieniami – ładowany od zewnątrz": 4500,
    "Piec elektryczny NARVI 9 kW": 1800,
}

START_POINT = {
    "lat": 52.34916,  
    "lng": 17.46995,  
    "address": "Zasutowo"  
}


def get_coordinates_from_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Pobiera współrzędne geograficzne dla podanego adresu używając Nominatim API (OpenStreetMap).
    
    Args:
        address (str): Adres do geokodowania
        
    Returns:
        Optional[Tuple[float, float]]: Krotka (lat, lng) lub None jeśli nie znaleziono
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1,
            "countrycodes": "pl"  
        }
        
        headers = {
            "User-Agent": "SaunaOffersApp/1.0"  
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0:
            lat = float(data[0]["lat"])
            lng = float(data[0]["lon"])
            return (lat, lng)
        else:
            print(f"Nie znaleziono współrzędnych dla adresu: {address}")
            return None
            
    except requests.RequestException as e:
        print(f"Błąd podczas geokodowania adresu {address}: {e}")
        return None
    except (KeyError, ValueError, IndexError) as e:
        print(f"Błąd parsowania odpowiedzi dla adresu {address}: {e}")
        return None

def calculate_distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    ray_of_the_earth = 6371.0
    R = ray_of_the_earth
    
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)

def get_distance_to_location(destination_address: str) -> Tuple[float, str]:
    if not destination_address or destination_address.strip() == "":
        return 0.0, "Brak adresu"
    
    destination_coords = get_coordinates_from_address(destination_address)
    
    if destination_coords is None:
        return 0.0, f"Nie można znaleźć lokalizacji: {destination_address}"
    
    destination_lat, destination_lng = destination_coords
    
    distance = calculate_distance_km(
        START_POINT["lat"], START_POINT["lng"],
        destination_lat, destination_lng
    )
    
    return distance, f"Odległość od {START_POINT['address']} do {destination_address}: {distance} km"

def calculate_delivery_cost(distance_km: float) -> float:
    transport_price = 0
    transport_price += (distance_km * 2) * 2.5
    return transport_price

def get_delivery_info(location: str) -> dict:
    distance, message = get_distance_to_location(location)
    delivery_cost = calculate_delivery_cost(distance)
    
    return {
        "distance_km": distance,
        "delivery_cost": delivery_cost,
        "message": message,
    }