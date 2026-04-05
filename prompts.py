# 🔹 Prompts pour les différents agents

def profile_prompt(destination, interests):
    if interests and interests.strip():
        return f"L'utilisateur a des centres d'intérêt : {interests}\nDestination : {destination}\nConfirme et enrichis ces centres d'intérêt."
    else:
        return f"L'utilisateur n'a pas spécifié de centres d'intérêt pour {destination}.\nSuggère 3-5 centres d'intérêt pertinents."

def planner_prompt(destination, start_date, end_date, interests, option_number):
    return f"""
Crée un itinéraire pour {destination}.
📅 Dates : {start_date} - {end_date}
🎯 Centres d'intérêt : {interests if interests else "À suggérer"}
⚠️ Option {option_number} sur 2.
Format : ## Jour 1 ... Matin, Après-midi, Soir
"""

def planner_compare_prompt(destination, option_a, option_b):
    return f"Compare les itinéraires A:\n{option_a}\nB:\n{option_b}\nFais un résumé comparatif court."

def transport_prompt(destination, start_date, end_date, origin="France"):
    return f"Propose des options de transport pour {destination} du {start_date} au {end_date}, départ de {origin}."

def hotel_prompt(destination, start_date, end_date, budget="moyen"):
    return f"Propose 3 options d'hébergement pour {destination}, budget : {budget}, du {start_date} au {end_date}."

def export_pdf_prompt(destination, itinerary, transport, hotel, user_name, user_email):
    return f"Destination : {destination}, Voyageur : {user_name}, Email : {user_email}\nItinéraire : {itinerary}\nTransport : {transport}\nHôtel : {hotel}"

def chat_prompt(user_question, context):
    return f"Contexte voyage : {context}\nQuestion utilisateur : {user_question}\nRéponds clairement et corrige les incohérences."