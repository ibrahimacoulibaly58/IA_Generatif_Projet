import re
import json
from datetime import datetime, timedelta
from tools import search_flights
from reasoning import react_cot_loop, tree_of_thoughts, self_correction

def run_agent(user_input, provider="groq"):
    import streamlit as st

    if not st.session_state.get("api_key"):
        return "⚠️ Ajoutez votre clé API dans la sidebar.", None, None

    # Détection d'intention : recherche de vol
    is_flight_req = bool(re.search(r"(vol|billet|avion|flight|avions)", user_input, re.IGNORECASE))

    # Détection de la ville
    city = "Paris"
    c_match = re.search(r"(?:à|pour|vers|depuis)\s+([A-Za-zÀ-ÿ\s]+?)(?:\s+(?:du|le|\d)|$)", user_input)
    if c_match:
        city = c_match.group(1).strip()

    # Détection des dates
    today = datetime.now()
    start = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    end = (today + timedelta(days=6)).strftime("%Y-%m-%d")
    d_match = re.search(r"(\d{1,2})[/-](\d{1,2})", user_input)
    if d_match:
        d, m = d_match.groups()
        start = f"{today.year}-{m.zfill(2)}-{d.zfill(2)}"
        end = (datetime.strptime(start, "%Y-%m-%d") + timedelta(days=4)).strftime("%Y-%m-%d")

    # Préférences utilisateur
    prefs = re.sub(r"(planifie|montre|vol|billet|météo|voyage|destination|activité).*", "", user_input, flags=re.IGNORECASE).strip()
    if not prefs:
        prefs = "Culture, nature, gastronomie, détente"

    # Prompt système pour ReAct
    system_prompt = f"""
Tu es un agent de voyage expert.
Outils disponibles: get_weather (météo), search_flights (vols)
RÈGLE: Si l'utilisateur demande des vols → utilise search_flights.
Sinon → get_weather + génération itinéraire.
Format strict: Thought → Action → Action Input → Observation → Final Answer
"""

    st.info("🔍 Étape 1/4: ReAct + Chain of Thought")
    final_ans, steps = react_cot_loop(system_prompt, provider=provider)

    # Extraction des données météo depuis les steps
    weather_data = None
    for step in steps:
        try:
            obs = json.loads(step.get("observation", "{}"))
            if "city" in obs and "temp_max" in obs:
                weather_data = obs
                break
        except:
            continue

    if not weather_data:
        # Valeur par défaut si échec API
        weather_data = {
            "city": city,
            "dates": [start],
            "temp_max": [20],
            "weather_desc": ["☀️ Ensoleillé"]
        }

    result_data = None
    if is_flight_req:
        # Recherche de vol
        try:
            json_match = re.search(r'\{[\s\S]*"outbound"[\s\S]*\}', final_ans)
            result_data = json.loads(json_match.group()) if json_match else search_flights("Paris", city, start, end, "economy")
        except:
            result_data = {"error": "Format de vol invalide"}
    else:
        # Génération itinéraire
        st.info("🌳 Étape 2/4: Tree of Thoughts")
        best_draft, _, _ = tree_of_thoughts(weather_data, prefs, provider=provider)
        st.info("🔄 Étape 3/4: Self-Correction")
        result_data, critique = self_correction(best_draft, weather_data, provider=provider)
        result_data["critique"] = critique

    st.success("✅ Étape 4/4: Finalisé")
    return "✨ Résultat généré avec succès.", result_data, {
        "react_steps": steps,
        "type": "flight" if is_flight_req else "itinerary"
    }