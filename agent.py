# agent.py
from prompts import *
from llm import call_llm

# 🤖 Agent 1 : Planificateur
def planner_agent(destination, days):
    # Génération météo
    weather = call_llm(
        f"Donne une météo réaliste simple pour {destination} sur {days} jours"
    )

    # Propositions d'activités selon météo
    activities = call_llm(
        f"Propose des activités adaptées à {destination} selon cette météo : {weather}"
    )

    # Création de l'itinéraire
    itinerary = call_llm(
        f"""
Crée un itinéraire clair pour {days} jours à {destination}.

Format :
Jour 1 :
- Matin :
- Après-midi :
- Soir :

Activités :
{activities}
"""
    )

    return weather, activities, itinerary


# 🤖 Agent 2 : Critique et Self-Correction
def critic_agent(itinerary):
    # Analyse critique
    critique = call_llm(
        f"""
Analyse cet itinéraire pour détecter :
- incohérences
- doublons
- activités impossibles ou mal ordonnées

Itinéraire :
{itinerary}
"""
    )

    # Amélioration selon critique
    improved = call_llm(
        f"""
Améliore cet itinéraire en corrigeant les problèmes détectés :

{itinerary}

En tenant compte de cette analyse :
{critique}
"""
    )

    return critique, improved


# 🎯 Agent principal
def run_agent(destination, days):
    steps = []

    # 🧠 Chain of Thought : Analyse de la demande
    thought = call_llm(cot_prompt(destination, days))
    steps.append(("🧠 Analyse", thought))

    # 🌳 Tree of Thoughts : Génération de plusieurs alternatives
    alternatives_list = []
    for i in range(3):  # Génère 3 alternatives
        alt_itinerary = call_llm(tot_prompt(destination))
        alternatives_list.append(alt_itinerary)
    steps.append(("🌳 Options de voyage", alternatives_list))

    # 🤖 Agent 1 : Sélection de la meilleure alternative
    best_alt = alternatives_list[0]  # On peut choisir selon un score ou critique future
    weather, activities, itinerary = planner_agent(destination, days)
    steps.append(("🤖 Agent 1", "Itinéraire généré avec Agent 1"))

    # 🤖 Agent 2 : Self-Correction et critique
    critique, improved_itinerary = critic_agent(itinerary)
    steps.append(("🤖 Agent 2", "Analyse et amélioration effectuées"))

    # Résumé automatique
    summary = call_llm(
        f"Résume le voyage à {destination} pour {days} jours de façon concise et claire."
    )

    return {
        "steps": steps,
        "summary": summary,
        "weather": weather,
        "activities": activities,
        "alternatives": alternatives_list,
        "critique": critique,
        "itinerary": improved_itinerary
    }