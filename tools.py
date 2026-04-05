import requests
import random
from datetime import datetime

def get_weather(city, start_date, end_date):
    """Récupère la météo via Open-Meteo (gratuit)"""
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=fr&format=json").json()
        if not geo.get("results"):
            return {"error": f"Ville '{city}' introuvable."}
        lat, lon = geo["results"][0]["latitude"], geo["results"][0]["longitude"]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum&start_date={start_date}&end_date={end_date}&timezone=auto"
        data = requests.get(url).json().get("daily", {})
        codes = {0: "☀️ Ensoleillé", 1: "🌤 Peu nuageux", 2: "⛅ Partiellement nuageux", 3: "☁️ Couvert", 45: "🌫 Brouillard", 51: "🌦 Bruine", 61: "🌧 Pluie", 71: "❄️ Neige", 95: "⚡ Orage"}
        return {
            "city": city,
            "dates": data.get("time", []),
            "temp_max": data.get("temperature_2m_max", []),
            "weather_desc": [codes.get(c, "🌪 Variable") for c in data.get("weathercode", [])],
            "precipitation": data.get("precipitation_sum", [])
        }
    except Exception as e:
        return {"error": str(e)}

def search_flights(origin, destination, date, return_date=None, cabin="economy"):
    """Recherche de vols (mode démo réaliste)"""
    airlines = ["Air France", "EasyJet", "Ryanair", "Lufthansa", "Transavia", "Iberia"]
    codes = ["AF", "U2", "FR", "LH", "TO", "IB"]
    base_prices = {"economy": 89, "premium": 210, "business": 650}
    
    def gen_leg(dep, arr, d):
        return [{
            "airline": random.choice(airlines), 
            "flight": f"{random.choice(codes)}{random.randint(100, 999)}",
            "departure": f"{d}T{random.choice(['06:15', '09:40', '13:20', '17:50'])}",
            "arrival": f"{d}T{random.choice(['08:00', '11:25', '15:05', '19:35'])}",
            "duration": f"{random.randint(1,4)}h{random.randint(0,59):02d}",
            "price": base_prices.get(cabin, 150) + random.randint(-30, 80), 
            "currency": "EUR", "cabin": cabin, 
            "stops": random.choice([0, 0, 1])
        } for _ in range(3)]
        
    return {
        "origin": origin, "destination": destination,
        "outbound": gen_leg(origin, destination, date),
        "return": gen_leg(destination, origin, return_date) if return_date else None,
        "search_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "note": "💡 Résultats simulés (démo). Connectez Amadeus/AviationStack pour du temps réel."
    }