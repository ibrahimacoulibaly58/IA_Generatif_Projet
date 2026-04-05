import os
from groq import Groq
from dotenv import load_dotenv
from prompts import *

# 🔑 Charger clé API
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ Clé API GROQ introuvable. Vérifie .env")

client = Groq(api_key=api_key)

SYSTEM_PROMPTS = {
    "default": "Tu es un assistant expert et précis. Pense étape par étape pour résoudre chaque problème.",
    "planner": "Tu es un planificateur expert. Applique CoT, ToT, ReAct et Self-Correction.",
    "transport": "Tu es un expert en transport. Utilise ReAct : Pensée → Action → Observation → Réponse.",
    "hotel": "Tu es un expert en hébergement. Applique CoT et vérifie chaque suggestion.",
    "profile": "Tu es un expert en profil voyageur. Déduis les centres d'intérêt étape par étape et vérifie la cohérence.",
    "export": "Tu es un expert en rédaction de documents. Vérifie et corrige toute incohérence avant de retourner le texte."
}

def call_llm_with_retry(prompt, agent_type="default", max_retries=3):
    for _ in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPTS.get(agent_type, SYSTEM_PROMPTS["default"])},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = str(e)
    return f"❌ Erreur après {max_retries} tentatives : {last_error}"


# 🔹 Agents
def profile_agent(destination, interests=""):
    prompt = profile_prompt(destination, interests)
    return call_llm_with_retry(prompt, agent_type="profile")

def planner_agent(destination, start_date, end_date, interests, option_number=1):
    prompt = planner_prompt(destination, start_date, end_date, interests, option_number)
    return call_llm_with_retry(prompt, agent_type="planner")

def compare_itineraries(destination, option_a, option_b):
    prompt = planner_compare_prompt(destination, option_a, option_b)
    return call_llm_with_retry(prompt, agent_type="planner")

def transport_agent(destination, start_date, end_date, origin="France"):
    prompt = transport_prompt(destination, start_date, end_date, origin)
    return call_llm_with_retry(prompt, agent_type="transport")

def hotel_agent(destination, start_date, end_date, budget="moyen"):
    prompt = hotel_prompt(destination, start_date, end_date, budget)
    return call_llm_with_retry(prompt, agent_type="hotel")

def export_agent(destination, itinerary, transport, hotel, user_name, user_email):
    prompt = export_pdf_prompt(destination, itinerary, transport, hotel, user_name, user_email)
    return call_llm_with_retry(prompt, agent_type="export")

def chat_agent(user_question, context=""):
    from prompts import chat_prompt
    prompt = chat_prompt(user_question, context)
    return call_llm_with_retry(prompt, agent_type="default")